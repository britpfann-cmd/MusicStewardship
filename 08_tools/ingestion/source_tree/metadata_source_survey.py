#!/usr/bin/env python3
"""
MusicStewardship representative metadata survey.

NON-DESTRUCTIVE:
- reads source files only
- samples audio files from each supplied source root
- uses ffprobe to capture technical metadata and ALL format tags
- preserves directory context and filename evidence
- does not interpret, normalize, retag, move, or modify source files

Output:
  <output>.csv  - one row per sampled audio file, with complete raw tag JSON
  <output>.md   - human-readable source-type report
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

AUDIO_EXTENSIONS = {
    ".flac", ".wav", ".mp3", ".m4a", ".alac",
    ".aiff", ".aif", ".caf", ".ogg", ".opus",
}

TECH_FIELDS = [
    "format_name", "format_long_name", "duration", "size", "bit_rate",
    "codec_name", "codec_long_name", "sample_rate", "channels",
    "channel_layout", "bits_per_sample",
]


def ffprobe(path: Path) -> tuple[dict[str, str], dict[str, str], str]:
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries",
        "format=format_name,format_long_name,duration,size,bit_rate:format_tags"
        ":stream=codec_name,codec_long_name,sample_rate,channels,channel_layout,bits_per_sample",
        "-of", "json",
        str(path),
    ]
    r = subprocess.run(
        cmd, capture_output=True, encoding="utf-8", errors="replace", check=False
    )
    if r.returncode != 0:
        return {}, {}, r.stderr.strip() or "ffprobe failed"

    try:
        data = json.loads(r.stdout or "{}")
    except json.JSONDecodeError:
        return {}, {}, "invalid ffprobe JSON"

    fmt = data.get("format", {}) or {}
    streams = data.get("streams", []) or []
    stream = streams[0] if streams else {}

    tech = {}
    for k in TECH_FIELDS:
        v = fmt.get(k, stream.get(k, ""))
        if v not in ("", None):
            tech[k] = str(v)

    tags = {str(k): str(v) for k, v in (fmt.get("tags") or {}).items()}
    return tech, tags, ""


def relative_ancestors(rel: Path) -> list[str]:
    parts = rel.parts[:-1]
    return list(parts)


def sample_files(root: Path, count: int, seed: int) -> list[Path]:
    files = [
        p for p in root.rglob("*")
        if p.is_file() and p.suffix.casefold() in AUDIO_EXTENSIONS
    ]
    files.sort(key=lambda p: p.relative_to(root).as_posix().casefold())
    if len(files) <= count:
        return files
    rng = random.Random(seed)
    return sorted(rng.sample(files, count), key=lambda p: p.relative_to(root).as_posix().casefold())


def survey_source(label: str, root: Path, count: int, seed: int) -> list[dict[str, str]]:
    if not root.is_dir():
        raise SystemExit(f"Source root does not exist or is not a directory: {root}")

    rows = []
    for path in sample_files(root, count, seed):
        rel = path.relative_to(root)
        tech, tags, error = ffprobe(path)

        row = {
            "source": label,
            "source_root": str(root),
            "relative_path": rel.as_posix(),
            "ancestor_path": "/".join(relative_ancestors(rel)),
            "filename": path.name,
            "extension": path.suffix.casefold(),
            "metadata_status": "ERROR" if error else ("PRESENT" if tags else "EMPTY"),
            "metadata_error": error,
            "technical_metadata": json.dumps(tech, ensure_ascii=False, sort_keys=True),
            "embedded_metadata": json.dumps(tags, ensure_ascii=False, sort_keys=True),
        }
        rows.append(row)
    return rows


def build_markdown(rows: list[dict[str, str]], output: Path) -> None:
    by_source = defaultdict(list)
    for row in rows:
        by_source[row["source"]].append(row)

    lines = [
        "# MusicStewardship Representative Metadata Survey",
        "",
        "This is an observational survey. Directory context, filenames, technical",
        "metadata, and embedded metadata are retained as separate evidence channels.",
        "",
    ]

    for source in sorted(by_source):
        srows = by_source[source]
        lines += [f"## {source}", ""]
        lines.append(f"Sampled audio files: **{len(srows)}**")
        lines.append("")

        # Tag presence
        tag_counts = Counter()
        tag_values = defaultdict(Counter)
        ext_counts = Counter()
        format_counts = Counter()

        for row in srows:
            ext_counts[row["extension"]] += 1
            tech = json.loads(row["technical_metadata"] or "{}")
            tags = json.loads(row["embedded_metadata"] or "{}")
            if tech.get("format_name"):
                format_counts[tech["format_name"]] += 1
            for k, v in tags.items():
                tag_counts[k] += 1
                tag_values[k][v] += 1

        lines.append("### Directory / filename context")
        for row in srows:
            lines.append(f"- `{row['relative_path']}`")
        lines.append("")

        lines.append("### File extensions")
        lines.append(", ".join(f"`{k}` ({v})" for k, v in sorted(ext_counts.items())))
        lines.append("")

        lines.append("### Embedded metadata fields")
        if tag_counts:
            lines.append("| Field | Files present | Distinct values |")
            lines.append("|---|---:|---:|")
            for k, n in sorted(tag_counts.items(), key=lambda x: (-x[1], x[0].casefold())):
                lines.append(f"| `{k}` | {n} | {len(tag_values[k])} |")
        else:
            lines.append("No embedded format tags were returned by ffprobe.")
        lines.append("")

        lines.append("### Technical metadata observed")
        if format_counts:
            lines.append(
                "Format/container values: "
                + ", ".join(f"`{k}` ({v})" for k, v in sorted(format_counts.items()))
            )
        lines.append("")

        lines.append("### Representative evidence")
        for row in srows:
            tags = json.loads(row["embedded_metadata"] or "{}")
            tech = json.loads(row["technical_metadata"] or "{}")
            lines.append(f"#### `{row['filename']}`")
            lines.append(f"- Directory context: `{row['ancestor_path'] or '.'}`")
            lines.append(f"- Extension: `{row['extension']}`")
            lines.append(f"- Technical: `{json.dumps(tech, ensure_ascii=False, sort_keys=True)}`")
            lines.append(f"- Embedded tags: `{json.dumps(tags, ensure_ascii=False, sort_keys=True)}`")
            if row["metadata_error"]:
                lines.append(f"- Probe error: `{row['metadata_error']}`")
            lines.append("")

    output.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", action="append", nargs=2, metavar=("LABEL", "ROOT"),
                    required=True,
                    help="Repeat for each source: --source TangoTunes M:\\TangoTunes")
    ap.add_argument("--count", type=int, default=8)
    ap.add_argument("--seed", type=int, default=20260918)
    ap.add_argument("-o", "--output", type=Path, required=True)
    args = ap.parse_args()

    if args.count < 1:
        ap.error("--count must be at least 1")

    rows = []
    for label, root_text in args.source:
        rows.extend(survey_source(label, Path(root_text), args.count, args.seed))

    args.output.parent.mkdir(parents=True, exist_ok=True)

    csv_path = args.output.with_suffix(".csv")
    md_path = args.output.with_suffix(".md")

    fields = [
        "source", "source_root", "relative_path", "ancestor_path",
        "filename", "extension", "metadata_status", "metadata_error",
        "technical_metadata", "embedded_metadata",
    ]
    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    build_markdown(rows, md_path)

    print(f"CSV: {csv_path}")
    print(f"Markdown: {md_path}")
    print(f"Audio files sampled: {len(rows)}")
    for label, _ in args.source:
        n = sum(1 for r in rows if r["source"] == label)
        print(f"  {label}: {n}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
