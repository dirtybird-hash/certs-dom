"""Widen the Security+ hub's global search from notebooks only to notebooks + acronyms + drill items.

Usage: python3 patch_hub.py <in.html> <out.html> [--repo]
--repo rewrites artifact URLs to the repo's relative filenames.
Idempotent: re-running replaces the EXTRA block rather than adding a second one.
"""
import json, re, sys, pathlib

src, dst = sys.argv[1], sys.argv[2]
REPO = '--repo' in sys.argv
HERE = pathlib.Path(__file__).parent
data = json.load(open(HERE / 'data.json'))

ACR_URL = 'https://claude.ai/artifact/AWyxEkC2q9eHzRvyDUNkb1'
DRILL_URL = {'1': 'https://claude.ai/artifact/V4c6LTwdzLraL6923m1FG2', '2': 'https://claude.ai/artifact/JLQhDRGVEeYBbUzRaUqgzv',
             '3': 'https://claude.ai/artifact/CLSzAzhXsHyydspYA3W4ti', '4': 'https://claude.ai/artifact/3TDmapWnJANA3HqVMHVvne',
             '5': 'https://claude.ai/artifact/Wyhp4zXtxfBbihG4azVnRt'}
if REPO:
    ACR_URL = 'acronym-drill.html'
    DRILL_URL = {d: f'domain{d}-drill.html' for d in DRILL_URL}

def esc(s): return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

extra = []
for a in data['acr']:
    extra.append({'d': str(a['dm']), 'o': a['o'], 'k': 'Acronym', 'id': 'acr-' + a['a'],
                  't': esc(a['a']) + ' &mdash; ' + esc(a['x']),
                  'h': '<p><strong>' + esc(a['a']) + '</strong> stands for ' + esc(a['x']) + '.</p>'})
for d, v in data['drills'].items():
    for c in v['F']:
        extra.append({'d': d, 'o': c['obj'], 'k': 'Flashcard', 'id': f'f{d}-{c["id"]}', 't': c['t'], 'h': '<p>' + c['d'] + '</p>'})
    for q in v['Q']:
        extra.append({'d': d, 'o': q['obj'], 'k': 'Quiz', 'id': f'q{d}-{q["id"]}', 't': q['q'],
                      'h': '<p><strong>Answer:</strong> ' + q['c'][q['a']] + '</p><p>' + q['e'] + '</p>'})
    for q in v['S']:
        extra.append({'d': d, 'o': q['obj'], 'k': 'Scenario', 'id': f's{d}-{q["id"]}', 't': q['q'],
                      'h': '<p><strong>Answer:</strong> ' + q['c'][q['a']] + '</p><p>' + q['e'] + '</p>'})
blob = json.dumps(extra, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')

s = pathlib.Path(src).read_text(encoding='utf-8')
block = ('/*EXTRA-START*/var EXTRA = ' + blob + ';\nvar EXTRA_URL = ' +
         json.dumps({'acr': ACR_URL, 'drill': DRILL_URL}) + ';/*EXTRA-END*/')
if '/*EXTRA-START*/' in s:
    s = re.sub(r'/\*EXTRA-START\*/.*?/\*EXTRA-END\*/', lambda m: block, s, count=1, flags=re.S)
else:
    def rep(old, new, count=1):
        global s
        assert s.count(old) == 1, 'anchor not found exactly once: ' + old[:60]
        s = s.replace(old, new, count)
    rep('/*INDEX-END*/', '/*INDEX-END*/\n' + block)
    # merge extras into the index before it is prepared
    rep('(function prepIndex(){', 'INDEX.forEach(function(x){ if(!x.k) x.k = "Note"; });\nINDEX = INDEX.concat(EXTRA);\n(function prepIndex(){')
    # hit cards: kind chip + the right destination
    rep("""'<span class="hit-meta"><span class="dchip">Domain ' + x.d + '</span><span class="ocode">' + x.o + '</span><span class="chev">&#9656;</span></span>' +""",
        """'<span class="hit-meta"><span class="dchip">Domain ' + x.d + '</span><span class="ocode">' + x.o + '</span><span class="kchip k-' + x.k.toLowerCase() + '">' + x.k + '</span><span class="chev">&#9656;</span></span>' +""")
    rep("""      (nb ? '<a class="hit-open" href="' + nb + '#' + x.id + '">Open in the Domain ' + x.d + ' Notebook <span aria-hidden="true">&rarr;</span></a>' : '') +""",
        """      (x.k === 'Note' ? (nb ? '<a class="hit-open" href="' + nb + '#' + x.id + '">Open in the Domain ' + x.d + ' Notebook <span aria-hidden="true">&rarr;</span></a>' : '')
       : x.k === 'Acronym' ? '<a class="hit-open" href="' + EXTRA_URL.acr + '">Open the Acronym Drill <span aria-hidden="true">&rarr;</span></a>'
       : '<a class="hit-open" href="' + EXTRA_URL.drill[x.d] + '">Practice in the Domain ' + x.d + ' Drill <span aria-hidden="true">&rarr;</span></a>') +""")
    # acronyms and short questions: open straight away is pointless; keep collapsed, but an exact acronym gets top score
    rep("""    if(x.ltt.indexOf(ql) !== -1) score += 50;""",
        """    if(x.ltt.indexOf(ql) !== -1) score += 50;
    if(x.k === 'Acronym' && x.ltt.split(' ')[0] === ql) score += 400;
    if(x.k === 'Note') score += 15;""")
    # kind filter
    rep("""var MAX_HITS = 60;""", """var MAX_HITS = 60, KIND = '';
var KINDS = [['', 'All'], ['Note', 'Notes'], ['Acronym', 'Acronyms'], ['Drill', 'Drill questions']];
function kindOf(x){ return x.k === 'Note' || x.k === 'Acronym' ? x.k : 'Drill'; }""")
    rep("""  var r = search(q), hits = r.hits, doms = {};""",
        """  var r = search(q), all = r.hits, per = {};
  all.forEach(function(h){ var k = kindOf(h.x); per[k] = (per[k] || 0) + 1; });
  if(KIND && !per[KIND]) KIND = '';
  var hits = KIND ? all.filter(function(h){ return kindOf(h.x) === KIND; }) : all, doms = {};""")
    rep("""    (hits.length ? " across " + nd + (nd === 1 ? " domain" : " domains") : "") + " for &ldquo;" + escH(q) + "&rdquo;</p>";""",
        """    (hits.length ? " across " + nd + (nd === 1 ? " domain" : " domains") : "") + " for &ldquo;" + escH(q) + "&rdquo;</p>";
  if(all.length){
    var fr = '<div class="kfilter" role="group" aria-label="Filter results">';
    KINDS.forEach(function(k){
      var n = k[0] ? (per[k[0]] || 0) : all.length;
      fr += '<button type="button" data-kind="' + k[0] + '" aria-pressed="' + (KIND === k[0]) + '"' + (n ? '' : ' disabled') + '>' + k[1] + ' <b>' + n + '</b></button>';
    });
    gRes.innerHTML = fr + '</div>' + gRes.innerHTML;
  }""")
    rep("""gIn.addEventListener("input", runSearch);""",
        """gIn.addEventListener("input", runSearch);
gRes.addEventListener("click", function(e){
  var b = e.target.closest && e.target.closest(".kfilter button"); if(!b || b.disabled) return;
  KIND = b.getAttribute("data-kind"); runSearch();
});""")
    # styles
    rep("""/* ---- mobile polish""", """.kfilter{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 10px;}
.kfilter button{font-family:var(--font-display);font-size:11.5px;border:1px solid var(--border);background:var(--surface);
  color:var(--text-muted);border-radius:999px;padding:5px 11px;cursor:pointer;}
.kfilter button[aria-pressed="true"]{border-color:var(--accent);color:var(--accent);background:var(--surface-2);}
.kfilter button:disabled{opacity:.45;cursor:default;}
.kfilter button b{font-weight:600;font-variant-numeric:tabular-nums;}
.hit-meta .kchip{color:var(--text-muted);border:1px solid var(--border);border-radius:999px;padding:1px 7px;}
.hit-meta .k-acronym{color:var(--hl-blue);border-color:var(--hl-blue);}
.hit-meta .k-flashcard,.hit-meta .k-quiz,.hit-meta .k-scenario{color:var(--hl-pink);border-color:var(--hl-pink);}

/* ---- mobile polish""")
    rep("""placeholder="Search every domain&hellip; e.g. &quot;OCSP&quot;, &quot;watering hole&quot;, &quot;cold site&quot;" autocomplete="off" aria-label="Search all notes">""",
        """placeholder="Search notes, acronyms and drill questions&hellip; e.g. OCSP, watering hole, cold site" autocomplete="off" aria-label="Search all notes, acronyms and drill questions">""")
pathlib.Path(dst).write_text(s, encoding='utf-8')
print(f'{dst}: {len(extra)} extra entries ({len(data["acr"])} acronyms), {len(s)//1024} KB')
