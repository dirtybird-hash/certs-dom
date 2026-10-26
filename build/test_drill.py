"""Drive each Domain Drill: the filter row lists this domain's objectives,
narrowing to one objective narrows the flashcards, and a quiz answer is
recorded in objStats under an objective of this domain.

Usage: PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers python3 test_drill.py [N ...]
"""
import sys, json, pathlib
from playwright.sync_api import sync_playwright

ns = [int(a) for a in sys.argv[1:]] or [1, 2, 3, 4]
fails = []
with sync_playwright() as pw:
    b = pw.chromium.launch()
    for n in ns:
        pg = b.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(pathlib.Path(f'/home/claude/cysa-domain{n}-drill.html').as_uri())
        objs = pg.evaluate('OBJS')
        btns = pg.evaluate("[...document.querySelectorAll('.obj')].map(b => b.getAttribute('data-o'))")
        ok_btns = btns == objs and all(o.startswith(f'{n}.') for o in objs)
        # narrow to the first objective: turn off every other button
        for o in objs[1:]:
            pg.click(f'.obj[data-o="{o}"]')
        count = pg.inner_text('#p-flash .count')
        want = pg.evaluate(f'FLASH.filter(x => x.o === "{objs[0]}").length')
        ok_filter = count.endswith(f'/ {want}') and pg.inner_text('#p-flash .otag') == objs[0]
        # restore all, answer one quiz question
        for o in objs[1:]:
            pg.click(f'.obj[data-o="{o}"]')
        pg.click('#t-quiz'); pg.click('#p-quiz .choice >> nth=0')
        st = pg.evaluate(f'JSON.parse(localStorage.getItem("cysa:domain{n}drill:v1"))')
        # one answer lands in objStats (exam item) or gkStats (general knowledge), never both
        rec = dict(st.get('objStats') or {}, **{'GK ' + k: v for k, v in (st.get('gkStats') or {}).items()}) if st else {}
        ok_rec = sum(v['t'] for v in rec.values()) == 1 and all(k.replace('GK ', '').startswith(f'{n}.') for k in rec)
        # choices are shuffled per showing: answer 40 questions by content, check
        # every answer scores and the right letter is spread across A-D
        pg.evaluate(f'localStorage.removeItem("cysa:domain{n}drill:v1")'); pg.reload(); pg.click('#t-quiz')
        letters, right = [], 0
        for _ in range(40):
            info = pg.evaluate('''() => {
              const t = document.querySelector('#p-quiz .qtext').textContent;
              const dec = h => { const d = document.createElement('div'); d.innerHTML = h; return d.textContent; };
              const q = QUIZ.find(x => dec(x.q) === t);
              const b = [...document.querySelectorAll('#p-quiz .choice')].find(x => +x.dataset.k === q.a);
              return b.querySelector('.k').textContent;
            }''')
            letters.append(info)
            pg.click(f'#p-quiz .choice:has(.k:text-is("{info}"))')
            right += pg.inner_text('#p-quiz-ex b').strip().lower() == 'correct'
            pg.click('#p-quiz-next')
        spread = {l: letters.count(l) for l in 'ABCD'}
        ok_shuffle = right == 40 and sum(1 for v in spread.values() if v) >= 3
        good = ok_btns and ok_filter and ok_rec and ok_shuffle and not errs
        print(f'{"PASS" if good else "FAIL"}  domain {n}: buttons {btns}  narrowed "{count}" (want {want})  recorded {rec}  40 answered by content: {right} scored correct, correct letter spread {spread}  errors {errs or "none"}')
        if not good: fails.append(n)
    b.close()
print('RESULT:', 'ALL PASS' if not fails else f'FAILURES {fails}')
