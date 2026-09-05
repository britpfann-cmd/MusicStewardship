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

def test_compound_decoder_preserves_empty_parts():
    decoder = CompoundDecoder()

    result = decoder.decode(
        "Ensemble / ",
        separator=" / ",
    )

    assert result == ["Ensemble", ""]

def test_compound_decoder_ignores_extra_parts():
    decoder = CompoundDecoder()

    result = decoder.decode(
        "Ensemble / Performer / Extra",
        separator=" / ",
        components=["ensemble", "performer"],
    )

    assert result == {
        "ensemble": "Ensemble",
        "performer": "Performer",
    }

def test_compound_decoder_omits_missing_parts():
    decoder = CompoundDecoder()

    result = decoder.decode(
        "Ensemble / Performer",
        separator=" / ",
        components=["ensemble", "performer", "role"],
    )

    assert result == {
        "ensemble": "Ensemble",
        "performer": "Performer",
    }

def test_compound_decoder_handles_value_without_separator():
    decoder = CompoundDecoder()

    result = decoder.decode(
        "Ensemble",
        separator=" / ",
        components=["ensemble", "performer"],
    )

    assert result == {
        "ensemble": "Ensemble",
    }

def test_compound_decoder_handles_empty_value():
    decoder = CompoundDecoder()

    result = decoder.decode(
        "",
        separator=" / ",
        components=["ensemble", "performer"],
    )

    assert result == {
        "ensemble": "",
    }

def test_compound_decoder_preserves_extra_parts():
    decoder = CompoundDecoder()

    result = decoder.decode(
        "Ensemble / Performer / Extra",
        separator=" / ",
        components=["ensemble", "performer"],
    )

    assert result == {
        "ensemble": "Ensemble",
        "performer": "Performer",
    }

def test_compound_decoder_preserves_missing_components():
    decoder = CompoundDecoder()

    result = decoder.decode(
        "Ensemble",
        separator=" / ",
        components=["ensemble", "performer"],
    )

    assert result == {
        "ensemble": "Ensemble",
    }

def test_compound_decoder_handles_empty_value():
    decoder = CompoundDecoder()

    result = decoder.decode(
        "",
        separator=" / ",
        components=["ensemble", "performer"],
    )

    assert result == {
        "ensemble": "",
    }


def test_compound_decoder_strips_parts():
    decoder = CompoundDecoder()

    result = decoder.decode(
        " Ensemble / Performer ",
        separator=" / ",
        components=["ensemble", "performer"],
    )

    assert result == {
        "ensemble": "Ensemble",
        "performer": "Performer",
    }

def test_compound_decoder_preserves_none():
    decoder = CompoundDecoder()

    result = decoder.decode(
        None,
        separator=" / ",
        components=["ensemble", "performer"],
    )

    assert result is None


def test_compound_decoder_accepts_empty_components():
    decoder = CompoundDecoder()

    result = decoder.decode(
        "Ensemble / Performer",
        separator=" / ",
        components=[],
    )

    assert result == {}

