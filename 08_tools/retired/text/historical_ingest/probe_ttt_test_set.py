#!/usr/bin/env python3

import csv
import json
import subprocess
import sys
from pathlib import Path


def probe_file(path: Path) -> dict:
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries",
        "format=filename,format_name,duration:format_tags",
        "-show_entries",
        "stream=index,codec_name,codec_long_name,sample_rate,channels,channel_layout,bits_per_sample",
        "-of", "json",
        str(path),
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())

    return json.loads(result.stdout)


def flatten_probe(test_case, release, source_file, data):
    fmt = data.get("format", {})
    tags = fmt.get("tags", {}) or {}
    streams = data.get("streams", [])

    audio = streams[0] if streams else {}

    row = {
        "test_case": test_case,
        "release": release,
        "source_file": source_file,
        "filename": Path(source_file).name,
        "format": fmt.get("format_name", ""),
        "duration": fmt.get("duration", ""),
        "codec": audio.get("codec_name", ""),
        "codec_long_name": audio.get("codec_long_name", ""),
        "sample_rate": audio.get("sample_rate", ""),
        "channels": audio.get("channels", ""),
        "channel_layout": audio.get("channel_layout", ""),
        "bits_per_sample": audio.get("bits_per_sample", ""),
    }

    # Preserve every embedded tag exactly as reported by ffprobe.
    for key, value in sorted(tags.items()):
        row[f"TAG:{key}"] = value

    return row


def main():
    if len(sys.argv) != 3:
        print(
            "Usage:\n"
            "  python probe_ttt_test_set.py INPUT_CSV OUTPUT_CSV"
        )
        return 2

    input_csv = Path(sys.argv[1])
    output_csv = Path(sys.argv[2])

    rows = []
    all_tag_names = set()

    with input_csv.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as f:
        reader = csv.DictReader(f)

        for item in reader:
            path = Path(item["source_file"])

            print(
                f"{item['test_case']}: "
                f"{item['filename']}"
            )

            try:
                data = probe_file(path)

                row = flatten_probe(
                    item["test_case"],
                    item["release"],
                    item["source_file"],
                    data,
                )

                all_tag_names.update(
                    key for key in row
                    if key.startswith("TAG:")
                )

                rows.append(row)

            except Exception as exc:
                print(
                    f"  ERROR: {exc}",
                    file=sys.stderr
                )

                rows.append({
                    "test_case": item["test_case"],
                    "release": item["release"],
                    "source_file": item["source_file"],
                    "filename": path.name,
                    "probe_error": str(exc),
                })

    base_fields = [
        "test_case",
        "release",
        "source_file",
        "filename",
        "format",
        "duration",
        "codec",
        "codec_long_name",
        "sample_rate",
        "channels",
        "channel_layout",
        "bits_per_sample",
        "probe_error",
    ]

    fieldnames = base_fields + sorted(all_tag_names)

    output_csv.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with output_csv.open(
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)

    print()
    print(f"Files processed: {len(rows)}")
    print(f"Unique embedded tags: {len(all_tag_names)}")
    print(f"CSV written: {output_csv}")


if __name__ == "__main__":
    raise SystemExit(main())