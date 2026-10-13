# Build tooling

How the pages in this repo are generated and maintained. Kept here so the toolkit can be
rebuilt — or retargeted at a different exam — without reconstructing the pipeline from scratch.

Python 3, no dependencies beyond the standard library. Node is used only for syntax checks.

## The two kinds of asset

**The pages are the templates.** There is no generator that writes a Notebook, Match or Drill
page from nothing. Building a new domain means copying an existing trio and swapping its data
arrays, objective config, badge classes, storage key and accent tokens. Watch for values that
do not travel with the data — a hardcoded flashcard count in the progress tile caused a bug
exactly once.

Each page holds its content in a JavaScript array near the top:

| Page | Array | Shape |
|---|---|---|
| Notebook | `TOPICS` | `{id, obj, title, html}` plus `GOTCHAS_TABLE` |
| Match | `PAIRS` | `{id, obj, term, def}` |
| Drill | `FLASHCARDS` / `QUIZ` / `SCENARIOS` | quiz `a` is a **zero-based** index into `c` |

**The scripts are the pipeline.** They index, assemble, patch and generate.

## tools/

Run in this order after any notebook edit. Skipping the first one leaves the hub's search
index stale, which is silent and easy to miss.

```
python3 tools/build_index.py    # bakes a search index of every notebook into the hub
python3 tools/build_repo.py     # wraps artifact fragments as standalone pages, rewrites links
python3 tools/strip_guides.py   # removes Study Guide cards; fails loudly if any claude.ai link survives
```

`build_repo.py` holds the artifact-URL-to-filename map. Publishing a new page means adding it
there in three places: `ART_TO_FILE`, `FILES` and `DESC`.

Artifact pages are published as **fragments** — no doctype, head or body; the platform wraps
them at publish time. `build_repo.py` adds a real wrapper for the standalone versions here.
Do not confuse the two forms.

## build/

`lib.py` — the `NB` class, which is the patch pipeline. Three operations against a notebook:

- `append(topic_id, html)` — inserts before that topic's Gotcha blockquote, or at the end of
  its body if it has none.
- `rep(old, new)` — exact string replacement that **asserts exactly one occurrence**. This is
  the safety rail; if a patch would hit zero or two places it fails rather than guessing.
- `gotcha(rows)` — adds rows to the gotcha table.

`apply_tc.py`, `apply_mc.py`, `apply_extras.py`, `depth.py`, `mergeq.py` — thin drivers that
read a JSON patch file and apply it through `NB`. Patch shape:

```json
{"appends": [{"topic": "id", "html": "..."}],
 "reps":    [{"old": "...", "new": "..."}],
 "gotcha_rows": [["term A", "term B", "the distinction"]]}
```

`acr_page.py` + `acr_style.css` + `acr_data.json` — generates the Acronym Drill. The data is a
flat list of `{"a": acronym, "x": expansion, "dm": domain, "o": objective}`. Retargeting to
another exam means replacing `acr_data.json` with that exam's published acronym list.

`prep_page.py` + `prep_style.css` + `prep_data.json` — generates the Test Prep Scheduler.
`prep_data.json` carries per-objective topic lists and card counts, which is how the planner
sizes each block. The planner reads `domainNdrill:v1` from localStorage and reweights the
remaining days by measured accuracy.

## Validation, every time

Two checks, in this order, before publishing anything:

```
# 1. extract each <script> block and syntax-check it
#    a missing IIFE brace silently broke a Drill once, with no visible error
node --check <extracted.js>

# 2. load every page headless and exercise it
#    assert: zero console errors, mobile scrollWidth <= 392, tabs clickable, hub search resolves
```

Counting occurrences in these files needs care: they are effectively single-line, so `grep -c`
counts *lines*, not matches. Use Python `str.count` on whitespace-flattened text.

## Storage keys

Per-viewer, per-origin. Each artifact has its own origin and cannot read another's data; on
this Pages site every page shares one origin, so cross-tool reads work here and only here.
That difference is not cosmetic — the Scheduler's reweighting is inert on the artifact version.

| Tool | Key |
|---|---|
| Drill | `domainNdrill:v1` → `{cardStatus, objStats: {"4.6": {c, t}}}` |
| Match | `domainNmatch:v2` |
| Acronym Drill | `sec701-acr-v1` |
| Scheduler | `sec701-prep-v1` |

## Retargeting to another exam

1. Parse the new objectives PDF into a bullet list; it is the spine for every coverage check.
2. Copy a domain trio per new domain, swap the data arrays, objective config, accent tokens
   and storage key prefix.
3. Replace `acr_data.json` with the new acronym list and `prep_data.json` with the new
   objective/topic map.
4. Update `build_repo.py`'s three maps, rebuild, validate, publish.

Coverage checks compare notebook text against the objective bullets. Expect false negatives
from plural and slash phrasing — CompTIA writes "system/process audit" and "published/documented"
— so verify every reported miss by hand before acting on it.

One lesson worth carrying: coverage completeness is not readiness. Every check here came back
clean while the drills sat unanswered. Build the drills early and use them from the start;
the per-objective accuracy data is the signal that matters.
