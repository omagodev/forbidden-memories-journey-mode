#!/usr/bin/env python3
"""Give every 48x62 NPC sheet a readable walk cycle (frames 1..4 = step A, passing, step B, passing) without changing its look.

The painted sheets only have idle / step A / step B, and the bake repeated idle as the passing frame; front and back steps differ
by a few pixels and the side 'idle' is already a stride, so walkers seemed to slide.  From the sheet's own pixels:
  * front/back (down, up): step A lifts the left leg (its pixels move up 2 texels, the sole leaves the ground) and shifts the
    upper body 1 texel over the planted leg; step B mirrors it.  The arms ride with the body, so they swing against the legs.
  * sides (left, right): steps A/B keep the sheet's real strides; the passing frames pull both legs under the hips
    (the leg rows squeezed toward the body's axis) with the body 1 texel higher.
Idle (frame 0) is never touched, so people who stand still look exactly as before.  A file is processed only while its passing
frames are still copies of idle, so running this twice changes nothing.  usage: walk_strides.py [assets/spr_*.bin ...]"""
import glob, os, struct, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
SKIP = ("lpc", "kenney", "crowd", "player", "bakura")   # bakura: the ghost hovers, no feet to step with

def read(p):
    d = open(p, "rb").read()
    nf, cw, ch, fx, fy = struct.unpack("<HHHHH", d[4:14])
    o, cells = 14, {}
    for di in range(4):
        for f in range(nf):
            k = np.frombuffer(d[o:o + cw * ch], np.uint8).reshape(ch, cw).copy(); o += cw * ch
            w = np.frombuffer(d[o:o + cw * ch * 4], np.uint8).reshape(ch, cw, 4).copy(); o += cw * ch * 4
            c = np.frombuffer(d[o:o + cw * ch * 3], np.uint8).reshape(ch, cw, 3).copy(); o += cw * ch * 3
            cells[di, f] = [k, w, c]
    assert o == len(d), p
    return d[:14], nf, cw, ch, fx, fy, cells

def write(p, head, nf, cells):
    with open(p, "wb") as f:
        f.write(head)
        for di in range(4):
            for fr in range(nf):
                k, w, c = cells[di, fr]
                f.write(k.tobytes()); f.write(w.tobytes()); f.write(c.tobytes())

def reoutline(k):
    solid = k == 0
    pad = np.pad(solid, 1)
    near = pad[:-2, 1:-1] | pad[2:, 1:-1] | pad[1:-1, :-2] | pad[1:-1, 2:]
    k = np.where(solid, 0, np.where(near, 254, 255)).astype(np.uint8)
    return k

def bbox(k):
    ys, xs = np.nonzero(k == 0)
    return xs.min(), ys.min(), xs.max(), ys.max()

def blank(cell):
    k, w, c = cell
    return [np.full_like(k, 255), np.zeros_like(w), np.zeros_like(c)]

def put(dst, src, mask_src, dy=0, dx=0):
    """copy the solid pixels of src under mask_src into dst moved by (dx, dy)"""
    ys, xs = np.nonzero(mask_src & (src[0] == 0))
    H, W = src[0].shape
    for y, x in zip(ys, xs):
        Y, X = y + dy, x + dx
        if 0 <= Y < H and 0 <= X < W:
            dst[0][Y, X] = 0; dst[1][Y, X] = src[1][y, x]; dst[2][Y, X] = src[2][y, x]

def regions(cell):
    x0, y0, x1, y1 = bbox(cell[0])
    h = y1 - y0 + 1
    hip = y1 - max(5, int(round(h * 0.22)))          # the leg rows: about the lowest fifth of a chibi figure
    cx = (x0 + x1 + 1) // 2
    H, W = cell[0].shape
    yy, xx = np.mgrid[0:H, 0:W]
    return hip, cx, yy, xx, y1

def front_step(cell, side):
    """side -1: lift the left leg, +1: the right; the body leans 1 texel over the planted one"""
    hip, cx, yy, xx, y1 = regions(cell)
    out = blank(cell)
    upper = yy <= hip
    legs = ~upper
    lifted = legs & ((xx < cx) if side < 0 else (xx >= cx))
    planted = legs & ~lifted
    put(out, cell, planted)
    put(out, cell, lifted, dy=-2)
    put(out, cell, upper, dx=-side)                 # over the planted leg
    out[0] = reoutline(out[0])
    return out

def side_pass(cell):
    """both legs under the hips: squeeze the leg rows toward the body's axis, body 1 texel up"""
    hip, cx, yy, xx, y1 = regions(cell)
    lx0, _, lx1, _ = bbox(np.where(yy > hip, cell[0], 255))
    axis = (lx0 + lx1) / 2.0
    out = blank(cell)
    put(out, cell, yy <= hip, dy=-1)
    H, W = cell[0].shape
    for y in range(hip + 1, H):
        row = [x for x in range(W) if cell[0][y, x] == 0]
        for x in row:
            X = int(round(axis + (x - axis) * 0.5))
            Y = y - 1 if y < y1 else y              # the soles stay on the ground
            if out[0][Y, X] != 0:
                out[0][Y, X] = 0; out[1][Y, X] = cell[1][y, x]; out[2][Y, X] = cell[2][y, x]
    out[0] = reoutline(out[0])
    return out

def process(p):
    head, nf, cw, ch, fx, fy, cells = read(p)
    if nf != 5: return "skip (frames %d)" % nf
    same = all((cells[d, f][0] == cells[d, 0][0]).all() and (cells[d, f][2] == cells[d, 0][2]).all() for d in range(4) for f in (2, 4))
    if not same: return "already done"
    for d in (0, 3):                                # down, up
        a, b = cells[d, 1], cells[d, 3]
        cells[d, 1] = front_step(a, -1)
        cells[d, 3] = front_step(b, +1)
    for d in (1, 2):                                # left, right
        cells[d, 2] = side_pass(cells[d, 0])
        cells[d, 4] = side_pass(cells[d, 0])
    write(p, head, nf, cells)
    return "strides"

def main():
    paths = sys.argv[1:] or sorted(glob.glob(os.path.join(HERE, "..", "assets", "spr_*.bin")))
    for p in paths:
        if any(s in os.path.basename(p) for s in SKIP): continue
        print(os.path.basename(p), process(p))

if __name__ == "__main__":
    main()
