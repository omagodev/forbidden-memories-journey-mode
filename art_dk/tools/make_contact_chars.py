#!/usr/bin/env python3
"""previews/contact_sheet_characters.png: Mago.dev (tee + robe) and InsetoKaiba: portraits (48x48 x6 + 256 version), aura overlay, baked sprite sheets."""
import os
from PIL import Image, ImageDraw
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *a: os.path.join(R, *a)
groups = [("Mago.dev - grey tee", "mago_tee", "mago_tee"), ("Mago.dev - hooded mage robe", "mago_hood", "mago_robe"), ("InsetoKaiba (parody)", "inseto", "inseto")]
sh = {k: Image.open(P("previews", "sheet_%s.png" % k)) for _, _, k in groups}
sw, shh = sh["inseto"].size
cw = max(sw, 288 + 10 + 256) + 20
o = Image.new("RGB", (cw * 3 + 20, 40 + 288 + 20 + shh + 40), (34, 30, 40)); d = ImageDraw.Draw(o)
d.text((10, 10), "Mago.dev x2 outfits + InsetoKaiba: FM-style portraits (48x48 bake + 256 hi-res), baked sprites (48x62, 4 dirs x idle+4 walk).", fill=(255, 255, 255))
for i, (title, pk, sk) in enumerate(groups):
    x = 10 + i * cw
    d.text((x, 28), title, fill=(255, 220, 120))
    o.paste(Image.open(P("portraits", pk + "_48x48_x6.png")), (x, 44))
    o.paste(Image.open(P("portraits", pk + "_256.png")), (x + 298, 44))
    o.paste(sh[sk], (x, 44 + 288 + 20))
o.save(P("previews", "contact_sheet_characters.png")); print(o.size)
