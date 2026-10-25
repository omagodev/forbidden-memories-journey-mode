# Duelist Kingdom story (new main story, chapter 1 written, Kingdom outlined)

The old story (`../story.json`, `../pt/`) is untouched and stays as backup. Everything for the new story lives in this folder.

```
duelist_kingdom/
  README.md                 this file
  en/story_dk.json          chapter 1 (home town to the ship), English
  en/ui_dk.en.json          extra UI strings
  en/story_readable_dk.en.md  all dialogue in reading order
  pt/story_dk.pt.json       same ids and structure, Brazilian Portuguese, ASCII only (no accents)
  pt/ui_dk.pt.json, pt/story_readable_dk.pt.md
  decks_dk.json             5 new 40-card decks (Villager 1, Villager 3, Yami Bakura, Shadi Courier, InsetoKaiba)
  kingdom_outline.json      star rules + Kingdom chapters 2-10 (outline) + Mago.dev glimpses 5-7 and the payoff (drafted as real pages)
  src/                      Python sources (dk_scripts.py dialogue EN+PT side by side, dk_data.py structure, dk_kingdom.py outline); run `python3 src/build_dk.py`
  tools/check_dk.py         validator, run `python3 tools/check_dk.py` (0 errors expected)
```

The JSON is the source of truth for the engine. Same text rules and most of the schema of `../SCHEMA.md`:

* ASCII only: `A-Z a-z 0-9`, space and `. , ! ? ' -`. At most 3 lines of 32 glyphs per page. Tokens `{name}` and `{male|female}` (PT uses `{sozinho|sozinha}` etc.).
* `speakers`, `flags` (bit = index, max bit 30), `stages`, `items`, `scripts[].pages[]` (`speaker`, `text`, `ask`, `label` on narrator pages), `duels[]`, `transitions[]`, `hud_objectives[]` (ordered, first match wins), `new_duelists[]`: as in the old story.
* `decks`: a duel's `deck` is looked up in `decks_dk.json` first, then in `../decks.json` (Simon Muran, Teana, Rex Raptor, Mage Soldier are reused as they are).
* `legacy_id` is always null (no legacy script numbering in this story). Script ids start with `dk1_`.

## What is new compared with the old schema

1. **Symbolic anchors instead of tiles.** Every NPC/object has `area` + `anchor`; `anchors` (top level) lists each anchor with a hint for the painted picture. The engine dev binds `<area>.<anchor>` to picture coordinates (and the objective arrow / mini-map use the same anchors). Areas are string ids (`village` is the existing painted village, the others are new).
2. **`visible`** on an NPC: `always` (exists while `stages` holds) or `placed` (only after a `place_npc` effect, removed with `remove_npc`). `moves[]` = `{at_stage, area, anchor}` relocation. `patrol` is a named loop for the art/engine.
3. **`effects` on a dialogue rule**: run after the script is read (the old schema had effects only on duels and transitions). Used for flags, items, cards, stage changes and NPC placement.
4. **New effects** (objects with one key): `give_card`, `give_item`, `set_flag`, `set_stage` as before, plus `add_stars {n}`, `set_time "day"|"night"` (night variant of the village background plus tint), `place_npc {npc, area, anchor}`, `move_npc {npc, area, anchor}`, `remove_npc`, `show_prop "ship"`, `teleport {area, anchor}`.
5. **New trigger kinds** in `transitions[]`: `character_creation_done`, `interact {object}` (as before) and `when_true`: fires once as soon as its `when` condition becomes true (checked after every effect), e.g. all three stamps collected.
6. **`quests[]`**: the journal. `{id, kind, optional, title, giver, steps[{objective, anchor}], reward}`. The engine shows the objective of every active quest (the HUD shows the quest updated last; `hud_objectives` is the stage/flag-driven fallback and is always consistent). Objective arrow = the `anchor` of the current step. A step is done when the matching flag/stage in the NPC/duel tables is set (see each quest's NPC/duel ids; flag names are `heard_*`, `treasure_*`, `*_won`...).
7. **`stars_wager`** on duels: false for the whole home-town arc (no stars at risk). From chapter 2 on (see `kingdom_outline.json`) a 'Wager 1 star?' page follows the ask.
8. **Variables**: `stars` (0..12), `time_of_day`, `eliminations`. Home-town flags are frozen from stage 10 on; the Kingdom uses a second 31-bit word (`kflags`).

## Symbolic anchors the engine must implement

Village (painted, existing): `village.hero_start`, `plaza_center`, `plaza_bench` (NEW prop), `house_ne_door`, `teana_stall`, `bakery_door`, `farmer_field`, `date_palm`, `mini_pyramid_hatch` (NEW hatch overlay), `notice_sign`, `river_bank`, `bridge_north`, `east_road`.
Observer anchors: `village.mago_roof`, `cistern.wall_glyph`, `harbor.breakwater`, `ship_deck.mast_top` (OBSERVER, not walkable).
Cistern (NEW): `spawn_stairs`, `bakura_spot`, `exit_stairs`. Harbor (NEW): `spawn_gate`, `inspector_spot`, `pier_end`, `farewell_simon`, `farewell_teana`, `farewell_jono`, `gangway`, `bridge_back`. Ship deck (NEW): `spawn_gangway`, `mai_spot`, `inseto_spot`, `barrel`, `bow`. Kingdom: `kingdom_beach.spawn`.
Full list with picture hints: `anchors` in `en/story_dk.json`.

Interactions the engine needs besides NPC talk: objects (`objects[]`, X on them), `solid_until` flag gates (bridge, hatch, harbor gate, gangway, bow), `interact` transitions with teleport, a **night** state for the bench scene (`set_time`), a `place_npc` that makes an NPC appear, and a `show_prop` for the ship at the pier.

## Mago.dev (the observer)

Speaker/NPC id `mago_dev` (speakers `mago_dev` portrait 244 robe, `mago_dev_tee` portrait 245 tee, `mago_hidden` = '???' before the hero knows him). Art: the local art workspace (not in this repository) (`baked/spr_mago_robe.bin`, `spr_mago_tee.bin`, `portraits/mago_hood_*`, `portraits/mago_tee_*`, `overlays/mago_aura_*.png`).
Rule: he programs reality but NEVER interferes. He has no dialogue rules in the home arc, never walks to the hero, never blocks, trades or gives anything. The engine shows him only through the top-level `observer_events[]`:
`{id, n, npc, sprite "robe", overlay "aura", area, anchor, show_during {script, pages[from,to]} | interact_object, vanish "glitch", flag}`. While the listed pages of the script are on screen, draw the robe sprite at the `OBSERVER` anchor with the green aura overlay (never walkable, no collision); when the pages end, play a short green glitch and remove it. `interact_object` events have no sprite: the object just shows green flickering writing. NPC `visible: "observer"` + `behavior: "observer"`.

| # | where | what | flag |
|---|---|---|---|
| 1 | village, night bench scene (`dk1_bench`) | silhouette on a far rooftop (`village.mago_roof`); the hooded man says 'ignore him, he only watches' | `mago_roof` |
| 2 | cistern (`cistern_glyph` object) | green characters on the wall: 'observe... do not edit'; Bakura mentions it afterwards | `mago_glyph` |
| 3 | harbor, Shadi's win (`dk1_shadi_win`) | silhouette on the breakwater (`harbor.breakwater`) looking at the Star Passage, which flickers green; Shadi: 'he only reads' | `mago_passage` |
| 4 | ship, arrival (`dk1_arrival`) | sits at the top of the mast (`ship_deck.mast_top`); Mai cannot see him | `mago_mast` |
| 5 | Kingdom ch. 6 | Isis senses a watcher in the cards (no sprite) | kflags |
| 6 | Kingdom ch. 7, Star Fair | still figure in the crowd; first line as '???': 'Take your time. I have all of it.' | kflags |
| 7 | Kingdom ch. 9, Castle Hall | in a mirror: 'I could delete him. I won't. It is your duel.' | kflags |
| payoff | epilogue, `village.plaza_bench` | the hero finally notices him in the tee; name tag Mago.dev; his one line: 'You did not need me. Good game.' | - |

Appearances 5-7 and the payoff are drafted as checked pages in `kingdom_outline.json` (`mago_dev`). Counting how many glimpses the hero saw (flags 1-4) is available for an optional extra line in the payoff.

## Stage flow (chapter 1)

`0` creation -> `1` rumors (3 NPCs) -> Simon's test duel -> `2` bench at night, hooded man gives the Stamp Card -> `3` three parallel quests (Lost / Won / Given, any order) -> `4` all stamps (`when_true`), guard opens the bridge -> `5` harbor exam, Shadi's trial -> `6` Star Passage + 1 star, farewells at the pier -> `7` ship deck, Mai's star rules, optional InsetoKaiba duel -> `10` Kingdom (chapter 2).

## Validation

`python3 tools/check_dk.py`: charset, 3x32 fit for every page in both languages, tokens, references (scripts, flags, anchors, items, NPCs, decks), each duel rule's script ends with an ask page, reward cards/items are named in the win text, deck rules (40, max 3, 14 distinct, no Ritual), and EN/PT parity (same ids, speakers, ask pages, flags, duels, transitions).

## Credits / notes

Story and dialogue: Atos Vinicius with Grok Bot. Duelist Kingdom is the setting of a well-known anime; this content uses only the idea of the setting with original characters, quests and text. InsetoKaiba is a fictional parody character (stylized caricature, original dialogue); no real person's name or likeness is used in the data.
