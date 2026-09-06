"""Completeness reporting."""

from collections.abc import Mapping

class CompletenessReport:
    """Machine-readable completeness result."""

    DESTINATIONS = {
        "COMMON_MODEL",
        "EXTRA_OVERLAY",
        "IGNORED",
        "UNACCOUNTED",
    }

 

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

    @classmethod
    def from_classification(cls, classification):
        """Create a report from field destination classifications."""
        if not isinstance(classification, Mapping):
            raise TypeError("classification must be a mapping")

        for field, destination in classification.items():
            if destination not in cls.DESTINATIONS:
                raise ValueError(
                    f"Invalid completeness destination: {destination}"
                )

        report = cls()

        for field, destination in classification.items():
            if destination == "UNACCOUNTED":
                report.unaccounted.append(field)
            else:
                report.accounted.append(field)

        return report


