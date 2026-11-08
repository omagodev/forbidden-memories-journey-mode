#!/usr/bin/env python3
"""Check the NPC walk cycles: every step of frames 1..4 must change the silhouette of the one before it (looping back to 1) by
at least MIN texels in each direction where the sheet has legs to move, the figure must stay inside the 48x62 cell with its
feet on the ground line, and idle (frame 0) must match the committed sheet (pass --base REV to compare against git)."""
import glob, os, subprocess, sys, tempfile
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from walk_strides import read, bbox, SKIP
MIN = 40
def main():
    base = sys.argv[sys.argv.index("--base") + 1] if "--base" in sys.argv else None
    bad = 0
    for p in sorted(glob.glob(os.path.join(os.path.dirname(__file__), "..", "assets", "spr_*.bin"))):
        n = os.path.basename(p)
        if any(s in n for s in SKIP): continue
        _, nf, cw, ch, fx, fy, c = read(p)
        if nf != 5: continue
        ref = None
        if base:
            blob = subprocess.run(["git", "show", "%s:mods/ow-poc/assets/%s" % (base, n)], capture_output=True).stdout
            if blob:
                t = tempfile.NamedTemporaryFile(delete=False); t.write(blob); t.close(); ref = read(t.name)[6]; os.unlink(t.name)
        worst = []
        for d in range(4):
            seq = [1, 2, 3, 4, 1]
            diffs = [int(((c[d, a][0] == 0) ^ (c[d, b][0] == 0)).sum()) for a, b in zip(seq, seq[1:])]
            worst.append(min(diffs))
            for f in range(nf):
                x0, y0, x1, y1 = bbox(c[d, f][0])
                if y1 > fy + 1 or y1 < fy - 3 or x0 < 0 or x1 >= cw: print("FAIL %s dir %d frame %d off the ground/cell (%d..%d, %d..%d)" % (n, d, f, x0, x1, y0, y1)); bad += 1
            if ref is not None and not ((ref[d, 0][0] == c[d, 0][0]).all() and (ref[d, 0][2] == c[d, 0][2]).all()):
                print("FAIL %s dir %d: idle changed" % (n, d)); bad += 1
        if min(worst) < MIN: print("FAIL %s: a walk step changes only %d texels" % (n, min(worst))); bad += 1
        else: print("ok   %s  smallest step change per direction %s" % (n, worst))
    print("%d failures" % bad)
    return 1 if bad else 0
if __name__ == "__main__":
    sys.exit(main())
