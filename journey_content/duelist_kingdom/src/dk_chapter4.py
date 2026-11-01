# -*- coding: utf-8 -*-
"""Chapter 4 - The Mountain Pass (kingdom_mountain): straight on from the Forest of Whispers.  Bandit Keith runs a
one-star toll at the rope bridge, Mai waits on the far side for a rival duel, the star-carver is caught
at work in the cave (Croquet, Pegasus's steward: the marks are how the castle watches who collects stars), and the
Mountain Mage guards the summit gate.  Six stars: the castle road (ten open the castle itself).  Same page rules as dk_scripts.py (ASCII, 3 x 32).
Imported at the end of dk_scripts.py (scripts) and dk_data.py (structure)."""

def scripts(sc, H, X, N):
    sc("dk4_enter", "Chapter 3 -> 4: the hero climbs the forest road into the Mountain Pass.", [
     N("Mountain Pass", "Passagem da Montanha", "Four stars glow on your glove. The rope falls away.",
       "Quatro estrelas brilham na luva. A corda cai sozinha."),
     H("Up we go. The castle has to be somewhere above the clouds.",
       "Pra cima. O castelo tem que estar acima das nuvens."),
    ], chapter=4)
    sc("dk4_to_mountain", "The forest road after the first visit.", [
     N("Mountain Road", "Estrada da Montanha", "The road climbs back into the rocks and the wind.",
       "A estrada volta a subir entre as pedras e o vento."),
    ], chapter=4)
    sc("dk4_to_forest", "The trail back down to the forest.", [
     N("Pine Trail", "Trilha dos Pinheiros", "The wind drops. Pine smell. The forest is below.",
       "O vento para. Cheiro de pinheiro. A floresta fica abaixo."),
    ], chapter=4)
    sc("dk4_arrival", "Chapter 4 opens: the pass, the chasm and a toll at the bridge.", [
     N("Mountain Pass", "Passagem", "A chasm splits the pass. One rope bridge. One man on it.",
       "Um abismo corta a passagem. Uma ponte de corda. Um homem nela."),
     H("Another star cut in the rock, up by that cave. Bigger this time.",
       "Outra estrela entalhada na rocha, perto da caverna. Maior."),
     X("keith", "Toll bridge, kid! Nobody crosses Bandit Keith for free.",
       "Ponte com pedagio, moleque! Ninguem passa pelo Bandit Keith de graca."),
     N("Objective", "Objetivo", "Talk to the man guarding the rope bridge.", "Fale com o homem que guarda a ponte de corda."),
    ], chapter=4)
    sc("dk4_keith_pre", "Keith's toll: a one-star wager to cross the bridge.", [
     X("keith", "House rules. Toll is one star. You win, you cross with mine.",
       "Regra da casa. O pedagio e uma estrela. Ganhou, passa com a minha."),
     X("keith", "You lose, the toll's mine and you walk back down. Fair, huh?",
       "Perdeu, o pedagio e meu e voce desce a pe. Justo, ne?"),
     H("Fair for you. That deck smells like rigged slot machines.",
       "Justo pra voce. Esse baralho cheira a caca-niquel viciado."),
     X("keith", "In America we call it strategy. Shuffle up or scram?",
       "Na America a gente chama de estrategia. Embaralha ou some?", ask=True),
    ], chapter=4)
    sc("dk4_keith_win", "Keith pays up and opens the bridge.", [
     X("keith", "Tch. Machines jammed. Here, my star. And this junk.",
       "Tch. As maquinas travaram. Toma, minha estrela. E essa sucata."),
     N("You got", "Voce ganhou", "A star and the card Pendulum Machine.", "Uma estrela e a carta Pendulum Machine."),
     X("keith", "Blondie's waiting on the other side. She's no pushover.",
       "A loirinha te espera do outro lado. Ela nao e moleza."),
     N("Objective", "Objetivo", "Cross the rope bridge.", "Atravesse a ponte de corda."),
    ], chapter=4)
    sc("dk4_keith_lose", "Keith wins the toll.", [
     X("keith", "Jackpot! Thanks for the star, kid. Bridge stays closed.",
       "Jackpot! Valeu pela estrela, moleque. A ponte segue fechada."),
     H("His machines hit hard. Cliff Cass's tent, or the mine pit.",
       "As maquinas dele batem forte. A tenda da Cass, ou o poco da mina."),
    ], chapter=4)
    sc("dk4_keith_after", "Keith after the duel, counting chips.", [
     X("keith", "Beat it. I'm counting chips. Bridge is yours, sucker.",
       "Some daqui. To contando fichas. A ponte e sua, otario."),
    ], chapter=4)
    sc("dk4_keith_short", "Keith turns away a duelist under four stars.", [
     X("keith", "Four stars minimum, kid. I don't rob the broke. Scram.",
       "Quatro estrelas no minimo, moleque. Nao roubo duro. Some."),
    ], chapter=4)
    sc("dk4_mai_pre", "Mai on the far side of the bridge: the rival duel from the ship.", [
     X("mai", "Took you long enough. I was starting to like the view.",
       "Demorou, hein. Eu ja estava gostando da vista."),
     H("Mai! You came up the pass alone? Keith let you through?",
       "Mai! Voce subiu sozinha? O Keith te deixou passar?"),
     X("mai", "Keith owed me. You owe me a duel. No stars, just pride.",
       "O Keith me devia. Voce me deve um duelo. Sem estrelas, so orgulho."),
     X("mai", "Show me the ship wasn't luck. Ready, kid?",
       "Me mostra que o navio nao foi sorte. Pronto, garoto?", ask=True),
    ], chapter=4)
    sc("dk4_mai_win", "Mai loses with style (no star: a pride duel) and points at the cave.", [
     X("mai", "Not bad. My ladies needed a lesson in humility.",
       "Nada mal. Minhas damas precisavam de uma licao."),
     N("You got", "Voce ganhou", "The card Harpie Lady. Mai keeps her star.", "A carta Harpie Lady. A Mai fica com a estrela."),
     X("mai", "Free tip. Someone taps stone in that cave every night.",
       "Dica gratis. Alguem bate na pedra daquela caverna toda noite."),
     N("Objective", "Objetivo", "Find who carves the stars in the cave.", "Descubra quem entalha as estrelas na caverna."),
    ], chapter=4)
    sc("dk4_mai_lose", "Mai wins the pride duel (no star lost).", [
     X("mai", "Pretty cards, weak hand. Come back when you've grown.",
       "Cartas bonitas, mao fraca. Volte quando crescer."),
     H("She wasn't kidding. I need sky cards. The mine pit has them.",
       "Ela nao estava brincando. Preciso de cartas do ceu. A mina tem."),
    ], chapter=4)
    sc("dk4_mai_after", "Mai after the duel.", [
     X("mai", "Go on, detective. The cave. I'll keep the view.",
       "Vai, detetive. A caverna. Eu fico com a vista."),
    ], chapter=4)
    sc("dk4_cave_dark", "The cave before Mai's tip.", [
     N("Star Cave", "Caverna da Estrela", "A huge star cut over the mouth. Inside, only cold and dark.",
       "Uma estrela enorme sobre a entrada. Dentro, so frio e escuro."),
    ], chapter=4)
    sc("dk4_carver", "The star-carver caught at work: Croquet, Pegasus's steward. The payoff of the Star Marks.", [
     N("Star Cave", "Caverna da Estrela", "Tap. Tap. A hooded man is chiseling a star into the wall.",
       "Tec. Tec. Um homem de capuz entalha uma estrela na parede."),
     H("Got you! The beach, the forest, here. You carve the stars!",
       "Te peguei! A praia, a floresta, aqui. Voce entalha as estrelas!"),
     X("croquet", "Ahem. Croquet, steward of Master Pegasus. Guilty.",
       "Aham. Croquet, mordomo do Mestre Pegasus. Culpado."),
     X("croquet", "Each star is a window. The Master watches who walks by.",
       "Cada estrela e uma janela. O Mestre ve quem passa por elas."),
     H("He's been watching me since the shore? Why me?",
       "Ele me observa desde a praia? Por que eu?"),
     X("croquet", "He watches everyone. You he watches... closely. Good day.",
       "Ele observa todos. Voce, ele observa... de perto. Bom dia."),
     N("You got", "Voce ganhou", "The Star Chisel he left behind.", "O Cinzel Estelar que ele deixou para tras."),
     N("Objective", "Objetivo", "Climb to the summit gate.", "Suba ate o portao do cume."),
    ], chapter=4)
    sc("dk4_cave_empty", "The cave after Croquet is gone.", [
     N("Star Cave", "Caverna da Estrela", "Only stone dust and the fresh star. He is long gone.",
       "So po de pedra e a estrela fresca. Ele ja sumiu."),
    ], chapter=4)
    sc("dk4_gate_shut", "The summit gate before the Mountain Mage comes out.", [
     N("Summit Gate", "Portao do Cume", "A stone arch in the clouds. Six stars are carved on it. The wind pushes you back.",
       "Um arco de pedra nas nuvens. Seis estrelas gravadas. O vento empurra voce."),
    ], chapter=4)
    sc("dk4_mage_pre", "The Mountain Mage, zone master: a one-star wager at the summit gate.", [
     X("mountain_mage", "Few reach the summit with five stars. Fewer leave with six.",
       "Poucos chegam ao cume com cinco estrelas. Menos saem com seis."),
     X("mountain_mage", "One star against one. The mountain does not bend.",
       "Uma estrela contra uma. A montanha nao se curva."),
     H("Ten stars open the castle. I'm not going back down now.",
       "Dez estrelas abrem o castelo. Nao desco agora."),
     X("mountain_mage", "Then stand firm, pebble. Shall the stone speak?",
       "Entao fique firme, pedrinha. A pedra pode falar?", ask=True),
    ], chapter=4)
    sc("dk4_mage_short", "The Mountain Mage refuses a duelist under five stars.", [
     X("mountain_mage", "Five stars, pebble. Win back what you lost, then climb.",
       "Cinco estrelas, pedrinha. Recupere o que perdeu e suba."),
    ], chapter=4)
    sc("dk4_mage_win", "The Mountain Mage loses: six stars, end of chapter 4.", [
     X("mountain_mage", "The stone cracks. My star, and my stone soldier.",
       "A pedra racha. Minha estrela, e meu soldado de pedra."),
     N("You got", "Voce ganhou", "A star and the card Giant Soldier of Stone.",
       "Uma estrela e a carta Giant Soldier of Stone."),
     X("mountain_mage", "Croquet came this way too. The castle knows you are coming.",
       "Croquet passou por aqui. O castelo sabe que voce vem."),
     H("Six stars. Four to go, and a host watching every step.",
       "Seis estrelas. Faltam quatro, e um anfitriao me vigiando."),
     N("End of Chapter 4", "Fim do Capitulo 4", "The Mountain Pass is behind you. The castle road opens.",
       "A Passagem da Montanha ficou para tras. A estrada do castelo abre."),
    ], chapter=4)
    sc("dk4_mage_lose", "The Mountain Mage keeps his stars.", [
     X("mountain_mage", "Pebbles roll back down. Return heavier, little one.",
       "Pedrinhas rolam morro abaixo. Volte mais pesado, pequeno."),
     H("Stone beats me. Cliff Cass and the Mine Shaft Pit, then.",
       "A pedra me venceu. A Cliff Cass e o Poco da Mina, entao."),
    ], chapter=4)
    sc("dk4_mage_after", "The Mountain Mage after the duel.", [
     X("mountain_mage", "The road beyond the arch is yours. Mind the eyes on it.",
       "A estrada alem do arco e sua. Cuidado com os olhos nela."),
    ], chapter=4)
    sc("dk4_castle_road", "The summit gate after chapter 4: the next part.", [
     N("Castle Road", "Estrada do Castelo", "The castle shines above the clouds. Chapter 5 arrives in the next part.",
       "O castelo brilha acima das nuvens. O capitulo 5 chega na proxima parte."),
    ], chapter=4)
    sc("dk4_cliff_cass", "Cliff Cass, the mountain tent.", [
     X("cliff_cass", "Rope, pitons, cards. Only the cards ever save anyone.",
       "Corda, grampos, cartas. So as cartas salvam alguem."),
    ], chapter=4)
    sc("dk4_trail_camp", "The trail camp: where you wake if the last star is lost up here.", [
     N("Trail Camp", "Acampamento", "A tarp, a cot and a lantern. Kingdom staff keep it lit.",
       "Uma lona, um catre e um lampiao. A equipe do Reino o mantem."),
    ], chapter=4)
    sc("k3_eliminated", "Last star lost in the forest or the mountains: wake at the area's trail camp with one star.", [
     N("Trail Camp", "Acampamento", "You wake under a tarp. A star chip rests on your chest.",
       "Voce acorda sob uma lona. Uma ficha de estrela esta no seu peito."),
     X("staff", "Pegasus sends his regards. One free star. Do better, duelist.",
       "Pegasus manda lembrancas. Uma estrela gratis. Faca melhor, duelista."),
     H("Back to one star. Shop, arena, thieves. Train, then climb.",
       "De volta a uma estrela. Loja, arena, ladroes. Treino e subo."),
    ], chapter=4)

SPEAKERS = {
 "keith": ("Bandit Keith", "Bandit Keith", "Keith", 12, "Gambler who runs a toll on the rope bridge (chapter 4)."),
 "mountain_mage": ("Mountain Mage", "Mago da Montanha", "Mountain Mage", 25, "Master of the Mountain Pass (chapter 4 zone master)."),
 "croquet": ("Croquet", "Croquet", "Croquet", 254, "Pegasus's steward, the star-carver. Voice only (hooded)."),
 "cliff_cass": ("Cliff Cass", "Cliff Cass", "Cass", 254, "Mountain tent keeper (economy)."),
}
FLAGS = [("mountain_arrived", "Chapter 4: entered the Mountain Pass."), ("keith_won", "Keith beaten at the bridge: fifth star."),
         ("mai_mountain_won", "Mai beaten across the bridge (pride duel, no star)."), ("carver_found", "Croquet caught carving: the Star Chisel."),
         ("mountain_mage_won", "Mountain Mage beaten: sixth star, end of chapter 4.")]
STAGES = [(17, "Chapter 4: the pass, Keith's toll at the bridge"), (18, "Chapter 4: across the bridge, Mai waits"),
          (19, "Chapter 4: the star-carver in the cave"), (20, "Chapter 4: the Mountain Mage at the summit gate"),
          (21, "Chapter 4 complete: the castle road is the next part")]
ANCHORS = {"kingdom_mountain": {"spawn": "Pine trail up from the forest (bottom left).", "trail_camp": "A tarp by the trail (bottom left).",
                                "keith_spot": "West end of the rope bridge.", "shop_stall": "Cliff Cass's tent (centre left).",
                                "arena_door": "The old mine shaft (top left): the Mine Shaft Pit.", "mai_spot": "East side, past the bridge.",
                                "cave_spot": "The cave mouth under the big carved star (right).", "gate_spot": "The steps of the summit gate (top).",
                                "summit_gate": "The stone arch at the top: the castle road.", "pass_center": "The open trail west of the chasm.",
                                "hangout_a": "East trail.", "hangout_b": "West trail by the pines."}}
ITEMS = [("star_chips", "Star Chips", "Fichas de Estrela", "Story star chips. Only gatekeepers and zone masters hand them out. Ten open the castle.", "Fichas de estrela da historia. So guardioes e mestres de zona as dao. Dez abrem o castelo.", "Shadi, then the Kingdom's gatekeepers"),
         ("star_chisel", "Star Chisel", "Cinzel Estelar", "Croquet's chisel. The tip still glows like a star.",
          "O cinzel do Croquet. A ponta ainda brilha como estrela.", "Croquet, in the Star Cave")]

def W(**k): return k
NPCS = [
 dict(id="keith", area="kingdom_mountain", anchor="keith_spot", duelist_id=12, stages=[17, 99], visible="placed",
      note="Bandit Keith's toll bridge: a one-star wager; needs four stars to be challenged.",
      rules=[W(when=W(stage=[17,17], flags_none=["keith_won"], earned=4), script="dk4_keith_pre", duel="keith"),
             W(when=W(stage=[17,17], flags_none=["keith_won"]), script="dk4_keith_short"),
             W(when=W(stage=[17,99]), script="dk4_keith_after")]),
 dict(id="mai_mountain", area="kingdom_mountain", anchor="mai_spot", duelist_id=11, stages=[18, 99], visible="placed",
      note="Mai, the rival from the ship, across the bridge: a pride duel, no star.",
      rules=[W(when=W(stage=[18,18], flags_none=["mai_mountain_won"]), script="dk4_mai_pre", duel="mai_mountain"),
             W(when=W(stage=[18,99]), script="dk4_mai_after")]),
 dict(id="star_carver", area="kingdom_mountain", anchor="cave_spot", duelist_id=None, stages=[19, 19], visible="placed",
      note="Croquet, hooded, carving a star in the cave: the payoff of the Star Marks; gone after the scene.",
      rules=[W(when=W(stage=[19,19], flags_none=["carver_found"]), script="dk4_carver",
               effects=[W(set_flag="carver_found"), W(give_item="star_chisel"), W(set_stage=20)])]),
 dict(id="mountain_mage", area="kingdom_mountain", anchor="gate_spot", duelist_id=25, stages=[20, 99], visible="placed",
      note="The zone master at the summit gate once the carver is found.",
      rules=[W(when=W(stage=[20,20], flags_none=["mountain_mage_won"], earned=5), script="dk4_mage_pre", duel="mountain_mage"),
             W(when=W(stage=[20,20], flags_none=["mountain_mage_won"]), script="dk4_mage_short"),
             W(when=W(stage=[20,99]), script="dk4_mage_after")]),
 dict(id="cliff_cass", area="kingdom_mountain", anchor="shop_stall", duelist_id=None, stages=[17, 99], visible="always", rules=[W(when=W(stage=[17,99]), script="dk4_cliff_cass")]),
]
NPC_SPEAKER = {"mai_mountain": "mai", "star_carver": "croquet"}
def B(en, pt): return {"en": en, "pt": pt}
OBJECTS = [
 dict(id="star_cave", name=B("Star Cave", "Caverna da Estrela"), area="kingdom_mountain", anchor="cave_spot", rules=[
  W(when=W(stage=[20,99]), script="dk4_cave_empty"), W(when=W(stage=[17,18]), script="dk4_cave_dark")]),
 dict(id="summit_gate", name=B("Summit gate", "Portao do cume"), area="kingdom_mountain", anchor="summit_gate", rules=[
  W(when=W(stage=[21,99], earned=6), script="dk4_castle_road"), W(when=W(stage=[17,99]), script="dk4_gate_shut")]),
 dict(id="rope_bridge_far", name=B("Rope bridge", "Ponte de corda"), area="kingdom_mountain", anchor="mai_spot", rules=[]),
 dict(id="trail_camp", name=B("Trail camp", "Acampamento da trilha"), area="kingdom_mountain", anchor="trail_camp", rules=[
  W(when=W(stage=[17,99]), script="dk4_trail_camp")]),
 dict(id="mountain_exit", name=B("Pine trail", "Trilha dos pinheiros"), area="kingdom_mountain", anchor="spawn", rules=[]),
]
DUELS = [
 dict(id="keith", npc="keith", duelist_id=12, deck="Keith Toll", tier=4, pre="dk4_keith_pre", win="dk4_keith_win", lose="dk4_keith_lose", win_flag="keith_won",
      on_win=[W(give_card="Pendulum Machine"), W(set_stage=18)], stars=1,
      note="Toll: +1 star on a win, -1 on a loss (won back with the win). Machines: needs forest and mountain upgrades."),
 dict(id="mai_mountain", npc="mai_mountain", duelist_id=11, deck="Mai Cliff", tier=4, pre="dk4_mai_pre", win="dk4_mai_win", lose="dk4_mai_lose", win_flag="mai_mountain_won",
      on_win=[W(give_card="Harpie Lady"), W(set_stage=19)], note="Pride duel, no star: stars come only from the zone's gatekeepers. Mai's harpies, now with real support."),
 dict(id="mountain_mage", npc="mountain_mage", duelist_id=25, deck="Mountain Mage Summit", tier=5, pre="dk4_mage_pre", win="dk4_mage_win", lose="dk4_mage_lose", win_flag="mountain_mage_won",
      on_win=[W(give_card="Giant Soldier of Stone"), W(set_stage=21)], stars=1,
      note="Zone master: +1 star on a win, -1 on a loss (won back with the win). Needs five stars to accept. Needs mountain cards or Mine Shaft Pit wins."),
]
TRANSITIONS = [
 dict(id="enter_mountain", when=W(stage=[16,16], earned=4), trigger=W(kind="interact", object="pass_road"), effects=[W(set_stage=17), W(teleport=W(area="kingdom_mountain", anchor="spawn"))], script="dk4_enter"),
 dict(id="to_mountain", when=W(stage=[17,99]), trigger=W(kind="interact", object="pass_road"), effects=[W(teleport=W(area="kingdom_mountain", anchor="spawn"))], script="dk4_to_mountain"),
 dict(id="to_forest", when=W(stage=[17,99]), trigger=W(kind="interact", object="mountain_exit"), effects=[W(teleport=W(area="kingdom_forest", anchor="pass_road"))], script="dk4_to_forest"),
 dict(id="mountain_arrival", when=W(stage=[17,17], flags_none=["mountain_arrived"]), trigger=W(kind="when_true", area="kingdom_mountain"), effects=[W(set_flag="mountain_arrived")], script="dk4_arrival"),
]
HUD = [
 (W(stage=[17,17]), "Beat Bandit Keith at the bridge - his toll is a star", "Venca o Bandit Keith na ponte - o pedagio e uma estrela"),
 (W(stage=[18,18]), "Cross the bridge - Mai waits on the far side", "Atravesse a ponte - Mai espera do outro lado"),
 (W(stage=[19,19]), "Find who carves the stars in the cave", "Descubra quem entalha as estrelas na caverna"),
 (W(stage=[20,20]), "Beat the Mountain Mage - a star on the line", "Venca o Mago da Montanha - uma estrela em jogo"),
 (W(stage=[21,99]), "Chapter 4 complete - the castle road waits", "Capitulo 4 completo - a estrada do castelo espera"),
]
CHAPTER = dict(n=4, title=B("The Mountain Pass", "A Passagem da Montanha"), region="kingdom_mountain", stage=[17,21],
               reward="six stars, Star Chisel, cards Pendulum Machine, Harpie Lady and Giant Soldier of Stone", unlock="the castle road (chapter 5)")
QUESTS = [
 dict(id="q13_mountain", kind="talk+duel+investigate", opt=False, title=B("The Mountain Pass", "A Passagem da Montanha"), giver="(none)",
      steps=[("Beat Bandit Keith at the bridge", "Venca o Bandit Keith na ponte", "kingdom_mountain.keith_spot"),
             ("Beat Mai across the bridge", "Venca a Mai do outro lado da ponte", "kingdom_mountain.mai_spot"),
             ("Find the star-carver in the cave", "Ache o entalhador na caverna", "kingdom_mountain.cave_spot"),
             ("Beat the Mountain Mage for a star", "Venca o Mago da Montanha por uma estrela", "kingdom_mountain.gate_spot")],
      reward="six stars, Star Chisel, cards Pendulum Machine, Harpie Lady and Giant Soldier of Stone"),
]
DECKS = {
 "Keith Toll": dict(duelist="Bandit Keith", tier=4, theme="Keith's rigged machines", notes="Chapter 4 toll (one star): needs forest or mountain upgrades.", cards={
   "Pendulum Machine": 1, "Mechanicalchacer": 2, "Cyber Soldier": 2, "Giga-tech Wolf": 2, "Machine Attacker": 2, "Ground Attacker Bugroth": 2,
   "Patrol Robo": 3, "Mechanical Snail": 2, "Mechanical Spider": 3, "Dharma Cannon": 2, "Cyber-Stein": 2, "Yaiba Robo": 3, "Holograh": 2,
   "Wasteland": 3, "Mountain": 2, "Sparks": 3, "Red Medicine": 2, "Machine Conversion Factory": 2}),
 "Mai Cliff": dict(duelist="Mai Valentine", tier=4, theme="Mai's harpies and sky birds on a Mountain field", notes="Chapter 4 rival duel (1 star).", cards={
   "Harpie Lady": 2, "Queen Bird": 2, "Monstrous Bird": 1, "Skull Red Bird": 2, "Blue-winged Crown": 2, "Faith Bird": 2, "Peacock": 2,
   "Takuhee": 2, "Droll Bird": 3, "Niwatori": 3, "Winged Dragon #2": 3, "Sonic Maid": 2, "Princess of Tsurugi": 2, "Follow Wind": 2,
   "Mountain": 3, "Sparks": 2, "Red Medicine": 3, "Cursebreaker": 2}),
 "Mountain Mage Summit": dict(duelist="Mountain Mage", tier=5, theme="Stone warriors, golems and the Mountain field", notes="Chapter 4 zone master (2 stars): beatable with mountain cards and arena wins.", cards={
   "Giant Soldier of Stone": 2, "Stone Ogre Grotto": 2, "Rock Ogre Grotto #2": 2, "Destroyer Golem": 2, "Sand Stone": 2, "Golgoil": 2,
   "Stone Armadiller": 3, "Rock Ogre Grotto #1": 3, "Haniwa": 3, "Stone Ghost": 2, "Dissolverock": 2, "Barrel Rock": 2, "Zanki": 2,
   "Celtic Guardian": 2, "Mountain": 3, "Sparks": 2, "Red Medicine": 2, "Invigoration": 2}),
}
