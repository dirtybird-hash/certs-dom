"""General-knowledge behavior in each Domain Drill.

1. Every card and question shows exactly one badge: Exam objective or General knowledge.
2. "Exam only" removes exactly the general-knowledge items from the flashcard deck.
3. Answering a general-knowledge question records into gkStats, never objStats,
   and an exam question records into objStats, never gkStats.

Usage: PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers python3 test_gk.py
"""
import pathlib
from playwright.sync_api import sync_playwright

fails = []
with sync_playwright() as pw:
    b = pw.chromium.launch()
    for n in (1, 2, 3, 4):
        pg = b.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(pathlib.Path(f'/home/claude/cysa-domain{n}-drill.html').as_uri())
        key = f'cysa:domain{n}drill:v1'
        total, gkf = pg.evaluate('[FLASH.length, FLASH.filter(x=>x.g).length]')
        # 1. badges on the flashcard face, both kinds seen across the deck
        seen = set(); badge_ok = True
        for _ in range(total):
            kinds = pg.eval_on_selector_all('#p-flash .kind', 'e=>e.map(x=>x.textContent)')
            badge_ok &= len(kinds) == 1; seen.update(kinds)
            pg.click('#f-known')
        # 2. exam-only count
        full = int(pg.inner_text('#p-flash .count').split('/')[1])
        pg.click('#examonly')
        exam = int(pg.inner_text('#p-flash .count').split('/')[1])
        ok_toggle = full == total and exam == total - gkf
        pg.click('#examonly')
        # 3. scoring separation: answer one GK and one exam quiz question
        pg.evaluate(f'localStorage.removeItem("{key}")'); pg.reload(); pg.click('#t-quiz')
        got = {'gk': False, 'ex': False}
        for _ in range(200):
            is_gk = pg.evaluate("document.querySelector('#p-quiz .kind').classList.contains('gk')")
            k = 'gk' if is_gk else 'ex'
            if not got[k]:
                before = pg.evaluate(f'JSON.parse(localStorage.getItem("{key}")||"{{}}")')
                pg.click('#p-quiz .choice >> nth=0')
                after = pg.evaluate(f'JSON.parse(localStorage.getItem("{key}"))')
                tot = lambda d, f: sum(v['t'] for v in (d.get(f) or {}).values())
                if is_gk: got['gk'] = tot(after, 'gkStats') == tot(before, 'gkStats') + 1 and tot(after, 'objStats') == tot(before, 'objStats')
                else:     got['ex'] = tot(after, 'objStats') == tot(before, 'objStats') + 1 and tot(after, 'gkStats') == tot(before, 'gkStats')
            if all(got.values()): break
            pg.click('#p-quiz-next')
        pg.click('#t-prog')
        prog = pg.inner_text('#p-prog')
        ok = badge_ok and seen == {'Exam objective', 'General knowledge'} and ok_toggle and all(got.values()) and 'General knowledge' in prog and not errs
        print(f'{"PASS" if ok else "FAIL"}  domain {n}: badges one-per-card {badge_ok} kinds {sorted(seen)} | deck {full} -> exam-only {exam} (GK {gkf}) | '
              f'scored separately gk={got["gk"]} exam={got["ex"]} | GK line in Progress {"General knowledge" in prog} | errors {errs or "none"}')
        if not ok: fails.append(n)
    b.close()
print('RESULT:', 'ALL PASS' if not fails else f'FAILURES {fails}')
