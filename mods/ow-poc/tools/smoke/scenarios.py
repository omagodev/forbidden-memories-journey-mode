"""Named smoke scenarios.  Each: desc, preset (journey.json "debug" name or number), debug (extra debug.json keys: flags, teleport, time,
skip_dialogue, win_duels), lang (0 en, 1 pt), steps (see jm_smoke.py), expect (log lines that must appear; (line, n) for n times)."""
MUSIC_DAY = "journey: music 10 (day)"
MUSIC_NIGHT = "journey: music 25 (night)"

SCENARIOS = {
    "hero_walk_with_inseto": dict(
        clean_hud=True,
        desc="the creator hero walking in all four directions next to InsetoKaiba in the village (v0.6.22 drew InsetoKaiba's sheet as the hero's walk frames): every page owned once",
        preset="2 rumors heard (Simon next)", debug={"teleport": [640, 380]},
        steps=[("wait", 60), ("snap", "idle")] + [st for d in ("up", "left", "down", "right") for st in (("walk", d, 3, 7, "hero"), ("wait", 20), ("snap", "idle_" + d))],
        expect=["sprite pages: sprite 0 bank 13 pages 0..1", "sprite pages: sprite 21 bank 13 pages 2..2"], forbid=["sprite page collision"]),
    "duel_loss_return": dict(
        clean_hud=True,
        desc="a lost duel returns to the opponent's lose scene with her own 168px face (Teana)",
        preset="13 two stamps (Teana last)", debug={"teleport": "teana_stall", "lose_duels": True},
        steps=[("wait", 200), ("press", "up", 3), ("wait", 10), ("press", "cross"), ("wait", 120), ("snap", "pre"), ("mash", "duel against", 3000),
               ("until", "_lose", 1500), ("wait", 150), ("snap", "lose_talk")],
        expect=["talk face: assets/faces/teana.hface", "_lose"]),
    "duel_two_opponents": dict(
        clean_hud=True,
        desc="two real duels in one session with every page shown: the Inspector, then Shadi; each pre/field/result shows its own 168px face, never the last opponent's",
        preset="14 harbor gate (Inspector)", debug={"teleport": [420, 356]},
        steps=[("wait", 200), ("press", "up", 3), ("wait", 10), ("press", "cross"), ("wait", 120), ("snap", "a_pre"), ("mash", "duel against", 3000),
               ("duel_kill",), ("until", "scene dk1_inspector_win", 1500), ("wait", 150), ("snap", "a_win"), ("mash", "saved", 2500), ("wait", 120),
               ("hold", "right", 200), ("wait", 20), ("snap", "walked"), ("press", "cross"), ("wait", 120), ("snap", "b_pre"), ("mash", "duel against Shadi", 3000),
               ("duel_kill",), ("until", "scene dk1_shadi_win", 1500), ("wait", 150), ("snap", "b_win")],
        expect=["duel faces: soldier map sheet 168x168", "scene dk1_inspector_win", "duel faces: shadi map sheet 168x168", "scene dk1_shadi_win"]),
    "duel_return_faces": dict(
        clean_hud=True,
        desc="a real duel with every page shown: Simon's 168px face before, on the field and in his win scene; then a different person (InsetoKaiba) talks with his own face, never Simon's stale one",
        preset="2 rumors heard (Simon next)", debug={"teleport": "house_ne_door"},
        steps=[("wait", 200), ("press", "up", 3), ("wait", 10), ("press", "cross"), ("wait", 120), ("snap", "pre_talk"), ("mash", "duel against", 3000),
               ("duel_kill",), ("until", "scene dk1_simon_win", 1500), ("wait", 150), ("snap", "win_talk"), ("mash", "saved", 2500), ("wait", 120),
               ("hold", "down", 12), ("hold", "left", 150), ("hold", "up", 6), ("wait", 30), ("snap", "walked")] + [("press", "cross", 5, 60)] + [("wait", 120), ("snap", "next_talk")],
        expect=["duel faces: simon map sheet 168x168", "scene dk1_simon_win"]),
    "duel_flow_screens": dict(
        clean_hud=True,
        desc="every screen between the talk and the field and from the last hit back to the map (pre/post-duel portraits)",
        preset="2 rumors heard (Simon next)", debug={"skip_dialogue": True, "teleport": "house_ne_door"},
        steps=[("wait", 300), ("press", "up", 3), ("wait", 10), ("press", "cross"), ("mash", "duel against", 3000)] + [st for i in range(6) for st in (("wait", 70), ("snap", "pre%d" % i))]
              + [("duel_kill",)] + [st for i in range(8) for st in (("wait", 90), ("snap", "post%d" % i))],
        expect=["duel over, won"]),
    "npc_walk_cycle": dict(
        clean_hud=True,
        desc="villagers walking (Jono, Kemet the farmer, Nabil): eight snaps 5 VBlanks apart must show the stride cycle",
        preset="6 Hakim's hint (Kemet next)", debug={"teleport": [700, 530]},
        steps=[("wait", 120)] + [st for i in range(8) for st in (("snap", "walk%d" % i), ("wait", 5))],
        expect=["npc anim: 3 frame 1", "npc anim: 3 frame 3", "npc anim: 6 frame 2", "npc anim: 9 frame 4"]),
    "rival_beach": dict(
        clean_hud=True, lang=0,
        desc="InsetoKaiba the recurring rival in the beach act: on the map, and his taunt",
        preset="18 beach landing (chapter 2)", debug={"teleport": [640, 496]},
        steps=[("wait", 90)] + [("press", "cross", 3, 45)] * 12 + [("wait", 60), ("snap", "map"), ("press", "up", 3), ("wait", 10), ("press", "cross"), ("wait", 90), ("snap", "talk1")],
        expect=["talk face"]),
    "rival_forest": dict(
        clean_hud=True, lang=0,
        desc="InsetoKaiba the recurring rival in the forest act: on the map, and his taunt",
        preset="22 forest arrival (chapter 3)", debug={"teleport": [800, 526]},
        steps=[("wait", 90)] + [("press", "cross", 3, 45)] * 12 + [("wait", 60), ("snap", "map"), ("press", "up", 3), ("wait", 10), ("press", "cross"), ("wait", 90), ("snap", "talk1")],
        expect=["talk face"]),
    "rival_mountain": dict(
        clean_hud=True, lang=0,
        desc="InsetoKaiba the recurring rival in the mountain act: on the map, and his taunt",
        preset="28 mountain arrival (chapter 4)", debug={"teleport": [420, 586]},
        steps=[("wait", 90)] + [("press", "cross", 3, 45)] * 12 + [("wait", 60), ("snap", "map"), ("press", "up", 3), ("wait", 10), ("press", "cross"), ("wait", 90), ("snap", "talk1")],
        expect=["talk face"]),
    "rival_meadow": dict(
        clean_hud=True, lang=0,
        desc="InsetoKaiba the recurring rival in the meadow act: on the map, and his taunt",
        preset="34 meadow arrival (chapter 5)", debug={"teleport": [960, 506]},
        steps=[("wait", 90)] + [("press", "cross", 3, 45)] * 12 + [("wait", 60), ("snap", "map"), ("press", "up", 3), ("wait", 10), ("press", "cross"), ("wait", 90), ("snap", "talk1")],
        expect=["talk face"]),
    "rival_desert": dict(
        clean_hud=True, lang=0,
        desc="InsetoKaiba the recurring rival in the desert act: on the map, and his taunt",
        preset="38 desert arrival (chapter 6)", debug={"teleport": [700, 586]},
        steps=[("wait", 90)] + [("press", "cross", 3, 45)] * 12 + [("wait", 60), ("snap", "map"), ("press", "up", 3), ("wait", 10), ("press", "cross"), ("wait", 90), ("snap", "talk1")],
        expect=["talk face"]),
    "rival_hall": dict(
        clean_hud=True, lang=0,
        desc="InsetoKaiba the recurring rival in the hall act: on the map, and his taunt",
        preset="49 hall arrival (chapter 9)", debug={"teleport": [780, 476]},
        steps=[("wait", 90)] + [("press", "cross", 3, 45)] * 12 + [("wait", 60), ("snap", "map"), ("press", "up", 3), ("wait", 10), ("press", "cross"), ("wait", 90), ("snap", "talk1")],
        expect=["talk face"]),
    "harbor_palm": dict(
        clean_hud=True,
        desc="the harbor's west palm over the boardwalk: behind it only the leaves and the trunk cover the hero, never the planks",
        preset="15 Courier at the pier end", debug={"teleport": [150, 372]},
        steps=[("wait", 90), ("snap", "east_of_palm"), ("hold", "left", 18), ("wait", 20), ("snap", "behind_crown"), ("hold", "left", 14), ("wait", 20),
               ("snap", "behind_crown_west"), ("hold", "up", 16), ("wait", 20), ("snap", "north"), ("hold", "down", 40), ("wait", 20), ("snap", "south")],
        expect=["dev mode 0"]),
    "talk_face_baker": dict(
        clean_hud=True,
        desc="the dialogue portrait of baker (source-sheet 168px face)",
        preset="5 Stamp Card (Hakim next)", debug={},
        steps=[("wait", 60), ("press", "up", 3), ("wait", 10), ("press", "cross"), ("wait", 60), ("mash", "baker.hface", 900), ("wait", 40), ("snap", "talk")],
        expect=["baker.hface"]),
    "talk_face_soldier": dict(
        clean_hud=True,
        desc="the dialogue portrait of soldier (source-sheet 168px face)",
        preset="14 harbor gate (Inspector)", debug={"teleport": "inspector_spot"},
        steps=[("wait", 60), ("press", "up", 3), ("wait", 10), ("press", "cross"), ("wait", 60), ("mash", "soldier.hface", 900), ("wait", 40), ("snap", "talk")],
        expect=["soldier.hface"]),
    "talk_face_dock_dan": dict(
        clean_hud=True,
        desc="the dialogue portrait of dock_dan (source-sheet 168px face)",
        preset="15 Courier at the pier end", debug={"teleport": "harbor.shop_stall"},
        steps=[("wait", 60), ("press", "up", 3), ("wait", 10), ("press", "cross"), ("wait", 60), ("mash", "trader.hface", 900), ("wait", 40), ("snap", "talk")],
        expect=["trader.hface"]),
    "readme_map_hero": dict(
        clean_hud=True,
        desc="a clean village shot with the 64px hero (README picture)",
        preset="2 rumors heard (Simon next)", debug={"teleport": "plaza_center"},
        steps=[("wait", 120), ("hold", "down", 20), ("wait", 60), ("snap", "map")],
        expect=["dev mode 0"]),
    "duel_face_simon": dict(
        clean_hud=True,
        desc="the duel's life-point faces: simon's own map face, the created hero's face (not the disc portraits)",
        preset="2 rumors heard (Simon next)", debug={"skip_dialogue": True, "teleport": "house_ne_door"},
        steps=[("wait", 300), ("press", "up", 3), ("wait", 10), ("press", "cross"), ("mash", "duel against", 3000), ("wait", 300)] + [("press", "circle", 5, 60)] * 3 + [("until", "duel faces", 3000), ("wait", 400), ("snap", "duel")],
        expect=["journey: duel faces: simon map sheet 168x168", "hero creator face"]),
    "duel_face_teana": dict(
        clean_hud=True,
        desc="the duel's life-point faces: teana's own map face, the created hero's face (not the disc portraits)",
        preset="13 two stamps (Teana last)", debug={"skip_dialogue": True, "teleport": "teana_stall"},
        steps=[("wait", 300), ("press", "up", 3), ("wait", 10), ("press", "cross"), ("mash", "duel against", 3000), ("wait", 300)] + [("press", "circle", 5, 60)] * 3 + [("until", "duel faces", 3000), ("wait", 400), ("snap", "duel")],
        expect=["journey: duel faces: teana map sheet 168x168", "hero creator face"]),
    "duel_face_hakim": dict(
        desc="the duel's life-point faces: hakim's own map face, the created hero's face (not the disc portraits)",
        preset="5 Stamp Card (Hakim next)", debug={"skip_dialogue": True},
        steps=[("wait", 300), ("press", "up", 3), ("wait", 10), ("press", "cross"), ("mash", "duel against", 3000), ("wait", 300)] + [("press", "circle", 5, 60)] * 3 + [("until", "duel faces", 3000), ("wait", 400), ("snap", "duel")],
        expect=["journey: duel faces: baker map sheet 48x48", "hero creator face"]),
    "duel_face_kemet": dict(
        desc="the duel's life-point faces: kemet's own map face, the created hero's face (not the disc portraits)",
        preset="6 Hakim's hint (Kemet next)", debug={"skip_dialogue": True},
        steps=[("wait", 300), ("press", "up", 3), ("wait", 10), ("press", "cross"), ("mash", "duel against", 3000), ("wait", 300)] + [("press", "circle", 5, 60)] * 3 + [("until", "duel faces", 3000), ("wait", 400), ("snap", "duel")],
        expect=["journey: duel faces: farmer map sheet 48x48", "hero creator face"]),
    "talk_face_simon": dict(
        clean_hud=True,
        desc="the dialogue portrait of simon (source-sheet 168px face where the sheet has one)",
        preset="6 Hakim's hint (Kemet next)", debug={"teleport": "house_ne_door"},
        steps=[("wait", 30), ("press", "up", 3), ("wait", 10), ("press", "cross"), ("wait", 90), ("snap", "talk")],
        expect=["talk face"]),
    "talk_face_guard": dict(
        desc="the dialogue portrait of guard (source-sheet 168px face where the sheet has one)",
        preset="6 Hakim's hint (Kemet next)", debug={"teleport": [652, 190]},
        steps=[("wait", 30), ("press", "up", 3), ("wait", 10), ("press", "cross"), ("wait", 90), ("snap", "talk")],
        expect=["talk face"]),
    "talk_face_jono": dict(
        desc="the dialogue portrait of jono (source-sheet 168px face where the sheet has one)",
        preset="6 Hakim's hint (Kemet next)", debug={"teleport": "plaza_center"},
        steps=[("wait", 30), ("press", "up", 3), ("wait", 10), ("press", "cross"), ("wait", 90), ("snap", "talk")],
        expect=["talk face"]),
    "talk_face_teana": dict(
        desc="the dialogue portrait of teana (source-sheet 168px face where the sheet has one)",
        preset="6 Hakim's hint (Kemet next)", debug={"teleport": "teana_stall"},
        steps=[("wait", 30), ("press", "up", 3), ("wait", 10), ("press", "cross"), ("wait", 90), ("snap", "talk")],
        expect=["talk face"]),
    "talk_face_farmer": dict(
        desc="the dialogue portrait of farmer (source-sheet 168px face where the sheet has one)",
        preset="6 Hakim's hint (Kemet next)", debug={"teleport": [700, 492]},
        steps=[("wait", 30), ("press", "up", 3), ("wait", 10), ("press", "cross"), ("wait", 90), ("snap", "talk")],
        expect=["talk face"]),
    "walk_sprites": dict(
        desc="the hero walking in all four directions (snaps mid-stride) and the villagers walking: UP must not tear, NPCs must step",
        preset="6 Hakim's hint (Kemet next)",
        steps=[("wait", 30), ("hold", "left", 50), ("hold", "down", 30), ("wait", 20), ("snap", "idle")] + [st for d in ("up", "left", "down", "right") for st in (("walk", d, 3, 7, "hero"), ("wait", 20), ("snap", "idle_" + d))]
              + [st for i in range(4) for st in (("wait", 9), ("snap", "npcs%d" % i))],
        expect=["debug: preset 5", "npc anim: 3 frame 1 dir 1 moving 1", "npc anim: 3 frame 3 dir 2 moving 1", "npc anim: 6 frame 3 dir 1 moving 1"]),
    "village_roads": dict(
        desc="the village with the new roads: plaza, west road, bakery, bridge (chord R1+L1+Right cycles the anchors)",
        preset="6 Hakim's hint (Kemet next)",
        steps=[("snap", "farmer_field")] + [s for i in range(5) for s in (("press", ["r1", "l1", "right"], 4, 40), ("wait", 40), ("snap", "anchor%d" % i))],
        expect=["debug: preset 5", "debug: teleport"]),
    "dk_part2_bench": dict(
        desc="quest 3: sit on the bench, night falls, the Mago.dev observer shows and glitches away",
        preset="3 Simon won (bench next)", debug={"skip_dialogue": True},
        steps=[("snap", "bench_day"), ("press", "cross"), ("until", "scene dk1_bench", 300), ("wait", 60), ("snap", "sit"),
               ("until", "observer", 900), ("wait", 40), ("snap", "observer"), ("until", "observer vanishes", 900), ("wait", 8), ("snap", "glitch"),
               ("until", "saved (stage 2", 900), ("wait", 400), ("snap", "after_bench_night")],
        expect=["scene dk1_bench", "painted: observer mago", "observer vanishes", MUSIC_DAY, MUSIC_NIGHT]),
    "dk_part2_hooded_man": dict(
        desc="quest 3: the hooded man gives the Stamp Card and the riddle; day returns; the Stamp Card is saved",
        preset="4 night, hooded man waits", debug={"skip_dialogue": True},
        steps=[("snap", "night_hooded_man"), ("press", "cross"), ("until", "scene dk1_hooded_riddle", 300), ("wait", 30), ("snap", "riddle_p0"),
               ("until", "saved (stage 3", 2500), ("wait", 250), ("snap", "day_again"),
               ("press", "triangle"), ("wait", 30), ("snap", "journal")],
        expect=["scene dk1_hooded_riddle", "saved (stage 3", MUSIC_NIGHT, MUSIC_DAY]),
    "dk_part2_baker": dict(
        desc="quest 4: Hakim's hint (needs the Stamp Card)",
        preset="5 Stamp Card (Hakim next)", debug={"skip_dialogue": True},
        steps=[("snap", "bakery"), ("press", "cross"), ("until", "scene dk1_baker", 300), ("wait", 40), ("snap", "baker_talk"),
               ("until", "saved (stage 3", 1500), ("wait", 60), ("snap", "after_baker")],
        expect=["scene dk1_baker", "saved (stage 3"]),
    "dk_part2_kemet_duel": dict(
        desc="quest 4: Kemet's duel is skipped as won (debug), the Lantern and the objective to open the hatch",
        preset="6 Hakim's hint (Kemet next)", debug={"skip_dialogue": True, "win_duels": True},
        steps=[("press", "cross"), ("until", "debug: duel against Kemet", 1500), ("wait", 20), ("snap", "after_win"),
               ("until", "saved (stage 3", 2500), ("wait", 60), ("snap", "end"),
               ("press", "triangle"), ("wait", 30), ("snap", "journal")],
        expect=["debug: duel against Kemet", "duel over, won", "scene dk1_farmer_win", ("journey: music 10 (day)", 2)]),
    "dk_part2_kemet_real_duel": dict(
        slow=True,   # not in "all": the LP poke (duel_win) does not end the duel under this harness yet; the debug win_duels covers the flow
        desc="quest 4 with the real duel: the game's duel screens, then back in the village (experimental)",
        preset="6 Hakim's hint (Kemet next)", debug={"skip_dialogue": True},
        steps=[("press", "cross"), ("until", "duel against Kemet", 1500), ("wait", 300), ("duel_win",), ("wait", 250), ("snap", "back"),
               ("until", "saved (stage 3", 2500), ("wait", 60), ("snap", "end")],
        expect=["duel against Kemet", "duel over, won", "scene dk1_farmer_win", ("journey: music 10 (day)", 2)]),
    "ui_dialog_en": dict(
        desc="dialogue UI (EN): speaker name in yellow at the start of the box text, banners for item / objective / complete",
        preset="6 Hakim's hint (Kemet next)", debug={"win_duels": True}, lang=0,
        steps=[("press", "cross"), ("until", "scene dk1_farmer_pre", 300), ("wait", 100), ("snap", "speech_nameplate"), ("mash", "debug: duel against Kemet", 1200),
               ("until", "scene dk1_farmer_win", 600), ("wait", 120), ("snap", "win_speech"), ("press", "cross", 5, 40), ("wait", 100), ("snap", "win_speech2"),
               ("press", "cross", 5, 6), ("wait", 6), ("snap", "banner_item_anim"), ("wait", 60), ("snap", "banner_item"),
               ("press", "cross", 5, 6), ("wait", 8), ("snap", "banner_objective_anim"), ("wait", 60), ("snap", "banner_objective"),
               ("press", "cross", 5, 6), ("wait", 60), ("snap", "after_scene")],
        expect=["scene dk1_farmer_win", "audio: sfx 0x2F plays"]),
    "ui_dialog_pt": dict(
        desc="dialogue UI (PT): speaker name in yellow at the start of the box text, banners for item / objective / complete",
        preset="6 Hakim's hint (Kemet next)", debug={"win_duels": True}, lang=1,
        steps=[("press", "cross"), ("until", "scene dk1_farmer_pre", 300), ("wait", 100), ("snap", "speech_nameplate"), ("mash", "debug: duel against Kemet", 1200),
               ("until", "scene dk1_farmer_win", 600), ("wait", 120), ("snap", "win_speech"), ("press", "cross", 5, 40), ("wait", 100), ("snap", "win_speech2"),
               ("press", "cross", 5, 6), ("wait", 6), ("snap", "banner_item_anim"), ("wait", 60), ("snap", "banner_item"),
               ("press", "cross", 5, 6), ("wait", 8), ("snap", "banner_objective_anim"), ("wait", 60), ("snap", "banner_objective"),
               ("press", "cross", 5, 6), ("wait", 60), ("snap", "after_scene")],
        expect=["scene dk1_farmer_win", "audio: sfx 0x2F plays"]),
    "ui_ask_en": dict(
        desc="Yes/No choice page with the coloured speaker name: the ask page shows the choices, Cross accepts and the duel intro starts",
        preset="6 Hakim's hint (Kemet next)", debug={"win_duels": True}, lang=0,
        steps=[("press", "cross"), ("until", "scene dk1_farmer_pre", 300), ("wait", 200), ("press", "cross", 5, 200), ("press", "cross", 5, 300), ("snap", "ask_page"), ("press", "down", 5, 30), ("snap", "ask_no"), ("press", "up", 5, 30),
               ("press", "cross", 5, 250), ("snap", "after_yes")],
        expect=["scene dk1_farmer_pre"]),
    "ui_ask_pt": dict(
        desc="Yes/No choice page (PT) with the coloured speaker name: the ask page shows the choices, Cross accepts and the duel intro starts",
        preset="6 Hakim's hint (Kemet next)", debug={"win_duels": True}, lang=1,
        steps=[("press", "cross"), ("until", "scene dk1_farmer_pre", 300), ("wait", 200), ("press", "cross", 5, 200), ("press", "cross", 5, 300), ("snap", "ask_page"), ("press", "down", 5, 30), ("snap", "ask_no"), ("press", "up", 5, 30),
               ("press", "cross", 5, 250), ("snap", "after_yes")],
        expect=["scene dk1_farmer_pre"]),
    "objective_chip_hud": dict(
        quick=True,
        desc="painted HUD shows the current objective chip; Triangle opens the journal",
        preset="3 Simon won (bench next)", lang=1,
        steps=[("wait", 40), ("snap", "chip"), ("press", "triangle", 5, 30), ("until", "journey: journal open", 600),
               ("snap", "journal"), ("press", "triangle", 5, 30), ("wait", 30), ("snap", "back")],
        expect=["journey: journal open"]),
    "menu_controls_row": dict(
        quick=True,
        desc="START menu has Controls; confirm opens the PC remapper (or shows the in-menu hint)",
        preset="6 Hakim's hint (Kemet next)", lang=0,
        steps=[("press", "start", 5, 30), ("wait", 20),
               ("press", "down", 5, 14), ("press", "down", 5, 14), ("press", "down", 5, 14), ("press", "down", 5, 14),
               ("snap", "controls_row"), ("press", "cross", 5, 40), ("wait", 40), ("snap", "controls_open")],
        expect=["journey: 267 scenes"]),
    "painted_menu": dict(
        desc="START opens the main menu over the painted village (items, status, save), Triangle closes it, the village is back and walkable",
        preset="6 Hakim's hint (Kemet next)",
        steps=[("snap", "village"), ("press", "start", 5, 30), ("wait", 20), ("snap", "menu"),
               ("press", "down", 5, 20), ("press", "cross", 5, 30), ("snap", "items"), ("press", "triangle", 5, 20),
               ("press", "down", 5, 20), ("press", "down", 5, 20), ("press", "cross", 5, 40), ("snap", "saved"),
               ("press", "triangle", 5, 20), ("press", "triangle", 5, 30), ("wait", 30), ("snap", "back_in_village"),
               ("press", ["r1", "l1", "right"], 4, 40), ("wait", 20), ("snap", "teleport_after_menu")],
        expect=["saved (stage 3", "debug: teleport"]),
    "painted_menu_deck": dict(
        desc="START > Deck editor from the painted village and back: the village is loaded again (banks, sprites)",
        preset="6 Hakim's hint (Kemet next)", settings={"deck_slots": 0},   # the engine's deck-slot list takes the pad away from the harness
        steps=[("press", "start", 5, 30), ("press", "cross", 5, 30), ("wait", 400), ("snap", "deck_editor"),
               ("press", "circle", 5, 60), ("wait", 400), ("snap", "back_from_deck_editor"),
               ("press", ["r1", "l1", "right"], 4, 40), ("wait", 20), ("snap", "walkable_after_deck")],
        expect=[("journey: mode on", 2), "debug: teleport"]),
    "music_day_night": dict(
        desc="the village song (10) by day, the night song (25) at night (R1+L1+Left), day again",
        preset="3 Simon won (bench next)",
        steps=[("until", MUSIC_DAY, 600), ("press", ["r1", "l1", "left"], 4, 30), ("until", MUSIC_NIGHT, 900), ("snap", "night"),
               ("press", ["r1", "l1", "left"], 4, 30), ("press", ["r1", "l1", "left"], 4, 30), ("until", "music 10 (day)", 900), ("snap", "day")],
        expect=[MUSIC_DAY, MUSIC_NIGHT, ("journey: music", 3)]),
    "dk_part2_pt": dict(
        desc="Portuguese text of the bench quest's first page",
        preset="3 Simon won (bench next)", lang=1,
        steps=[("press", "cross"), ("until", "scene dk1_bench", 300), ("wait", 120), ("snap", "pt_page0"), ("mash", "observer", 1500), ("wait", 20), ("snap", "pt_observer")],
        expect=["scene dk1_bench"]),
}

# ---------------------------------------------------------------- part 3: the cistern, Rex, Teana
H = "7 Lantern won (hatch next)"
SCENARIOS.update({
    "dk_part3_hatch_locked": dict(
        desc="part 3: the hatch of the little pyramid is shut without the lantern",
        preset="6 Hakim's hint (Kemet next)", debug={"skip_dialogue": True, "teleport": "mini_pyramid_hatch"},
        steps=[("wait", 30), ("snap", "hatch_closed"), ("press", "cross"), ("until", "scene dk1_hatch_locked", 300), ("wait", 60), ("snap", "locked_text"), ("wait", 200)],
        expect=["scene dk1_hatch_locked"], forbid=["now in the cistern"]),
    "dk_part3_cistern": dict(
        desc="part 3, the Lost: the open hatch, down into the cistern (fade, music), Bakura's duel (won by debug), the Founder's Scarab, journal",
        preset=H, debug={"skip_dialogue": True, "win_duels": True},
        steps=[("wait", 30), ("snap", "hatch_open"), ("press", "cross"), ("until", "scene dk1_cistern_enter", 300), ("until", "now in the cistern", 900), ("wait", 12), ("snap", "fade_in"),
               ("wait", 120), ("snap", "cistern_arrival"), ("hold", "down", 24), ("wait", 20), ("snap", "ghost_near"),
               ("hold", "down", 20), ("press", "cross"), ("until", "scene dk1_bakura_pre", 300), ("until", "debug: duel against Bakura", 1500), ("wait", 20),
               ("until", "scene dk1_bakura_win", 600), ("until", "saved (stage 3", 2500), ("wait", 60), ("snap", "after_win"),
               ("press", "triangle"), ("wait", 30), ("snap", "journal")],
        expect=["scene dk1_cistern_enter", "painted: now in the cistern", "scene dk1_bakura_pre", "debug: duel against Bakura", "duel over, won", "scene dk1_bakura_win",
                "journey: music 26 (cistern)", "painted: cistern, 1280x720 picture"]),
    "dk_part3_glyph": dict(
        desc="part 3: the glyphs on the cistern wall (observer without a figure), they glitch away, Bakura mentions them afterwards",
        preset="9 Lost stamp (glyph, stairs)", lang=0,
        steps=[("wait", 30), ("snap", "wall_before"), ("press", "cross"), ("until", "scene dk1_mago_glyph", 300), ("wait", 260), ("snap", "glyph_p0"), ("press", "cross", 5, 200), ("snap", "glyph_p1"),
               ("press", "cross", 5, 200), ("snap", "glyph_p2"), ("until", "observer vanishes", 600), ("wait", 8), ("snap", "glyph_glitch"), ("wait", 120), ("snap", "wall_after")],
        expect=["scene dk1_mago_glyph", "painted: observer mago_dev appears", "observer vanishes"]),
    "dk_part3_exit": dict(
        desc="part 3: the stairs up take the player back to the hatch in the village",
        preset="9 Lost stamp (glyph, stairs)", debug={"skip_dialogue": True, "teleport": "exit_stairs"},
        steps=[("wait", 30), ("snap", "stairs"), ("press", "cross"), ("until", "scene dk1_cistern_exit", 300), ("until", "now in the village", 900), ("wait", 120), ("snap", "village_hatch")],
        expect=["scene dk1_cistern_exit", "painted: now in the village", "journey: music 26 (cistern)", "journey: music 10 (day)"]),
    "dk_part3_rex": dict(
        desc="part 3, the Won: Rex Raptor on the east road, the duel (won by debug), Jono's Bandana",
        preset="10 Jono asked (Rex next)", debug={"skip_dialogue": True, "win_duels": True, "teleport": "rex_approach"},
        steps=[("wait", 40), ("snap", "near_rex"), ("hold", "right", 12), ("wait", 10), ("snap", "rex_close"), ("press", "cross"),
               ("until", "scene dk1_rex_pre", 300), ("until", "debug: duel against Rex", 1500), ("until", "scene dk1_rex_win", 600), ("until", "saved (stage 3", 2500), ("wait", 60), ("snap", "after_win")],
        expect=["scene dk1_rex_pre", "debug: duel against Rex", "duel over, won", "scene dk1_rex_win"]),
    "dk_part3_honey": dict(
        desc="part 3, the Given: honey from Hakim for Teana's cakes",
        preset="11 Teana's errands", debug={"skip_dialogue": True, "teleport": "bakery_door"},
        steps=[("press", "cross"), ("until", "scene dk1_baker_honey", 300), ("until", "saved (stage 3", 1500), ("wait", 60), ("snap", "honey")],
        expect=["scene dk1_baker_honey"]),
    "dk_part3_water": dict(
        desc="part 3, the Given: fill the jug at the river",
        preset="11 Teana's errands", debug={"skip_dialogue": True, "teleport": "river_bank"},
        steps=[("wait", 30), ("snap", "river"), ("press", "cross"), ("until", "scene dk1_river_fill", 300), ("until", "saved (stage 3", 1500), ("wait", 60), ("snap", "water")],
        expect=["scene dk1_river_fill"]),
    "dk_part3_dates": dict(
        desc="part 3, the Given: shake the date palm",
        preset="11 Teana's errands", debug={"skip_dialogue": True, "teleport": "date_palm"},
        steps=[("wait", 30), ("snap", "palm"), ("press", "cross"), ("until", "scene dk1_date_palm", 300), ("until", "saved (stage 3", 1500), ("wait", 60), ("snap", "dates")],
        expect=["scene dk1_date_palm"]),
    "dk_part3_teana_end": dict(
        desc="part 3, the Given: Teana's duel (won by debug), the Lucky Charm, the third stamp, stage 4 and 'Part 3 complete'",
        preset="13 two stamps (Teana last)", debug={"skip_dialogue": True, "win_duels": True},
        steps=[("wait", 30), ("press", "cross"), ("until", "scene dk1_teana_pre", 300), ("until", "debug: duel against Teana", 1500), ("until", "scene dk1_teana_win", 600),
               ("until", "scene dk1_treasures_done", 2500), ("until", "saved (stage 4", 2500), ("wait", 120), ("snap", "part_end"), ("until", "saved (stage 4", 2500), ("wait", 120), ("snap", "village_end"),
               ("press", "triangle"), ("wait", 30), ("snap", "journal")],
        expect=["scene dk1_teana_pre", "debug: duel against Teana", "scene dk1_teana_win", "scene dk1_treasures_done", "saved (stage 4", "saved (stage 4"]),
    "dk_part3_journal_en": dict(
        desc="the journal with the three treasure quests open (EN), then with the errands done and at the end of part 3",
        preset="10 Jono asked (Rex next)", lang=0,
        steps=[("wait", 30), ("press", "triangle"), ("wait", 20), ("snap", "j10"), ("press", "triangle"), ("wait", 20),
               ("press", ["r1", "l1", "up"], 4, 40), ("press", ["r1", "l1", "up"], 4, 40), ("press", ["r1", "l1", "up"], 4, 40), ("wait", 30), ("press", "triangle"), ("wait", 20), ("snap", "j13"),
               ("press", "triangle"), ("wait", 20), ("press", ["r1", "l1", "down"], 4, 40), ("press", ["r1", "l1", "down"], 4, 40), ("press", ["r1", "l1", "down"], 4, 40), ("press", ["r1", "l1", "down"], 4, 40),
               ("press", ["r1", "l1", "down"], 4, 40), ("wait", 30), ("press", "triangle"), ("wait", 20), ("snap", "j8")],
        expect=[]),
    "dk_part3_journal_pt": dict(
        desc="the journal (PT) with the three treasure quests open and with the errands (preset 12)",
        preset="12 errands done (Teana next)", lang=1,
        steps=[("wait", 30), ("press", "triangle"), ("wait", 20), ("snap", "j12"), ("press", "triangle"), ("wait", 20), ("press", ["r1", "l1", "down"], 4, 40), ("wait", 30),
               ("press", "triangle"), ("wait", 20), ("snap", "j11")],
        expect=[]),
    "ui_banners_p3_en": dict(
        desc="banners of part 3 (EN): Teana's win scene - item banner with the Lucky Charm icon, stamp banner, the three stamps, complete",
        preset="13 two stamps (Teana last)", debug={"win_duels": True}, lang=0,
        steps=[("press", "cross"), ("until", "scene dk1_teana_pre", 300), ("mash", "debug: duel against Teana", 1500), ("until", "page dk1_teana_win 0", 600), ("wait", 150), ("snap", "win_speech"),
               ("mash", "page dk1_teana_win 3 kind 2", 2500), ("wait", 6), ("snap", "banner_item_anim"), ("wait", 60), ("snap", "banner_item"),
               ("mash", "page dk1_teana_win 4 kind 2", 600), ("wait", 60), ("snap", "banner_stamp"),
               ("mash", "page dk1_treasures_done 0", 600), ("wait", 150), ("snap", "all_stamps"),
               ("mash", "page dk1_treasures_done 2 kind 1", 2500), ("wait", 60), ("snap", "banner_objective"),
               ("mash", "page dk_part3_end 0 kind 3", 1500), ("wait", 70), ("snap", "banner_complete")],
        expect=["scene dk1_teana_win", "saved (stage 4"]),
    "ui_banners_p3_pt": dict(
        desc="banners of part 3 (PT): Teana's win scene - item banner with the Lucky Charm icon, stamp banner, the three stamps, complete",
        preset="13 two stamps (Teana last)", debug={"win_duels": True}, lang=1,
        steps=[("press", "cross"), ("until", "scene dk1_teana_pre", 300), ("mash", "debug: duel against Teana", 1500), ("until", "page dk1_teana_win 0", 600), ("wait", 150), ("snap", "win_speech"),
               ("mash", "page dk1_teana_win 3 kind 2", 2500), ("wait", 6), ("snap", "banner_item_anim"), ("wait", 60), ("snap", "banner_item"),
               ("mash", "page dk1_teana_win 4 kind 2", 600), ("wait", 60), ("snap", "banner_stamp"),
               ("mash", "page dk1_treasures_done 0", 600), ("wait", 150), ("snap", "all_stamps"),
               ("mash", "page dk1_treasures_done 2 kind 1", 2500), ("wait", 60), ("snap", "banner_objective"),
               ("mash", "page dk_part3_end 0 kind 3", 1500), ("wait", 70), ("snap", "banner_complete")],
        expect=["scene dk1_teana_win", "saved (stage 4"]),
    "ui_hint_talk_en": dict(
        desc="the small action hint (round X button + 'Talk') next to Hakim, no big bottom bar; Dev mode off hides the top bar",
        preset="5 Stamp Card (Hakim next)", devcfg="0",
        steps=[("wait", 30), ("snap", "pill_talk")],
        expect=["journey: dev mode 0 (file)"]),
    "ui_hint_examine_pt": dict(
        desc="PT: the action hint 'Examinar' at the plaza bench",
        preset="3 Simon won (bench next)", devcfg="0", lang=1,
        steps=[("wait", 30), ("snap", "pill_examine_pt"), ("hold", "down", 140), ("wait", 20), ("snap", "no_hint_pt")],
        expect=["journey: dev mode 0 (file)"]),
    "ui_devmode_en": dict(
        desc="START menu has 'Dev mode: ON/OFF' (default ON with debug.json); toggling hides the top bar, the choice survives a restart",
        preset="3 Simon won (bench next)",
        steps=[("wait", 30), ("snap", "bar_visible"), ("press", "start", 5, 30), ("wait", 20),
               ("press", "down", 5, 14), ("press", "down", 5, 14), ("press", "down", 5, 14), ("press", "down", 5, 14), ("press", "down", 5, 14),
               ("snap", "menu_dev_on"), ("press", "cross", 5, 30), ("wait", 10), ("snap", "menu_dev_off"),
               ("press", "triangle", 5, 30), ("wait", 30), ("snap", "bar_hidden"),
               ("restart",), ("wait", 30), ("snap", "bar_hidden_after_restart")],
        expect=["journey: dev mode 1 (default, debug.json)", "journey: dev mode 0 (saved)", "journey: dev mode 0 (file)"]),
    "ui_devmode_pt": dict(
        desc="PT: 'Modo dev: LIGADO/DESLIGADO' in the START menu, on then off",
        preset="3 Simon won (bench next)", lang=1,
        steps=[("wait", 30), ("press", "start", 5, 30), ("wait", 20),
               ("press", "down", 5, 14), ("press", "down", 5, 14), ("press", "down", 5, 14), ("press", "down", 5, 14), ("press", "down", 5, 14),
               ("snap", "menu_dev_on_pt"), ("press", "cross", 5, 30), ("wait", 10), ("snap", "menu_dev_off_pt"),
               ("press", "right", 5, 30), ("wait", 10), ("snap", "menu_dev_on_again_pt")],
        expect=["journey: dev mode 0 (saved)", "journey: dev mode 1 (saved)"]),
    "mochila_simon_pt": dict(desc="Simon's win gives Magician of Faith: CARTA OBTIDA with its art, the chest lists it by name, the backpack's story cards tab and its details", preset="2 rumors heard", lang=1, settings={"deck_slots": 0},
        debug={"win_duels": True, "teleport": "house_ne_door", "flags": ["heard_teana", "heard_jono", "heard_guard"]},
        steps=[("wait", 30), ("press", "cross")] + [("press", "cross", 5, 30)] * 8 + [("until", "debug: duel", 1500), ("until", "scene dk1_simon_win", 1500)]
              + sum([[("press", "cross", 5, 30), ("snap", "w%02d" % i)] for i in range(24)], [])
              + [("press", "cross", 5, 30), ("wait", 90), ("snap", "after"), ("press", "start", 5, 30), ("press", "down", 5, 14), ("press", "cross", 5, 30), ("wait", 20), ("snap", "bag_items"),
                 ("press", "r1", 5, 30), ("wait", 60), ("snap", "bag_cards"), ("press", "cross", 5, 30), ("wait", 40), ("snap", "card_details"),
                 ("press", "circle", 5, 20), ("press", "circle", 5, 20), ("wait", 10), ("snap", "menu"), ("press", "up", 5, 14), ("press", "cross", 5, 30), ("wait", 200)]
              + [("press", "r1", 4, 8)] * 53 + [("press", "down", 4, 10)] * 3 + [("wait", 30), ("snap", "chest_428")]),
    "mochila_items_pt": dict(desc="the backpack (PT): seven items with their icons, the details of one, back to the grid", preset="3 Simon won (bench next)", lang=1,
        debug={"flags": ["courier_met", "farmer_won", "got_honey", "got_water", "got_dates", "treasure_lost", "treasure_won"]},
        steps=[("wait", 30), ("press", "start", 5, 30), ("press", "down", 5, 14), ("snap", "menu"), ("press", "cross", 5, 30), ("wait", 20), ("snap", "bag_items"),
               ("press", "right", 5, 14), ("press", "right", 5, 14), ("press", "down", 5, 14), ("wait", 10), ("snap", "bag_sel"), ("press", "cross", 5, 30), ("wait", 20), ("snap", "item_details"),
               ("press", "circle", 5, 20), ("press", "up", 5, 14), ("press", "left", 5, 14), ("press", "left", 5, 14), ("press", "cross", 5, 30), ("wait", 20), ("snap", "item_details2"),
               ("press", "triangle", 5, 20), ("press", "l1", 5, 20), ("wait", 20), ("snap", "bag_cards"), ("press", "circle", 5, 20), ("wait", 10), ("snap", "back_menu")]),
    "mochila_items_en": dict(desc="the backpack (EN): seven items with their icons, the details of one, back to the grid", preset="3 Simon won (bench next)", lang=0,
        debug={"flags": ["courier_met", "farmer_won", "got_honey", "got_water", "got_dates", "treasure_lost", "treasure_won"]},
        steps=[("wait", 30), ("press", "start", 5, 30), ("press", "down", 5, 14), ("snap", "menu"), ("press", "cross", 5, 30), ("wait", 20), ("snap", "bag_items"),
               ("press", "right", 5, 14), ("press", "right", 5, 14), ("press", "down", 5, 14), ("wait", 10), ("snap", "bag_sel"), ("press", "cross", 5, 30), ("wait", 20), ("snap", "item_details"),
               ("press", "circle", 5, 20), ("press", "up", 5, 14), ("press", "left", 5, 14), ("press", "left", 5, 14), ("press", "cross", 5, 30), ("wait", 20), ("snap", "item_details2"),
               ("press", "triangle", 5, 20), ("press", "l1", 5, 20), ("wait", 20), ("snap", "bag_cards"), ("press", "circle", 5, 20), ("wait", 10), ("snap", "back_menu")]),
    "shop_v2_pt": dict(desc="the card shop (PT): cards with quantity 3, packs, sell, the Monsters filter, Yes buys one Basic Insect", preset="13 two stamps (Teana last)", lang=1, debug={"skip_dialogue": True, "stage": 4, "coins": 1250, "flags": ["treasure_given", "treasure_lost", "treasure_won"]},
        steps=[("wait", 30), ("press", "cross"), ("wait", 400), ("snap", "shop"),
               ("press", "down", 5, 14), ("press", "right", 5, 14), ("press", "right", 5, 14), ("wait", 20), ("snap", "cards_sel"),
               ("press", "r1", 5, 20), ("wait", 20), ("snap", "packs"), ("press", "r1", 5, 20), ("wait", 20), ("snap", "sell"),
               ("press", "r1", 5, 20), ("press", "square", 5, 20), ("wait", 20), ("snap", "filter_monsters"), ("press", "cross", 5, 20), ("wait", 20), ("snap", "confirm"), ("press", "cross", 5, 20), ("wait", 30), ("snap", "bought")],
        expect=["journey: shop art teana", "journey: bought card"]),
    "shop_v2_en": dict(desc="the card shop (EN): cards with quantity 3, packs, sell, the Monsters filter, Yes buys one Basic Insect", preset="13 two stamps (Teana last)", lang=0, debug={"skip_dialogue": True, "stage": 4, "coins": 1250, "flags": ["treasure_given", "treasure_lost", "treasure_won"]},
        steps=[("wait", 30), ("press", "cross"), ("wait", 400), ("snap", "shop"),
               ("press", "down", 5, 14), ("press", "right", 5, 14), ("press", "right", 5, 14), ("wait", 20), ("snap", "cards_sel"),
               ("press", "r1", 5, 20), ("wait", 20), ("snap", "packs"), ("press", "r1", 5, 20), ("wait", 20), ("snap", "sell"),
               ("press", "r1", 5, 20), ("press", "square", 5, 20), ("wait", 20), ("snap", "filter_monsters"), ("press", "cross", 5, 20), ("wait", 20), ("snap", "confirm"), ("press", "cross", 5, 20), ("wait", 30), ("snap", "bought")],
        expect=["journey: shop art teana", "journey: bought card"]),
    "ui_devmode_release": dict(
        desc="release build (no debug.json): no top bar and no Dev mode row in the START menu; Down from Language goes straight to Back to title",
        no_debug_json=True,
        steps=[("wait", 60), ("snap", "release_default"), ("press", "start", 5, 30), ("wait", 20), ("snap", "menu_release"),
               ("press", "down", 5, 14), ("press", "down", 5, 14), ("press", "down", 5, 14), ("press", "down", 5, 14), ("press", "down", 5, 14),
               ("snap", "row_after_language"), ("press", "triangle", 5, 30), ("wait", 30), ("snap", "no_bar")],
        expect=["journey: dev mode 0 (default)"]),
    "ui_menu_rows_en": dict(
        desc="every START menu row fits inside the box (EN): Language and Dev mode selected, Back to title question open",
        preset="3 Simon won (bench next)", lang=0,
        steps=[("wait", 30), ("press", "start", 5, 30), ("wait", 20), ("snap", "menu_first"),
               ("press", "down", 5, 14), ("press", "down", 5, 14), ("press", "down", 5, 14), ("press", "down", 5, 14), ("snap", "row_language"),
               ("press", "down", 5, 14), ("snap", "row_dev"), ("press", "down", 5, 14), ("press", "cross", 5, 30), ("snap", "row_title_question"),
               ("press", "circle", 5, 20), ("press", "down", 5, 14), ("snap", "row_close")],
        expect=["journey: mode on"]),
    "ui_menu_rows_pt": dict(
        desc="every START menu row fits inside the box (PT): Language and Dev mode selected, Back to title question open",
        preset="3 Simon won (bench next)", lang=1,
        steps=[("wait", 30), ("press", "start", 5, 30), ("wait", 20), ("snap", "menu_first"),
               ("press", "down", 5, 14), ("press", "down", 5, 14), ("press", "down", 5, 14), ("press", "down", 5, 14), ("snap", "row_language"),
               ("press", "down", 5, 14), ("snap", "row_dev"), ("press", "down", 5, 14), ("press", "cross", 5, 30), ("snap", "row_title_question"),
               ("press", "circle", 5, 20), ("press", "down", 5, 14), ("snap", "row_close")],
        expect=["journey: mode on"]),
    "chargen_v3_en": dict(
        desc="NEW GAME: the LPC creator (bases, six tabs, grid, swatches, view toggle, name, confirm), then the village with that hero walking",
        boot="new", lang=0, debug={"skip_dialogue": True},
        steps=[("wait", 90), ("snap", "01_base"), ("press", "right", 5, 16), ("wait", 10), ("snap", "02_base_duelist"), ("press", "left", 5, 16), ("press", "cross", 5, 20), ("wait", 10), ("snap", "03_hair_tab"), ("press", "right", 5, 16), ("press", "right", 5, 16), ("press", "down", 5, 16), ("press", "down", 5, 16), ("press", "right", 5, 16), ("press", "right", 5, 16), ("press", "right", 5, 16), ("wait", 10), ("snap", "04_hair_changed"), ("press", "l2", 5, 16), ("press", "right", 5, 16), ("press", "right", 5, 16), ("press", "down", 5, 16), ("press", "down", 5, 16), ("press", "right", 5, 16), ("wait", 10), ("snap", "05_outfit_tab"), ("press", "l2", 5, 16), ("press", "right", 5, 16), ("press", "down", 5, 16), ("press", "right", 5, 16), ("press", "down", 5, 16), ("press", "right", 5, 16), ("wait", 10), ("snap", "06_colour_tab"), ("press", "l2", 5, 16), ("press", "right", 5, 16), ("press", "right", 5, 16), ("press", "r2", 5, 16), ("wait", 10), ("snap", "07_accessories_tab"), ("press", "l2", 5, 16), ("press", "right", 5, 16), ("wait", 10), ("snap", "08_legs_tab"), ("press", "l2", 5, 16), ("press", "right", 5, 16), ("press", "right", 5, 16), ("wait", 10), ("snap", "09_shoes_tab"), ("press", "square", 5, 16), ("snap", "10_view_portrait"), ("press", "square", 5, 16), ("press", "start", 5, 20), ("snap", "11_name"), ("press", "start", 5, 20), ("wait", 10), ("snap", "12_confirm"), ("press", "cross", 5, 60), ("wait", 200), ("snap", "13_in_game"), ("hold", "right", 30), ("snap", "14_in_game_walking"), ("hold", "down", 20), ("snap", "15_in_game_walking_down")],
        expect=["chargen: LPC parts ready", "journey: creator look", "journey: mode on"]),
    "chargen_v3_pt": dict(
        desc="NEW GAME: the LPC creator (bases, six tabs, grid, swatches, view toggle, name, confirm), then the village with that hero walking",
        boot="new", lang=1, debug={"skip_dialogue": True},
        steps=[("wait", 90), ("snap", "01_base"), ("press", "right", 5, 16), ("wait", 10), ("snap", "02_base_duelist"), ("press", "left", 5, 16), ("press", "cross", 5, 20), ("wait", 10), ("snap", "03_hair_tab"), ("press", "right", 5, 16), ("press", "right", 5, 16), ("press", "down", 5, 16), ("press", "down", 5, 16), ("press", "right", 5, 16), ("press", "right", 5, 16), ("press", "right", 5, 16), ("wait", 10), ("snap", "04_hair_changed"), ("press", "l2", 5, 16), ("press", "right", 5, 16), ("press", "right", 5, 16), ("press", "down", 5, 16), ("press", "down", 5, 16), ("press", "right", 5, 16), ("wait", 10), ("snap", "05_outfit_tab"), ("press", "l2", 5, 16), ("press", "right", 5, 16), ("press", "down", 5, 16), ("press", "right", 5, 16), ("press", "down", 5, 16), ("press", "right", 5, 16), ("wait", 10), ("snap", "06_colour_tab"), ("press", "l2", 5, 16), ("press", "right", 5, 16), ("press", "right", 5, 16), ("press", "r2", 5, 16), ("wait", 10), ("snap", "07_accessories_tab"), ("press", "l2", 5, 16), ("press", "right", 5, 16), ("wait", 10), ("snap", "08_legs_tab"), ("press", "l2", 5, 16), ("press", "right", 5, 16), ("press", "right", 5, 16), ("wait", 10), ("snap", "09_shoes_tab"), ("press", "square", 5, 16), ("snap", "10_view_portrait"), ("press", "square", 5, 16), ("press", "start", 5, 20), ("snap", "11_name"), ("press", "start", 5, 20), ("wait", 10), ("snap", "12_confirm"), ("press", "cross", 5, 60), ("wait", 200), ("snap", "13_in_game"), ("hold", "right", 30), ("snap", "14_in_game_walking"), ("hold", "down", 20), ("snap", "15_in_game_walking_down")],
        expect=["chargen: LPC parts ready", "journey: creator look", "journey: mode on"]),
    "chargen_continue_look": dict(
        desc="a saved look (debug look [2,1,4,1,0,1]) is what the village shows after Continue: deep skin, cloak plum, bob? see shots",
        preset="3 Simon won (bench next)", debug={"look": [3, 2, 1, 4, 3, 4, 2]},
        steps=[("wait", 60), ("snap", "hero_saved_look"), ("hold", "right", 20), ("snap", "hero_walks_right")],
        expect=["journey: mode on"]),

    "hero_face_talk": dict(desc="the hero's talk avatar is a 168x168 face composed from the 64px parts of the saved look (not a cut of the map cell): beach landing, Atos' line",
        preset="18 beach landing (chapter 2)", lang=1, debug={"look": [3, 7, 5, 4, 3, 4, 2, 1]},
        steps=[("wait", 60), ("until", "scene dk2_landing", 600), ("wait", 80), ("snap", "p1_narrator"), ("press", "cross", 5, 40), ("wait", 30), ("snap", "p2_mai"),
               ("press", "cross", 5, 40), ("wait", 30), ("snap", "p3_atos_preset")],
        expect=["scene dk2_landing", "talk face: hero preset 168x168"]),
    # ---- chapter 1 end and chapter 2 (the harbor, the ship, the Shore of Illusions)
    "cap2_harbor_pt": dict(desc="the harbor (PT): the Inspector at the gate, the blocked gate, music 18", preset="14 harbor gate (Inspector)", lang=1,
        debug={"teleport": "harbor.inspector_spot"}, steps=[("wait", 90), ("snap", "harbor_gate"), ("press", "cross"), ("wait", 120), ("snap", "inspector_talk")],
        expect=["journey: music 18"]),
    "cap2_pier_en": dict(desc="the pier (EN): farewells, the gangway", preset="16 farewells on the pier", lang=0,
        steps=[("wait", 90), ("snap", "pier_farewells")], expect=["journey: music 18"]),
    "cap2_ship_pt": dict(desc="the ship (PT): Mai and InsetoKaiba on deck, music 20", preset="17 on the ship (Mai, InsetoKaiba)", lang=1,
        steps=[("wait", 90), ("snap", "ship_deck"), ("press", ["r1", "l1", "right"], 4, 40), ("wait", 30), ("snap", "ship_anchor")],
        expect=["journey: music 20"]),
    "cap2_beach_pt": dict(desc="the beach (PT): the landing scene plays by itself; the Pegasus mirror", preset="18 beach landing (chapter 2)", lang=1,
        steps=[("wait", 60), ("snap", "beach"), ("until", "scene dk2_landing", 600), ("wait", 80), ("snap", "landing_dialogue")],
        expect=["scene dk2_landing", "journey: music 30"]),
    "cap2_beach_en": dict(desc="the beach (EN): the landing", preset="18 beach landing (chapter 2)", lang=0,
        steps=[("wait", 60), ("until", "scene dk2_landing", 600), ("wait", 80), ("snap", "landing_dialogue")], expect=["scene dk2_landing"]),
    "cap2_weevil_pt": dict(desc="Weevil's ambush on the beach (PT)", preset="19 Weevil ambush", lang=1,
        steps=[("wait", 60), ("until", "scene dk2_weevil", 900), ("wait", 80), ("snap", "weevil_ambush")], expect=["scene dk2_weevil"]),
    "cap2_shop_harbor_pt": dict(desc="Dock Dan's cart (PT)", preset="15 Courier at the pier end", lang=1,
        debug={"skip_dialogue": True, "coins": 900, "teleport": "harbor.shop_stall"},
        steps=[("wait", 60), ("snap", "at_stall"), ("press", "cross"), ("wait", 400), ("snap", "shop")], expect=["scene dk2_dock_dan"]),
    "cap2_shop_ship_en": dict(desc="Purser Pim's locker on the ship (EN)", preset="17 on the ship (Mai, InsetoKaiba)", lang=0,
        debug={"skip_dialogue": True, "coins": 900, "teleport": "ship_deck.shop_stall"},
        steps=[("wait", 60), ("press", "cross"), ("wait", 400), ("snap", "shop")], expect=["scene dk2_purser"]),
    "cap2_arena_ship_pt": dict(desc="the Bilge Ring (PT): the ladder and its arena-only cards", preset="17 on the ship (Mai, InsetoKaiba)", lang=1,
        debug={"skip_dialogue": True, "coins": 900, "xp": 400, "teleport": "ship_deck.arena_door"},
        steps=[("wait", 60), ("snap", "door"), ("press", "cross"), ("wait", 120), ("snap", "inside"), ("press", "cross"), ("wait", 40), ("snap", "arena")], expect=[]),
    "cap2_arena_harbor_en": dict(desc="the Net Loft Pit (EN)", preset="15 Courier at the pier end", lang=0,
        debug={"skip_dialogue": True, "coins": 900, "xp": 400, "teleport": "harbor.arena_door"},
        steps=[("wait", 60), ("press", "cross"), ("wait", 120), ("press", "cross"), ("wait", 40), ("snap", "arena")], expect=[]),
    "cap2_starter_deck": dict(desc="the weak starter deck in the deck editor", preset="6 Hakim's hint (Kemet next)", settings={"deck_slots": 0}, debug={"starter": True},
        steps=[("press", "start", 5, 30), ("press", "cross", 5, 30), ("wait", 400), ("snap", "deck_editor")], expect=["starter deck given"]),

})
GO = ("press", ["r1", "l1", "cross"], 4, 30)          # debug chord: stand next to the objective
def beat(scene, label, frames=900, after=200):
    return [("press", "circle", 4, 20), GO, ("wait", 20), ("press", "cross"), ("until", "scene " + scene, frames), ("wait", after), ("snap", label)]
SAVE = [("wait", 60), ("press", "start", 5, 30), ("press", "down", 5, 20), ("press", "cross", 5, 30), ("press", "triangle", 5, 20),
        ("press", "down", 5, 20), ("press", "down", 5, 20), ("press", "cross", 5, 40), ("press", "triangle", 5, 20), ("press", "triangle", 5, 30), ("wait", 30)]
REL = SAVE + [("release",), ("wait", 120)]
WALK = [s for i in range(14) for s in (("hold", "right", 90), ("hold", "down", 30), ("hold", "left", 90), ("hold", "up", 30))]
E2E = dict(skip_dialogue=True, win_duels=True)
SCENARIOS.update({
    "e2e_harbor_to_beach": dict(desc="play-through: Inspector, gate, Courier, farewells, board, Mai, InsetoKaiba, the mast cameo, the beach, the mirror, Weevil won, chapter 2 end",
        preset="14 harbor gate (Inspector)", lang=1, debug=dict(E2E, coins=300),
        steps=beat("dk1_inspector_pre", "inspector") + [("until", "duel over", 900), ("wait", 300), ("snap", "gate_open")]
            + beat("dk1_shadi_pre", "courier") + [("until", "duel over", 900), ("until", "observer", 900), ("wait", 30), ("snap", "breakwater_mago"), ("until", "saved (stage 6", 1500), ("wait", 200)]
            + beat("dk1_simon_farewell", "simon_farewell", after=400) + beat("dk1_teana_farewell", "teana_farewell", after=400) + beat("dk1_jono_thanks", "jono_thanks", after=400) + beat("dk1_jono_farewell", "jono_farewell", after=400)
            + beat("dk1_board", "board", after=100) + [("until", "journey: music 20", 900), ("wait", 200), ("snap", "ship")]
            + beat("dk1_mai_rules", "mai", after=500) + beat("dk1_inseto_pre", "inseto") + [("until", "duel over", 900), ("wait", 400)]
            + beat("dk1_arrival", "bow", after=20) + [("until", "observer", 600), ("wait", 20), ("snap", "mast_mago"), ("until", "journey: music 30", 1500), ("wait", 100)]
            + [("until", "scene dk2_landing", 600), ("wait", 600), ("snap", "beach")]
            + beat("dk2_mirror", "mirror", after=600) + [("until", "scene dk2_weevil_ambush", 900), ("wait", 600), ("snap", "weevil_ambush")]
            + beat("dk2_weevil_pre", "weevil_pre") + [("until", "star duel won", 900), ("wait", 600), ("snap", "weevil_won")]
            + beat("dk2_hooded_shore", "hooded", after=500) + beat("dk2_camp", "camp", after=500) + beat("dk3_enter", "jungle_to_forest", after=300)
            + [("press", "triangle", 5, 30), ("wait", 30), ("snap", "journal")],
        expect=["scene dk1_inspector_pre", "scene dk1_shadi_pre", "scene dk1_board", "scene dk1_mai_rules", "scene dk1_inseto_pre", "scene dk1_arrival",
                "observer mago", "scene dk2_landing", "scene dk2_mirror", "scene dk2_weevil_ambush", "star duel won, bet 1, stars 2", "saved (stage 12",
                "scene dk2_hooded_shore", "scene dk2_camp", "scene dk3_enter", "journey: music 18", "journey: music 20", "journey: music 30"]),
    "e2e_weevil_lose": dict(desc="Weevil's wager lost with the last star: the Shore Camp, one star back, no game over; then the rematch is won",
        preset="20 Weevil waits (wager)", lang=1, debug=dict(skip_dialogue=True, lose_duels=True, stars=1),
        steps=beat("dk2_weevil_pre", "weevil_pre") + [("until", "star duel lost", 900), ("until", "GAME OVER", 600), ("wait", 120), ("snap", "game_over")],
        expect=["star duel lost, bet 1, stars 0 (weevil holds 3)", "GAME OVER"], forbid=["saved (stage"]),
    "e2e_gang_harbor": dict(desc="a Jackal ambush in the harbor (west end, away from the objective)", preset="14 harbor gate (Inspector)", lang=0,
        debug={"skip_dialogue": True, "win_duels": True, "coins": 300, "gang_ready": True, "teleport": "harbor.hangout_b"},
        steps=[("wait", 60), ("press", ["r1", "l1", "circle"], 4, 30)] + [s for i in range(8) for s in (("hold", "right", 25), ("hold", "left", 25))] + [("snap", "ambush"), ("press", "cross", 5, 30), ("press", "cross", 5, 30), ("until", "duel over", 900), ("wait", 200), ("snap", "after_ambush")], expect=["ambush won"]),
    "e2e_gang_ship": dict(desc="a Jackal ambush on the ship", preset="17 on the ship (Mai, InsetoKaiba)", lang=1,
        debug={"skip_dialogue": True, "win_duels": True, "coins": 300, "gang_ready": True, "teleport": "ship_deck.hangout_b"},
        steps=[("wait", 60), ("press", ["r1", "l1", "circle"], 4, 30)] + WALK[:16] + [("snap", "ambush"), ("press", "cross", 5, 30), ("press", "cross", 5, 30), ("until", "duel over", 900), ("wait", 200), ("snap", "after_ambush")], expect=["ambush won"]),
    "chips_plain_win": dict(quick=True, desc="a plain duel win (Jackal ambush, no wager) leaves the Kingdom's Fichas Estrela alone: only the game's duel stars may change",
        preset="17 on the ship (Mai, InsetoKaiba)", lang=1,
        debug={"skip_dialogue": True, "win_duels": True, "coins": 300, "stars": 3, "gang_ready": True, "teleport": "ship_deck.hangout_b"},
        steps=[("wait", 60), ("press", ["r1", "l1", "circle"], 4, 30)] + WALK[:16] + [("press", "cross", 5, 30), ("press", "cross", 5, 30), ("until", "after duel", 900), ("wait", 120), ("snap", "hud_after_plain")],
        expect=["ambush won", "after duel, kingdom chips 3,"], forbid=["star duel won"]),
    "chips_wager_win": dict(quick=True, desc="a star duel (wager) win does move the Fichas Estrela: Rex, bet 1, 2 -> 3",
        preset="23 Rex waits (wager)", lang=1, debug=E2E,
        steps=beat("dk3_rex_pre", "rex_pre") + [("until", "after duel", 900), ("wait", 300), ("snap", "hud_after_wager")],
        expect=["star duel won, bet 1, stars 3", "after duel, kingdom chips 3,"]),
    # ---- the player's view: the state is made with debug.json, saved from the START menu, then the game restarts without it
    "final_harbor": dict(desc="player view: the harbor", preset="15 Courier at the pier end", lang=1, debug={"teleport": "harbor.harbor_mid"},
        steps=REL + [("snap", "harbor")], expect=["dev mode 0"]),
    "final_ship": dict(desc="player view: the ship with Mai and InsetoKaiba", preset="17 on the ship (Mai, InsetoKaiba)", lang=1, debug={"teleport": "ship_deck.mast_top"},
        steps=REL + [("snap", "ship")], expect=["dev mode 0"]),
    "final_beach": dict(desc="player view: the Shore of Illusions", preset="21 chapter 2 done", lang=1, debug={"teleport": "kingdom_beach.beach_center"},
        steps=REL + [("snap", "beach")], expect=["dev mode 0"]),
    "final_weevil": dict(desc="player view: Weevil's duel intro", preset="20 Weevil waits (wager)", lang=1, debug={"teleport": "kingdom_beach.weevil_spot"},
        steps=REL + [("hold", "down", 6), ("press", "up", 3, 10), ("press", "cross"), ("until", "scene dk2_weevil_pre", 300), ("wait", 90), ("snap", "weevil_intro"),
                     ("press", "cross", 5, 60), ("wait", 60), ("snap", "weevil_intro2")], expect=["scene dk2_weevil_pre"]),
    "final_camp": dict(desc="player view: the Shore Camp sign warns that zero stars ends the journey", preset="21 chapter 2 done", lang=1,
        debug={"teleport": "kingdom_beach.shore_camp"},
        steps=REL + [("press", "cross"), ("until", "scene dk2_camp", 300), ("wait", 60), ("press", "cross"), ("wait", 80), ("snap", "camp_warning")], expect=["scene dk2_camp", "dev mode 0"]),
    "final_gang": dict(desc="player view: a Jackal ambush on the ship", preset="17 on the ship (Mai, InsetoKaiba)", lang=1,
        debug={"coins": 300, "walked": 400, "teleport": "ship_deck.hangout_b"},
        steps=REL + [("hold", "left", 4), ("until", "stood by", 1500), ("wait", 400), ("snap", "ambush"), ("press", "cross", 5, 40), ("wait", 60), ("snap", "ambush2")],
        expect=["stood by", "dev mode 0"]),
    "final_mai": dict(desc="player view: Mai's portrait and sprite", preset="17 on the ship (Mai, InsetoKaiba)", lang=1, debug={"teleport": "ship_deck.mai_spot"},
        steps=REL + [("press", "cross"), ("until", "scene dk1_mai", 300), ("wait", 90), ("snap", "mai_talk")], expect=["scene dk1_mai"]),
    "final_inseto": dict(desc="player view: InsetoKaiba's portrait and sprite", preset="17 on the ship (Mai, InsetoKaiba)", lang=1, debug={"teleport": "ship_deck.inseto_spot"},
        steps=REL + [("press", "cross"), ("until", "scene dk1_inseto", 300), ("wait", 90), ("snap", "inseto_talk")], expect=["scene dk1_inseto"]),
})

FOREST_E2E = (beat("dk3_rex_pre", "rex_pre") + [("until", "star duel won", 900), ("wait", 600), ("snap", "rex_won")]
    + beat("dk3_mark_1", "mark1", after=300) + beat("dk3_mark_2", "mark2", after=300) + beat("dk3_mark_3", "mark3", after=100)
    + [("until", "scene dk3_clearing_open", 900), ("wait", 600), ("snap", "clearing_open")]
    + beat("dk3_mage_pre", "mage_pre") + [("until", "star duel won", 900), ("wait", 900), ("snap", "mage_won")]
    + beat("dk4_enter", "pass_to_mountain", after=300) + [("press", "triangle", 5, 30), ("wait", 30), ("snap", "journal")])
SCENARIOS.update({
    "e2e_ch2_to_ch3": dict(desc="chapter 2 -> 3: Weevil's wager won, the camp, the jungle path into the forest, Rex's wager, three Star Marks, the clearing, the Forest Mage's 2-star wager, chapter 3 end",
        preset="20 Weevil waits (wager)", lang=1, debug=dict(E2E, coins=300),
        steps=beat("dk2_weevil_pre", "weevil_pre") + [("until", "star duel won", 900), ("wait", 600)]
            + beat("dk2_hooded_shore", "hooded", after=500) + beat("dk2_camp", "camp", after=500)
            + beat("dk3_enter", "jungle_path", after=100) + [("until", "journey: music 21", 900), ("until", "scene dk3_arrival", 900), ("wait", 600), ("snap", "forest")]
            + FOREST_E2E,
        expect=["star duel won, bet 1, stars 2", "scene dk3_enter", "journey: music 21", "scene dk3_arrival", "star duel won, bet 1, stars 3", "scene dk3_mark_1", "scene dk3_mark_2",
                "scene dk3_mark_3", "scene dk3_clearing_open", "star duel won, bet 1, stars 4", "saved (stage 16", "scene dk4_enter"]),
    "cap3_arrival": dict(desc="chapter 3 opens: the forest, the arrival scene", preset="22 forest arrival (chapter 3)", lang=0, debug={"skip_dialogue": True},
        steps=[("until", "scene dk3_arrival", 600), ("wait", 300), ("snap", "forest")], expect=["scene dk3_arrival", "journey: music 21"]),
    "cap3_rex": dict(desc="Rex's wager (win)", preset="23 Rex waits (wager)", lang=0, debug=E2E,
        steps=beat("dk3_rex_pre", "rex_pre") + [("until", "star duel won", 900), ("wait", 600), ("snap", "won")], expect=["star duel won, bet 1, stars 3", "saved (stage 14"]),
    "cap3_rex_lose": dict(desc="Rex's wager lost: one star less", preset="23 Rex waits (wager)", lang=1, debug=dict(skip_dialogue=True, lose_duels=True),
        steps=beat("dk3_rex_pre", "rex_pre") + [("until", "star duel lost", 900), ("wait", 600), ("snap", "lost")], expect=["star duel lost, bet 1, stars 1 (rex_forest holds 3)"]),
    "cap3_marks": dict(desc="the three Star Marks open the clearing", preset="24 Star Marks", lang=0, debug=E2E,
        steps=beat("dk3_mark_1", "mark1", after=300) + beat("dk3_mark_2", "mark2", after=300) + beat("dk3_mark_3", "mark3", after=100)
            + [("until", "scene dk3_clearing_open", 900), ("wait", 600), ("snap", "clearing")], expect=["scene dk3_clearing_open", "saved (stage 15"]),
    "cap3_mage": dict(desc="the Forest Mage's two-star wager (win), chapter 3 end", preset="26 Forest Mage (wager)", lang=0, debug=E2E,
        steps=beat("dk3_mage_pre", "mage_pre") + [("until", "star duel won", 900), ("wait", 900), ("snap", "won")], expect=["star duel won, bet 1, stars 4", "saved (stage 16"]),
    "cap3_gang": dict(desc="a Jackal ambush in the forest", preset="24 Star Marks", lang=1,
        debug={"skip_dialogue": True, "win_duels": True, "coins": 300, "gang_ready": True, "teleport": "kingdom_forest.hangout_b"},
        steps=[("wait", 60), ("press", ["r1", "l1", "circle"], 4, 30)] + WALK[:16] + [("snap", "ambush"), ("press", "cross", 5, 30), ("press", "cross", 5, 30), ("until", "duel over", 900), ("wait", 200), ("snap", "after_ambush")], expect=["ambush won"]),
    "cap3_arena": dict(desc="the Hollow Log Ring (forest arena) with its exclusives", preset="24 Star Marks", lang=1,
        debug={"skip_dialogue": True, "coins": 900, "xp": 600, "teleport": "kingdom_forest.arena_door"},
        steps=[("wait", 60), ("press", "cross"), ("wait", 120), ("press", "cross"), ("wait", 40), ("snap", "arena")], expect=[]),
    "cap3_shop": dict(desc="Hermit Hob's hut (forest shop)", preset="24 Star Marks", lang=1,
        debug={"skip_dialogue": True, "coins": 900, "xp": 600, "teleport": "kingdom_forest.shop_stall"},
        steps=[("wait", 60), ("press", "cross"), ("wait", 200), ("press", "cross"), ("wait", 120), ("snap", "shop")], expect=[]),
    # player views (no debug.json)
    "final3_forest": dict(desc="player view: the forest with Rex and Hob", preset="23 Rex waits (wager)", lang=1, debug={"teleport": "kingdom_forest.forest_center"},
        steps=REL + [("snap", "forest")], expect=["dev mode 0"]),
    "final3_rex": dict(desc="player view: Rex's duel intro", preset="23 Rex waits (wager)", lang=1, debug={"teleport": "kingdom_forest.rex_spot"},
        steps=REL + [("press", "cross"), ("until", "scene dk3_rex_pre", 300), ("wait", 90), ("snap", "rex_intro")], expect=["scene dk3_rex_pre"]),
    "final3_mark": dict(desc="player view: a Star Mark", preset="24 Star Marks", lang=1, debug={"teleport": "kingdom_forest.star_mark_1"},
        steps=REL + [("press", "cross"), ("until", "scene dk3_mark_1", 300), ("wait", 90), ("snap", "mark")], expect=["scene dk3_mark_1"]),
    "final3_mage": dict(desc="player view: the Forest Mage at the gate", preset="26 Forest Mage (wager)", lang=1, debug={"teleport": "kingdom_forest.gate_spot"},
        steps=REL + [("hold", "down", 14), ("press", "up", 3, 10), ("snap", "gate"), ("press", "cross"), ("until", "scene dk3_mage", 300), ("wait", 90), ("snap", "mage_intro"),
                     ("press", "cross", 5, 60), ("wait", 60), ("snap", "mage_intro2")], expect=["scene dk3_mage_pre", "dev mode 0"]),
    "final3_end": dict(desc="player view: chapter 3 complete, five stars", preset="27 chapter 3 done", lang=1, debug={"teleport": "kingdom_forest.forest_center"},
        steps=REL + [("snap", "end"), ("press", "triangle", 5, 30), ("wait", 30), ("snap", "journal")], expect=["dev mode 0"]),
    "final3_gang": dict(desc="player view: a Jackal ambush in the forest", preset="24 Star Marks", lang=1,
        debug={"coins": 300, "walked": 400, "teleport": "kingdom_forest.hangout_b"},
        steps=REL + [("hold", "left", 4), ("until", "stood by", 1500), ("wait", 30), ("snap", "ambush0"), ("wait", 400), ("snap", "ambush"), ("press", "cross", 5, 40), ("wait", 60), ("snap", "ambush2")],
        expect=["stood by", "dev mode 0"]),
})

MOUNTAIN_E2E = (beat("dk4_keith_pre", "keith_pre") + [("until", "star duel won", 900), ("wait", 600), ("snap", "keith_won")]
    + beat("dk4_mai_pre", "mai_pre") + [("until", "scene dk4_mai_win", 900), ("wait", 600), ("snap", "mai_won")]
    + beat("dk4_carver", "carver", after=600)
    + beat("dk4_mage_pre", "mage_pre") + [("until", "star duel won", 900), ("wait", 900), ("snap", "mage_won")]
    + beat("dk4_castle_road", "castle_road", after=300) + [("press", "triangle", 5, 30), ("wait", 30), ("snap", "journal")])
SCENARIOS.update({
    "e2e_ch3_to_ch4": dict(desc="chapter 3 -> 4: the forest road into the Mountain Pass, Keith's Double or Nothing, Mai across the bridge, the star-carver, the Mountain Mage, chapter 4 end",
        preset="27 chapter 3 done", lang=1, debug=dict(E2E, coins=300),
        steps=beat("dk4_enter", "pass_road", after=100) + [("until", "journey: music 22", 900), ("until", "scene dk4_arrival", 900), ("wait", 600), ("snap", "mountain")]
            + MOUNTAIN_E2E,
        expect=["scene dk4_enter", "journey: music 22", "scene dk4_arrival", "star duel won, bet 1, stars 5", "scene dk4_mai_pre", "scene dk4_mai_win",
                "scene dk4_carver", "saved (stage 20", "star duel won, bet 1, stars 6", "saved (stage 21", "scene dk4_castle_road"]),
    "cap4_arrival": dict(desc="chapter 4 opens: the pass, the arrival scene", preset="28 mountain arrival (chapter 4)", lang=0, debug={"skip_dialogue": True},
        steps=[("until", "scene dk4_arrival", 600), ("wait", 300), ("snap", "mountain")], expect=["scene dk4_arrival", "journey: music 22"]),
    "cap4_keith": dict(desc="Keith's Double or Nothing (win: +2)", preset="29 Keith's toll (wager)", lang=0, debug=E2E,
        steps=beat("dk4_keith_pre", "keith_pre") + [("until", "star duel won", 900), ("wait", 600), ("snap", "won")], expect=["star duel won, bet 1, stars 5", "saved (stage 18"]),
    "cap4_keith_lose": dict(desc="Keith's toll: a bet of 4 is capped at his 3; lost, stars 1, he holds 6 (no game over)", preset="29 Keith's toll (wager)", lang=1,
        debug=dict(skip_dialogue=True, lose_duels=True, wager=4),
        steps=beat("dk4_keith_pre", "keith_pre") + [("until", "star duel lost", 900), ("wait", 300), ("snap", "lost")],
        expect=["wager 3", "star duel lost, bet 3, stars 1 (keith holds 6)"], forbid=["GAME OVER"]),
    "cap4_forest_lose": dict(desc="Rex's wager lost with the last star: game over (no camp rescue)", preset="23 Rex waits (wager)", lang=1,
        debug=dict(skip_dialogue=True, lose_duels=True, stars=1),
        steps=beat("dk3_rex_pre", "rex_pre") + [("until", "star duel lost", 900), ("until", "GAME OVER", 600), ("wait", 120), ("snap", "game_over")],
        expect=["star duel lost, bet 1, stars 0", "GAME OVER"], forbid=["saved (stage"]),
    "cap4_mai": dict(desc="Mai's pride duel (win, no star)", preset="30 Mai across the bridge (pride duel)", lang=0, debug=E2E,
        steps=beat("dk4_mai_pre", "mai_pre") + [("until", "scene dk4_mai_win", 900), ("wait", 600), ("snap", "won")], expect=["scene dk4_mai_win", "saved (stage 19"], forbid=["star duel"]),
    "cap4_carver": dict(desc="the star-carver in the cave", preset="31 the star-carver's cave", lang=0, debug=E2E,
        steps=beat("dk4_carver", "carver", after=600), expect=["scene dk4_carver", "saved (stage 20"]),
    "cap4_mage": dict(desc="the Mountain Mage's two-star wager (win), chapter 4 end", preset="32 Mountain Mage (wager)", lang=0, debug=E2E,
        steps=beat("dk4_mage_pre", "mage_pre") + [("until", "star duel won", 900), ("wait", 900), ("snap", "won")], expect=["star duel won, bet 1, stars 6", "saved (stage 21"]),
    "cap4_gang": dict(desc="a Jackal ambush on the pass", preset="30 Mai across the bridge (pride duel)", lang=1,
        debug={"skip_dialogue": True, "win_duels": True, "coins": 300, "gang_ready": True, "teleport": "kingdom_mountain.hangout_b"},
        steps=[("wait", 60), ("press", ["r1", "l1", "circle"], 4, 30)] + WALK[:16] + [("snap", "ambush"), ("press", "cross", 5, 30), ("press", "cross", 5, 30), ("until", "duel over", 900), ("wait", 200), ("snap", "after_ambush")], expect=["ambush won"]),
    "cap4_arena": dict(desc="the Mine Shaft Pit (mountain arena) with its exclusives", preset="30 Mai across the bridge (pride duel)", lang=1,
        debug={"skip_dialogue": True, "coins": 900, "xp": 900, "teleport": "kingdom_mountain.arena_door"},
        steps=[("wait", 60), ("press", "cross"), ("wait", 120), ("press", "cross"), ("wait", 40), ("snap", "arena")], expect=[]),
    "cap4_shop": dict(desc="Cliff Cass's tent (mountain shop)", preset="30 Mai across the bridge (pride duel)", lang=1,
        debug={"skip_dialogue": True, "coins": 900, "xp": 900, "teleport": "kingdom_mountain.shop_stall"},
        steps=[("wait", 60), ("press", "cross"), ("wait", 200), ("press", "cross"), ("wait", 120), ("snap", "shop")], expect=[]),
    # player views (no debug.json)
    "final4_mountain": dict(desc="player view: the pass with Keith and Cliff Cass", preset="29 Keith's toll (wager)", lang=1, debug={"teleport": "kingdom_mountain.pass_center"},
        steps=REL + [("snap", "mountain")], expect=["dev mode 0"]),
    "final4_keith": dict(desc="player view: Keith's toll intro", preset="29 Keith's toll (wager)", lang=1, debug={"teleport": "kingdom_mountain.keith_spot"},
        steps=REL + [("press", "cross"), ("until", "scene dk4_keith_pre", 300), ("wait", 90), ("snap", "keith_intro"), ("press", "cross", 5, 60), ("wait", 60), ("snap", "keith_intro2")], expect=["scene dk4_keith_pre"]),
    "final4_mai": dict(desc="player view: Mai across the bridge", preset="30 Mai across the bridge (pride duel)", lang=1, debug={"teleport": "kingdom_mountain.mai_spot"},
        steps=REL + [("press", "cross"), ("until", "scene dk4_mai_pre", 300), ("wait", 90), ("snap", "mai_intro")], expect=["scene dk4_mai_pre"]),
    "final4_carver": dict(desc="player view: the star-carver caught in the cave", preset="31 the star-carver's cave", lang=1, debug={"teleport": "kingdom_mountain.cave_spot"},
        steps=REL + [("hold", "down", 14), ("press", "up", 3, 10), ("snap", "cave"), ("press", "cross"), ("until", "scene dk4_carver", 300), ("wait", 90), ("snap", "carver1"),
                     ("press", "cross", 5, 60), ("press", "cross", 5, 60), ("wait", 60), ("snap", "carver2"), ("press", "cross", 5, 60), ("wait", 60), ("snap", "carver3")], expect=["scene dk4_carver"]),
    "final4_mage": dict(desc="player view: the Mountain Mage at the summit gate", preset="32 Mountain Mage (wager)", lang=1, debug={"teleport": "kingdom_mountain.gate_spot"},
        steps=REL + [("hold", "down", 14), ("press", "up", 3, 10), ("snap", "gate"), ("press", "cross"), ("until", "scene dk4_mage", 300), ("wait", 90), ("snap", "mage_intro")], expect=["scene dk4_mage_pre", "dev mode 0"]),
    "final4_end": dict(desc="player view: chapter 4 complete, ten stars", preset="33 chapter 4 done", lang=1, debug={"teleport": "kingdom_mountain.hangout_a"},
        steps=REL + [("snap", "end"), ("press", "triangle", 5, 30), ("wait", 30), ("snap", "journal")], expect=["dev mode 0"]),
    "final4_gang": dict(desc="player view: a Jackal ambush on the pass", preset="30 Mai across the bridge (pride duel)", lang=1,
        debug={"coins": 300, "walked": 400, "teleport": "kingdom_mountain.hangout_b"},
        steps=REL + [("hold", "left", 4), ("until", "stood by", 1500), ("wait", 120), ("snap", "ambush"), ("press", "cross", 5, 40), ("wait", 60), ("snap", "ambush2")],
        expect=["stood by", "dev mode 0"]),
})

SCENARIOS.update({
    # the star rebalance: one star per gatekeeper, gates that count them, a lost star won back with the next win
    "stars_pass_short": dict(desc="the mountain pass stays shut under four stars", preset="27 chapter 3 done", lang=1,
        debug={"skip_dialogue": True, "stars": 3, "teleport": "kingdom_forest.pass_road"},
        steps=[("wait", 60), ("press", "cross"), ("until", "scene dk3_pass_locked", 300), ("wait", 60), ("snap", "pass_shut")], expect=["scene dk3_pass_locked"], forbid=["scene dk4_enter"]),
    "wager_lose_rematch": dict(desc="a lost bet stays with the Forest Mage (he holds 4); the rematch before beating him bets 2 and wins them back", preset="26 Forest Mage (wager)", lang=1,
        debug=dict(skip_dialogue=True, lose_duels=True, wager=1),
        steps=beat("dk3_mage_pre", "mage_pre") + [("until", "star duel lost", 900), ("wait", 600), ("snap", "lost")],
        expect=["star duel lost, bet 1, stars 2 (forest_mage holds 4)"]),
    "wager_rematch_win": dict(desc="Forest Mage holds 4 after a loss (stars 2): rematch betting 2 wins, stars 4 (curve back), he holds 2", preset="26 Forest Mage (wager)", lang=1,
        debug=dict(skip_dialogue=True, win_duels=True, wager=2, stars=2, held={"2": 4}),
        steps=beat("dk3_mage_pre", "mage_pre") + [("until", "star duel won", 900), ("wait", 600), ("snap", "won")],
        expect=["wager 2", "star duel won, bet 2, stars 4 (forest_mage holds 2)", "saved (stage 16"]),
    "wager_bet3_win": dict(desc="a big bet on the Forest Mage: 3 stars, a win jumps to 6", preset="26 Forest Mage (wager)", lang=1,
        debug=dict(skip_dialogue=True, win_duels=True, wager=3),
        steps=beat("dk3_mage_pre", "mage_pre") + [("until", "star duel won", 900), ("wait", 600), ("snap", "won")],
        expect=["star duel won, bet 3, stars 6 (forest_mage holds 0)"]),
    "wager_after_beaten": dict(desc="beaten Forest Mage still holds 2 stars won from the hero (held 4): the rematch wager wins them back", preset="27 chapter 3 done", lang=1,
        debug={"skip_dialogue": True, "win_duels": True, "wager": 2, "stars": 2, "held": {"2": 4}, "teleport": "kingdom_forest.gate_spot"},
        steps=[("wait", 60), ("press", "cross"), ("until", "scene dk_wager_rematch", 300), ("until", "star duel won", 900), ("wait", 300), ("snap", "won_back")],
        expect=["scene dk_wager_rematch", "star duel won, bet 2, stars 4 (forest_mage holds 2)"]),
    "wager_back_out": dict(desc="the picker can be left with S: no duel", preset="20 Weevil waits (wager)", lang=1,
        debug={"skip_dialogue": True, "wager": -1},
        steps=beat("dk2_weevil_pre", "pre") + [("wait", 60), ("press", "triangle", 5, 30), ("wait", 60), ("snap", "backed_out")], expect=["scene dk2_weevil_pre"], forbid=["star duel", "wager 1"]),
    "stars_bag": dict(desc="player view: the Mochila shows the Star Chips with their count and text", preset="33 chapter 4 done", lang=1, debug={"teleport": "kingdom_mountain.hangout_a"},
        steps=REL + [("press", "start", 5, 30), ("press", "down", 5, 14), ("press", "cross", 5, 30), ("wait", 20)] + [("press", "right", 5, 10)] * 20 + [("wait", 20), ("snap", "bag_stars"), ("press", "cross", 5, 30), ("wait", 20), ("snap", "star_details")], expect=["dev mode 0"]),
})
SCENARIOS.update({
    "final_stars_pass_short": dict(desc="player view: the pass stays shut under four stars", preset="27 chapter 3 done", lang=1, debug={"stars": 3, "teleport": "kingdom_forest.pass_road"},
        steps=REL + [("press", "cross"), ("until", "scene dk3_pass_locked", 300), ("wait", 90), ("snap", "pass_shut")], expect=["scene dk3_pass_locked", "dev mode 0"]),
    "final_stars_gate_short": dict(desc="player view: the summit arch counts six stars", preset="32 Mountain Mage (wager)", lang=1, debug={"stars": 5, "teleport": "kingdom_mountain.summit_gate"},
        steps=REL + [("press", "cross"), ("until", "scene dk4_gate_shut", 300), ("wait", 90), ("snap", "gate_shut")], expect=["scene dk4_gate_shut", "dev mode 0"]),
})
SCENARIOS.update({
    # player view of the wager (shots/wager/)
    "final_wager_picker": dict(desc="player view: the wager picker before Keith (4 stars, he holds 3), first time: the game-over warning", preset="29 Keith's toll (wager)", lang=1,
        debug={"wager": -1, "teleport": "kingdom_mountain.keith_spot"},
        steps=REL + [("press", "cross"), ("until", "scene dk4_keith_pre", 300), ("mash", "wager picker", 1500), ("wait", 60), ("snap", "picker"),
              ("press", "right", 5, 20), ("press", "right", 5, 20), ("wait", 30), ("snap", "picker_bet3"), ("press", "right", 5, 20), ("wait", 30), ("snap", "picker_allin")],
        expect=["scene dk4_keith_pre", "wager picker (max 3, keith holds 3)", "dev mode 0"]),
    "final_wager_win": dict(desc="player view: won a 2-star bet against the Forest Mage", preset="26 Forest Mage (wager)", lang=1,
        debug={"skip_dialogue": True, "win_duels": True, "wager": 2},
        steps=beat("dk3_mage_pre", "pre") + [("until", "star duel won", 900), ("wait", 300)] + REL + [("wait", 30), ("snap", "win_result")],
        expect=["star duel won, bet 2, stars 5 (forest_mage holds 1)"]),
    "final_wager_loss": dict(desc="player view: lost a 1-star bet to Rex, he keeps it", preset="23 Rex waits (wager)", lang=1,
        debug={"skip_dialogue": True, "lose_duels": True, "wager": 1},
        steps=beat("dk3_rex_pre", "pre") + [("until", "star duel lost", 900), ("wait", 600)] + REL + [("wait", 30), ("snap", "loss_result")],
        expect=["star duel lost, bet 1, stars 1 (rex_forest holds 3)"]),
    "final_wager_gameover": dict(desc="player view: the last star lost to Weevil, GAME OVER", preset="20 Weevil waits (wager)", lang=1,
        debug={"skip_dialogue": True, "lose_duels": True, "wager": 1},
        steps=beat("dk2_weevil_pre", "pre") + [("until", "GAME OVER", 900), ("wait", 150), ("snap", "game_over")],
        expect=["GAME OVER"]),
    "final_wager_warn": dict(desc="player view: the trail camp staff warns that zero stars ends the journey", preset="29 Keith's toll (wager)", lang=1,
        debug={"teleport": "kingdom_mountain.trail_camp"},
        steps=REL + [("press", "cross"), ("until", "scene dk4_trail_camp", 300), ("wait", 40), ("press", "cross"), ("wait", 400), ("snap", "warning")], expect=["scene dk4_trail_camp", "dev mode 0"]),
    "final_wager_bag": dict(desc="player view: the Star Chips in the Mochila with the GAME OVER line", preset="33 chapter 4 done", lang=1, debug={"teleport": "kingdom_mountain.hangout_a"},
        steps=REL + [("press", "start", 5, 30), ("press", "down", 5, 14), ("press", "cross", 5, 30), ("wait", 20)] + [("press", "right", 5, 10)] * 20 + [("wait", 20), ("press", "cross", 5, 30), ("wait", 20), ("snap", "star_details")], expect=["dev mode 0"]),
})


# ---------------------------------------------------------------- quick suite (fast.py quick / jm_smoke.py quick / fast.sh --quick)
# Critical path only: star gates, wager picker open, bet-1 win, last-star GAME OVER, chapter jumps.
# Full e2e_* and final_* player-view runs stay available via `all` / named runs.
_QUICK = (
    "stars_pass_short",           # gate: pass shut under 4 stars
    "cap4_keith",                 # star duel bet 1 win (mountain)
    "wager_back_out",             # picker opens and can be cancelled
    "wager_bet3_win",             # wager amount honored on a win
    "e2e_weevil_lose",            # last star lost -> GAME OVER
    "final_wager_picker",         # picker UI (player view)
    "final_wager_gameover",       # GAME OVER player view
    "cap3_arrival",               # chapter 3 jump
    "cap4_arrival",               # chapter 4 jump
)
for _n in _QUICK:
    if _n in SCENARIOS:
        SCENARIOS[_n]["quick"] = True

SCENARIOS.update({
    "quick_wager_picker": dict(
        quick=True,
        desc="QUICK: wager picker opens before Weevil (bet left at default, back out with S)",
        preset="20 Weevil waits (wager)", lang=1,
        debug={"skip_dialogue": True, "wager": -1},
        steps=beat("dk2_weevil_pre", "pre") + [("wait", 40), ("press", "triangle", 5, 20), ("wait", 40), ("snap", "backed")],
        expect=["scene dk2_weevil_pre", "wager picker"], forbid=["star duel won", "star duel lost"]),
    "quick_wager_bet1_win": dict(
        quick=True,
        desc="QUICK: bet 1 on Weevil and win (stars 1 -> 2)",
        preset="20 Weevil waits (wager)", lang=1,
        debug=dict(skip_dialogue=True, win_duels=True, wager=1),
        steps=beat("dk2_weevil_pre", "pre") + [("until", "star duel won", 900), ("wait", 200), ("snap", "won")],
        expect=["wager 1", "star duel won, bet 1, stars 2"]),
    "quick_wager_gameover": dict(
        quick=True,
        desc="QUICK: lose the last star on Weevil -> GAME OVER (no save)",
        preset="20 Weevil waits (wager)", lang=1,
        debug=dict(skip_dialogue=True, lose_duels=True, wager=1, stars=1),
        steps=beat("dk2_weevil_pre", "pre") + [("until", "GAME OVER", 900), ("wait", 80), ("snap", "go")],
        expect=["star duel lost, bet 1, stars 0", "GAME OVER"], forbid=["saved (stage"]),
    "quick_gate_pass": dict(
        quick=True,
        desc="QUICK: mountain pass gate refuses under 4 stars",
        preset="27 chapter 3 done", lang=1,
        debug={"skip_dialogue": True, "stars": 3, "teleport": "kingdom_forest.pass_road"},
        steps=[("wait", 40), ("press", "cross"), ("until", "scene dk3_pass_locked", 300), ("wait", 40), ("snap", "shut")],
        expect=["scene dk3_pass_locked"], forbid=["scene dk4_enter"]),
    "quick_gate_summit": dict(
        quick=True,
        desc="QUICK: summit gate refuses under 6 stars",
        preset="32 Mountain Mage (wager)", lang=1,
        debug={"skip_dialogue": True, "stars": 5, "teleport": "kingdom_mountain.summit_gate"},
        steps=[("wait", 40), ("press", "cross"), ("until", "scene dk4_gate_shut", 300), ("wait", 40), ("snap", "shut")],
        expect=["scene dk4_gate_shut"]),
    "quick_ch4_done": dict(
        quick=True,
        desc="QUICK: jump to chapter 4 done (6 stars) and open the journal",
        preset="33 chapter 4 done", lang=1,
        debug={"skip_dialogue": True, "teleport": "kingdom_mountain.hangout_a"},
        steps=[("wait", 60), ("snap", "pass"), ("press", "triangle", 5, 30), ("wait", 30), ("snap", "journal")],
        expect=["journey: mode on"]),
})


# ---------------------------------------------------------------- chapter 5: the Meadow Maze
MEADOW_E2E = (beat("dk5_teana_pre", "teana_pre") + [("until", "scene dk5_teana_win", 1200), ("wait", 400), ("snap", "teana_won")]
    + beat("dk5_mage_pre", "mage_pre") + [("until", "star duel won", 1200), ("wait", 600), ("snap", "mage_won")]
    + beat("dk5_desert_road", "desert_road", after=200) + [("press", "triangle", 5, 30), ("wait", 30), ("snap", "journal")])
SCENARIOS.update({
    "e2e_ch4_to_ch5": dict(desc="chapter 4 -> 5: summit into the Meadow Maze, Teana, the Meadow Mage, chapter 5 end",
        preset="33 chapter 4 done", lang=1, debug=dict(E2E, coins=300),
        steps=beat("dk5_enter", "summit", after=100) + [("until", "journey: music 19", 900), ("until", "scene dk5_arrival", 900), ("wait", 400), ("snap", "meadow")]
            + MEADOW_E2E,
        expect=["scene dk5_enter", "journey: music 19", "scene dk5_arrival", "scene dk5_teana_win", "saved (stage 23",
                "star duel won, bet 1, stars 7", "saved (stage 24", "scene dk5_desert_road"]),
    "cap5_arrival": dict(quick=True, desc="chapter 5 opens: the maze, the arrival scene", preset="34 meadow arrival (chapter 5)", lang=0, debug={"skip_dialogue": True},
        steps=[("until", "scene dk5_arrival", 600), ("wait", 200), ("snap", "meadow")], expect=["scene dk5_arrival", "journey: music 19"]),
    "cap5_teana": dict(desc="Teana's friendly duel (win)", preset="35 Teana in the hedges (friendly)", lang=0, debug=E2E,
        steps=beat("dk5_teana_pre", "teana_pre") + [("until", "scene dk5_teana_win", 900), ("wait", 400), ("snap", "won")], expect=["scene dk5_teana_win", "saved (stage 23"]),
    "cap5_mage": dict(quick=True, desc="the Meadow Mage's one-star wager (win), chapter 5 end", preset="36 Meadow Mage (wager)", lang=0,
        debug=dict(E2E, teleport="kingdom_meadow.gate_spot"),
        steps=[("wait", 60), ("press", "cross"), ("until", "scene dk5_mage_pre", 600), ("wait", 100), ("snap", "mage_pre"),
               ("until", "star duel won", 1200), ("wait", 600), ("snap", "won")], expect=["scene dk5_mage_pre", "star duel won, bet 1, stars 7", "saved (stage 24"]),
    "cap5_mage_lose": dict(desc="Meadow Mage wager lost: one star less, stays in the meadow", preset="36 Meadow Mage (wager)", lang=1,
        debug=dict(skip_dialogue=True, lose_duels=True, wager=1, teleport="kingdom_meadow.gate_spot"),
        steps=[("wait", 60), ("press", "cross"), ("until", "scene dk5_mage_pre", 600), ("wait", 100), ("snap", "mage_pre"),
               ("until", "star duel lost", 1200), ("wait", 400), ("snap", "lost")],
        expect=["scene dk5_mage_pre", "star duel lost, bet 1, stars 5 (meadow_mage holds 3)"], forbid=["GAME OVER", "kingdom_beach"]),
    "cap5_shop": dict(desc="Rose Rue's flower cart (meadow shop)", preset="35 Teana in the hedges (friendly)", lang=1,
        debug={"skip_dialogue": True, "coins": 900, "xp": 900, "teleport": "kingdom_meadow.shop_stall"},
        steps=[("wait", 60), ("press", "cross"), ("wait", 200), ("press", "cross"), ("wait", 120), ("snap", "shop")], expect=[]),
    "cap5_arena": dict(desc="the Rabbit Hole Ring (meadow arena) with its exclusives", preset="35 Teana in the hedges (friendly)", lang=1,
        debug={"skip_dialogue": True, "coins": 900, "xp": 900, "teleport": "kingdom_meadow.arena_door"},
        steps=[("wait", 60), ("press", "cross"), ("wait", 120), ("press", "cross"), ("wait", 40), ("snap", "arena")], expect=[]),
    "cap5_camp": dict(quick=True, desc="meadow camp warns that zero stars ends the journey", preset="35 Teana in the hedges (friendly)", lang=1,
        debug={"skip_dialogue": True, "teleport": "kingdom_meadow.meadow_camp"},
        steps=[("wait", 40), ("press", "cross"), ("until", "scene dk5_meadow_camp", 300), ("wait", 60), ("snap", "camp")], expect=["scene dk5_meadow_camp"]),
    "cap5_gang": dict(desc="a Jackal ambush in the meadow", preset="35 Teana in the hedges (friendly)", lang=1,
        debug={"skip_dialogue": True, "win_duels": True, "coins": 300, "gang_ready": True, "teleport": "kingdom_meadow.hangout_b"},
        steps=[("wait", 60), ("press", ["r1", "l1", "circle"], 4, 30)] + WALK[:12] + [("snap", "ambush"), ("press", "cross", 5, 30), ("press", "cross", 5, 30), ("until", "duel over", 900), ("wait", 200), ("snap", "after")], expect=["ambush won"]),
    "final5_meadow": dict(desc="player view: the Meadow Maze", preset="35 Teana in the hedges (friendly)", lang=1, debug={"teleport": "kingdom_meadow.maze_center"},
        steps=REL + [("snap", "meadow")], expect=["dev mode 0"]),
    "final5_teana": dict(desc="player view: Teana in the hedges", preset="35 Teana in the hedges (friendly)", lang=1, debug={"teleport": "kingdom_meadow.teana_spot"},
        steps=REL + [("press", "cross"), ("until", "scene dk5_teana_pre", 300), ("wait", 90), ("snap", "teana")], expect=["scene dk5_teana_pre"]),
    "final5_mage": dict(desc="player view: the Meadow Mage at the star stone", preset="36 Meadow Mage (wager)", lang=1, debug={"teleport": "kingdom_meadow.gate_spot"},
        steps=REL + [("press", "cross"), ("until", "scene dk5_mage_pre", 300), ("wait", 90), ("snap", "mage")], expect=["scene dk5_mage_pre"]),
    "final5_end": dict(desc="player view: chapter 5 complete, seven stars", preset="37 chapter 5 done", lang=1, debug={"teleport": "kingdom_meadow.maze_center"},
        steps=REL + [("snap", "end"), ("press", "triangle", 5, 30), ("wait", 30), ("snap", "journal")], expect=["dev mode 0"]),
    "quick_gate_desert": dict(quick=True, desc="QUICK: desert arch refuses under 7 stars", preset="36 Meadow Mage (wager)", lang=1,
        debug={"skip_dialogue": True, "stars": 6, "teleport": "kingdom_meadow.desert_gate"},
        steps=[("wait", 40), ("press", "cross"), ("until", "scene dk5_gate_shut", 300), ("wait", 40), ("snap", "shut")],
        expect=["scene dk5_gate_shut"]),
})

DESERT_E2E = (beat("dk6_isis_pre", "isis_pre") + [("until", "scene dk6_isis_win", 1200), ("wait", 400), ("snap", "isis_won")]
    + beat("dk6_mage_pre", "mage_pre") + [("until", "star duel won", 1200), ("wait", 600), ("snap", "mage_won")]
    + beat("dk6_fair_road", "fair_road", after=200) + [("press", "triangle", 5, 30), ("wait", 30), ("snap", "journal")])
SCENARIOS.update({
    "e2e_ch5_to_ch6": dict(desc="chapter 5 -> 6: desert arch into the dunes, Isis, the Desert Mage, chapter 6 end",
        preset="37 chapter 5 done", lang=1, debug=dict(E2E, coins=300, teleport="kingdom_meadow.desert_gate"),
        steps=beat("dk6_enter", "arch", after=100) + [("until", "journey: music 23", 900), ("until", "scene dk6_arrival", 900), ("wait", 400), ("snap", "desert")]
            + DESERT_E2E,
        expect=["scene dk6_enter", "journey: music 23", "scene dk6_arrival", "scene dk6_isis_win", "saved (stage 26",
                "star duel won, bet 1, stars 8", "saved (stage 27", "scene dk6_fair_road"]),
    "cap6_arrival": dict(quick=True, desc="chapter 6 opens: the dunes, the arrival scene", preset="38 desert arrival (chapter 6)", lang=0, debug={"skip_dialogue": True},
        steps=[("until", "scene dk6_arrival", 600), ("wait", 200), ("snap", "desert")], expect=["scene dk6_arrival", "journey: music 23"]),
    "cap6_isis": dict(desc="Isis's reading duel (win)", preset="39 Isis at the fortune tent", lang=0, debug=E2E,
        steps=beat("dk6_isis_pre", "isis_pre") + [("until", "scene dk6_isis_win", 900), ("wait", 400), ("snap", "won")], expect=["scene dk6_isis_win", "saved (stage 26"]),
    "cap6_mage": dict(quick=True, desc="the Desert Mage's one-star wager (win), chapter 6 end", preset="40 Desert Mage (wager)", lang=0,
        debug=dict(E2E, teleport="kingdom_desert.gate_spot"),
        steps=[("wait", 60), ("press", "cross"), ("until", "scene dk6_mage_pre", 600), ("wait", 100), ("snap", "mage_pre"),
               ("until", "star duel won", 1200), ("wait", 600), ("snap", "won")], expect=["scene dk6_mage_pre", "star duel won, bet 1, stars 8", "saved (stage 27"]),
    "cap6_mage_lose": dict(desc="Desert Mage wager lost: one star less, stays in the desert", preset="40 Desert Mage (wager)", lang=1,
        debug=dict(skip_dialogue=True, lose_duels=True, wager=1, teleport="kingdom_desert.gate_spot"),
        steps=[("wait", 60), ("press", "cross"), ("until", "scene dk6_mage_pre", 600), ("wait", 100), ("snap", "mage_pre"),
               ("until", "star duel lost", 1200), ("wait", 400), ("snap", "lost")],
        expect=["scene dk6_mage_pre", "star duel lost, bet 1, stars 6 (desert_mage holds 3)"], forbid=["GAME OVER", "kingdom_beach"]),
    "cap6_shop": dict(desc="Nomad Nia's Caravan Tent (desert shop)", preset="39 Isis at the fortune tent", lang=1,
        debug={"skip_dialogue": True, "coins": 900, "xp": 900, "teleport": "kingdom_desert.shop_stall"},
        steps=[("wait", 60), ("press", "cross"), ("wait", 200), ("press", "cross"), ("wait", 120), ("snap", "shop")], expect=[]),
    "cap6_arena": dict(desc="the Sunken Tomb Pit (desert arena) with its exclusives", preset="39 Isis at the fortune tent", lang=1,
        debug={"skip_dialogue": True, "coins": 900, "xp": 900, "teleport": "kingdom_desert.arena_door"},
        steps=[("wait", 60), ("press", "cross"), ("wait", 120), ("press", "cross"), ("wait", 40), ("snap", "arena")], expect=[]),
    "cap6_camp": dict(quick=True, desc="desert camp warns that zero stars ends the journey", preset="39 Isis at the fortune tent", lang=1,
        debug={"skip_dialogue": True, "teleport": "kingdom_desert.desert_camp"},
        steps=[("wait", 40), ("press", "cross"), ("until", "scene dk6_desert_camp", 300), ("wait", 60), ("snap", "camp")], expect=["scene dk6_desert_camp"]),
    "cap6_gang": dict(desc="a Jackal ambush in the desert", preset="39 Isis at the fortune tent", lang=1,
        debug={"skip_dialogue": True, "win_duels": True, "coins": 300, "gang_ready": True, "teleport": "kingdom_desert.hangout_a"},
        steps=[("wait", 80), ("press", ["r1", "l1", "circle"], 4, 30)] + WALK[:16] + [("snap", "ambush"), ("press", "cross", 5, 30), ("press", "cross", 5, 30), ("until", "duel over", 1200), ("wait", 200), ("snap", "after")], expect=["ambush won"]),
    "final6_desert": dict(desc="player view: the Desert of Lost Stars", preset="39 Isis at the fortune tent", lang=1, debug={"teleport": "kingdom_desert.desert_center"},
        steps=REL + [("snap", "desert")], expect=["dev mode 0"]),
    "final6_isis": dict(desc="player view: Isis at the fortune tent", preset="39 Isis at the fortune tent", lang=1, debug={"teleport": "kingdom_desert.isis_spot"},
        steps=REL + [("press", "cross"), ("until", "scene dk6_isis_pre", 300), ("wait", 90), ("snap", "isis")], expect=["scene dk6_isis_pre"]),
    "final6_mage": dict(desc="player view: the Desert Mage at the buried star", preset="40 Desert Mage (wager)", lang=1, debug={"teleport": "kingdom_desert.gate_spot"},
        steps=REL + [("press", "cross"), ("until", "scene dk6_mage_pre", 300), ("wait", 90), ("snap", "mage")], expect=["scene dk6_mage_pre"]),
    "final6_end": dict(desc="player view: chapter 6 complete, eight stars", preset="41 chapter 6 done", lang=1, debug={"teleport": "kingdom_desert.desert_center"},
        steps=REL + [("snap", "end"), ("press", "triangle", 5, 30), ("wait", 30), ("snap", "journal")], expect=["dev mode 0"]),
    "quick_gate_fair": dict(quick=True, desc="QUICK: fair arch refuses under 8 stars", preset="40 Desert Mage (wager)", lang=1,
        debug={"skip_dialogue": True, "stars": 7, "teleport": "kingdom_desert.fair_gate"},
        steps=[("wait", 40), ("press", "cross"), ("until", "scene dk6_gate_shut", 300), ("wait", 40), ("snap", "shut")],
        expect=["scene dk6_gate_shut"]),
})

FAIR_E2E = (beat("dk7_jono_pre", "jono_pre") + [("until", "scene dk7_jono_win", 1200), ("wait", 400), ("snap", "jono_won")]
    + beat("dk7_champ_pre", "champ_pre") + [("until", "star duel won", 1200), ("wait", 600), ("snap", "champ_won")]
    + beat("dk7_castle_road", "castle_road", after=200) + [("press", "triangle", 5, 30), ("wait", 30), ("snap", "journal")])
SCENARIOS.update({
    "e2e_ch6_to_ch7": dict(desc="chapter 6 -> 7: fair arch into the plaza, Jono, the Ring Champion, chapter 7 end",
        preset="41 chapter 6 done", lang=1, debug=dict(E2E, coins=300, teleport="kingdom_desert.fair_gate"),
        steps=beat("dk7_enter", "arch", after=100) + [("until", "journey: music 24", 900), ("until", "scene dk7_arrival", 900), ("wait", 400), ("snap", "fair")]
            + FAIR_E2E,
        expect=["scene dk7_enter", "journey: music 24", "scene dk7_arrival", "scene dk7_jono_win", "saved (stage 29",
                "star duel won, bet 1, stars 9", "saved (stage 30", "scene dk7_castle_road"]),
    "cap7_arrival": dict(quick=True, desc="chapter 7 opens: the fair, the arrival scene", preset="42 fair arrival (chapter 7)", lang=0, debug={"skip_dialogue": True},
        steps=[("until", "scene dk7_arrival", 600), ("wait", 200), ("snap", "fair")], expect=["scene dk7_arrival", "journey: music 24"]),
    "cap7_jono": dict(desc="Jono's friendly fair duel (win)", preset="43 Jono at the raft (friendly)", lang=0, debug=E2E,
        steps=beat("dk7_jono_pre", "jono_pre") + [("until", "scene dk7_jono_win", 900), ("wait", 400), ("snap", "won")], expect=["scene dk7_jono_win", "saved (stage 29"]),
    "cap7_champ": dict(quick=True, desc="the Ring Champion's one-star wager (win), chapter 7 end", preset="44 Ring Champion (wager)", lang=0,
        debug=dict(E2E, teleport="kingdom_fair.gate_spot"),
        steps=[("wait", 60), ("press", "cross"), ("until", "scene dk7_champ_pre", 600), ("wait", 100), ("snap", "champ_pre"),
               ("until", "star duel won", 1200), ("wait", 600), ("snap", "won")], expect=["scene dk7_champ_pre", "star duel won, bet 1, stars 9", "saved (stage 30"]),
    "cap7_champ_lose": dict(desc="Ring Champion wager lost: one star less, stays at the fair", preset="44 Ring Champion (wager)", lang=1,
        debug=dict(skip_dialogue=True, lose_duels=True, wager=1, teleport="kingdom_fair.gate_spot"),
        steps=[("wait", 60), ("press", "cross"), ("until", "scene dk7_champ_pre", 600), ("wait", 100), ("snap", "champ_pre"),
               ("until", "star duel lost", 1200), ("wait", 400), ("snap", "lost")],
        expect=["scene dk7_champ_pre", "star duel lost, bet 1, stars 7 (ring_champ holds 3)"], forbid=["GAME OVER", "kingdom_beach"]),
    "cap7_shop": dict(desc="Bazaar Bea's Grand Bazaar (fair shop)", preset="43 Jono at the raft (friendly)", lang=1,
        debug={"skip_dialogue": True, "coins": 900, "xp": 900, "teleport": "kingdom_fair.shop_stall"},
        steps=[("wait", 60), ("press", "cross"), ("wait", 200), ("press", "cross"), ("wait", 120), ("snap", "shop")], expect=[]),
    "cap7_arena": dict(desc="the Underfair Big Top (fair arena) with its exclusives", preset="43 Jono at the raft (friendly)", lang=1,
        debug={"skip_dialogue": True, "coins": 900, "xp": 900, "teleport": "kingdom_fair.arena_door"},
        steps=[("wait", 60), ("press", "cross"), ("wait", 120), ("press", "cross"), ("wait", 40), ("snap", "arena")], expect=[]),
    "cap7_camp": dict(quick=True, desc="fair camp warns that zero stars ends the journey", preset="43 Jono at the raft (friendly)", lang=1,
        debug={"skip_dialogue": True, "teleport": "kingdom_fair.fair_camp"},
        steps=[("wait", 40), ("press", "cross"), ("until", "scene dk7_fair_camp", 300), ("wait", 60), ("snap", "camp")], expect=["scene dk7_fair_camp"]),
    "final7_fair": dict(desc="player view: the Star Fair", preset="43 Jono at the raft (friendly)", lang=1, debug={"teleport": "kingdom_fair.fair_center"},
        steps=REL + [("snap", "fair")], expect=["dev mode 0"]),
    "final7_jono": dict(desc="player view: Jono at the raft", preset="43 Jono at the raft (friendly)", lang=1, debug={"teleport": "kingdom_fair.jono_spot"},
        steps=REL + [("press", "cross"), ("until", "scene dk7_jono_pre", 300), ("wait", 90), ("snap", "jono")], expect=["scene dk7_jono_pre"]),
    "final7_champ": dict(desc="player view: the Ring Champion at the ropes", preset="44 Ring Champion (wager)", lang=1, debug={"teleport": "kingdom_fair.gate_spot"},
        steps=REL + [("press", "cross"), ("until", "scene dk7_champ_pre", 300), ("wait", 90), ("snap", "champ")], expect=["scene dk7_champ_pre"]),
    "final7_end": dict(desc="player view: chapter 7 complete, nine stars", preset="45 chapter 7 done", lang=1, debug={"teleport": "kingdom_fair.fair_center"},
        steps=REL + [("snap", "end"), ("press", "triangle", 5, 30), ("wait", 30), ("snap", "journal")], expect=["dev mode 0"]),
    "quick_gate_castle": dict(quick=True, desc="QUICK: castle arch refuses under 9 stars", preset="44 Ring Champion (wager)", lang=1,
        debug={"skip_dialogue": True, "stars": 8, "teleport": "kingdom_fair.castle_gate"},
        steps=[("wait", 40), ("press", "cross"), ("until", "scene dk7_gate_shut", 300), ("wait", 40), ("snap", "shut")],
        expect=["scene dk7_gate_shut"]),
})

GATE_E2E = (beat("dk8_inseto_pre", "inseto_pre") + [("until", "star duel won", 1200), ("wait", 600), ("snap", "inseto_won")]
    + beat("dk8_castle_announce", "castle_announce", after=200) + [("press", "triangle", 5, 30), ("wait", 30), ("snap", "journal")])
SCENARIOS.update({
    "e2e_ch7_to_ch8": dict(desc="chapter 7 -> 8: castle road into the plaza, InsetoKaiba rematch, chapter 8 end",
        preset="45 chapter 7 done", lang=1, debug=dict(E2E, coins=300, teleport="kingdom_fair.castle_gate"),
        steps=beat("dk8_arrival", "arch", after=100) + [("until", "journey: music 51", 900), ("wait", 400), ("snap", "gate")]
            + GATE_E2E,
        expect=["scene dk8_arrival", "journey: music 51", "star duel won, bet 1, stars 10", "saved (stage 32", "scene dk8_castle_announce"]),
    "cap8_arrival": dict(quick=True, desc="chapter 8 opens: the castle gate plaza", preset="46 gate arrival (chapter 8)", lang=0, debug={"skip_dialogue": True},
        steps=[("until", "journey: music 51", 600), ("wait", 200), ("snap", "gate")], expect=["journey: music 51"]),
    "cap8_inseto": dict(quick=True, desc="InsetoKaiba gate rematch (win), chapter 8 end", preset="47 InsetoKaiba at the lock (wager)", lang=0,
        debug=dict(E2E, teleport="castle_gate.gate_spot"),
        steps=[("wait", 60), ("press", "cross"), ("until", "scene dk8_inseto_pre", 600), ("wait", 100), ("snap", "inseto_pre"),
               ("until", "star duel won", 1200), ("wait", 600), ("snap", "won")], expect=["scene dk8_inseto_pre", "star duel won, bet 1, stars 10", "saved (stage 32"]),
    "cap8_inseto_lose": dict(desc="InsetoKaiba wager lost: one star less, stays at the gate", preset="47 InsetoKaiba at the lock (wager)", lang=1,
        debug=dict(skip_dialogue=True, lose_duels=True, wager=1, teleport="castle_gate.gate_spot"),
        steps=[("wait", 60), ("press", "cross"), ("until", "scene dk8_inseto_pre", 600), ("wait", 100), ("snap", "inseto_pre"),
               ("until", "star duel lost", 1200), ("wait", 400), ("snap", "lost")],
        expect=["scene dk8_inseto_pre", "star duel lost, bet 1, stars 8 (inseto_gate holds 3)"], forbid=["GAME OVER", "kingdom_beach"]),
    "cap8_shop": dict(desc="Pawn Paul's Gate Pawn Stall", preset="47 InsetoKaiba at the lock (wager)", lang=1,
        debug={"skip_dialogue": True, "coins": 900, "xp": 900, "teleport": "castle_gate.shop_stall"},
        steps=[("wait", 60), ("press", "cross"), ("wait", 200), ("press", "cross"), ("wait", 120), ("snap", "shop")], expect=[]),
    "cap8_arena": dict(desc="the Moat Pit (gate arena) with its exclusives", preset="47 InsetoKaiba at the lock (wager)", lang=1,
        debug={"skip_dialogue": True, "coins": 900, "xp": 900, "teleport": "castle_gate.arena_door"},
        steps=[("wait", 60), ("press", "cross"), ("wait", 120), ("press", "cross"), ("wait", 40), ("snap", "arena")], expect=[]),
    "cap8_camp": dict(quick=True, desc="gate camp warns that zero stars ends the journey", preset="47 InsetoKaiba at the lock (wager)", lang=1,
        debug={"skip_dialogue": True, "teleport": "castle_gate.gate_camp"},
        steps=[("wait", 40), ("press", "cross"), ("until", "scene dk8_gate_camp", 300), ("wait", 60), ("snap", "camp")], expect=["scene dk8_gate_camp"]),

    "music_tension_wager": dict(
        desc="star wager opens the tension cue",
        preset="47 InsetoKaiba at the lock (wager)", lang=1,
        debug={"skip_dialogue": True, "teleport": "castle_gate.gate_spot"},
        steps=[("until", "journey: music 51", 600), ("wait", 30),
               ("press", ["cross"], 1, 20), ("until", "ask", 600),
               ("press", ["cross"], 1, 20), ("until", "journey: music cue tension_wager", 900),
               ("until", "journey: music 54", 900), ("snap", "wager")],
        expect=["journey: music cue tension_wager", "journey: music 54"]),
    "music_epic_heishin": dict(
        desc="Heishin pre-duel plays epic_heishin",
        preset="50 Heishin at the crown (wager)", lang=1,
        debug={"skip_dialogue": False, "teleport": "castle_hall.heishin_spot"},
        steps=[("until", "journey: music 52", 600), ("press", ["cross"], 1, 20),
               ("until", "scene dk9_heishin_pre", 900), ("until", "journey: music cue epic_heishin", 900),
               ("until", "journey: music 55", 900), ("snap", "heishin")],
        expect=["scene dk9_heishin_pre", "journey: music cue epic_heishin", "journey: music 55"]),
    "music_epic_festival": dict(
        desc="Festival epilogue plays epic_festival",
        preset="54 chapter 10 wish", lang=1,
        debug={"skip_dialogue": True, "teleport": "castle_top.wish_orbs"},
        steps=[("wait", 40), ("press", "cross"), ("until", "scene dk10_epilogue", 900),
               ("until", "journey: music cue epic_festival", 900),
               ("until", "journey: music 57", 900), ("snap", "festival")],
        expect=["scene dk10_epilogue", "journey: music cue epic_festival", "journey: music 57"]),

    "final8_gate": dict(desc="player view: the Castle Gate", preset="47 InsetoKaiba at the lock (wager)", lang=1, debug={"teleport": "castle_gate.gate_center"},
        steps=REL + [("snap", "gate")], expect=["dev mode 0"]),
    "final8_inseto": dict(desc="player view: InsetoKaiba at the star-lock", preset="47 InsetoKaiba at the lock (wager)", lang=1, debug={"teleport": "castle_gate.gate_spot"},
        steps=REL + [("press", "cross"), ("until", "scene dk8_inseto_pre", 300), ("wait", 90), ("snap", "inseto")], expect=["scene dk8_inseto_pre"]),
    "final8_end": dict(desc="player view: chapter 8 complete, ten stars", preset="48 chapter 8 done", lang=1, debug={"teleport": "castle_gate.gate_center"},
        steps=REL + [("snap", "end"), ("press", "triangle", 5, 30), ("wait", 30), ("snap", "journal")], expect=["dev mode 0"]),
    "quick_gate_dream": dict(quick=True, desc="QUICK: castle door announces Dream Room at 10 stars", preset="48 chapter 8 done", lang=1,
        debug={"skip_dialogue": True, "teleport": "castle_gate.castle_door"},
        steps=[("wait", 40), ("press", "cross"), ("until", "scene dk8_castle_announce", 300), ("wait", 40), ("snap", "announce")],
        expect=["scene dk8_castle_announce"]),
})

HALL_E2E = (beat("dk9_heishin_pre", "heishin_pre") + [("until", "star duel won", 1200), ("wait", 600), ("snap", "heishin_won")])
# dream_stairs at stage 34 enters the Dream Room (dk10_arrival) before dk9_dream_road; ch10 e2e covers that
DREAM_E2E = (beat("dk10_pegasus_pre", "pegasus_pre") + [("until", "star duel won", 1200), ("wait", 600), ("snap", "pegasus_won")]
    # epilogue is on wish_orbs (cap10_epilogue); e2e stops at the Pegasus win / stage 36
    )
SCENARIOS.update({
    "e2e_ch8_to_ch9": dict(desc="chapter 8 -> 9: castle door into the hall, Heishin, chapter 9 end",
        preset="48 chapter 8 done", lang=1, debug=dict(E2E, coins=300, teleport="castle_gate.castle_door"),
        steps=beat("dk9_arrival", "arch", after=100) + [("until", "journey: music 52", 900), ("wait", 400), ("snap", "hall")]
            + HALL_E2E,
        expect=["scene dk9_arrival", "journey: music 52", "star duel won, bet 1, stars 10", "saved (stage 34"]),
    "e2e_ch9_to_ch10": dict(desc="chapter 9 -> 10: dream stairs, Pegasus, Festival epilogue",
        preset="51 chapter 9 done", lang=1, debug=dict(E2E, coins=300, teleport="castle_hall.dream_stairs"),
        steps=beat("dk10_arrival", "stairs", after=100) + [("until", "journey: music 27", 900), ("wait", 400), ("snap", "dream")]
            + DREAM_E2E,
        expect=["scene dk10_arrival", "journey: music 27", "star duel won, bet 1, stars 10", "saved (stage 36"],),
    "cap9_arrival": dict(quick=True, desc="chapter 9 opens: Castle Hall", preset="49 hall arrival (chapter 9)", lang=0, debug={"skip_dialogue": True},
        steps=[("until", "journey: music 52", 600), ("wait", 200), ("snap", "hall")], expect=["journey: music 52"]),
    "cap9_heishin": dict(quick=True, desc="Heishin crown wager (win), chapter 9 end", preset="50 Heishin at the crown (wager)", lang=0,
        debug=dict(E2E, teleport="castle_hall.heishin_spot"),
        steps=[("wait", 60), ("press", "cross"), ("until", "scene dk9_heishin_pre", 600), ("wait", 100), ("snap", "pre"),
               ("until", "star duel won", 1200), ("wait", 600), ("snap", "won")], expect=["scene dk9_heishin_pre", "star duel won, bet 1, stars 10", "saved (stage 34"]),
    "cap9_shop": dict(desc="Relic Rhea's Relic Alcove", preset="50 Heishin at the crown (wager)", lang=1,
        debug={"skip_dialogue": True, "coins": 900, "xp": 900, "teleport": "castle_hall.shop_stall"},
        steps=[("wait", 60), ("press", "cross"), ("wait", 200), ("press", "cross"), ("wait", 120), ("snap", "shop")], expect=[]),
    "cap9_arena": dict(desc="Crown Cellar arena exclusives", preset="50 Heishin at the crown (wager)", lang=1,
        debug={"skip_dialogue": True, "coins": 900, "xp": 900, "teleport": "castle_hall.arena_door"},
        steps=[("wait", 60), ("press", "cross"), ("wait", 120), ("press", "cross"), ("wait", 40), ("snap", "arena")], expect=[]),
    "cap9_camp": dict(quick=True, desc="hall camp zero-star warning", preset="50 Heishin at the crown (wager)", lang=1,
        debug={"skip_dialogue": True, "teleport": "castle_hall.hall_camp"},
        steps=[("wait", 40), ("press", "cross"), ("until", "scene dk9_hall_camp", 300), ("wait", 60), ("snap", "camp")], expect=["scene dk9_hall_camp"]),
    "cap10_arrival": dict(quick=True, desc="chapter 10 opens: Dream Room", preset="52 dream arrival (chapter 10)", lang=0, debug={"skip_dialogue": True},
        steps=[("until", "journey: music 27", 600), ("wait", 200), ("snap", "dream")], expect=["journey: music 27"]),
    "cap10_pegasus": dict(quick=True, desc="Pegasus final wager (win)", preset="53 Pegasus at the table (wager)", lang=0,
        debug=dict(E2E, teleport="castle_top.pegasus_spot"),
        steps=[("wait", 60), ("press", "cross"), ("until", "scene dk10_pegasus_pre", 600), ("wait", 100), ("snap", "pre"),
               ("until", "star duel won", 1200), ("wait", 600), ("snap", "won")], expect=["scene dk10_pegasus_pre", "star duel won, bet 1, stars 10", "saved (stage 36"]),
    "cap10_epilogue": dict(quick=True, desc="Festival wish epilogue on the plaza", preset="54 chapter 10 wish", lang=1,
        debug={"skip_dialogue": True, "teleport": "castle_top.wish_orbs"},
        steps=[("wait", 40), ("press", "cross"), ("until", "scene dk10_epilogue", 600), ("wait", 200), ("snap", "epi")], expect=["scene dk10_epilogue", "saved (stage 37"]),
    "final9_hall": dict(desc="player view: Castle Hall", preset="50 Heishin at the crown (wager)", lang=1, debug={"teleport": "castle_hall.hall_center"},
        steps=REL + [("snap", "hall")], expect=["dev mode 0"]),
    "final9_heishin": dict(desc="player view: Heishin at the crown", preset="50 Heishin at the crown (wager)", lang=1, debug={"teleport": "castle_hall.heishin_spot"},
        steps=REL + [("press", "cross"), ("until", "scene dk9_heishin_pre", 300), ("wait", 90), ("snap", "heishin")], expect=["scene dk9_heishin_pre"]),
    "final10_dream": dict(desc="player view: Dream Room", preset="53 Pegasus at the table (wager)", lang=1, debug={"teleport": "castle_top.dream_center"},
        steps=REL + [("snap", "dream")], expect=["dev mode 0"]),
    "final10_pegasus": dict(desc="player view: Pegasus at the table", preset="53 Pegasus at the table (wager)", lang=1, debug={"teleport": "castle_top.pegasus_spot"},
        steps=REL + [("press", "cross"), ("until", "scene dk10_pegasus_pre", 300), ("wait", 90), ("snap", "pegasus")], expect=["scene dk10_pegasus_pre"]),
    "final10_end": dict(desc="player view: festival epilogue", preset="55 festival epilogue", lang=1, debug={"teleport": "plaza_center"},
        steps=REL + [("snap", "festival")], expect=["dev mode 0"]),
})
SCENARIOS.update({
    "feupys_drop": dict(slow=True, settings={"mod.ow-poc.feupys_drop_bp": "10000"}, desc="InsetoKaiba's real ship duel won by an attack: the Feupys drop roll (force it with MEMORIES_MOD_OW_POC_FEUPYS_DROP_BP=10000)",
        preset="17 on the ship (Mai, InsetoKaiba)", lang=1, debug={"teleport": "ship_deck.inseto_spot", "skip_dialogue": True, "flags": ["mai_met"]},
        steps=[("wait", 300), ("press", "cross"), ("mash", "duel against", 3000), ("wait", 300), ("snap", "duel"), ("duel_kill",), ("wait", 300), ("snap", "after"),
               ("mash", "scene dk1_inseto_win", 1500), ("wait", 900)] + [("press", "cross", 5, 60)] * 8 + [("wait", 300), ("snap", "won")] + REL + [("until", "feupys: restored", 1500), ("wait", 120), ("snap", "reloaded")],
        expect=["duel over, won", "feupys: InsetoKaiba", "feupys: restored 1 owned"]),
})
SCENARIOS.update({
    "feupys_deck_save": dict(desc="a Feupys card in the Journey deck survives a save and a cold restart", preset="17 on the ship (Mai, InsetoKaiba)", lang=1,
        debug={"skip_dialogue": True},
        steps=[("wait", 300), ("poke_deck", 0, 734)] + REL + [("until", "feupys: restored", 1500), ("wait", 120), ("check_deck", 0, 734), ("snap", "reloaded")],
        expect=["feupys: restored 0 owned, 1 in the deck"]),
})
SCENARIOS.update({
    "feupys_editor": dict(desc="the deck editor puts an owned Feupys card in the deck; it survives a save and a cold restart", preset="17 on the ship (Mai, InsetoKaiba)", lang=1, debug={"skip_dialogue": True},
        steps=[("wait", 300), ("poke_extra", 734, 2), ("press", "start", 5, 30), ("press", "cross", 5, 30), ("wait", 400), ("press", "right", 5, 60),
               ("press", "cross", 5, 60), ("snap", "removed"), ("press", "left", 5, 60), ] + [("press", "r2", 3, 3)] * 120 + [("wait", 60), ("snap", "chest_end"), ("press", "up", 5, 40), ("press", "cross", 5, 60), ("snap", "added"),
               ("press", "right", 5, 60), ("snap", "deck_after"), ("press", "circle", 5, 120), ("snap", "x_circle"), ("press", "select", 5, 120), ("snap", "x_select"), ("press", "cross", 5, 200), ("snap", "x_cross"), ("wait", 400), ("snap", "left_editor"), ("deck_has", 734)] + REL + [
               ("until", "feupys: restored", 1500), ("wait", 120), ("deck_has", 734), ("snap", "reloaded")],
        expect=["feupys: restored 1 owned, 1 in the deck"]),
})
SCENARIOS.update({
    "rival_village": dict(
        clean_hud=True, lang=1,
        desc="InsetoKaiba in the village: first talk opens with the catchphrase, a second talk in the same place is the short line, a reload (fresh arrival) greets again",
        preset="2 rumors heard (Simon next)", debug={"teleport": [720, 356]},
        steps=[("wait", 90), ("snap", "map"), ("press", "up", 3), ("wait", 10), ("press", "cross"), ("wait", 240), ("snap", "talk1_catchphrase")]
              + [("press", "cross", 3, 70)] * 16 + [("wait", 60), ("press", "cross"), ("wait", 200), ("snap", "talk2_repeat")] + [("press", "cross", 3, 70)] * 4
              + REL + [("wait", 120), ("press", "up", 3), ("wait", 10), ("press", "cross"), ("wait", 240), ("snap", "talk3_after_reload")],
        expect=[("scene rv_inseto_village_first", 2), ("scene rv_inseto_village (", 1)], forbid=["sprite page collision"]),
})
SCENARIOS.update({
    "rival_fair": dict(
        clean_hud=True, lang=1,
        desc="InsetoKaiba at the Star Fair: arrival catchphrase on the first talk, then his old taunt",
        preset="42 fair arrival (chapter 7)", debug={"teleport": [820, 526]},
        steps=[("wait", 90)] + [("press", "cross", 3, 45)] * 12 + [("wait", 60), ("snap", "map"), ("press", "up", 3), ("wait", 10), ("press", "cross"), ("wait", 200), ("snap", "talk1")]
              + [("press", "cross", 3, 70)] * 10 + [("wait", 60), ("press", "cross"), ("wait", 200), ("snap", "talk2")],
        expect=["scene rv_inseto_fair_first", "scene dk7_inseto_taunt"], forbid=["sprite page collision"]),
})
