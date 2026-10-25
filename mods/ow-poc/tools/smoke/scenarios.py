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
               ("until", "scene dk1_treasures_done", 2500), ("until", "scene dk_part3_end", 2500), ("wait", 120), ("snap", "part_end"), ("until", "saved (stage 4", 2500), ("wait", 120), ("snap", "village_end"),
               ("press", "triangle"), ("wait", 30), ("snap", "journal")],
        expect=["scene dk1_teana_pre", "debug: duel against Teana", "scene dk1_teana_win", "scene dk1_treasures_done", "scene dk_part3_end", "saved (stage 4"]),
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
        expect=["scene dk1_teana_win", "scene dk_part3_end"]),
    "ui_banners_p3_pt": dict(
        desc="banners of part 3 (PT): Teana's win scene - item banner with the Lucky Charm icon, stamp banner, the three stamps, complete",
        preset="13 two stamps (Teana last)", debug={"win_duels": True}, lang=1,
        steps=[("press", "cross"), ("until", "scene dk1_teana_pre", 300), ("mash", "debug: duel against Teana", 1500), ("until", "page dk1_teana_win 0", 600), ("wait", 150), ("snap", "win_speech"),
               ("mash", "page dk1_teana_win 3 kind 2", 2500), ("wait", 6), ("snap", "banner_item_anim"), ("wait", 60), ("snap", "banner_item"),
               ("mash", "page dk1_teana_win 4 kind 2", 600), ("wait", 60), ("snap", "banner_stamp"),
               ("mash", "page dk1_treasures_done 0", 600), ("wait", 150), ("snap", "all_stamps"),
               ("mash", "page dk1_treasures_done 2 kind 1", 2500), ("wait", 60), ("snap", "banner_objective"),
               ("mash", "page dk_part3_end 0 kind 3", 1500), ("wait", 70), ("snap", "banner_complete")],
        expect=["scene dk1_teana_win", "scene dk_part3_end"]),
})
