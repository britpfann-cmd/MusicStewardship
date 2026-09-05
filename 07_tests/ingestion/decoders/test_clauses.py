"""Tests for clause decoders."""

from ingestion.decoders.clauses import ClauseDecoder


def test_clause_decoder_has_expected_name():
    decoder = ClauseDecoder()

    assert decoder.name == "CLAUSE"


def test_clause_decoder_returns_value():
    decoder = ClauseDecoder()

    result = decoder.decode("Original source clause")

    assert result == "Original source clause"

def test_clause_decoder_preserves_none():
    decoder = ClauseDecoder()

    result = decoder.decode(None)

    assert result is None

def test_clause_decoder_strips_surrounding_whitespace():
    decoder = ClauseDecoder()

    result = decoder.decode("  Original source clause  ")

    assert result == "Original source clause"

def test_clause_decoder_preserves_internal_whitespace():
    decoder = ClauseDecoder()

    result = decoder.decode("Original   source clause")

    assert result == "Original   source clause"

def test_clause_decoder_accepts_kwargs():
    decoder = ClauseDecoder()

    result = decoder.decode(
        "Original source clause",
        profile="example",
        diagnostics="example",
    )

    assert result == "Original source clause"

def test_clause_decoder_preserves_empty_string():
    decoder = ClauseDecoder()

    result = decoder.decode("")

    assert result == ""

def test_clause_decoder_converts_whitespace_only_to_empty_string():
    decoder = ClauseDecoder()

    result = decoder.decode("   ")

    assert result == ""