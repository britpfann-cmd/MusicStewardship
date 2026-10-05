"""Explicit catalog reconciliation operations.

Candidate discovery is analysis only. This module performs catalog-changing
operations only after an explicit reconciliation decision has been made.
"""

from typing import Any

from catalog.catalog_store import CatalogStore


def create_provisional_recording(
    store: CatalogStore,
    *,
    cataloged_instance_ids: list[str],
    reason: str,
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create one provisional Recording and associate selected CIs with it."""

    if not cataloged_instance_ids:
        raise ValueError("At least one CatalogedInstance is required.")

    if not reason.strip():
        raise ValueError("An explicit reconciliation reason is required.")

    try:
        recording_id = store.create_entity(
            "RECORDING",
            commit=False,
        )

        association_ids = []

        for ci_id in cataloged_instance_ids:
            association_id = store.assert_association(
                "CATALOGED_INSTANCE_RECORDING",
                "CATALOGED_INSTANCE",
                ci_id,
                "RECORDING",
                recording_id,
                status="PROVISIONAL",
                reason=reason,
                evidence=evidence or {},
                commit=False,
            )
            association_ids.append(association_id)

        store.conn.commit()

    except Exception:
        store.conn.rollback()
        raise

    return {
        "recording_id": recording_id,
        "status": "PROVISIONAL",
        "cataloged_instance_ids": list(cataloged_instance_ids),
        "association_ids": association_ids,
    }
