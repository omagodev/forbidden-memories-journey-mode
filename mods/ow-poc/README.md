# Journey Mode

An optional API 10 code mod for SLUS_01411 and the first user of a mod-run
game mode (`src/pc/platform/mod_mode.[ch]`). It adds a **JOURNEY MODE**
button to the title menu, below LOAD: a story mode with a walkable 3D world
of five areas, 14 people to talk to, the game's own dialogue boxes and duels,
area music, a character creator, a START menu and a save file. The design,
the data formats and the files are in `notes/journey-mode.md`.

Like the rest of the port it needs your own USA disc (SLUS-01411); nothing
from the disc is included. The decompilation the port builds on,
[memories-decomp](https://github.com/krystalgamer/memories-decomp), declares
no license.

## Playing

* Title screen: move down to JOURNEY MODE (third item) and press X. With a
  save the mode asks Continue or New journey.
* Creation: name (the game's own name-entry screen), gender, hair, hair
  colour, skin, outfit colour and portrait, with a 3D preview; Start begins
  the story.
* Map: arrows walk (Circle runs), X talks or examines, Start opens the menu
  (Deck editor, Items, Status, Save, Back to title), Triangle on the
  creation screen goes back.
* A person's dialogue ends with Yes/No when he wants a duel; Yes starts the
  game's own duel (deck screen, field, result), and you are back on the map
  with the result. Winning gives the cards and flags the story says, and the
  progress is saved after every duel.
* Gates, doors and the portal stay shut until the duelists that guard them
  are beaten; walking against one says what is missing.

## The decks

`mod.json` gives the duelists of the story (26 of them, the first five
chapters and the temples, the Labyrinth and the Final Temple) a fixed
40-card deck each (from the story content). They apply wherever the mod is
enabled, Free Duel included.

## Build

    python3 tools/pc/build_mod.py --target i386 mods/ow-poc

`tools/` has the generators for the assets: `make_world.py` (the map), `make_late.py` (the chapter 6 to 8 data),
`make_atlas.py` (the texture atlas, with portrait PNGs), `bake_npc.py`
(characters from Quaternius glTF, which are not in the repository),
`import_lpc_test.py` (the ten-frame Universal LPC protagonist and village-character test set: one idle plus the full nine-frame walk),
`make_veg.py` (the plant sprites), `make_props.py` (textures for the Kenney meshes and the ground), `bake_kenney.py`
(houses, fences, stalls, rocks and trees from the Kenney Fantasy Town Kit; `--compare sheet.png` draws every piece next
to the kit's Preview.png, `--flat` bakes the first, untextured look) and `import_lang.py` (the EN/PT language data).

## Credits

* Characters: [Quaternius](https://quaternius.com), CC0.
* LPC animation proof of concept: selected Universal LPC layers under OGA-BY 3.0 and CC-BY-SA 3.0; the complete selection,
  authors and source links are in `assets/lpc_test_credits.txt`.
* Houses, fences, stalls, carts, lanterns, banners, rocks and trees: **Fantasy Town Kit 2.0** by [Kenney](https://kenney.nl),
  CC0 (credit given as a courtesy). Only the baked pieces the map uses are in the repository (`assets/k_*.bin`).
* Props (boulder, sagebrush, agave, skull, tumbleweed, hoodoo, barrel cactus):
  **PSX Nature** by heyheythere, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
* Ground, plants and shadow textures, and the portraits' atlas layout: made by
  the scripts in `tools/`.
* Story, dialogue and decks: Atos Vinicius, with Grok Bot (English text of
  the whole story).
