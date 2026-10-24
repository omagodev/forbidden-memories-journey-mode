#!/usr/bin/env python3
"""Bake Kenney's Fantasy Town Kit 2.0 (CC0, https://kenney.nl) into the flat meshes of Journey Mode.

The kit is modular: walls, doors, windows, roofs, fences, stalls, rocks.  This script assembles houses
from the pieces and bakes each result (and a few single props) into one NPC1 mesh:

  "NPC1", u16 nv, u16 nf, u16 nframes (1), u16 0
  nframes * nv * 3  i16   vertex positions, world units, y up is negative
  nf * 10           u8    three u16 vertex indices, r, g, b, lift (a flat colour: the sun is baked in; lift is
                          half the depth units the face is sorted nearer, for doors and windows on a wall)

The camera of the mod never turns, so faces that cannot be seen from it (the back of a house, the inner
side of a wall, undersides) are left out, then the shell is simplified to a polygon budget with
quadratic edge collapse and every face takes the colour of the nearest original one.  The kit's palette
is a lilac stone; walls are turned to desert sand and the green roofs to blue.  S is the size of one
module in world units (a tile is 32).

The kit is not in the repository: pass the unzipped folder (Models/OBJ format/*.obj and Textures).
Only the baked pieces the map uses are committed (assets/k_*.bin).

Usage: bake_kenney.py KIT_DIR OUT_DIR [--preview DIR]
Needs numpy, Pillow and pymeshlab.
"""
import math
import os
import struct
import sys

import numpy as np
from PIL import Image, ImageDraw

KIT = None
PAL = None
SUN = np.array([-0.45, 0.85, 0.35])
SUN /= np.linalg.norm(SUN)
CAM = np.array([0.0, 0.77, 0.64])        # from the scene toward the camera (pitch 50 degrees)

_cache = {}


def load(name):
    if name in _cache:
        return _cache[name]
    V, VT, F = [], [], []
    for line in open(os.path.join(KIT, "Models", "OBJ format", name + ".obj")):
        p = line.split()
        if not p:
            continue
        if p[0] == "v":
            V.append([float(a) for a in p[1:4]])
        elif p[0] == "vt":
            VT.append([float(a) for a in p[1:3]])
        elif p[0] == "f":
            idx = [tuple(int(a) - 1 if a else -1 for a in (q.split("/") + ["", ""])[:2]) for q in p[1:]]
            for i in range(1, len(idx) - 1):
                F.append((idx[0], idx[i], idx[i + 1]))
    _cache[name] = (np.array(V), np.array(VT), F)
    return _cache[name]


def palette(vt):
    u, v = vt
    return PAL[min(511, max(0, int((1 - v) * 512))), min(511, max(0, int(u * 512)))].astype(float)


def recolour(c, blue_roof):
    """Lilac stone to sand, teal roofs to blue; reds, woods and greens stay."""
    r, g, b = c
    lum = 0.3 * r + 0.59 * g + 0.11 * b
    if b > r + 14 and b > g + 6:                      # the stone
        k = lum / 168.0
        if blue_roof == "rock":
            return np.array([150 * k, 146 * k, 140 * k])
        return np.array([232 * k, 204 * k, 152 * k])
    if g > r + 40 and g > b + 10 and blue_roof:        # a green roof
        k = lum / 150.0
        if blue_roof == "sand":
            return np.array([222 * k, 186 * k, 128 * k])
        return np.array([70 * k, 110 * k, 205 * k])
    return c


def rot_y(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def piece(name, yaw=0.0, pos=(0, 0, 0), scale=(1, 1, 1), keep="front", blue=False):
    """Triangles (points, normal, colour) of one kit piece. keep: "front" faces the camera could see,
    "east"/"west" the faces turned outward on that side as well as the tops, "all"."""
    V, VT, F = load(name)
    R = rot_y(yaw)
    sc = np.array(scale, float)
    out = []
    for tri in F:
        p = np.array([V[t[0]] for t in tri]) * sc
        p = p @ R.T + np.array(pos)
        n = np.cross(p[1] - p[0], p[2] - p[0])
        ln = np.linalg.norm(n)
        if ln < 1e-9:
            continue
        n /= ln
        if keep == "front" and n @ CAM < -0.02:
            continue
        if keep == "east" and not (n[0] > 0.5 or n[1] > 0.3 or n @ CAM > 0.3):
            continue
        if keep == "west" and not (n[0] < -0.5 or n[1] > 0.3 or n @ CAM > 0.3):
            continue
        col = sum(palette(VT[t[1]]) for t in tri) / 3.0
        out.append((p, n, recolour(col, blue)))
    return out


def gable_end(x, w, d, y0, rise, sign, blue):
    """The triangle that closes a gable roof at one end: x is the end, the base spans depth d."""
    col = recolour(np.array([160.0, 168.0, 201.0]), blue)
    a, b, c = np.array([x, y0, -d / 2]), np.array([x, y0, d / 2]), np.array([x, y0 + rise, 0.0])
    p = [a, b, c] if sign > 0 else [a, c, b]
    return [(np.array(p), np.array([sign, 0.0, 0.0]), col)]


def decal(points, colour, z):
    """A flat polygon on the front face (z), triangulated as a fan, facing +z."""
    pts = [np.array([x, y, z]) for x, y in points]
    return [(np.array([pts[0], pts[i], pts[i + 1]]), np.array([0.0, 0.0, 1.0]), np.array(colour, float), 64)
            for i in range(1, len(pts) - 1)]


def door_decal(cx, S, H, z):
    """A wooden door with a round top and a lighter frame."""
    w, h = 0.26 * S, 0.62 * S * H
    arch = [(cx + math.cos(a) * w, h + math.sin(a) * w * 0.9) for a in np.linspace(0, math.pi, 7)]
    frame = [(cx - w - 0.04 * S, 0.0), (cx + w + 0.04 * S, 0.0)] + [(x + (0.04 * S if x > cx else -0.04 * S), y + 0.04 * S) for x, y in arch]
    T = decal(frame, (190, 124, 93), z + 0.5)
    T += decal([(cx - w, 0.0), (cx + w, 0.0)] + arch, (121, 73, 57), z + 1.0)
    return T


def window_decal(cx, S, H, z):
    w, h, y = 0.17 * S, 0.22 * S * H, 0.52 * S * H
    T = decal([(cx - w - 0.04 * S, y - 0.04 * S), (cx + w + 0.04 * S, y - 0.04 * S), (cx + w + 0.04 * S, y + h + 0.04 * S), (cx - w - 0.04 * S, y + h + 0.04 * S)], (190, 124, 93), z + 0.5)
    T += decal([(cx - w, y), (cx + w, y), (cx + w, y + h), (cx - w, y + h)], (92, 112, 150), z + 1.0)
    return T


def house(width, depth, roof, door, windows, chimney, blue, S, H=1.25):
    """roof: "flat" (a sand coloured slab, like the target look) or a gable piece of the kit."""
    """A house of width x depth modules, front toward the camera (+z).  Returns triangles in world units."""
    T = []
    decals = []
    for i in range(width):                                 # the front wall, door and windows
        x = (i + 0.5 - width / 2) * S
        T += piece("wall", yaw=-math.pi / 2, pos=(x, 0, depth / 2 * S - 0.5 * S), scale=(S, S * H, S), blue=blue)
        if i == door:
            decals += door_decal(x, S, H, depth / 2 * S)
        elif i in windows:
            decals += window_decal(x, S, H, depth / 2 * S)
    for j in range(depth):                                  # the sides
        z = (j + 0.5 - depth / 2) * S
        T += piece("wall", yaw=0.0, pos=(width / 2 * S - 0.5 * S, 0, z), scale=(S, S * H, S), keep="east", blue=blue)
        T += piece("wall", yaw=math.pi,
                   pos=(-width / 2 * S + 0.5 * S, 0, z), scale=(S, S * H, S), keep="west", blue=blue)
    if roof == "flat":
        for i in range(width):
            for j in range(depth):
                T += piece("roof-flat", pos=((i + 0.5 - width / 2) * S, S * H, (j + 0.5 - depth / 2) * S), scale=(S, S, S), blue="sand")
    else:
        for i in range(width):                              # one gable module a column, stretched to the depth
            T += piece(roof, pos=((i + 0.5 - width / 2) * S, S * H, 0), scale=(S, S, S * depth), blue=blue)
        T += gable_end(width / 2 * S, width, depth * S * 0.98, S * H, 0.57 * S, 1, blue)
        T += gable_end(-width / 2 * S, width, depth * S * 0.98, S * H, 0.57 * S, -1, blue)
    if chimney:
        T += piece("chimney", yaw=0.0, pos=((chimney - width / 2) * S - 0.3 * S, S * H * 1.0, -0.15 * S), scale=(S, S, S), blue=blue)
    return T, decals


def simplify(T, target, boundary=False):
    """Weld, collapse to about `target` faces, give every face the colour of the nearest source face."""
    import pymeshlab
    pts = np.array([t[0] for t in T])                       # n x 3 x 3
    nrm = np.array([t[1] for t in T])
    col = np.array([t[2] for t in T])
    cen = pts.mean(1)
    verts = pts.reshape(-1, 3)
    key = np.round(verts * 64).astype(np.int64)
    uniq, inv = np.unique(key, axis=0, return_inverse=True)
    inv = np.asarray(inv).reshape(-1)
    vpos = np.zeros((len(uniq), 3))
    vpos[inv] = verts
    faces = inv.reshape(-1, 3)
    if len(faces) > target:
        ms = pymeshlab.MeshSet()
        ms.add_mesh(pymeshlab.Mesh(vertex_matrix=vpos, face_matrix=faces.astype(np.int32)))
        ms.meshing_remove_duplicate_faces()
        ms.meshing_remove_unreferenced_vertices()
        ms.meshing_decimation_quadric_edge_collapse(targetfacenum=target, preserveboundary=boundary, boundaryweight=1.0,
                                                    preservenormal=True, planarquadric=True, qualitythr=0.4)
        m = ms.current_mesh()
        vpos, faces = m.vertex_matrix(), m.face_matrix()
    out = []
    for f in faces:
        p = vpos[f]
        n = np.cross(p[1] - p[0], p[2] - p[0])
        ln = np.linalg.norm(n)
        if ln < 1e-9:
            continue
        n /= ln
        c = p.mean(0)
        # nearest source face by position, with a penalty for a different direction
        score = ((cen - c) ** 2).sum(1) + (1.0 - nrm @ n) * 40.0
        out.append((p, n, col[int(score.argmin())]))
    return out


def bake(T, path, preview=None):
    verts = {}
    vl = []
    fl = []
    for item in T:
        p, n, c = item[:3]
        lift = item[3] if len(item) > 3 else 0
        if n @ CAM < -0.3 and n[1] < 0:
            continue
        idx = []
        for q in p:
            k = tuple(np.round(q * 8).astype(int))
            if k not in verts:
                verts[k] = len(vl)
                vl.append(q)
            idx.append(verts[k])
        shade = 0.58 + 0.42 * max(0.0, float(n @ SUN))
        rgb = np.clip(c * shade * 1.10, 0, 255).astype(int)
        fl.append((idx, rgb, lift))
    out = b"NPC1" + struct.pack("<HHHH", len(vl), len(fl), 1, 0)
    for q in vl:
        out += struct.pack("<hhh", int(round(q[0])), int(round(-q[1])), int(round(q[2])))
    for idx, rgb, lift in fl:
        out += struct.pack("<HHHBBBB", idx[0], idx[1], idx[2], rgb[0], rgb[1], rgb[2], lift)
    open(path, "wb").write(out)
    if preview:
        draw_preview(vl, fl, preview)
    return len(vl), len(fl)


def draw_preview(vl, fl, path, pitch=50.0, dist=420.0):
    """Painter-sorted preview with the mod's projection."""
    pc, ps = math.cos(math.radians(pitch)), math.sin(math.radians(pitch))
    im = Image.new("RGB", (320, 240), (150, 190, 120))
    d = ImageDraw.Draw(im)
    pr = []
    for q in vl:
        x, y, z = q[0], -q[1], q[2]
        rz = -z
        zz = ps * (-y) * -1 + pc * rz + dist
        zz = ps * y + pc * rz + dist
        yy = pc * y - ps * rz
        pr.append((160 + x * 380 / zz, 190 + yy * 380 / zz, zz))
    tris = []
    for idx, rgb, lift in fl:
        zc = sum(pr[i][2] for i in idx) / 3 - lift * 0.5
        tris.append((zc, [pr[i][:2] for i in idx], tuple(int(v) for v in rgb)))
    for zc, pts, c in sorted(tris, key=lambda t: -t[0]):
        d.polygon(pts, fill=c)
    im.resize((640, 480), Image.NEAREST).save(path)


def prop(name, yaw, sx, sy, sz, tone=False, keep="front"):
    return lambda: piece(name, yaw=yaw, scale=(sx, sy, sz), blue=tone, keep=keep)


def main():
    global KIT, PAL
    KIT, out = sys.argv[1], sys.argv[2]
    prev = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    PAL = np.array(Image.open(os.path.join(KIT, "Models", "GLB format", "Textures", "colormap.png")).convert("RGB"))
    os.makedirs(out, exist_ok=True)
    S = 52.0
    jobs = [
        ("k_house_a", lambda: house(2, 1, "flat", 0, (1,), None, False, S), 90),
        ("k_house_b", lambda: house(3, 1, "flat", 1, (0, 2), None, False, S), 110),
        ("k_house_c", lambda: house(2, 1, "roof-gable", 1, (0,), None, True, S, 1.0), 100),
        ("k_house_d", lambda: house(3, 2, "flat", 1, (0, 2), None, False, S), 150),
    ]
    jobs += [
        ("k_fence_h", prop("fence", -math.pi / 2, 32, 44, 32), 18),
        ("k_fence_v", prop("fence", 0.0, 32, 44, 32), 18),
        ("k_stall_red", prop("stall-red", 0.0, 44, 44, 44), 70),
        ("k_stall_green", prop("stall-green", 0.0, 44, 44, 44), 70),
        ("k_cart", prop("cart", 0.0, 40, 40, 40), 70),
        ("k_lantern", prop("lantern", 0.0, 30, 30, 30), 22),
        ("k_banner", prop("banner-red", -math.pi / 2, 44, 44, 44), 24),
        ("k_rock_large", prop("rock-large", 0.0, 34, 34, 34, "rock"), 34),
        ("k_rock_small", prop("rock-small", 0.0, 30, 30, 30, "rock"), 22),
        ("k_rock_wide", prop("rock-wide", 0.0, 30, 30, 30, "rock"), 28),
        ("k_tree", prop("tree", 0.0, 34, 34, 34), 50),
    ]
    for name, build, target in jobs:
        T = build()
        if isinstance(T, tuple):                           # a house: the decals (door, windows) stay as they are
            T = simplify(T[0], target, True) + T[1]
        else:
            T = simplify(T, target)
        nv, nf = bake(T, os.path.join(out, name + ".bin"), os.path.join(prev, name + ".png") if prev else None)
        print(name, nv, "vertices", nf, "faces")


if __name__ == "__main__":
    main()
