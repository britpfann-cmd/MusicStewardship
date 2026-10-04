"""Regression tests for the Catalog v0.1 population loader."""

from __future__ import annotations

import csv
import importlib.util
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOADER_PATH = (
    PROJECT_ROOT / "08_tools" / "import" / "catalog_population_loader.py"
)

spec = importlib.util.spec_from_file_location(
    "catalog_population_loader_test",
    LOADER_PATH,
)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Cannot load population loader: {LOADER_PATH}")

loader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(loader)


class CatalogPopulationLoaderTests(unittest.TestCase):
    def write_rev_a_population(self, path: Path) -> None:
        contract = loader.library_card_import.certified_interface("A")
        fieldnames = list(contract.field_names)

        rows = []

        for number, title, date in (
            ("001", "Test Tango One", "1941-01-01"),
            ("002", "Test Tango Two", "1942-02-02"),
            ("003", None, None),
        ):
            row = {field: "" for field in fieldnames}

            row.update(
                {
                    "card_revision": "A",
                    "library_card_interface_revision": "A",
                    "c_processing_revision": "test.builder.revA",
                    "source_object_id": f"TEST-{number}",
                    "source_object_key": f"TestSource:{number}.flac",
                    "source_record_revision": "1",
                    "source_root": "TestSource",
                    "relative_path": f"{number}.flac",
                    "filename": f"{number}.flac",
                    "extension": ".flac",
                    "entry_type": "file",
                    "title": json.dumps([title]) if title else json.dumps([]),
                    "recording_date": json.dumps([date]) if date else json.dumps([]),
                    "source_context": json.dumps(["TEST"]),
                    "evidence_summary": json.dumps(["synthetic regression evidence"]),
                    "residual_evidence": json.dumps([]),
                    "construction_status": "candidate",
                    "conflicts": json.dumps([]),
                    "c_lineage": json.dumps(["TEST-LINEAGE"]),
                }
            )

            for field in contract.array_fields:
                if row[field] == "":
                    row[field] = json.dumps([])

            rows.append(row)

        with path.open("w", newline="", encoding="utf-8-sig") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    def test_repeated_population_load_is_idempotent(self):
        with tempfile.TemporaryDirectory() as temp:
            tempdir = Path(temp)
            csv_path = tempdir / "Library_Cards_RevA.csv"
            db_path = tempdir / "catalog.db"

            self.write_rev_a_population(csv_path)

            first = loader.load_population(csv_path, db_path)
            second = loader.load_population(csv_path, db_path)

            expected = {
                "library_cards": 3,
                "cataloged_instances": 3,
                "cataloged_instance_revisions": 3,
                "observations": 4,
                "recordings": 0,
                "performances": 0,
                "works": 0,
                "associations": 0,
            }

            self.assertEqual(first["database_counts"], expected)
            self.assertEqual(second["database_counts"], expected)

            conn = sqlite3.connect(db_path)
            try:
                active_links = conn.execute(
                    """
                    SELECT COUNT(*)
                    FROM cataloged_instance_evidence
                    WHERE relationship_status = 'ACTIVE'
                    """
                ).fetchone()[0]

                self.assertEqual(active_links, 3)

                current_states = conn.execute(
                    """
                    SELECT state_json
                    FROM current_cataloged_instance_revisions
                    ORDER BY state_json
                    """
                ).fetchall()

                self.assertEqual(len(current_states), 3)

                states = [
                    json.loads(state_json)
                    for (state_json,) in current_states
                ]

                by_source_id = {
                    state["source_object_id"]: state
                    for state in states
                }

                self.assertEqual(
                    by_source_id["TEST-001"]["title"],
                    ["Test Tango One"],
                )
                self.assertEqual(
                    by_source_id["TEST-001"]["recording_date"],
                    ["1941-01-01"],
                )
                self.assertEqual(
                    by_source_id["TEST-002"]["title"],
                    ["Test Tango Two"],
                )
                self.assertEqual(
                    by_source_id["TEST-002"]["recording_date"],
                    ["1942-02-02"],
                )

                # Sparse evidence still establishes a discrete Level-0
                # CatalogedInstance without inventing Level-1 values.
                self.assertEqual(
                    by_source_id["TEST-003"]["source_object_id"],
                    "TEST-003",
                )
                self.assertNotIn("title", by_source_id["TEST-003"])
                self.assertNotIn("recording_date", by_source_id["TEST-003"])

                observation_payloads = conn.execute(
                    """
                    SELECT context_json, evidence_json
                    FROM catalog_observations
                    """
                ).fetchall()

                self.assertEqual(len(observation_payloads), 4)
                for context_json, evidence_json in observation_payloads:
                    self.assertEqual(json.loads(context_json), {})
                    self.assertEqual(json.loads(evidence_json), {})

                preserved_cards = conn.execute(
                    """
                    SELECT DISTINCT lc.card_json
                    FROM cataloged_instance_evidence AS cie
                    JOIN library_cards AS lc
                      ON lc.library_card_id = cie.library_card_id
                    WHERE cie.relationship_status = 'ACTIVE'
                    """
                ).fetchall()

                self.assertEqual(len(preserved_cards), 3)
                for (card_json,) in preserved_cards:
                    card = json.loads(card_json)
                    self.assertEqual(
                        card["evidence_summary"],
                        ["synthetic regression evidence"],
                    )
                    self.assertEqual(
                        card["c_lineage"],
                        ["TEST-LINEAGE"],
                    )
            finally:
                conn.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
