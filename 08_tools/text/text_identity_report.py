#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MusicStewardship Text Identity Report

Reads Text Identity JSONL output and produces a human-readable Excel
workbook for review.

Sheets:
    Summary  - processing counts and correction statistics
    Concise  - compact record-level view
    Problems - records requiring human attention
    Full     - complete processing/provenance information

The report generator does not modify source data or the Names registry.
"""

import argparse
import json
from collections import Counter
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter


FULL_COLUMNS = [
    "record",
    "original_text",
    "corrected_text",
    "correction_applied",
    "corrections",
    "canonical_ref",
    "canonical_name",
    "canonical_status",
    "authority_source",
]

CONCISE_COLUMNS = [
    "record",
    "original_text",
    "corrected_text",
    "correction_applied",
    "canonical_name",
    "canonical_status",
    "review_reason",
]

PROBLEM_COLUMNS = [
    "record",
    "original_text",
    "corrected_text",
    "corrections",
    "canonical_ref",
    "canonical_name",
    "canonical_status",
    "authority_source",
    "review_reason",
    "reviewer_decision",
    "reviewer_notes",
]

REVIEW_STATUSES = {"PROVISIONAL", "UNRESOLVED"}


def load_jsonl(path: Path) -> list[dict]:
    """Load one JSON object per line from UTF-8 JSONL."""
    records = []

    with path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            line = line.rstrip("\r\n")

            if not line:
                continue

            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON on line {line_number}: {exc}"
                ) from exc

    return records


def correction_labels(records: list[dict]) -> Counter:
    """Count individual correction types."""
    counts = Counter()

    for record in records:
        for correction in record.get("corrections", []):
            counts[correction] += 1

    return counts


def review_reason(record: dict) -> str:
    """Return the human-review reason for a record."""
    status = record.get("canonical_status")

    if status == "UNRESOLVED":
        return "Identity not established"

    if status == "PROVISIONAL":
        return "Authority confirmation needed"

    return ""


def display_value(column_name: str, value):
    """Convert structured values to spreadsheet-friendly values."""
    if column_name == "corrections" and isinstance(value, list):
        return "; ".join(value)

    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)

    return value


def write_headers(sheet, columns: list[str]) -> None:
    """Write and format a worksheet header row."""
    for column_number, column_name in enumerate(columns, start=1):
        cell = sheet.cell(
            row=1,
            column=column_number,
            value=column_name,
        )
        cell.font = Font(bold=True)
        cell.fill = PatternFill(
            fill_type="solid",
            fgColor="D9EAF7",
        )
        cell.alignment = Alignment(
            horizontal="center",
            vertical="center",
            wrap_text=True,
        )

    sheet.row_dimensions[1].height = 30


def write_record_rows(
    sheet,
    records: list[dict],
    columns: list[str],
) -> None:
    """Write record rows to a worksheet."""
    for row_number, record in enumerate(records, start=2):
        for column_number, column_name in enumerate(
            columns,
            start=1,
        ):
            if column_name == "review_reason":
                value = review_reason(record)
            elif column_name == "reviewer_decision":
                value = ""
            elif column_name == "reviewer_notes":
                value = ""
            else:
                value = display_value(
                    column_name,
                    record.get(column_name),
                )

            sheet.cell(
                row=row_number,
                column=column_number,
                value=value,
            )

    if records:
        sheet.freeze_panes = "A2"
        sheet.auto_filter.ref = sheet.dimensions

    format_sheet(sheet)


def write_full_sheet(workbook: Workbook, records: list[dict]) -> None:
    """Write the complete processing/provenance view."""
    sheet = workbook.create_sheet("Full")

    write_headers(sheet, FULL_COLUMNS)
    write_record_rows(sheet, records, FULL_COLUMNS)


def write_concise_sheet(workbook: Workbook, records: list[dict]) -> None:
    """Write the compact record-level view."""
    sheet = workbook.create_sheet("Concise")

    write_headers(sheet, CONCISE_COLUMNS)
    write_record_rows(sheet, records, CONCISE_COLUMNS)


def write_problems_sheet(workbook: Workbook, records: list[dict]) -> None:
    """Write records requiring human attention."""
    sheet = workbook.create_sheet("Problems")

    problem_records = [
        record
        for record in records
        if record.get("canonical_status") in REVIEW_STATUSES
    ]

    write_headers(sheet, PROBLEM_COLUMNS)
    write_record_rows(sheet, problem_records, PROBLEM_COLUMNS)


def write_summary_sheet(workbook: Workbook, records: list[dict]) -> None:
    """Write processing summary statistics."""
    sheet = workbook.create_sheet("Summary")

    status_counts = Counter(
        record.get("canonical_status", "UNKNOWN")
        for record in records
    )

    changed_count = sum(
        bool(record.get("correction_applied"))
        for record in records
    )

    correction_counts = correction_labels(records)

    review_count = sum(
        record.get("canonical_status") in REVIEW_STATUSES
        for record in records
    )

    total = len(records)

    rows = [
        ("Metric", "Count"),
        ("Records processed", total),
        ("Records changed", changed_count),
        ("Records unchanged", total - changed_count),
        ("AUTHORIZED", status_counts.get("AUTHORIZED", 0)),
        ("PROVISIONAL", status_counts.get("PROVISIONAL", 0)),
        ("UNRESOLVED", status_counts.get("UNRESOLVED", 0)),
        ("Records requiring review", review_count),
    ]

    for correction, count in sorted(correction_counts.items()):
        rows.append(
            (f"Correction: {correction}", count)
        )

    for row_number, row in enumerate(rows, start=1):
        for column_number, value in enumerate(row, start=1):
            cell = sheet.cell(
                row=row_number,
                column=column_number,
                value=value,
            )

            if row_number == 1:
                cell.font = Font(bold=True)
                cell.fill = PatternFill(
                    fill_type="solid",
                    fgColor="D9EAF7",
                )

            cell.alignment = Alignment(
                vertical="top",
                wrap_text=True,
            )

    sheet.freeze_panes = "A2"

    sheet.column_dimensions["A"].width = 45
    sheet.column_dimensions["B"].width = 15


def format_sheet(sheet) -> None:
    """Apply useful widths, alignment, and filtering."""
    widths = {
        "A": 10,
        "B": 32,
        "C": 32,
        "D": 18,
        "E": 42,
        "F": 20,
        "G": 32,
        "H": 20,
        "I": 28,
        "J": 28,
        "K": 40,
    }

    for column_number, width in enumerate(
        widths.values(),
        start=1,
    ):
        column_letter = get_column_letter(column_number)
        sheet.column_dimensions[column_letter].width = width

    for row in sheet.iter_rows():
        for cell in row:
            cell.alignment = Alignment(
                vertical="top",
                wrap_text=True,
            )


def build_report(input_path: Path, output_path: Path) -> None:
    """Build the four-view Excel report."""
    records = load_jsonl(input_path)

    workbook = Workbook()

    # Remove the default worksheet.
    default_sheet = workbook.active
    workbook.remove(default_sheet)

    # Workbook order follows the operational reporting hierarchy.
    write_summary_sheet(workbook, records)
    write_concise_sheet(workbook, records)
    write_problems_sheet(workbook, records)
    write_full_sheet(workbook, records)

    workbook.save(output_path)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Create a four-view Excel report from "
            "Text Identity JSONL output."
        )
    )

    parser.add_argument(
        "input",
        type=Path,
        help="input JSONL file; output XLSX uses the same filename stem",
    )

    args = parser.parse_args()

    output_path = args.input.with_suffix(".xlsx")

    build_report(args.input, output_path)

    print(f"Report written: {output_path}")

    return 0