from rig import *
from poses import pose

def draw_face_down(c, p):
    hx, hy = p["head"]
    D = OUTLINE
    # eyes: 3x4 each, mirrored about x=24 (cols 19-21 and 26-28)
    eye = [["D", "D", "D"], ["W", "P", "P"], ["I", "P", "P"], ["I", "I", "s"]]
    col = {"D": (40, 28, 40), "W": (252, 250, 255), "P": (44, 38, 60), "I": (100, 128, 160)}
    for r, row in enumerate(eye):
        for cc, k in enumerate(row):
            for x in (19 + cc, 28 - cc):
                y = 18 + r
                xx = x
                if x > 23 and k == "W": k2 = "W"
                else: k2 = k
                if k2 == "s": c.paint(S().rect(xx, y, xx + 1, y + 1).mask(), 1, "sh")
                else: c.fixed(S().rect(xx, y, xx + 1, y + 1).mask(), col[k2])
    # eyebrows (hair colour, slot 2)
    for x in (19, 20, 21, 26, 27, 28): c.paint(S().rect(x, 16, x + 1, 17).mask(), 2, "sh")
    # nose and mouth
    c.paint(S().rect(23, 22, 25, 23).mask(), 1, "mid")
    c.fixed(S().rect(23, 24, 25, 25).mask(), (176, 84, 76))
    # cheeks
    for x in (17, 30): c.paint(S().rect(x, 22, x + 2, 24).mask(), 1, "hi")

def draw_face_left(c, p):
    col = {"D": (40, 28, 40), "W": (252, 250, 255), "P": (44, 38, 60), "I": (100, 128, 160)}
    eye = [["D", "D", "D"], ["W", "P", "P"], ["I", "P", "P"], ["I", "I", "P"]]
    for r, row in enumerate(eye):
        for cc, k in enumerate(row):
            x, y = 14 + cc, 18 + r
            c.fixed(S().rect(x, y, x + 1, y + 1).mask(), col[k])
    for x in (14, 15, 16): c.paint(S().rect(x, 16, x + 1, 17).mask(), 2, "sh")
    c.paint(S().rect(12, 20, 14, 22).mask(), 1, "hi")        # nose tip
    c.fixed(S().rect(15, 22, 17, 23).mask(), (176, 84, 76))
    c.paint(S().rect(18, 21, 20, 23).mask(), 1, "hi")        # cheek

def body_cell(d, f):
    p = pose(d, f); c = Cell()
    if d in ("down", "up"):
        hx, hy = p["head"]
        # far/under parts: neck, torso, legs, arms
        legs = S()
        yL, yR = p["legL"][1], p["legR"][1]
        legs.rect(19.8, 43.0, 23.6, yL).rect(24.4, 43.0, 28.2, yR)
        c.bevel(legs.mask(), 1, "mid", "base", "sh")
        c.bevel(S().poly([(17.2, 27), (30.8, 27), (29.4, 43.2), (18.6, 43.2)]).mask(), 1, "mid", "base", "sh")
        c.bevel(S().rect(21.4, 23.0, 26.6, 28.5).mask(), 1, "mid", "mid", "sh")
        for sh, hd in ((p["shL"], p["handL"]), (p["shR"], p["handR"])):
            c.bevel(S().cap(sh, (hd[0], hd[1] - 1.4), 1.7, 1.7).mask(), 1, "base", "hi", "mid")
            c.bevel(S().ell(hd[0], hd[1], 1.9, 1.9).mask(), 1, "base", "hi", "mid")
        c.bevel(S().ell(24.0, 16.0, 9.6, 9.0).mask(), 1, "base", "hi", "mid")
        c.bevel(S().ell(14.4, 17.8, 1.5, 2.0).mask() | S().ell(33.6, 17.8, 1.5, 2.0).mask(), 1, "mid", "base", "sh")
        c.bevel(S().ell(24.0, 16.0, 9.6, 9.0).mask(), 1, "base", "hi", "mid")
        # chin shadow
        yy = np.zeros((H, W), bool); yy[24:26, :] = True
        c.tone_at(S().ell(24.0, 16.0, 9.6, 9.0).mask() & yy, "mid")
        if d == "down": draw_face_down(c, p)
        else:
            # back of the head: slight shade
            pass
    else:
        hx, hy = p["head"]
        c.bevel(S().cap((24.6, 44.0), (p["far_foot"][0], p["far_foot"][1] - 4.2), 2.0).mask(), 1, "sh", "mid", "dk")
        c.bevel(S().cap((23.4, 44.0), (p["near_foot"][0], p["near_foot"][1] - 4.2), 2.0).mask(), 1, "mid", "base", "sh")
        c.bevel(S().cap(p["sh_far"], (p["far_hand"][0], p["far_hand"][1] - 1.4), 1.6).mask() | S().ell(*p["far_hand"], 1.8, 1.8).mask(), 1, "sh", "mid", "dk")
        c.bevel(S().poly([(19.6, 27), (28.4, 27), (27.4, 43.2), (20.6, 43.2)]).mask(), 1, "mid", "base", "sh")
        c.bevel(S().rect(20.6, 23.0, 26.0, 28.5).mask(), 1, "mid", "mid", "sh")
        c.bevel(S().cap(p["sh_near"], (p["near_hand"][0], p["near_hand"][1] - 1.4), 1.7).mask() | S().ell(*p["near_hand"], 1.9, 1.9).mask(), 1, "base", "hi", "mid")
        head = S().ell(23.0, 16.0, 9.3, 9.0).mask() | S().ell(14.3, 19.8, 1.5, 1.4).mask() | S().ell(16.6, 22.0, 2.8, 2.8).mask()
        c.bevel(head, 1, "base", "hi", "mid")
        c.bevel(S().ell(24.4, 18.2, 1.6, 2.0).mask(), 1, "mid", "base", "sh")
        yy = np.zeros((H, W), bool); yy[24:26, :] = True
        c.tone_at(head & yy, "mid")
        draw_face_left(c, p)
    return c
