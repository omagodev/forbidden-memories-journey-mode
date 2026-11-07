# InsetoKaiba's Feupys deck (Journey Mode 0.6.18)

InsetoKaiba (the ship duel, and the Gate wager rematch) now plays a fixed
40-card deck built around 12 parody cards. The names and artwork come from
cards shown in a video by the creator **Feupys**. This is a fan tribute: the
cards are not official and are not made or endorsed by Feupys or Konami, and
no permission from Feupys is claimed. Each card's art is cropped from the
source frame (the card only, never the person on screen). The "R10 o Bruxo"
art shows a photo of a real footballer, as it appears on the source card.

## Adapted to Forbidden Memories

The printed text does not fit the FM engine, so every card copies an FM card
for its effect and gets FM-sized stats. These are **our adaptations, not
Feupys' originals**:

| Card | Kind | Plays as (FM base) | Journey stats |
|---|---|---|---|
| O Trabalhador CLT de Olhos Azuis | Warrior / Earth, lv 8 | Judge Man | 2800 / 2600 (printed 4000/4000) |
| Amante Branca de Olhos Vermelhos | Spellcaster / Light, lv 7 | Mystical Elf | 2500 / 2100 |
| Obelisco Atormentador de Olhos Azuis | Fiend / Light, lv 8 | Rude Kaiser | 2700 / 2500 |
| Dragão de Olhos Azuis ao Lado de Ra | Dragon / Light, lv 8 | Blue-eyes White Dragon | 3000 / 2500 (printed 4000/4000) |
| Kuriboh Branco de Olhos Azuis | Fairy / Light, lv 1 | Kuriboh | 300 / 200 |
| Fui Comprar Cigarro | Trap | Fake Trap | — |
| Força do Roberto | Equip | Megamorph | — |
| R10 o Bruxo | Magic | Widespread Ruin | — |
| Agiota Evangélico | Magic | Dian Keto the Cure Master | — |
| Conselho de Mãe | Magic | Swords of Revealing Light | — |
| A Volta dos que Não Foram | Trap | Acid Trap Hole | — |
| Força Espelho de Olhos Azuis | Trap | Bear Trap | — |

The deck has 20 Feupys cards plus 20 retail cards (Saggi, Hitotsu-me Giant,
Mystic Horseman, Battle Ox, Rude Kaiser, Ryu-kishin Powered, Celtic Guardian,
Judge Man, Gyakutenno Megami). It hits hard (3000 ATK dragon, Megamorph-type
equips) but has no fusions or heavy removal, so it can be beaten.

## Getting the cards

* They are **never** in shops, packs, passwords, starting decks, other
  duelists' decks or ordinary drops (`drops:false`, `opponents:false`,
  `password:null`; the Journey shops and Eco pools only list cards 1–722).
* Each **won** duel against InsetoKaiba (ship or Gate rematch) has a
  **4%** chance (400 basis points) to give **one** of the 12, chosen at
  random. At most one per victory; the normal spoil is replaced in that case.
* Rematches: the ship duel can be retried until you win it; after that the
  Gate InsetoKaiba offers a wager rematch, so the chance is never locked out.
* Owned copies and deck slots are saved in the Journey save (save version 9)
  and restored on load. A new journey starts without them.
* Testing only: `MEMORIES_MOD_OW_POC_FEUPYS_DROP_BP=10000` forces the drop.
