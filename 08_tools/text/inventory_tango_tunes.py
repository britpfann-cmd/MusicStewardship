#!/usr/bin/env python3
"""
Inventory Tango Tunes source files for MusicStewardship ingest.

Non-destructive:
- reads files only
- captures relative path, filename, extension, size
- probes recognized audio with ffprobe
- captures common embedded tags
- preserves raw tag values
- emits a CSV suitable for source-specific mapping work

This is an INVENTORY stage, not canonicalization or correction.
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
from pathlib import Path

AUDIO_EXTENSIONS = {
    ".flac", ".wav", ".mp3", ".m4a", ".alac",
    ".aiff", ".aif", ".caf", ".ogg", ".opus",
}
EXCLUDED_NAMES = {".DS_Store"}
EXCLUDED_PREFIXES = ("._",)

FIELDS = [
    "source",
    "source_root",
    "relative_path",
    "filename",
    "extension",
    "size_bytes",
    "audio_probe_status",
    "duration",
    "format_name",
    "codec_name",
    "sample_rate",
    "channels",
    "bit_rate",
    "TITLE",
    "ARTIST",
    "ALBUM",
    "ALBUM_ARTIST",
    "GENRE",
    "DATE",
    "TRACK",
    "COMMENT",
    "COMPOSER",
    "PUBLISHER",
    "CONDUCTOR",
    "CATALOGNUMBER",
    "SOURCEMEDIA",
]

def probe(path: Path) -> dict[str, str]:
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries",
        "format=duration,format_name,bit_rate:format_tags"
        ":stream=codec_name,sample_rate,channels",
        "-of", "json", str(path),
    ]
    r = subprocess.run(
        cmd, capture_output=True, text=True,
        encoding="utf-8", errors="replace"
    )
    if r.returncode != 0:
        return {"audio_probe_status": "ERROR"}

    try:
        data = json.loads(r.stdout)
    except json.JSONDecodeError:
        return {"audio_probe_status": "ERROR"}

    fmt = data.get("format", {})
    streams = data.get("streams", [])
    tags = fmt.get("tags") or {}
    tags = {str(k).casefold(): str(v) for k, v in tags.items()}

    stream = streams[0] if streams else {}

    def tag(*names):
        for name in names:
            if name.casefold() in tags:
                return tags[name.casefold()]
        return ""

    return {
        "audio_probe_status": "OK",
        "duration": fmt.get("duration", ""),
        "format_name": fmt.get("format_name", ""),
        "codec_name": stream.get("codec_name", ""),
        "sample_rate": stream.get("sample_rate", ""),
        "channels": stream.get("channels", ""),
        "bit_rate": fmt.get("bit_rate", ""),
        "TITLE": tag("TITLE", "title"),
        "ARTIST": tag("ARTIST", "artist"),
        "ALBUM": tag("ALBUM", "album"),
        "ALBUM_ARTIST": tag("ALBUM_ARTIST", "album_artist"),
        "GENRE": tag("GENRE", "genre"),
        "DATE": tag("DATE", "date"),
        "TRACK": tag("TRACK", "track"),
        "COMMENT": tag("COMMENT", "comment"),
        "COMPOSER": tag("COMPOSER", "composer"),
        "PUBLISHER": tag("PUBLISHER", "publisher"),
        "CONDUCTOR": tag("CONDUCTOR", "conductor"),
        "CATALOGNUMBER": tag("CATALOGNUMBER", "catalognumber"),
        "SOURCEMEDIA": tag("SOURCEMEDIA", "sourcemedia"),
    }

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("source_root", type=Path)
    p.add_argument("output_csv", type=Path)
    p.add_argument("--source-name", default="TangoTunes")
    p.add_argument("--limit", type=int, default=0)
    args = p.parse_args()

    root = args.source_root
    if not root.is_dir():
        p.error(f"Source directory not found: {root}")

    files = sorted(
        x for x in root.rglob("*")
        if x.is_file()
        and x.suffix.casefold() in AUDIO_EXTENSIONS
        and x.name not in EXCLUDED_NAMES
        and not x.name.startswith(EXCLUDED_PREFIXES)
    )

    if args.limit:
        files = files[:args.limit]

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)

    with args.output_csv.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()

        errors = 0
        for i, path in enumerate(files, 1):
            if i <= 60:
                print(f"{i:04d} - {path}")
            elif i == 61:
                print("[remaining files processed silently; full results in CSV]")

            row = {
                field: ""
                for field in FIELDS
            }
            row.update({
                "source": args.source_name,
                "source_root": str(root),
                "relative_path": str(path.relative_to(root)),
                "filename": path.name,
                "extension": path.suffix.casefold(),
                "size_bytes": path.stat().st_size,
            })
            row.update(probe(path))
            if row["audio_probe_status"] == "ERROR":
                errors += 1
            writer.writerow(row)

    print()
    print(f"Audio files examined: {len(files)}")
    print(f"Probe errors: {errors}")
    print(f"Inventory CSV: {args.output_csv}")
    print("Source was not modified.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
