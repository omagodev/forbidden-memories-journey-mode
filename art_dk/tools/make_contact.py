#!/usr/bin/env python3
"""art_dk/previews/contact_sheet.png: backgrounds (+ collision overlay) on top, baked sprite sheets below."""
import os
from PIL import Image, ImageDraw
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sc = ["harbor", "forest", "castle"]; TW, TH = 600, 338
sp = ["captain", "rival", "tycoon"]
sheets = [Image.open(os.path.join(R, "previews", "sheet_%s.png" % n)) for n in sp]
zs = 1.0
W = 3 * TW + 4 * 10
sh = [s.resize((int(s.width * 0.6), int(s.height * 0.6)), Image.NEAREST) for s in sheets]
H = 40 + TH * 2 + 3 * 10 + 30 + max(s.height for s in sh) + 20
o = Image.new("RGB", (max(W, sum(s.width for s in sh) + 40), H), (34, 30, 40)); d = ImageDraw.Draw(o)
d.text((10, 10), "Duelist Kingdom art kit - backgrounds (1280x720) / walkable+occluder guess / baked sprites (48x62, 4 dirs x idle+4 walk)", fill=(255, 255, 255))
for i, n in enumerate(sc):
    x = 10 + i * (TW + 10)
    o.paste(Image.open(os.path.join(R, "backgrounds", "dk_%s_1280x720.jpg" % n)).resize((TW, TH)), (x, 40))
    o.paste(Image.open(os.path.join(R, "masks", "%s_overlay.png" % n)).resize((TW, TH)), (x, 40 + TH + 10))
y = 40 + 2 * TH + 30
x = 10
for n, s in zip(sp, sh):
    d.text((x, y - 16), n, fill=(255, 255, 255)); o.paste(s, (x, y)); x += s.width + 10
o.save(os.path.join(R, "previews", "contact_sheet.png")); print(o.size)
