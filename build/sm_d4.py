# Study Map, Domain 4: Reporting and Communication. Original prose, written
# against the CS0-003 objectives. Shape: see sm_page.py.

def I(t, what, does, where='', full='', trap='', flow=None, kids=None):
    return dict(t=t, what=what, does=does, where=where, full=full, trap=trap, flow=flow, kids=kids or [])

OBJ = {}

OBJ['4.1'] = {'title': 'Explain the importance of vulnerability management reporting and communication.', 'items': [
I('Vulnerability management reporting', 'Reports that tell people what is vulnerable and what is being done.', 'Turns scan output into decisions and accountability.', kids=[
  I('Vulnerabilities', 'The weaknesses found.', 'Listed with CVE, description and severity.'),
  I('Affected hosts', 'Which systems have each weakness.', 'Tells owners exactly what to fix.'),
  I('Risk score', 'A priority number for each finding.', 'Combines severity, exposure and asset value.'),
  I('Mitigation', 'The fix or workaround for each finding.', 'Patch, configuration change or compensating control.'),
  I('Recurrence', 'Findings that come back after being fixed.', 'Points to process problems, such as images that were never updated.'),
  I('Prioritization', 'The order fixes should happen in.', 'Puts the riskiest items first.'),
  ]),
I('Compliance reports', 'Reports showing status against a standard such as PCI DSS.', 'Prove to auditors and regulators that requirements are met.'),
I('Action plans', 'Concrete plans to reduce the risks found.', 'Assign what will be done, by whom and by when.', kids=[
  I('Configuration management', 'Keeping systems on approved secure settings.', 'Fixes misconfigurations and prevents drift.'),
  I('Patching', 'Applying vendor fixes.', 'Removes known vulnerabilities.'),
  I('Compensating controls', 'Alternatives when a fix isn&rsquo;t possible.', 'Reduce risk until a real fix exists.'),
  I('Awareness, education, and training', 'Teaching people.', 'Fixes human weaknesses such as falling for phishing.'),
  I('Changing business requirements', 'Business changes that alter the plan.', 'New systems or rules can change priorities.'),
  ]),
I('Inhibitors to remediation', 'Things that slow or block fixing vulnerabilities.', 'Explain delays and justify exceptions or compensating controls.', kids=[
  I('Memorandum of understanding (MOU)', 'An agreement with another party on how you work together.', 'Its terms can limit when or how you change shared systems.'),
  I('Service-level agreement (SLA)', 'A contract promising a level of service, such as uptime.', 'Uptime promises leave little time for patching reboots.'),
  I('Organizational governance', 'Approval processes and decision rights.', 'Slow approvals delay fixes.'),
  I('Business process interruption', 'A fix that would stop business work.', 'Delays changes to critical systems.'),
  I('Degrading functionality', 'A fix that would break or weaken features.', 'Teams resist a patch that breaks an app.'),
  I('Legacy systems', 'Old systems that can&rsquo;t be updated.', 'Often need isolation and compensating controls.'),
  I('Proprietary systems', 'Vendor-controlled systems you can&rsquo;t change yourself.', 'You wait on the vendor for fixes.'),
  ]),
I('Metrics and key performance indicators (KPIs)', 'Measures of how well vulnerability management is working.', 'Show progress and problem areas to leadership.', kids=[
  I('Trends', 'How numbers change over time.', 'Shows whether risk is going down.'),
  I('Top 10', 'The most common or most serious findings.', 'Focuses effort where it matters most.'),
  I('Critical vulnerabilities and zero-days', 'Counts of the most severe findings.', 'Tracked closely because they need fast action.'),
  I('SLOs', 'Target times for fixing by severity.', 'Measures whether remediation meets its deadlines.', full='Service-level objectives'),
  ]),
I('Stakeholder identification and communication', 'Working out who needs vulnerability information and how to tell them.', 'Executives get summaries, system owners get technical detail.'),
]}

OBJ['4.2'] = {'title': 'Explain the importance of incident response reporting and communication.', 'items': [
I('Stakeholder identification and communication', 'Knowing who must be told about an incident, and when.', 'Gets the right information to legal, PR, management, HR and technical teams, on a need-to-know basis.'),
I('Incident declaration and escalation', 'Declaration formally names something an incident; escalation hands it to a higher tier or team.', 'Starts the response plan and brings in the right people.'),
I('Incident response reporting', 'The written account of an incident.', 'Records what happened for leadership, regulators and future reference.', kids=[
  I('Executive summary', 'A short, non-technical overview.', 'Gives leaders the key facts and business impact quickly.'),
  I('Who, what, when, where, and why', 'The core facts of the incident.', 'Answers the basic questions in one place.'),
  I('Recommendations', 'Suggested improvements.', 'Prevent the incident from happening again.'),
  I('Timeline', 'A dated sequence of events, in UTC.', 'Shows how the incident unfolded and how fast the team responded.'),
  I('Impact', 'The harm caused.', 'Downtime, data affected, cost.'),
  I('Scope', 'What was affected.', 'Systems, users and data involved.'),
  I('Evidence', 'The proof collected.', 'Supports conclusions and any legal action.'),
  ]),
I('Communications', 'Managing what is said about an incident, and to whom.', 'Avoids accidental disclosure and meets legal duties.', kids=[
  I('Legal', 'The legal team.', 'Advises on regulatory duties, liability and law enforcement contact.', trap='Legal owns contact with law enforcement and reviews all outside statements.'),
  I('Public relations', 'The team that speaks for the company in public.', 'Prepares clear, accurate statements.', kids=[
    I('Customer communication', 'Telling affected customers.', 'Explains what happened and what they should do.'),
    I('Media', 'Handling reporters.', 'Only the designated spokesperson talks to the media.', trap='An analyst asked by a reporter declines and refers them to PR.'),
    ]),
  I('Regulatory reporting', 'Notifying regulators as the law requires.', 'GDPR gives 72 hours to notify the supervisory authority; HIPAA and state laws have their own rules.'),
  I('Law enforcement', 'Police and federal agencies.', 'Contacted when a crime is suspected, coordinated through legal.'),
  ]),
I('Root cause analysis', 'Finding why the incident was possible.', 'Points the fix at the cause so it doesn&rsquo;t happen again.'),
I('Lessons learned', 'The post-incident review.', 'Records what worked, what failed and what to change.'),
I('Metrics and KPIs', 'Measures of incident response performance.', 'Show where response is slow.',
  flow=['Compromise', 'Detected (MTTD)', 'Acknowledged (MTTA)', 'Responded (MTTR)', '*Remediated'], kids=[
  I('Mean time to detect', 'Average time from compromise to detection.', 'Improved by better monitoring and detection rules.', full='MTTD'),
  I('Mean time to respond', 'Average time from detection to response.', 'Improved by 24/7 coverage and SOAR.'),
  I('Mean time to remediate', 'Average time to fully fix and return to normal.', 'Lower means the business recovers sooner.'),
  I('Alert volume', 'How many alerts the SOC receives.', 'Too many causes fatigue; tune rules to cut false positives.'),
  ]),
]}
