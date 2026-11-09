"""Class deck checks for the Study Map, keyed by card id (as built by sm_page.norm).

Each one flags a place where a class deck is wrong or misleading and gives the correct
reading. Original prose; no deck text is reproduced. sm_page.py asserts every id exists.
"""
DECK = {
 "11-log-ingestion-logging-levels":
  "Day 14 lists syslog level 0 as &ldquo;unstable&rdquo;. Level 0 is <strong>Emergency: the system is unusable</strong>. Level 5, Notice, is a normal but significant condition, not an error.",
 "12-network-related-bandwidth-consumption":
  "Day 13, question 9 offers &ldquo;HTTP DDoS&rdquo; for a flood that comes from one source address. One source is a <strong>DoS</strong>; distributed means many sources, usually a botnet. The slide&rsquo;s own explanation says DoS, and that is the right reading.",
 "12-host-related-data-exfiltration":
  "Day 13, question 7 calls an FTP transfer to 10.0.0.1 exfiltration. 10.0.0.1 is a private, internal address, so the data never left the network. Read it as <strong>staging, or a transfer to a rogue internal host</strong>. It becomes exfiltration when the data crosses the boundary to a destination outside your control.",
 "13-domain-name-service-dns-and-internet-protocol-ip-2":
  "Day 13 treats WHOIS privacy protection as a sign that a domain is malicious. Many registrars turn privacy on by default, and GDPR redacts registrant details for many domains, so <strong>privacy alone proves nothing</strong>. Weigh it with stronger signals: a very recent creation date, a lookalike name, poor IP reputation.",
 "13-programming-languages-scripting-powershell":
  "Day 13 annotates <code>WebClient</code> as the Windows WebDAV client service. In a script, <code>New-Object Net.WebClient</code> creates the <strong>.NET <code>System.Net.WebClient</code> class</strong>; its <code>DownloadString</code> and <code>DownloadFile</code> methods fetch content over HTTP(S), and <code>IEX</code> then runs it in memory. The WebClient <em>service</em> is unrelated: it lets Windows map WebDAV shares.",
 "21-asset-discovery":
  "Day 14 keys &ldquo;identify vulnerabilities&rdquo; as the purpose of asset discovery. Its main purpose is an <strong>accurate inventory</strong>: what exists, where, and what it runs. Vulnerability scanning comes next and depends on it, because you can&rsquo;t scan what you don&rsquo;t know you have.",
 "21-critical-infrastructure-supervisory-control-and-":
  "Day 14 keys Transportation as the sector that uses SCADA. From those four options that is the best answer, but SCADA is most often described in <strong>energy (power grids, pipelines) and water and wastewater</strong>, so expect those in exam scenarios.",
 "22-web-application-scanners-zed-attack-proxy-zap":
  "Day 14 says ZAP&rsquo;s key strength over Burp Suite is robust manual testing. Manual, interactive testing is what Burp is known for. What sets <strong>ZAP</strong> apart is that it is <strong>free and open source with a full automated scanner and an API for CI/CD pipelines</strong>, which Burp keeps for its paid edition.",
 "22-multipurpose-nmap":
  "Day 14&rsquo;s port-state slide says <em>unfiltered</em> means &ldquo;accessible but no service&rdquo;. <strong>Unfiltered</strong> means the probe reached the port but Nmap can&rsquo;t tell whether it is open or closed; you see it with an ACK scan (<code>-sA</code>), which maps firewall rules, not services. A port with no service listening is <strong>closed</strong>.",
 "23-common-vulnerability-scoring-system-cvss-interpr":
  "Day 13, question 1 says &ldquo;CVE metrics&rdquo;: the metrics are <strong>CVSS</strong>; CVE is only the identifier. The vector prefix is <code>CVSS:3.1/</code>, not <code>CVSS:31</code>. The keyed answer has <code>A:L</code> although the question says availability is not affected, which is <code>A:N</code>. Two options use values that don&rsquo;t exist: AV takes only N, A, L or P; PR takes N, L or H; UI takes N or R.",
 "23-common-vulnerability-scoring-system-cvss-interpr-7":
  "Day 14 says a &ldquo;Low impact&rdquo; vulnerability means no impact on confidentiality, integrity or availability. That is <strong>None (N)</strong>. <strong>Low (L)</strong> means some loss: limited data read or changed, or reduced performance.",
 "32-containment-eradication-and-recovery-isolation":
  "Day 13, question 13 kills the malicious process first. <strong>Isolate the host, capture memory, then kill the process.</strong> Killing it first destroys what is in RAM: the decrypted payload, injected code, keys and live connections.",
}
