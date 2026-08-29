#!/usr/bin/env python3
"""
MusicStewardship Ingest Processing Ledger

A small SQLite-backed operational ledger for resumable ingestion.

Design:
  - lifecycle state = current business/process state
  - processing step = an operation being performed
  - processing log = immutable history of operations
  - asset identity is independent of path/name/representation

The ledger is intentionally independent of the eventual MusicStewardship
catalog schema. It can be used now and later integrated into the database.

Commands:
  init DB
  status DB [--asset ASSET_ID]
  begin DB ASSET_ID STEP [--source PATH] [--tool TOOL] [--version VERSION]
  complete DB ASSET_ID STEP
  fail DB ASSET_ID STEP ERROR [--message TEXT]
  note DB ASSET_ID TEXT
  resume DB ASSET_ID
  list DB [--state STATE] [--limit N]

A successful step is recorded only once per attempt. Re-running a completed
step is allowed only when explicitly desired by the caller; the ledger does
not silently rewrite history.
"""

from __future__ import annotations

import argparse
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


SCHEMA = """
PRAGMA foreign_keys = ON;

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


def ensure_asset(
    conn: sqlite3.Connection,
    asset_id: str,
    source: str = "",
    source_path: str = "",
    recording_id: str = "",
) -> None:
    t = now()
    conn.execute(
        """
        INSERT INTO assets (
            asset_id, recording_id, source, source_path,
            current_state, status, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, 'RECEIVED', 'PENDING', ?, ?)
        ON CONFLICT(asset_id) DO NOTHING
        """,
        (asset_id, recording_id, source, source_path, t, t),
    )


def write_human_ledger(conn: sqlite3.Connection, output: Path) -> None:
    """Write a human-readable summary plus detailed audit ledger."""
    assets = conn.execute(
        """
        SELECT asset_id, recording_id, source, source_path,
               current_state, current_step, status,
               created_at, updated_at, next_action, notes
        FROM assets
        ORDER BY updated_at DESC, asset_id
        """
    ).fetchall()

    def count_status(value):
        return sum(1 for a in assets if a["status"] == value)

    state_counts = {}
    for a in assets:
        state = a["current_state"] or "(none)"
        state_counts[state] = state_counts.get(state, 0) + 1

    next_counts = {}
    for a in assets:
        action = a["next_action"] or "(none)"
        next_counts[action] = next_counts.get(action, 0) + 1

    failed_events = conn.execute(
        "SELECT COUNT(*) AS n FROM processing_events WHERE result='FAILED'"
    ).fetchone()["n"]

    open_events = conn.execute(
        "SELECT COUNT(*) AS n FROM processing_events WHERE result='STARTED'"
    ).fetchone()["n"]

    noted_assets = sum(1 for a in assets if a["notes"])

    lines = [
        "# MusicStewardship Ingest Processing Ledger",
        "",
        f"_Generated: {now()}_",
        "",
        "## Overall Summary",
        "",
        "| Measure | Count |",
        "|---|---:|",
        f"| Assets | {len(assets)} |",
        f"| Pending | {count_status('PENDING')} |",
        f"| Running | {count_status('RUNNING')} |",
        f"| Complete | {count_status('COMPLETE')} |",
        f"| Failed | {count_status('FAILED')} |",
        "",
        "## Current Lifecycle",
        "",
        "| State | Count |",
        "|---|---:|",
    ]

    preferred_states = (
        "RECEIVED",
        "SCREENED",
        "IDENTIFIED",
        "TRANSLATED",
        "RECONCILED",
        "CATALOGED",
        "READY_FOR_MATERIALIZATION",
        "MATERIALIZED",
        "PUBLISHED_TO_DJ",
        "MAINTAINED",
        "ARCHIVED",
        "SUPERSEDED",
    )

    for state in preferred_states:
        lines.append(f"| `{state}` | {state_counts.get(state, 0)} |")

    for state in sorted(set(state_counts) - set(preferred_states)):
        lines.append(f"| `{state}` | {state_counts[state]} |")

    lines.extend([
        "",
        "## Next Actions",
        "",
        "| Next action | Count |",
        "|---|---:|",
    ])

    for action, count in sorted(next_counts.items()):
        lines.append(f"| `{action}` | {count} |")

    lines.extend([
        "",
        "## Audit / Exceptions",
        "",
        "| Measure | Count |",
        "|---|---:|",
        f"| Assets with notes | {noted_assets} |",
        f"| Failed processing events | {failed_events} |",
        f"| Open processing events | {open_events} |",
        "",
        "## Asset Details",
        "",
    ])

    if not assets:
        lines.append("_No assets yet._")
    else:
        for a in assets:
            lines.extend([
                f"### `{a['asset_id']}`",
                "",
                f"- **Recording ID:** {a['recording_id'] or '—'}",
                f"- **Source:** {a['source'] or '—'}",
                f"- **Source path:** `{a['source_path'] or '—'}`",
                f"- **Current state:** `{a['current_state']}`",
                f"- **Status:** `{a['status']}`",
                f"- **Current step:** `{a['current_step'] or '—'}`",
                f"- **Next action:** `{a['next_action'] or '—'}`",
                f"- **Created:** {a['created_at']}",
                f"- **Updated:** {a['updated_at']}",
            ])

            if a["notes"]:
                lines.extend(["", "**Notes**", "", a["notes"]])

            lines.extend([
                "",
                "| # | Step | Attempt | Result | Tool | Started | Completed | Error |",
                "|---:|---|---:|---|---|---|---|---|",
            ])

            events = conn.execute(
                """
                SELECT event_id, step, attempt, result, tool, tool_version,
                       started_at, completed_at, error_code, error_message
                FROM processing_events
                WHERE asset_id=?
                ORDER BY event_id
                """,
                (a["asset_id"],),
            ).fetchall()

            for e in events:
                tool = e["tool"] or ""
                if e["tool_version"]:
                    tool = f"{tool} {e['tool_version']}".strip()

                error = ""
                if e["error_code"]:
                    error = e["error_code"]
                if e["error_message"]:
                    error += f": {e['error_message']}" if error else e["error_message"]
                error = error.replace("|", "\\|").replace("\n", " ")

                lines.append(
                    f"| {e['event_id']} | `{e['step']}` | {e['attempt']} | "
                    f"`{e['result']}` | `{tool}` | {e['started_at']} | "
                    f"{e['completed_at'] or ''} | {error} |"
                )

            lines.extend(["", "---", ""])

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")


def cmd_export(args):
    conn = connect(args.db)
    write_human_ledger(conn, args.output)
    print(f"Human-readable ledger: {args.output}")


def cmd_init(args):
    conn = connect(args.db)
    conn.close()
    print(f"Initialized ingest ledger: {args.db}")
    output = args.output or args.db.with_suffix(".md")
    conn = connect(args.db)
    write_human_ledger(conn, output)
    conn.close()
    print(f"Human-readable ledger: {output}")


def cmd_begin(args):
    conn = connect(args.db)
    ensure_asset(
        conn, args.asset_id, args.source, args.source_path, args.recording_id
    )

    row = conn.execute(
        "SELECT COALESCE(MAX(attempt), 0) AS n "
        "FROM processing_events WHERE asset_id=? AND step=?",
        (args.asset_id, args.step),
    ).fetchone()
    attempt = row["n"] + 1
    t = now()

    conn.execute(
        """
        INSERT INTO processing_events (
            asset_id, step, attempt, started_at, result,
            tool, tool_version, input_fingerprint, notes
        )
        VALUES (?, ?, ?, ?, 'STARTED', ?, ?, ?, ?)
        """,
        (
            args.asset_id,
            args.step,
            attempt,
            t,
            args.tool,
            args.version,
            args.input_fingerprint,
            args.notes,
        ),
    )

    conn.execute(
        """
        UPDATE assets
        SET current_step=?,
            status='RUNNING',
            updated_at=?,
            source=COALESCE(NULLIF(?, ''), source),
            source_path=COALESCE(NULLIF(?, ''), source_path),
            recording_id=COALESCE(NULLIF(?, ''), recording_id)
        WHERE asset_id=?
        """,
        (
            args.step,
            t,
            args.source,
            args.source_path,
            args.recording_id,
            args.asset_id,
        ),
    )
    conn.commit()
    write_human_ledger(conn, args.db.with_suffix(".md"))
    print(f"STARTED {args.asset_id}: {args.step} (attempt {attempt})")


def cmd_complete(args):
    conn = connect(args.db)
    row = conn.execute(
        """
        SELECT event_id, attempt
        FROM processing_events
        WHERE asset_id=? AND step=? AND result='STARTED'
        ORDER BY event_id DESC
        LIMIT 1
        """,
        (args.asset_id, args.step),
    ).fetchone()

    if not row:
        raise SystemExit(
            f"No STARTED event found for {args.asset_id} / {args.step}"
        )

    t = now()
    conn.execute(
        """
        UPDATE processing_events
        SET completed_at=?,
            result='SUCCESS',
            output_fingerprint=?,
            notes=COALESCE(NULLIF(?, ''), notes)
        WHERE event_id=?
        """,
        (t, args.output_fingerprint, args.notes, row["event_id"]),
    )
    conn.execute(
        """
        UPDATE assets
        SET current_step=?,
            status='COMPLETE',
            updated_at=?,
            current_state=COALESCE(NULLIF(?, ''), current_state),
            next_action=?
        WHERE asset_id=?
        """,
        (
            args.step,
            t,
            args.state,
            args.next_action,
            args.asset_id,
        ),
    )
    conn.commit()
    write_human_ledger(conn, args.db.with_suffix(".md"))
    print(f"COMPLETE {args.asset_id}: {args.step}")


def cmd_fail(args):
    conn = connect(args.db)
    row = conn.execute(
        """
        SELECT event_id
        FROM processing_events
        WHERE asset_id=? AND step=? AND result='STARTED'
        ORDER BY event_id DESC
        LIMIT 1
        """,
        (args.asset_id, args.step),
    ).fetchone()

    if not row:
        raise SystemExit(
            f"No STARTED event found for {args.asset_id} / {args.step}"
        )

    t = now()
    conn.execute(
        """
        UPDATE processing_events
        SET completed_at=?,
            result='FAILED',
            error_code=?,
            error_message=?,
            notes=COALESCE(NULLIF(?, ''), notes)
        WHERE event_id=?
        """,
        (
            t,
            args.error,
            args.message,
            args.notes,
            row["event_id"],
        ),
    )
    conn.execute(
        """
        UPDATE assets
        SET status='FAILED',
            updated_at=?,
            next_action=?
        WHERE asset_id=?
        """,
        (t, args.next_action, args.asset_id),
    )
    conn.commit()
    write_human_ledger(conn, args.db.with_suffix(".md"))
    print(f"FAILED {args.asset_id}: {args.step} [{args.error}]")


def cmd_note(args):
    conn = connect(args.db)
    ensure_asset(conn, args.asset_id)
    t = now()
    conn.execute(
        """
        UPDATE assets
        SET notes = CASE
            WHEN notes IS NULL OR notes='' THEN ?
            ELSE notes || char(10) || ?
        END,
        updated_at=?
        WHERE asset_id=?
        """,
        (f"{t} {args.text}", f"{t} {args.text}", t, args.asset_id),
    )
    conn.commit()
    write_human_ledger(conn, args.db.with_suffix(".md"))
    print(f"NOTE {args.asset_id}: {args.text}")


def latest_events(conn, asset_id: str):
    return conn.execute(
        """
        SELECT *
        FROM processing_events
        WHERE asset_id=?
        ORDER BY event_id
        """,
        (asset_id,),
    ).fetchall()


def cmd_status(args):
    conn = connect(args.db)

    if getattr(args, "asset", None):
        asset_id = args.asset
        asset = conn.execute(
            "SELECT * FROM assets WHERE asset_id=?", (asset_id,)
        ).fetchone()
        if not asset:
            raise SystemExit(f"Unknown asset: {asset_id}")

        print(f"asset_id:      {asset['asset_id']}")
        print(f"recording_id:  {asset['recording_id'] or ''}")
        print(f"source:        {asset['source'] or ''}")
        print(f"source_path:   {asset['source_path'] or ''}")
        print(f"state:         {asset['current_state']}")
        print(f"step:          {asset['current_step'] or ''}")
        print(f"status:        {asset['status']}")
        print(f"next_action:   {asset['next_action'] or ''}")
        print(f"updated_at:    {asset['updated_at']}")
        print()
        print("Processing history:")

        for e in latest_events(conn, asset_id):
            detail = e["error_code"] or ""
            print(
                f"  {e['event_id']:4d} "
                f"{e['step']:<24} "
                f"attempt={e['attempt']} "
                f"{e['result']:<7} "
                f"{detail}"
            )
        return

    rows = conn.execute(
        """
        SELECT asset_id, recording_id, current_state, current_step,
               status, updated_at, next_action
        FROM assets
        ORDER BY updated_at DESC
        """
    ).fetchall()

    if not rows:
        print("No assets in ledger.")
        return

    print(
        f"{'asset_id':<28} {'state':<24} {'status':<10} "
        f"{'current_step':<24} {'updated_at'}"
    )
    for row in rows:
        print(
            f"{row['asset_id']:<28} "
            f"{row['current_state']:<24} "
            f"{row['status']:<10} "
            f"{(row['current_step'] or ''):<24} "
            f"{row['updated_at']}"
        )


def cmd_resume(args):
    conn = connect(args.db)
    asset = conn.execute(
        "SELECT * FROM assets WHERE asset_id=?", (args.asset_id,)
    ).fetchone()

    if not asset:
        raise SystemExit(f"Unknown asset: {args.asset_id}")

    event = conn.execute(
        """
        SELECT *
        FROM processing_events
        WHERE asset_id=?
        ORDER BY event_id DESC
        LIMIT 1
        """,
        (args.asset_id,),
    ).fetchone()

    print(f"Asset:       {asset['asset_id']}")
    print(f"State:       {asset['current_state']}")
    print(f"Status:      {asset['status']}")
    print(f"Last step:   {asset['current_step'] or ''}")
    print(f"Next action: {asset['next_action'] or ''}")

    if event:
        print(
            f"Last event:  {event['step']} / {event['result']} "
            f"(attempt {event['attempt']})"
        )

    if asset["status"] == "FAILED":
        print("Resume guidance: retry the failed step after addressing its error.")
    elif asset["status"] == "RUNNING":
        print("Resume guidance: inspect the running step; do not assume it failed.")
    elif asset["status"] == "COMPLETE":
        print("Resume guidance: begin the next_action step when ready.")
    else:
        print("Resume guidance: begin the next required step.")


def cmd_list(args):
    conn = connect(args.db)
    params = []
    where = ""

    if args.state:
        where = "WHERE current_state=?"
        params.append(args.state)

    rows = conn.execute(
        f"""
        SELECT asset_id, recording_id, source, current_state,
               current_step, status, next_action, updated_at
        FROM assets
        {where}
        ORDER BY updated_at DESC
        LIMIT ?
        """,
        (*params, args.limit),
    ).fetchall()

    for row in rows:
        print(
            f"{row['asset_id']}\t"
            f"{row['current_state']}\t"
            f"{row['status']}\t"
            f"{row['current_step'] or ''}\t"
            f"{row['next_action'] or ''}"
        )


def build_parser():
    p = argparse.ArgumentParser(
        description="MusicStewardship resumable ingest processing ledger"
    )
    sub = p.add_subparsers(dest="command", required=True)

    x = sub.add_parser("init")
    x.add_argument("db", type=Path)
    x.add_argument("--output", type=Path)
    x.set_defaults(func=cmd_init)

    x = sub.add_parser("export")
    x.add_argument("db", type=Path)
    x.add_argument("output", type=Path)
    x.set_defaults(func=cmd_export)

    x = sub.add_parser("begin")
    x.add_argument("db", type=Path)
    x.add_argument("asset_id")
    x.add_argument("step")
    x.add_argument("--recording-id", default="")
    x.add_argument("--source", default="")
    x.add_argument("--source-path", default="")
    x.add_argument("--tool", default="")
    x.add_argument("--version", default="")
    x.add_argument("--input-fingerprint", default="")
    x.add_argument("--notes", default="")
    x.set_defaults(func=cmd_begin)

    x = sub.add_parser("complete")
    x.add_argument("db", type=Path)
    x.add_argument("asset_id")
    x.add_argument("step")
    x.add_argument("--state", default="")
    x.add_argument("--next-action", default="")
    x.add_argument("--output-fingerprint", default="")
    x.add_argument("--notes", default="")
    x.set_defaults(func=cmd_complete)

    x = sub.add_parser("fail")
    x.add_argument("db", type=Path)
    x.add_argument("asset_id")
    x.add_argument("step")
    x.add_argument("error")
    x.add_argument("--message", default="")
    x.add_argument("--next-action", default="")
    x.add_argument("--notes", default="")
    x.set_defaults(func=cmd_fail)

    x = sub.add_parser("note")
    x.add_argument("db", type=Path)
    x.add_argument("asset_id")
    x.add_argument("text")
    x.set_defaults(func=cmd_note)

    x = sub.add_parser("status")
    x.add_argument("db", type=Path)
    x.add_argument("--asset", dest="asset")
    x.set_defaults(func=cmd_status)

    x = sub.add_parser("resume")
    x.add_argument("db", type=Path)
    x.add_argument("asset_id")
    x.set_defaults(func=cmd_resume)

    x = sub.add_parser("list")
    x.add_argument("db", type=Path)
    x.add_argument("--state")
    x.add_argument("--limit", type=int, default=100)
    x.set_defaults(func=cmd_list)

    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
