"""Versioned Library Card public-interface contracts.

The interface definition is shared by producers and consumers.  Neither side
owns or redefines a version.

Certification is deterministic and side-effect free: the same canonical
definition always produces the same certificate.
"""
from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path


REQUIRED_DEFINITION_COLUMNS = (
    "Field",
    "Cardinality",
    "Value form",
    "Meaning",
    "Required",
    "Native_or_Derived",
)

VALID_CARDINALITIES = {"0..1", "1", "0..n", "1..n"}


@dataclass(frozen=True)
class InterfaceContract:
    interface_id: str
    revision: str
    definition_path: Path
    fields: tuple[dict[str, str], ...]
    certificate: str

    @property
    def field_names(self) -> tuple[str, ...]:
        return tuple(row["Field"] for row in self.fields)

    @property
    def array_fields(self) -> frozenset[str]:
        return frozenset(
            row["Field"]
            for row in self.fields
            if row["Cardinality"] in {"0..n", "1..n"}
        )


def _read_definition(path: Path) -> tuple[dict[str, str], ...]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        if tuple(reader.fieldnames or ()) != REQUIRED_DEFINITION_COLUMNS:
            raise ValueError(
                "Interface definition columns do not match the certified "
                f"contract schema: {path}"
            )

        rows = tuple(dict(row) for row in reader)

    if not rows:
        raise ValueError(f"Interface definition is empty: {path}")

    names = [row["Field"] for row in rows]
    if len(names) != len(set(names)):
        raise ValueError(f"Duplicate public field in interface definition: {path}")

    for row in rows:
        if not row["Field"]:
            raise ValueError(f"Blank public field in interface definition: {path}")
        if row["Cardinality"] not in VALID_CARDINALITIES:
            raise ValueError(
                f"Invalid cardinality {row['Cardinality']!r} "
                f"for field {row['Field']!r}"
            )

    return rows


def _canonical_bytes(
    interface_id: str,
    revision: str,
    fields: tuple[dict[str, str], ...],
) -> bytes:
    payload = {
        "interface_id": interface_id,
        "revision": revision,
        "definition_columns": REQUIRED_DEFINITION_COLUMNS,
        "fields": fields,
    }
    return json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def certify_definition(
    *,
    interface_id: str,
    revision: str,
    definition_path: Path,
) -> InterfaceContract:
    """Load and deterministically certify one versioned interface definition."""
    fields = _read_definition(definition_path)
    digest = hashlib.sha256(
        _canonical_bytes(interface_id, revision, fields)
    ).hexdigest()

    return InterfaceContract(
        interface_id=interface_id,
        revision=revision,
        definition_path=definition_path,
        fields=fields,
        certificate=f"sha256:{digest}",
    )

# Certified Library Card interface definitions.
#
# Adding an entry here is an explicit act of making that interface version
# available to producers and consumers.  The definition itself remains the
# authority for its field contract.
_REPO_ROOT = Path(__file__).resolve().parents[1]

CERTIFIED_INTERFACES = {
    ("ING-CARD-001", "A"): {
        "definition_path": (
            _REPO_ROOT
            / "01_docs"
            / "05_Ingestion"
            / "MusicStewardship_Library_Card_Field_Definitions_RevA.csv"
        ),
        "certificate": (
            "sha256:"
            "a06b0925aee1195a71ad885ab280675173a968432d989b4b1806136bdd70a65e"
        ),
    },
}


def certified_interface(
    revision: str,
    *,
    interface_id: str = "ING-CARD-001",
) -> InterfaceContract:
    """Return and verify the exact certified contract for a supported version."""
    key = (interface_id, revision)
    try:
        registration = CERTIFIED_INTERFACES[key]
    except KeyError as exc:
        raise ValueError(
            f"Unsupported or uncertified Library Card interface: "
            f"{interface_id} revision {revision}"
        ) from exc

    contract = certify_definition(
        interface_id=interface_id,
        revision=revision,
        definition_path=registration["definition_path"],
    )

    expected = registration["certificate"]
    if contract.certificate != expected:
        raise ValueError(
            f"Certified Library Card interface content mismatch: "
            f"{interface_id} revision {revision}; "
            f"expected {expected}, got {contract.certificate}"
        )

    return contract
