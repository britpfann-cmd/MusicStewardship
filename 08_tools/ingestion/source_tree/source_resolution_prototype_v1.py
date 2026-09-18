"""
MusicStewardship Resolution Prototype v1

Evidence synthesis only. No entity matching, fuzzy matching, or external lookup.
"""

import argparse
import json
from collections import defaultdict
from pathlib import Path

SCHEMA = "musicstewardship.resolution.v1"


def classify_channel(observation):
    channel = observation.get("evidence_channel")
    if channel:
        return channel

    et = observation.get("evidence_type", "")
    if et.startswith("directory."):
        return "directory"
    if et.startswith("filename."):
        return "filename"
    if et.startswith("metadata."):
        return "embedded_metadata"
    if et.startswith("technical."):
        return "technical"
    return "source_specific"


def metadata_attribute(observation):
    locator = observation.get("source_locator", "")
    if locator.startswith("metadata.tag."):
        return locator[len("metadata.tag."):]
    return None


def direct_metadata_proposition(observation):
    attr = metadata_attribute(observation)
    if not attr:
        return None

    value = observation.get("normalized_value")
    if value in (None, ""):
        value = observation.get("raw_value")

    if value in (None, ""):
        return None

    return {
        "attribute": attr,
        "value": value,
        "status": "resolved",
        "supported_by": [observation["evidence_id"]],
        "context_used": [],
        "derivation": "direct_embedded_metadata",
        "notes": "Direct metadata observation; canonical entity/value resolution is deferred.",
    }


def build_record(record):
    observations = record.get("observations", [])

    evidence = defaultdict(list)
    for obs in observations:
        evidence[classify_channel(obs)].append(obs)

    # One initial evidence set contains every observation belonging to
    # the source object. This intentionally keeps the complete context
    # available to later source-specific interpretation rules.
    all_ids = [o["evidence_id"] for o in observations]

    propositions = []
    seen = set()

    # v1 only treats direct embedded metadata as a semantic proposition.
    # Directory and filename observations are preserved as contextual
    # evidence until source-specific interpretation rules are established.
    for obs in observations:
        prop = direct_metadata_proposition(obs)
        if not prop:
            continue

        key = (prop["attribute"], json.dumps(prop["value"], ensure_ascii=False, sort_keys=True))
        if key in seen:
            continue
        seen.add(key)

        prop["proposition_id"] = f"proposition:{len(propositions)+1:06d}"
        prop["context_used"] = [
            o["evidence_id"]
            for o in observations
            if classify_channel(o) in {"directory", "filename"}
        ]
        propositions.append(prop)

    if not propositions:
        status = "unresolved"
    else:
        status = "partially_resolved"

    return {
        "resolution_record_id": f"resolution:{record['candidate_record_id'].split(':')[-1]}",
        "schema": SCHEMA,
        "source": {
            "candidate_record_id": record["candidate_record_id"],
            **record.get("source", {}),
        },
        "context": {
            "directory_observations": [o["evidence_id"] for o in evidence.get("directory", [])],
            "filename_observations": [o["evidence_id"] for o in evidence.get("filename", [])],
            "related_source_objects": [],
        },
        "evidence": {
            channel: [o["evidence_id"] for o in obs]
            for channel, obs in sorted(evidence.items())
        },
        "evidence_sets": [
            {
                "evidence_set_id": f"evidence_set:{record['candidate_record_id'].split(':')[-1]}",
                "purpose": "complete_source_object",
                "observation_ids": all_ids,
            }
        ],
        "propositions": propositions,
        "resolution_status": status,
        "residual_evidence": list(record.get("residual_evidence", [])),
        "lineage": record.get("lineage", {}),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-input", required=True, help="Candidate Record JSON")
    ap.add_argument("-o", "--output", required=True, help="Output path without extension")
    args = ap.parse_args()

    with open(args.input, encoding="utf-8") as f:
        data = json.load(f)

    records = data.get("records", [])
    out_records = [build_record(r) for r in records]

    output = {
        "schema": SCHEMA,
        "source_root": data.get("source_root"),
        "source_label": data.get("source_label"),
        "builder": "resolution_prototype_v1",
        "input": args.input,
        "record_count": len(out_records),
        "records": out_records,
    }

    base = Path(args.output)
    json_path = base.with_suffix(".json")
    md_path = base.with_suffix(".md")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    lines = [
        "# MusicStewardship Resolution Prototype v1",
        "",
        f"- Candidate Records processed: {len(out_records)}",
        "",
    ]

    for r in out_records:
        lines.append(f"## {r['resolution_record_id']}")
        lines.append(f"- Source: `{r['source'].get('relative_path', '')}`")
        lines.append(f"- Status: **{r['resolution_status']}**")
        lines.append(f"- Propositions: {len(r['propositions'])}")
        for p in r["propositions"]:
            lines.append(
                f"  - `{p['attribute']}` = `{p['value']}` "
                f"({p['status']}; supported by {len(p['supported_by'])} observation(s))"
            )
        lines.append("")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"JSON: {json_path}")
    print(f"Markdown: {md_path}")
    print(f"Resolution Records: {len(out_records)}")
    print(f"Propositions: {sum(len(r['propositions']) for r in out_records)}")


if __name__ == "__main__":
    main()
