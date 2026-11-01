"""Named smoke scenarios.  Each: desc, preset (journey.json "debug" name or number), debug (extra debug.json keys: flags, teleport, time,
skip_dialogue, win_duels), lang (0 en, 1 pt), steps (see jm_smoke.py), expect (log lines that must appear; (line, n) for n times)."""
MUSIC_DAY = "journey: music 10 (day)"
MUSIC_NIGHT = "journey: music 25 (night)"

SCENARIOS = {
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
                "observer mago", "scene dk2_landing", "scene dk2_mirror", "scene dk2_weevil_ambush", "star duel won, stars 2", "saved (stage 12",
                "scene dk2_hooded_shore", "scene dk2_camp", "scene dk3_enter", "journey: music 18", "journey: music 20", "journey: music 30"]),
    "e2e_weevil_lose": dict(desc="Weevil's wager lost with the last star: the Shore Camp, one star back, no game over; then the rematch is won",
        preset="20 Weevil waits (wager)", lang=1, debug=dict(skip_dialogue=True, lose_duels=True, stars=1),
        steps=beat("dk2_weevil_pre", "weevil_pre") + [("until", "star duel lost", 900), ("until", "scene k1_eliminated", 600), ("wait", 600), ("snap", "camp_wakeup")],
        expect=["star duel lost, stars 1 (eliminations 1)", "scene k1_eliminated"]),
    "e2e_gang_harbor": dict(desc="a Jackal ambush in the harbor (west end, away from the objective)", preset="14 harbor gate (Inspector)", lang=0,
        debug={"skip_dialogue": True, "win_duels": True, "coins": 300, "gang_ready": True, "teleport": "harbor.hangout_b"},
        steps=[("wait", 60), ("press", ["r1", "l1", "circle"], 4, 30)] + [s for i in range(8) for s in (("hold", "right", 25), ("hold", "left", 25))] + [("snap", "ambush"), ("press", "cross", 5, 30), ("press", "cross", 5, 30), ("until", "duel over", 900), ("wait", 200), ("snap", "after_ambush")], expect=["ambush won"]),
    "e2e_gang_ship": dict(desc="a Jackal ambush on the ship", preset="17 on the ship (Mai, InsetoKaiba)", lang=1,
        debug={"skip_dialogue": True, "win_duels": True, "coins": 300, "gang_ready": True, "teleport": "ship_deck.hangout_b"},
        steps=[("wait", 60), ("press", ["r1", "l1", "circle"], 4, 30)] + WALK[:16] + [("snap", "ambush"), ("press", "cross", 5, 30), ("press", "cross", 5, 30), ("until", "duel over", 900), ("wait", 200), ("snap", "after_ambush")], expect=["ambush won"]),
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
    "final_camp": dict(desc="player view: woken at the Shore Camp with one star after losing the last one", preset="20 Weevil waits (wager)", lang=1,
        debug={"skip_dialogue": True, "lose_duels": True, "stars": 1},
        steps=beat("dk2_weevil_pre", "pre") + [("until", "scene k1_eliminated", 900), ("wait", 900)] + REL + [("snap", "camp"),
               ("press", "cross"), ("until", "scene dk2_camp", 300), ("wait", 90), ("snap", "camp_talk")], expect=["scene dk2_camp", "dev mode 0"]),
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
        expect=["star duel won, stars 2", "scene dk3_enter", "journey: music 21", "scene dk3_arrival", "star duel won, stars 3", "scene dk3_mark_1", "scene dk3_mark_2",
                "scene dk3_mark_3", "scene dk3_clearing_open", "star duel won, stars 4", "saved (stage 16", "scene dk4_enter"]),
    "cap3_arrival": dict(desc="chapter 3 opens: the forest, the arrival scene", preset="22 forest arrival (chapter 3)", lang=0, debug={"skip_dialogue": True},
        steps=[("until", "scene dk3_arrival", 600), ("wait", 300), ("snap", "forest")], expect=["scene dk3_arrival", "journey: music 21"]),
    "cap3_rex": dict(desc="Rex's wager (win)", preset="23 Rex waits (wager)", lang=0, debug=E2E,
        steps=beat("dk3_rex_pre", "rex_pre") + [("until", "star duel won", 900), ("wait", 600), ("snap", "won")], expect=["star duel won, stars 3", "saved (stage 14"]),
    "cap3_rex_lose": dict(desc="Rex's wager lost: one star less", preset="23 Rex waits (wager)", lang=1, debug=dict(skip_dialogue=True, lose_duels=True),
        steps=beat("dk3_rex_pre", "rex_pre") + [("until", "star duel lost", 900), ("wait", 600), ("snap", "lost")], expect=["star duel lost, stars 1"]),
    "cap3_marks": dict(desc="the three Star Marks open the clearing", preset="24 Star Marks", lang=0, debug=E2E,
        steps=beat("dk3_mark_1", "mark1", after=300) + beat("dk3_mark_2", "mark2", after=300) + beat("dk3_mark_3", "mark3", after=100)
            + [("until", "scene dk3_clearing_open", 900), ("wait", 600), ("snap", "clearing")], expect=["scene dk3_clearing_open", "saved (stage 15"]),
    "cap3_mage": dict(desc="the Forest Mage's two-star wager (win), chapter 3 end", preset="26 Forest Mage (wager)", lang=0, debug=E2E,
        steps=beat("dk3_mage_pre", "mage_pre") + [("until", "star duel won", 900), ("wait", 900), ("snap", "won")], expect=["star duel won, stars 4", "saved (stage 16"]),
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
        expect=["scene dk4_enter", "journey: music 22", "scene dk4_arrival", "star duel won, stars 5", "scene dk4_mai_pre", "scene dk4_mai_win",
                "scene dk4_carver", "saved (stage 20", "star duel won, stars 6", "saved (stage 21", "scene dk4_castle_road"]),
    "cap4_arrival": dict(desc="chapter 4 opens: the pass, the arrival scene", preset="28 mountain arrival (chapter 4)", lang=0, debug={"skip_dialogue": True},
        steps=[("until", "scene dk4_arrival", 600), ("wait", 300), ("snap", "mountain")], expect=["scene dk4_arrival", "journey: music 22"]),
    "cap4_keith": dict(desc="Keith's Double or Nothing (win: +2)", preset="29 Keith's toll (wager)", lang=0, debug=E2E,
        steps=beat("dk4_keith_pre", "keith_pre") + [("until", "star duel won", 900), ("wait", 600), ("snap", "won")], expect=["star duel won, stars 5", "saved (stage 18"]),
    "cap4_keith_lose": dict(desc="Keith's toll lost with the last star: wake at the mountain's trail camp, not the beach", preset="29 Keith's toll (wager)", lang=1,
        debug=dict(skip_dialogue=True, lose_duels=True, stars=1),
        steps=beat("dk4_keith_pre", "keith_pre") + [("until", "star duel lost", 900), ("until", "scene k3_eliminated", 600), ("wait", 600), ("snap", "trail_camp")],
        expect=["star duel lost, stars 1", "scene k3_eliminated"]),
    "cap4_forest_lose": dict(desc="Rex's wager lost with the last star: wake at the forest's trail camp (the chapter 3 gap)", preset="23 Rex waits (wager)", lang=1,
        debug=dict(skip_dialogue=True, lose_duels=True, stars=1),
        steps=beat("dk3_rex_pre", "rex_pre") + [("until", "star duel lost", 900), ("until", "scene k3_eliminated", 600), ("wait", 600), ("snap", "trail_camp")],
        expect=["star duel lost, stars 1", "scene k3_eliminated"]),
    "cap4_mai": dict(desc="Mai's pride duel (win, no star)", preset="30 Mai across the bridge (pride duel)", lang=0, debug=E2E,
        steps=beat("dk4_mai_pre", "mai_pre") + [("until", "scene dk4_mai_win", 900), ("wait", 600), ("snap", "won")], expect=["scene dk4_mai_win", "saved (stage 19"], forbid=["star duel"]),
    "cap4_carver": dict(desc="the star-carver in the cave", preset="31 the star-carver's cave", lang=0, debug=E2E,
        steps=beat("dk4_carver", "carver", after=600), expect=["scene dk4_carver", "saved (stage 20"]),
    "cap4_mage": dict(desc="the Mountain Mage's two-star wager (win), chapter 4 end", preset="32 Mountain Mage (wager)", lang=0, debug=E2E,
        steps=beat("dk4_mage_pre", "mage_pre") + [("until", "star duel won", 900), ("wait", 900), ("snap", "won")], expect=["star duel won, stars 6", "saved (stage 21"]),
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
    "stars_mage_short": dict(desc="the Mountain Mage refuses a duelist under five stars", preset="32 Mountain Mage (wager)", lang=1,
        debug={"skip_dialogue": True, "stars": 4, "teleport": "kingdom_mountain.gate_spot"},
        steps=[("wait", 60), ("press", "cross"), ("until", "scene dk4_mage_short", 300), ("wait", 60), ("snap", "refused")], expect=["scene dk4_mage_short"], forbid=["scene dk4_mage_pre"]),
    "stars_keith_short": dict(desc="Keith turns away a duelist under four stars", preset="29 Keith's toll (wager)", lang=1,
        debug={"skip_dialogue": True, "stars": 3, "teleport": "kingdom_mountain.keith_spot"},
        steps=[("wait", 60), ("press", "cross"), ("until", "scene dk4_keith_short", 300), ("wait", 60), ("snap", "refused")], expect=["scene dk4_keith_short"], forbid=["scene dk4_keith_pre"]),
    "stars_forest_mage_short": dict(desc="the Forest Mage refuses a duelist under three stars", preset="26 Forest Mage (wager)", lang=1,
        debug={"skip_dialogue": True, "stars": 2, "teleport": "kingdom_forest.gate_spot"},
        steps=[("wait", 60), ("press", "cross"), ("until", "scene dk3_mage_short", 300), ("wait", 60), ("snap", "refused")], expect=["scene dk3_mage_short"], forbid=["scene dk3_mage_pre"]),
    "stars_pass_short": dict(desc="the mountain pass stays shut under four stars", preset="27 chapter 3 done", lang=1,
        debug={"skip_dialogue": True, "stars": 3, "teleport": "kingdom_forest.pass_road"},
        steps=[("wait", 60), ("press", "cross"), ("until", "scene dk3_pass_locked", 300), ("wait", 60), ("snap", "pass_shut")], expect=["scene dk3_pass_locked"], forbid=["scene dk4_enter"]),
    "stars_owed": dict(desc="a lost wager leaves the star with the Forest Mage: he still accepts the rematch (owed 1)", preset="26 Forest Mage (wager)", lang=1,
        debug=dict(skip_dialogue=True, lose_duels=True),
        steps=beat("dk3_mage_pre", "mage_pre") + [("until", "star duel lost", 900), ("wait", 600), ("press", "cross"), ("wait", 200), ("snap", "rematch_offer")],
        expect=["star duel lost, stars 2 (eliminations 0, owed 1)", ("scene dk3_mage_pre", 2)], forbid=["scene dk3_mage_short"]),
    "stars_bag": dict(desc="player view: the Mochila shows the Star Chips with their count and text", preset="33 chapter 4 done", lang=1, debug={"teleport": "kingdom_mountain.hangout_a"},
        steps=REL + [("press", "start", 5, 30), ("press", "down", 5, 14), ("press", "cross", 5, 30), ("wait", 20)] + [("press", "right", 5, 10)] * 20 + [("wait", 20), ("snap", "bag_stars"), ("press", "cross", 5, 30), ("wait", 20), ("snap", "star_details")], expect=["dev mode 0"]),
})
