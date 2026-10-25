#!/usr/bin/env python3
"""Reference compositor for the chargen layers (numpy + Pillow only).  It does exactly what the engine should do on the CPU:

    for part in manifest["draw_order"]:                # body, outfit, hair, accessory
        for each texel of the part's layer cell:       # SPR1 layout: kind[], W1..W4[], rgb[]
            kind 255 -> leave the texel below alone
            kind 254 -> write the outline colour (34,24,30)
            kind   0 -> write clip(rgb + sum(W_q/100 * palette[q]  for q = 1..4) + 0.5)     (the same formula as jm_painted.c spr_bake)

so the .bin files can be loaded by the existing spr_load() (SPR1) and baked per layer with spr_bake()'s recolour code; the only new
thing is that a layer texel with kind 255 must NOT overwrite what is already in the page.  The palette of each layer's slots comes from the
manifest ("slots": slot number -> colour source) and the selection.

CLI:  python3 compose.py [--skin 0..3|name] [--outfit style[:colourway]] [--hair style[:colour]] [--acc style[:colourway]]
                          [--out PNG] [--sheet]   (sheet = 5 frames x 4 directions, otherwise only the idle frame of each direction)
      python3 compose.py --page out.bin ...        (256x256 RGB555 page, engine bank layout: x = frame*48, y = dir*64, bit 15 = opaque)
"""
import os, sys, json, struct, argparse
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 48, 62
DIRS = ["down", "left", "right", "up"]
OUTLINE = (34, 24, 30)
_cache = {}

def manifest(path=None):
    return json.load(open(path or os.path.join(HERE, "manifest.json")))

def load_spr1(path):
    d = open(path, "rb").read()
    assert d[:4] == b"SPR1"
    nf, cw, ch, fx, fy = struct.unpack_from("<HHHHH", d, 4)
    assert (cw, ch) == (W, H) and nf == 5
    pos = 14; n = W * H; out = {}
    for dn in DIRS:
        for f in range(nf):
            k = np.frombuffer(d, np.uint8, n, pos).reshape(H, W); pos += n
            w = np.frombuffer(d, np.uint8, n * 4, pos).reshape(H, W, 4); pos += n * 4
            r = np.frombuffer(d, np.uint8, n * 3, pos).reshape(H, W, 3); pos += n * 3
            out[(dn, f)] = (k, w, r)
    return out

def load_cgp1(path):
    """packed layer -> same dict as load_spr1"""
    d = open(path, "rb").read()
    assert d[:4] == b"CGP1"
    nf, cw, ch, nd = struct.unpack_from("<BBBH", d, 4); pos = 9
    desc = [None, None]
    for i in range(nd):
        desc.append((d[pos + 1:pos + 5], d[pos + 5:pos + 8])); pos += 8
    out = {}
    for dn in DIRS:
        for f in range(nf):
            x0, y0, w, h = d[pos:pos + 4]; pos += 4
            k = np.full((H, W), 255, np.uint8); wt = np.zeros((H, W, 4), np.uint8); rgb = np.zeros((H, W, 3), np.uint8)
            if w and h:
                sub = np.frombuffer(d, np.uint8, w * h, pos).reshape(h, w); pos += w * h
                for yy in range(h):
                    for xx in range(w):
                        i = sub[yy, xx]
                        if i == 0: continue
                        if i == 1: k[y0 + yy, x0 + xx] = 254
                        else:
                            k[y0 + yy, x0 + xx] = 0; wt[y0 + yy, x0 + xx] = np.frombuffer(desc[i][0], np.uint8); rgb[y0 + yy, x0 + xx] = np.frombuffer(desc[i][1], np.uint8)
            out[(dn, f)] = (k, wt, rgb)
    return out

def layer(man, part, style):
    key = (part, style)
    if key not in _cache: _cache[key] = load_spr1(os.path.join(HERE, man["parts"][part][style]["bin"]))
    return _cache[key]

def pick(lst, v):
    """colour/colourway by index or name"""
    if isinstance(v, int): return v % len(lst)
    s = str(v)
    if s.lstrip("-").isdigit(): return int(s) % len(lst)
    names = [e["name"] for e in lst]; return names.index(s)

def sources(man, sel):
    """selection -> {source name: rgb}"""
    p = man["palettes"]
    skin = p["skin"][pick(p["skin"], sel.get("skin", 1))]["rgb"]
    hair = p["hair"][pick(p["hair"], sel.get("hair_colour", 0))]["rgb"]
    src = {"skin": skin, "hair": hair}
    o = sel.get("outfit", "tunic")
    cw = man["parts"]["outfit"][o]["colourways"][pick(man["parts"]["outfit"][o]["colourways"], sel.get("outfit_colour", 0))]
    src.update({"outfit.main": cw["main"], "outfit.trim": cw["trim"], "outfit.trousers": cw["trousers"]})
    a = sel.get("accessory", "none")
    if a != "none":
        cw = man["parts"]["accessory"][a]["colourways"][pick(man["parts"]["accessory"][a]["colourways"], sel.get("accessory_colour", 0))]
        src.update({"accessory.a": cw["a"], "accessory.b": cw["b"]})
    return src

def slot_palette(man, part, style, src):
    slots = man["parts"][part][style]["slots"]
    return {int(q): src.get(name, (0, 0, 0)) for q, name in slots.items()}

def layers_of(man, sel):
    L = [("body", "base"), ("outfit", sel.get("outfit", "tunic")), ("hair", sel.get("hair", "short"))]
    if sel.get("accessory", "none") != "none": L.append(("accessory", sel["accessory"]))
    return L

def composite_cell(man, sel, d, f):
    """-> RGBA uint8 HxWx4 (alpha 255 where a texel is set)"""
    src = sources(man, sel)
    out = np.zeros((H, W, 4), np.uint8)
    for part, style in layers_of(man, sel):
        k, w, rgb = layer(man, part, style)[(d, f)]
        pal = slot_palette(man, part, style, src)
        col = rgb.astype(np.float64)
        for q in range(1, 5):
            col = col + (w[..., q - 1:q] / 100.0) * np.array(pal.get(q, (0, 0, 0)), np.float64)
        col = np.clip(col + 0.5, 0, 255).astype(np.uint8)
        solid = k == 0; ring = k == 254
        out[solid, :3] = col[solid]; out[solid, 3] = 255
        out[ring, :3] = OUTLINE; out[ring, 3] = 255
    return out

def composite_sheet(man, sel, frames=range(5), dirs=DIRS):
    im = Image.new("RGBA", (len(list(frames)) * W, len(dirs) * H), (0, 0, 0, 0))
    for r, d in enumerate(dirs):
        for j, f in enumerate(frames):
            im.alpha_composite(Image.fromarray(composite_cell(man, sel, d, f), "RGBA"), (j * W, r * H))
    return im

def rgb555(r, g, b): return 0x8000 | (int(r) >> 3) | (int(g) >> 3) << 5 | (int(b) >> 3) << 10

def composite_page(man, sel):
    """256x256 uint16 page like the engine's character pages: frame f at x = f*48, direction d at y = d*64 (down, left, right, up)"""
    page = np.zeros((256, 256), np.uint16)
    for r, d in enumerate(DIRS):
        for f in range(5):
            c = composite_cell(man, sel, d, f)
            for y in range(H):
                for x in range(W):
                    if c[y, x, 3]: page[r * 64 + y, f * 48 + x] = rgb555(*c[y, x, :3])
    return page

def parse_sel(a):
    sel = {"skin": 1, "outfit": "tunic", "outfit_colour": 0, "hair": "short", "hair_colour": 0, "accessory": "none", "accessory_colour": 0}
    if a.skin is not None: sel["skin"] = a.skin
    for key, val in (("outfit", a.outfit), ("hair", a.hair), ("accessory", a.acc)):
        if val:
            st, _, cl = val.partition(":")
            sel[key] = st
            if cl: sel[key + "_colour"] = cl
    return sel

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--skin"); ap.add_argument("--outfit"); ap.add_argument("--hair"); ap.add_argument("--acc")
    ap.add_argument("--out", default="compose_out.png"); ap.add_argument("--sheet", action="store_true"); ap.add_argument("--page"); ap.add_argument("--zoom", type=int, default=4)
    ap.add_argument("--manifest")
    a = ap.parse_args()
    man = manifest(a.manifest)
    sel = parse_sel(a)
    sel["skin"] = pick(man["palettes"]["skin"], sel["skin"])
    if a.page:
        pg = composite_page(man, sel); open(a.page, "wb").write(pg.astype("<u2").tobytes()); print("page", a.page, pg.nbytes, "bytes")
    sheet = composite_sheet(man, sel, range(5) if a.sheet else [0])
    bg = Image.new("RGBA", sheet.size, (150, 170, 120, 255)); bg.alpha_composite(sheet)
    bg = bg.resize((bg.width * a.zoom, bg.height * a.zoom), Image.NEAREST); bg.save(a.out); print("wrote", a.out, sel)
