#!/usr/bin/env python3
"""Install one language: assets/lang/<code>/story.json and ui.json, and list it in languages.json.

The mod needs only {id, pages:[{speaker, text, ask?, label?}]} for each script, so the other parts of
the story content file (decks, NPC tables, chapters) are left out.  The interface file is copied as it
is.  The first language in languages.json is the default of a new journey.

Usage: import_lang.py CODE story_content.json ui.json
"""
import json
import os
import sys

code, story, ui = sys.argv[1:4]
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "lang")
out = os.path.join(root, code)
os.makedirs(out, exist_ok=True)
d = json.load(open(story))
scripts = [{"id": s["id"], "pages": s["pages"]} for s in d["scripts"]]
json.dump({"scripts": scripts}, open(os.path.join(out, "story.json"), "w"), separators=(",", ":"))
u = json.load(open(ui))
json.dump(u, open(os.path.join(out, "ui.json"), "w"), indent=1, ensure_ascii=True)
codes_file = os.path.join(root, "languages.json")
codes = json.load(open(codes_file)) if os.path.exists(codes_file) else []
if code not in codes:
    codes.append(code)
json.dump(codes, open(codes_file, "w"))
print("%s: %d scripts, %d pages" % (code, len(scripts), sum(len(s["pages"]) for s in scripts)))
