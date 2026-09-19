#!/usr/bin/env python3
"""
MusicStewardship source-tree scanner.

Non-destructively inventories the complete supplied source tree:
- the supplied root
- every directory entry, including empty directories
- every file entry

The scanner preserves observed names and relative paths. It does not
normalize filename text or assign musical meaning.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path

RECOGNIZED_AUDIO_EXTENSIONS = {
    # Lossless / uncompressed
    ".flac", ".wav", ".aif", ".aiff", ".alac", ".ape", ".wv",
    ".tta", ".caf", ".dsf", ".dff", ".sd2",

    # Lossy / compressed
    ".mp3", ".m4a", ".mp4", ".aac", ".ogg", ".opus", ".wma",
}

OUTPUT_FIELDS = [
    "source_id",
    "source_root",
    "relative_path",
    "filename",
    "extension",
    "source_object_type",
    "artifact_reason",
    "top_level_collection",
    "directory_path",
    "directory_depth",
    "file_stem",
    "file_size",
    "file_mtime_ns",
    "source_object_id",
    "metadata_status",
]


def stable_object_id(source_id: str, relative_path: str) -> str:
    value = f"{source_id}|{relative_path}".encode("utf-8")
    return hashlib.sha256(value).hexdigest()[:24]


def classify_file(path: Path) -> tuple[str, str]:
    name = path.name
    parts = {part.lower() for part in path.parts}

    if name.startswith("._"):
        return "SOURCE_ARTIFACT", "APPLEDOUBLE"

    if "__macosx" in parts:
        return "SOURCE_ARTIFACT", "MACOSX_DIRECTORY"

    if path.suffix.lower() in RECOGNIZED_AUDIO_EXTENSIONS:
        return "AUDIO", ""

    if path.suffix.lower() in {".csv", ".tsv", ".xlsx", ".xls", ".ods"}:
        return "CATALOG_DATA", ""

    if path.suffix.lower() in {
        ".pdf", ".txt", ".md", ".rtf", ".doc", ".docx"
    }:
        return "DOCUMENTATION", ""

    if path.suffix.lower() in {
        ".jpg", ".jpeg", ".png", ".gif", ".webp", ".tif", ".tiff", ".bmp"
    }:
        return "GRAPHIC", ""

    return "OTHER_SOURCE_FILE", ""


def directory_record(root: Path, path: Path, source_id: str) -> dict[str, str]:
    relative = path.relative_to(root)
    relative_text = str(relative) if str(relative) != "." else ""
    parts = relative.parts

    parent = str(relative.parent) if str(relative.parent) != "." else ""
    depth = len(parts)

    return {
        "source_id": source_id,
        "source_root": str(root),
        "relative_path": relative_text,
        "filename": path.name if relative_text else root.name,
        "extension": "",
        "source_object_type": "DIRECTORY",
        "artifact_reason": "",
        "top_level_collection": parts[0] if parts else "",
        "directory_path": parent,
        "directory_depth": str(max(depth - 1, 0)),
        "file_stem": "",
        "file_size": "",
        "file_mtime_ns": str(path.stat().st_mtime_ns),
        "source_object_id": stable_object_id(source_id, relative_text),
        "metadata_status": "NOT_APPLICABLE",
    }


def file_record(root: Path, path: Path, source_id: str) -> dict[str, str]:
    relative = path.relative_to(root)
    relative_text = str(relative)
    object_type, artifact_reason = classify_file(path)
    parts = relative.parts
    directory_path = (
        str(relative.parent)
        if str(relative.parent) != "."
        else ""
    )

    stat = path.stat()

    return {
        "source_id": source_id,
        "source_root": str(root),
        "relative_path": relative_text,
        "filename": path.name,
        "extension": path.suffix.lower(),
        "source_object_type": object_type,
        "artifact_reason": artifact_reason,
        "top_level_collection": parts[0] if parts else "",
        "directory_path": directory_path,
        "directory_depth": str(len(parts) - 1),
        "file_stem": path.stem,
        "file_size": str(stat.st_size),
        "file_mtime_ns": str(stat.st_mtime_ns),
        "source_object_id": stable_object_id(source_id, relative_text),
        "metadata_status": "NOT_YET_READ",
    }


def discover(root: str | Path, source_id: str) -> list[dict[str, str]]:
    root = Path(root).resolve()

    if not root.exists():
        raise FileNotFoundError(f"Source root does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Source root is not a directory: {root}")

    records: list[dict[str, str]] = []

    # The supplied root is itself a source-tree node.
    records.append(directory_record(root, root, source_id))

    # Record directories explicitly. This preserves empty directories and
    # avoids reconstructing hierarchy later from file paths.
    directories = sorted(
        (p for p in root.rglob("*") if p.is_dir()),
        key=lambda p: (str(p.relative_to(root)).casefold(),
                       str(p.relative_to(root))),
    )

    for path in directories:
        records.append(directory_record(root, path, source_id))

    files = sorted(
        (p for p in root.rglob("*") if p.is_file()),
        key=lambda p: (str(p.relative_to(root)).casefold(),
                       str(p.relative_to(root))),
    )

    for path in files:
        records.append(file_record(root, path, source_id))

    return records


def write_csv(records: list[dict[str, str]], output: str | Path) -> None:
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(records)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Non-destructively inventory every entry in a supplied source tree."
    )
    parser.add_argument("root")
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    records = discover(args.root, args.source_id)
    write_csv(records, args.output)

    counts: dict[str, int] = {}
    for record in records:
        kind = record["source_object_type"]
        counts[kind] = counts.get(kind, 0) + 1

    print(f"Source objects: {len(records)}")
    for kind in sorted(counts):
        print(f"{kind}: {counts[kind]}")
    print(f"CSV written: {args.output}")


if __name__ == "__main__":
    main()
