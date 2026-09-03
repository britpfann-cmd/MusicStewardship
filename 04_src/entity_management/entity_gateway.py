"""IMPL-EM-001 — Entity Management Gateway.

Small reference implementation derived from SPEC-EM-001.

The implementation deliberately uses a simple SQLite store:
- observations are preserved as received;
- entities have stable UUID identifiers;
- associations are separate from observations;
- provisional/unresolved/review outcomes are explicit;
- current entity state is separate from observation history.

This is an implementation baseline, not the final catalog database.
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4()}"


@dataclass(frozen=True)
class Observation:
    entity_type: str
    source: str
    observed: dict[str, Any]
    context: dict[str, Any] | None = None
    evidence: dict[str, Any] | None = None
    interpreted: dict[str, Any] | None = None


class EntityGateway:
    """Common canonical entity-management boundary."""

    def __init__(self, db_path: str | Path = ":memory:") -> None:
        self.db_path = str(db_path)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_schema()

    def close(self) -> None:
        self.conn.close()

    def _create_schema(self) -> None:
        self.conn.executescript(
            """
            PRAGMA foreign_keys = ON;

            CREATE TABLE IF NOT EXISTS entities (
                entity_id TEXT PRIMARY KEY,
                entity_type TEXT NOT NULL,
                status TEXT NOT NULL,
                current_data TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS observations (
                observation_id TEXT PRIMARY KEY,
                entity_type TEXT NOT NULL,
                source TEXT NOT NULL,
                observed_data TEXT NOT NULL,
                context_data TEXT,
                evidence_data TEXT,
                interpreted_data TEXT,
                received_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS associations (
                association_id TEXT PRIMARY KEY,
                observation_id TEXT NOT NULL,
                entity_id TEXT,
                status TEXT NOT NULL,
                reason TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(observation_id) REFERENCES observations(observation_id),
                FOREIGN KEY(entity_id) REFERENCES entities(entity_id)
            );

            CREATE INDEX IF NOT EXISTS idx_entities_type
                ON entities(entity_type);

            CREATE INDEX IF NOT EXISTS idx_observations_source
                ON observations(source);

            CREATE INDEX IF NOT EXISTS idx_associations_observation
                ON associations(observation_id);

            CREATE INDEX IF NOT EXISTS idx_associations_entity
                ON associations(entity_id);
            """
        )
        self.conn.commit()

    def accept_observation(self, observation: Observation) -> str:
        """Preserve a source observation before canonical resolution."""
        observation_id = new_id("OBS")
        self.conn.execute(
            """
            INSERT INTO observations (
                observation_id, entity_type, source,
                observed_data, context_data, evidence_data,
                interpreted_data, received_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                observation_id,
                observation.entity_type,
                observation.source,
                json.dumps(observation.observed, ensure_ascii=False),
                json.dumps(observation.context or {}, ensure_ascii=False),
                json.dumps(observation.evidence or {}, ensure_ascii=False),
                json.dumps(observation.interpreted or {}, ensure_ascii=False),
                now(),
            ),
        )
        self.conn.commit()
        return observation_id

    def create_provisional(
        self,
        observation_id: str,
        data: dict[str, Any] | None = None,
        reason: str = "No adequate existing match",
    ) -> str:
        """Create a stable-ID provisional entity and associate the observation."""
        row = self._observation(observation_id)
        entity_id = new_id("ENT")
        t = now()

        entity_data = data or json.loads(row["interpreted_data"] or "{}")
        self.conn.execute(
            """
            INSERT INTO entities (
                entity_id, entity_type, status,
                current_data, created_at, updated_at
            )
            VALUES (?, ?, 'PROVISIONAL', ?, ?, ?)
            """,
            (
                entity_id,
                row["entity_type"],
                json.dumps(entity_data, ensure_ascii=False),
                t,
                t,
            ),
        )
        self._insert_association(
            observation_id, entity_id, "PROVISIONAL", reason
        )
        self.conn.commit()
        return entity_id

    def associate(
        self,
        observation_id: str,
        entity_id: str,
        status: str = "ASSOCIATED",
        reason: str = "",
    ) -> str:
        """Associate an observation with an existing canonical entity."""
        self._observation(observation_id)
        self._entity(entity_id)
        association_id = self._insert_association(
            observation_id, entity_id, status, reason
        )
        self.conn.commit()
        return association_id

    def mark_unresolved(
        self, observation_id: str, reason: str = ""
    ) -> str:
        """Preserve an observation without asserting canonical identity."""
        self._observation(observation_id)
        association_id = self._insert_association(
            observation_id, None, "UNRESOLVED", reason
        )
        self.conn.commit()
        return association_id

    def mark_review(
        self, observation_id: str, reason: str = ""
    ) -> str:
        """Preserve ambiguity/conflict for later review."""
        self._observation(observation_id)
        association_id = self._insert_association(
            observation_id, None, "REVIEW_REQUIRED", reason
        )
        self.conn.commit()
        return association_id

    def revise_association(
        self,
        association_id: str,
        entity_id: str | None,
        status: str,
        reason: str = "",
    ) -> None:
        """Revise the current association without deleting the observation."""
        self._entity(entity_id) if entity_id else None
        t = now()
        self.conn.execute(
            """
            UPDATE associations
            SET entity_id = ?, status = ?, reason = ?, updated_at = ?
            WHERE association_id = ?
            """,
            (entity_id, status, reason, t, association_id),
        )
        if self.conn.total_changes == 0:
            raise KeyError(f"Unknown association: {association_id}")
        self.conn.commit()

    def get_entity(self, entity_id: str) -> dict[str, Any]:
        row = self._entity(entity_id)
        return {
            "entity_id": row["entity_id"],
            "entity_type": row["entity_type"],
            "status": row["status"],
            "current_data": json.loads(row["current_data"]),
        }

    def get_observation(self, observation_id: str) -> dict[str, Any]:
        row = self._observation(observation_id)
        return {
            "observation_id": row["observation_id"],
            "entity_type": row["entity_type"],
            "source": row["source"],
            "observed": json.loads(row["observed_data"]),
            "context": json.loads(row["context_data"] or "{}"),
            "evidence": json.loads(row["evidence_data"] or "{}"),
            "interpreted": json.loads(row["interpreted_data"] or "{}"),
        }

    def _insert_association(
        self,
        observation_id: str,
        entity_id: str | None,
        status: str,
        reason: str,
    ) -> str:
        association_id = new_id("ASC")
        t = now()
        self.conn.execute(
            """
            INSERT INTO associations (
                association_id, observation_id, entity_id,
                status, reason, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                association_id,
                observation_id,
                entity_id,
                status,
                reason,
                t,
                t,
            ),
        )
        return association_id

    def _observation(self, observation_id: str) -> sqlite3.Row:
        row = self.conn.execute(
            "SELECT * FROM observations WHERE observation_id = ?",
            (observation_id,),
        ).fetchone()
        if row is None:
            raise KeyError(f"Unknown observation: {observation_id}")
        return row

    def _entity(self, entity_id: str) -> sqlite3.Row:
        row = self.conn.execute(
            "SELECT * FROM entities WHERE entity_id = ?",
            (entity_id,),
        ).fetchone()
        if row is None:
            raise KeyError(f"Unknown entity: {entity_id}")
        return row
