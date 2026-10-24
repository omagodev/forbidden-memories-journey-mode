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
    tiles = [grass(25), plank(26)]
    for i, t in enumerate(tiles):
        page.paste(t, ((i & 3) * T, (i >> 2) * T))
    sprites = [(jar(), 0), (signpost(), 24), (crate(), 56)]
    for im, x in sprites:
        page.paste(im, (x, 128), im)
    return page
