#!/usr/bin/env python3
"""Run the TTT Rosetta engine and build the human-facing workbook report."""
from pathlib import Path
import argparse, subprocess, sys

ROOT=Path(__file__).resolve().parents[2]
INGEST=ROOT/'08_tools'/'ingestion'

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('source_csv',type=Path)
    ap.add_argument('--state-dir',type=Path,required=True)
    ap.add_argument('--report',type=Path,required=True)
    ap.add_argument('--run-id')
    ap.add_argument('--force',action='store_true')
    a=ap.parse_args()
    mapping=INGEST/'mappings'/'TTT_to_MusicStewardship_Rosetta_v0.2.csv'
    bindings=INGEST/'mappings'/'TTT_source_field_bindings.csv'
    cmd=[sys.executable,str(INGEST/'rosetta_engine.py'),str(a.source_csv),str(mapping),str(bindings),'--state-dir',str(a.state_dir)]
    if a.run_id: cmd += ['--run-id',a.run_id]
    if a.force: cmd += ['--force']
    subprocess.run(cmd,check=True)
    subprocess.run([sys.executable,str(INGEST/'report_ttt_run.py'),'--state-dir',str(a.state_dir),'--output',str(a.report)],check=True)

if __name__=='__main__': main()
