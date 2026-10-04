"""Generate the Library Card field-contract section in the public specification."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "04_src"))

from library_card_interface import certified_interface


BEGIN = "<!-- BEGIN GENERATED LIBRARY CARD FIELD CONTRACT -->"
END = "<!-- END GENERATED LIBRARY CARD FIELD CONTRACT -->"


def markdown_table(contract):
    lines = [
        BEGIN,
        "",
        f"### Certified {contract.interface_id} Revision {contract.revision} field contract",
        "",
        "This table is generated from the certified CSV field definition. **Do not edit this table directly.**",
        "",
        "| Field | Cardinality | Value form | Meaning | Required | Native / Derived |",
        "|---|---|---|---|---|---|",
    ]

    for row in contract.fields:
        values = [
            row["Field"],
            row["Cardinality"],
            row["Value form"],
            row["Meaning"],
            row["Required"],
            row["Native_or_Derived"],
        ]
        values = [
            str(value).replace("|", r"\|").replace("\n", " ")
            for value in values
        ]
        lines.append("| " + " | ".join(values) + " |")

    lines.extend(["", END])
    return "\n".join(lines)


def replace_generated_section(text, generated):
    if BEGIN in text or END in text:
        if text.count(BEGIN) != 1 or text.count(END) != 1:
            raise ValueError("Generated field-contract markers are malformed.")
        before, remainder = text.split(BEGIN, 1)
        _, after = remainder.split(END, 1)
        return before.rstrip() + "\n\n" + generated + "\n\n" + after.lstrip()

    anchor = "These revisions shall not be conflated."
    if text.count(anchor) != 1:
        raise ValueError("Expected Section 14 insertion anchor not found exactly once.")

    return text.replace(
        anchor,
        anchor + "\n\n" + generated,
        1,
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--revision", required=True)
    ap.add_argument("--spec", type=Path, required=True)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    contract = certified_interface(args.revision)
    generated = markdown_table(contract)

    current = args.spec.read_text(encoding="utf-8")
    expected = replace_generated_section(current, generated)

    if args.check:
        if current != expected:
            raise SystemExit(
                "Library Card Markdown field contract is out of sync "
                "with the certified CSV definition."
            )
        print(
            f"{contract.interface_id} revision {contract.revision}: "
            "Markdown field contract is in sync."
        )
        return

    args.spec.write_text(expected, encoding="utf-8")
    print(
        f"{contract.interface_id} revision {contract.revision}: "
        f"updated {args.spec}"
    )


if __name__ == "__main__":
    main()
