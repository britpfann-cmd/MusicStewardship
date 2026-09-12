import csv
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
INGEST = ROOT / "08_tools" / "ingestion"
sys.path.insert(0, str(INGEST))

from rosetta_engine import run, read_csv


def test_repeat_run_skips_completed_work_items(tmp_path):
    src = INGEST / "tests" / "TTT_rosetta_engine_v0.2_regression_sample.csv"
    mapping = INGEST / "mappings" / "TTT_to_MusicStewardship_Rosetta_v0.2.csv"
    bindings = INGEST / "mappings" / "TTT_source_field_bindings.csv"

    rows = read_csv(src)
    rules = read_csv(mapping)
    binds = read_csv(bindings)

    state = tmp_path / "state"

    first = run(rows, rules, binds, state, run_id="RUN1")
    second = run(rows, rules, binds, state, run_id="RUN2")

    assert first["processed"] == 313
    assert first["new_observations"] == 349
    assert second["processed"] == 0
    assert second["skipped"] == 313

    with (state / "processing_log.csv").open(
        encoding="utf-8-sig", newline=""
    ) as f:
        log = list(csv.DictReader(f))

    assert len(log) == 313

    with (state / "observations.csv").open(
        encoding="utf-8-sig", newline=""
    ) as f:
        obs = list(csv.DictReader(f))

    assert len(obs) == 349
