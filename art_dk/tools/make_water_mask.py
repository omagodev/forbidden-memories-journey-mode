#!/usr/bin/env python3
"""Harbor sea region for the 6-frame water shimmer (same idea as painted_work/make_water.py): blue-dominant pixels inside the sea polygon."""
import os, numpy as np
from PIL import Image, ImageDraw
from PIL import ImageFilter
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = 1.25
pic = np.array(Image.open(os.path.join(R, "backgrounds", "dk_harbor_1280x720.jpg")).convert("RGB")).astype(int)
poly = Image.new("L", (1280, 720), 0)
ImageDraw.Draw(poly).polygon([(x*S, y*S) for x, y in [(660,0),(1024,0),(1024,576),(815,576),(800,520),(770,400),(765,330),(745,275),(715,175),(685,100)]], fill=255)
m = (np.array(poly) > 0) & (pic[..., 2] > pic[..., 0] + 25) & (pic[..., 2] > 90)
mi = Image.fromarray((m*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.MinFilter(9))
m = np.array(mi) > 127
Image.fromarray((m * 255).astype(np.uint8)).save(os.path.join(R, "masks", "harbor_water_mask_1280x720.png"))
ov = pic.copy(); ov[m] = (0.5 * ov[m] + 0.5 * np.array([255, 0, 255])).astype(int)
Image.fromarray(ov.astype(np.uint8)).save(os.path.join(R, "masks", "harbor_water_overlay.png")); print("water px", int(m.sum()))
