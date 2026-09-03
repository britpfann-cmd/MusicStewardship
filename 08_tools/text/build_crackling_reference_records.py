#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Build catalog-ready Crackling Tunes staging records.

v3 fixes the v2 join bug by deriving release_id from source_release
before joining to the reconciliation CSV.

Inputs:
  crackling_catalog_text_v2.csv
  crackling_to_tango_comparison_v5b.csv

Outputs:
  crackling_source_tracks.csv
  crackling_reference_records.csv
  crackling_reference_validation.md

Read-only. No audio files are modified.
"""

import argparse
import csv
import hashlib
import re
from collections import Counter
from pathlib import Path

SOURCE_COLUMNS = [
    "source_row", "source", "source_snapshot", "source_release",
    "release_id", "source_path", "source_file", "audio_format",
    "source_catalog_id", "source_track_number", "source_title",
    "source_artist", "source_albumartist", "source_date",
    "source_ensemble", "source_singers", "source_instrumental",
]

REFERENCE_COLUMNS = [
    "reference_record_id", "identity_status", "source", "source_snapshot",
    "source_row", "source_release", "release_id", "source_path",
    "source_file", "audio_format", "source_catalog_id",
    "source_track_number", "source_title", "source_artist",
    "source_albumartist", "source_date", "source_ensemble",
    "source_singers", "source_instrumental", "title", "ensemble",
    "singers", "instrumental", "recording_date", "tango_dj_ref",
    "tango_dj_release", "tango_dj_track_number", "tango_dj_title",
    "tango_dj_artist", "tango_dj_recording_date",
    "tango_dj_catalog_number", "tango_dj_matrix_number",
]


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def snapshot_id(path: Path) -> str:
    return f"{path.name}:{file_sha256(path)}"


def release_id_from_source(value: str) -> str:
    m = re.search(
        r"\b(\d{2})\.(\d{2})\s+Releases\b",
        value or "",
        re.IGNORECASE,
    )
    return f"CTMM{m.group(1)}{m.group(2)}" if m else ""


def collapse_source(rows):
    grouped = {}

    for row in rows:
        key = (
            row.get("source_path", ""),
            row.get("source_file", ""),
        )

        if key not in grouped:
            release = row.get("source_release", "")
            grouped[key] = {
                "source_release": release,
                "release_id": release_id_from_source(release),
                "source_path": row.get("source_path", ""),
                "source_file": row.get("source_file", ""),
                "audio_format": row.get("audio_format", ""),
                "source_catalog_id": row.get("catalog_number", ""),
                "source_track_number": "",
                "source_title": "",
                "source_artist": "",
                "source_albumartist": "",
                "source_date": "",
                "source_ensemble": "",
                "source_singers": "",
                "source_instrumental": "",
            }

        field = row.get("field_name", "").upper()
        value = row.get("original_text", "")

        if field == "TITLE":
            grouped[key]["source_title"] = value
        elif field == "ARTIST":
            grouped[key]["source_artist"] = value
        elif field == "ALBUMARTIST":
            grouped[key]["source_albumartist"] = value

    return grouped


def build_reconciliation_index(rows):
    """
    Primary key: release_id + source_file.
    Secondary index by source_file is used only to diagnose/confirm a
    unique fallback row.
    """
    by_key = {}
    by_file = {}

    for row in rows:
        release_id = row.get("release_id", "")
        source_file = row.get("source_file", "")
        by_key[(release_id, source_file)] = row
        by_file.setdefault(source_file, []).append(row)

    return by_key, by_file


def make_reference_id(release_id, catalog_id, row_number):
    if catalog_id:
        return f"CRACKLING-{release_id}-{catalog_id}"
    return f"CRACKLING-{release_id}-ROW{row_number:04d}"


def build(source_csv: Path, reconciliation_csv: Path):
    source_rows = read_csv(source_csv)
    recon_rows = read_csv(reconciliation_csv)

    grouped = collapse_source(source_rows)
    recon_by_key, recon_by_file = build_reconciliation_index(recon_rows)

    snapshot = snapshot_id(source_csv)

    source_records = []
    reference_records = []
    unresolved = []

    for row_number, key in enumerate(
        sorted(grouped.keys()), start=2
    ):
        item = dict(grouped[key])

        recon = recon_by_key.get(
            (item["release_id"], item["source_file"])
        )

        # Unique filename fallback only when it independently agrees on
        # release_id. This avoids accidentally joining duplicate filenames
        # from different monthly releases.
        if recon is None:
            alternatives = [
                r for r in recon_by_file.get(
                    item["source_file"], []
                )
                if r.get("release_id", "") == item["release_id"]
            ]
            if len(alternatives) == 1:
                recon = alternatives[0]

        if recon:
            item["source_catalog_id"] = (
                recon.get("source_catalog_id", "")
                or item["source_catalog_id"]
            )
            for field in (
                "source_track_number",
                "source_date",
                "source_ensemble",
                "source_singers",
                "source_instrumental",
            ):
                item[field] = recon.get(field, "")

        source_record = {
            "source_row": str(row_number),
            "source": "Crackling Tunes",
            "source_snapshot": snapshot,
            **item,
        }
        source_records.append(source_record)

        status = (
            recon.get("match_status", "UNRESOLVED")
            if recon else "UNRESOLVED_NO_RECONCILIATION_ROW"
        )

        ref_id = make_reference_id(
            item["release_id"],
            item["source_catalog_id"],
            row_number,
        )

        title = (
            recon.get("tango_title", "")
            if recon else ""
        ) or item["source_title"]

        recording_date = (
            recon.get("tango_recording_date", "")
            if recon else ""
        ) or item["source_date"]

        reference_records.append({
            "reference_record_id": ref_id,
            "identity_status": (
                "RESOLVED_BY_RELEASE_TRACK"
                if status == "RELEASE_TRACK_MATCH"
                else status
            ),
            "source": "Crackling Tunes",
            "source_snapshot": snapshot,
            "source_row": str(row_number),
            "source_release": item["source_release"],
            "release_id": item["release_id"],
            "source_path": item["source_path"],
            "source_file": item["source_file"],
            "audio_format": item["audio_format"],
            "source_catalog_id": item["source_catalog_id"],
            "source_track_number": item["source_track_number"],
            "source_title": item["source_title"],
            "source_artist": item["source_artist"],
            "source_albumartist": item["source_albumartist"],
            "source_date": item["source_date"],
            "source_ensemble": item["source_ensemble"],
            "source_singers": item["source_singers"],
            "source_instrumental": item["source_instrumental"],
            "title": title,
            "ensemble": item["source_ensemble"],
            "singers": item["source_singers"],
            "instrumental": (
                recon.get("tango_instrumental", "")
                if recon else ""
            ) or item["source_instrumental"],
            "recording_date": recording_date,
            "tango_dj_ref": (
                recon.get("tango_ref", "") if recon else ""
            ),
            "tango_dj_release": (
                recon.get("tango_release", "") if recon else ""
            ),
            "tango_dj_track_number": (
                recon.get("tango_track_number", "")
                if recon else ""
            ),
            "tango_dj_title": (
                recon.get("tango_title", "") if recon else ""
            ),
            "tango_dj_artist": (
                recon.get("tango_artist", "") if recon else ""
            ),
            "tango_dj_recording_date": (
                recon.get("tango_recording_date", "")
                if recon else ""
            ),
            "tango_dj_catalog_number": (
                recon.get("tango_catalog_number", "")
                if recon else ""
            ),
            "tango_dj_matrix_number": (
                recon.get("tango_matrix_number", "")
                if recon else ""
            ),
        })

        if status != "RELEASE_TRACK_MATCH":
            unresolved.append(
                (
                    status,
                    item["source_release"],
                    item["source_file"],
                )
            )

    return source_records, reference_records, unresolved


def write_csv(path: Path, rows, columns):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def write_validation(path: Path, source_records, reference_records, unresolved):
    counts = Counter(
        r["identity_status"] for r in reference_records
    )

    resolved = counts.get(
        "RESOLVED_BY_RELEASE_TRACK",
        0,
    )

    lines = [
        "# Crackling Tunes Reference Staging Validation",
        "",
        "## Counts",
        "",
        f"- Source-track records: **{len(source_records)}**",
        f"- Reference staging records: **{len(reference_records)}**",
        f"- Release/track-resolved records: **{resolved}/{len(reference_records)}**",
        f"- Exceptions: **{len(unresolved)}**",
        "",
        "## Identity status",
        "",
    ]

    for status, count in sorted(counts.items()):
        lines.append(f"- `{status}`: **{count}**")

    lines.extend(["", "## Exceptions", ""])

    if unresolved:
        for status, release, filename in unresolved:
            lines.append(
                f"- `{status}` — `{release}` — `{filename}`"
            )
    else:
        lines.append("None.")

    lines.extend([
        "",
        "## Provenance",
        "",
        "Every record retains `source_snapshot` and `source_row`.",
        "The source snapshot is content-addressed by SHA-256.",
        "",
        "## Safety",
        "",
        "This staging process does not modify or copy audio files.",
    ])

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Build Crackling Tunes source-track and "
            "reference-record staging CSVs."
        )
    )

    parser.add_argument("source_csv", type=Path)
    parser.add_argument("reconciliation_csv", type=Path)
    parser.add_argument("source_tracks_csv", type=Path)
    parser.add_argument("reference_records_csv", type=Path)
    parser.add_argument("validation_md", type=Path)

    args = parser.parse_args()

    for path in (
        args.source_csv,
        args.reconciliation_csv,
    ):
        if not path.is_file():
            parser.error(f"Input not found: {path}")

    source_records, reference_records, unresolved = build(
        args.source_csv,
        args.reconciliation_csv,
    )

    write_csv(
        args.source_tracks_csv,
        source_records,
        SOURCE_COLUMNS,
    )
    write_csv(
        args.reference_records_csv,
        reference_records,
        REFERENCE_COLUMNS,
    )
    write_validation(
        args.validation_md,
        source_records,
        reference_records,
        unresolved,
    )

    print(
        f"Source-track records: {len(source_records)}"
    )
    print(
        f"Reference staging records: {len(reference_records)}"
    )
    print(
        f"Unresolved/exceptions: {len(unresolved)}"
    )
    print(
        f"Wrote: {args.source_tracks_csv}"
    )
    print(
        f"Wrote: {args.reference_records_csv}"
    )
    print(
        f"Wrote: {args.validation_md}"
    )


if __name__ == "__main__":
    raise SystemExit(main())
