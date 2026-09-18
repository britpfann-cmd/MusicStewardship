#!/usr/bin/env python3
"""
MusicStewardship — Source Interpretation v1

Converts preserved Candidate Record evidence into source-semantic
interpretation propositions without performing canonical resolution.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


SCHEMA = "musicstewardship.source_interpretation.v1"

TECHNICAL_METADATA = {
    "bit_rate",
    "bits_per_sample",
    "channel_layout",
    "channels",
    "codec_long_name",
    "codec_name",
    "duration",
    "format_long_name",
    "format_name",
    "sample_rate",
    "size",
}


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def make_interpretation(
    interpretation_id: str,
    source_object_id: str,
    attribute: str,
    value,
    value_type: str,
    supported_by: list[str],
    derivation: str,
    context_used: list[str] | None = None,
    notes: str | None = None,
) -> dict:
    return {
        "interpretation_id": interpretation_id,
        "source_object_id": source_object_id,
        "attribute": attribute,
        "value": value,
        "value_type": value_type,
        "status": "resolved",
        "supported_by": supported_by,
        "context_used": context_used or [],
        "derivation": derivation,
        "notes": notes,
    }


def interpret_record(record: dict, sequence: int) -> list[dict]:
    source_object_id = record["candidate_record_id"]
    observations = record.get("observations", [])

    results = []

    def emit(
        attribute,
        value,
        value_type,
        observation,
        derivation,
        context_used=None,
        notes=None,
    ):
        results.append(
            make_interpretation(
                interpretation_id=(
                    f"interpretation:{sequence:06d}:{len(results) + 1:04d}"
                ),
                source_object_id=source_object_id,
                attribute=attribute,
                value=value,
                value_type=value_type,
                supported_by=[observation["evidence_id"]],
                derivation=derivation,
                context_used=context_used,
                notes=notes,
            )
        )

    directory_observations = [
        obs
        for obs in observations
        if obs.get("evidence_channel") == "directory"
        and obs.get("evidence_type") == "directory.component"
    ]

    filename_observations = [
        obs
        for obs in observations
        if obs.get("evidence_channel") == "filename"
    ]

    # ---------------------------------------------------------------
    # Directory interpretation
    # ---------------------------------------------------------------

    grouping_observations = []

    for obs in directory_observations:
        value = obs.get("raw_value")
        locator = obs.get("source_locator", "")

        if not value:
            continue

        if (
            isinstance(value, str)
            and value.strip().upper().startswith("TANDA")
        ):
            grouping_observations.append(obs)

            emit(
                "source_grouping_label",
                value,
                "source_label",
                obs,
                "classify_explicit_directory_marker",
                notes=(
                    "Explicit source grouping label. "
                    "Not interpreted as a canonical Tanda."
                ),
            )
        else:
            emit(
                "source_context",
                value,
                "source_organizational_label",
                obs,
                "preserve_directory_context",
                notes=f"Preserved from {locator}.",
            )

    # ---------------------------------------------------------------
    # Filename interpretation
    # ---------------------------------------------------------------

    for obs in filename_observations:
        evidence_type = obs.get("evidence_type")
        value = obs.get("raw_value")

        if value is None:
            continue

        if evidence_type == "filename.numeric_component":
            emit(
                "filename_numeric_component",
                value,
                "uninterpreted_source_value",
                obs,
                "preserve_filename_component",
                context_used=[
                    x["evidence_id"]
                    for x in directory_observations
                ],
                notes="No canonical identifier meaning assigned.",
            )

        elif evidence_type == "filename.leading_text":
            emit(
                "filename_leading_text",
                value,
                "uninterpreted_source_value",
                obs,
                "preserve_filename_leading_text",
                context_used=[
                    x["evidence_id"]
                    for x in directory_observations
                ],
                notes="No canonical semantic meaning assigned.",
            )

    # ---------------------------------------------------------------
    # Technical metadata is deliberately not interpreted here.
    #
    # It remains fully preserved in Candidate Record evidence.
    # Descriptive metadata interpretation can be added when a source
    # provides such evidence.
    # ---------------------------------------------------------------

    return results


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build Source Interpretation v1 from Candidate Records."
    )

    parser.add_argument(
        "-input",
        required=True,
        help="Candidate Record JSON",
    )

    parser.add_argument(
        "-o",
        "--output",
        required=True,
        help="Output JSON path; .json is added when omitted",
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    if output_path.suffix.lower() != ".json":
        output_path = output_path.with_suffix(".json")

    payload = load_json(input_path)
    records = payload.get("records", [])

    interpretations = []

    for sequence, record in enumerate(records, start=1):
        interpretations.extend(
            interpret_record(record, sequence)
        )

    output = {
        "schema": SCHEMA,
        "input": str(input_path),
        "candidate_records": len(records),
        "interpretations": interpretations,
        "summary": {
            "interpretation_count": len(interpretations),
            "source_objects_with_interpretations": len(
                {
                    item["source_object_id"]
                    for item in interpretations
                }
            ),
        },
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(
            output,
            f,
            indent=2,
            ensure_ascii=False,
        )
        f.write("\n")

    print(f"Candidate Records: {len(records)}")
    print(f"Interpretations: {len(interpretations)}")
    print(
        "Source Objects with Interpretations: "
        f"{output['summary']['source_objects_with_interpretations']}"
    )
    print(f"Output: {output_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
