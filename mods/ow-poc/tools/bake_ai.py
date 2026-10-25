import numpy as np, struct, sys
from PIL import Image
sys.path.insert(0, "/workspace/study/fmrecomp/sprite_work")
import bake_sprites as B
im = Image.open("/workspace/study/fmrecomp/sprite_work/ai_sheet.jpg").convert("RGB")
a = np.array(im).astype(int)
W, H = im.size; cw, ch = W // 3, H // 4
bg = (a[..., 0] > 170) & (a[..., 1] < 110) & (a[..., 2] > 70) & (a[..., 0] - a[..., 1] > 110)
alpha = (~bg)
# remove isolated specks
from PIL import ImageFilter
am = Image.fromarray((alpha * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(5))
alpha = np.array(am) > 127
boxes = {}
for r in range(4):
    for c in range(3):
        m = alpha[r * ch:(r + 1) * ch, c * cw:(c + 1) * cw]
        ys, xs = np.nonzero(m)
        boxes[(r, c)] = (xs.min(), ys.min(), xs.max(), ys.max())
hmax = max(b[3] - b[1] for b in boxes.values())
print("cell", cw, ch, "heights", sorted(set(b[3] - b[1] for b in boxes.values())))
TARGET = float(sys.argv[1]) if len(sys.argv) > 1 else 52.0
sc = TARGET / hmax
cells = {}
order = {0: "down", 1: "left", 2: "right", 3: "up"}
colmap = [0, 1, 0, 2, 0]      # idle, step A, idle, step B, idle
def cell(r, c):
    x0, y0, x1, y1 = boxes[(r, c)]
    sub = im.crop((c * cw + x0, r * ch + y0, c * cw + x1 + 1, r * ch + y1 + 1))
    m = Image.fromarray((alpha[r * ch + y0:r * ch + y1 + 1, c * cw + x0:c * cw + x1 + 1] * 255).astype(np.uint8))
    w, h = max(1, round(sub.width * sc)), max(1, round(sub.height * sc))
    # premultiplied area resize
    rgb = np.array(sub).astype(np.float64) * (np.array(m)[..., None] / 255.0)
    pr = Image.fromarray(rgb.astype(np.uint8)); 
    rs = np.array(pr.resize((w, h), Image.BOX)).astype(np.float64)
    al = np.array(m.resize((w, h), Image.BOX)).astype(np.float64) / 255.0
    col = rs / np.maximum(al[..., None], 1e-3)
    out_k = np.full((B.CH, B.CW), 255, np.uint8); out_rgb = np.zeros((B.CH, B.CW, 3))
    ox = B.FX - w // 2; oy = B.FY - h + 1
    for y in range(h):
        for x in range(w):
            X, Y = ox + x, oy + y
            if 0 <= X < B.CW and 0 <= Y < B.CH and al[y, x] >= 0.5:
                out_k[Y, X] = 0; out_rgb[Y, X] = np.clip(col[y, x], 0, 255)
    solid = out_k == 0
    pad = np.pad(solid, 1)
    near = pad[:-2, 1:-1] | pad[2:, 1:-1] | pad[1:-1, :-2] | pad[1:-1, 2:]
    out_k[(~solid) & near] = 254
    at = np.zeros((B.CH, B.CW, 7)); at[..., 4:7] = out_rgb
    return out_k, at
for r in range(4):
    for f, c in enumerate(colmap):
        cells[(order[r], f)] = cell(r, c)
B.write_bin("/workspace/study/fmrecomp/sprite_work/out/spr_ai.bin", cells, 4)
B.contact(cells, 4, {}, True).save("/workspace/study/fmrecomp/sprite_work/out/sheet_ai.png")
print("ok scale", sc)
