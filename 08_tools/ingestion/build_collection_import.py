#!/usr/bin/env python3
"""Generic end-to-end collection import orchestrator.

Two modes:
  --ingest-csv : start from an already-produced source-ingest CSV (test/replay)
  --tree-dir + --rules : run the generic source_ingest engine, then build canonical CSV.

The canonical CSV boundary is the only downstream interface.
"""
from __future__ import annotations
import argparse, subprocess, sys
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    src=ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--ingest-csv",type=Path)
    src.add_argument("--tree-dir",type=Path)
    ap.add_argument("--rules",type=Path)
    ap.add_argument("--translation",type=Path,required=True)
    ap.add_argument("--public-map",type=Path,required=True)
    ap.add_argument("--output-dir",type=Path,required=True)
    args=ap.parse_args()

    args.output_dir.mkdir(parents=True,exist_ok=True)
    ingest_csv=args.ingest_csv

    if args.tree_dir:
        if not args.rules:
            ap.error("--rules is required with --tree-dir")
        ingest_csv=args.output_dir/"source_ingest.csv"
        evidence=args.output_dir/"source_specific_evidence.json"
        cmd=[sys.executable,str(Path(__file__).with_name("source_ingest.py")),
             str(args.tree_dir),str(args.rules),"--output",str(ingest_csv),
             "--evidence-output",str(evidence)]
        subprocess.run(cmd,check=True)

    card_csv=args.output_dir/"Library_Cards_RevA.csv"
    report=args.output_dir/"build_report.json"
    cmd=[sys.executable,str(Path(__file__).with_name("build_library_cards.py")),
         str(ingest_csv),"--translation",str(args.translation),
         "--public-map",str(args.public_map),"--output",str(card_csv),
         "--report",str(report)]
    subprocess.run(cmd,check=True)

    print(f"Collection import complete: {args.output_dir}")
    print(f"Canonical CSV: {card_csv}")
    print(f"Build report : {report}")

if __name__=="__main__":
    main()
