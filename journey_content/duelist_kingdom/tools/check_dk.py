#!/usr/bin/env python3
"""Validates duelist_kingdom content (EN and PT): structure, references, charset, 3x32 fit, rewards named in win text, decks, EN/PT parity.
Usage: python3 tools/check_dk.py   (exit 0 = ok)"""
import csv, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
CAT = os.environ.get("FM_CATALOG", "/workspace/study/fmrecomp/fork/notes/card-catalog.csv")
BASE_DECKS = os.path.join(ROOT, "..", "decks.json")
LINE, LINES, NAME_W = 32, 3, 10
ALLOWED = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,!?'-")
TOKEN = re.compile(r"\{([^{}]*)\}")
errs, warns = [], []
def err(m): errs.append(m)
def expand(text, where):
    def rep(m):
        t = m.group(1)
        if t == "name": return "N" * NAME_W
        if "|" in t:
            a, b = t.split("|")
            if not a or not b: err("%s: bad gender token {%s}" % (where, t))
            return max(a, b, key=len)
        err("%s: unknown token {%s}" % (where, t)); return ""
    out = TOKEN.sub(rep, text)
    if "{" in out or "}" in out or "|" in out: err(where + ": stray brace/pipe")
    bad = sorted({c for c in out if c not in ALLOWED})
    if bad: err("%s: chars not in the font %r" % (where, "".join(bad)))
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
def cond_ok(when, flags, where):
    for k in when:
        if k not in ("stage", "flags_all", "flags_any", "flags_none"): err("%s: unknown condition %s" % (where, k))
    for k in ("flags_all", "flags_any", "flags_none"):
        for f in when.get(k, []):
            if f not in flags: err("%s: unknown flag %s" % (where, f))
    st = when.get("stage")
    if st and not (len(st) == 2 and st[0] <= st[1]): err("%s: bad stage range" % where)
def check_effects(effs, where, S, flags, items, cat, win_text, anchors, npc_ids, stages):
    for e in effs:
        if "give_card" in e:
            if e["give_card"] not in cat: err("%s: card %r not an FM card" % (where, e["give_card"]))
            if win_text is not None and e["give_card"] not in win_text: err("%s: reward card %r not named in the script text" % (where, e["give_card"]))
        if "give_item" in e:
            it = items.get(e["give_item"])
            if not it: err("%s: unknown item %s" % (where, e["give_item"]))
            elif win_text is not None and it not in win_text and e["give_item"] not in ("rumor_notebook", "jug", "star_chip"): err("%s: item %r not named in the script text" % (where, it))
        for k in ("set_flag",):
            if k in e and e[k] not in flags: err("%s: unknown flag %s" % (where, e[k]))
        if "set_stage" in e and e["set_stage"] not in stages: err(where + ": unknown stage")
        for k in ("place_npc", "move_npc"):
            if k in e:
                v = e[k]
                if v["npc"] not in npc_ids: err("%s: unknown npc %s" % (where, v["npc"]))
                if v["anchor"] not in anchors.get(v["area"], {}): err("%s: unknown anchor %s.%s" % (where, v["area"], v["anchor"]))
        if "teleport" in e:
            v = e["teleport"]
            if v["anchor"] not in anchors.get(v["area"], {}): err("%s: unknown anchor %s.%s" % (where, v["area"], v["anchor"]))
        if "remove_npc" in e and e["remove_npc"] not in npc_ids: err("%s: unknown npc" % where)
def main():
    cat = {r["name"]: r for r in csv.DictReader(open(CAT, newline="", encoding="utf-8"))}
    rit = {n for n, r in cat.items() if r["type"] == "Ritual"} | {n for n, r in cat.items() if int(r["id"]) in (356, 357, 360, 362, 364, 374, 380, 21) or int(r["id"]) >= 701}
    base = json.load(open(BASE_DECKS, encoding="utf-8"))["decks"]; dk = json.load(open(os.path.join(ROOT, "decks_dk.json"), encoding="utf-8"))["decks"]
    for k, d in dk.items():
        c = d["cards"]
        if sum(c.values()) != 40: err("deck %s has %d cards" % (k, sum(c.values())))
        if len(c) < 14: err("deck %s < 14 distinct" % k)
        for n, v in c.items():
            if n not in cat: err("deck %s unknown card %r" % (k, n))
            elif n in rit: err("deck %s ritual %r" % (k, n))
            if v > 3: err("deck %s %s x%d" % (k, n, v))
    st = {}
    for lg, path in (("en", "en/story_dk.json"), ("pt", "pt/story_dk.pt.json")):
        s = json.load(open(os.path.join(ROOT, path), encoding="utf-8")); st[lg] = s
        flags = {f["name"] for f in s["flags"]}
        if len({f["bit"] for f in s["flags"]}) != len(flags) or max(f["bit"] for f in s["flags"]) > 30: err("flag bits")
        stages = {x["stage"] for x in s["stages"]}; anchors = s["anchors"]; spk = s["speakers"]
        items = {i["id"]: i["name"] for i in s["items"]}
        scripts = {}
        for sc in s["scripts"]:
            if sc["id"] in scripts: err("dup script " + sc["id"])
            scripts[sc["id"]] = sc
        for sc in s["scripts"]:
            for i, p in enumerate(sc["pages"]):
                w = "[%s] %s[%d]" % (lg, sc["id"], i)
                if p["speaker"] not in spk: err(w + ": speaker"); continue
                if p["speaker"] == "narrator":
                    if not p.get("label"): err(w + ": narrator label")
                    else:
                        expand(p["label"], w + " label")
                        if len(p["label"]) > 20: warns.append(w + " label long")
                plain = expand(p["text"], w); lines = wrap(plain)
                if lines is None: err(w + ": word too long"); continue
                if len(lines) > LINES: err("%s: %d lines: %r" % (w, len(lines), p["text"]))
                if p.get("ask") and i != len(sc["pages"]) - 1: err(w + ": ask must be last")
        referenced = set(); npc_ids = {n["id"] for n in s["npcs"]}; obj_ids = {o["id"] for o in s["objects"]}
        duels = {d["id"]: d for d in s["duels"]}
        for e in s["npcs"] + s["objects"]:
            if e["anchor"] not in anchors.get(e["area"], {}): err("%s: unknown anchor %s.%s" % (e["id"], e["area"], e["anchor"]))
            for k, r in enumerate(e["dialogue_rules"]):
                w = "[%s] %s.rule[%d]" % (lg, e["id"], k)
                if r["script"] not in scripts: err(w + ": unknown script " + r["script"])
                referenced.add(r["script"]); cond_ok(r["when"], flags, w)
                if "duel" in r:
                    if r["duel"] not in duels: err(w + ": unknown duel")
                    elif duels[r["duel"]]["pre_script"] != r["script"]: err(w + ": duel pre_script differs")
                    elif not scripts[r["script"]]["pages"][-1].get("ask"): err(w + ": duel rule script must end with an ask page")
                elif r["script"] in scripts and scripts[r["script"]]["pages"][-1].get("ask"): err(w + ": ask page without duel")
                wt = " ".join(p["text"] for p in scripts[r["script"]]["pages"]) if r["script"] in scripts else ""
                check_effects(r.get("effects", []), w, s, flags, items, cat, wt, anchors, npc_ids, stages)
            for mv in e.get("moves", []):
                if mv["anchor"] not in anchors.get(mv["area"], {}): err("%s: bad move anchor" % e["id"])
        for d in s["duels"]:
            w = "[%s] duel %s" % (lg, d["id"])
            if d["npc"] not in npc_ids: err(w + ": npc")
            for k in ("pre_script", "win_script", "lose_script"):
                if d[k] not in scripts: err("%s: %s unknown" % (w, k))
                referenced.add(d[k])
            if d["win_flag"] not in flags: err(w + ": win_flag")
            if d["deck"] not in dk and d["deck"] not in base: err("%s: deck %r missing" % (w, d["deck"]))
            du = d["duelist_id"]
            if isinstance(du, int):
                if not 1 <= du <= 39: err(w + ": duelist id")
            elif du not in {x["id"] for x in s["new_duelists"]}: err(w + ": custom duelist")
            wt = " ".join(p["text"] for p in scripts[d["win_script"]]["pages"])
            check_effects(d["on_win"], w, s, flags, items, cat, wt, anchors, npc_ids, stages)
        for t in s["transitions"]:
            w = "[%s] transition %s" % (lg, t["id"])
            if t["script"] not in scripts: err(w + ": script")
            referenced.add(t["script"]); cond_ok(t["when"], flags, w)
            tr = t["trigger"]
            if tr["kind"] == "interact" and tr["object"] not in obj_ids: err(w + ": object")
            check_effects(t["effects"], w, s, flags, items, cat, None, anchors, npc_ids, stages)
        for h in s["hud_objectives"]:
            cond_ok(h["when"], flags, "hud"); expand(h["text"], "hud " + h["text"])
            if len(h["text"]) > 60: warns.append("hud long: " + h["text"])
        for q in s["quests"]:
            for stp in q["steps"]: expand(stp["objective"], "quest " + q["id"])
        for u in set(scripts) - referenced: warns.append("[%s] script never referenced: %s" % (lg, u))
        tot = sum(len(sc["pages"]) for sc in s["scripts"])
        print("%s: %d scripts, %d pages, %d npcs, %d objects, %d duels, %d quests" % (lg, len(scripts), tot, len(s["npcs"]), len(s["objects"]), len(s["duels"]), len(s["quests"])))
    # observer events (Mago.dev) and outline pages
    for lg in ("en", "pt"):
        s = st[lg]; scr = {x["id"]: x for x in s["scripts"]}
        for e in s["observer_events"]:
            w = "[%s] observer %s" % (lg, e["id"])
            if e["anchor"] not in s["anchors"].get(e["area"], {}): err(w + ": anchor")
            if e["flag"] not in {f["name"] for f in s["flags"]}: err(w + ": flag")
            if e["npc"] not in {n["id"] for n in s["npcs"]}: err(w + ": npc")
            if "show_during" in e:
                sd = e["show_during"]
                if sd["script"] not in scr or sd["pages"][1] >= len(scr[sd["script"]]["pages"]): err(w + ": show_during range")
            elif e["interact_object"] not in {o["id"] for o in s["objects"]}: err(w + ": object")
    ko = json.load(open(os.path.join(ROOT, "kingdom_outline.json"), encoding="utf-8")); spk = st["en"]["speakers"]
    mg = ko["mago_dev"]
    groups = [(a["id"], a["pages_en"], a["pages_pt"]) for a in mg["appearances"]] + [("payoff", mg["payoff"]["pages_en"], mg["payoff"]["pages_pt"])]
    for gid, pe, pp in groups:
        if [p["speaker"] for p in pe] != [p["speaker"] for p in pp]: err("outline parity " + gid)
        for lg, pages in (("en", pe), ("pt", pp)):
            for i, p in enumerate(pages):
                w = "[%s] outline %s[%d]" % (lg, gid, i)
                if p["speaker"] not in spk: err(w + ": speaker")
                if p["speaker"] == "narrator": expand(p["label"], w)
                lines = wrap(expand(p["text"], w))
                if lines is None or len(lines) > LINES: err(w + ": does not fit")
    # parity
    a, b = st["en"], st["pt"]
    if [x["id"] for x in a["scripts"]] != [x["id"] for x in b["scripts"]]: err("script id order differs")
    for x, y in zip(a["scripts"], b["scripts"]):
        if [(p["speaker"], bool(p.get("ask"))) for p in x["pages"]] != [(p["speaker"], bool(p.get("ask"))) for p in y["pages"]]: err("parity " + x["id"])
    for k in ("flags", "stages", "duels", "transitions"):
        if a[k] != b[k]: err("EN/PT differ in " + k)
    for w in warns: print("warning:", w)
    for e in errs: print("ERROR:", e)
    print("%d errors, %d warnings" % (len(errs), len(warns)))
    return 1 if errs else 0
sys.exit(main())
