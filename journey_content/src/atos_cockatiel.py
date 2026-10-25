"""Atos Vinicius mirror duelist (+ custom CLT cards) and the Cockatiel creator duelist."""

CUSTOM_CARDS = [
 {"name":"CLT Worker","kind":"monster","type":"Warrior","attribute":"Earth","level":4,"atk":1500,"def":1300,"replaces_vanilla_slot":720,
  "text":"Works Monday to Friday and still does overtime."},
 {"name":"Bills","kind":"monster","type":"Machine","attribute":"Dark","level":5,"atk":1900,"def":1500,"replaces_vanilla_slot":702,
  "text":"They arrive every month. They never fail. They never forgive."},
 {"name":"BBQ and Beer","kind":"equip","equips":["CLT Worker"],"replaces_vanilla_slot":318,"text":"Raises the power of the CLT Worker."},
 {"name":"Salary Raise","kind":"equip","equips":["CLT Worker"],"replaces_vanilla_slot":652,"text":"Raises the power of the CLT Worker."},
 {"name":"Might Not Live Tomorrow","kind":"equip","equips":["CLT Worker"],"replaces_vanilla_slot":657,"text":"So I spend it all! Big power boost."},
 {"name":"Regret","kind":"trap","replaces_vanilla_slot":689,"text":"Reverses the effects of power-up cards."},
 {"name":"Tax Hike","kind":"equip","equips":["Bills"],"replaces_vanilla_slot":309,"text":"Raises the power of the Bills."},
 {"name":"Layoff","kind":"magic","replaces_vanilla_slot":653,"text":"Destroys all the opponent's Warriors, including the CLT Worker."},
 {"name":"Weekend","kind":"magic","replaces_vanilla_slot":672,"text":"Destroys all the opponent's magic cards in play."},
 {"name":"Workers' Rights","kind":"magic","replaces_vanilla_slot":342,"text":"Severance, savings and days worked. Restores a great deal of Life Points."},
]
CUSTOM_NOTE = ("Names/stats come from the PS1 mod's patch_clt.py (type/attribute inferred from its numeric ids: 3 = Warrior, 14 = Machine). "
 "The Brazilian jokes are kept as jokes in English: CLT = the Brazilian labor code, FGTS/PIS = worker savings. "
 "In the port these are mod 'cards' appended after the disc's 722; the 'replaces_vanilla_slot' ids are only a trace of the PS1 patch.")

ATOS_DECK = {
 "duelist":"Atos Vinicius","chapter":9,"difficulty_tier":10,
 "theme":"Mirror Atos: the CLT overtime combo, Warriors with raise cards",
 "cards":{"Hero of the East":3,"Gaia the Fierce Knight":1,"Judge Man":1,"Flame Swordsman":1,"Dimensional Warrior":3,"Giltia the D. Knight":1,"Empress Judge":1,"Warrior of Tradition":1,"Celtic Guardian":2,"Karbonala Warrior":2,
          "Kojikocy":2,"Zanki":2,"Monster Tamer":1,"Swamp Battleguard":2,
          "Elegant Egotist":3,"Magical Labyrinth":2,"Megamorph":2,"Steel Shell":2,"Sogen":3,"Mooyan Curry":2,"Legendary Sword":3},
 "cards_with_custom_pack":{"CLT Worker":3,"Bills":2,"BBQ and Beer":3,"Salary Raise":3,"Might Not Live Tomorrow":3,"Regret":1,"Tax Hike":2,
          "Weekend":1,"Workers' Rights":2,
          "Hero of the East":2,"Gaia the Fierce Knight":1,"Judge Man":1,"Dimensional Warrior":2,"Giltia the D. Knight":1,"Empress Judge":1,"Celtic Guardian":1,"Karbonala Warrior":1,
          "Kojikocy":1,"Zanki":1,"Monster Tamer":1,"Sogen":2,"Mooyan Curry":2,"Legendary Sword":2,"Red Medicine":1},
 "notes":"Use cards_with_custom_pack when the CLT card pack is installed, otherwise cards. Both are 40 cards."
}

COCKATIEL = {
 "id":"cockatiel",
 "name":"Cockatiel",
 "legal_note":"Fictional Forbidden-Memories-style character. The name is only the bird; it uses no real person's name, face, voice or catchphrases.",
 "role":"Optional wandering duelist, Temple Crossroads, from chapter 6 on (stage 7+). Story script ids: side_cockatiel_pre / _win / _lose / _done / _epilogue.",
 "bio":"A bird tamer who walks from oasis to oasis with a flock that follows the wind. Speaks in cheerful chirps, hates losing, never hurts a bird. The little cockatiel on the shoulder is called Pip and only talks when it wants snacks.",
 "personality":["cheerful","competitive","a little vain about the crest","loyal to the flock"],
 "portrait_description":("Bust portrait, 48x48 final (draw at 192x192). A lean young traveler with a tall swept-up crest of yellow-blond hair like a bird crest, "
   "two round orange cheek marks painted on the face, a grey-and-yellow feathered cloak over a sand-colored tunic, a small grey cockatiel with a yellow face "
   "and orange cheek patch perched on the left shoulder. Big confident grin, one eyebrow raised. Palette: warm yellow, soft grey, orange, sand. "
   "Style: matches the game's hand-painted PS1 duelist portraits, 64 colors, dark outline, plain dark background. No text, no logos, not a likeness of any real person."),
 "model_hint":"Quaternius Hoodie or Punk character, yellow-tinted hair, plus a tiny grey bird prop on the shoulder (CC0).",
 "portrait_slot":{"proposed":"cports slot 6 / portrait id 0xF1","file":"portraits/cockatiel.png"},
 "port_duelist":{"id":"cockatiel","json":{"copy":"High Mage Kepura","name":"Cockatiel","slot":40},
                 "note":"copy gives AI and drop pools; deck is replaced by decks.json['Cockatiel'] (fixed 40)."},
 "drops":{"pow":{"replace":True,"Crimson Sunbird":2,"Punished Eagle":2,"Queen Bird":1,"Harpie Lady":2},
          "bcd":{"replace":True,"Droll Bird":3,"Faith Bird":3,"Tyhone":2,"Takuhee":2},
          "tec":{"replace":True,"Winged Trumpeter":2,"Follow Wind":2,"Silver Bow and Arrow":2,"Parrot Dragon":1}},
 "items":["cockatiel_feather"],
 "script_ids":["side_cockatiel_pre","side_cockatiel_win","side_cockatiel_lose","side_cockatiel_done","side_cockatiel_epilogue"],
 "deck":"Cockatiel",
 "play_style":"Fast Winged Beasts and Wind Dragons; plays Mountain early. Weak to Raigeki and to high-DEF walls.",
 "extra_lines":{
   "free_duel_taunt_win":"Chirp! Fly higher next time!",
   "free_duel_taunt_lose":"Pip says you cheated. Pip is wrong.",
   "idle_1":"Pip, stop eating the cards.",
   "idle_2":"The wind brought you here. Don't waste it."}
}
