"""MusicStewardship — D1 deterministic exact entity correspondence.

D1 scope:
* Consume a public Library Card.
* Consume an established entity population.
* Compare explicitly selected fields using exact ordered equality.
* Produce evidence-bearing relationship assertions only for exact matches.
* Do not modify the Library Card.
* Do not perform fuzzy matching, scoring, canonicalization, or recording resolution.

Rev 1 test rule:
    source_context AND source_grouping_label
    must both match exactly and in order.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


D_PROCESSING_REVISION = "d1_exact_entity_match.revA-test"

MATCH_FIELDS = (
    "source_context",
    "source_grouping_label",
)

RELATIONSHIP_TYPE = "corresponds_to"
SUBJECT_TYPE = "library_card"
OBJECT_TYPE = "entity"


def stable_id(prefix: str, *parts: str) -> str:
    material = "|".join(parts)
    digest = hashlib.sha256(material.encode("utf-8")).hexdigest()[:24]
    return f"{prefix}:{digest}"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_library_card(path: Path) -> dict[str, Any]:
    cards = list(__import__("csv").DictReader(
        path.open("r", newline="", encoding="utf-8-sig")
    ))

    if len(cards) != 1:
        raise ValueError(
            f"D1 test expects exactly one Library Card; found {len(cards)}."
        )

    card = cards[0]

    for field in MATCH_FIELDS:
        value = card.get(field, "")
        if value == "":
            return card

        decoded = json.loads(value)
        if not isinstance(decoded, list):
            raise ValueError(
                f"Library Card field {field!r} must contain a JSON array."
            )

        card[field] = decoded

    return card


def compare_field(
    card: dict[str, Any],
    entity: dict[str, Any],
    field: str,
) -> dict[str, Any]:

    observed = card.get(field, [])
    expected = entity.get("attributes", {}).get(field, [])

    matched = observed == expected

    return {
        "field": field,
        "matched": matched,
        "observed_value": observed,
        "entity_value": expected,
    }


def assess_entity(
    card: dict[str, Any],
    entity: dict[str, Any],
) -> dict[str, Any]:

    comparisons = [
        compare_field(card, entity, field)
        for field in MATCH_FIELDS
    ]

    exact_match = all(item["matched"] for item in comparisons)

    return {
        "entity_id": entity["entity_id"],
        "entity_name": entity.get("name", ""),
        "exact_match": exact_match,
        "comparisons": comparisons,
    }


def build_assertion(
    card: dict[str, Any],
    entity: dict[str, Any],
    assessment: dict[str, Any],
) -> dict[str, Any]:

    subject_id = card["source_object_id"]
    object_id = entity["entity_id"]

    assertion_id = stable_id(
        "assertion",
        subject_id,
        RELATIONSHIP_TYPE,
        object_id,
    )

    evidence = []

    for comparison in assessment["comparisons"]:
        field = comparison["field"]

        evidence_id = stable_id(
            "evidence",
            assertion_id,
            field,
        )

        evidence.append(
            {
                "evidence_id": evidence_id,
                "evidence_type": "exact_field_correspondence",
                "evidence_source": "library_card",
                "source_reference": subject_id,
                "observed_value": comparison["observed_value"],
                "method": "exact_ordered_equality",
                "field": field,
                "notes": (
                    f"Library Card {field} exactly matches "
                    f"established entity {object_id}."
                ),
            }
        )

    return {
        "assertion_id": assertion_id,
        "subject_id": subject_id,
        "subject_type": SUBJECT_TYPE,
        "relationship_type": RELATIONSHIP_TYPE,
        "object_id": object_id,
        "object_type": OBJECT_TYPE,
        "assessment_status": "supported",
        "evidence": evidence,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", type=Path, required=True)
    parser.add_argument("--entities", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    card = read_library_card(args.card)
    population = read_json(args.entities)

    if population.get("schema") != "musicstewardship.d_entity_population.v1":
        raise ValueError("Unsupported entity population schema.")

    entities = population.get("entities", [])

    assessments = [
        assess_entity(card, entity)
        for entity in entities
    ]

    assertions = [
        build_assertion(card, entity, assessment)
        for entity, assessment in zip(entities, assessments)
        if assessment["exact_match"]
    ]

    result = {
        "schema": "musicstewardship.d1_relationship_assessment.revA-test",
        "d_processing_revision": D_PROCESSING_REVISION,
        "relationship_rule": {
            "method": "exact_ordered_equality",
            "fields": list(MATCH_FIELDS),
        },
        "input": {
            "library_card_source_object_id": card["source_object_id"],
            "library_card_interface_revision": card.get(
                "library_card_interface_revision", ""
            ),
        },
        "entity_assessments": assessments,
        "assertions": assertions,
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)

    output = args.output_dir / "D1_relationship_assessment.json"
    output.write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"D processing revision : {D_PROCESSING_REVISION}")
    print(f"Entities assessed     : {len(assessments)}")
    print(
        "Exact matches         : "
        f"{sum(a['exact_match'] for a in assessments)}"
    )
    print(f"Assertions created    : {len(assertions)}")
    print(f"Output                : {output}")


if __name__ == "__main__":
    main()
