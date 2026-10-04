import csv
from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
INGEST = ROOT / "08_tools" / "ingestion"
sys.path.insert(0, str(INGEST))

from rosetta_engine import run, read_csv


SOURCE = (
    ROOT / "07_tests" / "ingestion"
    / "CracklingTunes_rosetta_v0.5_regression_sample.csv"
)

MAPPING = (
    INGEST / "mappings"
    / "CT_to_MusicStewardship_Rosetta_v0.5.csv"
)

BINDINGS = (
    INGEST / "mappings"
    / "CT_source_field_bindings_v0.5.csv"
)


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
        run_id="CT_REGRESSION_V05",
    )

    assert result["processed"] == 130
    assert result["failed"] == 0
    assert result["new_observations"] == 120

    with (state / "observations.csv").open(
        encoding="utf-8-sig", newline=""
    ) as f:
        observations = list(csv.DictReader(f))

    assert len(observations) == 120
    assert all(r["source_value"] for r in observations)
    assert all(r["rule_id"] for r in observations)
    assert all(
        r["information_class"] in {"CORE", "ASSOCIATED", "RESIDUAL"}
        for r in observations
    )

    return observations


def rule(rows, rule_id):
    return [r for r in rows if r["rule_id"] == rule_id]


def values(rows, rule_id):
    return {r["decoded_value"] for r in rule(rows, rule_id)}


def test_ct_rosetta_v05_regression(tmp_path):
    rows = load_observations(tmp_path)

    counts = Counter(r["rule_id"] for r in rows)

    assert counts == {
        "CT-CTRL-001": 8,
        "CT-CTRL-002": 8,
        "CT-CTRL-003": 8,
        "CT-CTRL-004": 8,
        "CT-CTRL-005": 8,
        "CT-CTRL-006": 8,
        "CT-CTRL-007": 4,
        "CT-CTRL-008": 2,
        "CT-CTRL-009": 8,
        "CT-CTRL-010": 8,
        "CT-CTRL-011": 6,
        "CT-CTRL-012": 8,
        "CT-CTRL-014": 4,
        "CT-CTRL-015": 8,
        "CT-CTRL-019": 8,
        "CT-CTRL-022": 8,
        "CT-CTRL-023": 8,
    }

    # Vocal participant representation is decoded as Person evidence.
    assert values(rows, "CT-CTRL-007") == {
        "Héctor Mauré",
        "Jorge Omar",
        "Robert Gale",
    }

    # Instrumental marker must not become a Person.
    assert values(rows, "CT-CTRL-008") == {"YES"}
    assert all(
        r["target_entity"] == "Performance"
        and r["target_property"] == "instrumental"
        for r in rule(rows, "CT-CTRL-008")
    )

    # Filename CT identifier is source evidence, not source-record identity.
    filename_ids = rule(rows, "CT-CTRL-015")
    assert len(filename_ids) == 8
    assert sum(r["decoded_value"] == "CT1515" for r in filename_ids) == 2
    assert sum(r["decoded_value"] == "CT1515-A1" for r in filename_ids) == 2
    assert sum(r["decoded_value"] == "CT1515-B1" for r in filename_ids) == 2

    # Embedded Catalog # is preserved as the CT-native catalog identifier.
    catalog_ids = rule(rows, "CT-CTRL-019")
    assert len(catalog_ids) == 8
    assert all(
        r["target_entity"] == "Identifier"
        and r["target_property"] == "source_catalog_id"
        for r in catalog_ids
    )

    # CATALOGNUMBER is an independent evidence channel and may contain
    # label/matrix representations rather than the CT identifier.
    assert values(rows, "CT-CTRL-014") == {
        "CT1515-A1",
        "CT1515-B1",
        "Label EG3945, matrix OA93388",
        "Label 1A-0752-B, matrix S-004844",
    }

    # Explicit source genre is preserved unchanged, including anomalies.
    assert values(rows, "CT-CTRL-022") == {"Tango", "113"}

    # Composer representation is preserved intact at C; slash-separated
    # credits are not decomposed into canonical Person identities here.
    composer_values = values(rows, "CT-CTRL-023")

    assert "Varela, Hector / Caruso, Luis Rafael" in composer_values
    assert "Cadícamo, Enrique / Cobián, Juan Carlos" in composer_values
    assert "Bahr, Carlos Andres / Sucher, Manuel Bernardo" in composer_values

    assert all(
        r["target_entity"] == "Person"
        and r["target_property"] == "name"
        for r in rule(rows, "CT-CTRL-023")
    )


def test_ct_identifier_channels_remain_distinct(tmp_path):
    rows = load_observations(tmp_path)

    nost = [
        r for r in rows
        if "Nostalgias" in r["source_record"]
    ]

    by_rule = {
        r["rule_id"]: r["decoded_value"]
        for r in nost
        if r["rule_id"] in {
            "CT-CTRL-014",
            "CT-CTRL-015",
            "CT-CTRL-019",
        }
    }

    assert by_rule == {
        "CT-CTRL-014": "Label EG3945, matrix OA93388",
        "CT-CTRL-015": "CT1901-A1",
        "CT-CTRL-019": "CT1901-A1",
    }

    filename_id = next(r for r in nost if r["rule_id"] == "CT-CTRL-015")
    catalog_id = next(r for r in nost if r["rule_id"] == "CT-CTRL-019")

    assert filename_id["semantic_term"] == "ct_source_identifier"
    assert filename_id["representation_level"] == "source"
    assert catalog_id["semantic_term"] == "ct_source_identifier"
    assert catalog_id["representation_level"] == "source"
