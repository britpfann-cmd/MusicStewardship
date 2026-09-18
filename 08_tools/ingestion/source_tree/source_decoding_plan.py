#!/usr/bin/env python3
"""Build a conservative decoding plan from a source semantic map.

The semantic map records observed structure.  This layer converts those
observations into candidate decoding operations, without assigning canonical
musical meaning.  A plan says what can be decoded and why; it does not claim
that a field such as "orchestra", "year", or "catalog number" has been proven.

Input:
    source_semantic_map.py JSON output

Output:
    <output>.json
    <output>.md

Design:
    Observe -> Propose decoding -> Extract candidates -> Confirm / Resolve

The plan is source-agnostic.  Source-specific semantics belong in later
profiles/rules, after confirmation.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "musicstewardship.source_tree_decoding_plan.v1"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Build a conservative decoding plan from a source semantic map."
    )
    p.add_argument("-input", required=True, help="Semantic-map JSON produced by source_semantic_map.py")
    p.add_argument("-o", "--output", required=True, help="Output path without .json/.md")
    return p.parse_args()


def add_plan(
    plans: list[dict[str, Any]],
    *,
    target: str,
    operation: str,
    evidence: list[str],
    confidence: str = "observed",
    notes: str = "",
) -> None:
    plans.append(
        {
            "target": target,
            "operation": operation,
            "confidence": confidence,
            "evidence": evidence,
            "notes": notes,
        }
    )


def analyze_filename_structure(
    inspection: dict[str, Any],
    plans: list[dict[str, Any]],
) -> None:
    """Turn observed filename regularities into generic candidate operations."""
    files = [
        c for c in inspection.get("children", [])
        if c.get("entry_type") == "FILE" and "filename" in c
    ]
    audio = [
        c for c in files
        if c["filename"].get("extension") in {".aif", ".aiff", ".flac", ".m4a", ".mp3", ".wav"}
    ]
    if not audio:
        return

    structures = [c["filename"].get("structure", {}) for c in audio]

    numeric_present = sum(bool(s.get("numeric_components")) for s in structures)
    suffixes = Counter(
        s.get("terminal_suffix")
        for s in structures
        if s.get("terminal_suffix")
    )

    if numeric_present == len(audio):
        add_plan(
            plans,
            target="filename.numeric_component",
            operation="extract_numeric_component",
            evidence=[
                f"{numeric_present}/{len(audio)} audio filenames contain an observable numeric component."
            ],
            notes="Extract the observed numeric token as source evidence; do not assign catalog/year/track meaning yet.",
        )

    text_before_number = 0
    for c in audio:
        stem = c["filename"].get("stem", "")
        match = re.search(r"\d+(?:-\d+)?", stem)
        if match and stem[:match.start()].strip():
            text_before_number += 1

    if text_before_number:
        add_plan(
            plans,
            target="filename.leading_text",
            operation="extract_text_before_first_numeric_component",
            evidence=[
                f"{text_before_number}/{len(audio)} audio filenames contain nonempty text before the first numeric component."
            ],
            notes="Preserve as a title/text candidate only. Confirmation is required before assigning a musical field.",
        )

    if suffixes:
        suffix_text = ", ".join(f"{k}={v}" for k, v in sorted(suffixes.items()))
        add_plan(
            plans,
            target="filename.terminal_suffix",
            operation="extract_terminal_suffix",
            evidence=[
                f"Observed terminal suffixes among audio filenames: {suffix_text}."
            ],
            notes=(
                "Record every observed suffix value exactly as source evidence. "
                "This extraction operation itself preserves the observed categorical "
                "values; a second preservation operation must not duplicate them. "
                "Their semantic meaning is not established by pattern analysis alone."
            ),
        )


def analyze_sequence_evidence(
    inspection: dict[str, Any],
    plans: list[dict[str, Any]],
) -> None:
    """Detect strong local sequence evidence without assigning its meaning."""
    audio_exts = {".aif", ".aiff", ".flac", ".m4a", ".mp3", ".wav"}
    leading_numbers: list[int] = []

    for child in inspection.get("children", []):
        if child.get("entry_type") != "FILE":
            continue
        filename = child.get("filename", {})
        if filename.get("extension") not in audio_exts:
            continue

        stem = str(filename.get("stem", ""))
        match = re.match(r"^\s*(\d+)(?:\s*[-.]|\s+)", stem)
        if match:
            leading_numbers.append(int(match.group(1)))

    if len(leading_numbers) < 5:
        return

    unique = sorted(set(leading_numbers))
    minimum = unique[0]
    maximum = unique[-1]
    span = maximum - minimum + 1
    coverage = len(unique) / span if span else 0.0
    duplicates = len(leading_numbers) - len(unique)

    # A near-complete local numeric range is evidence of a sequence, but
    # sequence evidence does not establish what the sequence represents.
    if coverage >= 0.90:
        add_plan(
            plans,
            target="filename.leading_numeric_component",
            operation="identify_sequence_number_candidate",
            evidence=[
                f"{len(leading_numbers)} audio filenames have a leading numeric component.",
                f"Observed unique values span {minimum}–{maximum} with {len(unique)}/{span} values present ({coverage:.1%} coverage).",
                f"The inspected population contains {duplicates} duplicate leading-number value(s).",
            ],
            notes=(
                "The local population provides sequence evidence. Record the leading "
                "numeric component as a sequence-number candidate, preserving its "
                "original numeric observation. Do not assign track, catalog, year, "
                "date, or other semantic meaning at this layer."
            ),
        )

def analyze_directory_evidence(
    inspection: dict[str, Any],
    plans: list[dict[str, Any]],
) -> None:
    """Identify useful directory-level evidence without naming its meaning."""
    obs = inspection.get("observations", {})
    dirs = [c for c in inspection.get("children", []) if c.get("entry_type") == "DIRECTORY"]

    if not dirs:
        return

    names = [d.get("name", "") for d in dirs]
    if len(names) == len(set(names)):
        add_plan(
            plans,
            target="parent_directory.name",
            operation="preserve_directory_component",
            evidence=[
                f"The inspected node contains {len(names)} immediate directory names.",
                "Directory names are source-organization evidence and remain attached to descendant files.",
            ],
            notes="Directory position and value may later become decoding evidence; do not assign canonical semantics here.",
        )

    shapes = obs.get("pattern_analysis", {}).get("directory_name_shapes", [])
    if shapes:
        repeated = [x for x in shapes if x.get("count", 0) > 1]
        if repeated:
            add_plan(
                plans,
                target="directory.name_pattern",
                operation="retain_repeated_directory_pattern",
                evidence=[
                    "Repeated directory-name shapes were observed at this level."
                ],
                notes="Repeated shapes can support a later directory decoder, but repetition alone does not establish field meaning.",
            )


def analyze_file_population(
    inspection: dict[str, Any],
    plans: list[dict[str, Any]],
) -> None:
    obs = inspection.get("observations", {})
    extensions = obs.get("file_extensions", {})
    if not extensions:
        return

    audio_exts = {".aif", ".aiff", ".flac", ".m4a", ".mp3", ".wav"}
    audio_count = sum(v for k, v in extensions.items() if k in audio_exts)
    if audio_count:
        add_plan(
            plans,
            target="file.entry_type",
            operation="classify_audio_by_extension",
            evidence=[
                f"{audio_count} immediate files use recognized audio filename extensions."
            ],
            notes="This is a file-classification observation, not a statement about musical content.",
        )

    non_audio = sum(v for k, v in extensions.items() if k not in audio_exts)
    if non_audio:
        add_plan(
            plans,
            target="file.entry_type",
            operation="preserve_non_audio_source_artifacts",
            evidence=[
                f"{non_audio} immediate files do not use the recognized audio extensions."
            ],
            notes="Do not discard associated graphics, documentation, metadata, or other source artifacts.",
        )


def build_plan(data: dict[str, Any]) -> dict[str, Any]:
    plans: list[dict[str, Any]] = []

    for inspection in data.get("inspections", []):
        rel = inspection.get("node", {}).get("relative_path", ".")
        before = len(plans)

        analyze_directory_evidence(inspection, plans)
        analyze_file_population(inspection, plans)
        analyze_filename_structure(inspection, plans)
        analyze_sequence_evidence(inspection, plans)

        for plan in plans[before:]:
            plan["scope"] = rel

    return {
        "schema": SCHEMA,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source_map_schema": data.get("schema"),
        "source_root": data.get("source_root"),
        "source_map_inspection_mode": data.get("inspection_mode"),
        "plan_status": "candidate_decoding_plan",
        "principle": "The plan converts observed structure into candidate decoding operations; it does not assign canonical meaning.",
        "plans": plans,
    }


def markdown(data: dict[str, Any]) -> str:
    lines = [
        "# Source Decoding Plan",
        "",
        "> Candidate decoding operations derived from observed source structure. "
        "This plan does not assign canonical musical meaning.",
        "",
        "## Source",
        "",
        f"- **Root:** `{data.get('source_root', {}).get('path', '')}`",
        f"- **Source map schema:** `{data.get('source_map_schema')}`",
        f"- **Status:** `{data.get('plan_status')}`",
        "",
        "## Candidate decoding operations",
        "",
    ]

    plans = data.get("plans", [])
    if not plans:
        lines += [
            "No decoding operations were proposed from the supplied observations.",
            "",
        ]
    else:
        for i, plan in enumerate(plans, 1):
            lines += [
                f"### {i}. `{plan['target']}`",
                "",
                f"- **Operation:** `{plan['operation']}`",
                f"- **Scope:** `{plan['scope']}`",
                f"- **Confidence:** `{plan['confidence']}`",
                "- **Evidence:**",
            ]
            for ev in plan["evidence"]:
                lines.append(f"  - {ev}")
            if plan.get("notes"):
                lines += [
                    "- **Notes:**",
                    f"  - {plan['notes']}",
                ]
            lines.append("")

    lines += [
        "## Boundary",
        "",
        "> Candidate extraction is not confirmation.  A decoding plan may identify "
        "a field candidate, but source-specific semantics and authoritative identity "
        "remain downstream confirmation/resolution work.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists() or not input_path.is_file():
        raise SystemExit(f"-input must be an existing JSON file: {args.input}")

    try:
        data = json.loads(input_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Cannot read semantic map: {exc}") from exc

    result = build_plan(data)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    json_path = output.with_suffix(".json")
    md_path = output.with_suffix(".md")

    json_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    md_path.write_text(markdown(result), encoding="utf-8")

    print(f"JSON: {json_path}")
    print(f"Markdown: {md_path}")
    print(f"Candidate plans: {len(result['plans'])}")
    for plan in result["plans"]:
        print(f"  {plan['scope']}: {plan['target']} -> {plan['operation']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
