#!/usr/bin/env python3
"""Writes story_readable.pt.md (all dialogue of story.pt.json in play order) next to story.pt.json. Usage: dump_story_pt.py [DIR] [lang]"""
import json, os, sys
D = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
lang = sys.argv[2] if len(sys.argv) > 2 else "pt"
s = json.load(open(os.path.join(D, "story.%s.json" % lang), encoding="utf-8")); spk = s["speakers"]
out = ["# JOURNEY MODE - story script (%s, generated from story.%s.json)\n" % (lang, lang)]
by = {}
for sc in s["scripts"]: by.setdefault(sc["chapter"], []).append(sc)
for ch in sorted(by):
    out.append("\n## %s\n" % (("Capitulo %d" % ch) if ch <= 8 else "Pos-jogo"))
    for sc in by[ch]:
        out.append("\n### %s\n" % sc["id"])
        for p in sc["pages"]:
            who = p["label"] if p["speaker"] == "narrator" else spk[p["speaker"]]["name"]
            out.append("- **%s**: %s%s" % (who, p["text"], "  _[ask]_" if p.get("ask") else ""))
open(os.path.join(D, "story_readable.%s.md" % lang), "w", encoding="utf-8").write("\n".join(out) + "\n")
print("wrote story_readable.%s.md" % lang)
