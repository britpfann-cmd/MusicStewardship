"""Preservation tests: only disposable repositories and mock NAS directories."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sqlite3
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "research_backup_test_module", ROOT / "08_tools/maintenance/research_backup.py"
)
backup = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(backup)
SHARE = r"\\mock-synology\research"


def git(root, *args):
    return subprocess.run(
        ["git", "-c", "core.hooksPath=", "-c", "user.name=Backup Test",
         "-c", "user.email=backup-test@example.invalid", "-C", str(root), *args],
        check=True, capture_output=True, text=True,
    )


def fingerprint(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file()}


@pytest.fixture
def project(tmp_path):
    source = tmp_path / "project"
    source.mkdir()
    git(source, "init", "-b", "master")
    (source / ".gitignore").write_text("99_sandbox/\n06_runtime/\n_from_chat/\n", encoding="utf-8")
    (source / "README.md").write_text("Original evidence\n", encoding="utf-8")
    git(source, "add", ".")
    git(source, "commit", "-m", "Fixture baseline")
    git(source, "tag", "baseline")
    for name in ("99_sandbox", "06_runtime", "_from_chat", "_to_chat", "empty"):
        (source / name).mkdir()
    (source / "99_sandbox/évidence.txt").write_text("Unique research", encoding="utf-8")
    (source / "06_runtime/processing_log.csv").write_text("run_id\nORIGINAL\n", encoding="utf-8")
    (source / "_from_chat/package.zip").write_bytes(b"original transfer package")
    connection = sqlite3.connect(source / "99_sandbox/catalog.db")
    connection.execute("CREATE TABLE observations (value TEXT)")
    connection.execute("INSERT INTO observations VALUES ('original observation')")
    connection.commit()
    connection.close()
    destination = tmp_path / "mock_nas"
    destination.mkdir()
    return source, destination


def run(project, **kwargs):
    source, destination = project
    return backup.run_backup(source, destination, SHARE, probe=lambda _: SHARE, **kwargs)


def test_dry_run_is_read_only_and_inventories_ignored_data(project):
    source, destination = project
    before = fingerprint(source)
    result = run(project, dry_run=True)
    paths = {f["path"] for f in result["inventory"]["files"]}
    assert "99_sandbox/catalog.db" in paths
    assert "06_runtime/processing_log.csv" in paths
    assert "_from_chat/package.zip" in paths
    assert result["sqlite_count"] == 1
    assert fingerprint(source) == before
    assert list(destination.iterdir()) == []


def test_caches_excluded_but_tracked_files_preserved(project):
    source, _ = project
    for directory in (".venv", "__pycache__", ".pytest_cache"):
        (source / directory).mkdir()
        (source / directory / "discard.txt").write_text("Disposable", encoding="utf-8")
    (source / ".venv/pyvenv.cfg").write_text("home = fixture\n", encoding="utf-8")
    (source / "env").mkdir()
    (source / "env/research.txt").write_text("Not a virtual environment", encoding="utf-8")
    (source / "historical.bak").write_text("Keep backup copies", encoding="utf-8")
    (source / "untracked.pyc").write_bytes(b"bytecode")
    git(source, "add", "-f", "__pycache__/discard.txt")
    paths = {f["path"] for f in run(project, dry_run=True)["inventory"]["files"]}
    assert "__pycache__/discard.txt" in paths
    assert ".venv/discard.txt" not in paths
    assert ".pytest_cache/discard.txt" not in paths
    assert "untracked.pyc" not in paths
    assert "historical.bak" in paths
    assert "env/research.txt" in paths


def test_full_backup_restores_git_sqlite_and_original_names(project):
    source, destination = project
    before = fingerprint(source)
    result = run(project, quiesced=True, backup_name="MusicStewardship_test")
    target = destination / "MusicStewardship_test"
    assert result["complete"]
    assert result["sqlite_verified"] == 1
    assert result["bundle_restore"] == "passed"
    assert target.parent == destination
    assert (target / "payload/project/empty").is_dir()
    assert (target / "payload/project/99_sandbox/évidence.txt").read_text(encoding="utf-8") == "Unique research"
    assert (target / "raw_sqlite/99_sandbox/catalog.db").read_bytes() == (source / "99_sandbox/catalog.db").read_bytes()
    complete = json.loads((target / "COMPLETE.json").read_text())
    assert complete["manifest_sha256"] == backup.sha256(target / "metadata/manifest.json")
    assert complete["verification_sha256"] == backup.sha256(target / "metadata/verification.json")
    manifest = json.loads((target / "metadata/manifest.json").read_text(encoding="utf-8"))
    backup.verify_files(target, manifest["files"])
    assert fingerprint(source) == before


def test_wal_database_uses_backup_api_without_touching_original(project):
    source, _ = project
    connection = sqlite3.connect(source / "99_sandbox/wal.db")
    try:
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA wal_autocheckpoint=0")
        connection.execute("CREATE TABLE evidence (value TEXT)")
        connection.execute("INSERT INTO evidence VALUES ('committed in WAL')")
        connection.commit()
        before = fingerprint(source)
        result = run(project, quiesced=True)
        target = Path(result["backup"])
        restored = target / "payload/project/99_sandbox/wal.db"
        assert backup.database_signature(restored)["table_counts"] == {"evidence": 1}
        assert not restored.with_name("wal.db-wal").exists()
        assert (target / "raw_sqlite/99_sandbox/wal.db-wal").exists()
        assert fingerprint(source) == before
    finally:
        connection.close()


def test_wrong_share_refuses_before_writing(project):
    source, destination = project
    with pytest.raises(backup.BackupError, match="mapping"):
        backup.run_backup(source, destination, SHARE, probe=lambda _: r"\\wrong\share", quiesced=True)
    assert list(destination.iterdir()) == []


@pytest.mark.parametrize("share", ["Z:", r"\\server", r"\\server\share\subfolder", r"\\server\.."])
def test_expected_share_must_be_explicit_unc_root(share):
    with pytest.raises(backup.BackupError):
        backup.canonical_share(share)


def test_requires_quiescence_confirmation(project):
    with pytest.raises(backup.BackupError, match="quiesced"):
        run(project)
    assert list(project[1].iterdir()) == []


def test_existing_backup_never_overwritten_or_deleted(project):
    _, destination = project
    existing = destination / "MusicStewardship_existing"
    existing.mkdir()
    (existing / "precious.txt").write_text("Do not overwrite", encoding="utf-8")
    before = fingerprint(existing)
    with pytest.raises(FileExistsError):
        run(project, quiesced=True, backup_name=existing.name)
    assert fingerprint(existing) == before
    assert not (existing / "COMPLETE.json").exists()


def test_successive_backups_are_independent_and_preserve_first(project):
    first = Path(run(project, quiesced=True)["backup"])
    before = fingerprint(first)
    second = Path(run(project, quiesced=True)["backup"])
    assert first != second
    assert first.parent == second.parent == project[1]
    assert fingerprint(first) == before
    assert (second / "COMPLETE.json").exists()


def test_corrupt_sqlite_aborts_without_publishing(project):
    (project[0] / "99_sandbox/corrupt.db").write_bytes(backup.SQLITE_HEADER + b"invalid database")
    with pytest.raises(sqlite3.DatabaseError):
        run(project, quiesced=True)
    assert list(project[1].iterdir()) == []


def test_restore_failure_leaves_incomplete_backup(project, monkeypatch):
    def fail(*args):
        raise backup.BackupError("Restoration failed")
    monkeypatch.setattr(backup, "verify_restore", fail)
    with pytest.raises(backup.BackupError, match="Restoration failed"):
        run(project, quiesced=True, backup_name="MusicStewardship_failed")
    target = project[1] / "MusicStewardship_failed"
    assert target.is_dir()
    assert not (target / "COMPLETE.json").exists()


def test_destination_corruption_detected_before_completion(project, monkeypatch):
    original = backup.copy_new
    def corrupt(source, destination):
        original(source, destination)
        if destination == project[1] / "MusicStewardship_corrupt/payload/project/README.md":
            destination.write_bytes(b"corrupted transfer")
    monkeypatch.setattr(backup, "copy_new", corrupt)
    with pytest.raises(backup.BackupError, match="verification failed"):
        run(project, quiesced=True, backup_name="MusicStewardship_corrupt")
    assert not (project[1] / "MusicStewardship_corrupt/COMPLETE.json").exists()


def test_source_change_aborts_before_publishing(project, monkeypatch):
    original = backup.inventory
    calls = 0
    def changed(source):
        nonlocal calls
        calls += 1
        result = original(source)
        if calls > 1:
            result["status"] += "simulated concurrent change"
        return result
    monkeypatch.setattr(backup, "inventory", changed)
    with pytest.raises(backup.BackupError, match="Source changed"):
        run(project, quiesced=True)
    assert list(project[1].iterdir()) == []


def test_git_lock_refuses_capture(project):
    (project[0] / ".git/index.lock").write_bytes(b"")
    with pytest.raises(backup.BackupError, match="Git lock"):
        run(project, dry_run=True)


def test_mapping_rechecked_before_publication(project):
    source, destination = project
    mappings = iter([SHARE, r"\\different\share"])
    with pytest.raises(backup.BackupError, match="mapping"):
        backup.run_backup(source, destination, SHARE, quiesced=True, probe=lambda _: next(mappings))
    assert list(destination.iterdir()) == []


def test_missing_destination_is_not_created(project):
    source, destination = project
    missing = destination / "absent"
    with pytest.raises(backup.BackupError, match="not accessible"):
        backup.run_backup(source, missing, SHARE, dry_run=True, probe=lambda _: SHARE)
    assert not missing.exists()


def test_destination_inside_source_is_rejected(project):
    with pytest.raises(backup.BackupError, match="separate"):
        backup.run_backup(project[0], project[0] / "99_sandbox", SHARE,
                          dry_run=True, probe=lambda _: SHARE)
