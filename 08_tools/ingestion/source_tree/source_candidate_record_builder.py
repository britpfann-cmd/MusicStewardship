#!/usr/bin/env python3
"""MusicStewardship Candidate Record Builder.

Build one Candidate Record per terminal source object by assembling preserved
Explorer Tree provenance, candidate extraction observations, and optional
embedded metadata evidence. This layer assembles evidence; it does not resolve
authority or entities.
"""
from __future__ import annotations
import argparse, json
from collections import defaultdict
from pathlib import Path
from typing import Any

SCHEMA = "musicstewardship.source_tree_candidate_record.v1"
METADATA_ATTRIBUTE_MAP = {"title":"title","TITLE":"title","artist":"artist","ARTIST":"artist","album_artist":"orchestra_or_album_artist","ALBUM_ARTIST":"orchestra_or_album_artist","album":"source_album","ALBUM":"source_album","genre":"genre","GENRE":"genre","date":"recording_date_or_year","DATE":"recording_date_or_year","composer":"composer","COMPOSER":"composer","conductor":"conductor","CONDUCTOR":"conductor"}
FILENAME_ATTRIBUTE_MAP = {"leading_text":"filename_leading_text_candidate","numeric_component":"filename_numeric_component","sequence_number_candidate":"sequence_number_candidate","terminal_suffix":"source_suffix"}
# Multiple observations are expected for these attributes and are not conflicts.
MULTI_VALUED_ATTRIBUTES = {"filename_numeric_component"}

def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f: return json.load(f)
def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
def clean_rel(value: str | None) -> str:
    return "" if value is None else str(value).replace("\\", "/").strip("/")
def root_path(value: Any) -> str:
    return str((value.get("path") or value.get("name") or "") if isinstance(value, dict) else (value or ""))
def relative_from_source_path(path_value: Any, root: str) -> str:
    value, root_n = str(path_value or "").replace("\\", "/"), root.replace("\\", "/").rstrip("/")
    return value[len(root_n)+1:] if value.lower().startswith(root_n.lower()+"/") else value.lstrip("/")
def source_key(source_root: str, relative_path: str) -> str:
    root = root_path(source_root).replace(chr(92), "/").rstrip("/")
    rel = clean_rel(relative_path)
    full = f"{root}/{rel}" if rel else root
    return full.lower()
def is_terminal_file(node: dict[str, Any]) -> bool: return str(node.get("entry_type", "")).upper() in {"FILE", "AUDIO"}
def extension_of(node: dict[str, Any]) -> str:
    name = str(node.get("name", "")); return "" if "." not in name else "." + name.rsplit(".",1)[1].lower()

def candidate_attribute(item: dict[str, Any]) -> str | None:
    target, operation = str(item.get("target") or ""), str(item.get("operation") or "")
    if target in FILENAME_ATTRIBUTE_MAP: return FILENAME_ATTRIBUTE_MAP[target]
    key = target.split(".",1)[-1]
    if key in FILENAME_ATTRIBUTE_MAP: return FILENAME_ATTRIBUTE_MAP[key]
    return {"extract_text_before_first_numeric_component":"filename_leading_text_candidate","extract_numeric_component":"filename_numeric_component","identify_sequence_number_candidate":"sequence_number_candidate","extract_terminal_suffix":"source_suffix","preserve_as_categorical_source_evidence":"source_evidence"}.get(operation)

def metadata_attribute(obs: dict[str, Any]) -> str | None:
    locator = str(obs.get("source_locator") or "")
    tag = locator[len("metadata.tag."):] if locator.startswith("metadata.tag.") else (obs.get("tag") or obs.get("key") or obs.get("field") or obs.get("name"))
    return None if tag is None else METADATA_ATTRIBUTE_MAP.get(str(tag))
def normalize_candidate_value(value: Any) -> Any: return value.strip() if isinstance(value, str) else value

def add_observation(record, obs, attribute, channel, evidence_id):
    raw = obs.get("raw_value", obs.get("value")); normalized = normalize_candidate_value(obs.get("normalized_value") if "normalized_value" in obs else raw)
    record["observations"].append({"evidence_id":evidence_id,"evidence_channel":channel,"evidence_type":obs.get("evidence_type"),"source_locator":obs.get("source_locator"),"raw_value":raw,"normalized_value":normalized,"extraction_method":obs.get("extraction_method"),"decoder":obs.get("decoder"),"confidence":obs.get("confidence"),"status":obs.get("status","candidate"),"derived_from":obs.get("derived_from")})
    (record["candidate_attributes"].setdefault(attribute,[]) if attribute else record["residual_evidence"]).append(evidence_id)

def build_directory_observations(node):
    parts=[p for p in clean_rel(node.get("relative_path")).split("/") if p]
    return [{"evidence_type":"directory.component","source_locator":f"directory.component[{d}]","raw_value":c,"extraction_method":"preserve_directory_component","decoder":"directory_component.v1","status":"candidate"} for d,c in enumerate(parts[:-1],1)]

def index_candidates(data, default_root):
    result=defaultdict(list); items=data.get("candidates",data.get("observations",[])); items=items.get("items",[]) if isinstance(items,dict) else items
    for item in items:
        root=root_path(item.get("source_root") or data.get("source_root") or default_root); rel=clean_rel(item.get("source_relative_path") or item.get("relative_path")) or relative_from_source_path(item.get("source_path"),root)
        if rel and root: result[source_key(root,rel)].append(item)
    return result

def index_metadata(data, default_root):
    result=defaultdict(list); source_objects=data.get("source_objects",[])
    if source_objects:
        for so in source_objects:
            root=root_path(so.get("source_root") or data.get("source_root") or default_root); rel=clean_rel(so.get("relative_path")) or relative_from_source_path(so.get("source_path"),root)
            if rel and root: result[source_key(root,rel)].extend(so.get("observations",[]))
        return result
    items=data.get("observations",[]); items=items.get("items",[]) if isinstance(items,dict) else items
    for obs in items:
        root=root_path(obs.get("source_root") or data.get("source_root") or default_root); rel=clean_rel(obs.get("relative_path")) or relative_from_source_path(obs.get("source_path"),root)
        if rel and root: result[source_key(root,rel)].append(obs)
    return result

def build_records(tree,candidates,metadata,plan=None):
    default_root=root_path(tree.get("source_root")); nodes=[]
    if isinstance(tree.get("inspections"),list):
        for inspection in tree["inspections"]: nodes.extend(inspection.get("children",[]))
    else:
        nodes=tree.get("children",tree.get("nodes",[])); nodes=nodes.get("items",[]) if isinstance(nodes,dict) else nodes
    ci, mi=index_candidates(candidates,default_root), index_metadata(metadata,default_root) if metadata else {}; records=[]
    for node in nodes:
        if not is_terminal_file(node): continue
        root=root_path(node.get("source_root") or default_root); rel=clean_rel(node.get("relative_path")); name=str(node.get("name","")); ext=extension_of(node); rid=f"candidate:{len(records)+1:06d}"
        record={"candidate_record_id":rid,"schema":SCHEMA,"status":"candidate","source_object_id":node.get("source_object_id"),"source":{"source_root":root,"relative_path":rel,"filename":name,"extension":ext,"entry_type":node.get("entry_type","FILE")},"candidate_attributes":{},"observations":[],"residual_evidence":[],"conflicts":[],"lineage":{"source_object_key":source_key(root,rel)}}
        for i,obs in enumerate(build_directory_observations(node),1): add_observation(record,obs,None,"directory",f"directory:{i:06d}")
        key=source_key(root,rel)
        for i,item in enumerate(ci.get(key,[]),1):
            attr=candidate_attribute(item); target=str(item.get("target") or ""); channel="filename" if target.startswith("filename.") else ("directory" if target.startswith("parent_directory.") or target.startswith("directory.") else "source_specific")
            add_observation(record,{"evidence_type":target or None,"source_locator":item.get("source_locator") or item.get("source_relative_path") or item.get("source_path") or target,"raw_value":item.get("value",item.get("raw_value")),"extraction_method":item.get("operation"),"decoder":item.get("decoder"),"confidence":item.get("confidence"),"status":item.get("status","candidate"),"derived_from":item.get("derived_from")},attr,channel,f"candidate:{i:06d}")
        for i,obs in enumerate(mi.get(key,[]),1):
            add_observation(
                record,
                obs,
                metadata_attribute(obs),
                "metadata",
                obs.get("evidence_id") or f"metadata:{i:06d}"
            )
        byid={o["evidence_id"]:o for o in record["observations"]}
        for attr,ids in record["candidate_attributes"].items():
            if attr in MULTI_VALUED_ATTRIBUTES: continue
            vals=sorted({repr(byid[x]["normalized_value"]) for x in ids})
            if len(vals)>1: record["conflicts"].append({"attribute":attr,"observation_ids":ids,"distinct_normalized_values":vals,"resolution":"not_resolved"})
        if record["conflicts"]: record["status"]="candidate_with_conflicts"
        elif not record["candidate_attributes"]: record["status"]="candidate_incomplete"
        records.append(record)
    return records

def markdown(records,source_label):
    lines=["# Candidate Record Build","",f"**Source:** `{source_label}`",f"**Candidate Records:** {len(records)}",""]
    for r in records:
        lines += [f"## {r['candidate_record_id']}","",f"- Status: `{r['status']}`",f"- Source root: `{r['source']['source_root']}`",f"- Relative path: `{r['source']['relative_path']}`",f"- Filename: `{r['source']['filename']}`",f"- Extension: `{r['source']['extension']}`","","### Candidate attributes",""]
        obs={o["evidence_id"]:o for o in r["observations"]}
        if not r["candidate_attributes"]: lines.append("- *(none)*")
        else:
            for attr,ids in r["candidate_attributes"].items():
                lines.append(f"- **{attr}**")
                for oid in ids: lines.append(f"  - `{oid}` = `{obs[oid]['raw_value']}` ({obs[oid]['evidence_channel']}, {obs[oid]['evidence_type']})")
        lines += ["","### Residual evidence",""]
        if not r["residual_evidence"]: lines.append("- *(none)*")
        else:
            for oid in r["residual_evidence"]: lines.append(f"- `{oid}` = `{obs[oid]['raw_value']}` ({obs[oid]['evidence_channel']}, {obs[oid]['evidence_type']})")
        if r["conflicts"]:
            lines += ["","### Unresolved conflicts",""]
            for c in r["conflicts"]: lines.append(f"- **{c['attribute']}**: "+", ".join(c["distinct_normalized_values"]))
        lines.append("")
    return "\n".join(lines)

def main():
    p=argparse.ArgumentParser(description="Build MusicStewardship Candidate Records."); p.add_argument("-map",required=True); p.add_argument("-plan"); p.add_argument("-candidates",required=True); p.add_argument("-metadata"); p.add_argument("-o","--output",required=True); a=p.parse_args()
    tree=load_json(Path(a.map)); candidates=load_json(Path(a.candidates)); metadata=load_json(Path(a.metadata)) if a.metadata else None; plan=load_json(Path(a.plan)) if a.plan else None; records=build_records(tree,candidates,metadata,plan)
    output=Path(a.output); stem=output.with_suffix("") if output.suffix.lower()==".json" else output; json_path=output if output.suffix.lower()==".json" else Path(str(output)+".json")
    write_json(json_path,{"schema":SCHEMA,"source_root":tree.get("source_root"),"source_label":tree.get("source_label"),"builder":"candidate_record_builder.v1","inputs":{"semantic_map":str(Path(a.map)),"decoding_plan":str(Path(a.plan)) if a.plan else None,"candidate_extraction":str(Path(a.candidates)),"metadata_evidence":str(Path(a.metadata)) if a.metadata else None},"record_count":len(records),"records":records})
    md=Path(str(stem)+".md"); md.write_text(markdown(records,root_path(tree.get("source_root"))),encoding="utf-8")
    print(f"JSON: {json_path}\nMarkdown: {md}\nCandidate Records: {len(records)}\nObservations: {sum(len(r['observations']) for r in records)}\nConflicted: {sum(r['status']=='candidate_with_conflicts' for r in records)}\nIncomplete: {sum(r['status']=='candidate_incomplete' for r in records)}")
    return 0
if __name__=="__main__": raise SystemExit(main())
