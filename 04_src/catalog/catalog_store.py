"""MusicStewardship Catalog Store v0.1."""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4()}"


class CatalogStore:
    def __init__(self, db_path: str | Path = ":memory:") -> None:
        self.conn = sqlite3.connect(str(db_path))
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        schema = Path(__file__).with_name("schema_v0_1.sql").read_text(
            encoding="utf-8-sig"
        )
        self.conn.executescript(schema)

    def close(self) -> None:
        self.conn.close()

    def accept_library_card(self, card: dict[str, Any]) -> str:
        required = (
            "source_object_id",
            "source_object_key",
            "source_record_revision",
        )
        for field in required:
            if not card.get(field):
                raise ValueError(f"Library Card missing {field!r}")

        existing = self.conn.execute(
            """
            SELECT library_card_id
            FROM library_cards
            WHERE source_object_id = ?
              AND source_record_revision = ?
            """,
            (
                card["source_object_id"],
                card["source_record_revision"],
            ),
        ).fetchone()

        if existing:
            return existing["library_card_id"]

        card_id = new_id("CARD")

        self.conn.execute(
            """
            INSERT INTO library_cards (
                library_card_id,
                source_object_id,
                source_object_key,
                source_record_revision,
                interface_revision,
                c_processing_revision,
                d_processing_revision,
                received_at,
                card_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                card_id,
                card["source_object_id"],
                card["source_object_key"],
                card["source_record_revision"],
                card.get("library_card_interface_revision"),
                card.get("c_processing_revision"),
                card.get("d_processing_revision"),
                now(),
                json.dumps(card, ensure_ascii=False),
            ),
        )
        self.conn.commit()
        return card_id

    def find_active_ci_for_library_card(
        self,
        library_card_id: str,
    ) -> str | None:
        rows = self.conn.execute(
            """
            SELECT cataloged_instance_id
            FROM cataloged_instance_evidence
            WHERE library_card_id = ?
              AND relationship_status = 'ACTIVE'
            ORDER BY created_at, cataloged_instance_evidence_id
            """,
            (library_card_id,),
        ).fetchall()

        if not rows:
            return None

        if len(rows) > 1:
            raise ValueError(
                "Library Card has multiple ACTIVE CatalogedInstance "
                f"relationships: {library_card_id}"
            )

        return rows[0]["cataloged_instance_id"]

    def create_cataloged_instance(
        self,
        library_card_id: str,
        state: dict[str, Any] | None = None,
        reason: str = "Initial catalog interpretation",
    ) -> str:
        existing_ci = self.find_active_ci_for_library_card(library_card_id)
        if existing_ci is not None:
            return existing_ci

        ci_id = new_id("CI")
        t = now()

        self.conn.execute(
            """
            INSERT INTO cataloged_instances
            (cataloged_instance_id,status,created_at,updated_at)
            VALUES (?, 'PROVISIONAL', ?, ?)
            """,
            (ci_id, t, t),
        )

        self.conn.execute(
            """
            INSERT INTO cataloged_instance_evidence (
                cataloged_instance_evidence_id,
                cataloged_instance_id,
                library_card_id,
                relationship_status,
                reason,
                created_at
            )
            VALUES (?, ?, ?, 'ACTIVE', ?, ?)
            """,
            (
                new_id("CIE"),
                ci_id,
                library_card_id,
                "Initial Library Card evidence",
                t,
            ),
        )

        self.add_ci_revision(ci_id, state or {}, reason, commit=False)
        self.conn.commit()
        return ci_id

    def add_ci_revision(
        self,
        ci_id: str,
        state: dict[str, Any],
        reason: str = "",
        *,
        commit: bool = True,
    ) -> str:
        row = self.conn.execute(
            """
            SELECT COALESCE(MAX(revision_number),0) AS n
            FROM cataloged_instance_revisions
            WHERE cataloged_instance_id = ?
            """,
            (ci_id,),
        ).fetchone()

        revision_number = int(row["n"]) + 1
        revision_id = new_id("CIR")
        t = now()

        self.conn.execute(
            """
            UPDATE cataloged_instance_revisions
            SET revision_status = 'HISTORICAL'
            WHERE cataloged_instance_id = ?
              AND revision_status = 'CURRENT'
            """,
            (ci_id,),
        )

        self.conn.execute(
            """
            INSERT INTO cataloged_instance_revisions (
                cataloged_instance_revision_id,
                cataloged_instance_id,
                revision_number,
                revision_status,
                state_json,
                reason,
                created_at
            )
            VALUES (?, ?, ?, 'CURRENT', ?, ?, ?)
            """,
            (
                revision_id,
                ci_id,
                revision_number,
                json.dumps(state, ensure_ascii=False),
                reason,
                t,
            ),
        )

        self.conn.execute(
            """
            UPDATE cataloged_instances
            SET updated_at = ?
            WHERE cataloged_instance_id = ?
            """,
            (t, ci_id),
        )

        if commit:
            self.conn.commit()

        return revision_id

    def create_entity(
        self,
        entity_type: str,
        data: dict[str, Any] | None = None,
    ) -> str:
        tables = {
            "RECORDING": ("recordings", "recording_id", "REC"),
            "PERFORMANCE": ("performances", "performance_id", "PERF"),
            "WORK": ("works", "work_id", "WORK"),
        }
        if entity_type not in tables:
            raise ValueError(f"Unsupported catalog entity type: {entity_type}")

        table, key, prefix = tables[entity_type]
        entity_id = new_id(prefix)
        t = now()

        self.conn.execute(
            f"""
            INSERT INTO {table}
            ({key},status,current_data_json,created_at,updated_at)
            VALUES (?, 'PROVISIONAL', ?, ?, ?)
            """,
            (
                entity_id,
                json.dumps(data or {}, ensure_ascii=False),
                t,
                t,
            ),
        )
        self.conn.commit()
        return entity_id

    def assert_association(
        self,
        association_type: str,
        subject_type: str,
        subject_id: str,
        object_type: str,
        object_id: str,
        status: str = "PROVISIONAL",
        reason: str = "",
        evidence: dict[str, Any] | None = None,
        supersedes: str | None = None,
    ) -> str:
        association_id = new_id("ASC")

        self.conn.execute(
            """
            INSERT INTO catalog_associations (
                association_id,
                association_type,
                subject_type,
                subject_id,
                object_type,
                object_id,
                status,
                reason,
                evidence_json,
                supersedes_association_id,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                association_id,
                association_type,
                subject_type,
                subject_id,
                object_type,
                object_id,
                status,
                reason,
                json.dumps(evidence or {}, ensure_ascii=False),
                supersedes,
                now(),
            ),
        )
        self.conn.commit()
        return association_id
