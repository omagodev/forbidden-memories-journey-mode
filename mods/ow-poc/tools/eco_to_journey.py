#!/usr/bin/env python3
"""Builds the runtime economy data of Journey Mode from the design content (journey_content/economy).

  python3 tools/eco_to_journey.py [ECONOMY_DIR]

Writes assets/economy.json (tier tables, the level curve, drop odds, the local card pools, the shops)
and assets/lang/<en|pt>/economy.json (the strings the screens show).  Nothing else is touched: the
story's own converter (dk_to_journey.py) owns journey.json and ui.json, so the two can run in any order.

The design files stay the source of truth; edit journey_content/economy/src/ and regenerate them with
their own generator first (gen_economy.py), then run this.
"""
import csv, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(MOD))
args = [a for a in sys.argv[1:] if not a.startswith("-")]
ECO = args[0] if args else os.path.join(REPO, "journey_content", "economy")
RARITIES = ("C", "B", "A", "S")
# Only the places the game can reach are copied: the runtime reader makes a node per JSON value, and
# the whole catalogue (10 pools, 9 shops) is 136 KB of it for areas the story does not open yet.  Add
# an id here when its part lands; "--all" writes everything (for a data check, not for the game).
POOLS_NOW = ("village",)
SHOPS_NOW = ("village",)


def load(name):
    with open(os.path.join(ECO, name), encoding="utf-8") as f:
        return json.load(f)


def main():
    every = "--all" in sys.argv[1:]
    eco = load("economy.json")
    rarity = load("card_rarity.json")
    pools = load("card_pools.json")
    shops = load("shops.json")
    levels = load("levels.json")

    tiers = eco["tiers"]
    out = {
        "schema": "journey-economy-runtime/1",
        "cap": eco["currency"]["cap"],
        "start": eco["currency"]["start"],
        "cap_level": levels["cap"],
        "tiers": {"coins": tiers["win_coins"], "xp": tiers["win_xp"], "nominal": tiers["nominal_level"]},
        # the context multiplier as whole percent, so the mod needs no floating point
        "ctx": {k: int(round(v * 100)) for k, v in eco["formulas"]["context_mult"].items()},
        # xp = win_xp[tier] * clamp(1 + slope*(nominal - level), lo, hi), all in percent
        "xp_mod": {"slope": 12, "lo": 20, "hi": 180, "loss_pct": 25},
        "levels": [{"xp": r["xp_total"], "rank": r["rank"], "shop": r["shop_tier"],
                    "shift": r["drop_shift"], "bonus": r["coin_bonus_pct"]} for r in levels["table"]],
        "ranks": levels["ranks"],
        "prices": dict(eco["prices"]["weq"], sell_rate=eco["prices"]["sell_rate"],
                       sell_base=eco["prices"]["sell_base_win"], round_to=eco["prices"]["round_to"]),
        "drops": {"ctx": eco["drop_odds"]["contexts"], "count": eco["drop_odds"]["cards_per_context"]},
        "duels": {d["id"]: d["tier"] for d in eco["rewards_story"]["duels"]},
        "quest_coins": eco["rewards_story"]["quest_coins"],

        "area_pool": {k: v for k, v in pools["rules"]["area_to_pool"].items()
                      if v and (every or v in POOLS_NOW)},
    }

    # The pools: the card id, its rarity, its weight and the level it appears at.  The card's name is
    # not copied: the game has its own (localised) card names and the screens read those.
    out["pools"] = {}
    for p in pools["pools"]:
        if not every and p["id"] not in POOLS_NOW: continue
        out["pools"][p["id"]] = [{"i": e["id"], "r": e["rarity"], "w": e["weight"], "l": e["min_level"],
                                  **({"a": 1} if e.get("arena_only") else {})} for e in p["entries"]]

    # The shops, as the screen needs them.  Card names stay here: a stall lists a fixed stock.
    out["shops"] = {}
    for s in shops["shops"]:
        if not every and s["id"] not in SHOPS_NOW: continue
        stock = s["stock"]
        out["shops"][s["id"]] = {
            "name_id": s["name_id"], "pool": s["pool"], "tier": s["tier"], "price_win": s["price_win"],
            "anchor": s["anchor"], "keeper": s["keeper"]["id"], "greet_id": s["keeper"].get("greet_id", ""),
            "open": s.get("open", {}),
            "always": [{"i": e.get("id"), "n": e["card"], "r": e["rarity"], "p": e["price"], "l": e.get("min_level", 1)}
                       for e in stock.get("always", [])],
            "rotating": stock.get("rotating", []),
            "limited": [{"i": e.get("id"), "n": e.get("card"), "r": e.get("rarity"), "p": e.get("price"),
                         "l": e.get("min_level", 1), "bit": e.get("bit")} for e in stock.get("limited", [])],
            "packs": stock.get("packs", []),
            "rotation": s.get("rotation", {}),
        }

    # ids for the cards the design names only by name (the shops' stock, the rarity table)
    by_name = {}
    for p in pools["pools"]:
        for e in p["entries"]:
            by_name[e["card"]] = e["id"]
    catalog = os.path.join(os.path.dirname(MOD), os.pardir, "notes", "card-catalog.csv")
    catalog = os.environ.get("FM_CATALOG", os.path.normpath(catalog))
    with open(catalog, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            by_name.setdefault(r["name"], int(r["id"]))

    # What a card is worth when sold, and what may not be sold: its class by card id, the design's
    # banned list, and the cards the story hands out (which the player must keep).
    out["sell"] = {}
    for name, cls in rarity["rarity"].items():
        if name in by_name:
            out["sell"][str(by_name[name])] = cls
    out["banned"] = sorted(by_name[n] for n in rarity["banned"] if n in by_name)
    out["protected"] = sorted(by_name[n] for n in eco["rewards_story"]["protected_cards"] if n in by_name)
    missing = []
    for sid, s in out["shops"].items():
        for group in ("always", "limited"):
            for e in s[group]:
                if e.get("i") is None:
                    e["i"] = by_name.get(e["n"])
                    if e["i"] is None:
                        missing.append("%s: %s" % (sid, e["n"]))

    write(os.path.join(MOD, "assets/economy.json"), out)
    merge_into_story(out)

    for code in ("en", "pt"):
        src = load(os.path.join("en", "economy.en.json") if code == "en" else os.path.join("pt", "economy.pt.json"))
        write(os.path.join(MOD, "assets/lang/%s/economy.json" % code),
              {k: src[k] for k in ("names", "ui", "dialogue") if k in src})

    print("economy.json: %d pools, %d shops, %d levels, %d story duel tiers, %d card classes "
          "(%d banned, %d protected)" % (len(out["pools"]), len(out["shops"]), len(out["levels"]),
          len(out["duels"]), len(out["sell"]), len(out["banned"]), len(out["protected"])))
    for m in sorted(set(missing)):
        print("warning: no card id for", m)


def merge_into_story(out):
    """Opens a keeper's stall from her small talk.

    The story data is generated by dk_to_journey.py and is not edited by hand, so the shop is wired in
    here instead, as the design's note says ("the converter merges these effects into existing rules").
    A keeper's idle rules - the ones that are a plain stage range, not a beat of her own quest and not a
    duel - get an "open_shop" result, so her stall opens once her line has been read.  Run this after
    dk_to_journey.py: that tool rewrites journey.json from scratch and would drop the merge.
    """
    path = os.path.join(MOD, "assets/journey.json")
    with open(path, encoding="utf-8") as f:
        story = json.load(f)
    keepers = {s["keeper"]: (sid, s.get("open", {}).get("stage_min", 0)) for sid, s in out["shops"].items()}
    touched = []
    for npc in story.get("npcs", []):
        if npc.get("id") not in keepers:
            continue
        shop_id, stage_min = keepers[npc["id"]]
        for rule in npc.get("talk", []):
            when = rule.get("when") or {}
            if rule.get("duel") or rule.get("effects"):
                continue
            if any(k in when for k in ("needs", "has", "lacks", "lacks_any")):
                continue                        # a beat of her own quest, not small talk
            if when.get("stage_ge", 0) < stage_min:
                continue
            rule["effects"] = {"open_shop": shop_id}
            touched.append("%s/%s" % (npc["id"], rule.get("scene", "?")))
    write(path, story)
    print("journey.json: shop opened from %d idle rules (%s)" % (len(touched), ", ".join(touched) or "none"))


def write(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, ensure_ascii=True, sort_keys=False)
        f.write("\n")


if __name__ == "__main__":
    main()
