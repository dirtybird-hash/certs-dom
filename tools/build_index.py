"""Regenerate the global search index inside security-toolkit.html from every domain notebook.
Run after editing any notebook, before publishing the hub or building the repo."""
import json, re, subprocess, pathlib, glob
root = pathlib.Path('/home/claude')
js = r"""
const fs=require('fs'); const out=[];
for (const f of process.argv.slice(1)) {
  const d=f.match(/domain(\d)-notebook/)[1];
  const c=fs.readFileSync(f,'utf8');
  const T=eval(c.match(/var TOPICS = (\[[\s\S]*?\n\]);/)[1]);
  T.forEach(t=>out.push({d:d,o:t.obj,id:t.id,t:t.title,h:t.html.trim()}));
}
process.stdout.write(JSON.stringify(out));
"""
files = sorted(glob.glob(str(root/'domain[0-9]-notebook.html')))
data = subprocess.run(['node','-e',js,*files],capture_output=True,text=True,check=True).stdout
data = data.replace('</', '<\\/')          # never let note content close the <script>
hub = root/'security-toolkit.html'
s = hub.read_text(encoding='utf-8')
new, n = re.subn(r'/\*INDEX-START\*/.*?/\*INDEX-END\*/',
                 lambda m: '/*INDEX-START*/var INDEX = ' + data + ';/*INDEX-END*/', s, flags=re.S)
assert n == 1, 'index markers not found exactly once'
hub.write_text(new, encoding='utf-8')
items = json.loads(data.replace('<\\/','</'))
print(f"index rebuilt: {len(items)} topics from {len(files)} notebooks, {len(data)//1024} KB")
