#!/usr/bin/env python3
"""Part 3 sprites: Rex Raptor (normal painted bake) and Bakura ghost (hover + dithered ghost look: texel 0 is the only transparency in the engine,
so 'translucent' = pale blue tint + ordered-dither holes that get denser towards the hem, and the figure is lifted 5 texels so it hovers).
Same pipeline/format as ../tools/bake_dk.py (SPR1, 48x62, 4 dirs x idle + 4-step walk).
usage: python3 tools/bake_p3.py [rex_raptor bakura_ghost]   -> baked/spr_<name>.bin, previews/sheet_<name>.png"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
os.environ.setdefault("SPR_OUT", os.path.join(ROOT, "baked")); os.environ.setdefault("SPR_SHEETS", os.path.join(ROOT, "previews"))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, "..", "tools"))
import bake_dk as D          # reuses the speck filter + row cutting + MIRROR
N = D.N; B = N.B
N.SH = os.path.join(ROOT, "sheets")
N.SPECS["rex_raptor"] = {"cells": dict(D.MIRROR)}
N.SPECS["bakura_ghost"] = {"cells": dict(D.MIRROR)}
CUR = [None]
_load = N.load
def load(name, **k): CUR[0] = name; return _load(name, **k)
N.load = load
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0
GHOST_TINT = np.array([196, 214, 246.0]); HOVER = 5
_to_cell = N.to_cell
def to_cell(sub, m, sc):
    if CUR[0] != "bakura_ghost": return _to_cell(sub, m, sc)
    kind, at = _to_cell(sub, m, sc * 0.89)          # ghost is drawn smaller so the 5-texel hover lift still fits the 62-texel frame
    kind = kind.copy(); at = at.copy()
    # outline texels become pale-blue body texels (a dark outline would kill the ghost look)
    ol = kind == 254; kind[ol] = 0; at[ol, 4:7] = (84, 98, 150); at[ol, :4] = 0
    solid = kind == 0
    rgb = at[..., 4:7]; rgb[solid] = 0.74 * rgb[solid] + 0.26 * GHOST_TINT
    # hover: lift the figure
    kind = np.roll(kind, -HOVER, axis=0); at = np.roll(at, -HOVER, axis=0); kind[-HOVER:] = 255; at[-HOVER:] = 0
    solid = kind == 0
    ys, xs = np.nonzero(solid)
    if len(ys):
        y0, y1 = ys.min(), ys.max(); yy, xx = np.mgrid[0:kind.shape[0], 0:kind.shape[1]]
        t = np.clip((yy - y0) / max(1, y1 - y0), 0, 1)
        p = 0.04 + 0.80 * np.clip((t - 0.30) / 0.70, 0, 1) ** 1.3        # drop probability: head solid, body faintly see-through, dense at the hem
        p[t < 0.30] = 0.0
        hole = BAYER[yy % 4, xx % 4] < p
        kind[solid & hole] = 255; at[solid & hole] = 0
    return kind, at
N.to_cell = to_cell
if __name__ == "__main__":
    if len(sys.argv) == 1: sys.argv += ["rex_raptor", "bakura_ghost"]
    N.main()
