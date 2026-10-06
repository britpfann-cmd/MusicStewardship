"""Load Rev A Library Cards into the MusicStewardship Catalog v0.1.

This is a population loader, not an identity resolver.

It:
* validates the Rev A Library Card structural contract,
* decodes the established public CSV representation,
* preserves each decoded Library Card,
* creates one CatalogedInstance for each accepted source card,
* harvests populated musical/source-description values as observations.

It does NOT:
* canonicalize names,
* deduplicate entities,
* create Recording / Performance / Work identities,
* choose among identity candidates,
* discard sparse or residual source evidence.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "04_src"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from catalog.catalog_store import CatalogStore


IMPORTER_PATH = PROJECT_ROOT / "08_tools" / "import" / "library_card_import.py"

spec = importlib.util.spec_from_file_location(
    "library_card_import_rev_a",
    IMPORTER_PATH,
)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Cannot load Library Card importer: {IMPORTER_PATH}")

library_card_import = importlib.util.module_from_spec(spec)
spec.loader.exec_module(library_card_import)


D_PROCESSING_REVISION = "catalog_population_loader.v0.1"

CURRENT_STATE_FIELDS = (
    "title",
    "artist",
    "orchestra_or_album_artist",
    "singer",
    "recording_identifier",
    "recording_date",
    "genre",
    "style",
    "source_album",
    "composer",
    "conductor",
)

OBSERVATION_FIELDS = (
    *CURRENT_STATE_FIELDS,
    "filename_leading_text_candidate",
)


def validate_and_decode(raw_card: dict[str, str]) -> dict[str, Any]:
    checks = library_card_import.verify_standard(raw_card)

    failures = [
        (field, detail)
        for field, result, detail in checks
        if result == "FAIL"
    ]

    if failures:
        detail = "; ".join(f"{field}: {message}" for field, message in failures)
        raise ValueError(f"Library Card structural validation failed: {detail}")

    contract = library_card_import.contract_for_card(raw_card)
    decoded = library_card_import.decode_card(raw_card)

    decoded["d_processing_revision"] = D_PROCESSING_REVISION
    decoded["d_import_interface_revision"] = contract.revision

    return decoded


def populated_values(value: Any) -> list[Any]:
    if value is None:
        return []

    if isinstance(value, list):
        return [
            item
            for item in value
            if item is not None and str(item).strip() != ""
        ]

    if str(value).strip() == "":
        return []

    return [value]


def rosetta_level2_observations(
    evidence_summary: Any,
) -> list[dict[str, Any]]:
    """Return canonical Level-2 observations preserved by Rosetta."""
    result = []

    for item in populated_values(evidence_summary):
        if not isinstance(item, dict):
            continue

        field = (
            str(item.get("semantic_term") or "").strip()
            or str(item.get("target_property") or "").strip()
        )
        value = item.get("decoded_value")

        if not field or not populated_values(value):
            continue

        result.append(
            {
                "field": field,
                "observed_value": value,
                "context": {
                    key: item.get(key)
                    for key in (
                        "target_entity",
                        "target_property",
                        "target_relationship",
                        "representation_level",
                    )
                    if item.get(key) not in (None, "")
                },
                "evidence": {
                    key: item.get(key)
                    for key in (
                        "rule_id",
                        "source_value",
                        "assurance",
                        "evidence_basis",
                    )
                    if item.get(key) not in (None, "")
                },
            }
        )

    return result

def load_population(
    csv_path: Path,
    db_path: Path,
) -> dict[str, Any]:
    raw_cards = library_card_import.read_csv_table(csv_path)

    if not raw_cards:
        raise ValueError(f"No Library Card records found: {csv_path}")

    store = CatalogStore(db_path)

    stats: Counter[str] = Counter()
    field_counts: Counter[str] = Counter()

    try:
        for raw_card in raw_cards:
            decoded = validate_and_decode(raw_card)

            card_id = store.accept_library_card(decoded)

            # Level 0 is structural: the persistent CatalogedInstance,
            # its active evidence relationship, and the preserved Library
            # Card establish acceptance and provenance. Level-0 values do
            # not need to be duplicated into operational state.
            ci_state = {}

            # Level 1: initial usable interpretation. Begin with whatever
            # obvious/likely catalog values arrived on the Library Card.
            # Missing values do not prevent catalog admission; later
            # discovery and reconciliation may revise this current state.
            for field in CURRENT_STATE_FIELDS:
                values = populated_values(decoded.get(field))
                if values:
                    ci_state[field] = values

            ci_id = store.create_cataloged_instance(
                card_id,
                ci_state,
                reason="Initial CatalogedInstance from Rev A Library Card",
            )

            stats["library_cards"] += 1
            stats["cataloged_instances"] += 1

            for field in OBSERVATION_FIELDS:
                for value in populated_values(decoded.get(field)):
                    store.add_observation(
                        library_card_id=card_id,
                        subject_type="CATALOGED_INSTANCE",
                        subject_id=ci_id,
                        field=field,
                        observed_value=value,
                        commit=False,
                    )
                    stats["observation_attempts"] += 1

            # Level 2: materialize structured Rosetta evidence generically.
            # Semantic interpretation belongs to Rosetta; this loader carries
            # canonical observations forward without source-specific knowledge.
            for observation in rosetta_level2_observations(
                decoded.get("evidence_summary")
            ):
                field = observation["field"]
                value = observation["observed_value"]

                store.add_observation(
                    library_card_id=card_id,
                    subject_type="CATALOGED_INSTANCE",
                    subject_id=ci_id,
                    field=field,
                    observed_value=value,
                    context=observation["context"],
                    evidence=observation["evidence"],
                    commit=False,
                )
                stats["observation_attempts"] += 1
            store.conn.commit()

        field_counts = Counter(
            {
                row[0]: row[1]
                for row in store.conn.execute(
                    """
                    SELECT observed_field, COUNT(*)
                    FROM catalog_observations
                    GROUP BY observed_field
                    """
                ).fetchall()
            }
        )

        db_counts = {
            "library_cards": store.conn.execute(
                "SELECT COUNT(*) FROM library_cards"
            ).fetchone()[0],
            "cataloged_instances": store.conn.execute(
                "SELECT COUNT(*) FROM cataloged_instances"
            ).fetchone()[0],
            "cataloged_instance_revisions": store.conn.execute(
                "SELECT COUNT(*) FROM cataloged_instance_revisions"
            ).fetchone()[0],
            "observations": store.conn.execute(
                "SELECT COUNT(*) FROM catalog_observations"
            ).fetchone()[0],
            "recordings": store.conn.execute(
                "SELECT COUNT(*) FROM recordings"
            ).fetchone()[0],
            "performances": store.conn.execute(
                "SELECT COUNT(*) FROM performances"
            ).fetchone()[0],
            "works": store.conn.execute(
                "SELECT COUNT(*) FROM works"
            ).fetchone()[0],
            "associations": store.conn.execute(
                "SELECT COUNT(*) FROM catalog_associations"
            ).fetchone()[0],
        }

    finally:
        store.close()

    return {
        "input": str(csv_path),
        "database": str(db_path),
        "processing_revision": D_PROCESSING_REVISION,
        "loaded": dict(stats),
        "observation_fields": dict(sorted(field_counts.items())),
        "database_counts": db_counts,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    args.db.parent.mkdir(parents=True, exist_ok=True)

    result = load_population(args.csv, args.db)

    text = json.dumps(result, indent=2, ensure_ascii=False)

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(text + "\n", encoding="utf-8")

    print(text)


if __name__ == "__main__":
    main()





