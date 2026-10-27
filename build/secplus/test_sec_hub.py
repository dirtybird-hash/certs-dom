"""Headless check of the widened Security+ hub search. Usage: python3 test_sec_hub.py page.html"""
import sys, pathlib
from playwright.sync_api import sync_playwright
PAGE = pathlib.Path(sys.argv[1]).resolve().as_uri()
fails, errs = [], []
def check(n, ok, info=''):
    print(('PASS ' if ok else 'FAIL ') + n, info)
    if not ok: fails.append(n)
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.route('**/fonts.googleapis.com/**', lambda r: r.abort())
    pg.goto(PAGE); pg.wait_for_timeout(150)
    def s(q):
        pg.fill('#gsearch', q); pg.wait_for_timeout(200)
        return pg.evaluate("""({n:document.querySelectorAll('.hit').length,
          kinds:[...document.querySelectorAll('.hit .kchip')].map(e=>e.textContent),
          first:(document.querySelector('.hit .hit-title')||{}).textContent,
          chips:[...document.querySelectorAll('.kfilter button')].map(b=>b.textContent)})""")
    r = s('ocsp'); check('notes still found', 'Note' in r['kinds'], r['chips'])
    check('drill items found', any(k in ('Flashcard','Quiz','Scenario') for k in r['kinds']), r['kinds'][:8])
    r = s('sase'); check('exact acronym ranks first', r['first'].startswith('SASE'), r['first'])
    r = s('hmac'); check('acronym searchable', 'Acronym' in r['kinds'], r['kinds'][:5])
    s('phishing')
    pg.click('.kfilter button[data-kind="Drill"]'); pg.wait_for_timeout(80)
    k = set(pg.evaluate("[...document.querySelectorAll('.hit .kchip')].map(e=>e.textContent)"))
    check('filter to drill questions', k and k <= {'Flashcard','Quiz','Scenario'}, k)
    pg.click('.kfilter button[data-kind=""]'); pg.wait_for_timeout(80)
    pg.click('.hit .hit-head'); pg.wait_for_timeout(50)
    check('hit expands', pg.evaluate("document.querySelector('.hit').classList.contains('open')"))
    links = pg.evaluate("[...document.querySelectorAll('.hit-open')].map(a=>a.getAttribute('href'))")
    check('links resolve', links and all(l and 'undefined' not in l for l in links), links[:3])
    pg.press('#gsearch', 'Escape'); pg.wait_for_timeout(50)
    check('Esc restores browse view', pg.is_visible('#domtabs') and pg.is_hidden('#gresults'))
    p3 = b.new_page(viewport={'width': 390, 'height': 800}); p3.route('**/fonts.googleapis.com/**', lambda r: r.abort())
    p3.goto(PAGE); p3.fill('#gsearch', 'certificate'); p3.wait_for_timeout(250)
    w = p3.evaluate('[document.documentElement.scrollWidth, document.documentElement.clientWidth]')
    check('no horizontal scroll at 390px', w[0] <= w[1], w)
    p3.screenshot(path='/home/claude/build/secplus/phone.png')
    b.close()
print('page errors:', errs or 'none'); print('RESULT:', 'ALL PASS' if not fails and not errs else f'FAILURES {fails}')
