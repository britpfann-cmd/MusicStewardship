"""Catalog submission history: interface revisions do not change source identity."""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / '04_src'))
from catalog.catalog_store import CatalogStore

def test_a_b_repeat_corrected(tmp_path):
    s = CatalogStore(tmp_path / 'catalog.db')
    try:
        base = {'source_object_id':'S1','source_object_key':'TTT:a.flac',
                'source_record_revision':'source_ingest.v2'}
        a = dict(base, library_card_interface_revision='A')
        b = dict(base, library_card_interface_revision='B', semantic_observations=[{'decoded_value':'A'}])
        corrected = dict(base, library_card_interface_revision='B', semantic_observations=[{'decoded_value':'B'}])
        card_id = s.accept_library_card(a)
        ci = s.create_cataloged_instance(card_id, {})
        assert s.accept_library_card(b) == card_id
        assert s.accept_library_card(b) == card_id
        assert s.accept_library_card(corrected) == card_id
        assert s.create_cataloged_instance(card_id, {'title':['Changed']}) == ci
        history = s.get_library_card_revision_history(card_id)
        assert [h['revision_number'] for h in history] == [1,2,3]
        assert [h['card'] for h in history] == [a,b,corrected]
        assert len(s.get_ci_revision_history(ci)) == 1
    finally: s.close()

def test_distinct_evidence_same_value(tmp_path):
    s = CatalogStore(tmp_path / 'catalog.db')
    try:
        cid = s.accept_library_card({'source_object_id':'S','source_object_key':'S:a','source_record_revision':'1'})
        ci = s.create_cataloged_instance(cid, {})
        kw = dict(library_card_id=cid, library_card_revision_id=s.latest_library_card_revision_id(cid),
                  subject_type='CATALOGED_INSTANCE',subject_id=ci,field='title',observed_value='A')
        a = s.add_observation(**kw,evidence={'rule_id':'R1'})
        assert s.add_observation(**kw,evidence={'rule_id':'R1'}) == a
        assert s.add_observation(**kw,evidence={'rule_id':'R2'}) != a
    finally: s.close()
