# Testing Journey Mode fast

A story check used to mean replaying the story (minutes per try).  Now: a state is one name, a check is 15-40 s, the whole set about 5 minutes.
Everything runs under Xvfb (`:92`, never another display) on the box; nothing needs a person.

## One-line commands (run from the repo root, or anywhere: the scripts find the repo)

| What | Command |
|---|---|
| Validate the story JSON (no build) | `python3 mods/ow-poc/tools/validate_story.py` |
| Validate + build the mod + deploy into the game dir (with timing) | `mods/ow-poc/tools/fast.sh` |
| ...after changing the story source (re-runs `dk_to_journey.py`) | `mods/ow-poc/tools/fast.sh --convert` |
| ...then run named scenarios | `mods/ow-poc/tools/fast.sh dk_part2_bench village_roads` |
| Regression: every scenario, PASS/FAIL table | `mods/ow-poc/tools/fast.sh all`  (or `python3 mods/ow-poc/tools/smoke/jm_smoke.py all`) |
| List scenarios | `python3 mods/ow-poc/tools/smoke/jm_smoke.py list` |
| Run one scenario without building | `python3 mods/ow-poc/tools/smoke/jm_smoke.py run dk_part2_hooded_man` |

Output: `tmp/smoke/<scenario>/shots/NN_label.png`, `game.log`, and `tmp/smoke/results.json` (set `SMOKE_OUT` to move it).  Environment:
`SMOKE_DISPLAY` (default `:92`), `JM_GAME` (game dir, default `tmp/pc/game32`), `MEMORIES_DISC` (the disc image; default `../game/YUGIOH.bin`),
`SMOKE_SCALE` (internal_scale, default 1: about 170 fps, the shots are the same picture).

## The debug aid in the mod (jm_debug.c)

Off unless a file `debug.json` sits beside `mod.json` (`mods/ow-poc/debug.json`) or in the mod's data folder
(`<user dir>/mod-data/ow-poc/debug.json`).  Without it no key does anything and the release behaves as before.  The file may be `{}`.

```json
{ "preset": "4 night, hooded man waits",   // a state from journey.json "debug" (name or index), applied on Continue
  "flags": ["baker_hint"], "clear_flags": [], "stage": 3, "wins": 2,   // then these
  "teleport": "bakery_door",               // an anchor of the painted village, or [x, y] in picture texels
  "time": "night",                         // day | night | auto (auto: the story decides)
  "skip_dialogue": true,                   // pages turn by themselves, questions answer Yes
  "win_duels": true }                      // a duel is not played, it counts as won (the win result applies)
```

In the painted village, hold **R1 and L1** (R1 first, so the L1 press is not the old map's key):

| Keys | Effect |
|---|---|
| R1+L1+Up / Down | next / previous story preset (stage, flags, place, time; the world is rebuilt) |
| R1+L1+Left | time of day: auto > night > day |
| R1+L1+Right | teleport to the next anchor (hero_start, plaza_center, plaza_bench, house_ne_door, ...) |
| R1+L1+Square | skip dialogue on/off |
| R1+L1+Triangle | win duels on/off |

Presets live in `dk_to_journey.py` (`DEBUG_PRESETS`) and are written into journey.json (`"debug"`); add one per new quest stage.

## How a scenario works (smoke/scenarios.py)

The harness writes a minimal `journey.sav` and the scenario's `debug.json` into a private user dir (`MEMORIES_USER_DIR`), boots the game,
goes JOURNEY MODE > Continue, replays `steps`, and checks the log.

```python
"dk_part2_baker": dict(desc="...", preset="5 Stamp Card (Hakim next)", debug={"skip_dialogue": True}, lang=0,
    steps=[("snap","bakery"), ("press","cross"), ("until","scene dk1_baker",300), ("snap","talk"), ("until","saved (stage 3",1500)],
    expect=["scene dk1_baker", "saved (stage 3"])
```
Steps: `("wait", n)`, `("press", key or [keys], hold, after)`, `("until", log text, max frames)` (a timeout fails the scenario),
`("mash", log text, max frames)` (X every 40 frames: dialogue that is not skipped), `("snap", label)`.  `expect` = log lines that must appear
(`(line, n)` for n times); the log must never hold "no scene", "unknown flag", "Traceback"... (`FORBID` in jm_smoke.py, `forbid` per scenario).
Pad keys: up down left right cross circle square triangle l1 r1 l2 r2 start select.  Frames are VBlanks (60 per game second).

Scenarios now: painted_menu, painted_menu_deck, village_roads, dk_part2_bench, dk_part2_hooded_man, dk_part2_baker, dk_part2_kemet_duel, dk_part2_kemet_real_duel (experimental, not in `all`),
music_day_night, dk_part2_pt, ui_dialog_*, ui_ask_*, and for part 3 the `dk_part3_*` and `ui_banners_p3_*` scenarios (26 run by `all`, plus one experimental real-duel scenario; `python3 mods/ow-poc/tools/smoke/jm_smoke.py list` shows all). See `docs/TESTING.md` for part 3.  For a new part: add a preset, add 2-4 scenarios, run `fast.sh all`.

## Workflow for a new part

1. Write/extend `journey_content/<part>` and `dk_to_journey.py` (+ a preset per stage).
2. `fast.sh --convert` (validator fails on a missing scene, flag, anchor, sprite, a page count differing between en/pt, an objective list that
   does not match ui.json).  Fix until it is quiet.
3. `fast.sh <new scenario>` and look at the shots; then `fast.sh all` before a package.
4. Package: copy `ow-poc.o`, `mod.json`, `assets/` into the Windows folder (never ship a `debug.json` unless it is a debug build).

Limits: a real duel cannot be driven reliably by the harness yet (`duel_win` pokes the opponent's life points but the duel did not end in the last try), so scenarios use the debug `win_duels`; the real duel return was checked by hand-written scripts earlier.  The shots are of the Linux build (the Windows exe is the same code); the music is checked by log lines (`journey: music N`), not by
ear; the harness cannot judge a picture, so shots are looked at.
