"""Tests for completeness checking."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(r"C:\Projects\MusicStewardship")
SRC = PROJECT_ROOT / "04_src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def test_completeness_stub_exists():
    from ingestion.completeness.checker import CompletenessChecker

    assert CompletenessChecker is not None

def test_completeness_checker_can_be_created():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    assert checker is not None


def test_completeness_checker_exposes_expected_destinations():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    assert checker.DESTINATIONS == {
        "COMMON_MODEL",
        "EXTRA_OVERLAY",
        "IGNORED",
        "UNACCOUNTED",
    }

def test_completeness_checker_accepts_empty_record():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check({})

    assert result == {}

def test_completeness_checker_accepts_record_with_values():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    record = {
        "title": "Example",
        "artist": "Example Artist",
    }

    result = checker.check(record)

    assert result == record

def test_completeness_checker_classifies_common_model_fields():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check(
        {"title": "Example"},
        field_destinations={"title": "COMMON_MODEL"},
    )

    assert result == {
        "title": "COMMON_MODEL",
    }

def check(self, record, field_destinations=None):
    """Classify record fields by their declared destination."""
    if field_destinations is None:
        return record

    return {
        field: field_destinations[field]
        for field in record
        if field in field_destinations
    }

    checker = CompletenessChecker()

    result = checker.check(
        {"source_note": "Original source note"},
        field_destinations={"source_note": "EXTRA_OVERLAY"},
    )

    assert result == {
        "source_note": "EXTRA_OVERLAY",
    }

def test_completeness_checker_classifies_ignored_fields():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check(
        {"internal_note": "Do not retain"},
        field_destinations={"internal_note": "IGNORED"},
    )

    assert result == {
        "internal_note": "IGNORED",
    }

def test_completeness_checker_classifies_unaccounted_fields():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check(
        {"unknown_field": "Unknown"},
        field_destinations={"unknown_field": "UNACCOUNTED"},
    )

    assert result == {
        "unknown_field": "UNACCOUNTED",
    }

def test_completeness_checker_marks_missing_destination_as_unaccounted():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check(
        {"title": "Example", "artist": "Example Artist"},
        field_destinations={"title": "COMMON_MODEL"},
    )

    assert result == {
        "title": "COMMON_MODEL",
        "artist": "UNACCOUNTED",
    }

def test_completeness_checker_preserves_all_record_fields():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check(
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

    assert set(result) == {"title", "artist", "year"}

def test_completeness_checker_rejects_invalid_destination():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    try:
        checker.check(
            {"title": "Example"},
            field_destinations={"title": "NOT_A_DESTINATION"},
        )
    except ValueError:
        return

    assert False, "Expected ValueError for invalid destination"

def test_completeness_checker_rejects_invalid_destination_even_with_valid_fields():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    try:
        checker.check(
            {
                "title": "Example",
                "artist": "Example Artist",
            },
            field_destinations={
                "title": "COMMON_MODEL",
                "artist": "UNKNOWN_DESTINATION",
            },
        )
    except ValueError:
        return

    assert False, "Expected ValueError for invalid destination"

def test_completeness_checker_preserves_none_destination_mapping():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    record = {"title": "Example"}

    result = checker.check(record, field_destinations=None)

    assert result == record

def test_completeness_checker_with_empty_destination_mapping_marks_fields_unaccounted():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check(
        {"title": "Example", "artist": "Example Artist"},
        field_destinations={},
    )

    assert result == {
        "title": "UNACCOUNTED",
        "artist": "UNACCOUNTED",
    }

def test_completeness_checker_rejects_mapping_for_unknown_record_field():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    try:
        checker.check(
            {"title": "Example"},
            field_destinations={
                "title": "COMMON_MODEL",
                "artist": "EXTRA_OVERLAY",
            },
        )
    except ValueError:
        return

    assert False, "Expected ValueError for destination mapping of unknown field"

def test_completeness_checker_accepts_mapping_for_multiple_destinations():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check(
        {
            "title": "Example",
            "source_note": "Original source note",
            "internal_note": "Do not retain",
        },
        field_destinations={
            "title": "COMMON_MODEL",
            "source_note": "EXTRA_OVERLAY",
            "internal_note": "IGNORED",
        },
    )

    assert result == {
        "title": "COMMON_MODEL",
        "source_note": "EXTRA_OVERLAY",
        "internal_note": "IGNORED",
    }

def test_completeness_checker_does_not_modify_record():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    record = {
        "title": "Example",
        "artist": "Example Artist",
    }

    checker.check(
        record,
        field_destinations={"title": "COMMON_MODEL"},
    )

    assert record == {
        "title": "Example",
        "artist": "Example Artist",
    }

def test_completeness_checker_does_not_modify_field_destinations():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    field_destinations = {
        "title": "COMMON_MODEL",
    }

    checker.check(
        {"title": "Example"},
        field_destinations=field_destinations,
    )

    assert field_destinations == {
        "title": "COMMON_MODEL",
    }

def test_completeness_checker_preserves_record_field_order():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check(
        {
            "artist": "Example Artist",
            "title": "Example",
            "year": "2026",
        },
        field_destinations={
            "title": "COMMON_MODEL",
            "artist": "COMMON_MODEL",
        },
    )

    assert list(result) == ["artist", "title", "year"]

def test_completeness_checker_rejects_mapping_with_none_destination():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    try:
        checker.check(
            {"title": "Example"},
            field_destinations={"title": None},
        )
    except ValueError:
        return

    assert False, "Expected ValueError for None destination"

def test_completeness_checker_classifies_ignored_field():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check(
        {"comment": "Not needed"},
        field_destinations={"comment": "IGNORED"},
    )

    assert result == {
        "comment": "IGNORED",
    }

def test_completeness_checker_classifies_unaccounted_field():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check(
        {"comment": "No mapping"},
        field_destinations={},
    )

    assert result == {
        "comment": "UNACCOUNTED",
    }

def test_completeness_checker_classifies_multiple_extra_overlay_fields():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check(
        {
            "source_note": "Original note",
            "source_id": "ABC-123",
        },
        field_destinations={
            "source_note": "EXTRA_OVERLAY",
            "source_id": "EXTRA_OVERLAY",
        },
    )

    assert result == {
        "source_note": "EXTRA_OVERLAY",
        "source_id": "EXTRA_OVERLAY",
    }

def test_completeness_checker_mixes_mapped_and_unaccounted_fields():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check(
        {
            "title": "Example",
            "artist": "Example Artist",
            "source_note": "Original note",
        },
        field_destinations={
            "title": "COMMON_MODEL",
            "source_note": "EXTRA_OVERLAY",
        },
    )

    assert result == {
        "title": "COMMON_MODEL",
        "artist": "UNACCOUNTED",
        "source_note": "EXTRA_OVERLAY",
    }

def test_completeness_checker_returns_record_when_destinations_are_none():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    record = {
        "title": "Example",
        "artist": "Example Artist",
    }

    result = checker.check(record, field_destinations=None)

    assert result is record

def test_completeness_checker_returns_record_when_no_destinations_are_supplied():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    record = {
        "title": "Example",
        "artist": "Example Artist",
    }

    result = checker.check(record)

    assert result is record

def test_completeness_checker_accepts_non_music_field_names():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check(
        {
            "foo": "one",
            "bar": "two",
        },
        field_destinations={
            "foo": "COMMON_MODEL",
            "bar": "EXTRA_OVERLAY",
        },
    )

    assert result == {
        "foo": "COMMON_MODEL",
        "bar": "EXTRA_OVERLAY",
    }

def test_completeness_checker_accepts_numeric_field_values():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check(
        {
            "track_number": 7,
            "year": 1942,
        },
        field_destinations={
            "track_number": "COMMON_MODEL",
            "year": "COMMON_MODEL",
        },
    )

    assert result == {
        "track_number": "COMMON_MODEL",
        "year": "COMMON_MODEL",
    }

def test_completeness_checker_handles_empty_destination_mapping():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check(
        {
            "title": "Example",
            "artist": "Example Artist",
        },
        field_destinations={},
    )

    assert result == {
        "title": "UNACCOUNTED",
        "artist": "UNACCOUNTED",
    }

def test_completeness_checker_returns_empty_result_for_empty_record_with_empty_mapping():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check(
        {},
        field_destinations={},
    )

    assert result == {}

def test_completeness_checker_accepts_all_destination_types_in_one_record():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check(
        {
            "title": "Example",
            "source_note": "Original note",
            "ignored_field": "Ignore me",
            "unknown_field": "No mapping",
        },
        field_destinations={
            "title": "COMMON_MODEL",
            "source_note": "EXTRA_OVERLAY",
            "ignored_field": "IGNORED",
        },
    )

    assert result == {
        "title": "COMMON_MODEL",
        "source_note": "EXTRA_OVERLAY",
        "ignored_field": "IGNORED",
        "unknown_field": "UNACCOUNTED",
    }

def test_completeness_checker_accepts_unaccounted_as_explicit_destination():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check(
        {"title": "Example"},
        field_destinations={
            "title": "UNACCOUNTED",
        },
    )

    assert result == {
        "title": "UNACCOUNTED",
    }

def test_completeness_checker_accepts_boolean_field_values():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check(
        {"is_compilation": True},
        field_destinations={"is_compilation": "COMMON_MODEL"},
    )

    assert result == {
        "is_compilation": "COMMON_MODEL",
    }

def test_completeness_checker_accepts_list_field_values():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check(
        {"artists": ["Artist One", "Artist Two"]},
        field_destinations={"artists": "EXTRA_OVERLAY"},
    )

    assert result == {
        "artists": "EXTRA_OVERLAY",
    }

def test_completeness_checker_accepts_tuple_field_values():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check(
        {"aliases": ("Artist One", "Artist Two")},
        field_destinations={"aliases": "EXTRA_OVERLAY"},
    )

    assert result == {
        "aliases": "EXTRA_OVERLAY",
    }

def test_completeness_checker_accepts_dict_field_values():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check(
        {"metadata": {"source": "example"}},
        field_destinations={"metadata": "EXTRA_OVERLAY"},
    )

    assert result == {
        "metadata": "EXTRA_OVERLAY",
    }

def test_completeness_checker_accepts_single_field_record():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check(
        {"title": "Example"},
        field_destinations={"title": "COMMON_MODEL"},
    )

    assert result == {
        "title": "COMMON_MODEL",
    }

def test_completeness_checker_accepts_field_names_with_spaces():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check(
        {"source note": "Original note"},
        field_destinations={"source note": "EXTRA_OVERLAY"},
    )

    assert result == {
        "source note": "EXTRA_OVERLAY",
    }

def test_completeness_checker_accepts_unicode_field_name():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check(
        {"título": "Example"},
        field_destinations={"título": "COMMON_MODEL"},
    )

    assert result == {
        "título": "COMMON_MODEL",
    }

def test_completeness_checker_accepts_unicode_field_value():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check(
        {"title": "Canción de amor"},
        field_destinations={"title": "COMMON_MODEL"},
    )

    assert result == {
        "title": "COMMON_MODEL",
    }

def test_completeness_checker_treats_field_names_as_case_sensitive():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check(
        {
            "title": "Example",
            "Title": "Another Example",
        },
        field_destinations={
            "title": "COMMON_MODEL",
        },
    )

    assert result == {
        "title": "COMMON_MODEL",
        "Title": "UNACCOUNTED",
    }

def test_completeness_checker_rejects_case_mismatched_mapping():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    try:
        checker.check(
            {"title": "Example"},
            field_destinations={"Title": "COMMON_MODEL"},
        )
    except ValueError:
        return

    assert False, "Expected ValueError for case-mismatched field mapping"

def test_completeness_checker_accepts_integer_field_name():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check(
        {1: "Example"},
        field_destinations={1: "COMMON_MODEL"},
    )

    assert result == {
        1: "COMMON_MODEL",
    }

def test_completeness_checker_accepts_tuple_field_name():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    field = ("source", "title")

    result = checker.check(
        {field: "Example"},
        field_destinations={field: "EXTRA_OVERLAY"},
    )

    assert result == {
        field: "EXTRA_OVERLAY",
    }

def test_completeness_checker_accepts_boolean_field_name():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check(
        {True: "Example"},
        field_destinations={True: "COMMON_MODEL"},
    )

    assert result == {
        True: "COMMON_MODEL",
    }

def test_completeness_checker_accepts_none_field_name():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check(
        {None: "Example"},
        field_destinations={None: "EXTRA_OVERLAY"},
    )

    assert result == {
        None: "EXTRA_OVERLAY",
    }

def test_completeness_checker_accepts_false_field_value():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check(
        {"flag": False},
        field_destinations={"flag": "COMMON_MODEL"},
    )

    assert result == {
        "flag": "COMMON_MODEL",
    }


def test_completeness_checker_accepts_zero_field_value():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check(
        {"count": 0},
        field_destinations={"count": "COMMON_MODEL"},
    )

    assert result == {
        "count": "COMMON_MODEL",
    }


def test_completeness_checker_accepts_empty_list_field_value():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check(
        {"artists": []},
        field_destinations={"artists": "EXTRA_OVERLAY"},
    )

    assert result == {
        "artists": "EXTRA_OVERLAY",
    }


def test_completeness_checker_accepts_empty_dict_field_value():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check(
        {"metadata": {}},
        field_destinations={"metadata": "EXTRA_OVERLAY"},
    )

    assert result == {
        "metadata": "EXTRA_OVERLAY",
    }


def test_completeness_checker_accepts_multiline_string_value():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check(
        {"note": "Line one\nLine two"},
        field_destinations={"note": "EXTRA_OVERLAY"},
    )

    assert result == {
        "note": "EXTRA_OVERLAY",
    }


def test_completeness_checker_accepts_long_string_value():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    value = "Example " * 100

    result = checker.check(
        {"note": value},
        field_destinations={"note": "EXTRA_OVERLAY"},
    )

    assert result == {
        "note": "EXTRA_OVERLAY",
    }

def test_completeness_checker_rejects_none_record():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    try:
        checker.check(None)
    except TypeError:
        return

    assert False, "Expected TypeError for None record"


def test_completeness_checker_rejects_non_mapping_record():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    try:
        checker.check(["title", "artist"])
    except TypeError:
        return

    assert False, "Expected TypeError for non-mapping record"

def test_completeness_checker_returns_all_unaccounted_with_empty_mapping():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check(
        {
            "title": "Example",
            "artist": "Example Artist",
        },
        field_destinations={},
    )

    assert result == {
        "title": "UNACCOUNTED",
        "artist": "UNACCOUNTED",
    }


def test_completeness_checker_classifies_mixed_mapped_and_unmapped_fields():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check(
        {
            "title": "Example",
            "artist": "Example Artist",
            "year": "2026",
        },
        field_destinations={
            "title": "COMMON_MODEL",
        },
    )

    assert result == {
        "title": "COMMON_MODEL",
        "artist": "UNACCOUNTED",
        "year": "UNACCOUNTED",
    }


def test_completeness_checker_does_not_modify_original_record():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    record = {
        "title": "Example",
        "artist": "Example Artist",
    }

    checker.check(
        record,
        field_destinations={
            "title": "COMMON_MODEL",
        },
    )

    assert record == {
        "title": "Example",
        "artist": "Example Artist",
    }


def test_completeness_checker_returns_new_result_mapping():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    record = {
        "title": "Example",
    }

    result = checker.check(
        record,
        field_destinations={
            "title": "COMMON_MODEL",
        },
    )

    assert result is not record

def test_completeness_checker_classifies_ignored_field():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check(
        {"internal_note": "Do not import"},
        field_destinations={"internal_note": "IGNORED"},
    )

    assert result == {
        "internal_note": "IGNORED",
    }


def test_completeness_checker_classifies_explicit_unaccounted_field():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check(
        {"unknown_field": "Example"},
        field_destinations={"unknown_field": "UNACCOUNTED"},
    )

    assert result == {
        "unknown_field": "UNACCOUNTED",
    }


def test_completeness_checker_classifies_all_four_destinations():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check(
        {
            "title": "Example",
            "source_note": "Original note",
            "internal_note": "Ignore this",
            "unknown": "Unmapped",
        },
        field_destinations={
            "title": "COMMON_MODEL",
            "source_note": "EXTRA_OVERLAY",
            "internal_note": "IGNORED",
            "unknown": "UNACCOUNTED",
        },
    )

    assert result == {
        "title": "COMMON_MODEL",
        "source_note": "EXTRA_OVERLAY",
        "internal_note": "IGNORED",
        "unknown": "UNACCOUNTED",
    }


def test_completeness_checker_allows_repeated_destination():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check(
        {
            "title": "Example",
            "artist": "Example Artist",
            "album": "Example Album",
        },
        field_destinations={
            "title": "COMMON_MODEL",
            "artist": "COMMON_MODEL",
            "album": "COMMON_MODEL",
        },
    )

    assert result == {
        "title": "COMMON_MODEL",
        "artist": "COMMON_MODEL",
        "album": "COMMON_MODEL",
    }

def test_completeness_checker_preserves_record_field_order():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check(
        {
            "year": "2026",
            "artist": "Example Artist",
            "title": "Example",
        },
        field_destinations={
            "title": "COMMON_MODEL",
            "artist": "COMMON_MODEL",
        },
    )

    assert list(result) == ["year", "artist", "title"]


def test_completeness_checker_does_not_modify_destination_mapping():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    field_destinations = {
        "title": "COMMON_MODEL",
    }

    checker.check(
        {"title": "Example"},
        field_destinations=field_destinations,
    )

    assert field_destinations == {
        "title": "COMMON_MODEL",
    }


def test_completeness_checker_result_can_be_modified_independently():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    record = {
        "title": "Example",
    }

    result = checker.check(
        record,
        field_destinations={
            "title": "COMMON_MODEL",
        },
    )

    result["title"] = "IGNORED"

    assert record == {
        "title": "Example",
    }


def test_completeness_checker_accepts_multiple_extra_overlay_fields():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check(
        {
            "source_note": "Original note",
            "source_id": "ABC-123",
            "source_url": "example",
        },
        field_destinations={
            "source_note": "EXTRA_OVERLAY",
            "source_id": "EXTRA_OVERLAY",
            "source_url": "EXTRA_OVERLAY",
        },
    )

    assert result == {
        "source_note": "EXTRA_OVERLAY",
        "source_id": "EXTRA_OVERLAY",
        "source_url": "EXTRA_OVERLAY",
    }

def test_completeness_checker_rejects_non_mapping_destinations():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    try:
        checker.check(
            {"title": "Example"},
            field_destinations=["title"],
        )
    except TypeError:
        return

    assert False, "Expected TypeError for non-mapping field_destinations"


def test_completeness_checker_rejects_none_destination_mapping_entry():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    try:
        checker.check(
            {"title": "Example"},
            field_destinations={"title": None},
        )
    except ValueError:
        return

    assert False, "Expected ValueError for None destination"


def test_completeness_checker_rejects_empty_string_destination():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    try:
        checker.check(
            {"title": "Example"},
            field_destinations={"title": ""},
        )
    except ValueError:
        return

    assert False, "Expected ValueError for empty destination"

def test_completeness_checker_rejects_none_destination():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    try:
        checker.check(
            {"title": "Example"},
            field_destinations={"title": None},
        )
    except ValueError:
        return

    assert False, "Expected ValueError for None destination"


def test_completeness_checker_rejects_empty_string_destination():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    try:
        checker.check(
            {"title": "Example"},
            field_destinations={"title": ""},
        )
    except ValueError:
        return

    assert False, "Expected ValueError for empty destination"


def test_completeness_checker_rejects_numeric_destination():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    try:
        checker.check(
            {"title": "Example"},
            field_destinations={"title": 1},
        )
    except ValueError:
        return

    assert False, "Expected ValueError for numeric destination"


def test_completeness_checker_rejects_false_destination():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    try:
        checker.check(
            {"title": "Example"},
            field_destinations={"title": False},
        )
    except ValueError:
        return

    assert False, "Expected ValueError for boolean destination"

def test_completeness_checker_accepts_common_model_destination():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    assert checker.check(
        {"field": "value"},
        field_destinations={"field": "COMMON_MODEL"},
    ) == {"field": "COMMON_MODEL"}


def test_completeness_checker_accepts_extra_overlay_destination():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    assert checker.check(
        {"field": "value"},
        field_destinations={"field": "EXTRA_OVERLAY"},
    ) == {"field": "EXTRA_OVERLAY"}


def test_completeness_checker_accepts_ignored_destination():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    assert checker.check(
        {"field": "value"},
        field_destinations={"field": "IGNORED"},
    ) == {"field": "IGNORED"}


def test_completeness_checker_accepts_unaccounted_destination():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    assert checker.check(
        {"field": "value"},
        field_destinations={"field": "UNACCOUNTED"},
    ) == {"field": "UNACCOUNTED"}


def test_completeness_checker_classifies_fully_mapped_record():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check(
        {
            "title": "Example",
            "artist": "Example Artist",
            "source_note": "Original note",
            "internal": "Ignore",
        },
        field_destinations={
            "title": "COMMON_MODEL",
            "artist": "COMMON_MODEL",
            "source_note": "EXTRA_OVERLAY",
            "internal": "IGNORED",
        },
    )

    assert result == {
        "title": "COMMON_MODEL",
        "artist": "COMMON_MODEL",
        "source_note": "EXTRA_OVERLAY",
        "internal": "IGNORED",
    }

def test_completeness_checker_uses_declared_destination_over_default():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check(
        {"title": "Example"},
        field_destinations={"title": "EXTRA_OVERLAY"},
    )

    assert result["title"] == "EXTRA_OVERLAY"


def test_completeness_checker_does_not_infer_destination_from_field_name():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check(
        {"source_note": "Original note"},
        field_destinations={},
    )

    assert result["source_note"] == "UNACCOUNTED"


def test_completeness_checker_classifies_fields_independently():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check(
        {
            "title": "Example",
            "artist": "Example Artist",
            "note": "Original note",
        },
        field_destinations={
            "title": "COMMON_MODEL",
            "artist": "EXTRA_OVERLAY",
        },
    )

    assert result["title"] == "COMMON_MODEL"
    assert result["artist"] == "EXTRA_OVERLAY"
    assert result["note"] == "UNACCOUNTED"


def test_completeness_checker_allows_same_field_value_with_different_destination():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check(
        {"title": "Example"},
        field_destinations={"title": "IGNORED"},
    )

    assert result == {
        "title": "IGNORED",
    }


def test_completeness_checker_returns_only_field_destinations():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check(
        {"title": "Example", "artist": "Example Artist"},
        field_destinations={
            "title": "COMMON_MODEL",
            "artist": "EXTRA_OVERLAY",
        },
    )

    assert set(result.values()) == {
        "COMMON_MODEL",
        "EXTRA_OVERLAY",
    }

def test_completeness_checker_groups_common_model_fields():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check(
        {
            "title": "Example",
            "artist": "Example Artist",
            "source_note": "Original note",
        },
        field_destinations={
            "title": "COMMON_MODEL",
            "artist": "COMMON_MODEL",
            "source_note": "EXTRA_OVERLAY",
        },
    )

    assert result == {
        "title": "COMMON_MODEL",
        "artist": "COMMON_MODEL",
        "source_note": "EXTRA_OVERLAY",
    }


def test_completeness_checker_groups_extra_overlay_fields():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check(
        {
            "source_note": "Original note",
            "source_id": "ABC-123",
        },
        field_destinations={
            "source_note": "EXTRA_OVERLAY",
            "source_id": "EXTRA_OVERLAY",
        },
    )

    assert result == {
        "source_note": "EXTRA_OVERLAY",
        "source_id": "EXTRA_OVERLAY",
    }


def test_completeness_checker_groups_ignored_fields():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check(
        {
            "internal_note": "Ignore",
            "temporary": "Discard",
        },
        field_destinations={
            "internal_note": "IGNORED",
            "temporary": "IGNORED",
        },
    )

    assert result == {
        "internal_note": "IGNORED",
        "temporary": "IGNORED",
    }


def test_completeness_checker_groups_unaccounted_fields():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check(
        {
            "title": "Example",
            "unknown_one": "A",
            "unknown_two": "B",
        },
        field_destinations={
            "title": "COMMON_MODEL",
        },
    )

    assert result == {
        "title": "COMMON_MODEL",
        "unknown_one": "UNACCOUNTED",
        "unknown_two": "UNACCOUNTED",
    }

def test_completeness_checker_classifies_none_value_by_field_destination():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check(
        {"title": None},
        field_destinations={"title": "COMMON_MODEL"},
    )

    assert result == {
        "title": "COMMON_MODEL",
    }

def test_completeness_checker_classifies_empty_string_by_field_destination():
    from ingestion.completeness.checker import CompletenessChecker

    checker = CompletenessChecker()

    result = checker.check(
        {"title": ""},
        field_destinations={"title": "COMMON_MODEL"},
    )

    assert result == {
        "title": "COMMON_MODEL",
    }

