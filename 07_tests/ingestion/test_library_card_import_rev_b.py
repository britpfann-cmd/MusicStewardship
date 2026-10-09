"""Rev B contract tests for the existing D Library Card importer."""
from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / '04_src'))
from library_card_interface import certified_interface

spec = importlib.util.spec_from_file_location('library_card_import_rev_b_test', ROOT / '08_tools' / 'import' / 'library_card_import.py')
importer = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(importer)

OBS = {
    'run_id': 'RUN-001', 'source_id': 'TTT', 'source_record': 'sample.flac',
    'source_element': 'filename', 'source_field': 'filename',
    'source_value': 'Original Ástor.flac', 'rule_id': 'TEST-RULE-1',
    'semantic_term': 'title', 'representation_level': 'DECODED',
    'information_class': 'ASSOCIATED', 'operation': 'decode',
    'decoder': 'test_decoder', 'target_entity': 'Composition',
    'target_property': 'title', 'target_relationship': '',
    'assurance': 'DECODED', 'preserve_source_value': 'true',
    'decoded_value': 'Ástor', 'status': 'SUCCESS',
    'processing_outcome': 'SUCCESS', 'outcome_reason': '',
    'residual': '', 'evidence_basis': 'source filename',
}


def card_for(revision):
    contract = certified_interface(revision)
    card = {}
    for definition in contract.fields:
        field, cardinality = definition['Field'], definition['Cardinality']
        card[field] = '[]' if cardinality in {'0..n', '1..n'} else ''
        if cardinality == '1..n':
            card[field] = '["test"]'
        elif cardinality == '1':
            card[field] = 'test'
    card['library_card_interface_revision'] = revision
    card['source_object_id'] = 'SOURCE-001'
    card['source_object_key'] = 'TTT:sample.flac'
    if revision == 'B':
        card['source_id'] = 'TTT'
        card['source_record'] = 'sample.flac'
        card['semantic_observations'] = json.dumps([OBS], ensure_ascii=False)
    return card


def test_rev_b_contract_and_observation_roundtrip():
    contract = certified_interface('B')
    assert len(contract.field_names) == 36
    assert list(contract.field_names)[-3:] == ['source_id', 'source_record', 'semantic_observations']
    card = card_for('B')
    decoded = importer.decode_card(card)
    assert decoded['semantic_observations'] == [OBS]
    assert decoded['source_id'] == 'TTT'
    assert decoded['source_record'] == 'sample.flac'
    assert not [check for check in importer.verify_standard(card) if check[1] == 'FAIL']


def test_rev_a_remains_supported_without_rev_b_fields():
    card = card_for('A')
    decoded = importer.decode_card(card)
    assert decoded['library_card_interface_revision'] == 'A'
    assert 'semantic_observations' not in decoded
    assert 'source_id' not in decoded


def test_rev_b_rejects_non_array_semantic_observations():
    card = card_for('B')
    card['semantic_observations'] = json.dumps(OBS)
    with pytest.raises(ValueError, match='JSON array'):
        importer.decode_card(card)


def test_rev_b_csv_import_preserves_observations(tmp_path):
    card = card_for('B')
    path = tmp_path / 'rev_b_cards.csv'
    with path.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(certified_interface('B').field_names))
        writer.writeheader()
        writer.writerow(card)
    _, imported, checks = importer.import_csv(path)
    assert len(imported) == 1
    assert imported[0]['semantic_observations'] == [OBS]
    assert imported[0]['d_import_interface_revision'] == 'B'
    assert imported[0]['source_object_id'] == card['source_object_id']
    assert not [check for check in checks if check[1] == 'FAIL']
