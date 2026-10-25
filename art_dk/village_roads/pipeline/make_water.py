#!/usr/bin/env python3
"""Water animation frames for the painted village: only the river cells, N looping frames."""
import sys, struct, math
import numpy as np
from PIL import Image, ImageFilter

import os
SRC = os.environ.get("VR_CLEAN", "/workspace/study/fmrecomp/painted_work/bg_clean.png")
TMP = os.environ.get("VR_TMP", "/tmp/vr_tmp"); os.makedirs(TMP, exist_ok=True)
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
N = int(sys.argv[2]) if len(sys.argv) > 2 else 6
CELL, STRIDE, COLS, ROWS = 128, 126, 11, 6

im = Image.open(SRC).convert("RGB")
rgb = np.array(im).astype(np.float32)
H, W = rgb.shape[:2]
hsv = np.array(im.convert("HSV")).astype(int)
h = hsv[:, :, 0] * 360 / 255; s = hsv[:, :, 1] / 255; v = hsv[:, :, 2] / 255
yy = np.arange(H)[:, None]
water = (h > 170) & (h < 235) & (s > 0.18) & (v > 0.30) & (yy < 150)
m = Image.fromarray((water * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.MinFilter(7))
water = np.array(m) > 0
water[100:, 1090:] = False                      # the blue trim of house B is not water

def to555(a):                                   # same ordered dither as make_painted.py
    bayer = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0 - 0.5
    hh, ww, _ = a.shape
    th = np.tile(bayer, (hh // 4 + 1, ww // 4 + 1))[:hh, :ww]
    out = np.zeros((hh, ww), np.uint16)
    for c, sh in enumerate((0, 5, 10)):
        q = np.clip(np.floor(a[:, :, c] / 255.0 * 31.0 + th * 0.9 + 0.5), 0, 31).astype(np.uint16)
        out |= q << sh
    return out | 0x8000

X, Y = np.meshgrid(np.arange(W), np.arange(H))
def frame(t):
    p = t / N
    dx = np.rint(2.2 * np.sin(2 * np.pi * (Y / 23.0 + p)) + 1.0 * np.sin(2 * np.pi * (Y / 9.0 - 2 * p))).astype(int)
    dy = np.rint(1.3 * np.sin(2 * np.pi * (X / 31.0 + p))).astype(int)
    sx = np.clip(X + dx, 0, W - 1); sy = np.clip(Y + dy, 0, H - 1)
    ok = water & water[sy, sx]
    out = np.where(ok[:, :, None], rgb[sy, sx], rgb)
    # glints: thin bright diagonal bands that drift
    g = np.maximum(0, np.sin(2 * np.pi * ((X * 0.7 + Y * 1.3) / 17.0 - p))) ** 8
    g2 = np.maximum(0, np.sin(2 * np.pi * ((X * 1.1 - Y * 0.6) / 29.0 + 2 * p))) ** 10
    add = (34 * g + 22 * g2)[:, :, None] * np.array([0.85, 1.0, 1.0])
    out = np.where(water[:, :, None], np.clip(out + add, 0, 255), out)
    return to555(out)

def cut(img, x0, y0):
    c = np.zeros((CELL, CELL), np.uint16)
    hh = min(CELL, H - y0); ww = min(CELL, W - x0)
    c[:hh, :ww] = img[y0:y0 + hh, x0:x0 + ww]
    if hh < CELL: c[hh:, :ww] = img[H - 1:H, x0:x0 + ww]
    if ww < CELL: c[:, ww:] = c[:, ww - 1:ww]
    return c

cells = []
for r in range(ROWS):
    for c in range(COLS):
        if water[r * STRIDE:r * STRIDE + CELL, c * STRIDE:c * STRIDE + CELL].sum() > 40:
            cells.append((r, c))
frames = [frame(t) for t in range(N)]
data = bytearray(struct.pack("<HH", N, len(cells)) + b"".join(struct.pack("<H", r * COLS + c) for r, c in cells))
for t in range(N):
    for r, c in cells:
        data += cut(frames[t], c * STRIDE, r * STRIDE).tobytes()
open(OUT + "/painted_water.raw", "wb").write(data)
Image.fromarray((water * 255).astype(np.uint8)).save(TMP + "/water_mask.png")
print("frames", N, "water cells", len(cells), "bytes", len(data), "banks", math.ceil(N * len(cells) / 32))
# offline preview strip
strip = Image.new("RGB", (1280, 150 * N))
for t in range(N):
    f = frames[t]
    a = np.zeros((150, 1280, 3), np.uint8)
    a[:, :, 0] = ((f[:150] & 31) << 3); a[:, :, 1] = (((f[:150] >> 5) & 31) << 3); a[:, :, 2] = (((f[:150] >> 10) & 31) << 3)
    strip.paste(Image.fromarray(a), (0, 150 * t))
strip.save(TMP + "/water_frames_strip.png")
