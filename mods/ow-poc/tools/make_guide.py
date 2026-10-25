#!/usr/bin/env python3
"""Write the objective guide into assets/journey.json.

"guide" is a list of rules in the order of the objectives: the first one whose "when" holds names where
the player should go (see jm_guide.c).  A target is {"npc": id}, {"tile": [x, z]} or {"rect": [x0, z0, x1,
z1]} in tiles.  Usage: make_guide.py [journey.json]
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from make_world import origin  # noqa: E402


def room_rect(area, x0, z0, x1, z1):
    ox, oy = origin(area - 8)
    return [ox + x0, oy + z0, ox + x1, oy + z1]


def npc(i, **when):
    return dict(when=when, npc=i)


def rect(r, **when):
    return dict(when=when, rect=r)


SIX = ["ocean_mage", "secmeton", "anubisius", "atenza", "martis", "kepura"]
G = [
    npc("simon", stage_lt=2),
    rect([0, 17, 63, 19], stage_lt=3),                              # across the river: the line row 19
    npc("rex", stage_lt=4, lacks=["rex_won"]),
    npc("weevil", stage_lt=4, lacks=["weevil_won"]),
    rect([0, 0, 63, 2], stage_lt=4),                                # the stone portal, rows above 3
    npc("seto", stage_lt=5, lacks=["seto_won"]),
    rect([0, 0, 63, 3], stage_lt=5),                                # the palace door
    npc("heishin", stage_lt=6, lacks=["heishin_won"]),
    rect([0, 24, 63, 24], stage_lt=6),                              # the glowing throne
    npc("mai", stage_lt=7, lacks=["mai_won"]),
    npc("keith", stage_lt=7, lacks=["keith_won"]),
    npc("shadi", stage_lt=7, lacks=["shadi_won"]),
    npc("pegasus", stage_lt=7, lacks=["pegasus_won"]),
    rect([0, 57, 63, 58], stage_lt=7),                              # the castle gate line
]
for i in SIX:
    G.append(npc(i, stage_ge=7, stage_lt=8, lacks=[i + "_won" if i != "ocean_mage" else "ocean_mage_won"]))
G.append(rect(room_rect(8, 14, 21, 17, 21), stage_ge=7, stage_lt=8))
for i, f in (("labyrinth_mage", "labyrinth_mage_won"), ("sebek", "sebek_won"), ("neku", "neku_won"),
             ("seto2", "seto2_won"), ("heishin2", "heishin2_won")):
    G.append(npc(i, stage_ge=8, stage_lt=9, lacks=[f]))
G.append(rect(room_rect(14, 15, 3, 16, 3), stage_ge=8, stage_lt=9))
for i, f in (("seto3", "seto3_won"), ("darknite", "darknite_won"), ("nitemare", "nitemare_won")):
    G.append(npc(i, stage_ge=9, stage_lt=10, lacks=[f]))


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "assets", "journey.json")
    j = json.load(open(path))
    j["guide"] = G
    json.dump(j, open(path, "w"), separators=(",", ":"))
    print("journey.json: %d guide rules" % len(G))


if __name__ == "__main__":
    main()
