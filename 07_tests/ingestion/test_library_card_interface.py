from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "04_src"))

from library_card_interface import certify_definition


DEFINITION = (
    ROOT
    / "01_docs"
    / "05_Ingestion"
    / "MusicStewardship_Library_Card_Field_Definitions_RevA.csv"
)


def test_certification_is_idempotent():
    first = certify_definition(
        interface_id="ING-CARD-001",
        revision="A",
        definition_path=DEFINITION,
    )
    second = certify_definition(
        interface_id="ING-CARD-001",
        revision="A",
        definition_path=DEFINITION,
    )

    assert first.certificate == second.certificate
    assert first.field_names == second.field_names
    assert len(first.field_names) == 33
    assert first.revision == "A"


def test_certificate_identifies_revision():
    rev_a = certify_definition(
        interface_id="ING-CARD-001",
        revision="A",
        definition_path=DEFINITION,
    )
    rev_b = certify_definition(
        interface_id="ING-CARD-001",
        revision="B",
        definition_path=DEFINITION,
    )

    assert rev_a.certificate != rev_b.certificate


def test_certificate_identifies_definition_content(tmp_path):
    changed_path = tmp_path / "changed.csv"
    shutil.copyfile(DEFINITION, changed_path)

    text = changed_path.read_text(encoding="utf-8-sig")
    text = text.replace(
        "Public exchange contract revision",
        "Changed contract meaning",
        1,
    )
    changed_path.write_text(text, encoding="utf-8")

    original = certify_definition(
        interface_id="ING-CARD-001",
        revision="A",
        definition_path=DEFINITION,
    )
    changed = certify_definition(
        interface_id="ING-CARD-001",
        revision="A",
        definition_path=changed_path,
    )

    assert original.certificate != changed.certificate


def test_certified_registry_resolves_rev_a():
    from library_card_interface import certified_interface

    contract = certified_interface("A")

    assert contract.interface_id == "ING-CARD-001"
    assert contract.revision == "A"
    assert len(contract.field_names) == 33
    assert contract.certificate.startswith("sha256:")


def test_certified_registry_rejects_unknown_revision():
    import pytest
    from library_card_interface import certified_interface

    with pytest.raises(ValueError, match="Unsupported or uncertified"):
        certified_interface("NOT-CERTIFIED")


def test_certified_registry_rejects_changed_content(tmp_path, monkeypatch):
    import pytest
    import library_card_interface as lci

    changed_path = tmp_path / "changed_rev_a.csv"
    shutil.copyfile(DEFINITION, changed_path)

    text = changed_path.read_text(encoding="utf-8-sig")
    text = text.replace(
        "Public exchange contract revision",
        "Unauthorized changed contract meaning",
        1,
    )
    changed_path.write_text(text, encoding="utf-8")

    original_registration = lci.CERTIFIED_INTERFACES[
        ("ING-CARD-001", "A")
    ]

    monkeypatch.setitem(
        lci.CERTIFIED_INTERFACES,
        ("ING-CARD-001", "A"),
        {
            "definition_path": changed_path,
            "certificate": original_registration["certificate"],
        },
    )

    with pytest.raises(
        ValueError,
        match="Certified Library Card interface content mismatch",
    ):
        lci.certified_interface("A")
