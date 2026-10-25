#!/usr/bin/env python3
"""Old Cistern: walkable mask, occluders (traced as column silhouettes: capital / shaft / plinth, not boxes), warps, anchors, torch list.
Coordinates are written in a 1024x576 view of the 1280x720 picture (x1.25 on output).  Same output formats as ../../tools/make_masks.py:
 masks/cistern_walkable_160x90.png (white = walkable, 8-texel cells, >=75% free), masks/cistern_walkable_320x180.png (4-texel cells, tighter),
 masks/cistern_overlay.png, masks/cistern_occluders.json"""
import json, os
import numpy as np
from PIL import Image, ImageDraw
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); S = 1.25
def R(x0, y0, x1, y1): return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
def column(cx, ytop, cw, sw, yb, ybase, bw, bcx):
    """round column silhouette: capital (wide, 42 high), shaft, flared plinth"""
    cap = 44
    return [(cx - cw / 2 + 5, ytop + 3), (cx - cw / 2 + 12, ytop), (cx + cw / 2 - 12, ytop), (cx + cw / 2 - 5, ytop + 3), (cx + cw / 2, ytop + 12), (cx + cw / 2, ytop + cap - 4),
            (cx + sw / 2, ytop + cap), (cx + sw / 2, yb), (bcx + bw / 2 - 4, yb + 6), (bcx + bw / 2, yb + 14), (bcx + bw / 2, ybase - 4), (bcx + bw / 2 - 8, ybase), (bcx - bw / 2 + 8, ybase),
            (bcx - bw / 2, ybase - 4), (bcx - bw / 2, yb + 14), (bcx - bw / 2 + 4, yb + 6), (cx - sw / 2, yb), (cx - sw / 2, ytop + cap), (cx - cw / 2, ytop + cap - 4), (cx - cw / 2, ytop + 12)]
COLS = {"col_back_left": column(163, 28, 68, 50, 188, 228, 66, 172), "col_back_right": column(868, 28, 58, 46, 190, 230, 76, 850),
        "col_left": column(35, 200, 62, 48, 360, 412, 82, 70), "col_right": column(990, 200, 62, 48, 360, 412, 84, 960),
        "col_front_left": column(207, 342, 72, 54, 495, 532, 90, 222), "col_front_right": column(817, 342, 72, 54, 495, 532, 90, 800)}
# feet footprints (what actually blocks walking): the plinth, not the whole column
FOOT = {"col_back_left": R(140, 198, 208, 230), "col_back_right": R(820, 198, 888, 232), "col_left": R(40, 372, 108, 414), "col_right": R(918, 372, 988, 414),
        "col_front_left": R(182, 497, 266, 534), "col_front_right": R(756, 497, 852, 536)}
OBST = [("jar_back_left", R(208, 144, 240, 186)), ("jar_back_mid", R(310, 152, 340, 182)), ("jar_right_1", R(925, 280, 950, 325)), ("jars_bottom_right", R(935, 427, 990, 497)),
        ("rubble_back_right", R(782, 165, 816, 202)), ("rubble_left", R(30, 420, 112, 482)), ("bridge_rail_left", R(440, 447, 462, 528)), ("bridge_rail_right", R(562, 447, 582, 528)),
        ("dais_rim_top", R(0, 0, 0, 0))]
FLOOR = [(172, 168), (462, 168), (466, 12), (556, 12), (560, 168), (640, 172), (745, 180), (815, 200), (905, 235), (935, 285), (945, 330), (950, 390), (958, 440), (975, 462),
         (60, 462), (50, 440), (58, 380), (72, 320), (100, 262), (112, 232), (150, 205)]
ADD = [("bridge_slab", R(463, 455, 561, 530)), ("ledge_below_channel", R(268, 530, 757, 562))]
WARPS = [("hatch_ladder_up", R(470, 14, 552, 62)), ("ghost_spot", R(488, 268, 532, 314)), ("wall_glyph_spot", R(270, 150, 350, 172))]
ANCHORS = {"spawn_stairs": (510, 178), "exit_stairs": (511, 40), "bakura_spot": (510, 292), "wall_glyph": (310, 160)}
TORCHES = [(217, 100), (413, 100), (607, 100), (772, 100), (97, 165), (924, 165), (20, 375), (1000, 375)]
OTHER_OCC = [("jar_back_left", R(206, 140, 242, 188), 186), ("jar_back_mid", R(308, 148, 342, 184), 182), ("jar_right_1", R(922, 276, 952, 328), 325), ("jars_bottom_right", R(932, 422, 992, 500), 497),
             ("bridge_rail_left", R(438, 445, 464, 530), 528), ("bridge_rail_right", R(560, 445, 584, 530), 528)]

def main():
    W, H = 1280, 720
    walk = Image.new("L", (W, H), 0); d = ImageDraw.Draw(walk)
    sc = lambda p: [(x * S, y * S) for x, y in p]
    d.polygon(sc(FLOOR), fill=255)
    for n, p in ADD: d.polygon(sc(p), fill=255)
    for p in FOOT.values(): d.polygon(sc(p), fill=0)
    for n, p in OBST: d.polygon(sc(p), fill=0)
    # stairs: steps are walkable but the two side piers are not
    d.rectangle([440 * S, 10 * S, 464 * S, 170 * S], fill=0); d.rectangle([555 * S, 10 * S, 580 * S, 170 * S], fill=0)
    # bridge side posts again (floor poly covers them)
    d.polygon(sc(R(440, 447, 462, 528)), fill=0); d.polygon(sc(R(562, 447, 582, 528)), fill=0)
    a = np.array(walk) > 127
    g8 = a.reshape(90, 8, 160, 8).mean(axis=(1, 3)) >= 0.75
    g4 = a.reshape(180, 4, 320, 4).mean(axis=(1, 3)) >= 0.80
    Image.fromarray((g8 * 255).astype(np.uint8)).save(os.path.join(ROOT, "masks", "cistern_walkable_160x90.png"))
    Image.fromarray((g4 * 255).astype(np.uint8)).save(os.path.join(ROOT, "masks", "cistern_walkable_320x180.png"))
    occ = [(n, p, ybase) for (n, p), ybase in zip(COLS.items(), [228, 230, 412, 412, 532, 532])] + [(n, p, b) for n, p, b in OTHER_OCC]
    pic = Image.open(os.path.join(ROOT, "backgrounds", "dk_cistern_1280x720.jpg")).convert("RGBA")
    red = np.zeros((H, W, 4), np.uint8)
    red[~np.kron(g8, np.ones((8, 8), bool))] = (255, 0, 0, 100)
    ov = Image.alpha_composite(pic, Image.fromarray(red)); d = ImageDraw.Draw(ov)
    for n, p in WARPS: d.polygon(sc(p), outline=(0, 255, 255, 255), fill=(0, 255, 255, 70)); d.text((p[0][0] * S + 3, p[0][1] * S + 3), n, fill=(255, 255, 255, 255))
    for n, p, by in occ:
        pts = sc(p); d.line(pts + [pts[0]], fill=(255, 230, 0, 255), width=2)
        xs = [q[0] for q in pts]; d.line([(min(xs), by * S), (max(xs), by * S)], fill=(255, 140, 0, 255), width=2)
    for n, (x, y) in ANCHORS.items(): d.ellipse([x * S - 5, y * S - 5, x * S + 5, y * S + 5], outline=(255, 0, 255, 255), width=2); d.text((x * S + 8, y * S - 6), n, fill=(255, 0, 255, 255))
    for x, y in TORCHES: d.ellipse([x * S - 4, y * S - 4, x * S + 4, y * S + 4], outline=(255, 160, 0, 255), width=2)
    ov.convert("RGB").save(os.path.join(ROOT, "masks", "cistern_overlay.png"))
    js = dict(scene="cistern", picture="backgrounds/dk_cistern_1280x720.jpg", size=[W, H],
              note="polygons in 1280x720 picture pixels; base_y = depth line (a character whose feet y < base_y is hidden by the cutout). Columns are traced as capital/shaft/plinth silhouettes (20 vertices); the collision footprint is only the plinth (see obstacles).",
              occluders=[dict(name=n, polygon=[[round(x * S), round(y * S)] for x, y in p], base_y=round(by * S)) for n, p, by in occ],
              warps=[dict(name=n, rect=[round(p[0][0] * S), round(p[0][1] * S), round(p[2][0] * S), round(p[2][1] * S)]) for n, p in WARPS],
              anchors={n: [round(x * S), round(y * S)] for n, (x, y) in ANCHORS.items()},
              story_anchor_map={"spawn_stairs": "bottom of the stone steps", "exit_stairs": "top of the stairs (hatch ladder up -> village.mini_pyramid_hatch)", "bakura_spot": "centre dais", "wall_glyph": "carved wall panel upper left (observer glyph)"},
              torches=[[round(x * S), round(y * S)] for x, y in TORCHES],
              obstacles=[dict(name=n, rect=[round(p[0][0] * S), round(p[0][1] * S), round(p[2][0] * S), round(p[2][1] * S)]) for n, p in OBST if p[0] != p[2]] +
                        [dict(name=n + "_plinth", rect=[round(p[0][0] * S), round(p[0][1] * S), round(p[2][0] * S), round(p[2][1] * S)]) for n, p in FOOT.items()],
              water_channel=[[round(265 * S), round(478 * S), round(440 * S), round(528 * S)], [round(582 * S), round(478 * S), round(757 * S), round(528 * S)]])
    json.dump(js, open(os.path.join(ROOT, "masks", "cistern_occluders.json"), "w"), indent=1)
    print("walkable cells 8px: %d/%d, 4px: %d/%d" % (g8.sum(), g8.size, g4.sum(), g4.size))
if __name__ == "__main__": main()
