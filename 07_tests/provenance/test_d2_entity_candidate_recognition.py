from __future__ import annotations

import csv
import json
import sqlite3
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "08_tools" / "provenance" / "d2_entity_candidate_recognition.py"


def write_d2_inputs(tmp_path: Path) -> tuple[Path, Path]:
    """Reproduce the five recognition cases without reading research artifacts."""
    observations = tmp_path / "observations.csv"
    entities = tmp_path / "entity_index.csv"
    observation_fields = [
        "source", "collection", "collection_type", "source_record_id",
        "entity_type", "observed_value", "context_json", "evidence_json",
    ]
    cases = [
        ("A", "Composition", "El choclo", "compositions", "test fixture"),
        ("A", "Person", "Héctor Mauré", "artists", "test fixture"),
        ("B", "Person", "Hector Maure", "artists", "test variant"),
        ("A", "Person", "Test Ambiguous", "artists", "test ambiguity"),
        ("A", "Composition", "Unknown composition", "compositions", "test no match"),
    ]
    with observations.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(observation_fields)
        for number, (source, entity_type, value, folder, basis) in enumerate(cases, 1):
            writer.writerow([
                f"TestSource-{source}", f"Collection-{source}", "restorer",
                f"OBS-{number:03d}", entity_type, value,
                json.dumps({"folder": folder}), json.dumps({"basis": basis}),
            ])

    entity_fields = [
        "entity_id", "entity_type", "observed_name", "name_source",
        "source_record_id", "association_status", "preferred_name", "short_name",
    ]
    entity_rows = [
        ("ENT-COMP-001", "Composition", "El choclo", "TestSource-A",
         "TEST-001", "confirmed", "El choclo", "El choclo"),
        ("ENT-PERSON-001", "Person", "Héctor Mauré", "TestSource-A",
         "TEST-002", "confirmed", "Héctor Mauré", "Mauré"),
        ("ENT-PERSON-001", "Person", "Hector Maure", "TestSource-B",
         "TEST-003", "confirmed", "Héctor Mauré", "Mauré"),
        ("ENT-PERSON-002", "Person", "Test Ambiguous", "TestSource-A",
         "TEST-004", "confirmed", "Test Ambiguous A", "Ambig A"),
        ("ENT-PERSON-003", "Person", "Test Ambiguous", "TestSource-B",
         "TEST-005", "confirmed", "Test Ambiguous B", "Ambig B"),
    ]
    with entities.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(entity_fields)
        writer.writerows(entity_rows)
    return observations, entities


def run_d2(tmp_path: Path) -> list[dict]:
    observations, entities = write_d2_inputs(tmp_path)
    output = tmp_path / "d2_candidate_results_test.jsonl"
    database = tmp_path / "d2_test_verification.sqlite"

    command = [
        sys.executable,
        str(SCRIPT),
        "--observations",
        str(observations),
        "--entities",
        str(entities),
        "--output",
        str(output),
        "--db",
        str(database),
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
        for line in output.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_d2_recognition_contract(tmp_path: Path):
    results = run_d2(tmp_path)

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


def test_d2_does_not_create_entities_or_associations(tmp_path: Path):
    # run_d2() is intentionally called again so this test is independently
    # executable rather than depending on another test's execution order.
    run_d2(tmp_path)

    db = sqlite3.connect(tmp_path / "d2_test_verification.sqlite")

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
