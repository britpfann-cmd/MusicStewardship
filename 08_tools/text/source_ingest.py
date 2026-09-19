#!/usr/bin/env python3
"""
Generic, rule-driven source ingestion engine.

Reads a source tree baseline plus a declarative source grammar and produces
file-level evidence. It preserves provenance and never rejects an audio file.

V2:
- Supports source-specific filename patterns.
- Supports source-specific embedded metadata fields.
- Reads embedded audio metadata with ffprobe.
- Embedded metadata is evidence, not canonical identity.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
from pathlib import Path


AUDIO_EXT = {
    ".aif", ".aiff", ".flac", ".mp3", ".wav", ".m4a",
    ".mp4", ".ogg", ".opus", ".wma", ".alac"
}


def read_csv(p):
    with p.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(p, rows):
    rows = list(rows)
    fields = list(rows[0]) if rows else []
    p.parent.mkdir(parents=True, exist_ok=True)

    with p.open("w", encoding="utf-8-sig", newline="") as f:
        if fields:
            w = csv.DictWriter(
                f,
                fieldnames=fields,
                extrasaction="ignore"
            )
            w.writeheader()
            w.writerows(rows)


def load_rules(p):
    """
    Read the simple YAML-like grammar format used by source profiles.

    Supported list sections:

        sources:
          - TangoTimeTravel

        filename_patterns:
          - 'regex'

        metadata_fields:
          - title
          - artist
    """
    rules = {}
    section = None

    for raw in p.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()

        if not line or line.startswith("#"):
            continue

        if line.endswith(":") and not line.startswith("-"):
            section = line[:-1]
            rules[section] = []

        elif line.startswith("- ") and section:
            value = line[2:].strip().strip("'\"")
            rules[section].append(value)

    return rules


def parse_simple_filename(name, patterns):
    stem = re.sub(r"\.[^.]+$", "", name or "")

    for index, pat in enumerate(patterns, start=1):
        try:
            m = re.match(pat, stem, re.I)
        except re.error:
            continue

        if m:
            return "MATCHED", index, m.groupdict()

    return "UNMATCHED", "", {}


def read_embedded_metadata(path, fields):
    """
    Read requested embedded tags using ffprobe.

    Missing metadata or inability to read metadata does not reject
    the asset.
    """
    if not fields:
        return {}

    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "quiet",
                "-show_entries", "format_tags",
                "-of", "json",
                str(path),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return {}

    if result.returncode != 0:
        return {}

    try:
        data = json.loads(result.stdout or "{}")
    except json.JSONDecodeError:
        return {}

    tags = data.get("format", {}).get("tags", {}) or {}

    normalized = {
        str(key).strip().lower(): str(value).strip()
        for key, value in tags.items()
    }

    aliases = {
        "title": ["title"],
        "artist": ["artist"],
        "album": ["album"],
        "date": ["date", "year"],
        "composer": ["composer"],
        "conductor": ["conductor"],
        "record": ["record"],
        "matrix": ["matrix"],
        "take": ["take"],
        "genre": ["genre"],
        "source_media": ["sourcemedia", "source_media"],
        "track": ["track", "tracknumber"],
        "album_artist": ["album_artist", "albumartist"],
        "catalognumber": ["catalognumber"],
        "comment": ["comment"],
        "encoded_by": ["encoded-by", "encoded_by", "encodedby"],
    }

    result_tags = {}

    for field in fields:
        candidates = aliases.get(field, [field])

        for candidate in candidates:
            value = normalized.get(candidate.lower())
            if value:
                result_tags[field] = value
                break

    return result_tags


def metadata_values_string(metadata):
    return ";".join(
        f"{key}={value}"
        for key, value in metadata.items()
        if value not in (None, "")
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tree_dir", type=Path)
    ap.add_argument("rules", type=Path)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument(
        "--evidence-output",
        required=False,
        type=Path,
        help="Optional JSON output for structured filename-decoder evidence.",
    )
    a = ap.parse_args()

    dirs = read_csv(
        a.tree_dir / "source_tree_directories.csv"
    )

    fs = read_csv(
        a.tree_dir / "source_tree_files.csv"
    )

    rules = load_rules(a.rules)

    ctx = {
        (d["source_id"], d["directory_path"]): d
        for d in dirs
    }

    selected = set(rules.get("sources", []))
    filename_patterns = rules.get("filename_patterns", [])
    metadata_fields = rules.get("metadata_fields", [])

    rows = []
    filename_evidence = []

    for f in fs:
        if f.get("is_audio") != "YES":
            continue

        sid = f["source_id"]

        if selected and sid not in selected:
            continue

        d = ctx.get(
            (sid, f["directory_path"]),
            {}
        )

        status, rule_id, filename_data = parse_simple_filename(
            f.get("filename", ""),
            filename_patterns,
        )

        relative_path = f.get(
            "relative_path",
            f.get("path", "")
        )

        source_root = f.get("source_root", "")

        actual_path = (
            Path(source_root) / relative_path
            if source_root
            else None
        )

        metadata = {}

        if actual_path and metadata_fields:
            metadata = read_embedded_metadata(
                actual_path,
                metadata_fields,
            )

        evidence = ["directory_context"]

        if status == "MATCHED":
            evidence.append("filename_rule")

        if metadata:
            evidence.append("embedded_metadata")

        if status == "MATCHED":
            for field_name, field_value in filename_data.items():
                filename_evidence.append({
                    "source_object": {
                        "source_id": sid,
                        "source_root": source_root,
                        "relative_path": relative_path,
                        "filename": f.get("filename", ""),
                    },
                    "evidence": {
                        "evidence_channel": "source_specific",
                        "evidence_type": "filename_rule",
                        "source_locator": f"filename.rule.{rule_id}.{field_name}",
                        "raw_value": field_value,
                        "normalized_value": field_value,
                        "extraction_method": "filename_regex",
                        "decoder": a.rules.stem,
                        "rule_id": rule_id,
                        "rule_field": field_name,
                        "status": "observed",
                    },
                })

        row = {
            "source_id": sid,
            "relative_path": relative_path,
            "filename": f.get("filename", ""),
            "directory_path": f.get("directory_path", ""),
            "directory_name": f.get(
                "directory_name",
                d.get("directory_name", "")
            ),
            "directory_name_shape": d.get(
                "name_shape",
                ""
            ),
            "directory_semantic_tokens": d.get(
                "semantic_tokens",
                ""
            ),
            "hierarchy_signature": d.get(
                "hierarchy_signature",
                ""
            ),
            "filename_rule_status": status,
            "filename_rule_id": rule_id,
            "filename_rule_values": ";".join(
                f"{k}={v}"
                for k, v in filename_data.items()
            ),
            "embedded_metadata_status": (
                "PRESENT" if metadata else "ABSENT"
            ),
            "embedded_metadata_values": metadata_values_string(
                metadata
            ),
            "source_rule_set": a.rules.stem,
            "evidence_sources": ";".join(evidence),
            "canonical_identity_status": "UNRESOLVED",
            "asset_acceptance": "RETAIN",
        }

        for field in metadata_fields:
            row[f"metadata_{field}"] = metadata.get(
                field,
                ""
            )

        rows.append(row)

    write_csv(a.output, rows)

    if a.evidence_output:
        evidence_payload = {
            "schema": "musicstewardship.source_specific_evidence.v1",
            "decoder": a.rules.stem,
            "evidence_channel": "source_specific",
            "evidence_type": "filename_rule",
            "source_objects": filename_evidence,
            "summary": {
                "source_objects": len({
                    (
                        x["source_object"]["source_id"],
                        x["source_object"]["source_root"],
                        x["source_object"]["relative_path"],
                    )
                    for x in filename_evidence
                }),
                "observations": len(filename_evidence),
            },
        }

        a.evidence_output.parent.mkdir(parents=True, exist_ok=True)
        a.evidence_output.write_text(
            json.dumps(
                evidence_payload,
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    matched = sum(
        x["filename_rule_status"] == "MATCHED"
        for x in rows
    )

    metadata_present = sum(
        x["embedded_metadata_status"] == "PRESENT"
        for x in rows
    )

    print(f"Audio records ingested: {len(rows)}")
    print(f"Sources in rule set: {len(selected)}")
    print(f"Filename rule matches: {matched}")
    print(f"Embedded metadata present: {metadata_present}")
    print("Assets rejected: 0")
    print(f"Output: {a.output}")


if __name__ == "__main__":
    main()
