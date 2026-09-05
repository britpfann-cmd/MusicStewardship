"""Date interpretation and abstraction."""

from .base import Decoder


class DateDecoder(Decoder):
    """Decode source date representations."""

    name = "DATE"

    def decode(self, value, **kwargs):
        """Parse an ISO date string into a Python date."""
        from datetime import date, datetime

        if value is None:
            return None

        if isinstance(value, datetime):
            return value.date()

        if isinstance(value, date):
            return value

        value = value.strip()

        try:
            return date.fromisoformat(value)
        except ValueError:
            return datetime.fromisoformat(value).date()