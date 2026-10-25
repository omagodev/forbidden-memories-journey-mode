#!/usr/bin/env python3
"""Build every chargen layer: SPR1-format .bin (engine loader compatible), RGBA sprite-sheet PNGs, packed CGP1 .bin and the manifest.
usage: python3 build.py   (from art_dk/chargen)"""
import os, sys, json, struct, zlib
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
from rig import *
from poses import DIRS
import body, outfits, hair, acc, palettes

STYLES = {"body": {"base": body.body_cell}, "outfit": outfits.OUTFITS, "hair": hair.HAIRS, "accessory": {k: v for k, v in acc.ACCS.items() if k != "none"}}
# does this layer keep its 1-texel outline where the (always present) body is solid?  (accessories that sit over the face need it)
RING_OVER_BODY = {"body": True, "outfit": False, "hair": False, "accessory": True}
RING_OVER_BODY_STYLE = {("accessory", "headband"): False}
SLOTS = {
    "body":      {"1": "skin", "2": "hair"},
    "outfit":    {"1": "outfit.main", "2": "outfit.trim", "3": "skin", "4": "outfit.trousers"},
    "hair":      {"1": "hair", "2": "outfit.main", "3": "outfit.trim", "4": "skin"},
    "accessory": {"1": "accessory.a", "2": "accessory.b", "3": "skin"},
}
NAMES = list(TONES)

def ring_of(m):
    return (shift(m, 1, 0) | shift(m, -1, 0) | shift(m, 0, 1) | shift(m, 0, -1)) & ~m

def all_cells(fn):
    """-> {(dir, frame): Cell} with right = mirrored left"""
    cells = {}
    for f in range(5):
        for d in ("down", "left", "up"): cells[(d, f)] = fn(d, f)
        cells[("right", f)] = cells[("left", f)].mirrored()
    return cells

def cell_arrays(c, body_solid, ring_over_body):
    kind = np.full((H, W), 255, np.uint8)
    ring = ring_of(c.solid)
    if not ring_over_body: ring &= ~body_solid
    kind[ring] = 254; kind[c.solid] = 0
    wts = np.zeros((H, W, 4), np.uint8); rgb = np.zeros((H, W, 3), np.uint8)
    for y, x in zip(*np.nonzero(c.solid)):
        s = int(c.slot[y, x])
        if s == 0: rgb[y, x] = c.rgb[y, x]
        else:
            w, fx = TONES[NAMES[c.tone[y, x]]]
            wts[y, x, s - 1] = int(round(w * 100)); rgb[y, x] = fx
    return kind, wts, rgb

def write_spr1(path, arrs):
    with open(path, "wb") as f:
        f.write(b"SPR1" + struct.pack("<HHHHH", 5, W, H, 24, 56))
        for d in DIRS:
            for fr in range(5):
                k, w, r = arrs[(d, fr)]
                f.write(k.tobytes()); f.write(w.tobytes()); f.write(r.tobytes())

def write_cgp1(path, arrs):
    """packed: 'CGP1', u8 nframes(5), u8 w, u8 h, u16 ntex; ntex x (u8 kind, 4 x u8 weight, 3 x u8 rgb) descriptors (index 0 = empty is implicit,
    1 = outline), then 20 cells (dir-major): u8 x0,y0,w,h and w*h bytes of descriptor index (0 empty, 1 outline, 2.. = descriptor n-2).  (zlib not applied)"""
    desc = {}; order = []
    def did(k, w, r):
        key = (int(k), tuple(int(v) for v in w), tuple(int(v) for v in r))
        if key not in desc: desc[key] = len(order) + 2; order.append(key)
        return desc[key]
    cells = []
    for d in DIRS:
        for fr in range(5):
            k, w, r = arrs[(d, fr)]
            idx = np.zeros((H, W), np.int32)
            for y, x in zip(*np.nonzero(k != 255)):
                idx[y, x] = 1 if k[y, x] == 254 else did(0, w[y, x], r[y, x])
            ys, xs = np.nonzero(idx)
            if len(ys) == 0: cells.append(bytes([0, 0, 0, 0])); continue
            x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
            sub = idx[y0:y1, x0:x1]
            cells.append(bytes([x0, y0, x1 - x0, y1 - y0]) + sub.astype(np.uint8).tobytes())
    assert len(order) < 254, len(order)
    with open(path, "wb") as f:
        f.write(b"CGP1" + struct.pack("<BBBH", 5, W, H, len(order)))
        for k, w, r in order: f.write(bytes([k]) + bytes(w) + bytes(r))
        for c in cells: f.write(c)

def slot_pal(part, style, selection_default):
    return selection_default

def render_png(arrs, pal):
    """arrs -> RGBA sheet 5x4 cells with the given slot palette {1..4: rgb}"""
    im = np.zeros((4 * H, 5 * W, 4), np.uint8)
    for r, d in enumerate(DIRS):
        for fr in range(5):
            k, w, rgb = arrs[(d, fr)]
            out = np.zeros((H, W, 4), np.uint8)
            col = rgb.astype(np.float64)
            for q in range(1, 5):
                col = col + (w[..., q - 1:q] / 100.0) * np.array(pal.get(q, (0, 0, 0)), np.float64)
            out[..., :3] = np.clip(col + 0.5, 0, 255).astype(np.uint8); out[..., 3] = np.where(k == 0, 255, 0)
            o = k == 254; out[o, :3] = OUTLINE; out[o, 3] = 255
            out[k == 255] = 0
            im[r * H:(r + 1) * H, fr * W:(fr + 1) * W] = out
    return Image.fromarray(im, "RGBA")

def default_pal(part, style):
    skin = palettes.SKIN[1][1]; hairc = palettes.HAIR[0][1]
    if part == "body": return {1: skin, 2: hairc}
    if part == "outfit":
        n, m, t, tr = palettes.OUTFIT[style][0]; return {1: m, 2: t, 3: skin, 4: tr}
    if part == "hair":
        n, m, t, tr = palettes.OUTFIT["cloak"][0]; return {1: hairc, 2: m, 3: t, 4: skin}
    n, a, b = palettes.ACC[style][0]; return {1: a, 2: b, 3: skin}

def main():
    os.makedirs(os.path.join(ROOT, "bin"), exist_ok=True); os.makedirs(os.path.join(ROOT, "packed"), exist_ok=True); os.makedirs(os.path.join(ROOT, "png"), exist_ok=True)
    body_cells = all_cells(body.body_cell)
    body_solid = {k: v.solid for k, v in body_cells.items()}
    man_parts = {}
    total_raw = total_packed = 0
    for part, styles in STYLES.items():
        man_parts[part] = {}
        for style, fn in styles.items():
            cells = body_cells if (part, style) == ("body", "base") else all_cells(fn)
            rob = RING_OVER_BODY_STYLE.get((part, style), RING_OVER_BODY[part])
            arrs = {k: cell_arrays(c, body_solid[k], rob) for k, c in cells.items()}
            fn_bin = "bin/%s_%s.bin" % (part, style); fn_pk = "packed/%s_%s.cgp1" % (part, style); fn_png = "png/%s_%s.png" % (part, style)
            write_spr1(os.path.join(ROOT, fn_bin), arrs); write_cgp1(os.path.join(ROOT, fn_pk), arrs)
            render_png(arrs, default_pal(part, style)).save(os.path.join(ROOT, fn_png))
            sb, sp = os.path.getsize(os.path.join(ROOT, fn_bin)), os.path.getsize(os.path.join(ROOT, fn_pk))
            total_raw += sb; total_packed += sp
            ent = {"bin": fn_bin, "packed": fn_pk, "png": fn_png, "offset": [0, 0], "slots": SLOTS[part], "ring_over_body": rob, "bytes_bin": sb, "bytes_packed": sp}
            man_parts[part][style] = ent
    print("raw SPR1 bytes", total_raw, "packed bytes", total_packed)
    return man_parts, total_raw, total_packed

def write_manifest(parts, total_raw, total_packed):
    for style, e in parts["outfit"].items():
        e["colourways"] = [{"name": n, "main": list(m), "trim": list(t), "trousers": list(tr)} for n, m, t, tr in palettes.OUTFIT[style]]
    for style, e in parts["accessory"].items():
        e["colourways"] = [{"name": n, "a": list(a), "b": list(b)} for n, a, b in palettes.ACC[style]]
    parts["accessory"]["none"] = {"bin": None, "slots": {}, "offset": [0, 0], "colourways": [{"name": "none"}]}
    man = {
        "format": "journey-chargen-1",
        "frame": {"w": W, "h": H, "anchor": [24, 56], "frames_per_direction": 5, "directions": DIRS,
                  "frame_meaning": "0 idle, 1 step A, 2 idle, 3 step B, 4 idle (walk cycle = frames 1..4, same as every SPR1 character)",
                  "page_layout": "assembled character = one 256x256 RGB555 page: frame f at x=f*48, direction d (down,left,right,up) at y=d*64"},
        "draw_order": ["body", "outfit", "hair", "accessory"],
        "outline_rgb": list(OUTLINE),
        "format_notes": {
            "bin": "SPR1 (identical to spr_ai.bin): header 'SPR1',u16 5,48,62,24,56; then 4 dirs (down,left,right,up) x 5 frames of: kind[2976] (0 solid, 254 outline, 255 empty), W1..W4 [2976*4] (weight*100), rgb[2976*3] (fixed part)",
            "texel_formula": "solid texel colour = clip(rgb + sum_q W_q/100 * palette[q], 0, 255); same as spr_bake() in jm_painted.c",
            "composite": "draw the layers in draw_order; kind 255 leaves the texel below untouched, kind 254 writes outline_rgb, kind 0 writes the colour",
            "packed": "CGP1: same data, bounding-box cropped and de-duplicated into at most 253 texel descriptors (see tools/build.py write_cgp1 and compose.py load_cgp1)",
            "right_direction": "the right row is the exact mirror (x -> 47-x) of the left row, already baked into every file",
        },
        "palettes": {"skin": [{"name": n, "rgb": list(c)} for n, c in palettes.SKIN], "hair": [{"name": n, "rgb": list(c)} for n, c in palettes.HAIR]},
        "slot_sources": {"skin": "palettes.skin[i]", "hair": "palettes.hair[i]", "outfit.main/trim/trousers": "parts.outfit[style].colourways[i]",
                         "accessory.a/b": "parts.accessory[style].colourways[i]"},
        "parts": parts,
        "avoid_combinations": [
            {"hair": "spiky", "accessory": "cap", "why": "the cap crown is smaller than the spikes, they stick out of it"},
            {"hair": "hood_down", "accessory": "scarf", "why": "scarf and the hood roll sit on the same neck area"},
            {"hair": "long", "accessory": "scarf", "why": "long hair is hidden under the scarf in the back view"},
        ],
        "totals": {"layer_files": sum(1 for p in parts.values() for e in p.values() if e.get("bin")), "bytes_bin": total_raw, "bytes_packed": total_packed},
        "budget": {"assembled_character": "1 page of 256x256 RGB555 = 131072 bytes in a sprite bank (5 frames x 4 dirs fit one page)",
                   "layers_in_ram_spr1": "4 selected layers x 476174 bytes = 1904696 bytes (SPR1 files are 8 bytes/texel); the packed CGP1 form is about 12 KB per layer",
                   "all_layers_on_disk": "bin 7142610 bytes (76 KB deflated), packed ~183 KB"},
        "selection_example": {"skin": 1, "outfit": "jacket", "outfit_colour": 0, "hair": "spiky", "hair_colour": 3, "accessory": "headband", "accessory_colour": 0},
    }
    json.dump(man, open(os.path.join(ROOT, "manifest.json"), "w"), indent=1)
    return man

if __name__ == "__main__":
    parts, a, b = main()
    write_manifest(parts, a, b)
