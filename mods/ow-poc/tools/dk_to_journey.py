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
REPO = os.path.dirname(os.path.dirname(MOD))
DK = sys.argv[1] if len(sys.argv) > 1 else os.path.join(REPO, "journey_content", "duelist_kingdom")
CATALOG = os.path.join(MOD, "tools", "card-catalog.csv")
# the people of the painted village: (3D mesh for the old map view, tile).  hooded_man has no fixed tile: the story places him ("places").
VILLAGE_NPCS = {"simon": ("Wizard", [14.5, 28.5]), "teana": ("Ninja_Sand_Female", [9.5, 32.5]), "jono": ("Ninja_Sand", [19.5, 32.5]), "guard": ("Knight_Male", [24.5, 23.5]),
                "hooded_man": ("Wizard", None), "baker": ("Worker_Male", [30.5, 30.5]), "farmer": ("Ninja_Sand", [21.5, 34.5]),
                "rex": ("Suit_Male", None), "bakura": ("Wizard", [2.5, 2.5]),
                # chapter 1 (harbor, ship) and chapter 2 (the Shore of Illusions): only in the painted places, so no tile; "places" show them by stage
                "soldier": ("Knight_Male", None), "shadi": ("Wizard", None), "mai": ("Ninja_Sand_Female", None), "inseto_kaiba": ("Suit_Male", None),
                "weevil": ("Suit_Male", None), "hooded_shore": ("Wizard", None), "dock_dan": ("Worker_Male", None), "purser": ("Worker_Male", None),
                "shell_sue": ("Ninja_Sand_Female", None),
                # chapter 3 (the Forest of Whispers)
                "rex_forest": ("Suit_Male", None), "forest_mage": ("Wizard", None), "hermit_hob": ("Worker_Male", None),
                # chapter 4 (the Mountain Pass)
                "keith": ("Suit_Male", None), "mai_mountain": ("Ninja_Sand_Female", None), "star_carver": ("Wizard", None),
                "mountain_mage": ("Wizard", None), "cliff_cass": ("Ninja_Sand_Female", None)}
# the anchors several places share ("shop_stall", "arena_door") are written with their area
QUALIFIED = {"dock_dan": "harbor.shop_stall", "purser": "ship_deck.shop_stall", "shell_sue": "kingdom_beach.shop_stall",
             "hermit_hob": "kingdom_forest.shop_stall", "rex_forest": "kingdom_forest.rex_spot", "forest_mage": "kingdom_forest.gate_spot",
             "keith": "kingdom_mountain.keith_spot", "mai_mountain": "kingdom_mountain.mai_spot", "star_carver": "kingdom_mountain.cave_spot",
             "mountain_mage": "kingdom_mountain.gate_spot", "cliff_cass": "kingdom_mountain.shop_stall"}
# who stands where, and when (the painted places; no tile on the old map)
PAINTED_PLACES = {
    "soldier": [{"when": {"stage_ge": 4}}],
    "shadi": [{"when": {"stage_ge": 5, "stage_lt": 6, "needs": ["inspector_won"], "lacks": ["shadi_won"]}}],
    "mai": [{"when": {"stage_ge": 7, "stage_lt": 8}}],
    "inseto_kaiba": [{"when": {"stage_ge": 7, "stage_lt": 8}}],
    "weevil": [{"when": {"stage_ge": 11, "needs": ["weevil_met"]}}],
    "hooded_shore": [{"when": {"stage_ge": 11, "lacks": ["hooded_shore"]}}],
    "dock_dan": [{"when": {"stage_ge": 5}}],
    "purser": [{"when": {"stage_ge": 7, "stage_lt": 8}}],
    "shell_sue": [{"when": {"stage_ge": 10}}],
    "rex_forest": [{"when": {"stage_ge": 13}}],
    "forest_mage": [{"when": {"stage_ge": 15}}],
    "hermit_hob": [{"when": {"stage_ge": 13}}],
    "keith": [{"when": {"stage_ge": 17}}],
    "mai_mountain": [{"when": {"stage_ge": 18}}],
    "star_carver": [{"when": {"stage_ge": 19, "stage_lt": 20}}],
    "mountain_mage": [{"when": {"stage_ge": 20}}],
    "cliff_cass": [{"when": {"stage_ge": 17}}],
}
# the friends come to the pier to say goodbye (stage 6): they keep their village tile, the painted anchor moves
FAREWELL = {"simon": "farewell_simon", "teana": "farewell_teana", "jono": "farewell_jono"}
# duelists of the mod's own (duelists/<id>.json: copy = the disc duelist whose face and AI it borrows, name = its deck in mod.json)
DK_DUELISTS = {"shadi": ("dk_shadi", "Shadi", "Shadi Courier"), "inseto_kaiba": ("dk_inseto", "Seto", "InsetoKaiba"),
               "weevil": ("dk_weevil", "Weevil Underwood", "Weevil Shore"),
               "rex_forest": ("dk_rex_forest", "Rex Raptor", "Rex Forest"), "forest_mage": ("dk_forest_mage", "Forest Mage", "Forest Mage Grove"),
               "keith": ("dk_keith", "Bandit Keith", "Keith Toll"), "mai_mountain": ("dk_mai_mountain", "Mai Valentine", "Mai Cliff"),
               "mountain_mage": ("dk_mountain_mage", "Mountain Mage", "Mountain Mage Summit")}
STARTER_NOTE = "a new journey's deck: 40 weak commons (journey_content/duelist_kingdom/decks_dk.json starter)"
# where the old 3D map would put people the painted picture shows elsewhere (Rex on the east road once placed, Bakura in the cistern: never really seen there)
PLACES = {"rex": [{"when": {"stage_ge": 3}, "tile": [37.5, 29.5]}]}
# the village's songs, sound-driver package numbers (song 0x7000 + 16 * n): 10 is the game's own campaign-map song (sustained, quiet),
# 25 a slow pad that swells in; both measured steady and low in activity (see DK_PART2_README)
VILLAGE_MUSIC = {"day": 10, "night": 25, "cistern": 26,
                 "harbor": 18, "ship_deck": 20, "kingdom_beach": 30, "kingdom_forest": 21, "kingdom_mountain": 22}   # the disc's Nile River, Desert Temple and Tournament Island songs      # 26: the Sand Ruins song, a low sustained pad: the cistern is dim and quiet
# debug presets (jm_debug.c: L1+R1+Up/Down in the village, or "preset" in debug.json): a state of the story to jump to
_H3 = ["heard_teana", "heard_jono", "heard_guard"]
_B = _H3 + ["simon_won", "mago_roof", "courier_met", "baker_hint"]
_ALL3 = _B + ["farmer_won", "jono_asked", "treasure_lost", "treasure_won", "teana_asked", "jug_taken", "got_honey", "got_water", "got_dates", "treasure_given"]
_SHIP = _ALL3 + ["inspector_won", "shadi_won", "mago_passage", "simon_farewell", "teana_farewell", "jono_farewell", "mai_met", "mago_mast"]
_SHORE = _SHIP + ["beach_arrived", "pegasus_mirror", "weevil_met", "weevil_won", "camp_met", "hooded_shore"]
_FOREST = _SHORE + ["forest_arrived", "rex_forest_won", "star_mark_1", "star_mark_2", "star_mark_3"]
_MOUNT = _FOREST + ["forest_mage_won"]
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
    {"name": "14 harbor gate (Inspector)", "stage": 5, "flags": _ALL3, "anchor": "spawn_gate", "time": "auto", "stars": 0},
    {"name": "15 Courier at the pier end", "stage": 5, "flags": _ALL3 + ["inspector_won"], "anchor": "harbor_mid", "time": "auto", "stars": 0},
    {"name": "16 farewells on the pier", "stage": 6, "flags": _ALL3 + ["inspector_won", "shadi_won", "mago_passage"], "anchor": "harbor_mid", "time": "auto", "stars": 1},
    {"name": "17 on the ship (Mai, InsetoKaiba)", "stage": 7, "flags": _ALL3 + ["inspector_won", "shadi_won", "mago_passage", "simon_farewell", "teana_farewell", "jono_farewell"],
     "anchor": "spawn_gangway", "time": "auto", "stars": 1},
    {"name": "18 beach landing (chapter 2)", "stage": 10, "flags": _SHIP, "anchor": "kingdom_beach.spawn", "time": "auto", "stars": 1},
    {"name": "19 Weevil ambush", "stage": 11, "flags": _SHIP + ["beach_arrived", "pegasus_mirror"], "anchor": "beach_center", "time": "auto", "stars": 1},
    {"name": "20 Weevil waits (wager)", "stage": 11, "flags": _SHIP + ["beach_arrived", "pegasus_mirror", "weevil_met"], "anchor": "beach_center", "time": "auto", "stars": 1},
    {"name": "21 chapter 2 done", "stage": 12, "flags": _SHIP + ["beach_arrived", "pegasus_mirror", "weevil_met", "weevil_won"], "anchor": "beach_center", "time": "auto", "stars": 2},
    {"name": "22 forest arrival (chapter 3)", "stage": 13, "flags": _SHORE, "anchor": "kingdom_forest.spawn", "time": "auto", "stars": 2},
    {"name": "23 Rex waits (wager)", "stage": 13, "flags": _SHORE + ["forest_arrived"], "anchor": "kingdom_forest.forest_center", "time": "auto", "stars": 2},
    {"name": "24 Star Marks", "stage": 14, "flags": _SHORE + ["forest_arrived", "rex_forest_won"], "anchor": "kingdom_forest.forest_center", "time": "auto", "stars": 3},
    {"name": "25 two marks read", "stage": 14, "flags": _SHORE + ["forest_arrived", "rex_forest_won", "star_mark_1", "star_mark_2"], "anchor": "kingdom_forest.hangout_a", "time": "auto", "stars": 3},
    {"name": "26 Forest Mage (wager)", "stage": 15, "flags": _FOREST, "anchor": "kingdom_forest.forest_center", "time": "auto", "stars": 3},
    {"name": "27 chapter 3 done", "stage": 16, "flags": _FOREST + ["forest_mage_won"], "anchor": "kingdom_forest.forest_center", "time": "auto", "stars": 4},
    {"name": "28 mountain arrival (chapter 4)", "stage": 17, "flags": _MOUNT, "anchor": "kingdom_mountain.spawn", "time": "auto", "stars": 4},
    {"name": "29 Keith's toll (wager)", "stage": 17, "flags": _MOUNT + ["mountain_arrived"], "anchor": "kingdom_mountain.pass_center", "time": "auto", "stars": 4},
    {"name": "30 Mai across the bridge (pride duel)", "stage": 18, "flags": _MOUNT + ["mountain_arrived", "keith_won"], "anchor": "kingdom_mountain.hangout_a", "time": "auto", "stars": 5},
    {"name": "31 the star-carver's cave", "stage": 19, "flags": _MOUNT + ["mountain_arrived", "keith_won", "mai_mountain_won"], "anchor": "kingdom_mountain.hangout_a", "time": "auto", "stars": 5},
    {"name": "32 Mountain Mage (wager)", "stage": 20, "flags": _MOUNT + ["mountain_arrived", "keith_won", "mai_mountain_won", "carver_found"], "anchor": "kingdom_mountain.hangout_a", "time": "auto", "stars": 5},
    {"name": "33 chapter 4 done", "stage": 21, "flags": _MOUNT + ["mountain_arrived", "keith_won", "mai_mountain_won", "carver_found", "mountain_mage_won"], "anchor": "kingdom_mountain.hangout_a", "time": "auto", "stars": 6},
]
# a narrator page with a label is not speech: its kind decides the banner (en labels; pt pages follow the same index)
LABEL_KIND = {"Objective": "objective", "Reward": "item", "You got": "item", "Stamp": "item", "End of Chapter 1": "complete", "End of Chapter 2": "complete", "End of Chapter 3": "complete", "End of Chapter 4": "complete"}
NOTIFY = {"en": {"objective": "NEW OBJECTIVE", "item": "ITEM OBTAINED", "complete": "QUEST COMPLETE", "caption": "", "press": "X: continue", "card": "CARD OBTAINED"},
          "pt": {"objective": "NOVO OBJETIVO", "item": "ITEM OBTIDO", "complete": "MISSAO CUMPRIDA", "caption": "", "press": "X: continuar", "card": "CARTA OBTIDA"}}
PART_END = {}      # a duel win that ends the part (a "then" script after the win scene); part 3 ends by an "auto" rule instead
# effects the runtime derives from state instead of executing (items from flags, time of day / placement from "painted" and "places")
DERIVED = {"give_item", "set_time", "remove_npc", "place_npc", "move_npc", "show_prop"}
# items are derived from flags; "until" is the flag that uses them up (the jug is filled at the river, the ingredients go into the cakes); icon files exist for the treasures
ITEM_FLAG = {"stamp_card": ("courier_met", None, "assets/icon_stamp_card.bin"), "lantern": ("farmer_won", None, "assets/icon_lantern.bin"),
             "jug": ("jug_taken", "got_water", "assets/icon_water_jug.bin"), "honey": ("got_honey", "treasure_given", "assets/icon_honey_jar.bin"),
             "river_water": ("got_water", "treasure_given", "assets/icon_river_water.bin"), "dates": ("got_dates", "treasure_given", "assets/icon_dates.bin"),
             "scarab": ("treasure_lost", None, "assets/icon_founders_scarab.bin"), "bandana": ("treasure_won", None, "assets/icon_jonos_bandana.bin"),
             "charm": ("treasure_given", None, "assets/icon_lucky_charm.bin"),
             "star_passage": ("shadi_won", None, "assets/icon_stamp_card.bin"), "bug_pin": ("inseto_won", None, "assets/icon_founders_scarab.bin"),
             "loaded_dice": ("weevil_won", None, None), "whisper_leaf": ("forest_mage_won", None, None), "star_chisel": ("carver_found", None, None),
             "star_chips": ("shadi_won", None, "assets/icon_star_chips.bin")}
ITEM_ORDER = ["stamp_card", "lantern", "jug", "honey", "river_water", "dates", "scarab", "bandana", "charm", "star_passage", "bug_pin", "loaded_dice", "whisper_leaf", "star_chisel", "star_chips"]
# Mochila texts for the Kingdom's items, accented (the UI font has them; the dialogue font is ASCII): (description, where from)
BAG_TEXT = {
 "en": {"star_chips": ("The Kingdom's star chips. Only the story's gatekeepers and zone masters hand them out, one each, and a lost one stays with the duelist who took it until you beat him. Ten open the castle.", "Shadi's Star Passage, then the duelists who guard each zone.")},
 "pt": {"star_chips": ("As fichas de estrela do Reino. Só os guardiões e mestres de zona da história as entregam, uma cada, e uma estrela perdida fica com quem a tomou até você vencê-lo. Dez abrem o castelo.", "A Passagem Estelar do Shadi, depois os duelistas que guardam cada zona."),
        "star_passage": ("Seu bilhete para o Reino dos Duelistas.", "Shadi, no porto."),
        "bug_pin": ("O broche dourado do InsetoKaiba. Ele jura que vai pegar de volta.", "InsetoKaiba, no navio."),
        "loaded_dice": ("Os dados viciados do Weevil. Melhor nunca usar.", "Weevil, na Costa das Ilusões."),
        "whisper_leaf": ("Uma folha que farfalha perto de uma estrela.", "O Mago da Floresta."),
        "star_chisel": ("O cinzel do Croquet. A ponta ainda brilha como estrela.", "Croquet, na Caverna da Estrela.")},
}
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
        elif k == "earned": out["earned_min"] = v      # stars handed out so far (held + lost-and-owed): a star gate
        elif k == "earned_lt": out["earned_lt"] = v
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
        elif k == "add_stars": r["stars"] = r.get("stars", 0) + v
        elif k == "teleport": r["warp"] = [v["area"], v["anchor"]]
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
            if d.get("stars"): win["wager"] = d["stars"]       # a Kingdom star duel: +stars the first win, -1 a loss (ow_poc.c)
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
    assert [f["bit"] for f in sorted(en["flags"], key=lambda f: f["bit"])] == list(range(len(flags))) and len(flags) <= 64   # bits 32.. live in the save's kflags
    duels = {d["id"]: d for d in en["duels"]}
    speakers = {}
    for k, v in en["speakers"].items():
        pid = v["portrait"]
        speakers[k] = {"portrait_id": pid if 0 < pid <= 40 else 0}
    speakers["atos"] = {"portrait": "player"}
    # faces the disc does not have (art_dk/portraits, the disc's 48x48 record layout)
    for k, f in (("inseto", "portrait_inseto"), ("mago_dev", "portrait_mago_hood"), ("mago_hood", "portrait_mago_hood"), ("mago_dev_tee", "portrait_mago_tee")):
        if k in speakers: speakers[k]["portrait_file"] = "assets/%s.bin" % f
    scripts = {s["id"]: s for s in en["scripts"]}
    npcs = []
    for n in en["npcs"]:
        if n["id"] not in VILLAGE_NPCS: continue
        talk = talk_rules(n["dialogue_rules"], scripts, duels)
        mesh, tile = VILLAGE_NPCS[n["id"]]
        e = {"id": n["id"], "name": n["name"], "mesh": mesh, "anchor": QUALIFIED.get(n["id"], n["anchor"]), "talk": talk,
             "duelist_id": n["duelist_id"] if isinstance(n["duelist_id"], int) else 0, "portrait_id": speakers[n["portrait_speaker"]]["portrait_id"]}
        if n["id"] in DK_DUELISTS: e["duelist"] = DK_DUELISTS[n["id"]][0]
        if tile: e["tile"] = tile
        if n["id"] in PAINTED_PLACES: e["places"] = [dict(p, anchor=e["anchor"]) for p in PAINTED_PLACES[n["id"]]]
        if n["id"] in FAREWELL: e.setdefault("places", []).insert(0, {"when": {"stage_ge": 6, "stage_lt": 7}, "anchor": FAREWELL[n["id"]]})
        if n["id"] in PLACES: e["places"] = PLACES[n["id"]]
        if n["id"] == "hooded_man":   # placed by the bench script, gone after the riddle: there from the bench scene until the Stamp Card is given
            e["places"] = [{"when": {"stage_ge": 2, "stage_lt": 3, "needs": ["mago_roof"], "lacks": ["courier_met"]}, "tile": [18.5, 30.5]}]
        npcs.append(e)
    # objects of the pictures: the bench, the notice board, the date palm, the river, the hatch of the little pyramid (village); the glyph and the stairs (cistern)
    objects = []
    for o in en["objects"]:
        if o["id"] not in ("plaza_bench", "notice_sign", "date_palm", "river_bank", "pyramid_hatch", "cistern_glyph", "cistern_exit",
                           "bridge_north", "harbor_bridge_back", "ship_gangway", "barrel", "ship_bow", "pegasus_mirror", "shore_camp", "jungle_path",
                           "star_mark_1", "star_mark_2", "star_mark_3", "forest_gate", "pass_road", "forest_exit",
                           "star_cave", "summit_gate", "trail_camp", "mountain_exit"): continue
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
        # the ways between the places: a transition of the story is the first rule of its object
        for tr in en["transitions"]:
            if tr["trigger"].get("kind") == "interact" and tr["trigger"].get("object") == o["id"] and o["id"] not in ("pyramid_hatch", "cistern_exit"):
                rule = {"when": when(tr["when"]), "scene": tr["script"], "effects": result(tr["effects"])}
                if o["id"] == "harbor_bridge_back": rule["when"] = {"stage_ge": 5}
                talk.insert(0, rule)
        if o["id"] in ("bridge_north", "harbor_bridge_back", "ship_gangway", "ship_bow", "jungle_path", "pegasus_mirror", "star_mark_1", "star_mark_2", "star_mark_3", "forest_gate", "pass_road", "forest_exit", "star_cave", "summit_gate", "trail_camp", "mountain_exit"): e["reach"] = 80
        if o["id"] == "shore_camp": e["reach"] = 90
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
        {"when": {"stage_ge": 4, "stage_lt": 5}, "anchor": "bridge_north"},   # the open bridge: the harbor road
        # the harbor, the ship and the Shore of Illusions (an anchor or person in another place than the player's: the next rule)
        {"when": {"stage_ge": 5, "stage_lt": 6, "lacks": ["inspector_won"]}, "npc": "soldier"},
        {"when": {"stage_ge": 5, "stage_lt": 6}, "npc": "shadi"},
        {"when": {"stage_ge": 6, "stage_lt": 7, "lacks": ["simon_farewell"]}, "npc": "simon"},
        {"when": {"stage_ge": 6, "stage_lt": 7, "lacks": ["teana_farewell"]}, "npc": "teana"},
        {"when": {"stage_ge": 6, "stage_lt": 7, "lacks": ["jono_farewell"]}, "npc": "jono"},
        {"when": {"stage_ge": 6, "stage_lt": 7}, "anchor": "gangway"},
        {"when": {"stage_ge": 7, "stage_lt": 8, "lacks": ["mai_met"]}, "npc": "mai"},
        {"when": {"stage_ge": 7, "stage_lt": 8, "lacks": ["inseto_won"]}, "npc": "inseto_kaiba"},   # the rival's duel, then the bow
        {"when": {"stage_ge": 7, "stage_lt": 8}, "anchor": "bow"},
        {"when": {"stage_ge": 10, "stage_lt": 11}, "anchor": "mirror_spot"},
        {"when": {"stage_ge": 11, "stage_lt": 12}, "npc": "weevil"},
        {"when": {"stage_ge": 12, "lacks": ["hooded_shore"]}, "npc": "hooded_shore"},
        {"when": {"stage_ge": 12, "lacks": ["camp_met"]}, "anchor": "shore_camp"},
        {"when": {"stage_ge": 12, "stage_lt": 13}, "anchor": "jungle_path"},
        # chapter 3: Rex, the three marks (any order), the Forest Mage at the gate, then the pass
        {"when": {"stage_ge": 13, "stage_lt": 14}, "npc": "rex_forest"},
        {"when": {"stage_ge": 14, "stage_lt": 15, "lacks": ["star_mark_1"]}, "anchor": "star_mark_1"},
        {"when": {"stage_ge": 14, "stage_lt": 15, "lacks": ["star_mark_2"]}, "anchor": "star_mark_2"},
        {"when": {"stage_ge": 14, "stage_lt": 15, "lacks": ["star_mark_3"]}, "anchor": "star_mark_3"},
        {"when": {"stage_ge": 15, "stage_lt": 16}, "npc": "forest_mage"},
        {"when": {"stage_ge": 16, "stage_lt": 17}, "anchor": "pass_road"},
        # chapter 4: Keith at the bridge, Mai across it, the carver in the cave, the Mountain Mage at the summit, then the castle road
        {"when": {"stage_ge": 17, "stage_lt": 18}, "npc": "keith"},
        {"when": {"stage_ge": 18, "stage_lt": 19}, "npc": "mai_mountain"},
        {"when": {"stage_ge": 19, "stage_lt": 20}, "npc": "star_carver"},
        {"when": {"stage_ge": 20, "stage_lt": 21}, "npc": "mountain_mage"},
        {"when": {"stage_ge": 21}, "anchor": "summit_gate"},
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
        # chapter 1, the harbor and the ship; chapter 2, the Shore of Illusions (one line each: the quest's objective)
        {"id": "q07_harbor", "active": {"stage_ge": 4}, "done": {"needs": ["inspector_won"]}, "lines": []},
        {"id": "q08_courier", "active": {"stage_ge": 5, "needs": ["inspector_won"]}, "done": {"needs": ["shadi_won"]}, "lines": []},
        {"id": "q09_farewell", "active": {"stage_ge": 6}, "done": {"stage_ge": 7}, "lines": []},
        {"id": "q10_ship", "active": {"stage_ge": 7}, "done": {"stage_ge": 10}, "lines": []},
        {"id": "q11_shore", "active": {"stage_ge": 10}, "done": {"needs": ["weevil_won"]}, "lines": []},
        {"id": "q12_forest", "active": {"stage_ge": 13}, "done": {"needs": ["forest_mage_won"]}, "lines": []},
        {"id": "q13_mountain", "active": {"stage_ge": 17}, "done": {"needs": ["mountain_mage_won"]}, "lines": []},
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
    cat = CARD
    starter = []
    for name, n in load(os.path.join(DK, "decks_dk.json"))["starter"]["cards"].items():
        starter += [cat[name]] * n
    assert len(starter) == 40, len(starter)
    items = []
    for iid in ITEM_ORDER:
        it = [x for x in en["items"] if x["id"] == iid][0]
        flag, until, icon = ITEM_FLAG[iid]
        e = {"name": it["name"], "flag": flag}
        if until: e["until"] = until
        if icon: e["icon"] = icon
        if iid == "star_chips": e["key"] = "star_chips"; e["count"] = "stars"   # the Mochila shows "Star Chips xN" (jm_bag.c)
        items.append(e)
    item_names = {c: [[x for x in src["items"] if x["id"] == iid][0]["name"] for iid in ITEM_ORDER] for c, src in (("en", en), ("pt", pt))}
    painted = {"bridge_open": {"stage_ge": 4},
               "music": VILLAGE_MUSIC,
               "night": {"stage_ge": 2, "stage_lt": 3, "needs": ["mago_roof"], "lacks": ["courier_met"]},
               "time_events": [{"script": "dk1_bench", "page": 1, "time": "night"}, {"script": "dk1_hooded_riddle", "page": 11, "time": "auto"}],
               "observers": [{"npc": ev["npc"], "sprite": ev["sprite"], "overlay": ev["overlay"], "anchor": ev["anchor"], "script": ev["show_during"]["script"],
                              "pages": list(range(ev["show_during"]["pages"][0], ev["show_during"]["pages"][1] + 1)), "vanish": ev["vanish"]},
                             # the glyph: no figure, only the writing, shown during the first two pages of the wall script and gone with a glitch on the third
                             {"npc": gl["npc"], "glyph": 1, "overlay": gl["overlay"], "anchor": gl["anchor"], "script": "dk1_mago_glyph", "pages": [0, 1], "vanish": "glitch"}]
                            + [{"npc": e["npc"], "sprite": e["sprite"], "overlay": e["overlay"], "anchor": e["anchor"], "script": e["show_during"]["script"],
                                "pages": list(range(e["show_during"]["pages"][0], e["show_during"]["pages"][1] + 1)), "vanish": e["vanish"]}
                               for e in en["observer_events"] if e["id"] in ("breakwater_passage", "mast_top")],
               # ways shut until the story opens them: the harbor gate (the Inspector's exam) and the gangplank (boarded by talking at it)
               "blocks": [{"area": 3, "rect": [452, 180, 474, 720], "when": {"lacks": ["inspector_won"]}},
                          {"area": 3, "rect": [985, 300, 1070, 420]}]}
    # stage 3 -> 4 by itself once the three treasures are in hand (the "when_true" transition), then the end of this part
    tr = [x for x in en["transitions"] if x["id"] == "treasures_done"][0]
    auto = [{"when": dict(when(tr["when"]), stage_lt=4), "result": {"stage": 4}, "scene": tr["script"]}]
    # chapter 2: the landing and Weevil's ambush play by themselves on the beach (area 5)
    for tid in ("landing", "weevil_ambush"):
        tr = [x for x in en["transitions"] if x["id"] == tid][0]
        auto.append({"when": dict(when(tr["when"]), area=5), "result": result(tr["effects"]), "scene": tr["script"]})
    # chapter 3: the forest's arrival and the opening of the clearing (all three marks read) play by themselves (area 6)
    for tid in ("forest_arrival", "clearing_open"):
        tr = [x for x in en["transitions"] if x["id"] == tid][0]
        auto.append({"when": dict(when(tr["when"]), area=6), "result": result(tr["effects"]), "scene": tr["script"]})
    # chapter 4: the mountain's arrival plays by itself (area 7)
    tr = [x for x in en["transitions"] if x["id"] == "mountain_arrival"][0]
    auto.append({"when": dict(when(tr["when"]), area=7), "result": result(tr["effects"]), "scene": tr["script"]})
    j = dict(old)
    j.update({
        "flags": flags, "npcs": npcs, "speakers": speakers, "objectives": objectives, "guide": guide, "journal": journal,
        "chapters": [{"when": {"stage_lt": 10}, "text": en["chapters"][0]["title"]}, {"when": {"stage_lt": 13}, "text": en["chapters"][1]["title"]}, {"when": {"stage_lt": 17}, "text": en["chapters"][2]["title"]}, {"text": en["chapters"][3]["title"]}],
        "starter_deck": starter, "starter_note": STARTER_NOTE, "items": items, "triggers": [], "spots": [],
        "objects": objects, "intro": "dk1_intro", "painted": painted, "debug": DEBUG_PRESETS, "auto": auto,
        "story": "duelist_kingdom chapters 1-4",
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
                           "Lucky Charm, card Kuriboh, stamp Given", "card Warrior of Tradition; the harbor gate opens",
                           "Star Passage, a star, card Illusionist Faceless Mage", "card Mystical Elf; Simon's secret", "the star rules; land on the island",
                           "a second star, Loaded Dice, card Hercules Beetle", "the fourth star, Whisper Leaf, cards Megazowler and Mystic Horseman",
                           "the sixth star, Star Chisel, cards Pendulum Machine, Harpie Lady and Giant Soldier of Stone"],
               "jr_extra": {"items": "Items:", "stamp": "Stamp Card:"}, "stamps": ["Lost", "Won", "Given"]},
        "pt": {"jr": {"heading": "DIARIO", "reward": "Recompensa:", "empty": "Nenhuma missao ainda.", "more": "Mais missoes chegam nas proximas partes da historia.", "close": "Triangulo: fechar"},
               "hint_painted": "Setas: andar   Circulo: correr   X: falar   Triangulo: diario   Select: mapa liga/desliga   Start: menu",
               "part_end": "A estrada do porto abre na parte 4.",
               "rewards": ["Caderno de Cochichos completo (3 cochichos)", "carta Magician of Faith; a lenda do Reino", "Cartao de Selos com tres espacos de selo",
                           "Escaravelho do Fundador, cartas Killer Needle e The 13th Grave, selo Perdido", "Bandana do Jono, cartas Uraby e Dragon Treasure, selo Ganho",
                           "Amuleto da Sorte, carta Kuriboh, selo Dado", "carta Warrior of Tradition; o portao do porto abre",
                           "Passagem Estelar, uma estrela, carta Illusionist Faceless Mage", "carta Mystical Elf; o segredo do Simon", "as regras das estrelas; chegar a ilha",
                           "a segunda estrela, Dados Viciados, carta Hercules Beetle", "a quarta estrela, Folha Sussurrante, cartas Megazowler e Mystic Horseman",
                           "a sexta estrela, Cinzel Estelar, cartas Pendulum Machine, Harpie Lady e Giant Soldier of Stone"],
               "jr_extra": {"items": "Itens:", "stamp": "Cartao de Selos:"}, "stamps": ["Perdido", "Ganho", "Dado"]},
    }
    en_kind = {s["id"]: [LABEL_KIND.get(p.get("label"), "caption" if p.get("label") else "") for p in s["pages"]] for s in en["scripts"]}
    for code, src in (("en", en), ("pt", pt)):
        sc = [{"id": s["id"], "pages": [dict(p, **({"kind": en_kind[s["id"]][i]} if en_kind[s["id"]][i] else {})) for i, p in enumerate(s["pages"])]} for s in src["scripts"]]
        with open(os.path.join(MOD, "assets/lang/%s/story.json" % code), "w", encoding="utf-8") as f:
            json.dump({"scripts": sc}, f, indent=1, ensure_ascii=True)
        ui = load(os.path.join(HERE, "base_ui_%s.json" % code))
        ex = ui_extra[code]
        ui["objectives"] = [p if code == "pt" else t for w, t, p in hud]
        ui["chapters"] = [src["chapters"][0]["title"], src["chapters"][1]["title"], src["chapters"][2]["title"], src["chapters"][3]["title"]]
        ui["items"] = item_names[code]
        ui["npc_names"] = {n["id"]: n["name"] for n in src["npcs"] if n["id"] in VILLAGE_NPCS}
        ui["speaker_names"] = {k: v["name"] for k, v in src["speakers"].items() if k not in ("atos", "narrator")}
        ui["areas"][0] = src["areas"][0]["name"]
        qs = {q["id"]: q for q in src["quests"]}
        qids = ["q01_whispers", "q02_sage", "q03_stakeout", "q04_lost", "q05_won", "q06_given", "q07_harbor", "q08_courier", "q09_farewell", "q10_ship", "q11_shore", "q12_forest", "q13_mountain"]
        ui["quest_titles"] = [qs[i]["title"] for i in qids]
        ui["quest_objectives"] = [qs[i]["steps"][0]["objective"] for i in qids]
        ui["quest_steps"] = [s["objective"] for i in flat_ids for s in qs[i]["steps"]]
        ui["quest_rewards"] = ex["rewards"]
        ui["journal"] = dict(ex["jr"], items=ex["jr_extra"]["items"], stamp=ex["jr_extra"]["stamp"], stamp_lost=ex["stamps"][0], stamp_won=ex["stamps"][1], stamp_given=ex["stamps"][2])
        ui["hint"]["painted"] = ex["hint_painted"]
        ui["messages"]["part_end"] = ex["part_end"]
        ui["notify"] = NOTIFY[code]
        ui.setdefault("painted", {})
        # the Kingdom's items get their Mochila text from the story (the home town's are in base_ui_*.json)
        bag = ui.setdefault("bag", {})
        for iid in ITEM_ORDER:
            flag = ITEM_FLAG[iid][0]
            key = "star_chips" if iid == "star_chips" else flag
            if key in bag: continue
            it = [x for x in src["items"] if x["id"] == iid][0]
            bag[key] = {"desc": BAG_TEXT.get(code, {}).get(iid, (it.get("description", ""), ""))[0] or it.get("description", ""),
                        "from": BAG_TEXT.get(code, {}).get(iid, ("", it.get("source", "")))[1] or it.get("source", "")}
        for aid in ("cistern", "harbor", "ship_deck", "kingdom_beach", "kingdom_forest", "kingdom_mountain"):
            ui["painted"][aid] = [a for a in src["areas"] if a["id"] == aid][0]["name"]
        with open(os.path.join(MOD, "assets/lang/%s/ui.json" % code), "w", encoding="utf-8") as f:
            json.dump(ui, f, indent=2, ensure_ascii=False)
            f.write("\n")
    # the duel decks of the new villagers (the game's duelists "Villager 1", "Villager 3", "Yami Bakura") go into mod.json
    dk_decks = load(os.path.join(DK, "decks_dk.json"))["decks"]
    mod = load(os.path.join(MOD, "mod.json"))
    folder = os.path.join(MOD, "duelists")
    os.makedirs(folder, exist_ok=True)
    for d in duels.values():
        if d["npc"] in VILLAGE_NPCS and d["deck"] in dk_decks:
            mod["decks"][d["deck"]] = dict({"fixed": True}, **dk_decks[d["deck"]]["cards"])
        elif d["npc"] in VILLAGE_NPCS and d["deck"] not in mod["decks"]:
            warnings.append("no deck for %s (%s)" % (d["id"], d["deck"]))
    for npc, (did, copy, name) in DK_DUELISTS.items():     # a duelist of its own, so the disc's duelist keeps his deck in Free Duel
        with open(os.path.join(folder, did + ".json"), "w", encoding="utf-8") as f:
            json.dump({"copy": copy, "name": name}, f, indent=1)
            f.write("\n")
    with open(os.path.join(MOD, "mod.json"), "w", encoding="utf-8") as f:
        json.dump(mod, f, indent=2, ensure_ascii=False)
        f.write("\n")
    for w in sorted(set(warnings)): print("warning:", w)
    print("journey.json: %d flags, %d npcs, %d objectives; scripts en %d pt %d" % (len(flags), len(npcs), len(objectives), len(en["scripts"]) + 1, len(pt["scripts"]) + 1))


build()
