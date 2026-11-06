# -*- coding: utf-8 -*-
"""Chapter 5 - The Meadow Maze (kingdom_meadow): straight on from the Mountain Pass.  Teana (the giggling
barrel from the ship) stowed away and waits in the hedges for a friendly duel, then becomes a helper with
hints; she carries a golden star from the hooded man that matches the Kingdom's star shape.  The Meadow Mage
at the maze centre holds stars for a wager (six -> seven on the minimum bet).  Rose Rue's cart, the Rabbit
Hole Ring with three exclusives, a Jackal ambush and a meadow camp.  Same page rules as dk_scripts.py (ASCII, 3 x 32).
Imported at the end of dk_scripts.py (scripts) and dk_data.py (structure)."""

def scripts(sc, H, X, N):
    sc("dk5_enter", "Chapter 4 -> 5: the summit road opens onto the Meadow Maze.", [
     N("Meadow Maze", "Labirinto da Campina", "Six stars. The wind turns soft. Hedges and flowers.",
       "Seis estrelas. O vento fica macio. Cercas e flores."),
     H("A maze. After the pass, this almost feels like a break.",
       "Um labirinto. Depois da passagem, quase parece descanso."),
    ], chapter=5)
    sc("dk5_to_meadow", "The castle road after the first visit.", [
     N("Meadow Road", "Estrada da Campina", "The hedges close in again. Flower smell. Soft ground.",
       "As cercas fecham de novo. Cheiro de flor. Chao macio."),
    ], chapter=5)
    sc("dk5_to_mountain", "The trail back up to the Mountain Pass.", [
     N("Summit Trail", "Trilha do Cume", "The wind turns hard. Stone underfoot. The pass is above.",
       "O vento endurece. Pedra sob os pes. A passagem fica acima."),
    ], chapter=5)
    sc("dk5_arrival", "Chapter 5 opens: the hedge maze, a giggle in the leaves.", [
     N("Meadow Maze", "Labirinto", "Tall green walls. Paths that twist. Someone giggles in the leaves.",
       "Paredes verdes altas. Caminhos tortos. Alguem ri nas folhas."),
     H("That laugh. I heard it inside a barrel on the ship.",
       "Essa risada. Eu ouvi dentro de um barril no navio."),
     X("teana", "Shh! You found me. Surprise!",
       "Xiu! Voce me achou. Surpresa!"),
     N("Objective", "Objetivo", "Talk to Teana in the hedges.", "Fale com a Teana nas cercas."),
    ], chapter=5)
    sc("dk5_teana_pre", "Teana the stowaway: a friendly duel, then she helps.", [
     X("teana", "I hid in that barrel. The ship smelled like fish and adventure!",
       "Eu me escondi naquele barril. O navio cheirava a peixe e aventura!"),
     H("Teana! The village is going to miss you. And the cakes.",
       "Teana! A vila vai sentir sua falta. E os bolos."),
     X("teana", "I brought a golden star. The hooded man gave it to me. Look - same shape as yours!",
       "Trouxe uma estrela dourada. O homem de capuz me deu. Olha - o mesmo formato da sua!"),
     X("teana", "Duel me first. Friendly. If you win, I guide you through the maze. Deal?",
       "Me desafie primeiro. Amistoso. Se ganhar, eu te guio no labirinto. Combinado?", ask=True),
    ], chapter=5)
    sc("dk5_teana_win", "Teana loses the friendly duel and becomes a helper.", [
     X("teana", "Ow, my pride! Fine. You win. I am your maze guide now.",
       "Ai, meu orgulho! Tudo bem. Voce ganhou. Sou sua guia do labirinto."),
     N("You got", "Voce ganhou", "Teana's Hint Charm. She will tip you from here on.",
       "O Amuleto de Dica da Teana. Ela te da dicas daqui pra frente."),
     X("teana", "Centre of the maze: a mage with stars. She does not giggle. Go careful.",
       "Centro do labirinto: uma maga com estrelas. Ela nao ri. Vai com cuidado."),
     N("Objective", "Objetivo", "Find the Meadow Mage at the maze centre.",
       "Ache a Maga da Campina no centro do labirinto."),
    ], chapter=5)
    sc("dk5_teana_lose", "Teana wins the friendly duel (no star).", [
     X("teana", "Hee! Still got it. Try again when you are ready. I will wait.",
       "Hihi! Ainda tenho jogo. Tente de novo quando quiser. Eu espero."),
     H("She plays cute and hits hard. Rose Rue's cart, or the rabbit hole.",
       "Ela faz gracinha e bate forte. O carrinho da Rose Rue, ou a toca do coelho."),
    ], chapter=5)
    sc("dk5_teana_after", "Teana the helper after the friendly duel.", [
     X("teana", "Left, left, right, then the star stone. Or ask me again. I like talking.",
       "Esquerda, esquerda, direita, depois a pedra da estrela. Ou me pergunta de novo."),
    ], chapter=5)
    sc("dk5_hint", "A free tip from helper Teana.", [
     X("teana", "The Mage holds stars. Bet small if you want the curve. Bet big if you are brave. Or broke.",
       "A Maga guarda estrelas. Aposte pouco pra curva. Aposte muito se for corajoso. Ou estiver duro."),
    ], chapter=5)
    sc("dk5_centre_early", "The star stone before Teana's tip.", [
     N("Star Stone", "Pedra da Estrela", "A carved star in the stone. The hedges still feel closed.",
       "Uma estrela entalhada na pedra. As cercas ainda parecem fechadas."),
    ], chapter=5)
    sc("dk5_mage_pre", "The Meadow Mage, zone master: a one-star wager at the maze centre.", [
     X("meadow_mage", "Six stars walk my maze. Few leave with seven.",
       "Seis estrelas andam no meu labirinto. Poucos saem com sete."),
     X("meadow_mage", "Two stars rest in these hedges. Wager what your nerve allows.",
       "Duas estrelas repousam nestas cercas. Aposte o que sua coragem deixar."),
     H("Ten open the castle. I am not turning back for flowers.",
       "Dez abrem o castelo. Nao volto por causa de flores."),
     X("meadow_mage", "Then bloom or wilt, traveler. Shall the meadow speak?",
       "Entao floresca ou murche, viajante. A campina pode falar?", ask=True),
    ], chapter=5)
    sc("dk5_mage_win", "The Meadow Mage loses: seven stars, end of chapter 5.", [
     X("meadow_mage", "The hedges part. My star, and a leaf from my crown.",
       "As cercas se abrem. Minha estrela, e uma folha da minha coroa."),
     N("You got", "Voce ganhou", "A star and the card Queen of Autumn Leaves.",
       "Uma estrela e a carta Queen of Autumn Leaves."),
     X("meadow_mage", "Beyond the arch the grass turns gold. Desert wind. The Kingdom still watches.",
       "Alem do arco a grama fica dourada. Vento do deserto. O Reino ainda observa."),
     H("Seven stars. Three to go. Teana is humming somewhere in the leaves.",
       "Sete estrelas. Faltam tres. A Teana esta cantarolando em algum lugar nas folhas."),
     N("End of Chapter 5", "Fim do Capitulo 5", "The Meadow Maze is behind you. The desert road opens.",
       "O Labirinto da Campina ficou para tras. A estrada do deserto abre."),
    ], chapter=5)
    sc("dk5_mage_lose", "The Meadow Mage keeps her stars.", [
     X("meadow_mage", "Petals fall. Return heavier, little bloom.",
       "Petalas caem. Volte mais pesado, florzinha."),
     H("She outplayed me. Rose Rue and the Rabbit Hole Ring, then.",
       "Ela me passou. Rose Rue e o Anel da Toca do Coelho, entao."),
    ], chapter=5)
    sc("dk5_mage_after", "The Meadow Mage after the duel.", [
     X("meadow_mage", "The arch is yours. Mind the thorns on the way.",
       "O arco e seu. Cuidado com os espinhos no caminho."),
    ], chapter=5)
    sc("dk5_desert_road", "The arch after chapter 5: the next part.", [
     N("Desert Road", "Estrada do Deserto", "Gold grass. Hot wind. Chapter 6 arrives in the next part.",
       "Grama dourada. Vento quente. O capitulo 6 chega na proxima parte."),
    ], chapter=5)
    sc("dk5_gate_shut", "The desert arch before seven stars.", [
     N("Desert Arch", "Arco do Deserto", "A vine-covered arch. Seven stars are carved on it. The hedges push you back.",
       "Um arco coberto de vinhas. Sete estrelas gravadas. As cercas empurram voce."),
    ], chapter=5)
    sc("dk5_rose_rue", "Rose Rue, the meadow flower cart.", [
     X("rose_rue", "Roses, thorns and cards. Only the cards ever bloom twice.",
       "Rosas, espinhos e cartas. So as cartas florescem duas vezes."),
    ], chapter=5)
    sc("dk5_meadow_camp", "The meadow camp: a lantern, and the game-over warning.", [
     N("Meadow Camp", "Acampamento", "A tarp among wildflowers. Kingdom staff keep a lantern lit.",
       "Uma lona entre flores do campo. A equipe do Reino mantem um lampiao."),
     X("staff", "Pretty place. Deadly rules. Lose your last star and your journey ends for good.",
       "Lugar bonito. Regras duras. Perdeu a ultima estrela e a jornada acaba de vez."),
    ], chapter=5)

SPEAKERS = {
 "teana": ("Teana", "Teana", "Teana", 20, "Stowaway from the ship barrel; becomes a maze helper (chapter 5)."),
 "meadow_mage": ("Meadow Mage", "Maga da Campina", "Meadow Mage", 29, "Master of the Meadow Maze (chapter 5 zone master)."),
 "rose_rue": ("Rose Rue", "Rose Rue", "Rue", 254, "Meadow flower-cart keeper (economy)."),
 "staff": ("Camp Staff", "Equipe do Acampamento", "Staff", 254, "Kingdom staff at the meadow camp."),
}
FLAGS = [("meadow_arrived", "Chapter 5: entered the Meadow Maze."),
         ("teana_meadow_won", "Teana beaten in the friendly duel: helper unlocked."),
         ("meadow_mage_won", "Meadow Mage beaten: seventh star, end of chapter 5.")]
STAGES = [(22, "Chapter 5: the maze, Teana in the hedges"),
          (23, "Chapter 5: Teana helps; the Meadow Mage at the centre"),
          (24, "Chapter 5 complete: the desert road is the next part")]
ANCHORS = {"kingdom_meadow": {
 "spawn": "Path in from the mountain (bottom left).",
 "meadow_camp": "A tarp among flowers (bottom left).",
 "teana_spot": "A clearing in the hedges where Teana waits.",
 "shop_stall": "Rose Rue's flower cart (top left).",
 "arena_door": "The rabbit-hole burrow (bottom right): the Rabbit Hole Ring.",
 "gate_spot": "The star stone at the maze centre.",
 "desert_gate": "The vine arch at the top: the desert road.",
 "maze_center": "Open grass near the star stone.",
 "hangout_a": "East hedge path.",
 "hangout_b": "West hedge path by the camp.",
}}
ITEMS = [("hint_charm", "Hint Charm", "Amuleto de Dica",
          "Teana's charm. She tips you through the maze and beyond.",
          "O amuleto da Teana. Ela te da dicas no labirinto e alem.",
          "Teana, in the Meadow Maze")]

def W(**k): return k
NPCS = [
 dict(id="teana_meadow", area="kingdom_meadow", anchor="teana_spot", duelist_id=20, stages=[22, 99], visible="placed",
      note="Teana the stowaway: friendly duel, then helper tips.",
      rules=[W(when=W(stage=[22,22], flags_none=["teana_meadow_won"]), script="dk5_teana_pre", duel="teana_meadow"),
             W(when=W(stage=[23,99], needs=["teana_meadow_won"]), script="dk5_hint"),
             W(when=W(stage=[23,99]), script="dk5_teana_after")]),
 dict(id="meadow_mage", area="kingdom_meadow", anchor="gate_spot", duelist_id=29, stages=[23, 99], visible="placed",
      note="The zone master at the maze centre once Teana is helping.",
      rules=[W(when=W(stage=[23,23], flags_none=["meadow_mage_won"]), script="dk5_mage_pre", duel="meadow_mage"),
             W(when=W(stage=[23,99]), script="dk5_mage_after")]),
 dict(id="rose_rue", area="kingdom_meadow", anchor="shop_stall", duelist_id=None, stages=[22, 99], visible="always",
      rules=[W(when=W(stage=[22,99]), script="dk5_rose_rue")]),
]
NPC_SPEAKER = {"teana_meadow": "teana"}
def B(en, pt): return {"en": en, "pt": pt}
OBJECTS = [
 dict(id="star_stone", name=B("Star stone", "Pedra da estrela"), area="kingdom_meadow", anchor="gate_spot", rules=[
  W(when=W(stage=[22,22]), script="dk5_centre_early")]),
 dict(id="desert_gate", name=B("Desert arch", "Arco do deserto"), area="kingdom_meadow", anchor="desert_gate", rules=[
  W(when=W(stage=[24,99], stars=7), script="dk5_desert_road"), W(when=W(stage=[22,99]), script="dk5_gate_shut")]),
 dict(id="meadow_camp", name=B("Meadow camp", "Acampamento da campina"), area="kingdom_meadow", anchor="meadow_camp", rules=[
  W(when=W(stage=[22,99]), script="dk5_meadow_camp")]),
 dict(id="meadow_exit", name=B("Summit trail", "Trilha do cume"), area="kingdom_meadow", anchor="spawn", rules=[]),
]
DUELS = [
 dict(id="teana_meadow", npc="teana_meadow", duelist_id=20, deck="Teana Maze", tier=4, pre="dk5_teana_pre", win="dk5_teana_win", lose="dk5_teana_lose", win_flag="teana_meadow_won",
      on_win=[W(give_item="hint_charm"), W(set_stage=23)],
      note="Friendly duel, no star: Teana becomes a helper with maze tips."),
 dict(id="meadow_mage", npc="meadow_mage", duelist_id=29, deck="Meadow Mage Grove", tier=5, pre="dk5_mage_pre", win="dk5_mage_win", lose="dk5_mage_lose", win_flag="meadow_mage_won",
      on_win=[W(give_card="Queen of Autumn Leaves"), W(set_stage=24)], stars=2,
      note="Zone master, holds 2 stars: bet 1 for the curve (6->7). Needs meadow cards or Rabbit Hole Ring wins."),
]
TRANSITIONS = [
 dict(id="enter_meadow", when=W(stage=[21,21], stars=6), trigger=W(kind="interact", object="summit_gate"), effects=[W(set_stage=22), W(teleport=W(area="kingdom_meadow", anchor="spawn"))], script="dk5_enter"),
 dict(id="to_meadow", when=W(stage=[22,99]), trigger=W(kind="interact", object="summit_gate"), effects=[W(teleport=W(area="kingdom_meadow", anchor="spawn"))], script="dk5_to_meadow"),
 dict(id="to_mountain_from_meadow", when=W(stage=[22,99]), trigger=W(kind="interact", object="meadow_exit"), effects=[W(teleport=W(area="kingdom_mountain", anchor="summit_gate"))], script="dk5_to_mountain"),
 dict(id="meadow_arrival", when=W(stage=[22,22], flags_none=["meadow_arrived"]), trigger=W(kind="when_true", area="kingdom_meadow"), effects=[W(set_flag="meadow_arrived")], script="dk5_arrival"),
]
HUD = [
 (W(stage=[22,22]), "Find Teana in the hedges - the giggle from the ship", "Ache a Teana nas cercas - a risada do navio"),
 (W(stage=[23,23]), "Beat the Meadow Mage - a star on the line", "Venca a Maga da Campina - uma estrela em jogo"),
 (W(stage=[24,99]), "Chapter 5 complete - the desert road waits", "Capitulo 5 completo - a estrada do deserto espera"),
]
CHAPTER = dict(n=5, title=B("The Meadow Maze", "O Labirinto da Campina"), region="kingdom_meadow", stage=[22,24],
               reward="seven stars, Hint Charm, card Queen of Autumn Leaves", unlock="the desert road (chapter 6)")
QUESTS = [
 dict(id="q14_meadow", kind="talk+duel", opt=False, title=B("The Meadow Maze", "O Labirinto da Campina"), giver="(none)",
      steps=[("Find Teana in the hedges", "Ache a Teana nas cercas", "kingdom_meadow.teana_spot"),
             ("Beat the Meadow Mage for a star", "Venca a Maga da Campina por uma estrela", "kingdom_meadow.gate_spot")],
      reward="seven stars, Hint Charm, card Queen of Autumn Leaves"),
]
DECKS = {
 "Teana Maze": dict(duelist="Teana", tier=4, theme="Teana's cakes, plants and light fairies", notes="Chapter 5 friendly duel (no star).", cards={
   "Mystical Elf": 2, "Happy Lover": 2, "Rainbow Flower": 3, "Firegrass": 3, "Arlownay": 2, "Abyss Flower": 2, "Dark Plant": 3, "Man Eater": 2, "Yashinoki": 2, "Pot the Trick": 2, "Curtain of the Dark Ones": 2, "Haniwa": 2, "Key Mace": 2, "Laughing Flower": 3, "Forest": 3, "Sparks": 2, "Red Medicine": 3}),
 "Meadow Mage Grove": dict(duelist="Meadow Mage", tier=5, theme="Plants, beasts and the Forest field", notes="Chapter 5 zone master (holds 2).", cards={
   "Queen of Autumn Leaves": 2, "Flower Wolf": 2, "Dark Witch": 1, "Garvas": 2, "Gemini Elf": 2, "Orion the Battle King": 1, "Spirit of the Harp": 2, "Prevent Rat": 2, "Bean Soldier": 2, "Tentacle Plant": 3, "Man-eating Plant": 2, "Firegrass": 3, "Yashinoki": 3, "Forest": 3, "Sparks": 2, "Red Medicine": 2, "Invigoration": 2, "Haniwa": 2, "Happy Lover": 2}),
}
