# -*- coding: utf-8 -*-
"""Chapter 9 - The Castle Hall (castle_hall): illusion halls after the Gate Key.
Chamberlain Heishin harvests lost stars for a Star Crown. Beat him; MAGO.DEV glimpse 7
in a hall mirror. Relic Rhea's alcove, Crown Cellar arena (3 exclusives), no gang.
ASCII 3x32. Stages 33-34. Flags: heishin_won (kflags2)."""

def scripts(sc, H, X, N):
    sc("dk9_enter", "Chapter 8 -> 9: the Gate Key opens the castle hall.", [
     N("Castle Hall", "Salao do Castelo", "Ten stars. Illusion stairs. Portraits wink. A crown hums ahead.",
       "Dez estrelas. Escadas de ilusao. Retratos piscando. Uma coroa zumbe a frente."),
     H("Heishin's harvest. The fair cellar makes sense now.",
       "A colheita do Heishin. O porao da feira faz sentido agora."),
    ], chapter=9)
    sc("dk9_to_hall", "Return to the hall.", [
     N("Castle Hall", "Salao", "Mirrors bend. The crown still waits, or the stairs up do.",
       "Espelhos curvam. A coroa ainda espera, ou as escadas pra cima."),
    ], chapter=9)
    sc("dk9_to_gate", "Back to the Castle Gate plaza.", [
     N("Gate Road", "Estrada do Portao", "Stone and beetle banners again. The plaza is behind.",
       "Pedra e bandeiras de besouro de novo. A praca fica atras."),
    ], chapter=9)
    sc("dk9_arrival", "Chapter 9 opens: Heishin at the Star Crown.", [
     N("Illusion Hall", "Salao", "Stairs that lead nowhere twice. A pedestal holds a crown of stolen stars.",
       "Escadas que nao levam a lugar nenhum duas vezes. Um pedestal segura uma coroa de estrelas roubadas."),
     X("heishin", "Chamberlain Heishin. The eliminated left their light with me. I will rule the island with it.",
       "Camareiro Heishin. Os eliminados deixaram a luz comigo. Vou governar a ilha com ela."),
     H("You herded them. From the fair. From every road.",
       "Voce os enfiou. Da feira. De cada estrada."),
     N("Objective", "Objetivo", "Challenge Heishin at the Star Crown.",
       "Desafie Heishin na Coroa Estelar."),
    ], chapter=9)
    sc("dk9_heishin_pre", "Heishin the chamberlain: star wager, twist villain.", [
     X("heishin", "Two stars under this crown. Wager what you dare. The Dream Room is upstairs - if you live.",
       "Duas estrelas sob esta coroa. Aposte o que ousar. A Sala dos Sonhos e la em cima - se viver."),
     H("I did not collect ten to kneel to a thief.",
       "Nao juntei dez pra ajoelhar pra um ladrao."),
     X("heishin", "Then the hall speaks. Shall we?",
       "Entao o salao fala. Vamos?", ask=True),
    ], chapter=9)
    sc("dk9_heishin_win", "Heishin loses: stars freed, MAGO glimpse 7, end of chapter 9.", [
     X("heishin", "The crown cracks. The lights fly home. No... my island...",
       "A coroa racha. As luzes voam pra casa. Nao... minha ilha..."),
     N("Hall", "Salao", "Eliminated duelists flicker free and bow, then vanish toward the shore.",
       "Duelistas eliminados piscam livres e se curvam, depois somem rumo a costa."),
     N("Mirror", "Espelho", "In a hall mirror, behind your reflection, a green shimmer watches and does not delete him.",
       "Num espelho do salao, atras do seu reflexo, um brilho verde observa e nao o apaga."),
     X("mago_hidden", "I could end this line. I will not. Play.",
       "Eu poderia acabar com esta linha. Nao vou. Jogue."),
     H("Who... was that? The stairs up are open. Pegasus waits.",
       "Quem... foi aquilo? As escadas sobem. Pegasus espera."),
     N("You got", "Voce ganhou", "Card Soul Hunter. The Dream Room stairs unlock.",
       "A carta Soul Hunter. As escadas da Sala dos Sonhos abrem."),
     N("End of Chapter 9", "Fim do Capitulo 9", "The Castle Hall yields. Pegasus's Dream is next.",
       "O Salao do Castelo cede. O Sonho de Pegasus e o proximo."),
    ], chapter=9)
    sc("dk9_heishin_lose", "Heishin keeps the crown.", [
     X("heishin", "The crown drinks. Crawl to Relic Rhea or the Crown Cellar, then return.",
       "A coroa bebe. Rasteje ate Rhea ou o Porao da Coroa, depois volte."),
     H("He outplayed me. Cards, then rematch.",
       "Ele me passou. Cartas, depois a revanche."),
    ], chapter=9)
    sc("dk9_heishin_after", "Heishin after defeat.", [
     X("heishin", "Pegasus knew. He always knew. Go upstairs and ask him why.",
       "Pegasus sabia. Sempre soube. Suba e pergunte por que."),
    ], chapter=9)
    sc("dk9_relic_rhea", "Relic Rhea, Relic Alcove.", [
     X("relic_rhea", "Crowns crack. Cards last. Buy what the hall drops.",
       "Coroas racham. Cartas duram. Compre o que o salao deixa."),
    ], chapter=9)
    sc("dk9_hall_camp", "Hall camp game-over warning.", [
     N("Hall Camp", "Acampamento", "A tarp by the entrance pillars. Staff keep one lantern for the starless.",
       "Uma lona junto aos pilares. A equipe mantem um lampiao pros sem estrela."),
     X("staff", "Pretty hall. Deadly rules. Lose your last star and your journey ends for good.",
       "Salao bonito. Regras duras. Perdeu a ultima estrela e a jornada acaba de vez."),
    ], chapter=9)
    sc("dk9_dream_shut", "Dream stairs before Heishin falls.", [
     N("Dream Stairs", "Escadas do Sonho", "Stairs up to a bright door. The crown's hum still blocks the step.",
       "Escadas pra uma porta clara. O zumbido da coroa ainda bloqueia o degrau."),
    ], chapter=9)
    sc("dk9_dream_road", "Dream stairs after Heishin: chapter 10 next.", [
     N("Dream Stairs", "Escadas do Sonho", "The crown is quiet. Upstairs: Pegasus, a wish, and the end of the show.",
       "A coroa esta quieta. La em cima: Pegasus, um desejo e o fim do show."),
    ], chapter=9)

SPEAKERS = {
 "heishin": ("Heishin", "Heishin", "Heishin", 254, "Chamberlain; twist villain of the Castle Hall (chapter 9)."),
 "mago_hidden": ("???", "???", "???", 254, "MAGO.DEV glimpse 7 in the hall mirror."),
 "relic_rhea": ("Relic Rhea", "Rhea das Reliquias", "Rhea", 254, "Relic Alcove keeper (economy)."),
 "staff": ("Camp Staff", "Equipe do Acampamento", "Staff", 254, "Kingdom staff at the hall camp."),
}
FLAGS = [("heishin_won", "Heishin beaten in the Castle Hall: Star Crown breaks, Dream Room opens.")]
STAGES = [(33, "Chapter 9: Castle Hall, Heishin at the Star Crown"),
          (34, "Chapter 9 complete: Dream Room stairs open")]
ANCHORS = {"castle_hall": {
 "spawn": "Entrance from the gate (bottom).",
 "hall_camp": "Tarp by the entrance pillars.",
 "shop_stall": "Relic Rhea's Relic Alcove (west).",
 "arena_door": "Crown Cellar hatch (east).",
 "heishin_spot": "Star Crown pedestal (top center).",
 "dream_stairs": "Stairs up to the Dream Room.",
 "hall_center": "Open floor by the star mosaic.",
 "mirror_spot": "A tall hall mirror (MAGO glimpse).",
 "hangout_a": "East colonnade.",
 "hangout_b": "West colonnade.",
}}
ITEMS = []

def W(**k): return k
NPCS = [
 dict(id="heishin_hall", area="castle_hall", anchor="heishin_spot", duelist_id=35, stages=[33, 99], visible="placed",
      note="Chamberlain Heishin: holds 2, Star Crown twist.",
      rules=[W(when=W(stage=[33,33], flags_none=["heishin_won"]), script="dk9_heishin_pre", duel="heishin_hall"),
             W(when=W(stage=[34,99], flags_all=["heishin_won"]), script="dk9_heishin_after")]),
 dict(id="relic_rhea", area="castle_hall", anchor="shop_stall", duelist_id=None, stages=[33, 99], visible="always",
      rules=[W(when=W(stage=[33,99]), script="dk9_relic_rhea")]),
]
NPC_SPEAKER = {"heishin_hall": "heishin"}
def B(en, pt): return {"en": en, "pt": pt}
OBJECTS = [
 dict(id="dream_stairs", name=B("Dream stairs", "Escadas do sonho"), area="castle_hall", anchor="dream_stairs", rules=[
  W(when=W(stage=[34,99]), script="dk9_dream_road"), W(when=W(stage=[33,99]), script="dk9_dream_shut")]),
 dict(id="hall_camp", name=B("Hall camp", "Acampamento do salao"), area="castle_hall", anchor="hall_camp", rules=[
  W(when=W(stage=[33,99]), script="dk9_hall_camp")]),
 dict(id="hall_exit", name=B("Gate road", "Estrada do portao"), area="castle_hall", anchor="spawn", rules=[]),
]
DUELS = [
 dict(id="heishin_hall", npc="heishin_hall", duelist_id=35, deck="Heishin Crown", tier=8, pre="dk9_heishin_pre", win="dk9_heishin_win", lose="dk9_heishin_lose", win_flag="heishin_won",
      on_win=[W(give_card="Soul Hunter"), W(set_stage=34)], stars=2,
      note="Chamberlain holds 2; narrative frees stolen stars. Player stays at 10 on min win."),
]
TRANSITIONS = [
 dict(id="enter_hall", when=W(stage=[32,32], stars=10), trigger=W(kind="interact", object="castle_door"), effects=[W(set_stage=33), W(teleport=W(area="castle_hall", anchor="spawn"))], script="dk9_arrival"),
 dict(id="to_hall", when=W(stage=[33,99]), trigger=W(kind="interact", object="castle_door"), effects=[W(teleport=W(area="castle_hall", anchor="spawn"))], script="dk9_to_hall"),
 dict(id="to_gate_from_hall", when=W(stage=[33,99]), trigger=W(kind="interact", object="hall_exit"), effects=[W(teleport=W(area="castle_gate", anchor="castle_door"))], script="dk9_to_gate"),
]
HUD = [
 (W(stage=[33,33]), "Beat Heishin at the Star Crown - a star on the line", "Venca Heishin na Coroa Estelar - uma estrela em jogo"),
 (W(stage=[34,34]), "Chapter 9 complete - the Dream Room waits upstairs", "Capitulo 9 completo - a Sala dos Sonhos espera la em cima"),
]
CHAPTER = dict(n=9, title=B("The Castle Hall", "O Salao do Castelo"), region="castle_hall", stage=[33,34],
               reward="card Soul Hunter; Dream Room stairs", unlock="Pegasus's Dream (chapter 10)")
QUESTS = [
 dict(id="q18_hall", kind="duel", opt=False, title=B("The Castle Hall", "O Salao do Castelo"), giver="(none)",
      steps=[("Beat Heishin at the Star Crown", "Venca Heishin na Coroa Estelar", "castle_hall.heishin_spot")],
      reward="card Soul Hunter; Dream Room open"),
]
DECKS = {
 "Heishin Crown": dict(duelist="Heishin", tier=8, theme="Dark ritual crown: stolen light and illusion beaters", notes="Chapter 9 chamberlain (holds 2).", cards={
   "Soul Hunter": 1, "King of Yamimakai": 1, "Dragon Seeker": 1, "Dark Magician": 1, "Illusionist Faceless Mage": 2,
   "Curtain of the Dark Ones": 2, "Saggi the Dark Clown": 2, "Mystic Clown": 2, "Dark Chimera": 2,
   "Yami": 3, "Dark Energy": 3, "Sparks": 2, "Hinotama": 2, "Red Medicine": 2, "Mooyan Curry": 2,
   "Swordstalker": 2, "Ansatsu": 2}),
}
