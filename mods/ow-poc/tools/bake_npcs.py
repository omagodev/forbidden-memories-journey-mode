#!/usr/bin/env python3
"""Bake the AI-painted 3x4 character sheets (rows: down, left, right, up; columns: idle, step A, step B, on a flat magenta
background) into the SPR1 sprite files the painted village loads (48x62 texels a frame, feet at (24,56), 1-texel outline).
All characters share ONE scale (the hero's), so heights stay in proportion.  usage: bake_npcs.py [hero simon teana jono guard]"""
import os, sys
import numpy as np
from PIL import Image, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bake_sprites as B
SH = os.path.join(HERE, "sprite_sheets")
OUT = os.environ.get("SPR_OUT", os.path.join(HERE, "..", "assets"))
ORDER = {0: "down", 1: "left", 2: "right", 3: "up"}
COLMAP = [0, 1, 0, 2, 0]          # idle, step A, idle, step B, idle (the walk cycle is frames 1..4)

def load(name):
    im = Image.open(os.path.join(SH, name + ".jpg")).convert("RGB")
    a = np.array(im).astype(int)
    bg = (a[..., 0] > 170) & (a[..., 1] < 110) & (a[..., 2] > 70) & (a[..., 0] - a[..., 1] > 110)
    am = Image.fromarray(((~bg) * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(5))
    return im, np.array(am) > 127

def cellbox(alpha, W, H, r, c):
    cw, ch = W // 3, H // 4
    m = alpha[r * ch:(r + 1) * ch, c * cw:(c + 1) * cw]
    ys, xs = np.nonzero(m)
    return xs.min(), ys.min(), xs.max(), ys.max()

def get_cell(im, alpha, r, c, flip=False, fix=None):
    """-> (rgb float HxWx3, mask bool HxW) cropped to the figure"""
    W, H = im.size; cw, ch = W // 3, H // 4
    x0, y0, x1, y1 = cellbox(alpha, W, H, r, c)
    sub = np.array(im.crop((c * cw + x0, r * ch + y0, c * cw + x1 + 1, r * ch + y1 + 1))).astype(np.float64)
    m = alpha[r * ch + y0:r * ch + y1 + 1, c * cw + x0:c * cw + x1 + 1].copy()
    if fix: sub, m = fix(sub, m)
    if flip: sub = sub[:, ::-1]; m = m[:, ::-1]
    return sub, m

def to_cell(sub, m, sc):
    h0, w0 = m.shape
    w, h = max(1, round(w0 * sc)), max(1, round(h0 * sc))
    mi = Image.fromarray((m * 255).astype(np.uint8))
    rgb = sub * (np.array(mi)[..., None] / 255.0)
    rs = np.array(Image.fromarray(rgb.astype(np.uint8)).resize((w, h), Image.BOX)).astype(np.float64)
    al = np.array(mi.resize((w, h), Image.BOX)).astype(np.float64) / 255.0
    col = rs / np.maximum(al[..., None], 1e-3)
    out_k = np.full((B.CH, B.CW), 255, np.uint8); out_rgb = np.zeros((B.CH, B.CW, 3))
    ox = B.FX - w // 2; oy = B.FY - h + 1
    if h > B.CH - 4 or w > B.CW: print("  warning: cell %dx%d exceeds the frame" % (w, h))
    for y in range(h):
        for x in range(w):
            X, Y = ox + x, oy + y
            if 0 <= X < B.CW and 0 <= Y < B.CH and al[y, x] >= 0.5:
                out_k[Y, X] = 0; out_rgb[Y, X] = np.clip(col[y, x], 0, 255)
    solid = out_k == 0
    pad = np.pad(solid, 1)
    near = pad[:-2, 1:-1] | pad[2:, 1:-1] | pad[1:-1, :-2] | pad[1:-1, 2:]
    out_k[(~solid) & near] = 254
    at = np.zeros((B.CH, B.CW, 7)); at[..., 4:7] = out_rgb
    return out_k, at

def paint_out_green(sub, m):
    """Simon's back view shows the green eye ornament that belongs to the front: paint the middle of the head as cream wrap"""
    H, W = m.shape
    sub = sub.copy()
    y0, y1, x0, x1 = int(H * 0.14), int(H * 0.40), int(W * 0.25), int(W * 0.75)
    reg = sub[y0:y1, x0:x1]
    cream = (reg[..., 0] > 205) & (reg[..., 1] > 185)
    reg[~cream & m[y0:y1, x0:x1]] = (238, 220, 142)
    return sub, m

# per character: which sheet cell feeds (row, col) -> (srcrow, srccol, flip), and an optional pixel fix for given rows
SPECS = {
    "hero": {}, "teana": {}, "simon": {"fix_rows": {3: paint_out_green}},
    "jono": {"cells": {(3, 1): (3, 2, True)}},                     # the sheet's back-view step A is a side view: mirror step B
    "guard": {"cells": {(2, 0): (1, 0, True), (2, 1): (1, 1, True), (2, 2): (1, 2, True)}},   # the sheet's right-facing row faces left
}

def main():
    which = sys.argv[1:] or list(SPECS)
    hero_im, hero_a = load("hero")
    W, H = hero_im.size
    hmax = max(cellbox(hero_a, W, H, r, c)[3] - cellbox(hero_a, W, H, r, c)[1] for r in range(4) for c in range(3))
    sc = 52.0 / hmax * (864 / W)
    print("hero sheet", W, H, "tallest", hmax, "scale", sc)
    for name in which:
        im, alpha = load(name)
        spec = SPECS[name]
        if im.size != hero_im.size: sc_n = sc * hero_im.size[0] / im.size[0]
        else: sc_n = sc
        tall = max(cellbox(alpha, im.size[0], im.size[1], r, c)[3] - cellbox(alpha, im.size[0], im.size[1], r, c)[1] + 1 for r in range(4) for c in range(3))
        if tall * sc_n > 56.0: sc_n = 56.0 / tall; print("  %s: scaled down to fit the frame (%.3f)" % (name, sc_n))
        cells = {}
        for r in range(4):
            for f, c0 in enumerate(COLMAP):
                sr, sc_, fl = spec.get("cells", {}).get((r, c0), (r, c0, False))
                fix = spec.get("fix_rows", {}).get(r)
                sub, m = get_cell(im, alpha, sr, sc_, fl, fix)
                cells[(ORDER[r], f)] = to_cell(sub, m, sc_n)
        B.write_bin(os.path.join(OUT, "spr_%s.bin" % name if name != "hero" else "spr_ai.bin"), cells, 4)
        B.contact(cells, 4, {}, True).save(os.path.join(os.environ.get("SPR_SHEETS", HERE), "sheet_%s.png" % name))
        print("baked", name)

if __name__ == "__main__":
    main()
