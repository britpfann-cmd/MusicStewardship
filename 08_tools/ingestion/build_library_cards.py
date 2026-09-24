#!/usr/bin/env python3
"""Generic source-ingest CSV -> canonical Library Card CSV builder.

The public Library Card field set is read from the existing Rev A translation
map. Source-specific vocabulary is supplied by a small translation CSV.
Unmapped source evidence is retained in residual_evidence.
"""
from __future__ import annotations
import argparse, csv, hashlib, json
from pathlib import Path

ARRAY_FIELDS = set()

def read_csv(path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w=csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)

def field_defs(path):
    rows=read_csv(path)
    return [r["Field"] for r in rows]

def parse_kv(text, key):
    if not text:
        return []
    out=[]
    for item in text.split(";"):
        if "=" not in item:
            continue
        k,v=item.split("=",1)
        if k == key and v != "":
            out.append(v)
    return out

def get_values(row, source_field):
    if "." in source_field:
        base,key=source_field.split(".",1)
        if base in row:
            return parse_kv(row.get(base,""),key)
        return []
    value=row.get(source_field,"")
    return [value] if value not in ("",None) else []

def uniq(values):
    out=[]
    for v in values:
        if v not in out:
            out.append(v)
    return out

def stable_id(source_id, relative_path):
    raw=f"{source_id}\0{relative_path}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:24]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("source_csv",type=Path)
    ap.add_argument("--translation",required=True,type=Path)
    ap.add_argument("--public-map",required=True,type=Path)
    ap.add_argument("--output",required=True,type=Path)
    ap.add_argument("--report",required=True,type=Path)
    args=ap.parse_args()

    source=read_csv(args.source_csv)
    translations=read_csv(args.translation)
    fields=field_defs(args.public_map)

    mapped=set()
    residual_fields=[]
    for t in translations:
        sf=t["source_field"]
        if t["translation_type"] in ("DIRECT","LABELED"):
            mapped.add(sf)
        if t["translation_type"] in ("RESIDUAL","RAW") or t["retain_source_as_residual"]=="YES":
            residual_fields.append(t)

    cards=[]
    source_count=len(source)
    for row in source:
        sid=row.get("source_id","")
        rel=row.get("relative_path","")
        card={f:"" for f in fields}
        card["card_revision"]="0"
        card["library_card_interface_revision"]="A"
        card["c_processing_revision"]="generic_library_card_builder.revA"
        card["source_object_id"]=stable_id(sid,rel)
        card["source_object_key"]=f"{sid}:{rel}"
        card["source_record_revision"]="source_ingest.v2"
        card["source_root"]=row.get("source_root","")
        card["relative_path"]=rel
        card["filename"]=row.get("filename","")
        card["extension"]=Path(row.get("filename","")).suffix.lstrip(".")
        card["entry_type"]="audio" if row.get("asset_acceptance")=="RETAIN" else ""
        residual=[]

        for t in translations:
            vals=get_values(row,t["source_field"])
            typ=t["translation_type"]
            canon=t["canonical_field"]
            if typ=="DIRECT" and canon in card:
                card[canon]=json.dumps(uniq((json.loads(card[canon]) if card[canon] else []) + vals),ensure_ascii=False)
            elif typ=="LABELED" and canon in card:
                arr=json.loads(card[canon]) if card[canon] else []
                label={"metadata_record":"Record","metadata_matrix":"Matrix","metadata_take":"Take","metadata_catalognumber":"Catalog Number"}.get(t["source_field"],t["source_field"])
                for v in vals: arr.append(f"{label}: {v}")
                card[canon]=json.dumps(uniq(arr),ensure_ascii=False)
            elif typ=="RESIDUAL":
                for v in vals: residual.append({"source_field":t["source_field"],"value":v})
            elif typ=="RAW":
                for v in vals: residual.append({"source_field":t["source_field"],"value":v})
            # NO_MAP intentionally leaves the source evidence elsewhere.

        # Source context is ordered and preserved.
        ctx=[]
        for sf in ("directory_path","directory_name","hierarchy_signature"):
            ctx += get_values(row,sf)
        card["source_context"]=json.dumps(uniq(ctx),ensure_ascii=False) if ctx else ""

        # Compact evidence summary.
        ev=[]
        for sf in ("evidence_sources","filename_rule_status","embedded_metadata_status","source_rule_set"):
            if row.get(sf): ev.append(f"{sf}={row[sf]}")
        card["evidence_summary"]=json.dumps(ev,ensure_ascii=False) if ev else ""

        # Always preserve raw source evidence at the card boundary, once.
        for sf in ("filename_rule_values","embedded_metadata_values"):
            if row.get(sf) and not any(x.get("source_field")==sf for x in residual):
                residual.append({"source_field":sf,"value":row[sf]})
        # Full source-ingest row is retained as a lossless audit payload for Rev A.
        residual.append({"source_field":"source_ingest_record","value":row})
        card["residual_evidence"]=json.dumps(residual,ensure_ascii=False) if residual else ""

        card["construction_status"]="candidate" if row.get("asset_acceptance")=="RETAIN" else "candidate_incomplete"
        card["conflicts"]="[]"
        lineage=[{
            "source_id":sid,
            "relative_path":rel,
            "source_rule_set":row.get("source_rule_set","")
        }]
        card["c_lineage"]=json.dumps(lineage,ensure_ascii=False)
        cards.append(card)

    write_csv(args.output,cards,fields)

    report={
        "source_records":source_count,
        "library_cards":len(cards),
        "cards_missing":source_count-len(cards),
        "residual_nonempty":sum(bool(c["residual_evidence"]) for c in cards),
        "status":"PASS" if source_count==len(cards) else "FAIL",
        "interface_revision":"A",
    }
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps(report,indent=2))

if __name__=="__main__":
    main()
