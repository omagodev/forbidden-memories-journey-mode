# -*- coding: utf-8 -*-
"""Chapter 3 - The Forest of Whispers (kingdom_forest): Rex Raptor lost and furious, three Star Marks cut in the
bark, the hidden clearing behind the stone gate and its master, the Forest Mage.  Same page rules as dk_scripts.py
(ASCII, 3 x 32).  Imported at the end of dk_scripts.py (scripts) and dk_data.py (structure)."""

def scripts(sc, H, X, N):
    sc("dk3_enter", "Chapter 2 -> 3: the hero takes the jungle path into the Forest of Whispers.", [
     N("Jungle Path", "Trilha da Selva", "Two stars glow on your glove. The sign lets you pass.",
       "Duas estrelas brilham na sua luva. A placa deixa voce passar."),
     H("Forest of Whispers. If the trees start talking, I'm leaving.",
       "Floresta dos Sussurros. Se as arvores falarem, eu vou embora."),
    ], chapter=3)
    sc("dk3_to_forest", "The jungle path after the first visit.", [
     N("Jungle Path", "Trilha da Selva", "The path climbs back into the whispering trees.",
       "A trilha volta a subir entre as arvores que sussurram."),
    ], chapter=3)
    sc("dk3_to_beach", "The south path back to the Shore of Illusions.", [
     N("Forest Edge", "Beira da Floresta", "The trees thin out. You smell the sea again.",
       "As arvores rareiam. Voce sente o cheiro do mar de novo."),
    ], chapter=3)
    sc("dk3_arrival", "Chapter 3 opens: the forest, the star cuts and a furious voice.", [
     N("Forest of Whispers", "Floresta", "Leaves rustle with no wind. Something is cut into the bark.",
       "Folhas mexem sem vento. Ha algo cortado na casca."),
     H("A star... carved into the tree. Fresh cut. Someone was here.",
       "Uma estrela... entalhada na arvore. Corte fresco. Alguem passou."),
     X("rex", "THIS WAY? NO! THAT WAY! Stupid trees keep moving!",
       "POR AQUI? NAO! POR ALI! Essas arvores idiotas ficam mudando!"),
     H("That shouting sounds familiar. Rex Raptor, from home?",
       "Esse grito e familiar. Rex Raptor, la de casa?"),
     N("Objective", "Objetivo", "Find the duelist shouting in the forest.", "Ache o duelista que grita na floresta."),
    ], chapter=3)
    sc("dk3_rex_pre", "Rex, lost for hours, blames the hero: a star wager.", [
     X("rex", "You! The kid from the village! Did you move the trees?",
       "Voce! O moleque da vila! Foi voce que mexeu nas arvores?"),
     H("Trees don't move, Rex. You're lost. Since when?",
       "Arvore nao anda, Rex. Voce ta perdido. Desde quando?"),
     X("rex", "Since breakfast! My dinos are hungry and so am I. Star on the line!",
       "Desde o cafe! Meus dinos tem fome e eu tambem. Estrela em jogo!"),
     H("One star each, then. And after that I show you the way out.",
       "Uma estrela cada, entao. Depois eu te mostro a saida."),
     X("rex", "Deal! Duel me right now, star for star?",
       "Fechado! Duela comigo agora, estrela por estrela?", ask=True),
    ], chapter=3)
    sc("dk3_rex_win", "Rex loses his star and calms down.", [
     X("rex", "Extinct... again. Fine. Take the star. You earned it.",
       "Extinto... de novo. Ta bom. Leva a estrela. Mereceu."),
     X("rex", "I saw those carved stars. Three of them. They point somewhere.",
       "Eu vi essas estrelas entalhadas. Sao tres. Elas apontam pra algo."),
     X("rex", "I followed them in circles. You try. I'm going to eat a mushroom.",
       "Segui em circulos. Tenta voce. Vou comer um cogumelo."),
     N("You got", "Voce ganhou", "A star and the card Megazowler.", "Uma estrela e a carta Megazowler."),
     N("Objective", "Objetivo", "Follow the three Star Marks on the trees.", "Siga as tres Marcas de Estrela nas arvores."),
    ], chapter=3)
    sc("dk3_rex_lose", "Rex wins the star.", [
     X("rex", "HA! Rawr! Still got it! Now which way is out?",
       "HA! Rawr! Ainda mando bem! Agora, qual e a saida?"),
     H("Ugh. My deck needs bigger teeth. The forest shop, maybe.",
       "Argh. Meu baralho precisa de dentes maiores. A loja, talvez."),
    ], chapter=3)
    sc("dk3_rex_after", "Rex after the duel, eating a mushroom.", [
     X("rex", "This mushroom tastes like socks. Go follow your stars.",
       "Esse cogumelo tem gosto de meia. Vai seguir suas estrelas."),
    ], chapter=3)
    sc("dk3_mark_1", "The first Star Mark (west).", [
     N("Star Mark", "Marca de Estrela", "A star cut deep in the bark. One point aims east.",
       "Uma estrela funda na casca. Uma ponta mira o leste."),
     H("One. The cut is clean, like a chisel. Not an animal.",
       "Uma. O corte e limpo, de cinzel. Nao foi bicho."),
    ], chapter=3)
    sc("dk3_mark_2", "The second Star Mark (north-east).", [
     N("Star Mark", "Marca de Estrela", "Another star, higher up. Its point aims at the stone gate.",
       "Outra estrela, mais alta. A ponta mira o portao de pedra."),
     H("Two. Whoever carves these is tall. Or brought a ladder.",
       "Duas. Quem entalha isso e alto. Ou trouxe uma escada."),
    ], chapter=3)
    sc("dk3_mark_3", "The third Star Mark (east).", [
     N("Star Mark", "Marca de Estrela", "A third star, still sticky with sap. It points to the gate too.",
       "Uma terceira estrela, ainda com seiva. Tambem aponta pro portao."),
     H("Three. Same hand. Same star. Who is marking this island?",
       "Tres. Mesma mao. Mesma estrela. Quem marca esta ilha?"),
    ], chapter=3)
    sc("dk3_mark_seen", "A Star Mark already read.", [
     N("Star Mark", "Marca de Estrela", "The carved star. You already followed this one.",
       "A estrela entalhada. Voce ja seguiu esta."),
    ], chapter=3)
    sc("dk3_gate_shut", "The stone gate before the three marks.", [
     N("Stone Gate", "Portao de Pedra", "Old stones and a cold blue glow. It will not let you in.",
       "Pedras velhas e um brilho azul frio. Nao deixa voce entrar."),
    ], chapter=3)
    sc("dk3_clearing_open", "The three marks read: the stone gate opens on the hidden clearing.", [
     N("Stone Gate", "Portao de Pedra", "The three stars glow at once. The gate hums and the mist parts.",
       "As tres estrelas brilham juntas. O portao zumbe e a nevoa abre."),
     X("forest_mage", "Three stars read, three steps true. The clearing welcomes you.",
       "Tres estrelas lidas, tres passos certos. A clareira te recebe."),
     H("You carved them? The stars on the trees?",
       "Foi voce que entalhou? As estrelas nas arvores?"),
     X("forest_mage", "Not I. They appear each moon. I only guard where they point.",
       "Eu nao. Elas surgem a cada lua. Eu so guardo onde apontam."),
     N("Objective", "Objetivo", "Duel the Forest Mage at the stone gate.", "Duele com o Mago da Floresta no portao."),
    ], chapter=3)
    sc("dk3_mage_pre", "The Forest Mage, zone master: a two-star wager.", [
     X("forest_mage", "I am the master of this wood. Three stars sleep in my roots.",
       "Sou o mestre deste bosque. Tres estrelas dormem nas minhas raizes."),
     X("forest_mage", "Wager what you dare. The forest is fair. Its roots are not.",
       "Aposte o que ousar. A floresta e justa. As raizes, nao."),
     H("One more star makes four. Let's grow some.",
       "Mais uma estrela e sao quatro. Vamos plantar."),
     X("forest_mage", "Then draw, sprout. Shall the roots begin?",
       "Entao compre, brotinho. As raizes podem comecar?", ask=True),
    ], chapter=3)
    sc("dk3_mage_win", "The Forest Mage loses: a star, the leaf, end of chapter 3.", [
     X("forest_mage", "The roots bow. Take my star, and this leaf.",
       "As raizes se curvam. Leve minha estrela, e esta folha."),
     N("You got", "Voce ganhou", "A star, the Whisper Leaf and the card Mystic Horseman.",
       "Uma estrela, a Folha Sussurrante e a carta Mystic Horseman."),
     X("forest_mage", "Whoever carves the stars walks every zone. Ask the mountains.",
       "Quem entalha as estrelas anda por toda zona. Pergunte as montanhas."),
     H("Four stars. Ten open the castle. A long way yet.",
       "Quatro estrelas. Dez abrem o castelo. Falta muito."),
     N("End of Chapter 3", "Fim do Capitulo 3", "The Forest of Whispers is behind you. The mountain pass waits.",
       "A Floresta dos Sussurros ficou para tras. A passagem da montanha espera."),
    ], chapter=3)
    sc("dk3_mage_lose", "The Forest Mage keeps his stars.", [
     X("forest_mage", "Roots hold. Come back with a stronger deck, little sprout.",
       "As raizes seguram. Volte com um baralho mais forte, brotinho."),
     H("Hermit Hob's hut and the Hollow Log Ring. Time to train.",
       "A cabana do Hob e o Ringue do Tronco Oco. Hora de treinar."),
    ], chapter=3)
    sc("dk3_mage_after", "The Forest Mage after the duel.", [
     X("forest_mage", "The leaf will whisper when a star is near. Listen to it.",
       "A folha sussurra quando uma estrela esta perto. Escute."),
    ], chapter=3)
    sc("dk3_pass_early", "The mountain pass before the clearing.", [
     N("Mountain Pass", "Passagem da Montanha", "A rope bars the road - Zone master's leave required.",
       "Uma corda bloqueia a estrada - Exige licenca do mestre da zona."),
    ], chapter=3)
    sc("dk3_pass_locked", "The mountain pass after chapter 3: the next part.", [
     N("Mountain Pass", "Passagem da Montanha", "The rope stays tight. The pass lets in only duelists with four stars.",
       "A corda segue firme. A passagem so deixa entrar quem tem quatro estrelas."),
    ], chapter=3)
    sc("dk3_hermit", "Hermit Hob, the forest hut.", [
     X("hermit_hob", "Mushrooms, moss and cards. The cards are the least weird.",
       "Cogumelos, musgo e cartas. As cartas sao o menos estranho."),
    ], chapter=3)

SPEAKERS = {
 "forest_mage": ("Forest Mage", "Mago da Floresta", "Forest Mage", 23, "Master of the Forest of Whispers (chapter 3 zone master)."),
 "hermit_hob": ("Hermit Hob", "Eremita Hob", "Hob", 254, "Forest hut keeper (economy)."),
}
FLAGS = [("forest_arrived", "Chapter 3: entered the Forest of Whispers."), ("rex_forest_won", "Rex beaten in the forest: third star."),
         ("star_mark_1", "Read the first Star Mark."), ("star_mark_2", "Read the second Star Mark."), ("star_mark_3", "Read the third Star Mark."),
         ("forest_mage_won", "Forest Mage beaten: fourth star, end of chapter 3.")]
STAGES = [(13, "Chapter 3: in the forest, Rex is lost"), (14, "Chapter 3: follow the three Star Marks"),
          (15, "Chapter 3: the clearing is open, the Forest Mage waits"), (16, "Chapter 3 complete: the mountain pass is the next part")]
ANCHORS = {"kingdom_forest": {"spawn": "South path in from the beach (bottom left).", "rex_spot": "The crossing of the paths, centre.",
                              "shop_stall": "Hermit Hob's sign by the bushes.", "star_mark_1": "A tree trunk on the west path.",
                              "star_mark_2": "A tree on the north-east path.", "star_mark_3": "A tree on the east path.",
                              "gate_spot": "The stone gate with the blue glow (top): the hidden clearing.",
                              "arena_door": "The hollow stump (left): the Hollow Log Ring.", "pass_road": "The road to the mountains (top right).",
                              "forest_center": "Centre of the cross of paths.", "hangout_a": "East grass.", "hangout_b": "South-west grass."}}
ITEMS = [("whisper_leaf", "Whisper Leaf", "Folha Sussurrante", "A leaf that rustles when a star is near.", "Uma folha que farfalha perto de uma estrela.", "the Forest Mage")]

def W(**k): return k
NPCS = [
 dict(id="rex_forest", area="kingdom_forest", anchor="rex_spot", duelist_id=9, stages=[13, 99], visible="placed",
      note="Rex Raptor again, lost in the forest; a star wager.",
      rules=[W(when=W(stage=[13,13], flags_none=["rex_forest_won"]), script="dk3_rex_pre", duel="rex_forest"),
             W(when=W(stage=[13,99]), script="dk3_rex_after")]),
 dict(id="forest_mage", area="kingdom_forest", anchor="gate_spot", duelist_id=23, stages=[15, 99], visible="placed",
      note="The zone master at the stone gate once the clearing is open.",
      rules=[W(when=W(stage=[15,15], flags_none=["forest_mage_won"]), script="dk3_mage_pre", duel="forest_mage"),
             W(when=W(stage=[15,99]), script="dk3_mage_after")]),
 dict(id="hermit_hob", area="kingdom_forest", anchor="shop_stall", duelist_id=None, stages=[13, 99], visible="always", rules=[W(when=W(stage=[13,99]), script="dk3_hermit")]),
]
NPC_SPEAKER = {"rex_forest": "rex"}
def B(en, pt): return {"en": en, "pt": pt}
def _mark(i):
    f = "star_mark_%d" % i
    return dict(id=f, name=B("Star Mark", "Marca de Estrela"), area="kingdom_forest", anchor=f, rules=[
     W(when=W(stage=[14,99], flags_none=[f]), script="dk3_mark_%d" % i, effects=[W(set_flag=f)]),
     W(when=W(stage=[13,99]), script="dk3_mark_seen")])
OBJECTS = [_mark(1), _mark(2), _mark(3),
 dict(id="forest_gate", name=B("Stone gate", "Portao de pedra"), area="kingdom_forest", anchor="gate_spot", rules=[
  W(when=W(stage=[13,14]), script="dk3_gate_shut")]),
 dict(id="pass_road", name=B("Mountain pass", "Passagem da montanha"), area="kingdom_forest", anchor="pass_road", rules=[
  W(when=W(stage=[16,99]), script="dk3_pass_locked"), W(when=W(stage=[13,15]), script="dk3_pass_early")]),
 dict(id="forest_exit", name=B("South path", "Trilha sul"), area="kingdom_forest", anchor="spawn", rules=[]),
]
DUELS = [
 dict(id="rex_forest", npc="rex_forest", duelist_id=9, deck="Rex Forest", tier=3, pre="dk3_rex_pre", win="dk3_rex_win", lose="dk3_rex_lose", win_flag="rex_forest_won",
      on_win=[W(give_card="Megazowler"), W(set_stage=14)], stars=2, note="Rex holds 2 stars; star wager. Rex's dinosaurs: the first wall after the weak starter."),
 dict(id="forest_mage", npc="forest_mage", duelist_id=23, deck="Forest Mage Grove", tier=4, pre="dk3_mage_pre", win="dk3_mage_win", lose="dk3_mage_lose", win_flag="forest_mage_won",
      on_win=[W(give_card="Mystic Horseman"), W(give_item="whisper_leaf"), W(set_stage=16)], stars=3,
      note="Zone master, holds 3 stars: bet 1 for the curve, more for a risky jump. Needs forest cards or arena wins."),
]
TRANSITIONS = [
 dict(id="enter_forest", when=W(stage=[12,12], stars=2), trigger=W(kind="interact", object="jungle_path"), effects=[W(set_stage=13), W(teleport=W(area="kingdom_forest", anchor="spawn"))], script="dk3_enter"),
 dict(id="to_forest", when=W(stage=[13,99]), trigger=W(kind="interact", object="jungle_path"), effects=[W(teleport=W(area="kingdom_forest", anchor="spawn"))], script="dk3_to_forest"),
 dict(id="to_beach", when=W(stage=[13,99]), trigger=W(kind="interact", object="forest_exit"), effects=[W(teleport=W(area="kingdom_beach", anchor="jungle_path"))], script="dk3_to_beach"),
 dict(id="forest_arrival", when=W(stage=[13,13], flags_none=["forest_arrived"]), trigger=W(kind="when_true", area="kingdom_forest"), effects=[W(set_flag="forest_arrived")], script="dk3_arrival"),
 dict(id="clearing_open", when=W(stage=[14,14], flags_all=["star_mark_1", "star_mark_2", "star_mark_3"]), trigger=W(kind="when_true", area="kingdom_forest"), effects=[W(set_stage=15)], script="dk3_clearing_open"),
]
HUD = [
 (W(stage=[13,13]), "Find the duelist shouting in the forest", "Ache o duelista que grita na floresta"),
 (W(stage=[14,14]), "Follow the three Star Marks on the trees", "Siga as tres Marcas de Estrela nas arvores"),
 (W(stage=[15,15]), "Beat the Forest Mage - a star on the line", "Venca o Mago da Floresta - uma estrela em jogo"),
 (W(stage=[16,16]), "Chapter 3 complete - the mountain pass waits", "Capitulo 3 completo - a passagem da montanha espera"),
]
CHAPTER = dict(n=3, title=B("The Forest of Whispers", "A Floresta dos Sussurros"), region="kingdom_forest", stage=[13,16],
               reward="four stars, Whisper Leaf, cards Megazowler and Mystic Horseman", unlock="the mountain pass (chapter 4)")
QUESTS = [
 dict(id="q12_forest", kind="talk+duel+investigate", opt=False, title=B("The Forest of Whispers", "A Floresta dos Sussurros"), giver="(none)",
      steps=[("Beat Rex Raptor for a star", "Venca o Rex Raptor por uma estrela", "kingdom_forest.rex_spot"),
             ("Follow the three Star Marks", "Siga as tres Marcas de Estrela", "kingdom_forest.star_mark_1"),
             ("Beat the Forest Mage for a star", "Venca o Mago da Floresta por uma estrela", "kingdom_forest.gate_spot")],
      reward="four stars, Whisper Leaf, cards Megazowler and Mystic Horseman"),
]
DECKS = {
 "Rex Forest": dict(duelist="Rex Raptor", tier=3, theme="Rex in the forest: a real dinosaur deck now", notes="Chapter 3 star duel: needs a few beach or forest upgrades.", cards={
   "Two-headed King Rex": 2, "Sword Arm of Dragon": 2, "Megazowler": 2, "Uraby": 3, "Crawling Dragon #2": 2, "Tomozaurus": 3, "Little D": 3,
   "Anthrosaurus": 3, "Petit Dragon": 3, "Grappler": 2, "Ancient Lizard Warrior": 2, "Dragon Treasure": 2, "Mountain": 3, "Sparks": 3,
   "Red Medicine": 2, "Hinotama": 3}),
 "Forest Mage Grove": dict(duelist="Forest Mage", tier=4, theme="Plants and beasts of the wood, Forest field", notes="Chapter 3 zone master (2 stars): beatable with forest cards and arena wins.", cards={
   "Trent": 2, "Queen of Autumn Leaves": 2, "Darkworld Thorns": 2, "Arlownay": 2, "Bean Soldier": 3, "Laughing Flower": 2,
   "Ancient Tree of Enlightenment": 2, "Yashinoki": 3, "Living Vase": 2, "Flower Wolf": 2, "Mystic Horseman": 2, "Garvas": 2,
   "Prevent Rat": 2, "Battle Steer": 2, "Mystical Elf": 1, "Forest": 3, "Sparks": 2, "Goblin's Secret Remedy": 2, "Raise Body Heat": 2}),
}
