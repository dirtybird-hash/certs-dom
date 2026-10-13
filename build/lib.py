import re,sys
class NB:
    def __init__(s,path): s.path=path; s.s=open(path).read(); s.n=0
    def _span(s,tid):
        a=s.s.find('{id:"%s",'%tid)
        if a<0: sys.exit("no topic "+tid+" in "+s.path)
        b=s.s.find("\n`}",a)
        return a,b
    def append(s,tid,html,before_gotcha=True):
        a,b=s._span(tid)
        body=s.s[a:b]
        k=body.rfind('<blockquote><span class="tag">Gotcha</span>')
        pos=a+k if (before_gotcha and k>0) else b
        s.s=s.s[:pos]+html.strip()+"\n"+s.s[pos:]; s.n+=1
    def after(s,tid,topic):
        a,b=s._span(tid)
        end=b+len("\n`}")
        # expect ",\n" after
        s.s=s.s[:end]+",\n"+topic.strip().rstrip(",")+s.s[end:]; s.n+=1
    def rep(s,o,n):
        if s.s.count(o)!=1: sys.exit("BAD rep in %s: %s (count %d)"%(s.path,o[:80],s.s.count(o)))
        s.s=s.s.replace(o,n); s.n+=1
    def gotcha(s,rows):
        k=s.s.rfind("</table></div>\n<p style=\"font-size:13px;color:var(--text-muted);\">")
        if k<0: sys.exit("no gotcha table end")
        s.s=s.s[:k]+rows.strip()+"\n"+s.s[k:]; s.n+=1
    def save(s): open(s.path,"w").write(s.s); print(s.path,"edits",s.n)
