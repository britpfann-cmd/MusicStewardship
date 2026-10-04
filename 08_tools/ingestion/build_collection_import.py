#!/usr/bin/env python3
"""Generic end-to-end collection import orchestrator.

Two modes:
  --ingest-csv : start from an already-produced source-ingest CSV (test/replay)
  --tree-dir + --rules : run the generic source_ingest engine, then Rosetta and common recombination.

The canonical CSV boundary is the only downstream interface.
"""
from __future__ import annotations
import argparse, subprocess, sys
from pathlib import Path

INGEST = Path(__file__).resolve().parent
TEXT_TOOLS = INGEST.parent / "text"

def main():
    ap=argparse.ArgumentParser()
    src=ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--ingest-csv",type=Path)
    src.add_argument("--tree-dir",type=Path)
    ap.add_argument("--rules",type=Path)
    ap.add_argument("--rosetta",type=Path,required=True)
    ap.add_argument("--bindings",type=Path,required=True)
    ap.add_argument("--run-id",required=True)
    ap.add_argument("--public-map",type=Path,required=True)
    ap.add_argument("--interface-revision",required=True)
    ap.add_argument("--output-dir",type=Path,required=True)
    args=ap.parse_args()

    args.output_dir.mkdir(parents=True,exist_ok=True)
    ingest_csv=args.ingest_csv

    if args.tree_dir:
        if not args.rules:
            ap.error("--rules is required with --tree-dir")
        ingest_csv=args.output_dir/"source_ingest.csv"
        evidence=args.output_dir/"source_specific_evidence.json"
        cmd=[sys.executable,str(TEXT_TOOLS / "source_ingest.py"),
             str(args.tree_dir),str(args.rules),"--output",str(ingest_csv),
             "--evidence-output",str(evidence)]
        subprocess.run(cmd,check=True)

    # Source-specific semantic decoding/interpretation.
    rosetta_state=args.output_dir/"rosetta_state"
    cmd=[sys.executable,str(INGEST / "rosetta_engine.py"),
         str(ingest_csv),str(args.rosetta),str(args.bindings),
         "--state-dir",str(rosetta_state),
         "--run-id",args.run_id]
    subprocess.run(cmd,check=True)

    # Common semantic recombination into the public Rev A boundary.
    card_csv=args.output_dir/"Library_Cards_RevA.csv"
    report=args.output_dir/"build_report.json"
    cmd=[sys.executable,
         str(INGEST / "build_library_cards_from_rosetta.py"),
         str(ingest_csv),
         "--public-map",str(args.public_map),
         "--interface-revision",args.interface_revision,
         "--observations",str(rosetta_state/"observations.csv"),
         "--run-id",args.run_id,
         "--output",str(card_csv),
         "--report",str(report)]
    subprocess.run(cmd,check=True)

    print(f"Collection import complete: {args.output_dir}")
    print(f"Canonical CSV: {card_csv}")
    print(f"Build report : {report}")

if __name__=="__main__":
    main()

