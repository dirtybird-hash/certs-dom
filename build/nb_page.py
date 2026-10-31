"""Build the CySA+ Notebook page (cysa-notebook.html) from nb_d1, nb_d2, nb_d34, nb_acr.
Run: python3 build/nb_page.py
"""
import json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from nb_d1 import D1
from nb_d2 import D2
from nb_d34 import D3, D4
from nb_acr import ACR

ROOT = pathlib.Path('/home/claude')
SPINE = json.load(open(ROOT / 'build/cysa-spine.json'))
DRILLS = {'1': 'https://claude.ai/artifact/KrYojQYtNqGKiiYQQ1iPXy', '2': 'https://claude.ai/artifact/Gud7EZdHrEfGnPxsyy29Fk',
          '3': 'https://claude.ai/artifact/R3jFowQmYqv5x3Kv2qYNoS', '4': 'https://claude.ai/artifact/HrmyyybMcjv3ut54g1ujfu'}
HUB = 'https://claude.ai/artifact/PrxFejEDNFYfNB7V7Ahjvq'
DNAME = {'1': 'Security Operations', '2': 'Vulnerability Management', '3': 'Incident Response &amp; Management', '4': 'Reporting &amp; Communication'}
DWT = {'1': '33%', '2': '30%', '3': '20%', '4': '17%'}

topics = []
for d, lst in (('1', D1), ('2', D2), ('3', D3), ('4', D4)):
    for t in lst:
        assert t['o'].startswith(d + '.'), t['id']
        topics.append({'id': t['id'], 'd': d, 'o': t['o'], 't': t['t'], 'q': t['q'], 'h': t['h'].strip()})
ids = [t['id'] for t in topics]
assert len(ids) == len(set(ids)), 'duplicate topic id'
for o in SPINE:                                  # every objective has at least one topic
    assert any(t['o'] == o for t in topics), 'no topic for ' + o
acr = [{'a': a[0], 'x': a[1], 'n': a[2], 'o': a[3], **({'f': a[4]} if len(a) > 4 else {})} for a in ACR]
objt = {o: v['title'] for o, v in SPINE.items()}

def js(v): return json.dumps(v, ensure_ascii=False).replace('</', '<\\/')

page = r"""<title>CySA+ Notebook</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap">
<style>
:root{
  --bg:#f6f5f2; --surface:#ffffff; --surface-2:#eef1f2; --border:#dbe0e3;
  --text:#171b1f; --text-muted:#5a6570; --accent:#6d4bc4;
  --d1:#6d4bc4; --d2:#1f8a5c; --d3:#a14b7a; --d4:#a9791c; --acr:#1f6f8b;
  --trap:#b3437c; --trap-bg:#fbeaf2; --hl:#fbf1d9; --th:#e7f4ee; --th-ink:#1f6b4a;
  --shadow:0 1px 2px rgba(20,24,28,.06),0 4px 14px rgba(20,24,28,.06);
  --font-display:'IBM Plex Mono',ui-monospace,SFMono-Regular,Menlo,monospace;
  --font-body:'IBM Plex Sans',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --bg:#0d1216; --surface:#151c22; --surface-2:#1b242b; --border:#2b363e; --text:#e7edf1; --text-muted:#93a2ac;
  --accent:#a98cf0; --d1:#a98cf0; --d2:#55d69a; --d3:#e58fba; --d4:#e0b24d; --acr:#5ab6d4;
  --trap:#ea86b8; --trap-bg:#301b26; --hl:#4a3b12; --th:#12291f; --th-ink:#55d69a;
  --shadow:0 1px 2px rgba(0,0,0,.4),0 10px 26px rgba(0,0,0,.35); color-scheme:dark;}}
:root[data-theme="dark"]{
  --bg:#0d1216; --surface:#151c22; --surface-2:#1b242b; --border:#2b363e; --text:#e7edf1; --text-muted:#93a2ac;
  --accent:#a98cf0; --d1:#a98cf0; --d2:#55d69a; --d3:#e58fba; --d4:#e0b24d; --acr:#5ab6d4;
  --trap:#ea86b8; --trap-bg:#301b26; --hl:#4a3b12; --th:#12291f; --th-ink:#55d69a;
  --shadow:0 1px 2px rgba(0,0,0,.4),0 10px 26px rgba(0,0,0,.35); color-scheme:dark;}
*{box-sizing:border-box;}
body{background:var(--bg);color:var(--text);font-family:var(--font-body);margin:0;font-size:16px;line-height:1.55;}
.wrap{max-width:760px;margin:0 auto;padding-inline:16px;padding-block:22px 64px;}
h1,h2,h3{font-family:var(--font-display);font-weight:600;letter-spacing:-.01em;margin:0;text-wrap:balance;}
.backlink{font-family:var(--font-display);font-size:11.5px;color:var(--text-muted);text-decoration:none;display:inline-block;
  margin-bottom:12px;padding:3px 9px;border:1px solid var(--border);border-radius:999px;background:var(--surface);}
.backlink:hover{color:var(--accent);border-color:var(--accent);}
.eyebrow{font-family:var(--font-display);font-size:11.5px;letter-spacing:.07em;text-transform:uppercase;color:var(--accent);margin:0 0 7px;}
h1{font-size:clamp(25px,5.4vw,32px);line-height:1.14;margin-bottom:8px;}
.lede{color:var(--text-muted);font-size:15px;max-width:62ch;margin:0;}

.sbox{position:relative;margin:20px 0 14px;}
.sbox input{width:100%;font-family:var(--font-body);font-size:16px;padding:13px 70px 13px 40px;border-radius:12px;
  border:1px solid var(--border);background:var(--surface);color:var(--text);box-shadow:var(--shadow);-webkit-appearance:none;appearance:none;}
.sbox input::-webkit-search-cancel-button{display:none;}
.sbox input:focus{outline:2px solid var(--accent);outline-offset:1px;}
.sbox svg{position:absolute;left:14px;top:50%;transform:translateY(-50%);width:16px;height:16px;color:var(--text-muted);pointer-events:none;}
.sbox .clear{position:absolute;right:6px;top:50%;transform:translateY(-50%);background:none;border:none;font-family:var(--font-display);
  font-size:12px;color:var(--text-muted);cursor:pointer;padding:10px;}

.tabs{display:flex;gap:6px;overflow-x:auto;padding-bottom:2px;margin-bottom:16px;scrollbar-width:thin;}
.tab{flex:1 0 auto;min-width:92px;background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:9px 12px;
  cursor:pointer;text-align:left;color:var(--text);display:flex;flex-direction:column;gap:2px;font-family:var(--font-body);}
.tab .n{font-family:var(--font-display);font-size:13px;font-weight:600;color:var(--tc);}
.tab .s{font-family:var(--font-display);font-size:10.5px;color:var(--text-muted);}
.tab[aria-selected="true"]{border-color:var(--tc);box-shadow:var(--shadow);}
.tab:focus-visible{outline:2px solid var(--accent);outline-offset:2px;}

.dhead{display:flex;justify-content:space-between;align-items:baseline;gap:10px;flex-wrap:wrap;padding-bottom:10px;
  border-bottom:2px solid var(--tc);margin-bottom:14px;}
.dhead h2{font-size:17px;}
.dhead .w{font-family:var(--font-display);font-size:12px;color:var(--text-muted);}
.ochips{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 14px;}
.ochips button{font-family:var(--font-display);font-size:12px;border:1px solid var(--border);background:var(--surface);color:var(--text-muted);
  border-radius:999px;padding:5px 11px;cursor:pointer;}
.ochips button[aria-pressed="true"]{border-color:var(--tc);color:var(--tc);background:var(--surface-2);}
.otitle{font-size:13px;color:var(--text-muted);margin:16px 0 8px;line-height:1.45;}
.otitle b{font-family:var(--font-display);color:var(--tc);margin-right:6px;}

.topic{background:var(--surface);border:1px solid var(--border);border-left:4px solid var(--tc);border-radius:12px;margin-bottom:9px;box-shadow:var(--shadow);}
.topic>button{width:100%;background:none;border:none;text-align:left;padding:13px 15px;cursor:pointer;color:var(--text);
  display:flex;gap:10px;align-items:baseline;font-family:var(--font-body);}
.topic>button:focus-visible{outline:2px solid var(--accent);outline-offset:-2px;}
.topic .tt{font-family:var(--font-display);font-size:14.5px;font-weight:600;line-height:1.35;flex:1;}
.topic .to{font-family:var(--font-display);font-size:11px;color:var(--text-muted);}
.topic .ch{color:var(--text-muted);transition:transform .2s;font-size:12px;}
.topic.open .ch{transform:rotate(90deg);}
.body{display:none;padding:0 17px 16px;font-size:15px;}
.topic.open .body{display:block;}
.body p{margin:0 0 11px;}
.body ul,.body ol{margin:0 0 12px;padding-left:22px;}
.body li{margin-bottom:6px;}
.body strong{font-weight:600;}
.tblwrap{overflow-x:auto;margin:0 0 13px;-webkit-overflow-scrolling:touch;}
.body table{width:100%;border-collapse:collapse;font-size:13.5px;}
.body th{background:var(--th);color:var(--th-ink);text-align:left;padding:7px 9px;border:1px solid var(--border);font-family:var(--font-display);font-size:11.5px;}
.body td{padding:7px 9px;border:1px solid var(--border);vertical-align:top;}
.body pre{font-family:var(--font-display);font-size:12.5px;line-height:1.55;background:var(--surface-2);border:1px solid var(--border);border-radius:8px;padding:10px 12px;margin:0 0 13px;overflow-x:auto;white-space:pre;-webkit-overflow-scrolling:touch;}
.body pre.wrap{white-space:pre-wrap;overflow-wrap:anywhere;}
.body pre code{background:none;padding:0;font-size:inherit;overflow-wrap:normal;}
.body figure{margin:0 0 14px;}
.body figure svg{display:block;width:100%;max-width:460px;height:auto;margin:0 auto;}
.body figcaption{font-size:12.5px;color:var(--text-muted);text-align:center;margin-top:6px;}
.body code{font-family:var(--font-display);font-size:12.5px;background:var(--surface-2);padding:1px 5px;border-radius:4px;overflow-wrap:anywhere;}
.body blockquote{margin:0 0 12px;border-left:3px solid var(--trap);background:var(--trap-bg);border-radius:0 8px 8px 0;padding:10px 13px;font-size:14px;}
.body blockquote .tag{font-family:var(--font-display);color:var(--trap);font-size:11px;text-transform:uppercase;letter-spacing:.04em;display:block;margin-bottom:3px;}
.drillit{font-family:var(--font-display);font-size:12px;color:var(--tc);text-decoration:none;display:inline-block;padding:6px 0 0;}
.drillit:hover{text-decoration:underline;}
mark{background:var(--hl);color:inherit;border-radius:3px;padding:0 1px;}

.acrtools{display:flex;flex-wrap:wrap;gap:4px;margin:0 0 12px;}
.acrtools button{font-family:var(--font-display);font-size:11.5px;min-width:30px;border:1px solid var(--border);background:var(--surface);
  color:var(--text-muted);border-radius:7px;padding:5px 7px;cursor:pointer;}
.acrtools button[aria-pressed="true"]{border-color:var(--acr);color:var(--acr);}
.acrtools button:disabled{opacity:.35;cursor:default;}
.acrlist{display:flex;flex-direction:column;gap:1px;background:var(--border);border:1px solid var(--border);border-radius:12px;overflow:hidden;}
.acr{background:var(--surface);padding:10px 14px;display:grid;grid-template-columns:92px 1fr;gap:4px 12px;}
.acr .a{font-family:var(--font-display);font-weight:600;color:var(--acr);font-size:14px;overflow-wrap:anywhere;}
.acr .x{font-weight:600;font-size:14.5px;}
.acr .n{grid-column:2;font-size:13.5px;color:var(--text-muted);line-height:1.5;}
.acr .f{grid-column:2;font-size:12.5px;color:var(--trap);line-height:1.45;}
.acr .ob{font-family:var(--font-display);font-size:11px;color:var(--text-muted);margin-left:6px;}
@media (max-width:520px){.acr{grid-template-columns:1fr;}.acr .n,.acr .f{grid-column:1;}}

.sres h3{font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--text-muted);margin:14px 0 8px;font-weight:500;}
.scount{font-family:var(--font-display);font-size:12px;color:var(--text-muted);margin:0 0 8px;}
.none{background:var(--surface);border:1px dashed var(--border);border-radius:12px;padding:18px;text-align:center;font-size:14px;color:var(--text-muted);}
.foot{margin-top:30px;padding-top:14px;border-top:1px solid var(--border);font-size:12px;color:var(--text-muted);}
.t1{--tc:var(--d1);} .t2{--tc:var(--d2);} .t3{--tc:var(--d3);} .t4{--tc:var(--d4);} .tA{--tc:var(--acr);}
</style>

<div class="wrap">
  <a class="backlink" href="__HUB__">&larr; CySA+ Toolkit</a>
  <p class="eyebrow">CompTIA CySA+ &middot; CS0-003</p>
  <h1>CySA+ Notebook</h1>
  <p class="lede">Reference notes for every objective, plus all __NACR__ acronyms on CompTIA&rsquo;s list. Look a topic up, read it, then hit <b>Drill this</b> to answer questions on it.</p>

  <div class="sbox" role="search">
    <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="8.5" cy="8.5" r="6"/><path d="M13 13l5 5" stroke-linecap="round"/></svg>
    <input type="search" id="q" placeholder="Search notes and acronyms &mdash; e.g. DMARC, kill chain, 2.3" autocomplete="off" spellcheck="false" aria-label="Search the notebook">
    <button class="clear" id="qclear" type="button" hidden>Clear</button>
  </div>

  <div class="tabs" role="tablist" id="tabs"></div>
  <div id="view"></div>

  <div class="foot">Original notes written against CompTIA&rsquo;s published CS0-003 objectives. Not official CompTIA content.
  CompTIA, CySA+ and CS0-003 are trademarks of CompTIA, Inc. Acronym expansions are as CompTIA lists them; corrections are noted in pink.</div>
</div>

<script>
var TOPICS = __TOPICS__;
var ACR = __ACR__;
var OBJT = __OBJT__;
(function(){
"use strict";
var DRILL = __DRILLS__, DNAME = __DNAME__, DWT = __DWT__;
var TABS = ['1','2','3','4','A'];
var state = {tab:'1', obj:null, letter:null, open:{}};
var qEl = document.getElementById('q'), view = document.getElementById('view'), clr = document.getElementById('qclear');
TOPICS.forEach(function(t){ t.plain = (t.o+' '+t.t+' '+t.h.replace(/<[^>]+>/g,' ')).replace(/&[a-z]+;/g,' ').toLowerCase(); });
ACR.forEach(function(a){ a.plain = (a.a+' '+a.x+' '+a.n.replace(/<[^>]+>/g,' ')+' '+(a.f||'')).replace(/&[a-z]+;/g,' ').toLowerCase(); });
try { var saved = JSON.parse(localStorage.getItem('cysa:notebook:v1')||'{}'); if (saved.tab && TABS.indexOf(saved.tab)>=0) state.tab = saved.tab; } catch(e){}
function persist(){ try { localStorage.setItem('cysa:notebook:v1', JSON.stringify({tab:state.tab})); } catch(e){} }

function esc(s){ return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }
function hlHTML(html, terms){
  if (!terms.length) return html;
  return html.replace(/(<[^>]*>)|([^<]+)/g, function(m, tag, txt){
    if (tag) return tag;
    terms.forEach(function(t){
      var re = new RegExp('(' + esc(t).replace(/[.*+?^${}()|[\]\\]/g,'\\$&') + ')','gi');
      txt = txt.replace(/(&[a-z#0-9]+;)|([^&]+)/gi, function(mm, ent, s){ return ent ? ent : s.replace(re,'<mark>$1</mark>'); });
    });
    return txt;
  });
}
function drawTabs(){
  var h = '';
  TABS.forEach(function(k){
    var sel = !qEl.value.trim() && state.tab === k;
    var n = k === 'A' ? ACR.length : TOPICS.filter(function(t){return t.d===k;}).length;
    h += '<button class="tab t'+k+'" role="tab" aria-selected="'+sel+'" data-tab="'+k+'"><span class="n">'+(k==='A'?'Acronyms':'Domain '+k)+'</span><span class="s">'+
         (k==='A' ? n+' terms' : n+' topics &middot; '+DWT[k]) + '</span></button>';
  });
  document.getElementById('tabs').innerHTML = h;
}
function topicHTML(t, terms){
  var open = state.open[t.id] || terms.length > 0;
  return '<article class="topic t'+t.d+(open?' open':'')+'" id="t-'+t.id+'"><button type="button" aria-expanded="'+open+'" data-topic="'+t.id+'">'+
    '<span class="tt">'+hlHTML(t.t, terms)+'</span><span class="to">'+t.o+'</span><span class="ch">&#9656;</span></button>'+
    '<div class="body">'+hlHTML(t.h, terms)+'<a class="drillit" href="'+DRILL[t.d]+'#q='+encodeURIComponent(t.q)+'">Drill this in Domain '+t.d+' &rarr;</a></div></article>';
}
function acrHTML(a, terms){
  return '<div class="acr" id="a-'+esc(a.a.replace(/[^A-Za-z0-9]/g,''))+'"><span class="a">'+hlHTML(esc(a.a), terms)+'</span><span class="x">'+hlHTML(esc(a.x), terms)+
    '<span class="ob">'+a.o+'</span></span><span class="n">'+hlHTML(a.n, terms)+'</span>'+(a.f?'<span class="f">'+hlHTML(a.f, terms)+'</span>':'')+'</div>';
}
function drawDomain(d){
  var objs = Object.keys(OBJT).filter(function(o){ return o.charAt(0)===d; });
  var h = '<div class="t'+d+'"><div class="dhead"><h2>'+d+'.0 '+DNAME[d]+'</h2><span class="w">'+DWT[d]+' of the exam</span></div>';
  h += '<div class="ochips" role="group" aria-label="Filter by objective"><button type="button" data-obj="" aria-pressed="'+(!state.obj)+'">All</button>';
  objs.forEach(function(o){ h += '<button type="button" data-obj="'+o+'" aria-pressed="'+(state.obj===o)+'">'+o+'</button>'; });
  h += '</div>';
  objs.forEach(function(o){
    if (state.obj && state.obj !== o) return;
    h += '<p class="otitle"><b>'+o+'</b>'+esc(OBJT[o])+'</p>';
    TOPICS.filter(function(t){ return t.o===o; }).forEach(function(t){ h += topicHTML(t, []); });
  });
  return h + '</div>';
}
function drawAcr(){
  var letters = {}; ACR.forEach(function(a){ letters[a.a.charAt(0).toUpperCase()] = 1; });
  var h = '<div class="tA"><div class="dhead"><h2>CS0-003 acronyms</h2><span class="w">'+ACR.length+' on CompTIA&rsquo;s list</span></div>';
  h += '<div class="acrtools" role="group" aria-label="Jump to letter"><button type="button" data-letter="" aria-pressed="'+(!state.letter)+'">All</button>';
  'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('').forEach(function(L){
    h += '<button type="button" data-letter="'+L+'" aria-pressed="'+(state.letter===L)+'"'+(letters[L]?'':' disabled')+'>'+L+'</button>';
  });
  h += '</div><div class="acrlist">';
  ACR.filter(function(a){ return !state.letter || a.a.charAt(0).toUpperCase()===state.letter; })
     .sort(function(x,y){ return x.a.toLowerCase() < y.a.toLowerCase() ? -1 : 1; })
     .forEach(function(a){ h += acrHTML(a, []); });
  return h + '</div></div>';
}
function drawSearch(raw){
  var terms = raw.toLowerCase().split(/\s+/).filter(Boolean);
  var match = function(x){ return terms.every(function(t){ return x.plain.indexOf(t) >= 0; }); };
  // an exact acronym hit ranks first
  var A = ACR.filter(match).sort(function(x,y){ var q=raw.trim().toLowerCase(); return (y.a.toLowerCase()===q) - (x.a.toLowerCase()===q); });
  var T = TOPICS.filter(match);
  if (terms.length === 1 && /^\d\.\d$/.test(terms[0])) T = TOPICS.filter(function(t){ return t.o === terms[0]; });
  var h = '<div class="sres"><p class="scount">'+T.length+' topic'+(T.length===1?'':'s')+' &middot; '+A.length+' acronym'+(A.length===1?'':'s')+'</p>';
  if (!T.length && !A.length) h += '<div class="none">Nothing matches &ldquo;'+esc(raw)+'&rdquo;. Try one word or a shorter form.</div>';
  if (A.length){ h += '<h3>Acronyms</h3><div class="acrlist tA">'; A.slice(0,30).forEach(function(a){ h += acrHTML(a, terms); }); h += '</div>'; }
  if (T.length){ h += '<h3>Topics</h3>'; T.forEach(function(t){ h += topicHTML(t, terms); }); }
  return h + '</div>';
}
function draw(){
  var raw = qEl.value.trim();
  clr.hidden = !raw;
  drawTabs();
  view.innerHTML = raw ? drawSearch(raw) : (state.tab === 'A' ? drawAcr() : drawDomain(state.tab));
}
document.getElementById('tabs').addEventListener('click', function(e){
  var b = e.target.closest('[data-tab]'); if (!b) return;
  state.tab = b.getAttribute('data-tab'); state.obj = null; state.letter = null; qEl.value = ''; persist(); draw();
});
view.addEventListener('click', function(e){
  var b;
  if ((b = e.target.closest('[data-topic]'))){
    var art = b.parentNode, id = b.getAttribute('data-topic'), open = !art.classList.contains('open');
    art.classList.toggle('open', open); b.setAttribute('aria-expanded', open); state.open[id] = open; return;
  }
  if ((b = e.target.closest('[data-obj]'))){ state.obj = b.getAttribute('data-obj') || null; draw(); return; }
  if ((b = e.target.closest('[data-letter]')) && !b.disabled){ state.letter = b.getAttribute('data-letter') || null; draw(); }
});
var timer;
qEl.addEventListener('input', function(){ clearTimeout(timer); timer = setTimeout(draw, 90); });
qEl.addEventListener('keydown', function(e){ if (e.key === 'Escape'){ qEl.value=''; draw(); } });
clr.addEventListener('click', function(){ qEl.value=''; draw(); qEl.focus(); });
document.addEventListener('keydown', function(e){
  var t = (document.activeElement||{}).tagName || '';
  if (e.key === '/' && !/^(INPUT|TEXTAREA|SELECT)$/.test(t)){ e.preventDefault(); qEl.focus(); }
});
// Deep links from the hub: #t=<topic id>, #a=<acronym>, #q=<search>
function route(){
  var h = location.hash || '', m;
  if ((m = /^#t=(.+)$/.exec(h))){
    var t = TOPICS.filter(function(x){ return x.id === decodeURIComponent(m[1]); })[0];
    if (t){ qEl.value=''; state.tab = t.d; state.obj = null; state.open[t.id] = true; draw();
      var el = document.getElementById('t-'+t.id); if (el) el.scrollIntoView({block:'start'}); return true; }
  } else if ((m = /^#a=(.+)$/.exec(h))){
    var a = decodeURIComponent(m[1]); qEl.value = a; draw(); return true;
  } else if ((m = /^#q=(.+)$/.exec(h))){
    try { qEl.value = decodeURIComponent(m[1]); } catch(e){ qEl.value = m[1]; } draw(); return true;
  }
  return false;
}
if (!route()) draw();
window.addEventListener('hashchange', route);
})();
</script>
"""
out = (page.replace('__TOPICS__', js(topics)).replace('__ACR__', js(acr)).replace('__OBJT__', js(objt))
           .replace('__DRILLS__', js(DRILLS)).replace('__DNAME__', js(DNAME)).replace('__DWT__', js(DWT))
           .replace('__HUB__', HUB).replace('__NACR__', str(len(acr))))
(ROOT / 'cysa-notebook.html').write_text(out, encoding='utf-8')
per = {d: sum(1 for t in topics if t['d'] == d) for d in '1234'}
print(f'notebook: {len(topics)} topics {per}, {len(acr)} acronyms, {len(out)//1024} KB')
