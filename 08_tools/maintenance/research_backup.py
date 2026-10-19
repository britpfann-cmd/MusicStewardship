"""Versioned project preservation. No network writes occur in dry-run mode."""
from __future__ import annotations

import argparse
from contextlib import closing
import ctypes
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import stat
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
import uuid


SCHEMA = "musicstewardship.backup.v1"
CACHE_DIRS = {"__pycache__", ".pytest_cache"}
SQLITE_HEADER = b"SQLite format 3\0"


class BackupError(RuntimeError):
    pass


def git(root: Path, *args: str) -> str:
    env = {k: v for k, v in os.environ.items() if k not in {
        "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY",
        "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_COMMON_DIR",
    }}
    env.update(GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0", GIT_NO_LAZY_FETCH="1")
    result = subprocess.run(
        ["git", "-c", "core.hooksPath=", "-c", "core.fsmonitor=false", "-C", str(root), *args],
        capture_output=True, text=True, encoding="utf-8", env=env,
    )
    if result.returncode:
        raise BackupError(f"Git {args[0]} failed: {result.stderr.strip()}")
    return result.stdout


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def json_bytes(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def write_new(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(data)


def copy_new(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with source.open("rb") as src, destination.open("xb") as dst:
        shutil.copyfileobj(src, dst)
    shutil.copystat(source, destination)


def mapped_share(destination: Path) -> str:
    """Read Z:'s mapping through Windows; never remap or authenticate a drive."""
    if os.name != "nt" or str(destination).replace("\\", "/").rstrip("/").upper() != "Z:":
        raise BackupError("The production destination must be the mapped Z: root")
    length = ctypes.c_ulong(32768)
    buffer = ctypes.create_unicode_buffer(length.value)
    query = ctypes.windll.mpr.WNetGetConnectionW
    query.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.POINTER(ctypes.c_ulong)]
    query.restype = ctypes.c_ulong
    result = query("Z:", buffer, ctypes.byref(length))
    if result:
        raise BackupError(f"Cannot resolve Z: mapping (Windows error {result})")
    return buffer.value


def canonical_share(value: str) -> str:
    value = value.replace("/", "\\").rstrip("\\")
    parts = value[2:].split("\\") if value.startswith("\\\\") else []
    if len(parts) != 2 or not all(parts) or any(p in {".", ".."} for p in parts):
        raise BackupError("Expected share must be an explicit UNC root: \\\\server\\share")
    return value.casefold()


def validate_destination(source: Path, destination: Path, expected_share: str, probe) -> str:
    expected = canonical_share(expected_share)
    actual = probe(destination)
    if canonical_share(actual) != expected:
        raise BackupError("Destination mapping does not match the expected UNC share")
    if not destination.is_dir():
        raise BackupError("Destination root is not accessible; it will not be created")
    resolved = destination.resolve()
    if resolved == source or resolved.is_relative_to(source) or source.is_relative_to(resolved):
        raise BackupError("Source and destination must be separate directory trees")
    return actual


def inventory(source: Path) -> dict:
    """Hash every included file; reject links rather than following external trees."""
    if not (source / ".git").is_dir():
        raise BackupError("A standalone repository with a real .git directory is required")
    if (source / ".git/objects/info/alternates").exists() or (source / ".git/commondir").exists():
        raise BackupError("External Git object stores/worktrees require a separate preservation design")
    tracked = set(git(source, "ls-files", "-z").rstrip("\0").split("\0"))
    entries, directories, excluded = [], [], []
    stack = [source]
    while stack:
        directory = stack.pop()
        for path in sorted(directory.iterdir()):
            relative = path.relative_to(source).as_posix()
            info = path.lstat()
            if path.is_symlink() or getattr(info, "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400):
                raise BackupError(f"Link/reparse point requires explicit handling: {relative}")
            if path.is_dir():
                has_tracked = any(p.startswith(relative + "/") for p in tracked)
                is_virtual_environment = (path / "pyvenv.cfg").is_file()
                if (path.name in CACHE_DIRS or is_virtual_environment) and not has_tracked:
                    excluded.append(relative + "/")
                    continue
                directories.append(relative)
                stack.append(path)
            elif path.is_file():
                if path.name == ".git":
                    raise BackupError(f"External/nested Git directory pointer: {relative}")
                if relative not in tracked and path.suffix.lower() in {".pyc", ".pyo"}:
                    excluded.append(relative)
                    continue
                if relative.startswith(".git/") and path.name.endswith(".lock"):
                    raise BackupError(f"Active Git lock: {relative}")
                with path.open("rb") as stream:
                    sqlite = stream.read(16) == SQLITE_HEADER
                before = (info.st_size, info.st_mtime_ns)
                digest = sha256(path)
                after = path.stat()
                if before != (after.st_size, after.st_mtime_ns):
                    raise BackupError(f"File changed while inventorying: {relative}")
                entries.append({"path": relative, "bytes": info.st_size,
                                "mtime_ns": info.st_mtime_ns, "sha256": digest, "sqlite": sqlite})
            else:
                raise BackupError(f"Unsupported filesystem entry: {relative}")
    return {"files": sorted(entries, key=lambda x: x["path"]),
            "directories": sorted(directories), "excluded": sorted(excluded),
            "head": git(source, "rev-parse", "HEAD").strip(),
            "refs": git(source, "for-each-ref", "--format=%(objectname) %(refname)"),
            "status": git(source, "status", "--porcelain=v1", "--untracked-files=all")}


def database_signature(path: Path) -> dict:
    with closing(sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)) as connection:
        integrity = [r[0] for r in connection.execute("PRAGMA integrity_check")]
        if integrity != ["ok"]:
            raise BackupError(f"SQLite integrity check failed for {path.name}")
        schema = connection.execute(
            "SELECT type,name,tbl_name,sql FROM sqlite_master ORDER BY type,name"
        ).fetchall()
        counts = {}
        for (name,) in connection.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
            quoted = '"' + name.replace('"', '""') + '"'
            counts[name] = connection.execute(f"SELECT COUNT(*) FROM {quoted}").fetchone()[0]
        violations = connection.execute("PRAGMA foreign_key_check").fetchall()
        return json.loads(json.dumps({"schema": schema, "table_counts": counts,
                                      "foreign_key_violations": violations}))


def sqlite_snapshot(source: Path, destination: Path) -> dict:
    """Use a disposable working copy: never open a live research DB with SQLite."""
    if destination.exists():
        raise BackupError("SQLite snapshot target already exists")
    destination.parent.mkdir(parents=True, exist_ok=True)
    deadline = time.monotonic() + 60

    def progress(status, remaining, total):
        if time.monotonic() > deadline:
            raise BackupError("SQLite backup timed out")

    with closing(sqlite3.connect(source.resolve().as_uri() + "?mode=ro", uri=True)) as src:
        with closing(sqlite3.connect(destination)) as dst:
            src.backup(dst, pages=256, progress=progress, sleep=0.05)
            # A backup can inherit WAL mode. Publish a standalone database so
            # read-only restoration checks do not create WAL/SHM beside it.
            dst.execute("PRAGMA journal_mode=DELETE")
    signature = database_signature(destination)
    if signature != database_signature(source):
        raise BackupError("SQLite snapshot schema/counts differ from captured input")
    return signature


def artifact_manifest(root: Path) -> list[dict]:
    return [{"path": p.relative_to(root).as_posix(), "bytes": p.stat().st_size, "sha256": sha256(p)}
            for p in sorted(root.rglob("*")) if p.is_file()]


def verify_files(root: Path, entries: list[dict]) -> None:
    for entry in entries:
        path = root / entry["path"]
        if not path.is_file() or path.stat().st_size != entry["bytes"] or sha256(path) != entry["sha256"]:
            raise BackupError(f"Artifact verification failed: {entry['path']}")


def verify_restore(backup: Path, manifest: dict, restore: Path, signatures: dict) -> dict:
    """Read the destination, restore separately, and validate data plus Git recovery."""
    verify_files(backup, manifest["files"])
    for directory in manifest["directories"]:
        if not (backup / directory).is_dir():
            raise BackupError(f"Missing backup directory: {directory}")
        (restore / directory).mkdir(parents=True, exist_ok=True)
    for entry in manifest["files"]:
        copy_new(backup / entry["path"], restore / entry["path"])
    verify_files(restore, manifest["files"])
    project = restore / "payload/project"
    git(project, "fsck", "--full")
    if git(project, "rev-parse", "HEAD").strip() != manifest["source"]["head"]:
        raise BackupError("Restored HEAD mismatch")
    if git(project, "for-each-ref", "--format=%(objectname) %(refname)") != manifest["source"]["refs"]:
        raise BackupError("Restored Git references differ")
    bundle = restore / "git/repository.bundle"
    git(project, "bundle", "verify", str(bundle))
    recovered = restore / "bundle-recovery.git"
    git(project, "clone", "--mirror", str(bundle), str(recovered))
    git(recovered, "fsck", "--full")
    if git(recovered, "for-each-ref", "--format=%(objectname) %(refname)") != manifest["source"]["refs"]:
        raise BackupError("Bundle recovery references differ")
    for relative, expected in signatures.items():
        if database_signature(project / relative) != expected:
            raise BackupError(f"Restored SQLite differs: {relative}")
    return {"files_verified": len(manifest["files"]), "sqlite_verified": len(signatures),
            "git_fsck": "passed", "bundle_restore": "passed",
            "foreign_key_violations": {p: s["foreign_key_violations"] for p, s in signatures.items()
                                       if s["foreign_key_violations"]}}


def run_backup(source: Path, destination: Path, expected_share: str, *, dry_run=False,
               quiesced=False, probe=mapped_share, backup_name=None) -> dict:
    source, destination = source.resolve(), destination.absolute()
    share = validate_destination(source, destination, expected_share, probe)
    initial = inventory(source)
    plan = {"schema": SCHEMA, "dry_run": dry_run, "source_root": str(source),
            "destination_root": str(destination), "mapped_share": share,
            "file_count": len(initial["files"]), "bytes": sum(f["bytes"] for f in initial["files"]),
            "sqlite_count": sum(f["sqlite"] for f in initial["files"]),
            "inventory": initial,
            "validation_limits": "Dry-run does not test writes, SQLite integrity, or restoration"}
    if dry_run:
        return plan
    if not quiesced:
        raise BackupError("Stop project/Git/database writers and explicitly confirm --quiesced")
    # Unique mkdir is the reservation: existing backup directories are never reused.
    name = backup_name or ("MusicStewardship_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ_") + uuid.uuid4().hex[:12])
    if Path(name).name != name or name in {".", ".."} or "/" in name or "\\" in name:
        raise BackupError("Invalid backup directory name")
    target = destination / name
    with tempfile.TemporaryDirectory(prefix="musicstewardship-backup-") as temp:
        work = Path(temp)
        capture, stage = work / "capture", work / "stage"
        for directory in initial["directories"]:
            (capture / directory).mkdir(parents=True, exist_ok=True)
        for entry in initial["files"]:
            copy_new(source / entry["path"], capture / entry["path"])
        verify_files(capture, initial["files"])
        if inventory(source) != initial:
            raise BackupError("Source changed during capture; no backup was published")
        databases = {f["path"] for f in initial["files"] if f["sqlite"]}
        companions = {p + suffix for p in databases for suffix in ("-wal", "-shm", "-journal")}
        for directory in initial["directories"]:
            (stage / "payload/project" / directory).mkdir(parents=True, exist_ok=True)
        for entry in initial["files"]:
            relative = entry["path"]
            prefix = "raw_sqlite" if relative in databases | companions else "payload/project"
            copy_new(capture / relative, stage / prefix / relative)
        signatures = {}
        for relative in sorted(databases):
            # WAL/SHM recovery can modify only this disposable copy, never capture or source.
            working_db = work / "sqlite_work" / relative
            for candidate in (relative, *(relative + s for s in ("-wal", "-shm", "-journal"))):
                if (capture / candidate).exists():
                    copy_new(capture / candidate, work / "sqlite_work" / candidate)
            signatures[relative] = sqlite_snapshot(working_db, stage / "payload/project" / relative)
        project = stage / "payload/project"
        git(project, "fsck", "--full")
        (stage / "git").mkdir()
        git(project, "bundle", "create", str(stage / "git/repository.bundle"), "--all")
        write_new(stage / "metadata/capture.json", json_bytes(plan | {
            "dry_run": False, "validation_limits": None,
            "captured_at_utc": datetime.now(timezone.utc).isoformat(),
            "tool_versions": {"python": sys.version, "sqlite": sqlite3.sqlite_version,
                              "git": git(project, "--version").strip()},
            "sqlite_method": "backup API from isolated capture; raw originals/sidecars in raw_sqlite",
            "sqlite_signatures": signatures,
        }))
        manifest = {"schema": SCHEMA, "source": initial,
                    "files": artifact_manifest(stage),
                    "directories": sorted(p.relative_to(stage).as_posix() for p in stage.rglob("*") if p.is_dir())}
        manifest_data = json_bytes(manifest)
        write_new(stage / "metadata/manifest.json", manifest_data)
        manifest_hash = sha256(stage / "metadata/manifest.json")
        write_new(stage / "metadata/manifest.sha256", (manifest_hash + "  manifest.json\n").encode())
        # Revalidate mapping immediately before writing to the share.
        validate_destination(source, destination, expected_share, probe)
        target.mkdir(exist_ok=False)
        for directory in sorted(p for p in stage.rglob("*") if p.is_dir()):
            (target / directory.relative_to(stage)).mkdir(parents=True, exist_ok=False)
        for path in sorted(p for p in stage.rglob("*") if p.is_file()):
            copy_new(path, target / path.relative_to(stage))
        if (target / "metadata/manifest.json").read_bytes() != manifest_data:
            raise BackupError("Destination manifest mismatch")
        if sha256(target / "metadata/manifest.json") != manifest_hash:
            raise BackupError("Destination manifest checksum mismatch")
        if (target / "metadata/manifest.sha256").read_bytes() != (stage / "metadata/manifest.sha256").read_bytes():
            raise BackupError("Destination checksum file mismatch")
        with tempfile.TemporaryDirectory(prefix="musicstewardship-restore-") as restored:
            report = verify_restore(target, manifest, Path(restored), signatures)
        write_new(target / "metadata/verification.json", json_bytes(report))
        if json.loads((target / "metadata/verification.json").read_text(encoding="utf-8")) != report:
            raise BackupError("Destination verification report mismatch")
        validate_destination(source, destination, expected_share, probe)
        if inventory(source) != initial:
            raise BackupError("Source changed before completion; backup remains incomplete")
        complete = {"schema": SCHEMA, "head": initial["head"], "manifest_sha256": manifest_hash,
                    "verification_sha256": sha256(target / "metadata/verification.json"),
                    "completed_at_utc": datetime.now(timezone.utc).isoformat()}
        write_new(target / "COMPLETE.json", json_bytes(complete))
        if json.loads((target / "COMPLETE.json").read_text(encoding="utf-8")) != complete:
            raise BackupError("Completion marker could not be verified")
        return {"backup": str(target), **report, "complete": True}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--expected-share", required=True, help=r"Architect-confirmed \\server\share for Z:")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--quiesced", action="store_true", help="Confirm all project/Git/database writers are stopped")
    args = parser.parse_args()
    try:
        result = run_backup(args.source, Path("Z:/"), args.expected_share,
                            dry_run=args.dry_run, quiesced=args.quiesced)
    except (BackupError, OSError, sqlite3.Error) as exc:
        parser.exit(1, f"Backup failed; existing backups/source were not overwritten: {exc}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
