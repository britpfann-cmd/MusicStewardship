#!/usr/bin/env python3
"""Parse a saved TANGO-DJ.AT Crackling Tunes HTML result into sorted CSV."""
import argparse, csv, re
from pathlib import Path
from bs4 import BeautifulSoup

FIELDS = [
    'tango_dj_ref','source_release','source_release_id','track_number','title',
    'genre','artist','recording_date','duration','rating','dj_recommended',
    'album','publisher','release_date','composer','author','catalog_number',
    'matrix_number','comment','instrumental'
]

def clean(s): return ' '.join(s.split()).strip()

def get_text(td): return clean(td.get_text(' ', strip=True))

def album_id(album):
    m=re.search(r'(CTMM\d{4})', album or '')
    return m.group(1) if m else ''

def num(s):
    m=re.search(r'\d+', s or '')
    return int(m.group()) if m else 999999

def parse(path):
    soup=BeautifulSoup(path.read_text(encoding='utf-8', errors='replace'),'html.parser')
    table=soup.find('table', id='searchresult')
    if table is None: raise SystemExit('searchresult table not found')
    out=[]
    for tr in table.find_all('tr'):
        tds=tr.find_all('td', recursive=False)
        if len(tds)<22: continue
        title=get_text(tds[7]); genre=get_text(tds[8]); artist=get_text(tds[9])
        recorded=get_text(tds[10]); duration=get_text(tds[11]); rating=get_text(tds[12]); dj=get_text(tds[13])
        album=get_text(tds[14]); publisher=get_text(tds[15]); released=get_text(tds[16])
        composer=get_text(tds[17]); author=get_text(tds[18]); catalog=get_text(tds[19]); matrix=get_text(tds[20]); comment=get_text(tds[21])
        ref=''
        a=tr.find('a', href=re.compile(r'[?&]ref=\d+'))
        if a:
            m=re.search(r'[?&]ref=(\d+)', a.get('href',''))
            if m: ref=m.group(1)
        out.append({
            'tango_dj_ref':ref,'source_release':album,'source_release_id':album_id(album),
            'track_number':num(get_text(tds[6])), 'title':title,'genre':genre,'artist':artist,
            'recording_date':recorded,'duration':duration,'rating':rating,
            'dj_recommended':'1' if 'recommended' in tr.get_text(' ',strip=True).lower() else ('0' if dj=='0' else dj),
            'album':album,'publisher':publisher,'release_date':released,'composer':composer,
            'author':author,'catalog_number':catalog,'matrix_number':matrix,'comment':comment,
            'instrumental': '1' if tds[4].find(class_='tooltip') else ''
        })
    out.sort(key=lambda r: ((r['source_release_id'] or r['source_release']), r['track_number']))
    return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('html',type=Path); ap.add_argument('csv',type=Path); a=ap.parse_args()
    rows=parse(a.html); a.csv.parent.mkdir(parents=True,exist_ok=True)
    with a.csv.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=FIELDS); w.writeheader(); w.writerows(rows)
    print(f'Parsed {len(rows)} TANGO-DJ recording rows from {a.html}')
    print(f'CSV written: {a.csv}')
    print(f'Releases: {len(set(r["source_release_id"] or r["source_release"] for r in rows))}')

if __name__=='__main__': main()
