"""Regression coverage for Rosetta incremental dependent-rule semantics."""
import csv
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "08_tools" / "ingestion"))
from rosetta_engine import run


def rule(rule_id, element, source_field="", input_term="", semantic_term=""):
    return {
        "rule_id": rule_id, "source_element": element,
        "source_field": source_field, "input_semantic_term": input_term,
        "semantic_term": semantic_term, "operation": "COPY", "decoder": "scalar",
        "target_entity": "Source Assertion", "target_property": "value",
        "target_relationship": "", "representation_level": "source",
        "information_class": "ASSOCIATED", "assurance": "source",
        "preserve_source_value": "YES", "evidence_basis": "source",
    }


def observations(state):
    with (state / "observations.csv").open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def test_skipped_upstream_restores_dependent_input(tmp_path):
    state = tmp_path / "state"
    rows = [{"source_id": "S", "relative_path": "track", "raw": "Tango"}]
    rules = [rule("UP", "raw_element", "raw", semantic_term="decoded_name"),
             rule("DOWN", "derived", input_term="decoded_name")]
    bindings = []
    first = run(rows, rules, bindings, state, run_id="R1")
    second = run(rows, rules, bindings, state, run_id="R2")
    assert (first["processed"], first["new_observations"]) == (2, 2)
    assert (second["processed"], second["skipped"]) == (0, 2)


def test_skipped_upstream_supports_new_downstream_rule(tmp_path):
    state = tmp_path / "state"
    rows = [{"source_id": "S", "relative_path": "track", "raw": "Tango"}]
    up = rule("UP", "raw_element", "raw", semantic_term="decoded_name")
    run(rows, [up], [], state, run_id="R1")
    downstream = rule("DOWN", "derived", input_term="decoded_name")
    result = run(rows, [up, downstream], [], state, run_id="R2")
    assert (result["processed"], result["skipped"], result["new_observations"]) == (1, 1, 1)
    assert observations(state)[-1]["decoded_value"] == "Tango"


def test_removed_input_invalidates_previous_observations(tmp_path):
    state = tmp_path / "state"
    rules = [rule("UP", "raw_element", "raw", semantic_term="decoded_name"),
             rule("DOWN", "derived", input_term="decoded_name")]
    row = {"source_id": "S", "relative_path": "track", "raw": "Tango"}
    run([row], rules, [], state, run_id="R1")
    result = run([{**row, "raw": ""}], rules, [], state, run_id="R2")
    assert result["processed"] == 2
    assert result["new_observations"] == 0
    with (state / "processing_log.csv").open(encoding="utf-8-sig", newline="") as f:
        log = list(csv.DictReader(f))
    assert len([r for r in log if r["run_id"] == "R2" and r["observation_count"] == "0"]) == 2


def test_duplicate_run_id_rejected_before_writing(tmp_path):
    state = tmp_path / "state"
    rows = [{"source_id": "S", "relative_path": "track", "raw": "Tango"}]
    rules = [rule("UP", "raw_element", "raw")]
    run(rows, rules, [], state, run_id="R1")
    with pytest.raises(ValueError, match="run_id already exists"):
        run(rows, rules, [], state, run_id="R1", force=True)
    assert len(observations(state)) == 1
