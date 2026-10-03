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

from catalog.catalog_store import CatalogStore, new_id, now


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

OBSERVATION_FIELDS = (
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

    decoded = library_card_import.decode_card(raw_card)

    if decoded.get("library_card_interface_revision") != "A":
        raise ValueError(
            "Unsupported Library Card interface revision: "
            f"{decoded.get('library_card_interface_revision')!r}"
        )

    decoded["d_processing_revision"] = D_PROCESSING_REVISION
    decoded["d_import_interface_revision"] = "A"

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


def add_observation(
    store: CatalogStore,
    *,
    library_card_id: str,
    cataloged_instance_id: str,
    field: str,
    value: Any,
    card: dict[str, Any],
) -> str:
    value_json = json.dumps(value, ensure_ascii=False)

    existing = store.conn.execute(
        """
        SELECT observation_id
        FROM catalog_observations
        WHERE library_card_id = ?
          AND subject_type = 'CATALOGED_INSTANCE'
          AND subject_id = ?
          AND observed_field = ?
          AND observed_value_json = ?
        """,
        (
            library_card_id,
            cataloged_instance_id,
            field,
            value_json,
        ),
    ).fetchone()

    if existing is not None:
        return existing["observation_id"]

    observation_id = new_id("OBS")

    context = {
        "source_object_id": card.get("source_object_id"),
        "source_object_key": card.get("source_object_key"),
        "source_record_revision": card.get("source_record_revision"),
        "c_processing_revision": card.get("c_processing_revision"),
        "d_processing_revision": card.get("d_processing_revision"),
    }

    evidence = {
        "source_context": card.get("source_context", []),
        "evidence_summary": card.get("evidence_summary", []),
        "residual_evidence": card.get("residual_evidence", []),
        "construction_status": card.get("construction_status"),
        "conflicts": card.get("conflicts", []),
        "c_lineage": card.get("c_lineage", []),
    }

    store.conn.execute(
        """
        INSERT INTO catalog_observations (
            observation_id,
            library_card_id,
            subject_type,
            subject_id,
            observed_field,
            observed_value_json,
            interpreted_value_json,
            context_json,
            evidence_json,
            observed_at
        )
        VALUES (?, ?, 'CATALOGED_INSTANCE', ?, ?, ?, NULL, ?, ?, ?)
        """,
        (
            observation_id,
            library_card_id,
            cataloged_instance_id,
            field,
            value_json,
            json.dumps(context, ensure_ascii=False),
            json.dumps(evidence, ensure_ascii=False),
            now(),
        ),
    )

    return observation_id


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

            ci_state = {
                "source_object_id": decoded["source_object_id"],
                "source_object_key": decoded["source_object_key"],
                "entry_type": decoded.get("entry_type"),
                "construction_status": decoded.get("construction_status"),
            }

            ci_id = store.create_cataloged_instance(
                card_id,
                ci_state,
                reason="Initial CatalogedInstance from Rev A Library Card",
            )

            stats["library_cards"] += 1
            stats["cataloged_instances"] += 1

            for field in OBSERVATION_FIELDS:
                for value in populated_values(decoded.get(field)):
                    add_observation(
                        store,
                        library_card_id=card_id,
                        cataloged_instance_id=ci_id,
                        field=field,
                        value=value,
                        card=decoded,
                    )
                    stats["observations"] += 1
                    field_counts[field] += 1

            store.conn.commit()

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
