"""Initial ingestion framework smoke tests."""

"""Initial ingestion framework smoke tests."""

from ingestion.engine import IngestionEngine
from ingestion.evidence import EvidenceRecord


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

def test_evidence_record_can_be_created():
    evidence = EvidenceRecord()

    assert evidence is not None   

def test_evidence_record_preserves_source_id():
    source_id = "example-source-001"

    evidence = EvidenceRecord(source_id=source_id)

    assert evidence.source_id == source_id

def test_evidence_record_preserves_values():
    values = {
        "title": "Example",
        "artist": "Test Artist",
    }

    evidence = EvidenceRecord(values=values)

    assert evidence.values is values

def test_evidence_record_preserves_provenance():
    provenance = {
        "source": "example",
        "rule": "copy",
    }

    evidence = EvidenceRecord(provenance=provenance)

    assert evidence.provenance is provenance    

def test_evidence_record_diagnostic():
    source_id = "example-source-001"
    values = {"title": "Example"}
    provenance = {"source": "example", "rule": "copy"}

    evidence = EvidenceRecord(
        source_id=source_id,
        values=values,
        provenance=provenance,
    )

    assert evidence.diagnostic() == {
        "source_id": source_id,
        "values": values,
        "provenance": provenance,
    }    