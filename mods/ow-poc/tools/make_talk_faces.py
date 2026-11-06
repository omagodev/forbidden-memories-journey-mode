#!/usr/bin/env python3
"""Talk-avatar presets from the Journey map sprites.
For every SPR1 sheet: take the down-facing standing frame, find the figure, frame head+shoulders in a square window,
upscale nearest-neighbour to 48x48 over the dialogue backdrop with a 1px outline glow, write
assets/faces/<name>.face (48*48 little-endian RGB555|0x8000) and a preview assets/faces/png/<name>.png."""
import os, struct, glob
from PIL import Image
ROOT = os.path.join(os.path.dirname(__file__), '..', 'assets')
OUT = os.path.join(ROOT, 'faces'); os.makedirs(os.path.join(OUT, 'png'), exist_ok=True)
BG_TOP, BG_BOT = (44, 30, 62), (14, 10, 26)
OUTLINE = (34, 24, 30)
# per-sheet framing tweaks: window side in sprite pixels (tall helmets / hats need more room)
SIDE = {'soldier': 36}

def load(path):
    d = open(path, 'rb').read()
    if d[:4] != b'SPR1': return None
    nf, w, h, fx, fy = struct.unpack_from('<5H', d, 4)
    tex = w * h; p = 14
    kind = d[p:p + tex]; p += tex * 5
    rgb = d[p:p + tex * 3]
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    for i in range(tex):
        k = kind[i]
        if k == 0: img.putpixel((i % w, i // w), (rgb[i*3], rgb[i*3+1], rgb[i*3+2], 255))
        elif k == 254: img.putpixel((i % w, i // w), OUTLINE + (255,))
    return img

def face(img, name=''):
    bb = img.getbbox()
    if not bb: return None
    x0, y0, x1, y1 = bb
    fig_h = y1 - y0
    # head width: widest opaque run in the top quarter of the figure
    a = img.split()[3]
    # head centre: the longest opaque run of each top row (a staff or a raised cup is a separate, thinner run)
    cs, ws = [], []
    for y in range(y0 + 2, y0 + max(8, int(fig_h * 0.3))):
        best, run, start = (0, 0), 0, 0
        for x in range(img.width + 1):
            if x < img.width and a.getpixel((x, y)):
                if not run: start = x
                run += 1
            else:
                if run > best[0]: best = (run, start)
                run = 0
        if best[0]: cs.append(best[1] + best[0] / 2); ws.append(best[0])
    cs.sort(); cx = cs[len(cs) // 2]
    hw = max(ws)
    hx0, hx1 = int(cx - hw / 2), int(cx + hw / 2) - 1
    side = max(hx1 - hx0 + 1 + 8, int(fig_h * 0.46))          # head + shoulders, a little air
    side = SIDE.get(name, side)
    side = min(side, img.width, fig_h)
    scale = 48 / side
    left = int(round(cx - side / 2)); top = y0 - max(1, side // 10)
    crop = img.crop((left, top, left + side, top + side))
    n = max(1, int(48 // side)) if 48 % side == 0 else None
    big = crop.resize((48, 48), Image.NEAREST)
    bg = Image.new('RGBA', (48, 48))
    for y in range(48):
        t = y / 47
        c = tuple(int(BG_TOP[i] * (1 - t) + BG_BOT[i] * t) for i in range(3))
        for x in range(48): bg.putpixel((x, y), c + (255,))
    # soft rim around the figure so it separates from the backdrop
    ba = big.split()[3]
    rim = Image.new('RGBA', (48, 48), (0, 0, 0, 0))
    for y in range(48):
        for x in range(48):
            if not ba.getpixel((x, y)) and any(0 <= x+dx < 48 and 0 <= y+dy < 48 and ba.getpixel((x+dx, y+dy)) for dx, dy in ((1,0),(-1,0),(0,1),(0,-1))):
                rim.putpixel((x, y), (120, 96, 150, 255))
    bg.alpha_composite(rim); bg.alpha_composite(big)
    # frame border like the dialogue box
    for i in range(48):
        for p in ((i, 0), (i, 47), (0, i), (47, i)): bg.putpixel(p, (200, 160, 60, 255))
    return bg

def write(name, im):
    im.save(os.path.join(OUT, 'png', name + '.png'))
    im.resize((192, 192), Image.NEAREST).save(os.path.join(OUT, 'png', name + '@4x.png'))
    b = bytearray()
    for y in range(48):
        for x in range(48):
            r, g, bl, _ = im.getpixel((x, y))
            b += struct.pack('<H', 0x8000 | (r >> 3) | (g >> 3) << 5 | (bl >> 3) << 10)
    open(os.path.join(OUT, name + '.face'), 'wb').write(b)

for f in sorted(glob.glob(os.path.join(ROOT, 'spr_*.bin'))):
    name = os.path.basename(f)[4:-4]
    im = load(f)
    fc = face(im, name) if im else None
    if fc: write(name, fc); print('ok', name, im.size)
    else: print('skip', name)
