#!/usr/bin/env python3
"""Self-check of the chargen layers (python3 tools/verify.py from art_dk/chargen)."""
import os, sys, itertools, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
sys.path.insert(0, ROOT)
import compose as C
man = C.manifest()
ok = True
def check(c, msg):
    global ok
    if not c: ok = False; print("FAIL", msg)
n = 0
for part, styles in man["parts"].items():
    for style, e in styles.items():
        if not e.get("bin"): continue
        a = C.load_spr1(os.path.join(ROOT, e["bin"])); b = C.load_cgp1(os.path.join(ROOT, e["packed"])); n += 1
        check(os.path.getsize(os.path.join(ROOT, e["bin"])) == 14 + 20 * 2976 * 8, "size " + e["bin"])
        for key in a:
            k, w, r = a[key]; kb, wb, rb = b[key]
            check((k == kb).all() and (w == wb).all() and (r == rb).all(), "packed != bin %s %s" % (e["bin"], key))
            if style != "base" or part != "body" or True:
                solid = k != 255
                check(not solid[0].any() and not solid[-1].any() and not solid[:, 0].any() and not solid[:, -1].any(), "touches the frame border %s %s" % (e["bin"], key))
            check(((k == 0) | (k == 254) | (k == 255)).all(), "bad kind")
            check(((w > 0).sum(-1) <= 1)[k == 0].all(), "more than one slot weight on a texel")
        for f in range(5):                      # right = mirror of left
            for x in range(3):
                check((a[("right", f)][x] == a[("left", f)][x][:, ::-1]).all(), "right != mirror(left) %s %d" % (e["bin"], f))
        # same pose grid: nothing extends below the feet line (row 57) or above row 0
        for key, (k, w, r) in a.items():
            ys = np.nonzero((k != 255).any(1))[0]
            if len(ys): check(ys.max() <= 57 and ys.min() >= 0, "outside the pose grid %s %s %d..%d" % (e["bin"], key, ys.min(), ys.max()))
# every body silhouette contains each outfit's solid texels in the lower body/legs region? (no skin leaks: each outfit hides the body legs)
leaks = 0
body = C.load_spr1(os.path.join(ROOT, man["parts"]["body"]["base"]["bin"]))
for st in man["parts"]["outfit"]:
    o = C.load_spr1(os.path.join(ROOT, man["parts"]["outfit"][st]["bin"]))
    for key in o:
        kb = body[key][0] == 0; ko = o[key][0] == 0
        # skin pixels of the body below the neck that stay uncovered (should only be hands / forearms, which the outfit redraws in slot 3)
        legs = kb.copy(); legs[:44] = False
        leak = legs & ~ko
        if leak.any(): leaks += 1; print("leg skin shows with outfit", st, key, int(leak.sum()))
print("legs leaking skin:", leaks)
# every combination composites (count them, composite a random sample)
nsk, nh = len(man["palettes"]["skin"]), len(man["palettes"]["hair"])
total = 0
for o, oe in man["parts"]["outfit"].items():
    for h in man["parts"]["hair"]:
        for a, ae in man["parts"]["accessory"].items():
            total += nsk * len(oe["colourways"]) * nh * len(ae["colourways"])
avoid = len(man["avoid_combinations"])
print("layer files", n, "| combinations (skin x outfit x colourway x hair x colour x accessory x colourway):", total)
import random; random.seed(4)
for _ in range(60):
    sel = dict(skin=random.randrange(nsk), outfit=random.choice(list(man["parts"]["outfit"])), hair=random.choice(list(man["parts"]["hair"])), hair_colour=random.randrange(nh),
               accessory=random.choice(list(man["parts"]["accessory"])))
    sel["outfit_colour"] = random.randrange(3); sel["accessory_colour"] = random.randrange(len(man["parts"]["accessory"][sel["accessory"]]["colourways"]))
    for d in C.DIRS:
        c = C.composite_cell(man, sel, d, random.randrange(5)); check(c[..., 3].any(), "empty composite")
pg = C.composite_page(man, dict(skin=1, outfit="jacket", hair="spiky", accessory="cap"))
check(pg.shape == (256, 256) and (pg != 0).any(), "page")
print("OK" if ok else "FAILED")
sys.exit(0 if ok else 1)
