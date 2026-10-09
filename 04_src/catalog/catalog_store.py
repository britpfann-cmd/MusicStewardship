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
        # Existing v0.1 databases predate the observation revision FK.
        columns = {row[1] for row in self.conn.execute("PRAGMA table_info(catalog_observations)")}
        if "library_card_revision_id" not in columns:
            self.conn.execute("ALTER TABLE catalog_observations ADD COLUMN library_card_revision_id TEXT REFERENCES library_card_revisions(library_card_revision_id)")
            self.conn.commit()
        # Backfill the original submissions on legacy databases, preserving
        # their original received_at and full stored card_json.
        self.conn.execute("""
            INSERT INTO library_card_revisions
            (library_card_revision_id, library_card_id, revision_number,
             interface_revision, c_processing_revision, d_processing_revision,
             card_json, received_at)
            SELECT 'LCR-' || library_card_id, library_card_id, 1,
                   interface_revision, c_processing_revision, d_processing_revision,
                   card_json, received_at
            FROM library_cards AS lc
            WHERE NOT EXISTS (SELECT 1 FROM library_card_revisions AS r
                              WHERE r.library_card_id = lc.library_card_id)
        """)
        self.conn.commit()

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

        submitted_json = json.dumps(card, ensure_ascii=False, sort_keys=True)
        if existing:
            card_id = existing["library_card_id"]
            previous = self.conn.execute(
                "SELECT revision_number, card_json FROM library_card_revisions "
                "WHERE library_card_id = ? ORDER BY revision_number DESC LIMIT 1",
                (card_id,),
            ).fetchone()
            if previous is not None and json.loads(previous["card_json"]) == card:
                return card_id
            revision_number = (previous["revision_number"] if previous else 0) + 1
            timestamp = now()
            self.conn.execute("""
                INSERT INTO library_card_revisions
                (library_card_revision_id, library_card_id, revision_number,
                 interface_revision, c_processing_revision, d_processing_revision,
                 card_json, received_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (new_id("LCR"), card_id, revision_number,
                  card.get("library_card_interface_revision"),
                  card.get("c_processing_revision"),
                  card.get("d_processing_revision"), submitted_json, timestamp))
            self.conn.execute("""
                UPDATE library_cards
                SET source_object_key = ?, interface_revision = ?,
                    c_processing_revision = ?, d_processing_revision = ?,
                    received_at = ?, card_json = ?
                WHERE library_card_id = ?
            """, (card["source_object_key"], card.get("library_card_interface_revision"),
                  card.get("c_processing_revision"), card.get("d_processing_revision"),
                  timestamp, submitted_json, card_id))
            self.conn.commit()
            return card_id

        card_id = new_id("CARD")
        timestamp = now()
        self.conn.execute("""
            INSERT INTO library_cards
            (library_card_id, source_object_id, source_object_key,
             source_record_revision, interface_revision, c_processing_revision,
             d_processing_revision, received_at, card_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (card_id, card["source_object_id"], card["source_object_key"],
              card["source_record_revision"], card.get("library_card_interface_revision"),
              card.get("c_processing_revision"), card.get("d_processing_revision"),
              timestamp, submitted_json))
        self.conn.execute("""
            INSERT INTO library_card_revisions
            (library_card_revision_id, library_card_id, revision_number,
             interface_revision, c_processing_revision, d_processing_revision,
             card_json, received_at) VALUES (?, ?, 1, ?, ?, ?, ?, ?)
        """, (new_id("LCR"), card_id, card.get("library_card_interface_revision"),
              card.get("c_processing_revision"), card.get("d_processing_revision"),
              submitted_json, timestamp))
        self.conn.commit()
        return card_id

    def latest_library_card_revision_id(self, library_card_id: str) -> str:
        row = self.conn.execute(
            "SELECT library_card_revision_id FROM library_card_revisions "
            "WHERE library_card_id = ? ORDER BY revision_number DESC LIMIT 1",
            (library_card_id,),
        ).fetchone()
        if row is None:
            raise ValueError(f"Unknown Library Card: {library_card_id}")
        return row["library_card_revision_id"]

    def get_library_card_revision_history(self, library_card_id: str) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            "SELECT * FROM library_card_revisions WHERE library_card_id = ? "
            "ORDER BY revision_number", (library_card_id,),
        ).fetchall()
        return [dict(row) | {"card": json.loads(row["card_json"])} for row in rows]

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

    def get_current_ci_state(
        self,
        ci_id: str,
    ) -> dict[str, Any] | None:
        row = self.conn.execute(
            """
            SELECT state_json
            FROM current_cataloged_instance_revisions
            WHERE cataloged_instance_id = ?
            """,
            (ci_id,),
        ).fetchone()

        if row is None:
            return None

        return json.loads(row["state_json"])

    def get_ci_provenance(
        self,
        ci_id: str,
    ) -> dict[str, Any] | None:
        ci_row = self.conn.execute(
            """
            SELECT
                cataloged_instance_id,
                status,
                created_at,
                updated_at
            FROM cataloged_instances
            WHERE cataloged_instance_id = ?
            """,
            (ci_id,),
        ).fetchone()

        if ci_row is None:
            return None

        evidence_rows = self.conn.execute(
            """
            SELECT
                lc.library_card_id,
                lc.source_object_id,
                lc.source_object_key,
                lc.source_record_revision,
                lc.interface_revision,
                lc.c_processing_revision,
                lc.d_processing_revision,
                lc.received_at,
                cie.reason AS relationship_reason,
                cie.created_at AS relationship_created_at
            FROM cataloged_instance_evidence AS cie
            JOIN library_cards AS lc
              ON lc.library_card_id = cie.library_card_id
            WHERE cie.cataloged_instance_id = ?
              AND cie.relationship_status = 'ACTIVE'
            ORDER BY cie.created_at, lc.library_card_id
            """,
            (ci_id,),
        ).fetchall()

        return {
            "cataloged_instance_id": ci_row["cataloged_instance_id"],
            "status": ci_row["status"],
            "created_at": ci_row["created_at"],
            "updated_at": ci_row["updated_at"],
            "active_library_card_evidence": [
                dict(row) for row in evidence_rows
            ],
        }

    def add_observation(
        self,
        *,
        library_card_id: str | None,
        library_card_revision_id: str | None = None,
        subject_type: str,
        subject_id: str | None,
        field: str,
        observed_value: Any,
        interpreted_value: Any | None = None,
        context: dict[str, Any] | None = None,
        evidence: dict[str, Any] | None = None,
        commit: bool = True,
    ) -> str:
        observed_value_json = json.dumps(
            observed_value,
            ensure_ascii=False,
        )

        context_json = json.dumps(context or {}, ensure_ascii=False, sort_keys=True)
        evidence_json = json.dumps(evidence or {}, ensure_ascii=False, sort_keys=True)
        # Distinguish evidence from different source rules/revisions, even
        # when the decoded field and value are identical.
        existing = self.conn.execute("""
            SELECT observation_id, context_json, evidence_json
            FROM catalog_observations
            WHERE library_card_id IS ?
              AND library_card_revision_id IS ?
              AND subject_type = ? AND subject_id IS ?
              AND observed_field = ? AND observed_value_json = ?
        """, (library_card_id, library_card_revision_id, subject_type,
              subject_id, field, observed_value_json)).fetchall()
        for candidate in existing:
            if (json.loads(candidate["context_json"] or "{}") == (context or {})
                    and json.loads(candidate["evidence_json"] or "{}") == (evidence or {})):
                return candidate["observation_id"]

        observation_id = new_id("OBS")

        interpreted_value_json = (
            None
            if interpreted_value is None
            else json.dumps(interpreted_value, ensure_ascii=False)
        )

        self.conn.execute(
            """
            INSERT INTO catalog_observations (
                observation_id,
                library_card_id,
                library_card_revision_id,
                subject_type,
                subject_id,
                observed_field,
                observed_value_json,
                interpreted_value_json,
                context_json,
                evidence_json,
                observed_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                observation_id,
                library_card_id,
                library_card_revision_id,
                subject_type,
                subject_id,
                field,
                observed_value_json,
                interpreted_value_json,
                json.dumps(context or {}, ensure_ascii=False),
                json.dumps(evidence or {}, ensure_ascii=False),
                now(),
            ),
        )

        if commit:
            self.conn.commit()

        return observation_id

    def get_ci_revision_history(
        self,
        ci_id: str,
    ) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            """
            SELECT
                cataloged_instance_revision_id,
                revision_number,
                revision_status,
                state_json,
                reason,
                created_at
            FROM cataloged_instance_revisions
            WHERE cataloged_instance_id = ?
            ORDER BY revision_number
            """,
            (ci_id,),
        ).fetchall()

        return [
            {
                "cataloged_instance_revision_id": row["cataloged_instance_revision_id"],
                "revision_number": row["revision_number"],
                "revision_status": row["revision_status"],
                "state": json.loads(row["state_json"]),
                "reason": row["reason"],
                "created_at": row["created_at"],
            }
            for row in rows
        ]
    def get_ci_observations(
        self,
        ci_id: str,
    ) -> list[dict[str, Any]]:
        rows = self.conn.execute(
            """
            SELECT
                observation_id,
                library_card_id,
                observed_field,
                observed_value_json,
                interpreted_value_json,
                context_json,
                evidence_json,
                observed_at
            FROM catalog_observations
            WHERE subject_type = 'CATALOGED_INSTANCE'
              AND subject_id = ?
            ORDER BY observed_field, observation_id
            """,
            (ci_id,),
        ).fetchall()

        observations = []

        for row in rows:
            observations.append(
                {
                    "observation_id": row["observation_id"],
                    "library_card_id": row["library_card_id"],
                    "field": row["observed_field"],
                    "observed_value": json.loads(
                        row["observed_value_json"]
                    ),
                    "interpreted_value": (
                        None
                        if row["interpreted_value_json"] is None
                        else json.loads(
                            row["interpreted_value_json"]
                        )
                    ),
                    "context": (
                        {}
                        if row["context_json"] is None
                        else json.loads(row["context_json"])
                    ),
                    "evidence": (
                        {}
                        if row["evidence_json"] is None
                        else json.loads(row["evidence_json"])
                    ),
                    "observed_at": row["observed_at"],
                }
            )

        return observations
    def create_entity(
        self,
        entity_type: str,
        data: dict[str, Any] | None = None,
        commit: bool = True,
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
        if commit:
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
        commit: bool = True,
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
        if commit:
            self.conn.commit()
        return association_id
