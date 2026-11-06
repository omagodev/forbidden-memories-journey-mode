# -*- coding: utf-8 -*-
"""Chapter 7 - The Star Fair (kingdom_fair): straight on from the Desert of Lost Stars.  Midpoint hub.
Jono arrives soaked on his raft for a friendly rival duel (MAGO.DEV glimpse 6 in the crowd).  The Ring
Champion holds stars at the central ring (eight -> nine on the minimum bet).  InsetoKaiba lands and taunts
only.  Bazaar Bea's Grand Bazaar, the Underfair Big Top with three exclusives, a Jackal ambush and a fair
camp.  Same page rules as dk_scripts.py (ASCII, 3 x 32).
Imported at the end of dk_scripts.py (scripts) and dk_data.py (structure)."""

def scripts(sc, H, X, N):
    sc("dk7_enter", "Chapter 6 -> 7: the fair arch opens onto the Star Fair.", [
     N("Star Fair", "Feira das Estrelas", "Eight stars. Banners snap. Music and frying oil.",
       "Oito estrelas. Bandeiras estalam. Musica e oleo fritando."),
     H("A whole fair. After the dunes, this almost feels loud on purpose.",
       "Uma feira inteira. Depois das dunas, quase parece barulho de proposito."),
    ], chapter=7)
    sc("dk7_to_fair", "The fair road after the first visit.", [
     N("Fair Road", "Estrada da Feira", "Star banners again. The ring waits in the middle.",
       "Bandeiras de estrela de novo. O ringue espera no meio."),
    ], chapter=7)
    sc("dk7_to_desert", "The trail back to the Desert of Lost Stars.", [
     N("Desert Trail", "Trilha do Deserto", "The wind turns hot. Sand underfoot. The dunes are behind.",
       "O vento esquenta. Areia sob os pes. As dunas ficam atras."),
    ], chapter=7)
    sc("dk7_arrival", "Chapter 7 opens: stalls, a ring, a soaked friend at the raft.", [
     N("Star Fair", "Feira", "Stalls in a circle. A rope ring. A raft bumps the pond. Someone coughs water.",
       "Barracas em circulo. Um ringue de corda. Uma jangada bate no lago. Alguem cospe agua."),
     H("That cough. That is Jono. Of course he built a raft.",
       "Essa tosse. E o Jono. Claro que ele fez uma jangada."),
     X("jono", "I sailed! Sort of. Mostly I sank and then floated. Cool fair though!",
       "Eu naveguei! Mais ou menos. Quase afundei e depois flutuei. Feira legal!"),
     N("Objective", "Objetivo", "Talk to Jono at the raft.",
       "Fale com o Jono na jangada."),
    ], chapter=7)
    sc("dk7_jono_pre", "Jono the soaked rival: a friendly duel, then the ring opens in the story.", [
     X("jono", "The village said I was too small for the Kingdom. The raft disagreed. Kind of.",
       "A vila disse que eu era pequeno demais pro Reino. A jangada discordou. Mais ou menos."),
     H("You made it. Dripping, but you made it.",
       "Voce chegou. Pingando, mas chegou."),
     X("jono", "Duel me. Friendly. If I win I brag forever. If you win I still brag a little.",
       "Me desafie. Amistoso. Se eu ganhar eu me gabo pra sempre. Se voce ganhar eu me gabo um pouco.", ask=True),
    ], chapter=7)
    sc("dk7_jono_win", "Jono loses; MAGO.DEV glimpse 6 flashes in the crowd.", [
     X("jono", "Ow. Fine. You are still the better one. Take a dry towel. Metaphorically.",
       "Ai. Tudo bem. Voce ainda e o melhor. Leve uma toalha seca. Metaforicamente."),
     N("Crowd", "Multidao", "In the crowd, one figure stands perfectly still in a green shimmer.",
       "Na multidao, uma figura fica perfeitamente parada num brilho verde."),
     X("mago_hidden", "Take your time. I have all of it.",
       "Leve o tempo que precisar. Eu tenho todo ele."),
     N("Crowd", "Multidao", "A glitch, and the spot is empty.",
       "Um glitch, e o lugar esta vazio."),
     H("Did someone just... talk? The ring is louder than my thoughts.",
       "Alguem acabou de... falar? O ringue esta mais alto que meus pensamentos."),
     X("jono", "The Ring Champion takes bets at the ropes. One star can become nine. Or zero. Careful.",
       "O Campeao do Ringue aceita apostas nas cordas. Uma estrela vira nove. Ou zero. Cuidado."),
     N("You got", "Voce ganhou", "Jono's Raft Charm. He tips you around the fair.",
       "O Amuleto da Jangada do Jono. Ele te da dicas pela feira."),
     N("Objective", "Objetivo", "Challenge the Ring Champion at the central ring.",
       "Desafie o Campeao do Ringue no ringue central."),
    ], chapter=7)
    sc("dk7_jono_lose", "Jono wins the friendly duel (no star).", [
     X("jono", "Ha! Raft power! Try again when you dry off. Wait. That is me.",
       "Ha! Poder da jangada! Tente de novo quando secar. Espera. Esse sou eu."),
     H("Bea's bazaar, or the Underfair Big Top, then rematch.",
       "O bazar da Bea, ou o Circo do Subsolo, depois a revanche."),
    ], chapter=7)
    sc("dk7_jono_after", "Jono after the friendly duel.", [
     X("jono", "I am going to invent a boat that does not sink. Name pending.",
       "Vou inventar um barco que nao afunda. Nome pendente."),
    ], chapter=7)
    sc("dk7_hint", "A free tip from helper Jono at the fair.", [
     X("jono", "Champion holds two. Min bet: nine stars. Castle gate after. Also: fried dough. Priority.",
       "O campeao guarda duas. Aposta min: nove estrelas. Portao do castelo depois. E: massa frita. Prioridade."),
    ], chapter=7)
    sc("dk7_ring_early", "The rope ring before Jono's tip.", [
     N("Duel Ring", "Ringue", "Ropes and dust. The crowd wants a star wager. Not yet.",
       "Cordas e poeira. A multidao quer aposta de estrela. Ainda nao."),
    ], chapter=7)
    sc("dk7_champ_pre", "The Ring Champion, zone master: a one-star wager at the fair ring.", [
     X("ring_champ", "Eight stars walk my fair. Few leave with nine.",
       "Oito estrelas andam na minha feira. Poucos saem com nove."),
     X("ring_champ", "Two stars rest under these ropes. Wager what your nerve allows.",
       "Duas estrelas repousam sob estas cordas. Aposte o que sua coragem deixar."),
     H("Ten open the castle. I did not cross a desert to hesitate.",
       "Dez abrem o castelo. Nao cruzei um deserto pra hesitar."),
     X("ring_champ", "Then cheer or choke, traveler. Shall the fair speak?",
       "Entao aplauda ou engasgue, viajante. A feira pode falar?", ask=True),
    ], chapter=7)
    sc("dk7_champ_win", "The Ring Champion loses: nine stars, end of chapter 7.", [
     X("ring_champ", "The ropes drop. My star, and a medal from my chest.",
       "As cordas caem. Minha estrela, e uma medalha do meu peito."),
     N("You got", "Voce ganhou", "A star and the card Twin-headed Thunder Dragon.",
       "Uma estrela e a carta Twin-headed Thunder Dragon."),
     X("ring_champ", "Beyond the arch the castle stones rise. One more star. The Kingdom still watches.",
       "Alem do arco as pedras do castelo sobem. Mais uma estrela. O Reino ainda observa."),
     H("Nine stars. One to go. Someone in a helicopter is yelling about bugs.",
       "Nove estrelas. Falta uma. Alguem num helicoptero esta gritando sobre insetos."),
     N("End of Chapter 7", "Fim do Capitulo 7", "The Star Fair is behind you. The castle road opens.",
       "A Feira das Estrelas ficou para tras. A estrada do castelo abre."),
    ], chapter=7)
    sc("dk7_champ_lose", "The Ring Champion keeps his stars.", [
     X("ring_champ", "The crowd boos soft. Return heavier, little spark.",
       "A multidao vaia baixinho. Volte mais pesado, faiscazinha."),
     H("He outplayed me. Bea's stalls and the Underfair Big Top, then.",
       "Ele me passou. As barracas da Bea e o Circo do Subsolo, entao."),
    ], chapter=7)
    sc("dk7_champ_after", "The Ring Champion after the duel.", [
     X("ring_champ", "The castle arch is yours. Mind the agents in the alleys.",
       "O arco do castelo e seu. Cuidado com os agentes nos becos."),
    ], chapter=7)
    sc("dk7_inseto_taunt", "InsetoKaiba's fair taunt: foreshadow only, no duel.", [
     X("inseto_kaiba", "A dragonfly lands where it wants. I land on your stars later.",
       "Uma libelula pousa onde quer. Eu pouso nas suas estrelas depois."),
     H("InsetoKaiba. Still loud. Still buggy.",
       "InsetoKaiba. Ainda barulhento. Ainda inseto."),
     X("inseto_kaiba", "The castle gate will be mine. Bring ten stars so the loss hurts more.",
       "O portao do castelo sera meu. Traga dez estrelas pra derrota doer mais."),
    ], chapter=7)
    sc("dk7_agents", "Heishin's agents herding eliminated duelists.", [
     N("Side Alley", "Beco", "Hooded staff push a line of starless duelists toward a cellar hatch.",
       "Equipe de capuz empurra uma fila de duelistas sem estrela pra um alcapao."),
     H("Eliminated... and still walking. Where are their stars going?",
       "Eliminados... e ainda andando. Pra onde vao as estrelas deles?"),
     X("staff", "Move along, festival guest. Cellar business is not your business.",
       "Siga em frente, convidado da feira. Assunto de porao nao e seu."),
    ], chapter=7)
    sc("dk7_castle_road", "The arch after chapter 7: the next part.", [
     N("Castle Road", "Estrada do Castelo", "Stone walls rise. One star left. Chapter 8 arrives in the next part.",
       "Muros de pedra sobem. Falta uma estrela. O capitulo 8 chega na proxima parte."),
    ], chapter=7)
    sc("dk7_gate_shut", "The castle arch before nine stars.", [
     N("Castle Arch", "Arco do Castelo", "A stone arch beyond the fair. Nine stars are carved on it. The crowd pushes you back.",
       "Um arco de pedra alem da feira. Nove estrelas gravadas. A multidao empurra voce."),
    ], chapter=7)
    sc("dk7_bazaar_bea", "Bazaar Bea, the Grand Bazaar.", [
     X("bazaar_bea", "Stars, snacks and cards. Only the cards outlast the fireworks.",
       "Estrelas, lanches e cartas. So as cartas duram mais que os fogos."),
    ], chapter=7)
    sc("dk7_fair_camp", "The fair camp: a tarp behind the stalls, and the game-over warning.", [
     N("Fair Camp", "Acampamento", "A tarp behind the stalls. Kingdom staff keep a lantern lit between banners.",
       "Uma lona atras das barracas. A equipe do Reino mantem um lampiao entre bandeiras."),
     X("staff", "Pretty fair. Deadly rules. Lose your last star and your journey ends for good.",
       "Feira bonita. Regras duras. Perdeu a ultima estrela e a jornada acaba de vez."),
    ], chapter=7)

SPEAKERS = {
 "jono": ("Jono", "Jono", "Jono", 19, "Soaked rival from the raft; friendly duel at the Star Fair (chapter 7)."),
 "ring_champ": ("Ring Champion", "Campeao do Ringue", "Champion", 254, "Master of the Star Fair ring (chapter 7 zone master)."),
 "inseto_kaiba": ("InsetoKaiba", "InsetoKaiba", "Inseto", 254, "Fair taunt only; foreshadows the castle gate (chapter 7)."),
 "mago_hidden": ("???", "???", "???", 254, "Hidden watcher in the fair crowd (MAGO.DEV glimpse 6)."),
 "bazaar_bea": ("Bazaar Bea", "Bea do Bazar", "Bea", 254, "Grand Bazaar keeper (economy)."),
 "staff": ("Camp Staff", "Equipe do Acampamento", "Staff", 254, "Kingdom staff at the fair camp / alley."),
}
FLAGS = [("fair_arrived", "Chapter 7: entered the Star Fair."),
         ("jono_fair_won", "Jono beaten in the friendly fair duel: helper tips + MAGO glimpse."),
         ("ring_champ_won", "Ring Champion beaten: ninth star, end of chapter 7.")]
STAGES = [(28, "Chapter 7: the fair, Jono at the raft"),
          (29, "Chapter 7: Jono helps; the Ring Champion at the ropes"),
          (30, "Chapter 7 complete: the castle road is the next part")]
ANCHORS = {"kingdom_fair": {
 "spawn": "Path in from the desert (bottom).",
 "fair_camp": "A tarp behind the stalls (bottom left).",
 "jono_spot": "The raft at the pond where Jono waits.",
 "shop_stall": "Bazaar Bea's Grand Bazaar (purple tent, west).",
 "arena_door": "The Underfair Big Top hatch (southeast).",
 "gate_spot": "The central rope ring where the Ring Champion waits.",
 "castle_gate": "The stone arch at the top: the castle road.",
 "inseto_spot": "Open ground where the dragonfly 'copter kicked dust.",
 "agents_alley": "A side alley where staff herd the starless.",
 "fair_center": "Open grass by the ring.",
 "hangout_a": "East stall path.",
 "hangout_b": "West stall path by the camp.",
}}
ITEMS = [("raft_charm", "Raft Charm", "Amuleto da Jangada",
          "Jono's charm. He tips you around the fair and beyond.",
          "O amuleto do Jono. Ele te da dicas na feira e alem.",
          "Jono, at the Star Fair")]

def W(**k): return k
NPCS = [
 dict(id="jono_fair", area="kingdom_fair", anchor="jono_spot", duelist_id=19, stages=[28, 99], visible="placed",
      note="Jono the soaked rival: friendly duel, then helper tips.",
      rules=[W(when=W(stage=[28,28], flags_none=["jono_fair_won"]), script="dk7_jono_pre", duel="jono_fair"),
             W(when=W(stage=[29,99], needs=["jono_fair_won"]), script="dk7_hint"),
             W(when=W(stage=[29,99]), script="dk7_jono_after")]),
 dict(id="ring_champ", area="kingdom_fair", anchor="gate_spot", duelist_id=None, stages=[29, 99], visible="placed",
      note="The zone master at the rope ring once Jono has dueled.",
      rules=[W(when=W(stage=[29,29], flags_none=["ring_champ_won"]), script="dk7_champ_pre", duel="ring_champ"),
             W(when=W(stage=[29,99]), script="dk7_champ_after")]),
 dict(id="inseto_fair", area="kingdom_fair", anchor="inseto_spot", duelist_id=None, stages=[28, 99], visible="placed",
      note="InsetoKaiba taunts only; foreshadows chapter 8.",
      rules=[W(when=W(stage=[28,99]), script="dk7_inseto_taunt")]),
 dict(id="bazaar_bea", area="kingdom_fair", anchor="shop_stall", duelist_id=None, stages=[28, 99], visible="always",
      rules=[W(when=W(stage=[28,99]), script="dk7_bazaar_bea")]),
]
NPC_SPEAKER = {"jono_fair": "jono", "inseto_fair": "inseto_kaiba"}
def B(en, pt): return {"en": en, "pt": pt}
OBJECTS = [
 dict(id="duel_ring", name=B("Duel ring", "Ringue"), area="kingdom_fair", anchor="gate_spot", rules=[
  W(when=W(stage=[28,28]), script="dk7_ring_early")]),
 dict(id="castle_gate", name=B("Castle arch", "Arco do castelo"), area="kingdom_fair", anchor="castle_gate", rules=[
  W(when=W(stage=[30,99], stars=9), script="dk7_castle_road"), W(when=W(stage=[28,99]), script="dk7_gate_shut")]),
 dict(id="fair_camp", name=B("Fair camp", "Acampamento da feira"), area="kingdom_fair", anchor="fair_camp", rules=[
  W(when=W(stage=[28,99]), script="dk7_fair_camp")]),
 dict(id="agents_alley", name=B("Side alley", "Beco"), area="kingdom_fair", anchor="agents_alley", rules=[
  W(when=W(stage=[28,99]), script="dk7_agents")]),
 dict(id="fair_exit", name=B("Desert trail", "Trilha do deserto"), area="kingdom_fair", anchor="spawn", rules=[]),
]
DUELS = [
 dict(id="jono_fair", npc="jono_fair", duelist_id=19, deck="Jono Fair", tier=6, pre="dk7_jono_pre", win="dk7_jono_win", lose="dk7_jono_lose", win_flag="jono_fair_won",
      on_win=[W(give_item="raft_charm"), W(set_stage=29)],
      note="Friendly rival duel, no star: Jono becomes a fair helper; MAGO.DEV glimpse 6."),
 dict(id="ring_champ", npc="ring_champ", duelist_id=None, deck="Ring Champion Circus", tier=7, pre="dk7_champ_pre", win="dk7_champ_win", lose="dk7_champ_lose", win_flag="ring_champ_won",
      on_win=[W(give_card="Twin-headed Thunder Dragon"), W(set_stage=30)], stars=2,
      note="Zone master, holds 2 stars: bet 1 for the curve (8->9). Needs fair cards or Underfair Big Top wins."),
]
TRANSITIONS = [
 dict(id="enter_fair", when=W(stage=[27,27], stars=8), trigger=W(kind="interact", object="fair_gate"), effects=[W(set_stage=28), W(teleport=W(area="kingdom_fair", anchor="spawn"))], script="dk7_enter"),
 dict(id="to_fair", when=W(stage=[28,99]), trigger=W(kind="interact", object="fair_gate"), effects=[W(teleport=W(area="kingdom_fair", anchor="spawn"))], script="dk7_to_fair"),
 dict(id="to_desert_from_fair", when=W(stage=[28,99]), trigger=W(kind="interact", object="fair_exit"), effects=[W(teleport=W(area="kingdom_desert", anchor="fair_gate"))], script="dk7_to_desert"),
 dict(id="fair_arrival", when=W(stage=[28,28], flags_none=["fair_arrived"]), trigger=W(kind="when_true", area="kingdom_fair"), effects=[W(set_flag="fair_arrived")], script="dk7_arrival"),
]
HUD = [
 (W(stage=[28,28]), "Talk to Jono at the raft - soaked and ready", "Fale com o Jono na jangada - encharcado e pronto"),
 (W(stage=[29,29]), "Beat the Ring Champion - a star on the line", "Venca o Campeao do Ringue - uma estrela em jogo"),
 (W(stage=[30,99]), "Chapter 7 complete - the castle road waits", "Capitulo 7 completo - a estrada do castelo espera"),
]
CHAPTER = dict(n=7, title=B("The Star Fair", "A Feira das Estrelas"), region="kingdom_fair", stage=[28,30],
               reward="nine stars, Raft Charm, card Twin-headed Thunder Dragon", unlock="the castle road (chapter 8)")
QUESTS = [
 dict(id="q16_fair", kind="talk+duel", opt=False, title=B("The Star Fair", "A Feira das Estrelas"), giver="(none)",
      steps=[("Talk to Jono at the raft", "Fale com o Jono na jangada", "kingdom_fair.jono_spot"),
             ("Beat the Ring Champion for a star", "Venca o Campeao do Ringue por uma estrela", "kingdom_fair.gate_spot")],
      reward="nine stars, Raft Charm, card Twin-headed Thunder Dragon"),
]
DECKS = {
 "Jono Fair": dict(duelist="Jono", tier=6, theme="Beast warriors and stubborn grit", notes="Chapter 7 friendly rival (no star).", cards={
   "Wolf": 3, "Silver Fang": 3, "Prevent Rat": 2, "Mavelus": 2, "Flame Cerebrus": 1, "Garvas": 2,
   "Flower Wolf": 1, "Axe Raider": 2, "Ansatsu": 2, "Wasteland": 2, "Forest": 2, "Sparks": 2,
   "Red Medicine": 3, "Mooyan Curry": 2, "Hinotama": 2, "Haniwa": 2, "Pot the Trick": 2}),
 "Ring Champion Circus": dict(duelist="Ring Champion", tier=7, theme="Showy fusion beaters and the fair field", notes="Chapter 7 zone master (holds 2).", cards={
   "Twin-headed Thunder Dragon": 1, "Bickuribox": 1, "Ushi Oni": 1, "Kaiser Dragon": 1, "Swordstalker": 2,
   "Flame Swordsman": 2, "Giltia the D. Knight": 1, "Axe Raider": 2, "Ansatsu": 2, "Monster Tamer": 2,
   "Beautiful Beast Trainer": 2, "Sogen": 3, "Sparks": 2, "Hinotama": 2, "Red Medicine": 2, "Invigoration": 2,
   "Mooyan Curry": 2, "Legendary Sword": 2}),
}
