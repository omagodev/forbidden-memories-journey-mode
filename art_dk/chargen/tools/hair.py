from rig import *
from poses import pose
# hair slots: 1 hair colour, 2 hood main (= outfit main), 3 hood trim (= outfit secondary), 4 skin (forehead shadow)
SKULL = {"down": (24.0, 16.0, 9.6, 9.0), "up": (24.0, 16.0, 9.6, 9.0), "left": (23.0, 16.0, 9.3, 9.0)}
TIE = (226, 64, 82)

def ys_below(bounds):
    """bounds: list of (x0, x1, y): mask of texels whose centre is ABOVE y in the x range (columns x0..x1-1)"""
    m = np.zeros((H, W), bool)
    for x0, x1, y in bounds:
        for x in range(int(x0), int(x1)):
            m[:int(round(y)), x] = True
    return m

def mirror_bounds(b): return [(48 - x1, 48 - x0, y) for x0, x1, y in b]

def finish_hair(c, m, base="base", fringe_y=None, streaks=(), shadow_band=True, skull=None):
    """shade a hair mask: highlight top-left, shade bottom/right, darker under the fringe, strand highlights"""
    c.bevel(m, 1, base, "hi", "sh")
    up = shift(m, 0, 1)
    # under-edge (texels with empty below): 'sh'
    c.tone_at(m & ~shift(m, 0, -1), "sh")
    # inner dark band: a row above the lowest edge
    c.tone_at(m & ~shift(m, 0, -2) & shift(m, 0, -1), "mid")
    for (p0, p1) in streaks:
        c.paint(line(p0, p1, 0.9).mask() & m, 1, "hi")
    if skull is not None:
        # forehead / face shade under the hair (skin slot)
        below = shift(m, 0, -1) & False
        s1 = shift(m, 0, 1) & ~m & skull
        c.paint(s1, 4, "sh")

def skull_mask(d):
    cx, cy, rx, ry = SKULL[d]; return S().ell(cx, cy, rx, ry).mask()

# ------------------------------------------------------------------ short
def short(d, f):
    p = pose(d, f); c = Cell(); sk = skull_mask(d)
    if d == "down":
        mass = S().ell(24.0, 13.6, 11.0, 9.0).mask()
        fr = [(0, 15, 21), (15, 17, 19), (17, 20, 15.4), (20, 23, 14.2), (23, 26, 15.2), (26, 29, 14.4), (29, 32, 16.8), (32, 34, 19), (34, 48, 21)]
        m = mass & ys_below(fr)
        m |= S().rect(13.1, 11.0, 15.4, 20.0).mask() | S().rect(32.6, 11.0, 34.9, 20.0).mask()
        m &= ~S().rect(0, 22, 48, 62).mask()
        finish_hair(c, m, streaks=[((19, 9.5), (17, 13)), ((24, 8.0), (22.5, 12)), ((28, 9.0), (30, 12.4))], skull=sk)
    elif d == "up":
        mass = S().ell(24.0, 14.4, 11.0, 10.2).mask() | S().rect(14.2, 14.0, 33.8, 22.6).mask()
        m = mass & ~S().rect(0, 23, 48, 62).mask()
        m &= ~(S().poly([(0, 20), (15, 23.2), (15, 40), (0, 40)]).mask() | S().poly([(48, 20), (33, 23.2), (33, 40), (48, 40)]).mask())
        finish_hair(c, m, streaks=[((19, 9.5), (17, 14)), ((24, 8.0), (24, 16)), ((29, 9.5), (31, 15)), ((21, 18), (19, 21))], skull=None)
    else:
        mass = S().ell(23.6, 13.6, 10.8, 9.0).mask()
        fr = [(0, 14, 17), (14, 16, 15.2), (16, 18, 13.8), (18, 21, 13.2), (21, 28, 15.0), (28, 34, 21.4), (34, 48, 21.4)]
        m = mass & ys_below(fr)
        m |= S().rect(28.4, 12.0, 33.8, 21.6).mask() & S().ell(25.0, 14.0, 9.6, 9.0).mask()
        m &= ~S().rect(0, 22.2, 48, 62).mask()
        finish_hair(c, m, streaks=[((19, 8.5), (17, 12)), ((25, 8.0), (30, 12.5)), ((30, 15), (30.5, 19.5))], skull=sk)
    return c

# ------------------------------------------------------------------ spiky
def spiky(d, f):
    p = pose(d, f); c = Cell(); sk = skull_mask(d)
    if d == "down":
        mass = S().ell(24.0, 13.6, 10.8, 8.4).mask()
        fr = [(0, 15, 20.5), (15, 17, 18.5), (17, 48, 14.6)]
        m = mass & ys_below(fr)
        m |= S().rect(13.2, 12.0, 15.4, 19.8).mask() | S().rect(32.6, 12.0, 34.8, 19.8).mask()
        # fringe spikes (down) and crown spikes (up)
        for x0 in (17.0, 20.6, 24.2, 27.8):
            m |= S().poly([(x0, 12.0), (x0 + 3.6, 12.0), (x0 + 1.9 + (0.6 if x0 > 22 else -0.6), 17.2 + (0.4 if x0 in (20.6, 24.2) else -0.4))]).mask()
        m |= S().poly([(29.6, 12.5), (33.0, 12.5), (32.6, 18.4)]).mask()
        for x0, tip, h in ((14.0, (12.0, 3.4), 8.0), (18.0, (17.4, 2.8), 7.0), (22.2, (23.8, 2.0), 6.0), (26.6, (30.2, 2.8), 7.0), (30.0, (35.6, 4.0), 8.0)):
            m |= S().poly([(x0, 9.6), (x0 + 4.8, 9.6), (tip[0] + 1.0 + (0.8 if tip[0] > 22 else 0), tip[1] + 0.0)]).mask() if False else S().poly([(x0, 10.5), (x0 + 5.2, 10.5), (tip[0] + 2.0, tip[1])]).mask()
        m &= ~rows(23, 62)
        finish_hair(c, m, streaks=[((18, 9.5), (17, 12.5)), ((25, 8.5), (24.4, 11)), ((31, 9.5), (31, 12))], skull=sk)
    elif d == "up":
        mass = S().ell(24.0, 14.0, 11.0, 9.6).mask() | S().rect(14.4, 14.0, 33.6, 21.0).mask()
        m = mass & ~rows(22, 62)
        for x0, tip in ((14.0, (12.0, 3.4)), (18.0, (17.4, 2.8)), (22.2, (23.8, 2.0)), (26.6, (30.2, 2.8)), (30.0, (35.6, 4.0))):
            m |= S().poly([(x0, 10.5), (x0 + 5.2, 10.5), (tip[0] + 2.0, tip[1])]).mask()
        for x0 in (15.4, 19.6, 23.8, 28.0):   # nape spikes pointing down
            m |= S().poly([(x0, 19.0), (x0 + 3.6, 19.0), (x0 + 1.8 + (0.5 if x0 > 22 else -0.5), 23.8)]).mask()
        finish_hair(c, m, streaks=[((19, 9.5), (17, 14)), ((25, 8.0), (25, 15)), ((30, 10), (31, 15))], skull=None)
    else:
        mass = S().ell(23.6, 13.4, 10.6, 8.6).mask()
        fr = [(0, 14, 17.6), (14, 16, 16.0), (16, 20, 13.8), (20, 28, 15.0), (28, 34, 21.0), (34, 48, 21.0)]
        m = mass & ys_below(fr)
        m |= S().rect(28.4, 12.0, 33.6, 21.0).mask() & S().ell(25.0, 14.0, 9.6, 9.0).mask()
        for pts in ([(14.6, 13.0), (18.6, 13.0), (13.6, 6.6)], [(17.0, 10.0), (22.0, 10.0), (19.4, 2.4)], [(21.0, 9.8), (26.8, 9.8), (26.4, 2.0)],
                    [(25.6, 10.0), (31.0, 10.0), (33.4, 2.6)], [(29.0, 11.6), (34.2, 14.0), (38.0, 9.0)], [(30.6, 16.0), (34.0, 19.6), (38.8, 17.0)],
                    [(13.0, 13.0), (17.6, 12.4), (12.4, 18.4)]):
            m |= S().poly(pts).mask()
        m &= ~rows(23, 62)
        finish_hair(c, m, streaks=[((19, 9), (19.4, 4)), ((25, 8), (26, 3.4)), ((30, 12), (33, 9))], skull=sk)
    return c

# ------------------------------------------------------------------ long
def long_(d, f):
    p = pose(d, f); c = Cell(); sk = skull_mask(d)
    sway = {0: 0, 1: 1, 2: 0, 3: -1, 4: 0}[f]
    if d == "down":
        top = short("down", f)
        mass = S().ell(24.0, 13.6, 11.2, 9.2).mask()
        fr = [(0, 15, 22), (15, 17, 19), (17, 20, 15.6), (20, 23, 14.0), (23, 26, 14.8), (26, 29, 14.2), (29, 32, 17.0), (32, 34, 19), (34, 48, 22)]
        m = mass & ys_below(fr)
        # long curtains over the shoulders
        for xs, sgn in (((12.4, 16.2), -1), ((31.8, 35.6), 1)):
            m |= S().poly([(xs[0], 12.0), (xs[1], 12.0), (xs[1] + sgn * 0.2, 31.0 + sway * sgn * 0.0), (xs[0] + 0.6 * sgn * -1 + 0.6, 34.0 - (0.8 if sgn * sway > 0 else 0)), (xs[0], 31.0)]).mask()
        m &= ~(rows(22, 62) & cols(16.2, 31.8))
        finish_hair(c, m, streaks=[((19, 9.5), (17, 13)), ((24, 8.0), (22.5, 12)), ((14, 18), (14.4, 30)), ((34, 18), (33.6, 30))], skull=sk)
    elif d == "up":
        mass = S().ell(24.0, 14.4, 11.2, 10.2).mask()
        m = mass | S().poly([(12.6, 15.0), (35.4, 15.0), (36.0 + sway * 0.6, 34.0), (24.0, 37.6), (12.0 + sway * 0.6, 34.0)]).mask()
        finish_hair(c, m, streaks=[((19, 9.5), (17, 14)), ((24, 8.0), (24, 16)), ((29, 9.5), (31, 15)), ((17, 22), (16, 32)), ((24, 24), (24, 35)), ((31, 22), (32, 32))], skull=None)
    else:
        mass = S().ell(23.6, 13.6, 10.8, 9.0).mask()
        fr = [(0, 14, 17), (14, 16, 15.2), (16, 18, 13.8), (18, 21, 13.2), (21, 28, 15.0), (28, 34, 22), (34, 48, 22)]
        m = mass & ys_below(fr)
        back = S().poly([(26.0, 13.0), (34.0, 14.0), (36.4 + sway, 33.0), (31.0, 36.4), (25.6, 33.0)]).mask()
        m |= back
        finish_hair(c, m, streaks=[((19, 8.5), (17, 12)), ((25, 8.0), (30, 12.5)), ((31, 18), (32, 30))], skull=sk)
    return c

# ------------------------------------------------------------------ ponytail
def ponytail(d, f):
    base = short(d, f)
    c = base; sway = {0: 0, 1: 1, 2: 0, 3: -1, 4: 0}[f]
    if d == "down":
        # the tail pokes out behind the right of the head, with the tie
        m = S().cap((33.0, 12.4), (36.2 + sway * 0.6, 22.0), 1.9, 1.5).mask()
        c.bevel(m, 1, "base", "hi", "sh")
        c.fixed(S().rect(32.6, 11.4, 35.0, 13.4).mask(), TIE)
    elif d == "up":
        m = S().cap((24.0, 10.5), (24.0 + sway * 1.0, 24.0), 2.6, 2.0).mask() | S().poly([(21.8, 18.0), (26.2, 18.0), (25.4 + sway, 31.6), (22.6 + sway, 31.6)]).mask()
        c.bevel(m, 1, "base", "hi", "sh")
        c.paint(line((24.0, 14.0), (24.0 + sway * 0.5, 29.0), 0.9).mask() & m, 1, "mid")
        c.fixed(S().rect(21.8, 12.6, 26.2, 14.6).mask(), TIE)
    else:
        m = S().cap((30.0, 11.8), (34.6 + sway, 20.0), 2.4, 1.2).mask() | S().cap((34.6 + sway, 20.0), (34.0 + sway * 1.5, 28.4), 1.6, 0.8).mask()
        c.bevel(m, 1, "base", "hi", "sh")
        c.paint(line((31.0, 14.0), (34.0 + sway, 26.0), 0.9).mask() & m, 1, "mid")
        c.fixed(S().rect(29.0, 9.6, 31.4, 13.4).mask(), TIE)
    return c

# ------------------------------------------------------------------ bob
def bob(d, f):
    p = pose(d, f); c = Cell(); sk = skull_mask(d)
    if d == "down":
        mass = S().ell(24.0, 14.6, 11.4, 10.0).mask()
        fr = [(0, 15, 25), (15, 48, 15.2), (15, 17, 25)]
        m = mass & ys_below([(0, 14, 28), (14, 16, 24), (16, 32, 15.0), (32, 34, 24), (34, 48, 28)])
        m |= S().poly([(12.6, 13.0), (16.2, 13.0), (16.4, 24.0), (14.6, 26.4), (12.4, 25.0)]).mask() | S().poly([(31.8, 13.0), (35.4, 13.0), (35.6, 25.0), (33.4, 26.4), (31.6, 24.0)]).mask()
        finish_hair(c, m, streaks=[((19, 9.5), (17, 13)), ((24, 8.0), (22.5, 12)), ((14, 17), (14.2, 23)), ((34, 17), (33.8, 23))], skull=sk)
    elif d == "up":
        m = S().ell(24.0, 14.6, 11.4, 10.0).mask() | S().poly([(12.6, 14.0), (35.4, 14.0), (35.0, 25.0), (31.0, 27.4), (17.0, 27.4), (13.0, 25.0)]).mask()
        finish_hair(c, m, streaks=[((19, 9.5), (17, 14)), ((24, 8.0), (24, 16)), ((29, 9.5), (31, 15)), ((18, 20), (17, 25)), ((30, 20), (31, 25))], skull=None)
    else:
        mass = S().ell(23.6, 14.0, 11.0, 9.6).mask()
        fr = [(0, 14, 17), (14, 16, 15.2), (16, 18, 13.8), (18, 21, 13.2), (21, 27, 15.0), (27, 34, 27.4), (34, 48, 27.4)]
        m = mass & ys_below(fr)
        m |= S().poly([(24.0, 14.0), (34.4, 14.0), (34.2, 25.4), (30.6, 27.8), (24.6, 26.6)]).mask()
        finish_hair(c, m, streaks=[((19, 8.5), (17, 12)), ((25, 8.0), (30, 12.5)), ((29, 18), (30, 25))], skull=sk)
    return c

# ------------------------------------------------------------------ hood down (short hair + the hood bunched at the neck)
def hood_down(d, f):
    c = short(d, f)
    sway = {0: 0, 1: 1, 2: 0, 3: -1, 4: 0}[f]
    def roll(m, edge=None, folds=()):
        c.bevel(m, 2, "base", "hi", "sh")
        c.tone_at(m & ~shift(m, 0, -2) & shift(m, 0, -1), "mid")
        if edge is not None: c.bevel(edge & m, 3, "base", "hi", "mid")
        for a, b in folds: c.paint(line(a, b, 0.9).mask() & m, 2, "sh")
    if d == "down":
        # a V shaped roll round the neck, open at the front
        m = line((15.6, 27.2), (22.0, 30.6), 4.4).mask() | line((32.4, 27.2), (26.0, 30.6), 4.4).mask() | S().ell(24.0, 31.6, 2.6, 1.6).mask()
        m |= S().poly([(14.0, 25.8), (20.0, 24.8), (21.0, 28.0), (15.0, 30.0)]).mask() | S().poly([(34.0, 25.8), (28.0, 24.8), (27.0, 28.0), (33.0, 30.0)]).mask()
        m &= ~S().poly([(21.4, 24.0), (26.6, 24.0), (24.0, 29.4)]).mask()
        edge = ~shift(m, 0, -1) | ~shift(m, -1, 0) & False
        roll(m, edge & rows(26, 40), folds=[((17.0, 27.0), (20.4, 29.6)), ((31.0, 27.0), (27.6, 29.6))])
    elif d == "up":
        m = S().poly([(14.4, 24.4), (33.6, 24.4), (35.0, 29.6), (29.0, 32.0), (26.6, 33.0), (24.0, 40.0), (21.4, 33.0), (19.0, 32.0), (13.0, 29.6)]).mask()
        edge = m & ~shift(m, 0, -1) | m & ~shift(m, 1, 0) & rows(30, 41) | m & ~shift(m, -1, 0) & rows(30, 41)
        roll(m, edge & rows(29, 41), folds=[((24.0, 27.0), (24.0, 37.0)), ((17.0, 26.6), (19.0, 30.0)), ((31.0, 26.6), (29.0, 30.0))])
    else:
        m = S().poly([(23.8, 24.4), (31.8, 24.8), (33.6 + sway * 0.4, 31.2), (30.0, 34.2), (28.0, 40.6 + sway * 0.4), (25.4, 34.6), (22.8, 31.0), (22.0, 27.0)]).mask()
        m |= S().ell(21.0, 28.4, 2.2, 2.6).mask()
        edge = m & ~shift(m, 0, -1) | m & ~shift(m, -1, 0) & rows(30, 42) | m & ~shift(m, 1, 0) & rows(32, 42)
        roll(m, edge & rows(30, 42), folds=[((27.0, 27.0), (29.0, 34.0)), ((24.0, 28.0), (25.0, 33.0))])
    return c

HAIRS = {"short": short, "spiky": spiky, "long": long_, "ponytail": ponytail, "bob": bob, "hood_down": hood_down}
