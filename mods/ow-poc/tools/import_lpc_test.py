#!/usr/bin/env python3
"""Build the Journey Mode LPC animation proof of concept.

The Universal LPC source keeps each animation in 64x64 cells.  This converter
composites a deliberately small, credited set of LPC layers, downsizes it once
with a high-quality filter to Journey's on-screen resolution, and keeps the
complete nine-pose walk cycle plus a separate idle pose.  The game then draws
the resulting 25x38 cells at 1:1, avoiding the shimmering caused by point-
sampling the old 48x62 test cells down to 24x31 every frame.

Usage:
  python mods/ow-poc/tools/import_lpc_test.py PATH_TO_LPC_REPOSITORY
"""
from __future__ import annotations

import argparse
import csv
import struct
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps


CELL = 64
OUT_W, OUT_H = 25, 38
SRC_ANCHOR = (32, 63)
CONTENT_ANCHOR = (12, 34)
DRAW_ANCHOR = (12, 32)       # two texels below the nominal feet: lets the shoes settle into the ground shadow
SCALE = 0.50
WALK_FRAMES = tuple(range(9))
# Journey rows are down, left, right, up; LPC rows are up, left, down, right.
LPC_ROWS = (2, 1, 3, 0)

# Bottom to top. Each person now has a distinct LPC silhouette selected to
# echo the existing FM portrait/painted sprite, not merely a different colour.
# Recolouring is local to the generated asset; upstream PNGs remain untouched.
CHARACTERS = {
    "test": (
        ("body/bodies/male", None), ("head/heads/human/male", None),
        ("feet/shoes/basic/male", (38, 30, 34)), ("legs/pants/male", (38, 42, 68)),
        ("torso/clothes/longsleeve/longsleeve2_vneck/male", (46, 72, 150)), ("hair/spiked2/adult", (72, 42, 28)),
    ),
    "simon": (
        ("body/bodies/male", None), ("head/heads/human/male", None),
        ("feet/shoes/basic/male", (64, 44, 30)), ("legs/pants/male", (84, 64, 38)),
        ("torso/clothes/longsleeve/formal/male", (176, 148, 72)), ("torso/waist/belt_mage", (28, 66, 144)),
        ("hat/cloth/hijab/male", (194, 174, 112)),
    ),
    "teana": (
        ("hair/long_tied/adult/bg", (62, 34, 26)),
        ("body/bodies/female", None), ("head/heads/human/female", None),
        ("feet/shoes/basic/thin", (72, 42, 32)), ("legs/pants/thin", (112, 54, 52)),
        ("legs/skirts/plain/thin", (210, 192, 142)), ("torso/clothes/longsleeve/longsleeve2_vneck/female", (210, 192, 142)),
        ("torso/waist/sash/female", (146, 42, 44)),
        ("hair/long_tied/adult/fg", (62, 34, 26)), ("hat/headband/tied/adult", (154, 34, 38)),
    ),
    "guard": (
        ("body/bodies/male", (112, 70, 42)), ("head/heads/human/male", (112, 70, 42)),
        ("feet/shoes/basic/male", (50, 34, 24)), ("legs/pants/male", (70, 46, 28)),
        ("torso/clothes/longsleeve/longsleeve2_buttoned/male", (78, 48, 26)), ("hat/helmet/nasal/adult", (76, 50, 28)),
    ),
    "jono": (
        ("body/bodies/male", None), ("head/heads/human/male", None),
        ("feet/shoes/basic/male", (60, 38, 26)), ("legs/pants/male", (138, 94, 48)),
        ("torso/clothes/sleeveless/sleeveless1/male", (164, 42, 28)), ("hair/messy2/adult", (255, 130, 0)),
    ),
    "rival": (
        ("cape/solid/bg", (58, 32, 84)),
        ("body/bodies/male", None), ("head/heads/human/male_gaunt", None),
        ("feet/shoes/basic/male", (32, 28, 34)), ("legs/pants/male", (34, 30, 46)),
        ("torso/clothes/longsleeve/longsleeves/male", (72, 42, 100)), ("cape/solid/fg", (58, 32, 84)),
        ("hat/cloth/hood/adult", (66, 36, 94)),
    ),
    "mago": (
        ("cape/solid/bg", (20, 38, 28)),
        ("body/bodies/male", (102, 62, 42)), ("head/heads/human/male_gaunt", (102, 62, 42)),
        ("feet/shoes/basic/male", (32, 26, 34)), ("legs/pants/male", (32, 42, 36)),
        ("torso/clothes/longsleeve/formal/male", (24, 32, 28)), ("cape/solid/fg", (20, 38, 28)),
        ("hair/long_messy/adult", (52, 34, 26)),
    ),
    "baker": (
        ("body/bodies/male", None), ("head/heads/human/male_plump", None),
        ("feet/shoes/basic/male", (74, 48, 30)), ("legs/pants/male", (106, 78, 48)),
        ("torso/clothes/longsleeve/longsleeve2_polo/male", (196, 176, 132)),
        ("torso/aprons/overalls/male", (216, 204, 172)), ("hat/cloth/leather_cap/adult", (210, 194, 154)),
    ),
    "farmer": (
        ("body/bodies/male", None), ("head/heads/human/male", None),
        ("feet/shoes/basic/male", (54, 38, 26)), ("legs/pants/male", (88, 58, 34)),
        ("torso/clothes/longsleeve/longsleeve2_buttoned/male", (126, 76, 36)),
        ("torso/aprons/overalls/male", (62, 104, 48)), ("beards/beard/medium", (76, 46, 24)),
        ("hat/magic/wizard/base/adult", (174, 118, 42)), ("hat/magic/wizard/belt/adult", (70, 44, 24)),
    ),
    "rex": (
        ("body/bodies/male", None), ("head/heads/human/male", None),
        ("feet/shoes/basic/male", (34, 28, 34)), ("legs/pants/male", (36, 38, 50)),
        ("torso/clothes/longsleeve/longsleeve2_cardigan/male", (104, 50, 130)), ("hair/spiked_liberty/adult", (196, 62, 24)),
    ),
    "bakura": (
        ("body/bodies/male", None), ("head/heads/human/male_gaunt", None),
        ("feet/shoes/basic/male", (70, 68, 88)), ("legs/pants/male", (82, 80, 108)),
        ("torso/clothes/longsleeve/longsleeve2_polo/male", (76, 88, 156)), ("hair/bangs/adult", (188, 182, 204)),
    ),
}


def layers_for(name: str) -> tuple[tuple[str, tuple[int, int, int] | None], ...]:
    return CHARACTERS[name]


def recolour(image: Image.Image, colour: tuple[int, int, int] | None) -> Image.Image:
    image = image.convert("RGBA")
    if colour is None:
        return image
    alpha = image.getchannel("A")
    gray = ImageOps.grayscale(image.convert("RGB"))
    # Preserve the source shading and its dark pixel-art outline while moving
    # the highlights towards the requested Journey palette.
    hi = tuple(min(255, c * 2 + 42) for c in colour)
    lo = tuple(max(8, min(48, c // 6)) for c in colour)
    result = ImageOps.colorize(gray, black=lo, white=hi).convert("RGBA")
    result.putalpha(alpha)
    return result


def load_layers(root: Path, animation: str, layers: tuple[tuple[str, tuple[int, int, int] | None], ...]) -> list[Image.Image]:
    sheets = []
    for relative, colour in layers:
        path = root / "spritesheets" / relative / f"{animation}.png"
        # A few LPC garments predate the separate idle sheet. Their first walk
        # pose is the compatible standing pose used with the base's idle row.
        if animation == "idle" and not path.is_file():
            path = root / "spritesheets" / relative / "walk.png"
        if not path.is_file():
            raise SystemExit(f"missing LPC layer: {path}")
        image = recolour(Image.open(path), colour)
        if image.height != CELL * 4 or image.width % CELL:
            raise SystemExit(f"unexpected LPC sheet size {image.size}: {path}")
        sheets.append(image)
    return sheets


def compose_cell(sheets: list[Image.Image], direction: int, frame: int) -> Image.Image:
    cell = Image.new("RGBA", (CELL, CELL))
    box = (frame * CELL, direction * CELL, (frame + 1) * CELL, (direction + 1) * CELL)
    for sheet in sheets:
        cell.alpha_composite(sheet.crop(box))
    # Resize once during import instead of throwing away every second texel at
    # runtime. Pillow's RGBA resize is alpha-aware, so coloured edge pixels do
    # not acquire a dark halo before SPR1's binary transparency conversion.
    scaled_size = round(CELL * SCALE)
    cell = cell.resize((scaled_size, scaled_size), Image.Resampling.LANCZOS)
    source_foot = (round(SRC_ANCHOR[0] * SCALE), round(SRC_ANCHOR[1] * SCALE))
    result = Image.new("RGBA", (OUT_W, OUT_H))
    result.alpha_composite(cell, (CONTENT_ANCHOR[0] - source_foot[0], CONTENT_ANCHOR[1] - source_foot[1]))
    return result


def cells(root: Path, layers: tuple[tuple[str, tuple[int, int, int] | None], ...]) -> list[list[Image.Image]]:
    idle = load_layers(root, "idle", layers)
    walk = load_layers(root, "walk", layers)
    result = []
    for direction in range(4):
        source_row = LPC_ROWS[direction]
        row = [compose_cell(idle, source_row, 0)]
        row.extend(compose_cell(walk, source_row, frame) for frame in WALK_FRAMES)
        result.append(row)
    return result


def write_spr1(path: Path, frames: list[list[Image.Image]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as output:
        output.write(b"SPR1" + struct.pack("<HHHHH", len(frames[0]), OUT_W, OUT_H, DRAW_ANCHOR[0], DRAW_ANCHOR[1]))
        for row in frames:
            for image in row:
                rgba = np.asarray(image, dtype=np.uint8)
                solid = rgba[..., 3] >= 128
                kind = np.where(solid, 0, 255).astype(np.uint8)
                output.write(kind.tobytes())
                output.write(bytes(OUT_W * OUT_H * 4))  # no runtime palette weights in this proof of concept
                rgb = rgba[..., :3].copy()
                rgb[~solid] = 0
                output.write(rgb.tobytes())


def previews(directory: Path, frames: list[list[Image.Image]], people: dict[str, list[list[Image.Image]]]) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    sheet = Image.new("RGBA", (len(frames[0]) * OUT_W, 4 * OUT_H), (38, 43, 48, 255))
    for direction, row in enumerate(frames):
        for frame, image in enumerate(row):
            sheet.alpha_composite(image, (frame * OUT_W, direction * OUT_H))
    sheet.resize((sheet.width * 4, sheet.height * 4), Image.Resampling.NEAREST).save(directory / "lpc_test_preview.png")

    # Down-facing animation: idle once, then the complete selected walk loop.
    sequence = [frames[0][0]] + frames[0][1:]
    sequence = [f.resize((OUT_W * 8, OUT_H * 8), Image.Resampling.NEAREST) for f in sequence]
    sequence[0].save(directory / "lpc_test_walk.gif", save_all=True, append_images=sequence[1:], duration=110,
                     loop=0, disposal=2, transparency=0)

    cols = 6
    lineup = Image.new("RGBA", (cols * OUT_W, ((len(people) + cols - 1) // cols) * OUT_H), (38, 43, 48, 255))
    for i, person in enumerate(people.values()):
        lineup.alpha_composite(person[0][0], ((i % cols) * OUT_W, (i // cols) * OUT_H))
    lineup.resize((lineup.width * 6, lineup.height * 6), Image.Resampling.NEAREST).save(directory / "lpc_people_preview.png")


def write_credits(root: Path, path: Path) -> None:
    selected = set()
    for layers in CHARACTERS.values():
        for relative, _colour in layers:
            for animation in ("idle", "walk"):
                candidate = f"{relative}/{animation}.png"
                if (root / "spritesheets" / candidate).is_file():
                    selected.add(candidate)
    with (root / "CREDITS.csv").open("r", encoding="utf-8", newline="") as source:
        reader = csv.DictReader(source)
        rows = [row for row in reader if row.get("filename", "").replace("\\", "/") in selected]
        fields = reader.fieldnames
    if not fields or len(rows) != len(selected):
        missing = sorted(selected - {row.get("filename", "").replace("\\", "/") for row in rows})
        raise SystemExit(f"missing LPC credit rows: {missing}")
    with path.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    here = Path(__file__).resolve().parent
    mod = here.parent
    parser = argparse.ArgumentParser()
    parser.add_argument("lpc", type=Path, help="Universal-LPC-Spritesheet-Character-Generator checkout")
    parser.add_argument("--out", type=Path, default=mod / "assets" / "spr_lpc_test.bin")
    parser.add_argument("--preview-dir", type=Path, default=here)
    args = parser.parse_args()
    people = {name: cells(args.lpc.resolve(), layers_for(name)) for name in CHARACTERS}
    write_spr1(args.out, people["test"])
    for name, frames in people.items():
        if name != "test":
            write_spr1(args.out.with_name(f"spr_lpc_{name}.bin"), frames)
    write_credits(args.lpc.resolve(), args.out.with_name("lpc_runtime_credits.csv"))
    previews(args.preview_dir, people["test"], people)
    print(f"LPC set: {args.out.parent} ({len(people)} characters, 4 directions, 1 idle + 9 walk frames, {OUT_W}x{OUT_H} at 1:1)")


if __name__ == "__main__":
    main()
