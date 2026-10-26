"""Generate CySA+ Domain Drill pages from d<N>_data.py.

The page design lives in kit/drill_template.html, derived from the published
pages so regenerating cannot drift from what shipped. Placeholders:
    data   __FLASH__ __QUIZ__ __SCEN__ __OBJTITLE__ __OBJS__   (JSON)
    page   __N__ __NAME__ __WEIGHT__ __OBJFIRST__ __OBJLAST__
    objs   __OBJBUTTONS__ __OBJCSS__ __OTAGCSS__   (filter row and its colors,
           built from the domain's own objectives; until 2026-10-25 these were
           hardcoded to 1.1-1.5, so Domains 2-4 shipped with Domain 1 filters)

Storage key per domain: cysa:domain<N>drill:v1
    {cardStatus:{...}, objStats:{"2.1":{c:correct, t:total}, ...}}
objStats is what the Progress tab reports as per-objective accuracy; it follows
the Security+ schema deliberately, so the same readiness reporting works.

Choices are shuffled in the page every time a question is shown, so the stored
answer index never becomes a letter to memorize. (Until 2026-10-25 they were
shown in stored order, and 137 of 142 answers sat in position B.)

General knowledge: each data file may also define GK_FLASHCARDS, GK_QUIZ and
GK_SCENARIOS (same shapes). Those items are cybersecurity material that is not
on the CS0-003 objectives. They carry 'g': 1, every item on the page is badged
"Exam objective" or "General knowledge", an "Exam only" toggle hides GK, and GK
answers are recorded in state.gkStats so objStats stays exam-only.

Guard rails: refuses to write if an item carries an objective outside its
domain, if OBJTITLE does not know an objective, or if a choice set is not four
options with a valid answer index. An unknown objective tag would otherwise
silently under-report accuracy.

Usage:  python3 drill_page.py          build every domain that has a data file
        python3 drill_page.py 2        build Domain 2 only
Output: /home/claude/cysa-domain<N>-drill.html (the name tools/build_repo.py reads)
"""
import json, html, pathlib, sys
import importlib.util

HERE = pathlib.Path(__file__).parent
OUTDIR = pathlib.Path('/home/claude')

DOMAINS = {   # number: (name as it appears in the page, exam weight %)
    1: ('Security Operations', 33),
    2: ('Vulnerability Management', 30),
    3: ('Incident Response &amp; Management', 20),
    4: ('Reporting &amp; Communication', 17),
}


def esc(s):
    return html.escape(s, quote=False).replace('"', '&quot;')


def rich(s):
    """Escape, then let newlines become line breaks inside an answer."""
    return esc(s).replace('\n', '<br>')


def js(x):
    return json.dumps(x, ensure_ascii=False, separators=(",", ": "))


def objparts(objs, titles):
    """Filter buttons and their per-objective colors (--o1..--o5 by position)."""
    buttons = ''.join(f'<button class="obj" data-o="{o}" aria-pressed="true">{o} {titles[o]}</button>'
                      for o in objs)
    objcss = '\n'.join(f'.obj[data-o="{o}"][aria-pressed="true"]{{background:var(--o{i});}}'
                        for i, o in enumerate(objs, 1))
    tags = [f'.otag[data-o="{o}"]{{background:var(--o{i});}}' for i, o in enumerate(objs, 1)]
    otagcss = '\n'.join(' '.join(tags[k:k + 2]) for k in range(0, len(tags), 2))
    return buttons, objcss, otagcss


def build(n):
    spec = importlib.util.spec_from_file_location(f'd{n}_data', HERE / f'd{n}_data.py')
    D = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(D)

    def flash(rows, gk):
        return [dict({'o': o, 'f': esc(f), 'b': rich(b)}, **({'g': 1} if gk else {})) for o, f, b in rows]

    def quiz(rows, gk):
        return [dict({'o': o, 'q': esc(q), 'c': [esc(x) for x in c], 'a': a, 'e': rich(e)}, **({'g': 1} if gk else {}))
                for o, q, c, a, e in rows]

    def scen(rows, gk):
        return [dict({'o': o, 's': esc(s), 'q': esc(q), 'c': [esc(x) for x in c], 'a': a, 'e': rich(e)}, **({'g': 1} if gk else {}))
                for o, s, q, c, a, e in rows]

    # General-knowledge items (GK_*) are filed under the nearest objective of the
    # domain, badged on the page, hidden by "Exam only", and scored in gkStats.
    FLASH = flash(D.FLASHCARDS, False) + flash(getattr(D, 'GK_FLASHCARDS', []), True)
    QUIZ = quiz(D.QUIZ, False) + quiz(getattr(D, 'GK_QUIZ', []), True)
    SCEN = scen(D.SCENARIOS, False) + scen(getattr(D, 'GK_SCENARIOS', []), True)
    OBJS = sorted(D.OBJTITLE)
    OBJTITLE = {k: esc(v) for k, v in D.OBJTITLE.items()}

    wrong = [o for o in OBJS if o.split('.')[0] != str(n)]
    if wrong:
        raise SystemExit(f'domain {n}: OBJTITLE carries objectives from another domain: {wrong}')
    for name, rows in (('FLASHCARDS', FLASH), ('QUIZ', QUIZ), ('SCENARIOS', SCEN)):
        bad = sorted({r['o'] for r in rows} - set(OBJS))
        if bad:
            raise SystemExit(f'domain {n} {name}: unknown objective(s) {bad}; OBJTITLE knows {OBJS}')
    for q in QUIZ + SCEN:
        if not (len(q['c']) == 4 and 0 <= q['a'] < 4):
            raise SystemExit(f'domain {n}: bad choice set: {q["q"][:60]}')

    if len(OBJS) > 5:
        raise SystemExit(f'domain {n}: template has colors for 5 objectives, got {len(OBJS)}')
    buttons, objcss, otagcss = objparts(OBJS, OBJTITLE)
    name, weight = DOMAINS[n]
    page = (pathlib.Path(HERE / 'kit' / 'drill_template.html').read_text(encoding='utf-8')
            .replace('__FLASH__', js(FLASH)).replace('__QUIZ__', js(QUIZ))
            .replace('__SCEN__', js(SCEN)).replace('__OBJTITLE__', js(OBJTITLE))
            .replace('__OBJS__', js(OBJS))
            .replace('__OBJBUTTONS__', buttons).replace('__OBJCSS__', objcss)
            .replace('__OTAGCSS__', otagcss)
            .replace('__NAME__', name).replace('__WEIGHT__', str(weight))
            .replace('__OBJFIRST__', OBJS[0]).replace('__OBJLAST__', OBJS[-1])
            .replace('__N__', str(n)))
    if '__' in page and any(f'__{k}__' in page for k in
                            ['FLASH', 'QUIZ', 'SCEN', 'OBJTITLE', 'OBJS', 'NAME', 'WEIGHT', 'OBJFIRST', 'OBJLAST', 'N',
                             'OBJBUTTONS', 'OBJCSS', 'OTAGCSS']):
        raise SystemExit(f'domain {n}: unfilled placeholder left in page')

    out = OUTDIR / f'cysa-domain{n}-drill.html'
    out.write_text(page, encoding='utf-8')
    gk = lambda rows: sum(1 for r in rows if r.get('g'))
    print(f'written {out}  {len(page)//1024} KB | flash {len(FLASH)} | quiz {len(QUIZ)} | scen {len(SCEN)}'
          f'  (general knowledge: {gk(FLASH)} / {gk(QUIZ)} / {gk(SCEN)})')
    for o in OBJS:
        print(f'   {o}  {sum(1 for x in FLASH if x["o"]==o):>3} / '
              f'{sum(1 for x in QUIZ if x["o"]==o):>2} / '
              f'{sum(1 for x in SCEN if x["o"]==o):>2}   {D.OBJTITLE[o]}')
    return out


if __name__ == '__main__':
    todo = [int(a) for a in sys.argv[1:]] or [n for n in DOMAINS if (HERE / f'd{n}_data.py').exists()]
    for n in todo:
        build(n)
