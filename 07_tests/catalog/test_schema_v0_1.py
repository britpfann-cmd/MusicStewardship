"""Vertical-slice verification for MusicStewardship Catalog v0.1."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

PROJECT_SRC = Path(__file__).resolve().parents[2] / "04_src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from catalog.catalog_store import CatalogStore


class CatalogV01Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = CatalogStore()

    def tearDown(self) -> None:
        self.store.close()

    def test_01_complete_vertical_slice_preserves_history(self):
        card = {
            "library_card_interface_revision": "A",
            "c_processing_revision": "TEST-C",
            "d_processing_revision": "TEST-D",
            "source_object_id": "SOURCE-001",
            "source_object_key": "collection/example.flac",
            "source_record_revision": "1",
            "title": ["Example Tango"],
            "artist": ["Example Orchestra"],
        }

        card_id = self.store.accept_library_card(card)

        ci_id = self.store.create_cataloged_instance(
            card_id,
            {"title": ["Example Tango"]},
        )

        recording_id = self.store.create_entity(
            "RECORDING",
            {"title": "Example Tango"},
        )
        performance_id = self.store.create_entity("PERFORMANCE")
        work_id = self.store.create_entity(
            "WORK",
            {"title": "Example Tango"},
        )

        self.store.assert_association(
            "CATALOGED_INSTANCE_RECORDING",
            "CATALOGED_INSTANCE",
            ci_id,
            "RECORDING",
            recording_id,
        )

        self.store.assert_association(
            "RECORDING_PERFORMANCE",
            "RECORDING",
            recording_id,
            "PERFORMANCE",
            performance_id,
        )

        old_work_association = self.store.assert_association(
            "PERFORMANCE_WORK",
            "PERFORMANCE",
            performance_id,
            "WORK",
            work_id,
        )

        self.store.add_ci_revision(
            ci_id,
            {
                "title": ["Example Tango"],
                "review": "later interpretation",
            },
            "Later catalog review",
        )

        replacement_work_id = self.store.create_entity(
            "WORK",
            {"title": "Corrected Work"},
        )

        new_work_association = self.store.assert_association(
            "PERFORMANCE_WORK",
            "PERFORMANCE",
            performance_id,
            "WORK",
            replacement_work_id,
            status="PROVISIONAL",
            reason="Later evidence changed work association",
            supersedes=old_work_association,
        )

        revisions = self.store.conn.execute(
            """
            SELECT *
            FROM cataloged_instance_revisions
            WHERE cataloged_instance_id = ?
            ORDER BY revision_number
            """,
            (ci_id,),
        ).fetchall()

        self.assertEqual(len(revisions), 2)
        self.assertEqual(revisions[0]["revision_status"], "HISTORICAL")
        self.assertEqual(revisions[1]["revision_status"], "CURRENT")

        associations = self.store.conn.execute(
            """
            SELECT *
            FROM catalog_associations
            WHERE association_type = 'PERFORMANCE_WORK'
            ORDER BY created_at
            """
        ).fetchall()

        self.assertEqual(len(associations), 2)

        current = self.store.conn.execute(
            """
            SELECT *
            FROM current_catalog_associations
            WHERE association_type = 'PERFORMANCE_WORK'
              AND subject_id = ?
            """,
            (performance_id,),
        ).fetchall()

        self.assertEqual(len(current), 1)
        self.assertEqual(current[0]["association_id"], new_work_association)
        self.assertEqual(current[0]["object_id"], replacement_work_id)

        saved_card = self.store.conn.execute(
            """
            SELECT card_json
            FROM library_cards
            WHERE library_card_id = ?
            """,
            (card_id,),
        ).fetchone()

        self.assertEqual(
            json.loads(saved_card["card_json"])["source_object_key"],
            "collection/example.flac",
        )

        chain = self.store.conn.execute(
            """
            SELECT *
            FROM current_catalog_chain
            WHERE cataloged_instance_id = ?
            """,
            (ci_id,),
        ).fetchone()

        self.assertEqual(chain["recording_id"], recording_id)
        self.assertEqual(chain["performance_id"], performance_id)
        self.assertEqual(chain["work_id"], replacement_work_id)

    def test_current_ci_state_distinguishes_empty_from_missing(self):
        card = {
            "source_object_id": "SOURCE-EMPTY",
            "source_object_key": "collection/empty.flac",
            "source_record_revision": "1",
        }

        card_id = self.store.accept_library_card(card)
        ci_id = self.store.create_cataloged_instance(card_id, state={})

        self.assertEqual(self.store.get_current_ci_state(ci_id), {})
        self.assertIsNone(
            self.store.get_current_ci_state("CI-DOES-NOT-EXIST")
        )
    def test_02_library_card_import_is_idempotent(self):
        card = {
            "source_object_id": "SOURCE-002",
            "source_object_key": "collection/two.flac",
            "source_record_revision": "1",
        }

        first = self.store.accept_library_card(card)
        second = self.store.accept_library_card(card)

        self.assertEqual(first, second)

        count = self.store.conn.execute(
            "SELECT COUNT(*) FROM library_cards"
        ).fetchone()[0]

        self.assertEqual(count, 1)

    def test_03_repeated_card_returns_same_cataloged_instance(self):
        card = {
            "source_object_id": "SOURCE-003",
            "source_object_key": "collection/three.flac",
            "source_record_revision": "1",
        }

        card_id = self.store.accept_library_card(card)

        first_ci = self.store.create_cataloged_instance(
            card_id,
            {"title": ["First interpretation"]},
        )

        second_ci = self.store.create_cataloged_instance(
            card_id,
            {"title": ["Should not create another revision"]},
        )

        self.assertEqual(first_ci, second_ci)

        ci_count = self.store.conn.execute(
            "SELECT COUNT(*) FROM cataloged_instances"
        ).fetchone()[0]

        revision_count = self.store.conn.execute(
            """
            SELECT COUNT(*)
            FROM cataloged_instance_revisions
            WHERE cataloged_instance_id = ?
            """,
            (first_ci,),
        ).fetchone()[0]

        evidence_count = self.store.conn.execute(
            """
            SELECT COUNT(*)
            FROM cataloged_instance_evidence
            WHERE library_card_id = ?
              AND relationship_status = 'ACTIVE'
            """,
            (card_id,),
        ).fetchone()[0]

        self.assertEqual(ci_count, 1)
        self.assertEqual(revision_count, 1)
        self.assertEqual(evidence_count, 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
