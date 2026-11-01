#!/usr/bin/env python3
"""Generates every JSON file of journey_content/economy/ from the card catalog, the story data and eco_text.py.
Run:  python3 src/gen_economy.py     (writes ../economy.json, shops.json, card_pools.json, gang.json, arenas.json, levels.json,
decks_economy.json, card_rarity.json, en/economy.en.json, pt/economy.pt.json).  Deterministic (seeded)."""
import csv, json, os, random, re, hashlib, math, collections
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
CAT = os.environ.get("FM_CATALOG", "/workspace/study/fmrecomp/fork/notes/card-catalog.csv")
STORY = os.path.join(ROOT, "..", "duelist_kingdom", "en", "story_dk.json")
import sys; sys.path.insert(0, HERE)
import eco_text as T

# ------------------------------------------------------------------ catalog
CARDS = {}
with open(CAT, newline="", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        r["id"] = int(r["id"]); CARDS[r["name"]] = r
def num(v):
    try: return int(v)
    except: return None
for r in CARDS.values():
    r["atk"], r["def"], r["cost"] = num(r["attack"]), num(r["defense"]), num(r["starchip_cost"])
MONSTER_TYPES = {r["type"] for r in CARDS.values()} - {"Magic", "Trap", "Equip", "Ritual"}
RITUAL_ONLY_IDS = {356, 357, 360, 362, 364, 374, 380, 21} | set(range(701, 723))     # as tools/check_decks.py
CUSTOM_SLOTS = {309, 318, 342, 652, 653, 657, 672, 689, 702, 720}                    # replaced by the OLD story's custom cards
EXODIA = {17, 18, 19, 20, 21}
def power(r): return max(r["atk"], 0.9 * r["def"])
def mon_class(r):
    p = power(r)
    return "C" if p <= 1250 else "B" if p <= 1700 else "A" if p <= 2100 else "S"
def is_monster(r): return r["type"] in MONSTER_TYPES
def banned(r):
    """never dropped, sold or put in an AI deck"""
    if r["type"] in ("Ritual", "Trap"): return True
    if r["id"] in RITUAL_ONLY_IDS or r["id"] in CUSTOM_SLOTS or r["id"] in EXODIA: return True
    if r["cost"] is None: return True                                    # 'N/A': ritual results
    if is_monster(r) and r["cost"] == 999999 and power(r) > 1950: return True   # legends with no password
    return False

# spells
FIELD = {"Forest": 330, "Wasteland": 331, "Mountain": 332, "Sogen": 333, "Umi": 334, "Yami": 335}
TYPE_FIELD = {"Plant": ["Forest"], "Insect": ["Forest"], "Beast": ["Forest"], "Beast-Warrior": ["Forest", "Sogen"],
              "Dinosaur": ["Wasteland", "Forest"], "Reptile": ["Wasteland", "Forest"], "Rock": ["Wasteland", "Mountain"],
              "Zombie": ["Yami", "Wasteland"], "Spellcaster": ["Yami"], "Fiend": ["Yami"], "Fairy": ["Sogen", "Forest"],
              "Warrior": ["Sogen", "Mountain"], "Machine": ["Wasteland", "Mountain"], "Winged Beast": ["Mountain"],
              "Dragon": ["Mountain"], "Thunder": ["Umi", "Mountain"], "Aqua": ["Umi"], "Fish": ["Umi"], "Sea Serpent": ["Umi"],
              "Pyro": ["Wasteland", "Mountain"]}
# design-level affinities (the game's own equip table decides what an equip really fits; verify in the FM editor)
TYPE_EQUIP = {"Plant": ["Vile Germs"], "Insect": ["Laser Cannon Armor", "Insect Armor with Laser Cannon", "Vile Germs"],
              "Beast": ["Beast Fangs", "Horn of the Unicorn"], "Beast-Warrior": ["Beast Fangs", "Mystical Moon"],
              "Dinosaur": ["Raise Body Heat", "Dragon Treasure", "Electro-whip"], "Reptile": ["Raise Body Heat", "Electro-whip"],
              "Rock": ["Invigoration", "Axe of Despair"], "Zombie": ["Violet Crystal", "Dark Energy"],
              "Spellcaster": ["Book of Secret Arts", "Dark Energy"], "Fiend": ["Dark Energy", "Sword of Dark Destruction", "Black Pendant"],
              "Fairy": ["Elf's Light", "Silver Bow and Arrow", "Horn of Light"], "Warrior": ["Legendary Sword", "Kunai with Chain", "Axe of Despair"],
              "Machine": ["Cyber Shield", "Machine Conversion Factory"], "Winged Beast": ["Follow Wind", "Silver Bow and Arrow"],
              "Dragon": ["Dragon Treasure", "Axe of Despair"], "Thunder": ["Electro-whip"], "Aqua": ["Power of Kaishin"],
              "Fish": ["Power of Kaishin"], "Sea Serpent": ["Power of Kaishin"], "Pyro": ["Salamandra"]}
SPELL_C = ["Red Medicine", "Sparks", "Cursebreaker", "Hinotama"] + list(FIELD)
SPELL_A = ["Swords of Revealing Light", "Stop Defense"]

# ------------------------------------------------------------------ locations
LOCS = [
 dict(id="village", area="village", tier=1, arrival=1, shop=True, arena=True, stage_min=3,
      types=["Plant", "Insect", "Reptile", "Beast", "Dinosaur"], max_power=1850, s=["Bracchio-raidus"],
      featured=["Mushroom Man", "Basic Insect", "Torike", "Armored Lizard", "Uraby", "Griffore", "Bean Soldier"],
      extra_spells=["Mooyan Curry"], theme="Plants, insects, beasts, lizards and dinosaurs of the oasis farms and the east road."),
 dict(id="harbor", area="harbor", tier=2, arrival=4, shop=True, arena=True, stage_min=5,
      types=["Fish", "Sea Serpent", "Aqua", "Thunder", "Winged Beast"], max_power=1950, s=["Aqua Dragon"],
      featured=["Rare Fish", "Bolt Penguin", "Droll Bird", "Flying Penguin", "Tongyo", "Kaminarikozou"], extra_spells=[],
      theme="Sea life, thunder and gulls of the river-mouth harbor."),
 dict(id="beach", area="kingdom_beach", tier=2, arrival=5, shop=True, arena=True,
      types=["Aqua", "Pyro", "Insect", "Reptile"], max_power=2050, s=[],
      featured=["Giant Turtle Who Feeds on Flames", "Fire Kraken", "Ganigumo", "Hunter Spider", "Flame Viper"], extra_spells=[],
      theme="Turtles, jellyfish, fire and sand bugs of the Shore of Illusions (Weevil's beach)."),
 dict(id="forest", area="kingdom_forest", tier=3, arrival=6, shop=True, arena=True,
      types=["Beast", "Beast-Warrior", "Plant", "Insect", "Dinosaur"], max_power=2150, s=[],
      featured=["Two-headed King Rex", "Hitotsu-me Giant", "Flower Wolf", "Man-eater Bug", "Trent"], extra_spells=[],
      theme="Beasts, wild warriors, thick plants, insects and Rex's dinosaurs of the Forest of Whispers."),
 dict(id="mountain", area="kingdom_mountain", tier=4, arrival=8, shop=True, arena=True,
      types=["Rock", "Warrior", "Machine", "Winged Beast"], max_power=2250, s=["Machine King", "Judge Man"],
      featured=["Giant Soldier of Stone", "Cyber Soldier", "Skull Red Bird", "Zanki", "Dice Armadillo"], extra_spells=[],
      theme="Rocks, gamblers' machines, harpy-like birds and warriors of the Mountain Pass."),
 dict(id="meadow", area="kingdom_meadow", tier=4, arrival=9, shop=True, arena=True,
      types=["Fairy", "Plant", "Spellcaster", "Beast"], max_power=2250, s=[],
      featured=["Petit Angel", "Dryad", "Queen of Autumn Leaves", "Mystical Sheep #1", "Shining Friendship"], extra_spells=[],
      theme="Fairies, flowers, gentle mages and small beasts of the hedge maze."),
 dict(id="desert", area="kingdom_desert", tier=5, arrival=11, shop=True, arena=True,
      types=["Rock", "Zombie", "Spellcaster", "Reptile"], max_power=2250, s=["Great Mammoth of Goldfine", "Labyrinth Wall"],
      featured=["The 13th Grave", "Pumpking the King of Ghosts", "Mystical Sand", "Rock Spirit", "Ill Witch"], extra_spells=[],
      theme="Mummies, sand rocks, fortune-teller mages and snakes of the Desert of Lost Stars."),
 dict(id="fair", area="kingdom_fair", tier=6, arrival=12, shop=True, arena=True,
      types=["Fiend", "Machine", "Warrior", "Thunder", "Dragon"], max_power=2300,
      s=["Twin-headed Thunder Dragon", "Bickuribox", "Kaiser Dragon", "Seiyaryu", "Ushi Oni"],
      featured=["Mystic Clown", "Crass Clown", "Thunder Dragon", "Metal Dragon", "Koumori Dragon"],
      extra_spells=["Swords of Revealing Light"], theme="Clowns, circus machines, sparks and festival dragons of the Star Fair."),
 dict(id="gate", area="castle_gate", tier=8, arrival=15, shop=True, arena=False,
      types=["Dragon", "Machine", "Warrior", "Insect"], max_power=2450, s=["Seiyaryu", "Kaiser Dragon", "Machine King", "Judge Man"],
      featured=["Dungeon Worm", "Metal Dragon", "Royal Guard"], extra_spells=["Swords of Revealing Light", "Stop Defense"],
      theme="Dragons, guardian machines and warriors at the Castle Gate (plus InsetoKaiba's beetles)."),
 dict(id="hall", area="castle_hall", tier=8, arrival=17, shop=False, arena=False,
      types=["Fiend", "Spellcaster", "Fairy", "Dragon"], max_power=2450, s=["Soul Hunter", "Bickuribox", "Ushi Oni", "Seiyaryu"],
      featured=["Mabarrel", "Dark Witch", "Orion the Battle King"], extra_spells=["Swords of Revealing Light"],
      theme="Illusion-hall fiends, mages, fairies and dragons (no shop, drops only)."),
 # last, so the arenas before it keep their save byte (arenas.json order is the save's order)
 dict(id="ship", area="ship_deck", tier=2, arrival=4, shop=True, arena=True, stage_min=7,
      types=["Fish", "Sea Serpent", "Aqua", "Winged Beast", "Warrior"], max_power=1950, s=[],
      featured=["Rare Fish", "Tongyo", "Penguin Soldier"], extra_spells=[],
      theme="Sea life, gulls and deckhand warriors of the Kingdom ship's bilge."),
]
# Arena exclusives: each drops only in its own location's clandestine ring (arena_only in its pool), and
# nowhere else: no shop, no pack, no other pool, no story reward (validate_economy.py checks all four).
ARENA_EXCLUSIVE = {
    "village": ["Bracchio-raidus", "Leogun", "Ancient One of the Deep Forest"],
    "harbor": ["Aqua Dragon", "Kairyu-shin", "Harpie Lady Sisters"],
    "ship": ["Deepsea Shark", "7 Colored Fish", "Skullbird"],
    "beach": ["Vermillion Sparrow", "Kwagar Hercules", "Boulder Tortoise"],
}
EXCLUSIVE_OF = {c: loc for loc, cs in ARENA_EXCLUSIVE.items() for c in cs}
LOC = {l["id"]: l for l in LOCS}
# the 'top' room (Pegasus) uses the hall's pool: duels there drop from "hall"
ARENA_ORDER = [l["id"] for l in LOCS if l["arena"]]
LOCATION_TO_AREA = {l["id"]: l["area"] for l in LOCS}

# ------------------------------------------------------------------ numbers
WIN_COINS = [30, 50, 80, 120, 170, 230, 300, 380, 480, 600]
WIN_XP    = [10, 16, 24, 34, 46, 60, 76, 94, 114, 136]
NOMINAL_LEVEL = [1, 4, 7, 10, 13, 16, 19, 22, 25, 28]
WEQ = {"C": 0.8, "B": 2.5, "A": 8.0, "S": 30.0}                 # single-card price in 'wins' of the shop's tier
PACK_WEQ = {"common": 4.0, "rare": 12.0, "grand": 30.0}
SELL_RATE, SELL_BASE_WIN = 0.25, 80
LEVEL_CAP = 30
BASE_ODDS = {"C": 68.0, "B": 25.0, "A": 6.5, "S": 0.5}
CONTEXT_ODDS = {
    "duel":          {"C": 68, "B": 25, "A": 6.5, "S": 0.5},
    "ambush_win":    {"C": 55, "B": 33, "A": 11, "S": 1},
    "arena_bout":    {"C": 60, "B": 30, "A": 9, "S": 1},
    "arena_champion": {"C": 35, "B": 40, "A": 22, "S": 3},
    "arena_clear":   {"C": 0, "B": 0, "A": 90, "S": 10},
}
CONTEXT_COUNT = {"duel": 1, "ambush_win": 1, "arena_bout": 1, "arena_champion": 2, "arena_clear": 1}
def r5(x): return int(round(x / 5.0)) * 5
def fnv(s):
    h = 2166136261
    for c in s.encode(): h = ((h ^ c) * 16777619) & 0xFFFFFFFF
    return h

# ------------------------------------------------------------------ pools
def build_pool(loc):
    ent = {}
    wl = set(loc["s"])
    for r in CARDS.values():
        if banned(r) or not is_monster(r) or r["type"] not in loc["types"]: continue
        c = mon_class(r)
        if c == "S" and r["name"] not in wl: continue
        if c != "S" and power(r) > loc["max_power"]: continue
        ent[r["name"]] = c
    for name in list(ent):
        if name in EXCLUSIVE_OF and EXCLUSIVE_OF[name] != loc["id"]: del ent[name]   # another ring's prize
    for name in ARENA_EXCLUSIVE.get(loc["id"], ()):
        ent[name] = mon_class(CARDS[name]) if mon_class(CARDS[name]) != "C" else "B"
    for t in loc["types"]:
        for fld in TYPE_FIELD.get(t, []): ent[fld] = "C"
        for eq in TYPE_EQUIP.get(t, []):
            if eq in CARDS and not banned(CARDS[eq]): ent[eq] = "B"
    for sp in ["Red Medicine", "Sparks", "Cursebreaker"] + loc["extra_spells"]:
        ent[sp] = "B" if sp == "Mooyan Curry" else "A" if sp in SPELL_A else "C"
    if "Pyro" in loc["types"]: ent["Hinotama"] = "C"
    out = []
    feat = set(loc["featured"])
    a = loc["arrival"]
    for name, cl in ent.items():
        r = CARDS[name]
        assert not banned(r) or name in ("Mooyan Curry",), name
        minlv = {"C": 1, "B": a, "A": a + 3, "S": a + 6}[cl]
        e = {"card": name, "id": r["id"], "rarity": cl, "weight": 3 if name in feat else 1, "min_level": max(1, minlv)}
        if cl == "S" or name in ARENA_EXCLUSIVE.get(loc["id"], ()): e["arena_only"] = True
        if name in ARENA_EXCLUSIVE.get(loc["id"], ()): e["exclusive"] = True
        if is_monster(r): e["kind"] = "monster"
        else: e["kind"] = "field" if name in FIELD else "equip" if r["type"] == "Equip" else "spell"
        out.append(e)
    miss = feat - set(ent)
    assert not miss, (loc["id"], miss)
    order = {"C": 0, "B": 1, "A": 2, "S": 3}
    out.sort(key=lambda e: (order[e["rarity"]], e["id"]))
    return out
POOLS = {l["id"]: build_pool(l) for l in LOCS}

# ------------------------------------------------------------------ decks
MIX = {  # tier -> class mix of the monster slots
 1: {"C": .72, "B": .28}, 2: {"C": .58, "B": .38, "A": .04}, 3: {"C": .42, "B": .43, "A": .15},
 4: {"C": .30, "B": .45, "A": .25}, 5: {"C": .24, "B": .42, "A": .31, "S": .03}, 6: {"C": .20, "B": .38, "A": .38, "S": .04},
 7: {"C": .15, "B": .35, "A": .42, "S": .08}, 8: {"C": .10, "B": .32, "A": .46, "S": .12}}
def monsters_of(loc_id, types):
    by = collections.defaultdict(list)
    for e in POOLS[loc_id]:
        if e["kind"] == "monster" and CARDS[e["card"]]["type"] in types: by[e["rarity"]].append(e["card"])
    return by
def build_deck(key, loc_id, types, tier, theme):
    rng = random.Random(fnv("deck:" + key))
    deck = collections.OrderedDict()
    def add(n, c):
        deck[n] = deck.get(n, 0) + c
    fields = []
    for t in types:
        for f in TYPE_FIELD.get(t, []):
            if f not in fields: fields.append(f)
    add(fields[0], 3 if tier >= 5 else 2)
    eq = []
    for t in types:
        for e in TYPE_EQUIP.get(t, []):
            if e not in eq and not banned(CARDS[e]): eq.append(e)
    for e in eq[:2 if tier < 4 else 3]: add(e, 2)
    add("Red Medicine", 3 if tier <= 4 else 2)
    if tier >= 4: add("Swords of Revealing Light", 2)
    spells = sum(deck.values())
    mon_total = 40 - spells
    by = monsters_of(loc_id, types)
    if sum(len(v) for v in by.values()) < 10:                      # a thin type: borrow the rest of the location's monsters
        by = monsters_of(loc_id, LOC[loc_id]["types"])
    mix = MIX[min(tier, 8)]
    counts = {k: int(round(mon_total * v)) for k, v in mix.items()}
    counts["C"] += mon_total - sum(counts.values())
    order = ["C", "B", "A", "S"]
    feat = {e["card"] for e in POOLS[loc_id] if e["weight"] == 3}
    leftover = 0
    for k in reversed(order):
        n = counts.get(k, 0) + leftover; leftover = 0
        cands = [c for c in by.get(k, []) if c not in deck]; rng.shuffle(cands)
        cands.sort(key=lambda c: c not in feat)
        if not cands: leftover = n; continue
        copies = {"C": 3, "B": 2, "A": 2, "S": 1}[k]
        chosen = cands[:max(1, math.ceil(n / copies))]
        got = 0; cap = copies
        while got < n:
            progress = False
            for nm in chosen:
                if got < n and deck.get(nm, 0) < cap: add(nm, 1); got += 1; progress = True
            if not progress:
                if cap < 3: cap += 1
                elif len(chosen) < len(cands): chosen = cands[:len(chosen) + 1]
                else: break
        leftover = n - got
    if leftover:                                                   # spill into the cheapest monsters
        for nm in by.get("C", []) + by.get("B", []):
            while leftover and deck.get(nm, 0) < 3: add(nm, 1); leftover -= 1
    assert sum(deck.values()) == 40 and len(deck) >= 14, (key, sum(deck.values()), len(deck))
    cards = dict(sorted(deck.items()))
    return {"duelist": key, "chapter": 0, "difficulty_tier": tier, "theme": theme, "fixed": True, "total": sum(cards.values()), "cards": cards}

# --- gang: hand-written decks
GANG_DECKS = {
 "Dusty": (1, "Jackal pup: wolves and small beasts on the Forest", {
   "Wolf": 3, "Silver Fang": 3, "Torike": 2, "Griffore": 2, "Dark Gray": 2, "Larvas": 2, "Sleeping Lion": 2, "Lisark": 2,
   "Frenzied Panda": 2, "Dig Beak": 2, "Master & Expert": 2, "Hitotsu-me Giant": 2, "Mountain Warrior": 2, "Gate Deeg": 2, "Forest": 3, "Beast Fangs": 3, "Red Medicine": 3, "Sogen": 1}),
 "Scrap": (1, "Jackal pup: scrap warriors and small machines", {
   "Battle Warrior": 3, "M-warrior #1": 2, "M-warrior #2": 2, "Kageningen": 2, "Doron": 2, "Hard Armor": 2, "Steel Scorpion": 2,
   "Mechanical Spider": 2, "Blast Juggler": 2, "Bat": 2, "Yaiba Robo": 2, "Hero of the East": 2, "Eyearmor": 2, "Dragon Statue": 2, "Mountain": 2, "Legendary Sword": 2,
   "Cyber Shield": 2, "Red Medicine": 3, "Sogen": 2}),
 "Fang": (2, "Jackal hunter: charging beast-warriors", {
   "Battle Steer": 2, "Garoozis": 2, "Rude Kaiser": 1, "Beaver Warrior": 2, "Hitotsu-me Giant": 3, "Mountain Warrior": 2, "Solitude": 2,
   "Ogre of the Black Shadow": 2, "Leogun": 2, "Flower Wolf": 2, "Pale Beast": 2, "Frenzied Panda": 2, "Tiger Axe": 2, "Battle Ox": 2, "Beast Fangs": 3,
   "Horn of the Unicorn": 2, "Forest": 3, "Red Medicine": 2, "Mystical Moon": 2}),
 "Viper": (2, "Jackal hunter: snakes and graveyard zombies", {
   "Krokodilus": 2, "Grappler": 2, "Serpent Marauder": 2, "Yormungarde": 2, "Beaked Snake": 2, "Ancient Lizard Warrior": 2,
   "Emperor of the Land and Sea": 1, "Zombie Warrior": 2, "The 13th Grave": 3, "Shadow Ghoul": 2, "The Snake Hair": 2,
   "Ghoul with an Appetite": 1, "Armored Zombie": 2, "Dragon Zombie": 2, "Skull Servant": 3, "Yami": 3, "Violet Crystal": 2, "Raise Body Heat": 2, "Red Medicine": 3}),
 "Madame Hex": (3, "Jackal elite: spellcasters and clowns with dark equips", {
   "Mystical Elf": 2, "Illusionist Faceless Mage": 2, "Rogue Doll": 2, "Maha Vailo": 2, "Musician King": 1, "Gemini Elf": 2,
   "Dark Elf": 2, "Ill Witch": 2, "Maiden of the Moonlight": 2, "Dark Witch": 1, "Mystic Clown": 2, "Feral Imp": 2, "Witty Phantom": 2,
   "Crass Clown": 2, "Spirit of the Winds": 2, "Yami": 3, "Book of Secret Arts": 2, "Dark Energy": 2, "Swords of Revealing Light": 2, "Red Medicine": 3}),
 "Granite": (3, "Jackal elite: stone walls and guardian machines", {
   "Giant Soldier of Stone": 2, "Sand Stone": 2, "Stone Ogre Grotto": 2, "Millennium Golem": 1, "Destroyer Golem": 2, "Stone Ghost": 2,
   "Barrel Rock": 2, "The Statue of Easter Island": 2, "Giganto": 1, "Cyber Soldier": 2, "Guardian of the Throne Room": 1,
   "Royal Guard": 1, "Blocker": 2, "Golgoil": 2, "Giga-tech Wolf": 2, "Rock Ogre Grotto #2": 2, "Mountain": 3, "Wasteland": 2, "Cyber Shield": 2,
   "Swords of Revealing Light": 2, "Red Medicine": 3}),
 "Old Jackal": (7, "Jackal boss: big beasts and fiends, swords of light", {
   "Garvas": 2, "Ancient One of the Deep Forest": 2, "Flower Wolf": 3, "Togex": 2, "Leogun": 2, "Monster Tamer": 2, "Swordstalker": 1,
   "Ushi Oni": 1, "Soul Hunter": 1, "Bickuribox": 1, "Beautiful Beast Trainer": 2, "Pale Beast": 2, "Beast Fangs": 3, "Horn of the Unicorn": 2,
   "Dark Energy": 2, "Yami": 2, "Forest": 2, "Swords of Revealing Light": 3, "Red Medicine": 3, "Mooyan Curry": 2}),
}
GANG_MEMBERS = [  # id, deck key, tier(1..3 gang tier; boss 4), copy base, slot
 ("dusty", "Dusty", 1, "Villager 2"), ("scrap", "Scrap", 1, "Villager 3"),
 ("fang", "Fang", 2, "Mage Soldier"), ("viper", "Viper", 2, "Desert Mage"),
 ("madame_hex", "Madame Hex", 3, "High Mage Secmeton"), ("granite", "Granite", 3, "Labyrinth Mage"),
 ("old_jackal", "Old Jackal", 4, "Guardian Sebek")]
GANG_SLOT0 = 43; FIGHTER_SLOT0 = 50
COPY_BY_TIER = {1: ["Villager 1", "Villager 2", "Villager 3"], 2: ["Mage Soldier", "Villager 1", "Ocean Mage"], 3: ["Ocean Mage", "Mage Soldier", "Forest Mage"],
                4: ["Forest Mage", "Mountain Mage", "Meadow Mage"], 5: ["Mountain Mage", "Meadow Mage", "Desert Mage"],
                6: ["Desert Mage", "High Mage Secmeton", "High Mage Anubisius"], 7: ["High Mage Atenza", "High Mage Martis", "Guardian Sebek"],
                8: ["Guardian Neku", "Labyrinth Mage", "High Mage Kepura"]}   # placeholders: portrait + AI of a generic disc duelist, no story character
FIGHTER_TYPES = {
 "doughboy": ["Plant", "Beast"], "beetle_ben": ["Insect"], "reed_ria": ["Reptile", "Beast"], "big_flour": ["Plant", "Insect", "Beast"],
 "deck_dora": ["Warrior", "Aqua"], "bilge_bo": ["Fish"], "rigger_rin": ["Winged Beast", "Sea Serpent"], "captain_krill": ["Fish", "Sea Serpent", "Warrior"],
 "gull_gus": ["Winged Beast"], "eel_ed": ["Fish", "Sea Serpent"], "rope_rae": ["Aqua", "Thunder"], "old_barnac": ["Fish", "Aqua", "Sea Serpent"],
 "crab_cal": ["Aqua"], "flare_fay": ["Pyro", "Reptile"], "sand_fly": ["Insect"], "hull_hank": ["Aqua", "Insect", "Pyro"],
 "moss_mel": ["Plant"], "bark_bo": ["Beast"], "twig_tess": ["Insect"], "old_stump": ["Beast-Warrior", "Beast", "Dinosaur"],
 "pick_pete": ["Rock"], "gear_gwen": ["Machine"], "wing_wes": ["Winged Beast"], "blast_bart": ["Warrior", "Machine", "Rock"],
 "daisy_dee": ["Fairy", "Plant"], "hare_hal": ["Beast"], "mist_mina": ["Spellcaster", "Fairy"], "maze_queen": ["Fairy", "Spellcaster", "Plant"],
 "mummy_moe": ["Zombie"], "scarab_sia": ["Reptile", "Zombie"], "dust_dara": ["Spellcaster"], "tomb_lord": ["Zombie", "Rock", "Spellcaster"],
 "clown_cleo": ["Fiend"], "juggle_jo": ["Machine", "Warrior"], "spark_sam": ["Thunder", "Dragon"]}
RUNG_OFFSET = [0, 1, 1, 2]

# ------------------------------------------------------------------ build all
def main():
    out = {}
    decks = collections.OrderedDict()
    # --- fighters / arenas
    fighters = []; arenas = []
    slot = FIGHTER_SLOT0
    fighter_text = {f[0]: f for f in T.FIGHTERS}
    for aid in ARENA_ORDER:
        loc = LOC[aid]; names = T.ARENA_NAMES[aid]
        ladder = []
        rung_ids = [f[0] for f in T.FIGHTERS if f[1] == aid]
        if aid == "fair": rung_ids.append("old_jackal")
        assert len(rung_ids) == 4, (aid, rung_ids)
        for i, fid in enumerate(rung_ids):
            tier = min(9, loc["tier"] + RUNG_OFFSET[i])
            champion = i == 3
            if fid == "old_jackal":
                deck_key = "Old Jackal"; fighter_ref = "old_jackal"; tier_used = 7
            else:
                nm = fighter_text[fid][2]
                deck_key = nm
                decks[nm] = build_deck(nm, aid, FIGHTER_TYPES[fid], tier, "%s: %s" % (nm, "/".join(FIGHTER_TYPES[fid])))
                base = COPY_BY_TIER[min(tier, 8)][(len(fighters)) % 3]
                fighters.append({"id": fid, "arena": aid, "rung": i + 1, "name": nm, "tier": tier,
                                 "duelist": {"id": "eco_" + fid, "copy": base, "name": nm, "slot": slot},
                                 "deck": deck_key, "types": FIGHTER_TYPES[fid], "text_id": "fighter_pre." + fid})
                slot += 1
                tier_used = tier
            ladder.append({"rung": i + 1, "fighter": fid, "tier": tier_used, "deck": deck_key, "champion": champion,
                           "coins": r5(WIN_COINS[tier_used - 1] * 0.8), "xp_base": WIN_XP[tier_used - 1],
                           "drops": {"context": "arena_champion" if champion else "arena_bout", "count": CONTEXT_COUNT["arena_champion" if champion else "arena_bout"]}})
        fee = r5(WIN_COINS[loc["tier"] - 1] * 1.0)
        ch = ladder[-1]
        arenas.append({
            "id": aid, "location": aid, "area": loc["area"], "interior_area": "arena_" + aid, "name": names[0], "setting": names[2],
            "keeper": names[6], "tip_id": "arena_tip." + aid, "name_id": "arena." + aid,
            "entry_anchor": "%s.arena_door" % loc["area"], "interior_anchors": ["entry", "ring", "bookie", "crowd"],
            "unlock": {"level_min": max(2, loc["arrival"] - 2), **({"stage_min": loc["stage_min"]} if "stage_min" in loc else {})},
            "fee": fee, "ladder": ladder, "pool": aid,
            "first_clear": {"coins": WIN_COINS[ch["tier"] - 1] * 3, "xp_mult": 2.0, "drops": {"context": "arena_clear", "count": 1}, "title_id": "arena_title." + aid},
            "repeat_clear": {"coins": WIN_COINS[ch["tier"] - 1] * 1, "xp_mult": 0.0, "drops": {"context": "arena_clear", "count": 1}},
            "run_rules": "A run is the whole ladder: pay the fee once, lose a bout and the run ends (earnings kept). Progress inside a run is saved in the arena byte (rung)."})
    # --- gang
    members = []
    for i, (gid, dkey, gtier, base) in enumerate(GANG_MEMBERS):
        tier, theme, cards = GANG_DECKS[dkey]
        decks[dkey] = {"duelist": dkey, "chapter": 0, "difficulty_tier": tier, "theme": theme, "fixed": True, "total": sum(cards.values()), "cards": dict(sorted(cards.items()))}
        members.append({"id": gid, "name": T.GANG[gid][0], "gang_tier": gtier, "difficulty_tier": tier, "deck": dkey,
                        "duelist": {"id": "eco_" + gid, "copy": base, "name": dkey if gid != "old_jackal" else "Old Jackal", "slot": GANG_SLOT0 + i},
                        "sprite": "gang_" + gid, "appears": "ambush" if gid != "old_jackal" else "arena_boss_only",
                        "taunt_id": "gang_taunt." + gid, "win_id": "gang_win." + gid, "lose_id": "gang_lose." + gid})
    decks_doc = {"schema": "journey-decks/1",
                 "rules": "Same as ../decks.json and duelist_kingdom/decks_dk.json: 40 cards, max 3 copies, at least 14 distinct, no Ritual cards, no ritual-only monsters, no card of the OLD story's custom slots. Forty cards is the only deck rule of Forbidden Memories (the game has no 'deck cost').",
                 "generated_by": "src/gen_economy.py (arena fighters, seeded) and hand-written gang decks",
                 "decks": decks}
    json.dump(decks_doc, open(os.path.join(ROOT, "decks_economy.json"), "w"), indent=1)

    # --- card pools
    pools_doc = {"schema": "journey-card-pools/1",
      "rules": {
        "droppable_only_here": "A card can drop in a location only if it is in that location's pool. Every duel won in an area of that location (story duels, rematches, ambushes) and every arena bout rolls from that location's pool. Duels in castle_top use 'hall'. cistern and ship_deck keep their story rewards only.",
        "roll": "1) pick the context's odds (economy.json drop_odds), add the level shift (levels.json), 2) drop rarities with no available card (min_level, arena_only for non-arena contexts) fall to the next lower rarity, 3) pick a card of that rarity by weight.",
        "area_to_pool": {"village": "village", "harbor": "harbor", "ship_deck": "ship", "kingdom_beach": "beach", "kingdom_forest": "forest", "kingdom_mountain": "mountain",
                         "kingdom_meadow": "meadow", "kingdom_desert": "desert", "kingdom_fair": "fair", "castle_gate": "gate", "castle_hall": "hall", "castle_top": "hall",
                         "cistern": None, "ship_deck": None},
        "min_level": "C from level 1; B from the location's arrival level; A arrival+3; S arrival+6 (S is arena_only)",
        "banned": "no ritual cards, ritual-only or ritual-result monsters, no Exodia pieces, no card whose slot the old story replaced with a custom card (%s), no password-less monster over power 1950 (the legends)" % sorted(CUSTOM_SLOTS),
        "rarity": "monsters: power = max(ATK, 0.9 DEF): C <= 1250, B <= 1700, A <= 2100, S above (S only from a per-location whitelist). Fields, Red Medicine, Sparks, Cursebreaker, Hinotama = C; equips and Mooyan Curry = B; Swords of Revealing Light and Stop Defense = A.",
        "weights": "weight 3 = featured (signature) card of the location, else 1"},
      "pools": []}
    for l in LOCS:
        pools_doc["pools"].append({"id": l["id"], "area": l["area"], "name": T.PLACE_NAMES[l["id"]][0], "theme": l["theme"], "types": l["types"],
                                   "arrival_level": l["arrival"], "max_power": l["max_power"], "s_whitelist": l["s"], "entries": POOLS[l["id"]]})
    json.dump(pools_doc, open(os.path.join(ROOT, "card_pools.json"), "w"), indent=1)

    # --- global rarity table
    rar = {}
    for r in CARDS.values():
        if r["type"] in ("Ritual",): continue
        if r["type"] in ("Trap",): c = "A"
        elif is_monster(r): c = mon_class(r)
        elif r["name"] in SPELL_A: c = "A"
        elif r["name"] in SPELL_C: c = "C"
        elif r["type"] == "Equip": c = "B"
        elif r["name"] == "Mooyan Curry": c = "B"
        else: c = "S"
        rar[r["name"]] = c
    json.dump({"schema": "journey-card-rarity/1", "note": "Class of every non-ritual card, used for selling and the deck-power cap. Cards with banned=true are never dropped or sold in shops.",
               "rarity": rar, "banned": sorted(n for n, r in CARDS.items() if banned(r))}, open(os.path.join(ROOT, "card_rarity.json"), "w"), indent=1)

    # --- story-protected cards
    st = json.load(open(STORY))
    give = set()
    def walk(n):
        if isinstance(n, dict):
            for k, v in n.items():
                if k == "give_card" and isinstance(v, str): give.add(v)
                walk(v)
        elif isinstance(n, list):
            for v in n: walk(v)
    walk(st)

    # --- shops
    shops = []
    bit = 0
    keepers = {"village": "teana", "harbor": "dock_dan", "ship": "purser", "beach": "shell_sue", "forest": "hermit_hob", "mountain": "cliff_cass",
               "meadow": "rose_rue", "desert": "nomad_nia", "fair": "bazaar_bea", "gate": "pawn_paul"}
    shop_anchor = {"village": "village.teana_stall"}
    for l in LOCS:
        if not l["shop"]: continue
        sid = l["id"]; w = WIN_COINS[l["tier"] - 1]
        pool = [e for e in POOLS[sid] if not e.get("arena_only")]   # the rings' prizes are never sold
        price = lambda cl: r5(w * WEQ[cl])
        feat = {e["card"] for e in pool if e["weight"] == 3}
        always = []
        for e in pool:
            if e["rarity"] == "C" and (e["kind"] == "field" and e["card"] in TYPE_FIELD.get(l["types"][0], []) or e["card"] == "Red Medicine"):
                always.append(e["card"])
        cm = [e["card"] for e in pool if e["rarity"] == "C" and e["kind"] == "monster"]
        cm.sort(key=lambda n: (n not in feat, CARDS[n]["id"]))
        always += cm[:5]
        singles = [{"card": n, "rarity": "C", "price": price("C"), "min_level": 1} for n in dict.fromkeys(always)]
        a_cands = [e for e in pool if e["rarity"] == "A" and e["kind"] == "monster"]
        a_cands.sort(key=lambda e: (-e["weight"], -power(CARDS[e["card"]])))
        limited = []
        for e in a_cands[:2 if sid not in ("fair", "gate") else 1]:
            limited.append({"card": e["card"], "rarity": "A", "price": price("A") * 2, "max_buy": 1, "bit": bit, "min_level": l["arrival"] + 3})
            bit += 1
        if sid in ("fair", "gate"):
            for s in l["s"][:2]:
                limited.append({"card": s, "rarity": "S", "price": price("S"), "max_buy": 1, "bit": bit, "min_level": l["arrival"] + 6})
                bit += 1
        if sid == "village":
            e = [e for e in pool if e["card"] == "Dragon Treasure"]
            # a stage-unlocked extra: after the Given treasure, Teana sells the Mooyan Curry she baked with the honey
            limited.append({"card": "Mooyan Curry", "rarity": "B", "price": price("B"), "max_buy": 3, "bit": bit, "min_level": 1,
                            "unlock": {"flags_all": ["treasure_given"]}})
            bit += 1
        packs = [
          {"id": "common", "kind": "common", "price": r5(w * PACK_WEQ["common"]), "min_level": 1, "count": 5,
           "slots": [{"rarity": "C"}, {"rarity": "C"}, {"rarity": "C"}, {"rarity": "B"}, {"odds": {"B": 75, "A": 25}}]},
          {"id": "rare", "kind": "rare", "price": r5(w * PACK_WEQ["rare"]), "min_level": max(6, l["arrival"] + 3), "count": 5,
           "slots": [{"rarity": "C"}, {"rarity": "B"}, {"rarity": "B"}, {"rarity": "A"}, {"odds": {"B": 40, "A": 60}}]},
          {"id": "grand", "kind": "grand", "price": r5(w * PACK_WEQ["grand"]), "min_level": max(16, l["arrival"] + 8), "count": 5,
           "slots": [{"rarity": "B"}, {"rarity": "B"}, {"rarity": "A"}, {"rarity": "A"}, {"odds": {"A": 100}}]}]
        shops.append({
          "id": sid, "area": l["area"], "name": T.SHOP_NAMES[sid][0], "name_id": "shop." + sid, "pool": sid,
          "keeper": {"id": keepers[sid], "name": T.KEEPERS[keepers[sid]][0], "existing_npc": sid == "village", "greet_id": "keeper_greet." + keepers[sid]},
          "anchor": shop_anchor.get(sid, "%s.shop_stall" % l["area"]), "price_win": w, "tier": l["tier"],
          "open": ({"stage_min": l["stage_min"]} if "stage_min" in l else {}),
          "stock": {
            "always": singles,
            "rotating": [
              {"slot": "b", "rarity": "B", "count": 3, "min_level": l["arrival"], "price": price("B"), "from": "pool"},
              {"slot": "a", "rarity": "A", "count": 2, "min_level": l["arrival"] + 3, "price": price("A"), "from": "pool"}],
            "limited": limited, "packs": packs},
          "rotation": {"every_duels": 6, "algorithm": "epoch = jm.duels / every_duels; for each slot, candidates = pool entries of the rarity with min_level <= level, not 'always'/'limited'; sort by fnv1a32(shop_id + ':' + slot + ':' + epoch + ':' + card_id); take the first count"},
          "imported": ({"from_pools": [x["id"] for x in LOCS if x["shop"] and x["id"] not in ("fair", "gate", "hall")], "packs_only": True, "price_mult": 1.25,
                        "note": "The Grand Bazaar also sells the common pack of every earlier location at +25%: a way to fill the gaps in the collection. Drops stay local."} if sid == "fair" else None),
          "sell": {"enabled": True, "rate": SELL_RATE, "unsellable": "cards the story gave, and copies the deck uses"},
          "stage_note": None})
    shop_doc = {"schema": "journey-shops/1",
      "rules": {
        "buy_sell": "Every shop buys and sells. Sell price = round5(sell_rate * weq[rarity] * sell_base_win), one global price (no arbitrage between towns, and always below the cheapest buy price).",
        "no_healing": "There is no healing item and no healing service: duels do not carry life points, so nothing needs healing.",
        "stock_kinds": "always = fixed singles (commons) and packs; rotating = B and A cards re-picked every 6 won or lost duels, no storage needed; limited = one-time or capped purchases (bit in bought[]); each entry may have min_level, unlock.stage_min or unlock.flags_all.",
        "no_shop": "cistern (quest dungeon), castle_hall and castle_top (finale) have no shop; harbor opens at stage 5."},
      "shops": shops}
    json.dump(shop_doc, open(os.path.join(ROOT, "shops.json"), "w"), indent=1)

    # --- levels
    levels = []
    cum = 0
    gang_levels = [(1, 4, {"1": 100}), (5, 7, {"1": 70, "2": 30}), (8, 10, {"1": 30, "2": 70}), (11, 13, {"2": 80, "3": 20}),
                   (14, 17, {"2": 40, "3": 60}), (18, 30, {"3": 100})]
    SHOP_TIER_LEVELS = [6, 10, 14, 18]
    events = collections.defaultdict(list)
    for ar in arenas: events[ar["unlock"]["level_min"]].append("arena:" + ar["id"])
    for i, lv in enumerate(SHOP_TIER_LEVELS): events[lv].append("shop_tier:%d" % (i + 2))
    for g in gang_levels[1:]: events[g[0]].append("gang_tier")
    for L in range(1, LEVEL_CAP + 1):
        need = 10 * L + L * L if L < LEVEL_CAP else 0
        sh_b, sh_a, sh_s = round(0.4 * (L - 1), 2), round(0.25 * (L - 1), 2), round(0.04 * (L - 1), 2)
        gw = [g for g in gang_levels if g[0] <= L <= g[1]][0][2]
        levels.append({"level": L, "xp_total": cum, "xp_to_next": need, "rank": 1 + min(6, L // 5),
                       "shop_tier": 1 + sum(1 for t in SHOP_TIER_LEVELS if L >= t),
                       "drop_shift": {"B": sh_b, "A": sh_a, "S": sh_s}, "coin_bonus_pct": 2 * ((L - 1) // 3),
                       "gang_tier_weights": gw, "deck_power_cap": 52 + 3 * L, "events": events.get(L, [])})
        cum += need
    levels_doc = {"schema": "journey-levels/1", "cap": LEVEL_CAP,
      "xp_curve": "xp_to_next(L) = 10*L + L^2 (level 1 -> 2 needs 11 xp, level 29 -> 30 needs 1131 xp), total 12,951 xp to reach 30. Level is derived from the saved xp total: no level field in the save.",
      "perks": {
        "shop_tier": "Which stock tier is visible: rotating A cards, rare packs and grand packs have their own min_level, tier is the summary shown in the status screen.",
        "drop_shift": "Percentage points moved from C to B, A and S in every drop roll (before context odds are applied as a base).",
        "coin_bonus_pct": "+2% duel win coins per 3 levels (max +18%).",
        "gang_tier_weights": "Which Jackal tier ambushes the player (see gang.json).",
        "arena_unlock": "Arenas ask level_min (arenas.json).",
        "deck_power_cap": "OPTIONAL (disabled by default, see economy.json features.deck_power_cap): Forbidden Memories has no deck cost; if enabled the deck editor's exit checks C=1, B=2, A=4, S=8 points per card against this cap."},
      "ranks": ["Rookie", "Duelist", "Challenger", "Veteran", "Expert", "Master", "Legend"],
      "table": levels}
    json.dump(levels_doc, open(os.path.join(ROOT, "levels.json"), "w"), indent=1)

    # --- gang
    gang_doc = {"schema": "journey-gang/1", "gang": {"id": "dune_jackals", "name": T.GANG_NAME[0], "name_id": "gang.name", "lore_id": "gang.lore",
        "sprite_hint": "Street duelists in sand-colored rags with a tin jackal-head amulet. Seven looks: dusty pup, scrap junker, fang brute, viper, hex lady, granite brute, old boss."},
      "members": members, "tier_by_level": [{"level": [a, b], "weights": w} for a, b, w in gang_levels],
      "stakes": {
        "percent_by_gang_tier": {"1": 0.10, "2": 0.15, "3": 0.20},
        "min_by_gang_tier": {"1": 10, "2": 25, "3": 60},
        "max_by_gang_tier": {"1": 120, "2": 400, "3": 1500},
        "formula": "stolen = min(coins, clamp(round(coins * pct), min, max)); never negative, never more than the player holds",
        "first_three_ambushes_factor": 0.5,
        "loss_streak_relief": {"after_losses": 2, "stolen_factor": 0.5, "cooldown_factor": 1.5},
        "truce_factor": 0.5,
        "recover_on_win": 0.5,
        "win_reward": {"coins_mult": 1.25, "drops_context": "ambush_win", "xp": "as a normal duel win of the member's difficulty tier"}},
      "ambush": {
        "who_approaches": "The gang approaches the player, never the other way round: members spawn off the edge of the view and run in at 6.5 units/frame, faster than the player's run (4.4).",
        "min_purse": 25,
        "min_purse_note": "A player with fewer coins than min_purse is never ambushed (nothing to steal); the countdown waits at zero.",
        "cooldown_walk_seconds": {"min": 75, "max": 150},
        "cooldown_note": "Counts only while the player walks (running counts by distance, so it advances 1.7x faster per second but the distance is the same). Rolled uniformly in [min,max] / area frequency.",
        "walk_speed_units_per_frame": 2.6, "run_speed_units_per_frame": 4.4,
        "tutorial": {"no_ambush_before_stage": 3, "warmup_walk_seconds": 300, "first_ambush": {"member": "dusty", "stake_cap_coins": 20,
                      "note": "The first ambush is always Dusty with a coin cap of 20 and a one-page explanation."}},
        "grace_walk_seconds": {"after_win": 45, "after_loss": 90, "after_area_change": 20, "after_scene_or_menu": 10},
        "frequency_by_area": {"village": 1.0, "harbor": 1.0, "ship_deck": 0.8, "kingdom_beach": 1.0, "kingdom_forest": 1.1, "kingdom_mountain": 1.1, "kingdom_meadow": 1.0, "kingdom_desert": 1.2},
        "eligible_areas": ["village", "harbor", "ship_deck", "kingdom_beach", "kingdom_forest", "kingdom_mountain", "kingdom_meadow", "kingdom_desert"],
        "never_in": ["cistern", "kingdom_fair", "castle_gate", "castle_hall", "castle_top", "every arena_* interior", "every shop screen"],
        "suppressed_while": ["a dialogue, banner or scene is on screen", "a menu or shop is open", "the quest arrow's target is within 150 units (a scripted beat is about to happen)",
                              "the player is within the safe radius of an anchor in safe_zones", "the player is on a stage window listed in blocked_stage_windows", "a duel just ended (grace)"],
        "safe_zones": [{"anchor": "village.teana_stall", "radius": 140}, {"anchor": "village.bakery_door", "radius": 120}, {"anchor": "village.house_ne_door", "radius": 110},
                        {"anchor": "village.mini_pyramid_hatch", "radius": 120}, {"anchor": "village.bridge_north", "radius": 120}, {"anchor": "village.hero_start", "radius": 120},
                        {"anchor": "*.shop_stall", "radius": 150}, {"anchor": "*.arena_door", "radius": 130}, {"anchor": "*.spawn", "radius": 150}, {"anchor": "kingdom_beach.camp", "radius": 200}],
        "blocked_stage_windows": [{"area": "village", "stage": [0, 2], "reason": "tutorial and first quests"}],
        "sequence": [
          "1. countdown hits 0 and every eligibility rule holds -> state AMBUSH_WARN",
          "2. player input is locked (no walk, no run, no menu): the player turns toward the nearest view edge, a red '!' pops over the head, banner 'AMBUSH!' (alert banner, 1.2 s) and the sting sound plays",
          "3. the chosen member runs in from the edge and stops 24 units from the player (about 0.7 s at 60 fps, 1.4 s at 30 fps)",
          "4. one taunt page (speaker name in yellow) and the stake line 'They want N coins!'",
          "5. the game's own duel starts at once; the duel's quit/forfeit option is disabled (it would count as a loss)",
          "6. win: coins x1.25, ambush_win drop, xp, recover 50% of the coins stolen last time, grace 45 s; loss: stolen coins taken, 'They took N coins!', member runs away, grace 90 s, never a game over"],
        "cannot_flee": "Movement is locked from the banner on; the gang is faster than a runner; the duel cannot be abandoned; the countdown only starts again after the duel."},
      "decks_file": "decks_economy.json"}
    json.dump(gang_doc, open(os.path.join(ROOT, "gang.json"), "w"), indent=1)

    # --- arenas
    arenas_doc = {"schema": "journey-arenas/1",
      "rules": {
        "clandestine": "Arenas are hidden: they appear as an interact object (arena_door anchor) only after the shop keeper's tip, which the keeper gives the first time the player talks to them with level >= unlock level. arena byte bit7 = found.",
        "run": "Pay the fee, fight rung 1 to 4 in order. A win pays the rung's coins (80% of a normal duel win) and xp and rolls the rung's drop context; the champion bout (rung 4) deals 2 drops. A loss ends the run (earnings kept, fee gone); the run can be repeated at once.",
        "first_clear": "Coins x3 of the champion tier, xp x2, a guaranteed A (S 10%) card, a rank title in the status screen.",
        "repeat": "After the first clear a run pays bout coins and xp as before; the clear bonus is the champion tier's coins x1 and one A/S card (no xp bonus). This is the card-farming loop of the location.",
        "levelling": "Arena xp uses the same level-difference factor as every duel (economy.json formulas.xp), so over-levelled farmers earn less.",
        "no_stars": "Arena duels never touch stars (stars_wager false).",
        "drops": "All arena drops come from the location's own pool (card_pools.json) with the contexts of economy.json."},
      "fighters": fighters, "arenas": arenas}
    json.dump(arenas_doc, open(os.path.join(ROOT, "arenas.json"), "w"), indent=1)

    # --- economy
    quests = {"q01_whispers": 20, "q02_sage": 30, "q03_stakeout": 20, "q04_lost": 80, "q05_won": 80, "q06_given": 60, "q07_harbor": 60,
              "q08_courier": 100, "q09_farewell": 0, "q10_ship": 0, "s01_baker": 25}
    story_duels = [{"id": d["id"], "tier": d["difficulty_tier"], "stars_wager": d.get("stars_wager")} for d in st["duels"]]
    eco = {"schema": "journey-economy/1",
      "currency": {"id": "coins", "name": "Coins", "name_id": "currency.name", "symbol": "c", "cap": 99999, "start": 0,
                   "note": "Not called 'star chips': the story already uses the Star Chip item for stars, and the outline's 'star chip' fair shops become coin shops."},
      "tiers": {"win_coins": WIN_COINS, "win_xp": WIN_XP, "nominal_level": NOMINAL_LEVEL,
                "note": "index = opponent difficulty tier - 1 (decks' difficulty_tier, 1..10). nominal_level is the level a duelist of that tier is 'worth'."},
      "formulas": {
        "coins_win": "round(win_coins[tier] * context_mult * (1 + coin_bonus_pct(level)/100))",
        "coins_loss": "0 (a lost duel pays nothing; an ambush loss costs stolen coins)",
        "context_mult": {"story_first_win": 1.0, "story_rematch": 0.5, "ambush_win": 1.25, "arena_bout": 0.8, "free_duel": 1.0},
        "xp": "round(win_xp[tier] * clamp(1 + 0.12*(nominal_level[tier] - player_level), 0.2, 1.8)); a loss gives 25% of that (min 1); 0 at level cap",
        "level": "largest L with levels.table[L].xp_total <= xp",
        "arena_fee": "round5(win_coins[arena tier] * 1.0)",
        "sell_price": "round5(sell_rate * weq[rarity] * sell_base_win)",
        "buy_price": "round5(win_coins[shop tier] * weq[rarity])  (packs: pack_weq)"},
      "prices": {"weq": WEQ, "pack_weq": PACK_WEQ, "sell_rate": SELL_RATE, "sell_base_win": SELL_BASE_WIN, "round_to": 5,
                 "meaning": "A common single costs about one win of the shop's tier, B 2.5 wins, A 8 wins, S 30 wins; packs 4 / 12 / 30 wins.",
                 "healing": "none"},
      "drop_odds": {"base_percent": BASE_ODDS, "contexts": CONTEXT_ODDS, "cards_per_context": CONTEXT_COUNT,
                    "s_rule": "S cards are arena_only: in every other context their share falls to A."},
      "rewards_story": {"quest_coins": quests, "quest_note": "paid when the quest's last step completes (new effect give_coins in the quest-complete banner)",
                        "intro": "The first coins come from Simon's test duel (stage 1 -> 2): the HUD shows 'Coins' for the first time with a one-page tutorial banner (eco_bits bit0).",
                        "duels": story_duels, "protected_cards": sorted(give),
                        "protected_note": "Cards the story hands out (give_card effects) cannot be sold."},
      "state": {
        "save_version": 4,
        "append_to": "Journey (mods/ow-poc/jm.h), after pt_set. Save_Read zero-fills the tail of an older file, so every new field must be valid at 0.",
        "c_struct": "typedef struct {\n  int coins;              /* 0..99999 */\n  int xp;                 /* total xp, level derived (levels.json) */\n  int amb_cd;             /* ambush countdown, 1/30 s of walking; 0 = roll a new one */\n  int amb_walk;           /* total walking time since new game, 1/30 s (tutorial warm-up) */\n  int gang_loot;          /* coins the last ambush took, 50% recoverable on the next win */\n  unsigned short amb_won, amb_lost;\n  unsigned char amb_streak, amb_first_done, pad[2];\n  unsigned char arena[8]; /* per arena (arenas.json order): bit7 found, bits 3-6 clears (0..15), bits 0-2 rung (0..4) */\n  unsigned int bought[2]; /* shops.json limited[].bit, 64 one-time purchases */\n  unsigned int eco_bits;  /* bit0 intro seen, bit1 gang truce, bit2 level-cap banner seen */\n} Economy;   /* 52 bytes */",
        "flags_used": 0,
        "flags_note": "No story flag is used (30 of 32 are taken). Everything is a counter or a bit inside Economy.",
        "rotation": "Shop stock rotation is derived from jm.duels, so no stock is stored."},
      "features": {"deck_power_cap": {"enabled": False, "points": {"C": 1, "B": 2, "A": 4, "S": 8}, "cap": "52 + 3 * level", "note": "Optional. FM has no deck cost."},
                   "ambush_repellent_item": {"enabled": False, "note": "A shop item that pauses the countdown for 5 minutes. Off by default: it weakens the difficulty the user asked for."},
                   "gang_truce_after_boss": {"enabled": True, "note": "Beating Old Jackal in the Underfair arena halves ambush frequency and stolen coins for good (eco_bits bit1)."}},
      "effects_new": ["give_coins {n}", "take_coins {n}", "give_xp {n}", "open_shop {id}", "open_arena {id}", "set_ambush {on|off}"],
      "conditions_new": ["coins_min", "level_min", "level_max"],
      "files": {"shops": "shops.json", "pools": "card_pools.json", "gang": "gang.json", "arenas": "arenas.json", "levels": "levels.json", "decks": "decks_economy.json", "rarity": "card_rarity.json",
                "text_en": "en/economy.en.json", "text_pt": "pt/economy.pt.json"},
      "new_areas": [{"id": "arena_" + a, "name_id": "arena." + a, "art": "NEW art (one screen interior)"} for a in ARENA_ORDER]}
    json.dump(eco, open(os.path.join(ROOT, "economy.json"), "w"), indent=1)

    # --- text files
    for lang, idx in (("en", 0), ("pt", 1)):
        names = {"currency": {"name": "Coins" if idx == 0 else "Moedas"},
                 "shops": {k: v[idx] for k, v in T.SHOP_NAMES.items()},
                 "places": {k: v[idx] for k, v in T.PLACE_NAMES.items()},
                 "keepers": {k: v[idx] for k, v in T.KEEPERS.items()},
                 "arenas": {k: v[idx] for k, v in T.ARENA_NAMES.items()},
                 "fighters": {f[0]: f[2 + idx] for f in T.FIGHTERS},
                 "gang": {"name": T.GANG_NAME[idx], **{k: v[idx] for k, v in T.GANG.items()}}}
        names["fighters"]["old_jackal"] = T.GANG["old_jackal"][idx]
        dlg = {}
        for k, v in T.KEEPERS.items(): dlg["keeper_greet." + k] = v[2 + idx]
        for k, v in T.GENERIC.items(): dlg[k] = v[idx]
        for k, v in T.ARENA_NAMES.items(): dlg["arena_tip." + k] = v[4 + idx]
        for k, v in T.ARENA_GENERIC.items(): dlg[k] = v[idx]
        for f in T.FIGHTERS: dlg["fighter_pre." + f[0]] = f[4 + idx]
        for k, v in T.GANG.items():
            dlg["gang_taunt." + k] = v[2 + idx]; dlg["gang_win." + k] = v[4 + idx]; dlg["gang_lose." + k] = v[6 + idx]
        desc = {"gang_lore": T.GANG_LORE[idx], "arena_settings": {k: v[2 + idx] for k, v in T.ARENA_NAMES.items()}}
        ui = {k: v[idx] for k, v in T.UI.items()}
        doc = {"schema": "journey-economy-text/1", "language": lang, "charset_dialogue": "A-Za-z0-9 .,!?'-  (<= 3 lines of 32)", "charset_ui": "dialogue charset plus : % + / $ positional %n$s",
               "names": names, "dialogue": dlg, "ui": ui, "descriptions": desc}
        d = os.path.join(ROOT, lang); os.makedirs(d, exist_ok=True)
        json.dump(doc, open(os.path.join(d, "economy.%s.json" % lang), "w"), indent=1, ensure_ascii=True)
    print("generated: pools", {k: len(v) for k, v in POOLS.items()}, "decks", len(decks), "fighters", len(fighters))

if __name__ == "__main__":
    main()
