# Character creator layers (chargen) - data format "journey-chargen-1"

The hero of Journey Mode is assembled at run time from layer files made by the art pipeline (`art_dk/chargen`, `import_chargen.py` copies
manifest + packed layers into `assets/chargen/`).  The creator (NEW GAME) cycles the categories, the choice is saved in journey.sav
(`Journey.cg[8]`, `cg_set`, save version 4) and the painted village draws the hero from the same layers (`jm_chargen.c`, `Cg_Compose`;
the hero's page is bank 13 page 2, the creator preview and the painted sprite share it).

## manifest.json
* `frame`: 48x62 texels, anchor (24,56), 5 frames per direction (0 idle, 1 step A, 2 idle, 3 step B, 4 idle), directions down,left,right,up.
* `draw_order`: ["body","outfit","hair","accessory"] - later layers overwrite, an empty texel leaves what is below.
* `outline_rgb`: colour of the outline texels (34,24,30).
* `palettes.skin[]`, `palettes.hair[]`: `{name, rgb}`.
* `parts.body.base`, `parts.outfit.<style>`, `parts.hair.<style>`, `parts.accessory.<style|none>`: `{packed: "packed/x.cgp1", slots: {"1": "skin", "2": "hair", "3": "outfit.main", ...}}`;
  outfit and accessory styles also carry `colourways[]` (`{name, main, trim, trousers}` / `{name, a, b}`).
* `avoid_combinations[]`: `{hair, accessory}` pairs the creator skips while cycling.
* Colour of a texel: `clip(rgb + sum_q W_q/100 * palette[q] + 0.5)` where palette[q] is the colour the style's slot q is mapped to (the same
  formula as `spr_bake()` in jm_painted.c).

## Packed layer `*.cgp1` (magic `CGP1`)
```
"CGP1" u8 frames(5) u8 w(48) u8 h(62) u16 ndesc      9 bytes
ndesc x { u8 kind, u8 W1..W4, u8 r, u8 g, u8 b }       descriptors (index 2..), 8 bytes each
20 x { u8 x0, y0, w, h ; w*h bytes }                   [direction][frame], bounding box; byte 0 = empty, 1 = outline, n>=2 = descriptor n-2
```
Size on disk: 15 layers, 183 KB in total (the raw SPR1 layers are 7.1 MB).

## Budget
One hero = one 256x256 RGB555 page (5 x 48 = 240 wide, 4 x 64 = 256 high).  Packed layers stay in memory (<= 32 layers), the page is composed on the
CPU only when the choice changes (<= 4 layers x 20 frames x 48x62 texels).
