"""Column-aware extraction of the CS0-003 objective spine.

pdftotext reads straight across the page, interleaving the PDF's three columns
and scrambling every bullet hierarchy. This reads each column top-to-bottom
instead, then rebuilds the tree from each line's indent.

Columns sit at x0 ~55, ~240 and ~415, with gutters at 232 and 402.
"""
import pdfplumber, re, json

PDF = '/mnt/user-data/uploads/StudyMaterials/CySA+/Course_Resources_export/comptia-cysa-cs0-003-exam-objectives-2-0.pdf'
COLS = [(0, 231.5), (231.5, 401.5), (401.5, 612)]   # glyphs sit exactly on 232/410
SKIP = re.compile(r'CompTIA Cybersecurity Analyst|Certification Exam: Exam Objectives|Copyright ©|^\d\.0 \||^Page \d|EXAM ACCREDITATION|'
                  r'EXAM DEVELOPMENT|TEST DETAILS|TEST OBJECTIVES|^\d+\.0 [A-Z]', re.I)

def lines(words, x0, x1, ytol=3.0):
    sel = sorted((w for w in words if x0 <= w['x0'] < x1), key=lambda w: (w['top'], w['x0']))
    out, cur = [], []
    for w in sel:
        if cur and abs(w['top'] - cur[0]['top']) <= ytol:
            cur.append(w)
        else:
            if cur: out.append(cur)
            cur = [w]
    if cur: out.append(cur)
    res = []
    for ls in out:
        ls.sort(key=lambda w: w['x0'])
        res.append({'top': ls[0]['top'], 'x0': ls[0]['x0'],
                    'text': ' '.join(w['text'] for w in ls).strip()})
    return res

raw = []
with pdfplumber.open(PDF) as pdf:
    for pno, page in enumerate(pdf.pages, 1):
        ws = page.extract_words(use_text_flow=False)
        for ci, (a, b) in enumerate(COLS):
            for ln in lines(ws, a, b):
                if not ln['text'] or SKIP.search(ln['text']): continue
                raw.append({'page': pno, 'col': ci, 'x0': round(ln['x0'], 1),
                            'top': round(ln['top'], 1), 'text': ln['text']})

json.dump(raw, open('raw_lines.json', 'w'), indent=0)
print('lines:', len(raw))
import collections
h = collections.Counter(int(r['x0'] // 5) * 5 for r in raw)
print('indent buckets (x0 -> count):')
for k in sorted(h):
    if h[k] > 3: print(f'   {k:>4} {h[k]:>4}')
