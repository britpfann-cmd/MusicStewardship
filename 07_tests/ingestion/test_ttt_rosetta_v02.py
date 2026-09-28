import csv
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
INGEST = ROOT / "08_tools" / "ingestion"
sys.path.insert(0, str(INGEST))

from rosetta_engine import run, read_csv


SOURCE = INGEST / "tests" / "TTT_rosetta_engine_v0.2_regression_sample.csv"
MAPPING = INGEST / "mappings" / "TTT_to_MusicStewardship_Rosetta_v0.2.csv"
BINDINGS = INGEST / "mappings" / "TTT_source_field_bindings.csv"


def load_observations(tmp_path):
    rows = read_csv(SOURCE)
    rules = read_csv(MAPPING)
    bindings = read_csv(BINDINGS)

    state = tmp_path / "state"
    result = run(
        rows,
        rules,
        bindings,
        state,
        run_id="REGRESSION",
    )

    assert result["processed"] == 396
    assert result["new_observations"] == 349

    with (state / "observations.csv").open(
        encoding="utf-8-sig", newline=""
    ) as f:
        observations = list(csv.DictReader(f))

    assert observations
    assert all(r["source_value"] for r in observations)
    assert all(r["rule_id"] for r in observations)
    assert all(
        r["information_class"] in {"CORE", "ASSOCIATED", "RESIDUAL"}
        for r in observations
    )

    # Processing outcome is a semantic result, distinct from information class.
    valid_outcomes = {
        "DECODED",
        "DERIVED",
        "PRESERVED",
        "NOT_ATTEMPTED",
        "PARTIAL",
        "UNDECODABLE",
        "CONFLICT",
        "REVIEW",
    }
    valid_reasons = {
        "",
        "OUT_OF_SCOPE",
        "NO_CAPABILITY",
        "DECODER_FAILURE",
        "AMBIGUOUS",
        "CONFLICTING_EVIDENCE",
        "HUMAN_REQUIRED",
        "PRESERVATION",
        "OTHER",
    }

    assert all(r["processing_outcome"] in valid_outcomes for r in observations)
    assert all(r["outcome_reason"] in valid_reasons for r in observations)

    # The v0.2 TTT regression corpus has established normal-processing
    # expectations for the new semantic outcome layer.
    from collections import Counter

    outcome_counts = Counter(r["processing_outcome"] for r in observations)

    assert outcome_counts == {
        "DECODED": 255,
        "DERIVED": 22,
        "PRESERVED": 72,
    }

    # Compound catalog numbers are both decomposed and preserved.
    decomposed = [
        r for r in observations
        if r["rule_id"] == "TTT-MAP-015A"
    ]
    preserved = [
        r for r in observations
        if r["rule_id"] == "TTT-MAP-015B"
    ]

    assert decomposed
    assert all(r["processing_outcome"] == "DECODED" for r in decomposed)

    assert preserved
    assert all(r["processing_outcome"] == "PRESERVED" for r in preserved)
    assert all(r["outcome_reason"] == "PRESERVATION" for r in preserved)

    return observations


def obs(rows, path_part, rule_id=None):
    result = [
        r for r in rows
        if path_part.lower() in r["source_record"].lower()
    ]
    if rule_id:
        result = [r for r in result if r["rule_id"] == rule_id]
    return result


def test_ttt_rosetta_v02_regression(tmp_path):
    rows = load_observations(tmp_path)

    # Native TTT artist grammar.
    assert {
        r["decoded_value"]
        for r in obs(rows, "Pajaro ciego", "TTT-MAP-007A")
    } == {"Aníbal Troilo"}

    assert {
        r["decoded_value"]
        for r in obs(rows, "Pajaro ciego", "TTT-MAP-008A")
    } == {"F. Fiorentino y A. Mandarino"}

    assert {
        r["decoded_value"]
        for r in obs(rows, "Pajaro ciego", "TTT-MAP-008B")
    } == {"F. Fiorentino", "A. Mandarino"}

    assert not obs(
        rows, "Comme il faut", "TTT-MAP-008A"
    ), "Instr. must not become a Person"

    # Embedded Lyrics clause becomes lyricist evidence
    # and derived has_lyrics.
    assert {
        r["decoded_value"]
        for r in obs(rows, "Yo soy el tango", "TTT-MAP-013A")
    } == {"Homero Expósito"}

    assert {
        r["decoded_value"]
        for r in obs(rows, "Yo soy el tango", "TTT-MAP-030A")
    } == {"YES"}

    # Compound identifiers preserve internal syntax.
    ids = {
        r["decoded_value"]
        for r in obs(rows, "Nueve de Julio", "TTT-MAP-015A")
    }
    assert ids == {
        "record=S-5242-A",
        "matrix=621/53",
        "take=1",
    }

    # Comment evidence is decoded without overwriting
    # the source comment.
    assert {
        r["decoded_value"]
        for r in obs(rows, "La cautiva", "TTT-MAP-029C")
    } == {
        "625/54, regression of concert pitch to A4:435Hz"
    }

    assert {
        r["decoded_value"]
        for r in obs(rows, "Inspiracion", "TTT-MAP-029B")
    } == {"Astor Piazzolla"}

    # Parenthetical text remains identity evidence,
    # not a new Person identity.
    assert {
        r["decoded_value"]
        for r in obs(rows, "Racing Club", "TTT-MAP-014A")
    } == {"Julian Porteño"}

