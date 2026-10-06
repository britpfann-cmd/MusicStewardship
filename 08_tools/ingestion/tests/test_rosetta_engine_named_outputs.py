#!/usr/bin/env python3
from __future__ import annotations

import csv
import sys
import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
ENGINE_PATH = REPO_ROOT / "08_tools" / "ingestion" / "rosetta_engine.py"
sys.path.insert(0, str(ENGINE_PATH.parent))

spec = importlib.util.spec_from_file_location("rosetta_engine", ENGINE_PATH)
engine = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(engine)


def base_rule(**overrides):
    rule = {
        "rule_id": "TEST-001",
        "source_element": "composer",
        "source_field": "COMPOSER",
        "input_semantic_term": "",
        "match_pattern": "",
        "semantic_term": "composer",
        "representation_level": "",
        "information_class": "ASSOCIATED",
        "operation": "EXTRACT",
        "decoder": "regex",
        "decoder_pattern": r"^Com:\s*(.+)$",
        "target_entity": "Source Assertion",
        "target_property": "composer_expression",
        "target_relationship": "",
        "assurance": "CANDIDATE",
        "preserve_source_value": "YES",
        "evidence_basis": "test",
    }
    rule.update(overrides)
    return rule


def test_existing_regex_behavior_unchanged():
    values, status = engine.apply(
        base_rule(),
        "Com: Enrique Delfino",
        {"COMPOSER": "Com: Enrique Delfino"},
    )
    assert status == "EMITTED"
    assert values == ["Enrique Delfino"]


def test_named_regex_emits_standard_observations(tmp_path):
    source_rows = [{
        "source_id": "TangoTunes",
        "relative_path": "sample.aif",
        "COMPOSER": "Aut: Mario Fernando Rada, Com: Enrique Delfino",
    }]
    rules = [base_rule(
        rule_id="TEST-NAMED-001",
        decoder="regex_named",
        decoder_pattern=r"^Aut:\s*(?P<author_expression>.+?),\s*Com:\s*(?P<composer_expression>.+)$",
        semantic_term="",
        target_property="",
    )]
    bindings = []

    result = engine.run(
        source_rows,
        rules,
        bindings,
        tmp_path,
        run_id="TEST_NAMED",
        rosetta_version="test",
        force=True,
    )

    with Path(result["observations"]).open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 2
    by_term = {r["semantic_term"]: r for r in rows}

    assert by_term["author_expression"]["decoded_value"] == "Mario Fernando Rada"
    assert by_term["composer_expression"]["decoded_value"] == "Enrique Delfino"

    for row in rows:
        assert row["source_value"] == "Aut: Mario Fernando Rada, Com: Enrique Delfino"
        assert row["rule_id"] == "TEST-NAMED-001"
        assert row["information_class"] == "ASSOCIATED"
        assert row["decoder"] == "regex_named"
        assert row["target_property"] == row["semantic_term"]


