#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Builds the Brazilian Portuguese data from the English files. Data only; never touches the fork.
  python3 build_pt.py            -> ../story.pt.json ../ui.pt.json ../cockatiel.pt.json            (ASCII, retail font)
                                    ../accents/story.pt.json ../accents/ui.pt.json ../accents/cockatiel.pt.json  (with accents)
                                    ../../ui.en.json                                                    (English UI reference)
Reads ../../story.json, ../../cockatiel.json and (read only) the fork's mods/ow-poc/assets/journey.json + mod.json."""
import copy, json, os, sys, unicodedata
HERE = os.path.dirname(os.path.abspath(__file__)); PT = os.path.join(HERE, ".."); ROOT = os.path.join(PT, "..")
FORK = os.environ.get("FM_FORK", "/workspace/study/fmrecomp/fork/mods/ow-poc")
sys.path.insert(0, HERE)
from dialogue_pt import S
import meta_pt as M

def ascii_(s):
    s = unicodedata.normalize("NFD", s)
    return "".join(c for c in s if not unicodedata.combining(c)).replace("ß", "ss")
def walk(o, f):
    if isinstance(o, str): return f(o)
    if isinstance(o, list): return [walk(x, f) for x in o]
    if isinstance(o, dict): return {k: walk(v, f) for k, v in o.items()}
    return o
def load(p): return json.load(open(p, encoding="utf-8"))
def dump(o, p):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f: json.dump(o, f, ensure_ascii=False, indent=1); f.write("\n")
def need(d, k, what):
    if k not in d: raise SystemExit("missing %s translation for %r" % (what, k))
    return d[k]

def build_story():
    s = load(os.path.join(ROOT, "story.json")); t = copy.deepcopy(s)
    t["language"] = "pt-BR"
    t["title"] = M.STORY_TITLE
    t["text_rules"] = {
        "charset": "ASCII letters, digits, space and . , ! ? ' - only (the retail font). The accents/ folder has the same text with accents for HD builds. '{', '}', '|' appear only in tokens.",
        "box": s["text_rules"]["box"], "limit": s["text_rules"]["limit"], "speaker_prefix": s["text_rules"]["speaker_prefix"]}
    t["tokens"] = {"{name}": "Player name (default 'Heroi').",
                   "{a|b}": "Gender choice: a for a male character, b for a female one, e.g. '{o|a}', '{ele|ela}', '{estrangeiro|estrangeira}', 'obrigad{o|a}'. Same token syntax as the English file."}
    for k, sp in t["speakers"].items():
        if sp["name"] in M.SPEAKER_NAMES: sp["name"], sp["short"] = M.SPEAKER_NAMES[sp["name"]]
    ids = {sc["id"] for sc in s["scripts"]}
    if set(S) != ids: raise SystemExit("script ids differ: missing %s extra %s" % (sorted(ids - set(S)), sorted(set(S) - ids)))
    for sc in t["scripts"]:
        src = S[sc["id"]]
        if len(src) != len(sc["pages"]): raise SystemExit("%s: %d pt pages vs %d en pages" % (sc["id"], len(src), len(sc["pages"])))
        for i, (p, line) in enumerate(zip(sc["pages"], src)):
            nar = p["speaker"] == "narrator"
            if nar != ("::" in line): raise SystemExit("%s[%d]: narrator pages need 'Label::text' (and only they)" % (sc["id"], i))
            if nar: p["label"], p["text"] = line.split("::", 1)
            else: p["text"] = line
    for h in t["hud_objectives"]: h["text"] = need(M.HUD_OBJECTIVES, h["text"], "hud objective")
    for a in t["areas"]: a["name"] = need(M.AREAS, a["name"], "area")
    t["ui_strings"] = {"backpack_title": M.STORY_UI["backpack_title"], "backpack_empty": M.STORY_UI["backpack_empty"],
        "objective_label": M.STORY_UI["objective_label"], "chapter_label": M.STORY_UI["chapter_label"],
        "area_names": [need(M.AREAS, n, "area") for n in s["ui_strings"]["area_names"]],
        "backpack_item_labels": {k: M.BACKPACK_LABELS.get(v) or need(M.ITEMS, v, "item") for k, v in s["ui_strings"]["backpack_item_labels"].items()},
        "ask_yes_no": M.STORY_UI["ask_yes_no"]}
    for it in t["items"]: it["name"] = need(M.ITEMS, it["name"], "item")
    for o in t["objects"]: o["name"] = need(M.OBJECTS, o["name"], "object")
    for n in t["npcs"]: n["name"] = M.NPC_NAMES.get(n["name"], n["name"])
    for c in t["chapters"]:
        c["title"] = need(M.STORY_CHAPTERS, c["title"], "chapter title")
        if c.get("design_title"): c["design_title"] = need(M.STORY_CHAPTERS, c["design_title"], "design title")
        c["hud"] = M.STORY_CHAPTER_HUD % c["n"]
    t["translation_note"] = ("pt-BR: player-visible fields only are translated (scripts[].pages text/label, speakers name/short for Guard and Prince, hud_objectives, areas name, ui_strings, items name, objects/npcs name, chapters title/design_title/hud, title). Ids, flags, rules, designer notes (desc, note, setting, source, region, reward, unlock) are copied from the English file unchanged.")
    return s, t

def build_cockatiel():
    c = load(os.path.join(ROOT, "cockatiel.json")); t = copy.deepcopy(c)
    t["extra_lines"] = {k: need(M.COCKATIEL_EXTRA, k, "cockatiel line") for k in c["extra_lines"]}
    t["translation_note"] = "pt-BR: only extra_lines (the in-game lines) are translated; the character sheet fields stay English (art/design briefs)."
    return c, t

def en_ui():
    j = load(os.path.join(FORK, "assets", "journey.json")); mod = load(os.path.join(FORK, "mod.json"))
    return {
        "language": {"name": "English", "label": "Language"},
        "mod": {"name": mod["name"], "description": mod["description"], "title_button": mod["menu"]["buttons"][0]["label"]},
        "choose": {"heading": "JOURNEY MODE", "continue": "Continue", "new_journey": "New journey", "language": "Language: %s"},
        "hud": {"status_line": "%s  -  %s    Objective: %s", "objective_label": "Objective:"},
        "hint": {"talk": "X: talk to %s", "examine": "X: examine", "controls": "Arrows: walk   Circle: run   X: talk   Start: menu"},
        "ask": {"yes": "Yes", "no": "No"},
        "messages": {"progress_saved": "Progress saved", "save_failed": "Save failed"},
        "creation": {
            "heading": "CREATE YOUR CHARACTER",
            "rows": {"name": "Name", "gender": "Gender", "hair": "Hair", "hair_colour": "Hair colour", "skin": "Skin",
                     "outfit_colour": "Outfit colour", "portrait": "Portrait", "start": "Start"},
            "gender": {"male": "Male", "female": "Female"},
            "hair_styles": ["Short", "Swept", "Tidy"],
            "hair_colours": ["Violet", "Black", "Brown", "Blonde", "Red"],
            "skins": ["Light", "Tan", "Dark"],
            "outfit_colours": ["Blue", "Red", "Green", "Black", "White"],
            "portraits": ["Portrait 1", "Portrait 2", "Portrait 3", "Portrait 4"],
            "hint_name": "X: type a name", "hint_begin": "X: begin", "hint_change": "Left/Right: change"},
        "menu": {"items": ["Deck editor", "Items", "Status", "Save", "Back to title", "Close"], "items_empty": "Nothing yet",
                 "objective": "Objective: %s", "status": "Duels %d    Wins %d    Losses %d", "deck": "Deck %d / 40 cards",
                 "saved": "Progress saved.", "save_failed": "The save failed.",
                 "quit_title": "Back to the title screen?", "quit_warn": "(unsaved progress is lost)", "yes": "Yes", "no": "No"},
        "defaults": {"player_name": "Hero"},
        # journey.json lists, in file order (the engine reads them from there; a translation replaces `name`/`text`)
        "areas": [a["name"] for a in j["areas"]],
        "chapters": [c["text"] for c in j["chapters"]],
        "objectives": [o["text"] for o in j["objectives"]],
        "items": [i["name"] for i in j["items"]],
        "npc_names": {n["id"]: n["name"] for n in j["npcs"]},
        "speaker_names": {k: v["name"] for k, v in j["speakers"].items() if "name" in v},
    }

def pt_ui(en):
    u = copy.deepcopy(M.UI_PT)
    u["areas"] = [need(M.AREAS, x, "area") for x in en["areas"]]
    u["chapters"] = [need(M.ENGINE_CHAPTERS, x, "chapter banner") for x in en["chapters"]]
    u["objectives"] = [need(M.ENGINE_OBJECTIVES, x, "objective") for x in en["objectives"]]
    u["items"] = [need(M.ITEMS, x, "item") for x in en["items"]]
    u["npc_names"] = {k: M.NPC_NAMES.get(v, v) for k, v in en["npc_names"].items()}
    u["speaker_names"] = {k: M.NPC_NAMES.get(v, v) for k, v in en["speaker_names"].items()}
    # same key order as English
    def order(e, p):
        if isinstance(e, dict): return {k: order(e[k], p[k]) for k in e}
        return p
    return order(en, u)

def main():
    s, ts = build_story(); c, tc = build_cockatiel(); en = en_ui(); tu = pt_ui(en)
    dump(en, os.path.join(ROOT, "ui.en.json"))
    for sub, f in (("", ascii_), ("accents", lambda x: x)):
        d = os.path.join(PT, sub)
        dump(walk(ts, f), os.path.join(d, "story.pt.json"))
        dump(walk(tu, f), os.path.join(d, "ui.pt.json"))
        dump(walk(tc, f), os.path.join(d, "cockatiel.pt.json"))
    print("built ASCII + accents (story, ui, cockatiel) and ../../ui.en.json")
if __name__ == "__main__": main()
