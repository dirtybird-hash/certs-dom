"""Generate the CySA+ Performance Tasks page from pbq_data.py.

Storage: cysa:pbq:v1
    {best:{<pbq id>:{order:n, match:n, total:n}}, objStats:{"3.1":{c,t}, ...}}

objStats follows the same schema as the Drill, so per-objective accuracy from
hands-on work and from question work land in comparable form.

Ordering is done with Up/Down buttons rather than HTML5 drag-and-drop: drag is
unusable with a keyboard, awkward on a phone, and cannot be driven in a
headless test. Buttons are all three.

Usage:  python3 pbq_page.py
"""
import json, html, pathlib, importlib.util

HERE = pathlib.Path(__file__).parent
spec = importlib.util.spec_from_file_location('pbq_data', HERE / 'pbq_data.py')
D = importlib.util.module_from_spec(spec)
spec.loader.exec_module(D)


def esc(s):
    return html.escape(s, quote=False).replace('"', '&quot;')


DATA = []
for p in D.PBQS:
    stages = list(p['order'])
    ev = p['evidence']
    assert sorted(e['stage'] for e in ev) == sorted(stages), \
        f"{p['id']}: evidence stages do not match the order list"
    DATA.append({
        'id': p['id'], 'obj': p['obj'], 'title': esc(p['title']),
        'scenario': esc(p['scenario']), 'task': esc(p['task']),
        'order': [esc(s) for s in stages],
        'ev': [{'t': esc(e['text']), 's': esc(e['stage']), 'w': esc(e['why'])} for e in ev],
    })

CSS = """
:root{
  --bg:#f6f5f2; --surface:#ffffff; --surface-2:#eef1f2; --border:#dbe0e3;
  --text:#171b1f; --text-muted:#5a6570;
  --accent:#1f6f8b; --accent-ink:#ffffff;
  --ok:#1f8a5c; --ok-bg:#e7f4ee; --bad:#b3433a; --bad-bg:#fbeae8;
  --shadow:0 1px 2px rgba(20,24,28,.06),0 4px 14px rgba(20,24,28,.06);
  --radius:16px;
  --font-display:'IBM Plex Mono',ui-monospace,SFMono-Regular,Menlo,monospace;
  --font-body:'IBM Plex Sans',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --bg:#0d1216; --surface:#151c22; --surface-2:#1b242b; --border:#2b363e;
  --text:#e7edf1; --text-muted:#93a2ac; --accent:#5ab6d4; --accent-ink:#06262a;
  --ok:#55d69a; --ok-bg:#12291f; --bad:#f0948b; --bad-bg:#331a18;
  --shadow:0 1px 2px rgba(0,0,0,.4),0 10px 26px rgba(0,0,0,.35); color-scheme:dark;}}
:root[data-theme="dark"]{
  --bg:#0d1216; --surface:#151c22; --surface-2:#1b242b; --border:#2b363e;
  --text:#e7edf1; --text-muted:#93a2ac; --accent:#5ab6d4; --accent-ink:#06262a;
  --ok:#55d69a; --ok-bg:#12291f; --bad:#f0948b; --bad-bg:#331a18;
  --shadow:0 1px 2px rgba(0,0,0,.4),0 10px 26px rgba(0,0,0,.35); color-scheme:dark;}

*{box-sizing:border-box;}
body{background:var(--bg);color:var(--text);font-family:var(--font-body);margin:0;
  font-size:16px;line-height:1.55;}
.wrap{max-width:780px;margin:0 auto;padding-inline:16px;padding-block:22px 60px;}
h1,h2{font-family:var(--font-display);font-weight:600;letter-spacing:-.01em;margin:0;text-wrap:balance;}
h1{font-size:clamp(25px,5.4vw,32px);line-height:1.14;margin-bottom:8px;}
h2{font-size:17px;margin:0 0 10px;}
p{margin:0 0 12px;}
a{color:var(--accent);}
.backlink{font-family:var(--font-display);font-size:11.5px;color:var(--text-muted);
  text-decoration:none;display:inline-block;margin-bottom:12px;padding:3px 9px;
  border:1px solid var(--border);border-radius:999px;background:var(--surface);}
.backlink:hover{color:var(--accent);border-color:var(--accent);}
.eyebrow{font-family:var(--font-display);font-size:11.5px;letter-spacing:.07em;
  text-transform:uppercase;color:var(--accent);margin:0 0 7px;}
.lede{color:var(--text-muted);font-size:15px;max-width:62ch;}

.card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);
  padding:20px 22px;box-shadow:var(--shadow);margin-top:18px;}
.tag{font-family:var(--font-display);font-size:10.5px;letter-spacing:.05em;text-transform:uppercase;
  background:var(--surface-2);color:var(--text-muted);border-radius:999px;padding:2px 9px;}
.scenario{background:var(--surface-2);border-left:3px solid var(--accent);
  border-radius:0 10px 10px 0;padding:13px 15px;margin:0 0 14px;font-size:15px;}
.task{font-size:14.5px;color:var(--text-muted);margin-bottom:4px;}
.steplabel{font-family:var(--font-display);font-size:11.5px;letter-spacing:.06em;
  text-transform:uppercase;color:var(--text-muted);margin:22px 0 8px;}

ol.stages{list-style:none;counter-reset:s;margin:0;padding:0;}
ol.stages li{counter-increment:s;display:flex;align-items:center;gap:10px;
  border:1px solid var(--border);border-radius:10px;background:var(--bg);
  padding:8px 10px;margin-bottom:6px;}
ol.stages li::before{content:counter(s);font-family:var(--font-display);font-size:12px;
  color:var(--text-muted);width:18px;flex:0 0 18px;text-align:right;}
.sname{flex:1;min-width:0;font-size:15px;}
.move{font-family:var(--font-display);font-size:12px;line-height:1;padding:5px 8px;
  border:1px solid var(--border);border-radius:8px;background:var(--surface);
  color:var(--text-muted);cursor:pointer;}
.move:hover:not(:disabled){border-color:var(--accent);color:var(--accent);}
.move:disabled{opacity:.35;cursor:default;}
li.right{background:var(--ok-bg);border-color:var(--ok);}
li.wrong{background:var(--bad-bg);border-color:var(--bad);}

.ev{border:1px solid var(--border);border-radius:12px;padding:12px 14px;margin-bottom:10px;
  background:var(--bg);}
.ev p{margin:0 0 9px;font-size:15px;}
.ev select{font-family:var(--font-body);font-size:14px;padding:7px 10px;width:100%;
  border:1px solid var(--border);border-radius:10px;background:var(--surface);color:var(--text);}
.ev.right{background:var(--ok-bg);border-color:var(--ok);}
.ev.wrong{background:var(--bad-bg);border-color:var(--bad);}
.why{font-size:14px;line-height:1.55;margin-top:9px;padding-top:9px;
  border-top:1px solid var(--border);color:var(--text);}
.why b{font-family:var(--font-display);font-size:11px;letter-spacing:.05em;
  text-transform:uppercase;color:var(--text-muted);display:block;margin-bottom:3px;}

.btnrow{display:flex;gap:8px;flex-wrap:wrap;margin-top:18px;}
.btn{font-family:var(--font-display);font-size:12.5px;padding:9px 15px;border-radius:10px;
  cursor:pointer;border:1px solid var(--border);background:var(--surface);color:var(--text);}
.btn:hover{border-color:var(--accent);color:var(--accent);}
.btn.primary{background:var(--accent);color:var(--accent-ink);border-color:var(--accent);}
.btn:focus-visible,.move:focus-visible,select:focus-visible{outline:2px solid var(--accent);outline-offset:2px;}
.score{font-family:var(--font-display);font-size:13px;margin-top:14px;padding:11px 13px;
  border-radius:12px;background:var(--surface-2);color:var(--text);}
.note{border-left:3px solid var(--border);background:var(--surface-2);border-radius:0 10px 10px 0;
  padding:12px 14px;font-size:13.5px;color:var(--text-muted);line-height:1.55;margin-top:22px;}
.foot{margin-top:22px;padding-top:14px;border-top:1px solid var(--border);
  font-size:12px;color:var(--text-muted);}
"""

JS = r"""
var KEY = "cysa:pbq:v1";
var st = {best:{}, objStats:{}};
try{ var raw = localStorage.getItem(KEY); if(raw) st = JSON.parse(raw) || st; }catch(e){}
if(!st.best) st.best = {}; if(!st.objStats) st.objStats = {};
function save(){ try{ localStorage.setItem(KEY, JSON.stringify(st)); }catch(e){} }

function shuffle(a){ a=a.slice(); for(var i=a.length-1;i>0;i--){var j=Math.floor(Math.random()*(i+1));var t=a[i];a[i]=a[j];a[j]=t;} return a; }

PBQS.forEach(function(p){ render(p); });

function render(p){
  var host = document.getElementById('pbq-' + p.id);
  var order = shuffle(p.order);
  var ev = shuffle(p.ev);
  var checked = false;

  function draw(){
    var h = '<div class="scenario">' + p.scenario + '</div>'
          + '<p class="task">' + p.task + '</p>'
          + '<p class="steplabel">Step 1 &mdash; sequence the stages</p><ol class="stages" id="ol-'+p.id+'">';
    order.forEach(function(s, i){
      var cls = '';
      if(checked) cls = (s === p.order[i]) ? ' class="right"' : ' class="wrong"';
      h += '<li'+cls+'><span class="sname">'+s+'</span>'
         + '<button class="move" data-i="'+i+'" data-d="-1" aria-label="Move '+s+' up"'+(i===0?' disabled':'')+'>&uarr;</button>'
         + '<button class="move" data-i="'+i+'" data-d="1" aria-label="Move '+s+' down"'+(i===order.length-1?' disabled':'')+'>&darr;</button></li>';
    });
    h += '</ol><p class="steplabel">Step 2 &mdash; attribute each artefact</p>';
    ev.forEach(function(e, i){
      var picked = e.pick || '';
      var cls = '';
      if(checked) cls = (picked === e.s) ? ' right' : ' wrong';
      h += '<div class="ev'+cls+'"><p>'+e.t+'</p><select data-i="'+i+'"'+(checked?' disabled':'')+'>'
         + '<option value="">Select a stage&hellip;</option>';
      p.order.forEach(function(s){
        h += '<option value="'+s+'"'+(picked===s?' selected':'')+'>'+s+'</option>';
      });
      h += '</select>';
      if(checked) h += '<div class="why"><b>'+(picked===e.s?'Correct — '+e.s:'Answer: '+e.s)+'</b>'+e.w+'</div>';
      h += '</div>';
    });
    h += '<div class="btnrow">'
       + (checked ? '<button class="btn primary" id="again-'+p.id+'">Try again</button>'
                  : '<button class="btn primary" id="check-'+p.id+'">Check my answers</button>')
       + '</div><div class="score" id="score-'+p.id+'"></div>';
    host.innerHTML = h;

    Array.prototype.forEach.call(host.querySelectorAll('.move'), function(b){
      b.onclick = function(){
        if(checked) return;
        var i = +b.getAttribute('data-i'), d = +b.getAttribute('data-d'), j = i + d;
        if(j < 0 || j >= order.length) return;
        var t = order[i]; order[i] = order[j]; order[j] = t;
        draw();
      };
    });
    Array.prototype.forEach.call(host.querySelectorAll('select'), function(s){
      s.onchange = function(){ ev[+s.getAttribute('data-i')].pick = s.value; };
    });
    var c = document.getElementById('check-'+p.id);
    if(c) c.onclick = function(){ checked = true; score(); draw(); };
    var a = document.getElementById('again-'+p.id);
    if(a) a.onclick = function(){ checked=false; order=shuffle(p.order); ev=shuffle(p.ev);
                                  ev.forEach(function(x){ x.pick=''; }); draw(); };
    drawScore();
  }

  function score(){
    var o = 0; order.forEach(function(s,i){ if(s===p.order[i]) o++; });
    var m = 0; ev.forEach(function(e){ if(e.pick===e.s) m++; });
    var total = p.order.length + p.ev.length;
    var got = o + m;
    var b = st.best[p.id];
    if(!b || got > (b.order + b.match)) st.best[p.id] = {order:o, match:m, total:total};
    var os = st.objStats[p.obj] || {c:0, t:0};
    os.c += got; os.t += total; st.objStats[p.obj] = os;
    save();
    p._last = {o:o, m:m, total:total};
  }

  function drawScore(){
    var el = document.getElementById('score-'+p.id);
    if(!el) return;
    var b = st.best[p.id];
    var txt = '';
    if(p._last) txt += 'This attempt: ' + p._last.o + ' / ' + p.order.length + ' in order, '
                     + p._last.m + ' / ' + p.ev.length + ' attributed. ';
    txt += b ? 'Best: ' + (b.order + b.match) + ' / ' + b.total + '.'
             : 'Not attempted yet.';
    el.textContent = txt;
  }

  draw();
}
"""

body = ['<title>CySA+ Performance Tasks</title>',
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
        'family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap">',
        f'<style>{CSS}</style>', '',
        '<div class="wrap">',
        '  <a class="backlink" href="https://claude.ai/artifact/PrxFejEDNFYfNB7V7Ahjvq">&larr; CySA+ toolkit</a>',
        '  <p class="eyebrow">CompTIA CySA+ &middot; CS0-003</p>',
        '  <h1>Performance Tasks</h1>',
        '  <p class="lede">Hands-on exercises in the shape the exam uses &mdash; sequence it, '
        'attribute it, then read why. Scored per objective, like the Drill.</p>']
for p in DATA:
    body += [f'  <div class="card">',
             f'    <h2>{p["title"]} <span class="tag">Objective {p["obj"]}</span></h2>',
             f'    <div id="pbq-{p["id"]}"></div>',
             f'  </div>']
body += ['  <div class="note">Progress saves in this browser under <code>cysa:pbq:v1</code>, '
         'with per-objective accuracy recorded the same way the Drill records it.</div>',
         '  <div class="foot">Original study material written against CompTIA\'s published '
         'CS0-003 objectives. Not official CompTIA content, and not affiliated with, '
         'authorized by or endorsed by CompTIA.</div>',
         '</div>', '',
         '<script>',
         'var PBQS = ' + json.dumps(DATA, ensure_ascii=False, separators=(",", ": ")) + ';',
         JS, '</script>', '']

out = pathlib.Path('/home/claude/cysa-pbq.html')
out.write_text('\n'.join(body), encoding='utf-8')
print(f'written {out}  {len("\n".join(body))//1024} KB | {len(DATA)} task(s)')
for p in DATA:
    print(f'   {p["obj"]}  {p["title"]}  — {len(p["order"])} stages, {len(p["ev"])} artefacts')
