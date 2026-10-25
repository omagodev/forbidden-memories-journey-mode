#!/usr/bin/env python3
"""AI portrait (1:1) -> FM dialogue-portrait record: 48x48 8-bit indices (0x900 bytes) + 64-entry BGR555 CLUT (0x80 bytes) = 0x980 bytes,
the layout of the campaign portrait bank (notes/dialog-portrait-bank.md).  Also writes a PNG preview (x1 and x6) and a 256x256 RGB version.
usage: make_portraits.py   (reads raw/*_portrait_*_raw.jpg)"""
import os, struct
import numpy as np
from PIL import Image
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JOBS = {"mago_tee": "mago_portrait_tee_raw.jpg", "mago_hood": "mago_portrait_hood_raw.jpg", "inseto": "inseto_portrait_raw.jpg"}
def build(name, src):
    im = Image.open(os.path.join(R, "raw", src)).convert("RGB"); W, H = im.size
    m = int(W * 0.012); im = im.crop((m, m, W - m, H - m))                    # drop the thin frame the generator draws
    im.resize((256, 256), Image.LANCZOS).save(os.path.join(R, "portraits", name + "_256.png"))
    small = im.resize((48, 48), Image.LANCZOS)
    q = small.quantize(64, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    pal = np.array(q.getpalette()[:64 * 3]).reshape(-1, 3); pal = np.vstack([pal, np.zeros((64 - len(pal), 3), int)])[:64]
    idx = np.array(q).astype(np.uint8)
    clut = b"".join(struct.pack("<H", ((int(b) >> 3) << 10) | ((int(g) >> 3) << 5) | (int(r) >> 3)) for r, g, b in pal)
    open(os.path.join(R, "portraits", "portrait_%s_48x48.bin" % name), "wb").write(idx.tobytes() + clut)
    prev = Image.fromarray(pal.astype(np.uint8)[idx]); prev.save(os.path.join(R, "portraits", name + "_48x48.png"))
    prev.resize((288, 288), Image.NEAREST).save(os.path.join(R, "portraits", name + "_48x48_x6.png"))
if __name__ == "__main__":
    for n, s in JOBS.items(): build(n, s); print("portrait", n)
