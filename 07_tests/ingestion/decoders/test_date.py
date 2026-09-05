"""Tests for date decoders."""

from ingestion.decoders.date import DateDecoder
from datetime import date


def test_date_decoder_has_expected_name():
    decoder = DateDecoder()

    assert decoder.name == "DATE"

def test_date_decoder_parses_iso_date():
    decoder = DateDecoder()

    result = decoder.decode("2026-09-05")

    from datetime import date

    assert result == date(2026, 9, 5)

def test_date_decoder_preserves_none():
    decoder = DateDecoder()

    result = decoder.decode(None)

    assert result is None

def test_date_decoder_preserves_date_object():
    from datetime import date

    decoder = DateDecoder()
    value = date(2026, 9, 5)

    result = decoder.decode(value)

    assert result is value

def test_date_decoder_converts_datetime_to_date():
    from datetime import datetime

    decoder = DateDecoder()
    value = datetime(2026, 9, 5, 14, 30)

    result = decoder.decode(value)

    assert result == value.date()

def test_date_decoder_rejects_invalid_date():
    decoder = DateDecoder()

    import pytest

    with pytest.raises(ValueError):
        decoder.decode("not-a-date")

def test_date_decoder_parses_iso_datetime_string():
    decoder = DateDecoder()

    result = decoder.decode("2026-09-05T14:30:00")

    assert result == date(2026, 9, 5) 

def test_date_decoder_parses_timezone_datetime_string():
    decoder = DateDecoder()

    result = decoder.decode("2026-09-05T14:30:00-04:00")

    assert result == date(2026, 9, 5)

def test_date_decoder_strips_surrounding_whitespace():
    decoder = DateDecoder()

    result = decoder.decode("  2026-09-05  ")

    assert result == date(2026, 9, 5)