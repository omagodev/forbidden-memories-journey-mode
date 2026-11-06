# -*- coding: utf-8 -*-
"""Chapter 8 - The Castle Gate (castle_gate): last numbered chapter before the castle / Dream Room.
InsetoKaiba rematch at the star-lock (nine -> ten on the minimum bet). Pawn Paul's Gate Pawn Stall,
the Moat Pit arena with three exclusives, intentional no-gang hub (gate is never_in). Gate key opens
the announcement for the castle hall / Dream Room (not implemented here). Same page rules as
dk_scripts.py (ASCII, 3 x 32). Imported at the end of dk_scripts.py (scripts) and dk_data.py (structure).

Flag budget: only inseto_gate_won is new. Arrival uses stage 31 (no *_arrived flag) so the 64-flag
ceiling still has room for one more story bit; castle hall / Dream Room still need more flags and
are blocked until MAX_FLAGS grows or more optional flags are folded."""

def scripts(sc, H, X, N):
    sc("dk8_enter", "Chapter 7 -> 8: the castle road opens onto the gate plaza.", [
     N("Castle Gate", "Portao do Castelo", "Nine stars. Stone walls. A glowing lock counts ten.",
       "Nove estrelas. Muros de pedra. Uma fechadura brilha contando dez."),
     H("InsetoKaiba is already posing. Of course he is.",
       "InsetoKaiba ja esta posando. Claro que esta."),
    ], chapter=8)
    sc("dk8_to_gate", "The castle road after the first visit.", [
     N("Castle Road", "Estrada do Castelo", "The star-lock still waits. The plaza is quieter than the fair.",
       "A fechadura de estrela ainda espera. A praca e mais quieta que a feira."),
    ], chapter=8)
    sc("dk8_to_fair", "The trail back to the Star Fair.", [
     N("Fair Trail", "Trilha da Feira", "Banners and frying oil again. The fair is behind you.",
       "Bandeiras e oleo fritando de novo. A feira fica atras."),
    ], chapter=8)
    sc("dk8_arrival", "Chapter 8 opens: plaza, pawn stall, Moat Pit, Inseto at the lock.", [
     N("Castle Gate", "Portao", "A wide stone plaza. A pawn stall. A torch pit. The gate's lock glows ten empty stars.",
       "Uma praca de pedra. Um cambista. Um poco de tochas. A fechadura do portao brilha com dez estrelas vazias."),
     X("inseto_kaiba", "You brought nine. Cute. I brought moths, beetles, and a better ego.",
       "Voce trouxe nove. Fofo. Eu trouxe mariposas, besouros e um ego melhor."),
     H("Ship rematch. Bigger deck. Same bugs.",
       "Revanche do navio. Baralho maior. Mesmos insetos."),
     N("Objective", "Objetivo", "Challenge InsetoKaiba at the star-lock.",
       "Desafie InsetoKaiba na fechadura de estrela."),
    ], chapter=8)
    sc("dk8_inseto_pre", "InsetoKaiba gate guardian: memorable rematch, one-star wager.", [
     X("inseto_kaiba", "Great Moth. Javelin Beetle. Crown jewels of the swarm. You are still a larva.",
       "Great Moth. Javelin Beetle. Joias da coroa do enxame. Voce ainda e uma larva."),
     H("I beat you on the ship. I will beat you at the door.",
       "Eu te venci no navio. Vou te vencer na porta."),
     X("inseto_kaiba", "Two stars under my wing. Wager what your nerve allows. Shall the gate speak?",
       "Duas estrelas sob minha asa. Aposte o que sua coragem deixar. O portao pode falar?", ask=True),
    ], chapter=8)
    sc("dk8_inseto_win", "InsetoKaiba loses: ten stars, gate key, end of chapter 8.", [
     X("inseto_kaiba", "...A worthy bug. Take the Crown Beetle. Take the key. I will grumble forever.",
       "...Um inseto digno. Leve o Crown Beetle. Leve a chave. Vou resmungar pra sempre."),
     N("You got", "Voce ganhou", "A star, Hercules Beetle (his Crown Beetle), and the Gate Key.",
       "Uma estrela, Hercules Beetle (o Crown Beetle dele) e a Chave do Portao."),
     X("inseto_kaiba", "The lock counts ten. Go on. The hall and the Dream Room are not my problem.",
       "A fechadura conta dez. Vai. O salao e a Sala dos Sonhos nao sao problema meu."),
     H("Ten stars. The castle opens. Dream Room next - if the story can carry it.",
       "Dez estrelas. O castelo abre. Sala dos Sonhos a seguir - se a historia aguentar."),
     N("End of Chapter 8", "Fim do Capitulo 8", "The Castle Gate yields. The castle hall / Dream Room is the next part.",
       "O Portao do Castelo cede. O salao / Sala dos Sonhos e a proxima parte."),
    ], chapter=8)
    sc("dk8_inseto_lose", "InsetoKaiba keeps his stars.", [
     X("inseto_kaiba", "Larva. Pawn Paul's stall and the Moat Pit, then crawl back.",
       "Larva. O cambista do Paul e o Poco do Fosso, depois rasteje de volta."),
     H("He outplayed me. Cards, then rematch.",
       "Ele me passou. Cartas, depois a revanche."),
    ], chapter=8)
    sc("dk8_inseto_after", "InsetoKaiba after the rematch.", [
     X("inseto_kaiba", "I am still the better bug. The door just disagrees today.",
       "Ainda sou o inseto melhor. A porta so discorda hoje."),
    ], chapter=8)
    sc("dk8_pawn_paul", "Pawn Paul, Gate Pawn Stall.", [
     X("pawn_paul", "Stars, scars and cards. I buy what the island drops and sell what the gate needs.",
       "Estrelas, cicatrizes e cartas. Compro o que a ilha deixa e vendo o que o portao precisa."),
    ], chapter=8)
    sc("dk8_gate_camp", "The gate camp: tarp by the plaza, game-over warning.", [
     N("Gate Camp", "Acampamento", "A tarp by the plaza stones. Kingdom staff keep one lantern for the starless.",
       "Uma lona junto as pedras da praca. A equipe do Reino mantem um lampiao pros sem estrela."),
     X("staff", "Pretty gate. Deadly rules. Lose your last star and your journey ends for good.",
       "Portao bonito. Regras duras. Perdeu a ultima estrela e a jornada acaba de vez."),
    ], chapter=8)
    sc("dk8_castle_shut", "The castle door before ten stars / before Inseto falls.", [
     N("Castle Door", "Porta do Castelo", "The lock shows empty notches. Ten stars open it. InsetoKaiba blocks the step.",
       "A fechadura mostra entalhes vazios. Dez estrelas abrem. InsetoKaiba bloqueia o degrau."),
    ], chapter=8)
    sc("dk8_castle_announce", "After chapter 8: the hall / Dream Room is announced, not entered.", [
     N("Castle Door", "Porta do Castelo", "The lock clicks to ten. Beyond: illusion halls, a chamberlain, and Pegasus's Dream Room.",
       "A fechadura trava em dez. Alem: salas de ilusao, um camareiro e a Sala dos Sonhos de Pegasus."),
     H("Heishin. Pegasus. The wish. Not this chapter - the next part of the Kingdom.",
       "Heishin. Pegasus. O desejo. Nao neste capitulo - na proxima parte do Reino."),
     N("Coming next", "A seguir", "Chapter 9: Castle Hall. Chapter 10: Pegasus's Dream. Flag budget is tight.",
       "Capitulo 9: Salao do Castelo. Capitulo 10: Sonho de Pegasus. O orcamento de flags esta apertado."),
    ], chapter=8)

SPEAKERS = {
 "inseto_kaiba": ("InsetoKaiba", "InsetoKaiba", "Inseto", 254, "Gate guardian rematch (chapter 8); ship rivalry payoff."),
 "pawn_paul": ("Pawn Paul", "Paul do Cambista", "Paul", 254, "Gate Pawn Stall keeper (economy)."),
 "staff": ("Camp Staff", "Equipe do Acampamento", "Staff", 254, "Kingdom staff at the gate camp."),
}
# Only one new flag: arrival is stage-driven (enter -> stage 31) so we stay at 64.
FLAGS = [("inseto_gate_won", "InsetoKaiba beaten at the castle gate: tenth star, Gate Key, end of chapter 8.")]
STAGES = [(31, "Chapter 8: the castle gate, InsetoKaiba at the lock"),
          (32, "Chapter 8 complete: ten stars; the castle / Dream Room is next")]
ANCHORS = {"castle_gate": {
 "spawn": "Path in from the fair (bottom).",
 "gate_camp": "A tarp by the plaza (bottom left).",
 "shop_stall": "Pawn Paul's Gate Pawn Stall (west).",
 "arena_door": "The Moat Pit hatch (east).",
 "gate_spot": "The star-lock where InsetoKaiba waits.",
 "castle_door": "The castle door beyond the lock (top).",
 "gate_center": "Open plaza stones.",
 "hangout_a": "East path by the pit.",
 "hangout_b": "West path by the pawn stall.",
}}
ITEMS = [("gate_key", "Gate Key", "Chave do Portao",
          "InsetoKaiba's key. The star-lock counts ten.",
          "A chave do InsetoKaiba. A fechadura conta dez.",
          "InsetoKaiba, at the Castle Gate")]

def W(**k): return k
NPCS = [
 dict(id="inseto_gate", area="castle_gate", anchor="gate_spot", duelist_id=None, stages=[31, 99], visible="placed",
      note="InsetoKaiba rematch: gate guardian, holds 2, min bet for the 9->10 curve.",
      rules=[W(when=W(stage=[31,31], flags_none=["inseto_gate_won"]), script="dk8_inseto_pre", duel="inseto_gate"),
             W(when=W(stage=[32,99], flags_all=["inseto_gate_won"]), script="dk8_inseto_after")]),
 dict(id="pawn_paul", area="castle_gate", anchor="shop_stall", duelist_id=None, stages=[31, 99], visible="always",
      rules=[W(when=W(stage=[31,99]), script="dk8_pawn_paul")]),
]
NPC_SPEAKER = {"inseto_gate": "inseto_kaiba"}
def B(en, pt): return {"en": en, "pt": pt}
OBJECTS = [
 dict(id="castle_door", name=B("Castle door", "Porta do castelo"), area="castle_gate", anchor="castle_door", rules=[
  W(when=W(stage=[32,99], stars=10), script="dk8_castle_announce"), W(when=W(stage=[31,99]), script="dk8_castle_shut")]),
 dict(id="gate_camp", name=B("Gate camp", "Acampamento do portao"), area="castle_gate", anchor="gate_camp", rules=[
  W(when=W(stage=[31,99]), script="dk8_gate_camp")]),
 dict(id="gate_exit", name=B("Fair trail", "Trilha da feira"), area="castle_gate", anchor="spawn", rules=[]),
]
DUELS = [
 dict(id="inseto_gate", npc="inseto_gate", duelist_id=None, deck="InsetoKaiba Gate", tier=8, pre="dk8_inseto_pre", win="dk8_inseto_win", lose="dk8_inseto_lose", win_flag="inseto_gate_won",
      on_win=[W(give_card="Hercules Beetle"), W(give_item="gate_key"), W(set_stage=32)], stars=2,
      note="Gate guardian rematch, holds 2 stars: bet 1 for the curve (9->10). Payoff of the ship rivalry."),
]
TRANSITIONS = [
 dict(id="enter_gate", when=W(stage=[30,30], stars=9), trigger=W(kind="interact", object="castle_gate"), effects=[W(set_stage=31), W(teleport=W(area="castle_gate", anchor="spawn"))], script="dk8_arrival"),
 dict(id="to_gate", when=W(stage=[31,99]), trigger=W(kind="interact", object="castle_gate"), effects=[W(teleport=W(area="castle_gate", anchor="spawn"))], script="dk8_to_gate"),
 dict(id="to_fair_from_gate", when=W(stage=[31,99]), trigger=W(kind="interact", object="gate_exit"), effects=[W(teleport=W(area="kingdom_fair", anchor="castle_gate"))], script="dk8_to_fair"),
]
# Arrival text is on enter (dk8_enter + dk8_arrival content folded into enter for first visit).
HUD = [
 (W(stage=[31,31]), "Beat InsetoKaiba at the star-lock - a star on the line", "Venca InsetoKaiba na fechadura - uma estrela em jogo"),
 (W(stage=[32,99]), "Chapter 8 complete - the castle / Dream Room waits", "Capitulo 8 completo - o castelo / Sala dos Sonhos espera"),
]
CHAPTER = dict(n=8, title=B("The Castle Gate", "O Portao do Castelo"), region="castle_gate", stage=[31,32],
               reward="ten stars, Gate Key, card Hercules Beetle (Crown Beetle)", unlock="the castle hall / Dream Room (chapter 9+)")
QUESTS = [
 dict(id="q17_gate", kind="duel", opt=False, title=B("The Castle Gate", "O Portao do Castelo"), giver="(none)",
      steps=[("Beat InsetoKaiba at the star-lock for a star", "Venca InsetoKaiba na fechadura por uma estrela", "castle_gate.gate_spot")],
      reward="ten stars, Gate Key, card Hercules Beetle"),
]
DECKS = {
 "InsetoKaiba Gate": dict(duelist="InsetoKaiba", tier=8, theme="Bigger insect swarm: Great Moth, Javelin Beetle, Crown Beetle payoff", notes="Chapter 8 gate rematch (holds 2).", cards={
   "Great Moth": 1, "Javelin Beetle": 1, "Hercules Beetle": 1, "Dungeon Worm": 1, "Killer Needle": 2,
   "Gokibore": 2, "Kuwagata α": 2, "Basic Insect": 2, "Larvae Moth": 2, "Cocoon of Evolution": 2,
   "Petit Moth": 2, "Insect Armor with Laser Cannon": 3, "Vile Germs": 2, "Forest": 3,
   "Sparks": 2, "Hinotama": 2, "Red Medicine": 2, "Mooyan Curry": 2}),
}
