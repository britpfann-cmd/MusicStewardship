#!/usr/bin/env python3
"""Attach reusable source-directory context to every audio file."""

from __future__ import annotations
import argparse,csv
from pathlib import Path

def read(p):
    with p.open("r",encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def write(p,rows):
    rows=list(rows); fields=list(rows[0]) if rows else []
    with p.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("tree_dir",type=Path); ap.add_argument("context",type=Path); ap.add_argument("--output",required=True,type=Path)
    a=ap.parse_args()
    ctx={(x["source_id"],x["directory_path"]):x for x in read(a.context)}
    rows=[]
    for f in read(a.tree_dir/"source_tree_files.csv"):
        if f.get("is_audio")!="YES": continue
        c=ctx.get((f["source_id"],f["directory_path"]),{})
        rows.append({**f,
            "context_name_shape":c.get("name_shape",""),
            "context_semantic_tokens":c.get("semantic_tokens",""),
            "context_hierarchy_signature":c.get("hierarchy_signature",""),
            "context_directory_state":c.get("directory_state",""),
            "context_audio_file_count":c.get("audio_file_count",""),
            "context_evidence_basis":c.get("source_evidence_basis","")})
    a.output.parent.mkdir(parents=True,exist_ok=True); write(a.output,rows)
    print(f"Audio files contextualized: {len(rows)}")
    print(f"Output: {a.output}")
if __name__=="__main__":main()
