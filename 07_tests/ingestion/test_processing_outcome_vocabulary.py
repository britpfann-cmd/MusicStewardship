from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "08_tools" / "ingestion" / "processing_outcome_vocabulary.py"

spec = importlib.util.spec_from_file_location("processing_outcome_vocabulary", MODULE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_information_classes_are_distinct_from_processing_outcomes():
    assert "RESIDUAL" in mod.INFORMATION_CLASSES
    assert "RESIDUAL" not in mod.PROCESSING_OUTCOMES
    assert "DECODED" in mod.PROCESSING_OUTCOMES


def test_preserved_is_not_an_attention_outcome():
    assert "PRESERVED" not in mod.ATTENTION_OUTCOMES
    assert "PRESERVED" in mod.NON_EXCEPTION_OUTCOMES


def test_unresolved_outcomes_are_attention_candidates():
    assert {"PARTIAL", "UNDECODABLE", "CONFLICT", "REVIEW"} <= mod.ATTENTION_OUTCOMES


def test_validation():
    assert mod.validate_processing_outcome("DECODED") == "DECODED"
    assert mod.validate_outcome_reason("PRESERVATION") == "PRESERVATION"
