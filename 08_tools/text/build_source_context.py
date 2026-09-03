#!/usr/bin/env python3
"""Build reusable directory/source context from a source-tree baseline."""

from __future__ import annotations
import argparse, csv, re
from collections import Counter, defaultdict
from pathlib import Path

def read_csv(p):
    with p.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def write_csv(p, rows):
    rows = list(rows)
    fields = list(rows[0]) if rows else []
    with p.open("w", encoding="utf-8", newline="") as f:
        if fields:
            w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)

def integer(x, d=0):
    try: return int(x)
    except: return d

def classify(name):
    s=(name or "").strip()
    if not s or s==".": return "ROOT"
    if re.fullmatch(r"\d+",s): return "NUMBERED"
    if re.search(r"\b(?:19|20)\d{2}\b",s): return "PERIOD_LIKE"
    if re.fullmatch(r"[A-Za-z]{0,5}[-_ ]?\d{3,}",s): return "IDENTIFIER_LIKE"
    return "TEXT_NAME"

def tokens(name):
    s=(name or "").casefold(); r=[]
    pats=[("CORTINA",r"\bcortinas?\b"),("RELEASE",r"\breleases?\b"),
          ("COMPILATION",r"\bcompilations?\b"),("TANGO",r"\btangos?\b"),
          ("MILONGA",r"\bmilongas?\b"),("VALS",r"\bvals(?:es)?\b"),
          ("INSTRUMENTAL",r"\binstrumental(?:es)?\b"),
          ("VOCAL",r"\b(?:vocal|vocals|cantado|cantores)\b")]
    for k,p in pats:
        if re.search(p,s): r.append(k)
    if "digital booklet" in s: r.append("DIGITAL_BOOKLET")
    if re.search(r"\b(?:19|20)\d{2}\b",s): r.append("PERIOD")
    return r

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("tree_dir",type=Path)
    ap.add_argument("--output",required=True,type=Path)
    a=ap.parse_args(); a.output.parent.mkdir(parents=True,exist_ok=True)
    dirs=read_csv(a.tree_dir/"source_tree_directories.csv")
    files=read_csv(a.tree_dir/"source_tree_files.csv")
    audio=Counter((x["source_id"],x["directory_path"]) for x in files if x.get("is_audio")=="YES")
    children=Counter((x["source_id"],x["parent_path"]) for x in dirs)
    rows=[]
    for d in dirs:
        sid=d["source_id"]; path=d["directory_path"]; name=d["directory_name"]
        state=("AUDIO_LEAF" if integer(d.get("directory_count"))==0 and audio[(sid,path)] else
               "AUDIO_AND_CHILDREN" if audio[(sid,path)] else "CONTAINER")
        parts=path.replace("\\","/").strip("/").split("/") if path!="." else []
        sig=[]
        for i,part in enumerate(parts):
            parent="/".join(parts[:i]) if i else "."
            pd=next((z for z in dirs if z["source_id"]==sid and z["directory_path"]==parent),None)
            pstate=pd.get("_state","CONTAINER") if pd else "CONTAINER"
            sig.append(f"{classify(part)}:{pstate}")
        rows.append({
            "source_id":sid,"directory_path":path,"directory_name":name,
            "parent_path":d["parent_path"],"depth":d["depth"],
            "directory_state":state,"audio_file_count":audio[(sid,path)],
            "child_directory_count":integer(d.get("directory_count")),
            "name_shape":classify(name),"semantic_tokens":";".join(tokens(name)),
            "hierarchy_signature":" / ".join(sig),
            "source_evidence_basis":"source tree structure; candidate only"
        })
    write_csv(a.output,rows)
    print(f"Source context records: {len(rows)}")
    print(f"Output: {a.output}")

if __name__=="__main__": main()
