"""Date interpretation and abstraction."""

from .base import Decoder


class DateDecoder(Decoder):
    """Decode source date representations."""

    name = "DATE"

    def decode(self, value, **kwargs):
        raise NotImplementedError
