"""Clause and comment decoders."""

from .base import Decoder


class ClauseDecoder(Decoder):
    """Extract structured information from clauses."""

    name = "CLAUSE"

    def decode(self, value, **kwargs):
        """Return the clause value unchanged."""
        if value is None:
            return None

        return value.strip()