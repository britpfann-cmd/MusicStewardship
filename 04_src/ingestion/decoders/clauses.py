"""Clause and comment decoders."""

from .base import Decoder


class ClauseDecoder(Decoder):
    """Extract structured information from clauses."""

    name = "CLAUSE"

    def decode(self, value, **kwargs):
        raise NotImplementedError
