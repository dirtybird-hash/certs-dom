"""Generate the CySA+ Domain 1 Drill page from d1_data.py.

The page design lives in kit/drill_template.html, derived from the published
page itself so regenerating cannot drift from what shipped. Five markers are
filled with JSON: __FLASH__, __QUIZ__, __SCEN__, __OBJTITLE__, __OBJS__.

Storage key: cysa:domain1drill:v1
    {cardStatus:{...}, objStats:{"1.1":{c:correct, t:total}, ...}}

objStats is what the Progress tab reports as per-objective accuracy. It follows
the Security+ schema deliberately, so the same readiness reporting works.

Usage:  python3 drill_page.py
"""
import json, html, pathlib
import importlib.util

HERE = pathlib.Path(__file__).parent
spec = importlib.util.spec_from_file_location('d1_data', HERE / 'd1_data.py')
D = importlib.util.module_from_spec(spec)
spec.loader.exec_module(D)


def esc(s):
    return html.escape(s, quote=False).replace('"', '&quot;')


def rich(s):
    """Escape, then let newlines become line breaks inside an answer."""
    return esc(s).replace('\n', '<br>')


FLASH = [{'o': o, 'f': esc(f), 'b': rich(b)} for o, f, b in D.FLASHCARDS]
QUIZ = [{'o': o, 'q': esc(q), 'c': [esc(x) for x in c], 'a': a, 'e': rich(e)}
        for o, q, c, a, e in D.QUIZ]
SCEN = [{'o': o, 's': esc(s), 'q': esc(q), 'c': [esc(x) for x in c], 'a': a, 'e': rich(e)}
        for o, s, q, c, a, e in D.SCENARIOS]
OBJS = sorted(D.OBJTITLE)
OBJTITLE = {k: esc(v) for k, v in D.OBJTITLE.items()}

# every item must carry an objective the page knows about, or the Progress
# tab silently under-reports — this has bitten before, so it is checked.
for name, rows in (('FLASHCARDS', FLASH), ('QUIZ', QUIZ), ('SCENARIOS', SCEN)):
    bad = sorted({r['o'] for r in rows} - set(OBJS))
    if bad:
        raise SystemExit(f'{name}: unknown objective(s) {bad}; OBJTITLE knows {OBJS}')
for q in QUIZ + SCEN:
    if not (len(q['c']) == 4 and 0 <= q['a'] < 4):
        raise SystemExit(f'bad choice set: {q["q"][:60]}')

page = (pathlib.Path(HERE / 'kit' / 'drill_template.html').read_text(encoding='utf-8')
        .replace('__FLASH__', json.dumps(FLASH, ensure_ascii=False, separators=(",", ": ")))
        .replace('__QUIZ__', json.dumps(QUIZ, ensure_ascii=False, separators=(",", ": ")))
        .replace('__SCEN__', json.dumps(SCEN, ensure_ascii=False, separators=(",", ": ")))
        .replace('__OBJTITLE__', json.dumps(OBJTITLE, ensure_ascii=False, separators=(",", ": ")))
        .replace('__OBJS__', json.dumps(OBJS, ensure_ascii=False, separators=(",", ": "))))

out = pathlib.Path('/home/claude/cysa-domain1-drill.html')
out.write_text(page, encoding='utf-8')
print(f'written {out}  {len(page)//1024} KB')
print(f'flash {len(FLASH)} | quiz {len(QUIZ)} | scen {len(SCEN)}')
for o in OBJS:
    print(f'   {o}  {sum(1 for x in FLASH if x["o"]==o):>3} / '
          f'{sum(1 for x in QUIZ if x["o"]==o):>2} / '
          f'{sum(1 for x in SCEN if x["o"]==o):>2}   {D.OBJTITLE[o]}')
