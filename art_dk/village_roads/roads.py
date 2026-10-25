#!/usr/bin/env python3
"""Replace the yellow-brick roads of the painted village with Egyptian-oasis paths.  Same pixel size as bg_clean/bg_raw (1280x720).
Usage: .venv/bin/python roads.py   -> mask_road.png, A_*/B_* (clean + raw), preview + diff, comparison.
Only pixels inside the road mask (plus a thin yellow fringe) change; palms/houses/water/bridge/bushes are not touched."""
import os, sys
import cv2, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
P = '/workspace/study/fmrecomp/painted_work/'
RAW = cv2.cvtColor(cv2.imread(P + 'bg_raw.jpg'), cv2.COLOR_BGR2RGB)
CLEAN = cv2.cvtColor(cv2.imread(P + 'bg_clean.png'), cv2.COLOR_BGR2RGB)
H, W = CLEAN.shape[:2]

def hsv(a):
    x = cv2.cvtColor(a, cv2.COLOR_RGB2HSV_FULL).astype(float)
    return x[..., 0] * 360 / 255, x[..., 1] / 255, x[..., 2] / 255

# ------------------------------------------------------------------ road mask: colour segmentation + geometric completion under the palm blobs
def road_mask():
    h, s, v = hsv(CLEAN)
    m = (((h > 34) & (h < 50) & (s > 0.70) & (v > 0.78)) * 255).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)); m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    nl, lab, st, _ = cv2.connectedComponentsWithStats(m)
    keep = np.zeros_like(m)
    for k in range(1, nl):
        if st[k, 4] > 1500: keep[lab == k] = 255
    g = np.zeros_like(keep)
    def poly(pts): cv2.fillPoly(g, [np.array(pts, np.int32)], 255)
    poly([(0, 417), (1280, 419), (1280, 472), (640, 473), (0, 471)])                           # horizontal road
    poly([(924, 0), (979, 0), (1060, 405), (1060, 420), (1004, 420)])                          # vertical road (north)
    poly([(988, 470), (1056, 470), (1060, 540), (1000, 540)])                                  # south stub
    poly([(220, 318), (283, 318), (265, 420), (202, 420)])                                     # west stub
    # geometric parts only where they do not eat obvious non-road (green/blue/wood) pixels
    nonroad = (h > 60) & (h < 260) & (s > 0.35)
    g[nonroad] = 0
    m = cv2.bitwise_or(keep, g)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    return m > 0

# ------------------------------------------------------------------ texture helpers
def vnoise(shape, scale, seed):
    rng = np.random.RandomState(seed)
    gh, gw = shape[0] // scale + 3, shape[1] // scale + 3
    g = rng.rand(gh, gw).astype(np.float32)
    return cv2.resize(g, (gw * scale, gh * scale), interpolation=cv2.INTER_CUBIC)[:shape[0], :shape[1]]
def blocky(shape, blk, seed):
    rng = np.random.RandomState(seed)
    g = rng.rand(shape[0] // blk + 2, shape[1] // blk + 2).astype(np.float32)
    return np.kron(g, np.ones((blk, blk), np.float32))[:shape[0], :shape[1]]

def dirt_tone(mask):
    h, s, v = hsv(CLEAN)
    ring = cv2.dilate(mask.astype(np.uint8), np.ones((61, 61), np.uint8)) > 0
    ring &= ~(cv2.dilate(mask.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0)
    dirt = ring & (h > 30) & (h < 46) & (s > 0.45) & (s < 0.70) & (v > 0.72)
    return np.median(CLEAN[dirt], axis=0), dirt.sum()

def shade(base, f): return np.clip(base[None, None, :] * f[..., None], 0, 255)

def variant_A(mask, dirt):
    """plain worn packed-sand path: slightly darker/redder than the surrounding dirt, soft ruts, pebbles, a few sandstone slabs"""
    sand = np.array([214, 176, 118.]); tone = (0.55 * dirt + 0.45 * sand) * np.array([0.97, 0.96, 0.95])
    n1 = vnoise((H, W), 24, 1); n2 = blocky((H, W), 3, 2); n3 = vnoise((H, W), 7, 3)
    f = 0.93 + 0.10 * (n1 - 0.5) * 2 + 0.07 * (n3 - 0.5) * 2 + 0.035 * (n2 - 0.5) * 2
    img = shade(tone, f)
    # pebbles / grains: darker and lighter 2px specks
    rng = np.random.RandomState(11)
    sp = blocky((H, W), 2, 5)
    img[sp > 0.990] *= 0.82; img[sp < 0.008] = np.clip(img[sp < 0.008] * 1.08, 0, 255)
    # sparse flagstones: irregular sandstone slabs, low contrast
    slabs = np.zeros((H, W), np.uint8); edge = np.zeros((H, W), np.uint8)
    ys, xs = np.nonzero(mask)
    cand = np.stack([xs, ys], 1)
    placed = []
    order = rng.permutation(len(cand))
    for i in order:
        x, y = cand[i]
        if len(placed) >= 70: break
        if any((x - px) ** 2 + ((y - py) * 1.6) ** 2 < 70 ** 2 for px, py in placed): continue
        w, hh = rng.randint(22, 34), rng.randint(13, 19)
        box = np.zeros((H, W), np.uint8)
        cv2.rectangle(box, (x - w // 2, y - hh // 2), (x + w // 2, y + hh // 2), 255, -1)
        if (box > 0).sum() == 0 or ((box > 0) & mask).sum() < 0.97 * (box > 0).sum(): continue
        # rounded, irregular corners
        box = cv2.GaussianBlur(box, (0, 0), 1.6); box = ((box > 128) * 255).astype(np.uint8)
        slabs |= box; placed.append((x, y))
        inner = cv2.erode(box, np.ones((3, 3), np.uint8)); edge |= (box & ~inner)
    sl = slabs > 0; ed = edge > 0
    stone = np.array([205, 168, 118], float) * (0.97 + 0.07 * (vnoise((H, W), 9, 21)[..., None] - 0.5) * 2)
    img[sl] = 0.55 * img[sl] + 0.45 * stone[sl] * (0.98 + 0.04 * blocky((H, W), 2, 9)[sl][:, None])
    img[ed] *= 0.80                         # thin shadow outline
    top = sl & np.roll(~sl, 1, axis=0); img[top] = np.clip(img[top] * 1.12, 0, 255)
    return img, sl | ed

def variant_B(mask, dirt):
    """flagstone path in warm sandstone: running bond of slabs with dirt joints"""
    mortar = np.array([176, 146, 106.])
    img = np.zeros((H, W, 3), float); img[:] = mortar
    rng = np.random.RandomState(7)
    sl = np.zeros((H, W), bool)
    bw, bh = 33, 20                                          # slab size in picture pixels (similar to the old brick cells)
    pal = [np.array(c, float) for c in [(206, 170, 122), (198, 160, 112), (212, 178, 130), (192, 156, 112), (203, 166, 120)]]
    n2 = blocky((H, W), 2, 3); gv = vnoise((H, W), 10, 4)
    for r, y0 in enumerate(range(380, 560, bh) if False else range(-bh * 2, H, bh)):
        off = (r % 2) * (bw // 2) + int(rng.randint(-3, 4))
        x = -bw + off
        while x < W:
            w = bw + int(rng.randint(-6, 8)); h_ = bh + int(rng.randint(-2, 3))
            c = pal[rng.randint(len(pal))] * (0.95 + 0.10 * rng.rand())
            x0, x1, ya, yb = x + 2, x + w - 2, y0 + 2, y0 + h_ - 2
            if x1 > 0 and x0 < W and yb > 0 and ya < H:
                X0, X1, Y0, Y1 = max(x0, 0), min(x1, W), max(ya, 0), min(yb, H)
                if X1 > X0 and Y1 > Y0:
                    blk = np.zeros((H, W), bool); blk[Y0:Y1, X0:X1] = True
                    # chamfer the corners
                    for cx_, cy_ in ((X0, Y0), (X1 - 1, Y0), (X0, Y1 - 1), (X1 - 1, Y1 - 1)): blk[cy_, cx_] = False
                    fl = 1 + 0.07 * (gv - 0.5) * 2 + 0.03 * (n2 - 0.5) * 2
                    img[blk] = c[None, :] * fl[blk][:, None]
                    # bevel: light top edge, shadow bottom edge
                    if Y1 - Y0 > 3:
                        img[Y0, X0:X1] = np.clip(img[Y0, X0:X1] * 1.10, 0, 255); img[Y1 - 1, X0:X1] *= 0.86
                    sl |= blk
            x += w
    img = np.clip(img, 0, 255)
    return img, sl

BRIDGE_Y = 112          # the north road crosses the river on a wooden bridge (rails/posts stay): planks, not stone, up to this row
def bridge_deck(tex, mask):
    out = tex.copy(); rng = np.random.RandomState(5)
    wood = np.array([166, 104, 48.]); y = 0
    n = blocky((H, W), 2, 8)
    while y < BRIDGE_Y + 8:
        t = rng.randint(8, 11); f = 0.93 + 0.14 * rng.rand()
        band = np.zeros((H, W), bool); band[y:y + t, :] = True
        out[band] = wood[None, :] * (f + 0.05 * (n[band] - 0.5) * 2)[:, None]
        out[y, :] *= 0.72                                   # dark gap between planks
        out[y + 1, :] = np.clip(out[y + 1, :] * 1.08, 0, 255)
        y += t
    sel = mask.copy(); sel[BRIDGE_Y:, :] = False
    tex2 = tex.copy(); tex2[sel] = out[sel]
    return tex2

# ------------------------------------------------------------------ compositing
def composite(base_img, mask, tex, edge_seed):
    """tex replaces mask pixels; the border is ragged/worn: a noisy band of width ~5px mixes with the original ground (dirt/grass),
    and yellow fringe pixels around the mask are neutralised."""
    h, s, v = hsv(base_img)
    m8 = mask.astype(np.uint8)
    dist_in = cv2.distanceTransform(m8, cv2.DIST_L2, 3)
    dist_out = cv2.distanceTransform(1 - m8, cv2.DIST_L2, 3)
    nz = blocky((H, W), 2, edge_seed) * 0.6 + vnoise((H, W), 5, edge_seed + 1) * 0.4
    # inside: alpha ramps 0.55..1 within 5 px of the edge, with noisy threshold -> worn, irregular edge
    a_in = np.clip((dist_in + (nz - 0.5) * 6.0) / 5.0, 0, 1) * 0.5 + 0.5
    a = np.where(mask, a_in, 0.0)
    # outside: sand spills 1-3px beyond the edge where the original is yellow fringe or dirt
    fringe = (~mask) & (dist_out <= 4.5) & (h > 32) & (h < 54) & (s > 0.62) & (v > 0.72)
    a = np.where(fringe, 0.9, a)
    spill = (~mask) & (dist_out <= 3.5) & (nz > 0.78) & (h > 28) & (h < 50) & (s > 0.4)       # dirt-coloured pixels only (never grass)
    a = np.where(spill, 0.45, a)
    out = base_img.astype(float) * (1 - a[..., None]) + tex * a[..., None]
    return np.clip(out, 0, 255).astype(np.uint8), a

def main():
    mask = road_mask()
    cv2.imwrite(os.path.join(HERE, 'mask_road.png'), (mask * 255).astype(np.uint8))
    dirt, nd = dirt_tone(mask); print('dirt tone', dirt, 'samples', nd, 'road px', mask.sum())
    # raw: do not touch the palm pixels (raw differs from clean there)
    diff = np.abs(RAW.astype(int) - CLEAN.astype(int)).sum(axis=2)
    palm_px = cv2.dilate((diff > 36).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    res = {}
    for name, fn in (('A', variant_A), ('B', variant_B)):
        tex, extra = fn(mask, dirt)
        tex = bridge_deck(tex, mask)
        cl, a = composite(CLEAN, mask, tex, 31)
        rw_tex_a = a * (~palm_px)
        rw = np.clip(RAW.astype(float) * (1 - rw_tex_a[..., None]) + tex * rw_tex_a[..., None], 0, 255).astype(np.uint8)
        res[name] = (cl, rw)
        cv2.imwrite(os.path.join(HERE, 'variants', 'bg_clean_%s.png' % name), cv2.cvtColor(cl, cv2.COLOR_RGB2BGR))
        cv2.imwrite(os.path.join(HERE, 'variants', 'bg_raw_%s.png' % name), cv2.cvtColor(rw, cv2.COLOR_RGB2BGR))
        ch = (np.abs(cl.astype(int) - CLEAN.astype(int)).sum(axis=2) > 6)
        cv2.imwrite(os.path.join(HERE, 'variants', 'diff_mask_%s.png' % name), (ch * 255).astype(np.uint8))
        print(name, 'changed px (clean) %d = %.1f%%' % (ch.sum(), 100 * ch.mean()))
if __name__ == '__main__':
    main()
