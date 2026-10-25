#!/usr/bin/env python3
"""Packs the part 3 art (art_dk/part3, read only) into the mod's assets.

  python3 tools/build_part3_assets.py [ART_DIR]

painted_cistern.raw      the Old Cistern as the village is stored: 4 banks of 128x128 cells (stride 126), the 11 x 6 picture cells
                         first, then the occluder cells (columns, jars, bridge rails: the picture cut by their polygon, 0 = transparent)
painted_cistern_occ.bin  u16 count, then per occluder cell: x0, y0, cell, base_y (u16 each)
painted_cistern_col.bin  320 x 180 bytes, 4 texels a cell, 1 = blocked
spr_rex.bin, spr_bakura.bin  the sprite sheets (SPR1), props and icons copied beside them
"""
import json, math, os, shutil, struct, sys
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
ART = (sys.argv[1] if len(sys.argv) > 1 else "/workspace/study/fmrecomp/art_dk") + "/part3"
OUT = os.path.join(MOD, "assets")
CELL, STRIDE = 128, 126
BW, BH = 1280, 720
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0 - 0.5


def to555(a):
    h, w, _ = a.shape
    ys, xs = np.mgrid[0:h, 0:w]
    th = BAYER[ys % 4, xs % 4]
    out = np.zeros((h, w), np.uint16)
    for c, sh in enumerate((0, 5, 10)):
        q = np.clip(np.floor(a[:, :, c] / 255.0 * 31.0 + th * 0.9 + 0.5), 0, 31).astype(np.uint16)
        out |= q << sh
    return out | 0x8000


def cut(img, mask, x0, y0):
    c = np.zeros((CELL, CELL), np.uint16)
    h = min(CELL, BH - y0); w = min(CELL, BW - x0)
    c[:h, :w] = img[y0:y0 + h, x0:x0 + w]
    if h < CELL: c[h:, :w] = img[BH - 1:BH, x0:x0 + w]
    if w < CELL: c[:, w:] = c[:, w - 1:w]
    if mask is not None:
        mk = np.zeros((CELL, CELL), bool)
        mk[:h, :w] = mask[y0:y0 + h, x0:x0 + w]
        c = np.where(mk, c, 0).astype(np.uint16)
    return c


def main():
    pic = np.array(Image.open(ART + "/backgrounds/dk_cistern_1280x720.jpg").convert("RGB")).astype(np.float32)
    tex = to555(pic)
    cells = []
    cols = math.ceil((BW - 1) / STRIDE); rows = math.ceil((BH - 1) / STRIDE)
    assert (cols, rows) == (11, 6)
    for r in range(rows):
        for c in range(cols):
            cells.append(cut(tex, None, c * STRIDE, r * STRIDE))
    occ = json.load(open(ART + "/masks/cistern_occluders.json"))
    table = []
    for o in occ["occluders"]:
        m = Image.new("L", (BW, BH), 0)
        ImageDraw.Draw(m).polygon([tuple(p) for p in o["polygon"]], fill=255)
        m = np.array(m) > 0
        ys, xs = np.nonzero(m)
        for r in range(ys.min() // STRIDE, ys.max() // STRIDE + 1):
            for c in range(xs.min() // STRIDE, xs.max() // STRIDE + 1):
                x0, y0 = c * STRIDE, r * STRIDE
                if m[y0:y0 + CELL, x0:x0 + CELL].sum() < 4: continue
                table.append((x0, y0, len(cells), int(o["base_y"])))
                cells.append(cut(tex, m, x0, y0))
    nb = math.ceil(len(cells) / 32)
    assert nb <= 4, "%d cells do not fit 4 banks" % len(cells)
    banks = np.zeros((4, 512, 1024), np.uint16)
    for i, c in enumerate(cells):
        b, k = divmod(i, 32)
        banks[b, (k // 8) * CELL:(k // 8 + 1) * CELL, (k % 8) * CELL:(k % 8 + 1) * CELL] = c
    with open(OUT + "/painted_cistern.raw", "wb") as f:
        f.write(struct.pack("<HHHH", 4, 0, 0, 0) + banks.tobytes())
    with open(OUT + "/painted_cistern_occ.bin", "wb") as f:
        f.write(struct.pack("<H", len(table)))
        for t in table: f.write(struct.pack("<HHHH", *t))
    walk = np.array(Image.open(ART + "/masks/cistern_walkable_320x180.png").convert("L")) > 127
    assert walk.shape == (180, 320)
    open(OUT + "/painted_cistern_col.bin", "wb").write((~walk).astype(np.uint8).tobytes())
    shutil.copy(ART + "/baked/spr_rex_raptor.bin", OUT + "/spr_rex.bin")
    shutil.copy(ART + "/baked/spr_bakura_ghost.bin", OUT + "/spr_bakura.bin")
    for n in ("hatch_closed", "hatch_open", "torch_glow"):
        shutil.copy(ART + "/overlays/prop_%s.raw" % n, OUT + "/prop_%s.raw" % n)
    for n in ("founders_scarab", "lucky_charm", "jonos_bandana"):
        shutil.copy(ART + "/icons/icon_%s_24x24.bin" % n, OUT + "/icon_%s.bin" % n)
    print("cistern: %d cells (%d picture + %d occluder) in %d banks, %d blocked of %d collision cells" % (len(cells), 66, len(table), nb, int((~walk).sum()), walk.size))


main()
