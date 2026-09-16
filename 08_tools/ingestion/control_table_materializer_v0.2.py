#!/usr/bin/env python3
"""Generic MusicStewardship source-control-table materializer v0.2."""

from __future__ import annotations
import argparse
import csv
from pathlib import Path

OPERATIONS = {
    "COPY","RENAME","STANDARDIZE","DECOMPOSE","COMBINE","LOOKUP",
    "EXTRACT","PATH_EXTRACT","DERIVE","REFERENCE","IGNORE",
    "SOURCE_CONTEXT","ASSERT",
}

CONTROL_REQUIRED = {
    "control_id","source","source_name","source_field","semantic_term",
    "representation_level","input_role","input_semantic_term",
    "operation","decoder","target_entity","target_property",
    "target_relationship","preserve_source_value","confidence","status",
    "notes","match_pattern","decoder_pattern",
}

ENGINE_FIELDS = [
    "rule_id","source","source_element","source_field","source_pattern",
    "information_class","operation","decoder","target_entity",
    "target_property","target_relationship","assurance",
    "preserve_source_value","confidence","status","rule",
    "evidence_basis","match_pattern","decoder_pattern",
    "input_role","input_semantic_term",
]

def read_csv(path: Path):
    with path.open("r",encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(line for line in f
                                   if not line.lstrip().startswith("#")))

def info_class(level):
    value=(level or "").strip().lower()
    if value in {"source","source→semantic","source->semantic"}:
        return "CORE"
    if value=="residual":
        return "RESIDUAL"
    return "ASSOCIATED"

def materialize(controls,evidence_label):
    if not controls:
        raise ValueError("Control table contains no rows.")
    missing=CONTROL_REQUIRED-set(controls[0])
    if missing:
        raise ValueError("Missing control-table columns: "+", ".join(sorted(missing)))

    seen=set(); out=[]
    for c in controls:
        cid=(c.get("control_id") or "").strip()
        sem=(c.get("semantic_term") or "").strip()
        op=(c.get("operation") or "").strip().upper()
        if not cid or cid in seen:
            raise ValueError(f"Invalid or duplicate control_id: {cid!r}")
        if not sem:
            raise ValueError(f"{cid}: blank semantic_term")
        if op not in OPERATIONS:
            raise ValueError(f"{cid}: unsupported operation {op!r}")

        out.append({
            "rule_id":cid,
            "source":c.get("source",""),
            "source_element":sem,
            "source_field":c.get("source_field",""),
            "source_pattern":c.get("source_name",""),
            "information_class":info_class(c.get("representation_level","")),
            "operation":op,
            "decoder":c.get("decoder",""),
            "target_entity":c.get("target_entity",""),
            "target_property":c.get("target_property",""),
            "target_relationship":c.get("target_relationship",""),
            "assurance":"OBSERVED",
            "preserve_source_value":c.get("preserve_source_value",""),
            "confidence":c.get("confidence",""),
            "status":c.get("status",""),
            "rule":c.get("notes",""),
            "evidence_basis":evidence_label,
            "match_pattern":c.get("match_pattern",""),
            "decoder_pattern":c.get("decoder_pattern",""),
            "input_role":c.get("input_role",""),
            "input_semantic_term":c.get("input_semantic_term",""),
        })
        seen.add(cid)
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("control_csv",type=Path)
    ap.add_argument("output_csv",type=Path)
    ap.add_argument("--evidence-label",default="Source control table")
    a=ap.parse_args()
    controls=read_csv(a.control_csv)
    rules=materialize(controls,a.evidence_label)
    a.output_csv.parent.mkdir(parents=True,exist_ok=True)
    with a.output_csv.open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=ENGINE_FIELDS); w.writeheader(); w.writerows(rules)
    print(f"Control rows:       {len(controls)}")
    print(f"Materialized rules: {len(rules)}")
    print(f"Output:             {a.output_csv}")

if __name__=="__main__":
    main()
