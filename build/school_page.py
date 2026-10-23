"""Generate the Simple Flash page from school_cards.json.

The page design lives in kit/sf_template.html, which was derived from the
published page itself, so regenerating cannot drift from what shipped. Three
markers are filled:

    __DECKCSS__   one colour rule pair per deck
    __DECKBTNS__  the filter chips
    __DECKS__     the card data as JSON

Storage key: cysa:schoolflash:v1 -> {status:{"<deck>|<question prefix>": ...}}

Adding a deck means one line in school_parse.py's DECKS and rerunning both
scripts. Colour slots are generated, so no CSS edit is needed.

Usage:  python3 school_parse.py && python3 school_page.py
"""
import json, html, pathlib

HERE = pathlib.Path(__file__).parent
decks = json.load(open(HERE / 'school_cards.json'))
SLOTS = 10                      # --d0 .. --d9 defined in the template


def esc(s):
    return html.escape(s, quote=False).replace('"', '&quot;')


DATA = [{'deck': esc(d['deck']),
         'file': esc(d['file']),
         'cards': [{'q': esc(c['q']), 'a': esc(c['a']).replace('\n', '<br>')}
                   for c in d['cards']]}
        for d in decks]
TOTAL = sum(len(d['cards']) for d in DATA)

deck_css = ''.join(
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
    print(f'WARNING: {len(DATA)} decks but only {SLOTS} colour slots — colours repeat')
