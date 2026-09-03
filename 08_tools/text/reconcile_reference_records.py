#!/usr/bin/env python3
"""Create reference-reconciliation candidates from ingest evidence.

Reference catalogs are inputs to corroboration, not automatic authorities.
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
    ap=argparse.ArgumentParser()
    ap.add_argument("evidence",type=Path); ap.add_argument("--reference",action="append",type=Path,default=[])
    ap.add_argument("--output",required=True,type=Path)
    a=ap.parse_args()
    refs=[]
    for p in a.reference:
        if p.exists(): refs.extend(read(p))
    rows=[]
    for r in read(a.evidence):
        basis=[]
        if r.get("filename_title_candidate"): basis.append("filename")
        if r.get("context_hierarchy_signature"): basis.append("directory_context")
        rows.append({
            "source_id":r.get("source_id",""),"relative_path":r.get("relative_path",r.get("path","")),
            "filename":r.get("filename",""),
            "local_evidence_basis":";".join(basis),
            "reference_sources_available":len(a.reference),
            "reference_candidate_status":"NEEDS_REFERENCE_MATCH",
            "reference_match_method":"not yet implemented",
            "candidate_performance_id":"",
            "match_confidence":"UNRESOLVED",
            "reconciliation_note":"Use curated reference records for corroboration; do not reject local asset"
        })
    a.output.parent.mkdir(parents=True,exist_ok=True); write(a.output,rows)
    print(f"Reconciliation candidates: {len(rows)}")
    print(f"Reference files supplied: {len(a.reference)}")
    print(f"Output: {a.output}")
if __name__=="__main__":main()
