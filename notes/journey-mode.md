# Journey Mode

Journey Mode is a story mode: a walkable 3D world with people to talk to,
duels against them, and a save of how far you got. It is a **code mod**
(`mods/ow-poc`, one i386 object plus assets) that uses the mod API and the
mode slot of `src/pc/platform/mod_mode.[ch]`; no game file is changed.
The mod's folder keeps its first name (`ow-poc`, from "open world") so that
settings and saves of the proof of concept keep working.

## How it runs

1. `mod.json` adds a title button, `JOURNEY MODE`, under LOAD
   (`"action": "event"`). The button raises `MEMORIES_EVENT_MENU`; the mod
   answers with its own selection id, and `MEMORIES_EVENT_SCENE` (before)
   hands the screen to `ModMode_Enter` (see `notes/modding.md`, "Game
   modes").
2. `ModMode` runs the mod's `run(first)` once per frame in the tower's
   main-mode slot (13) while the tower is off. `first` is 1 on every
   entry, including a return from a duel, the name entry or the deck
   editor, so the mod keeps a small "what I was doing" variable
   (`after_return` in `ow_poc.c`).
3. Each frame the mod's frame hook sorts the picture into the ordering
   table (`jm_gfx.c`): the world is projected by the mod's own float
   camera (45 degrees down, follows the player), not by the GTE. Polygons are
   Gouraud triangles (characters, props, walls), textured Gouraud quads
   (ground, plants, portraits) and a gradient backdrop. The sorted
   scene is in one ordering table slot (`ot_count - 8`) below the game's
   text box.
4. Text: dialogue is the game's own text box (`Tower_CreateBox`, string id
   `0xFFF7`, text from `ModMode_SetText`), with the speaker's portrait
   drawn above it; HUD, creation and the START menu use the overlay API
   (`overlay_size/draw_text/fill`), which is cropped by the window: the
   mod keeps to the middle 16:9 of the canvas.
5. Duels: `func_80024DC8(-1, duelist, 0x6000, 0x6000)` and
   `D_8009B368 = 13` make the game's own duel (deck screen, field,
   result) and bring it back to mode 13; `D_8009B362 == 0` is a win.
   The opponent's deck is the game's, or the fixed 40-card deck that
   the mod's `decks` table gives it (`mod.json`).
6. Sub-screens: the name is typed on the game's name-entry screen (main
   mode 9) and the deck is edited on the deck editor (mode 7); both are
   entered by setting `D_8009B26C` with `D_8009B269 = 13` and return
   to the mod.
7. Music: `SD_BGMPlay(0x7000 + track * 0x10)` per area, with
   `SD_BGMFadeOut` between areas.
8. Save: `journey.sav` in the mod's data directory
   (`host->open_data`), written by START > Save and after each duel or
   chapter scene; the same struct is registered with
   `host->register_state`, so save states carry it. Cards from rewards
   are in the game's own card chest (saved by the game's save); the file
   lists them too and gives back any that are missing after a load.

## Files

| file | what |
|---|---|
| `ow_poc.c` | entry, events, the state machine (choose, create, walk, scene, ask, menu, duel, leave), overlay |
| `jm_gfx.c` | assets, camera, polygon sorting, meshes, portraits |
| `jm_world.c` | map, collision, locked tiles, areas, the people and the draw loop |
| `jm_story.c` | rules (conditions, talk, spots, triggers), scenes and the text box |
| `jm_ui.c` | character creation, START menu |
| `jm_save.c` | the save file |
| `jm_json.c` | a small JSON reader |
| `assets/world.jwld` | the map |
| `assets/journey.json` | people, rules, locks, triggers, chapters, objectives |
| `assets/story.json` | the dialogue scripts |
| `assets/atlas.raw` | 768 x 256 RGB555 texture atlas |
| `assets/*.n2`, `assets/p_*.bin` | character meshes, prop meshes |
| `tools/` | the generators: `make_world.py`, `make_late.py`, `make_atlas.py`, `bake_npc.py`, `make_veg.py`, `import_story.py` |

## Data formats

### world.jwld

`"JWLD"`, u16 width, u16 height (64, 168), then three layers of
width x height bytes: tile, deco, tint. Tiles: 0 sand, 1 path, 2 water,
3 wall, 5 arena, 8 palm, 9 ruin, 10 column, 11 obelisk, 12 portal,
13 palace, 14 door, 15 throne, 16 gate. Deco: 1..7 a prop mesh (boulder,
sage, agave, skull, tumbleweed, hoodoo, barrel cactus), 8..15 a sprite
(bush, papyrus, oleander, fern palm, tufts, flowers). Tint 0..3 shades
a tile green near plants. The map is five areas in rows: the village
and fields, the Nile and the sand ruins, the Royal City, the throne
hall, the tournament island (`World_Area` in `jm_world.c` cuts them). Below
them, from row 72, are eight rooms of 32 x 24 tiles for chapters 6 to 8 (the
Temple Crossroads, the Sea, Forest, Mountain, Desert and Meadow temples, the
Labyrinth and the Final Temple). Written by `tools/make_world.py`.

### NPC meshes (`*.n2`)

`"NPC2"`, u16 vertices, u16 triangles, u16 frames, u16 0; then per
frame vertices (3 x i16, y down, 56 units tall); then per vertex
normal (3 x i8), slot (u8: 0 fixed, 1 skin, 2 hair, 3 outfit,
4 trousers) and colour (3 x u8); then triangles (3 x u16). Frames:
idle and four walk poses. Lit per vertex from a fixed sun, so skin,
hair and outfit are recoloured by the creation screen. Made by
`tools/bake_npc.py` from Quaternius glTF.

### journey.json

* `flags`: the names of the story flags, in bit order (the save keeps a
  32-bit word); duelists are `<id>_won`.
* `areas`: name and BGM track of each area.
* `start`: spawn tile.
* `npcs[]`: `id, name, mesh, tile [x, z] | null, duelist_id, portrait_id,
  places[]` (moves, `{when, tile | null}`, first match wins) and
  `talk[]` (rules, first match wins): `{when?, scene, duel?, win?, lose?}`;
  with `duel` set, the last page of the scene asks Yes/No and Yes starts
  the duel; `win`/`lose` are results `{scene?, flags?, stage?, cards?,
  items?, ...}` applied after the duel.
* `locks[]`: `{tile: "portal"|"door"|"throne"|"gate", needs: [flags]}` or
  `{rect, when}`; those tiles are solid until the flags are set.
* `spots[]`: where pushing against a lock gives a message scene.
* `triggers[]`: lines crossed by the player: `{when, scene?, set_stage?,
  teleport?, then?, rect?}`; `rect` is `[x0, z0, x1, z1]` in tiles, a
  `teleport` is how the rooms below the main map are entered, and `then`
  plays a second scene after the first.
* A duel's `win` result may carry `then` (a scene to play next) and
  `choice` (`{yes, no}` results for a Yes/No page that follows), which is
  how the two endings are picked.
* Entries added by `tools/make_late.py` (chapters 6 to 8, from the story
  content and `notes/card-catalog.csv`) are marked `"late": 1`; running the
  script again replaces them.
* `chapters[]`, `objectives[]`: `{when, text}`, first match wins (HUD).
* `speakers`: the player (`atos`), the Prince, and others with a
  portrait id.
* Conditions (`when`): `stage_ge`, `stage_lt`, `row_lt`, `row_gt`,
  `has`, `needs`, `lacks`, `lacks_any` (flag names).

### story.json

`{"scripts": [{"id", "pages": [{"speaker", "text", "ask"?, "label"?}]}]}`
as `journey_content/story.json` (schema in its SCHEMA.md): text uses
`{name}` and `{male|female}` tokens, at most 3 lines of 32 glyphs per
page, and the glyphs of the retail font. `tools/import_story.py` writes it
from the content file.

### journey.sav

12-byte header (`"MJS1"`, version 1, size) and the struct `Journey` in
`jm.h`: flags, stage, win/loss/duel counts, items, name and look, the
player's position, the cards that rewards gave.

## Making a change

* New person: add an entry to `journey.json` (mesh from `assets/*.n2`),
  bake a new mesh with `bake_npc.py` if needed.
* New text: add a script to `story.json`, point a talk rule at its id.
* A new map: change `tools/make_world.py` and run it.
* Build: `python3 tools/pc/build_mod.py --target i386 mods/ow-poc`.

## Not done yet

* The side duelists Cockatiel and the mirror Atos need duelists that the
  port does not have yet; their scripts are in `story.json` and unused.
* The deck editor is the game's own and ends at the game's "which deck?"
  list, which an automated test cannot drive; items and status are text
  only.
* The `decks` table in `mod.json` is a repository-wide setting: while the
  mod is enabled, Free Duel opponents with those names use these decks too.
* Characters have no eyes or mouth textures.
* The rooms of chapters 6 to 8 are plain: sand, a few walls and plants.

## Credits and licences

* Characters: Quaternius, CC0 (not in the repository; `bake_npc.py` takes
  the glTF folder).
* Props: PSX Nature by heyheythere, CC BY 4.0.
* Ground, plants and portrait atlas, generated by `make_atlas.py`.
* Story, decks: `journey_content` (Atos Vinicius with Grok Bot).
