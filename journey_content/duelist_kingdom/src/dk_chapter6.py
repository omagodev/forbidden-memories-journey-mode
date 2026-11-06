# -*- coding: utf-8 -*-
"""Chapter 6 - Desert of Lost Stars (kingdom_desert): straight on from the Meadow Maze.  Isis reads the
hero's cards and drops the star-collector clue (MAGO.DEV glimpse 5).  Teana the helper tags along with
hints.  Bakura floats in for a comic cards-only duel.  The Desert Mage at the buried star holds stars for
a wager (seven -> eight on the minimum bet).  Nomad Nia's Caravan Tent, the Sunken Tomb Pit with three
exclusives, a Jackal ambush and a desert camp.  Same page rules as dk_scripts.py (ASCII, 3 x 32).
Imported at the end of dk_scripts.py (scripts) and dk_data.py (structure)."""

def scripts(sc, H, X, N):
    sc("dk6_enter", "Chapter 5 -> 6: the desert arch opens onto the dunes.", [
     N("Desert of Lost Stars", "Deserto das Estrelas Perdidas", "Seven stars. Hot wind. Sand underfoot.",
       "Sete estrelas. Vento quente. Areia sob os pes."),
     H("The grass turned gold. The Kingdom still watches.",
       "A grama ficou dourada. O Reino ainda observa."),
    ], chapter=6)
    sc("dk6_to_desert", "The desert road after the first visit.", [
     N("Desert Road", "Estrada do Deserto", "Heat shimmer. Dunes ahead. The buried star waits.",
       "Calor no ar. Dunas a frente. A estrela enterrada espera."),
    ], chapter=6)
    sc("dk6_to_meadow", "The trail back to the Meadow Maze.", [
     N("Meadow Trail", "Trilha da Campina", "The wind turns soft. Hedges and flowers again.",
       "O vento fica macio. Cercas e flores de novo."),
    ], chapter=6)
    sc("dk6_arrival", "Chapter 6 opens: dunes, a fortune tent, a giggle of sand.", [
     N("Desert of Lost Stars", "Deserto", "Gold dunes. A striped tent. A purple tent. Someone hums nearby.",
       "Dunas douradas. Uma tenda listrada. Uma tenda roxa. Alguem cantarola perto."),
     H("Teana followed me. Of course she did.",
       "A Teana me seguiu. Claro que seguiu."),
     X("teana", "Hot! Soft! Adventure! And my charm still works out here.",
       "Quente! Macio! Aventura! E meu amuleto ainda funciona por aqui."),
     N("Objective", "Objetivo", "Talk to Isis at the purple fortune tent.",
       "Fale com a Isis na tenda roxa da cartomante."),
    ], chapter=6)
    sc("dk6_isis_pre", "Isis the fortune teller: a reading, then a tip about the star collector.", [
     X("isis", "Sand remembers every footstep. Sit. The cards already know your name.",
       "A areia lembra cada passo. Sente. As cartas ja sabem seu nome."),
     H("Seven stars. Three more for the castle. What do the cards say?",
       "Sete estrelas. Faltam tres pro castelo. O que as cartas dizem?"),
     X("isis", "The cards show a watcher. Not from this island. Not from this world.",
       "As cartas mostram um observador. Nao e desta ilha. Nao e deste mundo."),
     X("isis", "He writes reality, yet today he only reads. Do not seek him.",
       "Ele escreve a realidade, mas hoje so le. Nao o procure."),
     X("isis", "And this: someone upstairs collects stars of the eliminated. A harvest.",
       "E isto: alguem la em cima junta as estrelas dos eliminados. Uma colheita."),
     X("isis", "The Desert Mage keeps two at the buried star. Shall we read your courage too?",
       "O Mago do Deserto guarda duas na estrela enterrada. Queremos ler sua coragem tambem?", ask=True),
    ], chapter=6)
    sc("dk6_isis_win", "Isis's friendly reading duel ends; the tip sticks.", [
     X("isis", "The cards smile. Take this dust-charm. The Mage waits at the buried star.",
       "As cartas sorriem. Leve este amuleto de poeira. O Mago espera na estrela enterrada."),
     N("You got", "Voce ganhou", "Isis's Dust Charm. Teana still tips; Isis's clue stays with you.",
       "O Amuleto de Poeira da Isis. A Teana ainda da dicas; a pista da Isis fica com voce."),
     X("isis", "Bet small for the curve. Bet big if the dunes call your name.",
       "Aposte pouco pra curva. Aposte muito se as dunas chamarem seu nome."),
     N("Objective", "Objetivo", "Find the Desert Mage at the buried star.",
       "Ache o Mago do Deserto na estrela enterrada."),
    ], chapter=6)
    sc("dk6_isis_lose", "Isis wins the reading duel (no star).", [
     X("isis", "The cards are kind. Try again when the sand feels lighter.",
       "As cartas sao gentis. Tente de novo quando a areia pesar menos."),
     H("Nia's tent, or the Sunken Tomb Pit. Then back to Isis.",
       "A tenda da Nia, ou o Poco da Tumba Afundada. Depois volto pra Isis."),
    ], chapter=6)
    sc("dk6_isis_after", "Isis after the reading.", [
     X("isis", "The watcher still turns a page. You do not need him. Go.",
       "O observador ainda vira uma pagina. Voce nao precisa dele. Va."),
    ], chapter=6)
    sc("dk6_hint", "A free tip from helper Teana in the desert.", [
     X("teana", "Buried star, big mage, two chips. Min bet: eight. Fair gate after. Drink water!",
       "Estrela enterrada, mago grande, duas fichas. Aposta min: oito. Portao da feira depois. Beba agua!"),
    ], chapter=6)
    sc("dk6_teana_after", "Teana the helper hanging around the dunes.", [
     X("teana", "I packed cake crumbs. They melt. Sad. Still cute though!",
       "Trouxe migalhas de bolo. Derretem. Triste. Mas ainda fofo!"),
    ], chapter=6)
    sc("dk6_bakura_pre", "Bakura's comic desert cameo: cards only, no star.", [
     X("bakura", "The cistern was damp. The desert is dry. I am bored either way.",
       "A cisterna era umida. O deserto e seco. Eu me entedio dos dois jeitos."),
     H("Bakura? You floated all the way from home?",
       "Bakura? Voce flutuou ate aqui desde casa?"),
     X("bakura", "Ghosts travel light. Duel me for fun. No stars. Just cards.",
       "Fantasmas viajam leves. Duelo por diversao. Sem estrelas. So cartas.", ask=True),
    ], chapter=6)
    sc("dk6_bakura_win", "Bakura loses the comic duel.", [
     X("bakura", "Heh. Take a bone from my pocket. I will haunt someone cooler.",
       "Heh. Leve um osso do meu bolso. Vou assombrar alguem mais legal."),
     N("You got", "Voce ganhou", "The card Armored Zombie.",
       "A carta Armored Zombie."),
    ], chapter=6)
    sc("dk6_bakura_lose", "Bakura wins the comic duel.", [
     X("bakura", "See? Even sand ghosts can still shuffle. Rematch when you dare.",
       "Viu? Ate fantasmas de areia ainda embaralham. Revanche quando ousar."),
    ], chapter=6)
    sc("dk6_bakura_after", "Bakura after the comic duel.", [
     X("bakura", "The Mage is less fun than me. Go bother him.",
       "O Mago e menos divertido que eu. Vai incomodar ele."),
    ], chapter=6)
    sc("dk6_star_early", "The buried star before Isis's tip lands.", [
     N("Buried Star", "Estrela Enterrada", "A stone star half under the sand. The heat still feels heavy.",
       "Uma estrela de pedra meio sob a areia. O calor ainda pesa."),
    ], chapter=6)
    sc("dk6_mage_pre", "The Desert Mage, zone master: a one-star wager at the buried star.", [
     X("desert_mage", "Seven stars walk my dunes. Few leave with eight.",
       "Sete estrelas andam nas minhas dunas. Poucos saem com oito."),
     X("desert_mage", "Two stars rest under this stone. Wager what your nerve allows.",
       "Duas estrelas repousam sob esta pedra. Aposte o que sua coragem deixar."),
     H("Ten open the castle. I am not turning back for sand.",
       "Dez abrem o castelo. Nao volto por causa de areia."),
     X("desert_mage", "Then burn or bury, traveler. Shall the desert speak?",
       "Entao queime ou enterre, viajante. O deserto pode falar?", ask=True),
    ], chapter=6)
    sc("dk6_mage_win", "The Desert Mage loses: eight stars, end of chapter 6.", [
     X("desert_mage", "The dunes part. My star, and dust from my sash.",
       "As dunas se abrem. Minha estrela, e poeira da minha faixa."),
     N("You got", "Voce ganhou", "A star and the card Great Mammoth of Goldfine.",
       "Uma estrela e a carta Great Mammoth of Goldfine."),
     X("desert_mage", "Beyond the arch the banners snap. The Star Fair waits. The Kingdom still watches.",
       "Alem do arco as bandeiras estalam. A Feira das Estrelas espera. O Reino ainda observa."),
     H("Eight stars. Two to go. Teana is humming somewhere in the heat.",
       "Oito estrelas. Faltam duas. A Teana esta cantarolando em algum lugar no calor."),
     N("End of Chapter 6", "Fim do Capitulo 6", "The Desert of Lost Stars is behind you. The fair road opens.",
       "O Deserto das Estrelas Perdidas ficou para tras. A estrada da feira abre."),
    ], chapter=6)
    sc("dk6_mage_lose", "The Desert Mage keeps his stars.", [
     X("desert_mage", "Sand covers the weak. Return heavier, little spark.",
       "A areia cobre os fracos. Volte mais pesado, faiscazinha."),
     H("He outplayed me. Nia's tent and the Sunken Tomb Pit, then.",
       "Ele me passou. A tenda da Nia e o Poco da Tumba Afundada, entao."),
    ], chapter=6)
    sc("dk6_mage_after", "The Desert Mage after the duel.", [
     X("desert_mage", "The fair arch is yours. Mind the mirages on the way.",
       "O arco da feira e seu. Cuidado com as miragens no caminho."),
    ], chapter=6)
    sc("dk6_fair_road", "The arch after chapter 6: the next part.", [
     N("Fair Road", "Estrada da Feira", "Banners on the wind. Music far off. The Star Fair opens ahead.",
       "Bandeiras no vento. Musica ao longe. A Feira das Estrelas abre a frente."),
    ], chapter=6)
    sc("dk6_gate_shut", "The fair arch before eight stars.", [
     N("Fair Arch", "Arco da Feira", "A stone arch on the dune. Eight stars are carved on it. The sand pushes you back.",
       "Um arco de pedra na duna. Oito estrelas gravadas. A areia empurra voce."),
    ], chapter=6)
    sc("dk6_nomad_nia", "Nomad Nia, the caravan tent.", [
     X("nomad_nia", "Water, shade and cards. Only the cards travel farther than camels.",
       "Agua, sombra e cartas. So as cartas viajam mais longe que camelos."),
    ], chapter=6)
    sc("dk6_desert_camp", "The desert camp: a tarp, and the game-over warning.", [
     N("Desert Camp", "Acampamento", "A tarp among dunes. Kingdom staff keep a lantern lit even in daylight.",
       "Uma lona entre dunas. A equipe do Reino mantem um lampiao mesmo de dia."),
     X("staff", "Pretty dunes. Deadly rules. Lose your last star and your journey ends for good.",
       "Dunas bonitas. Regras duras. Perdeu a ultima estrela e a jornada acaba de vez."),
    ], chapter=6)

SPEAKERS = {
 "isis": ("Isis", "Isis", "Isis", 16, "Fortune teller of the desert (chapter 6); senses the watcher."),
 "desert_mage": ("Desert Mage", "Mago do Deserto", "Desert Mage", 27, "Master of the Desert of Lost Stars (chapter 6 zone master)."),
 "bakura": ("Yami Bakura", "Yami Bakura", "Bakura", 14, "Comic desert cameo; cards only, no star (chapter 6)."),
 "teana": ("Teana", "Teana", "Teana", 20, "Helper from the Meadow Maze; tips continue in the desert."),
 "nomad_nia": ("Nomad Nia", "Nomade Nia", "Nia", 254, "Desert caravan-tent keeper (economy)."),
 "staff": ("Camp Staff", "Equipe do Acampamento", "Staff", 254, "Kingdom staff at the desert camp."),
}
FLAGS = [("desert_arrived", "Chapter 6: entered the Desert of Lost Stars."),
         ("isis_desert_won", "Isis's reading duel won: dust charm and star-collector clue."),
         ("bakura_desert_won", "Bakura's comic desert duel won (cards only)."),
         ("desert_mage_won", "Desert Mage beaten: eighth star, end of chapter 6.")]
STAGES = [(25, "Chapter 6: the dunes, Isis at the fortune tent"),
          (26, "Chapter 6: Isis's clue; the Desert Mage at the buried star"),
          (27, "Chapter 6 complete: the fair road is the next part")]
ANCHORS = {"kingdom_desert": {
 "spawn": "Path in from the meadow (bottom left).",
 "desert_camp": "A tarp among dunes (bottom left).",
 "isis_spot": "The purple fortune tent.",
 "shop_stall": "Nomad Nia's striped caravan tent.",
 "arena_door": "The sunken tomb entrance (bottom right): the Sunken Tomb Pit.",
 "gate_spot": "The half-buried stone star where the Desert Mage waits.",
 "fair_gate": "The stone arch at the top: the fair road.",
 "bakura_spot": "A shimmer of heat near the dunes' center.",
 "teana_spot": "Shade near the desert camp where Teana waits.",
 "desert_center": "Open sand near the buried star.",
 "hangout_a": "East dune path.",
 "hangout_b": "West dune path by the camp.",
}}
ITEMS = [("dust_charm", "Dust Charm", "Amuleto de Poeira",
          "Isis's charm. A reminder: someone upstairs harvests lost stars.",
          "O amuleto da Isis. Lembrete: alguem la em cima colhe estrelas perdidas.",
          "Isis, in the Desert of Lost Stars")]

def W(**k): return k
NPCS = [
 dict(id="isis_desert", area="kingdom_desert", anchor="isis_spot", duelist_id=16, stages=[25, 99], visible="placed",
      note="Isis the fortune teller: reading duel, then the star-collector clue.",
      rules=[W(when=W(stage=[25,25], flags_none=["isis_desert_won"]), script="dk6_isis_pre", duel="isis_desert"),
             W(when=W(stage=[26,99]), script="dk6_isis_after")]),
 dict(id="teana_desert", area="kingdom_desert", anchor="teana_spot", duelist_id=20, stages=[25, 99], visible="placed",
      note="Teana the helper: tips continue from the meadow.",
      rules=[W(when=W(stage=[25,99], needs=["teana_meadow_won"]), script="dk6_hint"),
             W(when=W(stage=[25,99]), script="dk6_teana_after")]),
 dict(id="bakura_desert", area="kingdom_desert", anchor="bakura_spot", duelist_id=14, stages=[25, 99], visible="placed",
      note="Bakura comic cameo: cards only, no star.",
      rules=[W(when=W(stage=[25,99], flags_none=["bakura_desert_won"]), script="dk6_bakura_pre", duel="bakura_desert"),
             W(when=W(stage=[25,99], needs=["bakura_desert_won"]), script="dk6_bakura_after")]),
 dict(id="desert_mage", area="kingdom_desert", anchor="gate_spot", duelist_id=27, stages=[26, 99], visible="placed",
      note="The zone master at the buried star once Isis has spoken.",
      rules=[W(when=W(stage=[26,26], flags_none=["desert_mage_won"]), script="dk6_mage_pre", duel="desert_mage"),
             W(when=W(stage=[26,99]), script="dk6_mage_after")]),
 dict(id="nomad_nia", area="kingdom_desert", anchor="shop_stall", duelist_id=None, stages=[25, 99], visible="always",
      rules=[W(when=W(stage=[25,99]), script="dk6_nomad_nia")]),
]
NPC_SPEAKER = {"isis_desert": "isis", "teana_desert": "teana", "bakura_desert": "bakura"}
def B(en, pt): return {"en": en, "pt": pt}
OBJECTS = [
 dict(id="buried_star", name=B("Buried star", "Estrela enterrada"), area="kingdom_desert", anchor="gate_spot", rules=[
  W(when=W(stage=[25,25]), script="dk6_star_early")]),
 dict(id="fair_gate", name=B("Fair arch", "Arco da feira"), area="kingdom_desert", anchor="fair_gate", rules=[
  W(when=W(stage=[27,99], stars=8), script="dk6_fair_road"), W(when=W(stage=[25,99]), script="dk6_gate_shut")]),
 dict(id="desert_camp", name=B("Desert camp", "Acampamento do deserto"), area="kingdom_desert", anchor="desert_camp", rules=[
  W(when=W(stage=[25,99]), script="dk6_desert_camp")]),
 dict(id="desert_exit", name=B("Meadow trail", "Trilha da campina"), area="kingdom_desert", anchor="spawn", rules=[]),
]
DUELS = [
 dict(id="isis_desert", npc="isis_desert", duelist_id=16, deck="Isis Reading", tier=5, pre="dk6_isis_pre", win="dk6_isis_win", lose="dk6_isis_lose", win_flag="isis_desert_won",
      on_win=[W(give_item="dust_charm"), W(set_stage=26)],
      note="Friendly reading duel, no star: Isis's clue and dust charm."),
 dict(id="bakura_desert", npc="bakura_desert", duelist_id=14, deck="Bakura Desert", tier=3, pre="dk6_bakura_pre", win="dk6_bakura_win", lose="dk6_bakura_lose", win_flag="bakura_desert_won",
      on_win=[W(give_card="Armored Zombie")],
      note="Comic cameo, cards only, no star."),
 dict(id="desert_mage", npc="desert_mage", duelist_id=27, deck="Desert Mage Dunes", tier=6, pre="dk6_mage_pre", win="dk6_mage_win", lose="dk6_mage_lose", win_flag="desert_mage_won",
      on_win=[W(give_card="Great Mammoth of Goldfine"), W(set_stage=27)], stars=2,
      note="Zone master, holds 2 stars: bet 1 for the curve (7->8). Needs desert cards or Sunken Tomb Pit wins."),
]
TRANSITIONS = [
 dict(id="enter_desert", when=W(stage=[24,24], stars=7), trigger=W(kind="interact", object="desert_gate"), effects=[W(set_stage=25), W(teleport=W(area="kingdom_desert", anchor="spawn"))], script="dk6_enter"),
 dict(id="to_desert", when=W(stage=[25,99]), trigger=W(kind="interact", object="desert_gate"), effects=[W(teleport=W(area="kingdom_desert", anchor="spawn"))], script="dk6_to_desert"),
 dict(id="to_meadow_from_desert", when=W(stage=[25,99]), trigger=W(kind="interact", object="desert_exit"), effects=[W(teleport=W(area="kingdom_meadow", anchor="desert_gate"))], script="dk6_to_meadow"),
 dict(id="desert_arrival", when=W(stage=[25,25], flags_none=["desert_arrived"]), trigger=W(kind="when_true", area="kingdom_desert"), effects=[W(set_flag="desert_arrived")], script="dk6_arrival"),
]
HUD = [
 (W(stage=[25,25]), "Talk to Isis at the fortune tent - a reading in the dunes", "Fale com a Isis na tenda - uma leitura nas dunas"),
 (W(stage=[26,26]), "Beat the Desert Mage - a star on the line", "Venca o Mago do Deserto - uma estrela em jogo"),
 (W(stage=[27,27]), "Chapter 6 complete - take the fair arch", "Capitulo 6 completo - pegue o arco da feira"),
 (W(stage=[28,99]), "Beyond the desert - the Star Fair", "Alem do deserto - a Feira das Estrelas"),
]
CHAPTER = dict(n=6, title=B("Desert of Lost Stars", "Deserto das Estrelas Perdidas"), region="kingdom_desert", stage=[25,27],
               reward="eight stars, Dust Charm, card Great Mammoth of Goldfine", unlock="the fair road (chapter 7)")
QUESTS = [
 dict(id="q15_desert", kind="talk+duel", opt=False, title=B("Desert of Lost Stars", "Deserto das Estrelas Perdidas"), giver="(none)",
      steps=[("Talk to Isis at the fortune tent", "Fale com a Isis na tenda da cartomante", "kingdom_desert.isis_spot"),
             ("Beat the Desert Mage for a star", "Venca o Mago do Deserto por uma estrela", "kingdom_desert.gate_spot")],
      reward="eight stars, Dust Charm, card Great Mammoth of Goldfine"),
]
DECKS = {
 "Isis Reading": dict(duelist="Isis", tier=5, theme="Light fairies, spells and desert sand", notes="Chapter 6 reading duel (no star).", cards={
   "Mystical Elf": 2, "Ancient Elf": 2, "Fairy's Gift": 2, "Happy Lover": 2, "LaMoon": 2, "Weather Control": 2,
   "Time Wizard": 2, "Mystical Sand": 1, "Sand Stone": 2, "Wasteland": 3, "Swords of Revealing Light": 1,
   "Sparks": 2, "Red Medicine": 3, "Haniwa": 2, "Key Mace": 2, "Curtain of the Dark Ones": 2, "Pot the Trick": 2}),
 "Bakura Desert": dict(duelist="Yami Bakura", tier=3, theme="Zombies and dark comic spice", notes="Chapter 6 comic cameo (no star).", cards={
   "Armored Zombie": 2, "Clown Zombie": 2, "Dragon Zombie": 2, "The 13th Grave": 3, "Shadow Specter": 3,
   "Skull Servant": 3, "Yaranzo": 2, "Ghoul with an Appetite": 1, "Dark Energy": 2, "Wasteland": 3,
   "Sparks": 2, "Red Medicine": 2, "Mooyan Curry": 2, "Hinotama": 2, "Firegrass": 2}),
 "Desert Mage Dunes": dict(duelist="Desert Mage", tier=6, theme="Sand, rock and the Wasteland field", notes="Chapter 6 zone master (holds 2).", cards={
   "Great Mammoth of Goldfine": 1, "Skelgon": 2, "Shadow Ghoul": 2, "Mystical Sand": 2, "Destroyer Golem": 2,
   "Sand Stone": 2, "Stone Ogre Grotto": 2, "Rock Spirit": 1, "Armored Zombie": 2, "Dragon Zombie": 2,
   "Wasteland": 3, "Mountain": 2, "Sparks": 2, "Red Medicine": 2, "Invigoration": 2, "Hinotama": 2, "Mooyan Curry": 2}),
}
