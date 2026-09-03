#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Analyze the catalog-wide Crackling Tunes text extraction.

Input:
    CSV produced by extract_flac_text.py

Output:
    Markdown report describing observed patterns, completeness,
    formats, anomalies, and candidate transformation issues.

This report is descriptive. It does not propose or apply ingest
transformations automatically.
"""

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path


TEXT_FIELDS = (
    "ARTIST",
    "ALBUMARTIST",
    "COMPOSER",
    "TITLE",
)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:
        return list(csv.DictReader(file))


def pct(n: int, total: int) -> str:
    if total == 0:
        return "0.0%"
    return f"{100 * n / total:.1f}%"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Analyze Crackling Tunes catalog text extraction."
    )

    parser.add_argument(
        "input",
        type=Path,
        help="catalog text CSV",
    )

    parser.add_argument(
        "output",
        type=Path,
        help="Markdown analysis report",
    )

    args = parser.parse_args()

    rows = read_rows(args.input)

    # ------------------------------------------------------------------
    # File-level reconstruction
    # ------------------------------------------------------------------

    files = {}

    for row in rows:
        key = (
            row["source_release"],
            row["source_path"],
        )

        files.setdefault(
            key,
            {
                "release": row["source_release"],
                "path": row["source_path"],
                "file": row["source_file"],
                "format": row["audio_format"],
                "catalog": row["catalog_number"],
                "fields": {},
            },
        )

        files[key]["fields"][row["field_name"]] = (
            row["original_text"]
        )

    file_rows = list(files.values())

    # ------------------------------------------------------------------
    # Basic counts
    # ------------------------------------------------------------------

    release_files = Counter(
        x["release"] for x in file_rows
    )

    format_files = Counter(
        x["format"] for x in file_rows
    )

    release_formats = defaultdict(Counter)

    for item in file_rows:
        release_formats[item["release"]][
            item["format"]
        ] += 1

    # ------------------------------------------------------------------
    # Field completeness
    # ------------------------------------------------------------------

    field_present = Counter()
    field_empty = Counter()

    for item in file_rows:
        for field in TEXT_FIELDS:
            value = item["fields"].get(field, "")

            if value.strip():
                field_present[field] += 1
            else:
                field_empty[field] += 1

    # ------------------------------------------------------------------
    # Catalog-number completeness
    # ------------------------------------------------------------------

    catalog_present = sum(
        bool(x["catalog"].strip())
        for x in file_rows
    )

    catalog_missing = len(file_rows) - catalog_present

    # ------------------------------------------------------------------
    # Distinct values
    # ------------------------------------------------------------------

    distinct_values = {}

    for field in TEXT_FIELDS:
        values = Counter(
            x["fields"].get(field, "")
            for x in file_rows
            if x["fields"].get(field, "").strip()
        )

        distinct_values[field] = values

    # ------------------------------------------------------------------
    # Duplicate/variant values
    #
    # Conservative normalization is used only for detection.
    # It is NOT proposed as an ingest transformation.
    # ------------------------------------------------------------------

    def comparison_key(value: str) -> str:
        return " ".join(
            value.casefold().split()
        )

    variants = defaultdict(lambda: defaultdict(set))

    for field in TEXT_FIELDS:
        for value in distinct_values[field]:
            variants[field][
                comparison_key(value)
            ].add(value)

    variant_groups = {}

    for field in TEXT_FIELDS:
        groups = [
            sorted(values)
            for values in variants[field].values()
            if len(values) > 1
        ]

        variant_groups[field] = sorted(
            groups,
            key=lambda x: (-len(x), x),
        )

    # ------------------------------------------------------------------
    # Suspicious encoding
    # ------------------------------------------------------------------

    mojibake_markers = (
        "Ã",
        "Â",
        "â",
        "ð",
        "�",
        "╠",
        "╣",
        "╬",
        "ï",
    )

    encoding_suspects = []

    for item in file_rows:
        for field in TEXT_FIELDS:
            value = item["fields"].get(field, "")

            if any(
                marker in value
                for marker in mojibake_markers
            ):
                encoding_suspects.append(
                    (
                        item["release"],
                        item["file"],
                        field,
                        value,
                    )
                )

    # ------------------------------------------------------------------
    # Files with incomplete text identity
    # ------------------------------------------------------------------

    incomplete_files = []

    for item in file_rows:
        missing = [
            field
            for field in TEXT_FIELDS
            if not item["fields"].get(field, "").strip()
        ]

        if missing:
            incomplete_files.append(
                (
                    item["release"],
                    item["file"],
                    missing,
                )
            )

    # ------------------------------------------------------------------
    # Release-level field completeness
    # ------------------------------------------------------------------

    release_field_counts = defaultdict(
        lambda: defaultdict(lambda: [0, 0])
    )

    for item in file_rows:
        release = item["release"]

        for field in TEXT_FIELDS:
            release_field_counts[release][field][0] += 1

            if item["fields"].get(field, "").strip():
                release_field_counts[release][field][1] += 1

    # ------------------------------------------------------------------
    # Write report
    # ------------------------------------------------------------------

    args.output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with args.output.open(
        "w",
        encoding="utf-8",
    ) as out:

        out.write("# Crackling Tunes Catalog Analysis\n\n")

        out.write(
            "This report describes observed properties of the "
            "catalog-wide extraction. It does not establish "
            "transformation rules.\n\n"
        )

        out.write("## 1. Dataset\n\n")

        out.write(
            f"- Extracted text rows: **{len(rows):,}**\n"
        )
        out.write(
            f"- Audio files represented: **{len(file_rows):,}**\n"
        )
        out.write(
            f"- Releases represented: **{len(release_files):,}**\n"
        )
        out.write(
            f"- Catalog number present: **{catalog_present:,}** "
            f"({pct(catalog_present, len(file_rows))})\n"
        )
        out.write(
            f"- Catalog number missing: **{catalog_missing:,}** "
            f"({pct(catalog_missing, len(file_rows))})\n"
        )

        out.write("\n## 2. Audio Formats\n\n")
        out.write("| Format | Files | Percent |\n")
        out.write("|---|---:|---:|\n")

        for fmt, count in format_files.most_common():
            out.write(
                f"| {fmt} | {count} | "
                f"{pct(count, len(file_rows))} |\n"
            )

        out.write("\n## 3. Releases\n\n")
        out.write(
            "| Release | Files | Audio formats |\n"
        )
        out.write("|---|---:|---|\n")

        for release in sorted(release_files):
            formats = ", ".join(
                f"{fmt}={count}"
                for fmt, count in
                release_formats[release].items()
            )

            out.write(
                f"| {release} | "
                f"{release_files[release]} | "
                f"{formats} |\n"
            )

        out.write("\n## 4. Text Field Completeness\n\n")
        out.write("| Field | Present | Empty | Present % |\n")
        out.write("|---|---:|---:|---:|\n")

        for field in TEXT_FIELDS:
            out.write(
                f"| {field} | "
                f"{field_present[field]} | "
                f"{field_empty[field]} | "
                f"{pct(field_present[field], len(file_rows))} |\n"
            )

        out.write("\n## 5. Distinct Values\n\n")

        for field in TEXT_FIELDS:
            values = distinct_values[field]

            out.write(
                f"### {field}\n\n"
            )

            out.write(
                f"- Distinct non-empty values: "
                f"**{len(values):,}**\n\n"
            )

            out.write(
                "| Frequency | Value |\n"
            )
            out.write("|---:|---|\n")

            for value, count in values.most_common(25):
                safe_value = value.replace("|", "\\|")
                out.write(
                    f"| {count} | {safe_value} |\n"
                )

            if len(values) > 25:
                out.write(
                    f"\n_Only the 25 most frequent values are "
                    f"shown; {len(values) - 25:,} additional "
                    f"values are present._\n"
                )

            out.write("\n")

        out.write(
            "## 6. Potential Text Variants\n\n"
        )

        out.write(
            "These groups have identical values after a very "
            "conservative case/whitespace comparison but differ "
            "in their stored representation. They are candidates "
            "for investigation, not automatic normalization.\n\n"
        )

        for field in TEXT_FIELDS:
            groups = variant_groups[field]

            out.write(
                f"### {field}\n\n"
            )

            if not groups:
                out.write(
                    "No variants detected.\n\n"
                )
                continue

            for group in groups[:50]:
                out.write("- ")
                out.write(
                    " / ".join(
                        f"`{value}`"
                        for value in group
                    )
                )
                out.write("\n")

            if len(groups) > 50:
                out.write(
                    f"\n_{len(groups) - 50} additional "
                    "variant groups omitted._\n"
                )

            out.write("\n")

        out.write(
            "## 7. Possible Encoding Anomalies\n\n"
        )

        out.write(
            f"Potentially suspicious values: "
            f"**{len(encoding_suspects):,}**\n\n"
        )

        if encoding_suspects:
            out.write(
                "| Release | File | Field | Value |\n"
            )
            out.write("|---|---|---|---|\n")

            for release, filename, field, value in (
                encoding_suspects[:100]
            ):
                out.write(
                    f"| {release} | {filename} | "
                    f"{field} | {value.replace('|', '\\|')} |\n"
                )

            if len(encoding_suspects) > 100:
                out.write(
                    f"\n_Only the first 100 of "
                    f"{len(encoding_suspects):,} suspects "
                    "are shown._\n"
                )
        else:
            out.write(
                "No values matched the initial conservative "
                "suspect-character list.\n"
            )

        out.write("\n## 8. Incomplete Text Identity\n\n")

        out.write(
            f"Files missing at least one of the four selected "
            f"text fields: **{len(incomplete_files):,}**\n\n"
        )

        if incomplete_files:
            out.write(
                "| Release | File | Missing fields |\n"
            )
            out.write("|---|---|---|\n")

            for release, filename, missing in (
                incomplete_files[:100]
            ):
                out.write(
                    f"| {release} | {filename} | "
                    f"{', '.join(missing)} |\n"
                )

            if len(incomplete_files) > 100:
                out.write(
                    f"\n_Only the first 100 of "
                    f"{len(incomplete_files):,} files are shown._\n"
                )
        else:
            out.write(
                "Every extracted audio file contains all four "
                "selected text fields.\n"
            )

        out.write("\n## 9. Release-Level Completeness\n\n")

        out.write(
            "| Release | Files | ARTIST | ALBUMARTIST | "
            "COMPOSER | TITLE |\n"
        )
        out.write("|---|---:|---:|---:|---:|---:|\n")

        for release in sorted(release_files):
            values = []

            for field in TEXT_FIELDS:
                total, present = (
                    release_field_counts[release][field]
                )

                values.append(
                    f"{present}/{total}"
                )

            out.write(
                f"| {release} | "
                f"{release_files[release]} | "
                f"{values[0]} | "
                f"{values[1]} | "
                f"{values[2]} | "
                f"{values[3]} |\n"
            )

        out.write("\n## 10. Interpretation Notes\n\n")

        out.write(
            "The results in this report are observations from the "
            "current Crackling Tunes collection. They should be "
            "used to formulate and test ingest hypotheses.\n\n"
        )

        out.write(
            "A recurring source pattern should not automatically "
            "become a transformation rule. Candidate rules should "
            "be evaluated against multiple releases and against "
            "known exceptions before being incorporated into the "
            "ingest mapping.\n\n"
        )

        out.write(
            "Audio format is treated as an observed property of "
            "each file. The collection may contain different "
            "download formats because subscribers can select "
            "their preferred format. Format therefore should not "
            "be used as an identity distinction by itself.\n"
        )

    print(
        f"Analyzed {len(file_rows):,} audio files "
        f"from {len(release_files):,} releases."
    )
    print(f"Report written: {args.output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())