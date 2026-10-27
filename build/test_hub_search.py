"""Headless check of the CySA+ hub's toolkit-wide search, and of the drill #q= hand-off.
Usage: PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers python3 build/test_hub_search.py
"""
import pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path('/home/claude')
HUB = (ROOT / 'cysa-hub.html').resolve().as_uri()
fails, errs = [], []

def check(name, ok, info=''):
    print(('PASS ' if ok else 'FAIL ') + name, info)
    if not ok: fails.append(name)

with sync_playwright() as pw:
    b = pw.chromium.launch()
    pg = b.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(HUB)
    n = pg.evaluate('HUBIDX.length')
    srcs = pg.evaluate('[...new Set(HUBIDX.map(x=>x.s))].sort()')
    check('index covers every tool', srcs == ['d1', 'd2', 'd3', 'd4', 'nb', 'ops', 'pbq', 'sf'], f'{n} entries {srcs}')
    check('results hidden at rest', pg.is_hidden('#gres'))

    def search(q):
        pg.fill('#gq', q); pg.wait_for_timeout(200)
        return pg.evaluate('''() => ({hits: document.querySelectorAll('.ghit').length,
            count: (document.querySelector('.gcount')||{}).textContent || '',
            srcs: [...new Set([...document.querySelectorAll('.ghit .src')].map(e=>e.textContent))],
            marks: document.querySelectorAll('.ghit mark').length,
            none: !!document.querySelector('.gnone')})''')

    r = search('cvss')
    check('cvss spans several tools', r['hits'] > 3 and len(r['srcs']) >= 2 and r['marks'] > 0, r)
    r = search('netstat')
    check('task content searchable', 'Performance Tasks' in r['srcs'], r)
    r = search('get-filehash')
    check('Simple Flash content searchable', 'Simple Flash' in r['srcs'], r)
    r = search('mttd')
    check('Domain 4 content searchable', 'Domain 4 Drill' in r['srcs'], r)
    r = search('kill chain reconnaissance')
    check('multi-word AND search', r['hits'] > 0, r)
    r = search('dmarc')
    first = pg.evaluate("[...document.querySelectorAll('.ghit')].slice(0,2).map(h=>h.querySelector('.k').textContent+':'+h.querySelector('.gq').textContent)")
    check('acronym ranks first, then note', first[0].startswith('Acronym:DMARC') and first[1].startswith('Note:'), first)
    nbl = pg.evaluate("document.querySelector('.ghit .gopen').getAttribute('href')")
    check('notebook link deep-links', '2Zm7Tw7xCVcNJCC9bheaxv#a=DMARC' in nbl, nbl)
    r = search('zzqqxx')
    check('no-match message', r['none'] and r['hits'] == 0, r)

    # source filter
    search('vulnerability')
    total = pg.evaluate("+document.querySelector('.gsrc button[data-s=\"\"] b').textContent")
    pg.click('.gsrc button[data-s="d2"]'); pg.wait_for_timeout(50)
    only = pg.evaluate("[...new Set([...document.querySelectorAll('.ghit .src')].map(e=>e.textContent))]")
    check('filter to one tool', only == ['Domain 2 Drill'], f'{total} total -> {only}')
    check('result cap at 50', pg.evaluate("document.querySelectorAll('.ghit').length") <= 50)
    pg.click('.gsrc button[data-s=""]'); pg.wait_for_timeout(50)

    # links
    search('nmap')
    hrefs = pg.evaluate("[...document.querySelectorAll('.gopen')].map(a=>a.getAttribute('href'))")
    check('drill links carry #q=', any('#q=nmap' in h for h in hrefs), hrefs[:2])
    check('task links carry the task id', any('DoTioR9UxmZx2fEP4NRhrz#' in h for h in hrefs))

    # Esc and clear
    pg.press('#gq', 'Escape'); pg.wait_for_timeout(50)
    check('Esc clears and hides', pg.is_hidden('#gres') and pg.input_value('#gq') == '')
    pg.click('body'); pg.keyboard.press('/')
    check('/ focuses the box', pg.evaluate("document.activeElement.id") == 'gq')

    # html in content must not inject markup
    check('no script injection from content', pg.evaluate("document.querySelectorAll('#gres script').length") == 0)

    # drill hand-off
    for d in range(1, 5):
        p2 = b.new_page(); p2.on('pageerror', lambda e: errs.append(str(e)))
        p2.goto((ROOT / f'cysa-domain{d}-drill.html').resolve().as_uri() + '#q=incident')
        p2.wait_for_timeout(150)
        st = p2.evaluate("({v: document.getElementById('sq').value, open: !document.getElementById('p-srch').hidden})")
        check(f'Domain {d} drill opens on #q= search', st == {'v': 'incident', 'open': True}, st)
        p2.close()

    # phone width
    p3 = b.new_page(viewport={'width': 390, 'height': 800}); p3.goto(HUB)
    p3.fill('#gq', 'cvss'); p3.wait_for_timeout(200)
    w = p3.evaluate('[document.documentElement.scrollWidth, document.documentElement.clientWidth]')
    check('no horizontal scroll at 390px', w[0] <= w[1], w)
    p3.screenshot(path=str(ROOT / 'build/hubsearch-phone.png'), full_page=False)
    pg.set_viewport_size({'width': 1100, 'height': 900}); search('cvss')
    pg.screenshot(path=str(ROOT / 'build/hubsearch.png'))
    b.close()

print('page errors:', errs or 'none')
print('RESULT:', 'ALL PASS' if not fails and not errs else f'FAILURES {fails}')
