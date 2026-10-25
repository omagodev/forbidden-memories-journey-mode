#!/usr/bin/env python3
"""Grass, the bridge planks and small props for the atlas: textures and sprites drawn here, no outside art.
(The houses, fences, stalls and rocks are meshes: see bake_kenney.py.)

Page 2 (x 512..767) holds the portraits in its top 48 rows.  Below them:
  y 48..175   64x64 textures, index 16.. of the texture list (TX_* in jm.h), four to a row
  y 176..255  small sprites (SPR_* rectangles in jm.h)
"""
import math
import random

import numpy as np
from PIL import Image, ImageDraw

T = 64


def noise(size, cells, seed):
    r = np.random.default_rng(seed)
    g = r.random((cells, cells))
    xs = np.arange(size) * cells / size
    i0 = np.floor(xs).astype(int) % cells
    i1 = (i0 + 1) % cells
    f = xs - np.floor(xs)
    f = f * f * (3 - 2 * f)
    a, b, c, d = g[np.ix_(i0, i0)], g[np.ix_(i0, i1)], g[np.ix_(i1, i0)], g[np.ix_(i1, i1)]
    return (a * (1 - f[None, :]) + b * f[None, :]) * (1 - f[:, None]) + (c * (1 - f[None, :]) + d * f[None, :]) * f[:, None]


def shade(base, seed, spread=0.18, cells=6):
    n = noise(T, cells, seed)
    arr = np.array(base, float)[None, None, :] * (1 + (n[:, :, None] - 0.5) * spread)
    return Image.fromarray(np.clip(arr, 0, 255).astype("uint8")).convert("RGBA")





def grass(seed):
    im = shade((88, 164, 58), seed, 0.30, 8)
    d = ImageDraw.Draw(im)
    r = random.Random(seed)
    for _ in range(90):
        x, y = r.randint(1, T - 2), r.randint(3, T - 1)
        c = (58, 126, 40, 255) if r.random() < 0.6 else (130, 200, 80, 255)
        d.line((x, y, x + r.randint(-1, 1), y - r.randint(2, 4)), fill=c)
    return im


def plank(seed):
    im = shade((176, 124, 70), seed, 0.16, 6)
    d = ImageDraw.Draw(im)
    for y in range(0, T, 16):
        d.line((0, y, T, y), fill=(98, 64, 34, 255))
        d.line((0, y + 1, T, y + 1), fill=(204, 154, 94, 255))
    r = random.Random(seed)
    for y in range(0, T, 16):
        x = r.randint(8, 56)
        d.line((x, y, x, y + 15), fill=(110, 74, 40, 255))
        d.point((x + 3, y + 7), fill=(84, 54, 28, 255))
    return im



def neutral(seed, mean=206, spread=0.12, cells=5):
    n = noise(T, cells, seed)
    v = mean * (1 + (n - 0.5) * spread * 2)
    arr = np.stack([v, v, v], -1)
    return arr


def to_img(arr):
    return Image.fromarray(np.clip(arr, 0, 255).astype("uint8")).convert("RGBA")


# Textures for the faces of the Kenney meshes.  They are light grey on purpose: the mod multiplies them by the
# face colour (the kit's palette colour with the sun baked in) so the hue stays the kit's and only the
# surface detail is painted here.
def plaster(seed):
    arr = neutral(seed, 214, 0.10, 6)
    r = np.random.default_rng(seed)
    sp = r.random((T, T))
    arr[sp < 0.06] *= 0.90
    arr[sp > 0.95] *= 1.05
    for y in (21, 42):                                     # courses of stone
        arr[y, :, :] *= 0.80
        arr[y + 1, :, :] *= 1.04
    for row, y0 in enumerate((0, 22, 43)):
        off = (row * 19 + seed) % 32
        for x in (off, off + 32):
            arr[y0:y0 + 21, x % T, :] *= 0.84
    return to_img(arr)


def roof_tiles(seed):
    arr = neutral(seed, 208, 0.06, 4)
    r = np.random.default_rng(seed)
    for row in range(8):
        y0 = row * 8
        off = 8 if row & 1 else 0
        for k in range(-1, 5):
            x0 = off + k * 16
            f = 0.90 + r.random() * 0.14
            for x in range(max(0, x0), min(T, x0 + 16)):
                arr[y0:y0 + 8, x, :] *= f
                arr[y0 + 6:y0 + 8, x, :] *= 0.86          # the shadow under a tile
            if 0 <= x0 < T:
                arr[y0:y0 + 8, x0, :] *= 0.80
        arr[y0, :, :] *= 1.06
    return to_img(arr)


def wood_planks(seed):
    arr = neutral(seed, 210, 0.08, 8)
    r = np.random.default_rng(seed)
    for x in range(0, T, 16):                              # vertical boards
        arr[:, x, :] *= 0.72
        arr[:, (x + 1) % T, :] *= 1.06
        for _ in range(5):
            gx = x + int(r.integers(3, 14))
            y = int(r.integers(0, T - 14))
            arr[y:y + int(r.integers(6, 16)), gx, :] *= 0.88
    for y in (int(r.integers(10, 24)), int(r.integers(40, 56))):
        for x in range(0, T, 16):
            arr[y:y + 2, x + 6:x + 8, :] *= 0.70           # nails
    return to_img(arr)


def sand_q(seed, ripples):
    """Sand with grain, pebbles with a highlight and a shadow, and faint ripples."""
    base = np.array((214, 178, 118), float)
    n = 0.6 * noise(T, 3, seed) + 0.4 * noise(T, 9, seed + 1)
    arr = base[None, None, :] * (1 + (n[:, :, None] - 0.5) * 0.30)
    r = np.random.default_rng(seed)
    sp = r.random((T, T))
    arr[sp < 0.10] *= 0.84
    arr[sp > 0.93] *= 1.10
    if ripples:
        yy, xx = np.arange(T)[:, None], np.arange(T)[None, :]
        w = np.sin(yy * 0.6 + np.sin(xx * 0.2 + seed) * 2.0) * 0.5 + 0.5
        arr *= (0.92 + 0.14 * w)[:, :, None]
    im = to_img(arr)
    d = ImageDraw.Draw(im)
    for _ in range(9):
        x, y = int(r.integers(3, T - 6)), int(r.integers(3, T - 6))
        d.ellipse((x + 1, y + 1, x + 4, y + 3), fill=(128, 100, 66, 255))
        d.ellipse((x, y, x + 3, y + 2), fill=(176, 150, 112, 255))
        d.point((x, y), fill=(222, 202, 160, 255))
    return im


def grass_q(seed):
    base = np.array((84, 160, 56), float)
    n = 0.5 * noise(T, 4, seed) + 0.5 * noise(T, 12, seed + 3)
    im = to_img(base[None, None, :] * (1 + (n[:, :, None] - 0.5) * 0.42))
    d = ImageDraw.Draw(im)
    r = random.Random(seed)
    for _ in range(220):
        x, y = r.randint(1, T - 2), r.randint(3, T - 1)
        c = r.choice([(52, 116, 38, 255), (62, 132, 44, 255), (120, 190, 76, 255), (150, 212, 96, 255)])
        d.line((x, y, x + r.randint(-1, 1), y - r.randint(2, 5)), fill=c)
    for _ in range(4):
        x, y = r.randint(3, T - 4), r.randint(3, T - 4)
        d.point((x, y), fill=r.choice([(250, 244, 220, 255), (248, 214, 90, 255)]))
    return im


def sprite(w, h):
    return Image.new("RGBA", (w, h), (0, 0, 0, 0))


def jar():
    im = sprite(24, 32)
    d = ImageDraw.Draw(im)
    d.ellipse((3, 8, 21, 31), fill=(190, 98, 56, 255), outline=(110, 52, 30, 255))
    d.ellipse((6, 11, 12, 20), fill=(214, 128, 80, 255))
    d.rectangle((7, 3, 16, 9), fill=(176, 90, 52, 255), outline=(110, 52, 30, 255))
    d.ellipse((6, 1, 17, 6), fill=(70, 34, 20, 255), outline=(110, 52, 30, 255))
    d.line((5, 16, 19, 16), fill=(232, 190, 110, 255))
    d.line((6, 22, 18, 22), fill=(232, 190, 110, 255))
    return im


def signpost():
    im = sprite(32, 40)
    d = ImageDraw.Draw(im)
    d.rectangle((14, 14, 17, 39), fill=(120, 80, 44, 255), outline=(70, 44, 24, 255))
    d.rectangle((3, 3, 29, 17), fill=(184, 134, 78, 255), outline=(84, 54, 30, 255))
    d.line((5, 7, 26, 7), fill=(120, 80, 44, 255))
    d.line((5, 12, 22, 12), fill=(120, 80, 44, 255))
    d.polygon([(26, 5), (31, 10), (26, 15)], fill=(184, 134, 78, 255), outline=(84, 54, 30, 255))
    return im


def crate():
    im = sprite(32, 32)
    d = ImageDraw.Draw(im)
    d.polygon([(2, 10), (16, 3), (30, 10), (16, 17)], fill=(214, 162, 96, 255), outline=(98, 64, 34, 255))
    d.polygon([(2, 10), (16, 17), (16, 31), (2, 24)], fill=(160, 108, 58, 255), outline=(98, 64, 34, 255))
    d.polygon([(30, 10), (16, 17), (16, 31), (30, 24)], fill=(132, 88, 46, 255), outline=(98, 64, 34, 255))
    d.line((9, 14, 9, 28), fill=(98, 64, 34, 255))
    d.line((23, 14, 23, 28), fill=(84, 54, 28, 255))
    d.line((4, 12, 28, 12), fill=(238, 196, 128, 255))
    return im





def extras():
    """The 256 x 208 block for page 2, below the portraits (y 48..255 of the page)."""
    page = Image.new("RGBA", (256, 208), (0, 0, 0, 0))
    tiles = [grass(25), plank(26), plaster(27), roof_tiles(28), wood_planks(29), sand_q(31, False), sand_q(32, True), grass_q(33)]
    for i, t in enumerate(tiles):
        page.paste(t, ((i & 3) * T, (i >> 2) * T))
    sprites = [(jar(), 0), (signpost(), 24), (crate(), 56)]
    for im, x in sprites:
        page.paste(im, (x, 128), im)
    return page
