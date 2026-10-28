"""Generate the Simple Flash page from school_cards.json.

The page design lives in kit/sf_template.html, which was derived from the
published page itself, so regenerating cannot drift from what shipped. Three
markers are filled:

    __DECKCSS__   one color rule pair per deck
    __DECKBTNS__  the filter chips
    __DECKS__     the card data as JSON

Cards may carry a 'note' (school_parse.CORRECTIONS): shown under the original
answer as "Check: ...", so a wrong card is flagged without editing James's text.

Storage key: cysa:schoolflash:v1 -> {status:{"<deck>|<question prefix>": ...}}

Adding a deck means one line in school_parse.py's DECKS and rerunning both
scripts. Color slots are generated, so no CSS edit is needed.

Usage:  python3 school_parse.py && python3 school_page.py
"""
import json, html, pathlib

HERE = pathlib.Path(__file__).parent
decks = json.load(open(HERE / 'school_cards.json'))
SLOTS = 13                      # --d0 .. --d12 defined in the template


def esc(s):
    return html.escape(s, quote=False).replace('"', '&quot;')


DATA = [{'deck': esc(d['deck']),
         'file': esc(d['file']),
         'cards': [{'q': esc(c['q']),
                    'a': esc(c['a']).replace('\n', '<br>')
                         + (f'<span class="fixnote">Check: {esc(c["note"])}</span>' if c.get('note') else '')}
                   for c in d['cards']]}
        for d in decks]
TOTAL = sum(len(d['cards']) for d in DATA)

FIXCSS = ('.fixnote{display:block;margin-top:12px;padding:9px 12px;border-left:3px solid var(--accent);'
          'background:var(--bg);border-radius:0 8px 8px 0;font-size:13.5px;color:var(--text-muted);}\n')

deck_css = FIXCSS + ''.join(
    f'.deck[data-i="{i}"][aria-pressed="true"]{{background:var(--d{i % SLOTS});}}\n'
    f'.dtag[data-i="{i}"]{{background:var(--d{i % SLOTS});}}\n'
    for i in range(len(DATA)))

deck_btns = ''.join(
    f'<button class="deck" data-i="{i}" aria-pressed="true">'
    f'{d["deck"]} &middot; {len(d["cards"])}</button>'
    for i, d in enumerate(DATA))

page = (pathlib.Path(HERE / 'kit' / 'sf_template.html').read_text(encoding='utf-8')
        .replace('__DECKCSS__', deck_css.rstrip())
        .replace('__DECKBTNS__', deck_btns)
        .replace('__DECKS__', json.dumps(DATA, ensure_ascii=False)))

out = pathlib.Path('/home/claude/cysa-school-flashcards.html')
out.write_text(page, encoding='utf-8')
print(f'written {out}  {len(page)//1024} KB | {len(DATA)} decks, {TOTAL} cards')
if len(DATA) > SLOTS:
    print(f'WARNING: {len(DATA)} decks but only {SLOTS} color slots — colors repeat')
