#!/usr/bin/env python3
"""previews/contact_sheet_part3.png: cistern (picture + mask/occluder overlay), Rex Raptor + Bakura ghost sprites, props and icons."""
import os
from PIL import Image, ImageDraw
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); P = lambda *a: os.path.join(R, *a)
BG = (34, 30, 40)
bg = Image.open(P("backgrounds", "dk_cistern_1280x720.jpg")).resize((640, 360)); ov = Image.open(P("masks", "cistern_overlay.png")).resize((640, 360))
rex = Image.open(P("previews", "sheet_rex_raptor.png")); gh = Image.open(P("previews", "sheet_bakura_ghost.png"))
sw = int(rex.width * 0.8); rex = rex.resize((sw, int(rex.height * 0.8)), Image.NEAREST); gh = gh.resize((sw, int(gh.height * 0.8)), Image.NEAREST)
W = 1500; H = 40 + 360 + 30 + rex.height + 30 + 230
o = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(o)
d.text((10, 10), "Part 3 art: Old Cistern (picture + walkable/occluder/warp overlay), Rex Raptor, Bakura ghost (dithered, hovering), hatch/torch props, item icons", fill=(255, 255, 255))
o.paste(bg, (10, 40)); o.paste(ov, (660, 40))
y = 40 + 360 + 24
d.text((10, y - 14), "Rex Raptor", fill=(255, 220, 120)); o.paste(rex, (10, y)); d.text((20 + sw, y - 14), "Bakura ghost (hover 5 texels + ordered dither, no alpha)", fill=(255, 220, 120)); o.paste(gh, (20 + sw, y))
y2 = y + rex.height + 24
d.text((10, y2 - 14), "props (x4/x6): hatch closed / open, torch flame (3 frames), torch glow (dither) | icons 24x24 + 16x16 (x8)", fill=(255, 220, 120))
x = 10; pg = Image.new("RGB", (1, 1))
for p, z in (("overlays/prop_hatch_closed.png", 3), ("overlays/prop_hatch_open.png", 3), ("overlays/prop_torch_flame.png", 4), ("overlays/prop_torch_glow.png", 2),
             ("icons/icon_founders_scarab_24.png", 6), ("icons/icon_lucky_charm_24.png", 6), ("icons/icon_jonos_bandana_24.png", 6), ("icons/icon_founders_scarab_16.png", 6), ("icons/icon_lucky_charm_16.png", 6), ("icons/icon_jonos_bandana_16.png", 6)):
    im = Image.open(P(p)).convert("RGBA"); im = im.resize((im.width * z, im.height * z), Image.NEAREST)
    tile = Image.new("RGBA", im.size, (120, 150, 110, 255)); tile.alpha_composite(im); o.paste(tile.convert("RGB"), (x, y2)); x += im.width + 10
o.save(P("previews", "contact_sheet_part3.png")); print(o.size)
