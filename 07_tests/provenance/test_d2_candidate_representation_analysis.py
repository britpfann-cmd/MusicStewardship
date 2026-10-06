from __future__ import annotations
import json, sqlite3, subprocess, sys
from pathlib import Path

REPO_ROOT=Path(__file__).resolve().parents[2]
SCRIPT=REPO_ROOT/"08_tools"/"provenance"/"d2_candidate_representation_analysis.py"

def make_fixture(db):
    con=sqlite3.connect(db)
    con.executescript("""
    CREATE TABLE library_cards (
      library_card_id TEXT PRIMARY KEY,
      source_object_key TEXT NOT NULL
    );
    CREATE TABLE catalog_observations (
      observation_id TEXT PRIMARY KEY,
      library_card_id TEXT,
      subject_type TEXT NOT NULL,
      subject_id TEXT,
      observed_field TEXT NOT NULL,
      observed_value_json TEXT NOT NULL,
      interpreted_value_json TEXT,
      context_json TEXT,
      evidence_json TEXT,
      observed_at TEXT NOT NULL
    );
    """)

    con.executemany(
        "INSERT INTO library_cards VALUES (?,?)",
        [("lc1","SourceA:one.aif"),("lc2","SourceA:two.aif")]
    )

    rows=[
      ("o1","lc1","CATALOGED_INSTANCE","ci1","title",
       json.dumps(["Bar exposición -v"],ensure_ascii=False),
       None,"{}","{}","2026-10-06T00:00:00"),

      ("o2","lc1","CATALOGED_INSTANCE","ci1",
       "filename_leading_text_candidate",
       json.dumps(["Bar exposicion"],ensure_ascii=False),
       None,"{}","{}","2026-10-06T00:00:00"),

      ("o3","lc2","CATALOGED_INSTANCE","ci2","title",
       json.dumps(["Bar exposicion"],ensure_ascii=False),
       None,"{}","{}","2026-10-06T00:00:00"),

      ("o4","lc1","CATALOGED_INSTANCE","ci1","author_expression",
       json.dumps(["Juan Pérez"],ensure_ascii=False),
       None,"{}","{}","2026-10-06T00:00:00"),

      ("o5","lc1","CATALOGED_INSTANCE","ci1","composer_expression",
       json.dumps(["Juan Pérez"],ensure_ascii=False),
       None,"{}","{}","2026-10-06T00:00:00"),

      # Ambiguous/multiple contributor expression: preserve, but do not
      # automatically form a single Person representation.
      ("o6","lc2","CATALOGED_INSTANCE","ci2","composer_expression",
       json.dumps(["Carlos López y Juan Pérez"],ensure_ascii=False),
       None,"{}","{}","2026-10-06T00:00:00"),

      # Raw source syntax must not be decoded by D2.
      ("o7","lc2","CATALOGED_INSTANCE","ci2","composer",
       json.dumps(["Com: Source Specific Name"],ensure_ascii=False),
       None,"{}","{}","2026-10-06T00:00:00")
    ]

    con.executemany(
        "INSERT INTO catalog_observations VALUES (?,?,?,?,?,?,?,?,?,?)",
        rows
    )
    con.commit()
    con.close()

def read_jsonl(p):
    return [
        json.loads(x)
        for x in p.read_text(encoding="utf-8").splitlines()
        if x.strip()
    ]

def test_d2_candidate_representation_analysis(tmp_path):
    db=tmp_path/"catalog.sqlite"
    out=tmp_path/"d2a"
    make_fixture(db)

    c=subprocess.run(
        [sys.executable,str(SCRIPT),"--db",str(db),"--output-dir",str(out)],
        cwd=REPO_ROOT,capture_output=True,text=True
    )
    assert c.returncode==0,c.stderr

    reps=read_jsonl(out/"candidate_representations.jsonl")
    rels=read_jsonl(out/"same_ci_relationships.jsonl")
    groups=read_jsonl(out/"candidate_representation_groups.jsonl")
    candidate_sets=read_jsonl(out/"candidate_sets.jsonl")
    summary=json.loads(
        (out/"summary.json").read_text(encoding="utf-8")
    )

    assert len(reps)==5

    assert summary["representation_fields"]=={
        "author_expression":1,
        "composer_expression":1,
        "filename_leading_text_candidate":1,
        "title":2
    }

    people=[r for r in reps if r["entity_type"]=="Person"]
    assert len(people)==2

    assert {
        (r["role"],r["observed_field"],r["observed_value"])
        for r in people
    } == {
        ("author","author_expression","Juan Pérez"),
        ("composer","composer_expression","Juan Pérez")
    }

    # D2 must not reinterpret raw source-specific composer syntax.
    assert all(
        r["observed_value"]!="Com: Source Specific Name"
        for r in reps
    )

    assert len(rels)==1
    assert rels[0]["comparison_basis"]=="SUBSTANTIVE_DIFFERENCE"
    assert rels[0]["identity_asserted"] is False

    pg=[
        g for g in groups
        if g["comparison_method"]=="punctuation_spacing"
        and g["comparison_value"]=="barexposicion"
    ]
    assert len(pg)==1
    assert pg[0]["representation_count"]==2
    assert pg[0]["cataloged_instance_count"]==2
    assert pg[0]["identity_asserted"] is False

    # Candidate sets consolidate comparison methods by representation membership.
    assert summary["candidate_set_count"]==2
    assert summary["candidate_sets_by_entity_type"]=={
        "Work":1,
        "Person":1
    }
    assert summary["cross_ci_candidate_sets_by_entity_type"]=={
        "Work":1,
        "Person":0
    }

    work_sets=[s for s in candidate_sets if s["entity_type"]=="Work"]
    assert len(work_sets)==1
    assert work_sets[0]["cataloged_instance_count"]==2
    assert work_sets[0]["identity_asserted"] is False
    assert set(work_sets[0]["discovery_methods"])=={
        "unicode",
        "accent_case",
        "punctuation_spacing"
    }

    person_sets=[s for s in candidate_sets if s["entity_type"]=="Person"]
    assert len(person_sets)==1
    assert person_sets[0]["roles"]==["author","composer"]
    assert person_sets[0]["identity_asserted"] is False
    assert summary["identity_decisions_made"]==0
    assert summary["entities_created"]==0



