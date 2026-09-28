import csv
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
INGEST = ROOT / "08_tools" / "ingestion"
sys.path.insert(0, str(INGEST))

from rosetta_engine import run, read_csv


SOURCE = (
    ROOT
    / "07_tests"
    / "ingestion"
    / "ToTango_rosetta_v0.1_regression_sample.csv"
)

MAPPING = (
    INGEST
    / "mappings"
    / "ToTango_to_MusicStewardship_Rosetta_v0.1.csv"
)

BINDINGS = (
    INGEST
    / "mappings"
    / "ToTango_source_field_bindings.csv"
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
        run_id="TOTANGO_REGRESSION",
    )

    assert result["failed"] == 0

    with (state / "observations.csv").open(
        encoding="utf-8-sig",
        newline="",
    ) as f:
        observations = list(csv.DictReader(f))

    assert observations
    assert all(r["source_value"] for r in observations)
    assert all(r["rule_id"] for r in observations)

    return observations


def obs(rows, path_part, source_element=None):
    result = [
        r
        for r in rows
        if path_part.lower() in r["source_record"].lower()
    ]

    if source_element:
        result = [
            r
            for r in result
            if r["source_element"] == source_element
        ]

    return result


def values(rows, path_part, source_element):
    return {
        r["decoded_value"]
        for r in obs(rows, path_part, source_element)
    }


def test_totango_rosetta_v01_regression(tmp_path):
    rows = load_observations(tmp_path)

    # Simple two-part source token.
    assert values(rows, "Biagi42", "artist_token") == {"Biagi42"}
    assert values(rows, "Biagi42", "pre_year_token") == {"Biagi"}
    assert values(rows, "Biagi42", "year_token") == {"42"}
    assert not obs(rows, "Biagi42", "post_year_token")

    # Three-part source token.
    assert values(
        rows,
        "D'Agostino45Vargas",
        "artist_token",
    ) == {"D'Agostino45Vargas"}

    assert values(
        rows,
        "D'Agostino45Vargas",
        "pre_year_token",
    ) == {"D'Agostino"}

    assert values(
        rows,
        "D'Agostino45Vargas",
        "year_token",
    ) == {"45"}

    assert values(
        rows,
        "D'Agostino45Vargas",
        "post_year_token",
    ) == {"Vargas"}

    # Four-digit expression is preserved but must not be
    # misread as the established standalone two-digit grammar.
    assert values(
        rows,
        "Firpo Orquesta 1916",
        "artist_token",
    ) == {"Firpo Orquesta 1916"}

    assert not obs(rows, "Firpo Orquesta 1916", "year_token")
    assert not obs(rows, "Firpo Orquesta 1916", "pre_year_token")
    assert not obs(rows, "Firpo Orquesta 1916", "post_year_token")

    # Longer digit run is likewise preserved, not coerced.
    assert values(
        rows,
        "D'Agostino452Garcia",
        "artist_token",
    ) == {"D'Agostino452Garcia"}

    assert not obs(rows, "D'Agostino452Garcia", "year_token")
    assert not obs(rows, "D'Agostino452Garcia", "pre_year_token")
    assert not obs(rows, "D'Agostino452Garcia", "post_year_token")

