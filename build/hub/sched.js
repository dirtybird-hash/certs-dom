/* Test Prep Scheduler. One plan per certification, stored under that cert's own prefix
   (cysa:prep:v1, secplus:prep:v1, netplus:prep:v1, aplus:prep:v1), so switching the
   dropdown never touches another cert's checkmarks. The plan is stored once it is built,
   so the checklist stays put; it is rebuilt only when the date or minutes change or when
   "Rebuild from today" is pressed. */
(function(){
var CERTS = __SCHED_DATA__;
var LINKS = __SCHED_LINKS__;
var ORDER = ["aplus", "netplus", "secplus", "cysa"];
var DEFAULT_CERT = "cysa";
var SEL_KEY = "certhub:prep-cert:v1";

function keyOf(c){ return LINKS[c].prefix + ":prep:v1"; }
function lsGet(k){ try { var r = localStorage.getItem(k); return r ? JSON.parse(r) : null; } catch(e){ return null; } }
function lsSet(k, v){ try { localStorage.setItem(k, JSON.stringify(v)); } catch(e){} }
function lsDel(k){ try { localStorage.removeItem(k); } catch(e){} }

/* ---------- dates ---------- */
function pad(n){ return (n < 10 ? "0" : "") + n; }
function isoOf(dt){ return dt.getFullYear() + "-" + pad(dt.getMonth() + 1) + "-" + pad(dt.getDate()); }
function parseISO(s){ var p = String(s).split("-"); return new Date(+p[0], +p[1] - 1, +p[2]); }
function todayDate(){ var t = new Date(); t.setHours(0, 0, 0, 0); return t; }
var DAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
var MONS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
function pretty(dt){ return DAYS[dt.getDay()] + " " + MONS[dt.getMonth()] + " " + dt.getDate(); }
function isWeekend(dt){ var g = dt.getDay(); return g === 0 || g === 6; }
function esc(s){ return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;"); }
function link(href, text){ return '<a href="' + href + '" target="_blank" rel="noopener">' + esc(text) + '</a>'; }
function r5(n){ return Math.max(5, Math.round(n / 5) * 5); }
function clamp(n, a, b){ return Math.max(a, Math.min(b, n)); }

/* ---------- drill accuracy (same origin only: the Pages site, not the artifacts) ---------- */
function drillStats(c){
  var L = LINKS[c], out = {}, found = false;
  if (!L.drillKey) return { stats: out, found: false, supported: false };
  CERTS[c].domains.forEach(function(dm){
    var st = lsGet(L.drillKey.replace("{d}", dm.n));
    if (st && st.objStats){
      Object.keys(st.objStats).forEach(function(o){
        var v = st.objStats[o];
        if (v && typeof v.t === "number" && v.t > 0){ out[o] = { c: v.c || 0, t: v.t }; found = true; }
      });
    }
  });
  return { stats: out, found: found, supported: true };
}

function objectives(c){
  var stats = drillStats(c).stats, list = [];
  CERTS[c].domains.forEach(function(dm){
    dm.objs.forEach(function(o){
      var s = stats[o.o], acc = (s && s.t >= 4) ? s.c / s.t : null;
      var mult = acc === null ? 1.25 : acc < 0.6 ? 2.0 : acc < 0.75 ? 1.55 : acc < 0.9 ? 1.05 : 0.6;
      var share = dm.w / dm.objs.length;
      list.push({ d: dm.n, o: o.o, t: o.t, share: share, acc: acc, pri: share * mult });
    });
  });
  return list;
}

/* ---------- plan building ---------- */
function buildPlan(c, cfg, keepToday){
  var today = todayDate(), tISO = isoOf(today);
  var exam = parseISO(cfg.exam);
  var days = [], cur = new Date(today);
  while (cur < exam){
    var cap = isWeekend(cur) ? cfg.we : cfg.wd;
    days.push({ iso: isoOf(cur), cap: cap, phase: cap > 0 ? "" : "rest", tasks: [], used: 0 });
    cur.setDate(cur.getDate() + 1);
  }
  var n = days.length;
  var finalN = n >= 10 ? 3 : n >= 6 ? 2 : n >= 3 ? 1 : 0;
  var rem = n - finalN;
  var coverN = rem <= 3 ? rem : Math.ceil(rem * 0.6);
  days.forEach(function(d, i){
    if (d.phase === "rest") return;
    d.phase = i < coverN ? "coverage" : i < rem ? "mixed" : "final";
  });

  var objs = objectives(c).sort(function(a, b){ return b.pri - a.pri; });
  var done = cfg.done || {};
  var placed = {};

  /* Tasks already ticked today stay on today, exactly as they were. */
  if (n && keepToday){
    keepToday.forEach(function(t){
      if (done[t.id] === tISO){ days[0].tasks.push(t); days[0].used += t.mins; placed[t.id] = 1; }
    });
  }
  function skip(id){ return placed[id] || (done[id] && done[id] !== tISO); }

  /* Coverage: every objective gets a study block and a drill block, sized by its share
     of the coverage minutes, weakest and heaviest first. */
  var budget = 0;
  days.forEach(function(d){ if (d.phase === "coverage") budget += d.cap; });
  if (!budget) days.forEach(function(d){ budget += d.cap * 0.5; });
  var sumPri = 0; objs.forEach(function(o){ sumPri += o.pri; });
  var queue = [];
  objs.forEach(function(o){
    var per = clamp(r5(budget * o.pri / (sumPri || 1)), 20, 90);
    var sm = Math.max(10, r5(per * 0.55)), dm = Math.max(10, per - sm);
    queue.push({ id: "s|" + o.o, kind: "study", d: o.d, o: o.o, mins: sm, acc: o.acc });
    queue.push({ id: "q|" + o.o, kind: "drill", d: o.d, o: o.o, mins: dm, acc: o.acc });
  });
  var di = 0, overflow = {};
  queue.forEach(function(t){
    if (skip(t.id)) return;
    while (di < n && (days[di].cap <= 0 || (days[di].used > 0 && days[di].used + t.mins > days[di].cap))) di++;
    if (di >= n){ overflow[t.o] = 1; return; }
    days[di].tasks.push(t); days[di].used += t.mins;
  });

  /* Mixed: whatever room is left goes to mixed quizzes and weak-spot rounds. */
  var domOrder = CERTS[c].domains.slice().sort(function(a, b){ return b.w - a.w; });
  var weakRot = 0, mixRot = 0;
  function weakTask(d, k){
    var o = objs[weakRot++ % objs.length];
    return { id: "w|" + d.iso + "|" + k, kind: "weak", d: o.d, o: o.o, mins: 20, acc: o.acc };
  }
  function fill(d, allowMix){
    var k = 0;
    while (d.cap - d.used >= 15 && k < 12){
      var t;
      if (allowMix && k % 2 === 0){
        var dm = domOrder[mixRot++ % domOrder.length];
        t = { id: "m|" + d.iso + "|" + k, kind: "mix", d: dm.n, o: null, mins: Math.min(25, d.cap - d.used) };
      } else {
        t = weakTask(d, k); t.mins = Math.min(20, d.cap - d.used);
      }
      k++;
      if (skip(t.id)) continue;
      d.tasks.push(t); d.used += t.mins;
    }
  }
  days.forEach(function(d){ if (d.phase === "mixed") fill(d, true); });

  /* Final days: a timed practice exam, the review of its misses, then a light last day. */
  var finals = days.filter(function(d){ return d.phase === "final"; });
  finals.forEach(function(d, f){
    var last = f === finals.length - 1;
    function add(t){ if (!skip(t.id)){ d.tasks.push(t); d.used += t.mins; } }
    if (last){
      add({ id: "lt|" + d.iso, kind: "light", d: null, o: null, mins: Math.min(40, Math.max(15, d.cap - d.used)) });
      add({ id: "lg|" + d.iso, kind: "logistics", d: null, o: null, mins: 10 });
    } else if (f === 0){
      add({ id: "pe|" + d.iso, kind: "exam-sim", d: null, o: null, mins: Math.max(30, Math.min(90, d.cap - d.used)) });
      if (d.cap - d.used >= 20) add({ id: "rv|" + d.iso, kind: "review", d: null, o: null, mins: Math.min(30, d.cap - d.used) });
      fill(d, false);
    } else {
      if (LINKS[c].extra) add({ id: "x|" + d.iso, kind: "extra", d: null, o: null, mins: 25 });
      fill(d, false);
    }
  });

  days.forEach(function(d){ delete d.used; });
  days.push({ iso: cfg.exam, cap: 0, phase: "exam", tasks: [
    { id: "e|" + cfg.exam + "|id", kind: "exam-id", d: null, o: null, mins: 0 },
    { id: "e|" + cfg.exam + "|go", kind: "exam-go", d: null, o: null, mins: 0 }
  ]});
  return { start: tISO, exam: cfg.exam, wd: cfg.wd, we: cfg.we, days: days, overflow: Object.keys(overflow) };
}

/* ---------- task text ---------- */
function objTitle(c, o){
  var hit = null;
  CERTS[c].domains.forEach(function(dm){ dm.objs.forEach(function(x){ if (x.o === o) hit = x.t; }); });
  return hit || "";
}
function domName(c, d){
  var hit = "";
  CERTS[c].domains.forEach(function(dm){ if (dm.n === d) hit = dm.name; });
  return hit;
}
function titleOf(c, t){
  switch (t.kind){
    case "study": return "Study " + t.o + " · " + objTitle(c, t.o);
    case "drill": return "Drill " + t.o;
    case "mix": return "Mixed quiz · Domain " + t.d + " " + domName(c, t.d);
    case "weak": return "Weak spot · " + t.o;
    case "exam-sim": return "Timed practice exam · all domains";
    case "review": return "Review every missed question";
    case "extra": return LINKS[c].extra.title;
    case "light": return "Light review";
    case "logistics": return "Exam logistics check";
    case "exam-id": return "Bring ID and arrive early";
    case "exam-go": return CERTS[c].name + " exam — no new material today";
  }
  return "";
}
function detailOf(c, t){
  var L = LINKS[c];
  var accTxt = t.acc === null || t.acc === undefined ? "not drilled yet" : "you were at " + Math.round(t.acc * 100) + "% when this plan was built";
  switch (t.kind){
    case "study":
      if (L.notebook) return "Read the " + t.o + " topics in the " + link(L.notebook[t.d] || L.notebook["*"], L.nbLabel.replace("{d}", t.d)) + ".";
      if (L.guide) return "Work through section " + t.o + " in the " + link(L.guide, "Network+ study guide") + ".";
      return "Review " + t.o + " in your Core 2 study guide and class notes (StudyMaterials › Core 2 A+).";
    case "drill":
      if (L.drill) return link(L.drill[t.d], "Domain " + t.d + " Drill") + ": filter to " + t.o + ", flashcards first, then a quiz round.";
      if (L.guide) return "Recall cards and practice questions for " + t.o + " in the " + link(L.guide, "Network+ guide") + ".";
      return "From memory, write out the key terms and steps for " + t.o + ", then check them against your notes.";
    case "mix":
      if (L.drill) return "A quiz round in the " + link(L.drill[t.d], "Domain " + t.d + " Drill") + " with every objective mixed in.";
      if (L.guide) return "A mixed quiz round in the " + link(L.guide, "Network+ guide") + ", Domain " + t.d + " sections.";
      return "Practice questions covering all of Domain " + t.d + ".";
    case "weak":
      return "Another round on " + t.o + " " + esc(objTitle(c, t.o)) + " (" + accTxt + ")." +
        (L.drill ? " " + link(L.drill[t.d], "Open the Drill") : L.guide ? " " + link(L.guide, "Open the guide") : "");
    case "exam-sim":
      return L.simNote || "A full-length practice exam under exam timing. Don’t pause to look anything up.";
    case "review":
      return "Go back through every miss and write one line on why the right answer is right.";
    case "extra":
      return L.extra.detail;
    case "light":
      return (L.lightNote || "Acronyms and look-alike terms only.") + " Stop early and sleep.";
    case "logistics":
      return "Confirm the time, the test center or online check-in, and that the name on your ID matches your registration.";
    case "exam-id":
      return "Arrive 15 minutes early, or start online check-in 30 minutes before the start time.";
    case "exam-go":
      var cfg = state(c);
      return "Exam at " + esc(cfg.time || "09:00") + ". Eat properly beforehand. Cramming new topics today costs more than it returns.";
  }
  return "";
}

/* ---------- state ---------- */
var sel = ORDER.indexOf(lsGet(SEL_KEY)) === -1 ? DEFAULT_CERT : lsGet(SEL_KEY);
var cache = {};
function state(c){
  if (!cache[c]){
    var s = lsGet(keyOf(c)) || {};
    if (!s.done) s.done = {};
    if (s.wd == null) s.wd = 60;
    if (s.we == null) s.we = 120;
    if (!s.time) s.time = "09:00";
    cache[c] = s;
  }
  return cache[c];
}
function persist(c){ lsSet(keyOf(c), cache[c]); }

function rebuild(c){
  var s = state(c);
  if (!s.exam){ s.plan = null; persist(c); return; }
  var keep = [];
  if (s.plan){
    var tISO = isoOf(todayDate());
    s.plan.days.forEach(function(d){ d.tasks.forEach(function(t){ if (s.done[t.id] === tISO) keep.push(t); }); });
  }
  s.plan = parseISO(s.exam) > todayDate() || s.exam === isoOf(todayDate()) ? buildPlan(c, s, keep) : null;
  persist(c);
}

/* ---------- elements ---------- */
var $ = function(id){ return document.getElementById(id); };
var root = $("scheduler");
var certEl = $("s-cert"), dateEl = $("s-date"), timeEl = $("s-time"), wdEl = $("s-wd"), weEl = $("s-we");

ORDER.forEach(function(c){
  var o = document.createElement("option");
  o.value = c; o.textContent = CERTS[c].name + " — " + CERTS[c].code;
  certEl.appendChild(o);
});

function loadForm(){
  var s = state(sel);
  certEl.value = sel;
  dateEl.value = s.exam || "";
  timeEl.value = s.time || "09:00";
  wdEl.value = s.wd; weEl.value = s.we;
  root.style.setProperty("--sa", "var(" + LINKS[sel].accent + ")");
  var pr = LINKS[sel].presets || [];
  $("s-presets-row").hidden = !pr.length;
  var host = $("s-presets"); host.innerHTML = "";
  pr.forEach(function(p){
    var b = document.createElement("button");
    b.type = "button"; b.className = "preset"; b.textContent = p.label;
    b.addEventListener("click", function(){ dateEl.value = p.date; if (p.time) timeEl.value = p.time; onSettings(true); });
    host.appendChild(b);
  });
}

function onSettings(dateChanged){
  var s = state(sel);
  var wd = Math.max(0, Math.min(600, parseInt(wdEl.value, 10) || 0));
  var we = Math.max(0, Math.min(600, parseInt(weEl.value, 10) || 0));
  var changed = dateChanged || s.exam !== (dateEl.value || undefined) || s.wd !== wd || s.we !== we;
  s.exam = dateEl.value || undefined;
  s.time = timeEl.value || "09:00";
  s.wd = wd; s.we = we;
  if (changed) rebuild(sel); else persist(sel);
  render();
}

/* ---------- rendering ---------- */
function taskEl(t){
  var s = state(sel);
  var lab = document.createElement("label");
  lab.className = "task" + (s.done[t.id] ? " done" : "");
  var cb = document.createElement("input");
  cb.type = "checkbox"; cb.checked = !!s.done[t.id];
  cb.addEventListener("change", function(){
    if (cb.checked) s.done[t.id] = isoOf(todayDate()); else delete s.done[t.id];
    persist(sel);
    render();
  });
  var body = document.createElement("div"); body.className = "tb";
  body.innerHTML = '<div class="tt"><span class="t">' + esc(titleOf(sel, t)) + '</span>' +
    (t.d ? '<span class="badge">D' + esc(t.d) + '</span>' : '') +
    (t.mins ? '<span class="mins">' + t.mins + ' min</span>' : '') + '</div>' +
    '<div class="td">' + detailOf(sel, t) + '</div>';
  /* a click on a link inside the label should open the link, not toggle the box */
  body.addEventListener("click", function(ev){ if (ev.target.closest("a")) ev.stopPropagation(); });
  lab.appendChild(cb); lab.appendChild(body);
  return lab;
}

var PHASE = { coverage: "learn", mixed: "mixed", "final": "final", rest: "rest", exam: "exam" };

function render(){
  var s = state(sel);
  var tISO = isoOf(todayDate());
  var plan = s.plan;
  var passed = s.exam && s.exam < tISO;
  $("s-empty").hidden = !!plan;
  $("s-live").hidden = !plan;
  $("s-empty").textContent = passed
    ? "That exam date has passed. Enter a new one to build a fresh plan."
    : "Enter an exam date and the study breakdown appears here.";
  if (!plan) return;

  /* totals */
  var total = 0, doneN = 0, leftMin = 0, studyDays = 0, pastOpen = 0;
  var domMin = {};
  plan.days.forEach(function(d){
    if (d.iso >= tISO && d.phase !== "rest" && d.phase !== "exam") studyDays++;
    d.tasks.forEach(function(t){
      total++;
      if (s.done[t.id]) doneN++;
      else {
        leftMin += t.mins;
        if (d.iso < tISO) pastOpen++;
      }
      if (t.d) domMin[t.d] = (domMin[t.d] || 0) + t.mins;
    });
  });
  var exam = parseISO(s.exam), tm = (s.time || "09:00").split(":");
  exam.setHours(+tm[0] || 0, +tm[1] || 0, 0, 0);
  var ms = exam - new Date();
  var daysTo = Math.max(0, Math.ceil((parseISO(s.exam) - todayDate()) / 86400000));
  var stats = [
    [daysTo === 0 ? "Today" : String(daysTo), daysTo === 1 ? "day to the exam" : daysTo === 0 ? "exam day, " + s.time + (ms <= 0 ? " (started)" : "") : "days to the exam"],
    [String(studyDays), studyDays === 1 ? "study day left" : "study days left"],
    [(Math.round(leftMin / 6) / 10) + " h", "still to study"],
    [doneN + " / " + total, "tasks checked off"]
  ];
  $("s-stats").innerHTML = stats.map(function(p){
    return '<div class="sstat"><div class="n">' + esc(p[0]) + '</div><div class="l">' + esc(p[1]) + '</div></div>';
  }).join("");
  $("s-bar").style.width = (total ? Math.round(doneN / total * 100) : 0) + "%";

  /* warnings */
  var w = [];
  if (pastOpen) w.push(pastOpen + (pastOpen === 1 ? " task" : " tasks") + " from earlier days aren’t checked off. " +
    '<button type="button" class="sbtn" data-act="rebuild">Reschedule them from today</button>');
  if (!s.wd && !s.we && plan.days.length > 1) w.push("Weekday and weekend minutes are both zero, so there is no study time to plan. Set the minutes above.");
  else if (plan.overflow.length) w.push(plan.overflow.length + " objective" + (plan.overflow.length === 1 ? "" : "s") +
    " (" + esc(plan.overflow.join(", ")) + ") didn’t fit in the minutes you set. Raise the daily minutes, or they only come up again as weak-spot rounds.");
  $("s-warn").innerHTML = w.map(function(x){ return '<div class="swarn">' + x + '</div>'; }).join("");

  /* breakdown */
  var ds = drillStats(sel), domAcc = {};
  Object.keys(ds.stats).forEach(function(o){
    var d = o.split(".")[0], v = ds.stats[o];
    if (!domAcc[d]) domAcc[d] = { c: 0, t: 0 };
    domAcc[d].c += v.c; domAcc[d].t += v.t;
  });
  var rows = '<tr><th>Domain</th><th class="num">Weight</th><th class="num hide-sm">Objectives</th><th class="num">Planned</th><th class="num">Accuracy</th></tr>';
  var sumMin = 0;
  CERTS[sel].domains.forEach(function(dm){
    var m = domMin[dm.n] || 0; sumMin += m;
    var a = domAcc[dm.n], cell;
    if (!ds.supported) cell = '<span class="muted">—</span>';
    else if (!a || !a.t) cell = '<span class="muted">not drilled</span>';
    else { var p = Math.round(a.c / a.t * 100); cell = '<span class="' + (p < 60 ? "acc-bad" : p < 80 ? "acc-mid" : "acc-good") + '">' + p + '%</span>'; }
    rows += '<tr><td>' + esc(dm.n) + '.0 ' + esc(dm.name) + '</td><td class="num">' + dm.w + '%</td><td class="num hide-sm">' +
      dm.objs.length + '</td><td class="num">' + (Math.round(m / 6) / 10) + ' h</td><td class="num">' + cell + '</td></tr>';
  });
  $("s-brk").innerHTML = rows;

  /* today */
  var todayDay = null;
  plan.days.forEach(function(d){ if (d.iso === tISO) todayDay = d; });
  var th = $("s-today"); th.innerHTML = "";
  $("s-today-h").textContent = "Today · " + pretty(todayDate());
  if (!todayDay) th.innerHTML = '<div class="rest">Nothing on the plan for today. Press “Rebuild from today” to start the plan here.</div>';
  else if (!todayDay.tasks.length) th.innerHTML = '<div class="rest">' + (todayDay.phase === "rest" ? "Rest day — you set today’s minutes to zero." : "Today’s list is clear.") + '</div>';
  else todayDay.tasks.forEach(function(t){ th.appendChild(taskEl(t)); });

  /* full checklist */
  var host = $("s-days"); host.innerHTML = "";
  plan.days.forEach(function(d){
    var box = document.createElement("div");
    var isT = d.iso === tISO;
    /* Today's tasks are already in the Today box, so its day starts collapsed here. */
    box.className = "sday" + (isT ? " is-today" : "") + (d.iso < tISO ? " past" : "");
    var dn = 0, mins = 0;
    d.tasks.forEach(function(t){ if (s.done[t.id]) dn++; mins += t.mins; });
    var head = document.createElement("button");
    head.type = "button"; head.className = "dhead";
    head.setAttribute("aria-expanded", "false");
    head.innerHTML = '<span class="chev" aria-hidden="true">&#9656;</span><span class="dn">' + pretty(parseISO(d.iso)) + (isT ? " · today" : "") + '</span>' +
      '<span class="ph">' + PHASE[d.phase] + '</span>' +
      '<span class="dl' + (d.tasks.length && dn === d.tasks.length ? " full" : "") + '">' +
      (d.tasks.length ? dn + "/" + d.tasks.length + (mins ? " · " + mins + " min" : "") : "rest") + '</span>';
    head.addEventListener("click", function(){
      var open = box.classList.toggle("open");
      head.setAttribute("aria-expanded", open ? "true" : "false");
    });
    var body = document.createElement("div"); body.className = "dbody";
    if (!d.tasks.length) body.innerHTML = '<div class="task"><div class="tb"><div class="td">No study time set for this day.</div></div></div>';
    d.tasks.forEach(function(t){ body.appendChild(taskEl(t)); });
    box.appendChild(head); box.appendChild(body);
    host.appendChild(box);
  });

  /* note */
  var note = "Built " + pretty(parseISO(plan.start)) + ". Learn days pair reading with drilling, heaviest and weakest objectives first; mixed days rotate quiz rounds; the last days hold a timed practice exam and a light final review. ";
  if (sel === "aplus") note += "A+ Core 2 tools aren’t wired into this toolkit yet, so tasks point at your Core 2 study guide and class notes. Note that guide numbers its topics its own way; the objectives here follow CompTIA’s 220-1202 list.";
  else if (sel === "netplus") note += "The Network+ guide keeps its own progress, which this page doesn’t read, so objectives are ordered by exam weight alone.";
  else if (ds.found) note += "Objective order uses the Drill accuracy saved in this browser; rebuild after a few more quiz rounds and the order follows your weak spots.";
  else note += "No Drill results were found in this browser, so objectives are ordered by exam weight. On the GitHub Pages site this page shares storage with the Drills; on the claude.ai version each page is sandboxed, so scores can’t be read there.";
  $("s-note").textContent = note;
}

/* ---------- events ---------- */
certEl.addEventListener("change", function(){
  sel = certEl.value; lsSet(SEL_KEY, sel);
  loadForm();
  var s = state(sel);
  if (s.exam && !s.plan) rebuild(sel);
  render();
});
dateEl.addEventListener("change", function(){ onSettings(true); });
timeEl.addEventListener("change", function(){ onSettings(false); });
wdEl.addEventListener("change", function(){ onSettings(false); });
weEl.addEventListener("change", function(){ onSettings(false); });
$("s-rebuild").addEventListener("click", function(){ rebuild(sel); render(); });
$("s-warn").addEventListener("click", function(ev){
  if (ev.target.getAttribute && ev.target.getAttribute("data-act") === "rebuild"){ rebuild(sel); render(); }
});
/* Two-step clear: sandboxed artifact frames can block confirm(), which would make a
   confirm-guarded button silently do nothing. */
var clearBtn = $("s-clear"), clearArmed = null;
function disarm(){ clearArmed = null; clearBtn.textContent = "Clear this cert’s plan"; }
clearBtn.addEventListener("click", function(){
  if (!clearArmed){
    clearBtn.textContent = "Click again to clear the " + CERTS[sel].name + " plan";
    clearArmed = setTimeout(disarm, 4000);
    return;
  }
  clearTimeout(clearArmed); disarm();
  lsDel(keyOf(sel)); delete cache[sel];
  loadForm(); render();
});

loadForm();
if (state(sel).exam && !state(sel).plan) rebuild(sel);
render();
})();
