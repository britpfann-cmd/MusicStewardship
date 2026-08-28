#!/usr/bin/env python3
"""
Validate an entire TTT release directory against the TTT/TANGO-DJ reference
snapshot.

This is a NON-DESTRUCTIVE validation tool.

It:
  1. finds audio files in one TTT release directory;
  2. probes each file with ffprobe;
  3. builds canonical TTT staging fields using the same decomposition rules
     as build_ttt_canonical_staging.py;
  4. matches the files to the extracted TTT/TANGO-DJ reference snapshot;
  5. writes a detailed per-file CSV;
  6. writes a compact validation summary CSV.

The TTT file is the primary ingest source. TANGO-DJ is only an
authentication/reference source.

Usage:
  python validate_ttt_release.py RELEASE_DIR REFERENCE_CSV OUTPUT_CSV [SUMMARY_CSV]

Example:
  python validate_ttt_release.py ^
      "M:\\TangoTimeTravel\\Todos de Edgardo Donato 1940-1945" ^
      ".\\03_assets\\ReferenceCatalogs\\TANGO-DJ_AT\\2026-08-28\\TTT\\extracted\\TTT_TANGO-DJ_2026-08-28.csv" ^
      ".\\08_tools\\text\\tests\\TTT_Donato_1940-1945_validation.csv"

Requires ffprobe on PATH.
"""

from __future__ import annotations

import argparse
import csv
import re
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Iterable


AUDIO_EXTENSIONS = {".flac", ".wav", ".mp3", ".m4a", ".alac"}

REQUIRED_TAGS = (
    "TITLE",
    "ARTIST",
    "album_artist",
    "ALBUM",
    "GENRE",
    "DATE",
    "COMPOSER",
    "CONDUCTOR",
    "CATALOGNUMBER",
    "SOURCEMEDIA",
    "track",
)


def norm(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip()).casefold()


def track_norm(value: str) -> str:
    s = norm(value)
    match = re.search(r"\d+", s)
    return str(int(match.group())) if match else s


def split_artist(value: str) -> tuple[str, str, str]:
    if " / " not in value:
        return value.strip(), "", ""
    ensemble, remainder = value.split(" / ", 1)
    note = ""
    m = re.search(r"\s*(\(.*\))\s*$", remainder)
    if m:
        note = m.group(1).strip()
        remainder = remainder[:m.start()].strip()
    return ensemble.strip(), remainder.strip(), note


def split_composer(value: str) -> tuple[str, str, str]:
    if not value:
        return "", "", ""

    patterns = [
        r"(?i)\bLyrics?\s*:\s*(.+)$",
        r"(?i)\bVers\.\s*cast\.\s*:\s*(.+)$",
    ]

    for pattern in patterns:
        m = re.search(pattern, value)
        if not m:
            continue

        credit = m.group(1).strip()
        before = value[:m.start()].rstrip(" ,-")

        if "Vers." in m.group(0):
            return before.strip(), "", credit

        return before.strip(), credit, ""

    return value.strip(), "", ""


def split_catalog(value: str) -> tuple[str, str, str]:
    raw = (value or "").strip()
    record = ""
    matrix = ""
    take = ""

    m = re.search(
        r"(?i)\bRecord\s*:\s*(.*?)(?=,\s*Matrix\s*:|$)",
        raw,
    )
    if m:
        record = m.group(1).strip()

    m = re.search(
        r"(?i)\bMatrix\s*:\s*(.*?)(?=,\s*Take\s*:|$)",
        raw,
    )
    if m:
        matrix = m.group(1).strip()

    m = re.search(r"(?i)\bTake\s*:\s*(\d+)", raw)
    if m:
        take = m.group(1)

    return record, matrix, take


def parse_comment(value: str) -> dict[str, str]:
    text = (value or "").strip()
    out = {
        "pitch_hz": "",
        "key": "",
        "score_key": "",
    }

    m = re.search(
        r"(?i)\bA4\s*:\s*(\d+(?:\.\d+)?)\s*Hz\b",
        text,
    )
    if m:
        out["pitch_hz"] = m.group(1)

    m = re.search(r"(?i)\bKey\s*:\s*([^,;]+)", text)
    if m:
        out["key"] = m.group(1).strip()

    m = re.search(r"(?i)\bScore\s*:\s*([^,;]+)", text)
    if m:
        out["score_key"] = m.group(1).strip()

    return out


def ffprobe(path: Path) -> dict:
    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        (
            "format=duration,format_name:format_tags"
            ":stream=index,codec_name,sample_rate,channels,"
            "channel_layout,bits_per_sample"
        ),
        "-of",
        "json",
        str(path),
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

    import json
    return json.loads(result.stdout)


def probe_to_meta(path: Path, data: dict) -> dict[str, str]:
    fmt = data.get("format", {})
    tags = fmt.get("tags", {}) or {}
    stream = (data.get("streams") or [{}])[0]

    # ffprobe may preserve different capitalization. Build a case-insensitive
    # lookup while retaining the original value.
    tag_lookup = {str(k).casefold(): str(v) for k, v in tags.items()}

    def get_tag(name: str) -> str:
        return tag_lookup.get(name.casefold(), "").strip()

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
        **{f"TAG:{name}": get_tag(name) for name in REQUIRED_TAGS},
        "TAG:COMMENT": get_tag("COMMENT"),
        "probe_error": "",
    }


def build_indexes(reference: list[dict[str, str]]):
    by_album_track = defaultdict(list)
    by_album_title = defaultdict(list)
    by_title_date = defaultdict(list)

    for i, row in enumerate(reference):
        album = row.get("album", "")
        track = row.get("track_number", "")
        title = row.get("title", "")
        rec_date = row.get("recording_date", "")

        if album and track:
            by_album_track[(norm(album), track_norm(track))].append(i)

        if album and title:
            by_album_title[(norm(album), norm(title))].append(i)

        if title and rec_date:
            by_title_date[(norm(title), norm(rec_date))].append(i)

    return by_album_track, by_album_title, by_title_date


def find_reference(meta, indexes, reference):
    by_album_track, by_album_title, by_title_date = indexes

    album = meta["TAG:ALBUM"]
    track = meta["TAG:track"]
    title = meta["TAG:TITLE"]
    rec_date = meta["TAG:DATE"]

    candidates = by_album_track.get(
        (norm(album), track_norm(track)),
        [],
    )
    if len(candidates) == 1:
        return reference[candidates[0]], "ALBUM_TRACK", 1
    if len(candidates) > 1:
        return {}, "ALBUM_TRACK_AMBIGUOUS", len(candidates)

    candidates = by_album_title.get(
        (norm(album), norm(title)),
        [],
    )
    if len(candidates) == 1:
        return reference[candidates[0]], "ALBUM_TITLE", 1
    if len(candidates) > 1:
        return {}, "ALBUM_TITLE_AMBIGUOUS", len(candidates)

    candidates = by_title_date.get(
        (norm(title), norm(rec_date)),
        [],
    )
    if len(candidates) == 1:
        return reference[candidates[0]], "TITLE_DATE", 1
    if len(candidates) > 1:
        return {}, "TITLE_DATE_AMBIGUOUS", len(candidates)

    return {}, "NO_MATCH", 0


def date_swap(a: str, b: str) -> bool:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", a or ""):
        return False
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", b or ""):
        return False

    ay, am, ad = map(int, a.split("-"))
    by, bm, bd = map(int, b.split("-"))

    return (
        ay == by
        and am == bd
        and ad == bm
        and 1 <= bm <= 12
        and 1 <= bd <= 31
    )


def compare_value(source: str, reference: str) -> str:
    if not source and not reference:
        return "BOTH_MISSING"
    if not source or not reference:
        return "ONE_SIDE_MISSING"
    return "AGREE" if norm(source) == norm(reference) else "DISAGREE"


def make_record(meta: dict, ref: dict, match_method: str, count: int):
    title = meta["TAG:TITLE"]
    artist_raw = meta["TAG:ARTIST"]
    album_artist = meta["TAG:album_artist"]
    album = meta["TAG:ALBUM"]
    genre = meta["TAG:GENRE"]
    rec_date = meta["TAG:DATE"]
    composer_raw = meta["TAG:COMPOSER"]
    conductor = meta["TAG:CONDUCTOR"]
    catalog_raw = meta["TAG:CATALOGNUMBER"]
    source_media = meta["TAG:SOURCEMEDIA"]
    track = meta["TAG:track"]
    comment = meta["TAG:COMMENT"]

    ensemble_from_artist, performer_text, performance_note = split_artist(
        artist_raw
    )
    ensemble = album_artist or ensemble_from_artist

    composer, lyricist, other_credit = split_composer(composer_raw)
    record_number, matrix_number, take_number = split_catalog(catalog_raw)
    comment_fields = parse_comment(comment)

    ref_date = ref.get("recording_date", "")
    flags = []

    if match_method.endswith("AMBIGUOUS"):
        flags.append("AMBIGUOUS_REFERENCE")
    elif match_method == "NO_MATCH":
        flags.append("NO_REFERENCE_MATCH")

    if ref:
        if title and ref.get("title") and norm(title) != norm(ref["title"]):
            flags.append("TITLE_DIFFERS")

        if rec_date and ref_date and rec_date != ref_date:
            if date_swap(rec_date, ref_date):
                flags.append("DATE_TRANSPOSITION_SUSPECTED")
            else:
                flags.append("DATE_CONFLICT")

        if album and ref.get("album") and norm(album) != norm(ref["album"]):
            flags.append("ALBUM_REPRESENTATION_DIFF")

        if artist_raw and ref.get("artist"):
            flags.append("ARTIST_REPRESENTATION_DIFF")

        if catalog_raw and ref.get("catalog_number"):
            flags.append("CATALOG_REPRESENTATION_DIFF")

    auth_status = (
        "AUTHENTICATED"
        if ref and match_method != "NO_MATCH" and not match_method.endswith("AMBIGUOUS")
        else (
            "AMBIGUOUS_REFERENCE"
            if match_method.endswith("AMBIGUOUS")
            else "NO_REFERENCE_RECORD"
        )
    )

    return {
        "source_file": meta["source_file"],
        "source_filename": meta["source_filename"],
        "ttt_release_directory": str(Path(meta["source_file"]).parent),
        "format": meta["format"],
        "duration": meta["duration"],
        "codec": meta["codec"],
        "sample_rate": meta["sample_rate"],
        "channels": meta["channels"],
        "channel_layout": meta["channel_layout"],
        "bits_per_sample": meta["bits_per_sample"],
        "title": title,
        "ensemble": ensemble,
        "ensemble_type": "",
        "performer_text": performer_text,
        "performance_note": performance_note,
        "singer_text": (
            "" if performer_text.casefold() in {"", "instr."}
            else performer_text
        ),
        "instrumental": (
            "YES" if "instr." in performer_text.casefold() else "NO"
        ),
        "recording_date": rec_date,
        "genre": genre,
        "composer": composer,
        "lyricist": lyricist,
        "other_composer_credit": other_credit,
        "conductor": conductor,
        "record_number": record_number,
        "matrix_number": matrix_number,
        "take_number": take_number,
        "source_media": source_media,
        "release": album,
        "release_track_number": track,
        "pitch_hz": comment_fields["pitch_hz"],
        "key": comment_fields["key"],
        "score_key": comment_fields["score_key"],
        "source_comment": comment,
        "source_catalog_evidence": catalog_raw,
        "authentication_status": auth_status,
        "authentication_match_method": match_method,
        "authentication_candidate_count": count,
        "tango_dj_ref": ref.get("tango_dj_ref", ""),
        "reference_title": ref.get("title", ""),
        "reference_artist": ref.get("artist", ""),
        "reference_genre": ref.get("genre", ""),
        "reference_date": ref.get("recording_date", ""),
        "reference_catalog_number": ref.get("catalog_number", ""),
        "reference_matrix_number": ref.get("matrix_number", ""),
        "authentication_flags": ";".join(flags),
        "probe_error": meta.get("probe_error", ""),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("release_dir", type=Path)
    parser.add_argument("reference_csv", type=Path)
    parser.add_argument("output_csv", type=Path)
    parser.add_argument("summary_csv", type=Path, nargs="?")
    args = parser.parse_args()

    if not args.release_dir.is_dir():
        parser.error(f"Release directory not found: {args.release_dir}")
    if not args.reference_csv.is_file():
        parser.error(f"Reference CSV not found: {args.reference_csv}")

    with args.reference_csv.open(
        "r", encoding="utf-8-sig", newline=""
    ) as f:
        reference = list(csv.DictReader(f))

    files = sorted(
        p for p in args.release_dir.rglob("*")
        if p.is_file() and p.suffix.casefold() in AUDIO_EXTENSIONS
    )

    if not files:
        parser.error("No supported audio files found in release directory")

    indexes = build_indexes(reference)
    results = []

    for path in files:
        print(path.name)
        try:
            meta = probe_to_meta(path, ffprobe(path))
            ref, method, count = find_reference(meta, indexes, reference)
            results.append(make_record(meta, ref, method, count))
        except Exception as exc:
            meta = {
                "source_file": str(path),
                "source_filename": path.name,
                "format": "",
                "duration": "",
                "codec": "",
                "sample_rate": "",
                "channels": "",
                "channel_layout": "",
                "bits_per_sample": "",
                **{f"TAG:{name}": "" for name in REQUIRED_TAGS},
                "TAG:COMMENT": "",
                "probe_error": str(exc),
            }
            results.append(make_record(meta, {}, "PROBE_ERROR", 0))

    output_fields = list(results[0].keys())
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)

    with args.output_csv.open(
        "w", encoding="utf-8-sig", newline=""
    ) as f:
        writer = csv.DictWriter(f, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(results)

    summary = {
        "release_directory": str(args.release_dir),
        "files_examined": len(results),
        "authenticated": sum(
            r["authentication_status"] == "AUTHENTICATED"
            for r in results
        ),
        "no_reference_record": sum(
            r["authentication_status"] == "NO_REFERENCE_RECORD"
            for r in results
        ),
        "ambiguous_reference": sum(
            r["authentication_status"] == "AMBIGUOUS_REFERENCE"
            for r in results
        ),
        "probe_errors": sum(
            bool(r["probe_error"]) for r in results
        ),
        "date_transposition_suspected": sum(
            "DATE_TRANSPOSITION_SUSPECTED" in r["authentication_flags"]
            for r in results
        ),
        "date_conflicts": sum(
            "DATE_CONFLICT" in r["authentication_flags"]
            for r in results
        ),
        "title_differences": sum(
            "TITLE_DIFFERS" in r["authentication_flags"]
            for r in results
        ),
        "album_representation_differences": sum(
            "ALBUM_REPRESENTATION_DIFF" in r["authentication_flags"]
            for r in results
        ),
    }

    if args.summary_csv is None:
        args.summary_csv = args.output_csv.with_name(
            args.output_csv.stem + "_summary.csv"
        )

    with args.summary_csv.open(
        "w", encoding="utf-8-sig", newline=""
    ) as f:
        writer = csv.DictWriter(f, fieldnames=summary.keys())
        writer.writeheader()
        writer.writerow(summary)

    print()
    print(f"Files examined: {summary['files_examined']}")
    print(f"Authenticated: {summary['authenticated']}")
    print(f"No reference record: {summary['no_reference_record']}")
    print(f"Ambiguous reference: {summary['ambiguous_reference']}")
    print(f"Probe errors: {summary['probe_errors']}")
    print(
        "Date transposition suspected:",
        summary["date_transposition_suspected"],
    )
    print(f"Validation CSV: {args.output_csv}")
    print(f"Summary CSV: {args.summary_csv}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
