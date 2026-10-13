"""Assemble prep-scheduler.html: shared drill stylesheet + scheduler extras + markup + logic."""
import re

BASE = open('/home/claude/build/acr/acr_style.css').read()
# drop the acronym-drill-specific additions, keep the shared drill base
BASE = BASE.split('/* --- Acronym Drill additions --- */')[0]
EXTRA = open('/home/claude/build/acr/prep_style.css').read()
DATA = open('/home/claude/build/acr/prep_data.json').read()

HUB = 'https://claude.ai/artifact/VBQTcEFCBoLm2HbFYQ3MFE'
NB = {1: 'https://claude.ai/artifact/Rsb6YnjU33btaifdZgyFhB',
      2: 'https://claude.ai/artifact/QcBcJKdGD7MVZsMfbdNt1b',
      3: 'https://claude.ai/artifact/HSwrQ2Z2xXpmrQHGrZi8SN',
      4: 'https://claude.ai/artifact/Cfj2uJ53pJKpML2woMP6E8',
      5: 'https://claude.ai/artifact/A4gMbARsZBBK7upETX4cVQ'}
DR = {1: 'https://claude.ai/artifact/V4c6LTwdzLraL6923m1FG2',
      2: 'https://claude.ai/artifact/JLQhDRGVEeYBbUzRaUqgzv',
      3: 'https://claude.ai/artifact/CLSzAzhXsHyydspYA3W4ti',
      4: 'https://claude.ai/artifact/3TDmapWnJANA3HqVMHVvne',
      5: 'https://claude.ai/artifact/Wyhp4zXtxfBbihG4azVnRt'}
MT = {1: 'https://claude.ai/artifact/La2HXLBpgY7jR8m6FdAQzH',
      2: 'https://claude.ai/artifact/PTPN5nTY1X1j54RyTtxG8c',
      3: 'https://claude.ai/artifact/3UNruLDALUMjXckzBuWXxD',
      4: 'https://claude.ai/artifact/JsKxAbsK2oX2YzuqsSidnX',
      5: 'https://claude.ai/artifact/RPuAbmpbnVFFnqAwEwMUKg'}

BODY = """<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@500;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap">

<div class="topbar">
  <div class="topbar-inner">
    <a class="backlink" href="__HUB__"><span class="arr">&larr;</span> Security+ Toolkit</a>
    <div class="brand">
      <h1>Test Prep Scheduler</h1>
      <span class="sub">SY0-701 &middot; plan built from your exam date</span>
    </div>
    <div class="tabs" role="tablist">
      <button class="tab active" data-tab="today" role="tab">Today</button>
      <button class="tab" data-tab="plan" role="tab">Full plan</button>
      <button class="tab" data-tab="ready" role="tab">Readiness</button>
      <button class="tab" data-tab="setup" role="tab">Setup</button>
    </div>
  </div>
</div>

<div class="wrap">

  <!-- TODAY -->
  <section class="panel" id="panel-today">
    <div id="today-empty" class="note">Set your exam date and time on the <strong>Setup</strong> tab and the plan builds itself. Everything stays in this browser.</div>
    <div id="today-live" hidden>
      <div class="count">
        <span class="big" id="cd-days">&mdash;</span>
        <span class="lbl" id="cd-lbl"></span>
        <span class="when" id="cd-when"></span>
      </div>
      <div class="statgrid" id="today-stats"></div>
      <p class="lede" id="today-phase"></p>
      <div id="today-sessions"></div>
      <div class="btnrow">
        <button class="ghost" id="btn-replan">Rebuild the remaining days</button>
      </div>
    </div>
  </section>

  <!-- FULL PLAN -->
  <section class="panel" id="panel-plan" hidden>
    <p class="lede" id="plan-lede">No plan yet &mdash; add your exam date on the Setup tab.</p>
    <div id="plan-days"></div>
  </section>

  <!-- READINESS -->
  <section class="panel" id="panel-ready" hidden>
    <div id="ready-note"></div>
    <p class="lede">Weakest objectives first. Accuracy comes from the quiz rounds you have already answered in each Drill.</p>
    <div class="ready" id="ready-list"></div>
  </section>

  <!-- SETUP -->
  <section class="panel" id="panel-setup" hidden>
    <div class="card">
      <div class="form">
        <div class="field">
          <label for="exam-date">Exam date</label>
          <input type="date" id="exam-date">
        </div>
        <div class="field">
          <label for="exam-time">Exam time</label>
          <input type="time" id="exam-time" value="09:00">
          <span class="hint">Used for the countdown and to decide whether the exam-day session is a morning or an afternoon one.</span>
        </div>
        <div class="row2">
          <div class="field">
            <label for="wd-min">Weekday minutes</label>
            <input type="number" id="wd-min" min="0" max="600" step="15" value="60">
          </div>
          <div class="field">
            <label for="we-min">Weekend minutes</label>
            <input type="number" id="we-min" min="0" max="600" step="15" value="120">
          </div>
        </div>
        <div class="field">
          <span class="hint">The plan fills each day up to the minutes you have, weights the domains by their share of the exam (4.0 is 28%, 2.0 is 22%, 5.0 is 20%, 3.0 is 18%, 1.0 is 12%), and pushes the objectives you score worst on toward the front. Scenarios and the gotcha tables are held back for the last few days.</span>
        </div>
        <div class="btnrow">
          <button class="primary" id="btn-build">Build my plan</button>
          <button class="ghost" id="btn-clear">Clear everything</button>
        </div>
      </div>
    </div>
  </section>

</div>
"""

SCRIPT = """
var DOMAINS = __DATA__;
var NB_URL = __NB__, DR_URL = __DR__, MT_URL = __MT__;
var KEY = "sec701-prep-v1";
var DRILL_KEY = function(d){ return "domain" + d + "drill:v1"; };

/* ---------- storage ---------- */
function load(){
  try { var raw = localStorage.getItem(KEY); return raw ? JSON.parse(raw) : {}; }
  catch(e){ return {}; }
}
function save(){ try { localStorage.setItem(KEY, JSON.stringify(store)); } catch(e){} }
var store = load();
if (!store.done) store.done = {};

/* ---------- drill progress (same origin only) ---------- */
function drillStats(){
  var out = {}, found = false;
  for (var d = 1; d <= 5; d++){
    try {
      var raw = localStorage.getItem(DRILL_KEY(d));
      if (!raw) continue;
      var st = JSON.parse(raw);
      if (st && st.objStats){
        found = true;
        Object.keys(st.objStats).forEach(function(o){
          var v = st.objStats[o];
          if (v && typeof v.t === "number") out[o] = { c: v.c || 0, t: v.t };
        });
      }
    } catch(e){}
  }
  return { stats: out, found: found };
}

/* ---------- helpers ---------- */
function pad(n){ return (n < 10 ? "0" : "") + n; }
function isoOf(dt){ return dt.getFullYear() + "-" + pad(dt.getMonth()+1) + "-" + pad(dt.getDate()); }
function parseISO(s){ var p = String(s).split("-"); return new Date(+p[0], +p[1]-1, +p[2]); }
var DAYNAME = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];
var MONTH = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
function prettyDay(dt){ return DAYNAME[dt.getDay()] + " " + dt.getDate() + " " + MONTH[dt.getMonth()]; }
function isWeekend(dt){ var g = dt.getDay(); return g === 0 || g === 6; }
function hash(s){ var h = 5381, i; for (i = 0; i < s.length; i++) h = ((h * 33) ^ s.charCodeAt(i)) >>> 0; return h.toString(36); }
function esc(s){ return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;"); }

/* every objective, with its content weight and current accuracy */
function objectiveList(){
  var stats = drillStats().stats, list = [];
  Object.keys(DOMAINS).forEach(function(d){
    var dom = DOMAINS[d];
    var totalItems = 0;
    dom.objs.forEach(function(o){ totalItems += o.flash + o.quiz; });
    dom.objs.forEach(function(o){
      var share = totalItems ? (o.flash + o.quiz) / totalItems : 1 / dom.objs.length;
      var st = stats[o.o] || null;
      var acc = (st && st.t >= 4) ? st.c / st.t : null;
      var mult = 1.25;                        /* never drilled: needs a first pass */
      if (acc !== null){
        mult = acc < 0.6 ? 2.0 : acc < 0.75 ? 1.55 : acc < 0.9 ? 1.05 : 0.6;
      }
      list.push({
        d: +d, o: o.o, title: o.t, topics: o.topics,
        flash: o.flash, quiz: o.quiz, scen: o.scen, pairs: o.pairs,
        weight: dom.weight * share, acc: acc, seen: st ? st.t : 0,
        priority: dom.weight * share * mult
      });
    });
  });
  return list;
}

/* ---------- plan building ---------- */
function buildPlan(){
  if (!store.exam) return null;
  var examDate = parseISO(store.exam);
  var today = new Date(); today.setHours(0,0,0,0);
  var days = [];
  var cur = new Date(today);
  while (cur < examDate){ days.push(new Date(cur)); cur.setDate(cur.getDate() + 1); }
  var objs = objectiveList();

  /* phases: coverage, mixed, final */
  var n = days.length;
  var finalDays = n >= 6 ? 3 : n >= 4 ? 2 : n >= 2 ? 1 : 0;
  var coverDays = Math.max(0, Math.ceil((n - finalDays) * 0.55));
  var mixedDays = Math.max(0, n - finalDays - coverDays);

  /* coverage order: highest priority first, so weak and heavy objectives come early */
  var cover = objs.slice().sort(function(a,b){ return b.priority - a.priority; });
  var ci = 0;

  /* mixed rounds: repeat objectives proportionally to priority, weakest most often */
  var mixed = objs.slice().sort(function(a,b){ return b.priority - a.priority; });

  var plan = [];
  days.forEach(function(dt, idx){
    var mins = isWeekend(dt) ? (store.weMin || 0) : (store.wdMin || 0);
    var phase = idx < coverDays ? "coverage" : (idx < coverDays + mixedDays ? "mixed" : "final");
    var sessions = [];
    var left = mins;

    if (mins <= 0){
      plan.push({ iso: isoOf(dt), dt: dt, phase: "rest", mins: 0, sessions: [] });
      return;
    }

    if (phase === "coverage"){
      while (left >= 20 && ci < cover.length){
        var o = cover[ci++];
        var readMin = Math.min(18, Math.max(6, Math.round(o.topics.length * 1.6)));
        var cards = Math.min(o.flash, 24);
        var qs = Math.min(o.quiz, 10);
        var blk = readMin + Math.round(cards * 0.4) + qs;
        if (blk > left && sessions.length) { ci--; break; }
        sessions.push({
          kind: "read", d: o.d, obj: o.o,
          title: "Read " + o.o + " " + o.title,
          detail: o.topics.length + " topics in the Domain " + o.d + " Notebook" +
                  (o.topics.length ? " &mdash; starting at " + link(NB_URL[o.d] + "#" + o.topics[0].id, o.topics[0].title) : ""),
          mins: readMin
        });
        sessions.push({
          kind: "drill", d: o.d, obj: o.o,
          title: "Drill " + o.o + " &mdash; " + cards + " cards, " + qs + " questions",
          detail: "Domain " + o.d + " Drill: filter to " + o.o + ", flashcards then a quiz round. " +
                  link(DR_URL[o.d], "Open the Drill"),
          mins: Math.round(cards * 0.4) + qs
        });
        left = mins - totalMins(sessions);
      }
      if (left >= 12){
        var extra = cover[Math.min(ci, cover.length - 1)];
        sessions.push({
          kind: "match", d: extra.d, obj: extra.o,
          title: "Match round &mdash; Domain " + extra.d,
          detail: "Vocabulary against the clock. " + link(MT_URL[extra.d], "Open Match"),
          mins: 12
        });
      }
    } else if (phase === "mixed"){
      /* Objectives the coverage days never reached (ci still points at them) go first,
         so nothing on the exam goes into the final phase completely untouched. */
      var slots = Math.max(1, Math.floor(mins / 22));
      var picks = [], firstPass = 0;
      while (picks.length < slots && ci < cover.length){ picks.push(cover[ci++]); firstPass++; }
      if (picks.length < slots){
        picks = picks.concat(weightedPicks(mixed, slots - picks.length, idx));
      }
      picks.forEach(function(o, pi){
        var fresh = pi < firstPass;
        sessions.push({
          kind: "quiz", d: o.d, obj: o.o,
          title: (fresh ? "First pass &mdash; " : "Quiz round &mdash; ") + o.o + " " + o.title,
          detail: (fresh
            ? "No reading block fitted before this, so skim the " + o.topics.length +
              " topics in the Domain " + o.d + " Notebook first, then 10 questions. "
            : "10 questions in the Domain " + o.d + " Drill, filtered to " + o.o +
              (o.acc !== null ? " (you are at " + Math.round(o.acc * 100) + "% here)" : " (not drilled yet)") + ". ") +
            link(DR_URL[o.d], "Open the Drill"),
          mins: 18
        });
      });
      if (mins - totalMins(sessions) >= 12){
        var dm = heaviestDomain(picks);
        sessions.push({
          kind: "match", d: dm, obj: null,
          title: "Match round &mdash; Domain " + dm,
          detail: "Fast vocabulary pass. " + link(MT_URL[dm], "Open Match"),
          mins: 12
        });
      }
    } else {
      /* Final phase. Rotate scenarios, gotcha tables and weak-spot rounds across the
         five domains and keep filling until the day's minutes are used, so a long
         weekend day before the exam isn't left half empty. */
      var order = [4, 2, 5, 3, 1];
      var slot = idx - coverDays - mixedDays;
      var weakest = objs.slice().sort(function(a,b){ return b.priority - a.priority; });
      var k = 0, guard = 0;
      while (guard++ < 30){
        var left = mins - totalMins(sessions);
        var dX = order[(slot * 2 + k) % 5];
        var step = k % 3;
        if (step === 0 && left >= 20){
          sessions.push({
            kind: "scen", d: dX, obj: null,
            title: "Scenarios &mdash; Domain " + dX,
            detail: "Work 5 scenario questions, read every explanation. " + link(DR_URL[dX], "Open the Drill"),
            mins: 20
          });
        } else if (step === 1 && left >= 12){
          sessions.push({
            kind: "gotcha", d: dX, obj: null,
            title: "Gotchas &mdash; Domain " + dX,
            detail: "The Gotchas tab collects every compare-and-contrast pair in one table. " +
                    link(NB_URL[dX], "Open the Notebook"),
            mins: 12
          });
        } else if (step === 2 && left >= 12 && weakest.length){
          var weak = weakest[(slot + Math.floor(k / 3)) % weakest.length];
          sessions.push({
            kind: "quiz", d: weak.d, obj: weak.o,
            title: "Weak spot &mdash; " + weak.o,
            detail: "One more quiz round on " + weak.o + " " + weak.title + ". " + link(DR_URL[weak.d], "Open the Drill"),
            mins: 12
          });
        } else if (left < 12){
          break;
        }
        k++;
      }
      /* Long day: say plainly that the last hour is optional. */
      if (totalMins(sessions) >= 150){
        sessions.push({
          kind: "rest", d: null, obj: null,
          title: "Stop when it stops paying",
          detail: "Anything past about two and a half hours of review in one day returns less than sleep does. " +
                  "Tick what you finished and leave the rest &mdash; the plan re-sorts around whatever is still weak.",
          mins: 0
        });
      }
    }

    plan.push({ iso: isoOf(dt), dt: dt, phase: phase, mins: mins, sessions: sessions });
  });

  /* the exam day itself */
  plan.push({ iso: store.exam, dt: examDate, phase: "exam", mins: 0, sessions: [{
    kind: "exam", d: null, obj: null,
    title: "Exam day &mdash; no new material",
    detail: "Skim the five Gotchas tabs if you want something to do, eat properly, and get there early. Cramming new topics today costs more than it returns.",
    mins: 0
  }]});
  return plan;
}

function totalMins(list){ var t = 0; list.forEach(function(s){ t += s.mins; }); return t; }
function link(href, text){ return '<a href="' + href + '" target="_blank" rel="noopener">' + esc(text) + '</a>'; }
function heaviestDomain(picks){
  var best = 4, bw = -1;
  picks.forEach(function(p){ if (p.weight > bw){ bw = p.weight; best = p.d; } });
  return best;
}
/* deterministic weighted sampling without two of the same objective in one day */
function weightedPicks(list, count, seed){
  var pool = list.slice(), out = [], s = seed * 2654435761 % 2147483647;
  function rnd(){ s = (s * 48271) % 2147483647; return s / 2147483647; }
  while (out.length < count && pool.length){
    var total = 0, i;
    for (i = 0; i < pool.length; i++) total += pool[i].priority;
    var r = rnd() * total, acc = 0, hit = pool.length - 1;
    for (i = 0; i < pool.length; i++){ acc += pool[i].priority; if (r <= acc){ hit = i; break; } }
    out.push(pool[hit]);
    pool.splice(hit, 1);
  }
  return out;
}

/* ---------- rendering ---------- */
var plan = null;
function doneKey(iso, s){ return iso + "|" + hash(s.title); }

function render(){
  var hasExam = !!store.exam;
  document.getElementById("today-empty").hidden = hasExam;
  document.getElementById("today-live").hidden = !hasExam;
  if (!hasExam){ document.getElementById("plan-lede").textContent = "No plan yet — add your exam date on the Setup tab."; renderReady(); return; }

  plan = buildPlan();
  renderCountdown();
  renderToday();
  renderPlan();
  renderReady();
}

function renderCountdown(){
  var examDate = parseISO(store.exam);
  var t = (store.time || "09:00").split(":");
  examDate.setHours(+t[0] || 9, +t[1] || 0, 0, 0);
  var now = new Date();
  var ms = examDate - now;
  var days = Math.floor(ms / 86400000);
  var hrs = Math.floor((ms % 86400000) / 3600000);
  var el = document.getElementById("cd-days");
  var lbl = document.getElementById("cd-lbl");
  if (ms <= 0){ el.textContent = "0"; lbl.innerHTML = "Exam time has passed. Good luck &mdash; or set a new date on Setup."; }
  else if (days === 0){ el.textContent = hrs; lbl.innerHTML = "hours to go. Nothing new today."; }
  else { el.textContent = days; lbl.innerHTML = days === 1 ? "day to go" : "days to go"; }
  document.getElementById("cd-when").textContent =
    prettyDay(examDate) + ", " + (store.time || "09:00");
}

function renderToday(){
  var iso = isoOf(new Date());
  var day = null;
  plan.forEach(function(p){ if (p.iso === iso) day = p; });
  var host = document.getElementById("today-sessions");
  var phaseEl = document.getElementById("today-phase");
  host.innerHTML = "";
  if (!day){
    phaseEl.textContent = "Nothing scheduled for today.";
  } else if (!day.sessions.length){
    phaseEl.textContent = "Rest day — you set today's available time to zero.";
  } else {
    phaseEl.innerHTML = phaseLabel(day.phase) + " &middot; " + totalMins(day.sessions) + " minutes planned";
    day.sessions.forEach(function(s){ host.appendChild(sessionEl(day.iso, s)); });
  }
  /* stats */
  var totalS = 0, doneS = 0, totalM = 0;
  plan.forEach(function(p){ p.sessions.forEach(function(s){
    if (p.phase === "exam") return;
    totalS++; totalM += s.mins;
    if (store.done[doneKey(p.iso, s)]) doneS++;
  }); });
  var st = document.getElementById("today-stats");
  st.innerHTML = "";
  [[doneS + " / " + totalS, "sessions done"],
   [Math.round(totalM / 60) + " h", "planned in total"],
   [plan.length - 1 + "", "study days left"]].forEach(function(p){
    var e = document.createElement("div"); e.className = "stat";
    e.innerHTML = '<div class="n">' + p[0] + '</div><div class="l">' + p[1] + '</div>';
    st.appendChild(e);
  });
}

function phaseLabel(p){
  return p === "coverage" ? "<strong>Coverage</strong> — read then drill, weakest and heaviest objectives first"
       : p === "mixed" ? "<strong>Mixed practice</strong> — quiz rounds weighted to your weak spots"
       : p === "final" ? "<strong>Final days</strong> — scenarios and gotcha tables only"
       : p === "exam" ? "<strong>Exam day</strong>"
       : "<strong>Rest day</strong>";
}

function sessionEl(iso, s){
  var wrap = document.createElement("label");
  var k = doneKey(iso, s);
  wrap.className = "sess" + (store.done[k] ? " done" : "");
  var cb = document.createElement("input");
  cb.type = "checkbox"; cb.checked = !!store.done[k];
  cb.addEventListener("change", function(){
    if (cb.checked) store.done[k] = 1; else delete store.done[k];
    save();
    wrap.classList.toggle("done", cb.checked);
    renderToday();
  });
  var body = document.createElement("div");
  body.className = "body";
  var top = document.createElement("div");
  top.className = "stop";
  var title = document.createElement("span");
  title.className = "stitle"; title.innerHTML = s.title;
  top.appendChild(title);
  if (s.d){
    var b = document.createElement("span");
    b.className = "badge badge-d" + s.d;
    b.textContent = "D" + s.d;
    top.appendChild(b);
  }
  if (s.mins){
    var m = document.createElement("span");
    m.className = "mins"; m.textContent = s.mins + " min";
    top.appendChild(m);
  }
  var det = document.createElement("div");
  det.className = "detail"; det.innerHTML = s.detail;
  body.appendChild(top); body.appendChild(det);
  wrap.appendChild(cb); wrap.appendChild(body);
  return wrap;
}

function renderPlan(){
  var host = document.getElementById("plan-days");
  var iso = isoOf(new Date());
  document.getElementById("plan-lede").innerHTML =
    plan.length - 1 + " study days before the exam. The plan rebuilds itself from your latest drill scores every time you open this page, so the later days follow whatever you are still getting wrong.";
  host.innerHTML = "";
  plan.forEach(function(p){
    var div = document.createElement("div");
    var isToday = p.iso === iso;
    var past = p.iso < iso;
    div.className = "day" + (isToday ? " today open" : "") + (past ? " past" : "");
    var doneCount = 0;
    p.sessions.forEach(function(s){ if (store.done[doneKey(p.iso, s)]) doneCount++; });
    var head = document.createElement("button");
    head.type = "button"; head.className = "day-head";
    head.innerHTML = '<span class="d">' + prettyDay(p.dt) + (isToday ? " &middot; today" : "") + '</span>' +
      '<span class="tag">' + (p.phase === "exam" ? "exam" : p.phase) + '</span>' +
      '<span class="load">' + (p.sessions.length ? doneCount + "/" + p.sessions.length + " &middot; " + totalMins(p.sessions) + " min" : "rest") + '</span>' +
      '<span class="chev">&#9656;</span>';
    head.addEventListener("click", function(){ div.classList.toggle("open"); });
    var body = document.createElement("div");
    body.className = "day-body";
    if (!p.sessions.length){
      body.innerHTML = '<p class="lede">No time set for this day.</p>';
    } else {
      p.sessions.forEach(function(s){ body.appendChild(sessionEl(p.iso, s)); });
    }
    div.appendChild(head); div.appendChild(body);
    host.appendChild(div);
  });
}

function renderReady(){
  var ds = drillStats();
  var note = document.getElementById("ready-note");
  note.innerHTML = ds.found
    ? '<div class="note">Reading your saved Drill results from this browser. Answer more quiz questions and these numbers &mdash; and the plan &mdash; move with you.</div>'
    : '<div class="note warn">No Drill results found in this browser yet. Two reasons that happens: you have not answered any quiz questions, or you are on the published-artifact version of the tools, where each page is sandboxed separately. On the GitHub Pages site every page shares one origin, so the scores show up there. Until then the plan weights objectives by exam share and content volume alone.</div>';
  var list = objectiveList().sort(function(a, b){
    /* measured weakest first, then never drilled (heaviest first), then the strong ones */
    if (a.acc !== null && b.acc !== null) return a.acc - b.acc;
    if (a.acc === null && b.acc === null) return b.weight - a.weight;
    return a.acc === null ? 1 : -1;
  });
  var host = document.getElementById("ready-list");
  host.innerHTML = "";
  list.forEach(function(o){
    var row = document.createElement("div");
    row.className = "rrow";
    var pct = o.acc === null ? null : Math.round(o.acc * 100);
    var cls = pct === null ? "" : pct < 60 ? "bad" : pct < 80 ? "mid" : "good";
    row.innerHTML =
      '<span class="oc" style="background:var(--dom-' + o.d + ')">' + o.o + '</span>' +
      '<span class="ot">' + o.title + (o.acc === null ? ' <span style="color:var(--text-muted);font-size:12px;">not drilled</span>' : ' <span style="color:var(--text-muted);font-size:12px;">' + o.seen + ' answered</span>') + '</span>' +
      '<span class="bar"><span class="' + cls + '" style="width:' + (pct === null ? 0 : pct) + '%"></span></span>' +
      '<span class="pc">' + (pct === null ? "&mdash;" : pct + "%") + '</span>';
    host.appendChild(row);
  });
}

/* ---------- setup ---------- */
var dateEl = document.getElementById("exam-date");
var timeEl = document.getElementById("exam-time");
var wdEl = document.getElementById("wd-min");
var weEl = document.getElementById("we-min");
if (store.exam) dateEl.value = store.exam;
if (store.time) timeEl.value = store.time;
if (store.wdMin != null) wdEl.value = store.wdMin;
if (store.weMin != null) weEl.value = store.weMin;

document.getElementById("btn-build").addEventListener("click", function(){
  if (!dateEl.value){ dateEl.focus(); return; }
  store.exam = dateEl.value;
  store.time = timeEl.value || "09:00";
  store.wdMin = Math.max(0, parseInt(wdEl.value, 10) || 0);
  store.weMin = Math.max(0, parseInt(weEl.value, 10) || 0);
  save();
  render();
  selectTab("today");
});
document.getElementById("btn-clear").addEventListener("click", function(){
  store = { done: {} }; save(); dateEl.value = ""; render();
});
document.getElementById("btn-replan").addEventListener("click", function(){ render(); });

/* ---------- tabs ---------- */
var tabs = document.querySelectorAll(".tab");
function selectTab(name){
  tabs.forEach(function(t){ t.classList.toggle("active", t.dataset.tab === name); });
  ["today","plan","ready","setup"].forEach(function(n){
    document.getElementById("panel-" + n).hidden = (n !== name);
  });
}
tabs.forEach(function(t){ t.addEventListener("click", function(){ selectTab(t.dataset.tab); }); });

render();
"""

import json
html = ("<title>Test Prep Scheduler</title>\n<style>" + BASE + EXTRA + "</style>\n"
        + BODY.replace("__HUB__", HUB)
        + "\n<script>\n"
        + SCRIPT.replace("__DATA__", DATA)
                .replace("__NB__", json.dumps(NB))
                .replace("__DR__", json.dumps(DR))
                .replace("__MT__", json.dumps(MT))
        + "\n</script>\n")
open('/home/claude/prep-scheduler.html', 'w').write(html)
print('prep-scheduler.html bytes', len(html))
