#!/usr/bin/env python3
"""Packs the chapter 2 art (art_dk, read only) into the mod's assets: the harbor, the ship deck and the Shore of Illusions.

  python3 tools/build_kingdom_assets.py [ART_DIR] [--preview DIR]

Same formats as build_part3_assets.py: painted_<area>.raw (4 banks of 128px cells, stride 126, picture then
occluder cells), painted_<area>_occ.bin (u16 count, then x0,y0,cell,base_y), painted_<area>_col.bin (320x180, 1 = blocked).
Walkable masks: the harbor's is drawn (masks/harbor_walkable_160x90.png); the deck is a polygon less its cargo; the
beach is the sand (a colour test) plus the pier, less the tents, stall, mirror, rocks and trees.
"""
import json, math, os, shutil, struct, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
argv = sys.argv[1:]
if "--preview" in argv: i = argv.index("--preview"); PREV = argv[i + 1]; del argv[i:i + 2]
else: PREV = None
args = argv
ART = args[0] if args else "/workspace/study/fmrecomp/art_dk"
OUT = os.path.join(MOD, "assets")
CELL, STRIDE, BW, BH = 128, 126, 1280, 720
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0 - 0.5


def to555(a):
    h, w, _ = a.shape
    ys, xs = np.mgrid[0:h, 0:w]
    th = BAYER[ys % 4, xs % 4]
    out = np.zeros((h, w), np.uint16)
    for c, sh in enumerate((0, 5, 10)):
        out |= np.clip(np.floor(a[:, :, c] / 255.0 * 31.0 + th * 0.9 + 0.5), 0, 31).astype(np.uint16) << sh
    return out | 0x8000


def cut(img, mask, x0, y0):
    c = np.zeros((CELL, CELL), np.uint16)
    h = min(CELL, BH - y0); w = min(CELL, BW - x0)
    c[:h, :w] = img[y0:y0 + h, x0:x0 + w]
    if h < CELL: c[h:, :w] = img[BH - 1:BH, x0:x0 + w]
    if w < CELL: c[:, w:] = c[:, w - 1:w]
    if mask is not None:
        mk = np.zeros((CELL, CELL), bool); mk[:h, :w] = mask[y0:y0 + h, x0:x0 + w]
        c = np.where(mk, c, 0).astype(np.uint16)
    return c


def shape_mask(shapes):
    m = Image.new("L", (BW, BH), 0); d = ImageDraw.Draw(m)
    for s in shapes:
        if s[0] == "r": d.rectangle(s[1:5], fill=255)
        elif s[0] == "c": d.ellipse([s[1] - s[3], s[2] - s[3], s[1] + s[3], s[2] + s[3]], fill=255)
        else: d.polygon([tuple(p) for p in s[1]], fill=255)
    return np.array(m) > 0


def pack(name, pic_path, walk_px, occluders):
    """walk_px: 1280x720 bool; occluders: [(bool mask 1280x720, base_y)]"""
    pic = np.array(Image.open(pic_path).convert("RGB")).astype(np.float32)
    tex = to555(pic)
    cells, table = [], []
    for r in range(6):
        for c in range(11): cells.append(cut(tex, None, c * STRIDE, r * STRIDE))
    for m, base in occluders:
        ys, xs = np.nonzero(m)
        if not len(ys): continue
        for r in range(ys.min() // STRIDE, min(5, ys.max() // STRIDE) + 1):
            for c in range(xs.min() // STRIDE, min(10, xs.max() // STRIDE) + 1):
                x0, y0 = c * STRIDE, r * STRIDE
                if m[y0:y0 + CELL, x0:x0 + CELL].sum() < 4: continue
                table.append((x0, y0, len(cells), int(base)))
                cells.append(cut(tex, m, x0, y0))
    assert len(cells) <= 128, "%s: %d cells do not fit 4 banks" % (name, len(cells))
    banks = np.zeros((4, 512, 1024), np.uint16)
    for i, c in enumerate(cells):
        b, k = divmod(i, 32)
        banks[b, (k // 8) * CELL:(k // 8 + 1) * CELL, (k % 8) * CELL:(k % 8 + 1) * CELL] = c
    with open(OUT + "/painted_%s.raw" % name, "wb") as f: f.write(struct.pack("<HHHH", 4, 0, 0, 0) + banks.tobytes())
    with open(OUT + "/painted_%s_occ.bin" % name, "wb") as f:
        f.write(struct.pack("<H", len(table)))
        for t in table: f.write(struct.pack("<HHHH", *t))
    walk = np.array(Image.fromarray(walk_px.astype(np.uint8) * 255).resize((320, 180), Image.BOX)) > 200
    open(OUT + "/painted_%s_col.bin" % name, "wb").write((~walk).astype(np.uint8).tobytes())
    if PREV:
        a = pic.copy(); w = np.array(Image.fromarray(walk.astype(np.uint8) * 255).resize((BW, BH), Image.NEAREST)) > 0
        a[~w] = a[~w] * 0.55 + np.array([140, 0, 0]) * 0.45
        for m, _ in occluders: a[m] = a[m] * 0.6 + np.array([0, 0, 160]) * 0.4
        Image.fromarray(a.astype(np.uint8)).save(os.path.join(PREV, "mask_%s.png" % name))
    print("%s: %d cells (%d occluder), %d of %d collision cells walkable" % (name, len(cells), len(table), int(walk.sum()), walk.size))


def harbor():
    j = json.load(open(ART + "/masks/harbor_occluders.json"))
    walk = np.array(Image.open(ART + "/masks/harbor_walkable_160x90.png").convert("L").resize((BW, BH), Image.NEAREST)) > 127
    walk |= shape_mask([("r", 0, 300, 60, 430)])           # the road in from the village bridge, west end of the boardwalk
    occ = [(shape_mask([("p", o["polygon"])]), o["base_y"]) for o in j["occluders"]]
    pack("harbor", ART + "/backgrounds/dk_harbor_1280x720.jpg", walk, occ)


def ship_deck():
    deck = shape_mask([("p", [(250, 165), (1015, 165), (1090, 230), (1120, 335), (1090, 440), (1015, 512), (250, 512)]),
                       ("r", 560, 500, 636, 560)])        # the head of the gangway
    cargo = shape_mask([("c", 617, 350, 46), ("r", 262, 280, 356, 386), ("c", 350, 172, 30), ("c", 745, 168, 30),
                        ("r", 772, 140, 970, 212), ("c", 1080, 268, 26), ("r", 1036, 312, 1090, 378), ("c", 1080, 424, 26),
                        ("c", 302, 486, 30), ("c", 426, 494, 30), ("c", 950, 482, 30), ("r", 668, 452, 786, 552)])
    occ = [(shape_mask([("r", 668, 450, 786, 552)]), 548)]
    pack("ship_deck", ART + "/kingdom/backgrounds/dk_ship_deck_1280x720.jpg", deck & ~cargo, occ)


def beach():
    pic = np.array(Image.open(ART + "/kingdom/backgrounds/dk_beach_1280x720.jpg").convert("HSV")).astype(np.float32)
    h, s, v = pic[..., 0] * 360 / 255, pic[..., 1] / 255, pic[..., 2] / 255
    sand = (h > 22) & (h < 52) & (s > 0.18) & (s < 0.75) & (v > 0.62)
    sand = np.array(Image.fromarray(sand.astype(np.uint8) * 255).filter(ImageFilter.MedianFilter(9))) > 127
    walk = sand | shape_mask([("r", 225, 480, 355, 660)])
    walk &= ~shape_mask([("r", 0, 0, 1280, 40), ("r", 0, 690, 1280, 720), ("r", 600, 20, 720, 172),
                         ("r", 772, 130, 905, 285), ("c", 1000, 400, 30)])
    tents = ("r", 930, 190, 1225, 470)
    occ = [(shape_mask([("r", 600, 20, 720, 172)]) & ~sand, 172), (shape_mask([("r", 772, 130, 905, 285)]) & ~sand, 285),
           (shape_mask([tents]) & ~sand, 400)]
    pack("beach", ART + "/kingdom/backgrounds/dk_beach_1280x720.jpg", walk, occ)


def forest():
    """The Forest of Whispers: the paths and the grass are walkable (a colour test on the blurred picture), the
    trees, rocks and bushes are not; the canopies that hang over a path are drawn over the player."""
    src = ART + "/raw/dk_forest_raw.jpg"
    pic = Image.open(src).convert("RGB")
    hsv = np.array(pic.filter(ImageFilter.GaussianBlur(5)).convert("HSV")).astype(np.float32)
    h, v = hsv[..., 0] * 360 / 255, hsv[..., 2] / 255
    walk = (h < 78) & (v > 0.48)
    walk = np.array(Image.fromarray(walk.astype(np.uint8) * 255).filter(ImageFilter.MedianFilter(15))) > 127
    walk &= ~shape_mask([("r", 0, 0, 1280, 30), ("r", 480, 70, 640, 215)])        # the top edge; the stone gate itself
    walk |= shape_mask([("r", 150, 640, 260, 720), ("r", 520, 200, 590, 260)])    # the south path in from the beach; the gate's steps
    trees = [((360, 470, 590, 640), 690), ((640, 480, 880, 650), 700), ((1100, 400, 1280, 560), 620), ((740, 50, 920, 210), 260),
             ((0, 290, 160, 450), 520), ((170, 80, 360, 230), 300)]
    occ = [(shape_mask([("r",) + r]) & ~walk, base) for r, base in trees]
    pack("forest", src, walk, occ)


def mountain():
    """The Mountain Pass (chapter 4): the dirt and grass are walkable (a colour test), the chasm, the cliffs and the
    clouds are not; the rope bridge is the one way across; the pines and the tent are drawn over the player."""
    src = ART + "/raw/dk_mountain_raw.jpg"
    pic = Image.open(src).convert("RGB")
    hsv = np.array(pic.filter(ImageFilter.GaussianBlur(4)).convert("HSV")).astype(np.float32)
    h, sat, v = hsv[..., 0] * 360 / 255, hsv[..., 1] / 255, hsv[..., 2] / 255
    walk = (h < 85) & (h > 18) & (v > 0.42) & (sat > 0.38)
    walk = np.array(Image.fromarray(walk.astype(np.uint8) * 255).filter(ImageFilter.MedianFilter(15))) > 127
    chasm = [(550, 150), (570, 310), (590, 440), (575, 525), (535, 600), (520, 720), (830, 720), (800, 625), (750, 525),
             (762, 440), (750, 310), (700, 150), (690, 0), (560, 0)]
    walk &= ~shape_mask([("p", chasm), ("r", 0, 0, 1280, 40), ("r", 1240, 0, 1280, 720), ("r", 940, 0, 1280, 130),
                         ("r", 335, 255, 515, 395),                       # the tent and its crates
                         ("p", [(880, 120), (1060, 110), (1230, 220), (1240, 440), (1100, 440), (1060, 365), (1010, 360), (880, 330)])])   # the cave cliff
    walk |= shape_mask([("r", 575, 452, 760, 505),                         # the rope bridge
                        ("r", 150, 640, 300, 720),                         # the trail in from the forest
                        ("r", 780, 150, 880, 210), ("r", 990, 350, 1070, 400)])   # the gate's steps; the cave mouth
    pines = [((20, 430, 230, 680), 690), ((260, 540, 400, 700), 700), ((110, 220, 190, 330), 340), ((1150, 400, 1240, 500), 500)]
    occ = [(shape_mask([("r",) + r]) & ~walk, base) for r, base in pines]
    occ.append((shape_mask([("r", 345, 255, 505, 330)]), 400))             # the tent's roof
    pack("mountain", src, walk, occ)




def meadow():
    """The Meadow Maze (chapter 5): grass and maze paths are walkable; dense hedges are not; carts and
    hedge tops occlude the player."""
    src = ART + "/raw/dk_meadow_raw.jpg"
    pic = Image.open(src).convert("RGB")
    hsv = np.array(pic.filter(ImageFilter.GaussianBlur(4)).convert("HSV")).astype(np.float32)
    h, sat, v = hsv[..., 0] * 360 / 255, hsv[..., 1] / 255, hsv[..., 2] / 255
    walk = (h > 35) & (h < 160) & (v > 0.35)
    walk = np.array(Image.fromarray(walk.astype(np.uint8) * 255).filter(ImageFilter.MedianFilter(15))) > 127
    walk |= shape_mask([("r", 80, 620, 280, 720), ("r", 560, 300, 720, 420), ("r", 580, 80, 700, 180),
                        ("r", 980, 520, 1180, 680), ("r", 60, 120, 260, 280)])
    walk &= ~shape_mask([("r", 0, 0, 1280, 40), ("r", 0, 680, 1280, 720),
                         ("r", 300, 200, 420, 520), ("r", 860, 200, 980, 500)])
    hedges = [((320, 180, 500, 260), 280), ((740, 180, 920, 260), 280),
              ((320, 420, 500, 520), 540), ((740, 420, 920, 520), 540), ((40, 100, 220, 200), 220)]
    occ = [(shape_mask([("r",) + r]) & ~walk, base) for r, base in hedges]
    occ.append((shape_mask([("r", 100, 620, 260, 700)]), 710))
    pack("meadow", src, walk, occ)


def desert():
    """The Desert of Lost Stars (chapter 6): sand paths are walkable; deep dune bowls and tent
    footprints are not; tent roofs and the tomb mouth occlude the player."""
    src = ART + "/raw/dk_desert_raw.jpg"
    pic = Image.open(src).convert("RGB")
    hsv = np.array(pic.filter(ImageFilter.GaussianBlur(4)).convert("HSV")).astype(np.float32)
    h, sat, v = hsv[..., 0] * 360 / 255, hsv[..., 1] / 255, hsv[..., 2] / 255
    # sand / path: yellow-orange hues, decent brightness
    walk = (h > 15) & (h < 70) & (v > 0.35) & (sat > 0.15)
    walk = np.array(Image.fromarray(walk.astype(np.uint8) * 255).filter(ImageFilter.MedianFilter(15))) > 127
    walk |= shape_mask([("r", 120, 620, 320, 720), ("r", 380, 340, 560, 460), ("r", 560, 80, 720, 200),
                        ("r", 880, 500, 1100, 660), ("r", 160, 460, 300, 560), ("r", 820, 300, 980, 420)])
    walk &= ~shape_mask([("r", 0, 0, 1280, 50), ("r", 0, 690, 1280, 720),
                         ("r", 150, 470, 320, 560),   # caravan tent footprint
                         ("r", 820, 280, 1000, 380),  # fortune tent footprint
                         ("r", 920, 520, 1120, 640)]) # tomb mouth
    tents = [((150, 430, 320, 520), 540), ((820, 250, 1000, 340), 360), ((40, 100, 180, 200), 220)]
    occ = [(shape_mask([("r",) + r]) & ~walk, base) for r, base in tents]
    occ.append((shape_mask([("r", 940, 500, 1100, 580)]), 600))  # tomb pillars
    pack("desert", src, walk, occ)





def hall():
    """Castle Hall (chapter 9): stone floor walkable; stall/pit/pedestal blocked."""
    src = ART + "/raw/dk_hall_raw.jpg"
    pic = Image.open(src).convert("RGB")
    hsv = np.array(pic.filter(ImageFilter.GaussianBlur(4)).convert("HSV")).astype(np.float32)
    h, sat, v = hsv[..., 0] * 360 / 255, hsv[..., 1] / 255, hsv[..., 2] / 255
    walk = ((sat < 0.35) & (v > 0.30) & (v < 0.90)) | ((h > 20) & (h < 60) & (v > 0.35))
    walk = np.array(Image.fromarray(walk.astype(np.uint8) * 255).filter(ImageFilter.MedianFilter(15))) > 127
    walk |= shape_mask([("r", 560, 160, 720, 700), ("r", 160, 360, 360, 560), ("r", 880, 400, 1100, 600),
                        ("r", 200, 560, 340, 680), ("r", 200, 400, 300, 460), ("r", 960, 460, 1060, 520)])
    walk &= ~shape_mask([("r", 0, 0, 1280, 40), ("r", 0, 690, 1280, 720),
                         ("r", 500, 80, 780, 180), ("r", 120, 300, 300, 400), ("r", 940, 400, 1140, 500)])
    tents = [((120, 300, 300, 400), 420), ((40, 100, 180, 200), 220)]
    occ = [(shape_mask([("r",) + r]) & ~walk, base) for r, base in tents]
    occ.append((shape_mask([("r", 520, 80, 760, 160)]), 180))
    pack("hall", src, walk, occ)


def dream():
    """Dream Room (chapter 10): marble floor walkable; tents/table rim soft-blocked."""
    src = ART + "/raw/dk_dream_raw.jpg"
    pic = Image.open(src).convert("RGB")
    hsv = np.array(pic.filter(ImageFilter.GaussianBlur(4)).convert("HSV")).astype(np.float32)
    h, sat, v = hsv[..., 0] * 360 / 255, hsv[..., 1] / 255, hsv[..., 2] / 255
    walk = ((sat < 0.30) & (v > 0.35)) | ((h > 15) & (h < 55) & (v > 0.40))
    walk = np.array(Image.fromarray(walk.astype(np.uint8) * 255).filter(ImageFilter.MedianFilter(15))) > 127
    walk |= shape_mask([("r", 520, 200, 760, 700), ("r", 160, 520, 360, 680), ("r", 780, 360, 1000, 520),
                        ("r", 600, 320, 700, 420)])
    walk &= ~shape_mask([("r", 0, 0, 1280, 40), ("r", 0, 690, 1280, 720),
                         ("r", 140, 540, 280, 660), ("r", 320, 560, 420, 660)])
    tents = [((140, 540, 280, 640), 660), ((320, 560, 420, 640), 660)]
    occ = [(shape_mask([("r",) + r]) & ~walk, base) for r, base in tents]
    pack("dream", src, walk, occ)


def gate():
    """The Castle Gate (chapter 8): stone plaza walkable; stall, pit rim, and gate wall are not;
    stall awning and tower bases occlude."""
    src = ART + "/raw/dk_gate_raw.jpg"
    pic = Image.open(src).convert("RGB")
    hsv = np.array(pic.filter(ImageFilter.GaussianBlur(4)).convert("HSV")).astype(np.float32)
    h, sat, v = hsv[..., 0] * 360 / 255, hsv[..., 1] / 255, hsv[..., 2] / 255
    walk = ((h > 40) & (h < 160) & (v > 0.28)) | ((sat < 0.25) & (v > 0.35) & (v < 0.85))
    walk = np.array(Image.fromarray(walk.astype(np.uint8) * 255).filter(ImageFilter.MedianFilter(15))) > 127
    walk |= shape_mask([("r", 560, 160, 720, 700), ("r", 140, 360, 360, 560), ("r", 860, 400, 1120, 600),
                        ("r", 160, 560, 320, 680), ("r", 180, 400, 280, 460),  # front of pawn stall
                        ("r", 960, 460, 1080, 520)])  # front of moat pit hatch
    walk &= ~shape_mask([("r", 0, 0, 1280, 50), ("r", 0, 690, 1280, 720),
                         ("r", 400, 40, 880, 100),    # gate wall (leave doorstep walkable)
                         ("r", 120, 300, 300, 400),   # pawn stall footprint
                         ("r", 940, 400, 1140, 500)]) # moat pit bowl
    tents = [((120, 330, 320, 420), 440), ((40, 100, 180, 200), 220)]
    occ = [(shape_mask([("r",) + r]) & ~walk, base) for r, base in tents]
    occ.append((shape_mask([("r", 500, 40, 780, 140)]), 160))
    pack("gate", src, walk, occ)


def fair():
    """The Star Fair (chapter 7): grass and dirt paths are walkable; stall footprints and the pond
    are not; tent roofs and stall awnings occlude the player."""
    src = ART + "/raw/dk_fair_raw.jpg"
    pic = Image.open(src).convert("RGB")
    hsv = np.array(pic.filter(ImageFilter.GaussianBlur(4)).convert("HSV")).astype(np.float32)
    h, sat, v = hsv[..., 0] * 360 / 255, hsv[..., 1] / 255, hsv[..., 2] / 255
    walk = ((h > 40) & (h < 160) & (v > 0.30)) | ((h > 15) & (h < 50) & (sat > 0.20) & (v > 0.35))
    walk = np.array(Image.fromarray(walk.astype(np.uint8) * 255).filter(ImageFilter.MedianFilter(15))) > 127
    walk |= shape_mask([("r", 560, 620, 720, 720), ("r", 560, 320, 720, 460), ("r", 560, 80, 720, 180),
                        ("r", 140, 300, 280, 400), ("r", 960, 500, 1140, 640), ("r", 160, 540, 300, 640)])
    walk &= ~shape_mask([("r", 0, 0, 1280, 50), ("r", 0, 690, 1280, 720),
                         ("r", 120, 280, 300, 400),   # purple bazaar tent
                         ("r", 980, 320, 1160, 460),  # red tent
                         ("r", 80, 560, 200, 680)])   # pond
    tents = [((120, 250, 300, 340), 360), ((980, 300, 1160, 400), 420), ((40, 100, 160, 200), 220)]
    occ = [(shape_mask([("r",) + r]) & ~walk, base) for r, base in tents]
    occ.append((shape_mask([("r", 1000, 500, 1140, 580)]), 600))
    pack("fair", src, walk, occ)


harbor(); ship_deck(); beach(); forest(); mountain(); meadow(); desert(); fair(); gate(); hall(); dream()
for n in ("forest_mage", "keith", "mountain_mage", "meadow_mage", "desert_mage", "isis", "ring_champ", "pawn_paul", "heishin", "pegasus"):
    shutil.copy(ART + "/kingdom/baked/spr_%s.bin" % n, OUT + "/spr_%s.bin" % n)
for n in ("mai", "weevil", "shadi", "soldier", "trader", "camp_merchant"):
    shutil.copy(ART + "/kingdom/baked/spr_%s.bin" % n, OUT + "/spr_%s.bin" % n)
shutil.copy(ART + "/baked/spr_inseto.bin", OUT + "/spr_inseto.bin")
