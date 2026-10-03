"""MusicStewardship — D Name Ingestion.

Consumes the universal C Library Card CSV and harvests name-bearing
observations without canonicalization, deduplication, or entity resolution.

Output follows the established D2 observation interchange contract.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


NAME_FIELDS = (
    "title",
    "artist",
    "orchestra_or_album_artist",
    "singer",
    "composer",
    "conductor",
    "source_album",
)

REQUIRED_IDENTITY_FIELDS = (
    "source_object_id",
    "source_object_key",
    "source_record_revision",
)


def _decode_values(raw: str, field: str) -> list[Any]:
    if raw == "":
        return []

    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Library Card field {field!r} contains invalid JSON."
        ) from exc

    if not isinstance(value, list):
        raise ValueError(
            f"Library Card field {field!r} must contain a JSON array."
        )

    return value


def harvest_names(path: Path) -> list[dict[str, Any]]:
    """Harvest name observations from a universal Library Card CSV."""

    with path.open(
        "r",
        newline="",
        encoding="utf-8-sig",
    ) as fh:
        reader = csv.DictReader(fh)

        if not reader.fieldnames:
            raise ValueError("Library Card has no CSV header.")

        rows = list(reader)

    observations: list[dict[str, Any]] = []

    for row_number, card in enumerate(rows, start=2):
        for field in REQUIRED_IDENTITY_FIELDS:
            if not card.get(field, ""):
                raise ValueError(
                    f"Library Card row {row_number} is missing "
                    f"required identity field {field!r}."
                )

        for field in NAME_FIELDS:
            values = _decode_values(card.get(field, ""), field)

            for value in values:
                if not isinstance(value, str):
                    raise ValueError(
                        f"Library Card field {field!r} contains "
                        f"a non-string name value."
                    )

                context = {
                    "source_field": field,
                    "source_object_id": card["source_object_id"],
                    "source_object_key": card["source_object_key"],
                    "source_record_revision": card[
                        "source_record_revision"
                    ],
                }

                evidence = {
                    "harvester": "d_name_ingestion",
                    "source_record": dict(card),
                }

                observations.append(
                    {
                        "source": "",
                        "collection": "",
                        "collection_type": "library_card",
                        "source_record_id": card["source_object_id"],
                        "entity_type": "",
                        "observed_value": value,
                        "source_object_id": card["source_object_id"],
                        "source_record_revision": card["source_record_revision"],
                        "source_field": field,
                        "context_json": json.dumps(
                            context,
                            ensure_ascii=False,
                            separators=(",", ":"),
                        ),
                        "evidence_json": json.dumps(
                            evidence,
                            ensure_ascii=False,
                            separators=(",", ":"),
                        ),
                    }
                )

    return observations






