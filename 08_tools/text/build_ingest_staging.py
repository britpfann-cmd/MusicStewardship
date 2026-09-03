#!/usr/bin/env python3
"""
Build generic ingest staging records from generic source-ingest evidence.

This stage is source-agnostic.

It:
    - preserves source provenance
    - maps source-derived evidence into the staging vocabulary
    - preserves filename-derived evidence separately from embedded metadata
    - leaves canonical identity unresolved
    - does not perform reference matching
    - does not reject assets

Input:
    CSV produced by source_ingest.py

Output:
    Generic Reference Record staging CSV
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


# ---------------------------------------------------------------------------
# CSV helpers
# ---------------------------------------------------------------------------

def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    if not rows:
        return

    fields = list(rows[0].keys())

    with path.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=fields,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)


# ---------------------------------------------------------------------------
# Value helpers
# ---------------------------------------------------------------------------

def value(row: dict[str, str], field: str) -> str:
    """Return a trimmed source value, preserving empty values as empty."""
    return (row.get(field) or "").strip()


def first_value(row: dict[str, str], *fields: str) -> str:
    """Return the first non-empty value from the supplied fields."""
    for field in fields:
        v = value(row, field)
        if v:
            return v
    return ""


def build_source_context(row: dict[str, str]) -> str:
    """
    Preserve the source hierarchy as a compact context value.

    The original directory path remains separately preserved.
    """
    parts = []

    directory_path = value(row, "directory_path")
    directory_name = value(row, "directory_name")
    hierarchy_signature = value(row, "hierarchy_signature")

    if directory_path:
        parts.append(f"directory_path={directory_path}")

    if directory_name:
        parts.append(f"directory_name={directory_name}")

    if hierarchy_signature:
        parts.append(
            f"hierarchy_signature={hierarchy_signature}"
        )

    return ";".join(parts)


# ---------------------------------------------------------------------------
# Staging transformation
# ---------------------------------------------------------------------------

def build_staging_record(row: dict[str, str]) -> dict[str, str]:
    """
    Transform one generic source-ingest evidence record into one
    reference-record staging record.

    No canonical identity is selected here.
    """

    # -----------------------------------------------------------------------
    # Source provenance
    # -----------------------------------------------------------------------

    source = value(row, "source_id")

    source_file = value(row, "relative_path")
    source_filename = value(row, "filename")

    source_track_number = first_value(
        row,
        "metadata_track",
    )

    # Filename-derived release/track information is evidence.
    # Preserve it independently rather than silently treating it as
    # canonical source_track_number.
    filename_rule_values = value(
        row,
        "filename_rule_values",
    )

    if not source_track_number:
        source_track_number = first_value(
            row,
            "filename_release_track_number",
        )

    source_catalog_id = first_value(
        row,
        "metadata_catalognumber",
    )

    source_context = build_source_context(row)

    # -----------------------------------------------------------------------
    # Source evidence
    # -----------------------------------------------------------------------

    source_original_title = first_value(
        row,
        "metadata_title",
    )

    source_original_artist = first_value(
        row,
        "metadata_artist",
    )

    source_original_album = first_value(
        row,
        "metadata_album",
    )

    source_original_date = first_value(
        row,
        "metadata_date",
    )

    source_original_catalognumber = first_value(
        row,
        "metadata_catalognumber",
    )

    source_original_composer = first_value(
        row,
        "metadata_composer",
    )

    source_original_comment = first_value(
        row,
        "metadata_comment",
    )

    # -----------------------------------------------------------------------
    # Filename evidence
    # -----------------------------------------------------------------------

    filename_title = ""
    filename_artist = ""
    filename_release_track_number = ""

    rule_values = {}

    if filename_rule_values:
        for item in filename_rule_values.split(";"):
            if "=" not in item:
                continue

            key, val = item.split("=", 1)
            rule_values[key.strip()] = val.strip()

        filename_title = rule_values.get("title", "")
        filename_artist = rule_values.get("artist", "")
        filename_release_track_number = rule_values.get(
            "release_track_number",
            "",
        )

    # -----------------------------------------------------------------------
    # Normalized/decomposed values
    #
    # These remain empty. Normalization is a later explicit stage.
    # -----------------------------------------------------------------------

    canonical_title = ""
    canonical_ensemble = ""
    canonical_singers = ""
    canonical_record_number = ""
    canonical_matrix_number = ""
    canonical_take_number = ""

    normalization_rule = ""
    normalization_type = ""

    # -----------------------------------------------------------------------
    # Reconciliation / identity
    #
    # No identity decision is made here.
    # -----------------------------------------------------------------------

    identity_status = "UNRESOLVED"
    identity_confidence = "UNRESOLVED"

    divergence_type = ""
    divergence_status = ""
    review_note = ""

    # -----------------------------------------------------------------------
    # Construct staging record
    # -----------------------------------------------------------------------

    return {
        # Identity
        "reference_record_id": "",
        "title": "",
        "ensemble": "",
        "singers": "",
        "instrumental": "",
        "recording_date": "",

        # Source provenance
        "source": source,
        "source_snapshot": "",
        "source_release": "",
        "source_row": "",
        "source_file": source_file,
        "source_filename": source_filename,
        "source_catalog_id": source_catalog_id,
        "source_track_number": source_track_number,
        "source_context": source_context,

        # Source evidence
        "source_original_title": source_original_title,
        "source_original_artist": source_original_artist,
        "source_original_album": source_original_album,
        "source_original_date": source_original_date,
        "source_original_catalognumber":
            source_original_catalognumber,
        "source_original_composer":
            source_original_composer,
        "source_original_comment":
            source_original_comment,

        # Additional filename evidence
        #
        # These are deliberately retained because they are evidence
        # that does not necessarily agree with embedded metadata.
        "filename_title_evidence": filename_title,
        "filename_artist_evidence": filename_artist,
        "filename_release_track_number_evidence":
            filename_release_track_number,

        # Normalized/decomposed values
        "canonical_title": canonical_title,
        "canonical_ensemble": canonical_ensemble,
        "canonical_singers": canonical_singers,
        "canonical_record_number": canonical_record_number,
        "canonical_matrix_number": canonical_matrix_number,
        "canonical_take_number": canonical_take_number,
        "normalization_rule": normalization_rule,
        "normalization_type": normalization_type,

        # External references
        "reference_source": "",
        "external_reference_id": "",
        "external_release": "",
        "external_track_number": "",
        "external_title": "",
        "external_artist": "",
        "external_recording_date": "",
        "external_catalog_number": "",
        "external_matrix_number": "",
        "external_notes": "",

        # Reconciliation
        "identity_status": identity_status,
        "identity_confidence": identity_confidence,
        "divergence_type": divergence_type,
        "divergence_status": divergence_status,
        "review_note": review_note,

        # Original generic ingest evidence
        #
        # These fields make the staging record auditable without requiring
        # us to reopen the earlier ingest CSV.
        "filename_rule_status":
            value(row, "filename_rule_status"),
        "filename_rule_id":
            value(row, "filename_rule_id"),
        "filename_rule_values":
            filename_rule_values,
        "embedded_metadata_status":
            value(row, "embedded_metadata_status"),
        "embedded_metadata_values":
            value(row, "embedded_metadata_values"),
        "source_rule_set":
            value(row, "source_rule_set"),
        "evidence_sources":
            value(row, "evidence_sources"),
        "relative_path":
            value(row, "relative_path"),
        "directory_path":
            value(row, "directory_path"),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Build generic reference-record staging records "
            "from source-ingest evidence."
        )
    )

    parser.add_argument(
        "ingest_evidence",
        type=Path,
        help="CSV produced by the generic source ingestion engine",
    )

    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Output staging CSV",
    )

    args = parser.parse_args()

    input_rows = read_csv(args.ingest_evidence)

    output_rows = [
        build_staging_record(row)
        for row in input_rows
    ]

    write_csv(args.output, output_rows)

    unresolved = sum(
        row["identity_status"] == "UNRESOLVED"
        for row in output_rows
    )

    retained = sum(
        row["identity_status"] == "UNRESOLVED"
        for row in output_rows
    )

    print(f"Input ingest records: {len(input_rows)}")
    print(f"Staging records: {len(output_rows)}")
    print(f"Identity unresolved: {unresolved}")
    print(f"Assets retained: {retained}")
    print("Canonical identities selected: 0")
    print("Reference matches performed: 0")
    print(f"Output: {args.output}")


if __name__ == "__main__":
    main()