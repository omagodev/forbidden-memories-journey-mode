# journey_content/economy: schema and engine work

Design: `DESIGN.md` (read first). Data is the source of truth for the engine, same style as `../duelist_kingdom/`: English JSON, Portuguese (ASCII only) in `pt/`. Nothing here edits the fork or the dev tree.

```
economy/
  DESIGN.md                  the design (currency, prices, pools, levels, gang, arenas, story fit, open questions)
  README.md                  this file (schema, engine work, wiring examples)
  economy.json               currency, tier tables, formulas, drop odds, save-state layout, features, new effects/conditions, new areas
  shops.json                 9 shops: stock (always / rotating / limited / packs), keepers, anchors, open conditions
  card_pools.json            10 local pools (real FM ids/names), rarity, weight, min_level, arena_only
  card_rarity.json           class of every non-ritual card (selling, optional deck power cap) + the banned list
  gang.json                  Dune Jackals: members, tiers by level, stakes, ambush rules and sequence
  arenas.json                8 arenas, ladders, fees, rewards, 31 fighters (duelist slots 50-80)
  levels.json                30-level table (xp, rank, shop tier, drop shift, coin bonus, gang weights, deck power cap, unlock events)
  decks_economy.json         38 fixed 40-card decks (7 gang + 31 arena), format of decks_dk.json
  en/economy.en.json         names, dialogue (<= 3x32), ui strings, descriptions (master text)
  pt/economy.pt.json         same keys, Brazilian Portuguese, ASCII only
  src/gen_economy.py         generates every JSON above (seeded, deterministic); src/eco_text.py holds all strings (EN+PT side by side)
  validate_economy.py        validator, run: python3 validate_economy.py   (0 errors expected; 3 warnings are known)
```

`python3 src/gen_economy.py && python3 validate_economy.py` regenerates and checks everything. Edit `src/` (never the JSON by hand) when the design changes.

## Validator (what it checks)

Card ids and names against `fork/notes/card-catalog.csv` (and the ban list: rituals, ritual-only monsters, Exodia, traps, old-story custom slots, password-less legends); every pool non-empty with at least 3 C/B/A cards, types and rarity consistent with the stats, weights integer >= 1, **effective drop odds sum to 100 for every pool x context x level 1-30 x (arena or not)** and never fall on an empty rarity; shop prices equal the formulas, shop cards are in the shop's pool, one-time bits unique below 64, pack slots consistent, sell price below the cheapest buy price; deck legality (40 cards, <= 3 copies, >= 14 distinct, no ritual/Exodia/custom-slot card; **Forbidden Memories has no deck-cost rule, only these**); gang tiers cover levels 1-30 and sum to 100, stolen coins never exceed the purse or go below 0 (tested for purses 0-99,999 at every factor), first-ambush rules, safe-zone anchors; arena ladders (4 rungs, tiers non-decreasing, champion last, decks exist, unique duelist slots, copy bases are disc duelists, expected value per run positive at a 60% win rate); levels table arithmetic; EN/PT key parity, ASCII, charset, 3x32 fit for dialogue, format specifiers; consistency with `duelist_kingdom` (flag budget unchanged, areas, quest ids, duel ids, `give_card` protected list, duelist slots 40-42 not reused, no home-arc duel with `stars_wager`).

## Schema notes

* **Ids**: `shop.id` = `pool.id` = `arena.id` = the location (`village`, `harbor`, `beach`, `forest`, `mountain`, `meadow`, `desert`, `fair`, `gate`; the pool `hall` has no shop). `area` is the story/outline area id (`kingdom_beach` etc.). `area_to_pool` (card_pools.json `rules`) maps every area to its pool (`castle_top` -> `hall`, `cistern` and `ship_deck` -> none).
* **Drop roll** (engine): `context` odds (economy.json `drop_odds.contexts`) -> move `drop_shift` points from C (limited by the C share) -> rarities with no available entry (`min_level` > level, or `arena_only` outside arenas) fall to the next lower -> weighted pick. The number of cards per context is in `cards_per_context`.
* **Shop stock**: `always` and `limited` are fixed entries; `rotating[]` is `{slot, rarity, count, min_level, price, from: "pool"}` with the deterministic pick in `shops.json shops[].rotation` (`fnv1a32(shop + ":" + slot + ":" + epoch + ":" + card_id)`, `epoch = jm.duels / every_duels`). `limited[].bit` indexes `Economy.bought[]`. `unlock` may hold `stage_min` and `flags_all` (names from `story_dk.json`). Buy price = `round5(price_win * weq[rarity])` (formulas in economy.json). Sell price is global (`economy.json prices`).
* **Gang**: `members[].duelist` is a new duelist (`copy` = a disc duelist whose portrait/AI it borrows, `slot` >= 43, `id`), `deck` is a key of `decks_economy.json`. `ambush` holds every timer and zone; `sequence[]` is the order of events; `stakes` the percent/min/max per gang tier.
* **Arena**: `ladder[]` = `{rung, fighter, tier, deck, champion, coins, xp_base, drops{context,count}}`; `unlock` = `{level_min, stage_min?}`; `entry_anchor` = `<area>.arena_door`; `interior_area` = `arena_<id>` (listed in `economy.json new_areas`); `first_clear` / `repeat_clear` as in DESIGN. `fighter == "old_jackal"` refers to the gang member.
* **Text**: data files carry the English `name` inline; `*_id` fields point into `en/` and `pt/` (`names.shops.<id>`, `dialogue.fighter_pre.<id>`, `ui.<key>`). Dialogue obeys the story rules (ASCII letters, digits, space and `. , ! ? ' -`, 3 lines of 32). UI strings may also use `: % + /` (the story's ui already does) and `%d`/`%s`; `ui.pack_fmt` uses positional specifiers so Portuguese can reorder ("Pacote Oasis").

## Wiring into the story (examples, not applied)

The story files are not edited. When the engine work lands, `dk_to_journey.py` (or a sibling `eco_to_journey.py`) merges these effects into existing rules:

```json
{"when": {"stage": [1, 1], "flags_all": ["simon_won"]}, "effects": [{"give_coins": 30}, {"give_xp": 10}]}
{"id": "teana", "dialogue_rules": [{"when": {"stage": [3, 5]}, "script": "eco_teana_shop", "effects": [{"open_shop": "village"}]}]}
{"when": {"coins_min": 100, "level_min": 2}, "script": "eco_hakim_tip", "effects": [{"open_arena": "village"}]}
```

Duel rewards need no per-duel edits: coins/XP follow the deck's `difficulty_tier` and the rules above; the existing `on_win` cards stay, and the drop roll adds local cards. `quest_coins` are paid by the quest-complete banner.

## Engine work (sizes: S < 150 lines of C, M 150-400, L 400+, plus art where noted)

| # | piece | size | notes |
|---|---|---|---|
| 1 | Save: append `Economy` (52 bytes) to `Journey`, `VERSION 4`, level-from-xp helper | S | zero-fill of old saves already works (`Save_Read`); `register_state` size grows (old save states stop loading) |
| 2 | Data loaders for the six JSON files + lang strings (`Tr()` keys) | M | `jm_json.c` exists; new `jm_eco.c` |
| 3 | New effects `give_coins`, `take_coins`, `give_xp`, `open_shop`, `open_arena`, `set_ambush`; conditions `coins_min`, `level_min`, `level_max`; validator additions in `validate_story.py` | S-M | `Story_ApplyResult`, `Story_Cond` |
| 4 | Duel result hook: coins + XP by tier and context, level-up detection, banners (coins, XP, level up with unlock lines) | M | reuse the animated banner kinds (item/objective) and add an alert kind (red) for LEVEL UP and AMBUSH |
| 5 | Local drop roller: hook `Duel_SelectCardDrop` (mod API 4) and use `card_pools.json` by area and context; extra cards of a context via `Story_Cards` | M | `limits.card_drops` is a manifest lock (1 for Journey), so the 2nd champion card is granted by the mod; keep the game's SPOILS page showing the first card; set the starchip prize to 0 |
| 6 | **Shop screen** (overlay): tabs Cards / Packs / Sell, list with price, owned count, scroll, buy/sell confirm, rotating stock, pack opening reveal (5 cards, one at a time), coins HUD, keeper greeting | L | needs the chest's copy counts and the deck's counts (to know spare copies); pack rolls use the pool + slot rules |
| 7 | **Ambush system**: walking-distance countdown, eligibility (area, stage, safe zones, scenes/menus, grace), input lock, red `!`, AMBUSH banner, gang sprite run-in, taunt page, duel start with quit disabled, theft/recovery math, truce | L | all counters in `Economy`; the painted `Paint_Tick` is the place that already knows distance walked and speed (2.6 / 4.4 per frame) |
| 8 | **Arena**: hidden door object, tip, entry screen (fee, ladder, current rung), run state machine (4 rungs, loss ends the run, save mid-run), first-clear/repeat rewards, interior area, rank titles | L | one reusable interior scene with 4 art variants; fighter pre-duel pages from `dialogue.fighter_pre.*` |
| 9 | Status screen + HUD: coins, level, XP bar, rank, ambush record, arenas cleared; coins line next to the objective | S-M | `jm_ui.c` START menu already has Status/Backpack |
| 10 | New duelists and decks from the data: generator writes the port's `duelists/<id>.json` (copy, name) and the `decks` table from `decks_economy.json` (38 each) into the mod | M | `notes/more-duelists.md`; verify the port is fine with 38+3 added duelists (slots 42-80) |
| 11 | Converter + story validator: merge effects/anchors, check `*_id` text keys, 30-flag budget stays 30 | M | extend `dk_to_journey.py`, `validate_story.py` |
| 12 | Smoke scenarios: first coins, buy a pack, sell a spare, ambush loss/win, arena run, level up, save/load round trip | M | `tools/smoke` style |
| A1 | Art: 8 shopkeeper sprites + stall prop (Teana exists); 7 gang sprites; 31 fighters (a few bodies recoloured); coin icon, `!` icon, alert banner frame | L | all one-screen assets; start with palette swaps |
| A2 | Art: 8 arena interiors (one screen each, with anchors `entry`, `ring`, `bookie`, `crowd`) | L | settings in `en/economy.en.json descriptions.arena_settings` |

**New anchors the art/engine must add** (`<area>.<anchor>`): `shop_stall` and `arena_door` in each Kingdom/harbor area (`harbor`, `kingdom_beach`, `kingdom_forest`, `kingdom_mountain`, `kingdom_meadow`, `kingdom_desert`, `kingdom_fair`, `castle_gate`; `arena_door` not at the gate and the fair uses it for the big top), `village.arena_door` (a cellar hatch behind the bakery), `kingdom_beach.camp`, and the existing `*.spawn` of each new area. The village shop uses the existing `village.teana_stall`.

### Fallback if 38 added duelists are too many

The only thing that forces many slots is that the port ties a deck to a duelist. If the host cannot assign a fixed deck per duel at run time, run the **compact** variant: gang 7 slots (as now), and arena fighters reduced to 8 champions (one per arena, slots 50-57) plus 4 shared "pit fighters" (slots 58-61, tiers 1-4 reused by every arena with the deck of the nearest tier); everything else in the data (ladders, fees, rewards, pools) stays. `arenas.json` fighters would then point at shared decks; no rule changes.

## Known limits

* Equip/field affinities in the pools are design-level (type to equip), not read from the game's equip table; check them in the FM Editor before shipping.
* Portraits of the 38 new duelists are placeholders (the base disc duelist's face) until art exists.
* The beach and meadow pools have no S card, so arena S rolls there fall to A (validator warning).
* Mean monster ATK dips slightly from tier 5 to 6 (validator warning), because themed machine/warrior decks sit there.
