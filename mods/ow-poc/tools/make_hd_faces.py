#!/usr/bin/env python3
"""High-resolution talk faces (168x168) for the people whose map sheet was baked from a large source sheet (864x1152, 3x4 cells).
The window is the 48x48 preset's own head-and-shoulders window (make_talk_faces.py framing on the 48x62 map cell), mapped back
through the bake's figure box into the source cell (down, standing), so the face is the same drawing as the map sprite, only from
the source pixels.  Writes assets/faces/<name>.hface (168*168 little-endian RGB555|0x8000) and png previews.
Sheets without a large source keep their 48x48 .face."""
import os, sys, struct
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import make_talk_faces as T
import bake_npcs as N
REPO = os.path.join(HERE, '..', '..', '..')
SRC = {'simon': 'mods/ow-poc/tools/sprite_sheets/simon.jpg', 'teana': 'mods/ow-poc/tools/sprite_sheets/teana.jpg',
       'jono': 'mods/ow-poc/tools/sprite_sheets/jono.jpg', 'guard': 'mods/ow-poc/tools/sprite_sheets/guard.jpg',
       'inseto': 'art_dk/sheets/inseto.jpg', 'mago_robe': 'art_dk/sheets/mago_robe.jpg', 'rival': 'art_dk/sheets/rival.jpg',
       'rex': 'art_dk/part3/sheets/rex_raptor.jpg', 'bakura': 'art_dk/part3/sheets/bakura_ghost.jpg'}
HF, FR = 168, 3

def window(img, name):
    """the 48px preset's window (left, top, side) in map-cell pixels, as make_talk_faces.face() frames it"""
    bb = img.getbbox(); x0, y0, x1, y1 = bb; fig_h = y1 - y0; a = img.split()[3]
    cs, ws = [], []
    for y in range(y0 + 2, y0 + max(8, int(fig_h * 0.3))):
        best, run, start = (0, 0), 0, 0
        for x in range(img.width + 1):
            if x < img.width and a.getpixel((x, y)):
                if not run: start = x
                run += 1
            else:
                if run > best[0]: best = (run, start)
                run = 0
        if best[0]: cs.append(best[1] + best[0] / 2); ws.append(best[0])
    cs.sort(); cx = cs[len(cs) // 2]; hw = max(ws)
    side = max(int(cx + hw / 2) - int(cx - hw / 2) + 8, int(fig_h * 0.46))
    side = min(T.SIDE.get(name, side), img.width, fig_h)
    return int(round(cx - side / 2)), y0 - max(1, side // 10), side, bb

def build(name):
    spr = T.load(os.path.join(T.ROOT, 'spr_%s.bin' % name))
    left, top, side, (bx0, by0, bx1, by1) = window(spr, name)
    im, alpha = N.load(os.path.splitext(os.path.basename(SRC[name]))[0]) if False else (None, None)
    im = Image.open(os.path.join(REPO, SRC[name])).convert('RGB')
    a = np.array(im).astype(int)
    bg = (a[..., 0] > 170) & (a[..., 1] < 110) & (a[..., 2] > 70) & (a[..., 0] - a[..., 1] > 110)
    from PIL import ImageFilter
    am = Image.fromarray(((~bg) * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(5))
    alpha = np.array(am) > 127
    sx0, sy0, sx1, sy1 = N.cellbox(alpha, im.width, im.height, 0, 0)
    sc = (sy1 - sy0 + 1) / (by1 - by0)                   # source pixels per map pixel (the bake's one scale)
    cxs = (sx0 + sx1 + 1) / 2 - (bx0 + bx1) / 2 * sc      # x offset: the figure centres line up
    L, Tp, S = left * sc + cxs, sy0 + (top - by0) * sc, side * sc
    box = (int(round(L)), int(round(Tp)), int(round(L + S)), int(round(Tp + S)))
    cw, ch = im.width // 3, im.height // 4
    cell = Image.new('RGBA', (cw, ch), (0, 0, 0, 0))
    rgba = im.crop((0, 0, cw, ch)).convert('RGBA'); rgba.putalpha(Image.fromarray((alpha[:ch, :cw] * 255).astype(np.uint8)))
    cell.paste(rgba, (0, 0))
    crop = cell.crop(box)
    n = HF - 2 * FR
    fig = crop.resize((n, n), Image.LANCZOS)
    fa = np.array(fig.split()[3]) >= 128
    out = Image.new('RGB', (HF, HF))
    for y in range(HF):
        t = y / (HF - 1); out.paste(tuple(int(T.BG_TOP[i] * (1 - t) + T.BG_BOT[i] * t) for i in range(3)), (0, y, HF, y + 1))
    pad = np.pad(fa, 1); rim = (~fa) & (pad[:-2, 1:-1] | pad[2:, 1:-1] | pad[1:-1, :-2] | pad[1:-1, 2:])
    o = np.array(out); f = np.array(fig.convert('RGB'))
    inner = o[FR:FR + n, FR:FR + n]; inner[rim] = (34, 24, 30); inner[fa] = f[fa]
    for i in range(FR):
        col = (240, 200, 90) if i == 1 else (170, 128, 40)
        o[i, :] = o[HF - 1 - i, :] = o[:, i] = o[:, HF - 1 - i] = col
    out = Image.fromarray(o)
    out.save(os.path.join(T.OUT, 'png', name + '_hd.png'))
    b = bytearray()
    for r, g, bl in np.array(out).reshape(-1, 3).tolist(): b += struct.pack('<H', 0x8000 | (r >> 3) | (g >> 3) << 5 | (bl >> 3) << 10)
    open(os.path.join(T.OUT, name + '.hface'), 'wb').write(b)
    print('%-10s map window %2dpx -> source window %dpx (%.2f src px per map px) -> %d texels' % (name, side, box[2] - box[0], sc, HF))

if __name__ == '__main__':
    for k in (sys.argv[1:] or SRC): build(k)
