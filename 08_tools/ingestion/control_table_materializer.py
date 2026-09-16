#!/usr/bin/env python3
"""Generic MusicStewardship source-control-table materializer."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

OPERATIONS = {
    "COPY", "RENAME", "STANDARDIZE", "DECOMPOSE", "COMBINE", "LOOKUP",
    "EXTRACT", "PATH_EXTRACT", "DERIVE", "REFERENCE", "IGNORE",
    "SOURCE_CONTEXT", "ASSERT",
}

REQUIRED_CONTROL_FIELDS = {
    "control_id", "source", "source_name", "source_field", "semantic_term",
    "representation_level", "operation", "decoder", "target_entity",
    "target_property", "target_relationship", "preserve_source_value",
    "confidence", "status", "notes",
}

ENGINE_FIELDS = [
    "rule_id", "source", "source_element", "source_field", "source_pattern",
    "information_class", "operation", "decoder", "target_entity",
    "target_property", "target_relationship", "assurance",
    "preserve_source_value", "confidence", "status", "rule",
    "evidence_basis", "match_pattern", "decoder_pattern", "input_role",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(
            line for line in f if not line.lstrip().startswith("#")
        ))


def info_class(level: str) -> str:
    value = (level or "").strip().lower()
    if value in {"source", "source→semantic", "source->semantic"}:
        return "CORE"
    if value == "residual":
        return "RESIDUAL"
    return "ASSOCIATED"


def materialize(controls: list[dict[str, str]], evidence_label: str):
    if not controls:
        raise ValueError("Control table contains no rows.")

    missing = REQUIRED_CONTROL_FIELDS - set(controls[0])
    if missing:
        raise ValueError(
            "Missing control-table columns: " + ", ".join(sorted(missing))
        )

    seen: set[str] = set()
    rules = []

    for c in controls:
        cid = (c.get("control_id") or "").strip()
        semantic = (c.get("semantic_term") or "").strip()
        operation = (c.get("operation") or "").strip().upper()

        if not cid:
            raise ValueError("Blank control_id.")
        if cid in seen:
            raise ValueError(f"Duplicate control_id: {cid}")
        if not semantic:
            raise ValueError(f"{cid}: blank semantic_term.")
        if operation not in OPERATIONS:
            raise ValueError(f"{cid}: unsupported operation {operation!r}.")

        rules.append({
            "rule_id": cid,
            "source": c.get("source", ""),
            "source_element": semantic,
            # Each executable rule carries its own source field. This is the
            # key change that permits multiple source representations of one
            # semantic term.
            "source_field": c.get("source_field", ""),
            "source_pattern": c.get("source_name", ""),
            "information_class": info_class(c.get("representation_level", "")),
            "operation": operation,
            "decoder": c.get("decoder", ""),
            "target_entity": c.get("target_entity", ""),
            "target_property": c.get("target_property", ""),
            "target_relationship": c.get("target_relationship", ""),
            "assurance": "OBSERVED",
            "preserve_source_value": c.get("preserve_source_value", ""),
            "confidence": c.get("confidence", ""),
            "status": c.get("status", ""),
            "rule": c.get("notes", ""),
            "evidence_basis": evidence_label,
            "match_pattern": c.get("match_pattern", ""),
            "decoder_pattern": c.get("decoder_pattern", ""),
            "input_role": c.get("input_role", ""),
        })
        seen.add(cid)

    return rules


def write_csv(path: Path, rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=ENGINE_FIELDS,
                                extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("control_csv", type=Path)
    ap.add_argument("output_csv", type=Path)
    ap.add_argument("--evidence-label", default="Source control table")
    args = ap.parse_args()

    controls = read_csv(args.control_csv)
    rules = materialize(controls, args.evidence_label)
    write_csv(args.output_csv, rules)

    print(f"Control rows:       {len(controls)}")
    print(f"Materialized rules: {len(rules)}")
    print(f"Output:             {args.output_csv}")


if __name__ == "__main__":
    main()
