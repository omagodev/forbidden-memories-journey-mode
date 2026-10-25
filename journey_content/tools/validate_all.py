#!/usr/bin/env python3
"""Runs everything: strict JSON parse of every .json file, check_story.py, check_decks.py."""
import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
ok = True
for fn in sorted(os.listdir(ROOT)):
    if fn.endswith(".json"):
        try:
            json.load(open(os.path.join(ROOT, fn), encoding="utf-8")); print("json ok  ", fn)
        except Exception as e:
            ok = False; print("json FAIL", fn, e)
for tool in ("check_story.py", "check_decks.py"):
    print("--", tool)
    ok &= subprocess.call([sys.executable, os.path.join(HERE, tool)]) == 0
print("ALL OK" if ok else "FAILED"); sys.exit(0 if ok else 1)
