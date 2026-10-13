import json,re,string
# ---- Match pairs ----
letters=list(string.ascii_lowercase)
for d in range(1,6):
    try: patch=json.load(open('/home/claude/audit/tcm-d%d.json'%d))
    except FileNotFoundError: continue
    p='/home/claude/domain%d-match.html'%d; s=open(p).read()
    a=s.find('PAIRS'); b=s.find('\n];',a)
    body=s[a:b]
    used=set(re.findall(r'\{id:"([a-z]+)(\d+)",',body))
    # pick a fresh prefix not used
    prefixes=set(x[0] for x in used)
    pre=next(l for l in ['z','y','w','v','u','t'] if l not in prefixes)
    lines=''
    for i,pair in enumerate(patch['pairs'],1):
        assert '`' not in pair['def'] and '${' not in pair['def']
        lines+=',\n{id:"%s%d",obj:%s,term:%s,def:%s}'%(pre,i,json.dumps(pair['obj']),json.dumps(pair['term'],ensure_ascii=False),json.dumps(pair['def'],ensure_ascii=False))
    s=s[:b].rstrip().rstrip(',')+lines+s[b:]
    open(p,'w').write(s)
    print('match d%d +%d (prefix %s) total %d'%(d,len(patch['pairs']),pre,len(re.findall(r'\{id:"',s[a:b+len(lines)]))))
# ---- Drill flashcards + quiz ----
for d in range(1,6):
    try: patch=json.load(open('/home/claude/audit/tcd-d%d.json'%d))
    except FileNotFoundError: continue
    p='/home/claude/domain%d-drill.html'%d; s=open(p).read()
    for key,items in (('FLASHCARDS',patch.get('flashcards',[])),('QUIZ',patch.get('quiz',[]))):
        if not items: continue
        a=s.find(key+' = [')
        if a<0: a=s.find('var %s = ['%key)
        assert a>0,(d,key)
        b=s.find('\n];',a)
        ids=[int(x) for x in re.findall(r'\{id:(\d+),obj:',s[a:b])]
        n=max(ids); lines=''
        for x in items:
            n+=1
            assert '`' not in json.dumps(x) and '${' not in json.dumps(x)
            assert x['obj'].startswith('%d.'%d),(d,x['obj'])
            if key=='FLASHCARDS':
                lines+=',\n {id:%d,obj:%s,t:%s,d:%s}'%(n,json.dumps(x['obj']),json.dumps(x['t'],ensure_ascii=False),json.dumps(x['d'],ensure_ascii=False))
            else:
                assert len(x['c'])==4 and 0<=x['a']<4
                lines+=',\n {id:%d,obj:%s,q:%s,c:%s,a:%d,e:%s}'%(n,json.dumps(x['obj']),json.dumps(x['q'],ensure_ascii=False),json.dumps(x['c'],ensure_ascii=False),x['a'],json.dumps(x['e'],ensure_ascii=False))
        s=s[:b].rstrip().rstrip(',')+lines+s[b:]
        print('drill d%d %s +%d -> %d'%(d,key,len(items),n))
    open(p,'w').write(s)
