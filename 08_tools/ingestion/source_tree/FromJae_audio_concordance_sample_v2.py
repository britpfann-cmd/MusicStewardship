"""
FromJae audio concordance sample.

Evidence experiment only: directory ancestry, source filename, and embedded
audio metadata are placed side by side. Source files are never modified.
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
from pathlib import Path


def ffprobe_tags(path: Path) -> dict[str, str]:
    """Return embedded format tags without altering the source file."""
    cmd = [
        "ffprobe",
        "-v", "quiet",
        "-show_entries", "format_tags",
        "-of", "json",
        str(path),
    ]

    # Capture bytes explicitly. Windows Python otherwise uses the console
    # code page (often CP1252), which can fail on non-CP1252 tag bytes.
    result = subprocess.run(cmd, capture_output=True, check=False)

    stdout = result.stdout.decode("utf-8", errors="replace")
    stderr = result.stderr.decode("utf-8", errors="replace")

    if result.returncode != 0:
        return {"_ffprobe_error": stderr.strip() or "ffprobe failed"}

    try:
        data = json.loads(stdout or "{}")
    except json.JSONDecodeError:
        return {"_ffprobe_error": "invalid ffprobe JSON"}

    tags = data.get("format", {}).get("tags", {}) or {}
    return {str(k): str(v) for k, v in tags.items()}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create a small FromJae audio evidence-concordance sample."
    )
    parser.add_argument("tree_csv", type=Path)
    parser.add_argument("source_root", type=Path)
    parser.add_argument("output_csv", type=Path)
    parser.add_argument("--count", type=int, default=10)
    args = parser.parse_args()

    if args.count < 1:
        parser.error("--count must be at least 1")

    with args.tree_csv.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    audio = [r for r in rows if r.get("entry_type") == "AUDIO"][:args.count]

    if not audio:
        raise SystemExit("No AUDIO rows found in the Explorer Tree.")

    output_rows = []

    for row in audio:
        relative_path = row.get("relative_path", "")
        source_path = args.source_root / Path(relative_path)
        tags = ffprobe_tags(source_path)

        output_rows.append({
            "source_root": row.get("source_root", ""),
            "relative_path": relative_path,
            "ancestor_path": row.get("ancestor_path", ""),
            "source_filename": row.get("name", ""),
            "source_path": str(source_path),
            "file_exists": source_path.is_file(),
            "embedded_title": tags.get("title", ""),
            "embedded_artist": tags.get("artist", ""),
            "embedded_album": tags.get("album", ""),
            "embedded_album_artist": tags.get("album_artist", ""),
            "embedded_date": tags.get("date", tags.get("year", "")),
            "embedded_genre": tags.get("genre", ""),
            "embedded_track": tags.get("track", ""),
            "embedded_disc": tags.get("disc", ""),
            "embedded_comment": tags.get("comment", ""),
            "embedded_all_tags": json.dumps(
                tags, ensure_ascii=False, sort_keys=True
            ),
        })

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)

    with args.output_csv.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(output_rows[0]))
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Audio records examined: {len(output_rows)}")
    print(f"Output: {args.output_csv}")

    missing = sum(not r["file_exists"] for r in output_rows)
    if missing:
        print(f"WARNING: source files not found: {missing}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
