import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "04_src"))

from catalog.catalog_store import CatalogStore


MODULE_PATH = ROOT / "08_tools" / "catalog" / "catalog_reconciliation.py"
SPEC = importlib.util.spec_from_file_location(
    "catalog_reconciliation",
    MODULE_PATH,
)
reconciliation = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(reconciliation)


def test_create_provisional_recording_from_explicit_decision():
    store = CatalogStore()

    card_ids = []
    ci_ids = []

    for number in (1, 2):
        card = {
            "source_object_id": f"SOURCE-{number}",
            "source_object_key": f"collection/{number}.flac",
            "source_record_revision": "1",
        }
        card_id = store.accept_library_card(card)
        ci_id = store.create_cataloged_instance(
            card_id,
            state={"title": ["Example Tango"]},
        )
        card_ids.append(card_id)
        ci_ids.append(ci_id)

    before = store.conn.execute(
        "SELECT COUNT(*) FROM recordings"
    ).fetchone()[0]
    assert before == 0

    result = reconciliation.create_provisional_recording(
        store,
        cataloged_instance_ids=ci_ids,
        reason="Explicit review of candidate evidence",
        evidence={
            "decision_basis": "manual_review",
            "candidate_analysis": "test fixture",
        },
    )

    assert result["status"] == "PROVISIONAL"
    assert result["cataloged_instance_ids"] == ci_ids
    assert len(result["association_ids"]) == 2

    recordings = store.conn.execute(
        """
        SELECT recording_id, status
        FROM recordings
        """
    ).fetchall()

    assert len(recordings) == 1
    assert recordings[0]["recording_id"] == result["recording_id"]
    assert recordings[0]["status"] == "PROVISIONAL"

    associations = store.conn.execute(
        """
        SELECT subject_id, object_id, status, reason, evidence_json
        FROM current_catalog_associations
        WHERE association_type = 'CATALOGED_INSTANCE_RECORDING'
        ORDER BY subject_id
        """
    ).fetchall()

    assert len(associations) == 2
    assert {row["subject_id"] for row in associations} == set(ci_ids)
    assert {
        row["object_id"] for row in associations
    } == {result["recording_id"]}
    assert {row["status"] for row in associations} == {"PROVISIONAL"}
    assert {
        row["reason"] for row in associations
    } == {"Explicit review of candidate evidence"}

    store.close()



def test_provisional_recording_rolls_back_on_association_failure():
    store = CatalogStore()

    card_ids = []
    ci_ids = []

    for number in (1, 2):
        card_id = store.accept_library_card(
            {
                "source_object_id": f"ROLLBACK-SOURCE-{number}",
                "source_object_key": f"rollback/{number}.flac",
                "source_record_revision": "1",
            }
        )
        ci_ids.append(
            store.create_cataloged_instance(
                card_id,
                state={"title": ["Rollback Tango"]},
            )
        )
        card_ids.append(card_id)

    original_assert_association = store.assert_association
    call_count = 0

    def fail_on_second_association(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 2:
            raise RuntimeError("Deliberate second-association failure")
        return original_assert_association(*args, **kwargs)

    store.assert_association = fail_on_second_association

    try:
        reconciliation.create_provisional_recording(
            store,
            cataloged_instance_ids=ci_ids,
            reason="Rollback test",
            evidence={"test": "atomicity"},
        )
        assert False, "Expected deliberate reconciliation failure"
    except RuntimeError as exc:
        assert str(exc) == "Deliberate second-association failure"

    assert store.conn.execute(
        "SELECT COUNT(*) FROM recordings"
    ).fetchone()[0] == 0

    assert store.conn.execute(
        """
        SELECT COUNT(*)
        FROM catalog_associations
        WHERE association_type = 'CATALOGED_INSTANCE_RECORDING'
        """
    ).fetchone()[0] == 0

    store.close()
