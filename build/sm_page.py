"""Build the CySA+ Study Map page (cysa-studymap.html) from sm_d1..sm_d4.

Every CS0-003 objective item, top-level and sub-bullet, gets a card:
What it is / What it does / Where it lives, plus an optional flow diagram
(where something sits in a pipeline) and an optional exam trap.

Design: "Study Map, Midnight" (chosen 11-05). Dark by default; the switch in
the top right toggles light and is remembered per browser (cysa:sm:theme).

Data shape, one per objective, in sm_dN.py:
    OBJ = {'2.1': {'title': 'objective text', 'items': [I(...), ...]}}
I(t, what, does, where='', full='', trap='', flow=None, kids=None)

Two side files, keyed by card id:
    sm_deck.py   DECK  = {id: html}   class deck checks, shown under the card
    sm_steps.py  STEPS = {id: [(html, jump_id or None), ...]}   one entry per flow box;
                 the boxes become buttons, the fill follows the click, and the entry opens below

Usage: python3 sm_page.py [out.html]
"""
import json, sys, pathlib, re, importlib

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
OUT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '/home/claude/cysa-studymap.html')
NB = 'https://claude.ai/artifact/2Zm7Tw7xCVcNJCC9bheaxv'
HUB = 'https://claude.ai/artifact/PrxFejEDNFYfNB7V7Ahjvq'
DRILL = {'1': 'https://claude.ai/artifact/KrYojQYtNqGKiiYQQ1iPXy', '2': 'https://claude.ai/artifact/Gud7EZdHrEfGnPxsyy29Fk',
         '3': 'https://claude.ai/artifact/R3jFowQmYqv5x3Kv2qYNoS', '4': 'https://claude.ai/artifact/HrmyyybMcjv3ut54g1ujfu'}
DOMAINS = {'1': 'Security Operations', '2': 'Vulnerability Management', '3': 'Incident Response', '4': 'Reporting and Communication'}

objs = {}
for d in '1234':
    try:
        m = importlib.import_module('sm_d' + d)
        objs.update(m.OBJ)
    except ModuleNotFoundError:
        pass
from sm_deck import DECK
from sm_steps import STEPS

def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', re.sub(r'<[^>]+>|&[a-z]+;', '', s.lower())).strip('-')[:48]

seen = set()
def norm(item, o, parent=''):
    sid = (o.replace('.', '') + '-' + slug((parent + '-' if parent else '') + item['t']))[:60]
    base, n = sid, 2
    while sid in seen:
        sid = base + '-' + str(n); n += 1
    seen.add(sid)
    for k in ('what', 'does'):
        assert item.get(k), (o, item['t'], 'missing ' + k)
    out = {'id': sid, 't': item['t']}
    for k in ('full', 'what', 'does', 'where', 'trap'):
        if item.get(k): out[k] = item[k]
    if sid in DECK: out['deck'] = DECK[sid]
    if item.get('flow'): out['flow'] = item['flow']
    if item.get('kids'): out['kids'] = [norm(k, o, item['t']) for k in item['kids']]
    return out

data, count = [], 0
for o in sorted(objs, key=lambda x: [int(p) for p in x.split('.')]):
    items = [norm(i, o) for i in objs[o]['items']]
    def c(L): return sum(1 + c(x.get('kids', [])) for x in L)
    count += c(items)
    data.append({'o': o, 'title': objs[o]['title'], 'items': items})

def every(L):
    for x in L:
        yield x
        yield from every(x.get('kids', []))
cards = {x['id']: x for o in data for x in every(o['items'])}
for k in DECK: assert k in cards, ('deck check for unknown card', k)
for k, v in STEPS.items():
    assert k in cards and cards[k].get('flow'), ('steps for a card with no flow', k)
    assert len(v) == len(cards[k]['flow']), ('step count does not match flow', k)
    for _, go in v: assert go is None or go in cards, ('jump to unknown card', k, go)
STEPS_JS = {k: [[t, go] if go else [t] for t, go in v] for k, v in STEPS.items()}

nb_topics = {}
for mod, names in (('nb_d1', ['D1']), ('nb_d2', ['D2']), ('nb_d34', ['D3', 'D4'])):
    m = importlib.import_module(mod)
    for n in names:
        for t in getattr(m, n):
            nb_topics.setdefault(t['o'], []).append([t['id'], re.sub(r'&[a-z]+;', "'", t['t'])])

PAGE = r'''<title>CySA+ Study Map</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Sora:wght@600;700;800&family=Source+Sans+3:wght@400;600;700&family=JetBrains+Mono:wght@500&display=swap">
<style>
/* Layout: Study Map, Midnight. Top bar (brand, search, theme switch at top right),
   domain chips, then objective rail + topic cards. Dark is the default look. */
:root{
  --bg:#0F1720; --surface:#17222D; --surface-2:#1C2935; --border:#2E4052; --text:#E8EEF3; --muted:#A9B7C4;
  --accent:#5B9DFF; --accent-ink:#0B1220; --link:#7FB2FF; --flowbox:#17222D;
  --trap-bg:#2B2414; --trap-bd:#F5B74A; --trap-tx:#F6E9CF; --trap-lb:#F5B74A;
  --f-head:'Sora','Segoe UI',system-ui,sans-serif; --f-body:'Source Sans 3','Segoe UI',system-ui,sans-serif;
  --f-mono:'JetBrains Mono',ui-monospace,Consolas,monospace;
  color-scheme:dark;
}
.app[data-mode="light"]{
  --bg:#F5F8FC; --surface:#FFFFFF; --surface-2:#EEF3F9; --border:#D3DCE6; --text:#13202D; --muted:#4A5866;
  --accent:#2F6FE0; --accent-ink:#FFFFFF; --link:#2459B8; --flowbox:#FFFFFF;
  --trap-bg:#FFF5E0; --trap-bd:#D99A1E; --trap-tx:#3A2C0B; --trap-lb:#8A5A00;
  color-scheme:light;
}
html,body{background:#0F1720}
body{margin:0}
.app{background:var(--bg);color:var(--text);font-family:var(--f-body);font-size:17px;line-height:1.55;min-height:100vh}
*{box-sizing:border-box}
a{color:var(--link)}
.wrap{max-width:1240px;margin:0 auto;padding-block:20px 72px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));display:flex;flex-direction:column;gap:22px}
.top{display:flex;flex-wrap:wrap;align-items:center;gap:12px 16px}
.brand{display:flex;flex-direction:column;gap:2px;margin-right:auto;min-width:0}
.brand a{font-family:var(--f-head);font-size:12px;color:var(--muted);text-decoration:none}
.brand h1{margin:0;font-family:var(--f-head);font-size:24px;font-weight:800;letter-spacing:-.01em}
.search{flex:1 1 280px;max-width:420px;position:relative}
.search input{width:100%;font:inherit;font-size:16px;padding:11px 14px;border-radius:12px;border:1.5px solid var(--border);background:var(--surface);color:var(--text)}
.search input:focus-visible{outline:2px solid var(--accent);outline-offset:1px}
.mode{display:flex;border:1.5px solid var(--border);border-radius:12px;overflow:hidden;background:var(--surface)}
.mode button{font:600 14px var(--f-head);padding:10px 14px;border:0;background:transparent;color:var(--muted);cursor:pointer;display:flex;gap:6px;align-items:center;min-height:44px}
.mode button[aria-pressed="true"]{background:var(--accent);color:var(--accent-ink)}
.mode button:focus-visible{outline:2px solid var(--accent);outline-offset:-2px}
.doms{display:flex;flex-wrap:wrap;gap:8px}
.doms button{font:700 14px var(--f-head);padding:9px 15px;border-radius:999px;border:1.5px solid var(--border);background:var(--surface);color:var(--text);cursor:pointer;min-height:42px}
.doms button[aria-pressed="true"]{background:var(--accent);border-color:var(--accent);color:var(--accent-ink)}
.body{display:flex;flex-wrap:wrap;gap:28px;align-items:flex-start}
.rail{flex:1 1 240px;max-width:300px;display:flex;flex-direction:column;gap:6px}
.rail button{text-align:left;font:inherit;font-size:15px;line-height:1.35;padding:10px 12px;border-radius:10px;border:1.5px solid transparent;background:transparent;color:var(--text);cursor:pointer;display:flex;gap:10px}
.rail button b{font-family:var(--f-mono);font-size:13px;color:var(--link);flex:0 0 auto;padding-top:2px}
.rail button[aria-current="true"]{background:var(--surface);border-color:var(--accent)}
.rail button:focus-visible{outline:2px solid var(--accent)}
.rail .n{margin-left:auto;font-family:var(--f-mono);font-size:12px;color:var(--muted);padding-top:2px}
.main{flex:999 1 600px;min-width:0;display:flex;flex-direction:column;gap:22px}
.ohead{display:flex;flex-direction:column;gap:8px;border-bottom:2px solid var(--border);padding-bottom:16px}
.ohead .k{font:700 13px var(--f-head);letter-spacing:.08em;color:var(--link)}
.ohead h2{margin:0;font-family:var(--f-head);font-size:28px;font-weight:800;letter-spacing:-.01em;text-wrap:balance}
.ohead .links{display:flex;flex-wrap:wrap;gap:8px;margin-top:4px}
.btn{display:inline-flex;align-items:center;gap:6px;font:700 14px var(--f-head);padding:10px 16px;border-radius:12px;text-decoration:none;min-height:42px}
.btn.pri{background:var(--accent);color:var(--accent-ink)}
.btn.sec{border:1.5px solid var(--border);color:var(--text);background:var(--surface)}
.group{display:flex;flex-direction:column;gap:14px}
.card{background:var(--surface);border:1.5px solid var(--border);border-radius:16px;padding:20px 22px;display:flex;flex-direction:column;gap:12px;scroll-margin-top:16px}
.card.lead{border-color:var(--accent)}
.card h3{margin:0;font-family:var(--f-head);font-size:21px;font-weight:700;line-height:1.25}
.card h3 .full{display:block;font-family:var(--f-body);font-weight:600;font-size:15px;color:var(--muted);margin-top:3px}
.rows{display:grid;grid-template-columns:132px minmax(0,1fr);gap:8px 16px}
.rows .lb{font:700 12px var(--f-head);letter-spacing:.07em;text-transform:uppercase;color:var(--link);padding-top:4px}
.rows p{margin:0}
.kids{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;align-items:start}
.kids .card{background:var(--surface-2);padding:16px 18px}
.kids .card h3{font-size:18px}
.kids .rows{grid-template-columns:1fr;gap:2px}
.kids .rows p{margin-bottom:8px}
.flow{display:flex;flex-wrap:wrap;align-items:center;gap:8px}
.flow .bx{flex:1 1 140px;background:var(--flowbox);border:1.5px solid var(--border);border-radius:12px;padding:10px 12px;font-size:15px;line-height:1.35}
.flow .bx.on{background:var(--accent);border-color:var(--accent);color:var(--accent-ink);font-weight:700}
button.bx{font:inherit;font-size:15px;line-height:1.35;text-align:left;color:var(--text);cursor:pointer;min-height:44px;position:relative;padding-right:26px}
button.bx::after{content:"+";position:absolute;right:9px;top:50%;transform:translateY(-50%);font:700 15px var(--f-head);color:var(--link)}
button.bx.on::after{color:var(--accent-ink)}
button.bx[aria-expanded="true"]::after{content:"\2212"}
button.bx:hover{border-color:var(--accent)}
button.bx:focus-visible{outline:2px solid var(--link);outline-offset:2px}
@media (prefers-reduced-motion:no-preference){button.bx{transition:background-color .2s,border-color .2s,color .2s}}
.flow .bx.on{color:var(--accent-ink)}
.fhint{margin:-4px 0 0;font-size:13px;color:var(--muted)}
.fpanel{background:var(--surface-2);border:1.5px solid var(--border);border-left:4px solid var(--link);border-radius:12px;padding:12px 14px}
.fpanel b{display:block;font:700 12px var(--f-head);letter-spacing:.08em;color:var(--link);margin-bottom:4px}
.fpanel p{margin:0}
.fpanel p b{display:inline;font:inherit;font-weight:700;letter-spacing:0;color:var(--text);margin:0}
.fgo{margin-top:10px;font:700 14px var(--f-head);color:var(--link);background:transparent;border:1.5px solid var(--border);border-radius:10px;padding:8px 12px;min-height:40px;cursor:pointer}
.fgo:hover{border-color:var(--accent)}
.card.hl{border-color:var(--accent);box-shadow:0 0 0 3px var(--accent)}
.flow .ar{color:var(--link);font:700 20px var(--f-head)}
.trap{background:var(--trap-bg);border:1.5px solid var(--trap-bd);border-radius:12px;padding:12px 14px;color:var(--trap-tx)}
.trap b{display:block;font:700 12px var(--f-head);letter-spacing:.08em;color:var(--trap-lb);margin-bottom:2px}
.deck{margin-top:10px;background:var(--surface-2);border:1.5px solid var(--border);border-left:4px solid var(--accent);border-radius:12px;padding:12px 14px}
.deck b{display:block;font:700 12px var(--f-head);letter-spacing:.08em;color:var(--accent);margin-bottom:2px}
code{font-family:var(--f-mono);font-size:.86em;background:var(--surface-2);border:1px solid var(--border);border-radius:5px;padding:1px 5px;overflow-wrap:anywhere}
.deep{display:flex;flex-wrap:wrap;gap:6px 10px;font-size:15px;color:var(--muted)}
.deep a{font-weight:600}
.hits{font:600 14px var(--f-head);color:var(--muted)}
.empty{border:1.5px dashed var(--border);border-radius:16px;padding:22px;color:var(--muted)}
.foot{font-size:13px;color:var(--muted);border-top:1px solid var(--border);padding-top:14px}
@media (max-width:760px){.kids{grid-template-columns:1fr}.rows{grid-template-columns:1fr;gap:2px}.rows .lb{padding-top:6px}.rail{max-width:none}}
@media (prefers-reduced-motion:no-preference){.card{transition:border-color .15s}}
</style>
<div class="app" id="app">
<div class="wrap">
  <div class="top">
    <div class="brand"><a href="__HUB__">&larr; CySA+ Toolkit</a><h1>CySA+ Study Map</h1></div>
    <div class="search"><label for="q" style="position:absolute;left:-9999px">Search every topic</label><input id="q" type="search" placeholder="Search every topic, e.g. SIEM, beaconing, CVSS" autocomplete="off"></div>
    <div class="mode" role="group" aria-label="Color mode">
      <button type="button" id="m-dark" aria-pressed="true"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M21 13A9 9 0 1 1 11 3a7 7 0 0 0 10 10z"/></svg>Dark</button>
      <button type="button" id="m-light" aria-pressed="false"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>Light</button>
    </div>
  </div>
  <div class="doms" id="doms" role="group" aria-label="Domains"></div>
  <div class="body">
    <nav class="rail" id="rail" aria-label="Objectives"></nav>
    <main class="main" id="main"></main>
  </div>
  <div class="foot">Original study notes written against CompTIA&rsquo;s published CS0-003 objectives: every objective item has a card. Not official CompTIA content. CompTIA, CySA+ and CS0-003 are trademarks of CompTIA, Inc.</div>
</div>
</div>
<script>
var DATA = __DATA__;
var NBT = __NBT__;
var NB = '__NB__', DRILL = __DRILL__, DOMS = __DOMS__;
var STEPS = __STEPS__;
var st = {d: '2', o: null, q: ''};
function $(id){ return document.getElementById(id); }
function esc(s){ return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;'); }
function byO(o){ return DATA.filter(function(x){ return x.o === o; })[0]; }
function cnt(L){ return L.reduce(function(n, x){ return n + 1 + cnt(x.kids || []); }, 0); }
function setMode(m){
  $('app').setAttribute('data-mode', m);
  document.documentElement.style.background = m === 'light' ? '#F5F8FC' : '#0F1720';
  document.body.style.background = document.documentElement.style.background;
  $('m-dark').setAttribute('aria-pressed', String(m === 'dark'));
  $('m-light').setAttribute('aria-pressed', String(m === 'light'));
  try{ localStorage.setItem('cysa:sm:theme', m); }catch(e){}
}
function flow(f, id){
  var S = STEPS[id] || [];
  return '<div class="flow" role="group" aria-label="Steps">' + f.map(function(b, i){
    var on = b.charAt(0) === '*', t = on ? b.slice(1) : b;
    var cls = 'bx' + (on ? ' on' : '');
    return (i ? '<span class="ar" aria-hidden="true">&rarr;</span>' : '') + (S[i]
      ? '<button type="button" class="' + cls + '"' + (on ? ' data-key="1"' : '') + ' data-fid="' + id + '" data-i="' + i + '" aria-expanded="false" aria-controls="fp-' + id + '">' + t + '</button>'
      : '<div class="' + cls + '">' + t + '</div>');
  }).join('') + '</div>' + (S.length ? '<p class="fhint">Select a step to expand it.' + (f.some(function(b){ return b.charAt(0) === '*'; }) ? ' The fill starts on the one to remember and follows your click.' : '') + '</p><div class="fpanel" id="fp-' + id + '" role="region" aria-live="polite" hidden></div>' : '');
}
function stepPanel(id, i, label){
  var s = STEPS[id][i], n = STEPS[id].length;
  return '<b>STEP ' + (i + 1) + ' OF ' + n + ' &middot; ' + label + '</b><p>' + s[0] + '</p>'
    + (s[1] ? '<button type="button" class="fgo" data-go="' + s[1] + '">' + (s[1] === id ? 'Back to the top of this card' : 'Open the full card') + ' &rarr;</button>' : '');
}
function goTo(id){
  var hit = flat().filter(function(p){ return p[1].id === id; })[0];
  if (!hit) return;
  st.d = hit[0].charAt(0); st.o = hit[0]; st.q = ''; $('q').value = ''; draw();
  var el = document.getElementById(id);
  if (!el) return;
  el.scrollIntoView({block: 'start'});
  el.classList.add('hl'); setTimeout(function(){ el.classList.remove('hl'); }, 1800);
}
function card(x, top){
  var h = '<article class="card' + (top ? ' lead' : '') + '" id="' + x.id + '"><h3>' + x.t + (x.full ? '<span class="full">' + x.full + '</span>' : '') + '</h3>';
  h += '<div class="rows"><span class="lb">What it is</span><p>' + x.what + '</p><span class="lb">What it does</span><p>' + x.does + '</p>';
  if (x.where) h += '<span class="lb">Where it lives</span><p>' + x.where + '</p>';
  h += '</div>';
  if (x.flow) h += flow(x.flow, x.id);
  if (x.trap) h += '<div class="trap"><b>EXAM TRAP</b>' + x.trap + '</div>';
  if (x.deck) h += '<div class="deck"><b>CLASS DECK CHECK</b>' + x.deck + '</div>';
  h += '</article>';
  return h;
}
function group(x){
  var h = '<section class="group">' + card(x, true);
  if (x.kids && x.kids.length) h += '<div class="kids">' + x.kids.map(function(k){ return card(k) + (k.kids ? k.kids.map(function(g){ return card(g); }).join('') : ''); }).join('') + '</div>';
  return h + '</section>';
}
function drawDoms(){
  var h = '';
  for (var d in DOMS){
    var has = DATA.some(function(x){ return x.o.charAt(0) === d; });
    h += '<button type="button" data-d="' + d + '" aria-pressed="' + (d === st.d) + '"' + (has ? '' : ' disabled title="Coming next"') + '>' + d + ' &middot; ' + DOMS[d] + (has ? '' : ' (soon)') + '</button>';
  }
  $('doms').innerHTML = h;
  [].forEach.call($('doms').querySelectorAll('button'), function(b){ b.onclick = function(){ st.d = b.getAttribute('data-d'); st.o = null; st.q = ''; $('q').value = ''; draw(); }; });
}
function drawRail(){
  var list = DATA.filter(function(x){ return x.o.charAt(0) === st.d; });
  if (!st.o || st.o.charAt(0) !== st.d) st.o = list.length ? list[0].o : null;
  $('rail').innerHTML = list.map(function(x){
    return '<button type="button" data-o="' + x.o + '" aria-current="' + (x.o === st.o && !st.q) + '"><b>' + x.o + '</b><span>' + x.title.replace(/^(Given a scenario, |Explain |Compare and contrast )/, '').replace(/\.$/, '') + '</span><span class="n">' + cnt(x.items) + '</span></button>';
  }).join('');
  [].forEach.call($('rail').querySelectorAll('button'), function(b){ b.onclick = function(){ st.o = b.getAttribute('data-o'); st.q = ''; $('q').value = ''; draw(); window.scrollTo(0, 0); }; });
}
function drawObj(){
  var x = byO(st.o);
  if (!x){ $('main').innerHTML = '<div class="empty">This domain is being written now.</div>'; return; }
  var deep = (NBT[x.o] || []).map(function(t){ return '<a href="' + NB + '#t=' + t[0] + '">' + t[1] + '</a>'; }).join('');
  var h = '<header class="ohead"><span class="k">OBJECTIVE ' + x.o + ' &middot; ' + cnt(x.items) + ' TOPICS</span><h2>' + x.title + '</h2>'
        + '<div class="links"><a class="btn pri" href="' + DRILL[x.o.charAt(0)] + '">Drill ' + x.o + ' &rarr;</a></div>'
        + (deep ? '<div class="deep"><span>Deep notes:</span>' + deep + '</div>' : '') + '</header>';
  h += x.items.map(group).join('');
  $('main').innerHTML = h;
}
function flat(){ var out = []; DATA.forEach(function(o){ (function w(L){ L.forEach(function(x){ out.push([o.o, x]); w(x.kids || []); }); })(o.items); }); return out; }
var FLAT = null;
function drawSearch(){
  FLAT = FLAT || flat().map(function(p){ return [p[0], p[1], (p[1].t + ' ' + (p[1].full||'') + ' ' + p[1].what + ' ' + p[1].does + ' ' + (p[1].where||'') + ' ' + (p[1].trap||'') + ' ' + (p[1].deck||'')).replace(/<[^>]+>/g, ' ').toLowerCase()]; });
  var words = st.q.toLowerCase().split(/\s+/).filter(Boolean);
  var hits = FLAT.filter(function(p){ return words.every(function(w){ return p[2].indexOf(w) >= 0; }); });
  hits.sort(function(a, b){ return (b[1].t.toLowerCase().indexOf(words[0]) === 0) - (a[1].t.toLowerCase().indexOf(words[0]) === 0); });
  $('main').innerHTML = '<p class="hits">' + hits.length + ' topic' + (hits.length === 1 ? '' : 's') + ' match &ldquo;' + esc(st.q) + '&rdquo;</p>'
    + (hits.length ? hits.slice(0, 60).map(function(p){ var c = JSON.parse(JSON.stringify(p[1])); delete c.kids; c.t = '<span style="font-family:var(--f-mono);font-size:13px;color:var(--link);margin-right:8px">' + p[0] + '</span>' + c.t; return card(c); }).join('') : '<div class="empty">No topic matches. Try fewer words.</div>');
}
function draw(){
  drawDoms(); drawRail();
  if (st.q) drawSearch(); else drawObj();
  try{ history.replaceState(null, '', '#' + (st.q ? 'q' : 'o' + st.o.replace('.', '-'))); }catch(e){}
}
$('main').addEventListener('click', function(e){
  var b = e.target.closest('button.bx[data-fid]');
  if (b){
    var id = b.getAttribute('data-fid'), i = +b.getAttribute('data-i'), p = document.getElementById('fp-' + id), open = b.getAttribute('aria-expanded') === 'true';
    [].forEach.call(b.parentNode.querySelectorAll('button.bx'), function(x){ x.setAttribute('aria-expanded', 'false'); x.classList.toggle('on', open ? x.hasAttribute('data-key') : x === b); });
    if (open){ p.hidden = true; p.innerHTML = ''; return; }
    b.setAttribute('aria-expanded', 'true'); p.innerHTML = stepPanel(id, i, b.textContent); p.hidden = false;
    return;
  }
  var g = e.target.closest('button[data-go]');
  if (g) goTo(g.getAttribute('data-go'));
});
$('m-dark').onclick = function(){ setMode('dark'); };
$('m-light').onclick = function(){ setMode('light'); };
var qt; $('q').oninput = function(){ clearTimeout(qt); var v = this.value; qt = setTimeout(function(){ st.q = v.trim(); draw(); }, 150); };
(function init(){
  var m = 'dark'; try{ m = localStorage.getItem('cysa:sm:theme') || 'dark'; }catch(e){}
  setMode(m === 'light' ? 'light' : 'dark');
  var h = location.hash.slice(1), mo = /^o(\d)-(\d)$/.exec(h);
  if (mo && byO(mo[1] + '.' + mo[2])){ st.d = mo[1]; st.o = mo[1] + '.' + mo[2]; }
  else if (!DATA.some(function(x){ return x.o.charAt(0) === st.d; }) && DATA.length) st.d = DATA[0].o.charAt(0);
  draw();
})();
</script>
'''

def js(x): return json.dumps(x, ensure_ascii=False).replace('</', '<\\/')
page = (PAGE.replace('__DATA__', js(data)).replace('__NBT__', js(nb_topics)).replace('__NB__', NB)
        .replace('__HUB__', HUB).replace('__DRILL__', js(DRILL)).replace('__DOMS__', js(DOMAINS)).replace('__STEPS__', js(STEPS_JS)))
OUT.write_text(page, encoding='utf-8')
print(f'study map: {len(data)} objectives, {count} topics, {len(page)//1024} KB -> {OUT}')
