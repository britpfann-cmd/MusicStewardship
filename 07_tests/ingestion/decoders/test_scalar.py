"""Tests for scalar decoders."""

from ingestion.decoders.scalar import CopyDecoder
from ingestion.decoders.base import Decoder


def test_copy_decoder_returns_value():
    decoder = CopyDecoder()

    assert decoder.decode("hello") == "hello"


def test_copy_decoder_preserves_none():
    decoder = CopyDecoder()

    assert decoder.decode(None) is None

def test_copy_decoder_preserves_non_string_value():
    decoder = CopyDecoder()

    value = 12345

    assert decoder.decode(value) == value

def test_copy_decoder_accepts_kwargs():
    decoder = CopyDecoder()

    assert decoder.decode("hello", source_field="title") == "hello"  

def test_base_decoder_is_not_implemented():
    decoder = Decoder()

    try:
        decoder.decode("hello")
    except NotImplementedError:
        pass
    else:
        raise AssertionError("Base Decoder.decode() should not be implemented")       