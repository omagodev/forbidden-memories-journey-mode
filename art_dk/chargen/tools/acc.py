from rig import *
from poses import pose
from hair import ys_below
# accessory slots: 1 main colour, 2 second colour (trim / brim / tray), 3 skin, 4 spare
CARD = (238, 232, 212)

def sway_of(f): return {0: 0, 1: 1, 2: 0, 3: -1, 4: 0}[f]

def none(d, f): return Cell()

def headband(d, f):
    c = Cell(); sw = sway_of(f)
    if d in ("down", "up"):
        head = S().ell(24.0, 15.0, 10.5, 9.4).mask()
        band = S().poly([(12.0, 12.6), (24.0, 13.4), (36.0, 12.6), (36.0, 15.4), (24.0, 16.2), (12.0, 15.4)]).mask() & head
        c.bevel(band, 1, "base", "hi", "mid")
        if d == "down":
            c.bevel(S().ell(33.0, 14.4, 1.7, 1.7).mask(), 1, "hi", "hi", "mid")
            c.bevel(S().poly([(32.8, 15.4), (34.8, 15.4), (36.2 + sw * 0.6, 21.0), (34.2 + sw * 0.6, 20.0)]).mask(), 1, "base", "hi", "sh")
            c.bevel(S().poly([(32.0, 15.4), (33.6, 15.4), (33.4 - sw * 0.4, 20.6), (32.0 - sw * 0.4, 19.6)]).mask(), 1, "mid", "base", "sh")
        else:
            c.bevel(S().ell(24.0, 14.8, 1.9, 1.7).mask(), 1, "hi", "hi", "mid")
            c.bevel(S().poly([(23.2, 15.6), (25.6, 15.6), (26.6 + sw, 22.0), (24.4 + sw, 21.0)]).mask(), 1, "base", "hi", "sh")
            c.bevel(S().poly([(22.4, 15.6), (24.2, 15.6), (22.6 - sw, 21.0), (21.2 - sw, 20.0)]).mask(), 1, "mid", "base", "sh")
    else:
        head = S().ell(23.0, 15.0, 10.4, 9.4).mask()
        band = S().poly([(12.0, 16.0), (22.0, 14.2), (34.0, 12.4), (34.0, 15.4), (22.0, 17.2), (12.0, 18.8)]).mask() & head
        c.bevel(band, 1, "base", "hi", "mid")
        c.bevel(S().ell(32.4, 14.0, 1.7, 1.7).mask(), 1, "hi", "hi", "mid")
        c.bevel(S().poly([(32.0, 14.8), (33.8, 14.8), (36.6 + sw, 21.0), (35.0 + sw, 22.0)]).mask(), 1, "base", "hi", "sh")
        c.bevel(S().poly([(31.4, 14.8), (32.8, 14.8), (34.6 + sw * 1.2, 22.4), (33.2 + sw * 1.2, 23.2)]).mask(), 1, "mid", "base", "sh")
    return c

def scarf(d, f):
    c = Cell(); sw = sway_of(f)
    if d == "down":
        wrap = S().poly([(17.6, 25.6), (30.4, 25.6), (31.4, 29.6), (24.0, 31.4), (16.6, 29.6)]).mask()
        c.bevel(wrap, 1, "base", "hi", "mid")
        c.paint(line((19.0, 28.0), (24.0, 30.0), 0.9).mask() & wrap, 1, "mid")
        c.paint(line((29.0, 28.0), (24.0, 30.0), 0.9).mask() & wrap, 1, "mid")
        # tails: one long hanging over the chest with a stripe
        t = S().poly([(26.0, 29.4), (29.8, 28.8), (30.6 + sw * 0.6, 38.0), (27.4 + sw * 0.6, 39.6)]).mask()
        c.bevel(t, 1, "base", "hi", "mid"); c.paint(S().rect(27.0, 35.0, 31.0, 36.2).mask() & t, 2, "base")
        c.bevel(S().ell(26.4, 30.2, 2.0, 1.8).mask(), 1, "hi", "hi", "mid")
    elif d == "up":
        wrap = S().poly([(17.6, 25.2), (30.4, 25.2), (31.4, 29.0), (24.0, 30.8), (16.6, 29.0)]).mask()
        c.bevel(wrap, 1, "base", "hi", "mid")
        t = S().poly([(20.0, 29.2), (25.0, 29.4), (26.2 + sw, 40.0), (21.0 + sw, 41.0)]).mask()
        c.bevel(t, 1, "base", "hi", "mid"); c.paint(S().rect(20.0, 36.0, 27.0, 37.2).mask() & t, 2, "base")
        t2 = S().poly([(25.4, 29.4), (28.6, 29.0), (29.6 - sw, 36.0), (26.4 - sw, 37.0)]).mask()
        c.bevel(t2, 1, "mid", "base", "sh")
    else:
        wrap = S().poly([(19.4, 25.4), (28.0, 25.4), (29.4, 29.4), (24.0, 31.0), (18.6, 29.4)]).mask()
        c.bevel(wrap, 1, "base", "hi", "mid")
        t = S().poly([(26.6, 28.4), (30.0, 27.6), (37.6 + sw, 31.6), (36.6 + sw, 34.4), (30.0, 31.4)]).mask()
        c.bevel(t, 1, "base", "hi", "mid"); c.paint(S().rect(33.4 + sw, 27.0, 34.6 + sw, 36.0).mask() & t, 2, "base")
        c.bevel(S().ell(26.4, 29.8, 2.0, 1.8).mask(), 1, "hi", "hi", "mid")
    return c

def disk(d, f):
    c = Cell(); p = pose(d, f)
    if d == "down":
        hd = p["handR"]; sh = p["shR"]     # character's left arm = screen right
        c.bevel(S().cap((sh[0] + 0.2, sh[1] + 2.6), (hd[0] + 0.4, hd[1] - 1.6), 2.1).mask(), 2, "base", "hi", "mid")   # sleeve guard / arm band
        plate = S().poly([(33.4, hd[1] - 7.2), (38.6, hd[1] - 6.4), (39.8, hd[1] - 0.6), (37.6, hd[1] + 3.0), (33.6, hd[1] + 2.4)]).mask()
        c.bevel(plate, 1, "base", "hi", "sh")
        c.bevel(S().rect(35.2, hd[1] - 5.6, 38.4, hd[1] + 0.8).mask(), 2, "base", "hi", "mid")
        for k in range(3): c.fixed(S().rect(35.6, hd[1] - 5.0 + k * 2.0, 38.0, hd[1] - 3.8 + k * 2.0).mask(), CARD)
        c.fixed(S().rect(34.0, hd[1] - 3.0, 35.0, hd[1] - 2.0).mask(), (90, 220, 150))
        c.bevel(S().ell(hd[0], hd[1], 1.9, 1.9).mask(), 3, "base", "hi", "mid")
    elif d == "up":
        hd = p["handL"]; sh = p["shL"]     # seen from behind, the left arm is on screen left
        c.bevel(S().cap((sh[0] - 0.2, sh[1] + 2.6), (hd[0] - 0.4, hd[1] - 1.6), 2.1).mask(), 2, "base", "hi", "mid")
        plate = S().poly([(14.6, hd[1] - 7.2), (9.4, hd[1] - 6.4), (8.2, hd[1] - 0.6), (10.4, hd[1] + 3.0), (14.4, hd[1] + 2.4)]).mask()
        c.bevel(plate, 1, "base", "hi", "sh")
        c.bevel(S().rect(9.6, hd[1] - 5.6, 12.8, hd[1] + 0.8).mask(), 2, "base", "hi", "mid")
        for k in range(3): c.fixed(S().rect(10.0, hd[1] - 5.0 + k * 2.0, 12.4, hd[1] - 3.8 + k * 2.0).mask(), CARD)
        c.bevel(S().ell(hd[0], hd[1], 1.9, 1.9).mask(), 3, "base", "hi", "mid")
    else:
        sh, hd = p["sh_near"], p["near_hand"]
        c.bevel(S().cap((sh[0] + (hd[0] - sh[0]) * 0.35, sh[1] + (hd[1] - 1.3 - sh[1]) * 0.35), (hd[0], hd[1] - 1.8), 2.4).mask(), 2, "base", "hi", "mid")
        # plate pointing forward from the forearm (seen edge-on: a slim wedge with a card tray)
        fx = hd[0]
        plate = S().poly([(fx + 1.8, hd[1] - 4.6), (fx - 7.4, hd[1] - 5.4), (fx - 8.6, hd[1] - 2.8), (fx - 8.0, hd[1] + 0.6), (fx + 1.8, hd[1] + 0.4)]).mask()
        c.bevel(plate, 1, "base", "hi", "sh")
        c.bevel(S().rect(fx - 6.6, hd[1] - 4.2, fx + 0.6, hd[1] - 1.8).mask(), 2, "base", "hi", "mid")
        for k in range(3): c.fixed(S().rect(fx - 6.2 + k * 2.4, hd[1] - 3.8, fx - 4.6 + k * 2.4, hd[1] - 2.2).mask(), CARD)
        c.bevel(S().ell(hd[0], hd[1], 1.9, 1.9).mask(), 3, "base", "hi", "mid")
    return c

def cap(d, f):
    c = Cell()
    if d == "down":
        crown = S().ell(24.0, 12.4, 11.0, 7.4).mask() & rows(0, 15)
        c.bevel(crown, 1, "base", "hi", "mid")
        c.bevel(S().poly([(12.8, 14.0), (35.2, 14.0), (35.6, 16.0), (32.0, 17.4), (16.0, 17.4), (12.4, 16.0)]).mask(), 2, "base", "hi", "sh")   # brim seen from the front
        c.paint(S().rect(13, 13.0, 35, 14.0).mask() & crown, 2, "mid")
        c.fixed(S().rect(22.6, 8.0, 25.4, 11.0).mask(), (240, 232, 214)); c.paint(S().rect(23.2, 8.6, 24.8, 10.4).mask(), 2, "base")
        c.fixed(S().rect(23.8, 4.4, 24.2, 4.8).mask() & False, CARD)
        c.paint(line((24.0, 5.8), (24.0, 13.0), 0.8).mask() & crown, 1, "mid")
    elif d == "up":
        crown = S().ell(24.0, 12.8, 11.0, 7.6).mask() & rows(0, 17)
        c.bevel(crown, 1, "base", "hi", "mid")
        c.bevel(S().rect(14.0, 15.6, 34.0, 17.2).mask(), 2, "base", "hi", "mid")
        c.paint(line((24.0, 5.8), (24.0, 15.0), 0.8).mask() & crown, 1, "mid")
        c.paint(S().rect(22.0, 15.8, 26.0, 17.0).mask(), 1, "dk")
    else:
        crown = S().ell(23.4, 12.6, 10.4, 7.4).mask() & rows(0, 16)
        c.bevel(crown, 1, "base", "hi", "mid")
        c.bevel(S().poly([(14.6, 14.2), (22.0, 14.2), (22.0, 16.4), (8.6, 17.4), (8.0, 15.4)]).mask(), 2, "base", "hi", "sh")   # visor pointing forward
        c.bevel(S().rect(14.0, 14.8, 33.0, 16.2).mask() & crown, 2, "base", "hi", "mid")
        c.paint(line((22.0, 5.6), (18.0, 13.8), 0.8).mask() & crown, 1, "mid")
        c.paint(line((27.0, 6.4), (27.0, 14.0), 0.8).mask() & crown, 1, "mid")
    return c

ACCS = {"none": none, "headband": headband, "scarf": scarf, "duel_disk": disk, "cap": cap}
