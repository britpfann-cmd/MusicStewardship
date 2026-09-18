#!/usr/bin/env python3
"""
MusicStewardship generic Metadata Evidence Decoder.

Purpose:
    Extract and preserve embedded metadata and technical metadata from audio
    source objects without assigning canonical musical meaning.

Architecture:
    Source Object -> ffprobe -> Evidence Records -> downstream interpretation

This tool is intentionally non-destructive. It never modifies source files.

Input modes:
    --file PATH
        Decode one audio file.

    --root PATH
        Recursively inspect audio files beneath PATH. Optional --count and
        --seed provide a deterministic sample.

    --tree JSON
        Consume an Explorer Tree JSON inventory. The inventory must contain
        source_root and relative_path entries; entry_type may be used to
        restrict processing to AUDIO entries.

Outputs:
    JSON evidence result and CSV flattened evidence observations.

The raw ffprobe tag dictionary is retained in each source-object result in
addition to individual EvidenceRecord observations.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import subprocess
import sys
from pathlib import Path
from typing import Any

SCHEMA = "musicstewardship.metadata_evidence.v1"
DECODER = "metadata_tags.v1"

AUDIO_EXTENSIONS = {
    ".aac", ".aif", ".aiff", ".alac", ".flac", ".m4a", ".mp3", ".ogg",
    ".opus", ".wav", ".wma", ".ape", ".wv", ".mka"
}

TECHNICAL_FIELDS = (
    "format_name",
    "format_long_name",
    "duration",
    "size",
    "bit_rate",
    "codec_name",
    "codec_long_name",
    "sample_rate",
    "channels",
    "channel_layout",
    "bits_per_sample",
)

def norm_path(value: str) -> str:
    return value.replace("\\", "/")

def object_id(source_root: str, relative_path: str) -> str:
    key = f"{norm_path(source_root)}\0{norm_path(relative_path)}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:24]

def is_audio(path: Path) -> bool:
    # macOS AppleDouble sidecars (e.g. ._02 Querer.m4a) are preserved
    # source artifacts by Explorer Tree, but are not audio objects for
    # metadata extraction even when their suffix resembles an audio format.
    if not path.is_file():
        return False
    if path.name.startswith("._"):
        return False
    if path.name in {".DS_Store", "Thumbs.db", "desktop.ini"}:
        return False
    return path.suffix.lower() in AUDIO_EXTENSIONS


def run_ffprobe(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    cmd = [
        "ffprobe",
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        str(path),
    ]
    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except FileNotFoundError:
        return None, "ffprobe was not found on PATH"

    if proc.returncode != 0:
        stderr = proc.stderr.decode("utf-8", errors="replace").strip()
        return None, stderr or f"ffprobe exited with code {proc.returncode}"

    try:
        # Decode explicitly as UTF-8, preserving undecodable bytes visibly
        # rather than allowing a Windows code-page conversion.
        text = proc.stdout.decode("utf-8", errors="replace")
        return json.loads(text), None
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return None, f"Unable to decode/parse ffprobe JSON: {exc}"

def make_record(
    source_object_id: str,
    channel: str,
    evidence_type: str,
    locator: str,
    raw_value: Any,
    *,
    extraction_method: str,
    normalized_value: Any = None,
    status: str = "observed",
    derived_from: list[str] | None = None,
) -> dict[str, Any]:
    rec = {
        "evidence_id": hashlib.sha256(
            json.dumps(
                [source_object_id, channel, locator, raw_value],
                ensure_ascii=False,
                sort_keys=True,
                default=str,
            ).encode("utf-8")
        ).hexdigest()[:24],
        "source_object_id": source_object_id,
        "evidence_channel": channel,
        "evidence_type": evidence_type,
        "source_locator": locator,
        "raw_value": raw_value,
        "normalized_value": (
            raw_value if normalized_value is None else normalized_value
        ),
        "extraction_method": extraction_method,
        "decoder": DECODER,
        "confidence": None,
        "status": status,
    }
    if derived_from:
        rec["derived_from"] = derived_from
    return rec

def decode_file(
    path: Path,
    source_root: Path,
    relative_path: str,
) -> dict[str, Any]:
    sid = object_id(str(source_root), relative_path)
    result: dict[str, Any] = {
        "schema": SCHEMA,
        "source_object_id": sid,
        "source_root": norm_path(str(source_root)),
        "relative_path": norm_path(relative_path),
        "filename": path.name,
        "status": "success",
        "observations": [],
        "errors": [],
        "raw": {
            "format_tags": {},
            "stream_tags": [],
            "technical": {},
        },
    }

    probe, error = run_ffprobe(path)
    if probe is None:
        result["status"] = "error"
        result["errors"].append({
            "source_locator": "metadata",
            "error_type": "ffprobe_error",
            "message": error,
        })
        return result

    fmt = probe.get("format") or {}
    tags = fmt.get("tags") or {}
    streams = probe.get("streams") or []

    # Preserve the complete format-tag dictionary exactly as ffprobe supplied it.
    result["raw"]["format_tags"] = tags

    for field, value in tags.items():
        result["observations"].append(
            make_record(
                sid,
                "metadata",
                "tag",
                f"metadata.tag.{field}",
                value,
                extraction_method="ffprobe.format_tags",
            )
        )

    for index, stream in enumerate(streams):
        stream_tags = stream.get("tags") or {}
        result["raw"]["stream_tags"].append({
            "stream_index": index,
            "tags": stream_tags,
        })
        for field, value in stream_tags.items():
            result["observations"].append(
                make_record(
                    sid,
                    "metadata",
                    "stream_tag",
                    f"metadata.stream[{index}].tag.{field}",
                    value,
                    extraction_method="ffprobe.stream_tags",
                )
            )

    technical: dict[str, Any] = {}
    for field in TECHNICAL_FIELDS:
        value = fmt.get(field)
        if value is not None:
            technical[field] = value
            result["observations"].append(
                make_record(
                    sid,
                    "technical",
                    field,
                    f"technical.{field}",
                    value,
                    extraction_method="ffprobe.format",
                )
            )

    # Stream-level technical properties are preserved as observations too.
    for index, stream in enumerate(streams):
        for field in (
            "codec_name", "codec_long_name", "sample_rate", "channels",
            "channel_layout", "bits_per_sample", "duration", "bit_rate"
        ):
            value = stream.get(field)
            if value is not None:
                result["observations"].append(
                    make_record(
                        sid,
                        "technical",
                        field,
                        f"technical.stream[{index}].{field}",
                        value,
                        extraction_method="ffprobe.stream",
                    )
                )

    result["raw"]["technical"] = technical
    return result

def files_from_tree(tree_path: Path) -> tuple[Path, list[tuple[Path, str]]]:
    data = json.loads(tree_path.read_text(encoding="utf-8"))

    # Accept either a top-level list or common inventory wrappers.
    if isinstance(data, list):
        rows = data
    elif isinstance(data, dict):
        rows = (
            data.get("nodes")
            or data.get("entries")
            or data.get("objects")
            or data.get("source_objects")
        )
        if rows is None:
            raise ValueError("Tree JSON has no nodes/entries/objects collection")
    else:
        raise ValueError("Tree JSON must contain an object or array")

    roots = {
        str(row["source_root"])
        for row in rows
        if isinstance(row, dict) and row.get("source_root") is not None
    }
    if len(roots) != 1:
        raise ValueError(f"Expected exactly one source_root; found {len(roots)}")
    root = Path(next(iter(roots)))

    selected: list[tuple[Path, str]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        if row.get("entry_type") not in (None, "AUDIO"):
            continue
        rel = row.get("relative_path")
        if not rel or row.get("entry_type") == "DIRECTORY":
            continue
        path = root / Path(str(rel).replace("/", "\\"))
        if is_audio(path):
            selected.append((path, norm_path(str(rel))))
    selected.sort(key=lambda x: x[1].casefold())
    return root, selected

def choose_files(root: Path, count: int | None, seed: int) -> list[tuple[Path, str]]:
    files = [
        (p, norm_path(str(p.relative_to(root))))
        for p in root.rglob("*")
        if is_audio(p)
    ]
    files.sort(key=lambda x: x[1].casefold())
    if count is not None and count < len(files):
        rng = random.Random(seed)
        files = sorted(rng.sample(files, count), key=lambda x: x[1].casefold())
    return files

def write_outputs(results: list[dict[str, Any]], output_base: Path) -> None:
    output_base.parent.mkdir(parents=True, exist_ok=True)
    json_path = output_base.with_suffix(".json")
    csv_path = output_base.with_suffix(".csv")

    payload = {
        "schema": SCHEMA,
        "decoder": DECODER,
        "source_objects": results,
        "summary": {
            "source_objects": len(results),
            "observations": sum(len(r["observations"]) for r in results),
            "errors": sum(len(r["errors"]) for r in results),
        },
    }

    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    columns = [
        "source_object_id",
        "source_root",
        "relative_path",
        "filename",
        "status",
        "evidence_channel",
        "evidence_type",
        "source_locator",
        "raw_value",
        "normalized_value",
        "extraction_method",
        "decoder",
        "confidence",
        "derived_from",
    ]

    with csv_path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        for result in results:
            for obs in result["observations"]:
                row = {
                    "source_object_id": result["source_object_id"],
                    "source_root": result["source_root"],
                    "relative_path": result["relative_path"],
                    "filename": result["filename"],
                    "status": result["status"],
                    **obs,
                }
                if isinstance(row.get("raw_value"), (dict, list)):
                    row["raw_value"] = json.dumps(
                        row["raw_value"], ensure_ascii=False
                    )
                if isinstance(row.get("normalized_value"), (dict, list)):
                    row["normalized_value"] = json.dumps(
                        row["normalized_value"], ensure_ascii=False
                    )
                if isinstance(row.get("derived_from"), list):
                    row["derived_from"] = ";".join(row["derived_from"])
                writer.writerow({k: row.get(k) for k in columns})

    print(f"JSON: {json_path}")
    print(f"CSV:  {csv_path}")
    print(f"Source objects: {len(results)}")
    print(f"Observations: {payload['summary']['observations']}")
    print(f"Errors: {payload['summary']['errors']}")

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract MusicStewardship metadata evidence non-destructively."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--file", type=Path, help="Decode one audio file")
    group.add_argument("--root", type=Path, help="Recursively scan an audio root")
    group.add_argument("--tree", type=Path, help="Explorer Tree JSON inventory")

    parser.add_argument(
        "--count",
        type=int,
        default=None,
        help="Deterministic sample count when using --root",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=20260918,
        help="Sampling seed (default: 20260918)",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        required=True,
        help="Output base path; .json and .csv are appended",
    )

    args = parser.parse_args()

    if args.file:
        path = args.file.resolve()
        if not is_audio(path):
            parser.error(f"Not a recognized audio file: {path}")
        root = path.parent
        rel = path.name
        pairs = [(path, rel)]

    elif args.root:
        root = args.root.resolve()
        if not root.is_dir():
            parser.error(f"Root is not a directory: {root}")
        pairs = choose_files(root, args.count, args.seed)

    else:
        try:
            root, pairs = files_from_tree(args.tree.resolve())
        except Exception as exc:
            parser.error(str(exc))

    results = [
        decode_file(path, root, rel)
        for path, rel in pairs
    ]

    write_outputs(results, args.output)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
