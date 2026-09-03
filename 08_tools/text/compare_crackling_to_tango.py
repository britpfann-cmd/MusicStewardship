#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Crackling Tunes <-> TANGO-DJ reconciliation v5

Purpose
-------
Compare the Crackling Tunes source extraction with the TANGO-DJ reference
export for the same CTMM releases.

This version treats release + track position as the primary correspondence
signal. Text is then compared as evidence rather than as the identity key.

Crackling Tunes track position is derived from the CT catalog suffix:

    -A1 -> 1
    -B1 -> 2
    -A2 -> 3
    -B2 -> 4
    etc.

Examples:
    CT2424-A1 -> track 1
    CT2424-B1 -> track 2
    CT21001-A2 -> track 3

No source data is modified.
"""

import argparse
import csv
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path


OUTPUT_COLUMNS = [
    "source_release",
    "release_id",
    "source_file",
    "audio_format",
    "source_catalog_id",
    "source_track_number",
    "source_title",
    "source_artist",
    "source_albumartist",
    "source_date",
    "source_ensemble",
    "source_singers",
    "source_instrumental",
    "tango_ref",
    "tango_release",
    "tango_track_number",
    "tango_title",
    "tango_artist",
    "tango_recording_date",
    "tango_catalog_number",
    "tango_matrix_number",
    "tango_instrumental",
    "match_status",
    "track_match",
    "title_match",
    "date_match",
    "artist_match",
    "identity_note",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as f:
        return list(csv.DictReader(f))


def normalize_text(value: str) -> str:
    """Normalization used for comparison only."""
    if not value:
        return ""

    value = unicodedata.normalize("NFKD", value)
    value = "".join(
        ch for ch in value
        if not unicodedata.combining(ch)
    )

    value = value.lower()

    # Common apostrophe/dash variants.
    value = value.replace("’", "'")
    value = value.replace("´", "'")
    value = value.replace("`", "'")
    value = value.replace("–", "-")
    value = value.replace("—", "-")

    # Remove punctuation, retaining word content.
    value = re.sub(r"[^a-z0-9]+", " ", value)
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def normalize_title(value: str) -> str:
    """
    Normalize title for matching.

    Removes transfer-frequency annotations and surrounding punctuation.
    Keeps parenthetical alternate-title information because it can be
    useful evidence rather than silently discarding it.
    """
    if not value:
        return ""

    value = re.sub(
        r"\s*\(\s*\d+\s*hz\s*\)",
        "",
        value,
        flags=re.IGNORECASE,
    )

    value = re.sub(
        r"\s+\(\s*\)",
        "",
        value,
    )

    return normalize_text(value)


def release_id_from_source(value: str) -> str:
    """
    Convert:
        21.08 Releases -> CTMM2108
    """
    match = re.search(
        r"\b(\d{2})\.(\d{2})\s+Releases\b",
        value or "",
        flags=re.IGNORECASE,
    )

    if not match:
        return ""

    year, month = match.groups()
    return f"CTMM{year}{month}"


def release_id_from_text(value: str) -> str:
    match = re.search(
        r"\b(CTMM\d{4})\b",
        value or "",
        flags=re.IGNORECASE,
    )

    return match.group(1).upper() if match else ""


def parse_int(value: str):
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def derive_track_number(catalog_number: str) -> str:
    """
    Derive release track number from CT matrix-side suffix.

    A1 -> 1
    B1 -> 2
    A2 -> 3
    B2 -> 4
    ...
    """
    if not catalog_number:
        return ""

    match = re.search(
        r"-([AB])(\d+)\s*$",
        catalog_number.strip(),
        flags=re.IGNORECASE,
    )

    if not match:
        return ""

    side, take = match.groups()
    take_number = int(take)

    # A1/B1 = 1/2, A2/B2 = 3/4, ...
    track = (take_number - 1) * 2 + (
        1 if side.upper() == "A" else 2
    )

    return str(track)


def date_from_filename(filename: str) -> str:
    match = re.search(
        r"(\d{2})_(\d{2})_(\d{4})",
        filename or "",
    )

    if match:
        day, month, year = match.groups()
        return f"{year}-{month}-{day}"

    match = re.search(
        r"\b(19|20)\d{2}\b",
        filename or "",
    )

    if match:
        return match.group(0)

    return ""


def split_crackling_artist(value: str):
    """
    Crackling Tunes generally uses:
        Ensemble / Singer
        Ensemble / Singer / Singer
        Ensemble / Instrumental
    """
    if not value:
        return "", [], False

    parts = [
        p.strip()
        for p in re.split(r"\s*/\s*", value)
        if p.strip()
    ]

    if not parts:
        return "", [], False

    ensemble = parts[0]

    rest = parts[1:]

    singers = []
    instrumental = False

    for item in rest:
        if normalize_text(item) in {
            "instrumental",
            "instr",
        }:
            instrumental = True
            continue

        singers.append(item)

    return ensemble, singers, instrumental


def tango_artist_parts(value: str):
    """
    Best-effort decomposition of TANGO-DJ Artist.

    Recognizes the common:
        Orquesta X con Singer
        Orquesta X con Singer y Singer
        ... con Singer

    Other forms remain intact as an ensemble/performer assertion.
    """
    if not value:
        return "", []

    raw = value.strip()

    match = re.search(
        r"\s+\bcon\b\s+",
        raw,
        flags=re.IGNORECASE,
    )

    if match:
        ensemble = raw[:match.start()].strip()
        singer_text = raw[match.end():].strip()

        singers = [
            item.strip()
            for item in re.split(
                r"\s+\by\b\s+|,\s*",
                singer_text,
                flags=re.IGNORECASE,
            )
            if item.strip()
        ]

        return ensemble, singers

    # Common "X y su Orquesta..." form: retain the whole assertion,
    # because it is not safe to infer a singer here.
    return raw, []


def source_rows_to_tracks(
    rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    """Collapse the four extracted text rows per audio file."""
    grouped = {}

    for row in rows:
        key = (
            row.get("source_path", ""),
            row.get("source_file", ""),
        )

        if key not in grouped:
            catalog = row.get("catalog_number", "")

            grouped[key] = {
                "source_release": row.get(
                    "source_release",
                    "",
                ),
                "release_id": release_id_from_source(
                    row.get("source_release", "")
                ),
                "source_file": row.get(
                    "source_file",
                    "",
                ),
                "audio_format": row.get(
                    "audio_format",
                    "",
                ),
                "source_catalog_id": catalog,
                "source_track_number": (
                    derive_track_number(catalog)
                ),
                "source_title": "",
                "source_artist": "",
                "source_albumartist": "",
                "source_date": date_from_filename(
                    row.get("source_file", "")
                ),
            }

        field = row.get(
            "field_name",
            "",
        ).upper()

        value = row.get(
            "original_text",
            "",
        )

        if field == "TITLE":
            grouped[key]["source_title"] = value

        elif field == "ARTIST":
            grouped[key]["source_artist"] = value

        elif field == "ALBUMARTIST":
            grouped[key]["source_albumartist"] = value

    for track in grouped.values():
        ensemble, singers, instrumental = (
            split_crackling_artist(
                track["source_artist"]
            )
        )

        track["source_ensemble"] = ensemble
        track["source_singers"] = "; ".join(
            singers
        )
        track["source_instrumental"] = (
            "YES" if instrumental else "NO"
        )

    return list(grouped.values())


def build_tango_indexes(
    rows: list[dict[str, str]],
):
    by_release = defaultdict(list)
    by_release_track = defaultdict(list)
    by_release_title = defaultdict(list)

    for original in rows:
        row = dict(original)

        release_id = ""
        for field in (
            "album",
            "release",
            "tango_release",
        ):
            release_id = (
                release_id_from_text(
                    row.get(field, "")
                )
                or release_id
            )

        if not release_id:
            continue

        row["_release_id"] = release_id

        by_release[release_id].append(row)

        track_number = parse_int(
            row.get("track_number", "")
        )

        if track_number is not None:
            by_release_track[
                (release_id, track_number)
            ].append(row)

        title = normalize_title(
            row.get("title", "")
        )

        if title:
            by_release_title[
                (release_id, title)
            ].append(row)

    return (
        by_release,
        by_release_track,
        by_release_title,
    )


def field_compare(
    source: str,
    target: str,
    *,
    title=False,
):
    if not source or not target:
        return "UNKNOWN"

    if title:
        a = normalize_title(source)
        b = normalize_title(target)
    else:
        a = normalize_text(source)
        b = normalize_text(target)

    return "YES" if a == b else "NO"


def contains_name(
    source_name: str,
    target_text: str,
) -> str:
    """
    Compare a source performer/ensemble name against the richer
    TANGO-DJ Artist representation.

    Exact normalized equality is YES.
    Otherwise, if the normalized source name is contained in the
    target representation, also YES.
    """
    if not source_name or not target_text:
        return "UNKNOWN"

    source_norm = normalize_text(source_name)
    target_norm = normalize_text(target_text)

    if not source_norm:
        return "UNKNOWN"

    if source_norm == target_norm:
        return "YES"

    if source_norm in target_norm:
        return "YES"

    return "NO"


def make_result(
    source: dict[str, str],
    candidate,
    status: str,
):
    result = {
        "source_release": source["source_release"],
        "release_id": source["release_id"],
        "source_file": source["source_file"],
        "audio_format": source["audio_format"],
        "source_catalog_id": source["source_catalog_id"],
        "source_track_number": source[
            "source_track_number"
        ],
        "source_title": source["source_title"],
        "source_artist": source["source_artist"],
        "source_albumartist": source[
            "source_albumartist"
        ],
        "source_date": source["source_date"],
        "source_ensemble": source["source_ensemble"],
        "source_singers": source["source_singers"],
        "source_instrumental": source[
            "source_instrumental"
        ],
        "tango_ref": "",
        "tango_release": "",
        "tango_track_number": "",
        "tango_title": "",
        "tango_artist": "",
        "tango_recording_date": "",
        "tango_catalog_number": "",
        "tango_matrix_number": "",
        "tango_instrumental": "",
        "match_status": status,
        "track_match": "UNKNOWN",
        "title_match": "UNKNOWN",
        "date_match": "UNKNOWN",
        "artist_match": "UNKNOWN",
        "identity_note": "",
    }

    if candidate is None:
        result["identity_note"] = (
            "No TANGO-DJ candidate selected."
        )
        return result

    result["tango_ref"] = candidate.get(
        "ref",
        candidate.get("tango_ref", ""),
    )
    result["tango_release"] = candidate.get(
        "album",
        candidate.get("release", ""),
    )
    result["tango_track_number"] = candidate.get(
        "track_number",
        "",
    )
    result["tango_title"] = candidate.get(
        "title",
        "",
    )
    result["tango_artist"] = candidate.get(
        "artist",
        "",
    )
    result["tango_recording_date"] = candidate.get(
        "recording_date",
        "",
    )
    result["tango_catalog_number"] = candidate.get(
        "catalog_number",
        "",
    )
    result["tango_matrix_number"] = candidate.get(
        "matrix_number",
        "",
    )
    result["tango_instrumental"] = candidate.get(
        "instrumental",
        "",
    )

    source_track = parse_int(
        source["source_track_number"]
    )
    tango_track = parse_int(
        candidate.get("track_number", "")
    )

    if source_track is not None and tango_track is not None:
        result["track_match"] = (
            "YES"
            if source_track == tango_track
            else "NO"
        )

    result["title_match"] = field_compare(
        source["source_title"],
        candidate.get("title", ""),
        title=True,
    )

    result["date_match"] = field_compare(
        source["source_date"],
        candidate.get("recording_date", ""),
    )

    ensemble, _ = tango_artist_parts(
        candidate.get("artist", "")
    )

    result["artist_match"] = contains_name(
        source["source_ensemble"],
        ensemble,
    )

    notes = []

    if result["track_match"] == "NO":
        notes.append("track position differs")

    if result["title_match"] == "NO":
        notes.append("title differs")

    if result["date_match"] == "NO":
        notes.append("recording date differs")

    if result["artist_match"] == "NO":
        notes.append(
            "ensemble representation differs"
        )

    if not notes:
        notes.append(
            "release/track candidate corroborated"
        )

    result["identity_note"] = "; ".join(notes)

    return result


def compare(
    source_csv: Path,
    tango_csv: Path,
):
    source_rows = read_csv(source_csv)
    tango_rows = read_csv(tango_csv)

    sources = source_rows_to_tracks(
        source_rows
    )

    (
        by_release,
        by_release_track,
        by_release_title,
    ) = build_tango_indexes(
        tango_rows
    )

    results = []

    for source in sorted(
        sources,
        key=lambda row: (
            row["release_id"],
            parse_int(
                row["source_track_number"]
            )
            if parse_int(
                row["source_track_number"]
            ) is not None
            else 999999,
            normalize_title(
                row["source_title"]
            ),
            row["source_file"],
        ),
    ):
        release_id = source["release_id"]

        if not release_id:
            results.append(
                make_result(
                    source,
                    None,
                    "NO_RELEASE_ID",
                )
            )
            continue

        candidates = by_release.get(
            release_id,
            [],
        )

        if not candidates:
            results.append(
                make_result(
                    source,
                    None,
                    "NO_RELEASE",
                )
            )
            continue

        source_track = parse_int(
            source["source_track_number"]
        )

        # Primary correspondence: release + track position.
        if source_track is not None:
            track_candidates = (
                by_release_track.get(
                    (release_id, source_track),
                    [],
                )
            )

            if len(track_candidates) == 1:
                results.append(
                    make_result(
                        source,
                        track_candidates[0],
                        "RELEASE_TRACK_MATCH",
                    )
                )
                continue

            if len(track_candidates) > 1:
                results.append(
                    make_result(
                        source,
                        None,
                        "AMBIGUOUS",
                    )
                )
                continue

        # Secondary correspondence: release + normalized title.
        title = normalize_title(
            source["source_title"]
        )

        title_candidates = (
            by_release_title.get(
                (release_id, title),
                [],
            )
        )

        if len(title_candidates) == 1:
            results.append(
                make_result(
                    source,
                    title_candidates[0],
                    "TITLE_MATCH",
                )
            )
        elif len(title_candidates) > 1:
            results.append(
                make_result(
                    source,
                    None,
                    "AMBIGUOUS",
                )
            )
        else:
            results.append(
                make_result(
                    source,
                    None,
                    "NO_MATCH",
                )
            )

    return results


def write_csv(
    rows: list[dict[str, str]],
    path: Path,
):
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=OUTPUT_COLUMNS,
        )
        writer.writeheader()
        writer.writerows(rows)


def summarize(rows):
    counts = Counter(
        row["match_status"]
        for row in rows
    )

    print(
        f"Source tracks: {len(rows)}"
    )

    print()

    for status, count in sorted(
        counts.items()
    ):
        print(
            f"{status}: {count}"
        )

    matched = [
        row
        for row in rows
        if row["match_status"]
        in {
            "RELEASE_TRACK_MATCH",
            "TITLE_MATCH",
        }
    ]

    if not matched:
        return

    print()
    print(
        "Evidence agreement for matched candidates:"
    )

    for field in (
        "track_match",
        "title_match",
        "date_match",
        "artist_match",
    ):
        yes = sum(
            row[field] == "YES"
            for row in matched
        )
        no = sum(
            row[field] == "NO"
            for row in matched
        )
        unknown = sum(
            row[field] == "UNKNOWN"
            for row in matched
        )

        print(
            f"  {field}: "
            f"YES={yes} "
            f"NO={no} "
            f"UNKNOWN={unknown}"
        )


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Reconcile Crackling Tunes tracks "
            "against TANGO-DJ reference records."
        )
    )

    parser.add_argument(
        "source_csv",
        type=Path,
    )

    parser.add_argument(
        "tango_csv",
        type=Path,
    )

    parser.add_argument(
        "output_csv",
        type=Path,
    )

    args = parser.parse_args()

    if not args.source_csv.is_file():
        parser.error(
            f"Source CSV not found: {args.source_csv}"
        )

    if not args.tango_csv.is_file():
        parser.error(
            f"TANGO-DJ CSV not found: {args.tango_csv}"
        )

    rows = compare(
        args.source_csv,
        args.tango_csv,
    )

    write_csv(
        rows,
        args.output_csv,
    )

    summarize(rows)

    print()
    print(
        f"CSV written: {args.output_csv}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
