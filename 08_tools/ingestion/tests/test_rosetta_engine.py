#!/usr/bin/env python3
import csv, sys
from pathlib import Path
p = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name('TTT_rosetta_engine_sample_output.csv')
rows = list(csv.DictReader(p.open(encoding='utf-8-sig')))
assert rows, 'No observations emitted'
assert all(r['source_value'] for r in rows), 'Source value was lost'
assert all(r['rule_id'] for r in rows), 'Rule provenance missing'
assert all(r['information_class'] in {'CORE','ASSOCIATED','RESIDUAL'} for r in rows)
print(f'PASS: {len(rows)} observations preserve source value and rule provenance')
