from __future__ import annotations
import argparse, hashlib, json, re, sqlite3, unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Any

TITLE_FIELDS={"title":"embedded_title","filename_leading_text_candidate":"filename_title"}
PERSON_FIELDS={"author_expression":"author","composer_expression":"composer"}

def scalar_text(s):
    v=json.loads(s)
    if isinstance(v,str): return v.strip()
    if isinstance(v,list) and len(v)==1 and isinstance(v[0],str): return v[0].strip()
    return ""

def unicode_form(v): return unicodedata.normalize("NFC",v)
def accent_case_form(v):
    d=unicodedata.normalize("NFD",v)
    return unicodedata.normalize("NFC","".join(c for c in d if unicodedata.category(c)!="Mn")).casefold()
def punctuation_spacing_form(v): return re.sub(r"[\W_]+","",accent_case_form(v),flags=re.UNICODE)
def stable_id(prefix,*parts):
    return f"{prefix}_{hashlib.sha256(chr(31).join(parts).encode()).hexdigest()[:20]}"

def load_title_representations(db:Path):
    con=sqlite3.connect(db); con.row_factory=sqlite3.Row
    try:
        rows=con.execute("""
        SELECT o.observation_id,o.library_card_id,o.subject_id AS cataloged_instance_id,
               o.observed_field,o.observed_value_json,lc.source_object_key
        FROM catalog_observations o JOIN library_cards lc ON lc.library_card_id=o.library_card_id
        JOIN library_card_revisions r
          ON r.library_card_revision_id=o.library_card_revision_id
        WHERE o.subject_type='CATALOGED_INSTANCE'
          AND r.revision_number = (
              SELECT MAX(r2.revision_number)
              FROM library_card_revisions r2
              WHERE r2.library_card_id=r.library_card_id
          )
          AND o.observed_field IN ('title','filename_leading_text_candidate')
        ORDER BY o.subject_id,o.observed_field,o.observation_id
        """).fetchall()
    finally: con.close()
    out=[]
    for r in rows:
        value=scalar_text(r["observed_value_json"])
        if not value: continue
        out.append({
          "representation_id":stable_id("rep",r["observation_id"],r["observed_field"],value),
          "observation_id":r["observation_id"],"entity_type":"Work",
          "observed_field":r["observed_field"],"observed_value":value,
          "cataloged_instance_id":r["cataloged_instance_id"],"library_card_id":r["library_card_id"],
          "source_object_key":r["source_object_key"],"representation_source":TITLE_FIELDS[r["observed_field"]],
          "comparison_forms":{"unicode":unicode_form(value),"accent_case":accent_case_form(value),
                              "punctuation_spacing":punctuation_spacing_form(value)}})
    return out

def is_single_contributor_expression(value):
    value=value.strip()
    return (
        bool(value)
        and "," not in value
        and "|" not in value
        and re.search(r"\s+y\s+",value,flags=re.IGNORECASE) is None
    )

def load_person_representations(db:Path):
    con=sqlite3.connect(db); con.row_factory=sqlite3.Row
    try:
        rows=con.execute("""
        SELECT o.observation_id,o.library_card_id,
               o.subject_id AS cataloged_instance_id,
               o.observed_field,o.observed_value_json,
               lc.source_object_key
        FROM catalog_observations o
        JOIN library_cards lc ON lc.library_card_id=o.library_card_id
        JOIN library_card_revisions r
          ON r.library_card_revision_id=o.library_card_revision_id
        WHERE o.subject_type='CATALOGED_INSTANCE'
          AND r.revision_number = (
              SELECT MAX(r2.revision_number)
              FROM library_card_revisions r2
              WHERE r2.library_card_id=r.library_card_id
          )
          AND o.observed_field IN ('author_expression','composer_expression')
        ORDER BY o.subject_id,o.observed_field,o.observation_id
        """).fetchall()
    finally: con.close()

    out=[]
    for r in rows:
        value=scalar_text(r["observed_value_json"])
        if not value or not is_single_contributor_expression(value):
            continue

        field=r["observed_field"]
        role=PERSON_FIELDS[field]

        out.append({
          "representation_id":stable_id("rep",r["observation_id"],field,value),
          "observation_id":r["observation_id"],
          "entity_type":"Person",
          "role":role,
          "observed_field":field,
          "observed_value":value,
          "cataloged_instance_id":r["cataloged_instance_id"],
          "library_card_id":r["library_card_id"],
          "source_object_key":r["source_object_key"],
          "representation_source":"decoded_role_expression",
          "comparison_forms":{
              "unicode":unicode_form(value),
              "accent_case":accent_case_form(value),
              "punctuation_spacing":punctuation_spacing_form(value)
          }})
    return out
def equivalence_basis(a,b):
    if a["observed_value"]==b["observed_value"]: return "EXACT"
    if a["comparison_forms"]["unicode"]==b["comparison_forms"]["unicode"]: return "UNICODE_EQUIVALENT"
    if a["comparison_forms"]["accent_case"]==b["comparison_forms"]["accent_case"]: return "ACCENT_CASE_EQUIVALENT"
    if a["comparison_forms"]["punctuation_spacing"]==b["comparison_forms"]["punctuation_spacing"]: return "PUNCTUATION_SPACING_EQUIVALENT"
    return None

def build_same_ci_relationships(reps):
    by=defaultdict(list)
    for r in reps: by[r["cataloged_instance_id"]].append(r)
    out=[]
    for ci,m in sorted(by.items()):
        for i in range(len(m)):
            for j in range(i+1,len(m)):
                a,b=m[i],m[j]
                out.append({"relationship_id":stable_id("rel","SAME_CI",a["representation_id"],b["representation_id"]),
                  "relationship_type":"SAME_CI","cataloged_instance_id":ci,
                  "left_representation_id":a["representation_id"],"right_representation_id":b["representation_id"],
                  "comparison_basis":equivalence_basis(a,b) or "SUBSTANTIVE_DIFFERENCE","identity_asserted":False})
    return out

def build_comparison_groups(reps):
    out=[]
    for method in ("unicode","accent_case","punctuation_spacing"):
        buckets=defaultdict(list)
        for r in reps:
            key=(r["entity_type"],r["comparison_forms"][method])
            if key[1]: buckets[key].append(r)
        for (entity_type,value),m in buckets.items():
            if len(m)<2: continue
            out.append({"group_id":stable_id("grp",entity_type,method,value),"entity_type":entity_type,"comparison_method":method,"comparison_value":value,"representation_count":len(m),"cataloged_instance_count":len({x["cataloged_instance_id"] for x in m}),"representation_ids":[x["representation_id"] for x in m],"identity_asserted":False})
    return sorted(out,key=lambda g:(g["entity_type"],g["comparison_method"],g["comparison_value"],g["group_id"]))

def build_candidate_sets(groups,reps):
    """Consolidate comparison groups having identical representation membership."""
    rep_by_id={r["representation_id"]:r for r in reps}
    by_members=defaultdict(list)

    for g in groups:
        members=tuple(sorted(g["representation_ids"]))
        by_members[(g["entity_type"],members)].append(g)

    out=[]
    for (entity_type,members),variants in by_members.items():
        member_reps=[rep_by_id[rid] for rid in members]
        ci_ids=sorted({
            r["cataloged_instance_id"]
            for r in member_reps
        })
        roles=sorted({
            r["role"]
            for r in member_reps
            if r.get("role")
        })
        methods=sorted({
            g["comparison_method"]
            for g in variants
        })

        out.append({
            "candidate_set_id":stable_id(
                "set",entity_type,*members
            ),
            "entity_type":entity_type,
            "representation_ids":list(members),
            "cataloged_instance_ids":ci_ids,
            "representation_count":len(members),
            "cataloged_instance_count":len(ci_ids),
            "discovery_methods":methods,
            "roles":roles,
            "identity_asserted":False
        })

    return sorted(
        out,
        key=lambda s:(
            s["entity_type"],
            s["candidate_set_id"]
        )
    )
def write_jsonl(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text("".join(json.dumps(r,ensure_ascii=False,sort_keys=True)+"\n" for r in rows),encoding="utf-8")

def main():
    p=argparse.ArgumentParser(description="Report-only D2 candidate representation analysis.")
    p.add_argument("--db",type=Path,required=True); p.add_argument("--output-dir",type=Path,required=True)
    a=p.parse_args()
    work_reps=load_title_representations(a.db); person_reps=load_person_representations(a.db); reps=work_reps+person_reps; rels=build_same_ci_relationships(work_reps); groups=build_comparison_groups(reps); candidate_sets=build_candidate_sets(groups,reps)
    a.output_dir.mkdir(parents=True,exist_ok=True)
    write_jsonl(a.output_dir/"candidate_representations.jsonl",reps)
    write_jsonl(a.output_dir/"same_ci_relationships.jsonl",rels)
    write_jsonl(a.output_dir/"candidate_representation_groups.jsonl",groups)
    write_jsonl(a.output_dir/"candidate_sets.jsonl",candidate_sets)
    summary={"database":str(a.db),"entity_types":["Work","Person"],"representation_count":len(reps),"representations_by_entity_type":{t:sum(r["entity_type"]==t for r in reps) for t in ("Work","Person")},
      "representation_fields":{f:sum(r["observed_field"]==f for r in reps) for f in sorted(set(TITLE_FIELDS)|set(PERSON_FIELDS))},
      "same_ci_relationship_count":len(rels),
      "same_ci_comparison_basis":{b:sum(r["comparison_basis"]==b for r in rels) for b in sorted({r["comparison_basis"] for r in rels})},
      "comparison_group_count":len(groups),
      "candidate_set_count":len(candidate_sets),
      "candidate_sets_by_entity_type":{t:sum(s["entity_type"]==t for s in candidate_sets) for t in ("Work","Person")},
      "cross_ci_candidate_sets_by_entity_type":{t:sum(s["entity_type"]==t and s["cataloged_instance_count"]>1 for s in candidate_sets) for t in ("Work","Person")},
      "comparison_groups_by_method":{m:sum(g["comparison_method"]==m for g in groups) for m in sorted({g["comparison_method"] for g in groups})},
      "identity_decisions_made":0,"entities_created":0}
    (a.output_dir/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())




