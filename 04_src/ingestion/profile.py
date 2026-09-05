"""Source profile definitions."""

class SourceProfile:
    """Source-specific semantic and structural knowledge."""

    def __init__(self, source_id, rules=None):
        self.source_id = source_id
        self.rules = rules or []

    def describe(self):
        return {
            "source_id": self.source_id,
            "rule_count": len(self.rules),
        }
