#!/usr/bin/env python3
"""Bake the character creator's backdrop: the castle plaza (art_dk/backgrounds/dk_castle_1280x720.jpg) blurred, darkened, tinted
navy/purple and vignetted, at 320x180 (the overlay scales it up).  Output: assets/ui/chargen_bg.raw = "CGB1", u16 w, u16 h, RGB888 rows."""
import struct
from pathlib import Path
from PIL import Image, ImageFilter
import numpy as np

HERE = Path(__file__).resolve().parent
MOD = HERE.parent
REPO = MOD.parent.parent
W, H = 320, 180
im = Image.open(REPO / "art_dk/backgrounds/dk_castle_1280x720.jpg").convert("RGB").resize((W, H), Image.Resampling.LANCZOS)
im = im.filter(ImageFilter.GaussianBlur(2.2))
a = np.asarray(im).astype(np.float32) / 255.0
lum = a.mean(axis=2, keepdims=True)
a = a * 0.55 + lum * 0.45                                   # desaturate a little
tint = np.array([0.42, 0.40, 0.78])                         # navy / purple
a = a * tint * 0.95 + np.array([0.03, 0.02, 0.08])
yy, xx = np.mgrid[0:H, 0:W]
d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H * 0.45) / (H / 2)) ** 2)
a *= np.clip(1.15 - 0.55 * d, 0.35, 1.0)[..., None]         # vignette
out = (np.clip(a, 0, 1) * 255).astype(np.uint8)
dst = MOD / "assets/ui/chargen_bg.raw"
dst.write_bytes(b"CGB1" + struct.pack("<HH", W, H) + out.tobytes())
Image.fromarray(out).resize((W * 4, H * 4), Image.Resampling.BILINEAR).save("/workspace/tmp/chargen_bg_preview.png")
print(dst, dst.stat().st_size)
