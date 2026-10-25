# Testing Journey Mode: Duelist Kingdom, part 3

How to run and check the home-town arc up to part 3. The fast test loop (validator, `fast.sh`, scenario syntax, debug aid) is described in [`mods/ow-poc/tools/TESTING.md`](../mods/ow-poc/tools/TESTING.md); this page covers what part 3 adds.

You need your own legal copy of the USA disc (SLUS-01411). No game data is in this repository or in the release. Set `MEMORIES_DISC` to your disc image's `.bin` for the scripted runs, or pick it with "Choose ROM..." in the Windows build.

## Part 3 (test build)

After the Stamp Card (end of part 2) the story opens three quests that can be done in any order. Each gives one stamp (Lost / Won / Given). When all three glow, the guard lets you cross the bridge to the harbor; the harbor itself is part 4, so for now you get a "Quest complete" banner and the story ends at "Part 3 complete".

* **Quest 4, The Lost.** Win Kemet's lantern (part 2), walk to the little pyramid at the village edge and press X at the hatch. It opens onto the cistern, a new painted area (sandstone vault, water, torches, 320x180 map). A glyph on the wall brings the Mago.dev observer, who glitches away; then the ghost Bakura appears. Talk to him and duel him (deck "Yami Bakura"). Win: the Founder's Scarab and the Lost stamp. The stairs where you came in lead back out.
* **Quest 5, The Won.** Jono lost his bandana to Rex Raptor, who stands on the east road while this quest is open. Duel Rex (deck "Rex Raptor"), win Jono's Bandana and bring it back for the Won stamp.
* **Quest 6, The Given.** Teana wants honey (from Hakim the baker), river water (fill her jug at the river bank) and dates (shake the date palm). Bring them to her, win her duel (deck "Teana") and get the Lucky Charm and the Given stamp.

The yellow arrow and the objective bar follow the next task; the journal (A) lists the three quests and hides each when done. Banners (objective, item, stamp, quest complete) are separate from speech.

### Keys

Arrows walk, S runs, X talks or examines, A opens the journal, Right Shift the mini-map, ENTER the menu.

### Debug aid (off by default)

Rename `mods/ow-poc/debug.json.OFF` to `debug.json` (Windows package) or create `mods/ow-poc/debug.json` (`{}` is enough). Without that file no debug key does anything. You need a Journey save (NEW GAME, walk a few steps, ENTER > Save, then CONTINUE).

Hold R1 (W), then L1 (Q) and:

| Keys | Effect |
|---|---|
| Up / Down | next / previous story preset (the world is rebuilt) |
| Left | time of day: story decides > night > day |
| Right | teleport to the next named place |
| Square (Z) | skip dialogue on/off |
| Triangle (A) | win duels on/off (a duel counts as won, rewards included) |

Presets (`DEBUG_PRESETS` in `mods/ow-poc/tools/dk_to_journey.py`, written to `journey.json`): 1 home door, 2 rumors heard, 3 Simon won (bench next), 4 night / hooded man waits, 5 Stamp Card (Hakim next), 6 Hakim's hint (Kemet next), 7 Lantern won (hatch next), 8 in the cistern (Bakura), 9 Lost stamp (glyph, stairs), 10 Jono asked (Rex next), 11 Teana's errands, 12 errands done, 13 two stamps (Teana last). Presets 8 and 9 place you in the cistern. The debug file also accepts `preset`, `flags`, `stage`, `teleport`, `time`, `skip_dialogue` and `win_duels`. Progress made while debugging is saved with the normal save, so keep a copy of `journey.sav` first.

### Scripted checks

```
python3 mods/ow-poc/tools/validate_story.py
mods/ow-poc/tools/fast.sh --convert      # re-run the story converter, validate, build, deploy
mods/ow-poc/tools/fast.sh all            # every scenario, PASS/FAIL table
```

Part 3 scenarios: `dk_part3_hatch_locked`, `dk_part3_cistern`, `dk_part3_glyph`, `dk_part3_exit`, `dk_part3_rex`, `dk_part3_honey`, `dk_part3_water`, `dk_part3_dates`, `dk_part3_teana_end`, `dk_part3_journal_en`, `dk_part3_journal_pt`, `ui_banners_p3_en`, `ui_banners_p3_pt`. Scripted runs use Xvfb on display `:92`.

### Known limits (part 3)

* The duels with Rex, Bakura and Teana are real duels in the game, but the automated scenarios only check them with the debug "win duels" option; playing them for real is untested.
* The cistern is a painted picture with torch glow only (no animated water). Its collision map is hand-made, so a spot may differ from the picture by a few steps.
* The Bakura sprite is drawn with a dither, so the face is small and soft.
* Saving inside the cistern returns you to the hatch in the village when you continue.
* The Mago.dev glyph is drawn by code, not by a painted asset.
* The cistern song and the new sound effects were chosen by measurement, not by ear (`journey.json` `"painted": {"music": ...}`).
* The Windows executable has not been run by the author with part 3; the logic was checked on Linux (Xvfb) with the same mod object.
