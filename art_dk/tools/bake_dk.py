#!/usr/bin/env python3
"""Bake the Duelist Kingdom extras (captain, rival, tycoon) with the SAME code as the village NPCs (bake_npcs.py).
Sheets: art_dk/sheets/*.jpg (3x4 on magenta; hero.jpg is the scale reference).  Output: art_dk/baked/spr_<name>.bin + sheet_<name>.png
usage: python3 tools/bake_dk.py [captain rival tycoon]"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
os.environ.setdefault("SPR_OUT", os.path.join(ROOT, "baked"))
os.environ.setdefault("SPR_SHEETS", os.path.join(ROOT, "previews"))
sys.path.insert(0, HERE)
import bake_npcs as N
N.SH = os.path.join(ROOT, "sheets")
# the AI sheets draw the left AND right rows facing left: the right row is the mirrored left row
MIRROR = {(2, 0): (1, 0, True), (2, 1): (1, 1, True), (2, 2): (1, 2, True)}
N.SPECS.update({n: {"cells": dict(MIRROR)} for n in ("captain", "rival", "tycoon")})
# Mago.dev (2 outfits): the tee sheet back row step A is a side view -> mirror step B. InsetoKaiba: plain mirror spec
N.SPECS["mago_tee"] = {"cells": {**MIRROR, (3, 1): (3, 2, True)}}
N.SPECS["mago_robe"] = {"cells": {**MIRROR, (3, 1): (3, 2, True)}}
N.SPECS["inseto"] = {"cells": dict(MIRROR)}
# drop stray specks (generator noise / thin antenna wires) from the foreground mask: they would stretch a cell's bounding box and push the feet up
import numpy as np
from collections import deque
_load = N.load
def load(name, min_px=400):
    im, a = _load(name)
    H, W = a.shape; seen = np.zeros_like(a); out = a.copy()
    ys, xs = np.nonzero(a)
    for y0, x0 in zip(ys, xs):
        if seen[y0, x0]: continue
        q = deque([(y0, x0)]); seen[y0, x0] = True; comp = []
        while q:
            y, x = q.popleft(); comp.append((y, x))
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                yy, xx = y + dy, x + dx
                if 0 <= yy < H and 0 <= xx < W and a[yy, xx] and not seen[yy, xx]: seen[yy, xx] = True; q.append((yy, xx))
        if len(comp) < min_px:
            for y, x in comp: out[y, x] = False
    BANDS[id(out)] = row_bands(out)
    return im, out
N.load = load

# the AI sheets are not a perfect 4-row grid (boots of one row can spill 2-3 px into the next cell): cut rows at the emptiest line near each H/4 multiple
BANDS = {}
def row_bands(a):
    H = a.shape[0]; proj = a.sum(axis=1); b = [0]
    for k in range(1, 4):
        c = k * H // 4; lo, hi = c - 50, c + 50
        seg = proj[lo:hi]; z = np.nonzero(seg == seg.min())[0]
        b.append(lo + int(z[len(z) // 2]))
    return b + [H]
def cellbox(alpha, W, H, r, c):
    b = BANDS[id(alpha)]; cw = W // 3
    m = alpha[b[r]:b[r + 1], c * cw:(c + 1) * cw]
    ys, xs = np.nonzero(m)
    return xs.min(), ys.min(), xs.max(), ys.max()
def get_cell(im, alpha, r, c, flip=False, fix=None):
    W, H = im.size; cw = W // 3; b = BANDS[id(alpha)]
    x0, y0, x1, y1 = cellbox(alpha, W, H, r, c)
    sub = np.array(im.crop((c * cw + x0, b[r] + y0, c * cw + x1 + 1, b[r] + y1 + 1))).astype(np.float64)
    m = alpha[b[r] + y0:b[r] + y1 + 1, c * cw + x0:c * cw + x1 + 1].copy()
    if fix: sub, m = fix(sub, m)
    if flip: sub = sub[:, ::-1]; m = m[:, ::-1]
    return sub, m
N.cellbox = cellbox; N.get_cell = get_cell
if __name__ == "__main__":
    if len(sys.argv) == 1: sys.argv += ["captain", "rival", "tycoon", "mago_tee", "mago_robe", "inseto"]
    N.main()
