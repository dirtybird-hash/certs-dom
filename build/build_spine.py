"""Turn the extracted lines into the objective spine.

Layout: each page stacks two or three objectives as horizontal BANDS. Within a
band the bullets run across three columns. So the reading order is
page -> band -> column -> top-to-bottom. Reading whole columns down a page
mixes bullets between objectives, which is the trap.

Bullet glyphs (• / - / o) carry the level; a line with no glyph is a wrapped
continuation of the one above it.
"""
import json, re, collections

raw = json.load(open('raw_lines.json'))
OBJHEAD = re.compile(r'^([1-4]\.[1-9])\b\s*(.*)$')
STOP = re.compile(r'Acronym\s+Spelled|CS0-003 Acronym', re.I)
TITLES_ALL = ('Explain the importance of system and network architecture concepts in security operations.|Given a scenario, analyze indicators of potentially malicious activity.|Given a scenario, use appropriate tools or techniques to determine malicious activity.|Compare and contrast threat-intelligence and threat-hunting concepts.|Explain the importance of efficiency and process improvement in security operations.|Given a scenario, implement vulnerability scanning methods and concepts.|Given a scenario, analyze output from vulnerability assessment tools.|Given a scenario, analyze data to prioritize vulnerabilities.|Given a scenario, recommend controls to mitigate attacks and software vulnerabilities.|Explain concepts related to vulnerability response, handling, and management.|Explain concepts related to attack methodology frameworks.|Given a scenario, perform incident response activities.|Explain the preparation and post-incident activity phases of the incident management life cycle.|Explain the importance of vulnerability management reporting and communication.|Explain the importance of incident response reporting and communication.')
def is_title_fragment(t):
    t = t.strip().rstrip('.')
    return len(t) > 8 and any(t in full for full in TITLES_ALL.split('|'))
TITLE_START = re.compile(r'^(Explain|Given a scenario|Compare and contrast)\b', re.I)
NOISE = re.compile(r'^[1-4]\.0\s*\|?\s*$|^[1-4]\.0 \|')

start = next(i for i, r in enumerate(raw) if r['text'].startswith('1.1'))
end = next((i for i, r in enumerate(raw) if STOP.search(r['text']) and i > start), len(raw))
seg = [r for r in raw[start:end] if not NOISE.match(r['text'].strip())]

pages = collections.defaultdict(list)
for r in seg: pages[r['page']].append(r)

ordered, cur_obj = [], None
for pno in sorted(pages):
    rows = pages[pno]
    heads = sorted([r for r in rows if r['col'] == 0 and r['x0'] < 45 and OBJHEAD.match(r['text'])],
                   key=lambda r: r['top'])
    cuts = [h['top'] - 2 for h in heads] + [10**6]
    # anything above the first heading continues the previous objective
    if heads and heads[0]['top'] > 60:
        pre = [r for r in rows if r['top'] < cuts[0]]
        for c in (0, 1, 2):
            ordered += [(cur_obj, r) for r in sorted((x for x in pre if x['col'] == c), key=lambda r: r['top'])]
    elif not heads:
        for c in (0, 1, 2):
            ordered += [(cur_obj, r) for r in sorted((x for x in rows if x['col'] == c), key=lambda r: r['top'])]
    for i, h in enumerate(heads):
        cur_obj = OBJHEAD.match(h['text']).group(1)
        lo, hi = cuts[i], cuts[i + 1] if i + 1 < len(cuts) else 10**6
        band = [r for r in rows if lo <= r['top'] < hi]
        for c in (0, 1, 2):
            ordered += [(cur_obj, r) for r in sorted((x for x in band if x['col'] == c), key=lambda r: r['top'])]

spine = {}
stack = {}
pending = None
for obj, r in ordered:
    if obj is None: continue
    t = r['text'].strip()
    if t == '\u2022':
        pending = 1; continue
    if pending == 1 and not t.startswith(('\u2022','-','\u2013')) and not re.match(r'^o\s', t):
        t = '\u2022 ' + t
    pending = None
    o = spine.setdefault(obj, {'title_parts': [], 'bullets': []})
    m = OBJHEAD.match(t)
    if m and m.group(1) == obj and r['col'] == 0 and r['x0'] < 45:
        if m.group(2): o['title_parts'].append(m.group(2))
        stack = {}
        continue
    if t.startswith('•'):
        n = {'t': t.lstrip('•').strip(), 'children': []}
        o['bullets'].append(n); stack = {1: n}
    elif t.startswith(('-', '–')):
        n = {'t': t.lstrip('-–').strip(), 'children': []}
        (stack[1]['children'] if 1 in stack else o['bullets']).append(n)
        stack = {k: v for k, v in stack.items() if k < 2}; stack[2] = n
    elif re.match(r'^o\s+\S', t):
        n = {'t': t[1:].strip(), 'children': []}
        p = stack.get(2) or stack.get(1)
        (p['children'] if p else o['bullets']).append(n); stack[3] = n
    else:
        if TITLE_START.match(t) or is_title_fragment(t):
            continue
        tgt = stack.get(3) or stack.get(2) or stack.get(1)
        if tgt: tgt['t'] = (tgt['t'] + ' ' + t).strip()
        elif not o['bullets']: o['title_parts'].append(t)

out = {}
for num in sorted(spine):
    out[num] = {'title': re.sub(r'\s+', ' ', ' '.join(spine[num]['title_parts'])).strip(),
                'bullets': spine[num]['bullets']}
cnt = lambda ns: sum(1 + cnt(n['children']) for n in ns)
json.dump(out, open('spine.json', 'w'), indent=1)
tot = 0
for num in sorted(out):
    c = cnt(out[num]['bullets']); tot += c
    print(f"{num}  {c:>3} items  top:{len(out[num]['bullets']):>2}  {out[num]['title'][:58]}")
print('\ntotal:', tot, '| objectives:', len(out))
