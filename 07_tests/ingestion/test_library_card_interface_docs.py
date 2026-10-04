from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GENERATOR = ROOT / "08_tools" / "ingestion" / "generate_library_card_interface_docs.py"
SPEC = (
    ROOT
    / "01_docs"
    / "05_Ingestion"
    / "MusicStewardship_Library_Card_CSV_Public_Specification_ING-CARD-001_RevA.md"
)


def run_generator(*args):
    return subprocess.run(
        [sys.executable, str(GENERATOR), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )


def test_committed_markdown_matches_certified_rev_a_contract():
    result = run_generator(
        "--revision", "A",
        "--spec", str(SPEC),
        "--check",
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "Markdown field contract is in sync" in result.stdout


def test_generation_is_idempotent(tmp_path):
    copy = tmp_path / SPEC.name
    copy.write_text(SPEC.read_text(encoding="utf-8"), encoding="utf-8")

    first = run_generator(
        "--revision", "A",
        "--spec", str(copy),
    )
    assert first.returncode == 0, first.stdout + first.stderr
    after_first = copy.read_bytes()

    second = run_generator(
        "--revision", "A",
        "--spec", str(copy),
    )
    assert second.returncode == 0, second.stdout + second.stderr

    assert copy.read_bytes() == after_first
