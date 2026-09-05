"""Scalar decoders."""

from .base import Decoder


class CopyDecoder(Decoder):
    """Directly copy a source value."""

    name = "COPY"

    def decode(self, value, **kwargs):
        return value
