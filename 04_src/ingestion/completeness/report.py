"""Completeness reporting."""

class CompletenessReport:
    """Machine-readable completeness result."""

    def __init__(self):
        self.accounted = []
        self.unaccounted = []
        self.patterns = []

    @property
    def passed(self):
        return not self.unaccounted

    def summary(self):
        return {
            "passed": self.passed,
            "accounted": len(self.accounted),
            "unaccounted": len(self.unaccounted),
            "patterns": len(self.patterns),
        }
