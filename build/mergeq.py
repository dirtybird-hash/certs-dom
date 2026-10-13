import json,re
Q=json.load(open('/home/claude/audit/newq.json'))
counts={}
import sys
for d in [int(x) for x in sys.argv[1:]]:
    p='/home/claude/domain%d-drill.html'%d; s=open(p).read()
    assert 'qEl.textContent = q.q' in s
    for kind,var in (('quiz','QUIZ'),('scenario','SCENARIOS')):
        a=s.find('var %s = ['%var); b=s.find('\n];',a)
        body=s[a:b]
        ids=[int(x) for x in re.findall(r'\{id:(\d+),obj:',body)]
        n=max(ids)
        add=[x for x in Q if x['domain']==d and x['kind']==kind]
        lines=''
        for x in add:
            n+=1
            assert len(x['c'])==4 and 0<=x['a']<4 and x['obj'].startswith('%d.'%d)
            lines+=',\n {id:%d,obj:%s,q:%s,c:%s,a:%d,e:%s}'%(n,json.dumps(x['obj']),json.dumps(x['q'],ensure_ascii=False),json.dumps(x['c'],ensure_ascii=False),x['a'],json.dumps(x['e'],ensure_ascii=False))
        s=s[:b].rstrip().rstrip(',')+lines+s[b:]
        counts[(d,var)]=len(ids)+len(add)
    open(p,'w').write(s)
print(counts)
