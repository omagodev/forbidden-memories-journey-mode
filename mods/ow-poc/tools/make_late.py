#!/usr/bin/env python3
"""Add chapters 6 to 8 (stages 7 to 9, and the epilogue) to assets/journey.json.

The first five chapters are written by hand in journey.json.  The last three are
laid out on the eight rooms that make_world.py builds, with the people, duels,
locks, doors and objectives of the story content file, so this script reads that
file (journey_content/story.json) and the card list (notes/card-catalog.csv) and
writes everything it adds with "late": 1.  Running it again replaces its own
additions.

Usage: make_late.py story_content.json card-catalog.csv [journey.json]
"""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from make_world import origin, ROOM_W, ROOM_H  # noqa: E402

SIX = ["ocean_mage_won", "secmeton_won", "anubisius_won", "atenza_won", "martis_won", "kepura_won"]
FLAGS = SIX + ["labyrinth_mage_won", "sebek_won", "neku_won", "seto2_won", "altar_scene_seen", "heishin2_won",
               "seto3_won", "darknite_won", "nitemare_won", "ending_home", "ending_stay"]

# area, local tile, mesh (an assets/*.n2 name), duelist id, portrait speaker
NPCS = {
    "simon_crossroads": (8, (13.5, 14.5), "Wizard", 0, "simon"),
    "ocean_mage": (9, (16.0, 13.5), "Pirate_Male", 21, None),
    "secmeton": (9, (16.0, 5.5), "OldClassy_Male", 22, None),
    "anubisius": (10, (16.0, 6.5), "Goblin_Male", 24, None),
    "atenza": (11, (16.0, 4.5), "Viking_Male", 26, None),
    "martis": (12, (16.0, 7.5), "Worker_Male", 28, None),
    "kepura": (13, (16.0, 10.5), "Witch", 30, None),
    "labyrinth_mage": (14, (12.5, 18.0), "Wizard", 31, None),
    "sebek": (14, (13.5, 13.5), "Soldier_Male", 33, None),
    "neku": (14, (13.5, 9.5), "Ninja_Male", 34, None),
    "seto2": (14, (13.5, 5.5), "Knight_Golden_Male", 32, "seto"),
    "heishin2": (14, (16.0, 6.5), "Doctor_Male_Old", 35, "heishin"),
    "prince_labyrinth": (14, (19.0, 6.5), "Elf", 0, "prince"),
    "seto3": (15, (16.0, 15.0), "Knight_Golden_Male", 36, "seto"),
    "darknite": (15, (16.0, 9.0), "Zombie_Male", 37, None),
    "nitemare": (15, (16.0, 3.5), "Zombie_Male", 38, None),
}


def g(area, x, y):
    ox, oy = origin(area - 8)
    return [ox + x, oy + y]


def rect(area, x0, y0, x1, y1):
    ox, oy = origin(area - 8)
    return [ox + x0, oy + y0, ox + x1, oy + y1]


def cond(w):
    """The content file's `when` in this mod's keys."""
    out = {}
    if "stage" in w:
        lo, hi = w["stage"]
        if lo > 0:
            out["stage_ge"] = lo
        if hi < 99:
            out["stage_lt"] = hi + 1
    if w.get("flags_all"):
        out["has"] = list(w["flags_all"])
    if w.get("flags_none"):
        out["lacks"] = list(w["flags_none"])
    return out


def main():
    story = json.load(open(sys.argv[1]))
    cards = {r["name"]: int(r["id"]) for r in csv.DictReader(open(sys.argv[2]))}
    path = sys.argv[3] if len(sys.argv) > 3 else os.path.join(HERE, "..", "assets", "journey.json")
    j = json.load(open(path))
    for key in ("npcs", "locks", "spots", "triggers", "chapters", "objectives", "items", "areas"):
        j[key] = [e for e in j[key] if not e.get("late")]
    for f in FLAGS:
        if f not in j["flags"]:
            j["flags"].append(f)
    duels = {d["id"]: d for d in story["duels"]}
    items = {i["id"]: i for i in story["items"]}
    scripts = {s["id"] for s in story["scripts"]}

    # areas 8..15 (music track = (id - 0x7000) / 16)
    names = story["ui_strings"]["area_names"]
    for a in story["areas"][8:]:
        mid = (a.get("music") or {}).get("id")
        track = (int(mid, 16) - 0x7000) // 16 if mid else {10: 21, 11: 26, 14: 13, 15: 58}.get(a["id"], 20)
        j["areas"].append({"name": names[a["id"]], "track": track, "late": 1})

    # people
    for n in story["npcs"]:
        if n["id"] not in NPCS:
            continue
        area, (lx, ly), mesh, duelist, who = NPCS[n["id"]]
        e = {"id": n["id"], "name": n["name"], "mesh": mesh, "tile": g(area, lx, ly), "duelist_id": duelist,
             "portrait_id": duelist, "talk": [], "late": 1}
        if n["id"] == "heishin2":
            e["tile"] = None
            e["places"] = [{"when": {"has": ["seto2_won"], "lacks": ["heishin2_won"]}, "tile": g(area, lx, ly)}]
        if n["id"] == "prince_labyrinth":
            e["tile"] = None
            e["places"] = [{"when": {"has": ["heishin2_won"]}, "tile": g(area, lx, ly)}]
        if who and not duelist:
            e["portrait_speaker"] = who
        for r in n["dialogue_rules"]:
            if r["script"] not in scripts:
                continue
            t = {"scene": r["script"]}
            w = cond(r["when"])
            if w:
                t["when"] = w
            if r.get("duel"):
                d = duels[r["duel"]]
                t["duel"] = True
                win = {"scene": d["win_script"], "flags": [d["win_flag"]],
                       "cards": [cards[c["give_card"]] for c in d["on_win"] if "give_card" in c and c["give_card"] in cards]}
                if d["id"] == "nitemare":
                    win["then"] = "c8_choice"
                    win["cards"] = [cards["Dian Keto the Cure Master"]]
                    win["choice"] = {
                        "yes": {"scene": "ending_home", "flags": ["ending_home"], "stage": 10, "teleport": g(8, 16.0, 17.5)},
                        "no": {"scene": "ending_stay", "flags": ["ending_stay"], "stage": 10, "teleport": g(8, 16.0, 17.5)}}
                if d["id"] == "seto2":
                    win["flags"].append("altar_scene_seen")
                t["win"] = win
                t["lose"] = {"scene": d["lose_script"]}
            e["talk"].append(t)
        if n["id"] == "heishin2":
            e["talk"] = [{"when": {"lacks": ["heishin2_won"]}, "scene": "c7_altar_wake", "duel": True,
                          "win": {"scene": "c7_heishin2_win", "flags": ["heishin2_won"], "cards": [cards["Summoned Skull"]]},
                          "lose": {"scene": "c7_heishin2_lose"}}]
        j["npcs"].append(e)

    # doors and gates: solid until the flags are set
    L = j["locks"]
    L.append({"rect": rect(8, 0, 20, ROOM_W - 1, 20), "when": {"lacks_any": SIX}, "late": 1})   # the wall around the gate
    L.append({"rect": rect(9, 15, 9, 16, 9), "when": {"lacks": ["ocean_mage_won"]}, "late": 1})
    for y, f in ((16, "labyrinth_mage_won"), (12, "sebek_won"), (8, "neku_won"), (4, "heishin2_won")):
        L.append({"rect": rect(14, 15, y, 16, y), "when": {"lacks": [f]}, "late": 1})
    L.append({"rect": rect(15, 14, 12, 17, 12), "when": {"lacks": ["seto3_won"]}, "late": 1})
    L.append({"rect": rect(15, 14, 6, 17, 6), "when": {"lacks": ["darknite_won"]}, "late": 1})

    # what a locked door says when you push against it
    def spot(area, x, y, scene, when):
        return {"tile": g(area, x, y), "reach": 44, "when": when, "scene": scene, "late": 1}
    S = j["spots"]
    S.append(spot(8, 16, 19, "c6_gate_locked", {"stage_ge": 7, "stage_lt": 8, "lacks_any": SIX}))
    S.append(spot(9, 16, 10.5, "c6_secmeton_locked", {"lacks": ["ocean_mage_won"]}))
    for y, f, sc in ((17, "labyrinth_mage_won", "c7_door1_locked"), (13, "sebek_won", "c7_door2_locked"),
                     (9, "neku_won", "c7_door3_locked")):
        S.append(spot(14, 16, y, sc, {"lacks": [f]}))
    S.append(spot(14, 16, 5, "c7_altar_locked", {"lacks": ["seto2_won"]}))
    S.append(spot(15, 16, 13, "c8_hall_locked", {"lacks": ["seto3_won"]}))
    S.append(spot(15, 16, 7, "c8_stairs_locked", {"lacks": ["darknite_won"]}))

    # moves between rooms
    T = j["triggers"]
    for t in T:
        if t.get("scene") == "c5_end__c6_intro":
            t["teleport"] = g(8, 16.0, 17.5)
            t["then"] = "c6_arrival"
    pads = [(3, 9), (9, 10), (15, 11), (21, 12), (26, 13)]
    for px, area in pads:
        T.append({"when": {"stage_ge": 7}, "rect": rect(8, px, 4, px + 1, 5), "teleport": g(area, 16.0, 17.5), "late": 1})
        T.append({"when": {"stage_ge": 7}, "rect": rect(area, 15, 20, 16, 21), "teleport": g(8, px + 1.0, 7.5), "late": 1})
    T.append({"when": {"stage_ge": 7, "stage_lt": 8, "has": SIX}, "rect": rect(8, 14, 21, 17, 21),
              "scene": "c6_end__c7_intro", "set_stage": 8, "teleport": g(14, 16.0, 19.5), "late": 1})
    T.append({"when": {"stage_ge": 8, "stage_lt": 9, "has": ["heishin2_won"]}, "rect": rect(14, 15, 3, 16, 3),
              "scene": "c7_end__c8_intro", "set_stage": 9, "teleport": g(15, 16.0, 19.5), "late": 1})

    # chapters, objectives and the backpack
    for c in story["chapters"][5:8]:
        lo, hi = c["stage"]
        j["chapters"].insert(len(j["chapters"]) - 1, {"when": {"stage_ge": lo, "stage_lt": hi + 1},
                                                      "text": "Chapter %d: %s" % (c["n"], c["title"]), "late": 1})
    j["chapters"] = [c for c in j["chapters"] if c.get("text") != "Chapter 5 complete"] + [
        {"when": {"stage_ge": 10}, "text": "Epilogue", "late": 1}]
    last = [o for o in j["objectives"] if "when" not in o]          # the catch-all stays the last
    j["objectives"] = [o for o in j["objectives"] if "when" in o]
    for o in story["hud_objectives"]:
        if o["when"].get("stage", [0, 0])[0] >= 7:
            j["objectives"].append({"when": cond(o["when"]), "text": o["text"], "late": 1})
    j["objectives"] += last
    names = {i["id"]: i for i in story["items"]}
    for iid, it in names.items():
        fl = it.get("flag")
        if fl and fl in FLAGS and fl.endswith("_won") and not any(x.get("flag") == fl for x in j["items"]):
            j["items"].append({"name": it["name"], "flag": fl, "late": 1})
    json.dump(j, open(path, "w"), separators=(",", ":"))
    print("journey.json: %d npcs, %d locks, %d spots, %d triggers, %d flags" %
          (len(j["npcs"]), len(j["locks"]), len(j["spots"]), len(j["triggers"]), len(j["flags"])))


if __name__ == "__main__":
    main()
