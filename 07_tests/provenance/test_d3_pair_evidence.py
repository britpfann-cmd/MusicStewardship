import json
import tempfile
import unittest
from pathlib import Path
from d3_pair_evidence import build, read_jsonl

class D3Tests(unittest.TestCase):
    def test_overlap_and_nonname(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / 'input'; source.mkdir()
            reps = [
                {'representation_id': rid, 'observation_id': rid+'-obs',
                 'cataloged_instance_id': ci, 'entity_type': typ,
                 'observed_value': value, 'observed_field': field,
                 'source_object_key': ci, 'library_card_id': ci}
                for rid, ci, typ, value, field in [
                    ('r1','a','Work','El huracan','filename_leading_text_candidate'),
                    ('r2','b','Work','El huracan','filename_leading_text_candidate'),
                    ('r3','a','Work','El huracán','title'),
                    ('r4','b','Work','El huracán','title'),
                    ('r5','c','Person','VARIOUS','composer_expression'),
                    ('r6','d','Person','VARIOUS','composer_expression')]]
            sets = [
                {'candidate_set_id': sid, 'entity_type': typ, 'representation_ids': ids,
                 'identity_asserted': False, 'discovery_methods': ['test'], 'roles': []}
                for sid, typ, ids in [('s1','Work',['r1','r2']),
                                      ('s2','Work',['r3','r4']),
                                      ('s3','Work',['r1','r2','r3','r4']),
                                      ('s4','Person',['r5','r6'])]]
            for filename, items in [('candidate_representations.jsonl', reps),
                                    ('candidate_sets.jsonl', sets)]:
                (source / filename).write_text(''.join(json.dumps(x)+'\n' for x in items), encoding='utf-8')
            summary = build(source, root / 'out')
            self.assertEqual(summary['cross_instance_pairs'], 1)
            self.assertEqual(summary['excluded_non_name_candidate_sets'], 1)
            pair = list(read_jsonl(root/'out'/'d3_pair_evidence.jsonl'))[0]
            self.assertEqual(pair['supporting_candidate_set_ids'], ['s1','s2','s3'])
            self.assertEqual(len(pair['supporting_observation_ids']), 4)
            self.assertFalse(pair['identity_asserted'])

if __name__ == '__main__':
    unittest.main()
