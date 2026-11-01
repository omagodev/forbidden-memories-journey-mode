#!/usr/bin/env python3
"""Bake the shop screen's backdrop: the card-shop interior (art_dk/shop/shop_interior_src.jpg, AI-generated) with the emblem on the
top-left banner painted out (no logos), softened and darkened a little so the panels read on top, at 400x225 (the overlay scales it
up).  Output: assets/ui/shop_bg.raw = "CGB1", u16 w, u16 h, RGB888 rows (the same format as chargen_bg.raw)."""
import struct, sys
from pathlib import Path
from PIL import Image, ImageFilter
import numpy as np

HERE = Path(__file__).resolve().parent
MOD = HERE.parent
REPO = MOD.parent.parent
W, H = 400, 225
im = Image.open(REPO / "art_dk/shop/shop_interior_src.jpg").convert("RGB").resize((1280, 720), Image.Resampling.LANCZOS)
a = np.asarray(im).astype(np.float32)
for y in range(46, 140):                       # the banner's emblem: refill each row from the plain cloth at its sides
    l, r = a[y, 136:140].mean(axis=0), a[y, 207:211].mean(axis=0)
    for x in range(140, 207):
        t = (x - 140) / 66.0
        a[y, x] = l * (1 - t) + r * t
im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).resize((W, H), Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(0.8))
a = np.asarray(im).astype(np.float32) / 255.0
a = a * 0.80 + np.array([0.01, 0.01, 0.04])     # a touch darker and cooler
yy, xx = np.mgrid[0:H, 0:W]
d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H * 0.45) / (H / 2)) ** 2)
a *= np.clip(1.12 - 0.40 * d, 0.45, 1.0)[..., None]
out = (np.clip(a, 0, 1) * 255).astype(np.uint8)
dst = MOD / "assets/ui/shop_bg.raw"
dst.write_bytes(b"CGB1" + struct.pack("<HH", W, H) + out.tobytes())
if len(sys.argv) > 1:
    Image.fromarray(out).resize((W * 3, H * 3), Image.Resampling.BILINEAR).save(sys.argv[1])
print(dst, dst.stat().st_size)
