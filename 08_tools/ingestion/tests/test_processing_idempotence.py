import csv
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[3] / '08_tools' / 'ingestion'))
from rosetta_engine import run,read_csv

def test_repeat_run_skips_completed_work_items(tmp_path):
    root=Path(__file__).resolve().parents[1]
    src=Path(__file__).parent/'TTT_rosetta_engine_v0.2_regression_sample.csv'
    mapping=root/'mappings'/'TTT_to_MusicStewardship_Rosetta_v0.2.csv'
    bindings=root/'mappings'/'TTT_source_field_bindings.csv'
    rows=read_csv(src); rules=read_csv(mapping); binds=read_csv(bindings)
    state=tmp_path/'state'
    first=run(rows,rules,binds,state,run_id='RUN1')
    second=run(rows,rules,binds,state,run_id='RUN2')
    assert first['processed'] == 313
    assert first['new_observations'] == 349
    assert second['processed'] == 0
    assert second['skipped'] == 313
    with (state/'processing_log.csv').open(encoding='utf-8-sig',newline='') as f: log=list(csv.DictReader(f))
    assert len(log)==313
    with (state/'observations.csv').open(encoding='utf-8-sig',newline='') as f: obs=list(csv.DictReader(f))
    assert len(obs)==349
