# Study Map, Domain 1: Security Operations. Original prose, written against
# the CS0-003 objectives. Shape: see sm_page.py.

def I(t, what, does, where='', full='', trap='', flow=None, kids=None):
    return dict(t=t, what=what, does=does, where=where, full=full, trap=trap, flow=flow, kids=kids or [])

OBJ = {}

OBJ['1.1'] = {'title': 'Explain the importance of system and network architecture concepts in security operations.', 'items': [
I('Log ingestion', 'Getting logs from every system into one central place, parsed into common fields.',
  'Lets one search or correlation rule cover firewalls, servers, endpoints and cloud at once.',
  'Logs travel from sources to a collector and on to the SIEM.',
  flow=['Hosts, firewalls, cloud', 'Agents / syslog / APIs', '*Collector or SIEM'], kids=[
  I('Time synchronization', 'Every system agreeing on the time, using NTP.', 'Keeps events in the right order so correlation rules fire and timelines make sense.',
    'Hosts sync to internal NTP servers (UDP 123), which sync to a trusted source; store timestamps in UTC.',
    trap='Events from two systems don&rsquo;t line up, or a correlation rule never fires? Suspect time sync first.'),
  I('Logging levels', 'How much detail a source records. Syslog uses 0 Emergency, 1 Alert, 2 Critical, 3 Error, 4 Warning, 5 Notice, 6 Informational, 7 Debug.',
    'Sets the trade-off between detail and volume. Choosing level 4 keeps 0 through 4.', trap='Lower number means more severe. Debug (7) is the noisiest, not the most urgent.'),
  ]),
I('Operating system (OS) concepts', 'How Windows and Linux store settings, run programs and protect themselves.',
  'Tells you what normal looks like, so changes made by an attacker stand out.', kids=[
  I('Windows Registry', 'Windows&rsquo; central configuration database.', 'Holds system, user and program settings, including where malware hides persistence.',
    'Hives such as HKLM (machine) and HKCU (current user). Run keys under <code>Software/Microsoft/Windows/CurrentVersion/Run</code> start programs at logon. Edited with <code>regedit</code>.'),
  I('System hardening', 'Reducing a system&rsquo;s attack surface below its default build.', 'Removes unused software and services, closes ports, enforces a secure baseline, patches and turns on logging.', 'Applied with CIS Benchmarks, Group Policy, or configuration management tools.'),
  I('File structure', 'How the OS organizes folders and files.', 'Knowing the layout tells you where to look for evidence and where attackers stage files.',
    'Linux: <code>/etc</code> config, <code>/var/log</code> logs, <code>/home</code> users, <code>/tmp</code> temporary. Windows: <code>C:/Windows/System32</code>, user profiles, <code>%TEMP%</code>.', kids=[
    I('Configuration file locations', 'Where settings are stored as files.', 'Changes here are evidence of tampering or misconfiguration.',
      'Linux: <code>/etc/passwd</code>, <code>/etc/shadow</code>, <code>/etc/ssh/sshd_config</code>, <code>/etc/crontab</code>. Windows: the Registry, plus the hosts file in <code>System32/drivers/etc</code>.'),
    ]),
  I('System processes', 'Programs running on a host.', 'Knowing normal processes, their parents and paths exposes impostors.',
    'Windows: Task Manager, <code>tasklist</code>. Linux: <code>ps</code>, <code>top</code>.', trap='Right name, wrong folder or wrong parent (svchost.exe started by Word) is a malicious process.'),
  I('Hardware architecture', 'The physical building blocks: CPU, memory, storage, firmware, TPM.', 'Hardware features enable protections such as Secure Boot, TPM-backed encryption, DEP and secure enclaves.', 'On the motherboard and in firmware (UEFI).'),
  ]),
I('Infrastructure concepts', 'The ways compute is delivered: physical servers, virtual machines, containers and serverless functions.',
  'Changes what you manage, what can go wrong and what evidence exists.', kids=[
  I('Serverless', 'Code run by a cloud provider on demand, with no server for you to manage.', 'Runs a function when triggered, then stops. You secure the code and its permissions.',
    'In the provider&rsquo;s cloud (AWS Lambda, Azure Functions). Evidence is the provider&rsquo;s logs; there is no host to image.'),
  I('Virtualization', 'Running several complete operating systems on one physical host through a hypervisor.', 'Isolates workloads and lets you snapshot a VM for forensics.',
    'Type 1 hypervisors run on bare metal (ESXi, Hyper-V); Type 2 run on top of an OS (VirtualBox).', trap='VM escape is the key risk: breaking out of a guest to reach the host.'),
  I('Containerization', 'Packaging an app with its dependencies so it runs the same anywhere, sharing the host&rsquo;s kernel.', 'Starts fast and scales easily; containers are usually short-lived.',
    'Docker hosts and orchestrators such as Kubernetes.', trap='Containers share the host kernel, so isolation is weaker than VMs. Evidence disappears when a container is rebuilt; send logs off the host.'),
  ]),
I('Network architecture', 'How networks are laid out and where they live.', 'Decides how far an attacker can move and where you can watch traffic.', kids=[
  I('On-premises', 'Infrastructure you own and run in your own buildings.', 'Full control and full responsibility for every security layer.', 'Your data center or server rooms.'),
  I('Cloud', 'Infrastructure rented from a provider.', 'Responsibility is shared: the provider secures the platform, you secure what you put on it.', 'The provider&rsquo;s data centers (AWS, Azure, GCP).'),
  I('Hybrid', 'A mix of on-premises and cloud joined together.', 'Adds the connection and duplicate tooling as new risk; gaps appear at the seams.', 'Both places, linked by VPN or dedicated circuits.'),
  I('Network segmentation', 'Splitting a network into zones with controlled paths between them.', 'Limits lateral movement and narrows audit scope, such as isolating cardholder systems.', 'Enforced with VLANs, subnets, firewalls and a screened subnet (DMZ) for public servers.'),
  I('Zero trust', 'A model that never trusts a request because of where it comes from.', 'Verifies identity, device health and context on every request and gives least privilege per session.',
    'A policy decision point decides; a policy enforcement point (gateway, proxy, agent) allows or blocks.', flow=['User / device', '*Policy enforcement point', 'Policy decision point checks', 'Resource'],
    trap='Trusting a user because they are on the internal network is the opposite of zero trust.'),
  I('Secure access service edge (SASE)', 'Networking and security delivered together as one cloud service.', 'Combines SD-WAN with cloud security (SWG, CASB, ZTNA, firewall) close to wherever users are.', 'In the provider&rsquo;s cloud points of presence.'),
  I('Software-defined networking (SDN)', 'Separating the network&rsquo;s control plane (decides paths) from the data plane (forwards packets).', 'Lets you change routing and segmentation centrally in software, even during an incident.', 'A central controller programs switches through APIs.', trap='SDN is about separating control and data planes; a cloud-delivered security stack is SASE.'),
  ]),
I('Identity and access management (IAM)', 'Controlling who someone is and what they can do.', 'Covers accounts, authentication, authorization and access reviews.', 'Identity providers such as Active Directory and Entra ID; cloud IAM policies.', kids=[
  I('Multifactor authentication (MFA)', 'Login using two or more different factor types: something you know, have or are.', 'Stops most attacks that rely on stolen passwords.', trap='A password plus a security question is still one factor (both are something you know).'),
  I('Single sign-on (SSO)', 'One login that gives access to many applications in the same organization.', 'Fewer passwords and one strong login; but one stolen session opens everything.', 'An identity provider issues tokens that each app trusts.'),
  I('Federation', 'Trust between separate organizations so one can vouch for another&rsquo;s users.', 'Users sign in with their home identity to a partner&rsquo;s service. Uses SAML or OpenID Connect.', trap='SSO is within one organization; federation crosses organizations.'),
  I('Privileged access management (PAM)', 'Controls for admin and other powerful accounts.', 'Vaults credentials, grants admin rights only when needed, records sessions and rotates passwords.', 'A PAM vault and session gateway in front of servers.'),
  I('Passwordless', 'Signing in with no password: FIDO2 security keys, passkeys, biometrics.', 'Removes the shared secret, so phishing and password spraying stop working.'),
  I('Cloud access security broker (CASB)', 'A control point between users and cloud apps.', 'Finds shadow IT, enforces policy and applies DLP to SaaS.', 'Inline as a proxy, or connected to cloud apps by API.'),
  ]),
I('Encryption', 'Scrambling data so only key holders can read it.', 'Protects data in transit and at rest.', kids=[
  I('Public key infrastructure (PKI)', 'The system of certificate authorities, certificates and keys that proves identities.', 'Issues, renews and revokes certificates so strangers can trust each other&rsquo;s keys.',
    'Root CA (offline) signs intermediate CAs, which sign server and user certificates. Revocation via CRL or OCSP.', flow=['*Root CA', 'Intermediate CA', 'Server / user certificate']),
  I('Secure sockets layer (SSL) inspection', 'Decrypting encrypted traffic at a proxy or firewall to inspect it, then re-encrypting it.', 'Lets security tools see malware and data leaks hidden inside HTTPS.',
    'On a next-generation firewall or proxy; clients must trust its certificate.', trap='The protocol being inspected today is TLS. Privacy-sensitive sites (banking, health) are usually exempted.'),
  ]),
I('Sensitive data protection', 'Finding, classifying and guarding data that would cause harm if exposed.', 'Meets legal duties and reduces breach impact.', kids=[
  I('Data loss prevention (DLP)', 'Tools that spot sensitive data and stop it leaving.', 'Blocks, warns or logs when card numbers, PII or confidential files are emailed, uploaded or copied.', 'Endpoint agents, email and web gateways, and cloud (often through a CASB).', trap='Stopping data being sent out wants DLP. Encryption only protects it after it is stolen.'),
  I('Personally identifiable information (PII)', 'Information that identifies a person, alone or combined.', 'Triggers privacy laws such as GDPR and breach-notification duties.'),
  I('Cardholder data (CHD)', 'Payment card data: card number with name, expiry and service code.', 'Governed by PCI DSS; full track data, CVV and PIN must never be stored after authorization.'),
  ]),
]}

OBJ['1.2'] = {'title': 'Given a scenario, analyze indicators of potentially malicious activity.', 'items': [
I('Network-related', 'Signs of an attack seen in network traffic.', 'Point to scanning, command and control, spread or theft.', 'Seen in NetFlow, firewall and proxy logs, IDS alerts and packet captures.', kids=[
  I('Bandwidth consumption', 'Unusually heavy use of network capacity.', 'Can mean data being stolen, cryptomining or a DoS.'),
  I('Beaconing', 'Small, regular check-ins from a host to one outside address.', 'Malware asking its command server for instructions.', trap='Regular timing is the clue, not size. A beacon can be tiny.'),
  I('Irregular peer-to-peer', 'Workstations talking directly to each other.', 'Suggests lateral movement or a worm, since PCs normally talk to servers.'),
  I('Rogue devices on the network', 'Hardware that isn&rsquo;t authorized, such as an unknown laptop or wireless access point.', 'Can bridge attackers in or capture traffic. Spotted by NAC, DHCP logs or wireless scans.'),
  I('Scans/sweeps', 'Probing many ports on one host (scan) or one port on many hosts (sweep).', 'Reconnaissance. Seen from inside, it usually means someone already has a foothold.'),
  I('Unusual traffic spikes', 'Sudden departures from the normal traffic baseline.', 'Can signal DoS, exfiltration or a misconfiguration; needs a baseline to judge.'),
  I('Activity on unexpected ports', 'Services on non-standard ports, or a port carrying the wrong protocol.', 'Attackers hide command and control or tunnels this way.'),
  ]),
I('Host-related', 'Signs of compromise on a single computer.', 'Point to malware, persistence or misuse on that machine.', 'Seen in EDR, Event Viewer, Task Manager, file and registry monitoring.', kids=[
  I('Processor consumption', 'Sustained high CPU with no user activity.', 'Often cryptomining or password cracking.'),
  I('Memory consumption', 'Unexplained memory growth.', 'Can mean injected code or a malicious process; capture memory before rebooting.'),
  I('Drive capacity consumption', 'Disk space disappearing quickly.', 'Data being staged for theft or logs being flooded.'),
  I('Unauthorized software', 'Programs nobody approved.', 'Remote-access tools, hacking tools or malware; application allowlisting prevents it.'),
  I('Malicious processes', 'Processes doing harm, often disguised as system ones.', 'Check name, path, parent and signature together.'),
  I('Unauthorized changes', 'Settings or files changed without an approved change record.', 'Points to tampering; file integrity monitoring (FIM) catches it.'),
  I('Unauthorized privileges', 'Accounts with more rights than they should have.', 'Sign of privilege escalation or a backdoor admin account.'),
  I('Data exfiltration', 'Data being moved out of the organization without permission.', 'Large or after-hours outbound transfers, archives in temp folders, uploads to unusual sites.'),
  I('Abnormal OS process behavior', 'A legitimate process acting out of character.', 'For example Word starting PowerShell, or a browser making connections it never makes.'),
  I('File system changes or anomalies', 'New, renamed, hidden or altered files.', 'Dropped malware, web shells, encrypted files from ransomware.'),
  I('Registry changes or anomalies', 'New or modified Registry values.', 'Often persistence in Run keys or services.'),
  I('Unauthorized scheduled tasks', 'Scheduled tasks or cron jobs nobody created.', 'Persistence that relaunches malware at logon or on a timer.', 'Windows Task Scheduler (<code>schtasks</code>); Linux <code>crontab</code>.'),
  ]),
I('Application-related', 'Signs of attack seen in how applications behave.', 'Point to exploitation of apps or misuse of accounts.', 'Seen in application, web server and database logs.', kids=[
  I('Anomalous activity', 'App use that departs from normal.', 'Odd times, unusual volumes or functions a user never uses.'),
  I('Introduction of new accounts', 'Accounts appearing unexpectedly, especially admin ones.', 'Attacker persistence or privilege escalation.'),
  I('Unexpected output', 'An app returning things it shouldn&rsquo;t, such as database errors or other users&rsquo; data.', 'Sign of injection or broken access control.'),
  I('Unexpected outbound communication', 'An app or server connecting out to places it never contacts.', 'Command and control, or a web shell phoning home.'),
  I('Service interruption', 'An app crashing or becoming unavailable.', 'Could be DoS, exploitation attempts or ransomware.'),
  I('Application logs', 'Records an application writes about its own activity.', 'Source for errors, logins and transactions during an investigation.', 'Web server access and error logs, database logs, app-specific logs.'),
  ]),
I('Other', 'Indicators that don&rsquo;t fit network, host or application.', 'Mostly attacks on people.', kids=[
  I('Social engineering attacks', 'Manipulating people into giving access or information.', 'Phishing, pretexting, vishing and tailgating bypass technical controls.'),
  I('Obfuscated links', 'Links disguised to hide where they really go.', 'URL shorteners, lookalike characters and misleading link text lead to phishing or malware sites.', trap='Check the real destination (hover or expand it), not the text shown.'),
  ]),
]}

OBJ['1.3'] = {'title': 'Given a scenario, use appropriate tools or techniques to determine malicious activity.', 'items': [
I('Packet capture', 'Recording the actual network traffic.', 'Shows exactly what crossed the wire, not just that a connection happened.', 'Captured on a host, a SPAN port or a network tap; saved as .pcap files.', kids=[
  I('Wireshark', 'A graphical packet analyzer.', 'Dissects protocols, filters traffic and reassembles streams (Follow TCP Stream).', 'Desktop app on the analyst&rsquo;s machine; opens .pcap files.'),
  I('tcpdump', 'A command-line packet capture tool.', 'Captures and filters traffic and writes it to a file: <code>tcpdump -i eth0 port 22 -w ssh.pcap</code>.', 'Linux and Unix servers, often over SSH.'),
  ]),
I('Log analysis/correlation', 'Reviewing logs and linking related events across sources.', 'Turns many separate entries into one picture of an attack.', kids=[
  I('Security information and event management (SIEM)', 'Software that gathers logs from every system into one searchable place.', 'Collects, normalizes, correlates, alerts and keeps history.',
    'A central server or cloud service fed by agents, syslog (514, or 6514 with TLS) and APIs.', flow=['Sources', 'Agents / syslog / APIs', '*SIEM', 'SOAR / analyst'], trap='SIEM detects and alerts. SOAR acts.'),
  I('Security orchestration, automation, and response (SOAR)', 'A platform that runs response steps automatically through playbooks.', 'Enriches alerts, isolates hosts, blocks IPs and opens tickets in seconds.', 'Connected to the SIEM, EDR, firewall and ticketing through APIs.'),
  ]),
I('Endpoint security', 'Protection running on each device.', 'Detects and stops threats on the host itself.', kids=[
  I('Endpoint detection and response (EDR)', 'An agent that records and analyzes activity on each endpoint.', 'Detects suspicious behavior, keeps a history of processes and connections, and can isolate the host.', 'Agent on every endpoint, reporting to a central console.', trap='EDR catches behavior that signature antivirus misses (fileless and living-off-the-land attacks).'),
  ]),
I('Domain name service (DNS) and Internet Protocol (IP) reputation', 'Checking whether a domain or IP has a bad history.', 'Helps decide quickly if an address in an alert is malicious.', kids=[
  I('WHOIS', 'Registration records for domains and IP blocks.', 'Shows owner, registrar and creation date. A domain registered days ago is suspicious.', 'Command line <code>whois example.com</code> or web lookups.'),
  I('AbuseIPDB', 'A community database of reported malicious IP addresses.', 'Shows how often and why an IP was reported.', 'Website and API.'),
  ]),
I('File analysis', 'Examining a suspicious file to judge whether it is malicious.', 'Identifies malware without, or before, running it.', kids=[
  I('Strings', 'A tool that pulls readable text out of a binary.', 'Reveals URLs, IPs, commands and file paths inside a sample.', 'Linux <code>strings</code>; Sysinternals Strings on Windows.'),
  I('VirusTotal', 'A site that scans a file or hash with dozens of antivirus engines.', 'Gives a quick verdict and history.', 'Website and API.', trap='Submit the hash first. Uploading a sensitive file shares it publicly.'),
  ]),
I('Sandboxing', 'Running a suspicious file in an isolated environment.', 'Watches what it does (files, registry, network) without risking real systems.', 'An isolated VM or a cloud sandbox service.', kids=[
  I('Joe Sandbox', 'A commercial malware analysis sandbox.', 'Runs samples and produces a detailed behavior report.', 'Cloud service or on-premises.'),
  I('Cuckoo Sandbox', 'An open-source automated malware sandbox.', 'Detonates samples in VMs and reports behavior.', 'Self-hosted on your own analysis machine.'),
  ]),
I('Pattern recognition', 'Spotting known shapes of malicious activity in data.', 'Lets you recognize an attack from its pattern even without a signature.', kids=[
  I('Command and control (C2)', 'The channel an attacker uses to control compromised hosts.', 'Beaconing at regular intervals, odd DNS (long random subdomains), traffic to new or random-looking domains.'),
  ]),
I('Interpreting suspicious commands', 'Reading command lines and deciding if they are malicious.', 'Catches attackers using built-in tools: encoded PowerShell, downloads into memory, new admin accounts, reverse shells.', 'Seen in command-line logging (Windows Event 4688, PowerShell 4104), EDR and shell history.'),
I('Email analysis', 'Checking emails for signs of phishing and spoofing.', 'Confirms whether a message is genuine and where it really came from.', kids=[
  I('Header', 'The routing and metadata lines of an email.', 'Shows the real path and sender. Read Received lines bottom-up; compare From, Reply-To and Return-Path.'),
  I('Impersonation', 'Pretending to be a trusted sender.', 'Display-name spoofing and lookalike domains trick users into trusting the message.'),
  I('DomainKeys Identified Mail (DKIM)', 'A digital signature added to outgoing mail.', 'Proves the message came from the domain and wasn&rsquo;t changed.', 'Signature in the header; public key in DNS.'),
  I('Domain-based Message Authentication, Reporting, and Conformance (DMARC)', 'A domain&rsquo;s policy for mail that fails SPF or DKIM checks.', 'Tells receivers to do nothing, quarantine or reject, and where to send reports.', 'A DNS TXT record at <code>_dmarc.domain</code>.'),
  I('Sender Policy Framework (SPF)', 'A list of servers allowed to send mail for a domain.', 'Lets receivers reject mail from unlisted servers.', 'A DNS TXT record on the domain.', trap='SPF checks the sending server, DKIM checks the signature, DMARC says what to do when they fail.'),
  I('Embedded links', 'Links inside the email body.', 'May lead to phishing pages; the shown text can differ from the real URL.'),
  ]),
I('Hashing', 'Creating a fixed fingerprint of a file with SHA-256 or similar.', 'Identifies known malware and proves a file hasn&rsquo;t changed.', '<code>Get-FileHash</code> in PowerShell, <code>sha256sum</code> on Linux.'),
I('User behavior analysis', 'Comparing what accounts do against their normal patterns.', 'Finds compromised accounts and insiders.', 'UEBA features in SIEM and identity platforms.', kids=[
  I('Abnormal account activity', 'An account behaving unusually.', 'Odd login times, unusual data access, sudden privilege use.'),
  I('Impossible travel', 'Logins from places too far apart for the time between them.', 'One of the sessions is not the real user.', trap='A VPN exit node can cause a false alarm; check before acting.'),
  ]),
I('Programming languages/scripting', 'Code and data formats an analyst must be able to read.', 'Lets you understand scripts, logs and tool output during investigations.', kids=[
  I('JavaScript Object Notation (JSON)', 'A text format of name/value pairs in braces.', 'Used for API data, cloud logs and SIEM events.'),
  I('Extensible Markup Language (XML)', 'A tagged text data format.', 'Used for SAML assertions, Windows event exports and some APIs; target of XXE attacks.'),
  I('Python', 'A general-purpose scripting language.', 'Used to automate analysis and build tools; also used by attackers for reverse shells.'),
  I('PowerShell', 'Windows&rsquo; shell and scripting language.', 'Automates admin work; attackers abuse it for in-memory downloads and encoded commands.'),
  I('Shell script', 'Scripts for Unix shells such as bash.', 'Automates Linux tasks; attackers use them to download and run payloads.'),
  I('Regular expressions', 'Patterns for matching text.', 'Find IPs, emails or encoded commands in logs, and power SIEM and DLP rules.'),
  ]),
]}

OBJ['1.4'] = {'title': 'Compare and contrast threat-intelligence and threat-hunting concepts.', 'items': [
I('Threat actors', 'The people and groups behind attacks.', 'Knowing their motives and skills predicts what they will target and how.', kids=[
  I('Advanced persistent threat (APT)', 'A skilled, well-funded group that gets in and stays hidden for a long time.', 'Steals data or spies over months; often state-backed.'),
  I('Hacktivists', 'Attackers driven by a political or social cause.', 'Defacements, leaks and DDoS to make a point.'),
  I('Organized crime', 'Criminal groups attacking for money.', 'Ransomware, fraud and data theft for sale.'),
  I('Nation-state', 'Attackers working for a government.', 'Espionage and sabotage with large resources.'),
  I('Script kiddie', 'Low-skill attackers using other people&rsquo;s tools.', 'Opportunistic attacks for curiosity or status.'),
  I('Insider threat', 'Risk from people inside the organization.', 'They already have access, so perimeter controls don&rsquo;t stop them.', kids=[
    I('Intentional', 'An insider harming the organization on purpose.', 'Theft or sabotage; detected with monitoring, least privilege and DLP.'),
    I('Unintentional', 'An insider causing harm by mistake.', 'Clicking a phishing link or misdirecting data; reduced with training and guardrails.'),
    ]),
  I('Supply chain', 'Attacks that come through a trusted supplier.', 'Compromised software updates, service providers or hardware reach you through trust.'),
  ]),
I('Tactics, techniques, and procedures (TTP)', 'How an attacker operates: goals (tactics), methods (techniques) and specific steps (procedures).', 'Detections built on behavior last longer than ones built on hashes or IPs.', 'Catalogued in MITRE ATT&amp;CK.'),
I('Confidence levels', 'How much you can trust a piece of intelligence.', 'Decides whether to act on it.', kids=[
  I('Timeliness', 'Is it still current?', 'Old indicators may now belong to innocent owners.'),
  I('Relevancy', 'Does it apply to your sector and technology?', 'Intelligence about systems you don&rsquo;t run is noise.'),
  I('Accuracy', 'Is it correct and confirmed?', 'Wrong intelligence causes false alarms or blocks good traffic.'),
  ]),
I('Collection methods and sources', 'Where threat intelligence comes from.', 'A mix of sources gives better coverage.', kids=[
  I('Open source', 'Freely available public intelligence (OSINT).', 'Broad and free, but noisy and visible to attackers too.', kids=[
    I('Social media', 'Public posts and accounts.', 'Early warnings, leaked data and attacker chatter.'),
    I('Blogs/forums', 'Researcher write-ups and community discussions.', 'Detailed analyses and indicators.'),
    I('Government bulletins', 'Advisories from agencies such as CISA.', 'Authoritative alerts, including the Known Exploited Vulnerabilities catalog.'),
    I('Computer emergency response team (CERT)', 'National or sector teams that coordinate response.', 'Publish advisories and coordinate fixes.'),
    I('Cybersecurity incident response team (CSIRT)', 'An organization&rsquo;s incident response team.', 'Shares findings from incidents it handles.'),
    I('Deep/dark web', 'Hidden sites and markets.', 'Shows stolen data for sale and planned attacks.'),
    ]),
  I('Closed source', 'Intelligence that is paid for or restricted.', 'More targeted and timely.', kids=[
    I('Paid feeds', 'Commercial threat intelligence subscriptions.', 'Curated indicators and reports.'),
    I('Information sharing organizations', 'Industry groups such as ISACs.', 'Members share threats specific to their sector.'),
    I('Internal sources', 'Your own logs, incidents and telemetry.', 'The most relevant intelligence because it is about your environment.'),
    ]),
  ]),
I('Threat intelligence sharing', 'Getting intelligence to the teams that can use it.', 'Intelligence that stays with the intel team changes nothing.', kids=[
  I('Incident response', 'The team handling incidents.', 'Uses intelligence to scope and contain attacks faster.'),
  I('Vulnerability management', 'The team running scanning and patching.', 'Uses it to prioritize vulnerabilities being exploited now.'),
  I('Risk management', 'The function assessing business risk.', 'Uses it to judge likelihood realistically.'),
  I('Security engineering', 'The team building defenses.', 'Uses it to design controls against real attacker methods.'),
  I('Detection and monitoring', 'The SOC watching for threats.', 'Turns intelligence into detection rules and watchlists.'),
  ]),
I('Threat hunting', 'Proactively searching for attackers already hiding in your network.', 'Finds what automated alerts missed. It starts with a hypothesis.', 'Uses SIEM, EDR and network data.', flow=['*Hypothesis', 'Collect data', 'Analyze', 'Find and remove', 'New detections'], kids=[
  I('Indicators of compromise (IoC)', 'Evidence that a compromise has happened: hashes, IPs, domains, file names.', 'Gives hunters and tools something concrete to look for.', kids=[
    I('Collection', 'Gathering IoCs.', 'From incidents, feeds and sharing groups.'),
    I('Analysis', 'Checking IoCs for quality and relevance.', 'Removes stale or irrelevant indicators.'),
    I('Application', 'Putting IoCs to use.', 'Loads them into SIEM, EDR, firewalls and DNS filters.'),
    ]),
  I('Focus areas', 'Where hunts concentrate.', 'Places where attackers hide or where damage would be worst.', kids=[
    I('Configurations/misconfigurations', 'Weak or drifted settings.', 'What attackers exploit to get in or stay in.'),
    I('Isolated networks', 'Segments that get little monitoring.', 'Attackers hide where nobody looks.'),
    I('Business-critical assets and processes', 'The systems that matter most.', 'Where a compromise would hurt most.'),
    ]),
  I('Active defense', 'Raising the attacker&rsquo;s cost inside your own network.', 'Deception, decoys and making attacker progress slow and noisy.', trap='Active defense stays inside your own network. Attacking back at attacker systems is illegal.'),
  I('Honeypot', 'A decoy system with no real purpose, there to attract attackers.', 'Any interaction is suspicious; lets you study attacker TTPs safely.', 'Placed in the DMZ or internal network, isolated from real data.'),
  ]),
]}

OBJ['1.5'] = {'title': 'Explain the importance of efficiency and process improvement in security operations.', 'items': [
I('Standardize processes', 'Writing down one agreed way to handle each common task.', 'Makes responses consistent, reduces mistakes and shows what can be automated.', kids=[
  I('Identification of tasks suitable for automation', 'Picking which tasks a machine should do.', 'Automates the routine work so analysts focus on judgment.', kids=[
    I('Repeatable/do not require human interaction', 'Tasks with the same steps every time and no judgment call.', 'Best candidates: enrichment lookups, ticket creation, blocking known-bad indicators.'),
    ]),
  I('Team coordination to manage and facilitate automation', 'Security, IT and engineering agreeing on what to automate.', 'Prevents automation that breaks systems or acts on false positives.'),
  ]),
I('Streamline operations', 'Removing wasted effort from the SOC.', 'Speeds up response and reduces analyst fatigue.', kids=[
  I('Automation and orchestration', 'Automation does one task; orchestration links tasks across tools into a workflow.', 'Turns many manual steps into one consistent response.', kids=[
    I('Security orchestration, automation, and response (SOAR)', 'A platform that runs playbooks across security tools.', 'Responds to alerts in seconds and records every step.', 'Connected to SIEM, EDR, firewall and ticketing through APIs.'),
    ]),
  I('Orchestrating threat intelligence data', 'Feeding intelligence into tools automatically.', 'Gives analysts context without manual lookups.', kids=[
    I('Data enrichment', 'Adding context to an alert automatically.', 'Attaches reputation, location, WHOIS and history to IPs and domains.'),
    I('Threat feed combination', 'Merging several intelligence feeds.', 'Better coverage, and indicators seen in several feeds are more trustworthy.'),
    ]),
  I('Minimize human engagement', 'Letting machines do the repetitive work.', 'Frees analysts for investigations that need judgment.'),
  ]),
I('Technology and tool integration', 'Connecting security tools so they share data and actions.', 'Removes manual copying between consoles.', kids=[
  I('Application programming interface (API)', 'A defined way for one program to ask another for data or actions.', 'How SOAR, SIEM and EDR talk to each other.', 'Usually REST over HTTPS returning JSON.'),
  I('Webhooks', 'A program calling a URL to notify another the moment something happens.', 'Pushes events instantly instead of waiting to be polled.'),
  I('Plugins', 'Add-ons that extend a tool from inside.', 'Adds integrations or features the tool didn&rsquo;t ship with.'),
  ]),
I('Single pane of glass', 'One console showing data from many tools.', 'Analysts stop switching screens and miss less; the trade-off is a single point of failure for visibility.'),
]}
