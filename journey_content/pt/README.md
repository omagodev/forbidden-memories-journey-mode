# JOURNEY MODE - Brazilian Portuguese (pt-BR) and how to add a language

Data only. Nothing here touches the engine (`fork/mods/ow-poc`); the engine reads these files once it has a language switch.

## What is in this folder

| file | what |
|---|---|
| `story.pt.json` | same ids, order, speakers, `ask` flags and structure as `../story.json`; every player-visible text translated (148 scripts, 320 pages). **ASCII only** (retail font) |
| `ui.pt.json` | every other string of the mode (menus, HUD, creation screen, save messages, objectives, banners, area/item/NPC names, mod name and description). Same keys as `../ui.en.json`. ASCII only |
| `cockatiel.pt.json` | `../cockatiel.json` with the in-game `extra_lines` translated (the rest is a design sheet and stays English) |
| `accents/*.pt.json` | the same three files **with accents** (á ã ç é ê í ó ô õ ú ü), see "Accents" below |
| `story_readable.pt.md` | all dialogue in reading order, with accents, for proofreading |
| `src/dialogue_pt.py` | the dialogue, written with accents, one list of page strings per script id (this is the file to edit) |
| `src/meta_pt.py` | translations of everything that is not a dialogue page |
| `src/build_pt.py` | builds the JSON files above (ASCII and accents) and `../ui.en.json` |
| `tools/check_story_pt.py` | validator: key parity with English, tokens, charset, 3 x 32 fit, rewards named, format specifiers |
| `tools/dump_story_pt.py` | writes the readable markdown |

Build and check:

```
python3 src/build_pt.py                        # writes story/ui/cockatiel .pt.json (ASCII) and accents/
python3 tools/check_story_pt.py                # ASCII set
python3 tools/check_story_pt.py accents        # accented set
```

`../ui.en.json` is the English reference of the engine's UI strings. It was extracted from `ow_poc.c`, `jm_ui.c`, `assets/journey.json` and `mod.json` (the strings there are still hard-coded English in C and in `journey.json`); whoever implements the language switch should read from the active `ui.<lang>.json`. Lists (`areas`, `chapters`, `objectives`, `items`) are in the file order of `journey.json`; `npc_names` / `speaker_names` are by id.

## Text rules (same as English, see `../SCHEMA.md` section 1)

* **Charset** of `story.<lang>.json`: `A-Z a-z 0-9`, space and `. , ! ? ' -`. No `:` `;` `(` `)` `"`, no emoji, no accents (retail font). Write chapter lines as `Capitulo 2 - Ruinas de Areia`, not with a colon. The UI file may use `:` and `( )` (those strings are drawn by the host font) but the shipped ASCII file keeps accents out too.
* **Page** = one dialogue box: at most **3 lines of 32 glyphs** (greedy word wrap, a word may not exceed 32). `{name}` counts as 10 glyphs, `{a|b}` as its longer side. The checker simulates this.
* **Tokens**: `{name}` is the player's name. `{a|b}` is a gender choice: `a` for a male character, `b` for a female one; both sides non-empty, no nesting. Portuguese agreement: `{o|a}`, `{ele|ela}`, `{um|uma}`, `{novato|novata}`, `{estrangeiro|estrangeira}`, `{pronto|pronta}`, `{rapaz|moca}`, and inside a word `obrigad{o|a}`. Pegasus' catchphrase is `{name}-{menino|menina}`. No other braces.
* **Pages**: same number and order as the English script, same speaker, same `ask` (the last page asks Yes/No; the engine adds the Yes/No text from `ui.ask`). A narrator page keeps a `label` (at most 20 glyphs; "Objetivo", "Recompensa", "Fim do Capitulo 3", ...).
* **Names**: characters, duelists and **card names stay as the game writes them** (Simon Muran, High Mage Secmeton, Blue-eyes White Dragon, Workers' Rights). Only generic words are translated (Guarda, Principe). A win page must contain the exact name of every card it gives (the checker enforces it) and the translated item name from `items[].name` (e.g. `Tocha`, `Colar do Milenio`).
* **ui file**: keep every key, list length and printf specifier (`%s`, `%d`, same count and order). Do not translate keys.
* Translate meaning and tone, not word by word: casual, a little jokey, like the classic Forbidden Memories.

## Adding a language

1. Pick a code (`es`, `fr`, `de`, `pt-BR` is `pt` here). Copy `story.json` to `story.<code>.json`, `ui.en.json` to `ui.<code>.json`, `cockatiel.json` to `cockatiel.<code>.json` (or start from `pt/src/*.py` and copy the builder idea).
2. In `story.<code>.json` change `language`, translate every `scripts[].pages[].text` and the `label` of narrator pages, plus `speakers[].name/short` (only generic words), `hud_objectives[].text`, `areas[].name`, `ui_strings`, `items[].name`, `objects[].name`, `npcs[].name`, `chapters[].title/design_title/hud`, `title`. Leave ids, flags, rules, `desc`, `note`, `setting`, `source` alone.
3. In `ui.<code>.json` translate every value; also `language.name` (how the language is listed in the picker) and `defaults.player_name`.
4. Run `python3 pt/tools/check_story_pt.py --lang <code> <dir>` (add `--accents` for a language with accents). Fix every `ERROR`; there must be 0 missing or extra keys.
5. Put the files where the engine looks for languages (the loader is the engine's job; the proposed layout is `assets/lang/<code>/story.json`, `ui.json`, `cockatiel.json`).
6. Duels, deck screens, the name-entry screen and the game's own menus are the disc's text: they follow the port's own Game > Language and the disc's language packs, not these files.

## Accents: what the port can draw (finding)

Checked in the fork's source (`src/pc/text/`, `mods/ow-poc/jm_story.c`, `notes/translation.md`):

* **Dialogue box: accents work today, HD text off or on.** `jm_story.c` builds the box text with `Glyphs_NextCharacter` (UTF-8) and `Glyphs_Code(ch)`. For á é í ó ú â ê ô ã õ à ü ç ñ and capitals `Glyphs_Code` makes an **added glyph** (code 0x100 and up, written `F1`-`F5 xx`, which the game already reads): the retail letter with its mark drawn on, in all three text sizes, made the first time it is drawn from the game's own font in VRAM and kept in texture bank 15 (`glyphs.h`, `accents.inc` has 251 letters; limit 672 distinct added glyphs, far above Portuguese's ~40). The text box needs no change: every accented letter is one 8 px cell like the plain letter, so the engine's wrap (`BOX_W / 8`) and the 32-glyph rule still hold. `notes/translation.md` says it plainly: "Accented letters work (é, ñ, ç, ü...)".
* **Look**: capitals with a mark (Á É Ã Õ) give up one row of their body in the 8x12 font so they read a row shorter; lower case (é ã ô) is fine. HD text only re-sets those glyphs from a font at the higher scale; it is not needed for them to appear.
* **HUD, creation screen, START menu, messages, title button**: drawn with `host->draw_text` -> `OverlayText_Draw`, FreeType with the system / mod font fallback (`Glyphs_Face`), so any Unicode letter and `:` `( )` are fine there regardless of the retail font.
* **Not tested at run time**: I did not launch the port with accented text (the engine agent is using the shared test harness); the conclusion is from reading the code and the port's own notes. So the ASCII files are the safe default; `accents/` is ready to switch on after a quick in-game look at a page with `Ç Ã Õ Á É` (e.g. `c2_rex_pre`, `ending_stay`).
* Not supported by data alone: the title button's label comes from `mod.json` (`menu.buttons[].label`, static English `JOURNEY MODE`); a localised label needs engine support (`ui.mod.title_button` is provided for it).
