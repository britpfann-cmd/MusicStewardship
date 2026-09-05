"""Tests for completeness checking."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(r"C:\Projects\MusicStewardship")
SRC = PROJECT_ROOT / "04_src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def test_completeness_stub_exists():
    from ingestion.completeness.checker import CompletenessChecker

    assert CompletenessChecker is not None