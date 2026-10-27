"""Search tab in each Domain Drill: finds known items, highlights every term,
handles no-match, opens with '/', hides objective filters while open, records
nothing, and fits a phone screen.

Usage: PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers python3 test_search.py
"""
import pathlib
from playwright.sync_api import sync_playwright

PROBES = {1: 'joe sandbox', 2: 'nmap filtered', 3: 'legal hold', 4: 'governance'}
fails = []
with sync_playwright() as pw:
    b = pw.chromium.launch()
    for n, probe in PROBES.items():
        pg = b.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(pathlib.Path(f'/home/claude/cysa-domain{n}-drill.html').as_uri())
        before = pg.evaluate(f'localStorage.getItem("cysa:domain{n}drill:v1")')
        pg.keyboard.press('/')
        opened = pg.is_visible('#p-srch') and pg.evaluate('document.activeElement.id') == 'sq'
        filters_hidden = not pg.is_visible('.filters')
        pg.fill('#sq', probe)
        count = pg.inner_text('#scount')
        hits = pg.locator('#sres .hit').count()
        marks = pg.evaluate("[...document.querySelectorAll('#sres mark')].map(m=>m.textContent.toLowerCase())")
        every_term = all(any(t in m for m in marks) for t in probe.split())
        answers = pg.locator('#sres .ha').count() == hits
        pg.fill('#sq', 'zzqqxx')
        none_msg = 'Nothing in this domain matches' in pg.inner_text('#sres')
        pg.fill('#sq', 'a')
        short_hint = 'at least two characters' in pg.inner_text('#sres')
        pg.click('#t-flash')
        filters_back = pg.is_visible('.filters')
        after = pg.evaluate(f'localStorage.getItem("cysa:domain{n}drill:v1")')
        m = b.new_page(viewport={'width': 390, 'height': 800})
        m.goto(pathlib.Path(f'/home/claude/cysa-domain{n}-drill.html').as_uri()); m.click('#t-srch'); m.fill('#sq', probe)
        w = m.evaluate('[document.documentElement.scrollWidth, document.documentElement.clientWidth]')
        ok = opened and filters_hidden and hits > 0 and every_term and answers and none_msg and short_hint and filters_back and before == after and w[0] <= w[1] and not errs
        print(f'{"PASS" if ok else "FAIL"}  domain {n}: "{probe}" -> {count}, {hits} shown, all terms highlighted {every_term}, answers shown {answers} | '
              f"'/' opens+focuses {opened} | filters hidden/back {filters_hidden}/{filters_back} | no-match msg {none_msg} | storage untouched {before == after} | phone {w} | errors {errs or 'none'}")
        if not ok: fails.append(n)
    b.close()
print('RESULT:', 'ALL PASS' if not fails else f'FAILURES {fails}')
