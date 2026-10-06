#!/usr/bin/env python3
"""
Build Tango Tunes source-derived ingest staging.

Purpose:
  Convert the Tango Tunes inventory CSV into a source-faithful ingest CSV.

Principles:
  - Use only information actually present in the Tango Tunes inventory.
  - Parse filename evidence without pretending it is authoritative.
  - Mark missing useful fields for possible outside enrichment.
  - Preserve raw source values.
  - Do not modify source audio.
  - Do not import TANGO-DJ values here; enrichment is a later/reference step.

The result is suitable for later TANGO-DJ comparison and canonical staging.
"""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


def clean(value: str) -> str:
    return (value or "").strip()


def parse_filename(filename: str) -> dict[str, str]:
    """
    Parse the recurring Tango Tunes filename shape:

        title IDENTIFIER_SUFFIX.ext

    Examples observed:
        Araca la cana 74194_RP.aif
        Canto de amor 86527-2_TT.aif
        A Maria Rosa S-001960-1_FV.aif

    This parser is deliberately conservative.
    It records the identifier and suffix as source evidence but does not
    assert what either means.
    """
    stem = Path(filename).stem.strip()
    result = {
        "filename_title_candidate": "",
        "filename_identifier": "",
        "filename_suffix": "",
        "filename_parse_status": "UNPARSED",
    }

    m = re.match(
        r"^(?P<title>.+?)\s+"
        r"(?P<identifier>[A-Za-z]?[-]?\d[\w.-]*)"
        r"(?:_(?P<suffix>[A-Za-z][A-Za-z0-9-]*))?$",
        stem,
    )

    if not m:
        # Preserve the undecoded filename through the source record.
        # Do not present the whole stem as a decoded title candidate.
        result["filename_parse_status"] = "NO_PATTERN"
        return result

    result.update({
        "filename_title_candidate": clean(m.group("title")),
        "filename_identifier": clean(m.group("identifier")),
        "filename_suffix": clean(m.group("suffix") or ""),
        "filename_parse_status": "PARSED",
    })
    return result


def missing_status(row: dict[str, str]) -> dict[str, str]:
    """
    Mark absent useful information as a candidate for outside enrichment.

    These flags mean only that the source inventory did not provide the field;
    they do not mean the recording is defective.
    """
    mapping = {
        "derived_track_number": "TRACK",
        "derived_recording_date": "DATE",
        "derived_composer": "COMPOSER",
        "derived_publisher": "PUBLISHER",
        "derived_album": "ALBUM",
        "derived_album_artist": "ALBUM_ARTIST",
        "derived_genre": "GENRE",
        "derived_artist": "ARTIST",
    }

    out = {}
    missing = []

    for out_name, source_name in mapping.items():
        value = clean(row.get(source_name, ""))
        out[out_name] = value
        if not value:
            missing.append(out_name.upper())

    out["enrichment_needed"] = "YES" if missing else "NO"
    out["enrichment_fields"] = ";".join(missing)
    return out


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("inventory_csv", type=Path)
    p.add_argument("output_csv", type=Path)
    p.add_argument(
        "--source-name",
        default="TangoTunes",
        help="source name stored in the output",
    )
    args = p.parse_args()

    if not args.inventory_csv.is_file():
        p.error(f"Inventory CSV not found: {args.inventory_csv}")

    with args.inventory_csv.open(
        "r", encoding="utf-8-sig", newline=""
    ) as f:
        rows = list(csv.DictReader(f))

    output_fields = [
        "source",
        "source_id",
        "source_root",
        "relative_path",
        "filename",
        "extension",
        "size_bytes",

        # Raw source metadata
        "TITLE",
        "ARTIST",
        "ALBUM",
        "ALBUM_ARTIST",
        "GENRE",
        "DATE",
        "TRACK",
        "COMMENT",
        "COMPOSER",
        "PUBLISHER",
        "CONDUCTOR",
        "CATALOGNUMBER",
        "SOURCEMEDIA",

        # Filename/source-derived evidence
        "filename_title_candidate",
        "filename_identifier",
        "filename_suffix",
        "filename_parse_status",

        # Source-available values presented for downstream staging
        "derived_recording_date",
        "derived_track_number",
        "derived_composer",
        "derived_publisher",
        "derived_album",
        "derived_album_artist",
        "derived_genre",
        "derived_artist",

        # Enrichment markers
        "enrichment_needed",
        "enrichment_fields",
    ]

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)

    parse_counts = {}
    enrichment_count = 0

    with args.output_csv.open(
        "w", encoding="utf-8-sig", newline=""
    ) as f:
        writer = csv.DictWriter(f, fieldnames=output_fields)
        writer.writeheader()

        for row in rows:
            parsed = parse_filename(row.get("filename", ""))
            staged = {
                field: ""
                for field in output_fields
            }

            staged.update({
                "source": args.source_name,
                "source_id": args.source_name,
                "source_root": row.get("source_root", ""),
                "relative_path": row.get("relative_path", ""),
                "filename": row.get("filename", ""),
                "extension": row.get("extension", ""),
                "size_bytes": row.get("size_bytes", ""),
            })

            for field in (
                "TITLE", "ARTIST", "ALBUM", "ALBUM_ARTIST", "GENRE",
                "DATE", "TRACK", "COMMENT", "COMPOSER", "PUBLISHER",
                "CONDUCTOR", "CATALOGNUMBER", "SOURCEMEDIA",
            ):
                staged[field] = row.get(field, "")

            staged.update(parsed)
            staged.update(missing_status(row))

            writer.writerow(staged)

            key = parsed["filename_parse_status"]
            parse_counts[key] = parse_counts.get(key, 0) + 1
            if staged["enrichment_needed"] == "YES":
                enrichment_count += 1

    print(f"Source records: {len(rows)}")
    print("Filename parse status:")
    for key, count in sorted(parse_counts.items()):
        print(f"  {key}: {count}")
    print(f"Records marked for outside enrichment: {enrichment_count}")
    print(f"Tango Tunes ingest staging CSV: {args.output_csv}")
    print("Source audio was not modified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


