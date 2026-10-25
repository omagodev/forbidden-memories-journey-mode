# Village roads: Egyptian oasis paths instead of yellow bricks (t252u)
Everything is under `art_dk/village_roads/`. No other tree (snap_*, fork, painted_work) was edited; painted_work/bg_clean.png and bg_raw.jpg were only read.

**Comparison image: `comparison_before_after.png`** (before | A | B | diff mask). Close-up of the horizontal road: `comparison_zoom_horizontal_road.png`.

## What changed
Only the road pixels (yellow brick) were repainted, plus a thin yellow fringe at their border. Layout/size is identical: 1280x720, same road shape.
- Road mask: colour segmentation of the clean plate (hue 34-50, sat > 0.70, val > 0.78, one 104k px component) + geometric completion under the removed-palm smudges (horizontal road y 417-473, north road, south stub, west stub) -> `mask_road.png` (`mask_road_auto_only.png` = segmentation alone). 
- The north road crosses the river on the existing wooden bridge: that deck (rows < 112) is repainted as wooden planks in the left bridge's wood colour (both variants); rails/posts untouched.
- Worn edges: noisy alpha within ~5 px of the border + a few dirt-coloured spill pixels outside it (never over grass).
- **A** (`variants/bg_clean_A.png`, `bg_raw_A.png`): packed sand path, a little darker than the surrounding dirt, soft tonal blotches, grains, ~70 sparse sandstone flagstones with a thin shadow outline.
- **B** (`variants/bg_clean_B.png`, `bg_raw_B.png`): continuous flagstone path in warm sandstone (running bond, ~33x20 px slabs like the old brick cells, dirt joints, bevel highlights).
- Diff masks: `variants/diff_mask_A.png` / `diff_mask_B.png` (white = changed pixels, 12.8% of the picture, all inside the road mask + margin; 0 pixels changed elsewhere, so houses, palms, bushes, water, bridge rails are byte-identical).
- `bg_raw_*` is the same repaint on bg_raw.jpg (saved as PNG, lossless) but it never touches palm pixels (raw differs from clean there), because the pipeline cuts house occluders and palm sprites from the raw picture.
- Script: `roads.py` (needs `.venv/` = python with opencv-python-headless + scipy + numpy + Pillow; the venv is in this folder, run `.venv/bin/python roads.py`). To tune: tones in `variant_A`/`variant_B`, mask polygons in `road_mask()`.

## Engine pipeline output (ready to swap)
`out/A/` and `out/B/` hold the generated engine files, produced with copies of the existing scripts in `pipeline/` (`make_painted2.py`, `make_water.py`, `palm_masks.py`, `palms_def.py`; only the input/output paths and scratch dir changed). The same pipeline run on the ORIGINAL inputs is in `out/baseline/` and is **byte-identical** to `snap_painted_sprite2/mods/ow-poc/assets/*` (painted.raw, painted_col.bin, painted_palms.raw, painted_water.raw) and `painted_data.h`, which proves the standalone run reproduces the shipped files.

| file | A / B vs shipped |
|---|---|
| `assets/painted.raw` (66 background cells + 32 house-occluder cells) | changed (road) |
| `assets/painted_water.raw` | changed (the 11 water cells in the top strip also contain the north bridge/road pixels) |
| `assets/painted_palms.raw` | 53 texels changed (rim of palm P9, which overlaps the north road) |
| `assets/painted_col.bin` | identical (collision grid unchanged) |
| `painted_data.h` | identical (same cell counts / banks / occluder table) |
| water mask | identical |
So collision, occluder table, palm table, anchors, water cell list all keep their numbers; only texel data differs.
`out/A_decoded_from_painted_raw.png`, `out/B_decoded_from_painted_raw.png` = the background cells decoded back from painted.raw (sanity check, 555 colour, mean error ~4/255 vs the PNG).

## How the engine worker swaps one in (pick A or B)
```
V=/workspace/study/fmrecomp/art_dk/village_roads/out/B          # or out/A
M=<working tree>/mods/ow-poc
cp $V/assets/painted.raw $V/assets/painted_water.raw $V/assets/painted_palms.raw $M/assets/
# painted_col.bin and painted_data.h are identical; do not change (optional: cp $V/assets/painted_col.bin; cp $V/painted_data.h)
python3 tools/pc/build_mod.py --target i386 mods/ow-poc    # only needed if the .c changed; assets are data files loaded by the mod
```
Then redeploy assets into `tmp/pc/game32/mods/ow-poc/assets/` like `painted_work/deploy_anim2.sh` does. No code change. To regenerate from scratch (e.g. after editing `roads.py`):
```
cd art_dk/village_roads && .venv/bin/python roads.py
cd pipeline && export VR_TMP=$PWD/../out/_tmp VR_RAW=$PWD/../variants/bg_raw_B.png VR_CLEAN=$PWD/../variants/bg_clean_B.png
../.venv/bin/python make_painted2.py ../out/B && ../.venv/bin/python make_water.py ../out/B/assets 6
```
(`make_painted2.py` also needs `VR_TMP` as scratch; palm masks still come from the original painted_work/bg_raw.jpg, read-only, so palm shapes cannot move.)

## Limitations
- Road mask is segmentation + hand-set polygons; edges under the removed-palm smudges (west of x~480, y~430-470 and near P9 on the north road) come from the geometry, so they are straight where the original was hidden.
- Flagstones in A are procedural rectangles, not painted; B is regular. Neither is a GenerateImage repaint (kept the procedural route so every non-road pixel stays byte-identical). If a more hand-painted look is wanted, the mask can be fed to an inpainting pass quadrant by quadrant.
- Not tested in the engine (no engine edits allowed); the painted.raw decode check only verifies the data.
- The old clean plate still has the soft inpaint smudges where palms were removed (unchanged, hidden by the palm sprites).
