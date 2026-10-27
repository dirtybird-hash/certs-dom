"""Search box in each Domain Drill (always visible, above the tabs).

Checks: the box is visible on load; '/' focuses it; typing shows results for a
known item with every term highlighted and the answer shown; objective filters
hide while results show; no-match and too-short messages; Esc clears and returns
to the tab you were on; clicking a tab clears the search; nothing is recorded;
fits a phone screen.

Usage: PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers python3 test_search.py
"""
import pathlib
from playwright.sync_api import sync_playwright

PROBES = {1: 'joe sandbox', 2: 'nmap filtered', 3: 'legal hold', 4: 'governance'}
fails = []
with sync_playwright() as pw:
    b = pw.chromium.launch()
    for n, probe in PROBES.items():
        url = pathlib.Path(f'/home/claude/cysa-domain{n}-drill.html').as_uri()
        pg = b.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(url)
        before = pg.evaluate(f'localStorage.getItem("cysa:domain{n}drill:v1")')
        visible_on_load = pg.is_visible('#sq')
        pg.click('#t-quiz')
        pg.keyboard.press('/')
        focused = pg.evaluate('document.activeElement.id') == 'sq'
        pg.keyboard.type(probe)
        results_open = pg.is_visible('#p-srch') and not pg.is_visible('#p-quiz')
        filters_hidden = not pg.is_visible('.filters')
        hits = pg.locator('#sres .hit').count()
        marks = pg.evaluate("[...document.querySelectorAll('#sres mark')].map(m=>m.textContent.toLowerCase())")
        every_term = all(any(t in m for m in marks) for t in probe.split())
        answers = hits > 0 and pg.locator('#sres .ha').count() == hits
        pg.fill('#sq', 'zzqqxx'); none_msg = 'Nothing in this domain matches' in pg.inner_text('#sres')
        pg.fill('#sq', 'a'); short_hint = 'at least two characters' in pg.inner_text('#sres')
        pg.focus('#sq'); pg.keyboard.press('Escape')
        esc_back = pg.is_visible('#p-quiz') and not pg.is_visible('#p-srch') and pg.input_value('#sq') == '' and pg.is_visible('.filters')
        pg.fill('#sq', probe); pg.click('#t-flash')
        tab_clears = pg.input_value('#sq') == '' and pg.is_visible('#p-flash')
        after = pg.evaluate(f'localStorage.getItem("cysa:domain{n}drill:v1")')
        m = b.new_page(viewport={'width': 390, 'height': 800}); m.goto(url); m.fill('#sq', probe)
        w = m.evaluate('[document.documentElement.scrollWidth, document.documentElement.clientWidth]')
        ok = all([visible_on_load, focused, results_open, filters_hidden, hits > 0, every_term, answers, none_msg,
                  short_hint, esc_back, tab_clears, before == after, w[0] <= w[1]]) and not errs
        print(f'{"PASS" if ok else "FAIL"}  domain {n}: box on load {visible_on_load} | "/" focuses {focused} | "{probe}" -> {hits} hits, '
              f'terms marked {every_term}, answers {answers} | filters hidden {filters_hidden} | no-match {none_msg} short {short_hint} | '
              f'Esc back to Quiz {esc_back} | tab clears {tab_clears} | storage untouched {before == after} | phone {w} | errors {errs or "none"}')
        if not ok: fails.append(n)
    b.close()
print('RESULT:', 'ALL PASS' if not fails else f'FAILURES {fails}')
