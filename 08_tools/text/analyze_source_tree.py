#!/usr/bin/env python3
"""
Generic MusicStewardship source-tree analyzer.

Purpose
-------
Walk one or more source roots and capture directory hierarchy as source evidence.
The analyzer is deliberately descriptive: it does not assume that a particular
directory depth means orchestra, singer, release, etc.

For each directory it records:
- source identity and root
- relative path, parent path, depth
- directory/file counts
- representative filenames
- observed filename patterns
- candidate semantic roles based on conservative naming evidence

For each file it records its complete source-relative path and directory context.

This is an analysis/discovery stage. It does not modify source material.
"""

from __future__ import annotations

import argparse
import csv
import re
from collections import Counter, defaultdict
from pathlib import Path


AUDIO_EXTENSIONS = {
    ".flac", ".wav", ".mp3", ".m4a", ".alac",
    ".aiff", ".aif", ".caf", ".ogg", ".opus",
}

IGNORED_NAMES = {".DS_Store"}
IGNORED_PREFIXES = ("._",)

SEMANTIC_PATTERNS = [
    ("PRODUCT_OR_RELEASE", re.compile(
        r"(?i)\b(release|album|cd|vinyl|bandcamp|ttt|tango[\s_-]?time[\s_-]?travel|"
        r"tango[\s_-]?sparks|crackling[\s_-]?tunes|purchase|transfer)\b"
    )),
    ("ORCHESTRA_OR_ENSEMBLE", re.compile(
        r"(?i)\b(orquesta|tipica|típica|orchestra|ensemble|trio|trío|sextet|sexteto)\b"
    )),
    ("DJ_CATEGORY", re.compile(
        r"(?i)\b(tangos?|milongas?|vals(?:es)?|waltz|tango|music|musica|música|"
        r"cortinas?|dj|dance)\b"
    )),
    ("PERIOD", re.compile(
        r"(?i)\b(18\d{2}|19\d{2}|20\d{2}|early|late|golden|guardia|period)\b"
    )),
    ("CATALOG_OR_COLLECTION", re.compile(
        r"(?i)\b(catalog|catalogue|collection|coleccion|colección|archive|all|"
        r"restored|restoration|complete)\b"
    )),
]


def source_id_for(root: Path) -> str:
    return root.name or str(root)


def safe_rel(path: Path, root: Path) -> str:
    rel = path.relative_to(root)
    return "." if str(rel) == "." else rel.as_posix()


def visible_children(path: Path):
    try:
        for child in sorted(path.iterdir(), key=lambda p: p.name.casefold()):
            if child.name in IGNORED_NAMES or child.name.startswith(IGNORED_PREFIXES):
                continue
            yield child
    except (PermissionError, OSError):
        return


def filename_pattern(name: str) -> str:
    stem = Path(name).stem

    if re.match(r"^\s*\d+(?:\.\d+)?\s*[-.]?\s+.+$", stem):
        return "NUMBER_TITLE"
    if re.search(r"(?i)\b\d{3,6}(?:-\d+)?(?:_[A-Za-z0-9-]+)?$", stem):
        return "TITLE_IDENTIFIER"
    if "_" in stem:
        return "TITLE_UNDERSCORE_VARIANT"
    if " - " in stem:
        return "TITLE_DASH_VARIANT"
    return "TITLE_ONLY_OR_OTHER"


def semantic_candidates(name: str, child_names: list[str]) -> list[str]:
    candidates = []
    for role, pattern in SEMANTIC_PATTERNS:
        if pattern.search(name):
            candidates.append(role)

    # A directory containing many sequentially numbered files is likely
    # functioning as a track/release container, even if its name says little.
    numbered = sum(
        bool(re.match(r"^\s*\d+(?:\.\d+)?\s*[-.]?\s+", Path(n).stem))
        for n in child_names
    )
    if numbered >= 3:
        candidates.append("TRACK_CONTAINER")

    return list(dict.fromkeys(candidates))


def analyze_root(root: Path, source_id: str):
    directory_rows = []
    file_rows = []
    errors = []

    def walk(directory: Path):
        try:
            children = list(visible_children(directory))
        except Exception as exc:
            errors.append((safe_rel(directory, root), type(exc).__name__, str(exc)))
            return

        files = [p for p in children if p.is_file()]
        dirs = [p for p in children if p.is_dir()]

        rel = safe_rel(directory, root)
        depth = 0 if rel == "." else len(Path(rel).parts)
        names = [p.name for p in files]

        patterns = Counter(filename_pattern(n) for n in names)
        candidates = semantic_candidates(directory.name, names)

        directory_rows.append({
            "source_id": source_id,
            "source_root": str(root),
            "directory_path": rel,
            "parent_path": "." if rel == "." else safe_rel(directory.parent, root),
            "directory_name": directory.name,
            "depth": depth,
            "directory_count": len(dirs),
            "file_count": len(files),
            "audio_file_count": sum(p.suffix.casefold() in AUDIO_EXTENSIONS for p in files),
            "sample_filenames": " | ".join(names[:10]),
            "observed_filename_patterns": ";".join(
                f"{k}:{v}" for k, v in patterns.most_common()
            ),
            "semantic_role_candidates": ";".join(candidates),
            "analysis_status": "OK",
        })

        for f in files:
            file_rows.append({
                "source_id": source_id,
                "source_root": str(root),
                "relative_path": safe_rel(f, root),
                "directory_path": rel,
                "directory_depth": depth,
                "filename": f.name,
                "extension": f.suffix.casefold(),
                "is_audio": "YES" if f.suffix.casefold() in AUDIO_EXTENSIONS else "NO",
            })

        for d in dirs:
            walk(d)

    walk(root)
    return directory_rows, file_rows, errors


def write_csv(path: Path, rows: list[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Analyze one or more music source directory trees."
    )
    parser.add_argument(
        "roots", nargs="+", type=Path,
        help="one or more source roots; may ultimately be M:\\Music",
    )
    parser.add_argument(
        "--output-dir", type=Path, required=True,
        help="directory for tree analysis CSVs",
    )
    args = parser.parse_args()

    all_dirs = []
    all_files = []
    all_errors = []

    for root in args.roots:
        root = root.resolve()
        if not root.is_dir():
            print(f"ERROR: source root is not a directory: {root}")
            return 2

        sid = source_id_for(root)
        print(f"Analyzing source: {sid}")
        print(f"  Root: {root}")

        dirs, files, errors = analyze_root(root, sid)
        all_dirs.extend(dirs)
        all_files.extend(files)
        all_errors.extend(
            {"source_id": sid, "source_root": str(root),
             "relative_path": rel, "error_type": typ, "error": msg}
            for rel, typ, msg in errors
        )

        print(f"  Directories: {len(dirs)}")
        print(f"  Files:       {len(files)}")
        print(f"  Errors:      {len(errors)}")

    write_csv(args.output_dir / "source_tree_directories.csv", all_dirs)
    write_csv(args.output_dir / "source_tree_files.csv", all_files)
    write_csv(args.output_dir / "source_tree_errors.csv", all_errors)

    summary = []
    by_source = defaultdict(lambda: {"directories": 0, "files": 0, "audio": 0})
    for r in all_dirs:
        by_source[r["source_id"]]["directories"] += 1
    for r in all_files:
        by_source[r["source_id"]]["files"] += 1
        by_source[r["source_id"]]["audio"] += r["is_audio"] == "YES"

    for sid in sorted(by_source):
        x = by_source[sid]
        summary.append({
            "source_id": sid,
            "directories": x["directories"],
            "files": x["files"],
            "audio_files": x["audio"],
            "errors": sum(e["source_id"] == sid for e in all_errors),
        })

    write_csv(args.output_dir / "source_tree_summary.csv", summary)

    print()
    print("Tree analysis complete.")
    print(f"Sources:     {len(summary)}")
    print(f"Directories: {len(all_dirs)}")
    print(f"Files:       {len(all_files)}")
    print(f"Errors:      {len(all_errors)}")
    print(f"Output:      {args.output_dir}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
