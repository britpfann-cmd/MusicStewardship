"""Rosetta observation preservation checks with isolated processing state."""

import csv
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rosetta_engine import run


@pytest.fixture
def observation_rows(tmp_path):
    source_rows = [{
        "source_id": "TEST_SOURCE",
        "relative_path": "sample.flac",
        "title": "El choclo",
        "composer": "Ángel Villoldo",
        "note": "Uninterpreted source note",
    }]
    rules = [
        {
            "rule_id": f"TEST-{information_class}",
            "source_element": field,
            "source_field": field,
            "semantic_term": field,
            "information_class": information_class,
            "operation": "COPY",
            "decoder": "scalar",
            "target_entity": "Source Assertion",
            "target_property": field,
            "target_relationship": "",
            "assurance": "OBSERVED",
            "preserve_source_value": "YES",
            "evidence_basis": "deterministic test fixture",
        }
        for field, information_class in (
            ("title", "CORE"),
            ("composer", "ASSOCIATED"),
            ("note", "RESIDUAL"),
        )
    ]
    result = run(source_rows, rules, [], tmp_path / "state", run_id="TEST_PRESERVATION")
    with Path(result["observations"]).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def test_observations_preserve_source_value_and_rule_provenance(observation_rows):
    rows = observation_rows
    assert rows, 'No observations emitted'
    assert all(r['source_value'] for r in rows), 'Source value was lost'
    assert all(r['rule_id'] for r in rows), 'Rule provenance missing'
    assert all(r['information_class'] in {'CORE','ASSOCIATED','RESIDUAL'} for r in rows)
