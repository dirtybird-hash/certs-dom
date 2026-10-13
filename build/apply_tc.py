import json,sys
sys.path.insert(0,'/home/claude/build/acr')
from lib import NB
tot={'a':0,'r':0,'g':0}
for d in range(1,6):
    p='/home/claude/audit/tc-d%d.json'%d
    try: patch=json.load(open(p))
    except FileNotFoundError: print('no patch d%d'%d); continue
    nb=NB('/home/claude/domain%d-notebook.html'%d)
    for r in patch.get('reps',[]):
        assert '`' not in r['new'] and '${' not in r['new'], ('backtick',d,r['new'][:60])
        nb.rep(r['old'],r['new']); tot['r']+=1
    for a in patch.get('appends',[]):
        assert '`' not in a['html'] and '${' not in a['html'], ('backtick',d,a['topic'])
        nb.append(a['topic'],a['html']); tot['a']+=1
    rows=patch.get('gotcha_rows',[])
    if rows:
        nb.gotcha('\n'.join(rows)); tot['g']+=len(rows)
    nb.save()
print('totals',tot)
