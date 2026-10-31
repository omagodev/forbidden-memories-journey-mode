#!/usr/bin/env python3
"""Pack the painted secret-arena background and its collision mask.

The source stays in art_dk/arena. The runtime picture uses the same four-bank,
128x128-cell format as the painted village and cistern.
"""
import math
import os
import struct

import numpy as np
from PIL import Image, ImageDraw, ImageOps


HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "../../.."))
SOURCE = os.path.join(ROOT, "art_dk/arena/backgrounds/arena_village_1280x720.png")
CROWD_SOURCE = os.path.join(ROOT, "art_dk/arena/characters/arena_crowd_source.png")
CROWD_RIGHT_SOURCE = os.path.join(ROOT, "art_dk/arena/characters/arena_crowd_right_source.png")
CROWD_PREVIEW = os.path.join(ROOT, "art_dk/arena/characters/arena_crowd_runtime_preview.png")
OUT = os.path.join(os.path.dirname(HERE), "assets")
CELL, STRIDE = 128, 126
BW, BH = 1280, 720
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0 - 0.5


def to555(rgb):
    h, w, _ = rgb.shape
    ys, xs = np.mgrid[0:h, 0:w]
    threshold = BAYER[ys % 4, xs % 4]
    out = np.zeros((h, w), np.uint16)
    for channel, shift in enumerate((0, 5, 10)):
        q = np.clip(np.floor(rgb[:, :, channel] / 255.0 * 31.0 + threshold * 0.9 + 0.5), 0, 31).astype(np.uint16)
        out |= q << shift
    return out | 0x8000


def cut(texture, x0, y0):
    cell = np.zeros((CELL, CELL), np.uint16)
    h, w = min(CELL, BH - y0), min(CELL, BW - x0)
    cell[:h, :w] = texture[y0:y0 + h, x0:x0 + w]
    if h < CELL:
        cell[h:, :w] = texture[BH - 1:BH, x0:x0 + w]
    if w < CELL:
        cell[:, w:] = cell[:, w - 1:w]
    return cell


def build_collision():
    # Walkable inner floor plus the central staircase. The painted shelves,
    # sacks, barrels, pillars and the low foreground wall remain solid.
    walk = Image.new("L", (BW, BH), 0)
    draw = ImageDraw.Draw(walk)
    draw.polygon([(78, 126), (1202, 126), (1202, 538), (728, 548),
                  (728, 720), (552, 720), (552, 548), (78, 538)], fill=255)
    # Trim the bulky side props without stealing the spectator floor marks.
    blocked = [
        (78, 126, 154, 222), (78, 332, 142, 540),
        (1124, 126, 1202, 221), (1135, 330, 1202, 540),
    ]
    for box in blocked:
        draw.rectangle(box, fill=0)
    small = walk.resize((160, 90), Image.Resampling.NEAREST)
    return (np.array(small) <= 127).astype(np.uint8)


def build_crowd():
    """Turn the generated 3x3 character atlas into one nine-frame SPR1 page.

    The centre cell is frame zero (the ring master); the other eight cells are
    the spectators. They are stationary, so the same authored pose is stored
    for all four directions expected by the renderer.
    """
    order = [(1, 1), (0, 0), (1, 0), (2, 0), (0, 1), (2, 1), (0, 2), (1, 2), (2, 2)]

    def atlas_frames(path):
        source = Image.open(path).convert("RGBA")
        sw, sh = source.size
        if sw % 3 or sh % 3:
            raise SystemExit(f"crowd atlas must divide into a 3x3 grid, got {source.size}")
        cw, ch = sw // 3, sh // 3
        result = []
        for gx, gy in order:
            cell = source.crop((gx * cw, gy * ch, (gx + 1) * cw, (gy + 1) * ch))
            alpha = cell.getchannel("A")
            bbox = alpha.point(lambda value: 255 if value >= 24 else 0).getbbox()
            if not bbox:
                raise SystemExit(f"empty crowd cell {gx},{gy} in {path}")
            figure = cell.crop(bbox)
            scale = min(23 / figure.width, 36 / figure.height)
            size = (max(1, round(figure.width * scale)), max(1, round(figure.height * scale)))
            figure = figure.resize(size, Image.Resampling.NEAREST)
            frame = Image.new("RGBA", (25, 38), (0, 0, 0, 0))
            frame.alpha_composite(figure, ((25 - size[0]) // 2, 36 - size[1]))
            result.append(frame)
        return result

    front = atlas_frames(CROWD_SOURCE)
    right = atlas_frames(CROWD_RIGHT_SOURCE)
    left = [ImageOps.mirror(frame) for frame in right]
    directions = [front, left, right, front]

    payload = bytearray(b"SPR1" + struct.pack("<HHHHH", 9, 25, 38, 12, 36))
    for frames in directions:
        for frame in frames:
            rgba = np.array(frame, dtype=np.uint8)
            opaque = rgba[:, :, 3] >= 64
            kind = np.where(opaque, 0, 255).astype(np.uint8)
            weights = np.zeros((38, 25, 4), dtype=np.uint8)
            rgb = rgba[:, :, :3].copy()
            payload.extend(kind.tobytes())
            payload.extend(weights.tobytes())
            payload.extend(rgb.tobytes())
    with open(os.path.join(OUT, "spr_arena_crowd.bin"), "wb") as output:
        output.write(payload)

    preview = Image.new("RGBA", (25 * 9, 38 * 3), (35, 39, 47, 255))
    for row, frames in enumerate((front, left, right)):
        for index, frame in enumerate(frames):
            preview.alpha_composite(frame, (index * 25, row * 38))
    preview.resize((25 * 9 * 4, 38 * 3 * 4), Image.Resampling.NEAREST).save(CROWD_PREVIEW)
    return len(front)


def main():
    image = Image.open(SOURCE).convert("RGB")
    if image.size != (BW, BH):
        raise SystemExit(f"arena source must be {BW}x{BH}, got {image.size}")
    texture = to555(np.array(image).astype(np.float32))
    cells = []
    cols, rows = math.ceil((BW - 1) / STRIDE), math.ceil((BH - 1) / STRIDE)
    for row in range(rows):
        for col in range(cols):
            cells.append(cut(texture, col * STRIDE, row * STRIDE))
    assert len(cells) == 66
    banks = np.zeros((4, 512, 1024), np.uint16)
    for index, cell in enumerate(cells):
        bank, slot = divmod(index, 32)
        y, x = (slot // 8) * CELL, (slot % 8) * CELL
        banks[bank, y:y + CELL, x:x + CELL] = cell
    with open(os.path.join(OUT, "painted_arena.raw"), "wb") as output:
        output.write(struct.pack("<HHHH", 4, 0, 0, 0))
        output.write(banks.tobytes())
    collision = build_collision()
    with open(os.path.join(OUT, "painted_arena_col.bin"), "wb") as output:
        output.write(collision.tobytes())
    crowd = build_crowd()
    print(f"arena: {len(cells)} picture cells, {int(collision.sum())}/{collision.size} blocked collision cells, {crowd} unique people")


if __name__ == "__main__":
    main()
