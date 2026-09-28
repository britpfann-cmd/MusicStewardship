"""MusicStewardship — D Name Ingestion contract test.

D Name Ingestion consumes public C Library Cards.

The test verifies that name-bearing Library Card values are:
* extracted without changing their observed spelling;
* tied to the originating Library Card;
* tied to the originating C field;
* preserved as separate observations, including duplicates;
* not canonicalized or deduplicated;
* not resolved into entities merely by harvesting.

Entity recognition and association are downstream concerns.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from d_name_ingestion import harvest_names


NAME_FIELDS = (
    "title",
    "artist",
    "orchestra_or_album_artist",
    "singer",
    "composer",
    "conductor",
    "source_album",
)


def write_card(path: Path) -> None:
    fields = [
        "source_object_id",
        "source_object_key",
        "source_record_revision",
        *NAME_FIELDS,
    ]

    row = {
        "source_object_id": "TTT::asset-001",
        "source_object_key": "asset-001",
        "source_record_revision": "C.revA",
        "title": json.dumps(["A Media Luz"]),
        "artist": json.dumps(["Carlos Gardel"]),
        "orchestra_or_album_artist": json.dumps(["Orquesta Típica"]),
        "singer": json.dumps(["Carlos Gardel"]),
        "composer": json.dumps(["Carlos Gardel"]),
        "conductor": json.dumps([]),
        "source_album": json.dumps(["TTT Collection 01"]),
    }

    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerow(row)


def test_harvests_name_bearing_library_card_fields(tmp_path: Path) -> None:
    card = tmp_path / "Library_Cards_RevA.csv"
    write_card(card)

    observations = harvest_names(card)

    assert len(observations) == 6

    observed = {
        (item["source_object_id"], item["source_field"], item["observed_value"])
        for item in observations
    }

    assert ("TTT::asset-001", "title", "A Media Luz") in observed
    assert ("TTT::asset-001", "artist", "Carlos Gardel") in observed
    assert (
        "TTT::asset-001",
        "orchestra_or_album_artist",
        "Orquesta Típica",
    ) in observed
    assert ("TTT::asset-001", "singer", "Carlos Gardel") in observed
    assert ("TTT::asset-001", "composer", "Carlos Gardel") in observed
    assert (
        "TTT::asset-001",
        "source_album",
        "TTT Collection 01",
    ) in observed


def test_preserves_duplicate_observations(tmp_path: Path) -> None:
    card = tmp_path / "Library_Cards_RevA.csv"
    write_card(card)

    observations = harvest_names(card)

    gardel = [
        item
        for item in observations
        if item["observed_value"] == "Carlos Gardel"
    ]

    assert len(gardel) == 3

    assert {
        item["source_field"]
        for item in gardel
    } == {"artist", "singer", "composer"}


def test_does_not_canonicalize_observed_value(tmp_path: Path) -> None:
    card = tmp_path / "Library_Cards_RevA.csv"
    write_card(card)

    observations = harvest_names(card)

    artist = next(
        item
        for item in observations
        if item["source_field"] == "artist"
    )

    assert artist["observed_value"] == "Carlos Gardel"
    assert artist["observed_value"] != "Gardel, Carlos"


def test_does_not_create_entity_association(tmp_path: Path) -> None:
    card = tmp_path / "Library_Cards_RevA.csv"
    write_card(card)

    observations = harvest_names(card)

    for item in observations:
        assert "entity_id" not in item
        assert "association_status" not in item


def test_preserves_card_provenance(tmp_path: Path) -> None:
    card = tmp_path / "Library_Cards_RevA.csv"
    write_card(card)

    observations = harvest_names(card)

    assert all(
        item["source_object_id"] == "TTT::asset-001"
        for item in observations
    )
    assert all(
        item["source_record_revision"] == "C.revA"
        for item in observations
    )


def test_rejects_missing_required_card_identity(tmp_path: Path) -> None:
    card = tmp_path / "Library_Cards_RevA.csv"

    fields = ["source_object_key", "title"]
    with card.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerow(
            {
                "source_object_key": "asset-001",
                "title": json.dumps(["A Media Luz"]),
            }
        )

    with pytest.raises(ValueError):
        harvest_names(card)

