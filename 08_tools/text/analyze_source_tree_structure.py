#!/usr/bin/env python3
"""
analyze_source_tree_structure_v2_4.py

V2.4 adds recurring hierarchy signatures: complete structural paths from
source-relative root/category levels to audio-bearing leaves.

Design principle:
    observations -> structural signatures -> semantic candidates
    -> corroboration -> canonical facts

Directory names and tokens remain evidence, not canonical facts.
"""

from __future__ import annotations

import argparse
import csv
import re
from collections import Counter, defaultdict
from pathlib import Path


AUDIO_EXTENSIONS = {
    ".aif", ".aiff", ".flac", ".mp3", ".wav", ".m4a", ".mp4", ".ogg",
    ".opus", ".wma", ".alac"
}


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows):
    rows = list(rows)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def integer(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def classify_name(name: str) -> str:
    s = (name or "").strip()
    if not s or s == ".":
        return "ROOT"
    if re.fullmatch(r"\d+", s):
        return "NUMBERED"
    if re.search(r"\b(19|20)\d{2}\b", s):
        return "PERIOD_LIKE"
    if re.fullmatch(r"[A-Za-z]{0,4}[-_ ]?\d{3,}", s):
        return "IDENTIFIER_LIKE"
    if re.fullmatch(r"[A-Za-z0-9]+[-_]\d{3,}([-.]\w+)?", s):
        return "IDENTIFIER_LIKE"
    if re.fullmatch(r"[\dA-Fa-f]{6,}", s):
        return "IDENTIFIER_LIKE"
    return "TEXT_NAME"


def semantic_tokens(name: str):
    s = (name or "").casefold()
    tokens = []
    if re.search(r"\bcortinas?\b", s):
        tokens.append("CORTINA")
    if re.search(r"\breleases?\b", s):
        tokens.append("RELEASE")
    if re.search(r"\bcompilations?\b", s):
        tokens.append("COMPILATION")
    if "digital booklet" in s:
        tokens.append("DIGITAL_BOOKLET")
    if re.search(r"\btangos?\b", s):
        tokens.append("GENRE_TANGO")
    if re.search(r"\bmilongas?\b", s):
        tokens.append("GENRE_MILONGA")
    if re.search(r"\bvals(?:es)?\b", s):
        tokens.append("GENRE_VALS")
    if re.search(r"\b(instrumental|instrumentales)\b", s):
        tokens.append("INSTRUMENTAL")
    if re.search(r"\b(vocal|vocals|cantado|cantados|cantores)\b", s):
        tokens.append("VOCAL")
    if re.search(r"\b(19|20)\d{2}\b", s):
        tokens.append("PERIOD")
    return tokens


def filename_pattern(name: str) -> str:
    s = name or ""
    s = re.sub(r"\d+", "#", s)
    s = re.sub(r"[A-Fa-f0-9]{8,}", "HEX", s)
    return s


def path_parts(path: str):
    p = (path or "").replace("\\", "/").strip("/")
    if not p or p == ".":
        return []
    return [x for x in p.split("/") if x and x != "."]


def hierarchy_signature_for_dir(directory_path: str, dirs_by_path):
    parts = path_parts(directory_path)
    signature = []
    for i, part in enumerate(parts):
        parent_path = "/".join(parts[:i]) if i else "."
        d = dirs_by_path.get(parent_path)
        shape = classify_name(part)
        state = "CONTAINER"
        if d is not None:
            state = d.get("_state", "CONTAINER")
        signature.append(f"{shape}:{state}")
    return " / ".join(signature)


def build_directory_states(dirs, files):
    audio_by_dir = Counter()
    for f in files:
        if f.get("is_audio") == "YES":
            audio_by_dir[(f["source_id"], f["directory_path"])] += 1

    children = Counter()
    for d in dirs:
        children[(d["source_id"], d["parent_path"])] += 1

    states = {}
    for d in dirs:
        key = (d["source_id"], d["directory_path"])
        audio = audio_by_dir[key]
        child_count = integer(d.get("directory_count"))
        if child_count == 0 and audio > 0:
            state = "AUDIO_LEAF"
        elif child_count > 0 and audio > 0:
            state = "AUDIO_AND_CHILDREN"
        else:
            state = "CONTAINER"
        states[key] = state
    return states


def build_hierarchy_signatures(dirs, files):
    states = build_directory_states(dirs, files)

    # Source-relative directory index.
    dirs_by_source_path = {}
    for d in dirs:
        key = (d["source_id"], d["directory_path"])
        d2 = dict(d)
        d2["_state"] = states.get(key, "CONTAINER")
        dirs_by_source_path[key] = d2

    rows = []
    grouped = defaultdict(list)

    for d in dirs:
        if states.get((d["source_id"], d["directory_path"])) != "AUDIO_LEAF":
            continue

        sid = d["source_id"]
        path = d["directory_path"]
        parts = path_parts(path)
        sig_parts = []

        for i, part in enumerate(parts):
            parent_path = "/".join(parts[:i]) if i else "."
            pd = dirs_by_source_path.get((sid, parent_path))
            shape = classify_name(part)
            state = pd["_state"] if pd else "CONTAINER"
            sig_parts.append(f"{shape}:{state}")

        signature = " / ".join(sig_parts)
        grouped[(sid, signature)].append(path)

    for (sid, signature), examples in sorted(grouped.items()):
        if len(examples) < 2:
            continue
        rows.append({
            "source_id": sid,
            "hierarchy_signature": signature,
            "occurrences": len(examples),
            "max_depth": max(len(path_parts(x)) for x in examples),
            "example_path_1": examples[0],
            "example_path_2": examples[1] if len(examples) > 1 else "",
            "example_path_3": examples[2] if len(examples) > 2 else "",
            "interpretation": (
                "recurring structural signature; semantic role requires "
                "file-level or external corroboration"
            ),
        })
    rows.sort(key=lambda r: (-int(r["occurrences"]), r["source_id"], r["hierarchy_signature"]))
    return rows


def build_source_grammar_summary(signatures):
    by_source = defaultdict(list)
    for row in signatures:
        by_source[row["source_id"]].append(row)

    rows = []
    for sid, items in sorted(by_source.items()):
        total = sum(int(x["occurrences"]) for x in items)
        for rank, x in enumerate(items, 1):
            rows.append({
                "source_id": sid,
                "rank": rank,
                "hierarchy_signature": x["hierarchy_signature"],
                "occurrences": x["occurrences"],
                "share_of_recurring_signatures": (
                    f"{int(x['occurrences']) / total:.4f}" if total else "0"
                ),
                "example_path": x["example_path_1"],
            })
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input_dir", type=Path)
    ap.add_argument("--output-dir", required=True, type=Path)
    args = ap.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    dirs = read_csv(args.input_dir / "source_tree_directories.csv")
    files = read_csv(args.input_dir / "source_tree_files.csv")

    signatures = build_hierarchy_signatures(dirs, files)
    grammar_summary = build_source_grammar_summary(signatures)

    write_csv(args.output_dir / "source_tree_hierarchy_signatures.csv", signatures)
    write_csv(
        args.output_dir / "source_tree_hierarchy_signature_summary.csv",
        grammar_summary,
    )

    # Carry forward the structural inputs so the V2.4 output directory is
    # self-describing and independently reviewable.
    write_csv(args.output_dir / "source_tree_directories.csv", dirs)
    write_csv(args.output_dir / "source_tree_files.csv", files)

    sources = sorted({d["source_id"] for d in dirs})
    audio_files = sum(f.get("is_audio") == "YES" for f in files)

    md = [
        "# Source Tree Analysis — V2.4",
        "",
        "V2.4 adds recurring complete hierarchy signatures from source-relative",
        "directory paths to audio-bearing leaves.",
        "",
        "These signatures describe repeated filesystem structure. They are not",
        "canonical music facts and do not by themselves establish artist, album,",
        "genre, period, release, or performance identity.",
        "",
        f"Sources analyzed: {len(sources)}",
        f"Directories analyzed: {len(dirs)}",
        f"Files analyzed: {len(files)}",
        f"Audio files: {audio_files}",
        f"Recurring hierarchy signatures: {len(signatures)}",
        "",
        "## Interpretation discipline",
        "",
        "- Preserve the original source path.",
        "- Preserve complete hierarchy signatures as source evidence.",
        "- Treat directory names and tokens as observations.",
        "- Treat structural interpretations as candidates until corroborated.",
        "- Use file metadata, filename evidence, reference catalogs, and external",
        "  sources to increase certitude only as far as necessary.",
        "- Do not reject a music asset because its directory semantics are unclear.",
        "",
        "## Source-specific recurring signatures",
        "",
    ]

    for sid in sources:
        items = [x for x in signatures if x["source_id"] == sid][:10]
        md += [f"### {sid}", ""]
        if not items:
            md.append("No recurring complete signature with two or more instances.")
            md.append("")
            continue
        md += [
            "| Occurrences | Signature | Example |",
            "|---:|---|---|",
        ]
        for x in items:
            md.append(
                f"| {x['occurrences']} | {x['hierarchy_signature']} | "
                f"{x['example_path_1']} |"
            )
        md.append("")

    (args.output_dir / "source_tree_analysis_summary.md").write_text(
        "\n".join(md) + "\n", encoding="utf-8"
    )

    print("Source-tree hierarchy signature analysis complete.")
    print(f"Sources:               {len(sources)}")
    print(f"Directories analyzed:  {len(dirs)}")
    print(f"Files analyzed:        {len(files)}")
    print(f"Audio files:           {audio_files}")
    print(f"Recurring signatures:  {len(signatures)}")
    print(f"Output:                {args.output_dir}")


if __name__ == "__main__":
    main()
