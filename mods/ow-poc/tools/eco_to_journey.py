#!/usr/bin/env python3
"""Builds the runtime economy data of Journey Mode from the design content (journey_content/economy).

  python3 tools/eco_to_journey.py [ECONOMY_DIR]

Writes assets/economy.json (tier tables, the level curve, drop odds, the local card pools, the shops)
and assets/lang/<en|pt>/economy.json (the strings the screens show).  Nothing else is touched: the
story's own converter (dk_to_journey.py) owns journey.json and ui.json, so the two can run in any order.

The design files stay the source of truth; edit journey_content/economy/src/ and regenerate them with
their own generator first (gen_economy.py), then run this.
"""
import collections, csv, io, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(MOD))
args = [a for a in sys.argv[1:] if not a.startswith("-")]
ECO = args[0] if args else os.path.join(REPO, "journey_content", "economy")
RARITIES = ("C", "B", "A", "S")
# Only the places the game can reach are copied: the runtime reader makes a node per JSON value, and
# the whole catalogue (10 pools, 9 shops) is 136 KB of it for areas the story does not open yet.  Add
# an id here when its part lands; "--all" writes everything (for a data check, not for the game).
POOLS_NOW = ("village", "harbor", "ship", "beach", "forest", "mountain", "meadow", "desert", "fair", "gate", "hall")
SHOPS_NOW = ("village", "harbor", "ship", "beach", "forest", "mountain", "meadow", "desert", "fair", "gate", "hall")


def load(name):
    with open(os.path.join(ECO, name), encoding="utf-8") as f:
        return json.load(f)


def main():
    every = "--all" in sys.argv[1:]
    eco = load("economy.json")
    rarity = load("card_rarity.json")
    gang = load("gang.json")
    arenas = load("arenas.json")
    decks = load("decks_economy.json")
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

    # The arena exclusives of every pool (also the places not open yet): card id -> the arena whose ring alone drops it
    out["exclusive"] = {str(e["id"]): p["id"] for p in pools["pools"] for e in p["entries"] if e.get("exclusive")}

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

    out["gang"] = gang_runtime(gang, every)
    out["arenas"] = arenas_runtime(arenas, every)
    added = write_duelists(gang, arenas, decks, out, every)

    write(os.path.join(MOD, "assets/economy.json"), out)
    merge_into_story(out)
    print("duelists: %d written (%d of the gang, %d of the arenas)" %
          (len(added), len(gang["members"]), len(added) - len(gang["members"])))

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
    # The arena's door, so it is a thing on the ground and not an invisible spot.  It borrows the
    # cistern's hatch art (one piece, drawn for every "hatch" object of the area) and carries no talk
    # of its own: pressing X there is handled by the arena itself (Arena_DoorAt in ow_poc.c).
    doors = 0
    objects = story.setdefault("objects", [])
    have = {o.get("id") for o in objects}
    for sid, a in out["arenas"].items():
        anchor = a["entry_anchor"]          # "harbor.arena_door": several places have an arena_door
        oid = "arena_door_%s" % sid
        if oid in have:
            continue
        objects.append({"id": oid, "anchor": anchor, "prop": "hatch", "reach": 0})
        doors += 1

    write(path, story)
    print("journey.json: shop opened from %d idle rules (%s); %d arena door(s) added" %
          (len(touched), ", ".join(touched) or "none", doors))


def write(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, ensure_ascii=True, sort_keys=False)
        f.write("\n")




# ---------------------------------------------------------------- the gang and the arenas
# The gang roams every open-air area, so all seven of them come across; the arenas are tied to a
# place, so only the ones whose place exists are written, as the pools and shops are.
ARENAS_NOW = ("village", "harbor", "ship", "beach", "forest", "mountain", "meadow", "desert", "fair", "gate", "hall")
# No art for the gang yet, so each is drawn from a villager's sheet in a colour of his own.  Sand and
# rag tones, in the order the design lists them: dusty pup, scrap junker, fang brute, viper, hex
# lady, granite brute, old boss.  Replace this when the sprites exist.
GANG_TINTS = [0xC8B48C, 0x9A9AA6, 0xB07050, 0x7FA86A, 0xA07AB4, 0x8C8C8C, 0xD0A040]


def gang_runtime(gang, every):
    """What the mod needs to run the Dune Jackals: who they are, how often they come, what they take.

    The design has them spawn off the edge of the view when a countdown ends.  They are placed in the
    area instead - the player sees them loitering about - and the countdown is what makes one of them
    walk over and pick his excuse, so the timing the design balanced is unchanged.
    """
    amb = gang["ambush"]
    stakes = gang["stakes"]
    members = [m for m in gang["members"] if every or True]
    return {
        "name_id": gang["gang"]["name_id"],
        "members": [{
            "id": m["id"],
            "duelist": m["duelist"]["id"],
            "name": m["duelist"]["name"],
            "tier": m["gang_tier"],
            "difficulty": m["difficulty_tier"],
            "tint": GANG_TINTS[i % len(GANG_TINTS)],
            "taunt_id": m["taunt_id"],
            "win_id": m["win_id"],
            "lose_id": m["lose_id"],
        } for i, m in enumerate(members)],
        "tier_by_level": [{"from": r["level"][0], "to": r["level"][1], "weights": r["weights"]}
                          for r in gang["tier_by_level"]],
        "stakes": {
            "pct": stakes["percent_by_gang_tier"],
            "min": stakes["min_by_gang_tier"],
            "max": stakes["max_by_gang_tier"],
            "first_three": stakes["first_three_ambushes_factor"],
            "relief_after": stakes["loss_streak_relief"]["after_losses"],
            "relief_stolen": stakes["loss_streak_relief"]["stolen_factor"],
            "relief_cooldown": stakes["loss_streak_relief"]["cooldown_factor"],
            "truce": stakes["truce_factor"],
            "recover": stakes["recover_on_win"],
        },
        "ambush": {
            "min_purse": amb["min_purse"],
            # the countdown is kept in 30ths of a second of walking, as the save does
            "cooldown_min": int(amb["cooldown_walk_seconds"]["min"] * 30),
            "cooldown_max": int(amb["cooldown_walk_seconds"]["max"] * 30),
            "warmup": int(amb["tutorial"]["warmup_walk_seconds"] * 30),
            "stage_min": amb["tutorial"]["no_ambush_before_stage"],
            "first_member": amb["tutorial"]["first_ambush"]["member"],
            "first_cap": amb["tutorial"]["first_ambush"]["stake_cap_coins"],
            "grace_win": int(amb["grace_walk_seconds"]["after_win"] * 30),
            "grace_loss": int(amb["grace_walk_seconds"]["after_loss"] * 30),
            "grace_area": int(amb["grace_walk_seconds"]["after_area_change"] * 30),
            "grace_scene": int(amb["grace_walk_seconds"]["after_scene_or_menu"] * 30),
            "areas": amb["eligible_areas"],
            "frequency": amb["frequency_by_area"],
        },
    }


def arenas_runtime(arenas, every):
    fighters = {f["id"]: f for f in arenas["fighters"]}
    out = {}
    for slot, a in enumerate(arenas["arenas"]):
        if not every and a["id"] not in ARENAS_NOW:
            continue
        out[a["id"]] = {"slot": slot,
            "name_id": "names.arenas." + a["id"], "tip_id": a["tip_id"], "keeper": a.get("keeper", ""),
            "entry_anchor": a["entry_anchor"], "interior_area": a["interior_area"],
            "pool": a["pool"], "fee": a["fee"], "unlock": a["unlock"],
            "ladder": [{
                "rung": r["rung"],
                "fighter": r["fighter"],
                "duelist": fighters[r["fighter"]]["duelist"]["id"] if r["fighter"] in fighters else "",
                "name": fighters[r["fighter"]]["name"] if r["fighter"] in fighters else r["fighter"],
                "text_id": fighters[r["fighter"]]["text_id"] if r["fighter"] in fighters else "",
                "tier": r["tier"], "champion": 1 if r["champion"] else 0,
                "coins": r["coins"], "xp_base": r["xp_base"], "drops": r["drops"],
            } for r in a["ladder"]],
            "first_clear": a["first_clear"], "repeat_clear": a["repeat_clear"],
        }
    return out


def write_duelists(gang, arenas, decks, out, every):
    """The duelists the gang and the arenas need, and their decks.

    The port makes a duelist from duelists/<id>.json: `copy` is the disc opponent whose face, AI and
    drops it borrows, `name` is its own.  Its deck goes in mod.json under that name, the way the
    villagers' decks already do.  The mod asks the host for the id each of them got this run
    (duelist_id), because that depends on which mods are applied and in what order.

    Only the ones the game can reach are written: a duelist here is a row on the Free Duel grid too.
    """
    folder = os.path.join(MOD, "duelists")
    if not os.path.isdir(folder):
        os.mkdir(folder)
    wanted = []
    for m in gang["members"]:
        wanted.append(m["duelist"])
    arena_ids = set()
    for a in arenas["arenas"]:
        if not every and a["id"] not in ARENAS_NOW:
            continue
        for r in a["ladder"]:
            arena_ids.add(r["fighter"])
    for f in arenas["fighters"]:
        if f["id"] in arena_ids:
            wanted.append(f["duelist"])

    mod = os.path.join(MOD, "mod.json")
    with open(mod, encoding="utf-8") as fh:
        manifest = json.load(fh, object_pairs_hook=collections.OrderedDict)
    kept, missing = [], []
    for d in wanted:
        path = os.path.join(folder, "%s.json" % d["id"])
        write(path, collections.OrderedDict([("copy", d["copy"]), ("name", d["name"])]))
        kept.append(d["id"])
        deck = decks["decks"].get(d["name"])
        if not deck:
            missing.append(d["name"])
            continue
        entry = collections.OrderedDict([("fixed", True)])
        entry.update(deck["cards"])
        manifest["decks"][d["name"]] = entry
    with io.open(mod, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    # a duelist written before but no longer wanted would stay on the grid for ever
    for name in sorted(os.listdir(folder)):
        if name.startswith("eco_") and name.endswith(".json") and name[:-5] not in kept:   # dk_* are the story's
            os.remove(os.path.join(folder, name))
            print("removed duelists/%s" % name)
    for name in sorted(set(missing)):
        print("warning: no deck for", name)
    return kept


if __name__ == "__main__":
    main()
