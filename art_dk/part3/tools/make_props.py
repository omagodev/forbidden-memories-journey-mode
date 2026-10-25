#!/usr/bin/env python3
"""Part 3 props: pyramid hatch overlays (closed/open), torch glow (dithered, texel-0-only transparency) + 3-frame torch flame strip, 3 item icons (24x24 and 16x16).
Prop file format = the engine's prop_*.raw (see jm_painted.c prop_blit): u16 w, u16 h, then w*h u16 RGB555, bit15 set, 0 = transparent (w,h <= 256).
Icon extras: icons/icon_<id>_<n>x<n>.bin = u8 index[n*n] (0 = transparent) + 16-entry BGR555 CLUT (32 bytes), and icons/icon_<id>_<n>.raw in the prop format.
usage: python3 tools/make_props.py  (numpy + Pillow only)"""
import math, os, struct
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OV = os.path.join(ROOT, "overlays"); IC = os.path.join(ROOT, "icons")
os.makedirs(OV, exist_ok=True); os.makedirs(IC, exist_ok=True)

def to555(rgb, a):
    r, g, b = (rgb[..., 0] >> 3).astype(np.uint16), (rgb[..., 1] >> 3).astype(np.uint16), (rgb[..., 2] >> 3).astype(np.uint16)
    w = (r | (g << 5) | (b << 10) | 0x8000).astype(np.uint16)
    w[w == 0x8000] = 0x8001          # pure black must not become 0 (transparent)
    w[a == 0] = 0
    return w
def write_prop(path, rgba):
    a = np.array(rgba); w = to555(a[..., :3].astype(np.uint16), a[..., 3] > 127)
    open(path, "wb").write(struct.pack("<HH", w.shape[1], w.shape[0]) + w.astype("<u2").tobytes())
def outline(img, col=(40, 28, 22)):
    a = np.array(img); al = a[..., 3] > 127; pad = np.pad(al, 1)
    near = pad[:-2, 1:-1] | pad[2:, 1:-1] | pad[1:-1, :-2] | pad[1:-1, 2:]
    o = near & ~al; a[o] = (*col, 255); return Image.fromarray(a)
def ss(w, h, k=4): return Image.new("RGBA", (w * k, h * k), (0, 0, 0, 0)), k
def down(im, w, h): 
    a = np.array(im.resize((w, h), Image.BOX)); a[..., 3] = np.where(a[..., 3] > 110, 255, 0); return Image.fromarray(a)
def noise_tex(img, seed, amt=14):
    a = np.array(img).astype(float); rng = np.random.RandomState(seed)
    n = (rng.rand(*a.shape[:2]) - 0.5) * amt; a[..., :3] = np.clip(a[..., :3] + n[..., None], 0, 255); return Image.fromarray(a.astype(np.uint8))

# ---------------------------------------------------------------- pyramid hatch (stone slab set into the pyramid's sloped face)
def hatch(open_=False, W=48, H=34):
    im, k = ss(W, H); d = ImageDraw.Draw(im)
    frame = [(4, 30), (9, 6), (39, 6), (44, 30)]                                  # trapezoid: wider at the bottom (pyramid face)
    d.polygon([(x * k, y * k) for x, y in frame], fill=(146, 112, 70, 255))        # carved stone frame
    inner = [(8, 28), (12, 9), (36, 9), (40, 28)]
    if not open_:
        d.polygon([(x * k, y * k) for x, y in inner], fill=(196, 164, 112, 255))   # closed slab
        d.line([(14 * k, 12 * k), (34 * k, 12 * k)], fill=(224, 196, 140, 255), width=k)   # lit top edge
        for x0 in (18, 30):                                                         # glyph marks
            d.rectangle([x0 * k, 16 * k, (x0 + 2) * k, 22 * k], outline=(110, 84, 52, 255), width=k // 2)
        d.ellipse([22 * k, 22 * k, 26 * k, 26 * k], outline=(70, 56, 44, 255), width=k // 2 + 1)          # ring handle
        d.line([(24 * k, 20 * k), (24 * k, 22 * k)], fill=(70, 56, 44, 255), width=k // 2 + 1)
    else:
        d.polygon([(x * k, y * k) for x, y in inner], fill=(18, 14, 18, 255))      # dark shaft
        d.polygon([(14 * k, 26 * k), (34 * k, 26 * k), (36 * k, 28 * k), (12 * k, 28 * k)], fill=(120, 92, 60, 255))
        for i in range(3): d.line([(14 * k, (14 + 4 * i) * k), (34 * k, (14 + 4 * i) * k)], fill=(70, 62, 80, 255), width=k // 2)   # ladder rungs in the dark
        d.line([(16 * k, 10 * k), (15 * k, 27 * k)], fill=(90, 70, 50, 255), width=k // 2 + 1); d.line([(32 * k, 10 * k), (33 * k, 27 * k)], fill=(90, 70, 50, 255), width=k // 2 + 1)
        d.polygon([(10 * k, 8 * k), (20 * k, 8 * k), (16 * k, 12 * k), (8 * k, 12 * k)], fill=(176, 146, 100, 255))   # slab leaning aside
    out = noise_tex(down(im, W, H), 3)
    return outline(out)

# ---------------------------------------------------------------- torch glow: dithered radial glow (no alpha in the engine)
BAYER8 = np.array([[0, 32, 8, 40, 2, 34, 10, 42], [48, 16, 56, 24, 50, 18, 58, 26], [12, 44, 4, 36, 14, 46, 6, 38], [60, 28, 52, 20, 62, 30, 54, 22],
                   [3, 35, 11, 43, 1, 33, 9, 41], [51, 19, 59, 27, 49, 17, 57, 25], [15, 47, 7, 39, 13, 45, 5, 37], [63, 31, 55, 23, 61, 29, 53, 21]]) / 64.0
def glow(S=64):
    yy, xx = np.mgrid[0:S, 0:S]; r = np.hypot(xx - S / 2 + 0.5, (yy - S / 2 + 0.5) * 1.0) / (S / 2)
    dens = np.clip(1 - r, 0, 1) ** 1.6                                              # 1 at the centre -> 0 at the edge
    on = BAYER8[yy % 8, xx % 8] < dens * 0.85
    col = np.zeros((S, S, 4), np.uint8)
    core = np.clip(1 - r * 1.8, 0, 1)
    col[..., 0] = np.clip(255, 0, 255); col[..., 1] = (150 + 90 * core).astype(np.uint8); col[..., 2] = (40 + 120 * core).astype(np.uint8); col[..., 3] = np.where(on, 255, 0)
    return Image.fromarray(col)
def flame(frames=3, W=16, H=24):
    strip = Image.new("RGBA", (W * frames, H), (0, 0, 0, 0))
    for f in range(frames):
        im, k = ss(W, H); d = ImageDraw.Draw(im); sway = [-1.2, 0.6, 1.4][f % 3]; h = [17, 20, 18][f % 3]
        pts = [(8, 22), (4.5, 16), (6, 11), (8 + sway * 0.6, 22 - h), (10 + sway, 11), (11.5, 16)]
        d.polygon([(x * k, y * k) for x, y in pts], fill=(236, 110, 24, 255))
        pts2 = [(8, 22), (5.8, 17), (7, 13), (8 + sway * 0.4, 22 - h * 0.78), (9.2 + sway * 0.6, 13), (10.2, 17)]
        d.polygon([(x * k, y * k) for x, y in pts2], fill=(255, 200, 60, 255))
        d.ellipse([6.6 * k, 15 * k, 9.4 * k, 20.5 * k], fill=(255, 245, 190, 255))
        strip.paste(down(im, W, H), (f * W, 0))
    return strip

# ---------------------------------------------------------------- item icons
def scarab(S=24):
    k = 8; W = S * k; im = Image.new("RGBA", (W, W), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = W / 2
    leg = (120, 88, 20, 255)
    for dy in (-3.6, 0.2, 4.0):                                                      # legs
        for sx in (-1, 1): d.line([(c + sx * 4.5 * k, c + dy * k + 1.4 * k), (c + sx * 9.3 * k, c + dy * k + 2.6 * k)], fill=leg, width=int(1.1 * k))
    d.ellipse([c - 7 * k, c - 5.2 * k, c + 7 * k, c + 10 * k], fill=(222, 170, 40, 255))              # body (wing case)
    d.ellipse([c - 5 * k, c - 8.4 * k, c + 5 * k, c - 3.4 * k], fill=(196, 146, 34, 255))             # head
    d.ellipse([c - 4.6 * k, c - 4.4 * k, c + 4.6 * k, c + 1.8 * k], fill=(36, 150, 164, 255))          # lapis/turquoise inlay
    d.ellipse([c - 2.8 * k, c - 3.2 * k, c + 2.8 * k, c + 0.4 * k], fill=(96, 214, 214, 255))
    d.line([(c, c - 1 * k), (c, c + 9.6 * k)], fill=(130, 92, 20, 255), width=int(0.9 * k))           # wing split
    d.arc([c - 6 * k, c + 1 * k, c + 6 * k, c + 9 * k], 20, 160, fill=(255, 224, 120, 255), width=int(0.9 * k))   # highlight
    return outline(down(im, S, S))
def clover_charm(S=24):
    k = 8; W = S * k; im = Image.new("RGBA", (W, W), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = W / 2; cy = c + 1.5 * k
    d.arc([c - 3 * k, 0.4 * k, c + 3 * k, 6.4 * k], 180, 360, fill=(190, 40, 40, 255), width=int(1.1 * k))           # red cord loop
    d.ellipse([c - 9 * k, cy - 9 * k, c + 9 * k, cy + 9 * k], fill=(226, 176, 44, 255))                            # gold coin
    d.ellipse([c - 7.2 * k, cy - 7.2 * k, c + 7.2 * k, cy + 7.2 * k], fill=(244, 206, 84, 255))
    gr = (40, 150, 60, 255)
    for dx, dy in ((-2.4, -2.4), (2.4, -2.4), (-2.4, 2.4), (2.4, 2.4)): d.ellipse([c + (dx - 2.6) * k, cy + (dy - 2.6) * k, c + (dx + 2.6) * k, cy + (dy + 2.6) * k], fill=gr)
    d.ellipse([c - 1.4 * k, cy - 1.4 * k, c + 1.4 * k, cy + 1.4 * k], fill=(120, 214, 110, 255))
    d.line([(c + 1 * k, cy + 2 * k), (c + 4.6 * k, cy + 6.4 * k)], fill=(30, 110, 46, 255), width=int(0.9 * k))     # stem
    return outline(down(im, S, S))
def bandana(S=24):
    k = 8; W = S * k; im = Image.new("RGBA", (W, W), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    P = lambda pts: [(x * k, y * k) for x, y in pts]
    d.polygon(P([(2, 7), (21, 7), (20, 12), (12, 19), (4, 12)]), fill=(200, 38, 36, 255))                           # triangle of cloth
    d.polygon(P([(2, 7), (21, 7), (20.4, 9.6), (3, 9.6)]), fill=(232, 74, 60, 255))                                  # folded band
    d.polygon(P([(4, 12), (12, 19), (11, 12)]), fill=(150, 24, 28, 255))                                             # shadow fold
    for x, y in ((7, 11.5), (12, 12), (16, 11), (10, 15), (14.4, 14.2)): d.ellipse([(x - 0.7) * k, (y - 0.7) * k, (x + 0.7) * k, (y + 0.7) * k], fill=(250, 214, 110, 255))   # gold dots
    d.polygon(P([(19.5, 7), (23, 4), (22.4, 9.4)]), fill=(214, 52, 44, 255)); d.polygon(P([(19.5, 8), (23, 12.6), (21, 13)]), fill=(176, 30, 32, 255))   # knot tails
    d.ellipse([17.6 * k, 6 * k, 20.6 * k, 9.4 * k], fill=(160, 26, 30, 255))
    return outline(down(im, S, S))

def quant_icon(img, n):
    """RGBA -> 15 colours + transparent index 0 -> (indices, palette)"""
    a = np.array(img); mask = a[..., 3] > 127
    q = Image.fromarray(a[..., :3]).quantize(15, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    idx = np.array(q).astype(np.uint8) + 1; idx[~mask] = 0
    pal = np.array(q.getpalette()[:45]).reshape(-1, 3); pal = np.vstack([np.zeros((1, 3), int), pal, np.zeros((16 - 1 - len(pal), 3), int)])[:16]
    return idx, pal
def save_icon(name, img24):
    for n, im in ((24, img24), (16, None)):
        if im is None:
            sm = img24.resize((16, 16), Image.BOX); a = np.array(sm); a[..., 3] = np.where(a[..., 3] > 110, 255, 0); im = outline(Image.fromarray(a)) if False else Image.fromarray(a)
        idx, pal = quant_icon(im, n)
        clut = b"".join(struct.pack("<H", ((int(b) >> 3) << 10) | ((int(g) >> 3) << 5) | (int(r) >> 3)) for r, g, b in pal)
        open(os.path.join(IC, "icon_%s_%dx%d.bin" % (name, n, n)), "wb").write(idx.tobytes() + clut)
        rgba = np.zeros((n, n, 4), np.uint8); rgba[..., :3] = pal[idx]; rgba[..., 3] = np.where(idx > 0, 255, 0)
        Image.fromarray(rgba).save(os.path.join(IC, "icon_%s_%d.png" % (name, n)))
        write_prop(os.path.join(IC, "icon_%s_%d.raw" % (name, n)), Image.fromarray(rgba))

def main():
    for nm, im in (("prop_hatch_closed", hatch(False)), ("prop_hatch_open", hatch(True)), ("prop_torch_glow", glow(64)), ("prop_torch_flame", flame())):
        im.save(os.path.join(OV, nm + ".png")); write_prop(os.path.join(OV, nm + ".raw"), im); print(nm, im.size)
    save_icon("founders_scarab", scarab()); save_icon("lucky_charm", clover_charm()); save_icon("jonos_bandana", bandana())
if __name__ == "__main__": main()
