#!/usr/bin/env python3
"""
Build a first common catalog from reconciled source evidence.

V1 test:
- Builds Person, Group, Song, Performance, CatalogedInstance, Asset.
- Uses deterministic IDs.
- Preserves source evidence.
- Treats dates as values with explicit precision/status.
- Does not reject unresolved information.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path


def read_csv(path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def stable_id(prefix, *values):
    text = "|".join("" if v is None else str(v).strip() for v in values)
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}-{digest}"


def date_precision(value):
    value = (value or "").strip()

    if len(value) == 4 and value.isdigit():
        return "YEAR"

    if len(value) == 7 and value[4] == "-":
        return "MONTH"

    if len(value) == 10 and value[4] == "-" and value[7] == "-":
        return "DAY"

    if value:
        return "UNSPECIFIED"

    return "NONE"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path)
    ap.add_argument("--output-dir", required=True, type=Path)
    args = ap.parse_args()

    rows = read_csv(args.input)

    people = {}
    groups = {}
    songs = {}
    performances = {}
    instances = {}
    assets = {}

    for r in rows:
        title = (r.get("title") or "").strip()
        ensemble = (r.get("ensemble") or "").strip()
        date = (r.get("recording_date") or "").strip()

        if not title or not ensemble:
            continue

        group_id = stable_id("GRP", ensemble)
        song_id = stable_id("SONG", title)

        groups[group_id] = {
            "group_id": group_id,
            "name": ensemble,
        }

        songs[song_id] = {
            "song_id": song_id,
            "title": title,
        }

        performance_key = (song_id, group_id, date)

        if performance_key not in performances:
            performance_id = stable_id(
                "PERF",
                song_id,
                group_id,
                date,
            )

            performances[performance_key] = {
                "performance_id": performance_id,
                "song_id": song_id,
                "group_id": group_id,
                "recording_date": date,
                "date_precision": date_precision(date),
                "date_status": (
                    "PROVISIONAL"
                    if date_precision(date) != "DAY"
                    else "SOURCE_SUPPORTED"
                ),
                "identity_status": (
                    r.get("authentication_status") or "UNRESOLVED"
                ),
            }

        p = performances[performance_key]

        instance_id = stable_id(
            "INST",
            r.get("source") or "TangoTimeTravel",
            r.get("source_identifier"),
        )

        instances[instance_id] = {
            "instance_id": instance_id,
            "performance_id": p["performance_id"],
            "source": r.get("source", ""),
            "source_identifier": r.get("source_identifier", ""),
            "record_number": r.get("record_number", ""),
            "matrix_number": r.get("matrix_number", ""),
            "take_number": r.get("take_number", ""),
            "source_media": r.get("source_media", ""),
            "source_release": r.get("source_release", ""),
            "source_reference": r.get("source_reference", ""),
            "external_reference": r.get("external_reference", ""),
            "authentication_status": r.get("authentication_status", ""),
            "authentication_method": r.get("authentication_method", ""),
        }

        asset_id = stable_id(
            "ASSET",
            r.get("source") or "TangoTimeTravel",
            r.get("source_identifier"),
        )

        assets[asset_id] = {
            "asset_id": asset_id,
            "performance_id": p["performance_id"],
            "source": r.get("source", ""),
            "path": r.get("source_file", r.get("source_identifier", "")),
        }

    out = args.output_dir

    write_csv(
        out / "Group.csv",
        groups.values(),
        ["group_id", "name"],
    )

    write_csv(
        out / "Song.csv",
        songs.values(),
        ["song_id", "title"],
    )

    write_csv(
        out / "Performance.csv",
        performances.values(),
        [
            "performance_id",
            "song_id",
            "group_id",
            "recording_date",
            "date_precision",
            "date_status",
            "identity_status",
        ],
    )

    write_csv(
        out / "CatalogedInstance.csv",
        instances.values(),
        [
            "instance_id",
            "performance_id",
            "source",
            "source_identifier",
            "record_number",
            "matrix_number",
            "take_number",
            "source_media",
            "source_release",
            "source_reference",
            "external_reference",
            "authentication_status",
            "authentication_method",
        ],
    )

    write_csv(
        out / "Asset.csv",
        assets.values(),
        [
            "asset_id",
            "performance_id",
            "source",
            "path",
        ],
    )

    write_csv(
        out / "Person.csv",
        people.values(),
        ["person_id", "name"],
    )

    print(f"Input records: {len(rows)}")
    print(f"Groups: {len(groups)}")
    print(f"Songs: {len(songs)}")
    print(f"Performances: {len(performances)}")
    print(f"Cataloged instances: {len(instances)}")
    print(f"Assets: {len(assets)}")
    print(f"Output: {out}")


if __name__ == "__main__":
    main()
