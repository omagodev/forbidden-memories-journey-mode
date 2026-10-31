#!/usr/bin/env python3
"""The keeper's picture for the shop screen.

  python3 tools/make_shop_art.py --placeholder [keeper ...]   a stand-in, so the screen works today
  python3 tools/make_shop_art.py teana her_art.png            the real art (needs pillow)

Writes assets/shop_<keeper>.raw in the format the painted props use: u16 width, u16 height, then one
RGB555 halfword a texel, row by row.  Texel 0 is the only transparency the renderer has (no alpha),
so a transparent pixel is written as 0 and an opaque one is never allowed to land on 0.

The picture goes into the free lower part of texture bank 15 page 4, which bounds it:

    at most 248 x 170 texels.

A bigger image is scaled down to fit, keeping its shape.  Draw it as large as you like on screen; it is a texture.
The art may be a wide keeper-and-stall composition: it is drawn across the shop scene behind the
dialogue and stock panels.  A transparent background lets the painted village remain visible.
"""
import os, struct, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(os.path.dirname(HERE), "assets")
MAX_W, MAX_H = 248, 170       # the free rectangle of bank 15 page 4, below the bench and the hatches
PLACEHOLDER_W, PLACEHOLDER_H = 128, 168


def rgb555(r, g, b):
    """The renderer's halfword.  0 means transparent, so an opaque texel is nudged off it."""
    v = ((b >> 3) << 10) | ((g >> 3) << 5) | (r >> 3)
    return v if v else 1


def write_raw(path, width, height, texels):
    with open(path, "wb") as f:
        f.write(struct.pack("<HH", width, height))
        f.write(b"".join(struct.pack("<H", t) for t in texels))
    print("%s: %dx%d (%d bytes)" % (os.path.relpath(path), width, height, 4 + 2 * width * height))


def placeholder(keeper):
    """A stand-in that is obviously a stand-in: a framed panel, a seated figure, and the name.

    No pillow needed, so it works on a fresh clone.  Replace it with the real art and run this tool
    again with a PNG; nothing in the game changes but the file.
    """
    w, h = PLACEHOLDER_W, PLACEHOLDER_H
    px = [0] * (w * h)
    frame = rgb555(200, 160, 60)
    back = rgb555(28, 30, 70)
    cloth = rgb555(96, 70, 140)
    skin = rgb555(214, 170, 132)
    hair = rgb555(70, 48, 96)
    mark = rgb555(150, 150, 170)
    for y in range(h):
        for x in range(w):
            i = y * w + x
            edge = x < 2 or x >= w - 2 or y < 2 or y >= h - 2
            if edge:
                px[i] = frame
                continue
            # a soft vertical wash, so the figure sits on something
            px[i] = back if (x + y) % 23 else rgb555(34, 36, 82)
    cx = w // 2

    def disc(ox, oy, r, colour):
        for y in range(max(0, oy - r), min(h, oy + r + 1)):
            for x in range(max(0, ox - r), min(w, ox + r + 1)):
                if (x - ox) ** 2 + (y - oy) ** 2 <= r * r:
                    px[y * w + x] = colour

    def box(x0, y0, x1, y1, colour):
        for y in range(max(0, y0), min(h, y1)):
            for x in range(max(0, x0), min(w, x1)):
                px[y * w + x] = colour

    box(cx - 34, 96, cx + 34, h - 6, cloth)          # the body
    disc(cx, 74, 26, skin)                            # the head
    box(cx - 27, 48, cx + 27, 70, hair)               # hair over it
    disc(cx - 24, 72, 7, hair)
    disc(cx + 24, 72, 7, hair)
    disc(cx - 10, 74, 3, rgb555(40, 30, 40))          # the eyes
    disc(cx + 10, 74, 3, rgb555(40, 30, 40))
    for k in range(13):                               # a smile: an arc under them
        x = cx - 9 + k * 1.5
        y = 88 + int(3.4 * (1 - ((k - 6) / 6.0) ** 2))
        disc(int(x), y, 1, rgb555(150, 70, 70))
    box(cx - 36, 92, cx + 36, 96, rgb555(150, 118, 70))   # a collar, to break up the shapes
    for k in range(0, w - 16, 10):                    # a dashed band: this is a placeholder
        box(8 + k, h - 22, 8 + k + 5, h - 18, mark)
    return w, h, px


def convert(keeper, src):
    try:
        from PIL import Image
    except ImportError:
        sys.exit("pillow is needed to convert a PNG: pip install pillow")
    im = Image.open(src).convert("RGBA")
    if im.width > MAX_W or im.height > MAX_H:
        scale = min(MAX_W / im.width, MAX_H / im.height)
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.LANCZOS)
        print("scaled to %dx%d to fit the texture page" % (im.width, im.height))
    px = []
    clear = 0
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = im.getpixel((x, y))
            if a < 128:
                px.append(0)
                clear += 1
            else:
                px.append(rgb555(r, g, b))
    print("%d of %d texels transparent" % (clear, len(px)))
    return im.width, im.height, px


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    if args[0] == "--placeholder":
        for keeper in (args[1:] or ["teana"]):
            w, h, px = placeholder(keeper)
            write_raw(os.path.join(ASSETS, "shop_%s.raw" % keeper), w, h, px)
        return
    if len(args) != 2:
        sys.exit(__doc__)
    keeper, src = args
    w, h, px = convert(keeper, src)
    write_raw(os.path.join(ASSETS, "shop_%s.raw" % keeper), w, h, px)


if __name__ == "__main__":
    main()
