#!/usr/bin/env python3
"""Bake a Quaternius character (CC0, glTF) into an NPC2 mesh for Journey Mode.

NPC2 (little endian):
  "NPC2", u16 nv, u16 nf, u16 nframes, u16 0
  nframes * nv * 3  i16   vertex positions, y up is negative, 56 units tall
  nv * 7            u8    nx, ny, nz (i8, 127 = 1.0, idle pose), slot, r, g, b
  nf * 3            u16   triangle vertex indices

`slot` tells the engine which part of a character a vertex belongs to, so the
character creator can recolour it: 1 skin, 2 hair, 3 outfit, 4 trousers, 0 the
rest.  Colours are the material's own; the engine lights them per vertex
(Gouraud) with the vertex normal.  Frames: Idle, then four Walk poses.

The glTF files are not in the repository (Quaternius, "Ultimate Animated
Character Pack", https://quaternius.com, CC0 1.0): pass their directory.

Usage: bake_npc.py SRC_DIR OUT_DIR Name [Name...]   (e.g. Wizard Casual_Male)
Needs numpy and pymeshlab.
"""
import base64
import json
import math
import os
import struct
import sys

import numpy as np
import pymeshlab

HEIGHT = 56.0
TARGET = int(os.environ.get("JM_FACES", "700"))     # faces of a baked character
FRAMES = [("Idle", 0.0), ("Walk", 0.0), ("Walk", 0.25), ("Walk", 0.5), ("Walk", 0.75)]
SLOTS = {"Skin": 1, "Hair": 2, "Shirt": 3, "Main": 3, "Clothes": 3, "Pants": 4}


def load(src, name):
    g = json.load(open(os.path.join(src, name + ".gltf")))
    buf = [base64.b64decode(b["uri"].split(",", 1)[1]) for b in g["buffers"]]

    def acc(i):
        a = g["accessors"][i]
        bv = g["bufferViews"][a["bufferView"]]
        ct = {5126: "f4", 5123: "u2", 5125: "u4", 5121: "u1"}[a["componentType"]]
        n = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}[a["type"]]
        off = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
        arr = np.frombuffer(buf[bv["buffer"]], dtype=np.dtype(ct), count=a["count"] * n, offset=off)
        return arr.reshape(a["count"], n).astype(np.float64 if ct == "f4" else np.int64)

    return g, acc


def qmat(q):
    x, y, z, w = q
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def trs(t, r, s):
    m = np.eye(4)
    m[:3, :3] = qmat(r) * np.array(s)
    m[:3, 3] = t
    return m


def sample(g, acc, anim, tt):
    nodes = g["nodes"]
    T = [np.array(n.get("translation", [0, 0, 0]), float) for n in nodes]
    R = [np.array(n.get("rotation", [0, 0, 0, 1]), float) for n in nodes]
    S = [np.array(n.get("scale", [1, 1, 1]), float) for n in nodes]
    a = [x for x in g["animations"] if x["name"] == anim][0]
    for ch in a["channels"]:
        sm = a["samplers"][ch["sampler"]]
        ti = acc(sm["input"])[:, 0]
        vo = acc(sm["output"])
        t = tt * ti[-1]
        k = min(max(np.searchsorted(ti, t), 1), len(ti) - 1)
        f = min(max((t - ti[k - 1]) / max(1e-9, ti[k] - ti[k - 1]), 0), 1)
        v = vo[k - 1] * (1 - f) + vo[k] * f
        nd, p = ch["target"]["node"], ch["target"]["path"]
        if p == "rotation":
            R[nd] = v / np.linalg.norm(v)
        elif p == "translation":
            T[nd] = v
        elif p == "scale":
            S[nd] = v
    W = [None] * len(nodes)
    par = {c: i for i, n in enumerate(nodes) for c in n.get("children", [])}

    def world(i):
        if W[i] is None:
            W[i] = (world(par[i]) if i in par else np.eye(4)) @ trs(T[i], R[i], S[i])
        return W[i]

    return [world(i) for i in range(len(nodes))]


def srgb(c):
    return [int(255 * min(1.0, x ** (1 / 2.2))) for x in c]


def bake(src, name):
    g, acc = load(src, name)
    mesh = g["meshes"][0]
    skin = g["skins"][0]
    meshnode = [i for i, n in enumerate(g["nodes"]) if n.get("mesh") == 0][0]
    ibm = acc(skin["inverseBindMatrices"]).reshape(-1, 4, 4).transpose(0, 2, 1)
    joints = skin["joints"]
    total = sum(len(acc(q["indices"])) // 3 for q in mesh["primitives"])
    P, J, Wt, faces, col, slot = [], [], [], [], [], []
    base = 0
    for pr in mesh["primitives"]:
        pos = acc(pr["attributes"]["POSITION"])
        jo = acc(pr["attributes"]["JOINTS_0"])
        we = acc(pr["attributes"]["WEIGHTS_0"])
        idx = acc(pr["indices"])[:, 0].reshape(-1, 3)
        mat = g["materials"][pr["material"]]
        c = srgb(mat["pbrMetallicRoughness"].get("baseColorFactor", [.8, .8, .8, 1])[:3])
        mn = mat.get("name", "")
        if mn == "Skin" and c[0] < 40:
            c = [205, 150, 105]
        ms = pymeshlab.MeshSet()
        ms.add_mesh(pymeshlab.Mesh(vertex_matrix=pos, face_matrix=idx))
        ms.meshing_merge_close_vertices()
        tf = max(10, int(TARGET * len(idx) / total))
        if len(idx) > tf:
            ms.meshing_decimation_quadric_edge_collapse(targetfacenum=tf, preserveboundary=False, preservenormal=True)
        m = ms.current_mesh()
        v2, f2 = m.vertex_matrix(), m.face_matrix()
        nn = ((v2[:, None, :] - pos[None, :, :]) ** 2).sum(-1).argmin(1)
        P += list(v2)
        J += list(jo[nn])
        Wt += list(we[nn])
        faces += [(a + base, b + base, cc + base) for a, b, cc in f2]
        col += [c] * len(v2)
        slot += [SLOTS.get(mn, 0)] * len(v2)
        base += len(v2)
    P, J, Wt = np.array(P), np.array(J), np.array(Wt)
    frames = []
    for anim, t in FRAMES:
        Wm = sample(g, acc, anim, t)
        Mn = np.linalg.inv(Wm[meshnode])
        jm = np.array([Mn @ Wm[j] @ ibm[k] for k, j in enumerate(joints)])
        hp = np.c_[P, np.ones(len(P))]
        out = np.zeros((len(P), 3))
        for k in range(4):
            out += Wt[:, k:k + 1] * np.einsum("nij,nj->ni", jm[J[:, k]], hp)[:, :3]
        out = (Wm[meshnode] @ np.c_[out, np.ones(len(out))].T).T[:, :3]
        frames.append(out)
    f0 = frames[0]
    sc = HEIGHT / (f0[:, 1].max() - f0[:, 1].min())
    y0 = f0[:, 1].min()
    # the model's x is mirrored and y runs down in the engine's space
    tr = lambda p: np.c_[-p[:, 0], -(p[:, 1] - y0), p[:, 2]] * sc
    ef = [tr(f) for f in frames]
    nrm = np.zeros((len(P), 3))
    for a, b, c in faces:
        n = np.cross(ef[0][b] - ef[0][a], ef[0][c] - ef[0][a])
        for v in (a, b, c):
            nrm[v] += n
    ln = np.linalg.norm(nrm, axis=1, keepdims=True)
    nrm = nrm / np.maximum(ln, 1e-9)
    blob = b"NPC2" + struct.pack("<HHHH", len(P), len(faces), len(ef), 0)
    for fr in ef:
        for x, y, z in fr:
            blob += struct.pack("<3h", round(x), round(y), round(z))
    for i in range(len(P)):
        blob += struct.pack("<3bB3B", *[int(round(v * 127)) for v in nrm[i]], slot[i], *col[i])
    for a, b, c in faces:
        blob += struct.pack("<3H", a, b, c)
    return blob, len(P), len(faces)


if __name__ == "__main__":
    src, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    for n in sys.argv[3:]:
        data, nv, nf = bake(src, n)
        open(os.path.join(out, n + ".n2"), "wb").write(data)
        print(n, nv, "vertices", nf, "triangles", len(data), "bytes")
