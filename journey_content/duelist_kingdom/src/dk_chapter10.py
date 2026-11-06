# -*- coding: utf-8 -*-
"""Chapter 10 - Pegasus's Dream (castle_top): final duel and festival wish.
Pegasus plays with hidden-hand flavor. Canon wish: Festival. Epilogue on the
village plaza (Simon still owes a card; MAGO.DEV finally noticed). Stages 35-37.
Flags: pegasus_won, wish_festival (kflags2)."""

def scripts(sc, H, X, N):
    sc("dk10_enter", "Chapter 9 -> 10: stairs into the Dream Room.", [
     N("Dream Room", "Sala dos Sonhos", "Cards pinned like butterflies. A window to the sea. Pegasus smiles.",
       "Cartas pregadas como borboletas. Uma janela pro mar. Pegasus sorri."),
     H("Ten stars. One show left.",
       "Dez estrelas. Um show sobrando."),
    ], chapter=10)
    sc("dk10_to_dream", "Return to the Dream Room.", [
     N("Dream Room", "Sala dos Sonhos", "The sea window still burns orange. The table waits.",
       "A janela do mar ainda queima laranja. A mesa espera."),
    ], chapter=10)
    sc("dk10_to_hall", "Back down to the Castle Hall.", [
     N("Hall Stairs", "Escadas do Salao", "Illusion halls below. The crown pedestal is quiet.",
       "Salas de ilusao abaixo. O pedestal da coroa esta quieto."),
    ], chapter=10)
    sc("dk10_arrival", "Chapter 10 opens: Pegasus, Shadi cameo, the wish table.", [
     N("Dream Room", "Sala", "A dueling table. Three wish orbs. Shadi stands by a pillar and nods once.",
       "Uma mesa de duelo. Tres orbes de desejo. Shadi fica junto a um pilar e acena uma vez."),
     X("shadi", "You kept your stars. He is waiting. I am only the messenger - still.",
       "Voce guardou suas estrelas. Ele espera. Eu ainda sou so o mensageiro."),
     X("pegasus", "Darling! Ten stars, a cracked crown, and a rookie who ruins my chamberlain's hobby.",
       "Querido! Dez estrelas, uma coroa rachada e um novato que estraga o hobby do meu camareiro."),
     H("You knew about Heishin.",
       "Voce sabia do Heishin."),
     X("pegasus", "I wanted to see if anyone would stop him. You did. Now - a real duel. A wish if you win.",
       "Eu queria ver se alguem o parava. Voce parou. Agora - um duelo de verdade. Um desejo se vencer."),
     N("Objective", "Objetivo", "Duel Pegasus at the dream table.",
       "Duele com Pegasus na mesa dos sonhos."),
    ], chapter=10)
    sc("dk10_shadi", "Shadi's last cameo line in the Dream Room.", [
     X("shadi", "I deliver ends. Yours is a kind one, if you win.",
       "Eu entrego finais. O seu e gentil, se voce vencer."),
    ], chapter=10)
    sc("dk10_pegasus_pre", "Pegasus final duel: hidden-hand flavor, holds 2.", [
     X("pegasus", "I play with a hidden hand, darling. Two stars on the table. Wager what your nerve allows.",
       "Eu jogo com a mao escondida, querido. Duas estrelas na mesa. Aposte o que sua coragem deixar."),
     H("For everyone he hurt. For the wish.",
       "Por todos que ele machucou. Pelo desejo."),
     X("pegasus", "Then smile for the window. Shall the dream speak?",
       "Entao sorria pra janela. O sonho pode falar?", ask=True),
    ], chapter=10)
    sc("dk10_pegasus_win", "Pegasus loses: wish choice opens.", [
     X("pegasus", "Marvelous! The eye saw it, and still lost. Choose, hero: a Dream Card, everyone's stars back, or a Festival for all.",
       "Maravilhoso! O olho viu e mesmo assim perdeu. Escolha, heroi: uma Carta dos Sonhos, as estrelas de todos de volta, ou um Festival pra todos."),
     H("A festival. Everyone goes home happy - and parties first.",
       "Um festival. Todo mundo volta feliz - e festeja antes."),
     X("pegasus", "Canon, darling. A Festival it is. Meet me in your little village.",
       "Canonico, querido. Festival sera. Me encontre na sua vilazinha."),
     N("You got", "Voce ganhou", "Card Dark Magician. The Festival wish is set.",
       "A carta Dark Magician. O desejo do Festival esta feito."),
     N("End of Chapter 10", "Fim do Capitulo 10", "Pegasus's Dream yields. The Festival epilogue waits in the village.",
       "O Sonho de Pegasus cede. O epilogo do Festival espera na vila."),
    ], chapter=10)
    sc("dk10_pegasus_lose", "Pegasus keeps the table.", [
     X("pegasus", "Almost a finale. Relic Rhea downstairs, or try again when your deck smiles.",
       "Quase um finale. Rhea la embaixo, ou tente de novo quando seu baralho sorrir."),
     H("He read my hand. Rematch.",
       "Ele leu minha mao. Revanche."),
    ], chapter=10)
    sc("dk10_pegasus_after", "Pegasus after the win, before epilogue warp.", [
     X("pegasus", "Go home. I already sent the invitations. Fashionably late is still late.",
       "Va pra casa. Ja mandei os convites. Atrasado com estilo ainda e atrasado."),
    ], chapter=10)
    sc("dk10_wish_orb", "Wish pedestal reminder after Pegasus.", [
     N("Wish Orbs", "Orbes", "Festival burns brightest. The village plaza is calling.",
       "O Festival queima mais forte. A praca da vila chama."),
    ], chapter=10)
    sc("dk10_epilogue", "Festival epilogue on the village plaza.", [
     N("Festival", "Festival", "Your home plaza is strung with star lanterns. Every rival you met waves from a stall.",
       "Sua praca esta cheia de lampioes de estrela. Cada rival que voce encontrou acena de uma barraca."),
     X("simon", "You still owe me a card. Do not think a festival clears the debt.",
       "Voce ainda me deve uma carta. Nao ache que um festival limpa a divida."),
     H("I will duel you for it. After cake.",
       "Vou duelar com voce por ela. Depois do bolo."),
     N("Bench", "Banco", "On the plaza bench, the green shimmer finally sits still. You notice him.",
       "No banco da praca, o brilho verde finalmente fica quieto. Voce o nota."),
     X("mago_hidden", "Took you long enough.",
       "Demorou, hein."),
     H("MAGO.DEV. You were in every chapter.",
       "MAGO.DEV. Voce estava em cada capitulo."),
     X("mago_hidden", "And now you see me. Good game.",
       "E agora voce me ve. Bom jogo."),
     X("pegasus", "Darlings! Drink, duel, dance! My Kingdom loved its rookies today.",
       "Queridos! Bebam, duelam, dancem! Meu Reino amou seus novatos hoje."),
     N("The End", "Fim", "Duelist Kingdom complete. The festival lasts as long as you walk the plaza.",
       "Reino dos Duelistas completo. O festival dura enquanto voce andar pela praca."),
    ], chapter=10)
    sc("dk10_dream_camp", "Dream Room camp warning.", [
     N("Dream Camp", "Acampamento", "A small tarp by the wish orbs. Even finales have rules.",
       "Uma lona pequena junto aos orbes. Ate finais tem regras."),
     X("staff", "Pretty room. Deadly rules. Lose your last star and your journey ends for good.",
       "Sala bonita. Regras duras. Perdeu a ultima estrela e a jornada acaba de vez."),
    ], chapter=10)

SPEAKERS = {
 "pegasus": ("Pegasus", "Pegasus", "Pegasus", 15, "Final boss of the Dream Room (chapter 10)."),
 "shadi": ("Shadi", "Shadi", "Shadi", 13, "Last cameo in the Dream Room."),
 "simon": ("Simon Muran", "Simon Muran", "Simon", 1, "Festival epilogue: you still owe him a card."),
 "mago_hidden": ("MAGO.DEV", "MAGO.DEV", "MAGO", 254, "Finally noticed on the plaza bench."),
 "staff": ("Camp Staff", "Equipe do Acampamento", "Staff", 254, "Dream Room camp."),
}
FLAGS = [("pegasus_won", "Pegasus beaten in the Dream Room: wish unlocked."),
         ("wish_festival", "Canon wish: Festival for everyone; epilogue on the village plaza.")]
STAGES = [(35, "Chapter 10: Dream Room, Pegasus at the table"),
          (36, "Chapter 10: Pegasus beaten; Festival wish set"),
          (37, "Epilogue: village festival; Kingdom complete")]
ANCHORS = {"castle_top": {
 "spawn": "Stairs in from the hall (bottom).",
 "dream_camp": "Tarp by the wish orbs.",
 "pegasus_spot": "Dueling table center.",
 "wish_orbs": "Three wish orbs on a pedestal.",
 "shadi_spot": "Pillar where Shadi waits.",
 "sea_window": "Great window to the sea.",
 "dream_center": "Open marble by the seal.",
 "hangout_a": "East colonnade.",
 "hangout_b": "West colonnade.",
}}
ITEMS = []

def W(**k): return k
NPCS = [
 dict(id="pegasus_dream", area="castle_top", anchor="pegasus_spot", duelist_id=15, stages=[35, 99], visible="placed",
      note="Pegasus final boss: holds 2.",
      rules=[W(when=W(stage=[35,35], flags_none=["pegasus_won"]), script="dk10_pegasus_pre", duel="pegasus_dream"),
             W(when=W(stage=[36,99], flags_all=["pegasus_won"]), script="dk10_pegasus_after")]),
 dict(id="shadi_dream", area="castle_top", anchor="shadi_spot", duelist_id=13, stages=[35, 35], visible="placed",
      rules=[W(when=W(stage=[35,35]), script="dk10_shadi")]),
]
NPC_SPEAKER = {"pegasus_dream": "pegasus", "shadi_dream": "shadi"}
def B(en, pt): return {"en": en, "pt": pt}
OBJECTS = [
 dict(id="wish_orbs", name=B("Wish orbs", "Orbes do desejo"), area="castle_top", anchor="wish_orbs", rules=[
  W(when=W(stage=[36,99]), script="dk10_wish_orb")]),
 dict(id="dream_camp", name=B("Dream camp", "Acampamento do sonho"), area="castle_top", anchor="dream_camp", rules=[
  W(when=W(stage=[35,99]), script="dk10_dream_camp")]),
 dict(id="dream_exit", name=B("Hall stairs", "Escadas do salao"), area="castle_top", anchor="spawn", rules=[]),
]
DUELS = [
 dict(id="pegasus_dream", npc="pegasus_dream", duelist_id=15, deck="Pegasus Dream", tier=9, pre="dk10_pegasus_pre", win="dk10_pegasus_win", lose="dk10_pegasus_lose", win_flag="pegasus_won",
      on_win=[W(give_card="Dark Magician"), W(set_flag="wish_festival"), W(set_stage=36)], stars=2,
      note="Final boss holds 2; canon Festival wish set on win."),
]
TRANSITIONS = [
 dict(id="enter_dream", when=W(stage=[34,34]), trigger=W(kind="interact", object="dream_stairs"), effects=[W(set_stage=35), W(teleport=W(area="castle_top", anchor="spawn"))], script="dk10_arrival"),
 dict(id="to_dream", when=W(stage=[35,99]), trigger=W(kind="interact", object="dream_stairs"), effects=[W(teleport=W(area="castle_top", anchor="spawn"))], script="dk10_to_dream"),
 dict(id="to_hall_from_dream", when=W(stage=[35,99]), trigger=W(kind="interact", object="dream_exit"), effects=[W(teleport=W(area="castle_hall", anchor="dream_stairs"))], script="dk10_to_hall"),
 dict(id="festival_epilogue", when=W(stage=[36,36], flags_all=["wish_festival"]), trigger=W(kind="interact", object="wish_orbs"),
      effects=[W(set_stage=37), W(teleport=W(area="village", anchor="plaza_center"))], script="dk10_epilogue"),
]
HUD = [
 (W(stage=[35,35]), "Duel Pegasus at the dream table - a star on the line", "Duele com Pegasus na mesa - uma estrela em jogo"),
 (W(stage=[36,36]), "Touch the wish orbs - Festival epilogue", "Toque nos orbes - epilogo do Festival"),
 (W(stage=[37,99]), "Kingdom complete - walk the festival plaza", "Reino completo - ande na praca do festival"),
]
CHAPTER = dict(n=10, title=B("Pegasus's Dream", "O Sonho de Pegasus"), region="castle_top", stage=[35,37],
               reward="card Dark Magician; Festival ending", unlock="epilogue festival in the village")
QUESTS = [
 dict(id="q19_dream", kind="duel", opt=False, title=B("Pegasus's Dream", "O Sonho de Pegasus"), giver="(none)",
      steps=[("Duel Pegasus in the Dream Room", "Duele com Pegasus na Sala dos Sonhos", "castle_top.pegasus_spot"),
             ("Choose the Festival wish", "Escolha o desejo do Festival", "castle_top.wish_orbs")],
      reward="card Dark Magician; Festival epilogue"),
]
DECKS = {
 "Pegasus Dream": dict(duelist="Pegasus", tier=9, theme="Toon-tinged control with hidden-hand flavor and Dark Magician", notes="Chapter 10 final boss (holds 2).", cards={
   "Dark Magician": 1, "Illusionist Faceless Mage": 2, "Mystic Clown": 2, "Saggi the Dark Clown": 2,
   "Curtain of the Dark Ones": 2, "Dragon Piper": 2, "Ryu-Kishin Powered": 2, "Dark Energy": 3, "Yami": 3,
   "Sparks": 2, "Hinotama": 2, "Red Medicine": 2, "Mooyan Curry": 2, "Stop Defense": 2,
   "Swordstalker": 2, "Ansatsu": 2, "Legendary Sword": 2}),
}
