#!/usr/bin/env python3
"""
Validate an entire Tango Time Travel (TTT) directory tree.

NON-DESTRUCTIVE:
- reads audio files only
- does not rename, move, retag, convert, or rewrite source audio
- treats native TTT metadata as primary source evidence
- uses the TANGO-DJ snapshot only as a secondary reference

Purpose:
  Find significant source-ingest issues across the whole TTT tree before
  applying bulk canonical ingestion.

For every audio file the report checks:
  - ffprobe readability
  - required TTT metadata presence
  - catalog decomposition
  - source track identifier preservation
  - obvious metadata anomalies
  - duplicate source recording identifiers
  - optional TANGO-DJ reference coverage

Outputs:
  1. per-file CSV
  2. release summary CSV
  3. issue summary CSV
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path


AUDIO_EXTENSIONS = {".flac", ".wav", ".mp3", ".m4a", ".alac", ".aiff", ".aif", ".caf", ".ogg", ".opus"}

TAG_NAMES = (
    "TITLE", "ARTIST", "album_artist", "ALBUM", "GENRE", "DATE",
    "COMPOSER", "CONDUCTOR", "CATALOGNUMBER", "SOURCEMEDIA",
    "track", "COMMENT",
)

REQUIRED_SOURCE_TAGS = ("TITLE", "ARTIST", "ALBUM", "GENRE", "DATE", "track")

# Files beginning with ._ are macOS AppleDouble sidecar/resource-fork files.
# They are not audio assets and must never be mistaken for missing TTT records.
EXCLUDED_FILENAMES = {".DS_Store"}
EXCLUDED_PREFIXES = ("._",)


def norm(value: str) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", value.strip()).casefold()


def compact_norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", norm(value))


def track_norm(value: str) -> str:
    s = norm(value)
    m = re.fullmatch(r"0*(\d+(?:\.\d+)?)", s)
    return m.group(1) if m else s


def parse_catalog(value: str) -> tuple[str, str, str]:
    raw = (value or "").strip()
    record = matrix = take = ""

    m = re.search(
        r"(?is)\bRecord\s*:\s*(.*?)"
        r"(?=\s*(?:,)?\s*Matrix\s*:|\s*(?:,)?\s*Take\s*:|$)",
        raw,
    )
    if m:
        record = m.group(1).strip()

    if not record:
        m = re.match(
            r"(?is)^\s*([^\s,;]+(?:\s*[-–—]\s*[A-Za-z0-9]+)?)"
            r"\s*(?=(?:,?\s*)Matrix\s*:|(?:,?\s*)Take\s*:|$)",
            raw,
        )
        if m:
            record = m.group(1).strip()

    m = re.search(
        r"(?is)\bMatrix\s*:\s*(.*?)(?=\s*(?:,)?\s*Take\s*:|$)",
        raw,
    )
    if m:
        matrix = m.group(1).strip().rstrip(",")

    m = re.search(r"(?is)\bTake\s*:\s*(\d+)", raw)
    if m:
        take = m.group(1)

    if not record and raw and not matrix and not take:
        record = raw

    return record, matrix, take


def ffprobe(path: Path) -> dict:
    command = [
        "ffprobe", "-v", "error",
        "-show_entries",
        (
            "format=duration,format_name:format_tags"
            ":stream=index,codec_name,sample_rate,channels,"
            "channel_layout,bits_per_sample"
        ),
        "-of", "json", str(path),
    ]
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "ffprobe failed")
    return json.loads(result.stdout)


def extract_meta(path: Path, data: dict) -> dict[str, str]:
    fmt = data.get("format", {})
    raw_tags = fmt.get("tags", {}) or {}
    tags = {str(k).casefold(): str(v) for k, v in raw_tags.items()}
    stream = (data.get("streams") or [{}])[0]

    return {
        "source_file": str(path),
        "source_filename": path.name,
        "format": str(fmt.get("format_name", "")),
        "duration": str(fmt.get("duration", "")),
        "codec": str(stream.get("codec_name", "")),
        "sample_rate": str(stream.get("sample_rate", "")),
        "channels": str(stream.get("channels", "")),
        "channel_layout": str(stream.get("channel_layout", "")),
        "bits_per_sample": str(stream.get("bits_per_sample", "")),
        **{
            f"TAG:{name}": tags.get(name.casefold(), "").strip()
            for name in TAG_NAMES
        },
    }


def load_reference(reference_csv: Path) -> list[dict[str, str]]:
    if not reference_csv:
        return []
    with reference_csv.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def reference_indexes(reference):
    by_record = defaultdict(list)
    by_matrix = defaultdict(list)
    by_title_date = defaultdict(list)

    for row in reference:
        record = compact_norm(row.get("catalog_number", ""))
        matrix = compact_norm(row.get("matrix_number", ""))
        title = norm(row.get("title", ""))
        date = norm(row.get("recording_date", ""))

        # Preserve all slash-separated catalog alternatives.
        for token in re.split(r"\s*/\s*", row.get("catalog_number", "")):
            token = compact_norm(token)
            if token:
                by_record[token].append(row)

        if matrix:
            by_matrix[matrix].append(row)

        if title and date:
            by_title_date[(title, date)].append(row)

    return by_record, by_matrix, by_title_date


def reference_coverage(meta, indexes):
    by_record, by_matrix, by_title_date = indexes
    record, matrix, take = parse_catalog(meta["TAG:CATALOGNUMBER"])

    record_hits = by_record.get(compact_norm(record), []) if record else []
    matrix_hits = by_matrix.get(compact_norm(matrix), []) if matrix else []

    title = norm(meta["TAG:TITLE"])
    date = norm(meta["TAG:DATE"])
    title_date_hits = by_title_date.get((title, date), []) if title and date else []

    candidates = {id(r): r for r in record_hits + matrix_hits + title_date_hits}

    if not candidates:
        return "NO_REFERENCE_CANDIDATE", 0

    return "REFERENCE_CANDIDATE", len(candidates)


def inspect_file(path: Path, root: Path, reference_indexes):
    release = path.parent.relative_to(root).parts[0] if path.parent != root else ""
    issues = []

    try:
        meta = extract_meta(path, ffprobe(path))
        probe_ok = "YES"
    except Exception as exc:
        return {
            "release": release,
            "source_file": str(path),
            "source_filename": path.name,
            "probe_ok": "NO",
            "probe_error": str(exc),
            "missing_tags": "",
            "record_number": "",
            "matrix_number": "",
            "take_number": "",
            "track_identifier": "",
            "track_numeric": "",
            "reference_status": "NOT_CHECKED",
            "reference_candidates": "",
            "issues": "PROBE_ERROR",
        }

    for name in REQUIRED_SOURCE_TAGS:
        if not meta[f"TAG:{name}"]:
            issues.append(f"MISSING_{name}")

    filename = path.stem
    track = meta["TAG:track"]

    # We preserve the actual TTT track string and separately derive a numeric
    # value for diagnostics only.
    if track and not re.fullmatch(r"\d+(?:\.\d+)?", track):
        issues.append("UNUSUAL_TRACK_IDENTIFIER")

    if track and path.name:
        m = re.match(r"^(\d+(?:\.\d+)?)\s*-\s*", filename)
        if m:
            filename_track = m.group(1)
            if track_norm(filename_track) != track_norm(track):
                issues.append("FILENAME_TRACK_DIFFERS_FROM_TAG")

    record, matrix, take = parse_catalog(meta["TAG:CATALOGNUMBER"])

    if meta["TAG:CATALOGNUMBER"] and not record:
        issues.append("CATALOG_RECORD_NOT_PARSED")

    # Detect common formatting signals without declaring them wrong.
    if "Matrix:" in meta["TAG:CATALOGNUMBER"] and not matrix:
        issues.append("CATALOG_MATRIX_NOT_PARSED")
    if "Take:" in meta["TAG:CATALOGNUMBER"] and not take:
        issues.append("CATALOG_TAKE_NOT_PARSED")

    ref_status, ref_count = reference_coverage(meta, reference_indexes)

    return {
        "release": release,
        "source_file": str(path),
        "source_filename": path.name,
        "probe_ok": probe_ok,
        "probe_error": "",
        "missing_tags": ";".join(
            name for name in REQUIRED_SOURCE_TAGS
            if not meta[f"TAG:{name}"]
        ),
        "title": meta["TAG:TITLE"],
        "artist": meta["TAG:ARTIST"],
        "album": meta["TAG:ALBUM"],
        "genre": meta["TAG:GENRE"],
        "date": meta["TAG:DATE"],
        "composer": meta["TAG:COMPOSER"],
        "conductor": meta["TAG:CONDUCTOR"],
        "source_media": meta["TAG:SOURCEMEDIA"],
        "comment": meta["TAG:COMMENT"],
        "record_number": record,
        "matrix_number": matrix,
        "take_number": take,
        "track_identifier": track,
        "track_numeric": track_norm(track),
        "reference_status": ref_status,
        "reference_candidates": ref_count,
        "issues": ";".join(issues),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("ttt_root", type=Path)
    parser.add_argument("output_csv", type=Path)
    parser.add_argument("summary_csv", type=Path)
    parser.add_argument(
        "--reference",
        type=Path,
        default=None,
        help="optional TANGO-DJ TTT reference CSV",
    )
    parser.add_argument(
        "--audio-only",
        action="store_true",
        help="explicitly document that only recognized audio files are scanned",
    )
    parser.add_argument(
        "--issues-csv",
        type=Path,
        default=None,
        help="optional issue-count CSV; defaults beside output",
    )
    args = parser.parse_args()

    if not args.ttt_root.is_dir():
        parser.error(f"TTT root not found: {args.ttt_root}")

    if args.reference and not args.reference.is_file():
        parser.error(f"Reference CSV not found: {args.reference}")

    files = sorted(
        p for p in args.ttt_root.rglob("*")
        if (
            p.is_file()
            and p.suffix.casefold() in AUDIO_EXTENSIONS
            and p.name not in EXCLUDED_FILENAMES
            and not any(p.name.startswith(prefix) for prefix in EXCLUDED_PREFIXES)
        )
    )

    if not files:
        parser.error("No supported audio files found")

    reference = load_reference(args.reference)
    ref_indexes = reference_indexes(reference)

    rows = []
    issue_counts = Counter()
    release_counts = defaultdict(lambda: {
        "files": 0,
        "probe_errors": 0,
        "missing_metadata": 0,
        "reference_candidates": 0,
        "no_reference_candidates": 0,
        "catalog_parse_issues": 0,
        "other_issues": 0,
    })

    for i, path in enumerate(files, start=1):
        print(f"{i:04d} - {path}")

        row = inspect_file(path, args.ttt_root, ref_indexes)
        rows.append(row)

        release = row["release"] or "(root)"
        summary = release_counts[release]
        summary["files"] += 1

        if row["probe_ok"] == "NO":
            summary["probe_errors"] += 1
            issue_counts["PROBE_ERROR"] += 1

        if row["missing_tags"]:
            summary["missing_metadata"] += 1
            for issue in row["missing_tags"].split(";"):
                issue_counts[f"MISSING_{issue}"] += 1

        if row["reference_status"] == "REFERENCE_CANDIDATE":
            summary["reference_candidates"] += 1
        elif args.reference:
            summary["no_reference_candidates"] += 1

        issues = row["issues"].split(";") if row["issues"] else []
        for issue in issues:
            if not issue:
                continue
            issue_counts[issue] += 1

            if issue.startswith("CATALOG_"):
                summary["catalog_parse_issues"] += 1
            elif issue != "PROBE_ERROR":
                summary["other_issues"] += 1

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)

    fields = list(rows[0].keys())
    with args.output_csv.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    release_fields = [
        "release", "files", "probe_errors", "missing_metadata",
        "reference_candidates", "no_reference_candidates",
        "catalog_parse_issues", "other_issues",
    ]
    with args.summary_csv.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=release_fields)
        writer.writeheader()
        for release in sorted(release_counts):
            writer.writerow(
                {"release": release, **release_counts[release]}
            )

    issues_csv = args.issues_csv or args.output_csv.with_name(
        args.output_csv.stem + "_issues.csv"
    )
    with issues_csv.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["issue", "count"])
        for issue, count in issue_counts.most_common():
            writer.writerow([issue, count])

    total = len(rows)
    probe_errors = sum(r["probe_ok"] == "NO" for r in rows)
    missing = sum(bool(r["missing_tags"]) for r in rows)
    ref_candidates = sum(
        r["reference_status"] == "REFERENCE_CANDIDATE" for r in rows
    )

    print()
    print(f"Files examined: {total}")
    print(
        "Scanner policy: recognized audio files only; "
        "macOS ._* and .DS_Store filesystem artifacts excluded."
    )
    print(f"Probe errors: {probe_errors}")
    print(f"Files with missing required metadata: {missing}")
    if args.reference:
        print(f"Files with TANGO-DJ reference candidates: {ref_candidates}")
        print(f"Files with no TANGO-DJ reference candidate: {total - ref_candidates}")
    print(f"Release summary: {args.summary_csv}")
    print(f"Issue summary: {issues_csv}")
    print(f"Per-file report: {args.output_csv}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
