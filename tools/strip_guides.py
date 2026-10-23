#!/usr/bin/env python3
"""Remove the Study Guide cards from the Security+ hub (repo/security-plus/index.html).

The five Study Guides are Claude docs living on claude.ai; they have no
public mirror, so their cards must not ship in the public repo build.
Run after tools/build_repo.py. Idempotent.
"""
import re
import sys
import pathlib

p = pathlib.Path(__file__).resolve().parent.parent / "repo" / "security-plus" / "index.html"
if not p.exists():
    # build_repo.py skips a cert whose sources are absent, so this page may not
    # have been produced this run. Nothing built means nothing to strip.
    print("skipped — repo/security-plus/index.html was not built this run")
    sys.exit(0)
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
