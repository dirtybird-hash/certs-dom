import re,sys; sys.path.insert(0,"/home/claude/build/acr"); from extras import F,Q,P
def js(s): return s.replace('\\','\\\\').replace('"','\\"')
for d in range(1,6):
    p=f"/home/claude/domain{d}-drill.html"; s=open(p).read()
    fa=s.index("var FLASHCARDS"); qa=s.index("var QUIZ"); sa=s.index("var SCENARIOS")
    f=s[fa:qa]; ids=[int(x) for x in re.findall(r'\{id:(\d+),obj:',f)]; n=max(ids)
    add="".join(',\n {id:%d,obj:"%s",t:"%s",d:"%s"}'%(n+i+1,o,js(t),js(dd)) for i,(o,t,dd) in enumerate(F[d]))
    end=s.index("\n];",fa); s=s[:end]+add+s[end:]
    qa=s.index("var QUIZ"); q=s[qa:s.index("var SCENARIOS")]; qn=max(int(x) for x in re.findall(r'\{id:(\d+),obj:',q))
    addq="".join(',\n {id:%d,obj:"%s",q:"%s",c:[%s],a:%d,e:"%s"}'%(qn+i+1,o,js(qq),",".join('"%s"'%js(c) for c in cs),a,js(e)) for i,(o,qq,cs,a,e) in enumerate(Q[d]))
    end=s.index("\n];",qa); s=s[:end]+addq+s[end:]
    total=n+len(F[d])
    s=re.sub(r'(<p class="lede">)%d( term cards)'%n, r'\g<1>%d\2'%total, s)
    s=s.replace('<span id="flash-pos">1 / %d</span>'%n,'<span id="flash-pos">1 / %d</span>'%total)
    s=s.replace("(60-Object.keys","(FLASHCARDS.length-Object.keys")
    open(p,"w").write(s); print(p,"flash",total,"quiz",qn+len(Q[d]))
    p=f"/home/claude/domain{d}-match.html"; m=open(p).read()
    pa=m.index("var PAIRS"); end=m.index("\n];",pa)
    addp="".join(',\n{id:"x%d",obj:"%s",term:"%s",def:"%s"}'%(i+1,o,js(t),js(df)) for i,(o,t,df) in enumerate(P[d]))
    m=m[:end]+addp+m[end:]; open(p,"w").write(m)
    print(p,"pairs",len(re.findall(r'\{id:"[a-z]+\d+",obj:',m[pa:m.index("\n];",pa)])))
