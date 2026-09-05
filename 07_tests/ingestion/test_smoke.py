"""Initial ingestion framework smoke tests."""

"""Initial ingestion framework smoke tests."""

from ingestion.engine import IngestionEngine
from ingestion.evidence import EvidenceRecord
from ingestion.decoders.base import Decoder
from ingestion.decoders.scalar import CopyDecoder


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

def test_ingestion_engine_preserves_decoder():
    decoder = object()

    engine = IngestionEngine(decoder=decoder)

    assert engine.decoder is decoder  

def test_ingestion_engine_uses_decoder():
    class UpperDecoder:
        def decode(self, value, **kwargs):
            return value.upper()

    decoder = UpperDecoder()
    engine = IngestionEngine(decoder=decoder)

    assert engine.ingest("example") == "EXAMPLE"

def test_ingestion_engine_passes_profile_to_decoder():
    class ContextDecoder:
        def decode(self, value, **kwargs):
            return kwargs["profile"]

    profile = object()
    engine = IngestionEngine(profile=profile, decoder=ContextDecoder())

    assert engine.ingest("source") is profile

def test_ingestion_engine_passes_diagnostics_to_decoder():
    class ContextDecoder:
        def decode(self, value, **kwargs):
            return kwargs["diagnostics"]

    diagnostics = object()
    engine = IngestionEngine(
        diagnostics=diagnostics,
        decoder=ContextDecoder(),
    )

    assert engine.ingest("source") is diagnostics   

def test_ingestion_engine_passes_source_and_context_to_decoder():
    class ContextDecoder:
        def decode(self, value, **kwargs):
            return {
                "value": value,
                "profile": kwargs["profile"],
                "diagnostics": kwargs["diagnostics"],
            }

    profile = object()
    diagnostics = object()
    source = {"title": "Example"}

    engine = IngestionEngine(
        profile=profile,
        diagnostics=diagnostics,
        decoder=ContextDecoder(),
    )

    result = engine.ingest(source)

    assert result["value"] is source
    assert result["profile"] is profile
    assert result["diagnostics"] is diagnostics

def test_ingestion_engine_returns_decoder_result():
    class FixedDecoder:
        def decode(self, value, **kwargs):
            return "decoded-result"

    engine = IngestionEngine(decoder=FixedDecoder())

    assert engine.ingest("source") == "decoded-result"

def test_copy_decoder_is_a_decoder():
    decoder = CopyDecoder()

    assert isinstance(decoder, Decoder)

def test_ingestion_engine_accepts_decoder():
    decoder = CopyDecoder()

    engine = IngestionEngine(decoder=decoder)

    assert engine.decoder is decoder