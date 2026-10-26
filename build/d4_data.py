"""CySA+ Domain 4 drill content — objectives 4.1 to 4.2.

Original prose written against CompTIA's published CS0-003 objectives
(build/cysa-spine.json). Class decks and transcripts are read for scope
only; no instructor wording or Knowledge Check questions are reproduced,
because the repo is public.

Shapes:
    FLASHCARDS  (objective, front, back)
    QUIZ        (objective, question, [4 choices], answer_index, explanation)
    SCENARIOS   (objective, situation, question, [4 choices], answer_index, explanation)

Recovered 2026-10-25 from the published page (d4.frag.html) after the session that
built it ended without committing its source. drill_page.py regenerates that
page byte for byte from this file, which is the proof the recovery is lossless.
"""

FLASHCARDS = [
 ('4.1',
  'What belongs in a vulnerability report beyond the list of findings?',
  'The affected hosts, a risk score, the recommended mitigation, the priority order, and whether the finding has recurred. A list of CVEs is data; a report tells someone what to do, on which systems, in what order, and whether this is the second time.'),
 ('4.1',
  'Why does recurrence deserve its own place in a report?',
  'Because a vulnerability that returns is a process failure, not a technical one. It means a patch was rolled back, a rebuild used a stale image, or configuration drifted. Fixing it again without asking why it came back guarantees a third occurrence.'),
 ('4.1',
  'What is a compliance report, and how does it differ from a vulnerability report?',
  "A compliance report demonstrates conformance to a standard — PCI DSS, ISO 27001, HIPAA — against that standard's criteria and on its schedule. A vulnerability report describes technical risk. The same scan can feed both, but the audience, format and consequences of failure differ."),
 ('4.1',
  'What makes an action plan more useful than a remediation list?',
  'It names the mechanism, the owner and the timeframe. Configuration change, patching, compensating control, training, or accepting changed business requirements are different kinds of work owned by different people. "Patch these 40 hosts" is a list; an action plan says who does what by when.'),
 ('4.1',
  'When is awareness, education and training the right remediation?',
  'When the vulnerability is in behavior rather than in a system — repeated phishing success, credential sharing, misconfigured permissions set by well-meaning staff. Technical controls should carry as much of the load as possible, but some gaps genuinely close only through training.'),
 ('4.1',
  'How can changing business requirements be a remediation?',
  'Because removing the need removes the risk. If a legacy integration exists for a product line being retired, the cheapest fix is decommissioning rather than patching. Recognizing that is often more valuable than any technical control.'),
 ('4.1',
  'What is an inhibitor to remediation?',
  'Anything that prevents a known fix from being applied — contractual, organizational or technical. They are worth naming explicitly in reporting, because an unexplained open finding looks like negligence while a documented inhibitor is a managed decision.'),
 ('4.1',
  'How do an MOU and an SLA inhibit remediation differently?',
  'An SLA is a binding commitment with defined service levels and usually penalties, so patching that risks breaching it needs formal change. An MOU records a mutual understanding between parties without the same contractual force. Both constrain action; the SLA constrains it harder.'),
 ('4.1',
  'Why do legacy and proprietary systems inhibit remediation?',
  'Legacy systems may have no vendor support, so no patch exists at all. Proprietary systems may forbid modification under their support terms, meaning patching voids support or breaches contract. In both cases the answer is compensating controls and a replacement plan, not repeated escalation.'),
 ('4.1',
  'What do business process interruption and degraded functionality mean as inhibitors?',
  'Applying the fix costs something operationally — downtime during a critical period, or a feature that stops working after the update. Both are legitimate reasons to schedule rather than refuse, and both belong in the report so the trade-off is visible to whoever owns it.'),
 ('4.1',
  'What makes a vulnerability metric a KPI rather than a statistic?',
  'That it measures whether the program is working and drives a decision. "4,000 open findings" is a statistic. "Mean time to remediate critical findings, trending from 21 days to 9" is a KPI, because it shows direction and tells you whether the change you made helped.'),
 ('4.1',
  'Which vulnerability-management metrics are worth reporting regularly?',
  'Trends over time, a top-ten list of the most prevalent or most serious findings, counts of critical vulnerabilities and zero-days, and performance against the SLOs. Trends matter most: a single snapshot cannot distinguish improvement from decline.'),
 ('4.1',
  'Why is a top-ten list useful to a technical audience?',
  'Because remediation effort concentrates. A small number of findings usually account for most of the risk, often one missing patch across many hosts. A top ten converts a four-thousand-line report into the handful of actions that move the number.'),
 ('4.1',
  'Why does stakeholder identification come before writing the report?',
  "Because the audience determines the content. An executive needs exposure, trend and decisions required. A system owner needs their hosts and their deadlines. An auditor needs evidence against criteria. The same findings produce three different documents, and sending the wrong one wastes everybody's time."),
 ('4.2',
  'What is incident declaration, and why does it matter procedurally?',
  'The formal decision that an event is an incident. It matters because declaration starts the clock: it activates the response plan, authorizes the team, triggers notification obligations, and begins the timeline everything else is measured against. An undeclared incident has no owner.'),
 ('4.2',
  'What should drive escalation during an incident?',
  'Criteria defined in advance — severity, scope, asset criticality, data sensitivity, regulatory exposure. Escalation decided case by case under pressure is inconsistent and slow. The plan should make it mechanical enough that a tired analyst at 3 a.m. gets it right.'),
 ('4.2',
  'What does an executive summary in an incident report need to do?',
  'State what happened, what the impact was, whether it is contained, and what decisions are needed — in plain language, with no jargon, in about a paragraph. It is written for someone who will read only that section and may have to act on it in a meeting.'),
 ('4.2',
  'What do the who, what, when, where and why cover in an incident report?',
  'Who was involved and affected, what happened, when it occurred and was detected, where in the environment, and why it was possible. The last is the hardest and the most valuable, because it is the root cause rather than the sequence of events.'),
 ('4.2',
  'Why does an incident report need a timeline as well as a narrative?',
  'Because the narrative explains and the timeline evidences. Dwell time, detection delay and response speed are all visible only as a sequence of timestamps, and regulators and insurers ask for them specifically. It is also where clock synchronization pays off.'),
 ('4.2',
  'What is the difference between impact and scope in reporting?',
  'Scope is reach — which systems, accounts and data were touched. Impact is consequence — downtime, financial loss, regulatory exposure, harm to people. Executives act on impact; responders act on scope. A report that conflates them serves neither.'),
 ('4.2',
  'What role does evidence play in the report?',
  'It supports every claim and makes the findings defensible — log excerpts, hashes, images, chain of custody. Without it the report is assertion, which fails the moment anyone with a legal or regulatory interest asks how you know.'),
 ('4.2',
  'Why must legal be involved early in incident communications?',
  'Because disclosure obligations, privilege, contractual duties and evidence handling all have legal consequences that are difficult to undo. Communications sent before legal review can create liability, waive privilege, or commit the organization to statements later proven wrong.'),
 ('4.2',
  'What is public relations for during an incident, and what is the risk of getting it wrong?',
  'Controlling the external narrative — customers, press, partners. The risk is speaking too early with incomplete facts, then correcting. A retracted statement damages credibility more than a slower, accurate one, which is why PR works from confirmed findings rather than working hypotheses.'),
 ('4.2',
  'What governs regulatory reporting, and why does the deadline matter so much?',
  'The applicable regime — GDPR, HIPAA, PCI DSS, sector rules — each with its own trigger, recipient and deadline, some as short as 72 hours from awareness. Missing a deadline is a separate violation from the breach itself, with its own penalty.'),
 ('4.2',
  'When is law enforcement involved, and what changes once they are?',
  'When a crime has been committed, when the actor is beyond your reach, or when regulation requires it. Once involved, evidence handling becomes stricter, they may ask you to delay remediation to preserve an investigation, and disclosure timing may no longer be entirely yours.'),
 ('4.2',
  'What is mean time to detect, and what does a bad number indicate?',
  'The average elapsed time from an incident beginning to its being detected. A long MTTD means attackers operate undisturbed — dwell time — and it points at monitoring coverage and alerting quality rather than at response capability.'),
 ('4.2',
  'Distinguish mean time to respond from mean time to remediate.',
  'Respond measures detection to the first containment action — how quickly you act. Remediate measures detection to full resolution — how long the organization carried the exposure. A fast response with slow remediation means you stop the bleeding but take weeks to close the wound.'),
 ('4.2',
  'What does alert volume tell you as a metric?',
  'Whether the detection pipeline is sustainable. Rising volume with flat true-positive rates means analysts are being buried in noise, and alert fatigue causes real detections to be missed. It is a leading indicator of degraded detection quality.'),
 ('4.2',
  'Why are incident metrics reported as trends rather than single numbers?',
  'Because a single value has no meaning without direction. MTTD of nine days is bad if it was four last quarter and good if it was thirty. Trends show whether investment is working, which is the question leadership is actually asking.'),
 ('4.2',
  'What separates root cause analysis from lessons learned?',
  'Root cause analysis establishes the condition that permitted the incident. Lessons learned examines how the response itself performed — what worked, what did not, what to change. One is about the attack; the other is about the organization.'),
]

QUIZ = [
 ('4.1',
  'The same vulnerability scan has to inform the board, the server team and a PCI assessor. What does this most require?',
  ['A single comprehensive report circulated to all three', 'Stakeholder identification, producing different reports for different audiences', 'Raising the severity threshold so the report is shorter', 'Delaying reporting until all findings are remediated'],
  1,
  'The audience determines the content: the board needs exposure and decisions, the server team needs their hosts and deadlines, the assessor needs evidence against PCI criteria. One document serving all three serves none of them well.'),
 ('4.1',
  'A critical finding on a proprietary medical device cannot be patched because doing so voids vendor support. How should this appear in reporting?',
  ['As an open critical finding with no further detail', 'As a documented inhibitor to remediation, with compensating controls and a replacement plan', 'Removed from the report until the vendor issues guidance', 'Reclassified to a lower severity to reflect the constraint'],
  1,
  'The risk is unchanged, so lowering severity or omitting it misrepresents exposure. Naming the inhibitor converts an apparently neglected finding into a managed decision, and pairs it with what is actually being done about it.'),
 ('4.1',
  'Which of these is a KPI rather than a statistic?',
  ['4,218 open vulnerabilities across the estate', 'Mean time to remediate critical findings, trending from 21 days to 9 over two quarters', 'A list of all hosts with critical findings', 'The total number of scans performed last month'],
  1,
  'A KPI measures whether the program is working and supports a decision. A count is a snapshot with no direction — it cannot distinguish an improving program with good discovery from a deteriorating one.'),
 ('4.1',
  'The same vulnerability has been remediated three times in six months and keeps returning. What does the report most need to say?',
  ['That the patch should be applied again with higher priority', 'That recurrence indicates a process failure — image, rollback or drift — which needs addressing rather than re-patching', 'That the affected hosts should be isolated', 'That the finding is a false positive'],
  1,
  'Three recurrences means something systematically reintroduces it: a stale gold image, a rollback procedure, or configuration drift. Patching a fourth time without fixing that mechanism guarantees a fifth.'),
 ('4.1',
  'A legacy application must remain for eighteen months while its replacement is built, and it cannot be patched. What is the appropriate reporting position?',
  ['Accept the risk and close the finding', 'Keep it open with documented inhibitors, compensating controls, an owner and the replacement timeline', 'Escalate it weekly until it is patched', 'Transfer the risk through insurance and close it'],
  1,
  "Closing it hides live exposure, and weekly escalation of something already decided wastes everyone's attention. The finding stays open with the constraint, the interim controls and the end date visible, which is what makes it a managed risk."),
 ('4.2',
  'Why does formal incident declaration matter procedurally?',
  ['It satisfies insurance requirements', 'It activates the response plan, authorizes the team and starts the clock on notification obligations', 'It transfers responsibility to management', 'It is required before evidence can be collected'],
  1,
  'Declaration is the hinge: before it, nobody is formally empowered and no obligation timer has started. Several regulatory deadlines run from awareness, which is why the moment of declaration is recorded.'),
 ('4.2',
  'An executive summary in an incident report is best written for which purpose?',
  ['A complete technical account for the security team', 'Someone who reads only that section and may need to make a decision from it', 'Satisfying regulatory evidence requirements', 'Documenting the chain of custody'],
  1,
  'It has to stand alone, in plain language, covering what happened, the impact, whether it is contained and what is needed. Technical detail, evidence and custody belong in the body where the people who need them will look.'),
 ('4.2',
  'Personal data was exposed and GDPR applies. What is the most time-critical obligation?',
  ['Completing the forensic investigation before notifying anyone', 'Notifying the supervisory authority within the regulatory window, which can be as short as 72 hours from awareness', 'Issuing a public statement', 'Contacting law enforcement'],
  1,
  'The notification clock runs from awareness, not from the completion of the investigation, and missing it is a separate violation from the breach. Notification can be made with what is known and supplemented later.'),
 ('4.2',
  'Which pair of metrics best distinguishes how fast you act from how long exposure lasts?',
  ['Alert volume and mean time to detect', 'Mean time to respond and mean time to remediate', 'Mean time to detect and alert volume', 'Incident count and mean time to detect'],
  1,
  'Respond measures detection to first containment — speed of action. Remediate measures detection to full resolution — duration of exposure. A good response time with a poor remediation time is a recognizable and common pattern.'),
 ('4.2',
  'Alert volume has risen 40% while confirmed incidents stayed flat. What does this most likely indicate?',
  ['Detection coverage has improved', 'Analysts are absorbing more noise, raising the risk that real detections are missed', 'The environment is under sustained attack', 'The SIEM is misconfigured and dropping events'],
  1,
  'More alerts producing no more real findings means the signal-to-noise ratio fell. That is the mechanism of alert fatigue, and it is a leading indicator that a genuine detection will be missed.'),
 ('4.2',
  'Law enforcement asks you to delay rebuilding a compromised server to preserve evidence. What does this change?',
  ['Nothing; remediation takes precedence over investigation', 'Remediation timing and disclosure may no longer be entirely your decision, and evidence handling becomes stricter', 'Regulatory deadlines are suspended while they investigate', 'The organization is released from notification obligations'],
  1,
  'Their involvement constrains timing and tightens evidence handling, and compensating controls usually carry the risk meanwhile. It does not suspend regulatory deadlines — those obligations run independently, which is why legal needs to be in the room.'),
 ('4.2',
  'What distinguishes root cause analysis from a lessons-learned review?',
  ['Root cause is technical and lessons learned is managerial', 'Root cause examines the condition that allowed the incident; lessons learned examines how the response performed', 'Root cause is for regulators and lessons learned is internal', 'They are the same activity at different times'],
  1,
  'One asks why the attack was possible; the other asks how well the organization handled it. Both are needed — an incident can have a well-understood root cause and a badly run response, or the reverse.'),
]

SCENARIOS = [
 ('4.1',
  'Your quarterly report lists 4,218 open findings. The CISO says the board meeting is in two days, they will give security eight minutes, and last quarter they left the room unclear whether things were improving or deteriorating.',
  'What should the board material lead with?',
  ['The full findings list, sorted by CVSS score', 'Trend lines against SLOs, the top concentrations of risk, and the specific decisions being asked of them', 'The count of critical findings and the remediation backlog', 'A technical summary of the most severe vulnerability'],
  1,
  'Eight minutes and a prior failure to convey direction both point the same way: the board needs to know whether the program is working and what it must decide. Trends answer the first, top concentrations show where effort should go, and naming the decisions is the only part only they can do. Raw counts and CVSS lists are what left them unclear last time.'),
 ('4.1',
  'A critical finding affects 180 hosts. 140 can be patched in the next maintenance window. 30 run a vendor appliance whose support terms forbid modification. 10 are on an end-of-life platform scheduled for decommissioning in four months.',
  'How should the action plan be structured?',
  ['A single patching task covering all 180 hosts', 'Three tracks — patching, compensating controls under a documented inhibitor, and decommissioning — each with an owner and a date', 'Patch the 140 and record the remaining 40 as accepted risk', 'Escalate all 40 unpatched hosts to executive management'],
  1,
  'The three groups need different mechanisms and different owners, which is exactly the distinction between an action plan and a remediation list. Accepting the risk on 40 hosts hides live exposure, and blanket escalation asks leadership to decide something already determined by vendor terms and a retirement schedule.'),
 ('4.2',
  'At 23:40 an analyst confirms an attacker accessed a database containing customer names, addresses and partial payment card data. The investigation is perhaps 20% complete. The on-call manager wants to notify customers immediately to get ahead of it, and the communications lead is drafting a statement.',
  'What is the correct sequence?',
  ['Notify customers immediately, as transparency limits reputational damage', 'Declare the incident and engage legal first, so disclosure obligations and the content of any statement are established before anything goes out', 'Complete the forensic investigation before any notification', 'Notify the card brands first, then customers, then regulators'],
  1,
  'Statements made at 20% knowledge are routinely wrong and have to be retracted, which does more damage than a short delay. Legal determines which obligations apply, their deadlines and what can safely be said. Waiting for a complete investigation is also wrong — several regulatory clocks run from awareness, not from completion.'),
 ('4.2',
  'Post-incident review of a ransomware event shows: initial access 34 days before detection, detection by a user reporting encrypted files, containment within 90 minutes of detection, and full recovery after 11 days.',
  'Which metric most clearly identifies where to invest?',
  ['Mean time to respond, at 90 minutes', 'Mean time to detect, at 34 days — the attacker operated undisturbed and detection came from a user, not a control', 'Mean time to remediate, at 11 days', 'Alert volume during the incident'],
  1,
  'The response was fast once detection happened, and 11 days of recovery is unremarkable for ransomware. The failure is 34 days of undetected dwell time ending with a human noticing — which points squarely at monitoring coverage and alerting quality rather than at the response team.'),
]

OBJTITLE = {"4.1": "Vulnerability Reporting & Communication", "4.2": "Incident Reporting & Communication"}

# ---------------------------------------------------------------------------
# Added 2026-10-25 after a coverage check against the Day 6 deck: organizational
# governance is a named inhibitor to remediation in objective 4.1 and the drill
# did not teach it. Original prose.
# ---------------------------------------------------------------------------

FLASHCARDS += [
 ('4.1', 'How can organizational governance inhibit remediation?',
  'Through the approval process itself: change advisory boards, required sign-offs, change freezes and policy that routes every production change through review. Each is legitimate, but a fix that waits for the next monthly board meeting has turned a seven-day SLO into a thirty-day one.'),
 ('4.1', 'What is an emergency change, and why does vulnerability management depend on it?',
  'An expedited path through change management for urgent fixes, with approval from a smaller authority and review afterwards. Without one, governance quietly overrides every short remediation deadline. Pre-approved standard changes, such as routine monthly patching, do the same job for predictable work.'),
]

QUIZ += [
 ('4.1', 'A critical patch is tested and ready, but the change advisory board meets monthly and the next meeting is three weeks away. Which inhibitor is this, and what is the best response?',
  ['A legacy system; replace the server', 'Organizational governance; use the emergency change process', 'An SLA; renegotiate it with the customer', 'Business process interruption; schedule the patch for the quarterly window'],
  1, 'The fix is ready and nothing technical blocks it; only the approval cycle does. That is governance. Emergency change exists for this case: approve it now through the expedited path and let the board review it afterwards.'),
]

# ---------------------------------------------------------------------------
# GENERAL KNOWLEDGE (added 2026-10-25): governance frameworks and metrics the
# Day 6 deck stresses that are NOT on the CS0-003 objectives (4.1 names trends,
# top 10, critical vulnerabilities and zero-days, and SLOs). Badged,
# toggleable, scored separately from objective accuracy.
# ---------------------------------------------------------------------------

GK_FLASHCARDS = [
 ('4.1', 'What is COBIT?',
  "ISACA's framework for governing and managing enterprise IT: it links IT processes and controls to business objectives and is widely used by auditors. When a report has to show that controls exist and work, COBIT is often the yardstick."),
 ('4.1', 'What is ITIL, and why does it matter to remediation?',
  'A body of IT service management practice: incident, problem, change enablement, configuration management and more. Patching runs through ITIL-style change management, which is why standard and emergency changes decide how fast a fix can ship.'),
 ('4.1', 'Why does Sarbanes-Oxley reach into security?',
  'SOX requires US public companies to keep reliable internal controls over financial reporting. Auditors therefore test IT general controls on systems that touch the financials: access reviews, change management and segregation of duties. A vulnerability on those systems can become an audit finding.'),
 ('4.1', 'Name four vulnerability-management metrics beyond the objective list.',
  'Vulnerability density: findings per asset (or per thousand lines of code).\nRemediation rate: share of findings closed in the period.\nFalse positive rate: share of reported findings that were not real.\nPatch deployment rate: share of targeted systems actually patched.\nTrends in these show whether the program is improving.'),
 ('4.1', 'What is "vulnerability overload", and how do teams cope?',
  'More findings than the team can ever fix, so the backlog grows faster than remediation. Teams cope by prioritizing on exploitability and asset value, fixing root causes that clear many findings at once (one missing patch across a fleet), and agreeing on risk acceptance for the long tail.'),
]

GK_QUIZ = [
 ('4.1', 'A team closes 120 of 400 open findings this quarter. What is the remediation rate?',
  ['12%', '30%', '33%', '70%'],
  1, '120 ÷ 400 = 0.30, so 30%. Track it as a trend: one quarter shows activity, several show whether the backlog is shrinking.'),
 ('4.1', 'Which framework is primarily about governing IT so that it supports business goals and can be audited?',
  ['ITIL', 'COBIT', 'NIST CSF', 'OWASP ASVS'],
  1, 'COBIT is the governance and control framework. ITIL describes service management practice, NIST CSF organizes security outcomes, and OWASP ASVS is an application security verification standard.'),
]
