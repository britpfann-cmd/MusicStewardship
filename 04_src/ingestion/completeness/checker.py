from collections.abc import Mapping


class CompletenessChecker:
    """Verify that source information is accounted for."""

    DESTINATIONS = {
        "COMMON_MODEL",
        "EXTRA_OVERLAY",
        "IGNORED",
        "UNACCOUNTED",
    }

    def check(self, record, field_destinations=None):
        """Classify every record field by its declared destination."""
        if not isinstance(record, Mapping):
            raise TypeError("record must be a mapping")

        if field_destinations is None:
            return record

        if not isinstance(field_destinations, Mapping):
            raise TypeError("field_destinations must be a mapping")

        for field, destination in field_destinations.items():
            if destination not in self.DESTINATIONS:
                raise ValueError(
                    f"Invalid completeness destination: {destination}"
                )

            if field not in record:
                raise ValueError(
                    f"Destination mapping refers to unknown field: {field}"
                )

        return {
            field: field_destinations.get(field, "UNACCOUNTED")
            for field in record
        }

