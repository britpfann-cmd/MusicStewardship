#!/usr/bin/env python3
"""
Compare TTT embedded FLAC metadata with the TANGO-DJ TTT reference snapshot.

The TTT file is the primary source for MusicStewardship ingestion.
The TANGO-DJ record is an independent authentication/reference assertion.

Inputs:
  1. TTT_test_metadata.csv  - produced by probe_ttt_test_set.py
  2. TTT_TANGO-DJ_2026-08-28.csv - extracted TANGO-DJ snapshot

Output:
  TTT_tags_vs_reference_v2.csv

This version fixes the prior comparison bug by retaining the actual TTT
TAG:* values in the comparison output.
"""

from __future__ import annotations

import argparse
import csv
import re
import unicodedata
from collections import defaultdict
from pathlib import Path


def norm(value: str) -> str:
    if not value:
        return ""
    value = unicodedata.normalize("NFKC", value)
    value = value.casefold()
    value = re.sub(r"\s+", " ", value).strip()
    return value


def tag(row: dict[str, str], name: str) -> str:
    return row.get(f"TAG:{name}", "")


def track_norm(value: str) -> str:
    s = norm(value)
    m = re.search(r"\d+", s)
    return str(int(m.group())) if m else s


def build_index(rows, key_fn):
    idx = defaultdict(list)
    for i, row in enumerate(rows):
        key = key_fn(row)
        if key:
            idx[key].append(i)
    return idx


def compare(source: str, reference: str) -> str:
    if not source and not reference:
        return "BOTH_MISSING"
    if not source or not reference:
        return "ONE_SIDE_MISSING"
    return "AGREE" if norm(source) == norm(reference) else "DISAGREE"


def pick_reference(meta, by_album_track, by_album_title, by_title_date, reference):
    album = tag(meta, "ALBUM")
    title = tag(meta, "TITLE")
    track = tag(meta, "track")
    date = tag(meta, "DATE")

    key = (norm(album), track_norm(track))
    candidates = by_album_track.get(key, [])
    if len(candidates) == 1:
        return candidates[0], "ALBUM_TRACK"
    if len(candidates) > 1:
        return candidates, "ALBUM_TRACK_AMBIGUOUS"

    key = (norm(album), norm(title))
    candidates = by_album_title.get(key, [])
    if len(candidates) == 1:
        return candidates[0], "ALBUM_TITLE"
    if len(candidates) > 1:
        return candidates, "ALBUM_TITLE_AMBIGUOUS"

    key = (norm(title), norm(date))
    candidates = by_title_date.get(key, [])
    if len(candidates) == 1:
        return candidates[0], "TITLE_DATE"
    if len(candidates) > 1:
        return candidates, "TITLE_DATE_AMBIGUOUS"

    return None, "NO_MATCH"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("metadata_csv", type=Path)
    parser.add_argument("reference_csv", type=Path)
    parser.add_argument("output_csv", type=Path)
    args = parser.parse_args()

    with args.metadata_csv.open(
        "r", encoding="utf-8-sig", newline=""
    ) as f:
        metadata = list(csv.DictReader(f))

    with args.reference_csv.open(
        "r", encoding="utf-8-sig", newline=""
    ) as f:
        reference = list(csv.DictReader(f))

    by_album_track = build_index(
        reference,
        lambda r: (
            norm(r.get("album", "")),
            track_norm(r.get("track_number", "")),
        ) if r.get("album") and r.get("track_number") else None,
    )

    by_album_title = build_index(
        reference,
        lambda r: (
            norm(r.get("album", "")),
            norm(r.get("title", "")),
        ) if r.get("album") and r.get("title") else None,
    )

    by_title_date = build_index(
        reference,
        lambda r: (
            norm(r.get("title", "")),
            norm(r.get("recording_date", "")),
        ) if r.get("title") and r.get("recording_date") else None,
    )

    # Only compare fields where the two sources represent approximately the
    # same concept. Compound source fields are retained but not declared
    # equal merely because their text differs.
    fields = {
        "TITLE": "title",
        "ALBUM": "album",
        "GENRE": "genre",
        "DATE": "recording_date",
        "track": "track_number",
        "SOURCEMEDIA": "media",
        "COMPOSER": "composer",
    }

    output = []

    for meta in metadata:
        ref_index, method = pick_reference(
            meta,
            by_album_track,
            by_album_title,
            by_title_date,
            reference,
        )

        if isinstance(ref_index, int):
            ref = reference[ref_index]
            match_status = "MATCHED"
        elif isinstance(ref_index, list):
            ref = {}
            match_status = "AMBIGUOUS"
        else:
            ref = {}
            match_status = "NO_MATCH"

        row = {
            "test_case": meta.get("test_case", ""),
            "release": meta.get("release", ""),
            "filename": meta.get("filename", ""),
            "status": match_status,
            "match_method": method,
            "tango_dj_ref": ref.get("tango_dj_ref", ""),
            "ttt_title": tag(meta, "TITLE"),
            "reference_title": ref.get("title", ""),
            "ttt_artist": tag(meta, "ARTIST"),
            "reference_artist": ref.get("artist", ""),
            "ttt_album_artist": tag(meta, "album_artist"),
            "ttt_album": tag(meta, "ALBUM"),
            "reference_album": ref.get("album", ""),
            "ttt_genre": tag(meta, "GENRE"),
            "reference_genre": ref.get("genre", ""),
            "ttt_date": tag(meta, "DATE"),
            "reference_date": ref.get("recording_date", ""),
            "ttt_composer": tag(meta, "COMPOSER"),
            "reference_composer": ref.get("composer", ""),
            "ttt_conductor": tag(meta, "CONDUCTOR"),
            "ttt_catalognumber": tag(meta, "CATALOGNUMBER"),
            "reference_catalog_number": ref.get("catalog_number", ""),
            "reference_matrix_number": ref.get("matrix_number", ""),
            "ttt_sourcemedia": tag(meta, "SOURCEMEDIA"),
            "reference_media": ref.get("media", ""),
            "ttt_track": tag(meta, "track"),
            "reference_track": ref.get("track_number", ""),
            "ttt_comment": tag(meta, "COMMENT"),
        }

        for source_field, reference_field in fields.items():
            row[f"{source_field}_comparison"] = compare(
                tag(meta, source_field),
                ref.get(reference_field, ""),
            )

        # These are compound fields whose different text forms are expected
        # and therefore require decomposition rather than string equality.
        row["ARTIST_comparison"] = (
            "DECOMPOSE_REQUIRED"
            if match_status == "MATCHED"
            else "NOT_COMPARED"
        )
        row["CATALOGNUMBER_comparison"] = (
            "DECOMPOSE_REQUIRED"
            if match_status == "MATCHED"
            else "NOT_COMPARED"
        )
        row["CONDUCTOR_comparison"] = (
            "SOURCE_ONLY_IN_TEST"
            if match_status == "MATCHED"
            else "NOT_COMPARED"
        )

        output.append(row)

    output_fields = [
        "test_case", "release", "filename", "status", "match_method",
        "tango_dj_ref",
        "ttt_title", "reference_title",
        "ttt_artist", "reference_artist",
        "ttt_album_artist", "ttt_album", "reference_album",
        "ttt_genre", "reference_genre",
        "ttt_date", "reference_date",
        "ttt_composer", "reference_composer",
        "ttt_conductor",
        "ttt_catalognumber", "reference_catalog_number",
        "reference_matrix_number",
        "ttt_sourcemedia", "reference_media",
        "ttt_track", "reference_track",
        "ttt_comment",
        "TITLE_comparison",
        "ALBUM_comparison",
        "GENRE_comparison",
        "DATE_comparison",
        "track_comparison",
        "SOURCEMEDIA_comparison",
        "COMPOSER_comparison",
        "ARTIST_comparison",
        "CATALOGNUMBER_comparison",
        "CONDUCTOR_comparison",
    ]

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.output_csv.open(
        "w", encoding="utf-8-sig", newline=""
    ) as f:
        writer = csv.DictWriter(f, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(output)

    print(f"TTT files: {len(metadata)}")
    print(f"Reference records: {len(reference)}")
    print(f"Matched: {sum(r['status'] == 'MATCHED' for r in output)}")
    print(f"Ambiguous: {sum(r['status'] == 'AMBIGUOUS' for r in output)}")
    print(f"No match: {sum(r['status'] == 'NO_MATCH' for r in output)}")
    print(f"CSV written: {args.output_csv}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
