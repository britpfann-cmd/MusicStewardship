from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


REQUIRED_SOURCE_FIELDS = {
    "Key",
    "Source",
    "Title",
    "Artist",
    "Album",
    "Duration",
    "FileName",
    "Path",
}


def load_source(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)

        if not reader.fieldnames:
            raise ValueError(f"Source file has no header: {path}")

        missing = REQUIRED_SOURCE_FIELDS - set(reader.fieldnames)
        if missing:
            raise ValueError(
                f"Source file missing required fields: {sorted(missing)}"
            )

        return list(reader)


def make_observation(
    row: dict[str, str],
    *,
    source_field: str,
    entity_type: str,
    source_name: str,
    collection_type: str,
) -> dict[str, Any]:

    observed_value = row.get(source_field, "")

    if not observed_value:
        raise ValueError(
            f"Row {row.get('Key', '<no Key>')} has no value in "
            f"source field {source_field!r}"
        )

    # Preserve the complete source row. Nothing from the candidate record
    # is discarded merely because D2 is currently using one field.
    source_record = dict(row)

    return {
        "source": source_name,
        "collection": row["Source"],
        "collection_type": collection_type,
        "source_record_id": f"{row["Source"]}::{row["Key"]}",
        "entity_type": entity_type,
        "observed_value": observed_value,
        "context_json": json.dumps(
            {
                "source_field": source_field,
                "title": row["Title"],
                "artist": row["Artist"],
                "album": row["Album"],
                "duration": row["Duration"],
                "file_name": row["FileName"],
                "path": row["Path"],
            },
            ensure_ascii=False,
            separators=(",", ":"),
        ),
        "evidence_json": json.dumps(
            {
                "adapter": "d2_candidate_adapter",
                "source_record_key_field": "Key",
                "source_record": source_record,
            },
            ensure_ascii=False,
            separators=(",", ":"),
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Adapt cross-collection candidate records into D2 observations"
    )
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source-field", required=True)
    parser.add_argument("--entity-type", required=True)
    parser.add_argument(
        "--source-name",
        default="cross_collection_candidates.csv",
    )
    parser.add_argument(
        "--collection-type",
        default="candidate_evidence",
    )

    args = parser.parse_args()

    rows = load_source(args.input)

    fieldnames = [
        "source",
        "collection",
        "collection_type",
        "source_record_id",
        "entity_type",
        "observed_value",
        "context_json",
        "evidence_json",
    ]

    args.output.parent.mkdir(parents=True, exist_ok=True)

    with args.output.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            writer.writerow(
                make_observation(
                    row,
                    source_field=args.source_field,
                    entity_type=args.entity_type,
                    source_name=args.source_name,
                    collection_type=args.collection_type,
                )
            )

    print(f"Adapted {len(rows)} source records.")
    print(f"Source field: {args.source_field}")
    print(f"Entity type: {args.entity_type}")
    print(f"Output: {args.output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
