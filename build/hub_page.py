"""Build the CompTIA Toolkit hub (root index.html) with the Test Prep Scheduler.

Sources (all in build/):
  hub/hub.html       hub fragment, artifact form (claude.ai links), with three markers
  hub/sched.html     scheduler markup      -> <!--SCHED-HTML-->
  hub/sched.css      scheduler styles      -> /*SCHED-CSS*/
  hub/sched.js       scheduler logic       -> /*SCHED-JS*/
  sched_data.json    objective maps for every cert in the dropdown

Outputs:
  build/out/cert-hub.html   artifact fragment, published to the CompTIA Toolkit artifact
  index.html                repo page: same fragment, wrapped, links rewritten to repo paths

Run from the repo root:  python build/hub_page.py
"""
import json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
B = ROOT / 'build'

A = 'https://claude.ai/artifact/'
CYSA = {'hub': A + 'PrxFejEDNFYfNB7V7Ahjvq', 'nb': A + '2Zm7Tw7xCVcNJCC9bheaxv',
        'pbq': A + 'DoTioR9UxmZx2fEP4NRhrz', 'ops': A + '3v8xDmJgJFy1BMsCyLEhCE',
        'dr': {'1': A + 'KrYojQYtNqGKiiYQQ1iPXy', '2': A + 'Gud7EZdHrEfGnPxsyy29Fk',
               '3': A + 'R3jFowQmYqv5x3Kv2qYNoS', '4': A + 'HrmyyybMcjv3ut54g1ujfu'}}
SEC = {'hub': A + 'VBQTcEFCBoLm2HbFYQ3MFE', 'acr': A + 'AWyxEkC2q9eHzRvyDUNkb1',
       'nb': {'1': A + 'Rsb6YnjU33btaifdZgyFhB', '2': A + 'QcBcJKdGD7MVZsMfbdNt1b',
              '3': A + 'HSwrQ2Z2xXpmrQHGrZi8SN', '4': A + 'Cfj2uJ53pJKpML2woMP6E8',
              '5': A + 'A4gMbARsZBBK7upETX4cVQ'},
       'dr': {'1': A + 'V4c6LTwdzLraL6923m1FG2', '2': A + 'JLQhDRGVEeYBbUzRaUqgzv',
              '3': A + 'CLSzAzhXsHyydspYA3W4ti', '4': A + '3TDmapWnJANA3HqVMHVvne',
              '5': A + 'Wyhp4zXtxfBbihG4azVnRt'}}
NETPLUS = 'https://dirtybird-hash.github.io/netplus-study-guide2/'

def a(href, text):
    return f'<a href="{href}" target="_blank" rel="noopener">{text}</a>'

LINKS = {
  'cysa': {
    'prefix': 'cysa', 'accent': '--c-cysa', 'drillKey': 'cysa:domain{d}drill:v1',
    'notebook': {'*': CYSA['nb']}, 'nbLabel': 'CySA+ Notebook', 'drill': CYSA['dr'],
    'presets': [{'label': 'MeasureUp final · Wed Nov 11', 'date': '2026-11-11'},
                {'label': 'CompTIA exam · Thu Nov 12', 'date': '2026-11-12'}],
    'extra': {'title': 'Hands-on round',
              'detail': 'One ' + a(CYSA['pbq'], 'Performance Task') + ' and one ' +
                        a(CYSA['ops'], 'Ops Lab') + ' drill, scored, then read every explanation.'},
    'simNote': 'A MeasureUp practice exam, or the scenario sets from all four Drills back to back, '
               'under exam timing. Don’t pause to look anything up.',
    'lightNote': 'The acronym list in the ' + a(CYSA['nb'], 'Notebook') + ' and the look-alike pairs.',
  },
  'secplus': {
    'prefix': 'secplus', 'accent': '--c-sec', 'drillKey': 'secplus:domain{d}drill:v1',
    'notebook': SEC['nb'], 'nbLabel': 'Domain {d} Notebook', 'drill': SEC['dr'],
    'extra': {'title': 'Acronym Drill round',
              'detail': 'A quiz round in the ' + a(SEC['acr'], 'Acronym Drill') + ', both directions.'},
    'lightNote': 'The ' + a(SEC['acr'], 'Acronym Drill') + ' and the Gotchas tab in each Notebook.',
  },
  'netplus': {
    'prefix': 'netplus', 'accent': '--c-net', 'guide': NETPLUS,
    'extra': {'title': 'Ports and subnetting round',
              'detail': 'The port drill and ten subnetting problems in the ' + a(NETPLUS, 'Network+ guide') + '.'},
    'lightNote': 'Ports, the OSI layers and the troubleshooting steps in the ' + a(NETPLUS, 'Network+ guide') + '.',
  },
  'aplus': {
    'prefix': 'aplus', 'accent': '--c-ap',
    'lightNote': 'Your Core 2 class notes: command-line tools, Windows editions and the malware-removal steps.',
  },
}

# Repo paths for every artifact URL the hub can contain.
REPO_URLS = {CYSA['hub']: 'cysa/index.html', CYSA['nb']: 'cysa/notebook.html',
             CYSA['pbq']: 'cysa/performance-tasks.html', CYSA['ops']: 'cysa/ops-lab.html',
             SEC['hub']: 'security-plus/index.html', SEC['acr']: 'security-plus/acronym-drill.html'}
for d, u in CYSA['dr'].items(): REPO_URLS[u] = f'cysa/domain{d}-drill.html'
for d, u in SEC['nb'].items():  REPO_URLS[u] = f'security-plus/domain{d}-notebook.html'
for d, u in SEC['dr'].items():  REPO_URLS[u] = f'security-plus/domain{d}-drill.html'

HEAD = ('<!doctype html>\n<html lang="en">\n<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
        '<meta name="color-scheme" content="light dark">\n'
        '<meta name="description" content="{desc}">\n'
        '<style>:root{{box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);'
        'padding-bottom:env(safe-area-inset-bottom,0px)}}html{{scroll-padding-top:env(safe-area-inset-top,0px)}}'
        'body{{margin:0}}img{{max-width:100%}}[hidden]{{display:none!important}}</style>\n')
DESC = 'Study tools for every CompTIA certification on the track.'

def wrap(frag, urls):
    """Same wrapping as tools/build_repo.py, so the result matches a full repo build."""
    title = re.search(r'<title>(.*?)</title>', frag).group(1)
    s = re.sub(r'<title>.*?</title>\s*', '', frag, count=1)
    for url, fname in urls.items():
        s = s.replace(url, fname)
    return HEAD.format(desc=DESC) + f'<title>{title}</title>\n</head>\n<body>\n' + s.strip() + '\n</body>\n</html>\n'

def main():
    frag = (B / 'hub' / 'hub.html').read_text(encoding='utf-8')
    data = json.loads((B / 'sched_data.json').read_text(encoding='utf-8'))
    js = (B / 'hub' / 'sched.js').read_text(encoding='utf-8')
    js = (js.replace('__SCHED_DATA__', json.dumps(data, ensure_ascii=False, separators=(',', ':')))
            .replace('__SCHED_LINKS__', json.dumps(LINKS, ensure_ascii=False, separators=(',', ':'))))
    for marker, src in (('<!--SCHED-HTML-->\n', (B / 'hub' / 'sched.html').read_text(encoding='utf-8') + '\n'),
                        ('/*SCHED-CSS*/\n', (B / 'hub' / 'sched.css').read_text(encoding='utf-8').lstrip('\n')),
                        ('/*SCHED-JS*/\n', js)):
        assert frag.count(marker) == 1, marker
        frag = frag.replace(marker, src)
    out = B / 'out'; out.mkdir(exist_ok=True)
    (out / 'cert-hub.html').write_text(frag, encoding='utf-8')
    page = wrap(frag, {**REPO_URLS})
    (ROOT / 'index.html').write_text(page, encoding='utf-8')
    left = [u for u in re.findall(r'https://claude\.ai/artifact/\w+', page)]
    print(f'cert-hub.html {len(frag)} bytes; index.html {len(page)} bytes; claude.ai links left in repo page: {len(left)}')

if __name__ == '__main__':
    main()
