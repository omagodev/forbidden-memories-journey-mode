#!/usr/bin/env python3
"""Bake Kenney's Fantasy Town Kit 2.0 (CC0, https://kenney.nl) into the flat meshes of Journey Mode.

The kit is modular: walls, doors, windows, roofs, fences, stalls, rocks, trees.  This script assembles houses
from the pieces at the offsets the kit is built on (one module is one unit: a wall is 1 x 1 with its
outer face at x = +0.5, a gable roof sits on top of it) and bakes each result, and a few single props,
into one NPC1 mesh:

  "NPC1", u16 nv, u16 nf, u16 nframes (1), u16 0
  nframes * nv * 3  i16   vertex positions, world units, y up is negative
  nf * 10           u8    three u16 vertex indices, r, g, b, lift (a flat colour with the sun baked in)

Colours are the kit's own: every triangle takes the texel of the kit's palette (colormap.png) at the
centre of its UV triangle, with v flipped.  Faces the mod's camera cannot see (it never turns: the inside of
a wall, undersides, the back of a roof) are left out.  Big pieces are simplified with quadric edge
collapse and each face of the result takes the colour of the nearest original face.  S is the size of one
module in world units (a tile is 32).

The kit is not in the repository: pass the unzipped folder (Models/OBJ format/*.obj and Textures).
Only the baked pieces the map uses are committed (assets/k_*.bin).  kenney_sheet.py draws the pieces from
the OBJ files for a visual check against the kit's Preview.png.

Usage: bake_kenney.py KIT_DIR OUT_DIR [--preview DIR] [--compare sheet.png] [--flat]
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
    """(vertices, uvs, triangles of ((v, vt), ...)) of one OBJ piece."""
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
    """The colormap texel at a UV (v is up in OBJ, down in the image)."""
    u, v = vt
    return PAL[min(511, max(0, int((1 - v) * 512))), min(511, max(0, int(u * 512)))].astype(float)


def rot_y(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def cull(T, out_w=None):
    """Drop the faces the camera cannot see, and those turned away from out_w (a world vector)."""
    keep = []
    for p, n, c in T:
        if n @ CAM < -0.35 or n[1] < -0.5:
            continue
        if out_w is not None and n @ out_w < -0.3:
            continue
        keep.append((p, n, c))
    return keep


def piece(name, yaw=0.0, pos=(0, 0, 0), scale=(1, 1, 1), outward=None, raw=False):
    """Triangles (points, normal, colour) of one kit piece in world units.  outward, a vector in the piece's own
    frame, drops the faces turned away from it (the inside of a wall); faces the camera cannot see are
    always dropped."""
    V, VT, F = load(name)
    R = rot_y(yaw)
    sc = np.array(scale, float)
    out_w = None if outward is None else R @ np.array(outward, float)
    out = []
    for tri in F:
        p = np.array([V[t[0]] for t in tri]) * sc
        p = p @ R.T + np.array(pos)
        n = np.cross(p[1] - p[0], p[2] - p[0])
        ln = np.linalg.norm(n)
        if ln < 1e-12:
            continue
        n /= ln
        if not raw and (n @ CAM < -0.35 or n[1] < -0.5 or (out_w is not None and n @ out_w < -0.3)):
            continue
        uv = sum(np.array(VT[t[1]]) for t in tri) / 3.0
        out.append((p, n, palette(uv)))
    return out


def simplify(T, target, boundary=False):
    """Weld, collapse to about `target` faces, give every face the colour of the nearest source face."""
    import pymeshlab
    if len(T) <= target:
        return T
    pts = np.array([t[0] for t in T])
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
        if ln < 1e-12:
            continue
        n /= ln
        c = p.mean(0)
        score = ((cen - c) ** 2).sum(1) + (1.0 - nrm @ n) * 40.0     # near, and facing the same way
        out.append((p, n, col[int(score.argmin())]))
    return out


# ---------------------------------------------------------------------------------------- houses
def prune(T, min_area):
    """Drop the faces too small to show at the mod's camera distance (a world unit is a third of a pixel)."""
    return [t for t in T if 0.5 * np.linalg.norm(np.cross(t[0][1] - t[0][0], t[0][2] - t[0][0])) >= min_area]


def lod(T, target, out_w=None, boundary=False):
    """Simplify a whole piece, then keep the faces the camera can see.  Thin open shells (cloth, trunks, fences)
    need boundary=True or they collapse into spikes; the target is then only a floor."""
    return cull(simplify(T, target, boundary), out_w)


def house(width, S, floors=1, door=0, windows=(), roof="roof-gable", wood=False, q=1.0):
    """A house `width` modules wide and one deep, front toward the camera (+z), `floors` storeys, a gable roof
    along x.  Wall pieces stand on the front (outer face +z) and the two sides; the back is never seen.
    q scales the face budget of every piece."""
    T = []
    wall = "wall-wood" if wood else "wall"
    pre = "wall-wood-" if wood else "wall-"
    sc = (S, S, S)
    for f in range(floors):
        y = f * S
        for i in range(width):
            x = (i + 0.5 - width / 2) * S
            name = pre + "door" if (f == 0 and i == door) else pre + ("window-glass" if wood else "window-small") if (f > 0 or i in windows) else wall
            out_w = rot_y(-math.pi / 2) @ np.array([1.0, 0, 0])
            T += lod(piece(name, yaw=-math.pi / 2, pos=(x, y, S / 2 - 0.5 * S), scale=sc, raw=True),
                     int((64 if "door" in name else 54 if "window" in name else 14) * q), out_w)
        for yaw, x in ((0.0, width / 2 * S - 0.5 * S), (math.pi, -width / 2 * S + 0.5 * S)):
            T += lod(piece(wall, yaw=yaw, pos=(x, y, 0), scale=sc, raw=True), int(14 * q), rot_y(yaw) @ np.array([1.0, 0, 0]))
    ry = floors * S
    for i in range(width):
        x = (i + 0.5 - width / 2) * S
        if i in (0, width - 1):
            T += lod(piece(roof, yaw=0.0 if i == 0 else math.pi, pos=(x, ry, 0), scale=sc, raw=True), int(30 * q))
        else:
            T += lod(piece(roof + "-end", yaw=0.0, pos=(x, ry, 0), scale=sc, raw=True), int(16 * q))
    return T


def prop(name, yaw=0.0, scale=1.0, closed=False, outward=None):
    return lambda S: piece(name, yaw=yaw, scale=(scale,) * 3, outward=outward)


FLAT = False        # --flat: the first look, one flat shade a face and no textures


def texture_of(c, n, area):
    """Which atlas tile (bits 0..3 of a face's lift byte: 0 none, 1 plaster, 2 roof tiles, 3 planks) paints a face.
    Only faces big enough for the texture to show get one."""
    r, g, b = c
    if area < 36.0:
        return 0
    if r > 150 and g < 120 and b < 120 or (g > r + 40 and g > 140):    # red and teal roofs
        return 2
    if b > r + 12:                                                     # the kit's lilac plaster and stone
        return 1
    if r > g + 25 and g > b + 15:                                      # brown wood
        return 3
    return 0


def merge_quads(fl, vl):
    """Pair triangles of one colour that share an edge and lie in one plane into quads.  A quad is two
    consecutive faces (a b c) (a c d), the first with bit 7 of its lift byte set; the mod draws it as one
    flat quad (24 bytes of packet buffer instead of 40).  fl: list of (idx, rgb, normal)."""
    edge = {}
    for i, (idx, rgb, n, tex) in enumerate(fl):
        for k in range(3):
            edge.setdefault((idx[k], idx[(k + 1) % 3]), []).append(i)
    used = set()
    out = []
    for i, (idx, rgb, n, tex) in enumerate(fl):
        if i in used:
            continue
        mate = None
        for k in range(3):
            u, v = idx[k], idx[(k + 1) % 3]
            for j in edge.get((v, u), []):
                if j == i or j in used:
                    continue
                jdx, jrgb, jn, jtex = fl[j]
                if jtex != tex or int(np.abs(np.array(jrgb) - np.array(rgb)).max()) > 14 or float(n @ jn) < 0.96:
                    continue
                w = [t for t in jdx if t not in (u, v)]
                if len(w) != 1:
                    continue
                q = [idx[k], w[0], idx[(k + 1) % 3], idx[(k + 2) % 3]]
                pts = [vl[t] for t in q]
                if all(float(np.cross(pts[(m + 1) % 4] - pts[m], pts[(m + 2) % 4] - pts[(m + 1) % 4]) @ n) > 1e-6 for m in range(4)):
                    mate = (j, q)
                    break
            if mate:
                break
        used.add(i)
        if mate:
            used.add(mate[0])
            q = mate[1]
            out.append(([q[0], q[1], q[2]], rgb, True, tex))
            out.append(([q[0], q[2], q[3]], rgb, False, tex))
        else:
            out.append((idx, rgb, False, tex))
    return out


def bake(T, path, preview=None):
    verts = {}
    vl = []
    fl = []
    for p, n, c in T:
        idx = []
        for q in p:
            k = tuple(np.round(q * 8).astype(int))
            if k not in verts:
                verts[k] = len(vl)
                vl.append(q)
            idx.append(verts[k])
        if len(set(idx)) < 3:
            continue
        if FLAT:
            shade = 0.55 + 0.45 * max(0.0, float(n @ SUN))
        else:
            # light from the top left: tops brightest, sides darker, the north-west and south sides darkest,
            # and the foot of a wall darkens a little (ambient occlusion by height)
            shade = 0.50 + 0.62 * max(0.0, float(n @ SUN)) + 0.10 * float(n[1])
            foot = float(np.mean([q[1] for q in p]))
            if foot < 14.0:
                shade *= 0.80 + 0.20 * max(0.0, foot) / 14.0
        rgb = np.clip(c * shade * 1.04, 0, 255).astype(int)
        area = 0.5 * float(np.linalg.norm(np.cross(p[1] - p[0], p[2] - p[0])))
        fl.append((idx, rgb, n, 0 if FLAT else texture_of(c, n, area)))
    fq = merge_quads(fl, vl)
    out = b"NPC1" + struct.pack("<HHHH", len(vl), len(fq), 1, 0)
    for q in vl:
        out += struct.pack("<hhh", int(round(q[0])), int(round(-q[1])), int(round(q[2])))
    for idx, rgb, flag, tex in fq:
        out += struct.pack("<HHHBBBB", idx[0], idx[1], idx[2], rgb[0], rgb[1], rgb[2], (0x80 if flag else 0) | tex)
    open(path, "wb").write(out)
    if preview:
        draw_preview(vl, [(i, r) for i, r, _, _ in fq], preview)
    return len(vl), len(fq), sum(1 for f in fq if f[2])


def tris_to_mesh(T):
    """Vertex list and (indices, rgb) faces of raw (points, normal, colour) triangles, lit like bake() does."""
    vl, fl = [], []
    for p, n, c in T:
        shade = 0.55 + 0.45 * max(0.0, float(n @ SUN))
        fl.append(([len(vl), len(vl) + 1, len(vl) + 2], np.clip(c * shade * 1.12, 0, 255).astype(int)))
        vl += [q for q in p]
    return vl, fl


def draw_preview(vl, fl, path, pitch=50.0):
    """Painter-sorted preview with the mod's projection (JM_PREVIEW_DIST: the camera distance)."""
    ext = max(max(abs(q[0]), abs(q[1]), abs(q[2])) for q in vl) if vl else 50.0
    dist = float(os.environ.get("JM_PREVIEW_DIST", 0)) or max(40.0, 3.7 * ext)
    pc, ps = math.cos(math.radians(pitch)), math.sin(math.radians(pitch))
    im = Image.new("RGB", (320, 240), (150, 190, 120))
    d = ImageDraw.Draw(im)
    pr = []
    mx = (min(q[0] for q in vl) + max(q[0] for q in vl)) / 2 if vl else 0.0
    for q in vl:
        x, y, z = q[0] - mx, -q[1], q[2]
        zz = ps * y + pc * -z + dist
        yy = pc * y - ps * -z
        pr.append((160 + x * 380 / zz, 190 + yy * 380 / zz, zz))
    tris = []
    for idx, rgb in fl:
        tris.append((sum(pr[i][2] for i in idx) / 3, [pr[i][:2] for i in idx], tuple(int(v) for v in rgb)))
    for zc, pts, c in sorted(tris, key=lambda t: -t[0]):
        d.polygon(pts, fill=c)
    im = im.resize((640, 480), Image.NEAREST)
    if path:
        im.save(path)
    return im


def read_bin(path):
    b = open(path, "rb").read()
    nv, nf = struct.unpack("<HH", b[4:8])
    vl = [np.array(struct.unpack("<hhh", b[12 + 6 * i:18 + 6 * i]), float) * np.array([1, -1, 1]) for i in range(nv)]
    o = 12 + 6 * nv
    fl = []
    for i in range(nf):
        f = struct.unpack("<HHHBBBB", b[o + 10 * i:o + 10 * i + 10])
        fl.append((list(f[:3]), np.array(f[3:6])))
    return vl, fl


def contact_sheet(cells, path, kit):
    """Original piece (every face the camera sees) left, the baked mesh right, with face counts."""
    W, H = 480, 360
    cols = 2
    rows = (len(cells) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 2 * W, rows * (H + 18)), (46, 46, 52))
    d = ImageDraw.Draw(sheet)
    for i, (name, a, b, n0, n1) in enumerate(cells):
        x, y = (i % cols) * 2 * W, (i // cols) * (H + 18)
        sheet.paste(a.resize((W, H), Image.LANCZOS), (x, y))
        sheet.paste(b.resize((W, H), Image.LANCZOS), (x + W, y))
        d.text((x + 8, y + H + 3), "%s: kit piece (left, %d faces seen by the camera) / baked for the mod (right, %d polygons)" % (name, n0, n1), fill=(235, 235, 235))
    pv = os.path.join(kit, "Preview.png")
    if os.path.exists(pv):
        top = Image.open(pv).convert("RGB")
        top = top.resize((sheet.width, int(top.height * sheet.width / top.width)), Image.LANCZOS)
        full = Image.new("RGB", (sheet.width, top.height + sheet.height))
        full.paste(top, (0, 0))
        full.paste(sheet, (0, top.height))
        sheet = full
    sheet.save(path)


JOBS_HOUSE = {
    "k_house_a": (2, 48.0, 1, 0, (1,), "roof-high-gable"),
    "k_house_b": (3, 48.0, 1, 1, (0, 2), "roof-gable"),
    "k_house_c": (2, 48.0, 2, 1, (0,), "roof-gable", True),
    "k_house_d": (3, 48.0, 2, 1, (0, 2), "roof-high-gable"),
}


def main():
    global KIT, PAL
    KIT, out = sys.argv[1], sys.argv[2]
    global FLAT
    FLAT = "--flat" in sys.argv
    prev = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    PAL = np.array(Image.open(os.path.join(KIT, "Models", "GLB format", "Textures", "colormap.png")).convert("RGB"))
    os.makedirs(out, exist_ok=True)
    if prev:
        os.makedirs(prev, exist_ok=True)
    S = 48.0
    # name, builder(S), faces to simplify to (0: as they are), keep the boundary of open shells
    jobs = [
        ("k_house_a", lambda: house(*JOBS_HOUSE["k_house_a"]), 0),
        ("k_house_b", lambda: house(*JOBS_HOUSE["k_house_b"]), 0),
        ("k_house_c", lambda: house(*JOBS_HOUSE["k_house_c"]), 0),
        ("k_house_d", lambda: house(*JOBS_HOUSE["k_house_d"]), 0),
        ("k_fence_h", lambda: piece("fence", yaw=-math.pi / 2, scale=(32, 32, 32), raw=True), 44),
        ("k_fence_v", lambda: piece("fence", yaw=0.0, scale=(32, 32, 32), raw=True), 44),
        ("k_stall_red", lambda: piece("stall-red", scale=(58, 58, 58), raw=True), 170),
        ("k_stall_green", lambda: piece("stall-green", scale=(58, 58, 58), raw=True), 170),
        ("k_cart", lambda: piece("cart", scale=(40, 40, 40), raw=True), 150),
        ("k_lantern", lambda: piece("lantern", scale=(30, 30, 30), raw=True), 28),
        ("k_banner", lambda: piece("banner-red", yaw=-math.pi / 2, scale=(44, 44, 44), raw=True), 36),
        ("k_rock_large", lambda: piece("rock-large", scale=(34, 34, 34), raw=True), 44),
        ("k_rock_small", lambda: piece("rock-small", scale=(30, 30, 30), raw=True), 30),
        ("k_rock_wide", lambda: piece("rock-wide", scale=(30, 30, 30), raw=True), 34),
        ("k_tree_round", lambda: piece("tree-high-round", scale=(44, 44, 44), raw=True), 70),
        ("k_tree_pine", lambda: piece("tree", scale=(44, 44, 44), raw=True), 70),
    ]
    compare = sys.argv[sys.argv.index("--compare") + 1] if "--compare" in sys.argv else None
    cells = []
    for name, build, target in jobs:
        if not target:
            T = build()
        elif name.startswith("k_fence"):
            T = prune(cull(build()), 4.0)                    # the kit's rails and posts as they are, minus the bevels
        elif name.startswith(("k_rock", "k_tree", "k_cart")):
            T = lod(build(), target, None, name.startswith("k_tree"))   # solids: collapse first, then cull
        else:
            T = simplify(cull(build()), target, True)        # thin open shells (cloth, rails): cull first, keep the borders
        nv, nf, nq = bake(T, os.path.join(out, name + ".bin"), os.path.join(prev, name + ".png") if prev else None)
        if compare:
            if name.startswith("k_house"):
                src = house(*JOBS_HOUSE[name], q=1000)             # the same house, no face budget
            else:
                src = cull(build())
            a = draw_preview(*tris_to_mesh(src), None)
            vb, fb = read_bin(os.path.join(out, name + ".bin"))
            cells.append((name, a, draw_preview(vb, fb, None), len(src), nf - nq))
        print(name, nv, "vertices", nf, "faces,", nq, "quads (draws", nf - nq, "polygons)")
    if compare:
        contact_sheet(cells, compare, KIT)


if __name__ == "__main__":
    main()
