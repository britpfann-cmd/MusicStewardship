"""MusicStewardship D3.1/D3.2: report-only representation classification and pair evidence."""
import argparse
import hashlib
import json
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

NON_NAMES = {'VARIOUS'}
DOMAINS = {'Work': 'TITLE', 'Person': 'CONTRIBUTOR_NAME'}

def read_jsonl(path):
    with path.open(encoding='utf-8') as stream:
        for number, line in enumerate(stream, 1):
            if line.strip():
                try:
                    yield json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f'{path}:{number}: {exc}') from exc

def write_jsonl(path, rows):
    with path.open('w', encoding='utf-8', newline='\n') as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + '\n')

def build(input_dir, output_dir):
    if input_dir.resolve() == output_dir.resolve():
        raise ValueError('Input and output directories must differ')
    reps = {}
    classified = []
    for rep in read_jsonl(input_dir / 'candidate_representations.jsonl'):
        rid = rep['representation_id']
        if rid in reps:
            raise ValueError(f'Duplicate representation ID: {rid}')
        domain = DOMAINS[rep['entity_type']]
        classification = ('NON_NAME_LIKE' if domain == 'CONTRIBUTOR_NAME' and
                          rep['observed_value'].strip().upper() in NON_NAMES
                          else 'NAME_LIKE' if domain == 'CONTRIBUTOR_NAME' else 'TITLE_LIKE')
        reps[rid] = rep
        classified.append({'representation_id': rid, 'observation_id': rep['observation_id'],
                           'cataloged_instance_id': rep['cataloged_instance_id'],
                           'source_entity_type': rep['entity_type'], 'representation_domain': domain,
                           'classification': classification, 'observed_field': rep['observed_field'],
                           'observed_value': rep['observed_value']})
    pairs = defaultdict(lambda: {'set_ids': set(), 'rep_ids': set(), 'methods': set(), 'roles': set()})
    excluded_sets = 0
    input_sets = 0
    for candidate in read_jsonl(input_dir / 'candidate_sets.jsonl'):
        input_sets += 1
        if candidate.get('identity_asserted') is not False:
            raise ValueError(f"Candidate set {candidate['candidate_set_id']} does not explicitly deny identity assertion")
        domain = DOMAINS[candidate['entity_type']]
        member_reps = []
        for rid in candidate['representation_ids']:
            if rid not in reps:
                raise ValueError(f'Missing representation {rid}')
            rep = reps[rid]
            if DOMAINS[rep['entity_type']] != domain:
                raise ValueError(f'Domain mismatch for {rid}')
            if domain == 'CONTRIBUTOR_NAME' and rep['observed_value'].strip().upper() in NON_NAMES:
                continue
            member_reps.append(rep)
        if not member_reps:
            excluded_sets += 1
            continue
        by_ci = defaultdict(set)
        for rep in member_reps:
            by_ci[rep['cataloged_instance_id']].add(rep['representation_id'])
        for left, right in combinations(sorted(by_ci), 2):
            item = pairs[(domain, left, right)]
            item['set_ids'].add(candidate['candidate_set_id'])
            item['rep_ids'].update(by_ci[left] | by_ci[right])
            item['methods'].update(candidate.get('discovery_methods', []))
            item['roles'].update(candidate.get('roles', []))
    rows = []
    for (domain, left, right), evidence in sorted(pairs.items()):
        ids = sorted(evidence['rep_ids'])
        source_records = sorted({reps[rid]['source_object_key'] for rid in ids
                                 if reps[rid].get('source_object_key')})
        key = f'{domain}\0{left}\0{right}'
        rows.append({'pair_evidence_id': 'D3PAIR-' + hashlib.sha256(key.encode()).hexdigest()[:20],
                     'representation_domain': domain, 'cataloged_instance_ids': [left, right],
                     'supporting_candidate_set_ids': sorted(evidence['set_ids']),
                     'supporting_representation_ids': ids,
                     'supporting_observation_ids': sorted({reps[rid]['observation_id'] for rid in ids}),
                     'observed_values': sorted({reps[rid]['observed_value'] for rid in ids}),
                     'source_object_keys': source_records,
                     'discovery_methods': sorted(evidence['methods']), 'roles': sorted(evidence['roles']),
                     'identity_asserted': False})
    output_dir.mkdir(parents=True, exist_ok=True)
    write_jsonl(output_dir / 'd3_representation_classification.jsonl', classified)
    write_jsonl(output_dir / 'd3_pair_evidence.jsonl', rows)
    counts = Counter(row['representation_domain'] for row in rows)
    summary = {'input_representations': len(reps), 'input_candidate_sets': input_sets,
               'excluded_non_name_candidate_sets': excluded_sets,
               'cross_instance_pairs': len(rows), 'pairs_by_domain': dict(sorted(counts.items())),
               'identity_asserted': False,
               'scope': 'D3.1/D3.2 only; no contextual compatibility assessment or transitive grouping'}
    (output_dir / 'd3_summary.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    return summary

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-dir', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.input_dir, args.output_dir), indent=2))

if __name__ == '__main__':
    main()
