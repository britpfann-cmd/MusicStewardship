#!/usr/bin/env python3
"""Extract candidate fields from a source decoding plan.

This layer performs extraction only.  It does not confirm, resolve, normalize
to canonical values, or discard source evidence.

Pipeline:
    Explorer Tree -> Semantic Map -> Decoding Plan -> Candidate Extraction
                                             -> Confirmation / Resolution

Input:
    source semantic-map JSON
    source decoding-plan JSON

Output:
    <output>.json
    <output>.md

Each candidate retains:
    - source scope/path
    - original source filename
    - extraction operation
    - observed value
    - evidence
    - status = candidate

The implementation is intentionally generic.  It implements the operations
currently emitted by source_decoding_plan.py and should grow only when a
demonstrated decoding requirement cannot be expressed by the existing
operation vocabulary and parameters.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "musicstewardship.source_tree_candidate_extraction.v1"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Extract candidate fields from a semantic map and decoding plan."
    )
    p.add_argument("-map", required=True, help="Semantic-map JSON")
    p.add_argument("-plan", required=True, help="Decoding-plan JSON")
    p.add_argument("-o", "--output", required=True, help="Output path without .json/.md")
    return p.parse_args()


def load_json(path_text: str, label: str) -> dict[str, Any]:
    path = Path(path_text).expanduser().resolve()
    if not path.exists() or not path.is_file():
        raise SystemExit(f"{label} must be an existing JSON file: {path_text}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Cannot read {label}: {exc}") from exc


def make_candidate(
    *,
    scope: str,
    source_relative_path: str,
    source_name: str,
    target: str,
    operation: str,
    value: Any,
    evidence: str,
) -> dict[str, Any]:
    return {
        "status": "candidate",
        "scope": scope,
        "source_relative_path": source_relative_path,
        "source_name": source_name,
        "target": target,
        "operation": operation,
        "value": value,
        "evidence": evidence,
    }


def filename_candidates(
    inspection: dict[str, Any],
    applicable: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []

    ops = {p["operation"]: p for p in applicable}
    if not ops:
        return candidates

    for child in inspection.get("children", []):
        if child.get("entry_type") != "FILE" or "filename" not in child:
            continue

        name = child["name"]
        rel = child["relative_path"]
        structure = child["filename"].get("structure", {})
        stem = child["filename"].get("stem", "")

        if "extract_numeric_component" in ops:
            for value in structure.get("numeric_components", []):
                candidates.append(
                    make_candidate(
                        scope=inspection["node"]["relative_path"],
                        source_relative_path=rel,
                        source_name=name,
                        target="filename.numeric_component",
                        operation="extract_numeric_component",
                        value=value,
                        evidence=f"Numeric component observed in original filename `{name}`.",
                    )
                )

        if "identify_sequence_number_candidate" in ops:
            match = re.match(r"^\s*(\d+)(?:\s*[-.]|\s+)", stem)
            if match:
                candidates.append(
                    make_candidate(
                        scope=inspection["node"]["relative_path"],
                        source_relative_path=rel,
                        source_name=name,
                        target="filename.sequence_number_candidate",
                        operation="identify_sequence_number_candidate",
                        value=int(match.group(1)),
                        evidence=(
                            f"Leading numeric component `{match.group(1)}` in `{name}` "
                            "is supported by the inspected local filename population as sequence evidence; "
                            "its semantic meaning remains unconfirmed."
                        ),
                    )
                )

        if "extract_text_before_first_numeric_component" in ops:
            match = re.search(r"\d+(?:-\d+)?", stem)
            if match:
                value = stem[:match.start()].strip()
                if value:
                    candidates.append(
                        make_candidate(
                            scope=inspection["node"]["relative_path"],
                            source_relative_path=rel,
                            source_name=name,
                            target="filename.leading_text",
                            operation="extract_text_before_first_numeric_component",
                            value=value,
                            evidence=f"Text preceding the first numeric component in original filename `{name}`.",
                        )
                    )

        if "extract_terminal_suffix" in ops:
            value = structure.get("terminal_suffix")
            if value:
                candidates.append(
                    make_candidate(
                        scope=inspection["node"]["relative_path"],
                        source_relative_path=rel,
                        source_name=name,
                        target="filename.terminal_suffix",
                        operation="extract_terminal_suffix",
                        value=value,
                        evidence=f"Terminal suffix observed in original filename `{name}`.",
                    )
                )

        # `extract_terminal_suffix` already preserves the observed suffix value
        # as source evidence.  Do not emit a second candidate for the legacy
        # preservation operation when extraction is also present.  Retain the
        # legacy operation only when a plan explicitly requests preservation
        # without the extraction operation.
        if (
            "preserve_as_categorical_source_evidence" in ops
            and "extract_terminal_suffix" not in ops
        ):
            value = structure.get("terminal_suffix")
            if value:
                candidates.append(
                    make_candidate(
                        scope=inspection["node"]["relative_path"],
                        source_relative_path=rel,
                        source_name=name,
                        target="filename.terminal_suffix",
                        operation="preserve_as_categorical_source_evidence",
                        value=value,
                        evidence=f"Terminal suffix `{value}` retained exactly as observed in `{name}`.",
                    )
                )

    return candidates


def directory_candidates(
    inspection: dict[str, Any],
    applicable: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    ops = {p["operation"]: p for p in applicable}

    if "preserve_directory_component" not in ops:
        return candidates

    for child in inspection.get("children", []):
        if child.get("entry_type") != "DIRECTORY":
            continue
        candidates.append(
            make_candidate(
                scope=inspection["node"]["relative_path"],
                source_relative_path=child["relative_path"],
                source_name=child["name"],
                target="parent_directory.name",
                operation="preserve_directory_component",
                value=child["name"],
                evidence=f"Immediate directory name observed at `{inspection['node']['relative_path']}`.",
            )
        )

    return candidates


def file_class_candidates(
    inspection: dict[str, Any],
    applicable: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    ops = {p["operation"]: p for p in applicable}

    audio_exts = {".aif", ".aiff", ".flac", ".m4a", ".mp3", ".wav"}

    for child in inspection.get("children", []):
        if child.get("entry_type") != "FILE" or "filename" not in child:
            continue

        ext = child["filename"].get("extension", "")
        if "classify_audio_by_extension" in ops and ext in audio_exts:
            candidates.append(
                make_candidate(
                    scope=inspection["node"]["relative_path"],
                    source_relative_path=child["relative_path"],
                    source_name=child["name"],
                    target="file.entry_type",
                    operation="classify_audio_by_extension",
                    value="AUDIO",
                    evidence=f"Original filename uses recognized audio extension `{ext}`.",
                )
            )

        if "preserve_non_audio_source_artifacts" in ops and ext not in audio_exts:
            candidates.append(
                make_candidate(
                    scope=inspection["node"]["relative_path"],
                    source_relative_path=child["relative_path"],
                    source_name=child["name"],
                    target="file.entry_type",
                    operation="preserve_non_audio_source_artifacts",
                    value="NON_AUDIO_SOURCE_ARTIFACT",
                    evidence=f"Original filename uses non-audio extension `{ext or '[none]'}`.",
                )
            )

    return candidates


def extract(data: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []

    plans = plan.get("plans", [])
    inspections = data.get("inspections", [])

    for inspection in inspections:
        scope = inspection.get("node", {}).get("relative_path", ".")
        applicable = [p for p in plans if p.get("scope") == scope]

        candidates.extend(directory_candidates(inspection, applicable))
        candidates.extend(file_class_candidates(inspection, applicable))
        candidates.extend(filename_candidates(inspection, applicable))

    return {
        "schema": SCHEMA,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source_map_schema": data.get("schema"),
        "source_plan_schema": plan.get("schema"),
        "source_root": data.get("source_root"),
        "extraction_status": "candidate_only",
        "principle": "Extract facts; preserve evidence. Candidate extraction does not establish canonical meaning.",
        "candidates": candidates,
    }


def markdown(data: dict[str, Any]) -> str:
    lines = [
        "# Source Candidate Extraction",
        "",
        "> Candidate values extracted from observed source structure according to "
        "the decoding plan. Values remain unconfirmed source evidence.",
        "",
        "## Source",
        "",
        f"- **Root:** `{data.get('source_root', {}).get('path', '')}`",
        f"- **Map schema:** `{data.get('source_map_schema')}`",
        f"- **Plan schema:** `{data.get('source_plan_schema')}`",
        f"- **Status:** `{data.get('extraction_status')}`",
        "",
        "## Candidates",
        "",
    ]

    candidates = data.get("candidates", [])
    if not candidates:
        lines.append("No candidates were extracted.")
    else:
        for i, c in enumerate(candidates, 1):
            lines += [
                f"### {i}. `{c['target']}`",
                "",
                f"- **Value:** `{c['value']}`",
                f"- **Operation:** `{c['operation']}`",
                f"- **Scope:** `{c['scope']}`",
                f"- **Source path:** `{c['source_relative_path']}`",
                f"- **Source name:** `{c['source_name']}`",
                f"- **Status:** `{c['status']}`",
                f"- **Evidence:** {c['evidence']}",
                "",
            ]

    lines += [
        "## Boundary",
        "",
        "> These are candidates, not resolved library facts. No canonical field "
        "assignment, normalization, authority decision, or conflict resolution occurs here.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    source_map = load_json(args.map, "Semantic map")
    plan = load_json(args.plan, "Decoding plan")

    result = extract(source_map, plan)

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
    print(f"Candidates: {len(result['candidates'])}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
