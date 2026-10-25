#!/usr/bin/env python3
"""Pre-render characters into 4-direction sprite sheets for the painted scene.
Sources: n2 meshes (the game's own lighting + camera) or the animated Kenney Survivors character.
Cell 48x62 texels, feet anchor at (24,56). Output per character:  planes slot/shade/rgb  (see README in sprite_work)."""
import sys, os, struct, math
import numpy as np
from PIL import Image

CW, CH = 48, 62
FX, FY = 24, 56
SS = 5                        # supersampling
PITCH = math.radians(40)
CP, SP = math.cos(PITCH), math.sin(PITCH)
TEX_PER_WORLD = 380.0 / 1400.0 * 2.0        # texels per world unit at the player's depth (2 texels per game unit)
YAWS = [("down", 0.0), ("left", -math.pi / 2), ("right", math.pi / 2), ("up", math.pi)]   # same order as the game's yaw: atan2(dx,dy)

def load_n2(path):
    d = open(path, "rb").read()
    nv, nf, nfr = struct.unpack_from("<HHH", d, 4)
    pos = 12
    V = np.frombuffer(d, "<i2", nfr * nv * 3, pos).reshape(nfr, nv, 3).astype(np.float64); pos += nfr * nv * 6
    rec = np.frombuffer(d, np.uint8, nv * 7, pos).reshape(nv, 7); pos += nv * 7
    F = np.frombuffer(d, "<u2", nf * 3, pos).reshape(nf, 3).astype(np.int64)
    N = rec[:, :3].astype(np.int8).astype(np.float64) / 127.0
    return dict(V=V, N=N, slot=rec[:, 3].astype(int), col=rec[:, 4:7].astype(np.float64), F=F)

def raster(P2, Z, attrs, tri_shape):
    """P2: (n,3,2) supersampled pixel coords, Z (n,3) depth (smaller = nearer); attrs: (n,3,k). Returns (zbuf, attrbuf k)"""
    H, W = CH * SS, CW * SS
    zb = np.full((H, W), 1e18); k = attrs.shape[2]
    ab = np.zeros((H, W, k)); idx = np.full((H, W), -1, np.int32); bw = np.zeros((H, W, 3))
    for t in range(len(P2)):
        p = P2[t]
        x0 = max(int(math.floor(p[:, 0].min())), 0); x1 = min(int(math.ceil(p[:, 0].max())), W - 1)
        y0 = max(int(math.floor(p[:, 1].min())), 0); y1 = min(int(math.ceil(p[:, 1].max())), H - 1)
        if x1 < x0 or y1 < y0: continue
        den = (p[1, 1] - p[2, 1]) * (p[0, 0] - p[2, 0]) + (p[2, 0] - p[1, 0]) * (p[0, 1] - p[2, 1])
        if abs(den) < 1e-9: continue
        xs, ys = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        l0 = ((p[1, 1] - p[2, 1]) * (xs - p[2, 0]) + (p[2, 0] - p[1, 0]) * (ys - p[2, 1])) / den
        l1 = ((p[2, 1] - p[0, 1]) * (xs - p[2, 0]) + (p[0, 0] - p[2, 0]) * (ys - p[2, 1])) / den
        l2 = 1 - l0 - l1
        m = (l0 >= -1e-6) & (l1 >= -1e-6) & (l2 >= -1e-6)
        if not m.any(): continue
        z = l0 * Z[t, 0] + l1 * Z[t, 1] + l2 * Z[t, 2]
        sub = zb[y0:y1 + 1, x0:x1 + 1]
        win = m & (z < sub - 1e-6)
        if not win.any(): continue
        sub[win] = z[win]
        av = l0[..., None] * attrs[t, 0] + l1[..., None] * attrs[t, 1] + l2[..., None] * attrs[t, 2]
        ab[y0:y1 + 1, x0:x1 + 1][win] = av[win]
        idx[y0:y1 + 1, x0:x1 + 1][win] = t
        bw[y0:y1 + 1, x0:x1 + 1][win] = np.stack([l0, l1, l2], -1)[win]
    return zb, ab, idx, bw

def finish(cov_mask, attr_ss):
    """supersampled (H,W,7: W1..W4, fixed rgb) -> texel planes: solid by coverage, mean attrs of covered samples, 1-texel outline"""
    H, W = CH, CW
    def blk(a): return a.reshape(H, SS, W, SS, *a.shape[2:])
    m = cov_mask.astype(np.float64)
    cov = blk(m).mean((1, 3))
    solid = cov >= 0.45
    wsum = blk(m).sum((1, 3)); wsum[wsum == 0] = 1
    at = (blk(attr_ss * m[..., None]).sum((1, 3))) / wsum[..., None]
    pad = np.pad(solid, 1)
    near = pad[:-2, 1:-1] | pad[2:, 1:-1] | pad[1:-1, :-2] | pad[1:-1, 2:]
    out = (~solid) & near
    kind = np.where(solid, 0, np.where(out, 254, 255)).astype(np.uint8)
    at[~solid] = 0
    return kind, at

def render_n2(mesh, frame, yaw, scale, recolour=False):
    V = mesh["V"][frame] * scale
    cy, sy = math.cos(yaw), math.sin(yaw)
    mx, my, mz = V[:, 0], V[:, 1], V[:, 2]
    dx = cy * mx + sy * mz; dz = cy * mz - sy * mx
    sxp = dx * TEX_PER_WORLD; syp = (CP * my + SP * dz) * TEX_PER_WORLD
    depth = SP * my - CP * dz
    nx, ny, nz = mesh["N"].T
    rx = cy * nx + sy * nz; rz = cy * nz - sy * nx
    l = (0.40 + 0.55 * np.maximum(rx * 0.35 - ny * 0.80 + rz * 0.50, 0) + 0.10 * (-ny)) * 1.15
    X = (FX + sxp) * SS; Y = (FY + syp) * SS
    F = mesh["F"]
    P2 = np.stack([X[F], Y[F]], -1)
    a = (P2[:, 1, 0] - P2[:, 0, 0]) * (P2[:, 2, 1] - P2[:, 0, 1]) - (P2[:, 2, 0] - P2[:, 0, 0]) * (P2[:, 1, 1] - P2[:, 0, 1])
    keep = a >= 0
    F = F[keep]; P2 = P2[keep]
    va = np.zeros((len(l), 7))
    for i in range(len(l)):
        s_ = mesh["slot"][i]
        if recolour and 1 <= s_ <= 4: va[i, s_ - 1] = l[i]
        else: va[i, 4:7] = mesh["col"][i] * l[i]
    zb, ab, idx, bw = raster(P2, depth[F], va[F], None)
    return finish(idx >= 0, ab)

def load_kenney():
    z = np.load("/workspace/study/fmrecomp/sprite_work/kenney_frames.npz")
    return z

def render_kenney(z, key, yaw, tex, scale):
    P = z[key + "_P"].astype(np.float64); N = z[key + "_N"].astype(np.float64)
    tris = z["tris"]; uv = z["uv"].astype(np.float64)
    mx, my, mz = P[:, 0] * scale, -P[:, 2] * scale, -P[:, 1] * scale
    cy, sy = math.cos(yaw), math.sin(yaw)
    dx = cy * mx + sy * mz; dz = cy * mz - sy * mx
    sxp = dx * TEX_PER_WORLD; syp = (CP * my + SP * dz) * TEX_PER_WORLD
    depth = SP * my - CP * dz
    nx, ny, nz = N[:, 0], -N[:, 2], -N[:, 1]
    rx = cy * nx + sy * nz; rz = cy * nz - sy * nx
    l = (0.50 + 0.50 * np.maximum(rx * 0.35 - ny * 0.80 + rz * 0.50, 0) + 0.10 * (-ny)) * 1.08
    X = (FX + sxp) * SS; Y = (FY + syp) * SS
    P2 = np.stack([X[tris], Y[tris]], -1)
    attrs = np.concatenate([uv, l[tris][..., None]], -1)
    zb, ab, idx, bw = raster(P2, depth[tris], attrs, None)
    cov = idx >= 0
    tw, th = tex.shape[1], tex.shape[0]
    u = np.clip((ab[..., 0] * tw).astype(int), 0, tw - 1); v = np.clip(((1 - ab[..., 1]) * th).astype(int), 0, th - 1)
    rgb = np.clip(tex[v, u].astype(np.float64) * np.clip(ab[..., 2], 0, 1.5)[..., None], 0, 255)
    at = np.zeros(cov.shape + (7,)); at[..., 4:7] = rgb
    return finish(cov, at)

def colourise(cell, palette, outline=(34, 24, 30)):
    kind, at = cell
    rgb = at[..., 4:7].copy()
    for s_ in range(1, 5):
        if s_ in palette: rgb += at[..., s_ - 1:s_] * np.array(palette[s_])
    img = np.zeros((CH, CW, 4), np.uint8)
    img[..., :3] = np.clip(rgb, 0, 255).astype(np.uint8)
    img[..., 3] = np.where(kind == 0, 255, 0)
    o = kind == 254
    img[o, :3] = outline; img[o, 3] = 255
    return img

def hexrgb(h): return ((h >> 16) & 255, (h >> 8) & 255, h & 255)
def outfit_dark(o):
    r, g, b = hexrgb(o); return (r * 5 // 11, g * 5 // 11, b * 5 // 11)

def bake_char(name, frames_fn, nwalk, kenney=False, palette=None):
    """frames_fn(frame_index, yaw) -> (slot, shade, rgb, solid); frame 0 idle, 1..nwalk walk"""
    cells = {}
    for dname, yaw in YAWS:
        for f in range(nwalk + 1):
            cells[(dname, f)] = frames_fn(f, yaw)
    return cells

def write_bin(path, cells, nwalk):
    """'SPR1', u16 frames, cw, ch, fx, fy; then for dir (down,left,right,up) x frame: kind[ch*cw] (0 solid, 254 outline, 255 empty), W1..W4 (u8, value*100), fixed rgb"""
    with open(path, "wb") as f:
        f.write(b"SPR1" + struct.pack("<HHHHH", nwalk + 1, CW, CH, FX, FY))
        for dname, _ in YAWS:
            for fr in range(nwalk + 1):
                kind, at = cells[(dname, fr)]
                f.write(kind.tobytes())
                f.write(np.clip(at[..., :4] * 100, 0, 255).round().astype(np.uint8).tobytes())
                f.write(np.clip(at[..., 4:7], 0, 255).round().astype(np.uint8).tobytes())

def contact(cells, nwalk, palette, kenney, bg=(150, 170, 120), zoom=3, outline=(34, 24, 30)):
    cols = nwalk + 1
    im = Image.new("RGBA", (cols * CW, 4 * CH), bg + (255,))
    for r, (dname, _) in enumerate(YAWS):
        for f in range(cols):
            c = colourise(cells[(dname, f)], palette, outline)
            im.alpha_composite(Image.fromarray(c, "RGBA"), (f * CW, r * CH))
    return im.resize((im.width * zoom, im.height * zoom), Image.NEAREST)

if __name__ == "__main__":
    OUT = "/workspace/study/fmrecomp/sprite_work/out"; os.makedirs(OUT, exist_ok=True)
    AS = "/workspace/study/fmrecomp/snap_painted_sprite/mods/ow-poc/assets/"
    HAIR = [0x5A2A78, 0x1C1C22, 0x6A4020, 0xE0C050, 0xB82818]; SKIN = [0xEBBE96, 0xBE8C64, 0x785032]; OUTFIT = [0x3246AA, 0xAA2828, 0x287838, 0x2C2C34, 0xC8C8CE]
    which = sys.argv[1:] or ["player", "wizard", "kenney_m", "kenney_f"]
    for w in which:
        if w in ("player", "wizard", "witch", "knight"):
            nm = {"player": "Casual_Male", "wizard": "Wizard", "witch": "Witch", "knight": "Knight_Male"}[w]
            mesh = load_n2(AS + nm + ".n2")
            scale = float(os.environ.get("N2SCALE", "2.3"))
            palette = {1: hexrgb(SKIN[0]), 2: hexrgb(HAIR[0]), 3: hexrgb(OUTFIT[0]), 4: outfit_dark(OUTFIT[0])} if w == "player" else {}
            walk_frames = [1, 2, 3, 4]
            fn = lambda f, yaw, mesh=mesh, scale=scale, wf=walk_frames, rc=(w == 'player'): render_n2(mesh, 0 if f == 0 else wf[f - 1], yaw, scale, rc)
            cells = bake_char(w, fn, 4)
            nwalk, kenney = 4, False
        else:
            z = load_kenney()
            skin = {"kenney_m": "survivorMaleB", "kenney_f": "survivorFemaleA", "kenney_z": "zombieA"}[w]
            tex = np.array(Image.open("/workspace/study/fmrecomp/assets_ext/kenney_survivors/Skins/%s.png" % skin).convert("RGB"))
            ks = float(os.environ.get("KSCALE", "31"))
            fn = lambda f, yaw, z=z, tex=tex, ks=ks: render_kenney(z, "idle" if f == 0 else "run%d" % (f - 1), yaw, tex, ks)
            cells = bake_char(w, fn, 6)
            nwalk, kenney, palette = 6, True, {}
        write_bin(OUT + "/spr_%s.bin" % w, cells, nwalk)
        contact(cells, nwalk, palette, kenney).save(OUT + "/sheet_%s.png" % w)
        print("baked", w)
