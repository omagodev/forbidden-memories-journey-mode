#!/usr/bin/env python3
"""A contact sheet of kit pieces drawn straight from the OBJ files (palette colours, winding as stored),
to check the loader against the kit's own Preview.png.  Back faces are culled by the stored winding, so
a flipped triangle shows as a hole.

Usage: kenney_sheet.py KIT_DIR out.png [piece ...]
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bake_kenney as K  # noqa: E402

DEFAULT = ("wall wall-wood wall-door wall-wood-door wall-window-small wall-window-shutters wall-wood-window-glass wall-arch "
           "roof roof-high roof-gable roof-high-gable roof-corner roof-high-corner roof-point roof-flat "
           "chimney fence fence-gate stall-red stall-green cart lantern banner-red "
           "tree tree-high-round rock-large rock-small rock-wide pillar-stone hedge stairs-stone").split()


def render(name, size=160, yaw=35.0, pitch=32.0):
    V, VT, F = K.load(name)
    mid = (V.min(0) + V.max(0)) / 2
    ext = float(np.abs(V - mid).max()) or 1.0
    cy, sy = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    cp, sp = math.cos(math.radians(pitch)), math.sin(math.radians(pitch))
    sun = np.array([-0.5, 0.8, 0.4])
    sun /= np.linalg.norm(sun)
    tris = []
    for tri in F:
        p = np.array([V[t[0]] - mid for t in tri])
        n = np.cross(p[1] - p[0], p[2] - p[0])
        if np.linalg.norm(n) < 1e-12:
            continue
        n /= np.linalg.norm(n)
        # view: rotate about y, then tilt
        def view(q):
            x = q[0] * cy + q[2] * sy
            z = -q[0] * sy + q[2] * cy
            y = q[1] * cp - z * sp
            z2 = q[1] * sp + z * cp
            return np.array([x, y, z2])
        pv = np.array([view(q) for q in p])
        nv = view(n)
        if nv[2] <= 0:                          # facing away (the camera looks down -z of the view)
            continue
        col = sum(K.palette(VT[t[1]]) for t in tri) / 3.0
        shade = 0.55 + 0.45 * max(0.0, float(n @ sun))
        c = tuple(int(min(255, v * shade * 1.05)) for v in col)
        tris.append((float(pv[:, 2].mean()), [(size / 2 + q[0] / ext * size * 0.42, size * 0.55 - q[1] / ext * size * 0.42) for q in pv], c))
    im = Image.new("RGB", (size, size), (74, 74, 82))
    d = ImageDraw.Draw(im)
    for z, pts, c in sorted(tris, key=lambda t: t[0]):
        d.polygon(pts, fill=c)
    return im, len(F)


def main():
    K.KIT = sys.argv[1]
    K.PAL = np.array(Image.open(os.path.join(K.KIT, "Models", "GLB format", "Textures", "colormap.png")).convert("RGB"))
    names = sys.argv[3:] or DEFAULT
    cols = 8
    rows = (len(names) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 160, rows * 176), (74, 74, 82))
    d = ImageDraw.Draw(sheet)
    for i, n in enumerate(names):
        im, nt = render(n)
        x, y = (i % cols) * 160, (i // cols) * 176
        sheet.paste(im, (x, y))
        d.text((x + 4, y + 160), "%s %d" % (n, nt), fill=(220, 220, 220))
    sheet.save(sys.argv[2])


if __name__ == "__main__":
    main()
