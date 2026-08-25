#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MusicStewardship Text Identity Wrapper

Intake-stage utility for textual identity fields.

Produces three levels:
    A. original_text   - exact source value
    B. corrected_text  - deterministic Unicode/text correction
    C. canonical_*     - current authority result (lookup hook; not yet
                         connected to the names database)

The utility does not write to the database or alter source files.

Input:
    UTF-8 text, one value/record per line from stdin.

Output:
    Structured JSON Lines on stdout.

Diagnostics:
    Human-readable diagnostics on stderr when requested.

Examples:
    python text_identity.py < input.txt > output.jsonl
    python text_identity.py --diagnostics < input.txt > output.jsonl
"""

import argparse
import json
import sys
import unicodedata
from typing import Any
from pathlib import Path


def correct_text(text: str) -> tuple[str, list[str]]:
    """Apply deterministic text corrections.

    First repair broken Unicode/mojibake with ftfy, then apply
    canonical Unicode normalization and our explicit punctuation rules.
    """
    import ftfy

    corrected = ftfy.fix_text(text)
    changes = []

    if corrected != text:
        changes.append("ftfy Unicode/mojibake repair")

    normalized = unicodedata.normalize("NFC", corrected)

    if normalized != corrected:
        changes.append("Unicode NFC normalization")

    corrected = normalized

    replacements = {
        "’": "'",
        "´": "'",
        "`": "'",
    }

    for old, new in replacements.items():
        if old in corrected:
            corrected = corrected.replace(old, new)
            changes.append(
                f"{unicodedata.name(old)} -> ASCII apostrophe"
            )

    return corrected, changes

def resolve_canonical(corrected: str) -> dict:
    """Authority-resolution hook.

    The names/authority database is not connected yet. Therefore this
    initial implementation does not invent canonical identities.

    A future resolver will return:
        canonical_ref
        canonical_name
        canonical_status
        authority_source
    """
    if not corrected:
        return {
            "canonical_ref": None,
            "canonical_name": None,
            "canonical_status": "UNRESOLVED",
            "authority_source": None,
        }

    return {
        "canonical_ref": None,
        "canonical_name": None,
        "canonical_status": "UNRESOLVED",
        "authority_source": None,
    }

def process_value(
    original: str,
    record_number: int,
    names_adapter: Any = None,
) -> dict:
    corrected, changes = correct_text(original)

    if names_adapter is not None and corrected:
        name_record = names_adapter.verify_or_create(corrected)

        canonical = {
            "canonical_ref": name_record["name_ref"],
            "canonical_name": name_record["name_value"],
            "canonical_status": name_record["authority_status"],
            "authority_source": name_record["authority_source"] or None,
        }
    else:
        canonical = resolve_canonical(corrected)

    return {
        "record": record_number,
        "original_text": original,
        "corrected_text": corrected,
        "correction_applied": corrected != original,
        "corrections": changes,
        **canonical,
    }

def emit_diagnostic(result: dict) -> None:
    changed = "yes" if result["correction_applied"] else "no"
    print(
        f'record={result["record"]} '
        f'original={result["original_text"]!r} '
        f'corrected={result["corrected_text"]!r} '
        f'changed={changed} '
        f'status={result["canonical_status"]}',
        file=sys.stderr,
    )
    if result["corrections"]:
        print(
            f'  corrections={"; ".join(result["corrections"])}',
            file=sys.stderr,
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prepare MusicStewardship three-level text identity records."
    )
    parser.add_argument(
        "--diagnostics",
        action="store_true",
        help="write per-record processing diagnostics to stderr",
    )
    parser.add_argument(
        "--names-file",
        help="test Names registry file",
    )
    args = parser.parse_args()

    names_adapter = None

    if args.names_file:
        names_path = Path(args.names_file)
        sys.path.insert(0, str(names_path.parent))

        from names_adapter import NamesAdapter

        names_adapter = NamesAdapter(names_path)

    stdin = sys.stdin.buffer

    for record_number, raw_line in enumerate(stdin, start=1):
        line = raw_line.decode("utf-8")
        original = line.rstrip("\r\n")

        result = process_value(
            original,
            record_number,
            names_adapter,
        )

        print(
            json.dumps(
                result,
                ensure_ascii=False,
                separators=(",", ":"),
            )
        )

        if args.diagnostics:
            emit_diagnostic(result)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
