import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

ORCHESTRATOR = (
    ROOT / "08_tools" / "ingestion"
    / "build_collection_import.py"
)

SOURCE = (
    ROOT / "07_tests" / "ingestion"
    / "ToTango_rosetta_v0.1_regression_sample.csv"
)

ROSETTA = (
    ROOT / "08_tools" / "ingestion" / "mappings"
    / "ToTango_to_MusicStewardship_Rosetta_v0.2.csv"
)

BINDINGS = (
    ROOT / "08_tools" / "ingestion" / "mappings"
    / "ToTango_source_field_bindings.csv"
)

PUBLIC_MAP = (
    ROOT / "01_docs" / "05_Ingestion"
    / "MusicStewardship_Library_Card_CSV_Field_Translation_Map_RevA.csv"
)

RUN_ID = "TOTANGO_ORCHESTRATOR_REGRESSION"


def test_collection_import_rosetta_replay(tmp_path):
    output_dir = tmp_path / "collection_import"

    subprocess.run(
        [
            sys.executable,
            str(ORCHESTRATOR),
            "--ingest-csv", str(SOURCE),
            "--rosetta", str(ROSETTA),
            "--bindings", str(BINDINGS),
            "--run-id", RUN_ID,
            "--public-map", str(PUBLIC_MAP),
            "--interface-revision", "A",
            "--output-dir", str(output_dir),
        ],
        check=True,
    )

    card_path = output_dir / "Library_Cards_RevA.csv"
    report_path = output_dir / "build_report.json"
    observation_path = output_dir / "rosetta_state" / "observations.csv"

    assert card_path.exists()
    assert report_path.exists()
    assert observation_path.exists()

    with card_path.open(encoding="utf-8-sig", newline="") as f:
        cards = list(csv.DictReader(f))

    report = json.loads(report_path.read_text(encoding="utf-8"))

    assert len(cards) == 4
    assert report["status"] == "PASS"
    assert report["source_records"] == 4
    assert report["library_cards"] == 4
    assert report["rosetta_run_id"] == RUN_ID
    assert report["rosetta_observations"] == 34

    # Smoke-check the semantic path through the complete orchestration.
    biagi = next(
        c for c in cards
        if c["filename"] == "Biagi42_La Cumparsita.mp3"
    )
    assert json.loads(biagi["title"]) == ["La Cumparsita"]
    assert json.loads(biagi["recording_date"]) == ["42"]

