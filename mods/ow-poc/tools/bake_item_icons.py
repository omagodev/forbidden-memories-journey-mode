#!/usr/bin/env python3
"""Bake the story items' 24x24 icons (the banner and backpack format of icon_lucky_charm.bin): 576 bytes of palette indices,
then 16 RGB555 halfwords; index 0 is clear.  Each icon is drawn here with a few shapes at 24x24, then given the 1-texel dark
outline the other icons have.  Writes assets/icon_<name>.bin; with an argument also a preview sheet (PNG) of every icon."""
import struct, sys
from pathlib import Path
from PIL import Image, ImageDraw

MOD = Path(__file__).resolve().parent.parent
OUT = (40, 22, 12)


def stamp_card(d):
    d.rectangle([3, 5, 20, 18], fill=(236, 220, 176)); d.rectangle([3, 5, 20, 7], fill=(196, 60, 48))
    for i, c in enumerate([(200, 60, 50), (60, 110, 200), (70, 160, 80)]):
        d.ellipse([5 + i * 5, 10, 8 + i * 5, 13], fill=c)
    d.line([5, 16, 18, 16], fill=(170, 150, 110))


def lantern(d):
    d.arc([9, 1, 14, 6], 180, 360, fill=(120, 90, 40)); d.rectangle([7, 5, 16, 6], fill=(150, 110, 40))
    d.rectangle([8, 7, 15, 18], fill=(255, 200, 80)); d.rectangle([10, 9, 13, 16], fill=(255, 245, 190))
    d.line([8, 7, 8, 18], fill=(150, 110, 40)); d.line([15, 7, 15, 18], fill=(150, 110, 40)); d.line([11, 7, 11, 18], fill=(200, 150, 50))
    d.rectangle([7, 19, 16, 20], fill=(150, 110, 40))


def water_jug(d):
    d.ellipse([5, 8, 18, 21], fill=(196, 120, 72)); d.rectangle([9, 3, 14, 9], fill=(180, 106, 62))
    d.rectangle([8, 3, 15, 4], fill=(150, 86, 50)); d.arc([14, 9, 21, 16], 270, 90, fill=(150, 86, 50))
    d.line([7, 13, 16, 13], fill=(230, 170, 120)); d.ellipse([8, 10, 10, 12], fill=(236, 190, 150))


def honey_jar(d):
    d.rectangle([6, 8, 17, 20], fill=(240, 170, 40)); d.rectangle([5, 5, 18, 8], fill=(200, 140, 90))
    d.rectangle([7, 4, 16, 5], fill=(170, 110, 70)); d.rectangle([8, 12, 15, 17], fill=(250, 236, 200))
    d.polygon([(10, 7), (13, 7), (12, 11), (11, 11)], fill=(250, 200, 60)); d.point([9, 10], fill=(255, 240, 160))


def river_water(d):
    d.ellipse([5, 8, 18, 21], fill=(196, 120, 72)); d.rectangle([9, 3, 14, 9], fill=(180, 106, 62))
    d.rectangle([8, 3, 15, 4], fill=(150, 86, 50)); d.arc([14, 9, 21, 16], 270, 90, fill=(150, 86, 50))
    d.ellipse([8, 1, 15, 5], fill=(80, 170, 240)); d.line([7, 14, 16, 14], fill=(80, 170, 240)); d.line([8, 16, 15, 16], fill=(120, 200, 250))


def dates(d):
    d.line([12, 2, 12, 8], fill=(110, 80, 40)); d.line([12, 4, 6, 8], fill=(110, 80, 40)); d.line([12, 4, 18, 8], fill=(110, 80, 40))
    for x, y in [(4, 9), (9, 11), (14, 9), (7, 15), (12, 15), (16, 14)]:
        d.ellipse([x, y, x + 4, y + 6], fill=(130, 50, 30)); d.point([x + 1, y + 1], fill=(200, 110, 70))


ICONS = {"stamp_card": stamp_card, "lantern": lantern, "water_jug": water_jug, "honey_jar": honey_jar, "river_water": river_water, "dates": dates}


def bake(name, fn):
    im = Image.new("RGBA", (24, 24), (0, 0, 0, 0))
    fn(ImageDraw.Draw(im))
    a = im.load()
    solid = [[a[x, y][3] > 0 for x in range(24)] for y in range(24)]
    for y in range(24):                                    # the dark outline around the shape
        for x in range(24):
            if not solid[y][x] and any(0 <= x + dx < 24 and 0 <= y + dy < 24 and solid[y + dy][x + dx] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                a[x, y] = OUT + (255,)
    q = im.convert("RGB").quantize(colors=15, method=Image.Quantize.MEDIANCUT)
    pal = (q.getpalette() + [0] * 45)[:45]
    idx = bytes((q.getpixel((x, y)) + 1) if a[x, y][3] else 0 for y in range(24) for x in range(24))
    clut = [0] + [max(1, ((pal[i * 3 + 2] >> 3) << 10) | ((pal[i * 3 + 1] >> 3) << 5) | (pal[i * 3] >> 3)) for i in range(15)]
    (MOD / "assets" / f"icon_{name}.bin").write_bytes(idx + struct.pack("<16H", *clut))
    return im


if __name__ == "__main__":
    ims = [bake(n, f) for n, f in ICONS.items()]
    if len(sys.argv) > 1:
        sheet = Image.new("RGBA", (24 * 4 * len(ims), 96), (30, 28, 70, 255))
        for i, im in enumerate(ims):
            big = im.resize((96, 96), Image.NEAREST); sheet.paste(big, (i * 96, 0), big)
        sheet.save(sys.argv[1])
    print("baked", ", ".join(ICONS))
