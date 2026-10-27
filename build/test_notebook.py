"""Headless checks for the CySA+ Notebook.
Usage: PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers python3 build/test_notebook.py
"""
import pathlib
from playwright.sync_api import sync_playwright

PAGE = (pathlib.Path('/home/claude') / 'cysa-notebook.html').resolve().as_uri()
fails, errs = [], []
def check(name, ok, info=''):
    print(('PASS ' if ok else 'FAIL ') + name, info)
    if not ok: fails.append(name)

with sync_playwright() as pw:
    b = pw.chromium.launch()
    pg = b.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(PAGE); pg.wait_for_timeout(100)
    n = pg.evaluate('TOPICS.length'); na = pg.evaluate('ACR.length')
    check('data loaded', n >= 60 and na == 128, f'{n} topics, {na} acronyms')
    # every objective has topics on screen
    for d in '1234':
        pg.click(f'[data-tab="{d}"]'); pg.wait_for_timeout(30)
        objs = pg.evaluate("[...document.querySelectorAll('.otitle b')].map(e=>e.textContent)")
        cnt = pg.evaluate("document.querySelectorAll('.topic').length")
        check(f'Domain {d} renders', cnt > 0 and len(objs) > 0, f'{cnt} topics, objectives {objs}')
    # objective filter
    pg.click('[data-tab="1"]'); pg.click('[data-obj="1.3"]'); pg.wait_for_timeout(30)
    objs = pg.evaluate("[...new Set([...document.querySelectorAll('.topic .to')].map(e=>e.textContent))]")
    check('objective filter', objs == ['1.3'], objs)
    # expand / collapse
    pg.click('.topic >> nth=0 >> button'); pg.wait_for_timeout(30)
    check('topic expands', pg.evaluate("document.querySelector('.topic').classList.contains('open')"))
    link = pg.evaluate("document.querySelector('.topic .drillit').getAttribute('href')")
    check('drill link carries #q=', '#q=' in link and 'KrYojQYtNqGKiiYQQ1iPXy' in link, link)
    # acronyms tab + letter filter
    pg.click('[data-tab="A"]'); pg.wait_for_timeout(30)
    check('acronym tab lists all', pg.evaluate("document.querySelectorAll('.acr').length") == 128)
    pg.click('[data-letter="D"]'); pg.wait_for_timeout(30)
    ds = pg.evaluate("[...document.querySelectorAll('.acr .a')].map(e=>e.textContent)")
    check('letter filter', ds and all(x.startswith('D') for x in ds), ds)
    fixes = pg.evaluate("[...document.querySelectorAll('.acr .f')].length")
    check('corrections shown for DNS/DKIM', fixes >= 2, fixes)
    # search
    def s(q):
        pg.fill('#q', q); pg.wait_for_timeout(200)
        return pg.evaluate("({t:document.querySelectorAll('.sres .topic').length, a:document.querySelectorAll('.sres .acr').length, first:(document.querySelector('.sres .acr .a')||{}).textContent, m:document.querySelectorAll('mark').length, none:!!document.querySelector('.none')})")
    r = s('dmarc'); check('search dmarc: acronym first + topic', r['first'] == 'DMARC' and r['t'] >= 1 and r['m'] > 0, r)
    r = s('sasE'); check('case-insensitive', r['a'] >= 1, r)
    r = s('2.3'); check('objective search 2.3', r['t'] >= 3, r)
    r = s('order of volatility'); check('multi-word', r['t'] >= 1, r)
    r = s('qqzzxx'); check('no match message', r['none'], r)
    # marks must not break entities or tags
    r = s('rsquo'); check('entity names are not matched', r['t'] == 0 and r['a'] == 0, r)
    pg.press('#q', 'Escape'); pg.wait_for_timeout(50)
    check('Esc returns to tabs', pg.evaluate("!!document.querySelector('.tab[aria-selected=\"true\"]')"))
    # deep links
    p2 = b.new_page(); p2.on('pageerror', lambda e: errs.append(str(e)))
    p2.goto(PAGE + '#t=email-analysis'); p2.wait_for_timeout(150)
    check('#t= opens topic', p2.evaluate("document.getElementById('t-email-analysis').classList.contains('open')"))
    p2.goto(PAGE + '#a=CVSS'); p2.wait_for_timeout(150)
    check('#a= finds acronym', p2.evaluate("(document.querySelector('.sres .acr .a')||{}).textContent") == 'CVSS')
    # every topic body: balanced tables, no raw template leftovers
    bad = pg.evaluate("TOPICS.filter(t => (t.h.match(/<table/g)||[]).length !== (t.h.match(/<\\/table>/g)||[]).length || /__|\\{\\}/.test(t.h)).map(t=>t.id)")
    check('topic HTML well-formed', not bad, bad)
    # phone
    p3 = b.new_page(viewport={'width': 390, 'height': 800}); p3.goto(PAGE + '#t=packet-capture'); p3.wait_for_timeout(150)
    w = p3.evaluate('[document.documentElement.scrollWidth, document.documentElement.clientWidth]')
    check('no horizontal scroll at 390px', w[0] <= w[1], w)
    p3.screenshot(path='/home/claude/build/nb-phone.png')
    for d in 'A':
        p3.click(f'[data-tab="{d}"]'); p3.wait_for_timeout(50)
        w = p3.evaluate('[document.documentElement.scrollWidth, document.documentElement.clientWidth]')
        check('acronyms fit at 390px', w[0] <= w[1], w)
    pg.set_viewport_size({'width': 1100, 'height': 900}); pg.goto(PAGE + '#t=cvss'); pg.wait_for_timeout(150)
    pg.screenshot(path='/home/claude/build/nb-desk.png')
    b.close()
print('page errors:', errs or 'none')
print('RESULT:', 'ALL PASS' if not fails and not errs else f'FAILURES {fails}')
