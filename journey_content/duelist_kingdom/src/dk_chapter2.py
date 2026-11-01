# -*- coding: utf-8 -*-
"""Chapter 2 - The Shore of Illusions (kingdom_beach), the first Kingdom area, plus the keepers of the
harbor, the ship and the beach.  Pages follow the same rules as dk_scripts.py (ASCII, 3 x 32).
Imported at the end of dk_scripts.py (scripts) and dk_data.py (structure)."""

def scripts(sc, H, X, N):
    sc("dk2_landing", "Chapter 2 opens: the hero steps off the gangway onto the Shore of Illusions.", [
     N("Shore of Illusions", "Costa das Ilusoes", "Sand, tents and a painted sign - Welcome, bugs and champions.",
       "Areia, tendas e uma placa pintada - Bem-vindos, insetos e campeoes."),
     X("mai", "Off you go, sweetie. Keep that star warm. See you at the castle.",
       "Vai la, queridinho. Cuide dessa estrela. Te vejo no castelo."),
     H("A giant mirror in the middle of the beach? That is not normal.",
       "Um espelho gigante no meio da praia? Isso nao e normal."),
     N("Objective", "Objetivo", "Look into the mirror on the beach.", "Olhe o espelho da praia."),
    ], chapter=2)
    sc("dk2_mirror", "Pegasus's recorded welcome in the beach mirror. Sets the star rules.", [
     N("Mirror", "Espelho", "The glass ripples. A man in red with silver hair smiles out of it.",
       "O vidro ondula. Um homem de vermelho e cabelo prateado sorri."),
     X("pegasus", "Welcome, duelists, to my little Kingdom! This is only a recording.",
       "Bem-vindos, duelistas, ao meu pequeno Reino! Isto e so uma gravacao."),
     X("pegasus", "Every duelist carries stars. Before a duel you both wager. The winner takes the pot.",
       "Todo duelista leva estrelas. Antes do duelo os dois apostam. Quem vence leva tudo."),
     X("pegasus", "Ten stars open my castle gate. Zero stars... nobody likes zero.",
       "Dez estrelas abrem o portao do castelo. Zero estrelas... ninguem gosta."),
     X("pegasus", "Lose your last one and you are out of my Kingdom. Game over. No refunds.",
       "Perca a ultima e voce esta fora do meu Reino. Game over. Sem reembolso."),
     X("pegasus", "Now go and play! I will be watching. I am always watching.",
       "Agora vao jogar! Estarei olhando. Estou sempre olhando."),
     H("Always watching? Creepy. One star. Let's find a duel.",
       "Sempre olhando? Que medo. Uma estrela. Vamos achar um duelo."),
    ], chapter=2)
    sc("dk2_mirror_after", "The mirror after the recording.", [
     N("Mirror", "Espelho", "Only your own face now, and a faint smell of strawberry jam.",
       "So o seu rosto agora, e um leve cheiro de geleia de morango."),
    ], chapter=2)
    sc("dk2_weevil_ambush", "Weevil jumps out from behind a palm with his loaded dice.", [
     X("weevil", "Hihihi! A rookie with one shiny little star. How lucky for me.",
       "Hihihi! Um novato com uma estrelinha brilhante. Que sorte a minha."),
     H("Who are you? And why were you hiding behind a palm tree?",
       "Quem e voce? E por que estava atras de uma palmeira?"),
     X("weevil", "Weevil Underwood, champion of bugs! Let's roll to see who starts.",
       "Weevil Underwood, campeao dos insetos! Vamos rolar quem comeca."),
     N("Dice", "Dados", "Weevil rolls. Six. He rolls again. Six. And again. Six.",
       "Weevil rola. Seis. Rola de novo. Seis. E de novo. Seis."),
     H("Those dice are loaded! Every face is a six!", "Esses dados sao viciados! Toda face e seis!"),
     X("weevil", "Prove it. Duel me for your star, or walk away and cry.",
       "Prove. Duele pela sua estrela, ou va embora chorando."),
     N("Objective", "Objetivo", "Beat Weevil on the beach. Each of you wagers a star.",
       "Venca o Weevil na praia. Cada um aposta uma estrela."),
    ], chapter=2)
    sc("dk2_weevil_pre", "Weevil's star duel (first wager of the Kingdom).", [
     X("weevil", "I hold two stars. Bet what you dare. Winner takes it. Loser cries. Hihihi!",
       "Tenho duas estrelas. Aposte o que tiver coragem. Quem perder chora. Hihihi!"),
     X("weevil", "Well? My bugs are hungry. Duel?", "E entao? Meus insetos estao com fome. Duelar?", True),
    ], chapter=2)
    sc("dk2_weevil_win", "Weevil beaten: the hero's second star and the end of chapter 2.", [
     X("weevil", "Impossible! My bugs! My dice! My beautiful plan!",
       "Impossivel! Meus insetos! Meus dados! Meu lindo plano!"),
     X("weevil", "Take your star. And these dice. They never liked me anyway.",
       "Leve sua estrela. E estes dados. Eles nunca gostaram de mim."),
     N("Reward", "Recompensa", "You got a star, the Loaded Dice and the card Hercules Beetle.",
       "Voce ganhou uma estrela, os Dados Viciados e a carta Hercules Beetle."),
     H("Two stars. Eight to go. Note to self - bring my own dice.",
       "Duas estrelas. Faltam oito. Lembrete - trazer meus dados."),
     N("End of Chapter 2", "Fim do Capitulo 2", "Next - the Forest of Whispers, up the jungle path.",
       "A seguir - a Floresta dos Sussurros, pela trilha da selva."),
    ], chapter=2)
    sc("dk2_weevil_lose", "Weevil wins the wager.", [
     X("weevil", "Hihihi! Your star is mine. Bugs always win in the end.",
       "Hihihi! Sua estrela e minha. Insetos sempre vencem no fim."),
     H("I'll get stronger. New cards, then a rematch. No loaded dice.",
       "Vou ficar mais forte. Cartas novas, depois revanche. Sem dados viciados."),
    ], chapter=2)
    sc("dk2_weevil_after", "Weevil after losing.", [
     X("weevil", "Go away. The dice and I are not speaking.", "Va embora. Eu e os dados nao estamos nos falando."),
    ], chapter=2)
    sc("dk_wager_rematch", "A beaten star duelist still holds stars he won from the hero: a rematch wager to win them back.", [
     H("You still hold the stars you took from me. I want them back. Duel?",
       "Voce ainda tem as estrelas que tirou de mim. Quero de volta. Duelar?", True),
    ], chapter=2)
    sc("dk2_camp", "The Shore Camp sign: the safety net, first visit.", [
     N("Shore Camp", "Acampamento da Costa", "Cots, a fire and a sign - Lost your stars? Rest here.",
       "Catres, uma fogueira e uma placa - Perdeu suas estrelas? Descanse."),
     N("Shore Camp", "Acampamento da Costa", "Fine print - Zero stars means the end of your journey. No star is ever given back.",
       "Letras miudas - Zero estrelas e o fim da jornada. Nenhuma estrela e devolvida."),
     H("No safety net. Then I never bet my last star.",
       "Sem rede de seguranca. Entao nunca aposto a minha ultima."),
    ], chapter=2)
    sc("dk2_camp_after", "Shore Camp, later visits.", [
     N("Shore Camp", "Acampamento da Costa", "The fire crackles. A few eliminated duelists snore.",
       "A fogueira estala. Alguns duelistas eliminados roncam."),
    ], chapter=2)
    sc("dk2_hooded_shore", "The hooded man (Shadi) at the end of the beach pier: one line, then gone.", [
     X("hooded_man", "The Kingdom tests more than decks. Watch who collects the stars.",
       "O Reino testa mais que baralhos. Observe quem junta as estrelas."),
     N("Pier", "Cais", "A gust of sand. The end of the pier is empty again.",
       "Uma rajada de areia. O fim do cais esta vazio de novo."),
    ], chapter=2)
    sc("dk2_jungle_early", "The jungle path before Weevil.", [
     N("Jungle Path", "Trilha da Selva", "A sign - Forest of Whispers. Duelists with two stars only.",
       "Uma placa - Floresta dos Sussurros. So duelistas com duas estrelas."),
    ], chapter=2)
    # the stall keepers of the new places: a greeting, then the stall opens (the economy converter adds open_shop)
    sc("dk2_dock_dan", "Dock Dan, the harbor cart.", [
     X("dock_dan", "Fresh off the boat! Cards, cheap. Well, cheap-ish.",
       "Fresquinho do barco! Cartas baratas. Bom, quase baratas."),
    ], chapter=2)
    sc("dk2_purser", "Purser Pim, the ship's stall.", [
     X("purser", "Snacks, cards and seasick pills. Only the cards work.",
       "Lanches, cartas e remedio pra enjoo. So as cartas funcionam."),
    ], chapter=2)
    sc("dk2_shell_sue", "Shell Sue, the beach tent.", [
     X("shell_sue", "Shells, cards and secrets. Buy something, star boy.",
       "Conchas, cartas e segredos. Compre algo, menino estrela."),
    ], chapter=2)

SPEAKERS = {
 "pegasus": ("Pegasus", "Pegasus", "Pegasus", 15, "A recording in the beach mirror (chapter 2)."),
 "weevil": ("Weevil", "Weevil", "Weevil", 10, "Weevil Underwood, the bug champion with loaded dice."),
 "staff": ("Kingdom Staff", "Staff do Reino", "Staff", 254, "Pegasus's camp staff (voice only)."),
 "dock_dan": ("Dock Dan", "Dan do Cais", "Dan", 254, "Harbor stall keeper (economy)."),
 "purser": ("Purser Pim", "Comissario Pim", "Pim", 254, "Ship stall keeper (economy)."),
 "shell_sue": ("Shell Sue", "Sue Concha", "Sue", 254, "Beach tent keeper (economy)."),
}
FLAGS = [("beach_arrived", "Chapter 2: landed on the Shore of Illusions."), ("pegasus_mirror", "Heard Pegasus's recorded welcome."),
         ("weevil_met", "Weevil's ambush on the beach."), ("weevil_won", "Weevil beaten: second star, end of chapter 2."),
         ("camp_met", "Optional: read the Shore Camp sign."), ("hooded_shore", "Optional: the hooded man's line on the beach pier.")]
STAGES = [(11, "Chapter 2: the mirror heard, Weevil waits"), (12, "Chapter 2 complete: the forest path is the next part")]
ANCHORS = {"kingdom_beach": {"spawn": "Top of the landing pier (bottom left).", "mirror_spot": "In front of the standing mirror (top centre).",
                             "weevil_spot": "Sand left of centre, by the palms.", "shore_camp": "By the campfire among the tents (right).",
                             "shop_stall": "Shell Sue's striped stall.", "arena_door": "The sea cave in the cliff (top left): the Wreck Pit.",
                             "pier_far": "Far end of the landing pier (the hooded man).", "jungle_path": "Path into the jungle (top right)."},
           "harbor_extra": {"shop_stall": "Dock Dan's cart on the boardwalk.", "arena_door": "Warehouse door (top left): the Net Loft Pit."},
           "ship_extra": {"shop_stall": "Purser Pim's stall on deck.", "arena_door": "Cargo hatch: the Bilge Ring below deck."}}
ITEMS = [("loaded_dice", "Loaded Dice", "Dados Viciados", "Weevil's dice. Every face is a six.", "Os dados do Weevil. Toda face e seis.", "Weevil")]

def W(**k): return k
NPCS = [
 dict(id="weevil", area="kingdom_beach", anchor="weevil_spot", duelist_id=10, stages=[11, 99], visible="placed",
      note="Appears after the mirror; his ambush scene plays by itself the first time.",
      rules=[
  W(when=W(stage=[11,11], flags_all=["weevil_met"], flags_none=["weevil_won"]), script="dk2_weevil_pre", duel="weevil"),
  W(when=W(stage=[11,99]), script="dk2_weevil_after")]),
 dict(id="hooded_shore", area="kingdom_beach", anchor="pier_far", duelist_id=None, stages=[11, 99], visible="placed",
      note="Shadi in his hood, one line; gone once heard.",
      rules=[W(when=W(stage=[11,99], flags_none=["hooded_shore"]), script="dk2_hooded_shore", effects=[W(set_flag="hooded_shore")])]),
 dict(id="dock_dan", area="harbor", anchor="shop_stall", duelist_id=None, stages=[5, 99], visible="always", rules=[W(when=W(stage=[5,99]), script="dk2_dock_dan")]),
 dict(id="purser", area="ship_deck", anchor="shop_stall", duelist_id=None, stages=[7, 7], visible="always", rules=[W(when=W(stage=[7,7]), script="dk2_purser")]),
 dict(id="shell_sue", area="kingdom_beach", anchor="shop_stall", duelist_id=None, stages=[10, 99], visible="always", rules=[W(when=W(stage=[10,99]), script="dk2_shell_sue")]),
]
NPC_SPEAKER = {"hooded_shore": "hooded_man"}
def B(en, pt): return {"en": en, "pt": pt}
OBJECTS = [
 dict(id="pegasus_mirror", name=B("Standing mirror", "Espelho de pe"), area="kingdom_beach", anchor="mirror_spot", rules=[
  W(when=W(stage=[10,10], flags_none=["pegasus_mirror"]), script="dk2_mirror", effects=[W(set_flag="pegasus_mirror"), W(set_stage=11)]),
  W(when=W(stage=[10,99]), script="dk2_mirror_after")]),
 dict(id="shore_camp", name=B("Shore Camp", "Acampamento da Costa"), area="kingdom_beach", anchor="shore_camp", rules=[
  W(when=W(stage=[10,99], flags_none=["camp_met"]), script="dk2_camp", effects=[W(set_flag="camp_met")]),
  W(when=W(stage=[10,99]), script="dk2_camp_after")]),
 dict(id="jungle_path", name=B("Jungle path", "Trilha da selva"), area="kingdom_beach", anchor="jungle_path", rules=[
  W(when=W(stage=[10,12]), script="dk2_jungle_early")]),
]
DUELS = [
 dict(id="weevil", npc="weevil", duelist_id=10, deck="Weevil Shore", tier=2, pre="dk2_weevil_pre", win="dk2_weevil_win", lose="dk2_weevil_lose", win_flag="weevil_won",
      on_win=[W(give_card="Hercules Beetle"), W(give_item="loaded_dice"), W(set_stage=12)], stars=2,
      note="Weevil holds 2 stars; the player bets 1..min(his, Weevil's). Losing the last star is a game over."),
]
TRANSITIONS = [
 dict(id="landing", when=W(stage=[10,10], flags_none=["beach_arrived"]), trigger=W(kind="when_true", area="kingdom_beach"), effects=[W(set_flag="beach_arrived")], script="dk2_landing"),
 dict(id="weevil_ambush", when=W(stage=[11,11], flags_none=["weevil_met"]), trigger=W(kind="when_true", area="kingdom_beach"), effects=[W(set_flag="weevil_met")], script="dk2_weevil_ambush"),
]
HUD = [
 (W(stage=[10,10]), "Look into the mirror on the beach", "Olhe o espelho da praia"),
 (W(stage=[11,11]), "Beat Weevil - each of you wagers a star", "Venca o Weevil - cada um aposta uma estrela"),
 (W(stage=[12,12]), "Chapter 2 complete - the forest waits", "Capitulo 2 completo - a floresta espera"),
]
CHAPTER = dict(n=2, title=B("The Shore of Illusions", "A Costa das Ilusoes"), region="kingdom_beach", stage=[10,12], reward="a second star, Loaded Dice, card Hercules Beetle", unlock="Forest of Whispers (chapter 3)")
QUESTS = [
 dict(id="q11_shore", kind="talk+duel", opt=False, title=B("The Shore of Illusions", "A Costa das Ilusoes"), giver="pegasus",
      steps=[("Look into the mirror on the beach", "Olhe o espelho da praia", "kingdom_beach.mirror_spot"),
             ("Beat Weevil for a star", "Venca o Weevil por uma estrela", "kingdom_beach.weevil_spot")],
      reward="a second star, Loaded Dice, card Hercules Beetle"),
 dict(id="s05_camp", kind="investigate", opt=True, title=B("The Safety Net", "A Rede de Seguranca"), giver="(none)",
      steps=[("Read the Shore Camp sign", "Leia a placa do Acampamento", "kingdom_beach.shore_camp")], reward="you know where you wake up"),
 dict(id="s06_hooded", kind="talk", opt=True, title=B("Sand on the Pier", "Areia no Cais"), giver="hooded_man",
      steps=[("Talk to the hooded figure on the pier", "Fale com o vulto de capuz no cais", "kingdom_beach.pier_far")], reward="a warning"),
]
DECKS = {
 "Weevil Shore": dict(duelist="Weevil Underwood", tier=2, theme="Weevil on the beach: weak bugs and armour, loaded dice", notes="Chapter 2 star duel: beatable with a few upgrades.", cards={
   "Basic Insect": 3, "Killer Needle": 3, "Petit Moth": 3, "Larvae Moth": 2, "Big Insect": 2, "Hercules Beetle": 1, "Gokibore": 3, "Giant Flea": 2,
   "Needle Worm": 2, "Cockroach Knight": 2, "Man-eater Bug": 2, "Insect Armor with Laser Cannon": 2, "Forest": 3, "Sparks": 3, "Red Medicine": 2,
   "Laser Cannon Armor": 2, "Vile Germs": 3}),
}
# the starter deck of a new journey: forty weak, legal cards (see README "Difficulty curve")
STARTER_DECK = {"Hitotsu-me Giant": 3, "Torike": 2, "Beaver Warrior": 2, "Silver Fang": 2, "Wolf": 2, "Zombie Warrior": 2, "Dark Gray": 2,
                "Mushroom Man": 3, "Petit Dragon": 3, "Petit Angel": 2, "Winged Cleaver": 2, "Kurama": 2, "Hinotama Soul": 2, "Basic Insect": 2,
                "Red Medicine": 3, "Sparks": 3, "Forest": 2, "Hinotama": 1}
