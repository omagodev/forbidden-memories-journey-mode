#!/usr/bin/env python3
"""Checks decks.json: every card name exists in the FM card catalog, 40 cards, max 3 copies, no ritual-only cards.
Usage: python3 check_decks.py [decks.json] [card-catalog.csv] [cards.c]
Exit code 0 = all good."""
import csv, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
DECKS = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "decks.json")
CAT = sys.argv[2] if len(sys.argv) > 2 else "/workspace/study/fmrecomp/fork/notes/card-catalog.csv"
CARDS_C = sys.argv[3] if len(sys.argv) > 3 else "/workspace/study/fmrecomp/fork/src/pc/cards/cards.c"
TABLES_C = os.path.join(os.path.dirname(CARDS_C), "tables.c")
# ids that only exist through a Ritual / fusion-only path on the disc: never put in AI decks
RITUAL_MONSTERS = {356, 357, 360, 362, 364, 374, 380} | set(range(701, 723)) | {21}   # plus every card of type Ritual (read from the catalog)

def norm(s): return re.sub(r"[^a-z0-9]", "", s.lower())

def main():
    names = {}; RITUAL_ONLY = set(RITUAL_MONSTERS)
    with open(CAT, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            names[row["name"]] = int(row["id"])
            if row["type"] == "Ritual": RITUAL_ONLY.add(int(row["id"]))
    by_norm = {}
    for n in names: by_norm.setdefault(norm(n), []).append(n)
    dups = {k: v for k, v in by_norm.items() if len(v) > 1}
    if dups: print("note: catalog names that collide when normalised (port matching ignores case/punctuation):", dups)
    # duelist names the port knows
    duelists = set()
    try:
        src = open(TABLES_C, encoding="utf-8").read()
        block = src[src.index("Tables_DuelistNames[TABLES_DUELIST_COUNT]"):]
        block = block[:block.index("};")]
        duelists = set(re.findall(r'"([^"]+)"', block))
    except Exception as e:
        print("warning: could not read duelist names:", e)
    data = json.load(open(DECKS, encoding="utf-8"))
    custom = {c["name"] for c in data.get("custom_cards", [])}
    # sanity: the card registry file itself must be present (names come from the disc at run time)
    if not os.path.exists(CARDS_C): print("warning: cards.c not found:", CARDS_C)
    errors = 0; warnings = 0
    def err(m):
        nonlocal errors; errors += 1; print("ERROR:", m)
    def warn(m):
        nonlocal warnings; warnings += 1; print("warning:", m)
    seen_names = set()
    for key, d in data["decks"].items():
        for field, allow_custom in (("cards", False), ("cards_with_custom_pack", True)):
            if field not in d: continue
            cards = d[field]
            total = sum(cards.values())
            if total != 40: err("%s.%s has %d cards (need 40)" % (key, field, total))
            if d.get("total") not in (None, sum(d["cards"].values())): err("%s total field is wrong" % key)
            for name, n in cards.items():
                if not isinstance(n, int) or n < 1: err("%s: bad count for %s" % (key, name))
                if n > 3: err("%s: %s x%d (max 3)" % (key, name, n))
                if name in custom and allow_custom: continue
                if name not in names:
                    hint = by_norm.get(norm(name))
                    err("%s: unknown card %r%s" % (key, name, " (did you mean %r?)" % hint[0] if hint else ""))
                elif names[name] in RITUAL_ONLY: err("%s: %s is ritual-only/ritual card" % (key, name))
                seen_names.add(name)
            if field == "cards" and len(cards) < 14: err("%s: fewer than 14 distinct cards" % key)
        duelist = d.get("duelist")
        if duelists and duelist not in duelists and duelist not in ("Atos Vinicius", "Cockatiel"):
            err("%s: duelist %r is not a disc duelist name" % (key, duelist))
    for c in data.get("custom_cards", []):
        if c["name"] in names: warn("custom card %r shares a name with a disc card" % c["name"])
    print("%d decks, %d distinct disc cards used, %d errors, %d warnings" % (len(data["decks"]), len(seen_names), errors, warnings))
    return 1 if errors else 0

if __name__ == "__main__":
    sys.exit(main())
