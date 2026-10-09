"""Rev B C builder contract, evidence preservation and Rev A compatibility."""
import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / '08_tools/ingestion/build_library_cards_from_rosetta.py'
MAPS = ROOT / '01_docs/05_Ingestion'


def write_csv(path, rows):
    with path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def build(tmp_path, revision, history=False):
    source = tmp_path / 'source.csv'
    observations = tmp_path / 'observations.csv'
    write_csv(source, [dict(source_id='TEST_COLLECTION', relative_path='A/track.flac',
                            filename='track.flac', asset_acceptance='RETAIN',
                            source_root='M:/collection')])
    record = dict(run_id='RUN1', source_id='TEST_COLLECTION',
                  source_record='A/track.flac', rule_id='title-rule',
                  source_value='Título original', decoded_value='Título',
                  target_entity='Composition', target_property='title',
                  target_relationship='', semantic_term='title',
                  assurance='source', evidence_basis='filename',
                  representation_level='source', source_element='title',
                  source_field='filename', information_class='CORE',
                  operation='COPY', decoder='scalar',
                  preserve_source_value='yes', status='EMITTED',
                  processing_outcome='PRESERVED', outcome_reason='', residual='')
    write_csv(observations, [record])
    args = [sys.executable, str(BUILDER), str(source), '--public-map',
            str(MAPS / f'MusicStewardship_Library_Card_CSV_Field_Translation_Map_Rev{revision}.csv'),
            '--interface-revision', revision, '--observations', str(observations),
            '--run-id', 'RUN2' if history else 'RUN1',
            '--output', str(tmp_path / f'cards_{revision}.csv'),
            '--report', str(tmp_path / f'report_{revision}.json')]
    if history:
        processing = tmp_path / 'processing_log.csv'
        write_csv(processing, [dict(run_id='RUN1', source_id='TEST_COLLECTION',
                                    source_record='A/track.flac', rule_id='title-rule',
                                    work_item_id='work-1', status='COMPLETE',
                                    observation_count='1')])
        args.extend(['--processing-log', str(processing)])
    subprocess.run(args, check=True, capture_output=True, text=True)
    with (tmp_path / f'cards_{revision}.csv').open(encoding='utf-8-sig', newline='') as handle:
        return next(csv.DictReader(handle)), record


def test_rev_b_retains_complete_observations_and_source_identity(tmp_path):
    card, observation = build(tmp_path, 'B')
    assert card['source_id'] == 'TEST_COLLECTION'
    assert card['source_record'] == 'A/track.flac'
    assert json.loads(card['semantic_observations']) == [observation]
    assert json.loads(card['title']) == ['Título']
    assert card['library_card_interface_revision'] == 'B'


def test_rev_a_and_b_preserve_identity_and_existing_values(tmp_path):
    a, _ = build(tmp_path, 'A')
    b, _ = build(tmp_path, 'B')
    assert len(a) == 33 and len(b) == 36
    assert a['source_object_id'] == b['source_object_id']
    for key in a:
        if key != 'library_card_interface_revision':
            assert a[key] == b[key], key


def test_rev_b_history_selection_retains_prior_observations(tmp_path):
    card, observation = build(tmp_path, 'B', history=True)
    assert json.loads(card['semantic_observations']) == [observation]
