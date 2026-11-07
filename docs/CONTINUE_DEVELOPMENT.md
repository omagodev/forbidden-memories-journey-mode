<p align="right"><a href="CONTINUE_DEVELOPMENT.pt-BR.md"><img src="https://img.shields.io/badge/Ler_em_Portugu%C3%AAs-009c3b?style=for-the-badge&logo=data%3Aimage%2Fpng%3Bbase64%2CiVBORw0KGgoAAAANSUhEUgAAACgAAAAoCAYAAACM%2FrhtAAADvklEQVR42u2XXUybZRiGr1L8aC20YAt2UEopLHR2n4oHQDJnPDAx2zTMEzMzMCNqPHDJDvyJB4uZzMREs83FJYsJCyQzUZPFv2Qsi1M3DQaDBG0lQlbKaKE0%2FJT%2BUGg%2FWuYBaZNKyzoGAbX32fe97%2Fvkzv28z%2F08L%2BSQQw7%2Fbsg49%2BTt7Uwwb7sr%2BP8i2FgYoLEwsP0IquUxThsd9FoH6LUOcNroQC2PbY8i2V88yyfVwxgEKeX%2FuCTw6mgd3X7t1ihoFBbpNA9xuc6%2BihyAQZC4XGen0zx0T2quS8GXyiY5ZRxBI48RCiu4eGUPdkc5Q7f0AFhMXsRaD637eihSRZiJ3cfbbjMXpnZsLkGjsMinNUPsVa8UQs%2FvtbR3NDM1p067v6wkyDsvf8OeRx0A%2FBzU0DJiwSUpsyYoZ7%2FpRDYbj1eMcWnnIGZFJEnu6IethCMFGc%2BEIwV0%2F%2FIIYs04Rr2PqoIorz3oAZmMn0LFG3MHGwsD2MQ%2BThpGEfJWxA6FFbR3NGetQntHM6GwAgAh7zYnDaPYxL6sLCljitXyGGerHBwp9a5auzT6JlpLK7pSFTtUWn5w%2FkFpXgkLnjg%2FXhvktxtuyo3F%2FGWfSp55o%2BUKh%2Ff1rorVNa3n2FgtwXh%2BWoL5d2MdCTj7Inz5RQ%2BOoRkASnRKtDoV5dVF1DbpaGipRBtScuGj%2FiRJm6OSw6wmeKTUy1MaX0ZLSlHQKCxytmqEgw%2FMrCn700dfz1gYACazmprdpTS0VOJzLPLVx39CZJKr506tGfdrn45jYzUpRbQuH5Riqcc0GiHl%2B5YzyPffjvD%2B89cJumO8d%2FFZxL316%2FLBlBS7JCXP3dx9xxRbTF684ceYcM%2BztLRMICAllUsQTOCz8%2F3cHJjm0CvWjCTW6jppFez2a7HaGuia1qcNKNZ6mJuNsLS0zC6xLPl%2Fwj2fQi5B2jU2y8h3H6SN1TWtx2pryNgSM6Y4GM%2BnzWmhabAe%2B4IqZe3gE%2F3Iln0AeFz%2BpHIVlYWYzOpkyk1mNbqyYu5Xynmm8VpKDPuCiqbBetqclowVnJVRT0gKzk9VEEfG44UB5DIoUkWo0vu42isSjcbxz0UB8M9F8c9FiUbj7BLLmPbOM%2B7yc%2FzFTh7eOb5yf5dlnJio5gXHQ0xIiq1tdcbKJd469Pk9tbr%2F1rDwTzXfNYyl7TR30yk2bR50SUranBYODIuMS0Ja6zgwLN6xCDZ95E9Y0plJQ7IIzkwa1rSOLXsXJ6aTX%2Bc1G%2FZoymcDsZHEcg%2F3HHLIIYcV%2FA2BwaA%2BPOkCagAAAABJRU5ErkJggg%3D%3D" alt="🇧🇷 Ler em Português (BR)"></a></p>

# Continuing Journey Mode development (outside the original workspace)

This file is the hand-off: what exists, what to install, how to build, run and test, and what to do next.
Written 2026-10-25. Commands below are copied from scripts in this repository; **nothing was re-run when this file was written**
(the hand-off was done without a test pass), so treat "Not verified" notes as real.

## 1. What this project is

Journey Mode is a story / open-world mode for Yu-Gi-Oh! Forbidden Memories. It is a C code mod (`mods/ow-poc`) that runs on the native PC port
"FM Recompiled" (MIT-licensed port code, SDL3 + OpenGL + a CPU rasteriser that emulates the PS1 GPU). The mod adds an illustrated 2D world
(1280x720 illustrated backgrounds + 48x62 character sprites), dialogue, quests, duels with a deck per duelist, a save file and a character creator.

You need your **own legal USA disc image (SLUS-01411)**. No game data is in this repository and none must ever be committed.

### Current state (parts delivered)
| Part | Content | Status |
|---|---|---|
| 1-2 | Illustrated home town, NPC sprites, Duelist Kingdom story quests 1-3, music, roads | delivered, tested by the author on Windows |
| 2b/2c | Menu fixes, debug option, dialogue UI (yellow speaker name + colon in the text box, banners, Yes/No panel) | delivered |
| 3 | Cistern, Bakura ghost duel, Rex Raptor / Jono's bandana, Teana's errands + duel (quests 4-6), Mago.dev glyph observer | built, 26 smoke scenarios passed on Linux; **the Windows exe was never run by the author for part 3+** |
| 3b | Small action hint (X button pill) instead of the big bar; "Dev mode" ON/OFF in the START menu | built |
| 3c | START menu box as wide as its longest row (language text no longer leaks) | built |
| 4a | NEW GAME character creator with a hero assembled live from sprite layers (skin, outfit, hair, accessory + colours) | built, 37/37 smoke scenarios on Linux |
| 5a (economy phase 1) | coins, XP/level, shop | **NOT implemented.** Design + data only (section 8). The helper doing it stopped for lack of usage; no code was written. |

The story ends at "Part 3 complete" (end of the home-town arc). The harbor, ship, Kingdom chapters 2-10 and their art are not made.

## 2. Repository layout
- `src/`, `tools/pc/`, `config/`, `Makefile`, `CMakeLists.txt`, `play.sh`, `play.bat`, `build-pc.sh`: the FM Recompiled port (upstream code; see CREDITS.md).
- `mods/ow-poc/`: **the Journey Mode mod.**
  - `ow_poc.c` entry; `jm_painted.c` illustrated-world engine (maps, sprites, collision, NPCs, areas); `jm_ui.c` menus/dialogue/banners; `jm_lang.c`; `jm_save.c`; `jm_debug.c`; `jm_chargen.c` character creator; `jm.h`.
  - `assets/` baked data (maps `painted*.raw`, `painted_col.bin`, sprites `spr_*.bin`, props, `chargen/`, `lang/`, `journey.json` = generated story).
  - `ow-poc.o` the prebuilt 32-bit mod object (rebuild it after any `.c` change).
  - `mod.json`, `debug.json.OFF` (rename to `debug.json` to enable the debug aid).
  - `tools/`: converter, validator, baking scripts, `fast.sh`, `smoke/` (scenario harness), `TESTING.md`, `CHARGEN_FORMAT.md`.
- `journey_content/`: story data. `duelist_kingdom/` is the main story (EN in `en/`, PT in `pt/`, ASCII only, `src/` generators, `tools/check_dk.py`). Top-level files are the old story kept as backup. `economy/` is the shops/money/levels/gang/arenas design and data (not wired yet).
- `art_dk/`: art sources and bake tools (backgrounds, masks, occluders, sprites, portraits, `chargen/` layer generators, `part3/`). Large intermediates (`raw/` generations, `village_roads/out`, `variants`, `previews`) are **not** in the repo. Private reference photos are never in the repo.
- `docs/TESTING.md`: the part 3 test notes; `notes/`: port documentation (`notes/journey-mode.md` has the mod design).

## 3. Setup on a new machine
Prerequisites (from `play.sh` / `play.bat`): `python3`, plus on Linux `gcc ld objcopy nm readelf objdump`
(`sudo apt install gcc python3` on Debian/Ubuntu). On Windows `play.bat` downloads a private Python, compiler, CMake and Ninja into `tmp\` on first run.
For the art/bake scripts: `pip install numpy pillow` (and `scipy` for some art tools; the `village_roads` scripts used a venv).
The first build fetches Linux libs, SDL3 and llvm-mingw into `tmp/pc` (a few minutes, needs internet).

1. `git clone https://github.com/omagodev/forbidden-memories-journey-mode && cd forbidden-memories-journey-mode`
2. Put your USA disc `.bin` in `game/` (any name ending in `.bin`). Never commit it (`game/` is for your copy only).
3. Linux: `./play.sh` (builds and runs the Linux game, Windows cross-build skipped). Full build including the Windows exe: `./build-pc.sh` (needs llvm-mingw, fetched by `tools/pc/build_win32_deps.py`).
   Windows: `play.bat`. macOS: `./build-pc.sh` (ARM64 source build). Executables land in `tmp/pc/game32/memories-pc` (Linux) and `tmp/pc/win32/memories-pc.exe` (Windows).
4. Mod object: `python3 tools/pc/build_mod.py --target i386 mods/ow-poc` builds `mods/ow-poc/ow-poc.o` (i386 object; works for both the Linux and Windows games).
5. Deploy the mod into the game folder: copy `ow-poc.o`, `mod.json` and `assets/` to `tmp/pc/game32/mods/ow-poc/` - `mods/ow-poc/tools/fast.sh` does validate + build + deploy in one go.

Not verified: that a fresh clone builds end to end on a clean machine (it did in the author's workspace, where `tmp/pc` was already populated).

## 4. Fast edit-test loop (author's workflow)
Read `mods/ow-poc/tools/TESTING.md` (full detail). Essentials, run from the repo root:
- `python3 mods/ow-poc/tools/validate_story.py` : validate story JSON, no build.
- `mods/ow-poc/tools/fast.sh` : validate + build + deploy (about 1.5 s). `--convert` re-runs `dk_to_journey.py` first (story JSON in `journey_content/` -> runtime `journey.json`).
- `mods/ow-poc/tools/fast.sh all` : every smoke scenario (several minutes). `python3 mods/ow-poc/tools/smoke/jm_smoke.py list|run <name>` for one.
- The harness uses Xvfb on display `:92` (Linux). On Windows run it in WSL, or skip it and play with `debug.json`.
- Debug aid: rename `mods/ow-poc/debug.json.OFF` to `debug.json` (never ship it). Hold R1 (W key) then L1 (Q key) + Up/Down = story preset, Left = time of day, Right = next anchor, Square = skip dialogue, Triangle = win duels. `debug.json` fields are documented in TESTING.md (`preset`, `flags`, `stage`, `teleport`, `time`, `skip_dialogue`, `win_duels`, `look`).
- Limits: the harness cannot reliably play a real duel to its end, so scenarios use `win_duels`.

## 5. Game keys (release)
Arrows walk, S (Circle) run, X (Cross) talk/examine, A (Triangle) journal, Right Shift (Select) minimap, Enter (Start) main menu (items, deck editor, status, save, language, Dev mode, back to title), E (L2) water, R (R2) trees. Developers only: with an active `debug.json`, a Dev mode row appears in the START menu and toggles the mod's top info line (kept in `devmode.cfg`). Without `debug.json` (every player build) the row is hidden and the bar can't be turned on.

## 6. Authoring content and art
- **Story:** edit `journey_content/duelist_kingdom/src/dk_*.py` / the EN and PT JSON, run `fast.sh --convert` (the converter `mods/ow-poc/tools/dk_to_journey.py` -> `journey.json`; add one debug preset per new quest stage in `DEBUG_PRESETS`). Check with `journey_content/duelist_kingdom/tools/check_dk.py` and `validate_story.py`. Flags: 30 of 32 used, so new state should be save counters, not flags. PT text is ASCII only (retail font).
- **Illustrated-map pipeline constraints:** 1280x720 backgrounds tiled into 128x128 quads; occluder cutouts depth-sorted by base-line Y; collision grid 160x90 (8-texel cells); texel value 0 is the only transparency (no alpha); RGB555; nearest-neighbour. Texture banks 1-15 are shared with duels (which use 1-12), so banks reload on every entry: palms 1,2,3,7,12; water 4-6; picture 8-11; atlas 14; sprites bank 13 (pages: kenney 0-1, player 2, ai 3, simon 4, teana 5, jono 6, guard 7) and bank 15 (pages 6-7 Rex/Bakura; the rest free).
- **Sprites:** 48x62 texels, 4 directions, idle + 4-step walk, 1px outline. Bake scripts: `art_dk/tools/bake_dk.py`, `bake_npcs.py`, `bake_sprites.py`, `art_dk/part3/tools/bake_p3.py`, and `mods/ow-poc/tools/bake_ai.py`, `build_part3_assets.py` (default art path inside it is the old workspace path: pass your `art_dk` folder as argument 1).
- **Character creator layers:** generated procedurally by `art_dk/chargen/tools/` (`python3 tools/build.py && python3 tools/make_previews.py && python3 tools/verify.py` inside `art_dk/chargen`), then `python3 mods/ow-poc/tools/import_chargen.py` copies manifest + packed layers into `mods/ow-poc/assets/chargen/`. Format: `mods/ow-poc/tools/CHARGEN_FORMAT.md`. Avoided pairs: spiky+cap, hood_down+scarf, long+scarf.
- Some scripts still contain old absolute defaults like `/workspace/study/fmrecomp/...`; override them with the script argument or edit the constant.
- Not verified: that every baking script runs unchanged outside the original workspace.

## 7. Save format
`journey.sav` is at save version 4 (hero look `Journey.cg[8]` from the creator, stage, flags, place, time). Older saves load with the old hero. The economy design wants a 52-byte block appended (coins, XP, ambush timers, arena progress); the loader zero-fills a shorter file. Dev mode lives in a separate `devmode.cfg` in the mod data folder.

## 8. Next: economy (phases) - the user's request, design done, code not started
Design and machine-readable data are in `journey_content/economy/` (`DESIGN.md`, `README.md` with the engine work list and sizes, `economy.json`, `shops.json`, `card_pools.json`, `gang.json`, `arenas.json`, `levels.json`, `decks_economy.json`, `card_rarity.json`, EN/PT text, generators in `src/`, `validate_economy.py`). Regenerate with `python3 src/gen_economy.py && python3 validate_economy.py` inside that folder.
User requirements: a shop in every town (money), card drops only from the local pool, a difficulty curve, a duelist gang that ambushes the player at a set frequency, can't be fled, and takes money when it wins, clandestine arenas per location to farm local cards and level up.
- **Phase 1 (do first):** save fields for coins/XP, money notices in the existing banner style, duel rewards (coins/XP) and local-pool drops, level from XP, the village shop (shopkeeper NPC via `place_npc`, buy/sell screen sized to fit its box, stock unlocked at stage 3). Use the real card-collection mechanism already used for rewards (`give_item`/card reward code in the mod).
- **Phase 2:** the "Dune Jackals" ambush gang (75-150 s of walking between ambushes, only on roads/fields, no ambush in quests/shops/dialogue/first minutes, "AMBUSH!" banner, no walk/run/menu and the duel can't be quit, loss steals a percentage with min/max and never below 0, no game over).
- **Phase 3:** the 8 hidden arenas (4-rung ladders, entry fee, first-clear bonus, reruns drop local cards, XP).
- Needs ~38 new duelist slots (decks are tied to duelist slots; fallback in `economy/README.md`: 12 shared fighters + 8 champions).
- Check equip/field-card matches in the pools with the FM Editor before shipping.

## 9. Windows package (how the author's zips were made)
A package is a folder with: `memories-pc.exe` + `SDL3.dll` (from `tmp/pc/win32/` after `build-pc.sh`), `languages/`, `LICENSE`, `game/README.txt` (an empty `game` folder for the user's disc), `mods/` (the stock mods plus `mods/ow-poc` containing only `ow-poc.o`, `mod.json` and `assets/`; since v0.5.2-alpha the package no longer ships `debug.json.OFF`), `JOGAR_JourneyMode.bat` (sets `MEMORIES_HD_TEXT=1` and, since v0.6.17, `MEMORIES_DEFAULT_INTERNAL_SCALE=2`, then starts `memories-pc.exe`), and README files. The Windows exe was unchanged from part 2c until v0.6.17 (settings.c: the launcher default internal scale), otherwise only `ow-poc.o`, `mod.json` and `assets/` change between packages. Never ship a disc image or an active `debug.json`. There is no script in the repo that zips this; the author's workspace did it by hand.

## 10. Known limits / TODO
- Windows exe not verified for parts 3 to 4a; the Linux harness is the only automated test.
- Duels with Rex, Bakura and Teana tested only with debug auto-win; music (song 10 day, 25 night, 26 cistern) and new sound effects chosen by measurement, not by ear.
- Part 3: the cistern has torch glow but no animated water, hand-made collision may not match the picture, the Bakura face is small (dithered); saving in the cistern returns to the hatch on Continue; the glyph is drawn by code.
- Chargen: one body shape and one face; only the hero is layered; the journal shows the portrait.
- Mago.dev has no portrait/dialogue wired into the game yet. Story chapters 2-10 and their art are not made; the "stay" ending and the Nitemare flake are untested.
- PT accents need a font change (retail font is ASCII only). Menu title localisation of the JOURNEY MODE button is open.
- A GitHub release has not been published (open question: the package's `languages/*.txt` files were read from PAL discs by the port).

## 11. Conventions, credits, licensing
- Commits: English, `Area: terse description`, then a `Tested:` paragraph stating only what was verified.
- Credits: see `CREDITS.md` (FM Recompiled MIT port, memories-decomp declares no license, Kenney, Quaternius, heyheythere, QuickJS). Painted maps, sprites and portraits are AI-assisted original art; characters are inspired by Forbidden Memories and are not official art; "InsetoKaiba" is a stylized parody with no real name or likeness; Mago.dev is the author's own character. No private reference photo may be committed.

## 12. First 30 minutes checklist
1. Clone, put your disc `.bin` in `game/`, run `./play.sh` (Linux) or `play.bat` (Windows) once so `tmp/pc` fills.
2. `python3 mods/ow-poc/tools/validate_story.py`, then `mods/ow-poc/tools/fast.sh` to confirm build + deploy work.
3. Rename `mods/ow-poc/debug.json.OFF` to `debug.json`, start the game, JOURNEY MODE > Continue, hold R1+L1 and press Up to jump between story stages.
4. Read `journey_content/economy/README.md` and start phase 1 in `jm_save.c` (save block), `jm_ui.c` (banners/menu), `jm_painted.c` (shop NPC, effects).

### Fast tests

Use `python3 mods/ow-poc/tools/smoke/fast.py` for the preset table and `mods/ow-poc/tools/fast.sh --quick` for the critical-path smoke (gates, star wager, chapter jumps). Full `fast.sh all` stays for release. Details: [`mods/ow-poc/tools/TESTING.md`](../mods/ow-poc/tools/TESTING.md).


### v0.6.11: Journey deck/inventory isolation

`journey.sav` version 8 now stores the run's 40-card deck, 722 trunk counts and
performance starchips. New journeys clear the classic trunk; editor return saves
these fields with the story. Classic deck slots (including F6 and the pre-duel
picker) are disabled for the entire mod session, not just while walking.
This change needs the rebuilt game executable as well as the rebuilt mod.

Versions 1–7 never stored deck/trunk/starchips in `journey.sav`. Migration keeps
story/economy progress but reconstructs cards from the weak starter and recorded
story rewards only; old unrecorded drops, purchases and deck arrangements cannot
be reliably recovered from a shared classic save. Do not import the current
classic deck as a migration shortcut. Modern loads preserve exact quantities
and do not re-grant sold story rewards.

Regression (isolated user directory; classic slots enabled and seeded):

```sh
python3 mods/ow-poc/tools/smoke/deck_inventory.py
python3 mods/ow-poc/tools/smoke/jm_smoke.py run painted_menu_deck cap2_starter_deck
```
