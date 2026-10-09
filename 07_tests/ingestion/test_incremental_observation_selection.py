"""Regression tests for history-aware Rosetta observation selection.

Install as 07_tests/ingestion/test_incremental_observation_selection.py.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / '08_tools' / 'ingestion'))
from build_library_cards_from_rosetta import select_current_observations


def log(run, count, status='COMPLETE', work='work-1', rule='rule-1'):
    return dict(run_id=run, source_id='source-1', source_record='track.flac',
                rule_id=rule, work_item_id=work, status=status,
                observation_count=str(count))


def obs(run, value, rule='rule-1'):
    return dict(run_id=run, source_id='source-1', source_record='track.flac',
                rule_id=rule, decoded_value=value)


def test_skipped_second_run_preserves_first_run_observations():
    assert select_current_observations([obs('RUN1', 'title')],
                                       [log('RUN1', 1)]) == [obs('RUN1', 'title')]


def test_new_success_supersedes_old_observation():
    rows = [obs('RUN1', 'old'), obs('RUN2', 'new')]
    assert select_current_observations(rows, [log('RUN1', 1), log('RUN2', 1)]) == [rows[1]]


def test_zero_observation_success_supersedes_old_observation():
    assert select_current_observations([obs('RUN1', 'old')],
                                       [log('RUN1', 1), log('RUN2', 0)]) == []


def test_failed_attempt_does_not_supersede_last_success():
    rows = [obs('RUN1', 'valid')]
    assert select_current_observations(rows, [log('RUN1', 1), log('RUN2', 0, 'FAILED')]) == rows


def test_reused_attempt_identity_is_rejected():
    import pytest
    with pytest.raises(ValueError, match='Ambiguous processing history'):
        select_current_observations([obs('RUN1', 'old')],
                                    [log('RUN1', 1), log('RUN1', 1)])


def test_missing_observations_are_rejected():
    import pytest
    with pytest.raises(ValueError, match='observation-count mismatch'):
        select_current_observations([], [log('RUN1', 1)])
