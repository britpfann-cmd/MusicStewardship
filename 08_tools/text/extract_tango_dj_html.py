#!/usr/bin/env python3
"""
Extract TANGO-DJ/TTT recording rows from saved HTML snapshots.

Uses only Python standard-library modules. No BeautifulSoup or other
third-party packages are required.

Usage:
    python extract_tango_dj_html.py OUTPUT_CSV INPUT1.html [INPUT2.html ...]

The input HTML files are preserved as source snapshots. Every extracted row
retains the source snapshot filename.
"""

from __future__ import annotations

import argparse
import csv
import re
from html.parser import HTMLParser
from pathlib import Path


# Actual TANGO-DJ table column order in the saved page.
FIELD_NAMES = [
    "favorite",
    "cue",
    "cover",
    "lyrics",
    "instrumental",
    "media",
    "track_number",
    "title",
    "genre",
    "artist",
    "recording_date",
    "length",
    "rating",
    "dj",
    "album",
    "publisher",
    "release_date",
    "composer",
    "author",
    "catalog_number",
    "matrix_number",
    "comment",
    "track_modified",
    "feedback",
]

OUTPUT_FIELDS = [
    "snapshot_file",
    "tango_dj_ref",
    "instrumental",
    "media",
    "track_number",
    "title",
    "genre",
    "artist",
    "recording_date",
    "length",
    "rating",
    "dj",
    "album",
    "publisher",
    "release_date",
    "composer",
    "author",
    "catalog_number",
    "matrix_number",
    "comment",
    "track_modified",
    "has_lyrics",
]


class RecordingTableParser(HTMLParser):
    """Parse only rows from table id='searchresult'."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_target_table = False
        self.table_depth = 0
        self.in_row = False
        self.row_cells: list[str] = []
        self.current_cell: list[str] | None = None
        self.rows: list[list[str]] = []
        self.current_row_ref = ""
        self.in_link = False
        self.current_link_href = ""

    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)

        if tag == "table" and attr.get("id") == "searchresult":
            self.in_target_table = True
            self.table_depth = 1
            return

        if not self.in_target_table:
            return

        if tag == "table":
            self.table_depth += 1
            return

        if tag == "tr":
            if self.in_row:
                self._finish_row()
            self.in_row = True
            self.row_cells = []
            self.current_cell = None
            self.current_row_ref = ""
            return

        if tag == "td" and self.in_row:
            self.current_cell = []
            return

        if tag == "a" and self.current_cell is not None:
            self.in_link = True
            self.current_link_href = attr.get("href", "")
            return

    def handle_endtag(self, tag):
        if not self.in_target_table:
            return

        if tag == "td" and self.in_row and self.current_cell is not None:
            value = " ".join(
                "".join(self.current_cell).split()
            ).strip()
            self.row_cells.append(value)
            self.current_cell = None
            return

        if tag == "tr" and self.in_row:
            self._finish_row()
            return

        if tag == "a":
            self.in_link = False
            self.current_link_href = ""
            return

        if tag == "table":
            self.table_depth -= 1
            if self.table_depth == 0:
                self.in_target_table = False

    def handle_data(self, data):
        if self.current_cell is not None:
            self.current_cell.append(data)

    def _finish_row(self):
        if len(self.row_cells) == len(FIELD_NAMES):
            self.rows.append(self.row_cells[:])
        self.in_row = False
        self.row_cells = []
        self.current_cell = None


def extract_ref_from_html(text: str) -> list[str]:
    return re.findall(r"[?&]ref=(\d+)", text)


def parse_html(path: Path) -> list[dict[str, str]]:
    text = path.read_text(
        encoding="utf-8-sig",
        errors="replace",
    )

    parser = RecordingTableParser()
    parser.feed(text)
    parser.close()

    if not parser.rows:
        raise ValueError(
            f"No 24-column recording rows found in {path}"
        )

    refs = extract_ref_from_html(text)

    records = []

    # Ref links occur once per recording row in the saved TANGO-DJ table.
    # Use the ref sequence as a row-aligned fallback when available.
    ref_index = 0

    for cells in parser.rows:
        values = dict(zip(FIELD_NAMES, cells))

        ref = ""
        while ref_index < len(refs):
            ref = refs[ref_index]
            ref_index += 1
            # The first ref after a table row is the recording's ref link.
            # In TANGO-DJ rows it is the feedback URL.
            if ref:
                break

        records.append({
            "snapshot_file": path.name,
            "tango_dj_ref": ref,
            "instrumental": (
                "YES" if values["instrumental"] else "NO"
            ),
            "media": values["media"],
            "track_number": values["track_number"],
            "title": values["title"],
            "genre": values["genre"],
            "artist": values["artist"],
            "recording_date": values["recording_date"],
            "length": values["length"],
            "rating": values["rating"],
            "dj": values["dj"],
            "album": values["album"],
            "publisher": values["publisher"],
            "release_date": values["release_date"],
            "composer": values["composer"],
            "author": values["author"],
            "catalog_number": values["catalog_number"],
            "matrix_number": values["matrix_number"],
            "comment": values["comment"],
            "track_modified": values["track_modified"],
            "has_lyrics": (
                "YES" if values["lyrics"] else "NO"
            ),
        })

    return records


def track_sort_key(value: str):
    text = (value or "").strip()
    match = re.search(r"\d+", text)
    if match:
        return (int(match.group()), text)
    return (999999, text)


def sort_key(row: dict[str, str]):
    return (
        row["album"].casefold(),
        track_sort_key(row["track_number"]),
        row["title"].casefold(),
        row["tango_dj_ref"],
    )


def combine(inputs: list[Path]) -> list[dict[str, str]]:
    rows = []

    for path in inputs:
        parsed = parse_html(path)
        print(f"{path.name}: {len(parsed)} recording rows")
        rows.extend(parsed)

    # Exact duplicate suppression is deliberately conservative.
    # Rows from different dated snapshots are retained.
    seen = set()
    unique = []

    for row in rows:
        key = (
            row["snapshot_file"],
            row["tango_dj_ref"],
            row["album"],
            row["track_number"],
            row["title"],
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(row)

    unique.sort(key=sort_key)
    return unique


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output_csv", type=Path)
    parser.add_argument("inputs", nargs="+", type=Path)
    args = parser.parse_args()

    for path in args.inputs:
        if not path.is_file():
            parser.error(f"Input not found: {path}")

    rows = combine(args.inputs)

    args.output_csv.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with args.output_csv.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=OUTPUT_FIELDS,
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Combined rows: {len(rows)}")
    print(f"CSV written: {args.output_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
