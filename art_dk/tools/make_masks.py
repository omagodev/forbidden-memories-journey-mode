#!/usr/bin/env python3
"""Hand-guessed walkable/collision masks + occluder lists for the 3 Duelist Kingdom backgrounds.
All coordinates below are in a 1024x576 view of the 1280x720 picture (scaled x1.25 on output).
Outputs per scene (art_dk/masks/): <scene>_walkable_160x90.png (white = walkable, 8-texel cells like the village collision grid),
<scene>_overlay.png (picture + blocked red / warp cyan / occluder outlines yellow), <scene>_occluders.json
Obstacle  = (name, x0,y0,x1,y1)            -> blocks walking (feet box)
Occluder  = (name, polygon[(x,y)...], base_y) -> candidate cutout drawn in front of characters whose feet are above base_y
"""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = 1280 / 1024.0
def R(x0, y0, x1, y1): return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]

SCENES = {}
# ------------------------------------------------------------------ harbor
SCENES["harbor"] = dict(
  pic="backgrounds/dk_harbor_1280x720.jpg",
  blocked_polys=[("sea", [(672,0),(1024,0),(1024,576),(815,576),(800,520),(770,400),(765,330),(745,275),(715,175),(690,100)]),
                 ("ship_hull", [(795,40),(975,260),(960,350),(930,380),(850,370),(800,330),(795,150)])],
  obstacles=[("warehouse_A",143,20,290,178),("warehouse_B",338,20,452,165),("fence_top",285,40,475,80),
    ("palm_TL_trunk",80,105,118,135),("crate_TL",87,148,143,205),("rope_coil",135,170,178,208),("crate_mid",458,120,500,170),
    ("crates_top_right",617,105,680,165),("palm_top_trunk",580,70,615,102),("fence_left",0,80,45,180),("crate_small",250,170,280,200),
    ("palm_L_trunk",28,335,65,385),("warehouse_C",8,368,165,545),("warehouse_D",175,368,305,515),("pots_C",140,465,180,530),
    ("pot_D",305,445,330,485),("pots_D",190,495,255,555),("crates_bottom",262,505,360,565),("crate_BL",3,495,50,550),
    ("palm_BM_trunk",372,485,402,525),("crate_pier",643,335,698,400),("palm_BR_trunk",672,505,708,560),("fence_bottom",592,448,700,500),
    ("quay_posts_upper",712,160,752,270),("quay_posts_lower",730,330,780,520)],
  walk_polys=[("gangplank", R(715,265,845,322))],
  warps=[("to_ship_gangplank_end", R(800,268,845,320))],
  occluders=[
    ("warehouse_A", [(143,22),(290,22),(290,178),(143,178)], 178), ("warehouse_B", [(338,22),(452,22),(452,165),(338,165)], 165),
    ("palm_TL", [(30,0),(150,0),(150,70),(118,135),(80,135),(60,70),(30,60)], 135), ("palm_top", [(545,0),(655,0),(655,60),(612,102),(580,102),(560,60),(545,40)], 102),
    ("warehouse_C", [(8,368),(165,368),(165,545),(8,545)], 545), ("warehouse_D", [(175,368),(305,368),(305,515),(175,515)], 515),
    ("palm_L", [(0,260),(110,260),(110,320),(65,385),(28,385),(20,330),(0,310)], 385), ("palm_BM", [(340,415),(440,415),(440,470),(402,525),(372,525),(350,470)], 525),
    ("palm_BR", [(630,430),(750,430),(750,500),(708,560),(672,560),(640,500)], 560),
    ("crates_pots_front", [(3,495),(50,495),(50,550),(3,550)], 550), ("crates_bottom", [(262,505),(360,505),(360,565),(262,565)], 565),
    ("ship_rigging_sails", [(795,40),(975,40),(975,260),(795,260)], 260)])
# ------------------------------------------------------------------ forest
SCENES["forest"] = dict(
  pic="backgrounds/dk_forest_1280x720.jpg",
  blocked_polys=[("forest_top_band", R(0,0,1024,95)), ("shrine", R(395,65,495,150))],
  obstacles=[("tree1_trunk",20,150,70,215),("tree2_trunk",195,175,255,248),("tree3_trunk",108,75,152,142),("tree4_trunk",345,40,395,110),
    ("tree5_trunk",540,45,590,115),("tree6_trunk",632,150,690,205),("tree7_trunk",665,20,700,90),("tree8_trunk",855,105,890,155),
    ("tree9_trunk",885,205,950,295),("tree10_trunk",950,120,1010,210),("tree11_trunk",925,430,985,520),("tree12_trunk",335,510,415,576),
    ("tree13_trunk",572,505,650,576),("tree14_trunk",20,345,85,430),("canopy_wall_left",0,95,20,576),("canopy_wall_right",1000,95,1024,576),
    ("rocks_L",80,200,155,280),("rock_R1",790,125,845,170),("rock_R2",890,300,935,345),("rock_B",785,495,835,540),("rock_BL",50,445,100,490),
    ("rocks_BL2",230,490,280,550),("stump1",155,390,190,430),("stump2",100,465,118,500),("stump3",710,485,740,520),("stump4",810,175,850,220),
    ("log",735,525,830,576),("signpost",295,205,335,255),("bush1",275,275,335,330),("bush2",340,215,395,255),("bush3",625,270,660,305),
    ("pine",670,245,750,330),("bush4",740,415,800,470),("bush_BL",0,440,60,576),("bush_BR",860,520,1024,576)],
  walk_polys=[("shrine_steps", R(430,148,478,182))],
  warps=[("to_castle_north_east", R(720,96,815,140)), ("to_harbor_south_west", R(120,540,260,576)), ("shrine_steps", R(430,160,478,182))],
  occluders=[
    ("tree1", [(0,30),(115,30),(115,215),(0,215)], 215), ("tree2", [(140,65),(290,65),(290,248),(140,248)], 248), ("tree3", [(85,0),(185,0),(185,142),(85,142)], 142),
    ("tree4", [(290,0),(445,0),(445,110),(290,110)], 110), ("tree5", [(495,0),(635,0),(635,115),(495,115)], 115), ("tree6", [(590,40),(725,40),(725,205),(590,205)], 205),
    ("tree7", [(665,0),(760,0),(760,90),(665,90)], 90), ("tree8", [(815,30),(930,30),(930,155),(815,155)], 155), ("tree9", [(850,120),(985,120),(985,295),(850,295)], 295),
    ("tree10", [(930,30),(1024,30),(1024,210),(930,210)], 210), ("tree11", [(885,315),(1024,315),(1024,520),(885,520)], 520),
    ("tree12", [(285,375),(460,375),(460,576),(285,576)], 576), ("tree13", [(518,380),(700,380),(700,576),(518,576)], 576), ("tree14", [(0,235),(125,235),(125,430),(0,430)], 430),
    ("shrine", [(395,65),(495,65),(495,180),(395,180)], 150)])
# ------------------------------------------------------------------ castle courtyard
SCENES["castle"] = dict(
  pic="backgrounds/dk_castle_1280x720.jpg",
  blocked_polys=[("castle_top_wall", R(0,0,1024,150)), ("left_wall_block", R(0,150,160,576)), ("right_wall_block", R(915,150,1024,576)),
                 ("left_hedge", R(60,225,160,430)), ("right_hedge", R(865,225,960,430)), ("bottom_wall_left", R(0,425,265,576)), ("bottom_wall_right", R(760,425,1024,576))],
  obstacles=[("pedestal_statue_UL",165,95,240,245),("pedestal_statue_UR",785,95,860,245),("pedestal_statue_LL",250,380,340,560),("pedestal_statue_LR",685,380,775,560),
    ("fountain",440,250,585,365),("brazier_UL",310,185,350,250),("brazier_UR",670,185,715,245),("brazier_LL",355,380,395,450),("brazier_LR",630,380,670,450),
    ("hedge_UL",235,155,385,190),("hedge_UR",640,155,785,190),("planter_UC_L",385,140,425,195),("planter_UC_R",600,140,640,195),
    ("planter_L1",155,270,215,330),("planter_L2",150,330,215,405),("planter_R1",805,270,870,330),("planter_R2",805,330,865,405),
    ("hedge_BL",345,465,430,576),("hedge_BR",595,465,685,576),("pillar_gate_L",425,40,470,150),("pillar_gate_R",555,40,600,150)],
  walk_polys=[("door_threshold", R(473,128,548,160))],
  warps=[("to_castle_door", R(473,120,548,150)), ("to_forest_south", R(470,545,555,576))],
  occluders=[
    ("statue_UL", [(165,15),(240,15),(240,245),(165,245)], 245), ("statue_UR", [(785,15),(860,15),(860,245),(785,245)], 245),
    ("statue_LL", [(250,305),(340,305),(340,560),(250,560)], 560), ("statue_LR", [(685,305),(775,305),(775,560),(685,560)], 560),
    ("bottom_wall_left", [(30,425),(265,425),(265,560),(30,560)], 560), ("bottom_wall_right", [(760,425),(990,425),(990,560),(760,560)], 560),
    ("hedge_BL", [(345,465),(430,465),(430,576),(345,576)], 576), ("hedge_BR", [(595,465),(685,465),(685,576),(595,576)], 576),
    ("fountain", [(440,225),(585,225),(585,365),(440,365)], 365),
    ("gate_towers_pillars", [(425,0),(600,0),(600,150),(425,150)], 150)])

def build(name, sc):
    W, H = 1280, 720
    walk = Image.new("L", (W, H), 255); d = ImageDraw.Draw(walk)
    for n, p in sc["blocked_polys"]: d.polygon([(x * S, y * S) for x, y in p], fill=0)
    for n, x0, y0, x1, y1 in sc["obstacles"]: d.rectangle([x0 * S, y0 * S, x1 * S, y1 * S], fill=0)
    for n, p in sc["walk_polys"]: d.polygon([(x * S, y * S) for x, y in p], fill=255)
    a = np.array(walk) > 127
    # 160x90 grid of 8-texel cells; a cell is walkable only if >= 75% walkable
    g = a.reshape(90, 8, 160, 8).mean(axis=(1, 3)) >= 0.75
    Image.fromarray((g * 255).astype(np.uint8)).save(os.path.join(ROOT, "masks", "%s_walkable_160x90.png" % name))
    pic = Image.open(os.path.join(ROOT, sc["pic"])).convert("RGB")
    ov = pic.copy().convert("RGBA")
    red = Image.new("RGBA", (W, H), (255, 0, 0, 0)); rp = red.load()
    for cy in range(90):
        for cx in range(160):
            if not g[cy, cx]:
                for y in range(cy * 8, cy * 8 + 8):
                    for x in range(cx * 8, cx * 8 + 8): rp[x, y] = (255, 0, 0, 110)
    ov = Image.alpha_composite(ov, red); d = ImageDraw.Draw(ov)
    for n, p in sc["warps"]: d.polygon([(x * S, y * S) for x, y in p], outline=(0, 255, 255, 255), fill=(0, 255, 255, 90)); d.text((p[0][0] * S + 3, p[0][1] * S + 3), n, fill=(255, 255, 255, 255))
    for n, p, by in sc["occluders"]:
        pts = [(x * S, y * S) for x, y in p]; d.line(pts + [pts[0]], fill=(255, 230, 0, 255), width=2)
        d.line([(pts[0][0], by * S), (pts[1][0], by * S)], fill=(255, 140, 0, 255), width=2)
    ov.convert("RGB").save(os.path.join(ROOT, "masks", "%s_overlay.png" % name))
    js = dict(scene=name, picture=sc["pic"], size=[1280, 720], note="polygons in 1280x720 picture pixels; base_y = depth line (characters with feet y < base_y are hidden by the cutout)",
      occluders=[dict(name=n, polygon=[[round(x * S), round(y * S)] for x, y in p], base_y=round(by * S)) for n, p, by in sc["occluders"]],
      warps=[dict(name=n, rect=[round(p[0][0] * S), round(p[0][1] * S), round(p[2][0] * S), round(p[2][1] * S)]) for n, p in sc["warps"]],
      obstacles=[dict(name=n, rect=[round(x0 * S), round(y0 * S), round(x1 * S), round(y1 * S)]) for n, x0, y0, x1, y1 in sc["obstacles"]])
    json.dump(js, open(os.path.join(ROOT, "masks", "%s_occluders.json" % name), "w"), indent=1)
    print(name, "walkable cells %d / %d" % (g.sum(), g.size))

if __name__ == "__main__":
    for n, sc in SCENES.items(): build(n, sc)
