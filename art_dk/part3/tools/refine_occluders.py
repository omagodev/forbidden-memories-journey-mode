#!/usr/bin/env python3
"""Tighten the hand-drawn occluder polygons of make_cistern.py with GrabCut: seed = polygon (sure fg = polygon eroded 7 px, sure bg = outside polygon dilated 9 px),
then keep the biggest blob, close small holes, simplify with approxPolyDP (eps 1.3 px).  Writes the refined polygons back into masks/cistern_occluders.json
(field "polygon"; the rough one is kept as "polygon_rough") and masks/cistern_occluder_cutouts.png (debug).  Needs opencv (village_roads/.venv)."""
import json, os, cv2, numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = os.path.join(ROOT, "masks", "cistern_occluders.json")
js = json.load(open(J)); im = cv2.imread(os.path.join(ROOT, js["picture"]))
dbg = im.copy()
for o in js["occluders"]:
    rough = np.array(o.get("polygon_rough", o["polygon"]), np.int32)
    pm = np.zeros(im.shape[:2], np.uint8); cv2.fillPoly(pm, [rough], 255)
    sure_fg = cv2.erode(pm, np.ones((15, 15), np.uint8)) > 0
    maybe = cv2.dilate(pm, np.ones((19, 19), np.uint8)) > 0
    mask = np.full(im.shape[:2], cv2.GC_BGD, np.uint8); mask[maybe] = cv2.GC_PR_BGD; mask[pm > 0] = cv2.GC_PR_FGD; mask[sure_fg] = cv2.GC_FGD
    x, y, w, h = cv2.boundingRect(cv2.dilate(pm, np.ones((41, 41), np.uint8)))
    sub = im[y:y + h, x:x + w].copy(); sm = mask[y:y + h, x:x + w].copy()
    bg = np.zeros((1, 65)); fg = np.zeros((1, 65))
    cv2.grabCut(sub, sm, None, bg, fg, 8, cv2.GC_INIT_WITH_MASK)
    r = np.zeros(im.shape[:2], np.uint8); r[y:y + h, x:x + w] = ((sm == cv2.GC_FGD) | (sm == cv2.GC_PR_FGD)) * 255
    r = cv2.morphologyEx(r, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8)); r = cv2.morphologyEx(r, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    r |= (cv2.erode(pm, np.ones((9, 9), np.uint8)))               # never open holes in the core
    r &= (cv2.dilate(pm, np.ones((13, 13), np.uint8)))            # never grow far beyond the rough polygon
    nl, lab, st, _ = cv2.connectedComponentsWithStats(r)
    if nl > 1: r = ((lab == 1 + np.argmax(st[1:, 4])) * 255).astype(np.uint8)
    cs, _ = cv2.findContours(r, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE); c = max(cs, key=cv2.contourArea)
    ap = cv2.approxPolyDP(c, 1.3, True)[:, 0, :]
    o.setdefault("polygon_rough", o["polygon"]); o["polygon"] = ap.tolist(); o["vertices"] = len(ap)
    cv2.polylines(dbg, [ap.reshape(-1, 1, 2)], True, (0, 255, 255), 1)
    print("%-20s rough %2d -> refined %3d vertices, area %d -> %d" % (o["name"], len(rough), len(ap), cv2.contourArea(rough), cv2.contourArea(ap)))
json.dump(js, open(J, "w"), indent=1); cv2.imwrite(os.path.join(ROOT, "masks", "cistern_occluder_cutouts.png"), dbg)
# redraw the overlay with the refined outlines (run make_cistern.py first, then this)
from PIL import Image, ImageDraw
ovp = os.path.join(ROOT, "masks", "cistern_overlay.png"); ov = Image.open(ovp).convert("RGB"); d = ImageDraw.Draw(ov)
for o in js["occluders"]:
    pts = [tuple(p) for p in o["polygon"]]; d.line(pts + [pts[0]], fill=(60, 255, 120), width=2)
ov.save(ovp)
