from __future__ import annotations
import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

DOMAIN = {'Work': 'TITLE', 'Person': 'CONTRIBUTOR_NAME'}
NON_NAMES = {'VARIOUS'}

def read_jsonl(path):
    with path.open(encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]

def write_jsonl(path, rows):
    with path.open('w', encoding='utf-8') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + '\n')

def compare(a, b):
    if a['observed_value'] == b['observed_value']:
        return 'EXACT'
    for key in ('unicode', 'accent_case', 'punctuation_spacing'):
        av = a.get('comparison_forms', {}).get(key)
        bv = b.get('comparison_forms', {}).get(key)
        if av and bv and av == bv:
            return key.upper()
    return None

def title_annotation_base(value):
    return re.sub(r'\s+-v\d*\s*$', '', value, flags=re.IGNORECASE).strip()

def annotated_match(a, b):
    if a['entity_type'] != 'Work' or b['entity_type'] != 'Work':
        return False
    x, y = title_annotation_base(a['observed_value']), title_annotation_base(b['observed_value'])
    if x == a['observed_value'] and y == b['observed_value']:
        return False
    # Use existing D2 comparison normalization only; do not rewrite original observations.
    import unicodedata
    def form(v):
        d = unicodedata.normalize('NFD', v)
        return ''.join(c for c in d if unicodedata.category(c) != 'Mn').casefold()
    return form(x) == form(y)

def build(representations, candidate_sets):
    by_id = {r['representation_id']: r for r in representations}
    if len(by_id) != len(representations):
        raise ValueError('Duplicate representation IDs')
    by_ci_domain = defaultdict(list)
    for r in representations:
        if r['entity_type'] not in DOMAIN:
            continue
        by_ci_domain[(r['cataloged_instance_id'], r['entity_type'])].append(r)
    output = []
    for candidate in sorted(candidate_sets, key=lambda x: x['candidate_set_id']):
        entity_type = candidate['entity_type']
        if entity_type not in DOMAIN:
            continue
        members = [by_id[rid] for rid in candidate['representation_ids']]
        if any(r['entity_type'] != entity_type for r in members):
            raise ValueError('Candidate set mixes representation types')
        member_ids = set(candidate['representation_ids'])
        ci_ids = sorted({r['cataloged_instance_id'] for r in members})
        related, unresolved, contextual = [], [], []
        for ci in ci_ids:
            for r in by_ci_domain[(ci, entity_type)]:
                if r['representation_id'] in member_ids:
                    continue
                matches = sorted({basis for m in members if (basis := compare(r, m))})
                if matches:
                    related.append({'representation_id': r['representation_id'], 'cataloged_instance_id': ci, 'comparison_bases': matches})
                elif any(annotated_match(r, m) for m in members):
                    related.append({'representation_id': r['representation_id'], 'cataloged_instance_id': ci, 'comparison_bases': ['SOURCE_TITLE_ANNOTATION_V']})
                else:
                    # A different Person name co-occurring on the same source
                    # instance is contextual, regardless of contributor role.
                    # This is neither a same-person nor a different-person claim.
                    entry = {'representation_id': r['representation_id'], 'cataloged_instance_id': ci}
                    if entity_type == 'Person':
                        contextual.append({**entry, 'assessment': 'DIFFERENT_CONTRIBUTOR_NAME_CONTEXT', 'role': r.get('role')})
                    else:
                        unresolved.append({**entry, 'assessment': 'UNRESOLVED_DIFFERENCE_NOT_PROVEN_CONFLICT'})
        observed = [r['observed_value'] for r in members]
        non_name = entity_type == 'Person' and any(v.strip().upper() in NON_NAMES for v in observed)
        source_keys = sorted({r['source_object_key'] for r in members if r.get('source_object_key')})
        origins = sorted({r['representation_source'] for r in members if r.get('representation_source')})
        roles = sorted({r['role'] for r in members if r.get('role')})
        output.append({
            'd3_version': '0.3', 'candidate_set_id': candidate['candidate_set_id'],
            'representation_domain': DOMAIN[entity_type], 'group_status': 'NON_NAME_EXPRESSION' if non_name else ('CROSS_INSTANCE_LIKELY_SAME' if len(ci_ids) > 1 else 'WITHIN_INSTANCE_EVIDENCE'),
            'identity_asserted': False, 'entities_created': 0,
            'supporting_member_ids': sorted(member_ids), 'supporting_related': sorted(related, key=lambda x: x['representation_id']),
            'unresolved_relevant': sorted(unresolved, key=lambda x: x['representation_id']),
            'contextual_associations': sorted(contextual, key=lambda x: x['representation_id']),
            'potentially_conflicting': [], # requires contextual contradiction evidence, not merely differing strings
            'cataloged_instance_ids': ci_ids, 'representation_count': len(members),
            'cataloged_instance_count': len(ci_ids), 'distinct_source_record_count': len(source_keys),
            'source_object_keys': source_keys, 'representation_origins': origins,
            'roles': roles, 'discovery_methods': candidate.get('discovery_methods', []),
            'distinct_observed_values': sorted(set(observed)),
            'note': 'Source-population independence is not established by source_object_key.'
        })
    return output

def main():
    p = argparse.ArgumentParser(description='Read-only D3 v0.3 grouping evidence report')
    p.add_argument('--input-dir', type=Path, required=True)
    p.add_argument('--output-dir', type=Path, required=True)
    args = p.parse_args()
    reps = read_jsonl(args.input_dir / 'candidate_representations.jsonl')
    sets = read_jsonl(args.input_dir / 'candidate_sets.jsonl')
    groups = build(reps, sets)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(args.output_dir / 'd3_groups.jsonl', groups)
    counts = Counter((g['representation_domain'], g['group_status']) for g in groups)
    summary = {'d3_version': '0.3', 'input_candidate_sets': len(sets), 'output_groups': len(groups),
               'group_counts': {f'{k[0]}:{k[1]}': v for k, v in sorted(counts.items())},
               'groups_with_related_evidence': sum(bool(g['supporting_related']) for g in groups),
               'groups_with_unresolved_differences': sum(bool(g['unresolved_relevant']) for g in groups),
               'groups_with_contextual_associations': sum(bool(g['contextual_associations']) for g in groups),
               'identity_decisions_made': 0, 'entities_created': 0}
    (args.output_dir / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))

if __name__ == '__main__':
    main()
