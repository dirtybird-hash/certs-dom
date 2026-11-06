# Midnight restyle for the CySA+ toolkit pages that predate the Study Map.
# Takes each live artifact (wrapped or fragment), returns a fragment with:
#  - Midnight dark tokens as the default, light tokens under :root[data-theme="light"]
#  - Sora / Source Sans 3 / JetBrains Mono
#  - a Dark/Light switch at the top right, remembered per page in localStorage
# Page-specific tokens (ok/bad, terminal, objective colors) keep their own
# light and dark values; only the shared base tokens and the accent change.
import re, sys, json

TR = '/root/.claude/projects/-home-claude/b07c80a6-7848-5baf-a7f5-a5a053ce037b/tool-results/'
PAGES = {
  'd1':   dict(src=TR+'artifact-98af8aa4-1793676118-f951.html', url='KrYojQYtNqGKiiYQQ1iPXy', dom='1'),
  'd2':   dict(src=TR+'artifact-80d20209-1793676119-8da4.html', url='Gud7EZdHrEfGnPxsyy29Fk', dom='2'),
  'd3':   dict(src=TR+'artifact-c2bcdb2c-1793669385-ca1f.html', url='R3jFowQmYqv5x3Kv2qYNoS', dom='3'),
  'd4':   dict(src=TR+'artifact-8885627c-1793669386-be63.html', url='HrmyyybMcjv3ut54g1ujfu', dom='4'),
  'flash':dict(src='/home/claude/mid/live-flash/index.html',      url='5k2Wz7MQAfUfX2TKcHmDpn'),
  'pbq':  dict(src=TR+'artifact-67aa5834-1793848274-4db1.html', url='DoTioR9UxmZx2fEP4NRhrz'),
  'ops':  dict(src=TR+'artifact-179d9907-1793469104-5e8b.html', url='3v8xDmJgJFy1BMsCyLEhCE'),
  'guide':dict(src=TR+'artifact-df89fc2b-1793744654-8965.html', url='Uc1LhLJ1q5Gm3g9ds554e6'),
  'hub':  dict(src='/home/claude/cysa-hub.html',                    url='PrxFejEDNFYfNB7V7Ahjvq'),
}

FONT = ('https://fonts.googleapis.com/css2?family=Sora:wght@500;600;700&'
        'family=Source+Sans+3:ital,wght@0,400;0,500;0,600;0,700;1,400&'
        'family=JetBrains+Mono:wght@400;500;600&display=swap')
F_HEAD = "'Sora','Segoe UI',system-ui,sans-serif"
F_BODY = "'Source Sans 3','Segoe UI',system-ui,sans-serif"
F_MONO = "'JetBrains Mono',ui-monospace,SFMono-Regular,Menlo,monospace"

# Midnight base, same values as the Notebook and Study Map.
MID_D = {'bg':'#0F1720','surface':'#17222D','surface-2':'#1C2935','border':'#2E4052',
         'text':'#E8EEF3','text-muted':'#A9B7C4','accent':'#5B9DFF','accent-ink':'#0B1220',
         'shadow':'0 1px 2px rgba(0,0,0,.35),0 8px 22px rgba(0,0,0,.3)'}
MID_L = {'bg':'#F5F8FC','surface':'#FFFFFF','surface-2':'#EEF3F9','border':'#D3DCE6',
         'text':'#13202D','text-muted':'#4A5866','accent':'#2F6FE0','accent-ink':'#FFFFFF',
         'shadow':'0 1px 2px rgba(20,24,28,.06),0 4px 14px rgba(20,24,28,.06)'}
DOM_D = {'1':'#7FB2FF','2':'#4FD1A5','3':'#F08CC0','4':'#F5B74A'}
DOM_L = {'1':'#2F6FE0','2':'#1F8A5C','3':'#A14B7A','4':'#9A6A00'}

def strip_wrapper(s):
    if s.startswith('<!doctype html><html><head><meta charset=utf8>'):
        s = s[s.index('<body>') + len('<body>'):]
        if s.startswith('\n'): s = s[1:]
        s = re.sub(r'</body></html>\s*$', '', s)
    return s

def parse_vars(block):
    return dict(re.findall(r'--([a-z0-9-]+)\s*:\s*([^;]+?)\s*;', block + ';'))

def emit(sel, v, scheme):
    body = '\n'.join('  --%s:%s;' % (k, x) for k, x in v.items())
    return '%s{\n%s\n  color-scheme:%s;\n}' % (sel, body, scheme)

def toggle_html(key):
    moon = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M21 13A9 9 0 1 1 11 3a7 7 0 0 0 10 10z"/></svg>'
    sun = '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>'
    return ('<div class="mn-mode" role="group" aria-label="Color mode">'
            '<button type="button" id="mn-dark" aria-pressed="true">%sDark</button>'
            '<button type="button" id="mn-light" aria-pressed="false">%sLight</button></div>' % (moon, sun))

def toggle_js(key):
    return ('<script>\n/* Color mode: dark by default, choice remembered in this browser. */\n'
            '(function(){var K=%s,R=document.documentElement;'
            'function set(m){if(m==="light")R.setAttribute("data-theme","light");else R.removeAttribute("data-theme");'
            'var d=document.getElementById("mn-dark"),l=document.getElementById("mn-light");'
            'if(d)d.setAttribute("aria-pressed",String(m!=="light"));if(l)l.setAttribute("aria-pressed",String(m==="light"));'
            'try{localStorage.setItem(K,m);}catch(e){}}'
            'var m="dark";try{m=localStorage.getItem(K)||"dark";}catch(e){}set(m);'
            'document.getElementById("mn-dark").onclick=function(){set("dark");};'
            'document.getElementById("mn-light").onclick=function(){set("light");};})();\n</script>\n') % json.dumps(key)

def toggle_css(placement):
    pos = ('.mn-mode{position:absolute;top:max(14px,env(safe-area-inset-top,0px));right:max(16px,env(safe-area-inset-right,0px));z-index:20}'
           if placement == 'abs' else '.mn-mode{margin-left:auto}')
    return ('\n/* Midnight color-mode switch */\n' + pos +
            '\n.mn-mode{display:flex;border:1.5px solid var(--mn-bd);border-radius:11px;overflow:hidden;background:var(--mn-sf)}'
            '\n.mn-mode button{font:600 13px ' + F_HEAD + ';padding:7px 11px;border:0;background:transparent;color:var(--mn-mu);cursor:pointer;display:flex;gap:6px;align-items:center;min-height:36px}'
            '\n.mn-mode button[aria-pressed="true"]{background:var(--mn-ac);color:var(--mn-ai)}'
            '\n.mn-mode button:focus-visible{outline:2px solid var(--mn-ac);outline-offset:-2px}\n')

def restyle(name, cfg):
    s = strip_wrapper(open(cfg['src']).read())
    guide = name == 'guide'
    # fonts
    s, n = re.subn(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com/css2\?[^"]*">',
                   '<link rel="stylesheet" href="%s">' % FONT, s, count=1)
    assert n == 1, name + ': font link'
    # token blocks
    m = re.search(r':root\{\s*--bg:[^}]*\}', s); assert m, name + ': light root'
    light = parse_vars(m.group(0))
    md = re.search(r':root\[data-theme="dark"\]\{[^}]*\}', s); assert md, name + ': dark root'
    dark = dict(light); dark.update(parse_vars(md.group(0)))
    if guide:
        base_d = {'bg':MID_D['bg'],'surface':MID_D['surface'],'fg':MID_D['text'],'muted':MID_D['text-muted'],'line':MID_D['border'],
                  'info':'#7FB2FF','info-soft':'#16263A','accent':'#F5B74A','accent-soft':'#2B2414','bar':'#3E5A78'}
        base_l = {'bg':MID_L['bg'],'surface':MID_L['surface'],'fg':MID_L['text'],'muted':MID_L['text-muted'],'line':MID_L['border'],
                  'info':'#2459B8','info-soft':'#E7EEF8','accent':'#8A5A00','accent-soft':'#FFF5E0','bar':'#9FB3C4'}
        fonts = {'f-display':F_HEAD,'f-body':F_BODY,'f-mono':F_MONO}
    else:
        base_d, base_l = dict(MID_D), dict(MID_L)
        if 'dom' in cfg:
            base_d['accent'] = DOM_D[cfg['dom']]; base_l['accent'] = DOM_L[cfg['dom']]
        if name == 'hub':
            base_d.update({'drill':DOM_D['1'],'d2':DOM_D['2'],'d3':DOM_D['3'],'d4':DOM_D['4'],'nb':'#7FD3EE','ops':'#B7A6FF','flash':'#F2A877','pbq':'#5FD4C8'})
            base_l.update({'drill':DOM_L['1'],'d2':DOM_L['2'],'d3':DOM_L['3'],'d4':DOM_L['4'],'nb':'#1F6F8B','ops':'#5B4BC4','flash':'#A0522D','pbq':'#0D7B86'})
        if 'radius' in light: base_d['radius'] = base_l['radius'] = '14px'
        fonts = {'font-display':F_MONO,'font-body':F_BODY,'font-head':F_HEAD}
    dark.update(base_d); dark.update(fonts); light.update(base_l); light.update(fonts)
    # switch colors, named so they work on every page's token set
    tk = (lambda v: {'mn-bd':v['line'],'mn-sf':v['surface'],'mn-mu':v['muted'],'mn-ac':v['info'],'mn-ai':'#0B1220' if v is dark else '#FFFFFF'}) if guide else \
         (lambda v: {'mn-bd':v['border'],'mn-sf':v['surface'],'mn-mu':v['text-muted'],'mn-ac':v['accent'],'mn-ai':v['accent-ink']})
    dark.update(tk(dark)); light.update(tk(light))
    dark['mn-mark'] = '#4a3b12'; light['mn-mark'] = '#FBF1D9'
    new_tokens = emit(':root', dark, 'dark') + '\n' + emit(':root[data-theme="light"]', light, 'light')
    s = s[:m.start()] + new_tokens + s[m.end():]
    # drop the old dark blocks (auto and forced)
    s, n1 = re.subn(r'@media \(prefers-color-scheme: ?dark\)\{:root:not\(\[data-theme="light"\]\)\{[^}]*\}\}\n?', '', s)
    s, n2 = re.subn(r':root\[data-theme="dark"\]\{[^}]*\}\n?', '', s)
    assert n1 >= 1 and n2 >= 1, name + ': old dark blocks %d %d' % (n1, n2)
    # hub search highlight had its own pair of dark rules
    s = s.replace('@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) .ghit mark{background:#4a3b12;}}\n', '')
    s = s.replace(':root[data-theme="dark"] .ghit mark{background:#4a3b12;}\n', '')
    s = s.replace('.ghit mark{background:#fbf1d9;', '.ghit mark{background:var(--mn-mark);')
    # headings in Sora; white-on-color chips get dark ink in dark mode
    extra = toggle_css('inline' if name == 'ops' else 'abs')
    if not guide:
        extra += 'h1,h2,h3{font-family:var(--font-head);letter-spacing:-.015em;}\nh1{font-weight:700;}\n'
    extra += (':root:not([data-theme="light"]) .otag,:root:not([data-theme="light"]) .obj[aria-pressed="true"],'
              ':root:not([data-theme="light"]) .dtag,:root:not([data-theme="light"]) .deck[aria-pressed="true"]{color:#0B1220;}\n')
    i = s.index('</style>'); s = s[:i] + extra + s[i:]
    # place the switch
    key = 'cysa:%s:theme' % name
    if name == 'ops':
        s, n = re.subn(r'(<nav class="nav" aria-label="Ops Lab">.*?</nav>)', lambda k: k.group(1) + '\n    ' + toggle_html(key), s, count=1, flags=re.S)
        assert n == 1, 'ops nav'
    else:
        i = s.index('</style>') + len('</style>')
        s = s[:i] + '\n' + toggle_html(key) + s[i:]
    # script goes last
    j = s.rfind('</script>') + len('</script>')
    s = s[:j] + '\n' + toggle_js(key) + s[j:]
    assert 'IBM Plex' not in s.split('<script')[0], name + ': leftover IBM Plex in CSS'
    return s

if __name__ == '__main__':
    for name, cfg in PAGES.items():
        out = restyle(name, cfg)
        open('/home/claude/mid/%s.html' % name, 'w').write(out)
        print(name, len(out))
