#!/usr/bin/env python3
"""Copy the character-creator art (art_dk/chargen: manifest.json + the packed CGP1 layers) into assets/chargen/.
usage: import_chargen.py [art_dir]   (default ../../../../art_dk/chargen relative to the dev tree's parent)"""
import os, sys, json, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "..", "..", "..", "art_dk", "chargen")
DST = os.path.join(HERE, "..", "assets", "chargen")
os.makedirs(os.path.join(DST, "packed"), exist_ok=True)
man = json.load(open(os.path.join(SRC, "manifest.json")))
n = 0
for part in man["parts"].values():
    for st in part.values():
        if st.get("packed"):
            shutil.copy(os.path.join(SRC, st["packed"]), os.path.join(DST, st["packed"])); n += 1
        for k in ("bin", "png"): st.pop(k, None)          # the engine reads the packed files only
        st.pop("bytes_bin", None)
man.get("format_notes", {}).pop("bin", None); man.get("totals", {}).pop("bytes_bin", None)
json.dump(man, open(os.path.join(DST, "manifest.json"), "w"), indent=1)
print("chargen: %d packed layers + manifest -> %s" % (n, DST))
