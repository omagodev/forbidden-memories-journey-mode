#!/usr/bin/env python3
"""Generate assets/atlas.raw, Journey Mode's one texture sheet, with no outside art
except the five 48x48 portraits (made for this project).

The sheet is 768 x 256 pixels of RGB555 (bit 15 set where a pixel is solid, so
0 is transparent), written as u16 width, u16 height, then the pixels.  It is
loaded into texture bank 14 at (0, 0) and read through three texture pages:

  page 0, x 0..255    sixteen 64x64 ground and wall tiles (TILE_* order below)
  page 1, x 256..511  sprites: bushes, papyrus, oleander, fern palm, tufts,
                      flowers, a palm tree, a shadow
  page 2, x 512..767  portraits, 48x48 each: four for the player, the Prince,
                      then two slots the game fills at run time; below them
                      the textures and props of make_props.py

Usage: make_atlas.py PORTRAITS_DIR [out.raw]   (p1..p4.png, prince.png there)
       make_atlas.py --props [atlas.raw]       (only redraw the page 2 block below the portraits)
Needs numpy and Pillow.
"""
import math
import os
import random
import struct
import sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
T = 64
rng = np.random.default_rng(11)
R = random.Random(5)


def noise(size, cells, octaves=3, seed=0):
    """Tileable value noise in 0..1."""
    r = np.random.default_rng(seed)
    out = np.zeros((size, size))
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        c = cells * (2 ** o)
        g = r.random((c, c))
        # bilinear upsample with wraparound
        xs = np.arange(size) * c / size
        i0 = np.floor(xs).astype(int) % c
        i1 = (i0 + 1) % c
        f = xs - np.floor(xs)
        f = f * f * (3 - 2 * f)
        a = g[np.ix_(i0, i0)]
        b = g[np.ix_(i0, i1)]
        cc = g[np.ix_(i1, i0)]
        d = g[np.ix_(i1, i1)]
        fx = f[None, :]
        fy = f[:, None]
        v = (a * (1 - fx) + b * fx) * (1 - fy) + (cc * (1 - fx) + d * fx) * fy
        out += v * amp
        tot += amp
        amp *= 0.5
    return out / tot


def tint(base, n, spread):
    base = np.array(base, float)
    return np.clip(base[None, None, :] * (1 + (n[:, :, None] - 0.5) * spread), 0, 255)


def sand(seed, pebbles=0, ripples=False):
    n = noise(T, 4, 4, seed)
    img = tint((214, 178, 118), n, 0.34)
    r = np.random.default_rng(seed)
    sp = r.random((T, T))
    img[sp < 0.05] *= 0.86
    img[sp > 0.96] *= 1.10
    if ripples:
        yy = np.arange(T)[:, None]
        xx = np.arange(T)[None, :]
        w = np.sin((yy * 0.55 + np.sin(xx * 0.18 + seed) * 2.2)) * 0.5 + 0.5
        img *= (0.93 + 0.12 * w)[:, :, None]
    im = Image.fromarray(np.clip(img, 0, 255).astype("uint8"))
    d = ImageDraw.Draw(im)
    for _ in range(pebbles):
        x, y = r.integers(2, T - 4, 2)
        d.ellipse((x, y, x + 2, y + 1), fill=(150, 125, 90))
        d.point((x, y), fill=(190, 165, 125))
    return im


def cracked(seed):
    n = noise(T, 4, 3, seed)
    img = tint((190, 148, 96), n, 0.4)
    im = Image.fromarray(img.astype("uint8"))
    d = ImageDraw.Draw(im)
    r = random.Random(seed)
    for _ in range(7):
        x, y = r.randint(0, T), r.randint(0, T)
        for _ in range(9):
            nx, ny = x + r.randint(-7, 7), y + r.randint(-7, 7)
            d.line((x, y, nx, ny), fill=(112, 82, 52))
            x, y = nx, ny
    return im


def glyph(d, x, y, kind, col):
    if kind == 0:      # eye
        d.ellipse((x, y + 2, x + 8, y + 7), outline=col)
        d.ellipse((x + 3, y + 3, x + 5, y + 5), fill=col)
        d.line((x + 1, y + 8, x + 7, y + 10), fill=col)
    elif kind == 1:    # ankh
        d.ellipse((x + 1, y, x + 6, y + 5), outline=col)
        d.line((x + 3, y + 5, x + 3, y + 12), fill=col)
        d.line((x, y + 8, x + 7, y + 8), fill=col)
    elif kind == 2:    # waves
        for k in range(3):
            d.line([(x + i, y + k * 3 + (1 if (i // 2) % 2 else 0)) for i in range(9)], fill=col)
    elif kind == 3:    # bird
        d.polygon([(x, y + 6), (x + 5, y + 2), (x + 9, y + 5), (x + 5, y + 8)], outline=col)
        d.line((x + 9, y + 5, x + 11, y + 3), fill=col)
        d.line((x + 3, y + 8, x + 3, y + 11), fill=col)
    elif kind == 4:    # sun
        d.ellipse((x + 1, y + 1, x + 8, y + 8), outline=col)
        d.point((x + 4, y + 4), fill=col)
    else:              # reed
        d.line((x + 4, y + 11, x + 4, y), fill=col)
        d.line((x + 4, y + 3, x + 1, y), fill=col)
        d.line((x + 4, y + 3, x + 8, y + 1), fill=col)


def path_tile(seed):
    n = noise(T, 4, 3, seed)
    img = tint((226, 182, 74), n, 0.28)
    im = Image.fromarray(img.astype("uint8"))
    d = ImageDraw.Draw(im)
    r = random.Random(seed)
    for gx in range(2):
        for gy in range(2):
            x0, y0 = gx * 32, gy * 32
            d.rectangle((x0, y0, x0 + 31, y0 + 31), outline=(150, 108, 38))
            d.line((x0 + 1, y0 + 1, x0 + 30, y0 + 1), fill=(246, 214, 118))
            d.line((x0 + 1, y0 + 1, x0 + 1, y0 + 30), fill=(246, 214, 118))
            glyph(d, x0 + 9 + r.randint(-2, 2), y0 + 9, r.randint(0, 5), (132, 92, 30))
    return im


def water(seed, shift):
    n = noise(T, 4, 3, seed)
    img = tint((52, 118, 196), n, 0.42)
    yy = np.arange(T)[:, None]
    xx = np.arange(T)[None, :]
    w = np.sin(xx * 0.35 + yy * 0.18 + shift) + np.sin(xx * 0.12 - yy * 0.31 + shift * 0.7)
    img *= (0.9 + 0.1 * w)[:, :, None]
    img[w > 1.55] = img[w > 1.55] * 0.5 + np.array([200, 230, 255]) * 0.5
    return Image.fromarray(np.clip(img, 0, 255).astype("uint8"))


def blocks(base, light, dark, rows, seed, top=False):
    n = noise(T, 4, 3, seed)
    img = tint(base, n, 0.22)
    im = Image.fromarray(img.astype("uint8"))
    d = ImageDraw.Draw(im)
    h = T // rows
    r = random.Random(seed)
    for k in range(rows):
        y = k * h
        d.line((0, y, T, y), fill=dark)
        d.line((0, y + 1, T, y + 1), fill=light)
        off = r.randint(0, 20) if not top else 0
        for x in range(off, T + 20, 22):
            d.line((x % T, y, x % T, y + h), fill=dark)
    return im


def marble(seed):
    n = noise(T, 3, 4, seed)
    img = tint((222, 224, 232), n, 0.16)
    im = Image.fromarray(img.astype("uint8"))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, T - 1, T - 1), outline=(176, 142, 62))
    d.rectangle((3, 3, T - 4, T - 4), outline=(150, 160, 190))
    d.line((0, 0, T, T), fill=(206, 208, 220))
    return im


def lapis(seed):
    n = noise(T, 4, 3, seed)
    img = tint((40, 62, 140), n, 0.3)
    im = Image.fromarray(img.astype("uint8"))
    d = ImageDraw.Draw(im)
    for y in (4, 30, 58):
        d.rectangle((0, y, T, y + 3), fill=(212, 170, 60))
    for x in range(6, T, 14):
        d.polygon([(x, 10), (x + 4, 22), (x - 4, 22)], fill=(222, 184, 74))
    return im


def arena_tile():
    im = Image.new("RGB", (T, T), (226, 184, 82))
    d = ImageDraw.Draw(im)
    d.ellipse((4, 4, T - 5, T - 5), outline=(150, 100, 28), width=3)
    d.ellipse((14, 14, T - 15, T - 15), outline=(150, 100, 28), width=2)
    for k in range(8):
        a = k * math.pi / 4
        d.line((T / 2 + math.cos(a) * 12, T / 2 + math.sin(a) * 12, T / 2 + math.cos(a) * 27, T / 2 + math.sin(a) * 27), fill=(150, 100, 28))
    d.ellipse((26, 26, 37, 37), fill=(196, 58, 40))
    return im


def glow():
    yy, xx = np.mgrid[0:T, 0:T]
    r = np.sqrt((xx - 31.5) ** 2 + (yy - 31.5) ** 2) / 32
    v = np.clip(1.15 - r, 0, 1)
    img = np.stack([120 + 135 * v, 200 + 55 * v, 255 * np.ones_like(v)], -1) * (0.55 + 0.45 * v)[:, :, None]
    return Image.fromarray(np.clip(img, 0, 255).astype("uint8"))


def granite(seed):
    n = noise(T, 5, 4, seed)
    img = tint((92, 38, 44), n, 0.45)
    im = Image.fromarray(img.astype("uint8"))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, T - 1, T - 1), outline=(40, 14, 20))
    d.line((0, 1, T, 1), fill=(150, 80, 70))
    return im


def oasis(seed):
    n = noise(T, 5, 4, seed)
    img = tint((98, 150, 64), n, 0.5)
    im = Image.fromarray(img.astype("uint8"))
    d = ImageDraw.Draw(im)
    r = random.Random(seed)
    for _ in range(40):
        x, y = r.randint(0, T - 2), r.randint(2, T - 1)
        d.line((x, y, x + r.randint(-2, 2), y - r.randint(2, 4)), fill=(60, 110, 42))
    return im


TILES = [sand(1, 6), sand(2, 14), sand(3, 3, True), cracked(4),
         path_tile(5), path_tile(9), water(6, 0.0), water(6, 2.1),
         blocks((206, 168, 108), (232, 200, 142), (140, 104, 62), 2, 8, True),
         blocks((184, 142, 88), (214, 176, 118), (116, 82, 48), 4, 9),
         marble(10), lapis(11), arena_tile(), glow(), granite(12), oasis(13)]


def rgb555(img):
    a = np.array(img.convert("RGBA"))
    r, g, b, al = a[:, :, 0] >> 3, a[:, :, 1] >> 3, a[:, :, 2] >> 3, a[:, :, 3]
    px = (r.astype(np.uint16) | (g.astype(np.uint16) << 5) | (b.astype(np.uint16) << 10))
    return np.where(al > 127, px | 0x8000, 0).astype(np.uint16)


def sprites():
    """Page 1 (x 256..511): the vegetation of make_veg.py plus a palm and a shadow."""
    sys.path.insert(0, HERE)
    cwd = os.getcwd()
    tmp = os.path.join(HERE, "..", "..", "..", "tmp", "pc", "journey-veg")
    os.makedirs(tmp, exist_ok=True)
    os.chdir(tmp)
    import make_veg  # noqa: F401  (writes veg_atlas.png, veg_small.png, veg_palm.png)
    atlas = Image.open("veg_atlas.png").convert("RGBA")
    small = Image.open("veg_small.png").convert("RGBA")
    far = Image.open("veg_palm.png").convert("RGBA")
    os.chdir(cwd)
    page = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    page.paste(atlas, (0, 0))               # 4 sprites, 32x40 each
    page.paste(small, (128, 0))             # tufts (16x16 x2), flowers (16x8 x2)
    page.paste(far, (160, 0))               # far palm 32x40
    # a tall palm, 64 x 96, drawn big so it stays crisp at the internal scale
    palm = Image.new("RGBA", (64, 96), (0, 0, 0, 0))
    d = ImageDraw.Draw(palm)
    pts = [(32 + math.sin(t / 18.0) * 5, 94 - t) for t in range(0, 64)]
    for i, (x, y) in enumerate(pts):
        w = 3.2 - i * 0.015
        d.line((x - w, y, x + w, y), fill=(128, 90, 48, 255) if (i // 4) % 2 else (96, 64, 34, 255))
    tx, ty = pts[-1]
    G = [(122, 176, 62, 255), (80, 134, 46, 255), (46, 88, 32, 255)]
    for i in range(11):
        a = math.pi + 0.1 + i * (math.pi - 0.2) / 10
        L = 30 + R.uniform(-3, 2)
        q = [(tx + math.cos(a) * t * L, ty + math.sin(a) * t * L * 0.7 + t * t * 18) for t in [k / 9 for k in range(10)]]
        d.line(q, fill=G[i % 2], width=4)
        d.line(q[3:], fill=G[2], width=1)
    d.ellipse((tx - 4, ty - 2, tx + 4, ty + 5), fill=(112, 62, 30, 255))
    page.paste(palm, (192, 0), palm)
    # shadow blob 32x16 at (0,100), semi-dark ellipse
    sh = Image.new("RGBA", (32, 16), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse((1, 1, 30, 14), fill=(40, 28, 20, 255))
    page.paste(sh, (0, 100))
    return page


def patch_props():
    """Redraw the textures and props of make_props.py in an existing atlas, keeping the rest."""
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "assets", "atlas.raw")
    raw = open(out, "rb").read()
    w, h = struct.unpack("<HH", raw[:4])
    sheet = np.frombuffer(raw[4:], np.uint16).reshape(h, w).copy()
    sys.path.insert(0, HERE)
    import make_props
    sheet[48:256, 512:768] = rgb555(make_props.extras())
    open(out, "wb").write(struct.pack("<HH", w, h) + sheet.tobytes())
    print("atlas.raw props redrawn")


def main():
    if sys.argv[1] == "--props":
        return patch_props()
    ports = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "assets", "atlas.raw")
    sheet = np.zeros((256, 768), np.uint16)
    for i, t in enumerate(TILES):
        x, y = (i % 4) * T, (i // 4) * T
        sheet[y:y + T, x:x + T] = rgb555(t.convert("RGBA"))
    sheet[:, 256:512] = rgb555(sprites())
    sys.path.insert(0, HERE)
    import make_props
    sheet[48:256, 512:768] = rgb555(make_props.extras())
    for i, n in enumerate(["p1", "p2", "p3", "p4", "prince"]):
        im = Image.open(os.path.join(ports, n + ".png")).convert("RGBA").resize((48, 48))
        sheet[0:48, 512 + i * 48:512 + (i + 1) * 48] = rgb555(im)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "wb") as f:
        f.write(struct.pack("<HH", 768, 256) + sheet.tobytes())
    Image.fromarray(np.array(Image.new("RGB", (768, 256)))).save("/dev/null", "PNG") if False else None
    # a preview next to the raw file for review
    a = sheet
    prev = np.zeros((256, 768, 4), np.uint8)
    prev[:, :, 0] = (a & 31) << 3
    prev[:, :, 1] = ((a >> 5) & 31) << 3
    prev[:, :, 2] = ((a >> 10) & 31) << 3
    prev[:, :, 3] = np.where(a & 0x8000, 255, 0)
    Image.fromarray(prev).save(os.path.join(os.path.dirname(out), "..", "..", "..", "tmp", "pc", "journey-atlas.png"))
    print("atlas.raw", os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
