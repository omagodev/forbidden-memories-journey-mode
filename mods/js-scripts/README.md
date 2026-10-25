# JS Card Scripts (proof of concept)

An optional API 10 code mod that lets a card's effect be written in
JavaScript, YGOPro style, instead of in the `card_effects` and
`monster_effects` JSON. [QuickJS](https://github.com/quickjs-ng/quickjs) is
linked into the game (`src/pc/third_party/quickjs`, MIT, see
`src/pc/third_party/README.md`); `src/pc/script/js_host.[ch]` runs it and
knows nothing about the duel.

## Writing a card

A card names its script in its notes, and `scripts/<name>.js` defines any of
`onSummon`, `onFlip`, `onTurnStart`, `onCombat`, `onDestroyed` and
`onDestroyOpponent`:

```json
{ "id": "boletos", "copy": "Feral Imp", "name": "Boletos", "art": "art/boletos.png",
  "attack": 1200, "defense": 900, "notes": "JS card. <script: boletos>" }
```

```js
function onSummon(ctx) {
    var n = ctx.handCount(ctx.opp);
    if (n > 0) ctx.damage(ctx.opp, 500 * n);
}
```

Each handler receives `ctx`: `card`, `record`, `side`, `opp`, `damage`, `heal`,
`boost`, `destroy`, `handCount`, `fieldMonsters`, `cardId`, `atk`, `def`,
`life`, `log` and `say`.

## How it works

`js_scripts.c` hears `MEMORIES_EVENT_MONSTER`, finds the card's `<script: name>`
note, loads the script into its own QuickJS context and calls the handler. The
`ctx` operations become entries of the duel's effect queue
(`MonsterEffects_ScriptAction`, `src/pc/cards/monster_effects_duel.c`), so they
resolve with the game's own life-point splash.

## The example

**Boletos** (Dark, level 4, 1200/900): when summoned, the opponent loses 500
life points for each card in their hand. Its art was made for this project.

## Limits

The hooks are the six listed above, all on monsters, and `ctx` offers only
damage, healing, an ATK/DEF boost and destroy; a script cannot ask the player
for a target.
