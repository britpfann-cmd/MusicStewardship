from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


SCHEMA = "musicstewardship.ttt_grammar_fixture_evidence.v1"


def parse_rule_values(value: str) -> dict[str, str]:
    result = {}

    if not value:
        return result

    for item in value.split(";"):
        if "=" not in item:
            continue
        key, raw = item.split("=", 1)
        result[key] = raw

    return result


def main() -> None:
    ap = argparse.ArgumentParser(
        description=(
            "Convert the frozen TTT grammar-ingest CSV fixture into "
            "structured source-specific evidence. Test fixture only."
        )
    )
    ap.add_argument("input", type=Path)
    ap.add_argument("-o", "--output", required=True, type=Path)
    args = ap.parse_args()

    rows = list(
        csv.DictReader(
            args.input.open("r", encoding="utf-8-sig", newline="")
        )
    )

    source_objects = []
    observations = []

    for index, row in enumerate(rows, start=1):
        source_object_id = (
            f"ttt_fixture:{index:06d}"
        )

        source_object = {
            "source_object_id": source_object_id,
            "fixture_row": index,
            "source_id": row.get("source_id", ""),
            "relative_path": row.get("relative_path", ""),
            "filename": row.get("filename", ""),
            "directory_path": row.get("directory_path", ""),
            "directory_name": row.get("directory_name", ""),
            "filename_rule_status": row.get(
                "filename_rule_status", ""
            ),
            "filename_rule_id": row.get(
                "filename_rule_id", ""
            ),
            "source_rule_set": row.get(
                "source_rule_set", ""
            ),
        }

        source_objects.append(source_object)

        values = parse_rule_values(
            row.get("filename_rule_values", "")
        )

        for field_name, field_value in values.items():
            observations.append(
                {
                    "evidence_id": (
                        f"ttt_filename:{index:06d}:{field_name}"
                    ),
                    "source_object_id": source_object_id,
                    "evidence_channel": "source_specific",
                    "evidence_type": "filename_rule",
                    "source_locator": (
                        "filename.rule."
                        f"{row.get('filename_rule_id', '')}."
                        f"{field_name}"
                    ),
                    "raw_value": field_value,
                    "normalized_value": field_value,
                    "extraction_method": "fixture_csv_decoded_value",
                    "decoder": "TangoTimeTravel",
                    "rule_id": row.get(
                        "filename_rule_id", ""
                    ),
                    "rule_field": field_name,
                    "status": "observed",
                    "fixture_row": index,
                    "source_object_id_in_fixture": source_object_id,
                }
            )

    payload = {
        "schema": SCHEMA,
        "fixture": {
            "input": str(args.input),
            "purpose": (
                "Frozen TTT grammar-ingest evidence fixture; "
                "not an Explorer Tree inventory."
            ),
        },
        "source_objects": source_objects,
        "observations": observations,
        "summary": {
            "source_objects": len(source_objects),
            "observations": len(observations),
            "filename_rules": sorted(
                {
                    row.get("filename_rule_id", "")
                    for row in rows
                }
            ),
            "decoded_fields": sorted(
                {
                    observation["rule_field"]
                    for observation in observations
                }
            ),
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"Fixture rows: {len(rows)}")
    print(f"Source objects: {len(source_objects)}")
    print(f"Observations: {len(observations)}")
    print(
        "Decoded fields: "
        + ", ".join(payload["summary"]["decoded_fields"])
    )
    print(f"Output: {args.output}")


if __name__ == "__main__":
    main()
