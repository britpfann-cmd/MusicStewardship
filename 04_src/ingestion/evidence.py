"""Source evidence representation."""

class EvidenceRecord:
    """Preserves source information and provenance."""

    def __init__(self, source_id=None, values=None, provenance=None):
        self.source_id = source_id
        self.values = values or {}
        self.provenance = provenance or {}

    def diagnostic(self):
        """Return a diagnostic representation."""
        return {
            "source_id": self.source_id,
            "values": self.values,
            "provenance": self.provenance,
        }
