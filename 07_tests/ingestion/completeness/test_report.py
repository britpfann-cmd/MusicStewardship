"""Tests for completeness reporting."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(r"C:\Projects\MusicStewardship")
SRC = PROJECT_ROOT / "04_src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def test_completeness_report_can_be_created():
    from ingestion.completeness.report import CompletenessReport

    report = CompletenessReport()

    assert report is not None


def test_completeness_report_starts_with_empty_collections():
    from ingestion.completeness.report import CompletenessReport

    report = CompletenessReport()

    assert report.accounted == []
    assert report.unaccounted == []
    assert report.patterns == []


def test_completeness_report_passes_when_nothing_is_unaccounted():
    from ingestion.completeness.report import CompletenessReport

    report = CompletenessReport()

    assert report.passed is True


def test_completeness_report_fails_when_something_is_unaccounted():
    from ingestion.completeness.report import CompletenessReport

    report = CompletenessReport()
    report.unaccounted.append("artist")

    assert report.passed is False


def test_completeness_report_summary_starts_empty():
    from ingestion.completeness.report import CompletenessReport

    report = CompletenessReport()

    assert report.summary() == {
        "passed": True,
        "accounted": 0,
        "unaccounted": 0,
        "patterns": 0,
    }


def test_completeness_report_summary_counts_entries():
    from ingestion.completeness.report import CompletenessReport

    report = CompletenessReport()
    report.accounted.extend(["title", "artist"])
    report.unaccounted.append("year")
    report.patterns.extend(["pattern_a", "pattern_b", "pattern_c"])

    assert report.summary() == {
        "passed": False,
        "accounted": 2,
        "unaccounted": 1,
        "patterns": 3,
    }

def test_completeness_report_allows_multiple_accounted_entries():
    from ingestion.completeness.report import CompletenessReport

    report = CompletenessReport()
    report.accounted.extend(["title", "artist", "album"])

    assert report.accounted == ["title", "artist", "album"]


def test_completeness_report_allows_multiple_unaccounted_entries():
    from ingestion.completeness.report import CompletenessReport

    report = CompletenessReport()
    report.unaccounted.extend(["year", "country"])

    assert report.unaccounted == ["year", "country"]


def test_completeness_report_allows_multiple_patterns():
    from ingestion.completeness.report import CompletenessReport

    report = CompletenessReport()
    report.patterns.extend(["pattern_a", "pattern_b"])

    assert report.patterns == ["pattern_a", "pattern_b"]


def test_completeness_report_passed_changes_when_unaccounted_changes():
    from ingestion.completeness.report import CompletenessReport

    report = CompletenessReport()

    assert report.passed is True

    report.unaccounted.append("year")

    assert report.passed is False

    report.unaccounted.clear()

    assert report.passed is True


def test_completeness_report_summary_updates_after_entries_change():
    from ingestion.completeness.report import CompletenessReport

    report = CompletenessReport()

    report.accounted.append("title")

    assert report.summary()["accounted"] == 1

    report.accounted.append("artist")

    assert report.summary()["accounted"] == 2


def test_completeness_report_summary_tracks_all_collections_independently():
    from ingestion.completeness.report import CompletenessReport

    report = CompletenessReport()

    report.accounted.extend(["title", "artist"])
    report.unaccounted.append("year")
    report.patterns.extend(["p1", "p2"])

    summary = report.summary()

    assert summary["accounted"] == 2
    assert summary["unaccounted"] == 1
    assert summary["patterns"] == 2
    assert summary["passed"] is False

def test_completeness_reports_do_not_share_accounted_entries():
    from ingestion.completeness.report import CompletenessReport

    first = CompletenessReport()
    second = CompletenessReport()

    first.accounted.append("title")

    assert first.accounted == ["title"]
    assert second.accounted == []


def test_completeness_reports_do_not_share_unaccounted_entries():
    from ingestion.completeness.report import CompletenessReport

    first = CompletenessReport()
    second = CompletenessReport()

    first.unaccounted.append("artist")

    assert first.unaccounted == ["artist"]
    assert second.unaccounted == []


def test_completeness_reports_do_not_share_patterns():
    from ingestion.completeness.report import CompletenessReport

    first = CompletenessReport()
    second = CompletenessReport()

    first.patterns.append("pattern_a")

    assert first.patterns == ["pattern_a"]
    assert second.patterns == []


def test_completeness_report_passed_is_instance_specific():
    from ingestion.completeness.report import CompletenessReport

    first = CompletenessReport()
    second = CompletenessReport()

    first.unaccounted.append("artist")

    assert first.passed is False
    assert second.passed is True


def test_completeness_report_summary_is_instance_specific():
    from ingestion.completeness.report import CompletenessReport

    first = CompletenessReport()
    second = CompletenessReport()

    first.accounted.extend(["title", "artist"])
    first.unaccounted.append("year")

    assert first.summary() == {
        "passed": False,
        "accounted": 2,
        "unaccounted": 1,
        "patterns": 0,
    }

    assert second.summary() == {
        "passed": True,
        "accounted": 0,
        "unaccounted": 0,
        "patterns": 0,
    }


def test_completeness_report_empty_collections_remain_independent_after_clear():
    from ingestion.completeness.report import CompletenessReport

    first = CompletenessReport()
    second = CompletenessReport()

    first.accounted.extend(["title", "artist"])
    second.accounted.append("album")

    first.accounted.clear()

    assert first.accounted == []
    assert second.accounted == ["album"]

def test_completeness_report_can_be_created_from_classification():
    from ingestion.completeness.report import CompletenessReport

    classification = {
        "title": "COMMON_MODEL",
        "artist": "COMMON_MODEL",
    }

    report = CompletenessReport.from_classification(classification)

    assert report.accounted == ["title", "artist"]


def test_completeness_report_classification_marks_unaccounted_fields():
    from ingestion.completeness.report import CompletenessReport

    classification = {
        "title": "COMMON_MODEL",
        "artist": "UNACCOUNTED",
    }

    report = CompletenessReport.from_classification(classification)

    assert report.accounted == ["title"]
    assert report.unaccounted == ["artist"]


def test_completeness_report_classification_places_extra_overlay_fields_in_accounted():
    from ingestion.completeness.report import CompletenessReport

    classification = {
        "title": "COMMON_MODEL",
        "source_note": "EXTRA_OVERLAY",
    }

    report = CompletenessReport.from_classification(classification)

    assert report.accounted == ["title", "source_note"]
    assert report.unaccounted == []


def test_completeness_report_classification_places_ignored_fields_in_accounted():
    from ingestion.completeness.report import CompletenessReport

    classification = {
        "title": "COMMON_MODEL",
        "internal_note": "IGNORED",
    }

    report = CompletenessReport.from_classification(classification)

    assert report.accounted == ["title", "internal_note"]
    assert report.unaccounted == []


def test_completeness_report_classification_preserves_field_order():
    from ingestion.completeness.report import CompletenessReport

    classification = {
        "year": "UNACCOUNTED",
        "title": "COMMON_MODEL",
        "artist": "EXTRA_OVERLAY",
    }

    report = CompletenessReport.from_classification(classification)

    assert report.unaccounted == ["year"]
    assert report.accounted == ["title", "artist"]


def test_completeness_report_classification_produces_failed_report_when_unaccounted_exists():
    from ingestion.completeness.report import CompletenessReport

    classification = {
        "title": "COMMON_MODEL",
        "artist": "UNACCOUNTED",
    }

    report = CompletenessReport.from_classification(classification)

    assert report.passed is False
    assert report.summary() == {
        "passed": False,
        "accounted": 1,
        "unaccounted": 1,
        "patterns": 0,
    }

def test_completeness_report_from_classification_accepts_empty_mapping():
    from ingestion.completeness.report import CompletenessReport

    report = CompletenessReport.from_classification({})

    assert report.accounted == []
    assert report.unaccounted == []
    assert report.patterns == []
    assert report.passed is True


def test_completeness_report_from_classification_preserves_duplicate_fields_impossible():
    from ingestion.completeness.report import CompletenessReport

    classification = {
        "title": "COMMON_MODEL",
        "artist": "COMMON_MODEL",
    }

    report = CompletenessReport.from_classification(classification)

    assert len(report.accounted) == 2


def test_completeness_report_from_classification_rejects_none():
    from ingestion.completeness.report import CompletenessReport

    try:
        CompletenessReport.from_classification(None)
    except TypeError:
        return

    assert False, "Expected TypeError for None classification"


def test_completeness_report_from_classification_rejects_non_mapping():
    from ingestion.completeness.report import CompletenessReport

    try:
        CompletenessReport.from_classification(["title", "artist"])
    except TypeError:
        return

    assert False, "Expected TypeError for non-mapping classification"


def test_completeness_report_from_classification_rejects_invalid_destination():
    from ingestion.completeness.report import CompletenessReport

    try:
        CompletenessReport.from_classification(
            {"title": "NOT_A_DESTINATION"}
        )
    except ValueError:
        return

    assert False, "Expected ValueError for invalid destination"


def test_completeness_report_from_classification_rejects_mixed_invalid_destination():
    from ingestion.completeness.report import CompletenessReport

    try:
        CompletenessReport.from_classification(
            {
                "title": "COMMON_MODEL",
                "artist": "UNKNOWN_DESTINATION",
            }
        )
    except ValueError:
        return

    assert False, "Expected ValueError for invalid destination"

def test_completeness_checker_can_produce_report():
    from ingestion.completeness.checker import CompletenessChecker
    from ingestion.completeness.report import CompletenessReport

    checker = CompletenessChecker()

    classification = checker.check(
        {"title": "Example"},
        field_destinations={"title": "COMMON_MODEL"},
    )

    report = CompletenessReport.from_classification(classification)

    assert report.passed is True


def test_completeness_checker_classification_can_produce_unaccounted_report():
    from ingestion.completeness.checker import CompletenessChecker
    from ingestion.completeness.report import CompletenessReport

    checker = CompletenessChecker()

    classification = checker.check(
        {"title": "Example", "artist": "Example Artist"},
        field_destinations={"title": "COMMON_MODEL"},
    )

    report = CompletenessReport.from_classification(classification)

    assert report.passed is False
    assert report.unaccounted == ["artist"]


def test_completeness_checker_classification_preserves_accounted_fields_in_report():
    from ingestion.completeness.checker import CompletenessChecker
    from ingestion.completeness.report import CompletenessReport

    checker = CompletenessChecker()

    classification = checker.check(
        {
            "title": "Example",
            "artist": "Example Artist",
            "source_note": "Original",
        },
        field_destinations={
            "title": "COMMON_MODEL",
            "artist": "COMMON_MODEL",
            "source_note": "EXTRA_OVERLAY",
        },
    )

    report = CompletenessReport.from_classification(classification)

    assert report.accounted == ["title", "artist", "source_note"]
    assert report.unaccounted == []


def test_completeness_checker_classification_preserves_ignored_fields_in_report():
    from ingestion.completeness.checker import CompletenessChecker
    from ingestion.completeness.report import CompletenessReport

    checker = CompletenessChecker()

    classification = checker.check(
        {
            "title": "Example",
            "internal_note": "Ignore this",
        },
        field_destinations={
            "title": "COMMON_MODEL",
            "internal_note": "IGNORED",
        },
    )

    report = CompletenessReport.from_classification(classification)

    assert report.accounted == ["title", "internal_note"]
    assert report.unaccounted == []


def test_completeness_checker_classification_produces_expected_summary():
    from ingestion.completeness.checker import CompletenessChecker
    from ingestion.completeness.report import CompletenessReport

    checker = CompletenessChecker()

    classification = checker.check(
        {
            "title": "Example",
            "artist": "Example Artist",
            "year": "2026",
        },
        field_destinations={
            "title": "COMMON_MODEL",
            "artist": "COMMON_MODEL",
        },
    )

    report = CompletenessReport.from_classification(classification)

    assert report.summary() == {
        "passed": False,
        "accounted": 2,
        "unaccounted": 1,
        "patterns": 0,
    }


def test_completeness_checker_and_report_form_complete_pipeline():
    from ingestion.completeness.checker import CompletenessChecker
    from ingestion.completeness.report import CompletenessReport

    checker = CompletenessChecker()

    classification = checker.check(
        {
            "title": "Example",
            "artist": "Example Artist",
        },
        field_destinations={
            "title": "COMMON_MODEL",
            "artist": "COMMON_MODEL",
        },
    )

    report = CompletenessReport.from_classification(classification)

    assert report.passed is True
    assert report.accounted == ["title", "artist"]
    assert report.unaccounted == []
    