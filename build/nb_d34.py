# CySA+ Notebook, Domains 3 and 4. Original prose against CS0-003.
T = "<blockquote><span class=\"tag\">Exam trap</span>{}</blockquote>"

D3 = [
# ---------------------------------------------------------------- 3.1
dict(id="kill-chain", o="3.1", t="Cyber Kill Chain", q="kill chain", h="""
<p>Lockheed Martin&rsquo;s seven stages of an intrusion, in order:</p>
<div class="tblwrap"><table><tr><th>#</th><th>Stage</th><th>Attacker does</th><th>Defender can</th></tr>
<tr><td>1</td><td>Reconnaissance</td><td>Researches targets: staff, tech, exposed services</td><td>Limit public info, watch for scans</td></tr>
<tr><td>2</td><td>Weaponization</td><td>Pairs an exploit with a payload (malicious document)</td><td>Little visibility; threat intel</td></tr>
<tr><td>3</td><td>Delivery</td><td>Sends it: email, web, USB</td><td>Email filtering, web proxy, awareness</td></tr>
<tr><td>4</td><td>Exploitation</td><td>Triggers the vulnerability</td><td>Patching, exploit protection</td></tr>
<tr><td>5</td><td>Installation</td><td>Installs malware or persistence</td><td>EDR, application allow-listing</td></tr>
<tr><td>6</td><td>Command and Control</td><td>Establishes the remote channel</td><td>Egress filtering, DNS/proxy blocking</td></tr>
<tr><td>7</td><td>Actions on Objectives</td><td>Steals, encrypts, destroys</td><td>DLP, segmentation, backups</td></tr></table></div>
<p>Break any link and the chain fails, so the earlier you stop it, the less damage. Criticism: it is linear and perimeter-focused, and handles insiders and lateral movement poorly.</p>
""" + T.format("Weaponization happens on the attacker&rsquo;s side before anything touches you. Building the malicious file is weaponization; emailing it is delivery.")),

dict(id="diamond", o="3.1", t="Diamond Model of Intrusion Analysis", q="diamond", h="""
<p>Every intrusion event has four core features, drawn as the corners of a diamond:</p>
<ul><li><strong>Adversary</strong>: who is attacking.</li>
<li><strong>Capability</strong>: the tools and techniques used (malware, exploit).</li>
<li><strong>Infrastructure</strong>: what they used to deliver and control it (IPs, domains, email accounts).</li>
<li><strong>Victim</strong>: who or what was targeted.</li></ul>
<p>Edges connect them: an adversary uses a capability over infrastructure against a victim. The value is <strong>pivoting</strong>: from one known corner (a C2 domain) you discover others (other victims of that infrastructure, the adversary behind it). Meta-features include timestamp, phase, result, direction, methodology and resources; the social-political and technology axes describe the adversary-victim relationship and how capability meets infrastructure.</p>
""" + T.format("A question about analyzing relationships between attacker, tools, infrastructure and target, or pivoting from one to find the others, is the Diamond Model, not the Kill Chain.")),

dict(id="attack", o="3.1", t="MITRE ATT&CK", q="att&ck", h="""
<p>A free, continually updated knowledge base of real-world adversary behavior. Structure:</p>
<ul><li><strong>Tactics</strong> (14 in Enterprise, the &ldquo;why&rdquo;): Reconnaissance, Resource Development, Initial Access, Execution, Persistence, Privilege Escalation, Defense Evasion, Credential Access, Discovery, Lateral Movement, Collection, Command and Control, Exfiltration, Impact.</li>
<li><strong>Techniques and sub-techniques</strong> (the &ldquo;how&rdquo;), with IDs such as T1059 (Command and Scripting Interpreter) and T1059.001 (PowerShell).</li>
<li><strong>Groups, software, mitigations and detections</strong> linked to techniques.</li></ul>
<p>Uses: map detections to find gaps (ATT&amp;CK Navigator heat maps), describe incidents in a common language, plan adversary emulation. Matrices exist for Enterprise, Mobile and ICS.</p>
""" + T.format("ATT&amp;CK is not a sequence. Unlike the Kill Chain, attackers can use tactics in any order and repeat them.")),

dict(id="testing-methods", o="3.1", t="OSSTMM and the OWASP Testing Guide", q="osstmm", h="""
<p>Both are testing methodologies, not attack models:</p>
<ul><li><strong>OSSTMM</strong> (Open Source Security Testing Methodology Manual, from ISECOM): a peer-reviewed method for measuring operational security across channels (human, physical, wireless, telecommunications, data networks), with metrics for attack surface. Scientific and measurement-focused.</li>
<li><strong>OWASP Testing Guide</strong> (WSTG): a detailed method for testing web applications, organized by area (information gathering, configuration, identity, authentication, authorization, session management, input validation, error handling, cryptography, business logic, client-side).</li></ul>
""" + T.format("If the scope is a web application, the OWASP Testing Guide. If it is the organization&rsquo;s overall operational security, including people and physical, OSSTMM.")),

# ---------------------------------------------------------------- 3.2
dict(id="ir-lifecycle", o="3.2", t="The incident response life cycle", q="containment", h="""
<p>NIST SP 800-61 describes four phases, which CS0-003 follows:</p>
<ol><li><strong>Preparation</strong></li>
<li><strong>Detection and analysis</strong></li>
<li><strong>Containment, eradication and recovery</strong></li>
<li><strong>Post-incident activity</strong></li></ol>
<p>It loops: detection can send you back to containment as scope grows, and lessons learned feed the next round of preparation. (Some courses use a six-step version: preparation, identification, containment, eradication, recovery, lessons learned. Same content, split differently.) NIST published Revision 3 of SP 800-61 in April 2025, reorganized around the CSF 2.0 functions. CS0-003 was written against Revision 2, so answer with the four phases above.</p>
<p><strong>Event vs incident</strong>: an event is any observable occurrence; an incident is an event that violates or threatens security policy. All incidents are events; most events are not incidents.</p>
"""),

dict(id="evidence", o="3.2", t="Evidence: chain of custody, integrity, preservation, legal hold", q="chain of custody", h="""
<ul><li><strong>Chain of custody</strong>: a record of every person who handled evidence, when, why, and what they did, from collection to court. A gap can make the evidence inadmissible.</li>
<li><strong>Validating data integrity</strong>: hash the original and the copy (SHA-256) at acquisition and again before analysis. Matching hashes prove nothing changed. Use write blockers when imaging drives.</li>
<li><strong>Preservation</strong>: work on forensic copies, never the original; store originals securely; collect in <strong>order of volatility</strong>, most volatile first.</li>
<li><strong>Legal hold</strong>: a directive (often from legal counsel, when litigation is reasonably anticipated) to suspend normal deletion and retention schedules for relevant data. Applies to email, logs, backups and personal devices in scope.</li></ul>
<p><strong>Order of volatility</strong> (most to least): CPU registers and cache &rarr; memory (RAM), routing and ARP tables, process list &rarr; temporary file systems &rarr; disk &rarr; remote logs and monitoring data &rarr; physical configuration and network topology &rarr; archival media and backups.</p>
""" + T.format("Capture memory before you shut down or reimage. Pulling the power loses running processes, network connections and decryption keys that live only in RAM.")),

dict(id="cer", o="3.2", t="Containment, eradication and recovery", q="isolation", h="""
<p><strong>Scope</strong> (how many systems, accounts and data sets are involved) and <strong>impact</strong> (what the business loses) decide how aggressively you contain.</p>
<div class="tblwrap"><table><tr><th>Step</th><th>Options</th></tr>
<tr><td>Containment</td><td><strong>Isolation</strong> (EDR network containment, move to a quarantine VLAN, disable switch port), <strong>segmentation</strong>, disabling compromised accounts, blocking IOCs at firewall and DNS, removing the system from the network entirely</td></tr>
<tr><td>Eradication</td><td>Remove malware and persistence, close the entry point, reset credentials (including service accounts and, after domain compromise, KRBTGT twice), <strong>remediation</strong> of the root vulnerability</td></tr>
<tr><td>Recovery</td><td><strong>Re-imaging</strong> from a known-good image (more reliable than cleaning), restoring data from clean backups, patching and hardening before reconnecting, heightened monitoring afterward</td></tr></table></div>
<p><strong>Compensating controls</strong> fill gaps while a permanent fix waits, such as WAF rules for an unpatched app or extra monitoring on a system that can&rsquo;t be rebuilt yet.</p>
<p>Containment can tip off the attacker. If they might destroy data or move faster, sometimes you watch briefly (in a sandboxed segment) to learn scope before cutting them off. Decide that with management and legal.</p>
""" + T.format("Re-imaging is preferred over cleaning because you can never be sure cleaning removed every persistence mechanism. Restore data, not system binaries, from backups taken before the compromise.")),

dict(id="detection-analysis", o="3.2", t="Detection and analysis: IoCs and log analysis", q="ioc", h="""
<p>Detection sources: SIEM alerts, EDR, IDS/IPS, antivirus, FIM, third-party notifications, users reporting something odd.</p>
<p>Analysis steps: validate the alert (true or false positive), correlate across sources to build a timeline, determine scope, classify severity (functional impact, information impact, recoverability), then decide whether it&rsquo;s an incident and escalate.</p>
<p>Useful log sources: Windows Security log (4624 logon, 4625 failed logon, 4672 special privileges, 4688 process creation, 4720 account created, 4732 added to local group, 1102 audit log cleared), Linux <code>auth.log</code>/<code>secure</code>, web server access logs, firewall and proxy logs, DNS logs, cloud audit trails (AWS CloudTrail, Azure Activity Log).</p>
""" + T.format("Event ID 1102 (audit log cleared) is itself an indicator. Legitimate admins rarely clear the Security log.")),

# ---------------------------------------------------------------- 3.3
dict(id="preparation", o="3.3", t="Preparation: plans, playbooks, tools, tabletops, training", q="playbook", h="""
<ul><li><strong>Incident response plan</strong>: the governing document. Scope, authority, team roles and contacts, severity definitions, communication and escalation paths, reporting requirements.</li>
<li><strong>Playbooks</strong>: step-by-step procedures for a specific incident type (phishing, ransomware, lost laptop). They make response consistent and are often automated in SOAR.</li>
<li><strong>Tools</strong>: a jump kit ready in advance, with forensic laptop, write blockers, clean media, imaging and analysis software, cables, chain-of-custody forms, contact lists.</li>
<li><strong>Tabletop exercise</strong>: the team talks through a scenario in a meeting, without touching systems, to find gaps in the plan. Cheapest exercise type. Others: walkthroughs, simulations, full-scale exercises.</li>
<li><strong>Training</strong>: technical training for responders and awareness training for staff, who are often the first detectors.</li>
<li><strong>BC/DR</strong>: business continuity keeps critical functions running during disruption; disaster recovery restores IT. The <strong>BIA</strong> sets priorities; RTO (how fast) and RPO (how much data loss is tolerable) set targets.</li></ul>
""" + T.format("A plan is the overall document; a playbook is the per-scenario procedure. &ldquo;Step-by-step actions for a ransomware outbreak&rdquo; is a playbook.")),

dict(id="post-incident", o="3.3", t="Post-incident: forensics, root cause, lessons learned", q="lessons learned", h="""
<ul><li><strong>Forensic analysis</strong>: detailed examination of preserved evidence to reconstruct exactly what happened, often after recovery so it doesn&rsquo;t slow restoration.</li>
<li><strong>Root cause analysis</strong>: find the underlying cause, not the symptom. The phishing email was the trigger; the root cause might be no MFA plus users with local admin rights. Techniques: the five whys, fishbone diagrams.</li>
<li><strong>Lessons learned</strong>: a meeting soon after the incident (NIST suggests within several days) with everyone involved, blameless, covering what happened, what went well, what didn&rsquo;t, and what to change. Outputs update the IR plan, playbooks, controls and training. Changes to the plan go through change control.</li>
<li>Also: an incident summary report, retaining evidence per policy and legal holds, generating new IOCs and detections from what you learned.</li></ul>
"""),
]

D4 = [
# ---------------------------------------------------------------- 4.1
dict(id="vm-reporting", o="4.1", t="Vulnerability reporting and compliance reports", q="report", h="""
<p>A vulnerability management report should state, for each finding or group:</p>
<ul><li>the <strong>vulnerability</strong> (name, CVE, description)</li>
<li><strong>affected hosts</strong></li>
<li><strong>risk score</strong> (CVSS adjusted for context)</li>
<li><strong>mitigation</strong> (patch, configuration change, compensating control)</li>
<li><strong>recurrence</strong>: has it come back after being fixed? Recurrence points to a process failure such as a golden image that was never updated</li>
<li><strong>prioritization</strong>: what to do first and by when</li></ul>
<p>Tailor it to the reader: executives want risk trends and business impact; system owners want host lists and exact fixes. <strong>Compliance reports</strong> show status against a specific requirement (PCI DSS passing scans, HIPAA controls) for auditors and regulators.</p>
"""),

dict(id="action-plans", o="4.1", t="Action plans", q="action plan", h="""
<div class="tblwrap"><table><tr><th>Action</th><th>When it fits</th></tr>
<tr><td><strong>Configuration management</strong></td><td>The issue is a setting or drift from baseline; fix the baseline and enforce it</td></tr>
<tr><td><strong>Patching</strong></td><td>A vendor fix exists</td></tr>
<tr><td><strong>Compensating controls</strong></td><td>No patch, or patching is blocked; reduce risk another way</td></tr>
<tr><td><strong>Awareness, education and training</strong></td><td>People cause or could prevent the issue (admins misconfiguring, developers repeating the same flaw)</td></tr>
<tr><td><strong>Changing business requirements</strong></td><td>The business process itself creates the risk; change the requirement (retire a feature, stop storing data)</td></tr></table></div>
"""),

dict(id="inhibitors", o="4.1", t="Inhibitors to remediation", q="inhibitor", h="""
<ul><li><strong>MOU</strong> (memorandum of understanding): a less formal agreement between parties that may commit you to availability or limit changes you can make to shared systems.</li>
<li><strong>SLA</strong> (service-level agreement): contractual uptime promises that make downtime for patching costly or require advance notice.</li>
<li><strong>Organizational governance</strong>: change approval boards and sign-off chains slow fixes down.</li>
<li><strong>Business process interruption</strong>: the fix needs downtime the business can&rsquo;t accept right now (month-end close, peak season).</li>
<li><strong>Degrading functionality</strong>: the patch or hardening breaks a feature people rely on.</li>
<li><strong>Legacy systems</strong>: out of support, no patches available at all.</li>
<li><strong>Proprietary systems</strong>: only the vendor may change them; self-patching voids support or certification (medical devices, ICS).</li></ul>
<p>The usual answer to an inhibitor is a compensating control plus a documented exception and review date, not ignoring the finding.</p>
""" + T.format("An SLA is a contract with measurable obligations; an MOU is a statement of intent between parties, usually not legally binding. Both can block a patch window.")),

dict(id="vm-metrics", o="4.1", t="Vulnerability metrics and KPIs", q="kpi", h="""
<ul><li><strong>Trends</strong>: open findings over time, by severity. Is the program working, and are certain issues becoming systemic?</li>
<li><strong>Top 10</strong>: most common vulnerabilities, most vulnerable hosts or most affected business units. Focuses effort where one fix helps most.</li>
<li><strong>Critical vulnerabilities and zero-days</strong>: tracked separately because they need immediate attention and leadership visibility.</li>
<li><strong>SLOs</strong>: percentage of findings fixed within target time per severity. Measures performance against policy.</li></ul>
<p>A <strong>KPI</strong> is a metric chosen to show whether you are meeting a goal. Mean time to remediate by severity is a common one.</p>
"""),

dict(id="stakeholders-vm", o="4.1", t="Stakeholder identification (vulnerability management)", q="stakeholder", h="""
<p>Identify early who receives reports, who owns each asset and who approves fixes: system and application owners, IT operations, change board, security leadership, executives, compliance and audit, and sometimes vendors or customers bound by contract. A report sent to the wrong audience, or at the wrong level of detail, doesn&rsquo;t get acted on.</p>
"""),

# ---------------------------------------------------------------- 4.2
dict(id="declaration", o="4.2", t="Stakeholders, declaration and escalation", q="escalation", h="""
<p><strong>Stakeholders</strong> for an incident are named in the IR plan before anything happens: CSIRT, IT, executives, legal, HR (insider cases), PR/communications, compliance, and external parties (law enforcement, regulators, insurers, customers, partners).</p>
<p><strong>Declaration</strong>: the formal decision that an event is an incident, made by someone with defined authority using defined criteria. It triggers the plan, resources and notification clocks.</p>
<p><strong>Escalation</strong>: moving the incident to higher authority or more resources as severity rises, along pre-agreed paths with time thresholds, such as &ldquo;critical incidents reported to the CISO within one hour.&rdquo;</p>
"""),

dict(id="ir-report", o="4.2", t="Incident response report contents", q="executive summary", h="""
<ul><li><strong>Executive summary</strong>: short, non-technical, leading with business impact and current status. Written for leadership, so it goes first.</li>
<li><strong>Who, what, when, where and why</strong>: the facts of the incident.</li>
<li><strong>Timeline</strong>: timestamped sequence from first activity through detection, containment and recovery (in one time zone, ideally UTC).</li>
<li><strong>Scope</strong>: which systems, users and data were involved.</li>
<li><strong>Impact</strong>: operational, financial, data, legal and reputational.</li>
<li><strong>Evidence</strong>: what was collected, hashes, chain of custody references.</li>
<li><strong>Recommendations</strong>: specific improvements to prevent recurrence.</li>
<li>Root cause and lessons learned are often included.</li></ul>
""" + T.format("Technical detail does not belong in the executive summary. If the audience is the board, lead with impact, status and decisions needed.")),

dict(id="ir-comms", o="4.2", t="Communications: legal, PR, regulators, law enforcement", q="law enforcement", h="""
<ul><li><strong>Legal</strong>: involved early. Decides on privilege, notification obligations, contracts, evidence handling, and whether to involve law enforcement.</li>
<li><strong>Public relations</strong>: one controlled voice. <strong>Customer communication</strong> explains what happened and what customers should do; <strong>media</strong> statements are approved in advance. Technical staff don&rsquo;t talk to press.</li>
<li><strong>Regulatory reporting</strong>: many regimes have deadlines. GDPR requires notifying the supervisory authority within 72 hours of becoming aware of a qualifying breach; US public companies must disclose material incidents to the SEC within four business days of determining materiality; HIPAA, state breach laws and sector rules have their own clocks.</li>
<li><strong>Law enforcement</strong>: can help with attribution and recovery, but may take evidence or ask you to delay disclosure. Organizational and law-enforcement priorities can conflict, so legal and management decide.</li></ul>
<p>Use out-of-band channels (phone, separate chat) if the attacker may be reading corporate email.</p>
"""),

dict(id="ir-metrics", o="4.2", t="Incident metrics: MTTD, MTTR, alert volume", q="mttd", h="""
<div class="tblwrap"><table><tr><th>Metric</th><th>Measures from&hellip;to</th><th>Shows</th></tr>
<tr><td><strong>MTTD</strong> mean time to detect</td><td>Start of the incident &rarr; detection</td><td>Monitoring effectiveness (dwell time)</td></tr>
<tr><td><strong>MTTR</strong> mean time to respond</td><td>Detection &rarr; response or containment begins</td><td>Speed of the SOC and IR team</td></tr>
<tr><td><strong>MTTR</strong> mean time to remediate</td><td>Detection &rarr; fully fixed</td><td>End-to-end response capability</td></tr>
<tr><td><strong>Alert volume</strong></td><td>Count of alerts per period</td><td>Workload and tuning needs; a weak measure of security on its own</td></tr></table></div>
<p>The two MTTRs share an acronym, so read the question for which it means. CompTIA&rsquo;s acronym list also expands MTTR as mean time to repair.</p>
""" + T.format("Lower MTTD and MTTR are better. Rising alert volume is not success; it often means noisy rules and analyst fatigue.")),

dict(id="rca-lessons", o="4.2", t="Root cause analysis and lessons learned in reporting", q="root cause", h="""
<p>In 4.2, root cause and lessons learned are about <strong>communicating</strong> them: the report states the root cause plainly, the lessons-learned output becomes an action list with owners and due dates, and progress is reported back to leadership until each item closes. Without tracked actions, lessons learned are just a meeting.</p>
"""),
]
