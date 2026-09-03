#!/usr/bin/env python3
"""Build local Audio Asset records while preserving multiple copies.

No preferred copy is selected unless evidence exists; unresolved assets remain
eligible for later reconciliation/materialization.
"""
from __future__ import annotations
import argparse,csv,hashlib
from pathlib import Path

def read(p):
    with p.open("r",encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def write(p,rows):
    rows=list(rows); fields=list(rows[0]) if rows else []
    with p.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("reconciliation",type=Path); ap.add_argument("--output",required=True,type=Path)
    a=ap.parse_args(); rows=[]
    for r in read(a.reconciliation):
        key=f"{r.get('source_id','')}|{r.get('relative_path','')}|{r.get('filename','')}"
        aid="asset-"+hashlib.sha256(key.encode()).hexdigest()[:16]
        rows.append({**r,
            "audio_asset_id":aid,
            "performance_identity_status":"UNRESOLVED",
            "copy_role":"AVAILABLE_CANDIDATE",
            "preferred_copy_status":"UNSET",
            "retention_status":"RETAIN",
            "materialization_status":"NOT_MATERIALIZED"})
    a.output.parent.mkdir(parents=True,exist_ok=True); write(a.output,rows)
    print(f"Audio Asset records: {len(rows)}")
    print("Preferred copies selected: 0")
    print(f"Output: {a.output}")
if __name__=="__main__":main()
