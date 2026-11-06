# Study Map, Domain 3: Incident Response and Management. Original prose,
# written against the CS0-003 objectives. Shape: see sm_page.py.

def I(t, what, does, where='', full='', trap='', flow=None, kids=None):
    return dict(t=t, what=what, does=does, where=where, full=full, trap=trap, flow=flow, kids=kids or [])

OBJ = {}

OBJ['3.1'] = {'title': 'Explain concepts related to attack methodology frameworks.', 'items': [
I('Cyber kill chains', 'A model of the stages an attack moves through, from Lockheed Martin.',
  'Shows where a defense can break the chain; stopping any stage stops the attack.',
  flow=['Recon', 'Weaponization', 'Delivery', 'Exploitation', 'Installation', '*Command and control', 'Actions on objectives'],
  trap='Weaponization (building the payload) happens on the attacker&rsquo;s side, so you have no logs of it. Installation means persistence; exploitation is code running once.'),
I('Diamond Model of Intrusion Analysis', 'A model that describes one intrusion event with four connected points: adversary, capability, infrastructure and victim.',
  'Lets you pivot: from a known C2 server (infrastructure) to the malware (capability) or to other victims.',
  where='The four points: Adversary (who and why), Capability (malware, exploits, TTPs), Infrastructure (C2 servers, domains, IPs), Victim (people and systems targeted).',
  trap='C2 servers are infrastructure, not capability. Motive belongs with the adversary.'),
I('MITRE ATT&amp;CK', 'A free knowledge base of real attacker tactics and techniques, each with an ID such as T1059.',
  'Gives a common language to map detections, incidents and threat intelligence.', 'Online at attack.mitre.org; the ATT&amp;CK Navigator shows coverage.'),
I('Open Source Security Testing Methodology Manual (OSSTMM)', 'A manual for testing security in general, published by ISECOM.',
  'Covers testing of people, physical, wireless, telecom and data networks with measurable results.', trap='A general, broad security assessment points to OSSTMM; web applications only point to the OWASP Testing Guide.'),
I('OWASP Testing Guide', 'OWASP&rsquo;s methodology for testing web applications.', 'Lists test cases for authentication, sessions, input validation, configuration and business logic.',
  trap='The Testing Guide says how to test; ASVS lists the requirements an app must meet; the Top 10 lists the biggest risks.'),
]}

OBJ['3.2'] = {'title': 'Given a scenario, perform incident response activities.', 'items': [
I('Detection and analysis', 'Spotting a possible incident and working out what happened.', 'Confirms whether it is a real incident, how serious it is and how far it reaches.', kids=[
  I('IoC', 'Evidence that a compromise has occurred, such as a malicious hash, IP or domain.', 'Confirms an incident and helps find other affected systems.', full='Indicator of compromise'),
  I('Evidence acquisitions', 'Collecting data from affected systems in a way that holds up later.', 'Preserves what happened for analysis and possible legal action.',
    flow=['*RAM and CPU state', 'Network and processes', 'Disk', 'Logs and backups'], trap='Collect the most volatile evidence first. Powering off loses RAM.', kids=[
    I('Chain of custody', 'A record of who handled evidence, when, where and why.', 'Proves the evidence wasn&rsquo;t tampered with, so it stays admissible.', 'A custody form that travels with the evidence.'),
    I('Validating data integrity', 'Proving evidence hasn&rsquo;t changed.', 'Hash the original and the copy (SHA-256); matching hashes prove they are identical.'),
    I('Preservation', 'Keeping evidence in its original state.', 'Use write blockers, work on copies, store securely.'),
    I('Legal hold', 'A directive to keep relevant data and stop it being deleted.', 'Suspends normal retention and deletion, often quietly, before litigation.', 'Applied on email, file servers and cloud storage.', trap='&ldquo;Preserve evidence before notifying the employee&rdquo; is a legal hold.'),
    ]),
  I('Data and log analysis', 'Reviewing logs and data to rebuild events.', 'Shows what happened before, during and after the incident.', 'SIEM, log viewers, EDR timelines.', trap='&ldquo;What led up to the incident&rdquo; means logs.'),
  ]),
I('Containment, eradication, and recovery', 'Stopping the damage, removing the attacker, and returning to normal.', 'Limits harm, cleans systems and restores service.',
  flow=['*Contain', 'Eradicate', 'Recover'], kids=[
  I('Scope', 'How far the incident reaches: which systems, accounts and data.', 'Decides how wide containment must be.'),
  I('Impact', 'How much harm the incident causes.', 'Measured in downtime, recovery time, data loss and cost; drives priority.'),
  I('Isolation', 'Cutting an affected system off from the network.', 'Stops spread and C2 while keeping the system on for evidence.', 'Through EDR network containment, switch port shutdown or a quarantine VLAN.', trap='Ransomware on a PC: isolate it, don&rsquo;t power it off.'),
  I('Remediation', 'Fixing what let the attack in.', 'Patching, removing persistence, resetting credentials.'),
  I('Re-imaging', 'Wiping a system and reinstalling from a known-good image.', 'Returns it to a clean, trusted state.'),
  I('Compensating controls', 'Temporary alternative controls during recovery.', 'Reduce risk while the permanent fix is pending, such as extra monitoring or blocking rules.'),
  ]),
]}

OBJ['3.3'] = {'title': 'Explain the preparation and post-incident activity phases of the incident management life cycle.', 'items': [
I('Preparation', 'Everything done before an incident so the team can respond well.', 'Sets up plans, tools, people and practice. It is the first phase.',
  flow=['*Preparation', 'Detection and analysis', 'Containment, eradication, recovery', 'Post-incident activity'], kids=[
  I('Incident response plan', 'The written plan for handling incidents.', 'Defines roles, communication, escalation and phases.'),
  I('Tools', 'The kit responders need ready.', 'Forensic tools, write blockers, clean media, contact lists, out-of-band communication.'),
  I('Playbooks', 'Step-by-step guides for specific incident types.', 'Make responses to ransomware or phishing consistent; SOAR can automate them.'),
  I('Tabletop', 'A discussion exercise walking through a scenario.', 'Tests the plan and roles without touching systems.', trap='A new team with an approved plan should run a tabletop next.'),
  I('Training', 'Teaching staff their incident roles.', 'Keeps responders ready and users reporting quickly.'),
  I('Business continuity (BC)/disaster recovery (DR)', 'Plans to keep the business running (BC) and to restore IT after a disaster (DR).', 'Use targets such as RTO (time to restore) and RPO (how much data may be lost).'),
  ]),
I('Post-incident activity', 'Work done after the incident is resolved.', 'Learns from the incident and improves defenses.', kids=[
  I('Forensic analysis', 'Detailed examination of evidence.', 'Establishes exactly what happened and supports legal action.'),
  I('Root cause analysis', 'Finding the underlying reason the incident was possible.', 'Fixes the cause, not just the symptom, so it doesn&rsquo;t happen again.'),
  I('Lessons learned', 'A review of what went well and what didn&rsquo;t.', 'Produces recommendations and updates the plan; the need for changes is recorded here, and change control carries them out.'),
  ]),
]}
