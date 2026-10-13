import json,sys
sys.path.insert(0,'/home/claude/build/acr')
from lib import NB
for d in range(1,6):
    nb=NB('/home/claude/domain%d-notebook.html'%d)
    if d==4:
        nb.rep('<p>GCMP is built on <strong>GCM</strong> (Galois/Counter Mode).</p>',
 '<p>GCMP is built on <strong>GCM</strong> (Galois/Counter Mode).</p>\n<p><strong>Fine print on WPA3 ciphers:</strong> in the Wi-Fi Alliance specification, <strong>WPA3-Personal</strong> still encrypts with <strong>AES-CCMP</strong> (128-bit) &mdash; what it changes is the handshake (SAE). <strong>GCMP-256</strong> is required by the optional <strong>WPA3-Enterprise 192-bit mode</strong>. CompTIA and most study material simply pair "WPA3 = GCMP", so on the exam choose <strong>GCMP</strong> for WPA3 and <strong>CCMP</strong> for WPA2.</p>')
        nb.rep('<td>AES with GCMP (Galois/Counter Mode), SAE</td>','<td>AES with GCMP (Galois/Counter Mode), SAE &mdash; exam answer; strictly, GCMP-256 is the Enterprise 192-bit mode and Personal keeps CCMP</td>')
    items=json.load(open('/home/claude/audit/depth-d%d.json'%d))
    for it in items:
        assert '`' not in it['html'] and '${' not in it['html'], it['topic']
        nb.append(it['topic'],it['html'])
    nb.save()
