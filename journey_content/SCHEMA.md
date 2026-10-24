# JOURNEY MODE content schema

All files are plain UTF-8 JSON (ASCII only). Text is English. Nothing here contains engine code.
Run `python3 tools/validate_all.py` after any edit (JSON parse + `check_story.py` + `check_decks.py`).
The files are generated from `src/*.py` (`python3 src/build.py`), but the JSON is the source of truth for the engine.

| file | what |
|---|---|
| `story.json` | everything the map/dialogue engine needs: speakers, flags, stages, chapters, areas, NPCs, objects, duels, transitions, HUD objectives, UI strings and all 148 dialogue scripts |
| `decks.json` | 28 fixed 40-card decks + the custom CLT cards |
| `cockatiel.json` | the new Cockatiel duelist (bio, portrait brief, port duelist/drop definition, extra lines) |
| `port_decks_fragment.json` | the same decks in the port's `mod.json` `decks` format (`"fixed": true`) |
| `story_readable.md` | all dialogue in reading order (generated) |
| `credits.md` | credits and licences |

## 1. Text rules (`story.json.text_rules`)

* Allowed glyphs: `A-Z a-z 0-9`, space and `. , ! ? ' -`. No accents, no `:` `"` `;` `(` `)` and no emoji. Written like the retail font.
* One page = one `pages[]` item = one dialogue box: at most **3 lines of 32 glyphs** (the box has 268 px = 33 glyphs of 8 px, see `ow_poc.c say()`, which wraps at word boundaries and auto-pages after 3 lines). `tools/check_story.py` simulates that wrap.
* Tokens inside `text`:
  * `{name}` the player's name (default `Atos`); counted as 10 glyphs.
  * `{a|b}` gender choice. `a` is used for a male character, `b` for a female one (`{lad|lass}`, `{name}-{boy|girl}`). Counted as the longer option.
  * No other braces are allowed.
* Ask pages (`"ask": true`) are always the last page of their script; the engine adds the Yes/No (`ui_strings.ask_yes_no`) and starts the duel on Yes.

## 2. `story.json`

### 2.1 `speakers`
Key -> `{name, short, portrait, note?}`. `name` is the box heading (`{name}` for the player), `short` is the form the port uses in tight UI (matches `Tables_DuelistShortName`), `portrait` is the portrait id (`0xFE`=254 means no portrait, `240`=0xF0 is the custom Prince slot, 241/242 are new custom slots for Cockatiel and the mirror Atos; all others are the game's duelist ids, e.g. 1 = Simon).
The speaker `narrator` has no portrait (254) and every narrator page carries its own `label` ("Objective", "Reward", "End of Chapter 3", ...).

### 2.2 `flags` (the old `beat` bit field)
`{name, bit, value, note}`. Bits 0-10 keep the legacy values from `ow.c` (`beat&1`=Jono beaten ... `beat&1024`=Pegasus beaten). Bits 11-29 are new (chapters 6-8, side duelists, endings). `beat` is a 32-bit int, bit 30 is the highest allowed (checked).

### 2.3 `stages`
Legacy `stage` variable: 0 character creation, 1-2 chapter 1, 3 ch2, 4 ch3, 5 ch4, 6 ch5, **7 ch6, 8 ch7, 9 ch8, 10 post-game**. `chapter = stage-1` for stages 3-9.

### 2.4 Conditions (`when`)
Used by dialogue rules, transitions and HUD objectives. All present keys must hold (AND):
`stage: [min,max]` (inclusive), `flags_all: [names]`, `flags_any: [names]`, `flags_none: [names]`.

### 2.5 `npcs[]` and `objects[]`
* `npcs[]`: `id, name, area, tile{tile_x,tile_z} | placement (free text for new maps), duelist_id (game id 1-39, a string id from new_duelists, or null), model_hint, stages [min,max] where the NPC exists, dialogue_rules[]`. Legacy NPCs also carry `legacy_npc_index` (index in `ow.c` `NPCS[]`) and `legacy_talk_target`. Extra position fields: `hall_tile/hall_area` (moves to the throne hall at stage 5), `after_simon_won_tile` (guard).
* `objects[]`: things you press X on that are not people (portal, doors, gates, altar, stairs). `solid_until` lists the flags that must all be set before the tile stops being solid; `dialogue_rules` give the "locked" text.
* `dialogue_rules[]` (on both): **ordered, first match wins**: `{when, script, duel?, note?}`. If `duel` is set the script ends with an ask page and Yes starts that duel id. A rule list that does not match means "nothing to say".
Tiles are in 32-unit map tiles like `ow.c` (`T=32`); new areas have no tile numbers yet (`placement` is a hint for the map author).

### 2.6 `areas[]`
`id` 0-7 are the legacy areas (names translated; `music` = the existing `AREA_M` ids). 8-15 are new: Temple Crossroads (hub), Sea/Forest/Mountain/Desert/Meadow Temple, Labyrinth, Final Temple. `music.id` null = pick a track from the disc list. `setting` is a short art brief.

### 2.7 `items[]`
Backpack items: `id, name, source, flag?` (shown once the flag is set), `note?`.

### 2.8 `new_duelists[]`
Port duelists to add (`notes/more-duelists.md`): `id` (file name), `copy` (disc duelist used as AI/drops base), `name`, `slot` (40+), `portrait_file`.

### 2.9 `duels[]`
```
{ id, npc, duelist_id, chapter, deck (key in decks.json), difficulty_tier,
  pre_script, win_script, lose_script,
  pre_effects?[], win_flag?, on_win[], rewards_first_win_only, note? }
```
Flow: talk -> rule picks `pre_script` -> Yes on the ask page starts the duel against `duelist_id` with `deck` -> on win run `win_script`, set `win_flag` and run `on_win` (rewards only the first time when `rewards_first_win_only`) -> on loss run `lose_script` and return to the map.
Effects (objects with one key): `give_card` (disc card name), `give_card_custom` + `fallback_card` (custom CLT card, falls back when the custom card pack is absent), `give_item` (items id), `set_flag`, `set_stage`, `teleport {area, tile|spawn}`, `move_npc`, `remove_npc`, `place_npc`, `place_npcs` (legacy `place_npcs()`), `play_script` (chain another script right after), `play_script_after` (after the teleport).
`check_story.py` verifies every rewarded card/item is named in the win script.

### 2.10 `transitions[]`
Chapter changes: `{id, when (includes the exact stage), trigger, effects[], script, note?}`. Trigger kinds: `character_creation_done`, `walk_north_of_tile_row` (legacy `pz < row*T`), `walk_between_tile_rows`, `interact {object}`, `choice {script, answer}` (the Yes/No ask on a script).

### 2.11 `hud_objectives[]`
Ordered list, first match wins: the one-line objective in the HUD/pause menu (same role as `objective()` in `ow.c`). Shown with `ui_strings.objective_label`.

### 2.12 `chapters[]`
Summary per chapter: `n, title` (in-game banner title), `design_title`, `region, stage [min,max], duels[] (ids), reward, unlock`.

### 2.13 `scripts[]` (the dialogue)
```
{ id, legacy_id (0-66 for chapters 1-5, else null), chapter, desc,
  pages: [ { speaker, text, ask?, label? } ] }
```
`legacy_script_index` maps legacy numeric ids to the new string ids so the old `SCRP` block builder (`story.py build()`) can be reused: iterate `legacy_id` 0..66. Page order and speakers are exactly the original's.

## 3. `decks.json`
```
{ rules, difficulty_curve, custom_cards[], decks: { "<duelist name>": {
    duelist, chapter, difficulty_tier (1-10), theme, fixed: true, total: 40,
    cards: { "<disc card name>": copies },
    cards_with_custom_pack?: { ... } (Atos Vinicius only), notes } } }
```
* Card names are the disc's names from `fork/notes/card-catalog.csv`; the key is the duelist name as in `Tables_DuelistNames` (or `Cockatiel`, `Atos Vinicius` for added duelists).
* FM deck rules enforced: exactly 40 cards, at most 3 copies, at least 14 distinct cards, no ritual-only monsters and no Ritual cards.
* Difficulty tiers rise with the chapter: average monster ATK goes from about 1000 (tier 1) to about 2400 (tier 10); high-level monsters, field cards (Yami/Umi/Mountain...), removal and fusions appear later.
* `custom_cards[]`: the 10 CLT-themed cards of the Atos Vinicius duelist (English names; `replaces_vanilla_slot` is only the PS1 patch's slot id). Only the `cards_with_custom_pack` deck uses them; the plain `cards` deck is all disc cards.
* `port_decks_fragment.json` is the same data as `{"decks": {"<name or id>": {"fixed": true, "<card>": copies}}}` for a `mod.json`.

## 4. `cockatiel.json`
Character sheet for the new duelist: `bio, personality, portrait_description` (art brief for the 48x48 portrait), `model_hint, portrait_slot, port_duelist` (the `duelists/cockatiel.json` content), `drops` (pow/bcd/tec pools), `items, script_ids, deck, play_style, extra_lines`. Fictional: no real person's name, face or voice.

## 5. Tools
* `tools/check_story.py` - structure, references, charset, tokens, 3x32 fit, rewards vs. win text, legacy ids 0..66, decks present.
* `tools/check_decks.py [decks.json] [card-catalog.csv] [cards.c]` - every name must exist in the catalog (and duelist names in `tables.c`), 40 cards, max 3, no rituals.
* `tools/validate_all.py` - all of the above.
* `tools/dump_story.py` - regenerate `story_readable.md`.
* `src/build.py` - regenerate the JSON from the Python sources.
