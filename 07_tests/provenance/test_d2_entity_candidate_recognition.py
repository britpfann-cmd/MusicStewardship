from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "08_tools" / "provenance" / "d2_entity_candidate_recognition.py"
OBSERVATIONS = REPO_ROOT / "99_sandbox" / "d2_observations_test.csv"
ENTITIES = REPO_ROOT / "99_sandbox" / "d2_entity_index_test.csv"

OUTPUT = REPO_ROOT / "99_sandbox" / "d2_candidate_results_test.jsonl"
DATABASE = REPO_ROOT / "99_sandbox" / "d2_test_verification.sqlite"


def run_d2() -> list[dict]:
    if OUTPUT.exists():
        OUTPUT.unlink()

    if DATABASE.exists():
        DATABASE.unlink()

    command = [
        sys.executable,
        str(SCRIPT),
        "--observations",
        str(OBSERVATIONS),
        "--entities",
        str(ENTITIES),
        "--output",
        str(OUTPUT),
        "--db",
        str(DATABASE),
    ]

    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, (
        "D2 failed\n"
        f"STDOUT:\n{completed.stdout}\n"
        f"STDERR:\n{completed.stderr}"
    )

    return [
        json.loads(line)
        for line in OUTPUT.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_d2_recognition_contract():
    results = run_d2()

    assert len(results) == 5

    # 1. Composition: one candidate.
    assert results[0]["entity_type"] == "Composition"
    assert results[0]["observed_value"] == "El choclo"
    assert results[0]["recognition_status"] == "ONE_CANDIDATE"
    assert results[0]["candidate_count"] == 1
    assert results[0]["candidates"][0]["entity_id"] == "ENT-COMP-001"

    # 2. Person: one candidate.
    assert results[1]["observed_value"] == "Héctor Mauré"
    assert results[1]["recognition_status"] == "ONE_CANDIDATE"
    assert results[1]["candidates"][0]["entity_id"] == "ENT-PERSON-001"

    # 3. Different observed spelling -> same entity.
    assert results[2]["observed_value"] == "Hector Maure"
    assert results[2]["candidates"][0]["entity_id"] == "ENT-PERSON-001"

    # The source observation remains exactly as observed.
    assert results[2]["observed_value"] != results[2]["candidates"][0]["preferred_name"]
    assert results[2]["observed_value"] == "Hector Maure"

    # 4. Ambiguous recognition remains ambiguous.
    assert results[3]["recognition_status"] == "MULTIPLE_CANDIDATES"
    assert results[3]["candidate_count"] == 2
    assert {
        candidate["entity_id"]
        for candidate in results[3]["candidates"]
    } == {
        "ENT-PERSON-002",
        "ENT-PERSON-003",
    }

    # 5. No candidate.
    assert results[4]["recognition_status"] == "NO_CANDIDATE"
    assert results[4]["candidate_count"] == 0
    assert results[4]["candidates"] == []

    # Provenance survives D2 processing.
    for result in results:
        assert result["source"]
        assert result["collection"]
        assert result["collection_type"]
        assert result["source_record_id"]
        assert result["provenance"]["source"] == result["source"]
        assert result["provenance"]["collection"] == result["collection"]
        assert result["provenance"]["collection_type"] == result["collection_type"]
        assert result["provenance"]["source_record_id"] == result["source_record_id"]


def test_d2_does_not_create_entities_or_associations():
    # run_d2() is intentionally called again so this test is independently
    # executable rather than depending on another test's execution order.
    run_d2()

    db = sqlite3.connect(DATABASE)

    try:
        entity_count = db.execute(
            "SELECT COUNT(*) FROM entities"
        ).fetchone()[0]

        observation_count = db.execute(
            "SELECT COUNT(*) FROM observations"
        ).fetchone()[0]

        association_count = db.execute(
            "SELECT COUNT(*) FROM associations"
        ).fetchone()[0]
    finally:
        db.close()

    assert entity_count == 0
    assert observation_count == 5
    assert association_count == 0


if __name__ == "__main__":
    test_d2_recognition_contract()
    test_d2_does_not_create_entities_or_associations()
    print("D2 verification: PASS")
