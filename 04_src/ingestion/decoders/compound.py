"""Compound-field decoders."""

from .base import Decoder


class CompoundDecoder(Decoder):
    """Generic compound-field decoder.

    Actual decoding techniques will be added incrementally.
    """

    name = "DECOMPOSE"

    def decode(self, value, **kwargs):
        """Split a compound value and map parts to component names."""
        separator = kwargs["separator"]
        components = kwargs.get("components")
        parts = value.split(separator)

        if components is None:
            return parts

        return dict(zip(components, parts))