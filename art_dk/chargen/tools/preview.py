import numpy as np
from PIL import Image
from rig import *
def render_cell(layers, pals, bg=None):
    """layers: list of (Cell, pal dict slot->rgb, ringmask or None) back to front -> RGBA HxWx4"""
    out = np.zeros((H, W, 4), np.uint8)
    for c, pal, ring in layers:
        names = list(TONES)
        for y in range(H):
            for x in range(W):
                if ring is not None and ring[y, x] and not c.solid[y, x]:
                    out[y, x] = OUTLINE + (255,)
                if c.solid[y, x]:
                    if c.slot[y, x] == 0: col = c.rgb[y, x].astype(float)
                    else:
                        w, fx = TONES[names[c.tone[y, x]]]
                        col = np.array(fx) + w * np.array(pal[c.slot[y, x]])
                    out[y, x, :3] = np.clip(col + .5, 0, 255).astype(np.uint8); out[y, x, 3] = 255
    return out
def ring_of(c):
    m = c.solid; r = shift(m, 1, 0) | shift(m, -1, 0) | shift(m, 0, 1) | shift(m, 0, -1)
    return r & ~m
def sheet(cellfn, palfn, dirs=("down", "left", "up"), frames=(0, 1, 3), zoom=6, bg=(150, 170, 120)):
    pass
