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
    / "CracklingTunes_rosetta_v0.5_regression_sample.csv"
)

ROSETTA = (
    ROOT / "08_tools" / "ingestion" / "mappings"
    / "CT_to_MusicStewardship_Rosetta_v0.5.csv"
)

BINDINGS = (
    ROOT / "08_tools" / "ingestion" / "mappings"
    / "CT_source_field_bindings_v0.5.csv"
)

PUBLIC_MAP = (
    ROOT / "01_docs" / "05_Ingestion"
    / "MusicStewardship_Library_Card_CSV_Field_Translation_Map_RevA.csv"
)

RUN_ID = "CT_ORCHESTRATOR_REGRESSION_V05"


def test_ct_collection_import_v05(tmp_path):
    output_dir = tmp_path / "ct_collection_import"

    subprocess.run(
        [
            sys.executable,
            str(ORCHESTRATOR),
            "--ingest-csv", str(SOURCE),
            "--rosetta", str(ROSETTA),
            "--bindings", str(BINDINGS),
            "--run-id", RUN_ID,
            "--public-map", str(PUBLIC_MAP),
            "--output-dir", str(output_dir),
        ],
        check=True,
    )

    card_path = output_dir / "Library_Cards_RevA.csv"
    report_path = output_dir / "build_report.json"
    observation_path = (
        output_dir / "rosetta_state" / "observations.csv"
    )

    assert card_path.exists()
    assert report_path.exists()
    assert observation_path.exists()

    with card_path.open(
        encoding="utf-8-sig", newline=""
    ) as f:
        cards = list(csv.DictReader(f))

    report = json.loads(
        report_path.read_text(encoding="utf-8")
    )

    assert len(cards) == 8
    assert report["status"] == "PASS"
    assert report["source_records"] == 8
    assert report["library_cards"] == 8
    assert report["cards_missing"] == 0
    assert report["residual_nonempty"] == 8
    assert report["rosetta_run_id"] == RUN_ID
    assert report["rosetta_observations"] == 120

    # Explicit anomalous source genre survives C unchanged.
    nostalgias = next(
        c for c in cards
        if c["title"] == '["Nostalgias"]'
    )

    assert json.loads(nostalgias["genre"]) == ["113"]
    assert json.loads(nostalgias["composer"]) == [
        "Cadícamo, Enrique / Cobián, Juan Carlos"
    ]

    # Duplicate CT identifiers remain separate source records/cards.
    ct1515_a1 = [
        c for c in cards
        if "CT1515-A1" in c["filename"]
    ]

    assert len(ct1515_a1) == 2
    assert {
        tuple(json.loads(c["recording_date"]))
        for c in ct1515_a1
    } == {
        ("1944",),
        ("1944-05-17",),
    }

    # Compound composer representation remains intact.
    noche = next(
        c for c in cards
        if c["title"] == '["Noche de locura"]'
    )

    assert json.loads(noche["composer"]) == [
        "Bahr, Carlos Andres / Sucher, Manuel Bernardo"
    ]
