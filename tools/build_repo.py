"""Assemble the publishable site from the artifact source fragments.

Artifact pages are published as fragments (no doctype/head/body) because the platform
wraps them. This adds a real wrapper, rewrites absolute artifact URLs to relative
filenames, and lays the result out one folder per certification:

    repo/
      index.html            <- the cert picker (root hub)
      security-plus/        <- one folder per cert
        index.html          <- that cert's own hub
        domain1-notebook.html ...

Adding a cert means adding an entry to CERTS. Nothing else here changes.
"""
import re, pathlib

SRC = pathlib.Path('/home/claude')
OUT = pathlib.Path('/home/claude/repo')
OUT.mkdir(exist_ok=True)

# The root cert picker. Source file -> published name at the repo root.
ROOT = {'cert-hub.html': 'index.html'}
ROOT_DESC = {'index.html': 'Study tools for every CompTIA certification on the track.'}

SECPLUS_HUB = "https://claude.ai/artifact/VBQTcEFCBoLm2HbFYQ3MFE"

# Artifact URL -> the filename it becomes. Links between pages in the same cert folder
# stay bare filenames, so no path prefix is needed here.
SECPLUS_URLS = {
  "https://claude.ai/artifact/Rsb6YnjU33btaifdZgyFhB": "domain1-notebook.html",
  "https://claude.ai/artifact/La2HXLBpgY7jR8m6FdAQzH": "domain1-match.html",
  "https://claude.ai/artifact/V4c6LTwdzLraL6923m1FG2": "domain1-drill.html",
  "https://claude.ai/artifact/QcBcJKdGD7MVZsMfbdNt1b": "domain2-notebook.html",
  "https://claude.ai/artifact/PTPN5nTY1X1j54RyTtxG8c": "domain2-match.html",
  "https://claude.ai/artifact/JLQhDRGVEeYBbUzRaUqgzv": "domain2-drill.html",
  "https://claude.ai/artifact/HSwrQ2Z2xXpmrQHGrZi8SN": "domain3-notebook.html",
  "https://claude.ai/artifact/3UNruLDALUMjXckzBuWXxD": "domain3-match.html",
  "https://claude.ai/artifact/CLSzAzhXsHyydspYA3W4ti": "domain3-drill.html",
  "https://claude.ai/artifact/Cfj2uJ53pJKpML2woMP6E8": "domain4-notebook.html",
  "https://claude.ai/artifact/JsKxAbsK2oX2YzuqsSidnX": "domain4-match.html",
  "https://claude.ai/artifact/3TDmapWnJANA3HqVMHVvne": "domain4-drill.html",
  "https://claude.ai/artifact/A4gMbARsZBBK7upETX4cVQ": "domain5-notebook.html",
  "https://claude.ai/artifact/RPuAbmpbnVFFnqAwEwMUKg": "domain5-match.html",
  "https://claude.ai/artifact/Wyhp4zXtxfBbihG4azVnRt": "domain5-drill.html",
  SECPLUS_HUB: "index.html",
  "https://claude.ai/artifact/AWyxEkC2q9eHzRvyDUNkb1": "acronym-drill.html",
  "https://claude.ai/artifact/PQbQXhnhBj4rniTPMzJprV": "prep-scheduler.html",
}

SECPLUS_FILES = {'security-toolkit.html': 'index.html'}
for d in range(1, 6):
    for kind in ('notebook', 'match', 'drill'):
        SECPLUS_FILES[f'domain{d}-{kind}.html'] = f'domain{d}-{kind}.html'
SECPLUS_FILES['acronym-drill.html'] = 'acronym-drill.html'
SECPLUS_FILES['prep-scheduler.html'] = 'prep-scheduler.html'

SECPLUS_DESC = {'index.html': 'Study tools for the CompTIA Security+ SY0-701 exam, organized by domain.'}
for d in range(1, 6):
    SECPLUS_DESC[f'domain{d}-notebook.html'] = f'Searchable reference notes for Security+ Domain {d}.'
    SECPLUS_DESC[f'domain{d}-match.html']    = f'Term-and-definition matching game for Security+ Domain {d}.'
    SECPLUS_DESC[f'domain{d}-drill.html']    = f'Flashcards, quiz and scenario practice for Security+ Domain {d}.'
SECPLUS_DESC['acronym-drill.html']  = 'All 333 CompTIA Security+ SY0-701 acronyms as flashcards, a quiz and a searchable list.'
SECPLUS_DESC['prep-scheduler.html'] = 'Turns your Security+ exam date into a day-by-day study and drill plan that follows your weak spots.'

CERT_HUB = "https://claude.ai/artifact/B7ZnpG2Vvn7rt55DFHh9Ws"

CYSA_URLS = {
  CERT_HUB: "../index.html",                                        # back to the cert picker
  "https://claude.ai/artifact/PrxFejEDNFYfNB7V7Ahjvq": "index.html",          # the CySA+ hub itself
  "https://claude.ai/artifact/KrYojQYtNqGKiiYQQ1iPXy": "domain1-drill.html",
  "https://claude.ai/artifact/Gud7EZdHrEfGnPxsyy29Fk": "domain2-drill.html",
  "https://claude.ai/artifact/R3jFowQmYqv5x3Kv2qYNoS": "domain3-drill.html",
  "https://claude.ai/artifact/HrmyyybMcjv3ut54g1ujfu": "domain4-drill.html",
  "https://claude.ai/artifact/5k2Wz7MQAfUfX2TKcHmDpn": "simple-flash.html",
  "https://claude.ai/artifact/DoTioR9UxmZx2fEP4NRhrz": "performance-tasks.html",
}
CYSA_FILES = {
  'cysa-hub.html':             'index.html',
  'cysa-domain1-drill.html':   'domain1-drill.html',
  'cysa-domain2-drill.html':   'domain2-drill.html',
  'cysa-domain3-drill.html':   'domain3-drill.html',
  'cysa-domain4-drill.html':   'domain4-drill.html',
  'cysa-school-flashcards.html':'simple-flash.html',
  'cysa-pbq.html':             'performance-tasks.html',
}
CYSA_DESC = {
  'index.html':        'Study tools for the CompTIA CySA+ CS0-003 exam, organized by domain.',
  'domain1-drill.html':'Flashcards, quiz and scenario practice for CySA+ Domain 1, Security Operations.',
  'domain2-drill.html':'Flashcards, quiz and scenario practice for CySA+ Domain 2, Vulnerability Management.',
  'domain3-drill.html':'Flashcards, quiz and scenario practice for CySA+ Domain 3, Incident Response and Management.',
  'domain4-drill.html':'Flashcards, quiz and scenario practice for CySA+ Domain 4, Reporting and Communication.',
  'simple-flash.html': 'Course flashcards for CySA+, typed during class and kept verbatim.',
  'performance-tasks.html':
      'Hands-on CySA+ exercises in the shape the exam uses, scored per objective.',
}

CERTS = {
  'security-plus': {'files': SECPLUS_FILES, 'desc': SECPLUS_DESC, 'urls': SECPLUS_URLS},
  'cysa': {'files': CYSA_FILES, 'desc': CYSA_DESC, 'urls': CYSA_URLS},
}

HEAD = ('<!doctype html>\n<html lang="en">\n<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
        '<meta name="color-scheme" content="light dark">\n'
        '<meta name="description" content="{desc}">\n'
        '<style>:root{{box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);'
        'padding-bottom:env(safe-area-inset-bottom,0px)}}html{{scroll-padding-top:env(safe-area-inset-top,0px)}}'
        'body{{margin:0}}img{{max-width:100%}}[hidden]{{display:none!important}}</style>\n')


def build(srcname, outpath, desc, urls):
    src = SRC / srcname
    if not src.exists():
        # A cloud workspace is ephemeral; one cert's sources can be absent while
        # another's are present. Skip loudly rather than failing the whole build,
        # so a partial rebuild still produces the pages it can.
        print(f'{str(outpath.relative_to(OUT)):34}  SKIPPED — no source at {srcname}')
        return False
    s = src.read_text(encoding='utf-8')
    m = re.search(r'<title>(.*?)</title>', s)
    title = m.group(1) if m else outpath.name
    s = re.sub(r'<title>.*?</title>\s*', '', s, count=1)
    for url, fname in urls.items():
        s = s.replace(url, fname)
    head = HEAD.format(desc=desc) + f'<title>{title}</title>\n</head>\n<body>\n'
    doc = head + s.strip() + '\n</body>\n</html>\n'
    outpath.parent.mkdir(parents=True, exist_ok=True)
    outpath.write_text(doc, encoding='utf-8')
    rel = outpath.relative_to(OUT)
    print(f'{str(rel):34} {len(doc)//1024:4} KB   title="{title}"')
    return True


# The cert hub links to each cert's hub artifact; in the repo those become folder paths.
ROOT_URLS = {
  "https://claude.ai/artifact/VBQTcEFCBoLm2HbFYQ3MFE": "security-plus/index.html",
  "https://claude.ai/artifact/PrxFejEDNFYfNB7V7Ahjvq": "cysa/index.html",
}
for srcname, outname in ROOT.items():
    build(srcname, OUT / outname, ROOT_DESC[outname], ROOT_URLS)

for folder, cfg in CERTS.items():
    print(f'\n-- {folder}/')
    for srcname, outname in cfg['files'].items():
        build(srcname, OUT / folder / outname, cfg['desc'][outname], cfg['urls'])

print('\n--- remaining claude.ai links ---')
found = False
for f in sorted(OUT.rglob('*.html')):
    for line in f.read_text(encoding='utf-8').splitlines():
        if 'claude.ai' in line:
            found = True
            print(f'{f.relative_to(OUT)}: {line.strip()[:110]}')
if not found:
    print('none')
