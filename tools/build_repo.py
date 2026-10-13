import re, os, pathlib

OUT = pathlib.Path('/home/claude/repo')
OUT.mkdir(exist_ok=True)

HUB_URL   = "https://claude.ai/artifact/VBQTcEFCBoLm2HbFYQ3MFE"
ART_TO_FILE = {
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
  HUB_URL: "index.html",
  "https://claude.ai/artifact/AWyxEkC2q9eHzRvyDUNkb1": "acronym-drill.html",
  "https://claude.ai/artifact/PQbQXhnhBj4rniTPMzJprV": "prep-scheduler.html",
}

FILES = {
  'security-toolkit.html': 'index.html',
  'domain1-notebook.html': 'domain1-notebook.html',
  'domain1-match.html':    'domain1-match.html',
  'domain1-drill.html':    'domain1-drill.html',
  'domain2-notebook.html': 'domain2-notebook.html',
  'domain2-match.html':    'domain2-match.html',
  'domain2-drill.html':    'domain2-drill.html',
  'domain3-notebook.html': 'domain3-notebook.html',
  'domain3-match.html':    'domain3-match.html',
  'domain3-drill.html':    'domain3-drill.html',
  'domain4-notebook.html': 'domain4-notebook.html',
  'domain4-match.html':    'domain4-match.html',
  'domain4-drill.html':    'domain4-drill.html',
  'domain5-notebook.html': 'domain5-notebook.html',
  'domain5-match.html':    'domain5-match.html',
  'domain5-drill.html':    'domain5-drill.html',
  'acronym-drill.html':    'acronym-drill.html',
  'prep-scheduler.html':   'prep-scheduler.html',
}

HEAD = ('<!doctype html>\n<html lang="en">\n<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
        '<meta name="color-scheme" content="light dark">\n'
        '<meta name="description" content="{desc}">\n'
        '<style>:root{{box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);'
        'padding-bottom:env(safe-area-inset-bottom,0px)}}html{{scroll-padding-top:env(safe-area-inset-top,0px)}}'
        'body{{margin:0}}img{{max-width:100%}}[hidden]{{display:none!important}}</style>\n')

DESC = {
 'index.html':'Study tools for the CompTIA Security+ SY0-701 exam, organized by domain.',
 'domain1-notebook.html':'Searchable reference notes for Security+ Domain 1.',
 'domain1-match.html':'Term-and-definition matching game for Security+ Domain 1.',
 'domain1-drill.html':'Flashcards, quiz and scenario practice for Security+ Domain 1.',
 'domain2-notebook.html':'Searchable reference notes for Security+ Domain 2.',
 'domain2-match.html':'Term-and-definition matching game for Security+ Domain 2.',
 'domain2-drill.html':'Flashcards, quiz and scenario practice for Security+ Domain 2.',
 'domain3-notebook.html':'Searchable reference notes for Security+ Domain 3.',
 'domain3-match.html':'Term-and-definition matching game for Security+ Domain 3.',
 'domain3-drill.html':'Flashcards, quiz and scenario practice for Security+ Domain 3.',
 'domain4-notebook.html':'Searchable reference notes for Security+ Domain 4.',
 'domain4-match.html':'Term-and-definition matching game for Security+ Domain 4.',
 'domain4-drill.html':'Flashcards, quiz and scenario practice for Security+ Domain 4.',
 'domain5-notebook.html':'Searchable reference notes for Security+ Domain 5.',
 'domain5-match.html':'Term-and-definition matching game for Security+ Domain 5.',
 'domain5-drill.html':'Flashcards, quiz and scenario practice for Security+ Domain 5.',
 'acronym-drill.html':'All 333 CompTIA Security+ SY0-701 acronyms as flashcards, a quiz and a searchable list.',
 'prep-scheduler.html':'Turns your Security+ exam date into a day-by-day study and drill plan that follows your weak spots.',
}

for srcname, outname in FILES.items():
    s = open(srcname).read()

    # pull <title> out of the fragment so it can go in <head>
    m = re.search(r'<title>(.*?)</title>', s)
    title = m.group(1) if m else outname
    s = re.sub(r'<title>.*?</title>\s*', '', s, count=1)

    # rewrite artifact URLs -> relative filenames
    for url, fname in ART_TO_FILE.items():
        s = s.replace(url, fname)

    head = HEAD.format(desc=DESC[outname]) + f'<title>{title}</title>\n</head>\n<body>\n'
    doc = head + s.strip() + '\n</body>\n</html>\n'
    (OUT/outname).write_text(doc, encoding='utf-8')
    print(f'{outname:24} {len(doc)//1024:4} KB   title="{title}"')

# report any leftover absolute claude.ai links
print('\n--- remaining claude.ai links ---')
found = False
for f in OUT.glob('*.html'):
    for line in f.read_text(encoding='utf-8').splitlines():
        if 'claude.ai' in line:
            found = True
            print(f'{f.name}: {line.strip()[:120]}')
if not found: print('none')
