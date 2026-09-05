"""Tests for compound-field decoders."""

from ingestion.decoders.compound import CompoundDecoder


def test_compound_decoder_has_expected_name():
    decoder = CompoundDecoder()

    assert decoder.name == "DECOMPOSE"

def test_compound_decoder_splits_value_by_separator():
    decoder = CompoundDecoder()

    result = decoder.decode(
        "Ensemble / Performer",
        separator=" / ",
    )

    assert result == ["Ensemble", "Performer"]

def test_compound_decoder_maps_components():
    decoder = CompoundDecoder()

    result = decoder.decode(
        "Ensemble / Performer",
        separator=" / ",
        components=["ensemble", "performer"],
    )

    assert result == {
        "ensemble": "Ensemble",
        "performer": "Performer",
    }