#!/usr/bin/env python3
from pathlib import Path
import sys, subprocess

ROOT = Path(__file__).resolve().parents[2]
INGEST = ROOT / "08_tools" / "ingestion"
OUT = INGEST / "tests" / "TTT_rosetta_engine_v0.2_prototype_output.csv"
SOURCE = Path(sys.argv[1]) if len(sys.argv) > 1 else INGEST / "tests" / "TTT_grammar_ingest_v2_baseline_sample.csv"
MAPPING = INGEST / "mappings" / "TTT_to_MusicStewardship_Rosetta_v0.2.csv"
BINDINGS = INGEST / "mappings" / "TTT_source_field_bindings.csv"

subprocess.run([
    sys.executable, str(INGEST/"rosetta_engine.py"),
    str(SOURCE), str(MAPPING), str(BINDINGS),
    "--output", str(OUT)
], check=True)
