"""TEST-EM-001 — Entity Management Gateway verification.

Tests the acceptance criteria of SPEC-EM-001 against the reference
implementation IMPL-EM-001.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys

PROJECT_SRC = Path(__file__).resolve().parents[2] / "04_src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from entity_management import EntityGateway, Observation


class EntityGatewayTests(unittest.TestCase):
    def setUp(self) -> None:
        self.gateway = EntityGateway()

    def tearDown(self) -> None:
        self.gateway.close()

    def observation(self, **kwargs):
        base = dict(
            entity_type="Person",
            source="TEST",
            observed={"name": "Juan Pérez"},
            context={"record": "TEST-001"},
            evidence={"source_id": "TEST-001"},
            interpreted={"name": "Juan Pérez"},
        )
        base.update(kwargs)
        return Observation(**base)

    def test_01_source_observation_is_preserved(self):
        oid = self.gateway.accept_observation(self.observation())
        saved = self.gateway.get_observation(oid)
        self.assertEqual(saved["observed"]["name"], "Juan Pérez")
        self.assertEqual(saved["source"], "TEST")
        self.assertEqual(saved["evidence"]["source_id"], "TEST-001")

    def test_02_existing_entity_receives_additional_evidence(self):
        oid1 = self.gateway.accept_observation(self.observation(
            observed={"name": "Juan Pérez"},
            evidence={"source_id": "A"},
        ))
        eid = self.gateway.create_provisional(oid1)

        oid2 = self.gateway.accept_observation(self.observation(
            observed={"name": "Juan Perez"},
            evidence={"source_id": "B"},
        ))
        aid = self.gateway.associate(oid2, eid)

        self.assertIsNotNone(aid)
        self.assertEqual(self.gateway.get_entity(eid)["status"], "PROVISIONAL")
        self.assertEqual(self.gateway.get_observation(oid1)["evidence"]["source_id"], "A")
        self.assertEqual(self.gateway.get_observation(oid2)["evidence"]["source_id"], "B")

    def test_03_unknown_can_create_provisional_entity(self):
        oid = self.gateway.accept_observation(self.observation(
            observed={"name": "Unknown Person"}
        ))
        eid = self.gateway.create_provisional(oid)
        entity = self.gateway.get_entity(eid)
        self.assertEqual(entity["status"], "PROVISIONAL")
        self.assertTrue(eid.startswith("ENT-"))

    def test_04_insufficient_information_remains_unresolved(self):
        oid = self.gateway.accept_observation(self.observation(
            observed={},
            interpreted={},
        ))
        aid = self.gateway.mark_unresolved(oid, "Insufficient identity evidence")
        self.assertTrue(aid.startswith("ASC-"))
        self.assertEqual(self.gateway.get_observation(oid)["observed"], {})

    def test_05_same_text_can_map_to_different_entities(self):
        oid1 = self.gateway.accept_observation(self.observation(
            observed={"name": "A. Brown"}, evidence={"source_id": "A"}
        ))
        oid2 = self.gateway.accept_observation(self.observation(
            observed={"name": "A. Brown"}, evidence={"source_id": "B"}
        ))
        e1 = self.gateway.create_provisional(oid1)
        e2 = self.gateway.create_provisional(oid2)
        self.assertNotEqual(e1, e2)

    def test_06_different_text_can_map_to_same_entity(self):
        oid1 = self.gateway.accept_observation(self.observation(
            observed={"name": "Carlos Gardel"}
        ))
        eid = self.gateway.create_provisional(oid1)

        oid2 = self.gateway.accept_observation(self.observation(
            observed={"name": "C. Gardel"}
        ))
        self.gateway.associate(oid2, eid)
        self.assertEqual(self.gateway.get_entity(eid)["entity_type"], "Person")

    def test_07_reassignment_preserves_original_evidence(self):
        oid = self.gateway.accept_observation(self.observation(
            evidence={"source_id": "ORIGINAL"}
        ))
        e1 = self.gateway.create_provisional(oid)
        aid = self.gateway.associate(oid, e1, status="ASSOCIATED")

        e2_oid = self.gateway.accept_observation(self.observation(
            observed={"name": "Other Person"}
        ))
        e2 = self.gateway.create_provisional(e2_oid)

        self.gateway.revise_association(
            aid, e2, "REASSIGNED", "Later evidence changed the interpretation"
        )

        self.assertEqual(self.gateway.get_observation(oid)["evidence"]["source_id"], "ORIGINAL")
        self.assertEqual(self.gateway.get_entity(e2)["status"], "PROVISIONAL")

    def test_08_identity_is_not_text_hash(self):
        oid1 = self.gateway.accept_observation(self.observation(
            observed={"name": "Same Name"}
        ))
        oid2 = self.gateway.accept_observation(self.observation(
            observed={"name": "Same Name"}
        ))
        e1 = self.gateway.create_provisional(oid1)
        e2 = self.gateway.create_provisional(oid2)
        self.assertNotEqual(e1, e2)

    def test_09_review_state_preserves_ambiguity(self):
        oid = self.gateway.accept_observation(self.observation(
            observed={"name": "Ambiguous Person"},
            evidence={"candidate_count": 2},
        ))
        self.gateway.mark_review(oid, "Two plausible candidates")
        self.assertEqual(
            self.gateway.get_observation(oid)["evidence"]["candidate_count"], 2
        )

    def test_10_multiple_entity_types_use_same_gateway(self):
        for entity_type in ("Person", "Group", "Song", "Performance"):
            oid = self.gateway.accept_observation(
                self.observation(entity_type=entity_type)
            )
            eid = self.gateway.create_provisional(oid)
            self.assertEqual(self.gateway.get_entity(eid)["entity_type"], entity_type)

    def test_11_current_state_is_separate_from_observation_history(self):
        oid = self.gateway.accept_observation(self.observation())
        eid = self.gateway.create_provisional(oid, {"name": "Current Name"})
        entity = self.gateway.get_entity(eid)
        obs = self.gateway.get_observation(oid)
        self.assertEqual(entity["current_data"]["name"], "Current Name")
        self.assertEqual(obs["observed"]["name"], "Juan Pérez")

    def test_12_invalid_reference_is_rejected(self):
        with self.assertRaises(KeyError):
            self.gateway.associate("OBS-does-not-exist", "ENT-does-not-exist")


if __name__ == "__main__":
    unittest.main(verbosity=2)
