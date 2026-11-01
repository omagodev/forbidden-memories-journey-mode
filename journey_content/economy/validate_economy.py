#!/usr/bin/env python3
"""Validates journey_content/economy/*.json (EN + PT).  Usage: python3 validate_economy.py   (exit 0 = no errors)
Checks: card ids/names exist in the FM catalog and are not banned, pools (non-empty, weights, drop odds sum to 100 for every level and context),
shop prices vs the formulas, deck legality (40 cards, max 3, >= 14 distinct, no ritual; Forbidden Memories has no deck cost), gang tiers/stakes,
arena ladders and their expected value, levels table, ASCII/charset/3x32 fit and EN/PT parity, and consistency with duelist_kingdom (flags, areas,
quests, duelist slots, 30 of 32 flags: this design adds none)."""
import csv, json, math, os, re, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
CAT = os.environ.get("FM_CATALOG", os.path.join(REPO, "notes", "card-catalog.csv"))
TABLES_C = os.environ.get("FM_TABLES_C", os.path.join(REPO, "src", "pc", "cards", "tables.c"))
DK = os.path.join(HERE, "..", "duelist_kingdom")
errs, warns, infos = [], [], []
def err(m): errs.append(m)
def warn(m): warns.append(m)
def load(rel):
    with open(os.path.join(HERE, rel), encoding="utf-8") as f: return json.load(f)

# ---------------------------------------------------------------- catalog
CARDS = {}
with open(CAT, newline="", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        r["id"] = int(r["id"]); CARDS[r["name"]] = r
def num(v):
    try: return int(v)
    except Exception: return None
for r in CARDS.values(): r["atk"], r["def"], r["cost"] = num(r["attack"]), num(r["defense"]), num(r["starchip_cost"])
MONSTER = lambda r: r["type"] not in ("Magic", "Trap", "Equip", "Ritual")
RITUAL_ONLY = {356, 357, 360, 362, 364, 374, 380, 21} | set(range(701, 723)) | {r["id"] for r in CARDS.values() if r["type"] == "Ritual"}
CUSTOM_SLOTS = {309, 318, 342, 652, 653, 657, 672, 689, 702, 720}
EXODIA = {17, 18, 19, 20, 21}
def power(r): return max(r["atk"], 0.9 * r["def"])
def banned(r):
    if r["id"] in RITUAL_ONLY or r["id"] in CUSTOM_SLOTS or r["id"] in EXODIA or r["type"] == "Trap" or r["cost"] is None: return True
    return MONSTER(r) and r["cost"] == 999999 and power(r) > 1950
def mon_class(r):
    p = power(r); return "C" if p <= 1250 else "B" if p <= 1700 else "A" if p <= 2100 else "S"
def card(name, where):
    r = CARDS.get(name)
    if not r: err("%s: unknown card %r" % (where, name))
    return r

def r5(x): return int(round(x / 5.0)) * 5
RAR = ("C", "B", "A", "S")
KINGDOM_STAR_DUELS = {"weevil", "rex_forest", "forest_mage", "keith", "mai_mountain", "mountain_mage"}   # chapter 2-4 duels that wager star chips (the home town never does)

# ---------------------------------------------------------------- load
ECO = load("economy.json"); SHOPS = load("shops.json"); POOLS = load("card_pools.json"); GANG = load("gang.json")
ARENAS = load("arenas.json"); LEVELS = load("levels.json"); DECKS = load("decks_economy.json"); RARITY = load("card_rarity.json")
TEXT = {l: load("%s/economy.%s.json" % (l, l)) for l in ("en", "pt")}
STORY = json.load(open(os.path.join(DK, "en", "story_dk.json"), encoding="utf-8"))
OUTLINE = json.load(open(os.path.join(DK, "kingdom_outline.json"), encoding="utf-8"))
OLD_DECKS = json.load(open(os.path.join(HERE, "..", "decks.json")))["decks"]
DK_DECKS = json.load(open(os.path.join(DK, "decks_dk.json")))["decks"]
for doc, sch in ((ECO, "journey-economy/1"), (SHOPS, "journey-shops/1"), (POOLS, "journey-card-pools/1"), (GANG, "journey-gang/1"),
                 (ARENAS, "journey-arenas/1"), (LEVELS, "journey-levels/1"), (DECKS, "journey-decks/1")):
    if doc.get("schema") != sch: err("schema marker %r expected, got %r" % (sch, doc.get("schema")))
try:
    src = open(TABLES_C, encoding="utf-8").read(); blk = src[src.index("Tables_DuelistNames[TABLES_DUELIST_COUNT]"):]; blk = blk[:blk.index("};")]
    BASES = set(re.findall(r'"([^"]+)"', blk)) - {"Unused"}
except Exception as e:
    BASES = set(); warn("could not read duelist names: %s" % e)
story_flags = {f["name"] for f in STORY["flags"]}
if len(story_flags) + ECO["state"]["flags_used"] > 64: err("flag budget exceeded: %d story + %d economy" % (len(story_flags), ECO["state"]["flags_used"]))
if ECO["state"]["flags_used"] != 0: err("the economy must not use story flags (the story owns all 64 bits)")
story_areas = {a["id"] for a in STORY["areas"]} | {a["id"] for a in OUTLINE["areas"]}
new_areas = {a["id"] for a in ECO["new_areas"]}
known_areas = story_areas | new_areas
story_quests = {q["id"] for q in STORY["quests"]}
used_slots = {}
for n in STORY["new_duelists"]:
    used_slots[n["slot"]] = n["id"]

# ---------------------------------------------------------------- levels
T = LEVELS["table"]
if len(T) != LEVELS["cap"]: err("levels table has %d rows, cap %d" % (len(T), LEVELS["cap"]))
cum = 0
for i, row in enumerate(T):
    L = i + 1
    if row["level"] != L: err("levels row %d has level %d" % (i, row["level"]))
    need = 10 * L + L * L if L < LEVELS["cap"] else 0
    if row["xp_to_next"] != need: err("level %d xp_to_next %d != %d" % (L, row["xp_to_next"], need))
    if row["xp_total"] != cum: err("level %d xp_total %d != %d" % (L, row["xp_total"], cum))
    cum += need
    gw = row["gang_tier_weights"]
    if abs(sum(gw.values()) - 100) > 1e-9 or any(k not in ("1", "2", "3") for k in gw): err("level %d gang weights bad" % L)
    sh = row["drop_shift"]
    if any(v < 0 for v in sh.values()): err("level %d negative drop shift" % L)
    if i and (row["shop_tier"] < T[i - 1]["shop_tier"] or row["deck_power_cap"] <= T[i - 1]["deck_power_cap"] or row["coin_bonus_pct"] < T[i - 1]["coin_bonus_pct"]): err("level %d perks go down" % L)
infos.append("levels: cap %d, total xp %d" % (LEVELS["cap"], T[-1]["xp_total"]))
def level_of(xp): return max(r["level"] for r in T if r["xp_total"] <= xp)

# ---------------------------------------------------------------- drop odds
CTX = ECO["drop_odds"]["contexts"]
for k, v in CTX.items():
    if abs(sum(v.values()) - 100) > 1e-9: err("drop context %s odds sum %s" % (k, sum(v.values())))
    if k not in ECO["drop_odds"]["cards_per_context"]: err("context %s has no card count" % k)
def effective_odds(pool, ctx, level, arena):
    """mirrors the spec: shift from C (limited by C's share), unavailable rarities fall to the next lower one"""
    o = dict(CTX[ctx]); sh = T[level - 1]["drop_shift"]; tot = sum(sh.values()); move = min(o["C"], tot)
    if tot > 0 and move > 0:
        for k in "BAS": o[k] += sh[k] * move / tot
        o["C"] -= move
    avail = {r: 0 for r in RAR}
    for e in pool["entries"]:
        if e["min_level"] <= level and (arena or not e.get("arena_only")): avail[e["rarity"]] += e["weight"]
    for r in ("S", "A", "B"):
        if avail[r] == 0:
            nxt = RAR[RAR.index(r) - 1]; o[nxt] += o[r]; o[r] = 0
    return o, avail

# ---------------------------------------------------------------- pools
pool_ids = set()
POOL = {}
for p in POOLS["pools"]:
    pid = p["id"]; pool_ids.add(pid); POOL[pid] = p
    if p["area"] not in known_areas: err("pool %s: unknown area %s" % (pid, p["area"]))
    if not p["entries"]: err("pool %s is empty" % pid); continue
    seen = set(); cnt = collections.Counter()
    for e in p["entries"]:
        w = "pool %s %s" % (pid, e.get("card"))
        r = card(e["card"], w)
        if not r: continue
        if r["id"] != e["id"]: err("%s: id %s != catalog %s" % (w, e["id"], r["id"]))
        if banned(r): err("%s is banned (ritual / custom slot / Exodia / legend / N/A)" % w)
        if e["card"] in seen: err("%s listed twice" % w)
        seen.add(e["card"])
        if e["rarity"] not in RAR: err("%s: bad rarity" % w)
        if not isinstance(e["weight"], int) or e["weight"] < 1: err("%s: bad weight" % w)
        if not 1 <= e["min_level"] <= LEVELS["cap"]: err("%s: bad min_level" % w)
        if MONSTER(r):
            if r["type"] not in p["types"]: err("%s: type %s not in the pool's types %s" % (w, r["type"], p["types"]))
            if mon_class(r) != e["rarity"]: err("%s: rarity %s != computed %s" % (w, e["rarity"], mon_class(r)))
            if e["rarity"] == "S" and e["card"] not in p["s_whitelist"]: err("%s: S monster not whitelisted" % w)
            if e["rarity"] != "S" and power(r) > p["max_power"]: err("%s: power %d over the pool's max %d" % (w, power(r), p["max_power"]))
        if e["rarity"] == "S" and not e.get("arena_only"): err("%s: S must be arena_only" % w)
        cnt[e["rarity"]] += 1
    for k in ("C", "B", "A"):
        if cnt[k] < 3: err("pool %s has only %d %s cards" % (pid, cnt[k], k))
    for s in p["s_whitelist"]:
        if s not in seen: err("pool %s: whitelisted S card %s missing" % (pid, s))
    if cnt["S"] == 0: warn("pool %s has no S card: arena S rolls fall back to A" % pid)
    for ctx in CTX:
        for L in range(1, LEVELS["cap"] + 1):
            for arena in (False, True):
                o, av = effective_odds(p, ctx, L, arena)
                if abs(sum(o.values()) - 100) > 1e-6: err("pool %s ctx %s level %d: odds sum %.4f" % (pid, ctx, L, sum(o.values())))
                if any(v < -1e-9 for v in o.values()): err("pool %s ctx %s level %d: negative odds" % (pid, ctx, L))
                if av["C"] == 0 and CTX[ctx]["C"] > 0: err("pool %s: no C card at level %d" % (pid, L))
                if all(o[r] == 0 or av[r] > 0 for r in RAR) is False: err("pool %s ctx %s level %d: odds on an empty rarity" % (pid, ctx, L))
    # every (context) must be able to pay at least one card even with arena_clear (A/S only): falls to B/C
area_map = POOLS["rules"]["area_to_pool"]
for a, pid in area_map.items():
    if a not in known_areas: err("area_to_pool: unknown area %s" % a)
    if pid is not None and pid not in POOL: err("area_to_pool %s -> unknown pool %s" % (a, pid))
infos.append("pools: " + ", ".join("%s %d" % (k, len(v["entries"])) for k, v in POOL.items()))

# rarity table
for name in RARITY["rarity"]:
    if name not in CARDS: err("card_rarity: unknown card %s" % name)
for name, r in CARDS.items():
    if r["type"] != "Ritual" and name not in RARITY["rarity"]: err("card_rarity: %s missing" % name)
for n in RARITY["banned"]:
    if n in CARDS and not banned(CARDS[n]): err("card_rarity banned list has %s which the validator does not ban" % n)

# ---------------------------------------------------------------- decks
def check_deck(key, d, where):
    cards = d["cards"]; total = sum(cards.values())
    if total != 40: err("%s: %d cards (need 40)" % (where, total))
    if d.get("total") != total: err("%s: total field %s != %d" % (where, d.get("total"), total))
    if len(cards) < 14: err("%s: %d distinct cards (need >= 14)" % (where, len(cards)))
    mons = []
    for n, c in cards.items():
        r = card(n, where)
        if not r: continue
        if not isinstance(c, int) or not 1 <= c <= 3: err("%s: %s x%s (max 3)" % (where, n, c))
        if r["id"] in RITUAL_ONLY or r["type"] in ("Ritual", "Trap"): err("%s: %s is a ritual/trap card" % (where, n))
        if r["id"] in CUSTOM_SLOTS: err("%s: %s is a slot of the old story's custom cards" % (where, n))
        if r["id"] in EXODIA: err("%s: Exodia piece %s" % (where, n))
        if MONSTER(r): mons += [r["atk"]] * c
    return sum(mons) / max(1, len(mons))
tier_atk = collections.defaultdict(list)
for key, d in DECKS["decks"].items():
    if key in OLD_DECKS or key in DK_DECKS: err("deck key %s collides with decks.json / decks_dk.json" % key)
    avg = check_deck(key, d, "deck %s" % key)
    tier_atk[d["difficulty_tier"]].append(avg)
    if not 1 <= d["difficulty_tier"] <= 10: err("deck %s: bad tier" % key)
for t in sorted(tier_atk):
    a = sum(tier_atk[t]) / len(tier_atk[t])
    infos.append("deck tier %d: %d decks, mean monster ATK %d" % (t, len(tier_atk[t]), a))
ts = sorted(tier_atk); means = [sum(tier_atk[t]) / len(tier_atk[t]) for t in ts]
for i in range(1, len(ts)):
    if means[i] + 1 < means[i - 1] and ts[i] - ts[i - 1] == 1: warn("mean monster ATK drops from tier %d (%d) to tier %d (%d)" % (ts[i - 1], means[i - 1], ts[i], means[i]))

# ---------------------------------------------------------------- shops
price_win = lambda s: ECO["tiers"]["win_coins"][s["tier"] - 1]
weq, pweq = ECO["prices"]["weq"], ECO["prices"]["pack_weq"]
used_bits = set(); shop_ids = set()
min_buy = {k: 10 ** 9 for k in RAR}
def sell_price(rar): return r5(ECO["prices"]["sell_rate"] * weq[rar] * ECO["prices"]["sell_base_win"])
for s in SHOPS["shops"]:
    sid = s["id"]; shop_ids.add(sid); w = "shop %s" % sid
    if s["area"] not in known_areas: err("%s: unknown area %s" % (w, s["area"]))
    if s["pool"] not in POOL: err("%s: unknown pool" % w); continue
    pool = POOL[s["pool"]]; byname = {e["card"]: e for e in pool["entries"]}
    if s["price_win"] != price_win(s): err("%s: price_win %s != tiers table %s" % (w, s["price_win"], price_win(s)))
    st = s["stock"]
    if not st["always"]: err("%s: no always-stock" % w)
    for it in st["always"] + st["limited"]:
        e = byname.get(it["card"])
        if not e: err("%s: %s is not in the %s pool" % (w, it["card"], s["pool"])); continue
        if it["rarity"] != e["rarity"]: err("%s: %s rarity %s != pool %s" % (w, it["card"], it["rarity"], e["rarity"]))
        base = r5(s["price_win"] * weq[it["rarity"]])
        mult = it["price"] / base if base else 0
        if it in st["always"] and it["price"] != base: err("%s: %s price %d != %d" % (w, it["card"], it["price"], base))
        if it in st["limited"] and it["price"] not in (base, base * 2): err("%s: limited %s price %d not 1x or 2x of %d" % (w, it["card"], it["price"], base))
        if it["price"] <= 0: err("%s: price <= 0" % w)
        min_buy[it["rarity"]] = min(min_buy[it["rarity"]], base)
        if it["min_level"] < e["min_level"] and it in st["limited"] and it["rarity"] == "S": err("%s: S offered below its pool min_level" % w)
        un = it.get("unlock", {})
        for fl in un.get("flags_all", []):
            if fl not in story_flags: err("%s: unlock flag %s is not a story flag" % (w, fl))
    for it in st["limited"]:
        b = it["bit"]
        if b in used_bits or not 0 <= b < 64: err("%s: limited bit %s duplicated or out of 0..63" % (w, b))
        used_bits.add(b)
        if it["max_buy"] < 1: err("%s: max_buy" % w)
    for rot in st["rotating"]:
        cands = [e for e in pool["entries"] if e["rarity"] == rot["rarity"] and e["min_level"] <= 30 and not e.get("arena_only")]
        if len(cands) < rot["count"] + 2: err("%s: rotating %s has too few candidates (%d)" % (w, rot["rarity"], len(cands)))
        if rot["price"] != r5(s["price_win"] * weq[rot["rarity"]]): err("%s: rotating price" % w)
        min_buy[rot["rarity"]] = min(min_buy[rot["rarity"]], rot["price"])
    ids = [p["id"] for p in st["packs"]]
    if ids != ["common", "rare", "grand"]: err("%s: packs must be common, rare, grand" % w)
    for p in st["packs"]:
        if p["price"] != r5(s["price_win"] * pweq[p["kind"]]): err("%s: pack %s price %d" % (w, p["id"], p["price"]))
        if len(p["slots"]) != p["count"]: err("%s: pack %s has %d slots for count %d" % (w, p["id"], len(p["slots"]), p["count"]))
        for sl in p["slots"]:
            rs = [sl["rarity"]] if "rarity" in sl else list(sl["odds"])
            if "odds" in sl and abs(sum(sl["odds"].values()) - 100) > 1e-9: err("%s: pack %s slot odds" % (w, p["id"]))
            for r in rs:
                if r == "S": err("%s: packs must not contain S" % w)
                if not any(e["rarity"] == r and not e.get("arena_only") for e in pool["entries"]): err("%s: pack %s needs %s but the pool has none" % (w, p["id"], r))
        # expected value in single-card price vs pack price
    if s["keeper"]["id"] not in TEXT["en"]["names"]["keepers"] and not s["keeper"]["existing_npc"]: err("%s: keeper has no name text" % w)
    if s["keeper"]["greet_id"] not in TEXT["en"]["dialogue"]: err("%s: greet text missing" % w)
    if s["name"] != TEXT["en"]["names"]["shops"].get(sid): err("%s: inline name != EN text" % w)
    if s["rotation"]["every_duels"] < 1: err("%s: rotation" % w)
    if s["area"] != POOL[s["pool"]]["area"]: err("%s: shop area != pool area" % w)
for rar in RAR:
    if min_buy[rar] < 10 ** 9 and sell_price(rar) >= min_buy[rar]: err("sell price %d of %s is not below the cheapest buy price %d" % (sell_price(rar), rar, min_buy[rar]))
if len(shop_ids) != 10: err("expected 10 shops, found %d" % len(shop_ids))
for l in ("cistern", "castle_hall", "castle_top"):
    if any(s["area"] == l for s in SHOPS["shops"]): err("area %s must have no shop" % l)
infos.append("shops: " + ", ".join(sorted(shop_ids)) + "; one-time purchase bits used %d/64" % len(used_bits))

# ---------------------------------------------------------------- gang
G = GANG; members = {m["id"]: m for m in G["members"]}
for m in G["members"]:
    w = "gang %s" % m["id"]
    if m["deck"] not in DECKS["decks"]: err("%s: deck %s missing" % (w, m["deck"]))
    if m["duelist"]["copy"] not in BASES: err("%s: copy base %r is not a disc duelist" % (w, m["duelist"]["copy"]))
    sl = m["duelist"]["slot"]
    if sl in used_slots: err("%s: slot %d already used by %s" % (w, sl, used_slots[sl]))
    used_slots[sl] = m["duelist"]["id"]
    if sl < 43: err("%s: slot %d collides with the story's duelists (40-42)" % (w, sl))
    if m["name"] != TEXT["en"]["names"]["gang"][m["id"]]: err("%s: inline name != text" % w)
    for k in ("taunt_id", "win_id", "lose_id"):
        if m[k] not in TEXT["en"]["dialogue"]: err("%s: %s %s missing" % (w, k, m[k]))
    if m["gang_tier"] not in (1, 2, 3, 4): err("%s: gang_tier" % w)
    if DECKS["decks"].get(m["deck"], {}).get("difficulty_tier") != m["difficulty_tier"]: err("%s: difficulty tier != deck's" % w)
for t in (1, 2, 3):
    if not [m for m in G["members"] if m["gang_tier"] == t]: err("gang tier %d has no member" % t)
tb = G["tier_by_level"]; covered = set()
for row in tb:
    a, b = row["level"]
    if abs(sum(row["weights"].values()) - 100) > 1e-9: err("gang tier_by_level %s weights" % row["level"])
    covered |= set(range(a, b + 1))
    for t in row["weights"]:
        if not [m for m in G["members"] if m["gang_tier"] == int(t)]: err("gang tier_by_level uses empty tier %s" % t)
if covered != set(range(1, LEVELS["cap"] + 1)): err("gang tier_by_level does not cover levels 1..%d exactly" % LEVELS["cap"])
for i, row in enumerate(T):
    if row["gang_tier_weights"] != next(r["weights"] for r in tb if r["level"][0] <= row["level"] <= r["level"][1]): err("levels.json gang weights differ from gang.json at level %d" % row["level"])
sk = G["stakes"]
for t in ("1", "2", "3"):
    pct, mn, mx = sk["percent_by_gang_tier"][t], sk["min_by_gang_tier"][t], sk["max_by_gang_tier"][t]
    if not 0 < pct < 1 or not 0 < mn <= mx: err("stakes tier %s bad params" % t)
    for coins in list(range(0, 400)) + [999, 5000, 20000, 99999]:
        stolen = min(coins, max(mn, min(mx, int(round(coins * pct)))))
        if stolen < 0 or stolen > coins or coins - stolen < 0: err("stakes tier %s: stolen %d of %d" % (t, stolen, coins))
        for fac in (1.0, sk["first_three_ambushes_factor"], sk["loss_streak_relief"]["stolen_factor"], sk["truce_factor"]):
            s2 = min(coins, int(stolen * fac))
            if s2 < 0 or s2 > coins: err("stakes factor %s breaks bounds" % fac)
    cap = sk["max_by_gang_tier"][t]
amb = G["ambush"]
if not 0 < amb["cooldown_walk_seconds"]["min"] < amb["cooldown_walk_seconds"]["max"]: err("ambush cooldown min/max")
if amb["min_purse"] < min(sk["min_by_gang_tier"].values()): warn("min_purse below the smallest stolen amount")
for a in amb["eligible_areas"]:
    if a not in known_areas: err("ambush eligible area %s unknown" % a)
for a in amb["frequency_by_area"]:
    if a not in amb["eligible_areas"]: err("frequency for non-eligible area %s" % a)
for a in amb["eligible_areas"]:
    if a not in amb["frequency_by_area"]: err("eligible area %s has no frequency" % a)
for zn in amb["safe_zones"]:
    an = zn["anchor"]
    if not re.fullmatch(r"(\*|[a-z_]+)\.[a-z_]+", an): err("safe zone anchor %r" % an)
    elif an.split(".")[0] not in ("*",) and an.split(".")[0] not in known_areas: err("safe zone area %r" % an)
    if zn["radius"] <= 0: err("safe zone radius")
if amb["tutorial"]["no_ambush_before_stage"] < 3: err("ambushes must not start before stage 3 (tutorial)")
if amb["tutorial"]["first_ambush"]["member"] not in members: err("first ambush member unknown")
elif members[amb["tutorial"]["first_ambush"]["member"]]["gang_tier"] != 1: err("first ambush must be a tier 1 member")
if members["old_jackal"]["appears"] != "arena_boss_only": err("old_jackal must be arena-only")
if amb["tutorial"]["warmup_walk_seconds"] < 120: err("warm-up must be at least 2 minutes")
for k in ("after_win", "after_loss"):
    if amb["grace_walk_seconds"][k] < 30: err("grace %s too short" % k)
if "stars" in json.dumps(G["stakes"]).replace("stars_wager", ""): warn("gang stakes mention stars: the star system must stay untouched")

# ---------------------------------------------------------------- arenas
fighters = {f["id"]: f for f in ARENAS["fighters"]}
slots_seen = set()
for f in ARENAS["fighters"]:
    w = "fighter %s" % f["id"]
    if f["deck"] not in DECKS["decks"]: err("%s: deck %s missing" % (w, f["deck"]))
    if f["duelist"]["copy"] not in BASES: err("%s: copy base %r invalid" % (w, f["duelist"]["copy"]))
    sl = f["duelist"]["slot"]
    if sl in used_slots: err("%s: slot %d already used by %s" % (w, sl, used_slots[sl]))
    used_slots[sl] = f["duelist"]["id"]
    if f["name"] != TEXT["en"]["names"]["fighters"].get(f["id"]): err("%s: name != text" % w)
    if f["text_id"] not in TEXT["en"]["dialogue"]: err("%s: pre-duel text missing" % w)
    if DECKS["decks"].get(f["deck"], {}).get("difficulty_tier") != f["tier"]: err("%s: tier != deck tier" % w)
arena_ids = []
def ev(arena, p):
    """expected net coins of one run at a per-bout win chance p (first clear excluded; repeat clear bonus included)"""
    fee = arena["fee"]; total = -fee; alive = 1.0
    for r in arena["ladder"]:
        alive *= p; total += alive * r["coins"]
    total += alive * arena["repeat_clear"]["coins"]
    return total
for a in ARENAS["arenas"]:
    aid = a["id"]; w = "arena %s" % aid; arena_ids.append(aid)
    if a["area"] not in known_areas: err("%s: unknown area %s" % (w, a["area"]))
    if a["interior_area"] not in new_areas: err("%s: interior %s is not in economy.json new_areas" % (w, a["interior_area"]))
    if a["pool"] not in POOL: err("%s: pool" % w)
    if len(a["ladder"]) != 4: err("%s: ladder must have 4 rungs" % w)
    prev = 0
    for r in a["ladder"]:
        fg = fighters.get(r["fighter"]) or members.get(r["fighter"])
        if not fg: err("%s: fighter %s unknown" % (w, r["fighter"])); continue
        if r["tier"] < prev: err("%s: ladder tiers must not decrease" % w)
        prev = r["tier"]
        if r["deck"] not in DECKS["decks"]: err("%s: deck %s" % (w, r["deck"]))
        if r["coins"] != r5(ECO["tiers"]["win_coins"][r["tier"] - 1] * 0.8): err("%s: rung %d coins" % (w, r["rung"]))
        if r["xp_base"] != ECO["tiers"]["win_xp"][r["tier"] - 1]: err("%s: rung %d xp" % (w, r["rung"]))
        if r["drops"]["context"] not in CTX: err("%s: drop context" % w)
    if not a["ladder"][-1]["champion"] or sum(1 for r in a["ladder"] if r["champion"]) != 1: err("%s: exactly the last rung is the champion" % w)
    u = a["unlock"]
    if not 2 <= u["level_min"] <= LEVELS["cap"]: err("%s: unlock level" % w)
    if a["keeper"] not in TEXT["en"]["names"]["keepers"] and a["keeper"] not in ("baker",): err("%s: keeper %s has no name" % (w, a["keeper"]))
    if a["tip_id"] not in TEXT["en"]["dialogue"] or a["name_id"].split(".")[1] not in TEXT["en"]["names"]["arenas"]: err("%s: text ids" % w)
    if aid not in {s["id"] for s in SHOPS["shops"]}: err("%s: an arena needs a shop in the same location (the tip comes from the shopkeeper)" % w)
    p_even = ev(a, 0.5); p60 = ev(a, 0.6); p80 = ev(a, 0.8)
    normal_win = ECO["tiers"]["win_coins"][min(9, POOL[a["pool"]] and next(l for l in ARENAS["arenas"] if l["id"] == aid)["ladder"][0]["tier"]) - 1]
    infos.append("arena %-8s fee %4d  EV/run p=.5 %+6.0f  p=.6 %+6.0f  p=.8 %+6.0f (a normal duel win there: %d)" % (aid, a["fee"], p_even, p60, p80, normal_win))
    if p60 <= 0: err("%s: a 60%% player loses money on average (EV %+.0f)" % (w, p60))
    if p_even < -a["fee"] * 0.6: warn("%s: a coin-flip player loses most of the fee on average" % w)
    if p80 > 3.5 * sum(r["coins"] for r in a["ladder"]) / 4: warn("%s: very strong player earns a lot per run" % w)
    fc = a["first_clear"]
    if fc["coins"] <= 0: err("%s: first clear" % w)
if len(arena_ids) != 9: err("expected 9 arenas, got %d" % len(arena_ids))
if len(arena_ids) > 12: err("the save has 12 arena bytes (eco.arena[8] + arena_x[4])")
if "old_jackal" not in [r["fighter"] for r in next(a for a in ARENAS["arenas"] if a["id"] == "fair")["ladder"]]: err("the Underfair champion must be Old Jackal")
for l in ("cistern", "ship_deck", "castle_gate", "castle_hall", "castle_top"):
    if any(a["location"] == l for a in ARENAS["arenas"]): err("area %s must have no arena" % l)
if ARENAS["arenas"] and any(f.get("stars_wager") for f in ARENAS["fighters"]): err("arena duels must not wager stars")
infos.append("new duelist slots: %d (gang %d, arena fighters %d), range %d-%d" % (len(members) + len(fighters), len(members), len(fighters), min(used_slots), max(used_slots)))

# ---------------------------------------------------------------- economy / story integration
ec = ECO
for k in ("win_coins", "win_xp", "nominal_level"):
    if len(ec["tiers"][k]) != 10: err("tiers.%s needs 10 entries" % k)
    if sorted(ec["tiers"][k]) != ec["tiers"][k]: err("tiers.%s must increase" % k)
for q, v in ec["rewards_story"]["quest_coins"].items():
    if q not in story_quests: err("quest %s is not in story_dk.json" % q)
    if v < 0: err("quest coin reward")
story_duel_ids = {d["id"] for d in STORY["duels"]}
for d in ec["rewards_story"]["duels"]:
    if d["id"] not in story_duel_ids: err("story duel %s unknown" % d["id"])
    if d["stars_wager"] and d["id"] not in KINGDOM_STAR_DUELS: err("a home-town duel with stars_wager: the star system must stay as it is")
story_give = set()
def walk(n):
    if isinstance(n, dict):
        for k, v in n.items():
            if k == "give_card" and isinstance(v, str): story_give.add(v)
            walk(v)
    elif isinstance(n, list):
        for v in n: walk(v)
walk(STORY)
if set(ec["rewards_story"]["protected_cards"]) != story_give: err("protected_cards differ from the story's give_card effects")
for n in ec["rewards_story"]["protected_cards"]: card(n, "protected card")
# ---------------------------------------------------------------- arena exclusives
# A card marked exclusive drops only in its own ring: arena_only in exactly one pool, in no other pool,
# never sold (always, limited, packs draw from pools but skip arena_only), never a story reward or in the starter deck.
excl = {}
for p in POOLS["pools"]:
    for e in p["entries"]:
        if e.get("exclusive"):
            if e["card"] in excl: err("exclusive %s in two pools (%s, %s)" % (e["card"], excl[e["card"]], p["id"]))
            excl[e["card"]] = p["id"]
            if not e.get("arena_only"): err("exclusive %s is not arena_only in %s" % (e["card"], p["id"]))
            if p["id"] not in {a["pool"] for a in ARENAS["arenas"]}: err("exclusive %s: pool %s has no arena" % (e["card"], p["id"]))
for p in POOLS["pools"]:
    for e in p["entries"]:
        if e["card"] in excl and excl[e["card"]] != p["id"]: err("exclusive %s of %s also in pool %s" % (e["card"], excl[e["card"]], p["id"]))
for s in SHOPS["shops"]:
    st = s["stock"]
    for e in st["always"] + st["limited"]:
        if e["card"] in excl: err("exclusive %s is sold in shop %s" % (e["card"], s["id"]))
for n in excl:
    if n in story_give: err("exclusive %s is a story reward" % n)
try:
    STARTER = json.load(open(os.path.join(DK, "decks_dk.json"), encoding="utf-8"))["starter"]["cards"]
    for n in excl:
        if n in STARTER: err("exclusive %s is in the starter deck" % n)
    if sum(STARTER.values()) != 40: err("the starter deck has %d cards" % sum(STARTER.values()))
except KeyError:
    err("decks_dk.json has no starter deck")
for need in ("village", "harbor", "ship", "beach", "forest", "mountain"):
    if sum(1 for v in excl.values() if v == need) < 3: err("arena %s has fewer than 3 exclusives" % need)
infos.append("arena exclusives: " + "; ".join("%s: %s" % (k, ", ".join(sorted(c for c, v in excl.items() if v == k))) for k in sorted(set(excl.values()))))
for k in ec["files"].values():
    if not os.path.exists(os.path.join(HERE, k)): err("files: %s missing" % k)
# coin timeline of the home arc (deterministic part): quests + story duel wins at level ~1-5
home = 0; xp = 0; lvl = 1
for d in ec["rewards_story"]["duels"]:
    t = d["tier"]
    if d["id"] == "inseto": continue
    home += ec["tiers"]["win_coins"][t - 1]
    f = max(0.2, min(1.8, 1 + 0.12 * (ec["tiers"]["nominal_level"][t - 1] - lvl)))
    xp += round(ec["tiers"]["win_xp"][t - 1] * f); lvl = level_of(xp)
home_q = sum(v for q, v in ec["rewards_story"]["quest_coins"].items() if q != "s01_baker")
infos.append("home arc (story only): %d coins from duels + %d from quests = %d; xp %d -> level %d" % (home, home_q, home + home_q, xp, lvl))
village = next(s for s in SHOPS["shops"] if s["id"] == "village")
if home + home_q < 2 * village["stock"]["packs"][0]["price"]: warn("story coins in the home arc cover fewer than two village packs")

# ---------------------------------------------------------------- text
ALLOWED = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,!?'-")
UI_EXTRA = set(":%+/$")
def wrap(s, width=32):
    lines, cur = [], ""
    for w in s.split():
        if len(w) > width: return None
        t = (cur + " " + w) if cur else w
        if len(t) <= width: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines
def flat(d, p=""):
    for k, v in d.items():
        if isinstance(v, dict): yield from flat(v, p + k + ".")
        else: yield p + k, v
en, pt = TEXT["en"], TEXT["pt"]
for sec in ("names", "dialogue", "ui", "descriptions"):
    a, b = dict(flat(en[sec])), dict(flat(pt[sec]))
    if set(a) != set(b): err("EN/PT %s keys differ: %s" % (sec, sorted(set(a) ^ set(b))[:6]))
    for k, v in a.items():
        pv = b.get(k)
        if pv is None: continue
        for lang, s in (("en", v), ("pt", pv)):
            allowed = ALLOWED | (UI_EXTRA if sec == "ui" else set())
            bad = sorted({c for c in s if c not in allowed})
            if bad: err("[%s] %s.%s: chars not in the font %r" % (lang, sec, k, "".join(bad)))
        if sec == "ui":
            fa = re.findall(r"%(?:\d\$)?[ds]", v); fb = re.findall(r"%(?:\d\$)?[ds]", pv)
            if sorted(x[-1] for x in fa) != sorted(x[-1] for x in fb): err("ui.%s: format specifiers differ (%s vs %s)" % (k, fa, fb))
        if sec == "dialogue":
            for lang, s in (("en", v), ("pt", pv)):
                ls = wrap(s)
                if ls is None or len(ls) > 3: err("[%s] dialogue.%s does not fit 3x32: %r" % (lang, k, s))
        if sec == "names" and k.split(".")[0] in ("keepers", "fighters", "gang") and not k.endswith(".name") and k != "gang.name":
            for lang, s in (("en", v), ("pt", pv)):
                if len(s) > 16: err("[%s] speaker name %s too long (%d > 16, the longest story speaker): %r" % (lang, k, len(s), s))
for sec in ("ui",):
    for k, v in pt[sec].items():
        if not v.strip(): err("empty PT ui %s" % k)
# every id the data points to has a text
for s in SHOPS["shops"]:
    if s["id"] not in en["names"]["shops"] or s["id"] not in en["names"]["places"]: err("text for shop %s missing" % s["id"])
for p in POOLS["pools"]:
    if p["id"] not in en["names"]["places"]: err("place name for pool %s missing" % p["id"])
for a in ARENAS["arenas"]:
    for k in (a["tip_id"],):
        if k not in en["dialogue"]: err("text %s" % k)
for need in ("arena_clear", "arena_lost", "keeper_bye", "keeper_poor"):
    if need not in en["dialogue"]: err("dialogue %s missing" % need)
ui_needed = ["money", "level_label", "level_up", "ambush_banner", "ambush_stake", "ambush_lost", "shop_buy", "shop_sell", "arena_fee", "arena_round", "status_title"]
for k in ui_needed:
    if k not in en["ui"]: err("ui string %s missing" % k)
for r in range(1, 8):
    if "rank_%d" % r not in en["ui"]: err("ui rank_%d missing" % r)
infos.append("text: %d names, %d dialogue strings, %d ui strings per language" % (len(dict(flat(en["names"]))), len(en["dialogue"]), len(en["ui"])))

# ---------------------------------------------------------------- report
for i in infos: print("info:", i)
for w in warns: print("warning:", w)
for e in errs: print("ERROR:", e)
print("%d errors, %d warnings" % (len(errs), len(warns)))
sys.exit(1 if errs else 0)
