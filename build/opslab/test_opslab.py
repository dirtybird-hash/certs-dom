"""Drive every Ops Lab drill right and wrong through the UI, check storage, review, workbench.
Usage: PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers python3 build/opslab/test_opslab.py
"""
import pathlib, json, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent)); sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
from ops_data import D as _D
N = len(_D)   # drill count comes from the data file, not a hardcoded number
from playwright.sync_api import sync_playwright

PAGE = pathlib.Path('/home/claude/cysa-opslab.html').resolve().as_uri()
fails, errs = [], []
def check(n, ok, info=''):
    if not ok or info == 'show': print(('PASS ' if ok else 'FAIL ') + n, '' if info == 'show' else info)
    if not ok: fails.append(n)

ANSWER = r"""
([mode]) => {
  const C = OPS.CUR(), d = C.d;
  const click = sel => { const el = document.querySelector(sel); if (!el) throw new Error('missing ' + sel); el.click(); };
  if (d.ty === 'single' || d.ty === 'score'){
    const want = mode === 'right' ? d.ans : (d.ans + 1) % d.opts.length;
    if (d.ty === 'score'){
      const r = CVSS.score(CVSS.parse(d.vec));
      const sv = document.getElementById('sv'), ss = document.getElementById('ss');
      sv.value = mode === 'right' ? r.base.toFixed(1) : (r.base > 1 ? r.base - 1 : r.base + 1).toFixed(1); sv.dispatchEvent(new Event('input', {bubbles:true}));
      ss.value = r.sev; ss.dispatchEvent(new Event('change', {bubbles:true}));
    }
    click('[data-opt="' + want + '"]');
  } else if (d.ty === 'multi'){
    const want = mode === 'right' ? d.ans : d.opts.map((_, i) => i).filter(i => !d.ans.includes(i));
    want.forEach(i => click('[data-opt="' + i + '"]'));
  } else if (d.ty === 'line'){
    click('[data-line="' + (mode === 'right' ? d.ans : (d.ans + 1) % d.art.length) + '"]');
  } else if (d.ty === 'order'){
    // bubble into correct order with the up buttons; wrong mode = leave the (never-correct) shuffle
    if (mode === 'right'){
      for (let pass = 0; pass < 20; pass++){
        const o = OPS.CUR().order; let moved = false;
        for (let p = 1; p < o.length; p++){ if (o[p] < o[p-1]){ click('[data-up="' + p + '"]'); moved = true; break; } }
        if (!moved) break;
      }
    }
  }
  click('#chk');
  return {ok: OPS.CUR().ok, checked: OPS.CUR().checked, fb: !!document.querySelector('.fb'),
          whys: document.querySelectorAll('.why, .lw').length, nb: (document.querySelector('.fb a')||{}).href || ''};
}
"""

with sync_playwright() as pw:
    b = pw.chromium.launch()
    pg = b.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.route('**/fonts.googleapis.com/**', lambda r: r.abort())
    pg.goto(PAGE); pg.wait_for_timeout(100)
    drills = pg.evaluate('DRILLS.map(d => ({id:d.id, ty:d.ty, o:d.o, tr:d.tr}))')
    check(f'{N} drills loaded', len(drills) == N, len(drills))
    bad = []
    for d in drills:
        pg.goto(PAGE + '#d=' + d['id']); pg.wait_for_timeout(30)
        assert pg.evaluate('OPS.CUR().d.id') == d['id']
        r = pg.evaluate(ANSWER, ['right'])
        if not (r['ok'] and r['checked'] and r['fb'] and r['whys'] > 0 and '#t=' in r['nb']): bad.append(('right', d['id'], r))
        pg.click('#again'); pg.wait_for_timeout(20)
        r2 = pg.evaluate(ANSWER, ['wrong'])
        if r2['ok'] or not r2['checked']: bad.append(('wrong', d['id'], r2))
    check('every drill scores right answers right and wrong answers wrong', not bad, bad[:5])
    st = pg.evaluate('OPS.S()')
    allfirst = all(st['att'][d['id']]['first'] == 1 and st['att'][d['id']]['n'] == 2 and st['att'][d['id']]['last'] == 0 for d in drills)
    check('storage: first right, latest wrong, 2 attempts each', allfirst)
    per = {}
    for d in drills: per[d['o']] = per.get(d['o'], 0) + 1
    okobj = all(st['obj'][o]['t'] == 2 * n and st['obj'][o]['c'] == n for o, n in per.items())
    check('per-objective stats count every answer', okobj, st['obj'])
    # persistence across reload
    pg.goto(PAGE); pg.wait_for_timeout(80)
    txt = pg.inner_text('#app')
    check(f'home shows retry queue {N} after reload', f'Retry missed ({N})' in txt, txt[:300])
    # review view
    pg.click('.nav [data-view="review"]'); pg.wait_for_timeout(50)
    rows = pg.evaluate("document.querySelectorAll('table.rv tbody tr').length")
    accs = pg.evaluate("[...document.querySelectorAll('.oa .p')].map(e=>e.textContent)")
    check('review lists every drill and objective accuracy', rows == N and all('50%' in a for a in accs), (rows, accs[:4]))
    pg.click('[data-rf="retry"]'); pg.wait_for_timeout(30)
    check('needs-retry filter', pg.evaluate("document.querySelectorAll('table.rv tbody tr').length") == N)
    # unanswered guard
    pg.goto(PAGE + '#d=cv5'); pg.wait_for_timeout(30); pg.click('#chk')
    check('blank answer is not scored', pg.inner_text('#chkmsg') != '' and not pg.evaluate('OPS.CUR().checked'))
    # shuffling changes option order across showings
    orders = set()
    for _ in range(8):
        pg.goto(PAGE + '#d=cv5'); pg.reload(); pg.wait_for_timeout(15)
        orders.add(tuple(pg.evaluate('OPS.CUR().perm')))
    check('choices shuffle between showings', len(orders) > 1, len(orders))
    # workbench
    pg.goto(PAGE + '#bench'); pg.wait_for_timeout(50)
    def bench(vec):
        pg.fill('#vin', vec); pg.click('#vload'); pg.wait_for_timeout(30)
        return pg.inner_text('#sbox .big').split('/')[0].strip(), pg.inner_text('#verr')
    check('workbench 9.8', bench('CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H')[0] == '9.8')
    check('workbench 9.9 scope changed', bench('CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H')[0] == '9.9')
    check('workbench rejects bad vector', bench('CVSS:3.1/AV:N/AC:L')[1] != '')
    pg.select_option('select[data-m="AV"]', 'P'); pg.wait_for_timeout(30)
    check('metric select recalculates', pg.inner_text('#sbox .big').startswith('7.'), pg.inner_text('#sbox .big'))
    calc = pg.evaluate("document.getElementById('calc').textContent")
    check('calculation shown', 'Exploitability = 8.22' in calc and 'Roundup' in calc)
    # reset two-step
    pg.click('.nav [data-view="review"]'); pg.wait_for_timeout(30)
    pg.click('#reset'); armed = pg.inner_text('#reset')
    pg.click('#reset'); pg.wait_for_timeout(30)
    check('reset needs a second click and clears', 'again' in armed and pg.evaluate('Object.keys(OPS.S().att).length') == 0)
    # miss first, then fix it through the retry queue -> Recovered
    pg.goto(PAGE + '#d=ir3'); pg.reload(); pg.wait_for_timeout(30); pg.evaluate(ANSWER, ['wrong'])
    pg.goto(PAGE); pg.reload(); pg.wait_for_timeout(30)
    pg.click('[data-go="retry"]'); pg.wait_for_timeout(30)
    check('retry queue opens the missed drill', pg.evaluate('OPS.CUR().d.id') == 'ir3')
    pg.evaluate(ANSWER, ['right'])
    pg.click('.nav [data-view="review"]'); pg.wait_for_timeout(30)
    check('recovered counted', pg.evaluate("document.querySelectorAll('.st.rec').length") == 1 and 'Retry missed (0)' in pg.inner_text('#app'))
    # phone width on every type
    p3 = b.new_page(viewport={'width': 390, 'height': 800}); p3.route('**/fonts.googleapis.com/**', lambda r: r.abort())
    over = []
    for did in ['cv1', 'sc2', 'ir2', 'tr4', 'tr8', 'sc1']:
        p3.goto(PAGE + '#d=' + did); p3.wait_for_timeout(40)
        w = p3.evaluate('[document.documentElement.scrollWidth, document.documentElement.clientWidth]')
        if w[0] > w[1]: over.append((did, w))
    for v in ['', '#bench', '#review']:
        p3.goto(PAGE + v); p3.wait_for_timeout(40)
        w = p3.evaluate('[document.documentElement.scrollWidth, document.documentElement.clientWidth]')
        if w[0] > w[1]: over.append((v, w))
    check('no horizontal scroll at 390px', not over, over)
    p3.goto(PAGE + '#d=tr3'); p3.wait_for_timeout(40); p3.screenshot(path='/home/claude/build/opslab/phone-line.png', full_page=True)
    pg.set_viewport_size({'width': 1150, 'height': 950})
    pg.goto(PAGE + '#d=cv1'); pg.wait_for_timeout(40); pg.evaluate(ANSWER, ['wrong'])
    pg.screenshot(path='/home/claude/build/opslab/desk-score.png', full_page=True)
    pg.goto(PAGE); pg.wait_for_timeout(40); pg.screenshot(path='/home/claude/build/opslab/desk-home.png')
    pg.goto(PAGE + '#bench'); pg.wait_for_timeout(40); pg.screenshot(path='/home/claude/build/opslab/desk-bench.png')
    b.close()
print('page errors:', errs or 'none')
print('RESULT:', 'ALL PASS' if not fails and not errs else f'FAILURES {fails}')
