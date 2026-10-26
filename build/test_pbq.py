"""Drive every Performance Task both directions in headless Chromium.

For each PBQ: answer everything correctly through the UI and expect full marks;
Try again; answer everything wrongly (or blank, confirming the blank warning) and
expect zero. Then check objStats totals equal 2 x scored fields per objective
with exactly half correct, check legacy v2 storage loads, and exercise the console.

Usage: PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers python3 test_pbq.py page.html
"""
import sys, json, pathlib
from playwright.sync_api import sync_playwright

PAGE = pathlib.Path(sys.argv[1]).resolve().as_uri()

FILL = r"""
([pid, mode]) => {
  const p = PBQS.find(x => x.id === pid);
  const fire = (el, ev) => el.dispatchEvent(new Event(ev, {bubbles:true}));
  const ent = s => { const t = document.createElement('textarea'); t.innerHTML = s; return t.value; };
  p.q.forEach((q, i) => {
    const id = s => 'q-' + pid + '-' + i + (s === undefined ? '' : '-' + s);
    if (q.k === 'select') {
      const el = document.getElementById(id());
      el.value = mode === 'right' ? String(q.a) : String((q.a + 1) % q.opt.length); fire(el, 'change');
    } else if (q.k === 'text') {
      const el = document.getElementById(id());
      el.value = mode === 'right' ? ent(q.show).toUpperCase() + ' ' : 'zzz'; fire(el, 'input');
    } else if (q.k === 'multi') {
      q.opt.forEach((_, oi) => { const el = document.getElementById(id(oi));
        const want = mode === 'right' ? q.a.includes(oi) : !q.a.includes(oi);
        if (el.checked !== want) el.click(); });
    } else if (q.k === 'grid') {
      q.rows.forEach((_, ri) => q.cols.forEach((_, ci) => { const el = document.getElementById(id(ri + '-' + ci));
        const want = mode === 'right' ? q.a[ri][ci] : !q.a[ri][ci];
        if (el.checked !== want) el.click(); }));
    } else if (q.k === 'match') {
      q.it.forEach((it, ii) => { const el = document.getElementById(id(ii));
        el.value = mode === 'right' ? String(it.a) : String((it.a + 1) % q.ch.length); fire(el, 'change'); });
    }
  });
  return true;
}
"""

ORDER = r"""
([pid, mode]) => {
  const p = PBQS.find(x => x.id === pid);
  const ent = s => { const t = document.createElement('textarea'); t.innerHTML = s; return t.value; };
  p.q.forEach((q, i) => {
    if (q.k !== 'order') return;
    const target = mode === 'right' ? q.it.map(ent) : q.it.map(ent).slice(1).concat([ent(q.it[0])]);
    for (let pos = 0; pos < target.length; pos++) {
      for (let guard = 0; guard < 20; guard++) {
        const names = [...document.querySelectorAll('#qpane ol.stages li .sname')].map(x => x.textContent);
        const cur = names.indexOf(target[pos]);
        if (cur === pos) break;
        document.getElementById('q-' + pid + '-' + i + '-u' + cur).click();
      }
    }
  });
  return [...document.querySelectorAll('#qpane ol.stages li .sname')].map(x => x.textContent);
}
"""

def main():
    fails = []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page()
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.on('console', lambda m: m.type == 'error' and errs.append(m.text))
        pg.goto(PAGE)
        data = pg.evaluate('PBQS.map(p => ({id:p.id, pts:p.pts}))')
        expect = {}
        for p in data:
            pid, pts = p['id'], p['pts']
            pg.evaluate(f'location.hash = "{pid}"'); pg.wait_for_timeout(60)
            assert pg.evaluate('CUR') == pid, pid
            pg.evaluate(FILL, [pid, 'right']); pg.evaluate(ORDER, [pid, 'right'])
            pg.click('#check')
            got = pg.evaluate('RUN[CUR].last')
            ok1 = got == {'got': pts, 'total': pts}
            # wrong pass
            pg.click('#again')
            pg.evaluate(FILL, [pid, 'wrong']); pg.evaluate(ORDER, [pid, 'wrong'])
            pg.click('#check')
            got2 = pg.evaluate('RUN[CUR].last')
            ok2 = got2 == {'got': 0, 'total': pts}
            best = pg.evaluate(f'JSON.parse(localStorage.getItem("cysa:pbq:v1")).best["{pid}"]')
            ok3 = best == {'got': pts, 'total': pts}
            n_right = pg.evaluate('document.querySelectorAll("#qpane .why").length')
            print(f'{"PASS" if ok1 and ok2 and ok3 else "FAIL"}  {pid:18} right {got}  wrong {got2}  best {best}  explanations shown {n_right}')
            if not (ok1 and ok2 and ok3): fails.append(pid)
            for q in pg.evaluate(f'PBQS.find(x=>x.id==="{pid}").q.map(q => ({{o:q.o, n: q.k==="grid"?q.rows.length: q.k==="order"?q.it.length: q.k==="match"?q.it.length:1}}))'):
                expect[q['o']] = expect.get(q['o'], 0) + q['n']
        # blank-answer guard
        pg.evaluate('location.hash = "after-hours"'); pg.wait_for_timeout(60); pg.click('#again')
        pg.click('#check')
        warn = pg.inner_text('#unans'); still = pg.evaluate('RUN[CUR].checked')
        print(('PASS' if warn and not still else 'FAIL') + f'  blank guard: "{warn}" checked={still}')
        if not warn or still: fails.append('blank-guard')
        pg.click('#check')   # confirm: scores as all wrong
        print('PASS' if pg.evaluate('RUN[CUR].last.got') == 0 else 'FAIL', ' blank confirm scores 0')
        # objStats
        stats = pg.evaluate('JSON.parse(localStorage.getItem("cysa:pbq:v1")).objStats')
        expect['1.2'] += 0
        ah = pg.evaluate('PBQS.find(x=>x.id==="after-hours").q.map(q=>q.o)')
        extra = {}
        for o in ah: extra[o] = extra.get(o, 0) + 1
        bad = []
        for o, n in expect.items():
            want_t = 2 * n + extra.get(o, 0)
            s = stats.get(o, {})
            if s.get('t') != want_t or s.get('c') != n: bad.append((o, s, n, want_t))
        print(('PASS' if not bad else 'FAIL') + '  objStats per objective', bad or {k: v for k, v in sorted(stats.items())})
        if bad: fails.append('objstats')
        # console
        pg.evaluate('location.hash = "port-recon"'); pg.wait_for_timeout(60)
        tin = '#tin-port-recon'
        for cmd in ['help', 'nmap -sV -sC srv3.hq.lab', 'nmap 10.40.8.47', 'nmap srv9.hq.lab', 'ls -la', 'NMAP -sV SRV5']:
            pg.fill(tin, cmd); pg.press(tin, 'Enter')
        txt = pg.inner_text('#tscroll')
        checks = {'help': 'usage: nmap' in txt, 'srv3': '10.40.8.2)' in txt and 'Device: switch' in txt,
                  'by ip': 'srv4.hq.lab (10.40.8.47)' in txt, 'unknown host': 'Failed to resolve' in txt,
                  'unknown cmd': 'ls: command not found' in txt, 'case-insensitive': 'srv5.hq.lab (10.40.8.50)' in txt}
        print(('PASS' if all(checks.values()) else 'FAIL') + '  console', checks)
        if not all(checks.values()): fails.append('console')
        pg.fill(tin, 'clear'); pg.press(tin, 'Enter')
        print('PASS' if pg.inner_text('#tscroll').strip() == '' else 'FAIL', ' console clear')
        # legacy v2 storage
        pg2 = b.new_page(); pg2.on('pageerror', lambda e: errs.append(str(e)))
        pg2.goto(PAGE)
        pg2.evaluate('localStorage.setItem("cysa:pbq:v1", JSON.stringify({best:{killchain:{order:5,match:6,total:14}}, objStats:{"3.1":{c:11,t:14}}}))')
        pg2.reload(); pg2.wait_for_timeout(100)
        chip = pg2.inner_text('#picker')
        acc = pg2.inner_text('#acc')
        okl = 'Best 11/14' in chip and '3.1' in acc and '79%' in acc
        print(('PASS' if okl else 'FAIL') + f'  legacy v2 storage -> "Best 11/14", acc "{acc}"')
        if not okl: fails.append('legacy')
        # phone width: no horizontal page scroll
        pg3 = b.new_page(viewport={'width': 390, 'height': 800})
        for pid in [p['id'] for p in data]:
            pg3.goto(PAGE + '#' + pid); pg3.wait_for_timeout(50)
            w = pg3.evaluate('[document.documentElement.scrollWidth, document.documentElement.clientWidth]')
            if w[0] > w[1]: fails.append('overflow-' + pid); print('FAIL  phone overflow', pid, w)
        print('PASS  phone width checked for all tasks' if not any(f.startswith('overflow') for f in fails) else '')
        b.close()
    print('page errors:', errs or 'none')
    print('RESULT:', 'ALL PASS' if not fails and not errs else f'FAILURES {fails}')

main()
