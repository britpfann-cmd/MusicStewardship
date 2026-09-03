#!/usr/bin/env python3
"""Produce compact diagnostics for a generic ingest CSV."""
from __future__ import annotations
import argparse, csv
from pathlib import Path
from collections import Counter

def rows(p):
    with p.open("r",encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("input",type=Path)
    ap.add_argument("--output-dir",type=Path,required=True)
    a=ap.parse_args(); rs=rows(a.input); a.output_dir.mkdir(parents=True,exist_ok=True)
    status=Counter(r.get("filename_rule_status","") for r in rs)
    sources=Counter(r.get("source_id","") for r in rs)
    cols=list(rs[0]) if rs else []
    summary=a.output_dir/"ingest_summary.csv"
    with summary.open("w",encoding="utf-8",newline="") as f:
        w=csv.writer(f); w.writerow(["metric","value"])
        w.writerow(["records",len(rs)])
        for k,v in status.items(): w.writerow([f"filename_rule_status:{k}",v])
        for k,v in sources.items(): w.writerow([f"source:{k}",v])
        w.writerow(["columns",len(cols)])
    unmatched=a.output_dir/"unmatched_files.csv"
    with unmatched.open("w",encoding="utf-8",newline="") as f:
        fields=["source_id","relative_path","filename","directory_path"]
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
        for r in rs:
            if r.get("filename_rule_status")!="MATCHED":
                w.writerow({x:r.get(x,"") for x in fields})
    print(f"Records inspected: {len(rs)}")
    print("Filename statuses:", dict(status))
    print(f"Summary: {summary}")
    print(f"Unmatched: {unmatched}")

if __name__=="__main__": main()
