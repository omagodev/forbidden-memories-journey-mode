# art_dk/chargen: layered hero parts for the character-selection screen

Procedurally drawn (numpy + Pillow, `tools/*.py`) in the same painted chibi style as the AI hero (48x62 texels, 1-texel outline 34,24,30, big head, soft 3-tone shading).
No private reference was used; no AI image generation is involved, every texel comes from the scripts, so all layers share ONE pose grid (`tools/poses.py`) and line up by construction.
The old `spr_ai` hero is untouched.

## What is here
| path | what |
|---|---|
| `manifest.json` | parts, styles, slot to colour-source maps, palette swaps (skin x4, hair x5, outfit/accessory colourways x3), draw order, formats, per-style offsets (all `[0,0]`), combos to avoid, size totals |
| `bin/<part>_<style>.bin` | engine data, **SPR1** (byte-identical layout to `spr_ai.bin`: 5 frames x 4 dirs down,left,right,up; kind / W1..W4 / rgb per texel). 15 files x 476,174 bytes = 7,142,610 bytes (76 KB deflated) |
| `packed/*.cgp1` | the same data bounding-box cropped and de-duplicated (CGP1, 183 KB for all 15; about 12 KB per layer). Optional |
| `png/<part>_<style>.png` | RGBA sprite sheet per layer, 5 columns (frames) x 4 rows (down,left,right,up), default palette |
| `compose.py` | reference compositor + CLI (also `--page` = 256x256 RGB555 page in the engine bank layout) |
| `previews/` | `contact_sheet_combos.png` (8 assembled heroes, 4 directions x idle/stepA/stepB), `catalogue_variants.png` (every skin/outfit/hair/accessory variant), `walk_cycle_all_frames.png`, `layers_exploded.png` |
| `tools/` | `poses.py rig.py body.py outfits.py hair.py acc.py palettes.py` (art), `build.py` (bins, packed, png, manifest), `make_previews.py`, `verify.py` (self-test) |
Rebuild: `python3 tools/build.py && python3 tools/make_previews.py && python3 tools/verify.py` (from this directory).

## Parts and variants
Draw order: **body -> outfit -> hair -> accessory** (a layer texel with kind 255 does not touch the texels below).
- body `base` (1 file). Palette: skin x4 (fair, tan, brown, deep). Slot 2 = hair colour (eyebrows).
- outfit x4 styles: `tunic` (adventurer: short sleeves, V neck, sash, backpack), `jacket` (duelist: long sleeves, lapels, popped collar, back emblem), `cloak` (hooded traveller: mantle collar, clasp, swaying hem), `uniform` (school: blazer, shirt collar, tie). 3 colourways each (main / trim / trousers).
- hair x6 styles: `short`, `spiky`, `long`, `ponytail` (tail sways on the step frames), `bob`, `hood_down` (short hair + the hood bunched at the neck, coloured like the outfit). 5 colours: brown, black, blond, red, silver.
- accessory x4 + none: `headband` (knot + tails), `scarf` (tails fly on steps), `duel_disk` (on the character's left arm; white/black/gold), `cap` (visor). 3 colourways each.
- Combinations: 4 skin x (4 outfits x 3) x 6 hairs x 5 colours x (1 + 4 x 3) accessories = **18,720** (verify.py counts them), minus the pairs in `avoid_combinations`.

## Manifest schema (short)
```
format, frame{w,h,anchor,frames_per_direction,directions,frame_meaning,page_layout}, draw_order[], outline_rgb[3],
format_notes{bin,texel_formula,composite,packed,right_direction}, palettes{skin[{name,rgb}], hair[{name,rgb}]},
parts{ <part>{ <style>{ bin, packed, png, offset[x,y], slots{"1":source,...}, ring_over_body, bytes_*, colourways[...] (outfit, accessory) } } },
avoid_combinations[{hair,accessory,why}], budget{...}, totals{...}, selection_example{skin,outfit,outfit_colour,hair,hair_colour,accessory,accessory_colour}
```
Slot sources: `skin`, `hair`, `outfit.main|trim|trousers`, `accessory.a|b`. Slots per part: body {1 skin, 2 hair}; outfit {1 main, 2 trim, 3 skin, 4 trousers}; hair {1 hair, 2 outfit.main, 3 outfit.trim, 4 skin}; accessory {1 a, 2 b, 3 skin}.
Hands/skin that must stay in front of cloth are redrawn inside the outfit layer with the skin source (slot 3), so draw order never hides them.

## Engine recipe (CPU, once when the creator changes a choice)
1. For each layer in `draw_order`: `spr_load()` the SPR1 file (works unchanged: `nf` = 5), build `pal[1..4]` from the manifest slot map + selected variants.
2. Bake into the character's page exactly like `spr_bake()`: kind 254 -> outline 34,24,30; kind 0 -> `rgb + sum(W_q/100 * pal[q])` rounded and clamped; **kind 255 -> skip** (do not write 0), so upper layers overlay lower ones. Page position: x = frame*48, y = dir*64 (the same offsets as `spr_bake`). Whole page = 131,072 bytes; the 4 selected layers cost 4 x 476,174 bytes of RAM (or ~50 KB with the packed files).
3. Per-style `offset` is `[0,0]` everywhere (kept in the schema so a later style can nudge itself).
`python3 compose.py --skin deep --outfit cloak:plum --hair hood_down:black --acc none --sheet --out x.png` does the same on the PC; `--page x.bin` writes the page.

## Limits
- Not tested in the engine (no engine edits allowed); `compose.py` mirrors the formula of `spr_bake()`, `tools/verify.py` checks layout, mirror symmetry, frame margins, packed == bin and that no outfit lets leg skin through.
- The look is cleaner/flatter than the AI hero (procedural shapes, 5 tone steps, shading by W weight so hue shifts are small); the face is the same for every hero (only skin colour, eyebrow colour change). Only 1 body shape.
- Outline rule: layers other than the body drop their outline where the body is solid underneath (so cloth/hair meets skin without a dark line), except accessories (they keep it). That is baked into the kind bytes, so the engine must not add outlines itself.
- Avoid: `spiky`+`cap` (spikes stick out of the cap), `hood_down`+`scarf`, `long`+`scarf`. With `cloak` the `hood_down` roll is hidden against the cloak colour (it shows on the other outfits).
- `duel_disk` sits on the character's left arm in front/back view and on the near arm in the side rows (the right row is a mirror of the left row, so the disk stays on the camera-side arm there too, i.e. it appears on the character's right arm).
- Walk is the usual idle/step A/idle/step B/idle cycle; side-view legs are simple capsules, hair sway is 1 texel.
