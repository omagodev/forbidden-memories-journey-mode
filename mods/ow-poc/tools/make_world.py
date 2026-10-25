#!/usr/bin/env python3
"""Generate assets/world.jwld, the Journey Mode map, from rules in this file.

The map is 64 x 168 tiles: 72 rows in five areas (village and fields, the Nile and the
sand ruins, the Royal City, the throne hall, the tournament island).  Three
layers are written, each W*H bytes, row after row:

  tile   what the ground is (TILE_* below; the engine reads the same numbers)
  deco   a prop standing on the tile: 1..7 a PSX Nature mesh (boulder, sage,
         agave, skull, tumbleweed, hoodoo, barrel cactus), 8..15 a sprite (bush, papyrus,
         oleander, fern palm, grass and flower tufts), 16 jar, 17 signpost, 20 crate
         (sprites), 23 solid and invisible (a Kenney mesh of props.json stands there)
  tint   0..3, how much a tile is shaded green by the plants around it

File layout: "JWLD", u16 width, u16 height, then the three layers.  Next to it, props.json lists
the meshes placed on the map (houses, fences, stalls, rocks): {"props": [{"mesh", "x", "z", "yaw"}]}
with x and z in tiles.

Usage: make_world.py [out.jwld]   (default ../assets/world.jwld)
"""
import json
import struct
import sys
import os

MW, MAINH, CX, RO = 64, 72, 48, 16
ROOM_W, ROOM_H, ROOMS = 32, 24, 8       # chapters 6 to 8: eight rooms below the map, two across
MH = MAINH + ROOMS // 2 * ROOM_H
NX, NY = 14, 12 + RO

(SAND, PATH, WATER, WALL, _4, ARENA, _6, _7, PALM, RUIN, COL, OBEL, PORTAL, PAL,
 DOOR, THRONE, GATE, HOUSE, HOUSE_B, BRIDGE, GRASS) = range(21)
STAND = 23        # deco: an invisible solid prop (a mesh of props.json stands on the tile)


class Rng:
    """The linear congruential generator the map was laid out with."""

    def __init__(self, seed=777):
        self.s = seed

    def __call__(self):
        self.s = (self.s * 1103515245 + 12345) & 0xFFFFFFFF
        return (self.s >> 16) & 0x7FFF


def build():
    rnd = Rng()
    m = [[0] * MW for _ in range(MAINH)]
    d = [[0] * MW for _ in range(MAINH)]
    for y in range(MAINH):
        for x in range(MW):
            m[y][x] = PALM if (x == 0 or y == 0 or x == MW - 1 or y == MAINH - 1) else SAND
    for _ in range(70):
        x = 1 + rnd() % (MW - 2)
        y = 1 + RO + rnd() % (MAINH - 2 - RO)
        m[y][x] = PALM
    for _ in range(14):
        x = 1 + rnd() % (MW - 2)
        y = 1 + rnd() % (RO + 2)
        m[y][x] = PALM
    for x in range(1, MW - 1):                                     # the Nile
        for r in (4, 5, 6):
            m[r + RO][x] = WATER
    for y in range(2, 7 + RO):                                     # ford and ruins road
        m[y][24] = m[y][25] = PATH
    for x in range(1, MW - 1):                                     # the east-west road
        m[20 + RO][x] = m[21 + RO][x] = PATH
    for y in range(7 + RO, MAINH - 1):
        m[y][24] = m[y][25] = PATH
    for x in range(28, 42):                                        # the desert temple
        m[24 + RO][x] = WALL
        m[34 + RO][x] = WALL
    for y in range(24 + RO, 35 + RO):
        m[y][28] = WALL
        m[y][41] = WALL
    m[24 + RO][34] = m[24 + RO][35] = PATH
    for y in range(25 + RO, 34 + RO):
        for x in range(29, 41):
            m[y][x] = PATH
    for y in range(NY - 2, NY + 3):                                # the first duel square
        for x in range(NX - 2, NX + 3):
            m[y][x] = ARENA
    for y in range(NY, 24 + RO):
        for x in range(NX - 3, NX + 4):
            if m[y][x] == PALM:
                m[y][x] = SAND
    # chapter 2: the sand ruins
    for y in range(3, RO + 4):
        for x in range(14, 36):
            if m[y][x] == PALM:
                m[y][x] = SAND
    for y in range(6, 17, 3):
        m[y][21] = COL
        m[y][28] = COL
    m[9][21] = RUIN
    m[15][28] = RUIN
    for x in range(15, 19):
        m[12][x] = RUIN
    for x in range(31, 35):
        m[8][x] = RUIN
    m[13][15] = RUIN
    m[9][34] = RUIN
    m[4][22] = OBEL
    m[4][27] = OBEL
    m[2][23] = COL
    m[2][26] = COL
    m[2][24] = m[2][25] = PORTAL
    # chapter 3: the Royal City, walled, reached through the portal
    for y in range(1, 19):
        for x in range(CX, MW - 1):
            m[y][x] = SAND
    for y in range(20):
        m[y][CX - 1] = PAL
    for x in range(CX - 1, MW):
        m[19][x] = PAL
    for y in range(4, 19):
        for x in range(54, 57):
            m[y][x] = PATH
    for y in range(5, 9):
        for x in range(50, 61):
            if x < 54 or x > 56:
                m[y][x] = ARENA
    for x in range(CX, MW - 1):
        m[3][x] = PAL
    m[3][54] = m[3][55] = m[3][56] = DOOR
    for x in (50, 52, 58, 60):
        m[4][x] = COL
    for y in range(10, 18, 3):
        m[y][52] = COL
        m[y][58] = COL
    m[9][49] = OBEL
    m[9][61] = OBEL
    # chapter 4: the throne hall
    for y in range(23, 42):
        for x in range(CX - 1, MW):
            m[y][x] = PAL if (y == 23 or y == 41 or x == CX - 1 or x == MW - 1) else PATH
    for y in range(25, 28):
        for x in range(53, 58):
            m[y][x] = ARENA
    m[24][54] = m[24][55] = m[24][56] = THRONE
    for y in range(27, 40, 3):
        m[y][51] = COL
        m[y][59] = COL
    # chapter 5: the tournament island
    for y in range(56, 71):
        for x in range(7, 42):
            m[y][x] = WATER if (y == 56 or y == 70 or x <= 11 or x >= 37) else SAND
    for x in range(15, 34):
        m[58][x] = PAL
    m[58][23] = m[58][24] = m[58][25] = GATE
    m[58][14] = m[58][34] = OBEL
    for y in range(62, 66):
        for x in range(18, 31):
            m[y][x] = ARENA
    for x in range(16, 33):
        if x < 23 or x > 25:
            m[61][x] = WALL
            m[66][x] = WALL
    # PSX Nature meshes on open sand
    W = [1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 3, 1, 3, 1, 2, 2]
    for _ in range(130):
        x = 2 + rnd() % (CX - 4)
        y = 2 + rnd() % 53
        if m[y][x] != SAND or d[y][x]:
            continue
        ok = 1
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                t = m[y + dy][x + dx]
                if t in (PATH, ARENA, WATER, PORTAL) or d[y + dy][x + dx]:
                    ok = 0
        if NX - 3 <= x <= NX + 3 and y >= NY - 3:
            ok = 0
        w = W[rnd() & 15]
        rnd()
        if ok:
            d[y][x] = w
    for y in range(62, 66):
        m[y][16] = m[y][32] = WALL
    for y in range(59, 70):
        m[y][24] = m[y][25] = PATH
    return m, d, rnd


def veg_ok(m, d, x, y):
    if x < 2 or y < 2 or x >= MW - 2 or y >= MAINH - 2:
        return False
    if m[y][x] != SAND or d[y][x]:
        return False
    if NX - 3 <= x <= NX + 3 and NY - 3 <= y <= NY + 3:
        return False
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if m[y + dy][x + dx] in (PORTAL, ARENA, GATE, DOOR):
                return False
    return True


def vegetation(m, d, rnd, density=1):
    """Plants: bushes, papyrus along the Nile, clusters, tufts, island gardens."""
    for y in range(MAINH):
        for x in range(MW):
            if d[y][x] == 2:
                d[y][x] = 8 if (x + y) & 1 else 10
    for x in range(2, MW - 2):
        if 22 <= x <= 27:
            continue
        if veg_ok(m, d, x, 3 + RO) and rnd() % 5 < 3:
            d[3 + RO][x] = 9 if rnd() & 3 else 12
        if veg_ok(m, d, x, 7 + RO) and rnd() % 5 < 3:
            d[7 + RO][x] = 9 if rnd() & 3 else 13
    P = [8, 8, 10, 11, 12, 12, 13, 14, 15, 12, 8, 10, 13, 14, 11, 12]
    for i in range(72 * density):
        cx = 3 + rnd() % (CX - 6)
        cy = 4 + RO + rnd() % (55 - 4 - RO)
        n = 6 + rnd() % 6
        if i < 6:
            cx = 3 + rnd() % (CX - 6)
            cy = 3 + rnd() % (RO - 1)
            n = 4
        for _ in range(n):
            x = cx - 2 + rnd() % 5
            y = cy - 2 + rnd() % 5
            if veg_ok(m, d, x, y):
                d[y][x] = (13 if rnd() & 1 else 12) if i < 6 else P[rnd() & 15]
    for y in range(2, 56):
        for x in range(2, CX - 1):
            if m[y][x] == PALM and (rnd() & 1):
                k = rnd() & 3
                ax = x + (k == 0) - (k == 1)
                ay = y + (k == 2) - (k == 3)
                if veg_ok(m, d, ax, ay):
                    d[ay][ax] = 8 + (4 if rnd() & 1 else (0 if rnd() & 1 else 6))
    for _ in range(420 * density):
        x = 2 + rnd() % (CX - 4)
        y = 4 + rnd() % 60
        if veg_ok(m, d, x, y):
            d[y][x] = 12 + (rnd() & 3)
    for _ in range(30):
        x = 13 + rnd() % 23
        y = 59 + rnd() % 10
        if veg_ok(m, d, x, y):
            d[y][x] = 10 if rnd() & 1 else 14 + (rnd() & 1)
    t = [[0] * MW for _ in range(MAINH)]
    for y in range(1, MAINH - 1):
        for x in range(1, MW - 1):
            if m[y][x] == SAND:
                n = 0
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        v = d[y + dy][x + dx]
                        if 8 <= v < 12 or v == 10:
                            n += 2
                        elif v >= 12:
                            n += 1
                t[y][x] = 3 if n >= 6 else 2 if n >= 4 else 1 if n >= 2 else 0
    return t


def desert_props(m, d):
    """Skulls, tumbleweed, hoodoos and barrel cacti on open sand (a rng of its own, so the plants stay put)."""
    rnd = Rng(4242)
    for i in range(260):
        x = 2 + rnd() % (CX - 4)
        y = 4 + rnd() % 64
        if not veg_ok(m, d, x, y):
            continue
        k = rnd() % 20
        d[y][x] = 4 if k < 2 else 5 if k < 9 else 6 if k < 11 else 7


def origin(room):
    """Top left tile of room 0..7 (areas 8 to 15), two rooms to a row."""
    return (room % 2) * ROOM_W, MAINH + (room // 2) * ROOM_H


def put(m, room, x, y, tile, deco=None):
    ox, oy = origin(room)
    m[oy + y][ox + x] = tile
    return ox + x, oy + y


def rooms(m, d, t):
    """The eight rooms of chapters 6 to 8 (32 x 24 tiles each, a wall two tiles thick round a 28 x 20 floor).
    0 Temple Crossroads, 1 Sea, 2 Forest, 3 Mountain, 4 Desert, 5 Meadow, 6 Labyrinth, 7 Final Temple.
    Every room is entered at local (16, 17.5), apart from the Labyrinth and the Final Temple (16, 19.5);
    the temples' way back is the pad at the bottom (15..16, 20..21)."""
    rnd = Rng(9001)
    for r in range(ROOMS):
        ox, oy = origin(r)
        for y in range(ROOM_H):
            for x in range(ROOM_W):
                edge = x < 2 or y < 2 or x >= ROOM_W - 2 or y >= ROOM_H - 2
                m[oy + y][ox + x] = WALL if edge else SAND
                d[oy + y][ox + x] = 0
    # 0 Temple Crossroads: a cross of paths, the well, five pads to the temples, the gate to the Labyrinth
    for x in range(2, 30):
        put(m, 0, x, 12, PATH)
    for y in range(2, 22):
        put(m, 0, 15, y, PATH)
        put(m, 0, 16, y, PATH)
    for px in (3, 9, 15, 21, 26):
        for dx in (0, 1):
            for dy in (0, 1):
                put(m, 0, px + dx, 4 + dy, ARENA)
    put(m, 0, 12, 9, COL)
    put(m, 0, 19, 9, COL)
    for x in range(14, 18):
        put(m, 0, x, 20, GATE)
    # 1 Sea Temple: water on both sides, a wall with the tide door across, the inner sanctuary behind it
    for y in range(2, 22):
        for x in list(range(2, 8)) + list(range(24, 30)):
            put(m, 1, x, y, WATER)
    for x in range(8, 24):
        put(m, 1, x, 9, WALL)
    put(m, 1, 15, 9, DOOR)
    put(m, 1, 16, 9, DOOR)
    # 2 Forest Temple: palms everywhere but on the way
    for _ in range(95):
        x, y = 3 + rnd() % 26, 3 + rnd() % 18
        if abs(x - 15.5) > 2 and not (y > 17 or y < 6 and abs(x - 16) < 4):
            put(m, 2, x, y, PALM)
    # 3 Mountain Temple: boulders and columns up a switchback
    for y in range(6, 20, 5):
        for x in range(3, 29):
            if (y // 5) % 2 and x < 25 or not (y // 5) % 2 and x > 6:
                put(m, 3, x, y, WALL)
    # 4 Desert Temple: half buried columns
    for _ in range(26):
        x, y = 3 + rnd() % 26, 3 + rnd() % 17
        if abs(x - 15.5) > 2:
            put(m, 4, x, y, COL if rnd() & 1 else RUIN)
    # 6 Labyrinth: four chambers, doors between them, the dark stairs at the top
    for y in (16, 12, 8, 4):
        for x in range(2, 30):
            put(m, 6, x, y, WALL)
    for y in (16, 12, 8):
        put(m, 6, 15, y, DOOR)
        put(m, 6, 16, y, DOOR)
    put(m, 6, 15, 4, THRONE)
    put(m, 6, 16, 4, THRONE)
    # 7 Final Temple: a hall of shadows behind a mist wall, the stairs to Nitemare
    for y in (12, 6):
        for x in range(2, 30):
            put(m, 7, x, y, WALL)
    for x in range(14, 18):
        put(m, 7, x, 12, GATE)
        put(m, 7, x, 6, THRONE)
    for r in range(ROOMS):
        ox, oy = origin(r)
        # plants and props by room
        for _ in range({0: 30, 1: 26, 2: 40, 3: 26, 4: 28, 5: 90, 6: 0, 7: 10}[r]):
            x, y = 3 + rnd() % 26, 3 + rnd() % 18
            if m[oy + y][ox + x] != SAND or abs(x - 15.5) < 2.2 or (r in (1, 3, 6, 7) and y > 17):
                continue
            if r == 1:
                d[oy + y][ox + x] = 9 if x < 12 or x > 20 else 12
            elif r == 3:
                d[oy + y][ox + x] = 1 if rnd() & 1 else 3
            elif r == 4:
                d[oy + y][ox + x] = (4, 5, 5, 6, 7)[rnd() % 5]
            elif r == 5:
                d[oy + y][ox + x] = (12, 13, 12, 13, 14, 15, 8)[rnd() % 7]
            elif r == 7:
                d[oy + y][ox + x] = 6
            else:
                d[oy + y][ox + x] = (8, 10, 12, 13)[rnd() % 4]
    for r in range(ROOMS):                   # shade tiles near plants as in the map
        ox, oy = origin(r)
        for y in range(1, ROOM_H - 1):
            for x in range(1, ROOM_W - 1):
                if m[oy + y][ox + x] == SAND:
                    n = sum(1 for dy in (-1, 0, 1) for dx in (-1, 0, 1) if d[oy + y + dy][ox + x + dx] >= 8)
                    t[oy + y][ox + x] = 2 if n >= 3 else 1 if n >= 1 else 0


def village(m, d, props):
    """Houses, a market, fences and rocks in the village and a bridge over the Nile.  Houses are
    meshes baked by bake_kenney.py (a: 3x2 tiles, b: 5x2, c: 3x2 with a gable roof, d: 5x3); their tiles are
    solid and the mesh stands on them, door toward the camera."""
    size = {"a": (3, 2), "b": (5, 2), "c": (3, 2), "d": (5, 2)}
    houses = [("a", 3, 24), ("b", 8, 24), ("c", 18, 24), ("d", 28, 23), ("a", 2, 39), ("b", 8, 40), ("c", 28, 38),
              ("d", 13, 41), ("a", 20, 44), ("b", 3, 46), ("a", 14, 49)]
    for k, hx, hz in houses:
        w, h = size[k]
        for y in range(hz - 1, hz + h + 2):
            for x in range(hx - 1, hx + w + 1):
                if m[y][x] == PALM or d[y][x]:
                    m[y][x] = SAND
                d[y][x] = 0
        for y in range(hz, hz + h):
            for x in range(hx, hx + w):
                m[y][x] = HOUSE
        props.append({"mesh": "k_house_" + k, "x": hx + w / 2.0, "z": hz + h / 2.0, "yaw": 0})
    for y in range(20, 54):                                       # the kit's trees stand in the village, not palms
        for x in range(MW):
            if m[y][x] == PALM:
                m[y][x] = SAND
                if (x + y) % 4 == 0:
                    d[y][x] = STAND
                    props.append({"mesh": "k_tree_round" if (x * 3 + y) % 4 else "k_tree_pine", "x": x + 0.5, "z": y + 0.5, "yaw": x + y})
    for y in range(4 + RO, 7 + RO):                               # the bridge: planks and rails
        m[y][24] = m[y][25] = BRIDGE
        props.append({"mesh": "k_fence_v", "x": 24.5, "z": y + 0.5, "yaw": 3.1416})
        props.append({"mesh": "k_fence_v", "x": 25.5, "z": y + 0.5, "yaw": 0})
    for x, z, k in ((23, 20, "large"), (26, 20, "small"), (23, 22, "wide"), (26, 22, "large"), (20, 20, "wide"),
                    (13, 20, "large"), (9, 22, "wide"), (30, 22, "large"), (34, 20, "wide")):
        props.append({"mesh": "k_rock_" + k, "x": x + 0.5, "z": z + 0.5, "yaw": (x * 37 % 7) * 0.9})
    patches = [(1, 27, 4, 3), (5, 30, 5, 3), (17, 27, 4, 4), (20, 33, 4, 3), (2, 33, 4, 3), (10, 27, 2, 2), (19, 38, 5, 3), (9, 44, 4, 3)]
    for gx, gz, w, h in patches:
        for y in range(gz, gz + h):
            for x in range(gx, gx + w):
                if m[y][x] == SAND and not d[y][x]:
                    m[y][x] = GRASS
    def stand(x, z, mesh, yaw=0.0, at=0.5):
        if m[z][x] in (SAND, GRASS) and not d[z][x]:
            d[z][x] = STAND
            props.append({"mesh": mesh, "x": x + at, "z": z + at, "yaw": yaw})
    for x in range(1, 7):                                           # fences round yards
        stand(x, 35, "k_fence_h")
    for x in range(9, 12):
        stand(x, 35, "k_fence_h")
    for z in range(40, 44):
        stand(7, z, "k_fence_v", 0)
    for x in range(21, 24):
        stand(x, 43, "k_fence_h")
    for i, (x, z) in enumerate(((1, 22), (1, 29), (6, 30), (13, 27), (15, 34), (22, 30), (31, 27), (30, 33), (33, 41),
                                (11, 38), (25, 40), (17, 36), (5, 44), (22, 47), (34, 24), (16, 22))[::2]):
        stand(x, z, "k_tree_round" if i % 3 else "k_tree_pine", i * 0.7)
    for y in range(24, 54):                                         # palm sprites give way to the kit's trees
        for x in range(MW):
            if d[y][x] in (8, 10, 11):
                d[y][x] = 0
                if (x * 3 + y * 5) % 6 == 0:
                    stand(x, y, "k_tree_round" if (x + y) % 3 else "k_tree_pine", x + y)
    stand(6, 33, "k_cart", 0.4)
    stand(20, 34, "k_stall_red")
    stand(8, 34, "k_stall_green")
    stand(11, 32, "k_lantern")
    stand(26, 35, "k_lantern")
    stand(27, 33, "k_banner", 0.0)
    for x, z in ((26, 31), (23, 38)):
        stand(x, z, "k_lantern")
    for (x, z, k) in ((5, 26, 16), (9, 26, 16), (19, 26, 20), (21, 26, 16), (3, 41, 16), (8, 42, 20), (14, 45, 16),
                      (29, 28, 17), (26, 26, 17), (25, 34, 17)):
        if m[z][x] in (SAND, GRASS) and not d[z][x]:
            d[z][x] = k


def kenney_rocks(m, d, props):
    """The PSX Nature boulders (deco 1), hoodoos (6) and barrel cacti (7) become Kenney rocks that stand on the same
    solid tiles; the other PSX meshes (sage, agave, skull, tumbleweed) are left out."""
    rock = {1: "k_rock_large", 6: "k_rock_wide", 7: "k_rock_small"}
    for y in range(MH):
        for x in range(MW):
            v = d[y][x]
            if v in rock and (x * 7 + y * 13 + x * y) % 3:             # one rock of three: the kit's are denser than the PSX ones
                d[y][x] = 0
            elif v in rock:
                d[y][x] = STAND
                props.append({"mesh": rock[v], "x": x + 0.5, "z": y + 0.5, "yaw": ((x * 7 + y * 13) % 8) * 0.8})
            elif 1 <= v <= 7:
                d[y][x] = 0


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "assets", "world.jwld")
    m, d, rnd = build()
    props = []
    village(m, d, props)
    t = vegetation(m, d, rnd)
    desert_props(m, d)
    for layer in (m, d, t):
        layer.extend([[0] * MW for _ in range(MH - MAINH)])
    rooms(m, d, t)
    kenney_rocks(m, d, props)
    blob = b"JWLD" + struct.pack("<HH", MW, MH)
    for layer in (m, d, t):
        blob += bytes(v for row in layer for v in row)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "wb").write(blob)
    json.dump({"props": props}, open(os.path.join(os.path.dirname(out), "props.json"), "w"))
    n = sum(1 for row in d for v in row if v)
    print("world.jwld: %d bytes, %d props" % (len(blob), n))


if __name__ == "__main__":
    main()
