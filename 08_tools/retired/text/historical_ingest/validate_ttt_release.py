#!/usr/bin/env python3
"""
Validate one complete TTT release against the TTT/TANGO-DJ reference snapshot.

v4 authentication model:
  - TTT recording identifiers are primary evidence.
  - Release/package name is NOT required for recording identity.
  - A TANGO-DJ catalog may contain multiple rows for the same underlying
    recording (for example a TTT album row and a TTT-Transfer row).
  - Such duplicate representations are reported as
      AUTHENTICATED_MULTI_REFERENCE
    when all surviving reference rows have the same recording identity.
  - True ambiguity is reserved for surviving reference rows that differ in
    recording identity.

Authentication priority:
  1. record + matrix + take
  2. record + matrix
  3. record
  4. matrix + title + date
  5. release + track
  6. release + title
  7. title + date

Matrix normalization understands TTT's:
    Matrix: 60013, Take: 2
and TANGO-DJ's:
    matrix_number = 60013-2
as the same recording evidence.

This is NON-DESTRUCTIVE. Source audio is read only.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path


AUDIO_EXTENSIONS = {".flac", ".wav", ".mp3", ".m4a", ".alac"}

TAG_NAMES = (
    "TITLE", "ARTIST", "album_artist", "ALBUM", "GENRE", "DATE",
    "COMPOSER", "CONDUCTOR", "CATALOGNUMBER", "SOURCEMEDIA",
    "track", "COMMENT",
)


def norm(value: str) -> str:
    if not value:
        return ""
    value = (
        value.replace("\u2010", "-").replace("\u2011", "-")
        .replace("\u2012", "-").replace("\u2013", "-")
        .replace("\u2014", "-")
    )
    return re.sub(r"\s+", " ", value.strip()).casefold()


def compact_norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", norm(value))


def track_norm(value: str) -> str:
    s = norm(value)
    m = re.fullmatch(r"0*(\d+(?:\.\d+)?)", s)
    return m.group(1) if m else s


def split_matrix_take(value: str) -> tuple[str, str]:
    """Normalize matrix evidence such as 60013 or 60013-2."""
    raw = (value or "").strip()
    m = re.fullmatch(r"\s*(.+?)[-/](\d+)\s*", raw)
    if m:
        return compact_norm(m.group(1)), m.group(2)
    return compact_norm(raw), ""


def parse_catalog(value: str) -> tuple[str, str, str]:
    """Parse flexible TTT CATALOGNUMBER formatting."""
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


def parse_comment(value: str) -> dict[str, str]:
    text = (value or "").strip()
    out = {"pitch_hz": "", "key": "", "score_key": ""}

    m = re.search(r"(?i)\bA4\s*:\s*(\d+(?:\.\d+)?)\s*Hz\b", text)
    if m:
        out["pitch_hz"] = m.group(1)

    m = re.search(r"(?i)\bKey\s*:\s*([^,;]+)", text)
    if m:
        out["key"] = m.group(1).strip()

    m = re.search(r"(?i)\bScore\s*:\s*([^,;]+)", text)
    if m:
        out["score_key"] = m.group(1).strip()

    return out


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

    for pattern in (
        r"(?i)\bLyrics?\s*:\s*(.+)$",
        r"(?i)\bVers\.\s*cast\.\s*:\s*(.+)$",
    ):
        m = re.search(pattern, value)
        if not m:
            continue
        before = value[:m.start()].rstrip(" ,-")
        credit = m.group(1).strip()
        if "Vers." in m.group(0):
            return before.strip(), "", credit
        return before.strip(), credit, ""

    return value.strip(), "", ""


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
        command, capture_output=True, text=True,
        encoding="utf-8", errors="replace",
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
        "probe_error": "",
    }


def source_identity(meta: dict[str, str]) -> dict[str, str]:
    record, matrix, take = parse_catalog(meta["TAG:CATALOGNUMBER"])
    matrix_norm, embedded_take = split_matrix_take(matrix)
    return {
        "record": compact_norm(record),
        "matrix": matrix_norm,
        "take": norm(take or embedded_take),
    }


def reference_identity(row: dict[str, str]) -> dict[str, object]:
    record_field = row.get("catalog_number", "")
    record_tokens = [
        compact_norm(x) for x in re.split(r"\s*/\s*", record_field)
        if x.strip()
    ]
    matrix, matrix_take = split_matrix_take(row.get("matrix_number", ""))
    take = norm(row.get("take_number", "") or matrix_take)
    return {
        "record_tokens": record_tokens,
        "matrix": matrix,
        "take": take,
    }


def build_indexes(reference):
    indexes = defaultdict(lambda: defaultdict(list))
    for i, row in enumerate(reference):
        ident = reference_identity(row)
        for record in ident["record_tokens"]:
            if record:
                indexes["RECORD"][record].append(i)
                if ident["matrix"]:
                    indexes["RECORD_MATRIX"][(record, ident["matrix"])].append(i)
                    if ident["take"]:
                        indexes["RECORD_MATRIX_TAKE"][(record, ident["matrix"], ident["take"])].append(i)
        if ident["matrix"] and row.get("title") and row.get("recording_date"):
            indexes["MATRIX_TITLE_DATE"][(ident["matrix"], norm(row["title"]), norm(row["recording_date"]))].append(i)
        album = norm(row.get("album", ""))
        track = track_norm(row.get("track_number", ""))
        title = norm(row.get("title", ""))
        date = norm(row.get("recording_date", ""))
        if album and track:
            indexes["RELEASE_TRACK"][(album, track)].append(i)
        if album and title:
            indexes["RELEASE_TITLE"][(album, title)].append(i)
        if title and date:
            indexes["TITLE_DATE"][(title, date)].append(i)
    return indexes


def same_recording_reference_rows(rows: list[dict[str, str]]) -> bool:
    if len(rows) <= 1:
        return True
    idents = [reference_identity(r) for r in rows]

    common_pairs = None
    for ident in idents:
        pairs = {
            (record, ident["matrix"])
            for record in ident["record_tokens"]
            if record and ident["matrix"]
        }
        if common_pairs is None:
            common_pairs = pairs
        else:
            common_pairs &= pairs
    if common_pairs:
        return True

    common_records = None
    for ident in idents:
        records = set(ident["record_tokens"])
        if common_records is None:
            common_records = records
        else:
            common_records &= records
    if common_records:
        titles = {norm(r.get("title", "")) for r in rows}
        dates = {norm(r.get("recording_date", "")) for r in rows}
        if len(titles) == 1 and len(dates) <= 1:
            return True

    signatures = {
        (
            tuple(sorted(ident["record_tokens"])),
            ident["matrix"],
            ident["take"],
            norm(row.get("title", "")),
            norm(row.get("recording_date", "")),
        )
        for ident, row in zip(idents, rows)
    }
    return len(signatures) == 1


def find_reference(meta, indexes, reference):
    src = source_identity(meta)
    title = norm(meta["TAG:TITLE"])
    date = norm(meta["TAG:DATE"])
    album = norm(meta["TAG:ALBUM"])
    track = track_norm(meta["TAG:track"])

    checks = []
    if src["record"] and src["matrix"] and src["take"]:
        checks.append(("RECORD_MATRIX_TAKE", indexes["RECORD_MATRIX_TAKE"].get((src["record"], src["matrix"], src["take"]), [])))
    if src["record"] and src["matrix"]:
        checks.append(("RECORD_MATRIX", indexes["RECORD_MATRIX"].get((src["record"], src["matrix"]), [])))
    if src["record"]:
        checks.append(("RECORD", indexes["RECORD"].get(src["record"], [])))
    if src["matrix"] and title and date:
        checks.append(("MATRIX_TITLE_DATE", indexes["MATRIX_TITLE_DATE"].get((src["matrix"], title, date), [])))
    if album and track:
        checks.append(("RELEASE_TRACK", indexes["RELEASE_TRACK"].get((album, track), [])))
    if album and title:
        checks.append(("RELEASE_TITLE", indexes["RELEASE_TITLE"].get((album, title), [])))
    if title and date:
        checks.append(("TITLE_DATE", indexes["TITLE_DATE"].get((title, date), [])))

    for method, candidates in checks:
        if not candidates:
            continue
        unique_indices = list(dict.fromkeys(candidates))
        rows = [reference[i] for i in unique_indices]
        if len(rows) == 1:
            return rows[0], method, 1, rows
        if same_recording_reference_rows(rows):
            return rows[0], method + "_MULTI", len(rows), rows
        return {}, method + "_AMBIGUOUS", len(rows), rows

    return {}, "NO_MATCH", 0, []


def date_swap(a: str, b: str) -> bool:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", a or ""):
        return False
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", b or ""):
        return False
    ay, am, ad = map(int, a.split("-"))
    by, bm, bd = map(int, b.split("-"))
    return ay == by and am == bd and ad == bm and 1 <= bm <= 12 and 1 <= bd <= 31


def date_precision_difference(a: str, b: str) -> bool:
    if not a or not b:
        return False
    pairs = ((r"\d{4}", r"\d{4}-\d{2}-\d{2}"), (r"\d{4}-\d{2}", r"\d{4}-\d{2}-\d{2}"))
    for short_re, long_re in pairs:
        if re.fullmatch(short_re, a) and re.fullmatch(long_re, b):
            return a == b[:len(a)]
        if re.fullmatch(short_re, b) and re.fullmatch(long_re, a):
            return b == a[:len(b)]
    return False


def make_record(meta, ref, method, candidate_count, all_refs):
    ensemble_from_artist, performer_text, performance_note = split_artist(meta["TAG:ARTIST"])
    composer, lyricist, other_credit = split_composer(meta["TAG:COMPOSER"])
    record_number, matrix_number, take_number = parse_catalog(meta["TAG:CATALOGNUMBER"])
    comment = parse_comment(meta["TAG:COMMENT"])

    if method == "NO_MATCH":
        auth_status = "NO_REFERENCE_RECORD"
        flags = ["NO_REFERENCE_MATCH"]
    elif method.endswith("_AMBIGUOUS"):
        auth_status = "AMBIGUOUS_REFERENCE"
        flags = ["AMBIGUOUS_REFERENCE"]
    elif method.endswith("_MULTI"):
        auth_status = "AUTHENTICATED_MULTI_REFERENCE"
        flags = ["MULTIPLE_REFERENCE_ROWS_SAME_RECORDING"]
    else:
        auth_status = "AUTHENTICATED"
        flags = []

    source_date = meta["TAG:DATE"]
    ref_date = ref.get("recording_date", "")
    if ref:
        if meta["TAG:TITLE"] and ref.get("title") and norm(meta["TAG:TITLE"]) != norm(ref["title"]):
            flags.append("TITLE_DIFFERS")
        if meta["TAG:ALBUM"] and ref.get("album") and norm(meta["TAG:ALBUM"]) != norm(ref["album"]):
            flags.append("ALBUM_REPRESENTATION_DIFF")
        if source_date and ref_date and source_date != ref_date:
            if date_swap(source_date, ref_date):
                flags.append("DATE_TRANSPOSITION_SUSPECTED")
            elif date_precision_difference(source_date, ref_date):
                flags.append("DATE_PRECISION_DIFFERENCE")
            else:
                flags.append("DATE_CONFLICT")
        if meta["TAG:ARTIST"] and ref.get("artist"):
            flags.append("ARTIST_REPRESENTATION_DIFF")
        if meta["TAG:CATALOGNUMBER"] and ref.get("catalog_number"):
            flags.append("CATALOG_REPRESENTATION_DIFF")

    ref_ids = ";".join(r.get("tango_dj_ref", "") for r in all_refs if r.get("tango_dj_ref", ""))

    return {
        "source_file": meta["source_file"],
        "source_filename": meta["source_filename"],
        "format": meta["format"],
        "duration": meta["duration"],
        "codec": meta["codec"],
        "sample_rate": meta["sample_rate"],
        "channels": meta["channels"],
        "channel_layout": meta["channel_layout"],
        "bits_per_sample": meta["bits_per_sample"],
        "title": meta["TAG:TITLE"],
        "ensemble": meta["TAG:album_artist"] or ensemble_from_artist,
        "ensemble_type": "",
        "performer_text": performer_text,
        "performance_note": performance_note,
        "singer_text": "" if performer_text.casefold() in {"", "instr."} else performer_text,
        "instrumental": "YES" if "instr." in performer_text.casefold() else "NO",
        "recording_date": source_date,
        "genre": meta["TAG:GENRE"],
        "composer": composer,
        "lyricist": lyricist,
        "other_composer_credit": other_credit,
        "conductor": meta["TAG:CONDUCTOR"],
        "record_number": record_number,
        "matrix_number": matrix_number,
        "take_number": take_number,
        "source_media": meta["TAG:SOURCEMEDIA"],
        "release": meta["TAG:ALBUM"],
        "release_track_number": meta["TAG:track"],
        "pitch_hz": comment["pitch_hz"],
        "key": comment["key"],
        "score_key": comment["score_key"],
        "source_comment": meta["TAG:COMMENT"],
        "source_catalog_evidence": meta["TAG:CATALOGNUMBER"],
        "authentication_status": auth_status,
        "authentication_match_method": method,
        "authentication_candidate_count": candidate_count,
        "tango_dj_refs": ref_ids,
        "tango_dj_ref": ref.get("tango_dj_ref", ""),
        "reference_title": ref.get("title", ""),
        "reference_artist": ref.get("artist", ""),
        "reference_date": ref_date,
        "reference_album": ref.get("album", ""),
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

    files = sorted(p for p in args.release_dir.rglob("*") if p.is_file() and p.suffix.casefold() in AUDIO_EXTENSIONS)
    if not files:
        parser.error("No supported audio files found in release directory")

    with args.reference_csv.open("r", encoding="utf-8-sig", newline="") as f:
        reference = list(csv.DictReader(f))

    indexes = build_indexes(reference)
    results = []

    for i, path in enumerate(files, start=1):
        print(f"{i:03d} - {path.name}")
        try:
            meta = extract_meta(path, ffprobe(path))
            ref, method, count, all_refs = find_reference(meta, indexes, reference)
            results.append(make_record(meta, ref, method, count, all_refs))
        except Exception as exc:
            meta = {
                "source_file": str(path), "source_filename": path.name,
                "format": "", "duration": "", "codec": "", "sample_rate": "",
                "channels": "", "channel_layout": "", "bits_per_sample": "",
                **{f"TAG:{k}": "" for k in TAG_NAMES}, "probe_error": str(exc),
            }
            results.append(make_record(meta, {}, "PROBE_ERROR", 0, []))

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.output_csv.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)

    summary = {
        "release_directory": str(args.release_dir),
        "files_examined": len(results),
        "authenticated": sum(r["authentication_status"] == "AUTHENTICATED" for r in results),
        "authenticated_multi_reference": sum(r["authentication_status"] == "AUTHENTICATED_MULTI_REFERENCE" for r in results),
        "ambiguous_reference": sum(r["authentication_status"] == "AMBIGUOUS_REFERENCE" for r in results),
        "no_reference_record": sum(r["authentication_status"] == "NO_REFERENCE_RECORD" for r in results),
        "probe_errors": sum(bool(r["probe_error"]) for r in results),
        "matched_by_record_matrix_take": sum(r["authentication_match_method"] == "RECORD_MATRIX_TAKE" for r in results),
        "matched_by_record_matrix": sum(r["authentication_match_method"] == "RECORD_MATRIX" for r in results),
        "matched_by_record": sum(r["authentication_match_method"] == "RECORD" for r in results),
        "matched_by_matrix_title_date": sum(r["authentication_match_method"] == "MATRIX_TITLE_DATE" for r in results),
        "matched_by_release_track": sum(r["authentication_match_method"] == "RELEASE_TRACK" for r in results),
        "matched_by_release_title": sum(r["authentication_match_method"] == "RELEASE_TITLE" for r in results),
        "matched_by_title_date": sum(r["authentication_match_method"] == "TITLE_DATE" for r in results),
        "date_transposition_suspected": sum("DATE_TRANSPOSITION_SUSPECTED" in r["authentication_flags"] for r in results),
        "date_precision_difference": sum("DATE_PRECISION_DIFFERENCE" in r["authentication_flags"] for r in results),
        "date_conflicts": sum("DATE_CONFLICT" in r["authentication_flags"] for r in results),
        "title_differences": sum("TITLE_DIFFERS" in r["authentication_flags"] for r in results),
    }

    if args.summary_csv is None:
        args.summary_csv = args.output_csv.with_name(args.output_csv.stem + "_summary.csv")

    with args.summary_csv.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary.keys()))
        writer.writeheader()
        writer.writerow(summary)

    print()
    for key, value in summary.items():
        print(f"{key.replace('_', ' ').capitalize()}: {value}")
    print(f"Validation CSV: {args.output_csv}")
    print(f"Summary CSV: {args.summary_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
