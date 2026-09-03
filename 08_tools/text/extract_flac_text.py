#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MusicStewardship Crackling Tunes text extraction v2

Reads audio-file metadata from a directory tree and emits one row for
each selected text-bearing field.

Important v2 behavior:
    If CATALOG # is absent from embedded metadata, recover the Crackling
    Tunes CT identifier from the filename.

Example:
    [CT2302-A1] -> CT2302-A1
    (CT2302-B1) -> CT2302-B1

The source file itself is never modified.
"""

import argparse
import csv
import re
import subprocess
from pathlib import Path


TEXT_FIELDS = (
    "ARTIST",
    "ALBUMARTIST",
    "COMPOSER",
    "TITLE",
)

CATALOG_FIELD = "CATALOG #"

AUDIO_EXTENSIONS = {
    ".flac",
    ".m4a",
    ".mp3",
    ".wav",
    ".aac",
    ".alac",
    ".ogg",
    ".opus",
    ".wma",
}

CSV_COLUMNS = [
    "source_release",
    "source_path",
    "source_file",
    "audio_format",
    "catalog_number",
    "field_name",
    "original_text",
]


def detect_audio_format(path: Path) -> str:
    """Use the file extension as the initial format label."""
    return path.suffix.lower().lstrip(".").upper() or "UNKNOWN"


def extract_catalog_from_filename(name: str) -> str:
    """
    Recover a Crackling Tunes catalog identifier from a filename.

    Accept examples such as:
        [CT2302-A1]
        (CT2302-B1)
        CT2302-A1
        [CT21001-A2]

    The CT identifier is returned exactly as represented except that
    surrounding whitespace is removed and the CT prefix is uppercased.
    """
    if not name:
        return ""

    # Require the Crackling Tunes CT prefix and the source-side/take
    # suffix. This intentionally avoids guessing unrelated numbers.
    match = re.search(
        r"\b(CT\d{4,5}-[AB]\d+)\b",
        name,
        flags=re.IGNORECASE,
    )

    if not match:
        return ""

    value = match.group(1).upper()

    return value


def read_flac_tags(path: Path) -> dict[str, str]:
    """Read FLAC Vorbis comments using metaflac."""
    result = subprocess.run(
        [
            "metaflac",
            "--export-tags-to=-",
            str(path),
        ],
        capture_output=True,
        check=True,
    )

    tags: dict[str, str] = {}

    for raw_line in result.stdout.splitlines():
        line = raw_line.decode(
            "utf-8",
            errors="replace",
        )

        if "=" not in line:
            continue

        key, value = line.split("=", 1)

        if key not in tags:
            tags[key] = value

    return tags


def read_generic_tags(path: Path) -> dict[str, str]:
    """
    Read tags from non-FLAC audio using ffprobe.

    The extractor remains read-only.
    """
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format_tags",
            "-of",
            "default=noprint_wrappers=1",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    tags: dict[str, str] = {}

    for line in result.stdout.splitlines():
        if "=" not in line:
            continue

        key, value = line.split("=", 1)

        if key not in tags:
            tags[key] = value

    return tags


def read_tags(path: Path) -> dict[str, str]:
    """Use the appropriate metadata reader."""
    if path.suffix.lower() == ".flac":
        return read_flac_tags(path)

    return read_generic_tags(path)


def find_audio_files(input_path: Path) -> list[Path]:
    """
    Accept either:
        a directory containing releases, or
        a single release directory.
    """
    if input_path.is_file():
        return [input_path]

    files = []

    for path in sorted(
        input_path.rglob("*")
    ):
        if not path.is_file():
            continue

        if path.suffix.lower() in AUDIO_EXTENSIONS:
            files.append(path)

    return files


def infer_release(
    path: Path,
    root: Path,
) -> str:
    """
    Prefer the immediate release-directory name.

    For a file:
        root / 24.04 Releases / filename
    returns:
        24.04 Releases
    """
    try:
        relative = path.relative_to(root)
    except ValueError:
        return ""

    if len(relative.parts) >= 2:
        return relative.parts[0]

    return root.name


def extract_file(
    path: Path,
    root: Path,
) -> list[dict[str, str]]:
    """Extract selected fields for one audio file."""
    tags = read_tags(path)

    metadata_catalog = (
        tags.get(CATALOG_FIELD, "").strip()
    )

    filename_catalog = extract_catalog_from_filename(
        path.name
    )

    # Metadata remains authoritative when present.
    catalog_number = (
        metadata_catalog
        or filename_catalog
    )

    source_release = infer_release(
        path,
        root,
    )

    rows = []

    for field_name in TEXT_FIELDS:
        rows.append(
            {
                "source_release": source_release,
                "source_path": str(
                    path.relative_to(root)
                ).replace("\\", "/"),
                "source_file": path.name,
                "audio_format": detect_audio_format(
                    path
                ),
                "catalog_number": catalog_number,
                "field_name": field_name,
                "original_text": tags.get(
                    field_name,
                    "",
                ),
            }
        )

    return rows


def extract_directory(
    input_path: Path,
) -> tuple[
    list[dict[str, str]],
    int,
    int,
]:
    """
    Return:
        rows,
        audio_files_examined,
        metadata_failures
    """
    root = (
        input_path
        if input_path.is_dir()
        else input_path.parent
    )

    files = find_audio_files(
        input_path
    )

    rows = []
    failures = 0

    for path in files:
        try:
            rows.extend(
                extract_file(
                    path,
                    root,
                )
            )
        except subprocess.CalledProcessError:
            failures += 1

    return (
        rows,
        len(files),
        failures,
    )


def write_csv(
    rows: list[dict[str, str]],
    output_path: Path,
) -> None:
    """Write UTF-8 CSV."""
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=CSV_COLUMNS,
        )

        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Extract Crackling Tunes audio metadata into CSV. "
            "Falls back to CT identifiers found in filenames when "
            "CATALOG # is absent from embedded metadata."
        )
    )

    parser.add_argument(
        "input",
        type=Path,
        help="release directory or Crackling Tunes root",
    )

    parser.add_argument(
        "output",
        type=Path,
        help="output CSV file",
    )

    args = parser.parse_args()

    if not args.input.exists():
        parser.error(
            f"Input does not exist: {args.input}"
        )

    rows, audio_count, failures = (
        extract_directory(
            args.input
        )
    )

    write_csv(
        rows,
        args.output
    )

    print(
        f"Audio files examined: {audio_count}"
    )
    print(
        f"Metadata extraction failures: {failures}"
    )
    print(
        f"Extracted {len(rows)} text records."
    )
    print(
        f"CSV written: {args.output}"
    )

    # Report how many distinct source files received a catalog number.
    source_catalogs = {
        (
            row["source_file"],
            row["catalog_number"],
        )
        for row in rows
    }

    with_catalog = sum(
        bool(catalog)
        for _, catalog in source_catalogs
    )

    print(
        f"Source files with catalog number: "
        f"{with_catalog}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
