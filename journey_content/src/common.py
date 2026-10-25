"""Shared helpers for the Journey Mode content builders."""
import csv, os, re

CATALOG = "/workspace/study/fmrecomp/fork/notes/card-catalog.csv"

# speaker key -> display data. portrait: game duelist/portrait id (0xFE = no portrait,
# 0xF0.. = custom portrait slots of the port).
SPEAKERS = {
    "atos":          {"name": "{name}",        "short": "{name}",   "portrait": 39,   "note": "Player. Portrait 39 is the custom Atos face (duelist 39 is Duel Master K in the port, so it needs a custom slot)."},
    "simon":         {"name": "Simon Muran",   "short": "Simon",    "portrait": 1},
    "teana":         {"name": "Teana",         "short": "Teana",    "portrait": 2},
    "jono":          {"name": "Jono",          "short": "Jono",     "portrait": 3},
    "guard":         {"name": "Guard",         "short": "Guard",    "portrait": 5},
    "rex":           {"name": "Rex Raptor",    "short": "Rex",      "portrait": 9},
    "weevil":        {"name": "Weevil",        "short": "Weevil",   "portrait": 10},
    "seto":          {"name": "Seto",          "short": "Seto",     "portrait": 7},
    "mage_soldier":  {"name": "Mage Soldier",  "short": "Soldier",  "portrait": 18},
    "heishin":       {"name": "Heishin",       "short": "Heishin",  "portrait": 8},
    "mai":           {"name": "Mai",           "short": "Mai",      "portrait": 11},
    "keith":         {"name": "Bandit Keith",  "short": "Keith",    "portrait": 12},
    "shadi":         {"name": "Shadi",         "short": "Shadi",    "portrait": 13},
    "pegasus":       {"name": "Pegasus",       "short": "Pegasus",  "portrait": 15},
    "isis":          {"name": "Isis",          "short": "Isis",     "portrait": 16},
    "prince":        {"name": "Prince",        "short": "Prince",   "portrait": 240,  "note": "Custom portrait (cports slot 5), not a game duelist."},
    "ocean_mage":    {"name": "Ocean Mage",    "short": "Ocean Mage","portrait": 21},
    "secmeton":      {"name": "High Mage Secmeton",  "short": "H.M. Secmeton",  "portrait": 22},
    "anubisius":     {"name": "High Mage Anubisius", "short": "H.M. Anubisius", "portrait": 24},
    "atenza":        {"name": "High Mage Atenza",    "short": "H.M. Atenza",    "portrait": 26},
    "martis":        {"name": "High Mage Martis",    "short": "H.M. Martis",    "portrait": 28},
    "kepura":        {"name": "High Mage Kepura",    "short": "H.M. Kepura",    "portrait": 30},
    "labyrinth_mage":{"name": "Labyrinth Mage","short": "Labyrinth","portrait": 31},
    "sebek":         {"name": "Guardian Sebek","short": "G. Sebek", "portrait": 33},
    "neku":          {"name": "Guardian Neku", "short": "G. Neku",  "portrait": 34},
    "seto2":         {"name": "Seto",          "short": "Seto",     "portrait": 32,   "note": "Seto 2nd face; falls back to 7."},
    "heishin2":      {"name": "Heishin",       "short": "Heishin",  "portrait": 35,   "note": "Heishin 2nd face; falls back to 8."},
    "seto3":         {"name": "Seto",          "short": "Seto",     "portrait": 36,   "note": "Seto 3rd face (shadow-touched); falls back to 7."},
    "darknite":      {"name": "DarkNite",      "short": "DarkNite", "portrait": 37},
    "nitemare":      {"name": "Nitemare",      "short": "Nitemare", "portrait": 38},
    "cockatiel":     {"name": "Cockatiel",     "short": "Cockatiel","portrait": 241,  "note": "New custom portrait (cports slot 6). See cockatiel.json."},
    "mirror":        {"name": "Atos Vinicius", "short": "Atos V.",  "portrait": 242,  "note": "Mirror duelist; custom portrait (cports slot 7), may reuse the Atos face."},
    "narrator":      {"name": "(label)",       "short": "(label)",  "portrait": 254,  "note": "No portrait. Every narrator page carries its own 'label'."},
}

def pg(sp, text, ask=False):
    assert sp in SPEAKERS and sp != "narrator", sp
    d = {"speaker": sp, "text": text}
    if ask: d["ask"] = True
    return d

def nar(label, text):
    return {"speaker": "narrator", "label": label, "text": text}

def obj(text):  return nar("Objective", text)
def rew(text):  return nar("Reward", text)

def load_catalog():
    names = {}
    with open(CATALOG, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            names[row["name"]] = {"id": int(row["id"]), "type": row["type"], "level": row["level"],
                                  "atk": row["attack"], "def": row["defense"]}
    return names
