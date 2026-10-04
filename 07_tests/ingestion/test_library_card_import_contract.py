from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "04_src"))

from library_card_interface import certified_interface

IMPORTER_PATH = ROOT / "08_tools" / "import" / "library_card_import.py"

spec = importlib.util.spec_from_file_location(
    "library_card_import",
    IMPORTER_PATH,
)
importer = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(importer)


def valid_rev_a_card():
    contract = certified_interface("A")
    card = {}

    for row in contract.fields:
        field = row["Field"]
        cardinality = row["Cardinality"]

        if cardinality in {"0..n", "1..n"}:
            card[field] = '["test"]' if cardinality == "1..n" else "[]"
        elif cardinality == "1":
            card[field] = "test"
        else:
            card[field] = ""

    card["library_card_interface_revision"] = "A"
    return card


def test_rev_a_standard_validation_uses_public_shape():
    card = valid_rev_a_card()

    checks = importer.verify_standard(card)

    assert checks
    assert not [row for row in checks if row[1] == "FAIL"]


def test_rev_a_decode_preserves_interface_revision():
    card = valid_rev_a_card()

    decoded = importer.decode_card(card)

    assert decoded["library_card_interface_revision"] == "A"


def test_consumer_rejects_uncertified_interface_revision():
    import pytest

    card = valid_rev_a_card()
    card["library_card_interface_revision"] = "NOT-CERTIFIED"

    with pytest.raises(ValueError, match="Unsupported or uncertified"):
        importer.decode_card(card)


def test_consumer_independently_resolves_certified_revision():
    card = valid_rev_a_card()

    contract = importer.contract_for_card(card)

    assert contract.revision == "A"
    assert (
        contract.certificate
        == "sha256:a06b0925aee1195a71ad885ab280675173a968432d989b4b1806136bdd70a65e"
    )


def test_consumer_rejects_undeclared_field():
    import pytest

    card = valid_rev_a_card()
    card["undeclared_test_field"] = "not part of revision A"

    with pytest.raises(ValueError, match="undeclared fields"):
        importer.decode_card(card)


def test_consumer_rejects_missing_declared_field():
    import pytest

    card = valid_rev_a_card()
    del card["source_suffix"]

    with pytest.raises(ValueError, match="missing certified fields"):
        importer.decode_card(card)
