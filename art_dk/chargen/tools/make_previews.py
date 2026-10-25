#!/usr/bin/env python3
"""Contact sheets: previews/*.png  (run from art_dk/chargen:  python3 tools/make_previews.py)"""
import os, sys
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
sys.path.insert(0, ROOT)
import compose as C
man = C.manifest()
BG = (150, 170, 120, 255); PANEL = (46, 40, 52, 255)
OUT = os.path.join(ROOT, "previews"); os.makedirs(OUT, exist_ok=True)
try: FONT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
except Exception: FONT = ImageFont.load_default()

def cell(sel, d, f): return Image.fromarray(C.composite_cell(man, sel, d, f), "RGBA")

def combo_block(sel, frames=(0, 1, 3), zoom=3, label=None):
    w, h = len(frames) * C.W, 4 * C.H
    im = Image.new("RGBA", (w, h), BG)
    for r, d in enumerate(C.DIRS):
        for j, f in enumerate(frames): im.alpha_composite(cell(sel, d, f), (j * C.W, r * C.H))
    return im.resize((w * zoom, h * zoom), Image.NEAREST)

def name_of(sel):
    return "%s/%s | %s:%s | %s:%s | %s:%s" % (man["palettes"]["skin"][sel["skin"]]["name"], "", sel["outfit"], sel["outfit_colour"], sel["hair"], sel["hair_colour"], sel["accessory"], sel["accessory_colour"])

COMBOS = [
    dict(skin=1, outfit="tunic", outfit_colour=0, hair="short", hair_colour=0, accessory="none", accessory_colour=0),
    dict(skin=0, outfit="jacket", outfit_colour=0, hair="spiky", hair_colour=3, accessory="headband", accessory_colour=0),
    dict(skin=3, outfit="cloak", outfit_colour=1, hair="hood_down", hair_colour=1, accessory="none", accessory_colour=0),
    dict(skin=2, outfit="uniform", outfit_colour=0, hair="bob", hair_colour=4, accessory="scarf", accessory_colour=0),
    dict(skin=1, outfit="jacket", outfit_colour=1, hair="long", hair_colour=2, accessory="duel_disk", accessory_colour=0),
    dict(skin=0, outfit="tunic", outfit_colour=1, hair="ponytail", hair_colour=1, accessory="cap", accessory_colour=1),
    dict(skin=2, outfit="cloak", outfit_colour=2, hair="short", hair_colour=0, accessory="scarf", accessory_colour=2),
    dict(skin=3, outfit="uniform", outfit_colour=1, hair="ponytail", hair_colour=3, accessory="headband", accessory_colour=1),
]

def label(draw, xy, text, fill=(255, 255, 255)): draw.text(xy, text, font=FONT, fill=fill)

def sheet_combos():
    Z = 3; cols = 4
    bw, bh = 3 * C.W * Z, 4 * C.H * Z
    pad = 10; lab = 36
    rows = (len(COMBOS) + cols - 1) // cols
    im = Image.new("RGBA", (cols * (bw + pad) + pad, rows * (bh + lab + pad) + pad + 24), PANEL)
    d = ImageDraw.Draw(im)
    label(d, (pad, 4), "Journey Mode character creator: assembled combos. rows = down, left, right, up; columns = idle, step A, step B")
    for i, sel in enumerate(COMBOS):
        x = pad + (i % cols) * (bw + pad); y = 24 + pad + (i // cols) * (bh + lab + pad)
        im.alpha_composite(combo_block(sel, zoom=Z), (x, y))
        sk = man["palettes"]["skin"][sel["skin"]]["name"]; hc = man["palettes"]["hair"][sel["hair_colour"]]["name"]
        oc = man["parts"]["outfit"][sel["outfit"]]["colourways"][sel["outfit_colour"]]["name"]
        ac = man["parts"]["accessory"][sel["accessory"]]["colourways"][sel["accessory_colour"]]["name"]
        label(d, (x, y + bh + 3), "skin %s  outfit %s (%s)" % (sk, sel["outfit"], oc))
        label(d, (x, y + bh + 19), "hair %s (%s)  acc %s%s" % (sel["hair"], hc, sel["accessory"], "" if sel["accessory"] == "none" else " (%s)" % ac))
    im.convert("RGB").save(os.path.join(OUT, "contact_sheet_combos.png"))

def sheet_walk():
    sel = COMBOS[1]; Z = 4
    im = Image.new("RGBA", (5 * C.W * Z + 20, 4 * C.H * Z + 20), BG)
    sh = C.composite_sheet(man, sel).resize((5 * C.W * Z, 4 * C.H * Z), Image.NEAREST)
    im.alpha_composite(sh, (10, 10)); im.convert("RGB").save(os.path.join(OUT, "walk_cycle_all_frames.png"))

def sheet_catalogue():
    Z = 3; pad = 8; cw, ch = C.W * Z, C.H * Z
    base = dict(skin=1, outfit="tunic", outfit_colour=0, hair="short", hair_colour=0, accessory="none", accessory_colour=0)
    def row(sels, title, d="down"):
        return title, [Image.fromarray(C.composite_cell(man, s, d, 0), "RGBA").resize((cw, ch), Image.NEAREST) for s in sels]
    rows_ = []
    rows_.append(row([dict(base, skin=i) for i in range(4)], "skin tones (4)"))
    for st in ("tunic", "jacket", "cloak", "uniform"):
        rows_.append(row([dict(base, outfit=st, outfit_colour=i) for i in range(3)], "outfit %s x3 colourways" % st))
    for st in ("short", "spiky", "long", "ponytail", "bob", "hood_down"):
        rows_.append(row([dict(base, outfit="cloak", hair=st, hair_colour=i) for i in range(5)], "hair %s x5 colours" % st))
    for st in ("headband", "scarf", "duel_disk", "cap"):
        rows_.append(row([dict(base, accessory=st, accessory_colour=i) for i in range(3)], "accessory %s x3 colourways" % st))
    left = rows_[:5] + rows_[11:]; right = rows_[5:11]
    colw = pad + 5 * (cw + pad) + 200
    H_ = pad + max(len(left), len(right)) * (ch + pad)
    im = Image.new("RGBA", (2 * colw, H_), PANEL); d = ImageDraw.Draw(im)
    for ci, blk in enumerate((left, right)):
        for r, (title, imgs) in enumerate(blk):
            y = pad + r * (ch + pad)
            for i, t in enumerate(imgs):
                bg = Image.new("RGBA", t.size, BG); bg.alpha_composite(t); im.alpha_composite(bg, (ci * colw + pad + i * (cw + pad), y))
            label(d, (ci * colw + pad + 5 * (cw + pad) + 4, y + ch // 2 - 8), title)
    im.convert("RGB").save(os.path.join(OUT, "catalogue_variants.png"))

def sheet_layers():
    sel = COMBOS[1]; Z = 5
    from PIL import Image as I
    parts = [("body", "base"), ("outfit", sel["outfit"]), ("hair", sel["hair"]), ("accessory", sel["accessory"])]
    src = C.sources(man, sel)
    cols = []
    for k in range(1, len(parts) + 1):
        sub = dict(sel)
        # composite only the first k layers: emulate by temporarily building the list
        out = None
        import numpy as np
        for d_i, d in enumerate(("down", "left", "up")):
            pass
        cols.append(k)
    im = Image.new("RGBA", (6 * C.W * Z + 70, 3 * C.H * Z + 20), PANEL)
    import numpy as np
    for ci in range(5):
        for r, d in enumerate(("down", "left", "up")):
            out = np.zeros((C.H, C.W, 4), np.uint8)
            use = parts[ci:ci + 1] if ci < 4 else parts
            for part, style in use:
                k, w, rgb = C.layer(man, part, style)[(d, 1)]
                pal = C.slot_palette(man, part, style, src)
                col = rgb.astype(float)
                for q in range(1, 5): col = col + (w[..., q - 1:q] / 100.0) * np.array(pal.get(q, (0, 0, 0)), float)
                col = np.clip(col + .5, 0, 255).astype(np.uint8)
                s_ = k == 0; rg = k == 254
                out[s_, :3] = col[s_]; out[s_, 3] = 255; out[rg, :3] = C.OUTLINE; out[rg, 3] = 255
            bg = Image.new("RGBA", (C.W, C.H), BG); bg.alpha_composite(Image.fromarray(out, "RGBA"))
            im.alpha_composite(bg.resize((C.W * Z, C.H * Z), Image.NEAREST), (10 + ci * (C.W * Z + 12), 10 + r * (C.H * Z) // 1 * 0 + r * (C.H * Z)))
    d = ImageDraw.Draw(im)
    im.convert("RGB").save(os.path.join(OUT, "layers_exploded.png"))

if __name__ == "__main__":
    sheet_combos(); sheet_walk(); sheet_catalogue(); sheet_layers()
    print(os.listdir(OUT))
