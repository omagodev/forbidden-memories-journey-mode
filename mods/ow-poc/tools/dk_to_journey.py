#!/usr/bin/env python3
"""Builds the runtime story data of Journey Mode from the Duelist Kingdom content (journey_content/duelist_kingdom).

  python3 tools/dk_to_journey.py [DK_DIR]

Writes assets/journey.json (rules: flags, NPC talk rules, objectives, guide, journal, objects, painted: night/observers), assets/lang/<en|pt>/story.json
(the scripts), merges the story's texts into assets/lang/<en|pt>/ui.json and adds the duel decks of the new villagers to mod.json.
Scope so far: the home town, quests 1-3 (part 2 adds the bench at night, the hooded man, Mago.dev on the roof, the Stamp Card) and the
first steps of quest 4 (Hakim, Kemet's lantern duel).  The old story
(tools/base_*_old.json) stays as the base for what the new story does not define (areas, start tile, 3D world).
"""
import csv, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
DK = sys.argv[1] if len(sys.argv) > 1 else "/workspace/study/fmrecomp/journey_content/duelist_kingdom"
CATALOG = os.path.join(MOD, "tools", "card-catalog.csv")
# the people of the painted village: (3D mesh for the old map view, tile).  hooded_man has no fixed tile: the story places him ("places").
VILLAGE_NPCS = {"simon": ("Wizard", [14.5, 28.5]), "teana": ("Ninja_Sand_Female", [9.5, 32.5]), "jono": ("Ninja_Sand", [19.5, 32.5]), "guard": ("Knight_Male", [24.5, 23.5]),
                "hooded_man": ("Wizard", None), "baker": ("Worker_Male", [30.5, 30.5]), "farmer": ("Ninja_Sand", [21.5, 34.5])}
# the village's songs, sound-driver package numbers (song 0x7000 + 16 * n): 10 is the game's own campaign-map song (sustained, quiet),
# 25 a slow pad that swells in; both measured steady and low in activity (see DK_PART2_README)
VILLAGE_MUSIC = {"day": 10, "night": 25}
# debug presets (jm_debug.c: L1+R1+Up/Down in the village, or "preset" in debug.json): a state of the story to jump to
_H3 = ["heard_teana", "heard_jono", "heard_guard"]
DEBUG_PRESETS = [
    {"name": "1 home door", "stage": 1, "flags": [], "anchor": "hero_start", "time": "auto"},
    {"name": "2 rumors heard (Simon next)", "stage": 1, "flags": _H3, "anchor": "plaza_center", "time": "auto"},
    {"name": "3 Simon won (bench next)", "stage": 2, "flags": _H3 + ["simon_won"], "anchor": "plaza_bench", "time": "auto"},
    {"name": "4 night, hooded man waits", "stage": 2, "flags": _H3 + ["simon_won", "mago_roof"], "anchor": "plaza_center", "time": "auto"},
    {"name": "5 Stamp Card (Hakim next)", "stage": 3, "flags": _H3 + ["simon_won", "mago_roof", "courier_met"], "anchor": "bakery_door", "time": "auto"},
    {"name": "6 Hakim's hint (Kemet next)", "stage": 3, "flags": _H3 + ["simon_won", "mago_roof", "courier_met", "baker_hint"], "anchor": "farmer_field", "time": "auto"},
    {"name": "7 Lantern won (part 2 end)", "stage": 3, "flags": _H3 + ["simon_won", "mago_roof", "courier_met", "baker_hint", "farmer_won"], "anchor": "farmer_field", "time": "auto"},
]
# a narrator page with a label is not speech: its kind decides the banner (en labels; pt pages follow the same index)
LABEL_KIND = {"Objective": "objective", "Reward": "item", "You got": "item", "Stamp": "item", "End of Chapter 1": "complete"}
NOTIFY = {"en": {"objective": "NEW OBJECTIVE", "item": "ITEM OBTAINED", "complete": "QUEST COMPLETE", "caption": "", "press": "X: continue"},
          "pt": {"objective": "NOVO OBJETIVO", "item": "ITEM OBTIDO", "complete": "MISSAO CUMPRIDA", "caption": "", "press": "X: continuar"}}
PART_END = {"farmer": "dk_part2_end"}      # a duel win that ends the part: this script plays after the win scene
# effects the runtime derives from state instead of executing (items from flags, time of day / placement from "painted" and "places")
DERIVED = {"give_item", "set_time", "remove_npc", "place_npc"}
ITEM_FLAG = {"stamp_card": "courier_met", "lantern": "farmer_won"}
warnings = []


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def cards():
    out = {}
    with open(CATALOG, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            out[r["name"]] = int(r["id"])
    return out


CARD = cards()


def when(w):
    """DK condition -> runtime condition."""
    out = {}
    for k, v in (w or {}).items():
        if k == "stage":
            if v[0] > 0: out["stage_ge"] = v[0]
            if v[1] < 99: out["stage_lt"] = v[1] + 1
        elif k == "flags_all": out["needs"] = v
        elif k == "flags_none": out["lacks"] = v
        elif k == "flags_any": warnings.append("flags_any not supported: %r" % (w,))
        else: warnings.append("condition key %s ignored" % k)
    return out


def result(effects):
    """DK effects list -> a runtime result node {flags, stage, cards}."""
    r = {}
    for e in effects or []:
        (k, v), = e.items()
        if k == "set_flag": r.setdefault("flags", []).append(v)
        elif k == "set_stage": r["stage"] = v
        elif k == "give_card":
            if v not in CARD: raise SystemExit("unknown card " + v)
            r.setdefault("cards", []).append(CARD[v])
        elif k in DERIVED: pass
        else: warnings.append("effect %s ignored (not in part 2)" % k)
    return r


def part_end_script(lang):
    t = {"en": ("Part 2 complete", "That is all for this test build.", "Next: the pyramid hatch and the cistern (part 3)."),
         "pt": ("Parte 2 completa", "E tudo por esta versao de teste.", "Proximo: a escotilha da piramide e a cisterna (parte 3).")}[lang]
    return {"id": "dk_part2_end", "pages": [{"speaker": "narrator", "label": t[0], "kind": "complete", "text": t[1] + " " + t[2]}]}


def talk_rules(rules, scripts, duels, flags_extra=None):
    talk = []
    for r in rules:
        assert r["script"] in scripts, r["script"]
        t = {"when": when(r.get("when")), "scene": r["script"]}
        if r.get("duel"):
            d = duels[r["duel"]]
            win = result(d.get("on_win"))
            win.setdefault("flags", []).insert(0, d["win_flag"])
            win["scene"] = d["win_script"]
            if d["id"] in PART_END: win["then"] = PART_END[d["id"]]
            t["duel"] = True
            t["win"] = win
            t["lose"] = {"scene": d["lose_script"]}
        elif r.get("effects"):
            t["effects"] = result(r["effects"])
        if not t["when"]: del t["when"]
        talk.append(t)
    return talk


def build():
    en, pt = load(DK + "/en/story_dk.json"), load(DK + "/pt/story_dk.pt.json")
    old = load(os.path.join(HERE, "base_journey_old.json"))
    flags = [f["name"] for f in sorted(en["flags"], key=lambda f: f["bit"])]
    assert [f["bit"] for f in sorted(en["flags"], key=lambda f: f["bit"])] == list(range(len(flags))) and len(flags) <= 31
    duels = {d["id"]: d for d in en["duels"]}
    speakers = {}
    for k, v in en["speakers"].items():
        pid = v["portrait"]
        speakers[k] = {"portrait_id": pid if 0 < pid <= 40 else 0}
    speakers["atos"] = {"portrait": "player"}
    scripts = {s["id"]: s for s in en["scripts"]}
    npcs = []
    for n in en["npcs"]:
        if n["id"] not in VILLAGE_NPCS: continue
        talk = talk_rules(n["dialogue_rules"], scripts, duels)
        mesh, tile = VILLAGE_NPCS[n["id"]]
        e = {"id": n["id"], "name": n["name"], "mesh": mesh, "anchor": n["anchor"], "talk": talk,
             "duelist_id": n["duelist_id"] or 0, "portrait_id": speakers[n["portrait_speaker"]]["portrait_id"]}
        if tile: e["tile"] = tile
        if n["id"] == "hooded_man":   # placed by the bench script, gone after the riddle: there from the bench scene until the Stamp Card is given
            e["places"] = [{"when": {"stage_ge": 2, "stage_lt": 3, "needs": ["mago_roof"], "lacks": ["courier_met"]}, "tile": [18.5, 30.5]}]
        npcs.append(e)
    objects = []
    for o in en["objects"]:
        if o["id"] not in ("plaza_bench", "notice_sign"): continue
        talk = talk_rules(o["dialogue_rules"], scripts, duels)
        e = {"id": o["id"], "anchor": o["anchor"], "talk": talk}
        if o["id"] == "plaza_bench":
            e["prop"] = "bench"; e["reach"] = 78
            for t in talk:
                if t["scene"] == "dk1_bench":
                    t["pose"] = "sit"
                    t["when"].setdefault("lacks", []).append("mago_roof")      # the night scene plays once; after it the bench is the plain "after" line
        objects.append(e)
    ev = [e for e in en["observer_events"] if e["id"] == "roof_at_night"][0]
    three = ["heard_teana", "heard_jono", "heard_guard"]
    guide = [
        {"when": {"stage_ge": 1, "stage_lt": 2, "lacks": ["heard_teana"]}, "npc": "teana"},
        {"when": {"stage_ge": 1, "stage_lt": 2, "lacks": ["heard_jono"]}, "npc": "jono"},
        {"when": {"stage_ge": 1, "stage_lt": 2, "lacks": ["heard_guard"]}, "npc": "guard"},
        {"when": {"stage_ge": 1, "stage_lt": 2, "needs": three}, "npc": "simon"},
        {"when": {"stage_ge": 2, "stage_lt": 3, "lacks": ["simon_won"]}, "npc": "simon"},
        {"when": {"stage_ge": 2, "stage_lt": 3, "needs": ["simon_won"], "lacks": ["mago_roof"]}, "anchor": "plaza_bench"},
        {"when": {"stage_ge": 2, "stage_lt": 3, "needs": ["mago_roof"]}, "npc": "hooded_man"},
        {"when": {"stage_ge": 3, "stage_lt": 4, "lacks": ["baker_hint"]}, "npc": "baker"},
        {"when": {"stage_ge": 3, "stage_lt": 4, "needs": ["baker_hint"], "lacks": ["farmer_won"]}, "npc": "farmer"},
    ]
    journal = [
        {"id": "q01_whispers", "active": {"stage_ge": 1}, "done": {"needs": three},
         "lines": [{"npc": "teana", "done": {"needs": ["heard_teana"]}}, {"npc": "jono", "done": {"needs": ["heard_jono"]}}, {"npc": "guard", "done": {"needs": ["heard_guard"]}}]},
        {"id": "q02_sage", "active": {"stage_ge": 1, "needs": three}, "done": {"needs": ["simon_won"]}, "lines": []},
        {"id": "q03_stakeout", "active": {"stage_ge": 2, "needs": ["simon_won"]}, "done": {"needs": ["courier_met"]},
         "lines": [{"text": 0, "done": {"needs": ["mago_roof"]}}, {"text": 1, "done": {"needs": ["courier_met"]}}]},
        {"id": "q04_lost", "active": {"stage_ge": 3}, "done": {"needs": ["treasure_lost"]},
         "lines": [{"text": 2, "done": {"needs": ["baker_hint"]}}, {"text": 3, "done": {"needs": ["farmer_won"]}}]},
    ]
    # the HUD line: the story's list, plus "Talk to the hooded man" once the bench scene is over (its step is the second of quest 3)
    hood_when = {"stage_ge": 2, "stage_lt": 3, "needs": ["mago_roof"]}
    hud = [(when(h["when"]), h["text"]) for h in en["hud_objectives"]]
    hud_pt = [h["text"] for h in pt["hud_objectives"]]
    k = [i for i, (w, t) in enumerate(hud) if t.startswith("Sit on the plaza bench")][0]
    hud.insert(k, (hood_when, en["quests"][2]["steps"][1]["objective"]))
    hud_pt.insert(k, pt["quests"][2]["steps"][1]["objective"])
    objectives = [{"when": w, "text": t} for w, t in hud]
    items = [{"name": it["name"], "flag": ITEM_FLAG[it["id"]]} for it in en["items"] if it["id"] in ITEM_FLAG]
    item_names = {c: [it["name"] for it in src["items"] if it["id"] in ITEM_FLAG] for c, src in (("en", en), ("pt", pt))}
    painted = {"bridge_open": {"stage_ge": 4},
               "music": VILLAGE_MUSIC,
               "night": {"stage_ge": 2, "stage_lt": 3, "needs": ["mago_roof"], "lacks": ["courier_met"]},
               "time_events": [{"script": "dk1_bench", "page": 1, "time": "night"}, {"script": "dk1_hooded_riddle", "page": 11, "time": "auto"}],
               "observers": [{"npc": ev["npc"], "sprite": ev["sprite"], "overlay": ev["overlay"], "anchor": ev["anchor"], "script": ev["show_during"]["script"],
                              "pages": list(range(ev["show_during"]["pages"][0], ev["show_during"]["pages"][1] + 1)), "vanish": ev["vanish"]}]}
    j = dict(old)
    j.update({
        "flags": flags, "npcs": npcs, "speakers": speakers, "objectives": objectives, "guide": guide, "journal": journal,
        "chapters": [{"text": en["chapters"][0]["title"]}], "items": items, "triggers": [], "spots": [],
        "objects": objects, "intro": "dk1_intro", "painted": painted, "debug": DEBUG_PRESETS,
        "story": "duelist_kingdom part 2",
    })
    j["areas"] = [dict(a) for a in old["areas"]]
    j["areas"][0]["name"] = en["areas"][0]["name"]
    with open(os.path.join(MOD, "assets/journey.json"), "w", encoding="utf-8") as f:
        json.dump(j, f, indent=1, ensure_ascii=True)

    ui_extra = {
        "en": {"jr": {"heading": "JOURNAL", "reward": "Reward:", "empty": "No quests yet.", "more": "More quests arrive in the next parts of the story.", "close": "Triangle: close"},
               "hint_painted": "Arrows: walk   Circle: run   X: talk   Triangle: journal   Select: map on/off   Start: menu",
               "part_end": "The harbor road opens in part 3.",
               "rewards": ["Rumor Notebook filled (3 rumors)", "card Magician of Faith; the legend of the Kingdom", "Stamp Card with three stamp slots", "card Killer Needle, a Lantern (more in part 3)"],
               "jr_extra": {"items": "Items:", "stamp": "Stamp Card:"}, "stamps": ["Lost", "Won", "Given"]},
        "pt": {"jr": {"heading": "DIARIO", "reward": "Recompensa:", "empty": "Nenhuma missao ainda.", "more": "Mais missoes chegam nas proximas partes da historia.", "close": "Triangulo: fechar"},
               "hint_painted": "Setas: andar   Circulo: correr   X: falar   Triangulo: diario   Select: mapa liga/desliga   Start: menu",
               "part_end": "A estrada do porto abre na parte 3.",
               "rewards": ["Caderno de Cochichos completo (3 cochichos)", "carta Magician of Faith; a lenda do Reino", "Cartao de Selos com tres espacos de selo", "carta Killer Needle, uma Lanterna (mais na parte 3)"],
               "jr_extra": {"items": "Itens:", "stamp": "Cartao de Selos:"}, "stamps": ["Perdido", "Ganho", "Dado"]},
    }
    en_kind = {s["id"]: [LABEL_KIND.get(p.get("label"), "caption" if p.get("label") else "") for p in s["pages"]] for s in en["scripts"]}
    for code, src in (("en", en), ("pt", pt)):
        sc = [{"id": s["id"], "pages": [dict(p, **({"kind": en_kind[s["id"]][i]} if en_kind[s["id"]][i] else {})) for i, p in enumerate(s["pages"])]} for s in src["scripts"]]
        sc.append(part_end_script(code))
        with open(os.path.join(MOD, "assets/lang/%s/story.json" % code), "w", encoding="utf-8") as f:
            json.dump({"scripts": sc}, f, indent=1, ensure_ascii=True)
        ui = load(os.path.join(HERE, "base_ui_%s.json" % code))
        ex = ui_extra[code]
        ui["objectives"] = [h["text"] for h in src["hud_objectives"]]
        ui["objectives"].insert(k, src["quests"][2]["steps"][1]["objective"])
        ui["chapters"] = [src["chapters"][0]["title"]]
        ui["items"] = item_names[code]
        ui["npc_names"] = {n["id"]: n["name"] for n in src["npcs"] if n["id"] in VILLAGE_NPCS}
        ui["speaker_names"] = {k: v["name"] for k, v in src["speakers"].items() if k not in ("atos", "narrator")}
        ui["areas"][0] = src["areas"][0]["name"]
        ui["quest_titles"] = [q["title"] for q in src["quests"][:4]]
        ui["quest_objectives"] = [src["quests"][i]["steps"][0]["objective"] for i in range(4)]
        ui["quest_steps"] = [src["quests"][2]["steps"][0]["objective"], src["quests"][2]["steps"][1]["objective"],
                             src["quests"][3]["steps"][0]["objective"], src["quests"][3]["steps"][1]["objective"]]
        ui["quest_rewards"] = ex["rewards"]
        ui["journal"] = dict(ex["jr"], items=ex["jr_extra"]["items"], stamp=ex["jr_extra"]["stamp"], stamp_lost=ex["stamps"][0], stamp_won=ex["stamps"][1], stamp_given=ex["stamps"][2])
        ui["hint"]["painted"] = ex["hint_painted"]
        ui["messages"]["part_end"] = ex["part_end"]
        ui["notify"] = NOTIFY[code]
        with open(os.path.join(MOD, "assets/lang/%s/ui.json" % code), "w", encoding="utf-8") as f:
            json.dump(ui, f, indent=2, ensure_ascii=False)
            f.write("\n")
    # the duel decks of the new villagers (the game's duelists "Villager 1", "Villager 3") go into mod.json
    dk_decks = load(os.path.join(DK, "decks_dk.json"))["decks"]
    mod = load(os.path.join(MOD, "mod.json"))
    for d in duels.values():
        if d["npc"] in VILLAGE_NPCS and d["deck"] in dk_decks:
            mod["decks"][d["deck"]] = dict({"fixed": True}, **dk_decks[d["deck"]]["cards"])
    with open(os.path.join(MOD, "mod.json"), "w", encoding="utf-8") as f:
        json.dump(mod, f, indent=2, ensure_ascii=False)
        f.write("\n")
    for w in sorted(set(warnings)): print("warning:", w)
    print("journey.json: %d flags, %d npcs, %d objectives; scripts en %d pt %d" % (len(flags), len(npcs), len(objectives), len(en["scripts"]) + 1, len(pt["scripts"]) + 1))


build()
