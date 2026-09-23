from __future__ import annotations
import argparse
import json
from pathlib import Path

SCHEMA = "musicstewardship.source_record.v1"
BUILDER_REVISION = "source_record_builder.v1"

def load_json(path):
    with Path(path).open("r", encoding="utf-8-sig") as f:
        return json.load(f)

def write_json(path, obj):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False); f.write("\n")

def interpretation_index(data):
    result = {}
    for item in data.get("interpretations", []):
        key = item.get("source_object_id")
        if key: result.setdefault(key, []).append(item)
    return result

def build_source_records(candidate_data, interpretation_data):
    interpretations = interpretation_index(interpretation_data); records = []
    for candidate in candidate_data.get("records", []):
        cid = candidate["candidate_record_id"]
        source = candidate.get("source", {})
        lineage = candidate.get("lineage", {})
        record = {
            "source_record_id": f"source:{len(records)+1:06d}",
            "schema": SCHEMA,
            "builder_revision": BUILDER_REVISION,
            "source_object_id": candidate.get("source_object_id"),
            "source": {k: source.get(k) for k in ("source_root","relative_path","filename","extension","entry_type")},
            "source_context": [],
            "candidate_attributes": candidate.get("candidate_attributes", {}),
            "interpretations": [],
            "observations": candidate.get("observations", []),
            "residual_evidence": candidate.get("residual_evidence", []),
            "conflicts": candidate.get("conflicts", []),
            "construction_status": candidate.get("status", ""),
            "lineage": {
                "source_object_id": candidate.get("source_object_id"),
                "source_object_key": lineage.get("source_object_key"),
                "candidate_record_id": cid,
            },
        }
        for item in interpretations.get(cid, []):
            record["interpretations"].append(item)
            if item.get("attribute") == "source_context":
                record["source_context"].append({k:item.get(k) for k in ("value","status","supported_by","derivation","notes")})
        records.append(record)
    return records

def main():
    p=argparse.ArgumentParser(description="Build one Source Record per source object.")
    p.add_argument("-candidates",required=True); p.add_argument("-interpretation",required=True); p.add_argument("-o","--output",required=True)
    a=p.parse_args(); cd=load_json(a.candidates); idat=load_json(a.interpretation); records=build_source_records(cd,idat)
    out=Path(a.output); jp=out if out.suffix.lower()==".json" else Path(str(out)+".json"); mp=jp.with_suffix(".md")
    result={"schema":SCHEMA,"builder":BUILDER_REVISION,"source_root":cd.get("source_root"),"inputs":{"candidate_records":str(Path(a.candidates)),"source_interpretation":str(Path(a.interpretation))},"record_count":len(records),"records":records}
    write_json(jp,result)
    lines=["# Source Record Build","",f"**Schema:** `{SCHEMA}`",f"**Builder:** `{BUILDER_REVISION}`",f"**Source Records:** {len(records)}","\n"]
    for r in records:
        s=r["source"]; lines += [f"## {r['source_record_id']}",f"- Entry type: `{s.get('entry_type')}`",f"- Relative path: `{s.get('relative_path')}`",f"- Filename: `{s.get('filename')}`",f"- Source object ID: `{r.get('source_object_id')}`",f"- Construction status: `{r.get('construction_status')}`",f"- Interpretations: {len(r['interpretations'])}",f"- Observations: {len(r['observations'])}",f"- Residual evidence: {len(r['residual_evidence'])}",f"- Conflicts: {len(r['conflicts'])}",""]
    mp.write_text("\n".join(lines),encoding="utf-8",newline="\n"); print(f"Source Records: {len(records)}"); print(f"Output: {jp}"); print(f"Markdown: {mp}")
if __name__=="__main__": main()

