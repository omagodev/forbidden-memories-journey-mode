from rig import *
from poses import pose
# outfit slots: 1 main, 2 secondary/trim, 3 skin (hands, neck), 4 trousers
BOOT = {"base": (112, 76, 46), "hi": (150, 108, 68), "sh": (72, 46, 30)}
SHOE = {"base": (52, 46, 60), "hi": (96, 90, 108), "sh": (30, 26, 36)}
CREAM = {"base": (238, 232, 220), "hi": (252, 250, 244), "sh": (196, 188, 178)}
GOLD = (240, 200, 84)

def fixed_bevel(c, m, cols_):
    """bevel with fixed colours (dict base/hi/sh)"""
    up, left = shift(m, 0, 1), shift(m, 1, 0); down, right = shift(m, 0, -1), shift(m, -1, 0)
    c.fixed(m, cols_["base"])
    c.fixed(m & (~up | ~left), cols_["hi"])
    c.fixed(m & (~down | ~right), cols_["sh"])

def feet_down(c, p, boot):
    for side, (x0, x1) in (("legL", (19.2, 23.9)), ("legR", (24.1, 28.8))):
        fy = p[side][1]
        pants = S().rect(x0, 41.0, x1, fy - 4.4).mask()
        c.bevel(pants, 4, "base", "base", "mid")
        c.paint(pants & cols(x1 - 1.2 if side == "legL" else x1 - 1.2, 48) & rows(0, 62), 4, "mid") if False else None
        b = S().rect(x0 - 0.3, fy - 4.4, x1 + 0.3, fy).mask()
        # rounded toes
        fixed_bevel(c, b, boot)
        if d_is_front(p): c.fixed(S().rect(x0 + 0.4, fy - 1.0, x1 - 0.4, fy).mask() & False, boot["sh"])
def d_is_front(p): return p["d"] == "down"

def cuff_mask(sh, ex):
    dx, dy = ex[0] - sh[0], ex[1] - sh[1]; L = max((dx * dx + dy * dy) ** .5, 1e-6)
    u = (dx / L, dy / L)
    return S().cap((ex[0] - u[0] * 1.2, ex[1] - u[1] * 1.2), ex, 2.3).mask()

def arms_down(c, p, sleeve_end, long_cuff=None, slot_s=1):
    """skin hands first, then sleeves; sleeve_end = fraction of the arm covered by the sleeve (0.55 short, 1.0 long)"""
    for sh, hd, sgn in ((p["shL"], p["handL"], -1), (p["shR"], p["handR"], 1)):
        c.bevel(S().cap(sh, (hd[0], hd[1] - 1.3), 1.7).mask() | S().ell(hd[0], hd[1], 1.9, 1.9).mask(), 3, "base", "hi", "mid")
        ex = (sh[0] + (hd[0] - sh[0]) * sleeve_end, sh[1] + (hd[1] - 1.3 - sh[1]) * sleeve_end)
        sl = S().cap(sh, ex, 2.35).mask()
        c.bevel(sl, 1, "base", "hi", "mid")
        if long_cuff: c.bevel(cuff_mask(sh, ex), 2, "base", "hi", "mid")

def arms_up(c, p, sleeve_end, long_cuff=None):
    arms_down(c, p, sleeve_end, long_cuff)

def side_arm(c, p, which, sleeve_end, long_cuff=None, sleeve_slot=1):
    sh, hd = (p["sh_near"], p["near_hand"]) if which == "near" else (p["sh_far"], p["far_hand"])
    ex = (sh[0] + (hd[0] - sh[0]) * sleeve_end, sh[1] + (hd[1] - 1.3 - sh[1]) * sleeve_end)
    c.bevel(S().cap(sh, (hd[0], hd[1] - 1.3), 1.7).mask() | S().ell(hd[0], hd[1], 1.9, 1.9).mask(), 3, "base", "hi", "mid")
    sl = S().cap(sh, ex, 2.45).mask()
    c.bevel(sl, sleeve_slot, "base", "hi", "mid")
    if long_cuff: c.bevel(cuff_mask(sh, ex), 2, "base", "hi", "mid")

def legs_side(c, p, boot, pants_slot=4, flare=0.0, hem_y=None):
    """far leg then near leg: trousers capsule + boot"""
    for who, shade in (("far", "sh"), ("near", "base")):
        ft = p[who + "_foot"]
        hip = (24.4, 41.6) if who == "far" else (23.4, 41.6)
        ankle = (ft[0], ft[1] - 4.0)
        # trousers: hip -> ankle
        c.bevel(S().cap(hip, (ankle[0] + 0.4 * (hip[0] - ankle[0]) * 0.0, ankle[1]), 2.7, 2.5).mask(), pants_slot, "base" if who == "near" else "mid", "hi" if who == "near" else "base", "mid" if who == "near" else "sh")
        bt = S().ell(ft[0] - 1.3, ft[1] - 2.0, 3.7, 2.1).mask() | S().cap((ft[0] + 0.3, ft[1] - 4.2), (ft[0] - 0.2, ft[1] - 2.0), 2.3).mask()
        cols_ = boot if who == "near" else {k: tuple(int(v * 0.72) for v in col) for k, col in boot.items()}
        fixed_bevel(c, bt, cols_)

# ---------------------------------------------------------------- tunic (adventurer)
def tunic(d, f):
    p = pose(d, f); c = Cell()
    if d in ("down", "up"):
        feet_down(c, p, BOOT)
        if d == "up":
            pack = S().rect(18.2, 28.0, 29.8, 41.0).mask() & ~S().rect(18.2, 28, 18.8, 28.6).mask()
        torso = S().poly([(16.9, 27.2), (31.1, 27.2), (30.5, 41.8), (17.5, 41.8)]).mask()
        c.bevel(torso, 1, "base", "hi", "mid")
        c.tone_at(torso & rows(36, 42), "mid")
        c.tone_at(S().rect(17, 27, 31, 28.2).mask() & torso, "hi")
        belt = S().poly([(17.2, 38.0), (30.8, 38.0), (30.6, 40.6), (17.4, 40.6)]).mask()
        if d == "down":
            c.bevel(belt, 2, "base", "hi", "sh")
            c.bevel(S().poly([(27.2, 39.4), (30.4, 39.4), (31.2, 44.2), (28.6, 44.4)]).mask(), 2, "mid", "base", "sh")   # sash tail
            c.bevel(S().rect(26.0, 38.0, 28.6, 41.0).mask(), 2, "hi", "hi", "mid")                                       # knot
            neck = S().poly([(21.4, 27.0), (26.6, 27.0), (24.0, 31.2)]).mask()
            c.bevel(neck, 3, "mid", "base", "sh")
            c.paint(line((21.4, 27.4), (24.0, 31.6), 0.9).mask() & ~neck, 1, "sh")
            c.paint(line((26.6, 27.4), (24.0, 31.6), 0.9).mask() & ~neck, 1, "sh")
            c.paint(line((24.0, 32.0), (24.0, 36.5), 0.9).mask(), 1, "mid")
            for sx in (0,):
                pass
        else:
            c.bevel(belt, 2, "base", "hi", "sh")
            c.bevel(S().rect(23.0, 38.0, 25.0, 41.0).mask(), 2, "hi", "hi", "mid")
            c.paint(line((24.0, 28.0), (24.0, 38.0), 0.8).mask(), 1, "mid")
            # backpack
            pk = S().poly([(18.6, 28.4), (29.4, 28.4), (30.0, 42.0), (18.0, 42.0)]).mask()
            fixed_bevel(c, pk, {"base": (118, 78, 44), "hi": (154, 108, 62), "sh": (78, 50, 30)})
            c.fixed(S().rect(19.0, 29.0, 20.4, 40.0).mask() | S().rect(27.6, 29.0, 29.0, 40.0).mask(), (92, 60, 36))
            c.fixed(S().rect(20.4, 34.5, 27.6, 38.6).mask(), (142, 98, 58))
            c.fixed(S().rect(20.4, 34.5, 27.6, 35.4).mask(), (172, 124, 76))
            c.fixed(S().rect(23.2, 36.0, 24.8, 38.0).mask(), (214, 170, 80))
        arms_down(c, p, 0.5)
    else:
        legs_side(c, p, BOOT)
        # backpack behind (right side)
        pk = S().poly([(26.0, 28.4), (32.6, 29.4), (32.8, 40.5), (26.0, 41.6)]).mask()
        fixed_bevel(c, pk, {"base": (118, 78, 44), "hi": (154, 108, 62), "sh": (78, 50, 30)})
        c.fixed(S().rect(28.0, 33.0, 31.4, 38.0).mask(), (140, 96, 56))
        c.fixed(S().rect(30.6, 34.4, 31.8, 36.0).mask(), (214, 170, 80))
        side_arm(c, p, "far", 0.5)
        torso = S().poly([(19.4, 27.2), (28.6, 27.2), (28.8, 41.8), (19.4, 41.8)]).mask()
        c.bevel(torso, 1, "base", "hi", "mid")
        c.tone_at(torso & rows(36, 42), "mid")
        c.bevel(S().poly([(19.2, 38.0), (28.8, 38.0), (28.8, 40.6), (19.2, 40.6)]).mask(), 2, "base", "hi", "sh")
        c.bevel(S().poly([(18.4, 39.4), (20.4, 39.4), (19.2, 44.0), (17.6, 43.6)]).mask(), 2, "mid", "base", "sh")   # sash tail swings forward
        c.paint(line((19.8, 27.6), (22.4, 31.6), 0.9).mask(), 3, "mid")
        side_arm(c, p, "near", 0.5)
    return c

# ---------------------------------------------------------------- jacket (duelist)
def jacket(d, f):
    p = pose(d, f); c = Cell()
    if d in ("down", "up"):
        feet_down(c, p, SHOE)
        jk = S().poly([(16.2, 27.0), (31.8, 27.0), (32.6, 44.6), (15.4, 44.6)]).mask()
        c.bevel(jk, 1, "base", "hi", "mid")
        c.tone_at(jk & rows(38, 45), "mid")
        if d == "down":
            sh = S().poly([(22.4, 27.0), (25.6, 27.0), (26.0, 44.6), (22.0, 44.6)]).mask()    # open front, shirt inside
            fixed_bevel(c, S().poly([(22.4, 27.0), (25.6, 27.0), (24.8, 40.0), (23.2, 40.0)]).mask(), CREAM)
            c.paint(S().poly([(20.4, 27.0), (23.0, 27.0), (23.4, 38.0), (21.0, 38.0)]).mask(), 1, "sh")      # jacket edge inside lapel
            c.paint(S().poly([(25.0, 27.0), (27.6, 27.0), (27.0, 38.0), (24.6, 38.0)]).mask(), 1, "sh")
            c.bevel(S().poly([(19.6, 27.0), (22.8, 27.0), (23.0, 33.5), (20.6, 31.0)]).mask(), 2, "base", "hi", "mid")  # lapels
            c.bevel(S().poly([(25.2, 27.0), (28.4, 27.0), (27.4, 31.0), (25.0, 33.5)]).mask(), 2, "base", "hi", "mid")
            c.paint(line((23.6, 40.0), (23.6, 44.4), 0.8).mask(), 1, "dk"); c.paint(line((24.4, 40.0), (24.4, 44.4), 0.8).mask(), 1, "dk")
            c.fixed(S().rect(22.0, 36.2, 23.2, 37.4).mask(), GOLD)   # button
            c.fixed(S().rect(24.8, 36.2, 26.0, 37.4).mask(), GOLD)
            c.paint(S().rect(23.2, 38.0, 24.8, 40.6).mask(), 2, "mid")
        else:
            c.paint(line((24.0, 28.0), (24.0, 44.0), 0.9).mask(), 1, "sh")
            # emblem: diamond
            c.bevel(S().poly([(24.0, 31.0), (27.0, 34.0), (24.0, 37.0), (21.0, 34.0)]).mask(), 2, "base", "hi", "mid")
            c.paint(S().poly([(24.0, 32.6), (25.4, 34.0), (24.0, 35.4), (22.6, 34.0)]).mask(), 1, "sh")
            c.bevel(S().rect(17.6, 41.0, 30.4, 42.2).mask(), 2, "base", "hi", "mid")
        # popped collar
        for side in (-1, 1):
            cx = 24.0 + side * 3.6
            c.bevel(S().poly([(cx - 2.0 * side, 25.2), (cx + 1.3 * side, 25.0), (cx + 1.6 * side, 28.6), (cx - 2.2 * side, 28.4)]).mask(), 2, "base", "hi", "mid")
        c.bevel(S().rect(20.6, 25.4, 27.4, 27.0).mask() if d == "up" else S().rect(0, 0, 0, 0).mask(), 2, "base", "hi", "mid")
        arms_down(c, p, 0.8, long_cuff=True)
    else:
        legs_side(c, p, SHOE)
        side_arm(c, p, "far", 0.8, long_cuff=True)
        jk = S().poly([(18.8, 27.0), (29.0, 27.0), (29.8, 44.6), (18.4, 44.6)]).mask()
        c.bevel(jk, 1, "base", "hi", "mid")
        c.tone_at(jk & rows(38, 45), "mid")
        fixed_bevel(c, S().poly([(18.8, 27.0), (20.4, 27.0), (20.4, 40.0), (19.4, 40.0)]).mask(), CREAM)
        c.bevel(S().poly([(19.0, 27.0), (22.0, 27.0), (21.0, 32.0), (19.0, 34.0)]).mask(), 2, "base", "hi", "mid")
        c.bevel(S().rect(21.2, 25.2, 26.6, 28.6).mask(), 2, "base", "hi", "mid")
        c.fixed(S().rect(20.6, 36.2, 21.8, 37.4).mask(), GOLD)
        c.paint(line((19.4, 44.0), (29.6, 44.0), 0.9).mask(), 1, "sh")
        side_arm(c, p, "near", 0.8, long_cuff=True)
    return c

# ---------------------------------------------------------------- cloak (hooded traveller)
def cloak(d, f):
    p = pose(d, f); c = Cell()
    s = p["s"]
    if d in ("down", "up"):
        ss = (-s if d == "up" else s)
        # boots and trousers below the hem
        feet_down(c, p, BOOT)
        hemL, hemR = 50.4 - (1.0 if ss == 1 else 0.0), 50.4 - (1.0 if ss == -1 else 0.0)
        body = S().poly([(16.4, 27.0), (31.6, 27.0), (33.4, 40.0), (34.8, hemR), (24.0, hemR + 0.8), (13.2, hemL)]).mask()
        body |= S().poly([(16.4, 27.0), (31.6, 27.0), (33.4, 40.0), (14.6, 40.0)]).mask()
        # scalloped hem: carve small notches
        for x in (16, 20, 24, 28, 32):
            body &= ~S().poly([(x, 51.6 - (0.0)), (x + 1.6, 49.4 - (hemL < 50 and x < 24) - (hemR < 50 and x >= 24)), (x + 3.2, 51.6)]).mask() if False else ~np.zeros((H, W), bool)
        c.bevel(body, 1, "base", "hi", "mid")
        c.tone_at(body & rows(40, 52), "mid")
        # folds
        for x0, x1 in ((19.0, 17.6), (22.0, 20.8), (26.0, 27.2), (29.0, 30.6)):
            c.paint(line((x0, 33.0), (x1, 49.0), 0.9).mask() & body, 1, "sh")
        # trim along the hem and the front edge
        hem = S().poly([(13.2, hemL - 1.4), (24.0, min(hemL, hemR) + 0.0 - 0.6), (34.8, hemR - 1.4), (34.8, hemR + 0.3), (24.0, min(hemL, hemR) + 1.2), (13.2, hemL + 0.3)]).mask() & body
        c.bevel(hem, 2, "base", "hi", "sh")
        if d == "down":
            c.paint(line((24.0, 30.0), (24.0, hemL + 0.4), 0.9).mask() & body, 1, "dk")
            c.paint(line((24.0, 30.0), (24.0, hemL), 1.8).mask() & body & rows(30, 52) & ~line((24.0, 30.0), (24.0, hemL), 0.9).mask(), 2, "mid")
            c.paint(line((24.0, 30.0), (24.0, hemL + 0.4), 0.9).mask() & body, 1, "dk")
        else:
            c.paint(line((24.0, 28.0), (24.0, 49.0), 0.9).mask() & body, 1, "dk")
        # hands peeking out of the cloak
        for hd in (p["handL"], p["handR"]):
            c.bevel(S().ell(hd[0], hd[1], 1.9, 1.9).mask(), 3, "base", "hi", "mid")
        # sleeves: cloak folds over the arms
        for sh, hd in ((p["shL"], p["handL"]), (p["shR"], p["handR"])):
            c.bevel(S().cap(sh, (hd[0] + (-0.2 if hd[0] < 24 else 0.2), hd[1] - 2.6), 2.5).mask(), 1, "base", "hi", "mid")
        # mantle collar + clasp
        c.bevel(S().poly([(15.6, 27.6), (20.0, 25.0), (28.0, 25.0), (32.4, 27.6), (30.0, 31.6), (18.0, 31.6)]).mask(), 2, "base", "hi", "sh")
        if d == "down":
            c.bevel(S().poly([(21.4, 25.0), (26.6, 25.0), (24.0, 29.6)]).mask(), 3, "mid", "base", "sh")
            c.fixed(S().ell(24.0, 31.0, 1.5, 1.5).mask(), GOLD); c.fixed(S().rect(23.2, 30.2, 24.4, 31.0).mask(), (255, 238, 150))
        else:
            c.bevel(S().rect(21.0, 24.4, 27.0, 28.0).mask(), 2, "mid", "base", "sh")
    else:
        legs_side(c, p, BOOT)
        sw = 1.0 if s else 0.0
        back_lift = 0.0
        body = S().poly([(18.6, 27.0), (29.6, 27.0), (32.0 + 1.0 * s * 0 , 41.0), (33.4 + (1.5 * (1 if s > 0 else 0)), 50.4 - (1.0 if s > 0 else 0)),
                         (20.0 - 1.5 * (1 if s < 0 else 0), 50.4 - (1.0 if s < 0 else 0)), (17.2, 41.0)]).mask()
        # side fabric: back-biased flare
        c.bevel(body, 1, "base", "hi", "mid")
        c.tone_at(body & rows(40, 52), "mid")
        for x0, x1 in ((22.0, 21.2), (25.4, 26.6), (28.0, 30.0)):
            c.paint(line((x0, 33.0), (x1, 49.0), 0.9).mask() & body, 1, "sh")
        c.bevel(S().poly([(17.4, 47.0), (20.0 - 1.5 * (1 if s < 0 else 0), 49.0), (20.0 - 1.5 * (1 if s < 0 else 0), 50.7 - (1.0 if s < 0 else 0)), (17.0, 49.0)]).mask() & False, 2, "base")
        hemy = 50.4
        c.bevel(S().poly([(17.0, hemy - 1.6), (33.8, hemy - 1.6), (33.8, hemy + 0.3), (17.0, hemy + 0.3)]).mask() & body, 2, "base", "hi", "sh")
        c.bevel(S().poly([(17.8, 29.0), (20.4, 29.0), (19.6, 49.0), (17.2, 49.0)]).mask() & body & False, 2, "mid")
        side_arm(c, p, "near", 0.85)
        c.bevel(S().poly([(17.2, 27.6), (22.0, 25.0), (28.0, 25.0), (30.6, 27.8), (29.4, 31.4), (19.0, 31.4)]).mask(), 2, "base", "hi", "sh")
        c.bevel(S().rect(21.0, 24.6, 26.0, 28.0).mask(), 3, "mid", "base", "sh") if False else None
        c.fixed(S().ell(20.0, 30.6, 1.4, 1.4).mask(), GOLD)
    return c

# ---------------------------------------------------------------- uniform (school)
def uniform(d, f):
    p = pose(d, f); c = Cell()
    if d in ("down", "up"):
        feet_down(c, p, SHOE)
        bz = S().poly([(16.8, 27.0), (31.2, 27.0), (31.0, 43.0), (17.0, 43.0)]).mask()
        c.bevel(bz, 1, "base", "hi", "mid")
        c.tone_at(bz & rows(38, 44), "mid")
        if d == "down":
            fixed_bevel(c, S().poly([(21.2, 27.0), (26.8, 27.0), (24.0, 38.0)]).mask(), CREAM)
            # blazer opening edges (lapel V)
            c.bevel(S().poly([(18.4, 27.0), (21.6, 27.0), (24.0, 38.6), (22.4, 41.0)]).mask(), 1, "mid", "base", "sh")
            c.bevel(S().poly([(26.4, 27.0), (29.6, 27.0), (25.6, 41.0), (24.0, 38.6)]).mask(), 1, "mid", "base", "sh")
            fixed_bevel(c, S().poly([(21.0, 27.0), (23.4, 27.0), (24.0, 29.0), (22.2, 29.4)]).mask(), CREAM)
            fixed_bevel(c, S().poly([(25.0, 27.0), (27.0, 27.0), (25.8, 29.4), (24.0, 29.0)]).mask(), CREAM)
            tie = S().poly([(23.2, 28.8), (24.8, 28.8), (25.0, 35.6), (24.0, 37.6), (23.0, 35.6)]).mask()
            c.bevel(tie, 2, "base", "hi", "sh")
            c.paint(S().rect(23.2, 28.8, 24.8, 30.2).mask(), 2, "mid")
            c.fixed(S().rect(18.2, 33.0, 20.2, 34.4).mask(), (242, 236, 120)) if False else None
            c.paint(S().rect(18.0, 35.5, 20.0, 36.4).mask() & bz, 1, "sh")   # pocket flap
            c.paint(line((24.0, 40.0), (24.0, 43.0), 0.8).mask(), 1, "dk")
        else:
            c.paint(line((24.0, 28.0), (24.0, 43.0), 0.9).mask(), 1, "sh")
            fixed_bevel(c, S().poly([(20.8, 26.0), (27.2, 26.0), (26.0, 28.4), (22.0, 28.4)]).mask(), CREAM)
            c.paint(line((19.0, 41.0), (23.0, 41.0), 0.8).mask(), 1, "sh"); c.paint(line((25.0, 41.0), (29.0, 41.0), 0.8).mask(), 1, "sh")
        arms_down(c, p, 0.8, long_cuff=True)
    else:
        legs_side(c, p, SHOE)
        side_arm(c, p, "far", 0.8, long_cuff=True)
        bz = S().poly([(19.2, 27.0), (28.8, 27.0), (28.8, 43.0), (19.4, 43.0)]).mask()
        c.bevel(bz, 1, "base", "hi", "mid")
        c.tone_at(bz & rows(38, 44), "mid")
        fixed_bevel(c, S().poly([(19.2, 27.0), (21.4, 27.0), (20.4, 33.0), (19.2, 31.0)]).mask(), CREAM)
        fixed_bevel(c, S().rect(21.0, 25.6, 26.0, 28.2).mask(), CREAM)
        c.bevel(S().poly([(18.8, 29.2), (20.2, 29.2), (20.4, 36.4), (19.2, 37.0)]).mask(), 2, "base", "hi", "sh")  # tie
        c.paint(line((20.0, 39.0), (20.0, 43.0), 0.8).mask(), 1, "dk")
        side_arm(c, p, "near", 0.8, long_cuff=True)
    return c

OUTFITS = {"tunic": tunic, "jacket": jacket, "cloak": cloak, "uniform": uniform}
