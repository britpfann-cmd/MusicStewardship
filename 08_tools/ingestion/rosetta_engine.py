#!/usr/bin/env python3
"""Generic declarative Rosetta execution engine with restartable processing log.

Source-specific grammar remains in Rosetta/control CSV.  The engine provides
only generic operations, checkpointing/idempotent work-item execution, durable
processing evidence, and report inputs.
"""
from __future__ import annotations
import argparse, csv, re, hashlib
from pathlib import Path
from datetime import datetime, timezone

from processing_outcome_vocabulary import (
    INFORMATION_CLASSES,
    PROCESSING_OUTCOMES,
    OUTCOME_REASONS,
)

INFO_CLASSES = INFORMATION_CLASSES
OPERATIONS = {"COPY", "RENAME", "STANDARDIZE", "DECOMPOSE", "COMBINE", "LOOKUP",
              "EXTRACT", "PATH_EXTRACT", "DERIVE", "REFERENCE", "IGNORE",
              "SOURCE_CONTEXT", "ASSERT"}
PROCESS_FIELDS = ["run_id","work_item_id","source_id","source_record","rule_id",
                  "source_element","source_field","input_fingerprint","status",
                  "attempt","started_at","completed_at","observation_count",
                  "exception","engine_version","rosetta_version"]
OBS_FIELDS = ["run_id","source_id","source_record","source_element","source_field",
             "source_value","rule_id","semantic_term","representation_level","information_class","operation","decoder",
             "target_entity","target_property","target_relationship","assurance",
             "preserve_source_value","decoded_value","status",
             "processing_outcome","outcome_reason","residual","evidence_basis"]
ENGINE_VERSION = "0.4-processing-outcome"


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        lines = (line for line in f if not line.lstrip().startswith("#"))
        return list(csv.DictReader(lines))


def write_csv(path: Path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)


def append_csv(path: Path, rows, fields):
    rows = list(rows)
    if not rows: return
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists() and path.stat().st_size > 0
    with path.open("a", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        if not exists: w.writeheader()
        w.writerows(rows)


def split_semicolon(value): return [x.strip() for x in value.split(";") if x.strip()]

def labeled_fields(value):
    pat = re.compile(r"(Record|Matrix|Take)\s*:\s*(.*?)(?=(?:\s*,?\s*)(?:Record|Matrix|Take)\s*:|$)", re.I)
    return [(m.group(1).lower(), m.group(2).strip(" ,")) for m in pat.finditer(value)]

def clauses(value): return split_semicolon(value)

def regex_extract(text, pattern, findall=False):
    if not pattern: return [], "NO_PATTERN"
    try: rx = re.compile(pattern, re.I)
    except re.error as exc: return [f"REGEX_ERROR:{exc}"], "ERROR"
    if findall:
        matches = rx.findall(text); values=[]
        for m in matches:
            values.append("=".join(str(x).strip() for x in m if str(x).strip()) if isinstance(m, tuple) else str(m).strip())
        return values, "EMITTED" if values else "NO_MATCH"
    m=rx.search(text)
    if not m: return [], "NO_MATCH"
    return [m.group(1).strip()] if m.lastindex else [m.group(0).strip()], "EMITTED"

def classify_processing_outcome(rule, execution_status):
    """
    Translate low-level generic operation status into the controlled
    processing-outcome vocabulary.

    This classification is deliberately generic.  Source-specific
    semantics remain in the Rosetta control/binding layers.
    """
    op = (rule.get("operation") or "").upper()
    status = (execution_status or "").upper()

    if status == "IGNORED":
        return "NOT_ATTEMPTED", "OUT_OF_SCOPE"

    if status == "NO_MATCH":
        return "UNDECODABLE", ""

    if status == "ERROR":
        return "REVIEW", "DECODER_FAILURE"

    if status.startswith("UNSUPPORTED_OPERATION:"):
        return "NOT_ATTEMPTED", "NO_CAPABILITY"

    if status == "EMITTED":
        if op == "COPY":
            return "PRESERVED", "PRESERVATION"

        if op == "DERIVE":
            return "DERIVED", ""

        return "DECODED", ""

    # Conservative fallback: do not silently call an unknown execution
    # state successful.
    return "REVIEW", "OTHER"


def apply(rule, value, row):
    op=rule["operation"].upper(); dec=(rule.get("decoder") or "scalar").lower(); text=value or ""; pattern=(rule.get("decoder_pattern") or "").strip()
    if op == "IGNORE": return [], "IGNORED"
    if op in {"COPY","RENAME","REFERENCE","ASSERT","SOURCE_CONTEXT","LOOKUP"}: return [text], "EMITTED"
    if op == "STANDARDIZE": return [text.strip()], "EMITTED"
    if op == "PATH_EXTRACT":
        parts=[p for p in text.replace("\\","/").split("/") if p]; return ([parts[-1]] if parts else []), ("EMITTED" if parts else "NO_MATCH")
    if op == "DECOMPOSE":
        if dec == "separator": return (split_semicolon(text) if ";" in text else [x.strip() for x in text.split(" / ") if x.strip()]), "EMITTED"
        if dec == "list":
            try: return [x.strip() for x in re.split(pattern,text) if x.strip()], "EMITTED"
            except re.error as exc: return [f"REGEX_ERROR:{exc}"], "ERROR"
        if dec == "labeled_fields": return [f"{k}={v}" for k,v in labeled_fields(text)], "EMITTED"
        if dec == "clauses": return clauses(text), "EMITTED"
        if dec == "regex": return regex_extract(text,pattern)
        if dec == "regex_findall": return regex_extract(text,pattern,True)
        return [text], "EMITTED"
    if op == "EXTRACT":
        if dec == "parenthetical":
            m=re.search(r"\(([^()]*)\)",text); return ([m.group(1).strip()] if m else []), ("EMITTED" if m else "NO_MATCH")
        if dec == "regex": return regex_extract(text,pattern)
        if dec == "regex_findall": return regex_extract(text,pattern,True)
        if dec == "filename":
            stem=re.sub(r"\.[^.]+$","",text); m=re.match(r"\s*(\d+)\s*[-_]\s*(.+?)\s*$",stem)
            return ([f"track={m.group(1)}",f"title={m.group(2).strip()}" ] if m else [stem]), "EMITTED"
        return [text], "EMITTED"
    if op == "DERIVE":
        if dec == "regex_boolean":
            _,s=regex_extract(text,pattern); return (["YES"] if s=="EMITTED" else []),s
        if dec == "token":
            hit="instr." in text.lower(); return (["YES"] if hit else []), ("EMITTED" if hit else "NO_MATCH")
        return [text], "EMITTED"
    return [], f"UNSUPPORTED_OPERATION:{op}"

def rule_matches(rule,value):
    p=(rule.get("match_pattern") or "").strip()
    if not p: return True
    try: return re.search(p,value or "",re.I) is not None
    except re.error: return False

def fingerprint(value): return hashlib.sha256((value or "").encode("utf-8")).hexdigest()[:16]

def work_id(source_id, source_record, rule_id): return hashlib.sha256(f"{source_id}|{source_record}|{rule_id}".encode()).hexdigest()[:20]

def load_state(path):
    if not path.exists(): return []
    return read_csv(path)

def run(source_rows,rules,bindings,state_dir,run_id=None,rosetta_version="v0.2",force=False):
    state_dir=Path(state_dir); state_dir.mkdir(parents=True,exist_ok=True)
    log_path=state_dir/"processing_log.csv"; obs_path=state_dir/"observations.csv"
    old=load_state(log_path)
    completed={r["work_item_id"]:r for r in old if r.get("status")=="COMPLETE"}
    run_id=run_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    bind={b["source_element"]:b["source_field"] for b in bindings}
    new_log=[]; new_obs=[]; skipped=0; processed=0
    for row_no,row in enumerate(source_rows,start=2):
        sid=row.get("source_id","") or f"row-{row_no}"; source_record=row.get("relative_path") or row.get("filename") or str(row_no)
        semantic_values={}
        for rule in rules:
            elem=rule["source_element"]
            direct_field=rule.get("source_field") or bind.get(elem,"")
            input_semantic=rule.get("input_semantic_term") or ""
            field=direct_field

            if direct_field:
                value=row.get(direct_field,"") or ""
            elif input_semantic:
                value=semantic_values.get(input_semantic,"")
                field=f"semantic:{input_semantic}" if value else ""
            else:
                value=""

            if not direct_field and not input_semantic and elem=="instrumental": value=row.get("metadata_artist","")
            if not direct_field and not input_semantic and elem=="has_lyrics": value=row.get("metadata_composer","")
            resolved_values = semantic_values.get(input_semantic, []) if input_semantic and not direct_field else [value]
            resolved_values = [v for v in resolved_values if v]

            if not resolved_values:
                continue

            combined_value = "\n".join(str(v) for v in resolved_values)
            wid=work_id(sid,source_record,rule["rule_id"]); fp=fingerprint(combined_value)
            prior=completed.get(wid)
            if prior and prior.get("input_fingerprint")==fp and not force:
                skipped+=1; continue

            started=datetime.now(timezone.utc).isoformat()
            attempt=int(prior.get("attempt",0))+1 if prior else 1
            total_count=0

            try:
                for resolved_value in resolved_values:
                    if not rule_matches(rule,resolved_value):
                        continue

                    decoded,status=apply(rule,resolved_value,row)
                    processing_outcome,outcome_reason = classify_processing_outcome(
                        rule, status
                    )

                    if decoded:
                        semantic_values.setdefault(elem,[])
                        semantic_values[elem].extend(decoded)

                    for item in decoded:
                        new_obs.append({
                            "run_id":run_id,
                            "source_id":sid,
                            "source_record":source_record,
                            "source_element":elem,
                            "source_field":field,
                            "source_value":resolved_value,
                            "rule_id":rule["rule_id"],
                            "semantic_term":rule.get("semantic_term",""),
                            "representation_level":rule.get("representation_level",""),
                            "information_class":rule["information_class"],
                            "operation":rule["operation"],
                            "decoder":rule["decoder"],
                            "target_entity":rule["target_entity"],
                            "target_property":rule["target_property"],
                            "target_relationship":rule["target_relationship"],
                            "assurance":rule["assurance"],
                            "preserve_source_value":rule["preserve_source_value"],
                            "decoded_value":item,
                            "status":status,
                            "processing_outcome":processing_outcome,
                            "outcome_reason":outcome_reason,
                            "residual":"",
                            "evidence_basis":rule["evidence_basis"]
                        })
                        total_count+=1

                new_log.append({
                    "run_id":run_id,
                    "work_item_id":wid,
                    "source_id":sid,
                    "source_record":source_record,
                    "rule_id":rule["rule_id"],
                    "source_element":elem,
                    "source_field":field,
                    "input_fingerprint":fp,
                    "status":"COMPLETE",
                    "attempt":attempt,
                    "started_at":started,
                    "completed_at":datetime.now(timezone.utc).isoformat(),
                    "observation_count":total_count,
                    "exception":"",
                    "engine_version":ENGINE_VERSION,
                    "rosetta_version":rosetta_version
                })
                processed+=1
            except Exception as exc:
                new_log.append({"run_id":run_id,"work_item_id":wid,"source_id":sid,"source_record":source_record,"rule_id":rule["rule_id"],"source_element":elem,"source_field":field,"input_fingerprint":fp,"status":"FAILED","attempt":attempt,"started_at":started,"completed_at":"","observation_count":0,"exception":repr(exc),"engine_version":ENGINE_VERSION,"rosetta_version":rosetta_version})
    # Preserve prior history and add this run's state/results. On reprocessing a work item,
    # the new COMPLETE row supersedes the old state for restart decisions; observations remain auditable.
    append_csv(log_path,new_log,PROCESS_FIELDS); append_csv(obs_path,new_obs,OBS_FIELDS)
    return {"run_id":run_id,"processed":processed,"skipped":skipped,"failed":sum(r["status"]=="FAILED" for r in new_log),"new_observations":len(new_obs),"log":log_path,"observations":obs_path}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("source_csv",type=Path); ap.add_argument("mapping_csv",type=Path); ap.add_argument("bindings_csv",type=Path); ap.add_argument("--state-dir",required=True,type=Path); ap.add_argument("--run-id"); ap.add_argument("--rosetta-version",default="v0.2"); ap.add_argument("--force",action="store_true")
    a=ap.parse_args(); rules=read_csv(a.mapping_csv); bindings=read_csv(a.bindings_csv); rows=read_csv(a.source_csv)
    bad=[r for r in rules if r.get("information_class") not in INFO_CLASSES or r.get("operation","").upper() not in OPERATIONS]
    if bad: raise SystemExit(f"Invalid mapping rows: {[r.get('rule_id') for r in bad]}")
    result=run(rows,rules,bindings,a.state_dir,a.run_id,a.rosetta_version,a.force)
    print(f"Run: {result['run_id']}"); print(f"Source rows: {len(rows)}"); print(f"Work items processed: {result['processed']}"); print(f"Work items skipped (already complete): {result['skipped']}"); print(f"Failed: {result['failed']}"); print(f"New observations: {result['new_observations']}"); print(f"Processing log: {result['log']}"); print(f"Observations: {result['observations']}")
if __name__=="__main__": main()
