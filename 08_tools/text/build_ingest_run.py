#!/usr/bin/env python3
"""Run the generic ingest engine for one or more source profiles and build a run manifest."""
from __future__ import annotations
import argparse, csv, subprocess, sys
from pathlib import Path

def read_csv(p):
    with p.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("tree_dir", type=Path)
    ap.add_argument("profiles_dir", type=Path)
    ap.add_argument("--sources", nargs="+", required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--engine", type=Path, default=Path("08_tools/text/source_ingest.py"))
    a=ap.parse_args()
    a.output_dir.mkdir(parents=True, exist_ok=True)
    manifest=[]
    for source in a.sources:
        profile=a.profiles_dir/f"{source}.yaml"
        if not profile.exists():
            raise SystemExit(f"Missing source profile: {profile}")
        output=a.output_dir/f"{source}_ingest.csv"
        cmd=[sys.executable,str(a.engine),str(a.tree_dir),str(profile),"--output",str(output)]
        r=subprocess.run(cmd)
        if r.returncode:
            raise SystemExit(r.returncode)
        rows=read_csv(output)
        manifest.append({"source_id":source,"profile":str(profile),"output":str(output),"audio_records":len(rows)})
    mf=a.output_dir/"ingest_run_manifest.csv"
    with mf.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=manifest[0].keys()); w.writeheader(); w.writerows(manifest)
    print(f"Ingest run complete: {len(manifest)} sources")
    print(f"Manifest: {mf}")

if __name__=="__main__": main()
