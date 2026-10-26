"""Recover d<N>_data.py from a published Drill page.

The generator escapes text (html.escape, quote=False, then " -> &quot;) and turns
newlines in answers into <br>. This reverses both. Proof of losslessness is not
here: it is drill_page.py regenerating the published page byte for byte.

Usage: python3 recover_drill.py <N> <published.html> [out.py]
"""
import sys, re, json, html, pathlib

def unrich(s):
    return html.unescape(s.replace('<br>', '\n'))

def arrays(page):
    out = {}
    for k in ['FLASH', 'QUIZ', 'SCEN', 'OBJTITLE', 'OBJS']:
        m = re.search(rf'^var {k} = (.*);$', page, flags=re.M)
        out[k] = json.loads(m.group(1))
    return out

def recover(page):
    a = arrays(page)
    flash = [(x['o'], unrich(x['f']), unrich(x['b'])) for x in a['FLASH']]
    quiz = [(x['o'], unrich(x['q']), [unrich(c) for c in x['c']], x['a'], unrich(x['e'])) for x in a['QUIZ']]
    scen = [(x['o'], unrich(x['s']), unrich(x['q']), [unrich(c) for c in x['c']], x['a'], unrich(x['e'])) for x in a['SCEN']]
    objt = {k: unrich(v) for k, v in a['OBJTITLE'].items()}
    return flash, quiz, scen, objt

def emit(n, flash, quiz, scen, objt, src):
    L = [f'"""CySA+ Domain {n} drill content — objectives {min(objt)} to {max(objt)}.',
         '',
         "Original prose written against CompTIA's published CS0-003 objectives",
         '(build/cysa-spine.json). Class decks and transcripts are read for scope',
         'only; no instructor wording or Knowledge Check questions are reproduced,',
         'because the repo is public.',
         '',
         'Shapes:',
         '    FLASHCARDS  (objective, front, back)',
         '    QUIZ        (objective, question, [4 choices], answer_index, explanation)',
         '    SCENARIOS   (objective, situation, question, [4 choices], answer_index, explanation)',
         '',
         f'Recovered 2026-10-25 from the published page ({src}) after the session that',
         'built it ended without committing its source. drill_page.py regenerates that',
         'page byte for byte from this file, which is the proof the recovery is lossless.',
         '"""', '', 'FLASHCARDS = [']
    for o, f, b in flash:
        L.append(f' ({o!r},\n  {f!r},\n  {b!r}),')
    L += [']', '', 'QUIZ = [']
    for o, q, c, a, e in quiz:
        L.append(f' ({o!r},\n  {q!r},\n  {c!r},\n  {a},\n  {e!r}),')
    L += [']', '', 'SCENARIOS = [']
    for o, s, q, c, a, e in scen:
        L.append(f' ({o!r},\n  {s!r},\n  {q!r},\n  {c!r},\n  {a},\n  {e!r}),')
    L += [']', '', 'OBJTITLE = ' + json.dumps(objt, ensure_ascii=False), '']
    return '\n'.join(L)

if __name__ == '__main__':
    n, src = sys.argv[1], sys.argv[2]
    out = pathlib.Path(sys.argv[3] if len(sys.argv) > 3 else f'd{n}_data.py')
    page = pathlib.Path(src).read_text(encoding='utf-8')
    f, q, s, o = recover(page)
    out.write_text(emit(n, f, q, s, o, src.split('/')[-1]), encoding='utf-8')
    print(f'{out}: flash {len(f)} | quiz {len(q)} | scen {len(s)} | objectives {sorted(o)}')
