"""Base decoder interface."""

class Decoder:
    """Base class for reusable transformation techniques."""

    name = "base"

    def decode(self, value, **kwargs):
        raise NotImplementedError
