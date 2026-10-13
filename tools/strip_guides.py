#!/usr/bin/env python3
"""Remove the Study Guide cards from repo/index.html.

The five Study Guides are Claude docs living on claude.ai; they have no
public mirror, so their cards must not ship in the public repo build.
Run after tools/build_repo.py. Idempotent.
"""
import re
import sys
import pathlib

p = pathlib.Path(__file__).resolve().parent.parent / "repo" / "index.html"
t = p.read_text()

# each guide card is: ,{k:"guide", ... url:"https://claude.ai/..."}  immediately
# before the closing ] of that domain's tools array.
pat = re.compile(r',\s*\{k:"guide".*?url:"https://claude\.ai/[^"]*"\}', re.S)
t2, n = pat.subn("", t)

left = t2.count("claude.ai")
p.write_text(t2)
print(f"stripped {n} guide cards; claude.ai references remaining: {left}")
if n and left:
    sys.exit(1)
