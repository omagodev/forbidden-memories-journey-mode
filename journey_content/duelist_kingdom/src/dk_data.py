# -*- coding: utf-8 -*-
"""Structure of the Duelist Kingdom content: everything except the dialogue pages. B(en, pt) = bilingual string."""
def B(en, pt=None): return {"en": en, "pt": pt if pt is not None else en}

SPEAKERS = {  # key: (name_en, name_pt, short, portrait, note)
 "atos": ("{name}", "{name}", "{name}", 39, "Player (custom hero). Same custom Atos face slot as the old story."),
 "simon": ("Simon Muran", "Simon Muran", "Simon", 1, "Village sage."),
 "teana": ("Teana", "Teana", "Teana", 2, "Date-cake stall girl."),
 "jono": ("Jono", "Jono", "Jono", 3, "Loud friend, the Joey of this story."),
 "guard": ("Guard", "Guarda", "Guard", 5, "Villager 2 portrait."),
 "baker": ("Hakim", "Hakim", "Hakim", 4, "Villager 1 portrait: the baker."),
 "farmer": ("Kemet", "Kemet", "Kemet", 6, "Villager 3 portrait: the date farmer."),
 "academy_teacher": ("Professor Nabil", "Professor Nabil", "Nabil", 4, "An ordinary villager who runs a free Duel Academy in the plaza."),
 "hooded_man": ("Hooded Man", "Homem Encapuzado", "Hooded", 254, "Voice only (no portrait). It is Shadi in disguise; the portrait appears at the reveal."),
 "bakura": ("Bakura", "Bakura", "Bakura", 14, "Lonely cistern ghost (Yami Bakura portrait)."),
 "rex": ("Rex Raptor", "Rex Raptor", "Rex", 9, "Wandering dinosaur duelist."),
 "soldier": ("Mage Soldier", "Soldado Mago", "Soldier", 18, "Harbor inspector."),
 "shadi": ("Shadi", "Shadi", "Shadi", 13, "Pegasus's messenger."),
 "mai": ("Mai", "Mai", "Mai", 11, "Passenger on the ship; Harpie Lady duelist."),
 "inseto": ("InsetoKaiba", "InsetoKaiba", "Inseto K.", 243, "NEW custom portrait slot 243: arrogant insect-themed parody rival. Stylized caricature, see art list."),
 "mago_dev": ("Mago.dev", "Mago.dev", "Mago.dev", 244, "The observer, robe portrait (art_dk/portraits/mago_hood). Never interferes. Talks only at the epilogue payoff, when the hero finally speaks to him."),
 "mago_dev_tee": ("Mago.dev", "Mago.dev", "Mago.dev", 245, "Same character in the plain tee (art_dk/portraits/mago_tee): the epilogue payoff on the festival bench."),
 "mago_hidden": ("???", "???", "???", 244, "Mago.dev before the hero knows his name; same robe portrait."),
 "isis": ("Isis", "Isis", "Isis", 16, "Fortune teller of the Desert (Kingdom outline)."),
 "narrator": ("(label)", "(label)", "(label)", 254, "No portrait. Every narrator page carries its own label."),
}

FLAGS = [  # name, note
 ("heard_teana", "Rumor 1 heard."), ("heard_jono", "Rumor 2 heard."), ("heard_guard", "Rumor 3 heard."),
 ("read_notice", "Optional: read the notice board."), ("simon_won", "Simon's test duel won (legend told)."),
 ("courier_met", "Met the hooded man at night; Stamp Card received."), ("baker_hint", "Hakim told about the Founder's Scarab."),
 ("farmer_won", "Kemet beaten; Lantern received."), ("treasure_lost", "Founder's Scarab won from Bakura (stamp: Lost)."),
 ("jono_asked", "Jono told about the bandana."), ("treasure_won", "Rex beaten, bandana recovered (stamp: Won)."),
 ("jono_thanked", "Jono's thank-you gift received."), ("teana_asked", "Teana asked for ingredients; Water Jug given."),
 ("jug_taken", "Water Jug in the backpack."), ("got_honey", "Honey Jar from Hakim."), ("got_water", "River Water in the jug."),
 ("got_dates", "Dates from the palm."), ("treasure_given", "Teana beaten, Lucky Charm given (stamp: Given)."),
 ("baker_won", "Optional duel with Hakim won."), ("inspector_won", "Harbor exam won (gate open)."),
 ("shadi_won", "Courier's trial won: Star Passage and 1 star."), ("simon_farewell", "Goodbye to Simon."),
 ("teana_farewell", "Goodbye to Teana."), ("jono_farewell", "Goodbye to Jono."), ("mai_met", "Mai explained the star rules."),
 ("inseto_won", "Optional duel with InsetoKaiba won."),
 ("mago_roof", "Observer glimpse 1: rooftop during the night bench scene."), ("mago_glyph", "Observer glimpse 2: green glyph on the cistern wall."),
 ("mago_passage", "Observer glimpse 3: breakwater, reading the Star Passage."), ("mago_mast", "Observer glimpse 4: top of the ship's mast."),
]
STAGES = [
 (0, "Character creation"), (1, "Chapter 1 start: rumors in the village"), (2, "Rumors done, Simon told the legend: wait on the bench"),
 (3, "Stamp Card in hand: find the Lost, Won and Given treasures (any order)"), (4, "All three stamps: cross the bridge"),
 (5, "Harbor: exam and the Courier"), (6, "Star Passage in hand: farewells at the pier"), (7, "On the ship"),
 (10, "Chapter 2 start: Duelist Kingdom (see kingdom_outline.json)"),
]

AREAS = [  # id, name_en, name_pt, setting, status
 ("village", "Oasis Village", "Vila do Oasis", "The existing painted Egyptian village (river and bridge north, 4 houses, plaza, golden roads). Needs a NIGHT variant of the background.", "exists (painted)"),
 ("cistern", "Old Cistern", "Cisterna Antiga", "Small underground room under the little pyramid: stone steps, still water, a floating pale light, carved Founder reliefs. One screen.", "NEW art"),
 ("harbor", "Sunset Harbor", "Porto do Poente", "River-mouth harbor at golden hour: wooden pier, rope piles, crates, a stone gate with a guard post, empty pier end. The ship sprite is added at stage 6. One to two screens.", "NEW art"),
 ("ship_deck", "The Golden Eye (ship deck)", "O Olho Dourado (convez)", "Deck of a white ship with a golden eye painted on the sail: planks, barrels, rail, bow. One screen.", "NEW art"),
 ("kingdom_beach", "Shore of Illusions", "Costa das Ilusoes", "First area of the Kingdom, outline only (see kingdom_outline.json).", "later"),
]

ANCHORS = {  # area: {anchor: (hint for the painted picture / map author)}
 "village": {
  "hero_start": "Front of the NW house door (red zigzag house, top-left).",
  "plaza_center": "Middle of the big open dirt plaza.",
  "plaza_bench": "NEW prop: stone bench at the left edge of the plaza near the central palms.",
  "house_ne_door": "Door of the NE house (blue zigzag, top-right): Simon's hall.",
  "teana_stall": "Under the awning of the SW house (red cushions): Teana's date-cake stall.",
  "bakery_door": "Door of the SE house (blue zigzag, awning, bottom-right): Hakim's bakery.",
  "farmer_field": "Left-center bush field between the NW house and the crossroads.",
  "date_palm": "The palm cluster at center-right of the plaza (use the biggest palm).",
  "mini_pyramid_hatch": "The little pyramid beside the NW house. NEW overlay: a stone hatch on its side.",
  "notice_sign": "The wooden sign on the right side of the plaza (already in the painted art).",
  "river_bank": "River edge at the top, left of the bridge.",
  "bridge_north": "The wooden bridge at the top center: guard post and exit to the harbor road.",
  "mago_roof": "OBSERVER: far rooftop edge of the NE house (top-right), seen from the plaza at night. Robe sprite + green aura overlay, never walkable.",
  "east_road": "East end of the horizontal golden road (right edge).",
  "academy_corner": "Open ground by the notice board: Nabil's informal outdoor Duel Academy.",
 },
 "cistern": {"wall_glyph": "OBSERVER: carved wall panel where green characters flicker (green aura overlay).", "spawn_stairs": "Bottom of the stone steps.", "bakura_spot": "Center platform with the floating light.", "exit_stairs": "The stairs going up."},
 "harbor": {
  "spawn_gate": "Arrival from the bridge, in front of the stone gate.", "inspector_spot": "In front of the gate (guard post).",
  "pier_end": "End of the pier, where the Courier waits.", "farewell_simon": "Pier, left of center.", "farewell_teana": "Pier, center.",
  "farewell_jono": "Pier, right of center.", "breakwater": "OBSERVER: far stone breakwater across the water. Robe sprite + green aura, never walkable.", "gangway": "Gangway of the white ship (ship appears at stage 6).", "bridge_back": "Edge back to the bridge/village.",
 },
 "ship_deck": {"spawn_gangway": "Top of the gangway.", "mai_spot": "Near the rail, left.", "inseto_spot": "Center deck, striking a pose.", "barrel": "Barrel next to the mast.", "mast_top": "OBSERVER: top of the mast (crow's nest). Robe sprite + green aura, never walkable.", "bow": "Front of the ship."},
 "kingdom_beach": {"spawn": "Beach where the ship lands (engine dev binds when the Kingdom arc is built)."},
}

ITEMS = [  # id, name_en, name_pt, desc_en, desc_pt, source
 ("rumor_notebook", "Rumor Notebook", "Caderno de Boatos", "Your notes: a hooded man, a white ship, a torn poster.", "Suas anotacoes: um homem de capuz, um navio branco, um cartaz rasgado.", "Chapter start"),
 ("stamp_card", "Stamp Card", "Cartao de Selos", "Three stamp slots: Lost, Won, Given.", "Tres selos: Perdido, Ganho, Dado.", "Hooded Man"),
 ("honey", "Honey Jar", "Pote de Mel", "Sticky honey from Hakim.", "Mel grudento do Hakim.", "Hakim"),
 ("jug", "Water Jug", "Jarra de Agua", "Teana's jug. Fill it at the river.", "A jarra da Teana. Encha no rio.", "Teana"),
 ("river_water", "River Water", "Agua do Rio", "A jug of clear river water.", "Uma jarra de agua limpa do rio.", "River"),
 ("dates", "Dates", "Tamaras", "A basket of ripe dates.", "Uma cesta de tamaras maduras.", "Date palm"),
 ("lantern", "Lantern", "Lanterna", "Kemet's lantern. Lights dark places.", "A lanterna do Kemet. Ilumina lugares escuros.", "Kemet"),
 ("scarab", "Founder's Scarab", "Escaravelho do Fundador", "The Lost treasure of the village.", "O tesouro Perdido da vila.", "Bakura"),
 ("bandana", "Jono's Bandana", "Bandana do Jono", "The Won treasure.", "O tesouro Ganho.", "Rex Raptor"),
 ("charm", "Lucky Charm", "Amuleto da Sorte", "Teana's gift: the Given treasure.", "Presente da Teana: o tesouro Dado.", "Teana"),
 ("star_passage", "Star Passage", "Passagem Estelar", "Your ticket to Duelist Kingdom.", "Seu bilhete para o Reino dos Duelistas.", "Shadi"),
 ("star_chip", "Star Chip", "Ficha de Estrela", "One star. Win to gain, lose to lose.", "Uma estrela. Vencer ganha, perder perde.", "Shadi"),
 ("bug_pin", "Golden Bug Pin", "Pin do Inseto Dourado", "InsetoKaiba's tiny gold beetle pin. Pure vanity.", "O pin de besouro dourado do InsetoKaiba. Pura vaidade.", "InsetoKaiba"),
]

# npcs: id, speaker key, area, anchor, duelist_id, art role (EN), stages [min,max], visible, rules
def W(**k): return k
NPCS = [
 dict(id="simon", area="village", anchor="house_ne_door", duelist_id=1, stages=[0, 99], visible="always",
      moves=[dict(at_stage=6, area="harbor", anchor="farewell_simon")],
      rules=[
  W(when=W(stage=[1,1], flags_all=["heard_teana","heard_jono","heard_guard"], flags_none=["simon_won"]), script="dk1_simon_pre", duel="simon"),
  W(when=W(stage=[0,1]), script="dk1_simon_wait"),
  W(when=W(stage=[2,2]), script="dk1_simon_stage2"),
  W(when=W(stage=[3,5]), script="dk1_simon_treasures"),
  W(when=W(stage=[6,6], flags_none=["simon_farewell"]), script="dk1_simon_farewell", effects=[W(give_card="Mystical Elf"), W(set_flag="simon_farewell")]),
  W(when=W(stage=[6,99]), script="dk1_simon_after")]),
 dict(id="teana", area="village", anchor="teana_stall", duelist_id=2, stages=[0, 99], visible="always",
      moves=[dict(at_stage=6, area="harbor", anchor="farewell_teana")],
      rules=[
  W(when=W(stage=[1,1], flags_none=["heard_teana"]), script="dk1_teana_rumor", effects=[W(set_flag="heard_teana")]),
  W(when=W(stage=[1,1], flags_all=["heard_teana","heard_jono","heard_guard"]), script="dk1_teana_tell_simon"),
  W(when=W(stage=[1,1]), script="dk1_teana_rumor_after"),
  W(when=W(stage=[2,2]), script="dk1_teana_stage2"),
  W(when=W(stage=[3,3], flags_none=["teana_asked"]), script="dk1_teana_ask", effects=[W(give_item="jug"), W(set_flag="teana_asked"), W(set_flag="jug_taken")]),
  W(when=W(stage=[3,99], flags_all=["teana_asked","got_honey","got_water","got_dates"], flags_none=["treasure_given"]), script="dk1_teana_pre", duel="teana"),
  W(when=W(stage=[3,99], flags_all=["teana_asked"], flags_none=["treasure_given"]), script="dk1_teana_waiting"),
  W(when=W(stage=[3,5]), script="dk1_teana_after"),
  W(when=W(stage=[6,6], flags_none=["teana_farewell"]), script="dk1_teana_farewell", effects=[W(set_flag="teana_farewell")]),
  W(when=W(stage=[6,99]), script="dk1_teana_after_farewell")]),
 dict(id="jono", area="village", anchor="plaza_center", duelist_id=3, stages=[0, 99], visible="always", patrol="plaza_loop",
      moves=[dict(at_stage=6, area="harbor", anchor="farewell_jono")],
      rules=[
  W(when=W(stage=[1,1], flags_none=["heard_jono"]), script="dk1_jono_rumor", effects=[W(set_flag="heard_jono")]),
  W(when=W(stage=[1,1], flags_all=["heard_teana","heard_jono","heard_guard"]), script="dk1_jono_tell_simon"),
  W(when=W(stage=[1,1]), script="dk1_jono_rumor_after"),
  W(when=W(stage=[2,2]), script="dk1_jono_stage2"),
  W(when=W(stage=[3,99], flags_all=["treasure_won"], flags_none=["jono_thanked"]), script="dk1_jono_thanks", effects=[W(give_card="Dragon Treasure"), W(set_flag="jono_thanked")]),
  W(when=W(stage=[3,3], flags_none=["jono_asked"]), script="dk1_jono_ask", effects=[W(set_flag="jono_asked")]),
  W(when=W(stage=[3,99], flags_all=["jono_asked"], flags_none=["treasure_won"]), script="dk1_jono_waiting"),
  W(when=W(stage=[3,5]), script="dk1_jono_after"),
  W(when=W(stage=[6,6], flags_none=["jono_farewell"]), script="dk1_jono_farewell", effects=[W(set_flag="jono_farewell")]),
  W(when=W(stage=[6,99]), script="dk1_jono_after_farewell")]),
 dict(id="guard", area="village", anchor="bridge_north", duelist_id=None, stages=[0, 99], visible="always",
      rules=[
  W(when=W(stage=[1,1], flags_none=["heard_guard"]), script="dk1_guard_rumor", effects=[W(set_flag="heard_guard")]),
  W(when=W(stage=[1,1], flags_all=["heard_teana","heard_jono","heard_guard"]), script="dk1_guard_tell_simon"),
  W(when=W(stage=[1,1]), script="dk1_guard_rumor_after"),
  W(when=W(stage=[2,2]), script="dk1_guard_stage2"),
  W(when=W(stage=[3,3]), script="dk1_guard_block"),
  W(when=W(stage=[4,99]), script="dk1_guard_open")]),
 dict(id="baker", area="village", anchor="bakery_door", duelist_id=4, stages=[0, 99], visible="always",
      rules=[
  W(when=W(stage=[0,2]), script="dk1_baker_hello"),
  W(when=W(stage=[3,3], flags_all=["teana_asked"], flags_none=["got_honey"]), script="dk1_baker_honey", effects=[W(give_item="honey"), W(set_flag="got_honey")]),
  W(when=W(stage=[3,3], flags_none=["baker_hint"]), script="dk1_baker_hint", effects=[W(set_flag="baker_hint")]),
  W(when=W(stage=[3,5], flags_all=["baker_hint"], flags_none=["baker_won"]), script="dk1_baker_pre", duel="baker"),
  W(when=W(stage=[3,99]), script="dk1_baker_after")]),
 dict(id="farmer", area="village", anchor="farmer_field", duelist_id=6, stages=[0, 99], visible="always",
      rules=[
  W(when=W(stage=[0,2]), script="dk1_farmer_hello"),
  W(when=W(stage=[3,99], flags_all=["baker_hint"], flags_none=["farmer_won"]), script="dk1_farmer_pre", duel="farmer"),
  W(when=W(stage=[3,99], flags_none=["farmer_won"]), script="dk1_farmer_nohint"),
  W(when=W(stage=[3,99]), script="dk1_farmer_after")]),
 dict(id="academy_teacher", area="village", anchor="academy_corner", duelist_id=4, stages=[0, 99], visible="always",
      note="Optional, persistent rules tutorial. Each conversation advances one short class; the final class unlocks practice duels.",
      rules=[
  W(when=W(stage=[0,99], flags_none=["academy_started"]), script="dk1_academy_intro", effects=[W(set_flag="academy_started")]),
  W(when=W(stage=[0,99], flags_all=["academy_started"], flags_none=["academy_basics"]), script="dk1_academy_basics", effects=[W(set_flag="academy_basics")]),
  W(when=W(stage=[0,99], flags_all=["academy_basics"], flags_none=["academy_guardians"]), script="dk1_academy_guardians", effects=[W(set_flag="academy_guardians")]),
  W(when=W(stage=[0,99], flags_all=["academy_guardians"], flags_none=["academy_fields"]), script="dk1_academy_fields", effects=[W(set_flag="academy_fields")]),
  W(when=W(stage=[0,99], flags_all=["academy_fields"], flags_none=["academy_power"]), script="dk1_academy_power", effects=[W(set_flag="academy_power")]),
  W(when=W(stage=[0,99], flags_all=["academy_power"], flags_none=["academy_fusions"]), script="dk1_academy_fusions", effects=[W(set_flag="academy_fusions")]),
  W(when=W(stage=[0,99], flags_all=["academy_fusions"], flags_none=["academy_graduate"]), script="dk1_academy_exam", duel="academy"),
  W(when=W(stage=[0,99], flags_all=["academy_graduate"]), script="dk1_academy_review", duel="academy_rematch")]),
 dict(id="hooded_man", area="village", anchor="plaza_center", duelist_id=None, stages=[2, 2], visible="placed",
      note="Placed by the bench script at night; removed after the riddle.",
      rules=[W(when=W(stage=[2,2], flags_none=["courier_met"]), script="dk1_hooded_riddle",
               effects=[W(give_item="stamp_card"), W(set_flag="courier_met"), W(set_stage=3), W(set_time="day"), W(remove_npc="hooded_man"), W(place_npc=W(npc="rex", area="village", anchor="east_road"))])]),
 dict(id="rex", area="village", anchor="east_road", duelist_id=9, stages=[3, 99], visible="placed",
      rules=[
  W(when=W(stage=[3,3], flags_none=["jono_asked"]), script="dk1_rex_first"),
  W(when=W(stage=[3,99], flags_all=["jono_asked"], flags_none=["treasure_won"]), script="dk1_rex_pre", duel="rex"),
  W(when=W(stage=[3,99]), script="dk1_rex_after")]),
 dict(id="bakura", area="cistern", anchor="bakura_spot", duelist_id=14, stages=[3, 99], visible="always",
      rules=[
  W(when=W(stage=[3,99], flags_none=["treasure_lost"]), script="dk1_bakura_pre", duel="bakura"),
  W(when=W(stage=[3,99], flags_all=["treasure_lost","mago_glyph"]), script="dk1_bakura_glyph"),
  W(when=W(stage=[3,99]), script="dk1_bakura_after")]),
 dict(id="mago_dev", area="village", anchor="mago_roof", duelist_id=None, stages=[0, 99], visible="observer", behavior="observer",
      note="Never talks, never walks to the hero, never blocks. Appears only through observer_events (silhouette + green aura, vanishes with a glitch). Talkable only in the epilogue (kingdom_outline.json).",
      rules=[]),
 dict(id="soldier", area="harbor", anchor="inspector_spot", duelist_id=18, stages=[4, 99], visible="always",
      rules=[
  W(when=W(stage=[4,5], flags_none=["inspector_won"]), script="dk1_inspector_pre", duel="inspector"),
  W(when=W(stage=[4,99]), script="dk1_inspector_after")]),
 dict(id="shadi", area="harbor", anchor="pier_end", duelist_id=13, stages=[5, 6], visible="placed",
      note="Placed when the inspector is beaten; removed when the Passage is given.",
      rules=[W(when=W(stage=[5,5], flags_all=["inspector_won"], flags_none=["shadi_won"]), script="dk1_shadi_pre", duel="shadi")]),
 dict(id="mai", area="ship_deck", anchor="mai_spot", duelist_id=11, stages=[7, 7], visible="always",
      rules=[
  W(when=W(stage=[7,7], flags_none=["mai_met"]), script="dk1_mai_rules", effects=[W(set_flag="mai_met")]),
  W(when=W(stage=[7,7]), script="dk1_mai_after")]),
 dict(id="inseto_kaiba", area="ship_deck", anchor="inseto_spot", duelist_id="inseto_kaiba", stages=[7, 7], visible="always",
      rules=[
  W(when=W(stage=[7,7], flags_none=["mai_met"]), script="dk1_inseto_early"),
  W(when=W(stage=[7,7], flags_all=["mai_met"], flags_none=["inseto_won"]), script="dk1_inseto_pre", duel="inseto"),
  W(when=W(stage=[7,7]), script="dk1_inseto_after")]),
]
NPC_SPEAKER = {"inseto_kaiba": "inseto"}

OBJECTS = [  # id, name_en, name_pt, area, anchor, solid_until flags, rules
 dict(id="notice_sign", name=B("Notice board", "Mural de avisos"), area="village", anchor="notice_sign", rules=[
  W(when=W(stage=[1,99], flags_none=["read_notice"]), script="dk1_notice", effects=[W(set_flag="read_notice")]),
  W(when=W(stage=[1,99]), script="dk1_notice_after")]),
 dict(id="plaza_bench", name=B("Stone bench", "Banco de pedra"), area="village", anchor="plaza_bench", rules=[
  W(when=W(stage=[0,1]), script="dk1_bench_early"),
  W(when=W(stage=[2,2], flags_none=["courier_met"]), script="dk1_bench", effects=[W(set_time="night"), W(set_flag="mago_roof"), W(place_npc=W(npc="hooded_man", area="village", anchor="plaza_center"))]),
  W(when=W(stage=[2,99]), script="dk1_bench_after")]),
 dict(id="date_palm", name=B("Date palm", "Tamareira"), area="village", anchor="date_palm", rules=[
  W(when=W(stage=[3,3], flags_all=["teana_asked"], flags_none=["got_dates"]), script="dk1_date_palm", effects=[W(give_item="dates"), W(set_flag="got_dates")]),
  W(when=W(stage=[0,99]), script="dk1_date_palm_idle")]),
 dict(id="river_bank", name=B("River", "Rio"), area="village", anchor="river_bank", rules=[
  W(when=W(stage=[3,3], flags_all=["jug_taken"], flags_none=["got_water"]), script="dk1_river_fill", effects=[W(give_item="river_water"), W(set_flag="got_water")]),
  W(when=W(stage=[0,99]), script="dk1_river_idle")]),
 dict(id="pyramid_hatch", name=B("Little pyramid hatch", "Escotilha da piramidezinha"), area="village", anchor="mini_pyramid_hatch",
      solid_until=["farmer_won"], rules=[W(when=W(stage=[0,99], flags_none=["farmer_won"]), script="dk1_hatch_locked")]),
 dict(id="bridge_north", name=B("Bridge to the harbor road", "Ponte para a estrada do porto"), area="village", anchor="bridge_north",
      solid_until=["treasure_lost","treasure_won","treasure_given"], rules=[
  W(when=W(stage=[0,3]), script="dk1_bridge_locked")]),
 dict(id="cistern_glyph", name=B("Green glyphs", "Letras verdes"), area="cistern", anchor="wall_glyph", rules=[
  W(when=W(stage=[3,99], flags_none=["mago_glyph"]), script="dk1_mago_glyph", effects=[W(set_flag="mago_glyph")]),
  W(when=W(stage=[3,99]), script="dk1_mago_glyph_after")]),
 dict(id="cistern_exit", name=B("Stairs up", "Escada para cima"), area="cistern", anchor="exit_stairs", rules=[]),
 dict(id="harbor_gate", name=B("Harbor gate", "Portao do porto"), area="harbor", anchor="inspector_spot",
      solid_until=["inspector_won"], rules=[W(when=W(stage=[0,99], flags_none=["inspector_won"]), script="dk1_gate_locked")]),
 dict(id="harbor_bridge_back", name=B("Road to the village", "Estrada para a vila"), area="harbor", anchor="bridge_back", rules=[]),
 dict(id="ship_gangway", name=B("Gangway", "Prancha"), area="harbor", anchor="gangway",
      solid_until=["simon_farewell","teana_farewell","jono_farewell"], rules=[W(when=W(stage=[0,6]), script="dk1_gangway_locked")]),
 dict(id="barrel", name=B("Barrel", "Barril"), area="ship_deck", anchor="barrel", rules=[W(when=W(stage=[7,99]), script="dk1_barrel")]),
 dict(id="ship_bow", name=B("Bow", "Proa"), area="ship_deck", anchor="bow", solid_until=["mai_met"], rules=[W(when=W(stage=[7,7], flags_none=["mai_met"]), script="dk1_bow_wait")]),
]

DUELS = [  # id, npc, duelist_id, deck, tier, pre, win, lose, win_flag, on_win, note
 dict(id="simon", npc="simon", duelist_id=1, deck="Simon Muran", tier=1, pre="dk1_simon_pre", win="dk1_simon_win", lose="dk1_simon_lose", win_flag="simon_won",
      on_win=[W(give_card="Magician of Faith"), W(set_stage=2)], note="The sage's test. Win tells the legend."),
 dict(id="baker", npc="baker", duelist_id=4, deck="Villager 1", tier=1, pre="dk1_baker_pre", win="dk1_baker_win", lose="dk1_baker_lose", win_flag="baker_won",
      on_win=[W(give_card="Mooyan Curry")], note="Optional training duel."),
 dict(id="farmer", npc="farmer", duelist_id=6, deck="Villager 3", tier=1, pre="dk1_farmer_pre", win="dk1_farmer_win", lose="dk1_farmer_lose", win_flag="farmer_won",
      on_win=[W(give_card="Killer Needle"), W(give_item="lantern")], note="Required for the Lost treasure (opens the hatch)."),
 dict(id="bakura", npc="bakura", duelist_id=14, deck="Yami Bakura", tier=3, pre="dk1_bakura_pre", win="dk1_bakura_win", lose="dk1_bakura_lose", win_flag="treasure_lost",
      on_win=[W(give_card="The 13th Grave"), W(give_item="scarab")], note="Lost treasure. Ghost who just wants company."),
 dict(id="rex", npc="rex", duelist_id=9, deck="Rex Raptor", tier=2, pre="dk1_rex_pre", win="dk1_rex_win", lose="dk1_rex_lose", win_flag="treasure_won",
      on_win=[W(give_card="Uraby"), W(give_item="bandana")], note="Won treasure."),
 dict(id="teana", npc="teana", duelist_id=2, deck="Teana", tier=1, pre="dk1_teana_pre", win="dk1_teana_win", lose="dk1_teana_lose", win_flag="treasure_given",
      on_win=[W(give_card="Kuriboh"), W(give_item="charm")], note="Given treasure."),
 dict(id="inspector", npc="soldier", duelist_id=18, deck="Mage Soldier", tier=3, pre="dk1_inspector_pre", win="dk1_inspector_win", lose="dk1_inspector_lose", win_flag="inspector_won",
      on_win=[W(give_card="Warrior of Tradition"), W(place_npc=W(npc="shadi", area="harbor", anchor="pier_end"))], note="Harbor exam."),
 dict(id="shadi", npc="shadi", duelist_id=13, deck="Shadi Courier", tier=4, pre="dk1_shadi_pre", win="dk1_shadi_win", lose="dk1_shadi_lose", win_flag="shadi_won",
      on_win=[W(give_card="Illusionist Faceless Mage"), W(set_flag="mago_passage"), W(give_item="star_passage"), W(give_item="star_chip"), W(add_stars=1), W(set_stage=6),
              W(remove_npc="shadi"), W(show_prop="ship"),
              W(move_npc=W(npc="simon", area="harbor", anchor="farewell_simon")), W(move_npc=W(npc="teana", area="harbor", anchor="farewell_teana")), W(move_npc=W(npc="jono", area="harbor", anchor="farewell_jono"))],
      note="Courier's trial. Win = Passage + 1 star + friends appear."),
 dict(id="inseto", npc="inseto_kaiba", duelist_id="inseto_kaiba", deck="InsetoKaiba", tier=5, pre="dk1_inseto_pre", win="dk1_inseto_win", lose="dk1_inseto_lose", win_flag="inseto_won",
      on_win=[W(give_card="Javelin Beetle"), W(give_item="bug_pin")], note="Optional boss on the ship. No stars at risk (the Kingdom has not started). Rematch in Chapter 8."),
 dict(id="academy", npc="academy_teacher", duelist_id=4, deck="Villager 1", tier=1, pre="dk1_academy_exam", win="dk1_academy_win", lose="dk1_academy_lose", win_flag="academy_graduate",
      on_win=[], note="Optional final class. A harmless practice duel after all five rules lessons."),
 dict(id="academy_rematch", npc="academy_teacher", duelist_id=4, deck="Villager 1", tier=1, pre="dk1_academy_review", win="dk1_academy_rematch_win", lose="dk1_academy_lose", win_flag="academy_graduate",
      on_win=[], note="Repeatable practice duel after graduation; no additional reward."),
]

TRANSITIONS = [
 dict(id="start", when=W(stage=[0,0]), trigger=W(kind="character_creation_done"), effects=[W(set_stage=1), W(give_item="rumor_notebook")], script="dk1_intro"),
 dict(id="treasures_done", when=W(stage=[3,3], flags_all=["treasure_lost","treasure_won","treasure_given"]), trigger=W(kind="when_true"), effects=[W(set_stage=4)], script="dk1_treasures_done"),
 dict(id="enter_cistern", when=W(stage=[3,99], flags_all=["farmer_won"]), trigger=W(kind="interact", object="pyramid_hatch"), effects=[W(teleport=W(area="cistern", anchor="spawn_stairs"))], script="dk1_cistern_enter"),
 dict(id="leave_cistern", when=W(stage=[0,99]), trigger=W(kind="interact", object="cistern_exit"), effects=[W(teleport=W(area="village", anchor="mini_pyramid_hatch"))], script="dk1_cistern_exit"),
 dict(id="cross_bridge", when=W(stage=[4,5]), trigger=W(kind="interact", object="bridge_north"), effects=[W(set_stage=5), W(teleport=W(area="harbor", anchor="spawn_gate"))], script="dk1_bridge_cross",
      note="set_stage 5 is a no-op when already 5. Chapter banner optional."),
 dict(id="back_to_village", when=W(stage=[5,6]), trigger=W(kind="interact", object="harbor_bridge_back"), effects=[W(teleport=W(area="village", anchor="bridge_north"))], script="dk1_bridge_back"),
 dict(id="board", when=W(stage=[6,6], flags_all=["simon_farewell","teana_farewell","jono_farewell"]), trigger=W(kind="interact", object="ship_gangway"), effects=[W(set_stage=7), W(teleport=W(area="ship_deck", anchor="spawn_gangway")), W(place_npc=W(npc="mai", area="ship_deck", anchor="mai_spot"))], script="dk1_board"),
 dict(id="arrival", when=W(stage=[7,7], flags_all=["mai_met"]), trigger=W(kind="interact", object="ship_bow"), effects=[W(set_flag="mago_mast"), W(set_stage=10), W(teleport=W(area="kingdom_beach", anchor="spawn"))], script="dk1_arrival"),
]

def _hud():  # ordered, first match wins; (when, en, pt)
 H = []
 hs = ["heard_teana","heard_jono","heard_guard"]
 nm = {"heard_teana":("Teana","Teana"),"heard_jono":("Jono","Jono"),"heard_guard":("the Guard","o Guarda")}
 import itertools
 H.append((W(stage=[1,1], flags_all=hs), "Tell Simon what you heard", "Conte ao Simon o que ouviu"))
 for k in (1, 2, 3):
  for missing in itertools.combinations(hs, k):
   have = [h for h in hs if h not in missing]
   en = "Ask " + " and ".join(nm[m][0] for m in missing)
   pt = "Pergunte a " + " e ".join(nm[m][1] if m != "heard_guard" else "o Guarda" for m in missing) if False else None
   ptn = {"heard_teana":"Teana","heard_jono":"Jono","heard_guard":"ao Guarda"}
   ptt = "Pergunte " + " e ".join(("a " + ptn[m]) if m != "heard_guard" else "ao Guarda" for m in missing)
   cond = W(stage=[1,1]);
   if have: cond["flags_all"] = have
   cond["flags_none"] = list(missing)
   H.append((cond, en + " about the whispers", ptt + " sobre os cochichos"))
 H += [
  (W(stage=[2,2], flags_none=["simon_won"]), "Talk to Simon", "Fale com Simon"),
  (W(stage=[2,2]), "Sit on the plaza bench and wait for night", "Sente no banco da praca e espere anoitecer"),
  (W(stage=[3,3], flags_all=["teana_asked","got_honey","got_water","got_dates"], flags_none=["treasure_given"]), "Bring the ingredients to Teana", "Leve os ingredientes para a Teana"),
  (W(stage=[3,3], flags_all=["teana_asked"], flags_none=["treasure_given"]), "Teana's cakes - honey, river water, dates", "Bolinhos da Teana - mel, agua do rio, tamaras"),
  (W(stage=[3,3], flags_all=["jono_asked"], flags_none=["treasure_won"]), "Beat Rex on the east road", "Venca o Rex na estrada leste"),
  (W(stage=[3,3], flags_all=["farmer_won"], flags_none=["treasure_lost"]), "Open the little pyramid hatch", "Abra a escotilha da piramidezinha"),
  (W(stage=[3,3], flags_all=["baker_hint"], flags_none=["farmer_won"]), "Win Kemet's lantern", "Ganhe a lanterna do Kemet"),
  (W(stage=[3,3]), "Find a Lost, a Won and a Given treasure", "Ache um tesouro Perdido, um Ganho e um Dado"),
  (W(stage=[4,4]), "Cross the bridge to the harbor", "Cruze a ponte ate o porto"),
  (W(stage=[5,5], flags_none=["inspector_won"]), "Beat the Inspector at the harbor gate", "Venca o Inspetor no portao do porto"),
  (W(stage=[5,5]), "Meet the Courier at the end of the pier", "Encontre o Mensageiro no fim do cais"),
  (W(stage=[6,6]), "Say goodbye to your friends, then board", "Despeca-se dos amigos e embarque"),
  (W(stage=[7,7], flags_none=["mai_met"]), "Talk to the lady on deck", "Fale com a dama no convez"),
  (W(stage=[7,7]), "Go to the bow of the ship", "Va ate a proa do navio"),
 ]
 return H
HUD = _hud()

CHAPTERS = [dict(n=1, title=B("The Whispering Village", "A Vila dos Cochichos"), region="village, cistern, harbor, ship", stage=[1,7], reward="Star Passage, 1 star", unlock="Duelist Kingdom")]

# quests: id, kind, title, giver, summary, steps[(objective_en, objective_pt, anchor, hud)], reward, optional
QUESTS = [
 dict(id="q01_whispers", kind="talk", opt=False, title=B("Whispers in the Square", "Cochichos na Praca"), giver="(none)", start=B("Chapter start", "Inicio do capitulo"),
      steps=[("Ask Teana, Jono and the Guard","Pergunte a Teana, Jono e ao Guarda","village.teana_stall / plaza_center / bridge_north")],
      reward="Rumor Notebook filled (3 rumors)"),
 dict(id="q02_sage", kind="talk+duel", opt=False, title=B("The Sage's Test", "O Teste do Sabio"), giver="simon",
      steps=[("Tell Simon what you heard, accept his duel","Conte ao Simon e aceite o duelo","village.house_ne_door")], reward="card Magician of Faith; the legend of the Kingdom"),
 dict(id="q03_stakeout", kind="investigate", opt=False, title=B("Midnight at the Bench", "Meia-noite no Banco"), giver="simon",
      steps=[("Sit on the plaza bench until night","Sente no banco da praca ate anoitecer","village.plaza_bench"),("Talk to the hooded man","Fale com o homem encapuzado","village.plaza_center")], reward="Stamp Card"),
 dict(id="q04_lost", kind="fetch+duel+explore", opt=False, title=B("The Lost: Founder's Scarab", "O Perdido: Escaravelho do Fundador"), giver="baker",
      steps=[("Ask Hakim about lost treasures","Pergunte ao Hakim sobre tesouros perdidos","village.bakery_door"),("Win Kemet's lantern in a duel","Ganhe a lanterna do Kemet num duelo","village.farmer_field"),
             ("Open the pyramid hatch, enter the cistern","Abra a escotilha e entre na cisterna","village.mini_pyramid_hatch"),("Duel Bakura the lonely ghost","Duele com Bakura, o fantasma solitario","cistern.bakura_spot")],
      reward="Founder's Scarab, cards Killer Needle and The 13th Grave, stamp Lost"),
 dict(id="q05_won", kind="talk+duel", opt=False, title=B("The Won: Jono's Bandana", "O Ganho: A Bandana do Jono"), giver="jono",
      steps=[("Meet Rex or Jono, any order","Encontre o Rex ou o Jono, em qualquer ordem","village.east_road / plaza_center"),("Beat Rex on the east road","Venca o Rex na estrada leste","village.east_road")],
      reward="Jono's Bandana, cards Uraby and Dragon Treasure, stamp Won"),
 dict(id="q06_given", kind="fetch+duel", opt=False, title=B("The Given: Teana's Cakes", "O Dado: Os Bolinhos da Teana"), giver="teana",
      steps=[("Take the Water Jug from Teana","Pegue a Jarra de Agua com a Teana","village.teana_stall"),("Honey from Hakim","Mel do Hakim","village.bakery_door"),("Fill the jug at the river","Encha a jarra no rio","village.river_bank"),
             ("Pick dates from the palm","Colha tamaras na palmeira","village.date_palm"),("Return to Teana and duel her","Volte a Teana e duele","village.teana_stall")],
      reward="Lucky Charm, card Kuriboh, stamp Given"),
 dict(id="q07_harbor", kind="duel", opt=False, title=B("The Harbor Exam", "O Exame do Porto"), giver="guard",
      steps=[("Cross the bridge, the Guard lets you pass","Cruze a ponte, o Guarda deixa","village.bridge_north"),("Beat the Inspector","Venca o Inspetor","harbor.inspector_spot")], reward="card Warrior of Tradition; gate opens"),
 dict(id="q08_courier", kind="duel+reveal", opt=False, title=B("The Courier's Trial", "O Teste do Mensageiro"), giver="shadi",
      steps=[("Walk to the end of the pier","Ande ate o fim do cais","harbor.pier_end"),("Beat Shadi","Venca Shadi","harbor.pier_end")], reward="Star Passage, Star Chip (1 star), card Illusionist Faceless Mage"),
 dict(id="q09_farewell", kind="talk", opt=False, title=B("Goodbye, Home Town", "Adeus, Minha Vila"), giver="(none)",
      steps=[("Talk to Simon, Teana and Jono on the pier","Fale com Simon, Teana e Jono no cais","harbor.farewell_*"),("Board the ship","Embarque no navio","harbor.gangway")], reward="card Mystical Elf; Simon's secret"),
 dict(id="q10_ship", kind="talk", opt=False, title=B("Rules of the Sea", "Regras do Mar"), giver="mai",
      steps=[("Talk to Mai on deck","Fale com Mai no convez","ship_deck.mai_spot"),("Go to the bow","Va a proa","ship_deck.bow")], reward="the star rules; end of chapter 1"),
 dict(id="s01_baker", kind="duel", opt=True, title=B("Hakim's Oven Duel", "O Duelo do Forno do Hakim"), giver="baker", steps=[("Duel Hakim","Duele com Hakim","village.bakery_door")], reward="card Mooyan Curry"),
 dict(id="s02_notice", kind="investigate", opt=True, title=B("The Gold Nail", "O Prego Dourado"), giver="(none)", steps=[("Read the notice board","Leia o mural","village.notice_sign")], reward="flavor"),
 dict(id="s03_barrel", kind="investigate", opt=True, title=B("The Giggling Barrel", "O Barril que Ri"), giver="(none)", steps=[("Check the barrel on deck","Veja o barril no convez","ship_deck.barrel")], reward="foreshadows Teana in Chapter 5"),
 dict(id="s04_inseto", kind="duel", opt=True, title=B("The Bug-Lord of the Ship", "O Senhor dos Insetos do Navio"), giver="inseto_kaiba", steps=[("Duel InsetoKaiba on deck, after Mai","Duele com InsetoKaiba no convez, depois da Mai","ship_deck.inseto_spot")], reward="Golden Bug Pin, card Javelin Beetle"),
]

# decks for the duelists that have no deck in ../../decks.json
DECKS = {
 "Villager 1": dict(duelist="Villager 1", tier=1, theme="Baker Hakim: plants, beasts and curry healing", cards={
   "Mushroom Man":3,"The Wicked Worm Beast":2,"Griffore":2,"Torike":2,"Beaver Warrior":2,"Armored Lizard":2,"Mooyan Curry":3,"Red Medicine":3,"Forest":2,
   "Beast Fangs":2,"Sogen":3,"Dryad":2,"Eldeen":2,"Wing Egg Elf":2,"Basic Insect":2,"Larvae Moth":2,"Petit Moth":2,"Hitotsu-me Giant":2},
   notes="Optional training duel: slow, many healing cards."),
 "Villager 3": dict(duelist="Villager 3", tier=1, theme="Farmer Kemet: insects and beasts on the Forest", cards={
   "Basic Insect":3,"Big Insect":2,"Killer Needle":3,"Giant Flea":2,"Larvae Moth":3,"Petit Moth":2,"Cockroach Knight":2,"Man-eater Bug":2,"Forest":3,
   "Beast Fangs":2,"Mushroom Man":2,"Griffore":2,"Torike":2,"Gokibore":2,"Hitotsu-me Giant":2,"Red Medicine":2,"Sogen":3,"Mooyan Curry":1},
   notes="Lantern duel: simple swarm."),
 "Yami Bakura": dict(duelist="Yami Bakura", tier=3, theme="Cistern ghost: Zombies with Yami", cards={
   "Skull Servant":3,"Shadow Specter":2,"Phantom Ghost":3,"Flame Ghost":2,"Wood Remains":2,"The 13th Grave":2,"Zombie Warrior":3,"Dokuroizo the Grim Reaper":1,
   "Magical Ghost":2,"Three-legged Zombies":2,"Pumpking the King of Ghosts":1,"Yami":3,"Dark Energy":2,"Dark Hole":1,"Stop Defense":1,"Bone Mouse":3,
   "The Wandering Doomed":2,"Temple of Skulls":1,"Fiend's Hand":2,"Graveyard and the Hand of Invitation":2},
   notes="Lost-treasure duel: spooky, sturdy, not cruel."),
 "Shadi Courier": dict(duelist="Shadi", tier=4, theme="Courier's trial: Rock walls with illusionists (a softer Shadi)", cards={
   "Giant Soldier of Stone":3,"Rock Spirit":3,"Stone Ghost":3,"Illusionist Faceless Mage":3,"Mysterious Puppeteer":2,"Protector of the Throne":2,"Royal Guard":1,
   "Skull Servant":2,"Spirit of the Mountain":2,"Mountain":3,"Steel Shell":2,"Mystical Moon":2,"Stop Defense":2,"Swords of Revealing Light":2,
   "Magical Labyrinth":1,"Ancient Sorcerer":1,"Dark Elf":1,"Soul of the Pure":2,"Wasteland":1,"Wall Shadow":1,"Millennium Golem":1},
   notes="Final trial of chapter 1."),
 "InsetoKaiba": dict(duelist="Kaiba (parody)", tier=5, theme="InsetoKaiba: 'unbeatable' insect swarm with Laser Cannon armors on the Forest", cards={
   "Hercules Beetle":3,"Giant Flea":2,"Killer Needle":2,"Big Insect":2,"Gokibore":2,"Hunter Spider":3,"Jirai Gumo":1,"Dungeon Worm":2,"Kwagar Hercules":1,
   "Great Moth":1,"Cocoon of Evolution":2,"Petit Moth":2,"Larvae Moth":2,"Insect Armor with Laser Cannon":3,"Vile Germs":2,"Forest":3,
   "Cockroach Knight":2,"Man-eater Bug":1,"Laser Cannon Armor":2,"Dark Hole":1,"Raigeki":1},
   notes="Optional ship boss. Chapter 8 rematch uses the same theme with Javelin Beetle and Great Moth (tier 8)."),
}

NEW_DUELISTS = [dict(id="inseto_kaiba", copy="Kaiba", name="InsetoKaiba", slot=42, portrait_slot=243, portrait_file="portraits/inseto_kaiba.png",
   note="Parody rival. Stylized caricature only, no real likeness or real name. AI base = Kaiba (duelist 17); drops: insect cards. Slots 40 and 41 are Cockatiel and mirror Atos of the old story.")]

# Observer events: Mago.dev appears but never acts. show_during = 0-based inclusive page range of a script during which he is visible.
OBSERVER_EVENTS = [
 dict(id="roof_at_night", n=1, npc="mago_dev", sprite="robe", overlay="aura", area="village", anchor="mago_roof", show_during=dict(script="dk1_bench", pages=[3, 4]), vanish="glitch", flag="mago_roof",
      note="He watches the hero waiting on the bench. The hooded man says to ignore him."),
 dict(id="cistern_glyph", n=2, npc="mago_dev", sprite=None, overlay="aura", area="cistern", anchor="wall_glyph", interact_object="cistern_glyph", flag="mago_glyph",
      note="Only his writing shows: green characters flickering on the wall. Bakura mentions it afterwards."),
 dict(id="breakwater_passage", n=3, npc="mago_dev", sprite="robe", overlay="aura", area="harbor", anchor="breakwater", show_during=dict(script="dk1_shadi_win", pages=[1, 4]), vanish="glitch", flag="mago_passage",
      note="He looks at the Star Passage from afar; Shadi says he only reads."),
 dict(id="mast_top", n=4, npc="mago_dev", sprite="robe", overlay="aura", area="ship_deck", anchor="mast_top", show_during=dict(script="dk1_arrival", pages=[0, 3]), vanish="glitch", flag="mago_mast",
      note="Sits at the top of the mast watching the island. Mai cannot see him."),
]

# ---------------------------------------------------------------- chapter 2 (the Shore of Illusions): dk_chapter2.py
import dk_chapter2 as _C2
SPEAKERS.update(_C2.SPEAKERS)
FLAGS += _C2.FLAGS
STAGES = sorted(STAGES + _C2.STAGES)
AREAS = [a if a[0] != "kingdom_beach" else ("kingdom_beach", "Shore of Illusions", "Costa das Ilusoes",
         "First area of the Kingdom: landing pier, a standing mirror, tents of the Shore Camp, a stall, a sea cave, a jungle path.", "exists (painted, chapter 2)")
         for a in AREAS]
ANCHORS["kingdom_beach"] = _C2.ANCHORS["kingdom_beach"]
ANCHORS["harbor"].update(_C2.ANCHORS["harbor_extra"]); ANCHORS["ship_deck"].update(_C2.ANCHORS["ship_extra"])
ITEMS += _C2.ITEMS
NPCS += _C2.NPCS
NPC_SPEAKER.update(_C2.NPC_SPEAKER)
OBJECTS += _C2.OBJECTS
DUELS += _C2.DUELS
TRANSITIONS += _C2.TRANSITIONS
HUD += _C2.HUD
CHAPTERS.append(_C2.CHAPTER)
QUESTS += _C2.QUESTS
DECKS.update(_C2.DECKS)
STARTER_DECK = _C2.STARTER_DECK

# ---------------------------------------------------------------- chapter 3 (the Forest of Whispers): dk_chapter3.py
import dk_chapter3 as _C3
SPEAKERS.update(_C3.SPEAKERS)
FLAGS += _C3.FLAGS
STAGES = sorted(STAGES + _C3.STAGES)
AREAS.append(("kingdom_forest", "Forest of Whispers", "Floresta dos Sussurros", "Second Kingdom area: a cross of paths in an old forest, a stone gate with a blue glow (the hidden clearing), a hermit's hut, a hollow stump.", "exists (painted, chapter 3)"))
ANCHORS["kingdom_forest"] = _C3.ANCHORS["kingdom_forest"]
ITEMS += _C3.ITEMS
NPCS += _C3.NPCS
NPC_SPEAKER.update(_C3.NPC_SPEAKER)
OBJECTS += _C3.OBJECTS
DUELS += _C3.DUELS
TRANSITIONS += _C3.TRANSITIONS
HUD += _C3.HUD
CHAPTERS.append(_C3.CHAPTER)
QUESTS += _C3.QUESTS
DECKS.update(_C3.DECKS)

# ---------------------------------------------------------------- chapter 4 (the Mountain Pass): dk_chapter4.py
import dk_chapter4 as _C4
SPEAKERS.update(_C4.SPEAKERS)
FLAGS += _C4.FLAGS
STAGES = sorted(STAGES + _C4.STAGES)
for _i, _a in enumerate(AREAS):
    if _a[0] == "kingdom_mountain": del AREAS[_i]; break
AREAS.append(("kingdom_mountain", "Mountain Pass", "Passagem da Montanha", "Third Kingdom area: a chasm and a rope bridge, an old mine shaft, a cliff tent, a cave under a carved star, the summit gate.", "exists (illustrated, chapter 4)"))
ANCHORS["kingdom_mountain"] = _C4.ANCHORS["kingdom_mountain"]
ITEMS += _C4.ITEMS
NPCS += _C4.NPCS
NPC_SPEAKER.update(_C4.NPC_SPEAKER)
OBJECTS += _C4.OBJECTS
DUELS += _C4.DUELS
TRANSITIONS += _C4.TRANSITIONS
HUD += _C4.HUD
CHAPTERS.append(_C4.CHAPTER)
QUESTS += _C4.QUESTS
DECKS.update(_C4.DECKS)

# ---------------------------------------------------------------- chapter 5 (the Meadow Maze): dk_chapter5.py
import dk_chapter5 as _C5
SPEAKERS.update(_C5.SPEAKERS)
FLAGS += _C5.FLAGS
STAGES = sorted(STAGES + _C5.STAGES)
for _i, _a in enumerate(AREAS):
    if _a[0] == "kingdom_meadow": del AREAS[_i]; break
AREAS.append(("kingdom_meadow", "Meadow Maze", "Labirinto da Campina", "Fourth Kingdom area: a hedge maze, a flower cart, a rabbit-hole arena, a star stone at the centre, the desert arch.", "exists (illustrated, chapter 5)"))
ANCHORS["kingdom_meadow"] = _C5.ANCHORS["kingdom_meadow"]
ITEMS += _C5.ITEMS
NPCS += _C5.NPCS
NPC_SPEAKER.update(_C5.NPC_SPEAKER)
OBJECTS += _C5.OBJECTS
DUELS += _C5.DUELS
TRANSITIONS += _C5.TRANSITIONS
HUD += _C5.HUD
CHAPTERS.append(_C5.CHAPTER)
QUESTS += _C5.QUESTS
DECKS.update(_C5.DECKS)


# ---------------------------------------------------------------- chapter 6 (the Desert of Lost Stars): dk_chapter6.py
import dk_chapter6 as _C6
SPEAKERS.update(_C6.SPEAKERS)
FLAGS += _C6.FLAGS
STAGES = sorted(STAGES + _C6.STAGES)
for _i, _a in enumerate(AREAS):
    if _a[0] == "kingdom_desert": del AREAS[_i]; break
AREAS.append(("kingdom_desert", "Desert of Lost Stars", "Deserto das Estrelas Perdidas", "Fifth Kingdom area: dunes, a fortune tent, a caravan tent, a sunken tomb arena, a buried star, the fair arch.", "exists (illustrated, chapter 6)"))
ANCHORS["kingdom_desert"] = _C6.ANCHORS["kingdom_desert"]
ITEMS += _C6.ITEMS
NPCS += _C6.NPCS
NPC_SPEAKER.update(_C6.NPC_SPEAKER)
OBJECTS += _C6.OBJECTS
DUELS += _C6.DUELS
TRANSITIONS += _C6.TRANSITIONS
HUD += _C6.HUD
CHAPTERS.append(_C6.CHAPTER)
QUESTS += _C6.QUESTS
DECKS.update(_C6.DECKS)

# Appended after every released chapter flag so existing save bits keep their
# meaning.  These optional academy lessons use the previously unused tail.
FLAGS += [
 ("academy_started", "Professor Nabil introduced the optional Duel Academy."),
 ("academy_basics", "Academy class 1 complete: turns, hand and battle."),
 ("academy_guardians", "Academy class 2 complete: Guardian Star cycles."),
 ("academy_fields", "Academy class 3 complete: terrain bonuses."),
 ("academy_power", "Academy class 4 complete: equips and stacked bonuses."),
 ("academy_fusions", "Academy class 5 complete: ordered fusion chains."),
 ("academy_graduate", "Won Professor Nabil's optional practice duel."),
]
