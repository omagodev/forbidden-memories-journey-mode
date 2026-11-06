#!/usr/bin/env python3
"""Checks the story data before a build: python3 mods/ow-poc/tools/validate_story.py   (exit 1 on any error).

journey.json: at most 64 flags and none twice, every flag a condition or effect names exists, every scene a rule points to (scene, then,
win / lose, yes / no) exists in every language, speakers are known, anchors exist in jm_painted.c, observers and time events point at real
script pages, sprite / prop files exist, debug presets are consistent.  lang/*/story.json: same scene ids and page counts in all languages.
lang/*/ui.json: the objective list is as long as journey.json's (the HUD indexes it)."""
import json, re, sys
from pathlib import Path

MOD = Path(__file__).resolve().parent.parent
A = MOD / "assets"
errors, warnings = [], []
err = lambda m: errors.append(m)

J = json.load(open(A / "journey.json"))
langs = sorted(p.name for p in (A / "lang").iterdir() if p.is_dir())
S = {l: {s["id"]: s for s in json.load(open(A / "lang" / l / "story.json"))["scripts"]} for l in langs}
UI = {l: json.load(open(A / "lang" / l / "ui.json")) for l in langs}
flags = J["flags"]
if len(flags) > 64: err("%d flags (max 64)" % len(flags))
if len(set(flags)) != len(flags): err("a flag is listed twice")
anchors = set(re.findall(r'\{"(\w+)",\s*\d+,\s*\d+(?:,\s*\d+)?\}', (MOD / "jm_painted.c").read_text()))
speakers = set(J["speakers"]) | {"narrator"}
npc_ids = {n["id"] for n in J["npcs"]}

def walk(node, path="$"):
    if isinstance(node, dict):
        for k, v in node.items():
            yield path, k, v
            yield from walk(v, path + "." + k)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk(v, "%s[%d]" % (path, i))

scenes_used = set()
LEGACY = ("$.locks", "$.triggers", "$.spots")      # the old 3D map's data: its flags (rex_won ...) are named on first use, not listed
for path, k, v in walk(J):
    if path.startswith(LEGACY): continue
    if k in ("needs", "lacks", "lacks_any") and isinstance(v, list):
        for f in v:
            if f not in flags: err("%s.%s: unknown flag %r" % (path, k, f))
    if k == "flags" and isinstance(v, list) and "debug" not in path and "flags" != path:
        for f in v:
            if isinstance(f, str) and f not in flags: err("%s.flags: unknown flag %r" % (path, f))
    if k in ("scene", "then") and isinstance(v, str): scenes_used.add((path, v))
    if k in ("anchor", "prop_anchor") and isinstance(v, str):
            bare = v.split(".", 1)[-1]
            if v not in anchors and bare not in anchors: err("%s: unknown anchor %r" % (path, v))
    if k == "warp" and isinstance(v, list):
            areas_ok = ("village", "cistern", "harbor", "ship_deck", "kingdom_beach", "kingdom_forest", "kingdom_mountain", "kingdom_meadow", "kingdom_desert", "kingdom_fair", "arena_village")
            bare = v[1].split(".", 1)[-1] if len(v) == 2 and isinstance(v[1], str) else None
            if len(v) != 2 or (v[1] not in anchors and bare not in anchors) or v[0] not in areas_ok: err("%s: bad warp %r" % (path, v))
    if k == "area" and isinstance(v, int) and ".when" in path:
        if v < 0 or v > 10: err("%s: unknown area %r" % (path, v))
    if k == "icon" and isinstance(v, str) and not (MOD / v).exists(): err("%s: icon file %s missing" % (path, v))
for l in langs:
    for path, sc in sorted(scenes_used):
        if sc not in S[l]: err("[%s] %s: scene %r does not exist" % (l, path, sc))
if J.get("intro") and any(J["intro"] not in S[l] for l in langs): err("intro scene missing")

# every language: same ids, same page counts, known speakers, text present
ref = langs[0]
for l in langs:
    if set(S[l]) != set(S[ref]): err("[%s] scene ids differ from [%s]: %s" % (l, ref, sorted(set(S[l]) ^ set(S[ref]))[:6]))
    for sid, s in S[l].items():
        if sid in S[ref] and len(s["pages"]) != len(S[ref][sid]["pages"]): err("[%s] %s: %d pages, [%s] has %d" % (l, sid, len(s["pages"]), ref, len(S[ref][sid]["pages"])))
        for i, p in enumerate(s["pages"]):
            if p.get("speaker") not in speakers: err("[%s] %s page %d: unknown speaker %r" % (l, sid, i, p.get("speaker")))
            if not p.get("text", "").strip(): err("[%s] %s page %d: empty text" % (l, sid, i))
            if len(p.get("text", "")) > 150: warnings.append("[%s] %s page %d: %d characters (the box shows about 4 lines of 28)" % (l, sid, i, len(p["text"])))
    if len(UI[l]["objectives"]) != len(J["objectives"]): err("[%s] ui.json has %d objectives, journey.json %d" % (l, len(UI[l]["objectives"]), len(J["objectives"])))

# painted: observers, time events, props, sprites
P = J.get("painted", {})
for o in P.get("observers", []):
    sc = S[ref].get(o["script"])
    if not sc: err("observer %s: script %r missing" % (o["npc"], o["script"])); continue
    for pg in o["pages"]:
        if pg >= len(sc["pages"]): err("observer %s: page %d past the end of %s" % (o["npc"], pg, o["script"]))
for t in P.get("time_events", []):
    sc = S[ref].get(t["script"])
    if not sc or t["page"] >= len(sc["pages"]): err("time event %s page %s does not exist" % (t["script"], t["page"]))
for f in ("painted.raw", "painted_col.bin", "painted_palms.raw", "painted_water.raw", "painted_cistern.raw", "painted_cistern_col.bin", "painted_cistern_occ.bin",
          "painted_arena.raw", "painted_arena_col.bin",
          "spr_rex.bin", "spr_bakura.bin", "spr_arena_crowd.bin", "prop_hatch_closed.raw", "prop_hatch_open.raw", "prop_torch_glow.raw"):
    if not (A / f).exists(): err("assets/%s missing" % f)
for n in J["npcs"]:
    if n.get("sprite") and not (A / ("spr_%s.bin" % n["sprite"])).exists() and not (A / n["sprite"]).exists(): warnings.append("npc %s: sprite file %s not found" % (n["id"], n["sprite"]))
for o in J.get("objects", []):
    pr = {"hatch": "hatch_closed"}.get(o.get("prop"), o.get("prop"))
    if pr and not (A / ("prop_%s.raw" % pr)).exists(): err("object %s: prop_%s.raw missing" % (o["id"], pr))
for o in P.get("observers", []):
    for kind in ((o["sprite"],) if o.get("sprite") else ()):
        if not (A / ("spr_mago_%s.bin" % kind)).exists() and not (A / ("spr_%s.bin" % kind)).exists(): err("observer sprite %s missing" % kind)
    if not (A / ("prop_%s.raw" % o["overlay"])).exists(): err("observer overlay prop_%s.raw missing" % o["overlay"])
# NPC talk rules: duel rules need a win scene; every NPC has a rule for the stage ranges they are visible in (warn only)
for n in J["npcs"]:
    for t in n.get("talk", []):
        if t.get("duel") and "win" not in t: err("npc %s: a duel rule without a win result (%s)" % (n["id"], t.get("scene")))
        if t.get("duel") and "lose" not in t: warnings.append("npc %s: duel rule %s without a lose result" % (n["id"], t.get("scene")))
# the journal: every quest has a title, an objective and a reward in every language; every line's text index exists
for l in langs:
    u = UI[l]
    nq = len(J["journal"])
    for key in ("quest_titles", "quest_objectives", "quest_rewards"):
        if len(u[key]) != nq: err("[%s] ui.json %s has %d entries, the journal %d quests" % (l, key, len(u[key]), nq))
    if len(u["items"]) != len(J["items"]): err("[%s] ui.json items has %d names, journey.json %d items" % (l, len(u["items"]), len(J["items"])))
    for q in J["journal"]:
        for ln in q.get("lines", []):
            if "text" in ln and ln["text"] >= len(u["quest_steps"]): err("[%s] journal %s: step text %d does not exist" % (l, q["id"], ln["text"]))
for a in J.get("auto", []):
    if "stage_lt" not in a["when"]: err("auto rule %s has no stage_lt: it would run again" % a["scene"])
# debug presets
for i, d in enumerate(J.get("debug", [])):
    for f in d.get("flags", []):
        if f not in flags: err("debug preset %d: unknown flag %r" % (i, f))
    a = d.get("anchor")
    if a and a not in anchors and a.split(".", 1)[-1] not in anchors: err("debug preset %d: unknown anchor %r" % (i, a))
for w in warnings: print("warn:", w)
for e in errors: print("ERROR:", e)
print("validate_story: %d scenes (%s), %d flags, %d errors, %d warnings" % (len(S[ref]), "/".join(langs), len(flags), len(errors), len(warnings)))
sys.exit(1 if errors else 0)
