"""Build cysa-opslab.html from ops_data.py + cvss.js.  Run: python3 build/opslab/ops_page.py"""
import json, sys, pathlib, re
HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent))
from ops_data import TRACKS, D
from nb_d1 import D1
from nb_d2 import D2
from nb_d34 import D3, D4

ROOT = pathlib.Path('/home/claude')
HUB = 'https://claude.ai/artifact/PrxFejEDNFYfNB7V7Ahjvq'
NOTEBOOK = 'https://claude.ai/artifact/2Zm7Tw7xCVcNJCC9bheaxv'
SPINE = json.load(open(HERE.parent / 'cysa-spine.json'))
NBIDS = {t['id'] for t in D1 + D2 + D3 + D4}

# ---- guard rails: every drill is complete and consistent
ids = set()
for d in D:
    assert d['id'] not in ids, d['id']; ids.add(d['id'])
    assert d['o'] in SPINE, (d['id'], d['o'])
    assert d['tr'] in {t['id'] for t in TRACKS}
    assert d['nb'] in NBIDS, (d['id'], 'notebook topic missing', d['nb'])
    for k in ('title', 'brief', 'prompt', 'explain', 'keep'): assert d.get(k), (d['id'], k)
    ty = d['ty']
    if ty == 'single': assert 0 <= d['ans'] < len(d['opts'])
    elif ty == 'multi': assert all(0 <= a < len(d['opts']) for a in d['ans']) and len(d['ans']) >= 2
    elif ty == 'order': assert len(d['opts']) >= 3 and 'ans' not in d
    elif ty == 'score': assert d['vec'].startswith('CVSS:3.1/') and 0 <= d['ans'] < len(d['opts'])
    elif ty == 'line': assert isinstance(d['art'], list) and 0 <= d['ans'] < len(d['art'])
    else: raise AssertionError(ty)
    if ty != 'line':
        for o in d['opts']: assert len(o) == 2 and o[0] and o[1], d['id']

objt = {o: v['title'] for o, v in SPINE.items()}
def js(v): return json.dumps(v, ensure_ascii=False).replace('</', '<\\/')
cvss_js = (HERE / 'cvss.js').read_text().replace("if (typeof module !== 'undefined') module.exports = CVSS;", '')

PAGE = (HERE / 'ops_template.html').read_text()
out = (PAGE.replace('__CVSS__', cvss_js).replace('__DRILLS__', js(D)).replace('__TRACKS__', js(TRACKS))
           .replace('__OBJT__', js(objt)).replace('__HUB__', HUB).replace('__NOTEBOOK__', NOTEBOOK)
           .replace('__NDRILLS__', str(len(D))))
assert '__' not in re.sub(r'__(proto|plain)__', '', out.split('<script>')[0]), 'unreplaced placeholder'
(ROOT / 'cysa-opslab.html').write_text(out, encoding='utf-8')
per = {}
for d in D: per[d['tr']] = per.get(d['tr'], 0) + 1
print(f'ops lab: {len(D)} drills {per}, {len(out)//1024} KB')
