"""Build the toolkit-wide search index for the CySA+ hub.

Loads every built CySA+ tool page in headless Chromium, reads its data straight
from the page (so the index always matches what was published), flattens it to
plain text and writes it into cysa-hub.html between the HUBIDX markers.

Run after rebuilding any drill, Simple Flash or Performance Tasks, before
publishing the hub:
    PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers python3 build/hub_search.py
"""
import json, re, pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path('/home/claude')
HUB = ROOT / 'cysa-hub.html'

PLAIN = r"""
window.__plain = function(s){
  if (s === undefined || s === null) return '';
  var d = document.createElement('div'); d.innerHTML = String(s);
  d.querySelectorAll('br,p,li,tr,div').forEach(function(n){ n.insertAdjacentText('beforebegin','\n'); });
  return d.textContent.replace(/[ \t]+/g,' ').replace(/\n\s*\n+/g,'\n').trim();
};
"""

DRILL = r"""
(src) => { const P = window.__plain, out = [];
  FLASH.forEach(c => out.push({s:src, k:'Flashcard', o:c.o, g:c.g?1:0, q:P(c.f), a:P(c.b), e:''}));
  QUIZ.forEach(q => out.push({s:src, k:'Quiz', o:q.o, g:q.g?1:0, q:P(q.q), a:P(q.c[q.a]), e:P(q.e)}));
  SCEN.forEach(q => out.push({s:src, k:'Scenario', o:q.o, g:q.g?1:0, q:P(q.s)+'\n'+P(q.q), a:P(q.c[q.a]), e:P(q.e)}));
  return out; }
"""

FLASHSF = r"""
() => { const P = window.__plain, out = [];
  DECKS.forEach(d => d.cards.forEach(c => out.push({s:'sf', k:d.deck, o:'', g:0, q:P(c.q), a:P(c.a), e:P(c.fix||c.note||'')})));
  return out; }
"""

PBQ = r"""
() => { const P = window.__plain, out = [];
  PBQS.forEach(p => {
    out.push({s:'pbq', k:'Task', o:p.obj, g:0, id:p.id, q:P(p.title), a:P(p.sc), e:P(p.task)});
    p.q.forEach(q => {
      const base = {s:'pbq', k:p.title, o:q.o, g:0, id:p.id};
      if (q.k === 'select') out.push(Object.assign({}, base, {q:P(q.p), a:P(q.opt[q.a]), e:P(q.w)}));
      else if (q.k === 'text') out.push(Object.assign({}, base, {q:P(q.p), a:P(q.show), e:P(q.w)}));
      else if (q.k === 'multi') out.push(Object.assign({}, base, {q:P(q.p), a:q.a.map(i => P(q.opt[i])).join('; '), e:P(q.w)}));
      else if (q.k === 'order') out.push(Object.assign({}, base, {q:P(q.p), a:q.it.map(P).join(' → '), e:P(q.w)}));
      else if (q.k === 'match') q.it.forEach(it => out.push(Object.assign({}, base, {q:P(q.p)+'\n'+P(it.t), a:P(q.ch[it.a]), e:P(it.w)})));
      else if (q.k === 'grid') q.rows.forEach((r, ri) => out.push(Object.assign({}, base, {
          q:P(q.p)+'\n'+P(r),
          a:q.cols.map((c, ci) => (q.a[ri][ci] ? '✓ ' : '✗ ') + P(c)).join('; '),
          e:P((q.rw||[])[ri]||q.w)})));
    });
  });
  return out; }
"""

NOTEBOOK = r"""
() => { const P = window.__plain, out = [];
  ACR.forEach(a => out.push({s:'nb', k:'Acronym', o:a.o, g:0, id:'a=' + encodeURIComponent(a.a),
      q:a.a, a:P(a.x), e:P(a.n) + (a.f ? ' (' + P(a.f) + ')' : '')}));
  TOPICS.forEach(t => {
    const body = P(t.h);
    out.push({s:'nb', k:'Note', o:t.o, g:0, id:'t=' + t.id, q:P(t.t), a:'', e:body});
  });
  return out; }
"""

def main():
    items = []
    with sync_playwright() as pw:
        b = pw.chromium.launch(); pg = b.new_page()
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        def load(name):
            pg.goto((ROOT / name).resolve().as_uri()); pg.add_script_tag(content=PLAIN)
        for n in range(1, 5):
            load(f'cysa-domain{n}-drill.html'); items += pg.evaluate(DRILL, f'd{n}')
        load('cysa-school-flashcards.html'); items += pg.evaluate(FLASHSF)
        load('cysa-pbq.html'); items += pg.evaluate(PBQ)
        load('cysa-notebook.html'); items += pg.evaluate(NOTEBOOK)
        b.close()
    assert not errs, errs
    for it in items:                     # drop empty keys to keep the index small
        for k in [k for k, v in it.items() if v in ('', 0) and k not in ('q',)]: del it[k]
    data = json.dumps(items, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    s = HUB.read_text(encoding='utf-8')
    new, n = re.subn(r'/\*HUBIDX-START\*/.*?/\*HUBIDX-END\*/',
                     lambda m: '/*HUBIDX-START*/var HUBIDX = ' + data + ';/*HUBIDX-END*/', s, flags=re.S)
    assert n == 1, 'HUBIDX markers not found exactly once'
    HUB.write_text(new, encoding='utf-8')
    by = {}
    for it in items: by[it['s']] = by.get(it['s'], 0) + 1
    print(f'hub index: {len(items)} entries, {len(data)//1024} KB', by)

main()
