"""Parse the course flashcard files into decks.

James types these during class into S:\\CySA+\\flashcards (ROCKY's share; the
same folder is C:\\Users\\there\\StudyMaterials\\CySA+\\flashcards locally).
Three formats are in use and all three must keep working:

    q: question          question            question
    a: answer            answer              <blank>
                         more answer         A: answer
                                             A: more answer

Parsing is line-driven rather than block-driven. A blank line only ends a card
once an answer has been seen — that is what lets a question and its "A:" answer
be separated by a blank line without the question becoming an answerless card
and the answer becoming a question. Markers are case-insensitive, because the
early files used "a:" and the later ones use "A:".

Content is James's own transcription of his coursework. It is his to publish.

Usage:  python3 school_parse.py            -> writes school_cards.json
"""
import pathlib, json, re, sys

SRC = pathlib.Path('/mnt/user-data/uploads/s/CySA+/flashcards')
if not SRC.exists():                                   # older mount spelling
    SRC = pathlib.Path('/mnt/user-data/uploads/StudyMaterials/CySA+/flashcards')

DECKS = [
    ('Cryptography',              'Cryptographyflashcard.txt'),
    ('Managing Risk',             'ManagingRiskFlash.txt'),
    ('Public Key Infrastructure', 'PublicKeyInfrastructureFlash.txt'),
    ('OS Process Management',     'OS Process ManagementFlash.txt'),
    ('Malicious Techniques',      'Malicious Techniques & Procedures.txt'),
    ('Threat Intelligence',       'Threat Intelligence Information.txt'),
    ('Managing Network Settings', 'Managing Network Settings.txt'),
    ('Authentication',            'Authentication.txt'),
    ('Authorization',             'Authorization.txt'),
    ('Data Privacy',              'Data Privacy.txt'),
    ('Security & Network Monitoring', 'Security & Network Monitoring.txt'),
]

# Corrections are shown UNDER the original answer, never in place of it: the
# decks are James's own transcription and stay verbatim. Keyed by deck name and
# the start of the question. A key that matches no card is an error, so a
# correction cannot silently stop showing after a deck is edited.
CORRECTIONS = {
    ('Security & Network Monitoring', 'You are managing a Linux system and need to capture SSH traffic'):
        'Check the syntax: tcpdump -i ens33 -v -A -s0 port 22. The snapshot flag is -s0 '
        '(a zero, meaning no length limit), and the filter is "port 22" with no dash.',
    ('Security & Network Monitoring', 'Which is a core function of a SIEM system?'):
        'A SIEM\'s core functions are log aggregation, correlation and alerting. Analysts use '
        'a SIEM to hunt, but threat hunting is an analyst activity rather than what the SIEM itself does.',
    ('Security & Network Monitoring', 'Which splunk command determines which local host items'):
        'The full command is "splunk add monitor <path>", which tells a forwarder to collect a file or directory.',
    ('Authorization', 'You are configuring Windows Dynamic Access Control.'):
        'The abbreviation is CAP: Central Access Policy.',
}

ANS_MARK = re.compile(r'^\s*[Aa]\s*:\s*')
Q_MARK   = re.compile(r'^\s*[Qq]\s*:\s*')


def parse(text):
    cards, q, a, in_ans = [], [], [], False

    def flush():
        nonlocal q, a, in_ans
        qt = ' '.join(x.strip() for x in q if x.strip()).strip()
        at = '\n'.join(x.strip() for x in a if x.strip()).strip()
        if qt:
            cards.append({'q': qt, 'a': at or '(no answer recorded)'})
        q, a, in_ans = [], [], False

    for raw in text.replace('\r\n', '\n').replace('\r', '\n').split('\n'):
        line = raw.rstrip()
        if not line.strip():
            if in_ans:
                flush()
            continue
        if ANS_MARK.match(line):
            in_ans = True
            a.append(ANS_MARK.sub('', line))
        elif Q_MARK.match(line):
            if q:
                flush()
            q.append(Q_MARK.sub('', line))
        elif in_ans:
            a.append(line)
        elif q:
            a.append(line)
            in_ans = True
        else:
            q.append(line)
    flush()
    return cards


if __name__ == '__main__':
    out, missing = [], []
    for name, fname in DECKS:
        p = SRC / fname
        if not p.exists():
            missing.append(fname)
            continue
        cards = parse(p.read_text(encoding='utf-8', errors='replace'))
        for (dk, qstart), note in CORRECTIONS.items():
            if dk != name:
                continue
            hits = [c for c in cards if c['q'].startswith(qstart)]
            if len(hits) != 1:
                sys.exit(f'correction for {dk!r} / {qstart!r} matched {len(hits)} cards')
            hits[0]['note'] = note
        if not cards:
            print(f'{name:28} SKIPPED — file is empty')
            continue
        out.append({'deck': name, 'file': fname, 'cards': cards})
        multi = sum(1 for c in cards if '\n' in c['a'])
        print(f'{name:28} {len(cards):>3} cards  ({multi} multi-line)')

    if missing:
        print('\nnot found in', SRC, '->', ', '.join(missing), file=sys.stderr)

    json.dump(out, open(pathlib.Path(__file__).parent / 'school_cards.json', 'w'), indent=1)
    print('\ntotal:', sum(len(d['cards']) for d in out), 'cards in', len(out), 'decks')
