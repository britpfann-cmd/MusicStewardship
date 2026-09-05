"""Initial ingestion framework smoke tests."""

from ingestion.engine import IngestionEngine


def test_ingestion_engine_can_be_created():
    engine = IngestionEngine()

    assert engine is not None

def test_ingestion_engine_preserves_profile():
    profile = object()

    engine = IngestionEngine(profile=profile)

    assert engine.profile is profile

def test_ingestion_engine_preserves_diagnostics():
    diagnostics = object()

    engine = IngestionEngine(diagnostics=diagnostics)

    assert engine.diagnostics is diagnostics
    
def test_ingestion_engine_returns_source():
    engine = IngestionEngine()

    source = {"title": "Example", "artist": "Test Artist"}

    assert engine.ingest(source) == source