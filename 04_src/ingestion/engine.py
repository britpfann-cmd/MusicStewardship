"""Core ingestion engine."""

class IngestionEngine:
    """Orchestrates source ingestion and transformation."""

    def __init__(self, profile=None, diagnostics=None, decoder=None):
        self.profile = profile
        self.diagnostics = diagnostics
        self.decoder = decoder

    def ingest(self, source):
        """Ingest a source record or collection."""
        if self.decoder is None:
            return source

        return self.decoder.decode(
            source,
            profile=self.profile,
            diagnostics=self.diagnostics,
        )