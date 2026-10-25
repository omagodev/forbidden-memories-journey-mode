#!/usr/bin/env python3
"""Validates story.json: structure, references, text fit (3 lines x 32 glyphs), charset, tokens, rewards vs. cards.
Usage: python3 check_story.py [story.json] [decks.json] [card-catalog.csv]   Exit 0 = ok."""
import csv, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
STORY = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "story.json")
DECKS = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "decks.json")
CAT = sys.argv[3] if len(sys.argv) > 3 else "/workspace/study/fmrecomp/fork/notes/card-catalog.csv"
LINE, LINES, NAME_W = 32, 3, 10
ALLOWED = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,!?'-")
TOKEN = re.compile(r"\{([^{}]*)\}")

def expand(text, errs, where):
    """Return the worst-case plain string and report bad tokens / characters."""
    def rep(m):
        t = m.group(1)
        if t == "name": return "N" * NAME_W
        if "|" in t:
            a, b = t.split("|")
            if not a or not b or "{" in t: errs.append("%s: bad gender token {%s}" % (where, t))
            return max(a, b, key=len)
        errs.append("%s: unknown token {%s}" % (where, t)); return ""
    out = TOKEN.sub(rep, text)
    if "{" in out or "}" in out or "|" in out: errs.append("%s: stray brace/pipe" % where)
    bad = sorted({c for c in out if c not in ALLOWED})
    if bad: errs.append("%s: characters not in the font: %r" % (where, "".join(bad)))
    return out

def wrap(s):
    lines, cur = [], ""
    for w in s.split():
        if len(w) > LINE: return None
        t = (cur + " " + w) if cur else w
        if len(t) <= LINE: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def cond_ok(when, flags, stages, where, errs):
    for k in when:
        if k not in ("stage", "flags_all", "flags_any", "flags_none"): errs.append("%s: unknown condition %s" % (where, k))
    for k in ("flags_all", "flags_any", "flags_none"):
        for f in when.get(k, []):
            if f not in flags: errs.append("%s: unknown flag %s" % (where, f))
    st = when.get("stage")
    if st and not (len(st) == 2 and st[0] <= st[1]): errs.append("%s: bad stage range %s" % (where, st))

def main():
    s = json.load(open(STORY, encoding="utf-8"))
    cat = {}
    with open(CAT, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f): cat[r["name"]] = int(r["id"])
    decks = json.load(open(DECKS, encoding="utf-8")) if os.path.exists(DECKS) else None
    custom = {c["name"] for c in decks.get("custom_cards", [])} if decks else set()
    errs, warns = [], []
    flags = {f["name"] for f in s["flags"]}
    bits = [f["bit"] for f in s["flags"]]
    if len(set(bits)) != len(bits) or max(bits) > 30: errs.append("flag bits clash or exceed 30")
    for f in s["flags"]:
        if f["value"] != 1 << f["bit"]: errs.append("flag %s value/bit mismatch" % f["name"])
    stages = {x["stage"] for x in s["stages"]}
    areas = {a["id"] for a in s["areas"]}
    spk = s["speakers"]
    scripts = {}
    for sc in s["scripts"]:
        if sc["id"] in scripts: errs.append("duplicate script id " + sc["id"])
        scripts[sc["id"]] = sc
    pages = 0; maxlen = 0; hist = {1: 0, 2: 0, 3: 0}
    for sc in s["scripts"]:
        if not sc["pages"]: errs.append(sc["id"] + ": no pages")
        for i, p in enumerate(sc["pages"]):
            where = "%s[%d]" % (sc["id"], i); pages += 1
            if p["speaker"] not in spk: errs.append(where + ": unknown speaker " + p["speaker"])
            if p["speaker"] == "narrator":
                lab = p.get("label")
                if not lab: errs.append(where + ": narrator page needs a label")
                else: expand(lab, errs, where + " label")
                if len(lab or "") > 20: warns.append(where + ": label longer than 20 glyphs")
            elif "label" in p: errs.append(where + ": label only on narrator pages")
            plain = expand(p["text"], errs, where)
            lines = wrap(plain)
            if lines is None: errs.append(where + ": a word is longer than %d glyphs" % LINE); continue
            maxlen = max(maxlen, len(plain))
            if len(lines) > LINES: errs.append("%s: %d lines (max %d): %r" % (where, len(lines), LINES, p["text"]))
            else: hist[len(lines)] += 1
            if p.get("ask") and i != len(sc["pages"]) - 1: errs.append(where + ": ask page must be last")
    # legacy ids
    legacy = {sc["legacy_id"]: sc["id"] for sc in s["scripts"] if sc.get("legacy_id") is not None}
    if sorted(legacy) != list(range(67)): errs.append("legacy ids 0..66 are not all present exactly once")
    if len([sc for sc in s["scripts"] if sc.get("legacy_id") is not None]) != 67: errs.append("legacy script count != 67")
    if {int(k): v for k, v in s["legacy_script_index"].items()} != legacy: errs.append("legacy_script_index mismatch")
    # references
    referenced = set()
    npc_ids = {n["id"] for n in s["npcs"]} | {o["id"] for o in s["objects"]}
    duels = {d["id"]: d for d in s["duels"]}
    custom_duelists = {d["id"] for d in s["new_duelists"]}
    for n in s["npcs"] + s["objects"]:
        if n["area"] not in areas: errs.append("%s: unknown area %s" % (n["id"], n["area"]))
        for k, r in enumerate(n.get("dialogue_rules", [])):
            w = "%s.rule[%d]" % (n["id"], k)
            if r["script"] not in scripts: errs.append(w + ": unknown script " + r["script"])
            referenced.add(r["script"]); cond_ok(r["when"], flags, stages, w, errs)
            if "duel" in r and r["duel"] not in duels: errs.append(w + ": unknown duel " + r["duel"])
        if "duelist_id" in n and isinstance(n["duelist_id"], str) and n["duelist_id"] not in custom_duelists:
            errs.append("%s: unknown custom duelist %s" % (n["id"], n["duelist_id"]))
        for fl in n.get("solid_until", []):
            if fl not in flags: errs.append("%s: unknown flag %s" % (n["id"], fl))
    for d in s["duels"]:
        w = "duel " + d["id"]
        if d["npc"] not in npc_ids: errs.append(w + ": unknown npc")
        for k in ("pre_script", "win_script", "lose_script"):
            if d[k] not in scripts: errs.append("%s: unknown %s %s" % (w, k, d[k]))
            referenced.add(d[k])
        if d.get("win_flag") and d["win_flag"] not in flags: errs.append(w + ": unknown win_flag")
        du = d["duelist_id"]
        if isinstance(du, int):
            if not 1 <= du <= 39: errs.append(w + ": duelist id out of 1..39")
        elif du not in custom_duelists: errs.append(w + ": unknown custom duelist")
        if decks and d.get("deck") not in decks["decks"]: errs.append("%s: deck %r not in decks.json" % (w, d.get("deck")))
        # the win page must tell the player about every card/item given
        win_text = " ".join(p["text"] for p in scripts[d["win_script"]]["pages"]) if d["win_script"] in scripts else ""
        for e in d["on_win"] + d.get("pre_effects", []):
            if "give_card" in e:
                c = e["give_card"]
                if c not in cat: errs.append("%s: reward card %r is not an FM card" % (w, c))
                if c not in win_text: errs.append("%s: win script does not mention reward card %r" % (w, c))
            if "give_card_custom" in e:
                if e["give_card_custom"] not in custom: errs.append(w + ": unknown custom card")
                if e.get("fallback_card") not in cat: errs.append(w + ": fallback card unknown")
                if e["give_card_custom"] not in win_text: errs.append("%s: win script does not mention %r" % (w, e["give_card_custom"]))
            if "give_item" in e:
                it = next((x for x in s["items"] if x["id"] == e["give_item"]), None)
                if not it: errs.append("%s: unknown item %s" % (w, e["give_item"]))
                elif it["name"] not in win_text and not (e["give_item"] == "canteen"): errs.append("%s: win script does not mention item %r" % (w, it["name"]))
            for key in ("set_flag",):
                if key in e and e[key] not in flags: errs.append(w + ": unknown flag " + e[key])
            if "set_stage" in e and e["set_stage"] not in stages: errs.append(w + ": unknown stage")
    for t in s["transitions"]:
        w = "transition " + t["id"]
        if t["script"] not in scripts: errs.append(w + ": unknown script")
        referenced.add(t["script"]); cond_ok(t["when"], flags, stages, w, errs)
        for e in t["effects"]:
            if "set_stage" in e and e["set_stage"] not in stages: errs.append(w + ": unknown stage")
            if "set_flag" in e and e["set_flag"] not in flags: errs.append(w + ": unknown flag")
            if "teleport" in e and e["teleport"]["area"] not in areas: errs.append(w + ": unknown area")
            if "play_script_after" in e:
                referenced.add(e["play_script_after"])
                if e["play_script_after"] not in scripts: errs.append(w + ": unknown chained script")
    for e_duel in s["duels"]:
        for e in e_duel["on_win"]:
            if "play_script" in e:
                referenced.add(e["play_script"])
                if e["play_script"] not in scripts: errs.append("unknown chained script " + e["play_script"])
    for h in s["hud_objectives"]:
        cond_ok(h["when"], flags, stages, "hud", errs); expand(h["text"], errs, "hud " + h["text"])
        if len(h["text"]) > 30: warns.append("hud text long: " + h["text"])
    for ch in s["chapters"]:
        for d in ch["duels"]:
            if d not in duels: errs.append("chapter %d: unknown duel %s" % (ch["n"], d))
    for sc in s["scripts"]:
        if sc["id"] not in referenced: warns.append("script never referenced: " + sc["id"])
        if sc["chapter"] < 1 or sc["chapter"] > 9: errs.append(sc["id"] + ": bad chapter")
    # every opponent of chapters 1-8 must have a deck
    if decks:
        for d in s["duels"]:
            if d.get("deck") and d["deck"] in decks["decks"]:
                if decks["decks"][d["deck"]]["difficulty_tier"] != d["difficulty_tier"]: errs.append("tier mismatch for " + d["id"])
    print("scripts %d, pages %d, longest page %d glyphs; pages by lines: %s" % (len(s["scripts"]), pages, maxlen, hist))
    for w in warns: print("warning:", w)
    for e in errs: print("ERROR:", e)
    print("%d errors, %d warnings" % (len(errs), len(warns)))
    return 1 if errs else 0

if __name__ == "__main__":
    sys.exit(main())
