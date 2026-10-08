import unittest
from d3_likely_same_grouping import build

def rep(i, ci, value, kind='Work'):
    return {'representation_id': i, 'cataloged_instance_id': ci, 'entity_type': kind,
            'observed_value': value, 'source_object_key': ci,
            'representation_source': 'embedded_title', 'comparison_forms': {'unicode': value,
            'accent_case': value.casefold(), 'punctuation_spacing': ''.join(c for c in value.casefold() if c.isalnum())}}

def candidate(*ids, kind='Work'):
    return {'candidate_set_id': 'set_test', 'entity_type': kind,
            'representation_ids': list(ids), 'discovery_methods': ['unicode']}

class TestD3(unittest.TestCase):
    def test_related_same_ci(self):
        result = build([rep('a','ci1','Colibriyo'),rep('b','ci2','Colibriyo'),rep('c','ci1','Colibriyo')], [candidate('a','b')])[0]
        self.assertEqual([x['representation_id'] for x in result['supporting_related']], ['c'])
        self.assertEqual(result['distinct_source_record_count'], 2)
        self.assertFalse(result['identity_asserted'])
    def test_annotated_title(self):
        result = build([rep('a','ci1','Bar exposicion'),rep('b','ci2','Bar exposicion'),rep('c','ci1','Bar exposición -v2')], [candidate('a','b')])[0]
        self.assertEqual(result['supporting_related'][0]['comparison_bases'], ['SOURCE_TITLE_ANNOTATION_V'])
    def test_various(self):
        result = build([rep('a','ci1','VARIOUS','Person'),rep('b','ci2','VARIOUS','Person')], [candidate('a','b',kind='Person')])[0]
        self.assertEqual(result['group_status'], 'NON_NAME_EXPRESSION')
    def test_no_transitive_merging(self):
        reps = [rep('a','ci1','A'),rep('b','ci2','A'),rep('c','ci3','A')]
        sets = [candidate('a','b'),dict(candidate('b','c'), candidate_set_id='set_two')]
        self.assertEqual(len(build(reps, sets)), 2)

    def test_different_roles_contextual(self):
        a = rep('a', 'ci1', 'Francisco Bohigas', 'Person'); a['role'] = 'author'
        b = rep('b', 'ci2', 'Francisco Bohigas', 'Person'); b['role'] = 'author'
        c = rep('c', 'ci1', 'Alejandro Michetti', 'Person'); c['role'] = 'composer'
        result = build([a, b, c], [candidate('a', 'b', kind='Person')])[0]
        self.assertEqual([x['representation_id'] for x in result['contextual_associations']], ['c'])
        self.assertEqual(result['unresolved_relevant'], [])
        self.assertFalse(result['identity_asserted'])
        self.assertEqual(result['entities_created'], 0)

    def test_same_role_contextual(self):
        a = rep('a', 'ci1', 'Francisco Bohigas', 'Person'); a['role'] = 'author'
        b = rep('b', 'ci2', 'Francisco Bohigas', 'Person'); b['role'] = 'author'
        c = rep('c', 'ci1', 'Another Author', 'Person'); c['role'] = 'author'
        result = build([a, b, c], [candidate('a', 'b', kind='Person')])[0]
        self.assertEqual([x['representation_id'] for x in result['contextual_associations']], ['c'])
        self.assertEqual(result['unresolved_relevant'], [])

    def test_matching_name_across_roles(self):
        a = rep('a', 'ci1', 'Francisco Bohigas', 'Person'); a['role'] = 'author'
        b = rep('b', 'ci2', 'Francisco Bohigas', 'Person'); b['role'] = 'author'
        c = rep('c', 'ci1', 'Francisco Bohigas', 'Person'); c['role'] = 'composer'
        result = build([a, b, c], [candidate('a', 'b', kind='Person')])[0]
        self.assertEqual([x['representation_id'] for x in result['supporting_related']], ['c'])
        self.assertEqual(result['contextual_associations'], [])

    def test_unknown_role_contextual(self):
        a = rep('a', 'ci1', 'Francisco Bohigas', 'Person'); a['role'] = 'author'
        b = rep('b', 'ci2', 'Francisco Bohigas', 'Person'); b['role'] = 'author'
        c = rep('c', 'ci1', 'Unknown Contributor', 'Person')
        result = build([a, b, c], [candidate('a', 'b', kind='Person')])[0]
        self.assertEqual([x['representation_id'] for x in result['contextual_associations']], ['c'])
        self.assertEqual(result['unresolved_relevant'], [])

    def test_mixed_supporting_roles_other_name_contextual(self):
        a = rep('a', 'ci1', 'Virgilio San Clemente', 'Person'); a['role'] = 'author'
        b = rep('b', 'ci2', 'Virgilio San Clemente', 'Person'); b['role'] = 'composer'
        c = rep('c', 'ci1', 'Maruja Pacheco Huergo', 'Person'); c['role'] = 'composer'
        result = build([a, b, c], [candidate('a', 'b', kind='Person')])[0]
        self.assertEqual([x['representation_id'] for x in result['contextual_associations']], ['c'])
        self.assertEqual(result['unresolved_relevant'], [])
        self.assertEqual(result['supporting_related'], [])
        self.assertFalse(result['identity_asserted'])
        self.assertEqual(result['entities_created'], 0)

    def test_different_names_not_identity_support(self):
        a = rep('a', 'ci1', 'Juan Canaro', 'Person'); a['role'] = 'composer'
        b = rep('b', 'ci2', 'Juan Canaro', 'Person'); b['role'] = 'author'
        c = rep('c', 'ci1', 'Osvaldo Sosa Cordero', 'Person'); c['role'] = 'author'
        result = build([a, b, c], [candidate('a', 'b', kind='Person')])[0]
        self.assertEqual(result['supporting_member_ids'], ['a', 'b'])
        self.assertEqual(result['supporting_related'], [])
        self.assertEqual([x['representation_id'] for x in result['contextual_associations']], ['c'])
        self.assertEqual(result['potentially_conflicting'], [])

if __name__ == '__main__':
    unittest.main()
