"""Generic source completeness checker."""

class CompletenessChecker:
    """Verify that source information is accounted for."""

    DESTINATIONS = {
        "COMMON_MODEL",
        "EXTRA_OVERLAY",
        "IGNORED",
        "UNACCOUNTED",
    }

    def check(self, record):
        raise NotImplementedError
