"""Compound-field decoders."""

from .base import Decoder


class CompoundDecoder(Decoder):
    """Generic compound-field decoder.

    Actual decoding techniques will be added incrementally.
    """

    name = "DECOMPOSE"

    def decode(self, value, **kwargs):
        raise NotImplementedError
