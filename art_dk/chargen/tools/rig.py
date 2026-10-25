#!/usr/bin/env python3
"""Raster + painting helpers for the chargen layers (supersampled shapes -> 1 texel masks, tone-table shading).
Cell = one 48x62 frame of one layer: per texel slot (0 = fixed rgb, 1..4 = palette slot), tone (index in TONES) and rgb."""
import numpy as np
from PIL import Image, ImageDraw
W, H = 48, 62
SS = 6
OUTLINE = (34, 24, 30)

# tone table: name -> (weight on the palette colour, fixed rgb added).  colour = clip(fixed + weight * palette[slot])
TONES = {
    "hi":   (1.14, (0, 0, 0)),
    "base": (1.00, (0, 0, 0)),
    "mid":  (0.84, (6, 0, 2)),
    "sh":   (0.68, (12, 0, 6)),
    "dk":   (0.50, (14, 2, 10)),
}
TONE_IDX = {k: i for i, k in enumerate(TONES)}

class Shape:
    """accumulates supersampled shapes; .mask() -> HxW bool (coverage >= 50%)"""
    def __init__(self):
        self.im = Image.new("L", (W * SS, H * SS), 0); self.d = ImageDraw.Draw(self.im)
    def _p(self, x, y): return (x * SS, y * SS)
    def poly(self, pts):
        self.d.polygon([self._p(*p) for p in pts], fill=255); return self
    def ell(self, cx, cy, rx, ry):
        self.d.ellipse([(cx - rx) * SS, (cy - ry) * SS, (cx + rx) * SS - 1, (cy + ry) * SS - 1], fill=255); return self
    def rect(self, x0, y0, x1, y1):
        if x1 > x0 and y1 > y0: self.d.rectangle([x0 * SS, y0 * SS, x1 * SS - 1, y1 * SS - 1], fill=255)
        return self
    def cap(self, p0, p1, r0, r1=None):
        """capsule: circles at p0/p1 joined by the tangent quad"""
        r1 = r0 if r1 is None else r1
        (x0, y0), (x1, y1) = p0, p1
        self.ell(x0, y0, r0, r0); self.ell(x1, y1, r1, r1)
        dx, dy = x1 - x0, y1 - y0; L = max((dx * dx + dy * dy) ** .5, 1e-6)
        nx, ny = -dy / L, dx / L
        self.poly([(x0 + nx * r0, y0 + ny * r0), (x1 + nx * r1, y1 + ny * r1), (x1 - nx * r1, y1 - ny * r1), (x0 - nx * r0, y0 - ny * r0)])
        return self
    def mask(self):
        a = np.asarray(self.im, np.float32).reshape(H, SS, W, SS).mean((1, 3)) / 255.0
        return a >= 0.5

def S(): return Shape()

def shift(m, dx, dy):
    o = np.zeros_like(m)
    ys, xs = slice(max(dy, 0), H + min(dy, 0)), slice(max(dx, 0), W + min(dx, 0))
    yd, xd = slice(max(-dy, 0), H + min(-dy, 0)), slice(max(-dx, 0), W + min(-dx, 0))
    o[ys, xs] = m[yd, xd]; return o

class Cell:
    def __init__(self):
        self.solid = np.zeros((H, W), bool)
        self.slot = np.zeros((H, W), np.uint8); self.tone = np.zeros((H, W), np.uint8); self.rgb = np.zeros((H, W, 3), np.uint8)
    def paint(self, m, slot, tone="base"):
        m = m & True
        self.solid |= m; self.slot[m] = slot; self.tone[m] = TONE_IDX[tone]; self.rgb[m] = 0
    def fixed(self, m, rgb):
        self.solid |= m; self.slot[m] = 0; self.rgb[m] = rgb; self.tone[m] = 0
    def erase(self, m):
        self.solid &= ~m
    def bevel(self, m, slot, base="base", hi="hi", lo="mid", lo2=None):
        """paint mask m with a 1-texel highlight on its top/left edge and shade on its bottom/right edge"""
        up, left = shift(m, 0, 1), shift(m, 1, 0)      # up[y,x] = m[y-1,x]
        down, right = shift(m, 0, -1), shift(m, -1, 0)
        t = np.full((H, W), TONE_IDX[base], np.uint8)
        edge_tl = m & (~up | ~left)
        edge_br = m & (~down | ~right)
        names = list(TONES)
        self.solid |= m; self.slot[m] = slot; self.rgb[m] = 0
        self.tone[m] = TONE_IDX[base]
        self.tone[edge_tl] = TONE_IDX[hi]
        self.tone[edge_br] = TONE_IDX[lo]
    def band(self, m, slot, tones, y0, y1):
        """vertical tone gradient: tones list spread over rows y0..y1 inside the mask"""
        self.solid |= m; self.slot[m] = slot; self.rgb[m] = 0
        ys = np.arange(H)[:, None] * np.ones((1, W))
        k = np.clip(((ys - y0) / max(y1 - y0, 1) * len(tones)).astype(int), 0, len(tones) - 1)
        for i, t in enumerate(tones):
            sel = m & (k == i); self.tone[sel] = TONE_IDX[t]
    def tone_at(self, m, tone):
        self.tone[m & self.solid] = TONE_IDX[tone]
    def mirrored(self):
        c = Cell()
        c.solid = self.solid[:, ::-1].copy(); c.slot = self.slot[:, ::-1].copy(); c.tone = self.tone[:, ::-1].copy(); c.rgb = self.rgb[:, ::-1].copy()
        return c

def line(p0, p1, w=1.0):
    return S().cap(p0, p1, w / 2.0)
def rows(y0, y1, x0=0, x1=W):
    m = np.zeros((H, W), bool); m[int(y0):int(y1), int(x0):int(x1)] = True; return m
def cols(x0, x1):
    m = np.zeros((H, W), bool); m[:, int(x0):int(x1)] = True; return m
