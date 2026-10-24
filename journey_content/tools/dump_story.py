#!/usr/bin/env python3
"""Writes a readable story_readable.md (all dialogue, in play order per chapter) next to story.json."""
import json, os
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
s = json.load(open(os.path.join(ROOT, "story.json"), encoding="utf-8"))
spk = s["speakers"]
out = ["# JOURNEY MODE - story script (generated from story.json)\n"]
by_ch = {}
for sc in s["scripts"]: by_ch.setdefault(sc["chapter"], []).append(sc)
for ch in sorted(by_ch):
    title = next((c["title"] for c in s["chapters"] if c["n"] == ch), "Epilogue / post-game")
    out.append("\n## Chapter %d - %s\n" % (ch, title) if ch <= 8 else "\n## Post-game\n")
    for sc in by_ch[ch]:
        out.append("\n### %s%s\n_%s_\n" % (sc["id"], "  (legacy %d)" % sc["legacy_id"] if sc.get("legacy_id") is not None else "", sc["desc"]))
        for p in sc["pages"]:
            who = p["label"] if p["speaker"] == "narrator" else spk[p["speaker"]]["name"]
            out.append("- **%s**: %s%s" % (who, p["text"], "  _[Duel? Yes/No]_" if p.get("ask") else ""))
open(os.path.join(ROOT, "story_readable.md"), "w", encoding="utf-8").write("\n".join(out) + "\n")
print("wrote story_readable.md")
