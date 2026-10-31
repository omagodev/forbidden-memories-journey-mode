#!/usr/bin/env python3
"""Bake the character creator's modular LPC parts (the hero is built from these at run time).

Every layer is composed alone, downsized the same way as import_lpc_test.py (64x64 cells, LANCZOS to 32x32, placed in a 25x38 cell, idle +
nine walk frames, rows down/left/right/up) and stored as assets/lpc_parts/<name>.lpl:
    "LPL1", u8 w, u8 h, u8 frames, u8 0, then 4*frames cells of (w*h alpha, w*h*3 RGB), then 4 cells of 64x64 (the idle pose of
each direction at the source resolution, same layout) for the creator's big preview.
The game tints a layer at run time with the same colorize as the importer (grey -> lo..hi of the chosen colour), composes the layers in
z order and thresholds alpha at 128, which reproduces the existing LPC hero (base "Hero" = spr_lpc_test.bin's layers and colours).
manifest.json lists the categories, options, colours and base presets; lpc_runtime_credits.csv gets a row for every LPC file used.

Usage: python3 mods/ow-poc/tools/bake_lpc_parts.py PATH_TO_LPC_REPOSITORY"""
import csv, json, struct, sys
from pathlib import Path
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import import_lpc_test as L                      # noqa: E402  (shared downsizing: CELL, OUT_W/H, anchors, rows)

MOD = HERE.parent
OUT = MOD / "assets" / "lpc_parts"
ALLOWED = ("OGA-BY", "CC-BY-SA", "CC0", "GPL")

# A layer path may hold "{b}" (male / female), "{l}" (male / thin: legs and feet) for the body type.
BODY = {"male": {"b": "male", "l": "male"}, "female": {"b": "female", "l": "thin"}}
Z = {"cape_bg": 5, "hair_bg": 8, "body": 10, "head": 12, "feet": 20, "legs": 22, "top": 30, "cape_fg": 40, "facial": 45, "hair": 50, "hat": 60}

# skin: a per-channel multiplier of the LPC body's own colours (keeps the shading and the eyes' hue)
SKIN = [("natural", (1.0, 1.0, 1.0)), ("fair", (1.04, 1.0, 0.98)), ("tan", (0.9, 0.78, 0.66)), ("brown", (0.74, 0.58, 0.45)), ("dark", (0.58, 0.42, 0.31)),
        ("deep", (0.44, 0.31, 0.23))]
HAIR_COL = [("brown", (72, 42, 28)), ("black", (30, 28, 34)), ("dark brown", (52, 34, 26)), ("blond", (150, 80, 10)), ("red", (130, 34, 16)),
            ("orange", (170, 80, 10)), ("silver", (120, 120, 136)), ("blue", (30, 52, 120)), ("violet", (72, 34, 104)), ("green", (28, 84, 42))]
TOP_COL = [("blue", (46, 72, 150)), ("red", (120, 22, 26)), ("green", (26, 80, 38)), ("black", (24, 24, 30)), ("white", (150, 150, 146)),
           ("violet", (68, 30, 108)), ("gold", (128, 96, 22)), ("teal", (16, 84, 92)), ("brown", (80, 48, 24)), ("grey", (72, 72, 82))]
HAIR = [("spiked", ["hair/spiked2/adult"]), ("hawk", ["hair/shorthawk/adult"]), ("liberty", ["hair/spiked_liberty/adult"]),
        ("porcupine", ["hair/spiked_porcupine/adult"]), ("messy", ["hair/messy1/adult"]), ("messy 2", ["hair/messy2/adult"]),
        ("bedhead", ["hair/bedhead/adult"]), ("mop", ["hair/mop/adult"]), ("parted", ["hair/parted/adult"]), ("swoop", ["hair/swoop/adult"]),
        ("curly", ["hair/curly_short/adult"]), ("afro", ["hair/afro/adult"]), ("bob", ["hair/bob/adult"]), ("pixie", ["hair/pixie/adult"]),
        ("long", ["hair/long/adult"]), ("long messy", ["hair/long_messy/adult"]), ("ponytail", ["hair/ponytail/adult/bg", "hair/ponytail/adult/fg"]),
        ("long tied", ["hair/long_tied/adult/bg", "hair/long_tied/adult/fg"]), ("pigtails", ["hair/pigtails/adult"]), ("buzzcut", ["hair/buzzcut/adult"]),
        ("none", [])]
TOP = [("v-neck", "torso/clothes/longsleeve/longsleeve2_vneck/{b}"), ("longsleeve", "torso/clothes/longsleeve/longsleeve/{b}"),
       ("buttoned", "torso/clothes/longsleeve/longsleeve2_buttoned/{b}"), ("polo", "torso/clothes/longsleeve/longsleeve2_polo/{b}"),
       ("cardigan", "torso/clothes/longsleeve/longsleeve2_cardigan/{b}"), ("cuffed", "torso/clothes/longsleeve/longsleeves_cuffed/{b}"),
       ("t-shirt", "torso/clothes/shortsleeve/tshirt/{b}"), ("t-shirt v", "torso/clothes/shortsleeve/tshirt_vneck/{b}"),
       ("short polo", "torso/clothes/shortsleeve/shortsleeve_polo/{b}"), ("sleeveless", "torso/clothes/sleeveless/sleeveless1/{b}"),
       ("tank v", "torso/clothes/sleeveless/sleeveless2_vneck/{b}")]
LEGS = [("navy pants", "legs/pants/{l}", (38, 42, 68)), ("black pants", "legs/pants/{l}", (30, 30, 36)), ("brown pants", "legs/pants/{l}", (84, 64, 38)),
        ("grey pants", "legs/pants2/{l}", (92, 92, 104)), ("khaki pants", "legs/pants2/{l}", (150, 128, 82)), ("jeans", "legs/cuffed/{l}", (52, 78, 132)),
        ("shorts", "legs/shorts/shorts/{l}", (106, 78, 48)), ("leggings", "legs/leggings/{l}", (34, 30, 46)), ("red skirt", "legs/skirts/plain/{l}", (146, 42, 44)),
        ("formal", "legs/formal/{l}", (36, 36, 44))]
SHOES = [("shoes", "feet/shoes/basic/{l}", (38, 30, 34)), ("brown shoes", "feet/shoes/basic/{l}", (74, 48, 30)), ("boots", "feet/boots/basic/{l}", (64, 44, 30)),
         ("black boots", "feet/boots/fold/{l}", (32, 28, 34)), ("rimmed boots", "feet/boots/rimmed/{l}", (90, 60, 36)), ("sandals", "feet/sandals/{l}", (110, 80, 50)),
         ("slippers", "feet/slippers/{l}", (140, 40, 40))]
ACC = [("none", []),
       ("red cape", [("cape/solid/bg", "cape_bg", (150, 30, 34)), ("cape/solid/fg", "cape_fg", (150, 30, 34))]),
       ("violet cape", [("cape/solid/bg", "cape_bg", (66, 36, 94)), ("cape/solid/fg", "cape_fg", (66, 36, 94))]),
       ("tattered cape", [("cape/tattered/bg", "cape_bg", (34, 32, 40)), ("cape/tattered/fg", "cape_fg", (34, 32, 40))]),
       ("hood", [("hat/cloth/hood/adult", "hat", (52, 40, 70))]),
       ("bandana", [("hat/cloth/bandana/adult", "hat", (154, 34, 38))]),
       ("headband", [("hat/headband/tied/adult", "hat", (154, 34, 38))]),
       ("rune band", [("hat/headband/thick/adult", "hat", (40, 60, 130))]),
       ("leather cap", [("hat/cloth/leather_cap/adult", "hat", (120, 84, 50))]),
       ("wizard hat", [("hat/magic/wizard/base/adult", "hat", (60, 50, 130)), ("hat/magic/wizard/belt/adult", "hat", (176, 140, 56))]),
       ("glasses", [("facial/glasses/round/adult", "facial", None)]),
       ("sunglasses", [("facial/glasses/sunglasses/adult", "facial", None)]),
       ("eyepatch", [("facial/patches/eyepatch/ambi/adult", "facial", None)])]
# Base presets: [skin, hair, hair colour, top, top colour, legs, shoes, accessory] + body.  "Hero" is the current LPC hero (spr_lpc_test).
BASES = [("Hero", "male", [0, 0, 0, 0, 0, 0, 0, 0]),
         ("Duelist", "female", [2, 17, 4, 4, 5, 7, 3, 6]),
         ("Rogue", "male", [4, 5, 1, 9, 1, 2, 5, 5]),
         ("Mystic", "female", [1, 14, 1, 1, 5, 1, 3, 2]),
         ("Scholar", "male", [3, 8, 3, 3, 2, 4, 1, 10]),
         ("Ranger", "female", [5, 10, 2, 2, 7, 5, 4, 3])]

used = set()


def bake(rel, body):
    """the layer at `rel` (with {b}/{l} filled) as a .lpl; returns its file name (cached)"""
    path = rel.format(**BODY[body]) if "{" in rel else rel
    name = path.replace("/", "_") + ".lpl"
    if (OUT / name).exists() and name in baked:
        return name
    frames = L.cells(ROOT, ((path, None),))                 # untinted: the game tints
    for a in ("idle", "walk"):
        if (ROOT / "spritesheets" / path / f"{a}.png").is_file():
            used.add(f"{path}/{a}.png")
    with (OUT / name).open("wb") as f:
        f.write(b"LPL1" + bytes([L.OUT_W, L.OUT_H, len(frames[0]), 0]))
        for row in frames:
            for im in row:
                a = np.asarray(im, dtype=np.uint8)
                f.write(a[..., 3].tobytes())
                rgb = a[..., :3].copy(); rgb[a[..., 3] == 0] = 0
                f.write(rgb.tobytes())
        # the same layer at the source resolution (64x64, the idle pose of each direction): the creator's big preview and busts
        idle = L.load_layers(ROOT, "idle", ((path, None),))[0]
        for d in range(4):
            cell = idle.crop((0, L.LPC_ROWS[d] * L.CELL, L.CELL, (L.LPC_ROWS[d] + 1) * L.CELL))
            a = np.asarray(cell, dtype=np.uint8)
            f.write(a[..., 3].tobytes())
            rgb = a[..., :3].copy(); rgb[a[..., 3] == 0] = 0
            f.write(rgb.tobytes())
    baked.add(name)
    return name


def layers(spec, body):
    return [{"file": bake(rel, body), "z": Z[z], "tint": tint} for rel, z, tint in spec]


def main():
    global ROOT, baked
    ROOT = Path(sys.argv[1]).resolve()
    baked = set()
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.lpl"):
        old.unlink()
    man = {"format": "journey-lpc-parts-1", "hi": 64, "w": L.OUT_W, "h": L.OUT_H, "frames": 10, "anchor": list(L.DRAW_ANCHOR),
           "slots": ["skin", "hair", "hair_colour", "top", "top_colour", "legs", "shoes", "accessory"],
           "skin": [{"name": n, "mul": c} for n, c in SKIN], "hair_colour": [{"name": n, "rgb": c} for n, c in HAIR_COL],
           "top_colour": [{"name": n, "rgb": c} for n, c in TOP_COL], "body": {}, "hair": [], "top": [], "legs": [], "shoes": [], "accessory": [],
           "bases": [{"name": n, "body": b, "cg": cg} for n, b, cg in BASES]}
    for body in BODY:
        man["body"][body] = layers([("body/bodies/" + BODY[body]["b"], "body", "skin"), ("head/heads/human/" + BODY[body]["b"], "head", "skin")], body)
    for n, paths in HAIR:
        o = {"name": n, "male": [], "female": []}
        for body in BODY:
            o[body] = layers([(p, "hair_bg" if p.endswith("/bg") else "hair", "hair") for p in paths], body)
        man["hair"].append(o)
    for n, p in TOP:
        man["top"].append({"name": n, **{b: layers([(p, "top", "top")], b) for b in BODY}})
    for n, p, c in LEGS:
        man["legs"].append({"name": n, "rgb": c, **{b: layers([(p, "legs", list(c))], b) for b in BODY}})
    for n, p, c in SHOES:
        man["shoes"].append({"name": n, "rgb": c, **{b: layers([(p, "feet", list(c))], b) for b in BODY}})
    for n, spec in ACC:
        man["accessory"].append({"name": n, **{b: layers([(r, z, list(t) if t else None) for r, z, t in spec], b) for b in BODY}})
    # credits: only the four allowed licence families; a part whose file has none of them stops the bake
    rows = {r["filename"].replace("\\", "/"): r for r in csv.DictReader((ROOT / "CREDITS.csv").open(encoding="utf-8"))}
    fields = list(next(iter(rows.values())).keys())
    out_rows = {}
    old = MOD / "assets" / "lpc_runtime_credits.csv"
    if old.exists():
        for r in csv.DictReader(old.open(encoding="utf-8")):
            out_rows[r["filename"]] = r
    for f in sorted(used):
        r = rows.get(f)
        if not r:
            raise SystemExit(f"no credit row for {f}")
        if not any(a in r["licenses"] for a in ALLOWED):
            raise SystemExit(f"licence not allowed for {f}: {r['licenses']}")
        out_rows[f] = r
    with old.open("w", encoding="utf-8", newline="") as o:
        w = csv.DictWriter(o, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for k in sorted(out_rows):
            w.writerow(out_rows[k])
    (OUT / "manifest.json").write_text(json.dumps(man, indent=1) + "\n")
    print(f"LPC parts: {len(baked)} layers, hair {len(HAIR)}, hair colours {len(HAIR_COL)}, tops {len(TOP)} x {len(TOP_COL)} colours, "
          f"legs {len(LEGS)}, shoes {len(SHOES)}, accessories {len(ACC)}, skins {len(SKIN)}, bases {len(BASES)}; credits {len(out_rows)} rows")


if __name__ == "__main__":
    main()
