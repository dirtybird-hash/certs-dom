# CompTIA Study Toolkit

Self-contained study tools for CompTIA certifications, one folder per exam.

Open `index.html` in any browser — no build step, no dependencies, no server required. Every page is a single HTML file with its CSS and JavaScript inline. With GitHub Pages enabled, the whole thing works as a static site.

## Certifications

| Folder | Exam | State |
|---|---|---|
| `security-plus/` | Security+ **SY0-701** | Complete — all five domains built and verified against the published objectives |
| — | A+ Core 2 **220-1202** | Material exists outside this repo; not wired in yet |
| — | Network+ **N10-009** | Material exists outside this repo; not wired in yet |
| — | CySA+ **CS0-003** | Not started |

`index.html` at the root is the certification picker and holds the Test Prep Scheduler. Each cert folder holds its own hub plus its tools.

## What each tool does

**Notebook** — browse or search notes by topic. Definitions, comparison tables and gotcha call-outs, filtered by objective, plus a tab collecting every easily-confused pair.

**Match** — a patch-panel matching game. Drag a term across to its definition, or tap one then the other. Timed, with best times saved per objective and round size.

**Drill** — flashcards you mark as known or still learning, multiple-choice questions with explanations, scenario questions in the style of performance-based items, and a progress tab showing accuracy per objective so weak areas surface on their own.

**Acronym Drill** — the exam's full published acronym list, drilled both directions, with a quiz that draws its wrong answers from the same domain so the choices stay plausible.

**Test Prep Scheduler** (on the root hub) — pick the certification (A+ Core 2, Network+, Security+ or CySA+), enter the exam date and the minutes you can give it on weekdays and weekends, and it builds a study breakdown by domain plus a day-by-day checklist: study and drill blocks for every objective, mixed rounds in the middle, a timed practice exam and a light review at the end. For Security+ and CySA+ it reads the accuracy the Drill pages have recorded and puts your weakest objectives first. Each cert keeps its own plan and checkmarks.

## Security+ coverage

All five domains — 100% of the exam by weight.

| Domain | Weight | Notebook | Match | Drill |
|---|---|---|---|---|
| 1.0 General Security Concepts | 12% | 20 topics | 92 pairs | 86 flash / 50 quiz / 15 scenarios |
| 2.0 Threats, Vulnerabilities & Mitigations | 22% | 50 topics | 115 pairs | 98 / 41 / 15 |
| 3.0 Security Architecture | 18% | 37 topics | 143 pairs | 115 / 50 / 15 |
| 4.0 Security Operations | 28% | 48 topics | 194 pairs | 165 / 72 / 15 |
| 5.0 Security Program Management & Oversight | 20% | 24 topics | 111 pairs | 96 / 45 / 15 |

## Notes

Progress in Match, Drill, the Acronym Drill and the Scheduler is stored in your browser's local storage. It stays on the device you used, is not synced anywhere, and clearing site data resets it.

Keys are namespaced per certification (`secplus:domain1drill:v1` and so on), so one exam's Domain 1 never overwrites another's. Because browser storage is per-origin, this cross-tool reading only works on the deployed site, where every page shares one origin — not across separately hosted copies of individual pages.

Pages follow your system light/dark setting and work down to phone width.

## Building

`build/README.md` documents the pipeline: what generates what, the patch library, the validation steps, and how to retarget the whole system at another exam.

## About the content

These are original study notes written against CompTIA's published exam objectives. They are not transcriptions of any course, textbook or lecture, and they do not reproduce exam questions. Where a concept came from coursework, it was read, understood, and then written up independently — the source material itself is not included here.

## Disclaimer

Personal study material. This is **not** official CompTIA content and is not affiliated with, authorized by, or endorsed by CompTIA.

CompTIA, A+, Network+, Security+, CySA+ and the exam codes above are trademarks of CompTIA, Inc. Accuracy is not guaranteed — verify anything you are unsure of against the current official exam objectives before test day.
