# art_dk: Duelist Kingdom art kit (backgrounds, masks, NPC sprites)
Generated 2026-10-24 with the same painted look as the village (GenerateImage, village print as style reference). Nothing outside this dir was touched.
Preview of everything: `previews/contact_sheet.png`.

## Backgrounds (1280x720 JPG, same size/pipeline as `generated_bg_village_1280x720.jpg`)
| scene | file | notes |
|---|---|---|
| Harbor / dock (ship leaves here) | `backgrounds/dk_harbor_1280x720.jpg` | wide plank pier = walkable spine, sand + 4 mud-brick warehouses on the left, sea on the right (clean flat blue, separate from the land), ship docked at the end of a gangplank |
| DK forest clearing / path | `backgrounds/dk_forest_1280x720.jpg` | open grass+dirt clearing in the middle, trees on all edges (big trees in the foreground bottom), mossy shrine (blue glow) top centre, castle tower peeking top right |
| DK castle courtyard | `backgrounds/dk_castle_1280x720.jpg` | cream stone courtyard + red carpet to the gate, fountain, 4 statue pedestals, braziers, hedges, crenellated walls in front at the bottom |
Raw generator outputs are copies in `raw/` (identical).

## Masks (guesses, hand-drawn rectangles/polygons: `tools/make_masks.py`)
Per scene in `masks/`:
- `<scene>_walkable_160x90.png`: white = walkable, 160x90 cells of 8 texels (same grid as the village `village_col.bin`; a cell is walkable if >=75% free). Convert to the .bin with the same byte layout the village collision uses (1 byte per cell) via `np.array(Image.open(f))>127`.
- `<scene>_overlay.png`: picture + red = blocked, cyan = warp rects, yellow = occluder outlines (orange line = base_y depth line).
- `<scene>_occluders.json`: occluder polygons + `base_y` (1280x720 px, same data model as `house_polys` in `painted_work/make_painted2.py`), warp rects, obstacle rects.
- `harbor_water_mask_1280x720.png` + `harbor_water_overlay.png`: the sea only (ship, pier, quay excluded) for the 6-frame water shimmer (`painted_work/make_water.py` idea). Script: `tools/make_water_mask.py`.

Occluder lists (name -> base_y in 1280 px; full list with polygons in the json):
- **harbor**: warehouse_A/B (top, base 223/206), warehouse_C/D (bottom, 681/644), palms TL/top/L/BM/BR (trunk bases 169/128/481/656/700), crates+pots in front (688/706), ship rigging+sails (325, drawn over characters that walk on the gangplank).
  Warp: `to_ship_gangplank_end` (rect 1000,335 - 1056,400) = boarding the ship (chapter transition).
- **forest**: 14 big trees (each: whole crown+trunk as occluder, only the trunk box blocks walking) and the shrine. Warps: `to_castle_north_east` (NE end of the dirt path), `to_harbor_south_west` (SW end of the path), `shrine_steps`.
- **castle**: 4 statue pedestals (2 up, 2 down), bottom crenellated walls left/right (in front of the player at the bottom), bottom hedges, fountain, gate pillars/towers. Warps: `to_castle_door` (red carpet to the gate), `to_forest_south` (carpet exit at the bottom).

## Sprites (3 generic extras, painted, same pipeline as Simon/Teana/Jono/Guard)
| id | design | sheet (AI, 864x1152, 3 cols x 4 rows on magenta) | baked (SPR1, 48x62, 4 dirs x idle + 4-step walk) | preview |
|---|---|---|---|---|
| captain | old ship captain: white beard, navy coat, captain hat | `sheets/captain.jpg` | `baked/spr_captain.bin` | `previews/sheet_captain.png` |
| rival | hooded dark-purple cloak, teal eyes, holds a card | `sheets/rival.jpg` | `baked/spr_rival.bin` | `previews/sheet_rival.png` |
| tycoon | elegant silver-haired man, red tailored suit, golden goblet (original design) | `sheets/tycoon.jpg` | `baked/spr_tycoon.bin` | `previews/sheet_tycoon.png` |
`sheets/hero.jpg` is only the scale reference (hero = 52 texels tall); all three baked at the hero's scale (captain/rival/tycoon shrunk 1-10% to fit the 62-texel frame).

### How to bake
```
cd art_dk
python3 tools/bake_dk.py                 # all three (needs numpy+Pillow only); or: python3 tools/bake_dk.py tycoon
# -> baked/spr_<name>.bin (~476 KB each, same file format as spr_simon.bin...), previews/sheet_<name>.png
```
`tools/bake_dk.py` just imports a copy of `bake_npcs.py`/`bake_sprites.py` (identical to snap_painted_sprite2/mods/ow-poc/tools) and adds one spec: the AI sheets draw the left AND right rows both facing left, so the right row is the mirrored left row (`{(2,c):(1,c,True)}`, same trick the guard uses).
To use in the mod: copy `baked/spr_*.bin` into `mods/ow-poc/assets/` and register them in `jm_painted.c` like `spr_guard` (bank 13 pages 0-7 are all in use: each new character needs 1 page-pair; bank 15 is free, so 3 characters fit there, a duel/story scene should reload banks on entry as the village does).
New NPC = write a prompt like the ones below, drop `sheets/<name>.jpg`, add the name to the tuple in `bake_dk.py`, run it.

Prompt template used (reference image = `guard.jpg`): "Character sprite sheet, exactly the same layout and painted chibi style as the reference sheet (3 columns x 4 rows on a flat solid magenta #FF00FF background, one character, same scale, feet on the same baseline, no text, no shadows). Rows: front/down, left, right, back/up. Columns: idle, walking step A, walking step B. Character: <design>. Same proportions as the reference: big head, small body, about 2.5 heads tall, thick dark outline."

## Limitations
- Masks and occluder polygons are rough guesses (bounding hulls from eyeballing the picture), NOT pixel-accurate cutouts: trees/palms use a box/hull of crown+trunk, so a cutout would also lift some ground/grass around them. For the engine they need a clean-up pass (polygon tracing like `house_polys`; for trees consider inpainting the clean plate as done for the village palms). Collision is cell-coarse (8 texels).
- Backgrounds are slightly more "painterly/smooth" and higher-res looking than the village print (less voxel-blocky); colours match, perspective is the same ~3/4 high view. No sea animation frames or tree-sway frames made yet (only the harbor water mask).
- The castle courtyard is less open than the village (lots of statues/hedges), but the central cream-stone plaza and carpets are clearly walkable.
- Sprites: AI sheets give idle + 2 step poses, so the walk is idle-step-idle-step (4-step cycle) like the other NPCs. The rival's face is mostly hood shadow; the tycoon's goblet makes the left/right sprites asymmetric after mirroring (the goblet ends up in the hand toward the camera in the right row; acceptable). Back views of the tycoon/rival are plain (no details).
- Pegasus-style tycoon is an original design (red suit, silver hair, cravat, goblet, no trademark text). The anime character covers one eye; ours has hair swept but both eyes visible.
- Not tested in the engine (no engine edits allowed); bank/page budget described above is from HANDOFF.md.


## Characters of the story: Mago.dev (2 outfits) and InsetoKaiba (added t239u/t240u)
Contact sheet: `previews/contact_sheet_characters.png` (portraits at 48x48 x6 and 256, plus the baked sprite sheets).
The private reference photos are kept outside this repository and are not included. The AI was given them as loose inspiration; the outputs are stylized drawings (Mago.dev) and a cartoon caricature (InsetoKaiba, a Kaiba-style parody: shaved head, small mohawk tuft, goatee, long white black-trimmed coat, white-red duel disk on the arm, silver beetle brooch), not likenesses.

| id | what | sprite sheet (AI, 864x1152) | baked sprite | portrait record (FM layout 48x48 8-bit + 64-colour BGR555 CLUT = 0x980 bytes) | hi-res portrait |
|---|---|---|---|---|---|
| mago_tee | Mago.dev, medium shoulder-length dark curls (v3), thin mustache+goatee, grey t-shirt, jeans | `sheets/mago_tee.jpg` | `baked/spr_mago_tee.bin` | `portraits/portrait_mago_tee_48x48.bin` | `portraits/mago_tee_256.png` |
| mago_robe | same, dark hooded mage robe (hood down on the sprite) with thin green code-rune trim | `sheets/mago_robe.jpg` | `baked/spr_mago_robe.bin` | `portraits/portrait_mago_hood_48x48.bin` (hood up, green-lit eyes) | `portraits/mago_hood_256.png` |
| inseto | InsetoKaiba parody | `sheets/inseto.jpg` | `baked/spr_inseto.bin` | `portraits/portrait_inseto_48x48.bin` | `portraits/inseto_256.png` |
Previews of each portrait: `portraits/<id>_48x48.png` and `_48x48_x6.png`; sprite previews `previews/sheet_<id>.png`.
Tools: `tools/bake_dk.py` (sprites; now also drops stray specks and cuts sheet rows at the emptiest line because the generator lets boots spill into the next row), `tools/make_portraits.py` (portraits -> .bin; the `.bin` follows `notes/dialog-portrait-bank.md`: 0x900 index bytes then the 0x80-byte CLUT, so it can replace one of the 25 campaign records or be loaded by a mod), `tools/make_contact_chars.py`.
"programs reality" overlay: `overlays/mago_aura_1024.png` (RGBA, alpha from brightness, neon-green concentric code sigil with 0/1 digits and braces), `overlays/mago_aura_128.png` (small version for a 128x128 additive/texel-0-transparent quad), preview on grass `overlays/mago_aura_preview_on_grass.png`. Idea: draw it as a flat quad under or behind the sprite, slowly rotating or pulsing, when Mago.dev "looks at" the world (story beat), or as a faint 1-texel-green glow only in the robe variant.

Notes: the three sprites' feet scale was re-fit with the new row cutting (all six DK sprites re-baked: captain/rival/tycoon are within 1-5% of the first bake). Rejected generation kept for reference: `raw/mago_sheet_robe_rejected_scrambled.jpg` (columns scrambled), `raw/inseto_sheet_v1_antenna_rejected.jpg` (thin antenna wire dissolves at 48x62, so the final InsetoKaiba has a solid thick tuft; the "insect" cue is the beetle brooch and the tuft).
Limitations: 48x48 portraits are posterized to 64 colours; the Mago.dev sprite colours of the robe's green trim are dark (thin lines at 48x62). Duel disk on InsetoKaiba is one-sided: on the back row it sits on the left of the screen only. Mago.dev tee back-walk uses a mirrored frame. No face likeness work beyond the stated features.

### Update t241u: Mago.dev hair made shorter (v2)
Both Mago.dev outfits were regenerated with short, compact, tight dark curls (about chin-to-neck, close to the head, ears/neck visible), same face, mustache and goatee: new portraits (`portraits/portrait_mago_tee_48x48.bin`, `portrait_mago_hood_48x48.bin`, `mago_*_256.png`, previews), new sheets (`sheets/mago_tee.jpg`, `sheets/mago_robe.jpg`) and re-baked sprites (`baked/spr_mago_tee.bin`, `baked/spr_mago_robe.bin`, `previews/sheet_mago_*.png`). The previous long-hair versions are kept in `raw/v1_long_hair/` (not used). InsetoKaiba and the other sprites were not touched. The paragraph above that describes the Mago.dev design as "long dark curls" refers to the v1 look; the current look is the short curly hair.

### Update t242u: Mago.dev hair set to MEDIUM length (v3, current)
v2 (short) was too short, so both outfits were regenerated once more with shoulder-length dark curls (falls to the neck/shoulders, moderate volume, ears partly covered). Current files: `sheets/mago_tee.jpg`, `sheets/mago_robe.jpg`, `baked/spr_mago_tee.bin`, `baked/spr_mago_robe.bin`, `portraits/portrait_mago_tee_48x48.bin`, `portraits/portrait_mago_hood_48x48.bin`, `portraits/mago_*_256.png`, previews and `previews/contact_sheet_characters.png`. The robe sheet's back-walk step A was a side view, so `bake_dk.py` now mirrors step B for it (like the tee). History: `raw/v1_long_hair/` (too big), `raw/v2_short_hair/` (too short), both unused. InsetoKaiba unchanged. "Mago.dev ... short tight curls" in earlier notes refers to v2.

## Part 3 (Old Cistern, Rex Raptor, Bakura ghost, props, icons) - `part3/`
Contact sheet: `part3/previews/contact_sheet_part3.png`. Pipeline = the same as above (picture 1280x720, masks 160x90, occluder JSON, SPR1 sprites 48x62, prop raw format). Rebuild helpers live in `part3/tools/`.

**1. Old Cistern** (`part3/backgrounds/dk_cistern_1280x720.jpg`, raw copy in `part3/raw/`): dim torch-gold + blue water glow, big sandstone slab floor, stone stairs up at the top centre, round carved dais in the middle, narrow water channel with a small stone bridge slab near the bottom, 6 columns (4 on the sides, 2 in the foreground), carved relief panel upper left, 8 wall torches.
- `part3/masks/cistern_walkable_160x90.png` (8-texel cells, >=75% free) and a tighter `cistern_walkable_320x180.png` (4-texel cells, >=80% free; collision follows plinth footprints, jars, bridge rails, wall edges, the two stair piers).
- `part3/masks/cistern_occluders.json`: 6 columns + 3 jar groups + 2 bridge rails with `base_y`, `warps`, `anchors`, `torches`, `obstacles`, `water_channel`. Columns are NOT boxes: rough capital/shaft/plinth silhouettes were refined with GrabCut (`tools/refine_occluders.py`) to 36-54-vertex polygons (rough ones kept as `polygon_rough`); collision is only the plinth footprint. Debug: `masks/cistern_overlay.png` (red = blocked, cyan = warps, yellow = rough, green = refined outline, orange = base_y), `masks/cistern_occluder_cutouts.png`.
- Warps (1280x720 px rects): `hatch_ladder_up` rect (588,18)-(690,78) (top of the stairs), `ghost_spot` (610,335)-(665,392) (dais), `wall_glyph_spot` (338,188)-(438,215). Anchors matching the story data (1280x720 px): `spawn_stairs` (638,222) bottom of the steps, `exit_stairs` (639,50), `bakura_spot` (638,365) dais centre, `wall_glyph` (388,200) relief panel (observer glyph).
- Rebuild: `python3 tools/make_cistern.py && ../village_roads/.venv/bin/python tools/refine_occluders.py` (refine needs opencv; make_cistern rewrites the rough polygons, so always run both in this order).

**2. Sprites** (`part3/baked/spr_rex_raptor.bin`, `spr_bakura_ghost.bin`, SPR1, 48x62, 4 dirs x idle + 4-step walk; sheets in `part3/sheets/`, previews `part3/previews/sheet_*.png`, bake: `python3 tools/bake_p3.py` from `part3/`):
- **Rex Raptor**: original adult-duelist design: spiky orange hair, dino-tooth necklace, purple jacket over black, black duel disk. Right row = mirrored left row.
- **Bakura ghost**: pale boy with long white spiky hair in a tattered cream cloak fading into wisps, no feet. Engine has only texel 0 = transparent, so the ghost look is baked as pale-blue tint + ordered 4x4 Bayer dither holes (head solid, body faintly see-through, dense at the hem) and the figure is lifted 5 texels to hover (draw the normal shadow under it; the 4 walk frames are near-identical, so bob the quad +-1 unit in code if you want motion). Drawn 11% smaller so the lift fits the frame; the dark outline became a pale-blue one.
- Register like the other NPC sprites (bank 15 is free; each needs one page pair).

**3. Props / icons** (`part3/overlays/`, `part3/icons/`; generated by `tools/make_props.py`, numpy+Pillow only). Prop `.raw` = engine prop format (u16 w, u16 h, RGB555 with bit 15 set, 0 = transparent), loadable by the same `prop_blit` as `prop_bench.raw`:
- `prop_hatch_closed.raw` / `prop_hatch_open.raw` (48x34, trapezoid stone hatch with ring handle / dark shaft with ladder rungs; place on the little pyramid's face NW house: the pyramid is at about x 125-170, y 222-262 of the village picture) + PNGs.
- `prop_torch_glow.raw` (64x64, dithered orange glow, no alpha) and `prop_torch_flame.raw` (48x24 strip = 3 flicker frames of 16x24); torch positions in `cistern_occluders.json` (`torches`). Stone bench prop already exists in the engine (`prop_bench.raw`), not touched.
- Icons: Founder's Scarab (gold scarab, turquoise inlay), Lucky Charm (gold coin with green four-leaf clover on a red cord), Jono's bandana (red cloth, gold dots, knot). Each at 24x24 and 16x16: `icons/icon_<id>_<n>.png` (preview), `icon_<id>_<n>x<n>.bin` (n*n index bytes, 0 = transparent, then a 16-entry BGR555 CLUT = 32 bytes), `icon_<id>_<n>.raw` (prop format). ids: `founders_scarab`, `lucky_charm`, `jonos_bandana`.

**Limitations (part 3)**: the cistern masks/occluders are traced by hand+GrabCut, not pixel-perfect (a little leak above the back-left column and on rubble); the dais, bridge slab and stairs are treated as walkable floor (no height). The ghost's face is small and soft at 48x62. Not tested in the engine (no engine edits allowed). `part3/sheets/hero.jpg` is only the scale reference.
