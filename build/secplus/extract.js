// Pull drill and acronym data out of the Security+ pages without running them.
// Each array literal is located by its "var NAME = [" line and evaluated alone.
const fs = require('fs'), path = require('path'), vm = require('vm');
const dir = process.argv[2];
function grab(file, name){
  const s = fs.readFileSync(path.join(dir, file), 'utf8');
  const i = s.indexOf('var ' + name + ' = ');
  if (i < 0) throw new Error(name + ' not in ' + file);
  let j = s.indexOf('[', i), depth = 0, inStr = null, k = j;
  for (; k < s.length; k++){
    const c = s[k];
    if (inStr){ if (c === '\\'){ k++; continue; } if (c === inStr) inStr = null; continue; }
    if (c === '"' || c === "'" || c === '`'){ inStr = c; continue; }
    if (c === '[' || c === '{') depth++;
    else if (c === ']' || c === '}'){ depth--; if (depth === 0) break; }
  }
  return vm.runInNewContext('(' + s.slice(j, k + 1) + ')');
}
const out = {acr: grab('acronym-drill.html', 'ACR'), drills: {}};
for (let d = 1; d <= 5; d++){
  const f = 'domain' + d + '-drill.html';
  out.drills[d] = {F: grab(f, 'FLASHCARDS'), Q: grab(f, 'QUIZ'), S: grab(f, 'SCENARIOS')};
}
process.stdout.write(JSON.stringify(out));
