from __future__ import annotations

import csv
import importlib.util
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "04_src"))

from library_card_interface import certified_interface


PRODUCER = (
    ROOT
    / "08_tools"
    / "ingestion"
    / "build_library_cards_from_rosetta.py"
)

MAP = (
    ROOT
    / "01_docs"
    / "05_Ingestion"
    / "MusicStewardship_Library_Card_CSV_Field_Translation_Map_RevA.csv"
)


spec = importlib.util.spec_from_file_location("library_card_rosetta_producer", PRODUCER)
producer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(producer)


def read_map():
    with MAP.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_map(path, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def test_rev_a_translation_map_conforms_to_certified_contract():
    contract = certified_interface("A")
    rows = producer.validate_public_map(MAP, contract)

    assert len(rows) == 33


@pytest.mark.parametrize(
    ("column", "bad_value"),
    [
        ("interface_revision", "B"),
        ("public_field", "not_the_certified_field"),
        ("cardinality", "0..n"),
        ("required", "no"),
    ],
)
def test_translation_map_contract_mismatch_is_rejected(
    tmp_path, column, bad_value
):
    contract = certified_interface("A")
    rows = read_map()
    rows[0][column] = bad_value

    altered = tmp_path / "altered_map.csv"
    write_map(altered, rows)

    with pytest.raises(ValueError, match=column):
        producer.validate_public_map(altered, contract)


def test_translation_map_field_count_mismatch_is_rejected(tmp_path):
    contract = certified_interface("A")
    rows = read_map()[:-1]

    altered = tmp_path / "short_map.csv"
    write_map(altered, rows)

    with pytest.raises(ValueError, match="field count"):
        producer.validate_public_map(altered, contract)
