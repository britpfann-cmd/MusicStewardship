import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INGEST = ROOT / "08_tools" / "ingestion"

sys.path.insert(0, str(INGEST))
from rosetta_engine import run, read_csv

SOURCE = (
    ROOT / "07_tests" / "ingestion"
    / "ToTango_rosetta_v0.1_regression_sample.csv"
)
MAPPING = (
    INGEST / "mappings"
    / "ToTango_to_MusicStewardship_Rosetta_v0.2.csv"
)
BINDINGS = (
    INGEST / "mappings"
    / "ToTango_source_field_bindings.csv"
)
PUBLIC_MAP = (
    ROOT / "01_docs" / "05_Ingestion"
    / "MusicStewardship_Library_Card_CSV_Field_Translation_Map_RevA.csv"
)
ASSEMBLER = (
    INGEST / "build_library_cards_from_rosetta.py"
)

RUN_ID = "TOTANGO_COMMON_RECOMBINATION_REGRESSION"


def build_cards(tmp_path):
    rows = read_csv(SOURCE)
    rules = read_csv(MAPPING)
    bindings = read_csv(BINDINGS)

    state = tmp_path / "state"

    result = run(
        rows,
        rules,
        bindings,
        state,
        run_id=RUN_ID,
    )
    assert result["failed"] == 0

    output = tmp_path / "library_cards.csv"
    report = tmp_path / "report.json"

    subprocess.run(
        [
            sys.executable,
            str(ASSEMBLER),
            str(SOURCE),
            "--public-map", str(PUBLIC_MAP),
            "--observations", str(state / "observations.csv"),
            "--run-id", RUN_ID,
            "--output", str(output),
            "--report", str(report),
        ],
        check=True,
    )

    with output.open(encoding="utf-8-sig", newline="") as f:
        cards = list(csv.DictReader(f))

    return {c["filename"]: c for c in cards}


def array_value(card, field):
    return json.loads(card[field]) if card[field] else []


def semantic_evidence(card, property_name):
    evidence = json.loads(card["evidence_summary"])
    return [
        e for e in evidence
        if isinstance(e, dict)
        and e.get("target_property") == property_name
    ]


def test_common_recombination_totango_v02(tmp_path):
    cards = build_cards(tmp_path)

    assert len(cards) == 4

    biagi = cards["Biagi42_La Cumparsita.mp3"]
    dagostino = cards[
        "D'Agostino45Vargas_La cumparista.mp3"
    ]
    firpo = cards[
        "Firpo Orquesta 1916_primeragrabación_La Cumparsita.mp3"
    ]
    anomalous = cards[
        "D'Agostino452Garcia_No aflojes.mp3"
    ]

    # Legitimate Rev A destinations are populated.
    assert array_value(biagi, "title") == ["La Cumparsita"]
    assert array_value(biagi, "recording_date") == ["42"]

    assert array_value(dagostino, "title") == ["La cumparista"]
    assert array_value(dagostino, "recording_date") == ["45"]

    # Unsupported year shapes remain unpromoted.
    assert array_value(firpo, "recording_date") == []
    assert array_value(anomalous, "recording_date") == []

    # Source performer representations must not be coerced into
    # stronger Rev A performer-role assertions.
    for card in cards.values():
        assert array_value(card, "artist") == []
        assert array_value(card, "orchestra_or_album_artist") == []
        assert array_value(card, "singer") == []

    # Nevertheless, decoded source knowledge survives the C boundary.
    principal = semantic_evidence(
        dagostino,
        "principal_performer_representation",
    )
    associated = semantic_evidence(
        dagostino,
        "associated_performer_representation",
    )

    assert [e["decoded_value"] for e in principal] == ["D'Agostino"]
    assert [e["decoded_value"] for e in associated] == ["Vargas"]

    assert principal[0]["rule_id"] == "TOT-CTRL-010"
    assert associated[0]["rule_id"] == "TOT-CTRL-012"


TTT_SOURCE = (
    INGEST / "tests"
    / "TTT_rosetta_engine_v0.2_regression_sample.csv"
)
TTT_MAPPING = (
    INGEST / "mappings"
    / "TTT_to_MusicStewardship_Rosetta_v0.2.csv"
)
TTT_BINDINGS = (
    INGEST / "mappings"
    / "TTT_source_field_bindings.csv"
)
TTT_CANDIDATE_ASSEMBLER = ASSEMBLER
TTT_RUN_ID = "TTT_COMMON_RECOMBINATION_REGRESSION"


def build_ttt_cards(tmp_path):
    rows = read_csv(TTT_SOURCE)
    rules = read_csv(TTT_MAPPING)
    bindings = read_csv(TTT_BINDINGS)

    state = tmp_path / "ttt_state"
    result = run(
        rows,
        rules,
        bindings,
        state,
        run_id=TTT_RUN_ID,
    )

    assert result["failed"] == 0
    assert result["processed"] == 396
    assert result["new_observations"] == 349

    output = tmp_path / "ttt_library_cards.csv"
    report = tmp_path / "ttt_report.json"

    subprocess.run(
        [
            sys.executable,
            str(TTT_CANDIDATE_ASSEMBLER),
            str(TTT_SOURCE),
            "--public-map", str(PUBLIC_MAP),
            "--observations", str(state / "observations.csv"),
            "--run-id", TTT_RUN_ID,
            "--output", str(output),
            "--report", str(report),
        ],
        check=True,
    )

    with output.open(encoding="utf-8-sig", newline="") as f:
        cards = list(csv.DictReader(f))

    assert len(cards) == 12
    return {c["filename"]: c for c in cards}


def test_common_recombination_ttt_v02(tmp_path):
    cards = build_ttt_cards(tmp_path)

    comme = cards["001 - Comme il faut.flac"]

    assert array_value(comme, "title") == ["Comme il faut"]
    assert array_value(comme, "recording_date") == ["1938-07-03"]
    assert array_value(
        comme, "orchestra_or_album_artist"
    ) == ["Aníbal Troilo"]
    assert array_value(comme, "recording_identifier") == [
        "record=7160-A",
        "matrix=9326",
        "take=1",
    ]
    assert array_value(comme, "genre") == ["Tango"]
    assert array_value(comme, "source_album") == [
        "Todos de Aníbal Troilo 1938-1945, Tango Time Travel 13"
    ]
    assert array_value(comme, "composer") == ["Eduardo Arolas"]
    assert array_value(comme, "conductor") == ["Aníbal Troilo"]

    # More-specific performer roles are not manufactured by recombination.
    for card in cards.values():
        assert array_value(card, "artist") == []
        assert array_value(card, "singer") == []

