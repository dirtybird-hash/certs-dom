"""Generate the CySA+ Performance Tasks page from pbq_data.py.

v3: one engine for every PBQ layout. A PBQ is evidence tabs (logs, tables,
documents, a working console) beside a set of scored questions (select, text,
multi, grid, order, match). See pbq_data.py for the shapes.

Storage: cysa:pbq:v1  (unchanged key, so v2 progress carries over)
    {best:{<pbq id>:{got:n, total:n}}, objStats:{"3.1":{c,t}, ...}, open:<pbq id>}
    v2 best entries {order, match, total} are read as got = order + match.

Every scored field is one point and carries its own objective, so a PBQ that
spans 2.5 and 2.3 credits each objective separately. objStats uses the Drill's
schema, so hands-on and question accuracy land in comparable form.

Ordering uses Up/Down buttons rather than drag-and-drop: usable by keyboard,
on a phone, and in a headless test.

The generator refuses to write if any answer key is malformed: an objective it
does not know, an answer index out of range, a grid of the wrong shape, a match
answer that is not one of the choices, a console pattern that does not compile,
or a duplicate id. A bad key would silently mis-score and mis-report accuracy.

Usage:  python3 pbq_page.py [out.html]
"""
import json, html, pathlib, importlib.util, re, sys

HERE = pathlib.Path(__file__).parent
spec = importlib.util.spec_from_file_location('pbq_data', HERE / 'pbq_data.py')
D = importlib.util.module_from_spec(spec)
spec.loader.exec_module(D)

OBJTITLE = {
    '1.1': 'System and network architecture',
    '1.2': 'Indicators of malicious activity',
    '1.3': 'Tools and techniques to determine malicious activity',
    '1.4': 'Threat intelligence and threat hunting',
    '1.5': 'Efficiency and process improvement',
    '2.1': 'Vulnerability scanning methods and concepts',
    '2.2': 'Analyze output from vulnerability assessment tools',
    '2.3': 'Analyze data to prioritize vulnerabilities',
    '2.4': 'Controls to mitigate attacks and software vulnerabilities',
    '2.5': 'Vulnerability response, handling and management',
    '3.1': 'Attack methodology frameworks',
    '3.2': 'Incident response activities',
    '3.3': 'Preparation and post-incident activity',
    '4.1': 'Vulnerability management reporting and communication',
    '4.2': 'Incident response reporting and communication',
}


def esc(s):
    return html.escape(str(s), quote=True)


class BadKey(Exception):
    pass


def need(cond, msg):
    if not cond:
        raise BadKey(msg)


def build():
    out, seen = [], set()
    for p in D.PBQS:
        pid = p['id']
        need(re.fullmatch(r'[a-z0-9-]+', pid), f'{pid}: id must be a bare token')
        need(pid not in seen, f'{pid}: duplicate id'); seen.add(pid)
        need(p['obj'] in OBJTITLE, f'{pid}: unknown objective {p["obj"]}')
        ev = []
        for e in p['evidence']:
            k = e['kind']
            if k == 'log':
                ev.append({'k': k, 'l': esc(e['label']), 'c': esc(e.get('cmd', '')), 'b': esc(e['body'])})
            elif k == 'table':
                w = len(e['head'])
                need(all(len(r) == w for r in e['rows']), f'{pid}/{e["label"]}: ragged table')
                ev.append({'k': k, 'l': esc(e['label']), 'cap': esc(e.get('caption', '')),
                           'm': bool(e.get('mono')), 'h': [esc(x) for x in e['head']],
                           'r': [[esc(x) for x in r] for r in e['rows']]})
            elif k == 'doc':
                ev.append({'k': k, 'l': esc(e['label']),
                           'f': [[esc(a), esc(b)] for a, b in e['fields']],
                           'p': [esc(x) for x in e['paras']]})
            elif k == 'terminal':
                def cmdlist(lst):
                    res = []
                    for c in lst:
                        for rx in c['match']:
                            re.compile(rx)  # raises on a bad pattern
                        res.append({'m': c['match'], 'o': esc(c['out'])})
                    return res
                ev.append({'k': k, 'l': esc(e['label']), 'pr': esc(e['prompt']),
                           'bn': esc(e['banner']), 'hp': esc(e['help']),
                           'cm': cmdlist(e['cmds']), 'ms': cmdlist(e.get('miss', []))})
            else:
                raise BadKey(f'{pid}: unknown evidence kind {k}')

        qs, objs = [], []
        for i, q in enumerate(p['questions']):
            k, obj = q['kind'], q.get('obj', p['obj'])
            need(obj in OBJTITLE, f'{pid} q{i}: unknown objective {obj}')
            base = {'k': k, 'o': obj, 'p': esc(q['prompt'])}
            if k == 'select':
                n = len(q['options'])
                need(n >= 2 and len(set(q['options'])) == n, f'{pid} q{i}: options')
                need(0 <= q['answer'] < n, f'{pid} q{i}: answer out of range')
                base.update(opt=[esc(x) for x in q['options']], a=q['answer'],
                            fx=bool(q.get('fixed')), w=esc(q['why']))
                pts = 1
            elif k == 'text':
                need(q['answers'], f'{pid} q{i}: no accepted answers')
                base.update(a=[re.sub(r'\s+', ' ', x.strip().lower()) for x in q['answers']],
                            ph=esc(q.get('placeholder', '')), w=esc(q['why']),
                            show=esc(q['answers'][0]))
                pts = 1
            elif k == 'multi':
                n = len(q['options'])
                need(q['answer'] and all(0 <= a < n for a in q['answer']), f'{pid} q{i}: multi answer')
                base.update(opt=[esc(x) for x in q['options']], a=sorted(q['answer']),
                            w=esc(q['why']))
                pts = 1
            elif k == 'grid':
                R, C = len(q['rows']), len(q['cols'])
                need(len(q['answer']) == R and all(len(r) == C for r in q['answer']), f'{pid} q{i}: grid shape')
                need(len(q['rowwhy']) == R, f'{pid} q{i}: rowwhy count')
                base.update(rows=[esc(x) for x in q['rows']], cols=[esc(x) for x in q['cols']],
                            a=q['answer'], rw=[esc(x) for x in q['rowwhy']])
                pts = R
            elif k == 'order':
                need(len(q['items']) >= 3 and len(set(q['items'])) == len(q['items']), f'{pid} q{i}: order items')
                base.update(it=[esc(x) for x in q['items']], w=esc(q['why']))
                pts = len(q['items'])
            elif k == 'match':
                ch = q['choices']
                need(len(set(ch)) == len(ch), f'{pid} q{i}: duplicate choices')
                items = []
                for it in q['items']:
                    need(it['answer'] in ch, f'{pid} q{i}: "{it["answer"]}" is not a choice')
                    items.append({'t': esc(it['text']), 'a': ch.index(it['answer']), 'w': esc(it['why'])})
                base.update(ch=[esc(x) for x in ch], it=items, sh=(pid == 'killchain'))
                pts = len(items)
            else:
                raise BadKey(f'{pid} q{i}: unknown question kind {k}')
            qs.append(base)
            objs += [obj] * pts
        need(qs, f'{pid}: no questions')
        tags = sorted(set(objs))
        out.append({'id': pid, 'obj': p['obj'], 'objs': tags, 'pts': len(objs),
                    'title': esc(p['title']), 'sc': esc(p['scenario']), 'task': esc(p['task']),
                    'ev': ev, 'q': qs})
    return out


DATA = build()

CSS = r"""
/* Layout: task picker on top; each task is a two-pane exam view, evidence tabs
   left (sticky on wide screens) and the scored questions right; stacks on phones. */
:root{
  --bg:#f6f5f2; --surface:#ffffff; --surface-2:#eef1f2; --border:#dbe0e3;
  --text:#171b1f; --text-muted:#5a6570;
  --accent:#1f6f8b; --accent-ink:#ffffff; --accent-soft:#e3f0f4;
  --ok:#1f8a5c; --ok-bg:#e7f4ee; --bad:#b3433a; --bad-bg:#fbeae8;
  --term-bg:#0f1a1f; --term-fg:#cfe3ea; --term-dim:#7f98a2; --term-accent:#7fd3ee;
  --shadow:0 1px 2px rgba(20,24,28,.06),0 4px 14px rgba(20,24,28,.06);
  --radius:16px;
  --font-display:'IBM Plex Mono',ui-monospace,SFMono-Regular,Menlo,monospace;
  --font-body:'IBM Plex Sans',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --bg:#0d1216; --surface:#151c22; --surface-2:#1b242b; --border:#2b363e;
  --text:#e7edf1; --text-muted:#93a2ac; --accent:#5ab6d4; --accent-ink:#06262a; --accent-soft:#16303a;
  --ok:#55d69a; --ok-bg:#12291f; --bad:#f0948b; --bad-bg:#331a18;
  --term-bg:#081014; --term-fg:#cfe3ea; --term-dim:#6f8892; --term-accent:#7fd3ee;
  --shadow:0 1px 2px rgba(0,0,0,.4),0 10px 26px rgba(0,0,0,.35); color-scheme:dark;}}
:root[data-theme="dark"]{
  --bg:#0d1216; --surface:#151c22; --surface-2:#1b242b; --border:#2b363e;
  --text:#e7edf1; --text-muted:#93a2ac; --accent:#5ab6d4; --accent-ink:#06262a; --accent-soft:#16303a;
  --ok:#55d69a; --ok-bg:#12291f; --bad:#f0948b; --bad-bg:#331a18;
  --term-bg:#081014; --term-fg:#cfe3ea; --term-dim:#6f8892; --term-accent:#7fd3ee;
  --shadow:0 1px 2px rgba(0,0,0,.4),0 10px 26px rgba(0,0,0,.35); color-scheme:dark;}

*{box-sizing:border-box;}
body{background:var(--bg);color:var(--text);font-family:var(--font-body);margin:0;
  font-size:16px;line-height:1.55;}
.wrap{max-width:1240px;margin:0 auto;padding-left:max(16px,env(safe-area-inset-left,0px));
  padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:22px 60px;}
h1,h2,h3{font-family:var(--font-display);font-weight:600;letter-spacing:-.01em;margin:0;text-wrap:balance;}
h1{font-size:clamp(25px,5.4vw,32px);line-height:1.14;margin-bottom:8px;}
h2{font-size:clamp(19px,3.4vw,23px);line-height:1.2;}
p{margin:0 0 12px;}
a{color:var(--accent);}
code{font-family:var(--font-display);font-size:.9em;}
.backlink{font-family:var(--font-display);font-size:11.5px;color:var(--text-muted);
  text-decoration:none;display:inline-block;margin-bottom:12px;padding:3px 9px;
  border:1px solid var(--border);border-radius:999px;background:var(--surface);}
.backlink:hover{color:var(--accent);border-color:var(--accent);}
.eyebrow{font-family:var(--font-display);font-size:11.5px;letter-spacing:.07em;
  text-transform:uppercase;color:var(--accent);margin:0 0 7px;}
.lede{color:var(--text-muted);font-size:15px;max-width:68ch;}
.label{font-family:var(--font-display);font-size:11px;letter-spacing:.07em;
  text-transform:uppercase;color:var(--text-muted);margin:0 0 8px;}

/* objective accuracy */
.acc{display:flex;flex-wrap:wrap;gap:6px;margin:6px 0 0;}
.acc .chip{font-family:var(--font-display);font-size:11.5px;padding:4px 10px;border-radius:999px;
  border:1px solid var(--border);background:var(--surface);font-variant-numeric:tabular-nums;}
.acc .chip b{font-weight:600;}
.acc .none{font-size:13.5px;color:var(--text-muted);}

/* picker */
.picker{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:8px;margin:20px 0 4px;}
.pick{display:flex;flex-direction:column;gap:6px;text-align:left;cursor:pointer;
  border:1px solid var(--border);background:var(--surface);color:var(--text);
  border-radius:12px;padding:10px 12px;font:inherit;}
.pick:hover{border-color:var(--accent);}
.pick[aria-current="true"]{border-color:var(--accent);background:var(--accent-soft);
  box-shadow:inset 0 0 0 1px var(--accent);}
.pick .pt{font-size:14px;font-weight:600;line-height:1.3;}
.pick .pm{display:flex;justify-content:space-between;gap:8px;align-items:center;
  font-family:var(--font-display);font-size:11px;color:var(--text-muted);font-variant-numeric:tabular-nums;}
.pick .done{color:var(--ok);}

/* task */
.task{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);
  box-shadow:var(--shadow);margin-top:18px;padding:20px clamp(14px,2.4vw,24px) 22px;}
.thead{display:flex;flex-wrap:wrap;gap:8px 12px;align-items:baseline;justify-content:space-between;margin-bottom:12px;}
.tags{display:flex;flex-wrap:wrap;gap:5px;}
.tag{font-family:var(--font-display);font-size:10.5px;letter-spacing:.05em;text-transform:uppercase;
  background:var(--surface-2);color:var(--text-muted);border-radius:999px;padding:2px 9px;white-space:nowrap;}
.scenario{background:var(--surface-2);border-left:3px solid var(--accent);
  border-radius:0 10px 10px 0;padding:12px 15px;margin:0 0 10px;font-size:15px;max-width:90ch;}
.instr{font-size:14.5px;color:var(--text-muted);max-width:90ch;margin-bottom:16px;}
.split{display:grid;grid-template-columns:minmax(0,1fr);gap:18px;}
@media (min-width:980px){
  .split.two{grid-template-columns:minmax(0,1.12fr) minmax(0,1fr);align-items:start;}
  .split.two .evpane{position:sticky;top:12px;max-height:calc(100vh - 24px);display:flex;flex-direction:column;}
  .split.two .evbody{overflow:auto;min-height:0;}
}

/* evidence */
.evpane{border:1px solid var(--border);border-radius:12px;background:var(--bg);min-width:0;}
.tabs{display:flex;flex-wrap:wrap;gap:4px;padding:8px 8px 0;border-bottom:1px solid var(--border);}
.tab{font-family:var(--font-display);font-size:12px;padding:7px 11px;border:1px solid transparent;
  border-bottom:none;border-radius:8px 8px 0 0;background:transparent;color:var(--text-muted);cursor:pointer;
  margin-bottom:-1px;}
.tab:hover{color:var(--accent);}
.tab[aria-selected="true"]{background:var(--surface);color:var(--text);border-color:var(--border);}
.evbody{padding:12px;min-width:0;}
.cmd{font-family:var(--font-display);font-size:12px;color:var(--text-muted);margin:0 0 6px;word-break:break-all;}
pre.out{font-family:var(--font-display);font-size:12px;line-height:1.5;margin:0;padding:12px;
  background:var(--surface);border:1px solid var(--border);border-radius:8px;overflow-x:auto;
  white-space:pre;color:var(--text);}
.tblwrap{overflow-x:auto;border:1px solid var(--border);border-radius:8px;background:var(--surface);}
table.ev{border-collapse:collapse;width:100%;font-size:13px;}
table.ev th,table.ev td{padding:6px 10px;border-bottom:1px solid var(--border);text-align:left;vertical-align:top;}
table.ev th{font-family:var(--font-display);font-size:10.5px;letter-spacing:.05em;text-transform:uppercase;
  color:var(--text-muted);background:var(--surface-2);white-space:nowrap;}
table.ev tr:last-child td{border-bottom:none;}
table.ev.mono td{font-family:var(--font-display);font-size:11.5px;overflow-wrap:anywhere;min-width:4.5ch;}
.cap{font-size:12.5px;color:var(--text-muted);margin:0 0 6px;}
.doc{background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:12px 14px;}
.doc dl{display:grid;grid-template-columns:max-content minmax(0,1fr);gap:4px 12px;margin:0 0 12px;
  font-size:13px;padding-bottom:10px;border-bottom:1px solid var(--border);}
.doc dt{font-family:var(--font-display);font-size:11px;color:var(--text-muted);padding-top:2px;}
.doc dd{margin:0;overflow-wrap:anywhere;}
.doc p{font-size:14.5px;}
.doc p:last-child{margin-bottom:0;}

/* console */
.term{background:var(--term-bg);color:var(--term-fg);border-radius:8px;font-family:var(--font-display);
  font-size:12px;line-height:1.5;display:flex;flex-direction:column;min-height:300px;}
.term .scroll{padding:12px 12px 4px;overflow:auto;max-height:440px;flex:1;}
.term pre{margin:0;white-space:pre;font:inherit;color:inherit;}
.term .dim{color:var(--term-dim);}
.term .ps{color:var(--term-accent);}
.term form{display:flex;gap:8px;align-items:center;padding:8px 12px 12px;}
.term input{flex:1;min-width:0;background:transparent;border:none;color:var(--term-fg);
  font:inherit;outline:none;padding:4px 0;caret-color:var(--term-accent);}
.term:focus-within{box-shadow:0 0 0 2px var(--accent);}

/* questions */
.qpane{display:flex;flex-direction:column;gap:12px;min-width:0;}
.q{border:1px solid var(--border);border-radius:12px;padding:12px 14px;background:var(--bg);}
.q.right{background:var(--ok-bg);border-color:var(--ok);}
.q.wrong{background:var(--bad-bg);border-color:var(--bad);}
.q.mixed{border-color:var(--bad);}
.qp{font-size:15px;font-weight:500;margin:0 0 9px;}
.q select,.q input[type=text]{font-family:var(--font-body);font-size:14px;padding:7px 10px;width:100%;
  border:1px solid var(--border);border-radius:10px;background:var(--surface);color:var(--text);}
.q input[type=text]{font-family:var(--font-display);font-size:13.5px;}
.opts{display:flex;flex-direction:column;gap:6px;}
.opt{display:flex;gap:9px;align-items:flex-start;font-size:14.5px;cursor:pointer;
  padding:6px 8px;border-radius:8px;border:1px solid var(--border);background:var(--surface);}
.opt input{margin-top:4px;accent-color:var(--accent);}
.opt.key{border-color:var(--ok);}
.gridwrap{overflow-x:auto;}
table.grid{border-collapse:collapse;width:100%;font-size:13.5px;}
table.grid th,table.grid td{padding:7px 8px;border-bottom:1px solid var(--border);text-align:center;}
table.grid th{font-family:var(--font-display);font-size:10.5px;letter-spacing:.04em;text-transform:uppercase;
  color:var(--text-muted);font-weight:500;}
table.grid td:first-child,table.grid th:first-child{text-align:left;font-family:var(--font-display);font-size:12.5px;}
table.grid input{width:18px;height:18px;accent-color:var(--accent);}
table.grid tr.right td{background:var(--ok-bg);}
table.grid tr.wrong td{background:var(--bad-bg);}
.keymark{font-family:var(--font-display);font-size:10.5px;color:var(--ok);display:block;}
ol.stages{list-style:none;counter-reset:s;margin:0;padding:0;}
ol.stages li{counter-increment:s;display:flex;align-items:center;gap:10px;
  border:1px solid var(--border);border-radius:10px;background:var(--surface);
  padding:7px 10px;margin-bottom:6px;}
ol.stages li::before{content:counter(s);font-family:var(--font-display);font-size:12px;
  color:var(--text-muted);width:18px;flex:0 0 18px;text-align:right;}
ol.stages li.right{background:var(--ok-bg);border-color:var(--ok);}
ol.stages li.wrong{background:var(--bad-bg);border-color:var(--bad);}
.sname{flex:1;min-width:0;font-size:14.5px;}
.move{font-family:var(--font-display);font-size:12px;line-height:1;padding:5px 8px;
  border:1px solid var(--border);border-radius:8px;background:var(--surface);
  color:var(--text-muted);cursor:pointer;}
.move:hover:not(:disabled){border-color:var(--accent);color:var(--accent);}
.move:disabled{opacity:.35;cursor:default;}
.mitem{border:1px solid var(--border);border-radius:10px;padding:9px 11px;margin-bottom:8px;background:var(--surface);}
.mitem:last-child{margin-bottom:0;}
.mitem p{margin:0 0 7px;font-size:14.5px;}
.mitem.right{background:var(--ok-bg);border-color:var(--ok);}
.mitem.wrong{background:var(--bad-bg);border-color:var(--bad);}
.mitem .mt{font-family:var(--font-display);font-size:13px;font-weight:600;}
.why{font-size:14px;line-height:1.55;margin-top:9px;padding-top:9px;border-top:1px solid var(--border);}
.why b{font-family:var(--font-display);font-size:11px;letter-spacing:.05em;text-transform:uppercase;
  color:var(--text-muted);display:block;margin-bottom:3px;}
.rowwhy{font-size:13.5px;margin:6px 0 0;}
.rowwhy b{font-family:var(--font-display);font-size:12px;}

.btnrow{display:flex;gap:8px;flex-wrap:wrap;align-items:center;}
.btn{font-family:var(--font-display);font-size:12.5px;padding:9px 15px;border-radius:10px;
  cursor:pointer;border:1px solid var(--border);background:var(--surface);color:var(--text);}
.btn:hover{border-color:var(--accent);color:var(--accent);}
.btn.primary{background:var(--accent);color:var(--accent-ink);border-color:var(--accent);}
.btn.primary:hover{color:var(--accent-ink);filter:brightness(1.08);}
.btn:focus-visible,.move:focus-visible,.tab:focus-visible,.pick:focus-visible,select:focus-visible,
input:focus-visible{outline:2px solid var(--accent);outline-offset:2px;}
.score{font-family:var(--font-display);font-size:13px;padding:10px 13px;border-radius:12px;
  background:var(--surface-2);font-variant-numeric:tabular-nums;}
.unans{font-size:13px;color:var(--bad);}
.note{border-left:3px solid var(--border);background:var(--surface-2);border-radius:0 10px 10px 0;
  padding:12px 14px;font-size:13.5px;color:var(--text-muted);line-height:1.55;margin-top:22px;max-width:90ch;}
.foot{margin-top:22px;padding-top:14px;border-top:1px solid var(--border);font-size:12px;color:var(--text-muted);}
@media (prefers-reduced-motion:no-preference){.pick,.btn,.tab{transition:border-color .12s,background-color .12s,color .12s;}}
"""

JS = r"""
var KEY = "cysa:pbq:v1";
var st = {best:{}, objStats:{}};
try{ var raw = localStorage.getItem(KEY); if(raw) st = JSON.parse(raw) || st; }catch(e){}
if(!st || typeof st !== 'object') st = {best:{}, objStats:{}};
if(!st.best) st.best = {}; if(!st.objStats) st.objStats = {};
function save(){ try{ localStorage.setItem(KEY, JSON.stringify(st)); }catch(e){} }
function bestGot(b){ if(!b) return null; return (typeof b.got === 'number') ? b.got : ((b.order||0) + (b.match||0)); }

function $(id){ return document.getElementById(id); }
function shuffle(a){ a=a.slice(); for(var i=a.length-1;i>0;i--){var j=Math.floor(Math.random()*(i+1));var t=a[i];a[i]=a[j];a[j]=t;} return a; }
function range(n){ var r=[]; for(var i=0;i<n;i++) r.push(i); return r; }
function escT(s){ return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }
function norm(s){ return String(s||'').trim().toLowerCase().replace(/\s+/g,' ').replace(/\.$/,''); }
function each(nodes, fn){ Array.prototype.forEach.call(nodes, fn); }

var BYID = {}; PBQS.forEach(function(p){ BYID[p.id] = p; });
var RUN = {};   // per-PBQ working state, kept while the page is open

function fresh(p){
  var r = {ans:{}, perm:{}, ord:{}, items:{}, checked:false, tab:0, term:{}, hist:[], last:null};
  p.q.forEach(function(q, i){
    if(q.k === 'select' || q.k === 'multi') r.perm[i] = q.fx ? range(q.opt.length) : shuffle(range(q.opt.length));
    if(q.k === 'order'){ var o; do { o = shuffle(q.it); } while(o.join('|') === q.it.join('|')); r.ord[i] = o; }
    if(q.k === 'match') r.items[i] = q.sh ? shuffle(range(q.it.length)) : range(q.it.length);
    if(q.k === 'multi') r.ans[i] = [];
    if(q.k === 'grid') r.ans[i] = q.rows.map(function(){ return q.cols.map(function(){ return false; }); });
    if(q.k === 'match') r.ans[i] = {};
  });
  return r;
}
function run(p){ if(!RUN[p.id]) RUN[p.id] = fresh(p); return RUN[p.id]; }

/* ---------- accuracy strip and picker ---------- */
function drawAcc(){
  var keys = Object.keys(st.objStats).filter(function(k){ return st.objStats[k].t > 0; }).sort();
  var el = $('acc');
  if(!keys.length){ el.innerHTML = '<span class="none">No tasks checked yet. Accuracy appears here per objective after your first attempt.</span>'; return; }
  el.innerHTML = keys.map(function(k){
    var s = st.objStats[k], pct = Math.round(100*s.c/s.t);
    return '<span class="chip" title="'+escT(OBJ[k]||'')+'"><b>'+k+'</b> '+pct+'% &middot; '+s.c+'/'+s.t+'</span>';
  }).join('');
}
function drawPicker(cur){
  $('picker').innerHTML = PBQS.map(function(p){
    var b = st.best[p.id], g = bestGot(b);
    var stat = (g === null) ? '<span>Not attempted</span>'
             : '<span class="'+(g===b.total?'done':'')+'">Best '+g+'/'+b.total+'</span>';
    return '<button class="pick" type="button" data-id="'+p.id+'" aria-current="'+(p.id===cur)+'">'
         + '<span class="pt">'+p.title+'</span>'
         + '<span class="pm"><span>'+p.objs.join(' &middot; ')+'</span>'+stat+'</span></button>';
  }).join('');
  each($('picker').querySelectorAll('.pick'), function(b){
    b.onclick = function(){ open(b.getAttribute('data-id'), true); };
  });
}

/* ---------- task ---------- */
var CUR = null;
function open(id, scroll){
  if(!BYID[id]) id = PBQS[0].id;
  CUR = id; st.open = id; save();
  try{ if(location.hash.slice(1) !== id) history.replaceState(null, '', '#'+id); }catch(e){}
  drawPicker(id);
  drawTask(BYID[id]);
  if(scroll){ var t = $('task'); if(t && t.scrollIntoView) t.scrollIntoView({block:'start'}); }
}

function drawTask(p){
  var r = run(p);
  var hasEv = p.ev.length > 0;
  var h = '<div class="thead"><h2>'+p.title+'</h2><div class="tags">'
        + p.objs.map(function(o){ return '<span class="tag" title="'+escT(OBJ[o]||'')+'">Objective '+o+'</span>'; }).join('')
        + '</div></div>'
        + '<div class="scenario">'+p.sc+'</div><p class="instr">'+p.task+'</p>'
        + '<div class="split'+(hasEv?' two':'')+'">';
  if(hasEv){
    h += '<section class="evpane" aria-label="Evidence"><div class="tabs" role="tablist">';
    p.ev.forEach(function(e, i){
      h += '<button class="tab" type="button" role="tab" id="tab-'+p.id+'-'+i+'" aria-selected="'+(i===r.tab)+'" data-i="'+i+'">'+e.l+'</button>';
    });
    h += '</div><div class="evbody" id="evbody" role="tabpanel"></div></section>';
  }
  h += '<section class="qpane" id="qpane" aria-label="Questions"></section></div>';
  $('task').innerHTML = h;
  if(hasEv){
    each($('task').querySelectorAll('.tab'), function(b){
      b.onclick = function(){ r.tab = +b.getAttribute('data-i');
        each($('task').querySelectorAll('.tab'), function(x){ x.setAttribute('aria-selected', String(x===b)); });
        drawEvidence(p); };
    });
    drawEvidence(p);
  }
  drawQuestions(p);
}

function drawEvidence(p){
  var r = run(p), e = p.ev[r.tab], body = $('evbody'), h = '';
  if(e.k === 'log'){
    if(e.c) h += '<p class="cmd">'+e.c+'</p>';
    h += '<pre class="out">'+e.b+'</pre>';
  } else if(e.k === 'table'){
    if(e.cap) h += '<p class="cap">'+e.cap+'</p>';
    h += '<div class="tblwrap"><table class="ev'+(e.m?' mono':'')+'"><thead><tr>'
       + e.h.map(function(x){ return '<th>'+x+'</th>'; }).join('') + '</tr></thead><tbody>'
       + e.r.map(function(row){ return '<tr>'+row.map(function(x){ return '<td>'+x+'</td>'; }).join('')+'</tr>'; }).join('')
       + '</tbody></table></div>';
  } else if(e.k === 'doc'){
    h += '<div class="doc">';
    if(e.f.length) h += '<dl>' + e.f.map(function(f){ return '<dt>'+f[0]+'</dt><dd>'+f[1]+'</dd>'; }).join('') + '</dl>';
    h += e.p.map(function(x){ return '<p>'+x+'</p>'; }).join('') + '</div>';
  } else if(e.k === 'terminal'){
    var key = r.tab;
    if(!r.term[key]) r.term[key] = ['<pre class="dim">'+e.bn+'</pre>'];
    h += '<div class="term"><div class="scroll" id="tscroll">'+r.term[key].join('')+'</div>'
       + '<form id="tform" autocomplete="off"><span class="ps">'+e.pr+'</span>'
       + '<input id="tin-'+p.id+'" type="text" spellcheck="false" autocapitalize="off" aria-label="Console command" placeholder="nmap -sV -sC srv1.hq.lab"></form></div>';
  }
  body.innerHTML = h;
  if(e.k === 'terminal') wireTerm(p, e);
}

function termRun(e, cmd){
  var c = cmd.trim().replace(/\s+/g,' ');
  if(c === '') return null;
  if(c === 'help') return e.hp;
  var lists = [e.cm, e.ms];
  for(var L=0; L<lists.length; L++){
    for(var i=0; i<lists[L].length; i++){
      var m = lists[L][i].m;
      for(var j=0; j<m.length; j++){ if(new RegExp(m[j], 'i').test(c)) return lists[L][i].o; }
    }
  }
  return escT(c.split(' ')[0]) + ': command not found (type help)';
}

function wireTerm(p, e){
  var r = run(p), key = r.tab, sc = $('tscroll'), inp = $('tin-'+p.id), hp = r.hist.length;
  sc.scrollTop = sc.scrollHeight;
  $('tform').onsubmit = function(ev){
    ev.preventDefault();
    var cmd = inp.value; inp.value = '';
    if(cmd.trim()){ r.hist.push(cmd); } hp = r.hist.length;
    if(cmd.trim() === 'clear'){ r.term[key] = []; sc.innerHTML = ''; return; }
    var out = termRun(e, cmd);
    var add = '<pre><span class="ps">'+e.pr+'</span> '+escT(cmd)+'</pre>' + (out === null ? '' : '<pre>'+out+'</pre>');
    r.term[key].push(add);
    sc.insertAdjacentHTML('beforeend', add);
    sc.scrollTop = sc.scrollHeight;
  };
  inp.onkeydown = function(ev){
    if(ev.key === 'ArrowUp' && hp > 0){ hp--; inp.value = r.hist[hp]; ev.preventDefault(); }
    else if(ev.key === 'ArrowDown'){ if(hp < r.hist.length-1){ hp++; inp.value = r.hist[hp]; } else { hp = r.hist.length; inp.value = ''; } ev.preventDefault(); }
  };
}

/* ---------- questions ---------- */
function qid(p, i, s){ return 'q-'+p.id+'-'+i+(s===undefined?'':'-'+s); }

function marks(p){   // [{i, ok, o}] one per scored field
  var r = run(p), m = [];
  p.q.forEach(function(q, i){
    var a = r.ans[i];
    if(q.k === 'select') m.push({i:i, ok: a !== undefined && a !== '' && +a === q.a, o:q.o});
    else if(q.k === 'text') m.push({i:i, ok: q.a.indexOf(norm(a)) >= 0, o:q.o});
    else if(q.k === 'multi') m.push({i:i, ok: a.slice().sort(function(x,y){return x-y;}).join(',') === q.a.join(','), o:q.o});
    else if(q.k === 'grid') q.rows.forEach(function(_, ri){
      m.push({i:i, ok: q.a[ri].every(function(v, ci){ return v === a[ri][ci]; }), o:q.o}); });
    else if(q.k === 'order') r.ord[i].forEach(function(s, pi){ m.push({i:i, ok: s === q.it[pi], o:q.o}); });
    else if(q.k === 'match') q.it.forEach(function(it, ii){ m.push({i:i, ok: a[ii] !== undefined && a[ii] !== '' && +a[ii] === it.a, o:q.o}); });
  });
  return m;
}

function unanswered(p){
  var r = run(p), n = 0;
  p.q.forEach(function(q, i){
    var a = r.ans[i];
    if(q.k === 'select' && (a === undefined || a === '')) n++;
    else if(q.k === 'text' && !norm(a)) n++;
    else if(q.k === 'multi' && !a.length) n++;
    else if(q.k === 'match') q.it.forEach(function(_, ii){ if(a[ii] === undefined || a[ii] === '') n++; });
  });
  return n;
}

function why(ok, label, text){ return '<div class="why"><b>'+(ok ? 'Correct' : 'Answer: '+label)+'</b>'+text+'</div>'; }

function drawQuestions(p, focusSel){
  var r = run(p), C = r.checked, h = '';
  p.q.forEach(function(q, i){
    var a = r.ans[i], cls = '', inner = '';
    if(q.k === 'select'){
      var ok = C && a !== undefined && a !== '' && +a === q.a;
      if(C) cls = ok ? ' right' : ' wrong';
      inner = '<select id="'+qid(p,i)+'" data-i="'+i+'"'+(C?' disabled':'')+'><option value="">Choose&hellip;</option>'
        + r.perm[i].map(function(oi){ return '<option value="'+oi+'"'+(String(a)===String(oi)?' selected':'')+'>'+q.opt[oi]+'</option>'; }).join('')
        + '</select>' + (C ? why(ok, q.opt[q.a], q.w) : '');
    } else if(q.k === 'text'){
      var okt = C && q.a.indexOf(norm(a)) >= 0;
      if(C) cls = okt ? ' right' : ' wrong';
      inner = '<input type="text" id="'+qid(p,i)+'" data-i="'+i+'" placeholder="'+q.ph+'" value="'+escT(a||'')+'"'
        + ' autocomplete="off" spellcheck="false"'+(C?' disabled':'')+'>' + (C ? why(okt, q.show, q.w) : '');
    } else if(q.k === 'multi'){
      var okm = C && a.slice().sort(function(x,y){return x-y;}).join(',') === q.a.join(',');
      if(C) cls = okm ? ' right' : ' wrong';
      inner = '<div class="opts">' + r.perm[i].map(function(oi){
          var on = a.indexOf(oi) >= 0, key = C && q.a.indexOf(oi) >= 0;
          return '<label class="opt'+(key?' key':'')+'"><input type="checkbox" id="'+qid(p,i,oi)+'" data-i="'+i+'" data-o="'+oi+'"'
               + (on?' checked':'')+(C?' disabled':'')+'><span>'+q.opt[oi]+(key?' <span class="keymark">correct choice</span>':'')+'</span></label>';
        }).join('') + '</div>'
        + (C ? why(okm, q.a.map(function(x){ return q.opt[x]; }).join('; '), q.w) : '');
    } else if(q.k === 'grid'){
      var rowsOk = q.rows.map(function(_, ri){ return q.a[ri].every(function(v, ci){ return v === a[ri][ci]; }); });
      if(C) cls = rowsOk.every(Boolean) ? ' right' : ' mixed';
      inner = '<div class="gridwrap"><table class="grid"><thead><tr><th>Server</th>'
        + q.cols.map(function(c){ return '<th scope="col">'+c+'</th>'; }).join('') + '</tr></thead><tbody>'
        + q.rows.map(function(rw, ri){
            return '<tr'+(C?' class="'+(rowsOk[ri]?'right':'wrong')+'"':'')+'><th scope="row">'+rw+'</th>'
              + q.cols.map(function(c, ci){
                  return '<td><input type="checkbox" id="'+qid(p,i,ri+'-'+ci)+'" data-i="'+i+'" data-r="'+ri+'" data-c="'+ci+'"'
                    + ' aria-label="'+rw+': '+c+'"'+(a[ri][ci]?' checked':'')+(C?' disabled':'')+'>'
                    + (C ? '<span class="keymark">'+(q.a[ri][ci]?'meets':'fails')+'</span>' : '') + '</td>';
                }).join('') + '</tr>';
          }).join('') + '</tbody></table></div>'
        + (C ? '<div class="why">' + q.rows.map(function(rw, ri){
              return '<p class="rowwhy"><b>'+rw+' &mdash; '+(rowsOk[ri]?'correct':'check again')+'.</b> '+q.rw[ri]+'</p>'; }).join('') + '</div>' : '');
    } else if(q.k === 'order'){
      var ord = r.ord[i];
      if(C) cls = ord.every(function(s, pi){ return s === q.it[pi]; }) ? ' right' : ' mixed';
      inner = '<ol class="stages">' + ord.map(function(s, pi){
          var lc = C ? (s === q.it[pi] ? ' class="right"' : ' class="wrong"') : '';
          return '<li'+lc+'><span class="sname">'+s+'</span>'
            + '<button class="move" type="button" id="'+qid(p,i,'u'+pi)+'" data-i="'+i+'" data-p="'+pi+'" data-d="-1" aria-label="Move '+s+' up"'+((C||pi===0)?' disabled':'')+'>&uarr;</button>'
            + '<button class="move" type="button" id="'+qid(p,i,'d'+pi)+'" data-i="'+i+'" data-p="'+pi+'" data-d="1" aria-label="Move '+s+' down"'+((C||pi===ord.length-1)?' disabled':'')+'>&darr;</button></li>';
        }).join('') + '</ol>' + (C ? '<div class="why"><b>Correct order</b>'+q.w+'</div>' : '');
    } else if(q.k === 'match'){
      var allOk = q.it.every(function(it, ii){ return a[ii] !== undefined && a[ii] !== '' && +a[ii] === it.a; });
      if(C) cls = allOk ? ' right' : ' mixed';
      inner = r.items[i].map(function(ii){
          var it = q.it[ii], pk = a[ii], okk = pk !== undefined && pk !== '' && +pk === it.a;
          var short = it.t.length < 40;
          return '<div class="mitem'+(C?(okk?' right':' wrong'):'')+'">'
            + (short ? '<p class="mt">'+it.t+'</p>' : '<p>'+it.t+'</p>')
            + '<select id="'+qid(p,i,ii)+'" data-i="'+i+'" data-m="'+ii+'"'+(C?' disabled':'')+' aria-label="Answer for '+escT(it.t.replace(/&[a-z#0-9]+;/g,' ').slice(0,60))+'">'
            + '<option value="">Choose&hellip;</option>'
            + q.ch.map(function(c, ci){ return '<option value="'+ci+'"'+(String(pk)===String(ci)?' selected':'')+'>'+c+'</option>'; }).join('')
            + '</select>' + (C ? why(okk, q.ch[it.a], it.w) : '') + '</div>';
        }).join('');
    }
    h += '<div class="q'+cls+'"><p class="qp">'+q.p+'</p>'+inner+'</div>';
  });
  h += '<div class="btnrow">'
     + (C ? '<button class="btn primary" type="button" id="again">Try again</button>'
          : '<button class="btn primary" type="button" id="check">Check my answers</button>')
     + '<span class="unans" id="unans"></span></div>'
     + '<div class="score" id="score" aria-live="polite"></div>';
  var pane = $('qpane');
  pane.innerHTML = h;
  wireQuestions(p);
  drawScore(p);
  if(focusSel){ var f = $(focusSel); if(f && !f.disabled) f.focus(); }
}

function wireQuestions(p){
  var r = run(p), pane = $('qpane');
  each(pane.querySelectorAll('select[data-i]'), function(s){
    s.onchange = function(){
      var i = +s.getAttribute('data-i');
      if(s.hasAttribute('data-m')) r.ans[i][+s.getAttribute('data-m')] = s.value;
      else r.ans[i] = s.value;
    };
  });
  each(pane.querySelectorAll('input[type=text][data-i]'), function(t){
    t.oninput = function(){ r.ans[+t.getAttribute('data-i')] = t.value; };
    t.onkeydown = function(ev){ if(ev.key === 'Enter'){ ev.preventDefault(); } };
  });
  each(pane.querySelectorAll('input[type=checkbox][data-i]'), function(c){
    c.onchange = function(){
      var i = +c.getAttribute('data-i');
      if(c.hasAttribute('data-o')){
        var o = +c.getAttribute('data-o'), arr = r.ans[i], k = arr.indexOf(o);
        if(c.checked && k < 0) arr.push(o); if(!c.checked && k >= 0) arr.splice(k, 1);
      } else {
        r.ans[i][+c.getAttribute('data-r')][+c.getAttribute('data-c')] = c.checked;
      }
    };
  });
  each(pane.querySelectorAll('.move'), function(b){
    b.onclick = function(){
      var i = +b.getAttribute('data-i'), pi = +b.getAttribute('data-p'), d = +b.getAttribute('data-d'), o = r.ord[i], j = pi + d;
      if(j < 0 || j >= o.length) return;
      var t = o[pi]; o[pi] = o[j]; o[j] = t;
      drawQuestions(p, qid(p, i, (d < 0 ? 'u' : 'd') + j));
    };
  });
  var c = $('check');
  if(c) c.onclick = function(){
    var n = unanswered(p);
    if(n && c.getAttribute('data-confirm') !== '1'){
      $('unans').textContent = n + (n === 1 ? ' answer is' : ' answers are') + ' still blank. Select Check again to score anyway.';
      c.setAttribute('data-confirm', '1'); c.textContent = 'Check anyway'; return;
    }
    score(p); r.checked = true; drawQuestions(p); drawPicker(p.id); drawAcc();
  };
  var a = $('again');
  if(a) a.onclick = function(){
    var keep = {tab:r.tab, term:r.term, hist:r.hist, last:r.last};
    RUN[p.id] = fresh(p); Object.keys(keep).forEach(function(k){ RUN[p.id][k] = keep[k]; });
    drawQuestions(p);
    var first = $('qpane').querySelector('select,input'); if(first) first.focus();
  };
}

function score(p){
  var m = marks(p), got = 0;
  m.forEach(function(x){
    if(x.ok) got++;
    var os = st.objStats[x.o] || {c:0, t:0};
    os.t += 1; if(x.ok) os.c += 1; st.objStats[x.o] = os;
  });
  var b = st.best[p.id], bg = bestGot(b);
  if(bg === null || got > bg || b.total !== m.length) st.best[p.id] = {got:got, total:m.length};
  run(p).last = {got:got, total:m.length};
  save();
}

function drawScore(p){
  var el = $('score'), b = st.best[p.id], g = bestGot(b), last = run(p).last, txt = '';
  if(last) txt += 'This attempt: ' + last.got + ' / ' + last.total + '. ';
  txt += (g === null) ? (p.pts + ' scored fields. Not attempted yet.') : ('Best: ' + g + ' / ' + b.total + '.');
  el.textContent = txt;
}

drawAcc();
var start = (location.hash || '').slice(1);
open(BYID[start] ? start : (BYID[st.open] ? st.open : PBQS[0].id), false);
window.addEventListener('hashchange', function(){ var h = location.hash.slice(1); if(BYID[h] && h !== CUR) open(h, true); });
"""

total_pts = sum(p['pts'] for p in DATA)
body = ['<title>CySA+ Performance Tasks</title>',
        '<meta name="claude:viewport-fit-sides" content="cover">',
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
        'family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap">',
        f'<style>{CSS}</style>', '',
        '<div class="wrap">',
        '  <a class="backlink" href="https://claude.ai/artifact/PrxFejEDNFYfNB7V7Ahjvq">&larr; CySA+ toolkit</a>',
        '  <p class="eyebrow">CompTIA CySA+ &middot; CS0-003</p>',
        '  <h1>Performance Tasks</h1>',
        f'  <p class="lede">{len(DATA)} hands-on exercises in the shapes the exam uses: read the evidence, '
        'run the console, decide, then read why. Every field is scored against its own objective.</p>',
        '  <p class="label" style="margin-top:14px">Your accuracy by objective</p>',
        '  <div class="acc" id="acc"></div>',
        '  <nav class="picker" id="picker" aria-label="Tasks"></nav>',
        '  <article class="task" id="task"></article>',
        '  <div class="note">Progress saves in this browser under <code>cysa:pbq:v1</code>. '
        'Use this one copy of the page for all your practice, so your scores stay in one place.</div>',
        '  <div class="foot">Original study material written against CompTIA\'s published '
        'CS0-003 objectives. Scenarios, logs and addresses are invented; external addresses use '
        'documentation ranges. Not official CompTIA content, and not affiliated with, '
        'authorized by or endorsed by CompTIA.</div>',
        '</div>', '',
        '<script>',
        'var PBQS = ' + json.dumps(DATA, ensure_ascii=False, separators=(",", ":")) + ';',
        'var OBJ = ' + json.dumps(OBJTITLE, ensure_ascii=False) + ';',
        JS, '</script>', '']

out = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '/home/claude/cysa-pbq.html')
out.parent.mkdir(parents=True, exist_ok=True)
text = '\n'.join(body)
out.write_text(text, encoding='utf-8')
print(f'written {out}  {len(text)//1024} KB | {len(DATA)} tasks, {total_pts} scored fields')
for p in DATA:
    print(f'   {p["obj"]:4} {",".join(p["objs"]):16} {p["pts"]:3} pts  {html.unescape(p["title"])}')
