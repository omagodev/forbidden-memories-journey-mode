#!/usr/bin/env python3
"""InsetoKaiba's lines (EN/PT): the catchphrase only as the opening of a *_first scene (the first talk after arriving in a place),
exactly once there; 'macaco'/'monkey' nowhere else in the story; his village scenes (before Simon explains the Kingdom) say
nothing of invitations, stars, the Kingdom or Pegasus."""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
CP = {"pt": "Eu vim ver o macaco.", "en": "I came to see the monkey."}
WORD = {"pt": re.compile(r"macac", re.I), "en": re.compile(r"monkey", re.I)}
SPOIL = re.compile(r"convite|invitation|estrela|star|reino|kingdom|pegasus", re.I)
bad = 0
for lang in ("en", "pt"):
    s = json.load(open(os.path.join(HERE, "..", "assets", "lang", lang, "story.json")))["scripts"]
    for x in s:
        texts = [p["text"] for p in x["pages"]]
        hits = sum(len(WORD[lang].findall(t)) for t in texts)
        if x["id"].startswith("rv_inseto_") and x["id"].endswith("_first"):
            if hits != 1 or CP[lang] not in texts[0]: print("FAIL %s %s: catchphrase must open the scene once" % (lang, x["id"])); bad += 1
        elif hits: print("FAIL %s %s: '%s' outside the arrival catchphrase" % (lang, x["id"], WORD[lang].pattern)); bad += 1
        if x["id"].startswith("rv_inseto_village") and any(SPOIL.search(t) for t in texts):
            print("FAIL %s %s: village lines spoil what Simon explains" % (lang, x["id"])); bad += 1
j = json.load(open(os.path.join(HERE, "..", "assets", "journey.json")))
for n in j["npcs"]:
    if n["id"].startswith("inseto_") and n["id"] not in ("inseto_kaiba", "inseto_gate"):
        t = n["talk"]
        if not (t[0]["scene"].endswith("_first") and "inseto_here" in t[0]["when"].get("lacks", []) and "inseto_here" in t[0]["effects"]["flags"]):
            print("FAIL %s: first talk per arrival not guarded by inseto_here" % n["id"]); bad += 1
print("%d failures" % bad)
sys.exit(1 if bad else 0)
