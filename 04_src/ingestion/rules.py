"""Source transformation rule definitions."""

class TransformationRule:
    """Declarative description of a source transformation."""

    def __init__(
        self,
        field,
        operation,
        target=None,
        arguments=None,
    ):
        self.field = field
        self.operation = operation
        self.target = target
        self.arguments = arguments or {}

    def describe(self):
        return {
            "field": self.field,
            "operation": self.operation,
            "target": self.target,
            "arguments": self.arguments,
        }

    def apply(self, value, decoder):
        """Apply the supplied decoder to a value."""
        return decoder.decode(
            value,
            rule=self,
            arguments=self.arguments,
            **self.arguments,
        )