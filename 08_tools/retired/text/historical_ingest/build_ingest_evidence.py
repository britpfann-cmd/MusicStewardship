#!/usr/bin/env python3
"""Combine file, filename, directory-context and measured audio evidence.

This stage does not select a canonical identity and never rejects an asset
because evidence is incomplete.
"""
from __future__ import annotations
import argparse,csv,re
from pathlib import Path

def read(p):
    with p.open("r",encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def write(p,rows):
    rows=list(rows); fields=list(rows[0]) if rows else []
    with p.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)

def parse_filename(name):
    stem=re.sub(r"\.[^.]+$","",name or "")
    m=re.match(r"^(.*?)(?:\s+)(\d{3,6}(?:-\d+)?)_(TT|RP|FV)$",stem,re.I)
    if m:return ("PARSED",m.group(1).strip(),m.group(2),m.group(3).upper())
    return ("UNPARSED",stem,"","")

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("contextualized",type=Path); ap.add_argument("--output",required=True,type=Path)
    a=ap.parse_args(); rows=[]
    for r in read(a.contextualized):
        st,title,cat,suffix=parse_filename(r.get("filename",""))
        rows.append({**r,
            "filename_parse_status":st,
            "filename_title_candidate":title,
            "filename_catalog_identifier_candidate":cat,
            "filename_source_suffix_candidate":suffix,
            "evidence_completeness":"PARTIAL" if st=="UNPARSED" else "FILENAME_PLUS_CONTEXT",
            "canonical_identity_status":"UNRESOLVED",
            "asset_acceptance":"RETAIN",
            "evidence_rule":"preserve asset; enrich later as necessary"})
    a.output.parent.mkdir(parents=True,exist_ok=True); write(a.output,rows)
    print(f"Ingest evidence records: {len(rows)}")
    print("Canonical identities selected: 0")
    print("Assets rejected: 0")
    print(f"Output: {a.output}")
if __name__=="__main__":main()
