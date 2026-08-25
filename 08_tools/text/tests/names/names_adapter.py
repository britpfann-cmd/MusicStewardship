#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Mock Names adapter for MusicStewardship text-identity tests.

This is a test implementation only.

It provides the interface that the real Names database will eventually
implement. It does not define the Names database schema or authority rules.
"""

from pathlib import Path


class NamesAdapter:
    """Minimal interface to the test Names registry."""

    def __init__(self, names_file: str | Path):
        self.names_file = Path(names_file)
        self.records = {}
        self._load()

    def _load(self) -> None:
        """Load the mock Names registry."""
        with self.names_file.open("r", encoding="utf-8") as file:
            header = file.readline().rstrip("\r\n").split("|")

            for line in file:
                line = line.rstrip("\r\n")
                if not line:
                    continue

                values = line.split("|")
                record = dict(zip(header, values))
                self.records[record["name_value"]] = record

    def lookup(self, corrected_text: str) -> dict | None:
        """Return an existing Names record, or None."""
        return self.records.get(corrected_text)

    def verify_or_create(self, corrected_text: str) -> dict:
        """
        Return an existing Names record or create a provisional one.

        New records are provisional because no higher authority has
        authorized them.
        """
        existing = self.lookup(corrected_text)

        if existing is not None:
            return existing

        name_ref = f"PROV-{len(self.records) + 1:04d}"

        record = {
            "name_ref": name_ref,
            "name_value": corrected_text,
            "authority_status": "PROVISIONAL",
            "authority_source": "",
        }

        self.records[corrected_text] = record
        return record