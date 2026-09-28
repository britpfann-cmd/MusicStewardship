from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "04_src"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from entity_management.entity_gateway import EntityGateway, Observation


INDEX_FIELDS = {
    "entity_id",
    "entity_type",
    "observed_name",
    "name_source",
    "source_record_id",
    "association_status",
    "preferred_name",
    "short_name",
}

OBSERVATION_FIELDS = {
    "source",
    "collection",
    "collection_type",
    "source_record_id",
    "entity_type",
    "observed_value",
    "context_json",
    "evidence_json",
}


def load_entity_index(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)

        if not reader.fieldnames:
            raise ValueError(f"Entity index has no header: {path}")

        missing = INDEX_FIELDS - set(reader.fieldnames)
        if missing:
            raise ValueError(
                f"Entity index missing required fields: {sorted(missing)}"
            )

        return list(reader)


def load_observations(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)

        if not reader.fieldnames:
            raise ValueError(f"Observation file has no header: {path}")

        missing = OBSERVATION_FIELDS - set(reader.fieldnames)
        if missing:
            raise ValueError(
                f"Observation file missing required fields: {sorted(missing)}"
            )

        return list(reader)


def parse_json_field(value: str, field_name: str) -> dict[str, Any]:
    if not value:
        return {}

    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"{field_name} is not valid JSON: {value!r}"
        ) from exc

    if not isinstance(parsed, dict):
        raise ValueError(f"{field_name} must contain a JSON object")

    return parsed


def recognize_candidates(
    entity_index: list[dict[str, str]],
    entity_type: str,
    observed_value: str,
) -> list[dict[str, Any]]:
    """
    D2 recognition rule, deliberately conservative.

    entity_type and observed_name must match exactly.

    Recognition is not resolution. Multiple matching entities remain
    multiple candidates.
    """
    candidates: list[dict[str, Any]] = []

    for row in entity_index:
        if row["entity_type"] != entity_type:
            continue

        if row["association_status"].strip().upper() == "REJECTED":
            continue

        if row["observed_name"] != observed_value:
            continue

        candidates.append(
            {
                "entity_id": row["entity_id"],
                "entity_type": row["entity_type"],
                "observed_name": row["observed_name"],
                "name_source": row["name_source"],
                "source_record_id": row["source_record_id"],
                "association_status": row["association_status"],
                "preferred_name": row["preferred_name"],
                "short_name": row["short_name"],
                "recognition_basis": {
                    "method": "exact_observed_name",
                    "entity_type_exact": True,
                    "observed_name_exact": True,
                },
            }
        )

    return candidates


def process_observation(
    gateway: EntityGateway,
    row: dict[str, str],
    entity_index: list[dict[str, str]],
) -> dict[str, Any]:

    context = parse_json_field(row["context_json"], "context_json")
    evidence = parse_json_field(row["evidence_json"], "evidence_json")

    observation = Observation(
        entity_type=row["entity_type"],
        source=row["source"],
        observed={
            "value": row["observed_value"],
            "source_record_id": row["source_record_id"],
        },
        context={
            "collection": row["collection"],
            "collection_type": row["collection_type"],
            **context,
        },
        evidence=evidence,
    )

    observation_id = gateway.accept_observation(observation)

    candidates = recognize_candidates(
        entity_index=entity_index,
        entity_type=row["entity_type"],
        observed_value=row["observed_value"],
    )

    if not candidates:
        status = "NO_CANDIDATE"
    elif len(candidates) == 1:
        status = "ONE_CANDIDATE"
    else:
        status = "MULTIPLE_CANDIDATES"

    return {
        "observation_id": observation_id,
        "entity_type": row["entity_type"],
        "observed_value": row["observed_value"],
        "source": row["source"],
        "collection": row["collection"],
        "collection_type": row["collection_type"],
        "source_record_id": row["source_record_id"],
        "recognition_status": status,
        "candidate_count": len(candidates),
        "candidates": candidates,
        "provenance": {
            "source": row["source"],
            "collection": row["collection"],
            "collection_type": row["collection_type"],
            "source_record_id": row["source_record_id"],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="D2 entity candidate recognition"
    )
    parser.add_argument("--observations", type=Path, required=True)
    parser.add_argument("--entities", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--db",
        type=Path,
        default=Path(":memory:"),
        help="SQLite database path; default is in-memory",
    )

    args = parser.parse_args()

    entity_index = load_entity_index(args.entities)
    observations = load_observations(args.observations)

    db_path = ":memory:" if str(args.db) == ":memory:" else str(args.db)

    gateway = EntityGateway(db_path=db_path)

    args.output.parent.mkdir(parents=True, exist_ok=True)

    with args.output.open("w", encoding="utf-8", newline="") as fh:
        for row in observations:
            result = process_observation(
                gateway=gateway,
                row=row,
                entity_index=entity_index,
            )
            fh.write(json.dumps(result, ensure_ascii=False) + "\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
