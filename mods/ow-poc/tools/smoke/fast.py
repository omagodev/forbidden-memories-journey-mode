#!/usr/bin/env python3
"""One entry for fast Journey Mode checks: list presets, list/run quick scenarios.

    python3 mods/ow-poc/tools/smoke/fast.py                 # help + preset table + quick list
    python3 mods/ow-poc/tools/smoke/fast.py presets         # every debug preset (ch1-N)
    python3 mods/ow-poc/tools/smoke/fast.py quick           # run the critical-path suite (~few minutes)
    python3 mods/ow-poc/tools/smoke/fast.py run NAME [...]  # one or more scenarios (no rebuild)
    python3 mods/ow-poc/tools/smoke/fast.py list            # all scenarios; quick ones marked *

Or via the build wrapper (validate + build + deploy, then smoke):

    mods/ow-poc/tools/fast.sh --quick                       # critical path only
    mods/ow-poc/tools/fast.sh wager_picker_open wager_bet1_win
    mods/ow-poc/tools/fast.sh all                           # full e2e (slow)

A single beat is usually 15-40 s: jump with a debug preset, skip dialogue, win/lose duels by debug.
Full chapter play-throughs are the e2e_* scenarios (minutes each); keep them for release, use --quick while iterating.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MOD = HERE.parent.parent
REPO = MOD.parent.parent
sys.path.insert(0, str(HERE))
import scenarios  # noqa: E402
import jm_smoke   # noqa: E402


def presets():
    j = json.load(open(MOD / "assets" / "journey.json"))
    rows = j.get("debug") or []
    print("%-4s %-48s stage stars anchor" % ("#", "name"))
    for i, p in enumerate(rows):
        print("%-4d %-48s %5s %5s %s" % (
            i + 1, p.get("name", "?"), p.get("stage", "-"), p.get("stars", "-"), p.get("anchor", "-")))
    print("%d presets (L1+R1+Up/Down in-game when debug.json exists; or \"preset\" in debug.json)." % len(rows))
    return 0


def list_sc():
    for k, v in scenarios.SCENARIOS.items():
        mark = "*" if v.get("quick") else ("!" if v.get("slow") else " ")
        print("%s %-28s %s" % (mark, k, v["desc"]))
    print("* = in --quick / fast.py quick; ! = slow (skipped by `all`)")
    return 0


def quick_names():
    return [k for k, v in scenarios.SCENARIOS.items() if v.get("quick") and not v.get("slow")]


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "help"
    if cmd in ("help", "-h", "--help"):
        print(__doc__.strip())
        print()
        presets()
        print()
        print("Quick suite (%d):" % len(quick_names()))
        for n in quick_names():
            print("  -", n, ":", scenarios.SCENARIOS[n]["desc"])
        return 0
    if cmd == "presets":
        return presets()
    if cmd == "list":
        return list_sc()
    if cmd == "quick":
        names = quick_names()
        if not names:
            print("no scenarios marked quick=True"); return 1
        print("quick suite: %s" % ", ".join(names))
        return jm_smoke.main(["jm_smoke.py", "run"] + names)
    if cmd == "run":
        if len(argv) < 3:
            print(__doc__); return 2
        return jm_smoke.main(["jm_smoke.py", "run"] + argv[2:])
    print(__doc__); return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
