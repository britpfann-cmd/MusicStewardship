#!/usr/bin/env python3
"""
MusicStewardship TTT ingest runner with resumable ledger integration.

This runner currently performs the operational workflow on a TTT release tree:
    DISCOVER -> PROBE -> SCREEN -> TRANSLATE -> REFERENCE_CHECK -> RECONCILE

It does NOT modify source audio.

The ledger records one asset per source file and creates a processing event
for each step. Existing successful steps are skipped, allowing safe resumption.

Current implementation:
  - PROBE: ffprobe must successfully read the file.
  - SCREEN: required TTT identity tags are checked.
  - TRANSLATE: invokes the existing TTT canonical staging translator by
    reproducing its decomposition logic for this operational runner.
  - REFERENCE_CHECK: checks whether the source has at least one TANGO-DJ
    reference candidate by record, matrix, title/date, or release/track.
  - RECONCILE: currently records that source-derived values remain primary and
    external reference information is retained as annotation. No source
    values are overwritten.

The generated CSV is a staging/output report, not the permanent database.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sqlite3
import subprocess
from datetime import datetime, timezone
from pathlib import Path


AUDIO_EXTENSIONS = {".flac", ".wav", ".mp3", ".m4a", ".alac"}
REQUIRED_TAGS = ("TITLE", "ARTIST", "ALBUM", "GENRE", "DATE", "track")


SCHEMA = """
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS assets (
    asset_id TEXT PRIMARY KEY,
    recording_id TEXT,
    source TEXT,
    source_path TEXT,
    current_state TEXT NOT NULL DEFAULT 'RECEIVED',
    current_step TEXT,
    status TEXT NOT NULL DEFAULT 'PENDING',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    next_action TEXT,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS processing_events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id TEXT NOT NULL,
    step TEXT NOT NULL,
    attempt INTEGER NOT NULL,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    result TEXT NOT NULL DEFAULT 'STARTED',
    tool TEXT,
    tool_version TEXT,
    input_fingerprint TEXT,
    output_fingerprint TEXT,
    error_code TEXT,
    error_message TEXT,
    notes TEXT,
    FOREIGN KEY(asset_id) REFERENCES assets(asset_id)
);

CREATE INDEX IF NOT EXISTS idx_processing_events_asset
    ON processing_events(asset_id, event_id);

CREATE INDEX IF NOT EXISTS idx_assets_state
    ON assets(current_state, status);
"""


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def connect(db: Path) -> sqlite3.Connection:
    db.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def file_asset_id(path: Path, root: Path) -> str:
    rel = path.relative_to(root).as_posix()
    digest = hashlib.sha1(rel.encode("utf-8")).hexdigest()[:12]
    return f"TTT-{digest}"


def ffprobe(path: Path) -> dict:
    cmd = [
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
        cmd, capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "ffprobe failed")
    return json.loads(result.stdout)


def extract_tags(probe: dict) -> dict[str, str]:
    raw = (probe.get("format", {}).get("tags") or {})
    tags = {str(k).casefold(): str(v).strip() for k, v in raw.items()}
    return {
        "TITLE": tags.get("title", ""),
        "ARTIST": tags.get("artist", ""),
        "ALBUM": tags.get("album", ""),
        "GENRE": tags.get("genre", ""),
        "DATE": tags.get("date", ""),
        "track": tags.get("track", ""),
        "COMPOSER": tags.get("composer", ""),
        "CONDUCTOR": tags.get("conductor", ""),
        "CATALOGNUMBER": tags.get("catalognumber", ""),
        "SOURCEMEDIA": tags.get("sourcemedia", ""),
        "COMMENT": tags.get("comment", ""),
        "album_artist": tags.get("album_artist", ""),
    }


def normalize(value: str) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", value.strip()).casefold()


def compact(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", normalize(value))


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


def load_reference(path: Path) -> list[dict[str, str]]:
    if not path:
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def reference_candidates(meta: dict[str, str], reference):
    if not reference:
        return [], "NO_REFERENCE_DATA"

    record, matrix, take = parse_catalog(meta["CATALOGNUMBER"])
    record_key = compact(record)
    matrix_key = compact(matrix)
    title = normalize(meta["TITLE"])
    date = normalize(meta["DATE"])
    album = normalize(meta["ALBUM"])
    track = normalize(meta["track"])

    hits = []
    method = "NO_MATCH"

    for row in reference:
        ref_catalogs = [
            compact(x) for x in
            re.split(r"\s*/\s*", row.get("catalog_number", ""))
            if x.strip()
        ]
        ref_record = next(iter(ref_catalogs), "")
        ref_matrix = compact(row.get("matrix_number", ""))
        ref_title = normalize(row.get("title", ""))
        ref_date = normalize(row.get("recording_date", ""))
        ref_album = normalize(row.get("album", ""))
        ref_track = normalize(row.get("track_number", ""))

        strong = False

        if record_key and matrix_key:
            if record_key in ref_catalogs and matrix_key in ref_matrix:
                strong = True
                method = "RECORD_MATRIX"
        elif record_key and record_key in ref_catalogs:
            strong = True
            method = "RECORD"
        elif title and date and ref_title == title and ref_date == date:
            strong = True
            method = "TITLE_DATE"
        elif album and track and ref_album == album and ref_track == track:
            strong = True
            method = "RELEASE_TRACK"

        if strong:
            hits.append(row)

    return hits, method if hits else "NO_MATCH"


def event_exists(conn, asset_id: str, step: str, result: str = "SUCCESS") -> bool:
    row = conn.execute(
        """
        SELECT 1 FROM processing_events
        WHERE asset_id=? AND step=? AND result=?
        LIMIT 1
        """,
        (asset_id, step, result),
    ).fetchone()
    return row is not None


def begin_event(conn, asset_id: str, step: str, tool: str, version: str = "",
                input_fingerprint: str = "", notes: str = "") -> int:
    row = conn.execute(
        """
        SELECT COALESCE(MAX(attempt),0)+1 AS next_attempt
        FROM processing_events
        WHERE asset_id=? AND step=?
        """,
        (asset_id, step),
    ).fetchone()
    attempt = row["next_attempt"]
    t = now()
    conn.execute(
        """
        INSERT INTO processing_events
        (asset_id, step, attempt, started_at, result, tool, tool_version,
         input_fingerprint, notes)
        VALUES (?, ?, ?, ?, 'STARTED', ?, ?, ?, ?)
        """,
        (
            asset_id, step, attempt, t, tool, version,
            input_fingerprint, notes,
        ),
    )
    conn.execute(
        """
        UPDATE assets
        SET current_step=?, status='RUNNING', updated_at=?
        WHERE asset_id=?
        """,
        (step, t, asset_id),
    )
    conn.commit()
    return conn.execute("SELECT last_insert_rowid()").fetchone()[0]


def complete_event(conn, event_id: int, asset_id: str, step: str,
                   state: str, next_action: str,
                   output_fingerprint: str = "", notes: str = "") -> None:
    t = now()
    conn.execute(
        """
        UPDATE processing_events
        SET completed_at=?, result='SUCCESS', output_fingerprint=?,
            notes=COALESCE(NULLIF(?, ''), notes)
        WHERE event_id=?
        """,
        (t, output_fingerprint, notes, event_id),
    )
    conn.execute(
        """
        UPDATE assets
        SET current_step=?, current_state=?, status='COMPLETE',
            updated_at=?, next_action=?
        WHERE asset_id=?
        """,
        (step, state, t, next_action, asset_id),
    )
    conn.commit()


def fail_event(conn, event_id: int, asset_id: str, step: str,
               error_code: str, message: str) -> None:
    t = now()
    conn.execute(
        """
        UPDATE processing_events
        SET completed_at=?, result='FAILED',
            error_code=?, error_message=?
        WHERE event_id=?
        """,
        (t, error_code, message, event_id),
    )
    conn.execute(
        """
        UPDATE assets
        SET current_step=?, status='FAILED', updated_at=?
        WHERE asset_id=?
        """,
        (step, t, asset_id),
    )
    conn.commit()


def ensure_asset(conn, asset_id: str, source: str, source_path: str) -> None:
    t = now()
    conn.execute(
        """
        INSERT INTO assets
        (asset_id, source, source_path, current_state, status,
         created_at, updated_at)
        VALUES (?, ?, ?, 'RECEIVED', 'PENDING', ?, ?)
        ON CONFLICT(asset_id) DO UPDATE SET
            source_path=excluded.source_path,
            updated_at=excluded.updated_at
        """,
        (asset_id, source, source_path, t, t),
    )
    conn.commit()


def process_file(
    conn: sqlite3.Connection,
    path: Path,
    root: Path,
    reference: list[dict[str, str]],
    tool_version: str,
) -> dict[str, str]:

    asset_id = file_asset_id(path, root)
    ensure_asset(conn, asset_id, "TangoTimeTravel", str(path))

    row = {
        "asset_id": asset_id,
        "source_file": str(path),
        "source_filename": path.name,
        "state": "",
        "status": "",
        "title": "",
        "artist": "",
        "album": "",
        "genre": "",
        "date": "",
        "track": "",
        "record_number": "",
        "matrix_number": "",
        "take_number": "",
        "reference_status": "",
        "reference_candidates": "",
        "next_action": "",
        "error": "",
    }

    # PROBE
    probe = None
    if event_exists(conn, asset_id, "PROBE"):
        probe = ffprobe(path)
    else:
        event = begin_event(
            conn, asset_id, "PROBE", "ffprobe", tool_version
        )
        try:
            probe = ffprobe(path)
            complete_event(
                conn, event, asset_id, "PROBE",
                "SCREENED", "SCREEN",
            )
        except Exception as exc:
            fail_event(
                conn, event, asset_id, "PROBE",
                "PROBE_ERROR", str(exc),
            )
            row.update(status="FAILED", state="RECEIVED", error=str(exc))
            return row

    tags = extract_tags(probe)
    row.update(
        title=tags["TITLE"],
        artist=tags["ARTIST"],
        album=tags["ALBUM"],
        genre=tags["GENRE"],
        date=tags["DATE"],
        track=tags["track"],
    )

    # SCREEN
    missing = [k for k in REQUIRED_TAGS if not tags[k]]
    if event_exists(conn, asset_id, "SCREEN"):
        pass
    else:
        event = begin_event(
            conn, asset_id, "SCREEN", "validate_ttt_tree", tool_version
        )
        if missing:
            fail_event(
                conn, event, asset_id, "SCREEN",
                "MISSING_TTT_METADATA",
                "Missing required tags: " + ", ".join(missing),
            )
            row.update(
                status="FAILED",
                state="RECEIVED",
                error="Missing required tags: " + ", ".join(missing),
            )
            return row
        complete_event(
            conn, event, asset_id, "SCREEN", "SCREENED", "TRANSLATE"
        )

    record, matrix, take = parse_catalog(tags["CATALOGNUMBER"])
    row.update(
        record_number=record,
        matrix_number=matrix,
        take_number=take,
    )

    # TRANSLATE
    if not event_exists(conn, asset_id, "TRANSLATE"):
        event = begin_event(
            conn, asset_id, "TRANSLATE",
            "build_ttt_canonical_staging.py", tool_version,
        )
        translated = {
            "title": tags["TITLE"],
            "ensemble": tags["album_artist"] or split_artist(tags["ARTIST"])[0],
            "artist": tags["ARTIST"],
            "genre": tags["GENRE"],
            "date": tags["DATE"],
            "composer": tags["COMPOSER"],
            "conductor": tags["CONDUCTOR"],
            "source_media": tags["SOURCEMEDIA"],
        }
        output_fingerprint = hashlib.sha256(
            json.dumps(translated, sort_keys=True, ensure_ascii=False).encode()
        ).hexdigest()
        complete_event(
            conn, event, asset_id, "TRANSLATE",
            "TRANSLATED", "REFERENCE_CHECK",
            output_fingerprint=output_fingerprint,
        )

    # REFERENCE_CHECK
    hits, method = reference_candidates(tags, reference)
    if not event_exists(conn, asset_id, "REFERENCE_CHECK"):
        event = begin_event(
            conn, asset_id, "REFERENCE_CHECK",
            "reference_candidate_check", tool_version,
        )
        note = f"{len(hits)} reference candidate(s); method={method}"
        complete_event(
            conn, event, asset_id, "REFERENCE_CHECK",
            "REFERENCE_CHECKED", "RECONCILE",
            notes=note,
        )

    # RECONCILE
    if not event_exists(conn, asset_id, "RECONCILE"):
        event = begin_event(
            conn, asset_id, "RECONCILE",
            "ttt_source_precedence", tool_version,
        )
        if hits:
            note = (
                f"Source values remain primary. "
                f"{len(hits)} TANGO-DJ reference row(s) retained for comparison."
            )
            next_action = "CATALOG"
        else:
            note = (
                "No TANGO-DJ candidate. Source values remain primary; "
                "reference gap retained for follow-up."
            )
            next_action = "CATALOG"
        complete_event(
            conn, event, asset_id, "RECONCILE",
            "RECONCILED", next_action,
            notes=note,
        )

    row.update(
        state="RECONCILED",
        status="COMPLETE",
        reference_status=(
            "REFERENCE_CANDIDATE" if hits else "NO_REFERENCE_CANDIDATE"
        ),
        reference_candidates=str(len(hits)),
        next_action="CATALOG",
    )
    return row


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("ttt_root", type=Path)
    parser.add_argument("ledger_db", type=Path)
    parser.add_argument("output_csv", type=Path)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    if not args.ttt_root.is_dir():
        parser.error(f"TTT root not found: {args.ttt_root}")
    if not args.reference.is_file():
        parser.error(f"Reference CSV not found: {args.reference}")

    reference = load_reference(args.reference)

    files = sorted(
        p for p in args.ttt_root.rglob("*")
        if p.is_file() and p.suffix.casefold() in AUDIO_EXTENSIONS
    )
    if args.limit:
        files = files[:args.limit]

    conn = connect(args.ledger_db)
    results = []

    for i, path in enumerate(files, 1):
        print(f"{i:04d} - {path}")
        results.append(
            process_file(conn, path, args.ttt_root, reference, "1.0")
        )

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.output_csv.open(
        "w", encoding="utf-8-sig", newline=""
    ) as f:
        fields = list(results[0].keys()) if results else ["asset_id"]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)

    print()
    print(f"Files processed: {len(results)}")
    print(
        "Complete:",
        sum(r.get("status") == "COMPLETE" for r in results),
    )
    print(
        "Failed:",
        sum(r.get("status") == "FAILED" for r in results),
    )
    print(f"Ledger: {args.ledger_db}")
    print(f"Report: {args.output_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
