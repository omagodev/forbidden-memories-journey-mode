#!/usr/bin/env python3
"""Builds the runtime story data of Journey Mode from the Duelist Kingdom content (journey_content/duelist_kingdom).

  python3 tools/dk_to_journey.py [DK_DIR]

Writes assets/journey.json (rules: flags, NPC talk rules, objectives, guide, journal, objects, painted: night/observers), assets/lang/<en|pt>/story.json
(the scripts), merges the story's texts into assets/lang/<en|pt>/ui.json and adds the duel decks of the new villagers to mod.json.
Scope so far: the home town, quests 1-3 (part 2: the bench at night, the hooded man, Mago.dev on the roof, the Stamp Card, Hakim and Kemet's
lantern duel) and part 3: the three treasures (the Lost in the old cistern under the little pyramid with the ghost Bakura, the Won from Rex Raptor,
the Given from Teana after her errands), the glyph on the cistern wall and the way to stage 4.  The old story
(tools/base_*_old.json) stays as the base for what the new story does not define (areas, start tile, 3D world).
"""
import csv, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
DK = sys.argv[1] if len(sys.argv) > 1 else "/workspace/study/fmrecomp/journey_content/duelist_kingdom"
CATALOG = os.path.join(MOD, "tools", "card-catalog.csv")
# the people of the painted village: (3D mesh for the old map view, tile).  hooded_man has no fixed tile: the story places him ("places").
VILLAGE_NPCS = {"simon": ("Wizard", [14.5, 28.5]), "teana": ("Ninja_Sand_Female", [9.5, 32.5]), "jono": ("Ninja_Sand", [19.5, 32.5]), "guard": ("Knight_Male", [24.5, 23.5]),
                "hooded_man": ("Wizard", None), "baker": ("Worker_Male", [30.5, 30.5]), "farmer": ("Ninja_Sand", [21.5, 34.5]),
                "rex": ("Suit_Male", None), "bakura": ("Wizard", [2.5, 2.5])}
# where the old 3D map would put people the painted picture shows elsewhere (Rex on the east road once placed, Bakura in the cistern: never really seen there)
PLACES = {"rex": [{"when": {"stage_ge": 3}, "tile": [37.5, 29.5]}]}
# the village's songs, sound-driver package numbers (song 0x7000 + 16 * n): 10 is the game's own campaign-map song (sustained, quiet),
# 25 a slow pad that swells in; both measured steady and low in activity (see DK_PART2_README)
VILLAGE_MUSIC = {"day": 10, "night": 25, "cistern": 26}      # 26: the Sand Ruins song, a low sustained pad: the cistern is dim and quiet
# debug presets (jm_debug.c: L1+R1+Up/Down in the village, or "preset" in debug.json): a state of the story to jump to
_H3 = ["heard_teana", "heard_jono", "heard_guard"]
_B = _H3 + ["simon_won", "mago_roof", "courier_met", "baker_hint"]
DEBUG_PRESETS = [
    {"name": "1 home door", "stage": 1, "flags": [], "anchor": "hero_start", "time": "auto"},
    {"name": "2 rumors heard (Simon next)", "stage": 1, "flags": _H3, "anchor": "plaza_center", "time": "auto"},
    {"name": "3 Simon won (bench next)", "stage": 2, "flags": _H3 + ["simon_won"], "anchor": "plaza_bench", "time": "auto"},
    {"name": "4 night, hooded man waits", "stage": 2, "flags": _H3 + ["simon_won", "mago_roof"], "anchor": "plaza_center", "time": "auto"},
    {"name": "5 Stamp Card (Hakim next)", "stage": 3, "flags": _H3 + ["simon_won", "mago_roof", "courier_met"], "anchor": "bakery_door", "time": "auto"},
    {"name": "6 Hakim's hint (Kemet next)", "stage": 3, "flags": _B, "anchor": "farmer_field", "time": "auto"},
    {"name": "7 Lantern won (hatch next)", "stage": 3, "flags": _B + ["farmer_won"], "anchor": "mini_pyramid_hatch", "time": "auto"},
    {"name": "8 in the cistern (Bakura)", "stage": 3, "flags": _B + ["farmer_won"], "anchor": "spawn_stairs", "time": "auto"},
    {"name": "9 Lost stamp (glyph, stairs)", "stage": 3, "flags": _B + ["farmer_won", "treasure_lost"], "anchor": "wall_glyph", "time": "auto"},
    {"name": "10 Jono asked (Rex next)", "stage": 3, "flags": _B + ["jono_asked"], "anchor": "plaza_center", "time": "auto"},
    {"name": "11 Teana's errands", "stage": 3, "flags": _B + ["teana_asked", "jug_taken"], "anchor": "teana_stall", "time": "auto"},
    {"name": "12 errands done (Teana next)", "stage": 3, "flags": _B + ["teana_asked", "jug_taken", "got_honey", "got_water", "got_dates"], "anchor": "teana_stall", "time": "auto"},
    {"name": "13 two stamps (Teana last)", "stage": 3, "flags": _B + ["farmer_won", "jono_asked", "treasure_lost", "treasure_won", "teana_asked", "jug_taken", "got_honey", "got_water", "got_dates"],
     "anchor": "teana_stall", "time": "auto"},
]
# a narrator page with a label is not speech: its kind decides the banner (en labels; pt pages follow the same index)
LABEL_KIND = {"Objective": "objective", "Reward": "item", "You got": "item", "Stamp": "item", "End of Chapter 1": "complete"}
NOTIFY = {"en": {"objective": "NEW OBJECTIVE", "item": "ITEM OBTAINED", "complete": "QUEST COMPLETE", "caption": "", "press": "X: continue", "card": "CARD OBTAINED"},
          "pt": {"objective": "NOVO OBJETIVO", "item": "ITEM OBTIDO", "complete": "MISSAO CUMPRIDA", "caption": "", "press": "X: continuar", "card": "CARTA OBTIDA"}}
PART_END = {}      # a duel win that ends the part (a "then" script after the win scene); part 3 ends by an "auto" rule instead
# effects the runtime derives from state instead of executing (items from flags, time of day / placement from "painted" and "places")
DERIVED = {"give_item", "set_time", "remove_npc", "place_npc"}
# items are derived from flags; "until" is the flag that uses them up (the jug is filled at the river, the ingredients go into the cakes); icon files exist for the treasures
ITEM_FLAG = {"stamp_card": ("courier_met", None, "assets/icon_stamp_card.bin"), "lantern": ("farmer_won", None, "assets/icon_lantern.bin"),
             "jug": ("jug_taken", "got_water", "assets/icon_water_jug.bin"), "honey": ("got_honey", "treasure_given", "assets/icon_honey_jar.bin"),
             "river_water": ("got_water", "treasure_given", "assets/icon_river_water.bin"), "dates": ("got_dates", "treasure_given", "assets/icon_dates.bin"),
             "scarab": ("treasure_lost", None, "assets/icon_founders_scarab.bin"), "bandana": ("treasure_won", None, "assets/icon_jonos_bandana.bin"),
             "charm": ("treasure_given", None, "assets/icon_lucky_charm.bin")}
ITEM_ORDER = ["stamp_card", "lantern", "jug", "honey", "river_water", "dates", "scarab", "bandana", "charm"]
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
    t = {"en": ("Part 3 complete", "That is all for this test build.", "Next: across the bridge to the harbor (part 4)."),
         "pt": ("Parte 3 completa", "E tudo por esta versao de teste.", "Proximo: a ponte e o porto (parte 4).")}[lang]
    return {"id": "dk_part3_end", "pages": [{"speaker": "narrator", "label": t[0], "kind": "complete", "text": t[1] + " " + t[2]}]}


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
        if n["id"] in PLACES: e["places"] = PLACES[n["id"]]
        if n["id"] == "hooded_man":   # placed by the bench script, gone after the riddle: there from the bench scene until the Stamp Card is given
            e["places"] = [{"when": {"stage_ge": 2, "stage_lt": 3, "needs": ["mago_roof"], "lacks": ["courier_met"]}, "tile": [18.5, 30.5]}]
        npcs.append(e)
    # objects of the pictures: the bench, the notice board, the date palm, the river, the hatch of the little pyramid (village); the glyph and the stairs (cistern)
    objects = []
    for o in en["objects"]:
        if o["id"] not in ("plaza_bench", "notice_sign", "date_palm", "river_bank", "pyramid_hatch", "cistern_glyph", "cistern_exit"): continue
        talk = talk_rules(o["dialogue_rules"], scripts, duels)
        e = {"id": o["id"], "anchor": o["anchor"], "talk": talk}
        if o["id"] == "plaza_bench":
            e["prop"] = "bench"; e["reach"] = 78
            for t in talk:
                if t["scene"] == "dk1_bench":
                    t["pose"] = "sit"
                    t["when"].setdefault("lacks", []).append("mago_roof")      # the night scene plays once; after it the bench is the plain "after" line
        if o["id"] == "pyramid_hatch":
            tr = [x for x in en["transitions"] if x["id"] == "enter_cistern"][0]
            assert tr["trigger"]["object"] == "pyramid_hatch"
            dst = tr["effects"][0]["teleport"]
            talk.insert(0, {"when": when(tr["when"]), "scene": tr["script"], "effects": {"warp": [dst["area"], dst["anchor"]]}})
            e["prop"] = "hatch"; e["prop_anchor"] = "hatch_prop"; e["open_when"] = {"needs": ["farmer_won"]}; e["reach"] = 62
        if o["id"] == "cistern_exit":
            tr = [x for x in en["transitions"] if x["id"] == "leave_cistern"][0]
            dst = tr["effects"][0]["teleport"]
            talk.append({"scene": tr["script"], "effects": {"warp": [dst["area"], dst["anchor"]]}})
            e["reach"] = 80
        if o["id"] == "cistern_glyph": e["reach"] = 90
        objects.append(e)
    ev = [e for e in en["observer_events"] if e["id"] == "roof_at_night"][0]
    gl = [e for e in en["observer_events"] if e["id"] == "cistern_glyph"][0]
    three = ["heard_teana", "heard_jono", "heard_guard"]
    cakes = ["teana_asked", "got_honey", "got_water", "got_dates"]
    S3 = {"stage_ge": 3, "stage_lt": 4}

    def g(extra, **kw):
        w = dict(S3); w.update(extra)
        return dict({"when": w}, **kw)
    guide = [
        {"when": {"stage_ge": 1, "stage_lt": 2, "lacks": ["heard_teana"]}, "npc": "teana"},
        {"when": {"stage_ge": 1, "stage_lt": 2, "lacks": ["heard_jono"]}, "npc": "jono"},
        {"when": {"stage_ge": 1, "stage_lt": 2, "lacks": ["heard_guard"]}, "npc": "guard"},
        {"when": {"stage_ge": 1, "stage_lt": 2, "needs": three}, "npc": "simon"},
        {"when": {"stage_ge": 2, "stage_lt": 3, "lacks": ["simon_won"]}, "npc": "simon"},
        {"when": {"stage_ge": 2, "stage_lt": 3, "needs": ["simon_won"], "lacks": ["mago_roof"]}, "anchor": "plaza_bench"},
        {"when": {"stage_ge": 2, "stage_lt": 3, "needs": ["mago_roof"]}, "npc": "hooded_man"},
        # the cistern first (its rules hold only there): Bakura, then the glyph is optional, then the stairs
        {"when": {"stage_ge": 3, "area": 1, "lacks": ["treasure_lost"]}, "npc": "bakura"},
        {"when": {"stage_ge": 3, "area": 1}, "anchor": "exit_stairs"},
        # the village, in the order of the HUD line: Teana's cakes, Rex, the hatch, Kemet, Hakim
        g({"needs": cakes, "lacks": ["treasure_given"]}, npc="teana"),
        g({"needs": ["teana_asked"], "lacks": ["got_honey", "treasure_given"]}, npc="baker"),
        g({"needs": ["teana_asked", "got_honey"], "lacks": ["got_water", "treasure_given"]}, anchor="river_bank"),
        g({"needs": ["teana_asked", "got_honey", "got_water"], "lacks": ["got_dates", "treasure_given"]}, anchor="date_palm"),
        g({"needs": ["jono_asked"], "lacks": ["treasure_won"]}, npc="rex"),
        g({"needs": ["farmer_won"], "lacks": ["treasure_lost"]}, anchor="hatch_prop"),
        g({"needs": ["baker_hint"], "lacks": ["farmer_won"]}, npc="farmer"),
        g({"lacks": ["baker_hint"]}, npc="baker"),
        {"when": {"stage_ge": 4, "stage_lt": 5}},      # no npc, no anchor: the bridge
    ]
    steps = {q["id"]: [s["objective"] for s in q["steps"]] for q in en["quests"]}
    flat_ids = ["q03_stakeout", "q04_lost", "q05_won", "q06_given"]
    base = {}
    k = 0
    for qid in flat_ids:
        base[qid] = k; k += len(steps[qid])
    st = lambda q, i: {"text": base[q] + i}      # a line's text: the flat quest_steps list
    journal = [
        {"id": "q01_whispers", "active": {"stage_ge": 1}, "done": {"needs": three},
         "lines": [{"npc": "teana", "done": {"needs": ["heard_teana"]}}, {"npc": "jono", "done": {"needs": ["heard_jono"]}}, {"npc": "guard", "done": {"needs": ["heard_guard"]}}]},
        {"id": "q02_sage", "active": {"stage_ge": 1, "needs": three}, "done": {"needs": ["simon_won"]}, "lines": []},
        {"id": "q03_stakeout", "active": {"stage_ge": 2, "needs": ["simon_won"]}, "done": {"needs": ["courier_met"]},
         "lines": [dict(st("q03_stakeout", 0), done={"needs": ["mago_roof"]}), dict(st("q03_stakeout", 1), done={"needs": ["courier_met"]})]},
        {"id": "q04_lost", "active": {"stage_ge": 3}, "done": {"needs": ["treasure_lost"]}, "hide_done": 1,
         "lines": [dict(st("q04_lost", 0), active={"lacks": ["baker_hint"]}, done={"needs": ["baker_hint"]}),
                   dict(st("q04_lost", 1), active={"needs": ["baker_hint"], "lacks": ["farmer_won"]}, done={"needs": ["farmer_won"]}),
                   dict(st("q04_lost", 2), active={"needs": ["farmer_won"], "lacks": ["treasure_lost"], "area": 0}),
                   dict(st("q04_lost", 3), active={"needs": ["farmer_won"], "lacks": ["treasure_lost"], "area": 1}, done={"needs": ["treasure_lost"]})]},
        {"id": "q05_won", "active": {"stage_ge": 3}, "done": {"needs": ["treasure_won"]}, "hide_done": 1,
         "lines": [dict(st("q05_won", 0), active={"lacks": ["jono_asked"]}, done={"needs": ["jono_asked"]}),
                   dict(st("q05_won", 1), active={"needs": ["jono_asked"], "lacks": ["treasure_won"]}, done={"needs": ["treasure_won"]})]},
        {"id": "q06_given", "active": {"stage_ge": 3}, "done": {"needs": ["treasure_given"]}, "hide_done": 1,
         "lines": [dict(st("q06_given", 0), active={"lacks": ["teana_asked"]}, done={"needs": ["teana_asked"]}),
                   dict(st("q06_given", 1), active={"needs": ["teana_asked"], "lacks": ["got_honey"]}, done={"needs": ["got_honey"]}),
                   dict(st("q06_given", 2), active={"needs": ["teana_asked"], "lacks": ["got_water"]}, done={"needs": ["got_water"]}),
                   dict(st("q06_given", 3), active={"needs": ["teana_asked"], "lacks": ["got_dates"]}, done={"needs": ["got_dates"]}),
                   dict(st("q06_given", 4), active={"needs": cakes, "lacks": ["treasure_given"]}, done={"needs": ["treasure_given"]})]},
    ]
    # the HUD line: the story's list, plus "Talk to the hooded man" once the bench scene is over (its step is the second of quest 3) and
    # "Duel Bakura" while the player is in the cistern (the fourth step of quest 4); the language files get the same list in the same order
    hood_when = {"stage_ge": 2, "stage_lt": 3, "needs": ["mago_roof"]}
    cist_when = {"stage_ge": 3, "stage_lt": 4, "area": 1, "lacks": ["treasure_lost"]}
    hud = [(when(h["when"]), h["text"], pt["hud_objectives"][i]["text"]) for i, h in enumerate(en["hud_objectives"])]
    k = [i for i, (w, t, p) in enumerate(hud) if t.startswith("Sit on the plaza bench")][0]
    hud.insert(k, (hood_when, en["quests"][2]["steps"][1]["objective"], pt["quests"][2]["steps"][1]["objective"]))
    hud.insert(0, (cist_when, en["quests"][3]["steps"][3]["objective"], pt["quests"][3]["steps"][3]["objective"]))
    objectives = [{"when": w, "text": t} for w, t, p in hud]
    items = []
    for iid in ITEM_ORDER:
        it = [x for x in en["items"] if x["id"] == iid][0]
        flag, until, icon = ITEM_FLAG[iid]
        e = {"name": it["name"], "flag": flag}
        if until: e["until"] = until
        if icon: e["icon"] = icon
        items.append(e)
    item_names = {c: [[x for x in src["items"] if x["id"] == iid][0]["name"] for iid in ITEM_ORDER] for c, src in (("en", en), ("pt", pt))}
    painted = {"bridge_open": {"stage_ge": 4},
               "music": VILLAGE_MUSIC,
               "night": {"stage_ge": 2, "stage_lt": 3, "needs": ["mago_roof"], "lacks": ["courier_met"]},
               "time_events": [{"script": "dk1_bench", "page": 1, "time": "night"}, {"script": "dk1_hooded_riddle", "page": 11, "time": "auto"}],
               "observers": [{"npc": ev["npc"], "sprite": ev["sprite"], "overlay": ev["overlay"], "anchor": ev["anchor"], "script": ev["show_during"]["script"],
                              "pages": list(range(ev["show_during"]["pages"][0], ev["show_during"]["pages"][1] + 1)), "vanish": ev["vanish"]},
                             # the glyph: no figure, only the writing, shown during the first two pages of the wall script and gone with a glitch on the third
                             {"npc": gl["npc"], "glyph": 1, "overlay": gl["overlay"], "anchor": gl["anchor"], "script": "dk1_mago_glyph", "pages": [0, 1], "vanish": "glitch"}]}
    # stage 3 -> 4 by itself once the three treasures are in hand (the "when_true" transition), then the end of this part
    tr = [x for x in en["transitions"] if x["id"] == "treasures_done"][0]
    auto = [{"when": dict(when(tr["when"]), stage_lt=4), "result": {"stage": 4}, "scene": tr["script"], "then": "dk_part3_end"}]
    j = dict(old)
    j.update({
        "flags": flags, "npcs": npcs, "speakers": speakers, "objectives": objectives, "guide": guide, "journal": journal,
        "chapters": [{"text": en["chapters"][0]["title"]}], "items": items, "triggers": [], "spots": [],
        "objects": objects, "intro": "dk1_intro", "painted": painted, "debug": DEBUG_PRESETS, "auto": auto,
        "story": "duelist_kingdom part 3",
    })
    j["areas"] = [dict(a) for a in old["areas"]]
    j["areas"][0]["name"] = en["areas"][0]["name"]
    with open(os.path.join(MOD, "assets/journey.json"), "w", encoding="utf-8") as f:
        json.dump(j, f, indent=1, ensure_ascii=True)

    ui_extra = {
        "en": {"jr": {"heading": "JOURNAL", "reward": "Reward:", "empty": "No quests yet.", "more": "More quests arrive in the next parts of the story.", "close": "Triangle: close"},
               "hint_painted": "Arrows: walk   Circle: run   X: talk   Triangle: journal   Select: map on/off   Start: menu",
               "part_end": "The harbor road opens in part 4.",
               "rewards": ["Rumor Notebook filled (3 rumors)", "card Magician of Faith; the legend of the Kingdom", "Stamp Card with three stamp slots",
                           "Founder's Scarab, cards Killer Needle and The 13th Grave, stamp Lost", "Jono's Bandana, cards Uraby and Dragon Treasure, stamp Won",
                           "Lucky Charm, card Kuriboh, stamp Given"],
               "jr_extra": {"items": "Items:", "stamp": "Stamp Card:"}, "stamps": ["Lost", "Won", "Given"]},
        "pt": {"jr": {"heading": "DIARIO", "reward": "Recompensa:", "empty": "Nenhuma missao ainda.", "more": "Mais missoes chegam nas proximas partes da historia.", "close": "Triangulo: fechar"},
               "hint_painted": "Setas: andar   Circulo: correr   X: falar   Triangulo: diario   Select: mapa liga/desliga   Start: menu",
               "part_end": "A estrada do porto abre na parte 4.",
               "rewards": ["Caderno de Cochichos completo (3 cochichos)", "carta Magician of Faith; a lenda do Reino", "Cartao de Selos com tres espacos de selo",
                           "Escaravelho do Fundador, cartas Killer Needle e The 13th Grave, selo Perdido", "Bandana do Jono, cartas Uraby e Dragon Treasure, selo Ganho",
                           "Amuleto da Sorte, carta Kuriboh, selo Dado"],
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
        ui["objectives"] = [p if code == "pt" else t for w, t, p in hud]
        ui["chapters"] = [src["chapters"][0]["title"]]
        ui["items"] = item_names[code]
        ui["npc_names"] = {n["id"]: n["name"] for n in src["npcs"] if n["id"] in VILLAGE_NPCS}
        ui["speaker_names"] = {k: v["name"] for k, v in src["speakers"].items() if k not in ("atos", "narrator")}
        ui["areas"][0] = src["areas"][0]["name"]
        qs = {q["id"]: q for q in src["quests"]}
        qids = ["q01_whispers", "q02_sage", "q03_stakeout", "q04_lost", "q05_won", "q06_given"]
        ui["quest_titles"] = [qs[i]["title"] for i in qids]
        ui["quest_objectives"] = [qs[i]["steps"][0]["objective"] for i in qids]
        ui["quest_steps"] = [s["objective"] for i in flat_ids for s in qs[i]["steps"]]
        ui["quest_rewards"] = ex["rewards"]
        ui["journal"] = dict(ex["jr"], items=ex["jr_extra"]["items"], stamp=ex["jr_extra"]["stamp"], stamp_lost=ex["stamps"][0], stamp_won=ex["stamps"][1], stamp_given=ex["stamps"][2])
        ui["hint"]["painted"] = ex["hint_painted"]
        ui["messages"]["part_end"] = ex["part_end"]
        ui["notify"] = NOTIFY[code]
        ui["painted"] = {"cistern": [a for a in src["areas"] if a["id"] == "cistern"][0]["name"]}
        with open(os.path.join(MOD, "assets/lang/%s/ui.json" % code), "w", encoding="utf-8") as f:
            json.dump(ui, f, indent=2, ensure_ascii=False)
            f.write("\n")
    # the duel decks of the new villagers (the game's duelists "Villager 1", "Villager 3", "Yami Bakura") go into mod.json
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
