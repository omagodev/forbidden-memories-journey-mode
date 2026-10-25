// Boletos -- "When summoned, the opponent loses 500 LP for each card in their hand."
// Handlers receive ctx: {card, record, side, opp, damage, heal, boost, destroy,
//                        handCount, fieldMonsters, cardId, atk, def, life, log, say}
function onSummon(ctx) {
    var n = ctx.handCount(ctx.opp);
    ctx.log("Boletos summoned: opponent holds " + n + " card(s) in hand");
    if (n > 0) {
        ctx.say("BOLETOS! The opponent loses " + (n * 500) + " LP (" + n + " cards in hand)");
        ctx.damage(ctx.opp, 500 * n);
    }
}
