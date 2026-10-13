"""Assemble acronym-drill.html from the shared drill stylesheet plus this page's markup and logic."""
import json

STYLE = open('/home/claude/build/acr/acr_style.css').read()
DATA = open('/home/claude/build/acr/acr_data.json').read()
HUB = 'https://claude.ai/artifact/VBQTcEFCBoLm2HbFYQ3MFE'

BODY = """<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@500;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap">

<div class="topbar">
  <div class="topbar-inner">
    <a class="backlink" href="__HUB__"><span class="arr">&larr;</span> Security+ Toolkit</a>
    <div class="brand">
      <h1>Acronym Drill</h1>
      <span class="sub">SY0-701 &middot; 333 official acronyms &middot; all five domains</span>
    </div>
    <div class="tabs" role="tablist">
      <button class="tab active" data-tab="flash" role="tab">Flashcards</button>
      <button class="tab" data-tab="quiz" role="tab">Quiz</button>
      <button class="tab" data-tab="browse" role="tab">Browse</button>
      <button class="tab" data-tab="progress" role="tab">Progress</button>
    </div>
  </div>
</div>

<div class="wrap">

  <!-- FLASHCARDS -->
  <section class="panel" id="panel-flash">
    <p class="lede">Every acronym CompTIA publishes for SY0-701. Pick a direction &mdash; the exam asks both ways &mdash; then click a card to flip it and mark whether you knew it.</p>
    <div class="dirrow" id="flash-dir"></div>
    <div class="chiprow" id="flash-filters"></div>
    <div class="card" style="gap:14px;display:flex;flex-direction:column;">
      <div class="deck-meta">
        <span id="flash-badge"></span>
        <span id="flash-pos">1 / 333</span>
      </div>
      <div class="flip-outer">
        <div class="flip-card" id="flip-card">
          <div class="flip-inner">
            <div class="flip-face front">
              <div class="flip-term" id="flash-term"></div>
              <div class="flip-hint">tap to reveal</div>
            </div>
            <div class="flip-face back">
              <div class="flip-def" id="flash-def"></div>
              <div class="flip-hint">tap to flip back</div>
            </div>
          </div>
        </div>
      </div>
      <div class="markrow">
        <button class="ghost mark-learning" id="btn-learning">Still learning</button>
        <button class="ghost mark-know" id="btn-know">Got it</button>
      </div>
      <div class="deckctl">
        <button class="ghost" id="btn-prev">&larr; Prev</button>
        <button class="ghost" id="btn-shuffle">Shuffle</button>
        <button class="ghost" id="btn-next">Next &rarr;</button>
      </div>
    </div>
  </section>

  <!-- QUIZ -->
  <section class="panel" id="panel-quiz" hidden>
    <p class="lede">Ten a round, four choices, drawn from the domains you pick. Wrong answers come from the same domain, so the near misses are the ones you would actually confuse.</p>
    <div class="dirrow" id="quiz-dir"></div>
    <div class="chiprow" id="quiz-filters"></div>
    <div class="card" id="quiz-start-card">
      <button class="primary" id="quiz-start">Start round</button>
    </div>
    <div class="card" id="quiz-run-card" hidden>
      <div class="qmeta">
        <span id="quiz-badge"></span>
        <span id="quiz-pos"></span>
      </div>
      <div class="qtext" id="quiz-q"></div>
      <div id="quiz-opts"></div>
      <div class="explain" id="quiz-explain" hidden></div>
      <div style="margin-top:14px;display:flex;justify-content:flex-end;">
        <button class="primary" id="quiz-next" disabled>Next</button>
      </div>
    </div>
    <div class="card roundend" id="quiz-end-card" hidden>
      <h2>Round complete</h2>
      <div class="score" id="quiz-score"></div>
      <p class="lede" id="quiz-score-note"></p>
      <button class="primary" id="quiz-again">Run another round</button>
    </div>
  </section>

  <!-- BROWSE -->
  <section class="panel" id="panel-browse" hidden>
    <p class="lede">The whole list, searchable by acronym or by meaning. Click any row to mark it known. The domain shown is where that acronym is taught in the notebooks.</p>
    <div class="searchrow">
      <input id="browse-q" type="search" placeholder="Search SAE, forward secrecy, 802.1X&hellip;" aria-label="Search acronyms">
    </div>
    <div class="chiprow" id="browse-filters" style="margin-bottom:12px;"></div>
    <div id="browse-count" class="lede"></div>
    <div class="alist" id="browse-list"></div>
  </section>

  <!-- PROGRESS -->
  <section class="panel" id="panel-progress" hidden>
    <p class="lede">What you have marked as known, by domain. This lives in your browser only.</p>
    <div class="statgrid" id="prog-stats"></div>
    <div class="card" style="margin-top:14px;">
      <button class="ghost" id="btn-reset">Reset progress</button>
    </div>
  </section>

</div>
"""

SCRIPT = """
var ACR = __DATA__;
var DOMNAME = {1:"General Security Concepts",2:"Threats & Vulnerabilities",3:"Security Architecture",4:"Security Operations",5:"Program Management"};
var KEY = "sec701-acr-v1";

function loadState(){
  try { var raw = localStorage.getItem(KEY); return raw ? JSON.parse(raw) : {}; }
  catch(e){ return {}; }
}
function saveState(){
  try { localStorage.setItem(KEY, JSON.stringify(known)); } catch(e){}
}
var known = loadState();

var state = { flashDir:"a2x", quizDir:"mix", flashDoms:new Set(), quizDoms:new Set(), browseDoms:new Set() };

function badge(item){
  var s = document.createElement("span");
  s.className = "badge badge-d" + (item.dm || 0);
  s.textContent = item.o ? item.o : ("Domain " + item.dm);
  return s;
}
function pool(doms){
  if (!doms.size) return ACR.slice();
  return ACR.filter(function(x){ return doms.has(x.dm); });
}
function shuffle(a){
  for (var i=a.length-1;i>0;i--){ var j=Math.floor(Math.random()*(i+1)); var t=a[i]; a[i]=a[j]; a[j]=t; }
  return a;
}
function domChips(host, set, onchange){
  host.innerHTML = "";
  var defs = [{v:0,l:"All domains"},{v:1,l:"1.0"},{v:2,l:"2.0"},{v:3,l:"3.0"},{v:4,l:"4.0"},{v:5,l:"5.0"}];
  defs.forEach(function(d){
    var b = document.createElement("button");
    b.className = "chip" + ((d.v===0 && !set.size) || set.has(d.v) ? " on" : "");
    b.textContent = d.l;
    b.addEventListener("click", function(){
      if (d.v === 0) { set.clear(); }
      else if (set.has(d.v)) { set.delete(d.v); }
      else { set.add(d.v); }
      domChips(host, set, onchange);
      onchange();
    });
    host.appendChild(b);
  });
}
function dirChips(host, current, onchange){
  host.innerHTML = "";
  var defs = [{v:"a2x",l:"Acronym &rarr; meaning"},{v:"x2a",l:"Meaning &rarr; acronym"},{v:"mix",l:"Mixed"}];
  defs.forEach(function(d){
    var b = document.createElement("button");
    b.className = "chip" + (d.v === current() ? " on" : "");
    b.innerHTML = d.l;
    b.addEventListener("click", function(){ onchange(d.v); });
    host.appendChild(b);
  });
}

/* ---------- Flashcards ---------- */
var deck = [], di = 0, flipped = false;
var flipCard = document.getElementById("flip-card");
function buildDeck(){
  deck = shuffle(pool(state.flashDoms));
  di = 0; renderCard();
}
function renderCard(){
  if (!deck.length) return;
  var it = deck[di];
  var showAcr = state.flashDir === "a2x" || (state.flashDir === "mix" && (di % 2 === 0));
  var termEl = document.getElementById("flash-term");
  termEl.textContent = showAcr ? it.a : it.x;
  termEl.className = "flip-term" + (showAcr ? "" : " small");
  document.getElementById("flash-def").textContent = showAcr ? it.x : it.a;
  var b = document.getElementById("flash-badge");
  b.innerHTML = ""; b.appendChild(badge(it));
  if (known[it.a]) { var k = document.createElement("span"); k.className = "badge"; k.style.background = "var(--correct)"; k.style.marginLeft = "6px"; k.textContent = "known"; b.appendChild(k); }
  document.getElementById("flash-pos").textContent = (di+1) + " / " + deck.length;
  flipped = false; flipCard.classList.remove("flipped");
}
flipCard.addEventListener("click", function(){ flipped = !flipped; flipCard.classList.toggle("flipped", flipped); });
document.getElementById("btn-next").addEventListener("click", function(){ di = (di+1) % deck.length; renderCard(); });
document.getElementById("btn-prev").addEventListener("click", function(){ di = (di-1+deck.length) % deck.length; renderCard(); });
document.getElementById("btn-shuffle").addEventListener("click", buildDeck);
document.getElementById("btn-know").addEventListener("click", function(){
  known[deck[di].a] = 1; saveState(); di = (di+1) % deck.length; renderCard(); renderProgress();
});
document.getElementById("btn-learning").addEventListener("click", function(){
  delete known[deck[di].a]; saveState(); di = (di+1) % deck.length; renderCard(); renderProgress();
});

/* ---------- Quiz ---------- */
var round = [], qi = 0, score = 0, answered = false;
function makeQuestion(item, all){
  var askAcr = state.quizDir === "a2x" || (state.quizDir === "mix" && Math.random() < 0.5);
  var sameDom = all.filter(function(x){ return x.dm === item.dm && x.a !== item.a; });
  var bank = sameDom.length >= 3 ? sameDom : ACR.filter(function(x){ return x.a !== item.a; });
  var wrong = shuffle(bank.slice()).slice(0,3);
  var choices = shuffle([item].concat(wrong));
  return {
    item: item,
    askAcr: askAcr,
    q: askAcr ? ("What does " + item.a + " stand for?") : ("Which acronym is " + item.x + "?"),
    choices: choices.map(function(c){ return askAcr ? c.x : c.a; }),
    answer: choices.indexOf(item)
  };
}
function startRound(){
  var p = pool(state.quizDoms);
  round = shuffle(p.slice()).slice(0, Math.min(10, p.length)).map(function(it){ return makeQuestion(it, p); });
  qi = 0; score = 0;
  document.getElementById("quiz-start-card").hidden = true;
  document.getElementById("quiz-end-card").hidden = true;
  document.getElementById("quiz-run-card").hidden = false;
  renderQuestion();
}
function renderQuestion(){
  answered = false;
  var q = round[qi];
  var b = document.getElementById("quiz-badge");
  b.innerHTML = ""; b.appendChild(badge(q.item));
  document.getElementById("quiz-pos").textContent = (qi+1) + " / " + round.length;
  document.getElementById("quiz-q").textContent = q.q;
  var opts = document.getElementById("quiz-opts");
  opts.innerHTML = "";
  q.choices.forEach(function(text, i){
    var btn = document.createElement("button");
    btn.className = "opt";
    btn.textContent = text;
    btn.addEventListener("click", function(){ answer(i, btn); });
    opts.appendChild(btn);
  });
  var ex = document.getElementById("quiz-explain");
  ex.hidden = true; ex.textContent = "";
  document.getElementById("quiz-next").disabled = true;
}
function answer(i, btn){
  if (answered) return;
  answered = true;
  var q = round[qi];
  var kids = document.getElementById("quiz-opts").children;
  for (var k=0;k<kids.length;k++){
    kids[k].disabled = true;
    if (k === q.answer) kids[k].classList.add("correct");
  }
  if (i === q.answer){ score++; known[q.item.a] = 1; saveState(); }
  else { btn.classList.add("incorrect"); delete known[q.item.a]; saveState(); }
  var ex = document.getElementById("quiz-explain");
  ex.textContent = q.item.a + " is " + q.item.x + ". Taught in Domain " + q.item.dm + " (" + DOMNAME[q.item.dm] + ")" + (q.item.o ? ", objective " + q.item.o : "") + ".";
  ex.hidden = false;
  document.getElementById("quiz-next").disabled = false;
  renderProgress();
}
document.getElementById("quiz-next").addEventListener("click", function(){
  qi++;
  if (qi >= round.length){
    document.getElementById("quiz-run-card").hidden = true;
    document.getElementById("quiz-end-card").hidden = false;
    document.getElementById("quiz-score").textContent = score + " / " + round.length;
    var pct = Math.round(score / round.length * 100);
    document.getElementById("quiz-score-note").textContent =
      pct === 100 ? "Clean round. Take a domain you have not drilled yet." :
      pct >= 80 ? "Solid. The misses are marked as still learning in your progress." :
      "Worth a pass through the flashcards for this domain before the next round.";
  } else { renderQuestion(); }
});
document.getElementById("quiz-start").addEventListener("click", startRound);
document.getElementById("quiz-again").addEventListener("click", startRound);

/* ---------- Browse ---------- */
function renderBrowse(){
  var q = document.getElementById("browse-q").value.trim().toLowerCase();
  var list = pool(state.browseDoms).filter(function(x){
    if (!q) return true;
    return x.a.toLowerCase().indexOf(q) >= 0 || x.x.toLowerCase().indexOf(q) >= 0;
  });
  list.sort(function(a,b){ return a.a.localeCompare(b.a); });
  var host = document.getElementById("browse-list");
  host.innerHTML = "";
  document.getElementById("browse-count").textContent =
    list.length + (list.length === 1 ? " acronym" : " acronyms") + (q ? " matching " + q : "");
  if (!list.length){
    var e = document.createElement("div");
    e.className = "emptynote";
    e.textContent = "No match. Try part of the expansion instead, or clear the domain filter.";
    host.appendChild(e);
    return;
  }
  list.forEach(function(it){
    var row = document.createElement("div");
    row.className = "arow" + (known[it.a] ? " known" : "");
    var ac = document.createElement("div"); ac.className = "ac"; ac.textContent = it.a;
    var ax = document.createElement("div"); ax.className = "ax"; ax.textContent = it.x;
    var ao = document.createElement("div"); ao.className = "ao"; ao.textContent = it.o ? it.o : ("D" + it.dm);
    row.appendChild(ac); row.appendChild(ax); row.appendChild(ao);
    row.addEventListener("click", function(){
      if (known[it.a]) delete known[it.a]; else known[it.a] = 1;
      saveState(); row.classList.toggle("known"); renderProgress();
    });
    host.appendChild(row);
  });
}
document.getElementById("browse-q").addEventListener("input", renderBrowse);

/* ---------- Progress ---------- */
function renderProgress(){
  var host = document.getElementById("prog-stats");
  host.innerHTML = "";
  var rows = [{d:0,l:"All acronyms"}];
  [1,2,3,4,5].forEach(function(d){ rows.push({d:d,l:"Domain " + d + ".0"}); });
  rows.forEach(function(r){
    var set = r.d === 0 ? ACR : ACR.filter(function(x){ return x.dm === r.d; });
    var n = set.filter(function(x){ return known[x.a]; }).length;
    var pct = set.length ? Math.round(n / set.length * 100) : 0;
    var el = document.createElement("div");
    el.className = "stat";
    var num = document.createElement("div"); num.className = "n"; num.textContent = n + " / " + set.length;
    var lab = document.createElement("div"); lab.className = "l"; lab.textContent = r.l;
    var meter = document.createElement("div"); meter.className = "meter";
    var fill = document.createElement("span"); fill.style.width = pct + "%";
    meter.appendChild(fill);
    el.appendChild(num); el.appendChild(lab); el.appendChild(meter);
    host.appendChild(el);
  });
}
document.getElementById("btn-reset").addEventListener("click", function(){
  known = {}; saveState(); renderProgress(); renderBrowse(); renderCard();
});

/* ---------- Tabs ---------- */
var tabs = document.querySelectorAll(".tab");
tabs.forEach(function(t){
  t.addEventListener("click", function(){
    tabs.forEach(function(x){ x.classList.remove("active"); });
    t.classList.add("active");
    ["flash","quiz","browse","progress"].forEach(function(name){
      document.getElementById("panel-" + name).hidden = (name !== t.dataset.tab);
    });
  });
});

/* ---------- Init ---------- */
function paintFlashDir(){
  dirChips(document.getElementById("flash-dir"), function(){ return state.flashDir; }, function(v){
    state.flashDir = v; paintFlashDir(); renderCard();
  });
}
function paintQuizDir(){
  dirChips(document.getElementById("quiz-dir"), function(){ return state.quizDir; }, function(v){
    state.quizDir = v; paintQuizDir();
  });
}
paintFlashDir();
paintQuizDir();
domChips(document.getElementById("flash-filters"), state.flashDoms, buildDeck);
domChips(document.getElementById("quiz-filters"), state.quizDoms, function(){});
domChips(document.getElementById("browse-filters"), state.browseDoms, renderBrowse);
buildDeck();
renderBrowse();
renderProgress();
"""

html = ("<title>Security+ Acronym Drill</title>\n<style>" + STYLE + "</style>\n"
        + BODY.replace("__HUB__", HUB)
        + "\n<script>\n" + SCRIPT.replace("__DATA__", DATA) + "\n</script>\n")
open('/home/claude/acronym-drill.html', 'w').write(html)
print('acronym-drill.html bytes', len(html))
