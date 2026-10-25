#!/usr/bin/env python3
"""Painted village v2: clean plate (palms removed) + palm sway sprites + house occluders + collision.
Outputs into the mod: assets/painted.raw, painted_col.bin, painted_palms.raw, painted_data.h"""
import sys, struct, math
import numpy as np, cv2
from PIL import Image, ImageDraw
from palm_masks import masks
from palms_def import PALMS

import os
HERE = os.path.dirname(os.path.abspath(__file__))
W_DIR = os.environ.get("VR_TMP", os.path.join(HERE, "tmp")); os.makedirs(W_DIR, exist_ok=True)       # scratch (palms_tmp.raw, preview) - NOT painted_work
RAW_IN = os.environ.get("VR_RAW", "/workspace/study/fmrecomp/painted_work/bg_raw.jpg")
CLEAN_IN = os.environ.get("VR_CLEAN", "/workspace/study/fmrecomp/painted_work/bg_clean.png")
OUT = sys.argv[1]; os.makedirs(OUT + "/assets", exist_ok=True)
ORIG = cv2.cvtColor(cv2.imread(RAW_IN), cv2.COLOR_BGR2RGB)
CLEAN = cv2.cvtColor(cv2.imread(CLEAN_IN), cv2.COLOR_BGR2RGB)
BH, BW = ORIG.shape[:2]
CELL, STRIDE = 128, 126
POSES = [-1.0, -0.5, 0.0, 0.5, 1.0]         # frame 2 = rest (the original picture); the game plays 0,1,2,3,4,3,2,1 (ping-pong)
AMP = 5.5                                    # crown displacement in texels at pose 1

def to555(a):
    bayer = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0 - 0.5
    h, w, _ = a.shape
    ys, xs = np.mgrid[0:h, 0:w]
    return to555_abs(a, xs, ys)

def to555_abs(a, xs, ys):
    bayer = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0 - 0.5
    th = bayer[ys % 4, xs % 4]
    out = np.zeros(a.shape[:2], np.uint16)
    for c, sh in enumerate((0, 5, 10)):
        q = np.clip(np.floor(a[:, :, c] / 255.0 * 31.0 + th * 0.9 + 0.5), 0, 31).astype(np.uint16)
        out |= q << sh
    return out | 0x8000

tex_clean = to555(CLEAN.astype(np.float32))
tex_orig = to555(ORIG.astype(np.float32))

# ------------------------------------------------------------ palm sprite masks (7x7 dilated, exclusive)
pm = masks()
palm_mask = {}
taken = np.zeros((BH, BW), bool)
for n in PALMS:
    d = cv2.dilate((pm[n] * 255).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    d &= ~taken
    palm_mask[n] = d
    taken |= d

# decontaminate the 2-px rim of each sprite (colour bleed from the old background -> halo when it sways)
from scipy import ndimage as ndi
core = cv2.erode((taken * 255).astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
_, (iy, ix) = ndi.distance_transform_edt(~core, return_indices=True)
SPR = ORIG.copy()
rim = taken & ~core
SPR[rim] = ORIG[iy[rim], ix[rim]]

# ------------------------------------------------------------ houses (occluders), without the palm pixels
house_polys = {
 "A": ([(80,135),(193,99),(240,135),(241,228),(190,250),(122,262),(100,232),(80,205)], 245),
 "B": ([(1133,112),(1187,86),(1272,128),(1280,150),(1280,262),(1217,258),(1165,232),(1133,215)], 240),
 "Baw": ([(1046,124),(1112,121),(1136,148),(1072,172),(1046,150)], 236),
 "C": ([(55,537),(190,474),(248,520),(262,545),(310,582),(312,660),(285,665),(255,692),(240,690),(215,668),(150,690),(111,685),(55,640)], 690),
 "D": ([(1110,525),(1169,480),(1280,538),(1280,700),(1230,690),(1180,680),(1130,700),(1100,718),(1045,692),(1045,624),(1103,586)], 700),
}
def poly_mask(pts):
    m = Image.new("L", (BW, BH), 0)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    return np.array(m) > 0

def cut(img555, mask, x0, y0):
    c = np.zeros((CELL, CELL), np.uint16)
    h = min(CELL, BH - y0); w = min(CELL, BW - x0)
    c[:h, :w] = img555[y0:y0 + h, x0:x0 + w]
    if h < CELL: c[h:, :w] = img555[BH - 1:BH, x0:x0 + w]
    if w < CELL: c[:, w:] = c[:, w - 1:w]
    if mask is not None:
        mk = np.zeros((CELL, CELL), bool)
        mk[:h, :w] = mask[y0:y0 + h, x0:x0 + w]
        c = np.where(mk, c, 0).astype(np.uint16)
    return c

cells = []
cols = math.ceil((BW - 1) / STRIDE); rows = math.ceil((BH - 1) / STRIDE)
for r in range(rows):
    for c in range(cols):
        cells.append(cut(tex_clean, None, c * STRIDE, r * STRIDE))
n_bg = len(cells)
occ_tab = []
for name, (pts, by) in house_polys.items():
    m = poly_mask(pts) & ~taken
    ys, xs = np.nonzero(m)
    for r in range(ys.min() // STRIDE, ys.max() // STRIDE + 1):
        for c in range(xs.min() // STRIDE, xs.max() // STRIDE + 1):
            x0, y0 = c * STRIDE, r * STRIDE
            if m[y0:y0 + CELL, x0:x0 + CELL].sum() < 4: continue
            occ_tab.append((x0, y0, len(cells), by))
            cells.append(cut(tex_orig, m, x0, y0))
def write_banks(path, cells, extra=b""):
    nb = math.ceil(len(cells) / 32)
    banks = np.zeros((nb, 512, 1024), np.uint16)
    for i, c in enumerate(cells):
        b, k = divmod(i, 32)
        banks[b, (k // 8) * CELL:(k // 8 + 1) * CELL, (k % 8) * CELL:(k % 8 + 1) * CELL] = c
    open(path, "wb").write(struct.pack("<HHHH", nb, 0, 0, 0) + banks.tobytes())
    return nb
nbanks = write_banks(OUT + "/assets/painted.raw", cells)

# ------------------------------------------------------------ palm sway frames
def sway_frame(rgb_w, a_w, X0, Y0, ytop, by, cx, rx, pose, phase_amp=1.0):
    h, w = a_w.shape
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32)
    ya = ys + Y0; xa = xs + X0
    hh = np.clip((by - ya) / max(1.0, by - ytop), 0, 1)
    ds = AMP * pose * hh ** 1.7 + 1.3 * pose * hh ** 2 * np.sin(2 * np.pi * (xa - cx) / (2.0 * rx))
    pre = rgb_w * a_w[:, :, None]
    mapx = (xs - ds).astype(np.float32); mapy = ys.astype(np.float32)
    p2 = np.stack([cv2.remap(pre[:, :, c].astype(np.float32), mapx, mapy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0) for c in range(3)], axis=2)
    a2 = cv2.remap(a_w.astype(np.float32), mapx, mapy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    keep = a2 > 0.5
    rgb2 = np.where(keep[:, :, None], p2 / np.maximum(a2, 1e-3)[:, :, None], 0)
    return rgb2, keep

pal_tab = []      # (x0, y0, ncx, ncy, base_y, first_slot)
pal_cells = []
strip_rows = []
for pi_, (n, (fr, tr, by)) in enumerate(PALMS.items()):
    m = palm_mask[n]
    ys, xs = np.nonzero(m)
    X0 = (xs.min() - 8) & ~1; Y0 = (ys.min() - 3) & ~1
    X1 = xs.max() + 8; Y1 = ys.max() + 3
    X0 = max(X0, 0); Y0 = max(Y0, 0)
    w, h = X1 - X0 + 1, Y1 - Y0 + 1
    ncx = math.ceil(w / STRIDE); ncy = math.ceil(h / STRIDE)
    Wn, Hn = ncx * STRIDE + 2, ncy * STRIDE + 2     # window padded to the cell grid
    rgb_w = np.zeros((Hn, Wn, 3), np.float32); a_w = np.zeros((Hn, Wn), np.float32)
    hh_, ww_ = min(Hn, BH - Y0), min(Wn, BW - X0)
    rgb_w[:hh_, :ww_] = SPR[Y0:Y0 + hh_, X0:X0 + ww_]
    a_w[:hh_, :ww_] = m[Y0:Y0 + hh_, X0:X0 + ww_]
    ytop = ys.min()
    frames = []
    for pose in POSES:
        if pose == 0.0:
            rgb2, keep = rgb_w, a_w > 0.5
        else:
            rgb2, keep = sway_frame(rgb_w, a_w, X0, Y0, ytop, by, fr[0], fr[2], pose)
        yy, xx = np.mgrid[0:Hn, 0:Wn]
        t = to555_abs(rgb2.astype(np.float32), xx + X0, yy + Y0)
        frames.append(np.where(keep, t, 0).astype(np.uint16))
    keepers = []
    for cy in range(ncy):
        for cx_ in range(ncx):
            if any((t[cy * STRIDE:cy * STRIDE + CELL, cx_ * STRIDE:cx_ * STRIDE + CELL] != 0).any() for t in frames):
                keepers.append((cx_, cy))
    first = len(pal_cells)
    for t in frames:
        for (cx_, cy) in keepers:
            c = np.zeros((CELL, CELL), np.uint16)
            sub = t[cy * STRIDE:cy * STRIDE + CELL, cx_ * STRIDE:cx_ * STRIDE + CELL]
            c[:sub.shape[0], :sub.shape[1]] = sub
            pal_cells.append(c)
    pal_tab.append((X0, Y0, by, first, keepers))
    # preview strip
    prev = []
    for t in frames:
        a = np.zeros((Hn, Wn, 3), np.uint8)
        a[:, :, 0] = ((t & 31) << 3); a[:, :, 1] = (((t >> 5) & 31) << 3); a[:, :, 2] = (((t >> 10) & 31) << 3)
        a[t == 0] = (255, 0, 255)
        prev.append(Image.fromarray(a))
    strip_rows.append((n, prev))
nb_pal = write_banks(W_DIR + "/palms_tmp.raw", pal_cells)
# palm file: header, table, then the cells (32 KB each, in slot order)
data = bytearray(struct.pack("<HHHH", len(POSES), len(pal_tab), len(pal_cells), 0))
for (X0, Y0, by, first, keepers) in pal_tab:
    data += struct.pack("<HHHHBB", int(X0), int(Y0), int(by), int(first), len(keepers), 0)
    for (cx_, cy) in keepers: data += struct.pack("<BB", cx_, cy)
for c in pal_cells: data += c.tobytes()
open(OUT + "/assets/painted_palms.raw", "wb").write(data)

# ------------------------------------------------------------ collision
blk = Image.new("L", (1280, 720), 0)
d = ImageDraw.Draw(blk)
rects = [
 (80,218,242,265),(1135,215,1280,262),(1052,200,1068,236),(1118,205,1134,236),
 (55,628,262,698),(236,648,260,694),(298,598,314,665),
 (1100,640,1280,705),(1043,660,1060,692),(1098,690,1112,716),
 (225,180,255,215),(212,222,240,252),(30,620,90,690),(122,665,160,700),(1112,198,1150,235),(1225,205,1280,255),(1180,235,1210,265),(1144,649,1199,695),(1200,678,1235,708),
 (50,285,120,345),(75,470,115,510),(30,0,110,60),(930,285,980,325),(1155,345,1220,395),(880,535,970,595),(1085,330,1115,362),
 (5,262,50,290),(50,275,100,305),(100,290,150,318),(150,300,190,330),
 (850,655,900,685),(900,670,950,700),(950,685,1000,716),(240,500,335,568),(1205,262,1280,320),
]
for n, (fr, tr, by) in PALMS.items():
    rects.append((tr[0] + 4, by - 16, tr[2] - 4, min(719, by + 2)))
rects.append((0, 0, 1280, 26))
for r in rects: d.rectangle(r, fill=255)
a = np.array(blk) > 0
hsv = np.array(Image.fromarray(ORIG).convert("HSV")).astype(int)
hh = hsv[:, :, 0] * 360 / 255; ss = hsv[:, :, 1] / 255; vv = hsv[:, :, 2] / 255
water = (hh > 170) & (hh < 235) & (ss > 0.18) & (vv > 0.30) & (np.arange(720)[:, None] < 150)
from PIL import ImageFilter
wm = Image.fromarray((water * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(9))
a |= np.array(wm) > 0
a[20:135, 595:690] = False; a[0:110, 955:1012] = False
a[0:26, 595:690] = False; a[0:26, 955:1012] = False
cb = np.zeros((90, 160), np.uint8)
for cy in range(90):
    for cx in range(160):
        cb[cy, cx] = 1 if a[cy*8:cy*8+8, cx*8:cx*8+8].mean() > 0.30 else 0
open(OUT + "/assets/painted_col.bin", "wb").write(cb.tobytes())

with open(OUT + "/painted_data.h", "w") as f:
    f.write("/* generated by painted_work/make_painted2.py */\n")
    f.write("#define PB_W %d\n#define PB_H %d\n#define PB_UPS 1\n#define PB_COLS %d\n#define PB_ROWS %d\n#define PB_STRIDE %d\n" % (BW, BH, cols, rows, STRIDE))
    f.write("#define PB_BANKS %d\n#define PB_OCC %d\n" % (nbanks, len(occ_tab)))
    f.write("static const short pb_occ[][4] = {\n")
    for t in occ_tab: f.write("  {%d,%d,%d,%d},\n" % t)
    f.write("};\n")

# debug: palm frame strips
rows_img = []
for n, prev in strip_rows:
    w = sum(p.width for p in prev) + 4 * len(prev); h = max(p.height for p in prev)
    im = Image.new("RGB", (w, h), (30, 30, 30)); x = 0
    for p in prev: im.paste(p, (x, 0)); x += p.width + 4
    rows_img.append((n, im))
sel = [i for i in rows_img if i[0] in ("PB", "PD", "PC1")]
H_ = sum(i[1].height + 4 for i in sel); W_ = max(i[1].width for i in sel)
big = Image.new("RGB", (W_, H_), (30, 30, 30)); y = 0
for n, im in sel: big.paste(im, (0, y)); y += im.height + 4
big.save(W_DIR + "/palm_frames_preview.png")
print("bg cells %d, house occluder cells %d, banks %d | palms %d, frames %d, palm cells %d (%d banks, %.2f MB)" %
      (n_bg, len(occ_tab), nbanks, len(pal_tab), len(POSES), len(pal_cells), nb_pal, len(pal_cells) * 32768 / 1e6))
for t in pal_tab: print(int(t[0]),int(t[1]),t[2],t[3],t[4])
