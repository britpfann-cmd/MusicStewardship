#!/usr/bin/env python3
"""Common Rosetta recombination -> certified Rev A or Rev B Library Card.

The public Library Card field set is defined by the authoritative revision-specific public map.
Source-specific semantic interpretation is supplied by Rosetta observations.
Common recombination assembles semantics having legitimate Rev A destinations
and preserves other source/Rosetta evidence without inventing additional
source-specific interpretation.
"""
from __future__ import annotations
import argparse, csv, hashlib, json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "04_src"))

from library_card_interface import certified_interface

ARRAY_FIELDS = set()

def read_csv(path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w=csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)

def validate_public_map(path, contract):
    rows=read_csv(path)
    definitions=list(contract.fields)

    if len(rows) != len(definitions):
        raise ValueError(
            "C-side public map field count does not match certified "
            f"{contract.interface_id} revision {contract.revision}: "
            f"{len(rows)} map rows vs {len(definitions)} certified fields"
        )

    for position, (row, definition) in enumerate(
        zip(rows, definitions), start=1
    ):
        expected_required=str(definition["Required"]).strip().lower()
        actual_required=str(row.get("required","")).strip().lower()

        checks = (
            ("interface_revision", row.get("interface_revision",""),
             contract.revision),
            ("public_field", row.get("public_field",""),
             definition["Field"]),
            ("cardinality", row.get("cardinality",""),
             definition["Cardinality"]),
            ("required", actual_required, expected_required),
        )

        for attribute, actual, expected in checks:
            if actual != expected:
                raise ValueError(
                    f"C-side public map row {position} {attribute} mismatch "
                    f"for certified {contract.interface_id} revision "
                    f"{contract.revision}: expected {expected!r}, "
                    f"got {actual!r}"
                )

    return rows

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

def select_current_observations(observation_rows, processing_rows):
    """Select observations belonging to the latest COMPLETE work-item attempt.

    Processing history remains append-only. A COMPLETE attempt with zero
    observations supersedes an earlier successful attempt. Failed attempts do
    not replace the last successful attempt.
    """
    latest = {}
    attempt_keys = set()
    for log in processing_rows:
        if log.get("status") != "COMPLETE":
            continue
        work = log.get("work_item_id", "")
        key = (log.get("run_id", ""), log.get("source_id", ""),
               log.get("source_record", ""), log.get("rule_id", ""))
        if not all(key) or not work:
            raise ValueError("Incomplete COMPLETE processing-log entry")
        if key in attempt_keys:
            raise ValueError(
                "Ambiguous processing history: repeated run/source/record/rule "
                f"identity {key!r}"
            )
        attempt_keys.add(key)
        latest[work] = log

    selected_keys = {
        (entry["run_id"], entry["source_id"],
         entry["source_record"], entry["rule_id"])
        for entry in latest.values()
    }
    selected = [o for o in observation_rows if
                (o.get("run_id", ""), o.get("source_id", ""),
                 o.get("source_record", ""), o.get("rule_id", ""))
                in selected_keys]

    counts = {}
    for o in selected:
        key = (o["run_id"], o["source_id"], o["source_record"], o["rule_id"])
        counts[key] = counts.get(key, 0) + 1
    for entry in latest.values():
        key = (entry["run_id"], entry["source_id"],
               entry["source_record"], entry["rule_id"])
        expected = int(entry.get("observation_count", "0") or "0")
        if counts.get(key, 0) != expected:
            raise ValueError(
                f"Processing history observation-count mismatch for {key!r}: "
                f"expected {expected}, found {counts.get(key, 0)}"
            )
    return selected


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("source_csv",type=Path)
    ap.add_argument("--public-map",required=True,type=Path)
    ap.add_argument("--interface-revision",required=True)
    ap.add_argument("--observations",required=True,type=Path)
    ap.add_argument("--processing-log",type=Path,
                    help="Use latest successful work-item observations across runs")
    ap.add_argument("--run-id",required=True)
    ap.add_argument("--output",required=True,type=Path)
    ap.add_argument("--report",required=True,type=Path)
    args=ap.parse_args()

    source=read_csv(args.source_csv)
    contract=certified_interface(args.interface_revision)
    fields=list(contract.field_names)

    validate_public_map(args.public_map, contract)

    all_observations = read_csv(args.observations)
    if args.processing_log is not None:
        observations = select_current_observations(
            all_observations, read_csv(args.processing_log)
        )
    else:
        # Legacy Rev A behavior, preserved for existing callers.
        observations = [o for o in all_observations
                        if o.get("run_id") == args.run_id]
    observations_by_record={}
    for o in observations:
        key=(o.get("source_id",""),o.get("source_record",""))
        observations_by_record.setdefault(key,[]).append(o)

    cards=[]
    source_count=len(source)
    for row in source:
        sid=row.get("source_id","")
        rel=row.get("relative_path","")
        card={f:"" for f in fields}
        card["card_revision"]="0"
        card["library_card_interface_revision"]=contract.revision
        card["c_processing_revision"]="common_rosetta_recombination"
        card["source_object_id"]=stable_id(sid,rel)
        card["source_object_key"]=f"{sid}:{rel}"
        card["source_record_revision"]="source_ingest.v2"
        card["source_root"]=row.get("source_root","")
        card["relative_path"]=rel
        card["filename"]=row.get("filename","")
        card["extension"]=Path(row.get("filename","")).suffix.lstrip(".")
        card["entry_type"]="audio" if row.get("asset_acceptance")=="RETAIN" else ""
        residual=[]

        # Rev B adds explicit source provenance and full semantic observations.
        # Rev A remains byte-for-byte equivalent in its public field values.
        if contract.revision == "B":
            card["source_id"] = sid
            card["source_record"] = (rel or row.get("filename", ""))
            if not sid or not card["source_record"]:
                raise ValueError("Rev B requires source_id and source_record")

        # Common recombination of source-specific Rosetta observations.
        rosetta_obs=observations_by_record.get((sid,rel),[])
        if contract.revision == "B":
            # Preserve the complete observation records, not only the reduced
            # evidence_summary projection used in Rev A.
            card["semantic_observations"] = json.dumps(
                rosetta_obs, ensure_ascii=False
            )

        semantic_targets={
            ("Composition","title"):"title",
            ("Composition","alternate_title"):"filename_leading_text_candidate",
            ("Source Assertion","source_composer"):"composer",
            ("Recording","date"):"recording_date",
            ("Ensemble","source_album_artist"):"orchestra_or_album_artist",
            ("Release","title"):"source_album",
            ("Performance","genre"):"genre",
            ("Person","name","credit:Composer"):"composer",
            ("Person","name","credit:Conductor"):"conductor",
            ("Identifier","component","record/matrix/take"):"recording_identifier",
        }
        for o in rosetta_obs:
            entity=o.get("target_entity","")
            prop=o.get("target_property","")
            relationship=o.get("target_relationship","")
            canon=semantic_targets.get(
                (entity,prop,relationship),
                semantic_targets.get((entity,prop))
            )
            value=o.get("decoded_value","")
            if canon and value:
                arr=json.loads(card[canon]) if card[canon] else []
                card[canon]=json.dumps(uniq(arr+[value]),ensure_ascii=False)

        # Rosetta assertions remain evidence even when Rev A has no
        # appropriately neutral catalog field for them.
        rosetta_evidence=[
            {
                "rule_id":o.get("rule_id",""),
                "semantic_term":o.get("semantic_term",""),
                "representation_level":o.get("representation_level",""),
                "target_entity":o.get("target_entity",""),
                "target_property":o.get("target_property",""),
                "target_relationship":o.get("target_relationship",""),
                "source_value":o.get("source_value",""),
                "decoded_value":o.get("decoded_value",""),
                "assurance":o.get("assurance",""),
                "evidence_basis":o.get("evidence_basis",""),
            }
            for o in rosetta_obs
        ]

        # Source context is ordered and preserved.
        ctx=[]
        for sf in ("directory_path","directory_name","hierarchy_signature"):
            ctx += get_values(row,sf)
        card["source_context"]=json.dumps(uniq(ctx),ensure_ascii=False) if ctx else ""

        # Compact evidence summary.
        ev=[]
        for sf in ("evidence_sources","filename_rule_status","embedded_metadata_status","source_rule_set"):
            if row.get(sf): ev.append(f"{sf}={row[sf]}")
        if rosetta_evidence:
            ev.extend(rosetta_evidence)
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
        "interface_revision":contract.revision,
        "rosetta_run_id":args.run_id,
        "rosetta_observations":len(observations),
        "observation_selection": ("latest_complete" if args.processing_log
                                  else "run_id"),
    }
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps(report,indent=2))

if __name__=="__main__":
    main()

