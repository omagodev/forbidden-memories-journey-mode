"""Themed 40-card decks. name -> copies (max 3). Exactly 40 cards each. Real FM card names (notes/card-catalog.csv)."""

DECKS = {}
def deck(key, duelist, chapter, tier, theme, cards, notes=""):
    DECKS[key] = {"duelist": duelist, "chapter": chapter, "difficulty_tier": tier, "theme": theme, "cards": cards, "notes": notes}

# ---------------------------------------------------------------- chapter 1 (tier 1: low levels, ATK <= ~1600)
deck("Simon Muran", "Simon Muran", 1, 1, "Old sage: Spellcasters and Fairies with healing and light equips",
 {"Mystical Elf":3,"White Magical Hat":3,"Spirit of the Harp":2,"Lady of Faith":2,"Magician of Faith":2,"Eldeen":2,
  "Ancient Elf":2,"Dryad":2,"Rogue Doll":2,"Fairy's Gift":2,
  "Elf's Light":3,"Book of Secret Arts":3,"Mystical Moon":2,"Mooyan Curry":2,"Red Medicine":2,"Sogen":1,"Forest":1},
 "Tutorial deck: slow, no big hitters; equips make duels readable.")
deck("Teana", "Teana", 1, 1, "Mischievous imps: small Fiends with Yami support",
 {"Feral Imp":3,"Horn Imp":3,"Ryu-kishin":2,"Kuriboh":3,"Sangan":2,"Mask of Darkness":2,"Meda Bat":2,"Midnight Fiend":2,
  "Needle Ball":2,"Big Eye":2,"Witty Phantom":2,"Hiro's Shadow Scout":1,
  "Dark Energy":3,"Black Pendant":2,"Yami":2,"Dark Hole":1,"Stop Defense":2},
 "Tutorial deck: weak monsters, Fiends like Yami.")
deck("Jono", "Jono", 1, 1, "Street brawler: baby dragons and warriors with Dragon Treasure",
 {"Baby Dragon":3,"Petit Dragon":3,"Winged Dragon #1":2,"Lesser Dragon":2,"Battle Warrior":2,"Hero of the East":2,"Doron":2,
  "Dimensional Warrior":2,"Beaver Warrior":2,"Armored Lizard":2,"Battle Ox":1,
  "Dragon Treasure":3,"Legendary Sword":3,"Mountain":2,"Sogen":2,"Red Medicine":2,"Beast Fangs":2},
 "Tutorial deck: aggressive but fragile.")

# ---------------------------------------------------------------- chapter 2 (tier 2)
deck("Rex Raptor", "Rex Raptor", 2, 2, "Dinosaurs on the Wasteland",
 {"Two-headed King Rex":3,"Uraby":3,"Crawling Dragon #2":3,"Mammoth Graveyard":2,"Megazowler":2,"Sword Arm of Dragon":2,
  "Tomozaurus":2,"Little D":2,"Trakadon":2,"Anthrosaurus":2,"Pragtical":1,
  "Wasteland":3,"Beast Fangs":2,"Dragon Treasure":2,"Hinotama":3,"Raise Body Heat":2,"Swords of Revealing Light":2,"Mooyan Curry":2},
 "First real duel: strong ATK, few tricks.")
deck("Weevil Underwood", "Weevil Underwood", 2, 2, "Insect swarm on the Forest",
 {"Basic Insect":3,"Larvae Moth":2,"Cocoon of Evolution":2,"Great Moth":1,"Petit Moth":2,"Killer Needle":2,"Hercules Beetle":2,
  "Big Insect":2,"Giant Flea":2,"Gokibore":2,"Kwagar Hercules":1,"Dungeon Worm":2,"Needle Worm":1,"Man-eater Bug":2,
  "Forest":3,"Insect Armor with Laser Cannon":2,"Vile Germs":2,"Eatgaboon":1,"Sparks":2,"Dian Keto the Cure Master":2},
 "Cheats a little: a Trap and cheap cards, but low power.")

# ---------------------------------------------------------------- chapter 3 (tier 3)
deck("Seto", "Seto", 3, 3, "Palace priest: Spellcasters and Light support",
 {"Mystical Elf":2,"Maha Vailo":2,"Kamion Wizard":2,"Gemini Elf":2,"Rock Spirit":2,"Ill Witch":2,"Witch of the Black Forest":2,
  "Maiden of the Moonlight":2,"Dark Elf":2,"Flame Manipulator":2,"Aqua Madoor":2,"Illusionist Faceless Mage":1,"Musician King":1,
  "Mystical Moon":2,"Elf's Light":2,"Book of Secret Arts":2,"Mooyan Curry":2,"Swords of Revealing Light":2,"Spellbinding Circle":1,"Yami":1,"Sogen":2},
 "Gatekeeper duel. Needs the player's first fusions to win comfortably.")
deck("Mage Soldier", "Mage Soldier", 3, 3, "Arena trainer: Warriors on the Sogen",
 {"Celtic Guardian":2,"Swamp Battleguard":2,"Flame Swordsman":1,"Judge Man":1,"Karbonala Warrior":2,"Gaia the Fierce Knight":1,
  "Beautiful Headhuntress":2,"Kojikocy":2,"Zanki":2,"Ansatsu":2,"Monster Tamer":1,"Giltia the D. Knight":1,"Axe Raider":0,
  "Sogen":3,"Legendary Sword":3,"Silver Bow and Arrow":2,"Cyber Shield":2,"Electro-whip":2,"Warrior Elimination":1,"Dian Keto the Cure Master":2,
  "Swords of Revealing Light":2,"Raigeki":1},
 "Optional training duel with a clean Warrior plan.")

# ---------------------------------------------------------------- chapter 4 (tier 4)
deck("Heishin", "Heishin", 4, 4, "Traitor priest: Fiends and Zombies with dark equips",
 {"Shadow Ghoul":2,"Skelgon":2,"Ghoul with an Appetite":2,"Pumpking the King of Ghosts":2,"Neck Hunter":2,"Reaper of the Cards":2,
  "King of Yamimakai":2,"Dark Chimera":2,"Metal Guardian":2,"Mabarrel":2,"Soul Hunter":1,"Summoned Skull":1,"Great Mammoth of Goldfine":1,
  "Yami":3,"Dark Energy":3,"Black Pendant":2,"Sword of Dark Destruction":3,"Dark Hole":1,"Raigeki":1,"Curse of Millennium Shield":0,
  "Malevolent Nuzzler":2},
 "First boss. Heavy dark equips; punish with Sogen or Forest field changes.")

# ---------------------------------------------------------------- chapter 5 (tier 5-6)
deck("Mai Valentine", "Mai Valentine", 5, 5, "Harpies and fairies",
 {"Harpie Lady":3,"Harpie Lady Sisters":2,"Harpie's Pet Dragon":2,"Fiend Refrection #1":2,"Fiend Refrection #2":2,"Dancing Elf":2,
  "Muse-A":2,"Goddess of Whim":2,"Winged Egg of New Life":1,"Dark Witch":2,"Shining Friendship":2,
  "Harpie's Feather Duster":1,"Mountain":3,"Silver Bow and Arrow":3,"Follow Wind":2,"Elf's Light":2,"Swords of Revealing Light":2,"Spellbinding Circle":1,"Hourglass of Courage":2},
 "Feather Duster clears the player's spells and traps.")
deck("Bandit Keith", "Bandit Keith", 5, 5, "Machine gang with Machine Conversion Factory",
 {"Cyber Soldier":2,"Cannon Soldier":2,"Giant Mech-soldier":2,"Machine King":1,"Metal Dragon":2,"Mechanicalchacer":2,"Saber Slasher":2,
  "Giganto":2,"Launcher Spider":1,"Cyber Saurus":2,"Machine Attacker":2,"Ground Attacker Bugroth":2,"Dice Armadillo":1,"Giga-tech Wolf":2,
  "Machine Conversion Factory":3,"Laser Cannon Armor":2,"Cyber Shield":2,"Steel Shell":2,"Great White":1,"Raigeki":1,"Dian Keto the Cure Master":2,"Metalmorph":2},
 "Hard hitting Machines; weak to Raigeki and field control.")
deck("Shadi", "Shadi", 5, 5, "Spirit guardian: Rock and Warrior walls with spellcasters",
 {"Illusionist Faceless Mage":3,"Spirit of the Mountain":2,"Rock Spirit":2,"Mystical Sand":1,"Giant Soldier of Stone":2,"Millennium Golem":1,
  "Mysterious Puppeteer":2,"Guardian of the Labyrinth":2,"Protector of the Throne":2,"Royal Guard":1,"Stone D.":1,"Wall Shadow":1,
  "Skull Servant":2,"Dark Elf":1,"Ancient Sorcerer":1,
  "Mountain":2,"Wasteland":2,"Steel Shell":2,"Magical Labyrinth":2,"Mystical Moon":2,"Swords of Revealing Light":2,"Spellbinding Circle":1,"Stop Defense":2},
 "Defensive. Wins by stalling; use high-ATK fusions.")
deck("Pegasus", "Pegasus", 5, 6, "Illusionist showman: Fairies, light Dragons and Toons",
 {"Dark Witch":2,"Ocubeam":2,"Gyakutenno Megami":2,"Goddess with the Third Eye":2,"Orion the Battle King":2,"Doma The Angel of Silence":1,
  "Thousand Dragon":1,"Seiyaryu":1,"Kaiser Dragon":1,"Sky Dragon":2,"Thunder Dragon":1,"Toon Alligator":2,"Maiden of the Moonlight":2,
  "Musician King":2,"Mystical Elf":1,"Lady of Faith":2,
  "Mystical Moon":2,"Elf's Light":3,"Horn of Light":2,"Dragon Treasure":2,"Swords of Revealing Light":2,"Spellbinding Circle":1,"Sogen":1},
 "Chapter 5 boss.")

# ---------------------------------------------------------------- chapter 6 (tier 6-7)
deck("Ocean Mage", "Ocean Mage", 6, 6, "Sea guard: Aqua and Fish on Umi",
 {"Water Magician":2,"Fairy of the Fountain":2,"Amazon of the Seas":2,"Rare Fish":2,"Deepsea Shark":2,"Bottom Dweller":2,"Kairyu-shin":1,
  "Aqua Dragon":1,"Sea King Dragon":1,"Roaring Ocean Snake":2,"Marine Beast":1,"Rainbow Marine Mermaid":2,"High Tide Gyojin":2,"Giant Red Seasnake":1,
  "Umi":3,"Violet Crystal":2,"Water Element":0,"Dian Keto the Cure Master":2,"Mooyan Curry":2,"Swords of Revealing Light":2,"Sparks":2,"Hinotama":0,"Raise Body Heat":0,"Elegant Egotist":1},
 "Umi boosts Aqua and Fish, weakens Thunder and Machine.")
deck("High Mage Secmeton", "High Mage Secmeton", 6, 7, "Tide master: Sea Serpents and heavy Aqua",
 {"Suijin":1,"Aqua Dragon":2,"Sea King Dragon":2,"Takriminos":2,"Spike Seadra":2,"Kairyu-shin":2,"Man-eating Black Shark":2,"Marine Beast":2,
  "Misairuzame":2,"Metal Fish":1,"Roaring Ocean Snake":2,"Deepsea Shark":2,"Amphibious Bugroth":2,"Turtle Bird":1,
  "Umi":3,"Violet Crystal":3,"Elegant Egotist":2,"Dian Keto the Cure Master":2,"Raigeki":1,"Swords of Revealing Light":2,"Spellbinding Circle":1,"Mooyan Curry":1},
 "Chapter 6 sea boss: big water monsters under Umi.")
deck("High Mage Anubisius", "High Mage Anubisius", 6, 7, "Forest keeper: Beasts and Plants on the Forest",
 {"Garvas":2,"Ancient One of the Deep Forest":2,"Flower Wolf":2,"Leogun":2,"Rose Spectre of Dunn":1,"Queen of Autumn Leaves":2,"Trent":2,
  "Bean Soldier":2,"Wolf":2,"Silver Fang":2,"Frenzied Panda":1,"Mon Larvas":2,"Pale Beast":2,"Togex":2,"Great Bill":1,
  "Forest":3,"Beast Fangs":3,"Horn of the Unicorn":2,"Vile Germs":2,"Mooyan Curry":2,"Swords of Revealing Light":2,"Bad Reaction to Simochi":0,"Raise Body Heat":0},
 "Chapter 6 forest boss.")
deck("High Mage Atenza", "High Mage Atenza", 6, 7, "Summit lord: Dragons and Thunder on the Mountain",
 {"Sky Dragon":2,"Kaiser Dragon":1,"Thunder Dragon":2,"Twin-headed Thunder Dragon":1,"Kaminari Attack":2,"Stone D.":1,"Millennium Golem":1,
  "Crawling Dragon":2,"Darkfire Dragon":1,"Blackland Fire Dragon":1,"Parrot Dragon":2,"Harpie's Pet Dragon":1,"The Immortal of Thunder":2,"Curse of Dragon":2,
  "Mountain":3,"Dragon Treasure":3,"Horn of Light":2,"Legendary Sword":2,"Raigeki":1,"Swords of Revealing Light":2,"Spellbinding Circle":1,"Dian Keto the Cure Master":2},
 "Chapter 6 mountain boss: Dragons love the Mountain field.")
deck("High Mage Martis", "High Mage Martis", 6, 7, "Dune walker: Zombies and Rock on the Wasteland",
 {"Skelgon":2,"Great Mammoth of Goldfine":1,"Pumpking the King of Ghosts":2,"Ghoul with an Appetite":2,"Shadow Ghoul":2,"Dragon Zombie":2,"Armored Zombie":2,
  "Zombie Warrior":2,"Skull Servant":2,"Mystical Sand":2,"Sand Stone":1,"Stone Ogre Grotto":1,"Giant Soldier of Stone":2,"Krokodilus":1,"Magical Ghost":2,
  "Wasteland":3,"Dark Energy":2,"Black Pendant":2,"Sword of Dark Destruction":2,"Dark Hole":1,"Raigeki":1,"Eternal Rest":1,"Stop Defense":1},
 "Chapter 6 desert boss: Zombies and Rock gain on the Wasteland.")
deck("High Mage Kepura", "High Mage Kepura", 6, 7, "Meadow guardian: Fairies, Plants and Warriors on the Sogen",
 {"Queen of Autumn Leaves":2,"Dryad":2,"Beautiful Beast Trainer":2,"Orion the Battle King":2,"Dark Witch":2,"Muse-A":2,"Tenderness":2,
  "Shining Friendship":2,"Hourglass of Courage":2,"Winged Egg of New Life":1,"Goddess of Whim":2,"Gyakutenno Megami":1,"Trent":1,"Empress Judge":1,"Warrior of Tradition":1,
  "Sogen":3,"Elf's Light":3,"Mystical Moon":2,"Legendary Sword":2,"Dian Keto the Cure Master":2,"Mooyan Curry":1,"Swords of Revealing Light":2,"Spellbinding Circle":1},
 "Chapter 6 meadow boss: defensive but with strong supports.")
deck("Cockatiel", "Cockatiel", 6, 7, "Wandering bird tamer: Winged Beasts and Wind Dragons on the Mountain",
 {"Tyhone":2,"Faith Bird":3,"Spirit of the Books":2,"Droll Bird":2,"Mavelus":2,"Takuhee":2,"Skull Red Bird":2,"Blue-winged Crown":2,"Crow Goblin":2,
  "Wing Eagle":2,"Peacock":2,"Queen Bird":1,"Punished Eagle":1,"Parrot Dragon":2,"Crimson Sunbird":1,"Niwatori":1,
  "Mountain":3,"Follow Wind":2,"Winged Trumpeter":1,"Silver Bow and Arrow":2,"Horn of Light":1,"Swords of Revealing Light":1},
 "Optional side duel. Fast flyers; Mountain field gives Winged Beasts and Dragons +500.")

# ---------------------------------------------------------------- chapter 7 (tier 8-9)
deck("Labyrinth Mage", "Labyrinth Mage", 7, 8, "Maze keeper: walls, guardians and machines",
 {"Guardian of the Labyrinth":3,"Gatekeeper":2,"Blocker":2,"Golgoil":2,"Giant Soldier of Stone":2,"Barrel Rock":2,"Stone Armadiller":2,"Labyrinth Tank":1,
  "Wall Shadow":1,"Pendulum Machine":1,"Royal Guard":2,"Steel Ogre Grotto #1":1,"Protector of the Throne":2,"Stone D.":1,
  "Magical Labyrinth":3,"Steel Shell":3,"Cyber Shield":2,"Spellbinding Circle":2,"Swords of Revealing Light":2,"Dian Keto the Cure Master":2,"Raigeki":1,"Mountain":1,"Wasteland":0},
 "Chapter 7: very high DEF, slow; wins by out-lasting.")
deck("Guardian Sebek", "Guardian Sebek", 7, 8, "Crocodile judge: Reptiles and Aqua on the Umi and Wasteland",
 {"Krokodilus":3,"Emperor of the Land and Sea":2,"Armored Lizard":2,"Ancient Lizard Warrior":2,"Grappler":2,"Toon Alligator":2,"Yormungarde":2,"Drooling Lizard":2,
  "Beaked Snake":1,"Sinister Serpent":2,"Mechaleon":1,"Kairyu-shin":2,"Aqua Dragon":1,"Roaring Ocean Snake":2,"Amphibious Bugroth":2,
  "Umi":3,"Wasteland":1,"Violet Crystal":2,"Dragon Capture Jar":1,"Raigeki":1,"Dian Keto the Cure Master":2,"Swords of Revealing Light":2,"Spellbinding Circle":1},
 "Chapter 7.")
deck("Guardian Neku", "Guardian Neku", 7, 8, "Cat judge: big Beasts and Beast-Warriors on the Forest",
 {"Nekogal #1":2,"Nekogal #2":2,"Sleeping Lion":2,"Leogun":2,"Garvas":2,"Rude Kaiser":2,"Pale Beast":2,"Togex":2,"Tatsunootoshigo":2,"Flower Wolf":2,
  "Garoozis":1,"Rabid Horseman":2,"Battle Steer":2,"Dark Rabbit":2,"Wolf":2,"Beast Fangs":3,
  "Forest":3,"Horn of the Unicorn":2,"Raise Body Heat":0,"Legendary Sword":1,"Swords of Revealing Light":2,"Dian Keto the Cure Master":2,"Spellbinding Circle":1,"Raigeki":1},
 "Chapter 7: heavy Beasts.")
deck("Seto 2nd", "Seto 2nd", 7, 9, "White Dragon priest: Light Dragons and Spellcasters",
 {"Blue-eyes White Dragon":2,"Kaiser Dragon":2,"Seiyaryu":2,"Sky Dragon":2,"Gaia the Dragon Champion":1,"Curse of Dragon":2,"Red-eyes B. Dragon":1,"Thousand Dragon":1,
  "Thunder Dragon":2,"Mystical Elf":2,"Maiden of the Moonlight":2,"Gemini Elf":2,"Dark Magician":1,"Musician King":1,
  "Dragon Treasure":3,"Horn of Light":2,"Mountain":3,"Legendary Sword":2,"Swords of Revealing Light":2,"Spellbinding Circle":1,"Raigeki":1,"Dian Keto the Cure Master":2,"Mystical Moon":0},
 "Chapter 7 miniboss: top-end Dragons but few of them.")
deck("Heishin 2nd", "Heishin 2nd", 7, 9, "Shadow-powered Heishin: top Fiends and Magicians on Yami",
 {"Summoned Skull":2,"Dark Magician":2,"Soul Hunter":2,"Ushi Oni":2,"Bickuribox":2,"Fiend's Mirror":2,"Shadow Ghoul":2,"Zoa":1,"Neck Hunter":2,
  "Dragon Seeker":2,"Skelgon":1,"Great Mammoth of Goldfine":1,"Air Eater":1,"Dark Elf":1,
  "Yami":3,"Dark Energy":3,"Black Pendant":3,"Sword of Dark Destruction":3,"Dark Hole":2,"Raigeki":1,"Shadow Spell":1,"Stop Defense":0,"Eatgaboon":0,"Malevolent Nuzzler":1},
 "Chapter 7 boss.")

# ---------------------------------------------------------------- chapter 8 (tier 9-10)
deck("Seto 3rd", "Seto 3rd", 8, 9, "Shadow-touched Seto: dark Dragons and Blue-eyes",
 {"Blue-eyes White Dragon":3,"Red-eyes B. Dragon":2,"Kaiser Dragon":2,"Seiyaryu":2,"Gaia the Dragon Champion":2,"Curse of Dragon":2,"Thousand Dragon":1,
  "Twin-headed Thunder Dragon":1,"Sky Dragon":2,"Dark Magician":2,"Summoned Skull":1,"Darkfire Dragon":1,
  "Yami":2,"Dragon Treasure":3,"Dark Energy":2,"Black Pendant":2,"Mountain":2,"Legendary Sword":2,"Raigeki":1,"Dark Hole":1,"Swords of Revealing Light":1,"Spellbinding Circle":1,"Horn of Light":0},
 "Hardest 'normal' duelist before the end.")
deck("DarkNite", "DarkNite", 8, 10, "Night herald: Fiends, Zombies and Spellcasters, all dark",
 {"Summoned Skull":2,"Dark Magician":2,"Soul Hunter":2,"Ushi Oni":2,"Air Eater":2,"Bickuribox":2,"Dragon Seeker":2,"Fiend's Mirror":1,"Zoa":2,"Skelgon":2,
  "Shadow Ghoul":2,"Dark Elf":1,"Succubus Knight":2,"Swordstalker":2,"Whiptail Crow":1,"Great Mammoth of Goldfine":1,
  "Yami":3,"Dark Energy":3,"Black Pendant":3,"Sword of Dark Destruction":3,"Dark Hole":1,"Raigeki":1,"Shadow Spell":0},
 "Chapter 8 miniboss; Nitemare's warm-up.")
deck("Nitemare", "Nitemare", 8, 10, "The nightmare itself: the strongest normal cards under Yami",
 {"Summoned Skull":3,"Dark Magician":3,"Zoa":2,"Soul Hunter":2,"Air Eater":2,"Bickuribox":2,"Dragon Seeker":2,"Fiend's Mirror":2,"Ushi Oni":2,"Red-eyes B. Dragon":2,
  "Gaia the Dragon Champion":1,"Seiyaryu":1,"Blue-eyes White Dragon":1,"Kaiser Dragon":1,"B. Skull Dragon":1,
  "Yami":3,"Dark Energy":3,"Black Pendant":3,"Sword of Dark Destruction":3,"Dark Hole":1,"Raigeki":1,"Shadow Spell":1},
 "Final boss. No rituals; relies on raw power and fusions.")

# ---------------------------------------------------------------- tuning to exactly 40 cards (+ = add, - = remove)
_ADJ = {
 "Simon Muran": {"Hourglass of Life":2,"Petit Angel":2},
 "Teana": {"Wicked Mirror":2,"Lord of Zemia":2},
 "Jono": {"Tiger Axe":2,"Mountain Warrior":1},
 "Weevil Underwood": {"Alinsection":2,"Great Moth":-1,"Cockroach Knight":1},
 "Seto": {"Sparks":2},
 "Labyrinth Mage": {"Blocker":-2,"Giganto":2,"Golgoil":-2,"Metal Dragon":2},
 "Mage Soldier": {"Hibikime":2,"Warrior of Tradition":1},
 "Heishin": {"Mystic Clown":2},
 "Mai Valentine": {"Hoshiningen":-0,"Punished Eagle":1,"Crow Goblin":1,"Peacock":1,"Blue-winged Crown":1,"Dancing Elf":-2},
 "Shadi": {"Soul of the Pure":1},
 "Pegasus": {"Fairy's Gift":1},
 "Ocean Mage": {"Octoberser":2,"Akihiron":1},
 "High Mage Anubisius": {"Bean Soldier":-1},
 "High Mage Atenza": {"Koumori Dragon":2,"Tyhone #2":1},
 "High Mage Martis": {"Fire Reaper":1},
 "High Mage Kepura": {"Muse-A":-1},
 "Cockatiel": {"Kurama":1},
 "Guardian Sebek": {"Dragon Capture Jar":-1,"Sinister Serpent":-2,"Sea King Dragon":2,"Mechaleon":-1,"Bracchio-raidus":1,"Beaked Snake":-1,"Spike Seadra":1},
 "Guardian Neku": {"Nekogal #1":-1,"Wolf":-1,"Dark Rabbit":-1,"Battle Steer":-1},
 "Seto 2nd": {"Mystical Moon":1},
 "Seto 3rd": {"Horn of Light":2},
 "DarkNite": {"Whiptail Crow":-1,"Great Mammoth of Goldfine":-1},
 "Nitemare": {"Blue-eyes White Dragon":-1,"Kaiser Dragon":-1},
}
for _k, _a in _ADJ.items():
    _c = DECKS[_k]["cards"]
    for _n, _d in _a.items():
        _c[_n] = _c.get(_n, 0) + _d
for _v in DECKS.values():
    _v["cards"] = {n: x for n, x in _v["cards"].items() if x > 0}
