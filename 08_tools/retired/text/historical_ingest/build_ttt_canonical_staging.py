#!/usr/bin/env python3
"""
Build MusicStewardship canonical staging records from TTT embedded metadata.

Primary source:
    TTT_test_metadata.csv

Authentication reference:
    TTT_tags_vs_reference_v2.csv

The TTT file supplies the values used for the staging record. TANGO-DJ is
used to authenticate the identity and flag discrepancies; it does not
overwrite the TTT-derived values.

Special handling:
  * ARTIST is decomposed into ensemble + performer/singer/instrumental note.
  * COMPOSER is decomposed into composer text + lyricist/other credit text.
  * CATALOGNUMBER is decomposed into record, matrix, and take where present.
  * COMMENT is parsed for pitch, key, score, and retained verbatim.
  * A date disagreement is flagged as DATE_TRANSPOSITION_SUSPECTED when the
    two dates are identical after swapping month/day. This is a review flag,
    not an automatic correction.
"""

from __future__ import annotations

import argparse
import csv
import re
from datetime import date
from pathlib import Path


def tag(row: dict[str, str], name: str) -> str:
    return row.get(f"TAG:{name}", "").strip()


def split_artist(value: str) -> tuple[str, str, str]:
    """
    TTT examples:
      'Aníbal Troilo / F. Fiorentino y A. Mandarino'
      'Aníbal Troilo / Instr.'
      'Rodolfo Biagi / Instr. (solo de piano)'

    Return:
      ensemble, performer_text, performance_note
    """
    if " / " not in value:
        return value, "", ""

    ensemble, remainder = value.split(" / ", 1)
    note = ""

    m = re.search(r"\s*(\(.*\))\s*$", remainder)
    if m:
        note = m.group(1).strip()
        remainder = remainder[:m.start()].strip()

    return ensemble.strip(), remainder.strip(), note


def split_composer(value: str) -> tuple[str, str, str]:
    """
    Preserve the raw field while separating common TTT lyric markers.
    Return:
      composer_text, lyricist_text, other_credit_text
    """
    lyric = ""
    other = value

    patterns = [
        r"(?i)\bLyrics?\s*:\s*(.+)$",
        r"(?i)\bVers\.\s*cast\.\s*:\s*(.+)$",
    ]

    for pattern in patterns:
        m = re.search(pattern, other)
        if m:
            credit = m.group(1).strip()
            if "Lyric" in m.group(0):
                lyric = credit
            else:
                lyric = lyric or ""
                other = other[:m.start()].rstrip(" ,-")
                return other, lyric, credit

            other = other[:m.start()].rstrip(" ,-")
            break

    return other.strip(), lyric, ""


def split_catalog(value: str) -> tuple[str, str, str, str]:
    """
    Decompose TTT CATALOGNUMBER.
    Returns:
      record_number, matrix_number, take_number, raw_catalog_evidence
    """
    raw = value.strip()
    record = ""
    matrix = ""
    take = ""

    m = re.search(r"(?i)\bRecord\s*:\s*(.*?)(?=,\s*Matrix\s*:|$)", raw)
    if m:
        record = m.group(1).strip()

    m = re.search(r"(?i)\bMatrix\s*:\s*(.*?)(?=,\s*Take\s*:|$)", raw)
    if m:
        matrix = m.group(1).strip()

    m = re.search(r"(?i)\bTake\s*:\s*(\d+)", raw)
    if m:
        take = m.group(1)

    return record, matrix, take, raw


def parse_comment(value: str) -> dict[str, str]:
    out = {
        "pitch_hz": "",
        "key": "",
        "score_key": "",
        "comment_note": value.strip(),
    }

    if not value:
        return out

    m = re.search(r"(?i)\bA4\s*:\s*(\d+(?:\.\d+)?)\s*Hz\b", value)
    if m:
        out["pitch_hz"] = m.group(1)

    m = re.search(r"(?i)\bKey\s*:\s*([^,;]+)", value)
    if m:
        out["key"] = m.group(1).strip()

    m = re.search(r"(?i)\bScore\s*:\s*([^,;]+)", value)
    if m:
        out["score_key"] = m.group(1).strip()

    return out


def date_swap(a: str, b: str) -> bool:
    """
    Detect likely MM/DD transposition for complete ISO dates.
    Example:
      1938-07-03 vs 1938-03-07 -> True
    """
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", a or ""):
        return False
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", b or ""):
        return False

    ya, ma, da = map(int, a.split("-"))
    yb, mb, db = map(int, b.split("-"))

    return ya == yb and ma == db and da == mb and 1 <= mb <= 12 and 1 <= db <= 31


def normalize_title(value: str) -> str:
    value = value.strip()
    # Keep the source spelling in title; this is only for flags.
    return re.sub(r"\s+", " ", value)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("metadata_csv", type=Path)
    parser.add_argument("authentication_csv", type=Path)
    parser.add_argument("output_csv", type=Path)
    parser.add_argument("validation_csv", type=Path)
    args = parser.parse_args()

    with args.metadata_csv.open("r", encoding="utf-8-sig", newline="") as f:
        metadata = list(csv.DictReader(f))

    with args.authentication_csv.open("r", encoding="utf-8-sig", newline="") as f:
        auth = list(csv.DictReader(f))

    auth_by_case = {r.get("test_case", ""): r for r in auth}

    records = []
    validation = []

    for meta in metadata:
        case = meta.get("test_case", "")
        ref = auth_by_case.get(case, {})

        title = tag(meta, "TITLE")
        artist_raw = tag(meta, "ARTIST")
        album_artist = tag(meta, "album_artist")
        album = tag(meta, "ALBUM")
        genre = tag(meta, "GENRE")
        recording_date = tag(meta, "DATE")
        composer_raw = tag(meta, "COMPOSER")
        conductor = tag(meta, "CONDUCTOR")
        catalog_raw = tag(meta, "CATALOGNUMBER")
        source_media = tag(meta, "SOURCEMEDIA")
        track = tag(meta, "track")
        comment_raw = tag(meta, "COMMENT")

        ensemble_from_artist, performer_text, performance_note = split_artist(artist_raw)
        ensemble = album_artist or ensemble_from_artist

        composer_text, lyricist_text, other_credit = split_composer(composer_raw)
        record_number, matrix_number, take_number, catalog_evidence = split_catalog(catalog_raw)
        comment = parse_comment(comment_raw)

        ref_title = ref.get("reference_title", "")
        ref_date = ref.get("reference_date", "")
        ref_genre = ref.get("reference_genre", "")
        ref_album = ref.get("reference_album", "")
        ref_artist = ref.get("reference_artist", "")
        ref_catalog = ref.get("reference_catalog_number", "")

        auth_status = ref.get("status", "NO_AUTH_RECORD")

        flags = []

        if auth_status == "NO_MATCH":
            flags.append("NO_REFERENCE_MATCH")
        elif auth_status == "AMBIGUOUS":
            flags.append("AMBIGUOUS_REFERENCE")

        if ref_title and normalize_title(title).casefold() != normalize_title(ref_title).casefold():
            flags.append("TITLE_DIFFERS")

        if recording_date and ref_date and recording_date != ref_date:
            if date_swap(recording_date, ref_date):
                flags.append("DATE_TRANSPOSITION_SUSPECTED")
            else:
                flags.append("DATE_CONFLICT")

        if ref_genre and genre and genre.casefold() != ref_genre.casefold():
            flags.append("GENRE_CONFLICT")

        if ref_album and album and album.casefold() != ref_album.casefold():
            flags.append("ALBUM_REPRESENTATION_DIFF")

        # These are expected representation differences, not authentication
        # failures, so record them as such.
        if artist_raw and ref_artist:
            flags.append("ARTIST_REPRESENTATION_DIFF")

        if catalog_raw and ref_catalog:
            flags.append("CATALOG_REPRESENTATION_DIFF")

        record = {
            "test_case": case,
            "source_file": meta.get("source_file", ""),
            "source_release_directory": meta.get("release", ""),
            "source_filename": meta.get("filename", ""),
            "tango_dj_ref": ref.get("tango_dj_ref", ""),
            "authentication_status": auth_status,
            "authentication_flags": ";".join(flags),
            "title": title,
            "ensemble": ensemble,
            "ensemble_type": "",
            "performer_text": performer_text,
            "performance_note": performance_note,
            "singer_text": "" if performer_text.casefold() in {"", "instr."} else performer_text,
            "instrumental": "YES" if "instr." in performer_text.casefold() else "NO",
            "recording_date": recording_date,
            "genre": genre,
            "composer": composer_text,
            "lyricist": lyricist_text,
            "other_composer_credit": other_credit,
            "conductor": conductor,
            "record_number": record_number,
            "matrix_number": matrix_number,
            "take_number": take_number,
            "source_media": source_media,
            "release": album,
            "release_track_number": track,
            "pitch_hz": comment["pitch_hz"],
            "key": comment["key"],
            "score_key": comment["score_key"],
            "source_comment": comment_raw,
            "source_catalog_evidence": catalog_evidence,
            "reference_title": ref_title,
            "reference_artist": ref_artist,
            "reference_date": ref_date,
            "reference_catalog_number": ref_catalog,
        }

        records.append(record)

        validation.append({
            "test_case": case,
            "title": title,
            "tango_dj_ref": ref.get("tango_dj_ref", ""),
            "authentication_status": auth_status,
            "authentication_flags": ";".join(flags),
            "source_date": recording_date,
            "reference_date": ref_date,
            "date_rule": (
                "TRANSPOSITION_SUSPECTED"
                if "DATE_TRANSPOSITION_SUSPECTED" in flags
                else "NO_DATE_DISCREPANCY"
                if recording_date == ref_date
                else "OTHER_DATE_CASE"
            ),
        })

    output_fields = list(records[0].keys()) if records else []
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.output_csv.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=output_fields)
        w.writeheader()
        w.writerows(records)

    validation_fields = list(validation[0].keys()) if validation else []
    with args.validation_csv.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=validation_fields)
        w.writeheader()
        w.writerows(validation)

    print(f"TTT source records: {len(records)}")
    print(
        "Authenticated:",
        sum(r["authentication_status"] == "MATCHED" for r in records),
    )
    print(
        "No reference match:",
        sum(r["authentication_status"] == "NO_MATCH" for r in records),
    )
    print(
        "Date transposition suspected:",
        sum("DATE_TRANSPOSITION_SUSPECTED" in r["authentication_flags"] for r in records),
    )
    print(f"Canonical staging CSV: {args.output_csv}")
    print(f"Validation CSV: {args.validation_csv}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
