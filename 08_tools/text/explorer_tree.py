#!/usr/bin/env python3
"""
MusicStewardship Explorer Tree parser.

Consumes the complete source-tree inventory produced by source_tree.py.

The scanner is responsible for observing the supplied tree. This parser
represents that observation. It does not reconstruct missing directories
from file paths, normalize names, or assign musical meaning.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path, PurePosixPath


OUTPUT_FIELDS = [
    "source_root",
    "relative_path",
    "parent_relative_path",
    "name",
    "entry_type",
    "depth",
    "ancestor_path",
]


def path_parts(relative_path: str) -> tuple[str, ...]:
    if not relative_path:
        return ()
    return PurePosixPath(relative_path.replace("\\", "/")).parts


def parent_of(relative_path: str) -> str:
    parts = path_parts(relative_path)
    return "/".join(parts[:-1])


def depth_of(relative_path: str) -> int:
    return len(path_parts(relative_path))


def ancestor_path_of(relative_path: str) -> str:
    parts = path_parts(relative_path)
    return "/".join(parts[:-1])


def build_tree(scanner_csv: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    source_roots: set[str] = set()
    seen_paths: set[tuple[str, str]] = set()

    with scanner_csv.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        if not reader.fieldnames:
            raise ValueError("Scanner CSV has no header.")

        required = {
            "source_root",
            "relative_path",
            "source_object_type",
        }
        missing = required - set(reader.fieldnames)
        if missing:
            raise ValueError(
                "Scanner CSV is missing required fields: "
                + ", ".join(sorted(missing))
            )

        for row in reader:
            source_root = row["source_root"]
            relative_path = row["relative_path"].replace("\\", "/")
            entry_type = row["source_object_type"]

            source_roots.add(source_root)

            key = (source_root, relative_path)
            if key in seen_paths:
                raise ValueError(
                    f"Duplicate source-tree entry: {source_root} | {relative_path}"
                )
            seen_paths.add(key)

            if relative_path:
                name = row.get("filename") or PurePosixPath(relative_path).name
            else:
                name = row.get("filename") or Path(source_root).name

            rows.append(
                {
                    "source_root": source_root,
                    "relative_path": relative_path,
                    "parent_relative_path": parent_of(relative_path),
                    "name": name,
                    "entry_type": entry_type,
                    "depth": str(depth_of(relative_path)),
                    "ancestor_path": ancestor_path_of(relative_path),
                }
            )

    if len(source_roots) != 1:
        raise ValueError(
            "Input must contain exactly one supplied source_root; found: "
            + ", ".join(sorted(source_roots))
        )

    rows.sort(
        key=lambda r: (
            r["relative_path"].casefold(),
            r["relative_path"],
            r["entry_type"],
        )
    )
    return rows


def write_csv(rows: list[dict[str, str]], output_csv: Path) -> None:
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    with output_csv.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build an Explorer Tree from a complete source-tree inventory."
    )
    parser.add_argument("scanner_csv", type=Path)
    parser.add_argument("output_csv", type=Path)
    args = parser.parse_args()

    rows = build_tree(args.scanner_csv)
    write_csv(rows, args.output_csv)

    print(f"Explorer Tree nodes: {len(rows)}")
    print(f"CSV written: {args.output_csv}")


if __name__ == "__main__":
    main()
