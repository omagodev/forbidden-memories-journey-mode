/* Journey Mode economy: coins, experience, the level curve, the local card pools and the shops.
 *
 * The numbers are data, not code: assets/economy.json holds the tier tables, the level curve, the
 * drop odds, the pools and the shops, and assets/lang/<code>/economy.json the strings.  Both are
 * built from journey_content/economy (the design) by tools/eco_to_journey.py.  When they are not
 * there every call here does nothing, so a build whose assets predate the economy plays as before.
 *
 * Money and experience live in jm.eco (Journey's appended Economy block, save version 5).
 */
#include "jm.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static JsonNode *eco;                   /* assets/economy.json */
static JsonNode *txt;                   /* assets/lang/<code>/economy.json */
static int tried;                       /* the data has been looked for (a missing file is not retried) */

/* ------------------------------------------------------------------ data */
int Eco_Load(void)
{
    char *t;
    if (eco) return 1;
    if (tried) return 0;
    tried = 1;
    t = Jm_ReadText("assets/economy.json");
    if (t) { eco = Json_Parse(t); free(t); }
    if (!eco) { LOG("journey: no economy data (assets/economy.json); coins are off"); return 0; }
    LOG("journey: economy data (%d levels)", Json_Count(Json_Get(eco, "levels")));
    return 1;
}

int Eco_Ready(void) { return eco != NULL; }

/* A block of the economy data, for the parts of it that live in another file (the gang, the arenas). */
JsonNode *Eco_Block(const char *key) { return eco ? Json_Get(eco, key) : NULL; }


void Eco_LoadLang(const char *code)
{
    char path[80], *t;
    JsonNode *j = NULL;
    if (!code) return;
    snprintf(path, sizeof(path), "assets/lang/%s/economy.json", code);
    t = Jm_ReadText(path);
    if (t) { j = Json_Parse(t); free(t); }
    if (!j) return;                     /* no strings for this language: the ones loaded stay */
    if (txt) Json_Free(txt);
    txt = j;
}

/* The string at a dotted path of the economy text ("ui.money_gain"), or the path itself. */
const char *EcoTr(const char *path)
{
    const JsonNode *n = txt;
    const char *p = path;
    while (n && *p) {
        char seg[40];
        size_t len = 0;
        while (p[len] && p[len] != '.') len++;
        if (len >= sizeof(seg)) return path;
        memcpy(seg, p, len);
        seg[len] = 0;
        n = (seg[0] >= '0' && seg[0] <= '9') ? Json_At(n, atoi(seg)) : Json_Get(n, seg);
        p += len + (p[len] == '.');
    }
    return n && n->str ? n->str : path;
}

static JsonNode *table(void) { return eco ? Json_Get(eco, "levels") : NULL; }
static JsonNode *row_of(int level) { return Json_At(table(), level - 1); }
static int rounded(int value, int percent) { return (value * percent + 50) / 100; }

/* ------------------------------------------------------------ the notices
 * Coins, experience and a level up arrive together and the message line shows one thing at a time,
 * so they queue and are shown in turn. */
#define NOTES 5
#define TONE_GAIN 0x60F060u              /* coins and experience: the message line's own green */
#define TONE_ALERT 0xFFD24Au             /* a level up, and anything the player must not miss */
static char notes[NOTES][56];
static unsigned tones[NOTES];
static int note_count, note_wait;

static void note_tone(const char *s, unsigned rgb)
{
    if (!s || !*s || note_count >= NOTES) return;
    strncpy(notes[note_count], s, sizeof(notes[0]) - 1);
    notes[note_count][sizeof(notes[0]) - 1] = 0;
    tones[note_count] = rgb;
    note_count++;
}

static void note(const char *s) { note_tone(s, TONE_GAIN); }
/* A line on the message queue from another file; `alert` puts it in the colour a level up uses. */
void Eco_Note(const char *text, int alert) { note_tone(text, alert ? TONE_ALERT : TONE_GAIN); }

static void note_num(const char *key, int value)
{
    char buf[56];
    Ui_Fmt1(buf, sizeof(buf), EcoTr(key), value);
    note(buf);
}

void Eco_Tick(void)
{
    if (note_wait > 0) { note_wait--; return; }
    if (note_count <= 0) return;
    Ui_MessageTone(notes[0], tones[0]);
    memmove(notes[0], notes[1], sizeof(notes[0]) * (NOTES - 1));
    memmove(&tones[0], &tones[1], sizeof(tones[0]) * (NOTES - 1));
    note_count--;
    note_wait = 75;                     /* the message lasts 120 frames; the next one waits its turn */
}

/* ------------------------------------------------------------- the level */
int Eco_Level(void)
{
    JsonNode *t = table();
    int i, n = Json_Count(t), level = 1;
    for (i = 0; i < n; i++) {
        JsonNode *r = Json_At(t, i);
        if (jm.eco.xp < (int)Json_Num(r, "xp", 0)) break;
        level = i + 1;
    }
    return level;
}

int Eco_Rank(void) { return (int)Json_Num(row_of(Eco_Level()), "rank", 1); }

const char *Eco_RankName(void)
{
    char key[24];
    snprintf(key, sizeof(key), "ui.rank_%d", Eco_Rank());
    return EcoTr(key);
}

int Eco_XpBar(int *into, int *span)
{
    int level = Eco_Level(), base, next;
    JsonNode *after = Json_At(table(), level);
    *into = *span = 0;
    if (!after) return 0;               /* the last level has nothing left to fill */
    base = (int)Json_Num(row_of(level), "xp", 0);
    next = (int)Json_Num(after, "xp", 0);
    *into = jm.eco.xp - base;
    *span = next - base;
    return *span > 0;
}

/* ------------------------------------------------------------- the purse */
void Eco_GiveCoins(int n)
{
    int cap = (int)Json_Num(eco, "cap", 99999);
    if (!eco || n <= 0) return;
    if (n > cap - jm.eco.coins) n = cap - jm.eco.coins;
    if (n <= 0) return;
    jm.eco.coins += n;
    note_num("ui.money_gain", n);
}

int Eco_TakeCoins(int n)
{
    if (n <= 0) return 1;
    if (!eco || jm.eco.coins < n) return 0;
    jm.eco.coins -= n;
    return 1;
}

int Eco_GiveXp(int n)
{
    int before, after, cap;
    if (!eco || n <= 0) return 0;
    cap = (int)Json_Num(eco, "cap_level", Json_Count(table()));
    before = Eco_Level();
    if (before >= cap) {                /* at the cap experience stops being paid */
        if (!(jm.eco.eco_bits & ECO_CAP_SEEN)) { jm.eco.eco_bits |= ECO_CAP_SEEN; note(EcoTr("ui.xp_max")); }
        return 0;
    }
    jm.eco.xp += n;
    note_num("ui.xp_gain", n);
    after = Eco_Level();
    if (after > before) {
        char buf[56];
        note_tone(EcoTr("ui.level_up"), TONE_ALERT);
        Ui_Fmt1(buf, sizeof(buf), EcoTr("ui.level_up_now"), after);
        note_tone(buf, TONE_ALERT);
        if ((int)Json_Num(row_of(after), "shop", 0) > (int)Json_Num(row_of(before), "shop", 0))
            note_tone(EcoTr("ui.unlock_shop_tier"), TONE_ALERT);   /* better goods are on sale now */
    }
    return after - before;
}

/* ------------------------------------------------------- what a duel pays */
int Eco_DuelTier(const char *npc_id)
{
    if (!eco || !npc_id) return 0;
    return (int)Json_Num(Json_Get(eco, "duels"), npc_id, 0);
}

int Eco_WinCoins(int tier, const char *context)
{
    JsonNode *tiers = eco ? Json_Get(eco, "tiers") : NULL;
    JsonNode *n = tiers ? Json_At(Json_Get(tiers, "coins"), tier - 1) : NULL;
    int coins, mult, bonus;
    if (!n || tier < 1) return 0;
    mult = (int)Json_Num(Json_Get(eco, "ctx"), context, 100);
    bonus = (int)Json_Num(row_of(Eco_Level()), "bonus", 0);
    coins = rounded((int)n->num, mult);
    return rounded(coins, 100 + bonus);
}

int Eco_WinXp(int tier)
{
    JsonNode *tiers = eco ? Json_Get(eco, "tiers") : NULL;
    JsonNode *xp = tiers ? Json_At(Json_Get(tiers, "xp"), tier - 1) : NULL;
    JsonNode *nom = tiers ? Json_At(Json_Get(tiers, "nominal"), tier - 1) : NULL;
    JsonNode *mod = eco ? Json_Get(eco, "xp_mod") : NULL;
    int pct, lo, hi;
    if (!xp || !nom || tier < 1) return 0;
    /* a duelist worth more than the player pays more, one worth less pays less, inside the bounds */
    pct = 100 + (int)Json_Num(mod, "slope", 12) * ((int)nom->num - Eco_Level());
    lo = (int)Json_Num(mod, "lo", 20);
    hi = (int)Json_Num(mod, "hi", 180);
    if (pct < lo) pct = lo;
    if (pct > hi) pct = hi;
    return rounded((int)xp->num, pct);
}

int Eco_LossXp(int tier)
{
    int full = Eco_WinXp(tier);
    int part = rounded(full, (int)Json_Num(Json_Get(eco, "xp_mod"), "loss_pct", 25));
    if (full > 0 && part < 1) part = 1;         /* a loss still teaches something */
    return part;
}

int Eco_QuestCoins(const char *quest_id)
{
    if (!eco || !quest_id) return 0;
    return (int)Json_Num(Json_Get(eco, "quest_coins"), quest_id, 0);
}

void Eco_DuelReward(const char *npc_id, int won, int rematch)
{
    int tier = Eco_DuelTier(npc_id);
    if (!eco || tier < 1) return;               /* a duel the design gives no tier pays nothing */
    if (won) Eco_GiveCoins(Eco_WinCoins(tier, rematch ? "story_rematch" : "story_first_win"));
    Eco_GiveXp(won ? Eco_WinXp(tier) : Eco_LossXp(tier));
    LOG("journey: duel %s tier %d %s: %d coins, level %d (xp %d)", npc_id, tier, won ? "won" : "lost",
        jm.eco.coins, Eco_Level(), jm.eco.xp);
}

/* ------------------------------------------------------ the quest payout
 * The design pays a quest when its last step is done.  The quests are journey.json "journal", whose
 * "done" condition is made of story flags, so a quest that has just become done is spotted by
 * comparing it with the bits already paid (jm.eco.quests_paid). */
void Eco_QuestTick(void)
{
    JsonNode *list = jm_rules ? Json_Get(jm_rules, "journal") : NULL, *q;
    int i = 0;
    if (!eco || !list) return;
    for (q = list->child; q && i < 16; q = q->next, i++) {
        const char *id = Json_Str(q, "id", "");
        int coins;
        if (jm.eco.quests_paid & (1u << i)) continue;
        if (!Story_Cond(Json_Get(q, "done"))) continue;
        jm.eco.quests_paid |= (unsigned short)(1u << i);
        coins = Eco_QuestCoins(id);
        if (coins > 0) {
            Eco_GiveCoins(coins);
            LOG("journey: quest %s paid %d coins", id, coins);
        }
    }
}

/* ------------------------------------------------------------- the pools
 * A won duel drops a card of the place the player is in: the pool of the area, rolled with the
 * context odds, the level's shift towards the better classes, and the entry weights. */
static const char *area_id(void)
{
    /* The flour cellar is under the village and its arena data uses the village card pool. */
    return paint_area_now() == 1 ? "cistern" : "village";
}

static JsonNode *pool_of_area(void)
{
    JsonNode *map = eco ? Json_Get(eco, "area_pool") : NULL;
    const char *name = map ? Json_Str(map, area_id(), NULL) : NULL;
    return name ? Json_Get(Json_Get(eco, "pools"), name) : NULL;
}

static int rarity_index(const char *r)
{
    switch (r && *r ? *r : 'C') {
    case 'B': return 1;
    case 'A': return 2;
    case 'S': return 3;
    default: return 0;
    }
}
static const char *rarity_name(int i) { return i == 3 ? "S" : i == 2 ? "A" : i == 1 ? "B" : "C"; }

/* hundredths of a percent, so the design's 0.04% stays exact in integers */
#define ODDS_TOTAL 10000
static int bp(double percent) { return (int)(percent * 100.0 + 0.5); }

/* The odds of each class in this context at this level, after the shift and after a class with
 * nothing to give falls to the one below (the rule in journey_content/economy/README.md). */
static int class_odds(const char *context, int arena, int odds[4], int weight[4])
{
    JsonNode *pool = pool_of_area(), *e;
    JsonNode *ctx = eco ? Json_Get(Json_Get(Json_Get(eco, "drops"), "ctx"), context) : NULL;
    JsonNode *shift = Json_Get(row_of(Eco_Level()), "shift");
    int i, level = Eco_Level(), total = 0, move, sh[4];
    if (!pool || !ctx) return 0;
    for (i = 0; i < 4; i++) {
        odds[i] = bp(Json_Num(ctx, rarity_name(i), 0));
        sh[i] = bp(Json_Num(shift, rarity_name(i), 0));
        weight[i] = 0;
    }
    /* the level moves points out of C into the better classes, never more than C has */
    total = sh[1] + sh[2] + sh[3];
    move = total < odds[0] ? total : odds[0];
    if (total > 0 && move > 0) {
        for (i = 1; i < 4; i++) odds[i] += (int)((long)sh[i] * move / total);
        odds[0] -= move;
    }
    for (e = pool->child; e; e = e->next) {         /* what the place can actually give now */
        if ((int)Json_Num(e, "l", 1) > level) continue;
        if (!arena && (int)Json_Num(e, "a", 0)) continue;
        weight[rarity_index(Json_Str(e, "r", "C"))] += (int)Json_Num(e, "w", 1);
    }
    for (i = 3; i >= 1; i--)                        /* a class with nothing falls to the one below */
        if (weight[i] == 0) { odds[i - 1] += odds[i]; odds[i] = 0; }
    return weight[0] + weight[1] + weight[2] + weight[3] > 0;
}

int Eco_DropCount(const char *context)
{
    return (int)Json_Num(Json_Get(Json_Get(eco, "drops"), "count"), context, 1);
}

/* A card of the local pool, or 0 when the place has none (the cistern) or the data is missing. */
static char drop_ctx[24] = "duel";
void Eco_SetDropContext(const char *context) { snprintf(drop_ctx, sizeof(drop_ctx), "%s", context ? context : "duel"); }
const char *Eco_DropContext(void) { return drop_ctx; }

int Eco_RollDrop(const char *context)
{
    JsonNode *pool = pool_of_area(), *e;
    /* the arena is the only place an S card is given out, so its contexts unlock those entries */
    int arena = context && !strncmp(context, "arena", 5);
    int odds[4], weight[4], i, roll, sum = 0, want, level = Eco_Level();
    if (!pool || !class_odds(context, arena, odds, weight)) return 0;
    roll = rand() % ODDS_TOTAL;
    for (i = 0; i < 4; i++) {                       /* which class */
        sum += odds[i];
        if (roll < sum || i == 3) break;
    }
    while (i > 0 && weight[i] == 0) i--;            /* the fall-through, in case of rounding */
    if (weight[i] <= 0) return 0;
    want = rand() % weight[i];                      /* which card of it, by weight */
    sum = 0;
    for (e = pool->child; e; e = e->next) {
        if ((int)Json_Num(e, "l", 1) > level) continue;
        if (!arena && (int)Json_Num(e, "a", 0)) continue;
        if (rarity_index(Json_Str(e, "r", "C")) != i) continue;
        sum += (int)Json_Num(e, "w", 1);
        if (want < sum) return (int)Json_Num(e, "i", 0);
    }
    return 0;
}

/* ------------------------------------------------------------- the shops */
extern unsigned char gLibrary_abCardChest[];
extern unsigned short gDuel_awPlayerDeck[40];
extern int Cards_NameUtf8(int id, char *out, size_t size);

static JsonNode *shop;                  /* the shop whose screen is open */
static char shop_id[16];

/* A line of the dialogue block.  Its keys hold a dot of their own ("keeper_greet.teana"), so they
 * are looked up whole instead of walked like the ui paths. */
const char *EcoDlg(const char *key)
{
    JsonNode *d = txt ? Json_Get(txt, "dialogue") : NULL;
    const char *s = d ? Json_Str(d, key, NULL) : NULL;
    return s ? s : "";
}

static int shop_is_open(JsonNode *s)
{
    JsonNode *o = Json_Get(s, "open"), *f, *n;
    if (!o) return 1;
    if (Json_Get(o, "stage_min") && jm.stage < (int)Json_Num(o, "stage_min", 0)) return 0;
    if (Json_Get(o, "level_min") && Eco_Level() < (int)Json_Num(o, "level_min", 0)) return 0;
    for (f = Json_Get(o, "flags_all"), n = f ? f->child : NULL; n; n = n->next)
        if (n->str && !Story_Has(n->str)) return 0;
    return 1;
}

int Eco_ShopAt(const char *npc_id)
{
    JsonNode *all = eco ? Json_Get(eco, "shops") : NULL, *n;
    if (!all || !npc_id || !*npc_id) return 0;
    for (n = all->child; n; n = n->next) {
        if (strcmp(Json_Str(n, "keeper", ""), npc_id)) continue;
        if (!shop_is_open(n)) return 0;
        shop = n;
        snprintf(shop_id, sizeof(shop_id), "%s", n->key ? n->key : "");
        return 1;
    }
    return 0;
}

int Eco_ShopSet(const char *id)
{
    JsonNode *n = eco ? Json_Get(Json_Get(eco, "shops"), id) : NULL;
    if (!n || !shop_is_open(n)) return 0;
    shop = n;
    snprintf(shop_id, sizeof(shop_id), "%s", id);
    return 1;
}

const char *Eco_ShopName(void)
{
    char path[48];
    if (!shop) return "";
    snprintf(path, sizeof(path), "names.shops.%s", shop_id);
    return EcoTr(path);
}

const char *Eco_ShopGreet(void) { return shop ? EcoDlg(Json_Str(shop, "greet_id", "")) : ""; }
const char *Eco_ShopKeeper(void) { return shop ? Json_Str(shop, "keeper", "") : ""; }

/* --------------------------------------------------------- what a card is
 * The class of any card (the design's rarity table by id), what it sells for, and whether it may be
 * sold at all: some cards are banned and the ones the story hands out are protected. */
static int in_list(const char *key, int card)
{
    JsonNode *l = eco ? Json_Get(eco, key) : NULL, *n;
    for (n = l ? l->child : NULL; n; n = n->next)
        if ((int)n->num == card) return 1;
    return 0;
}

int Eco_CardClass(int card)
{
    char key[12];
    JsonNode *m = eco ? Json_Get(eco, "sell") : NULL;
    const char *r;
    snprintf(key, sizeof(key), "%d", card);
    r = m ? Json_Str(m, key, NULL) : NULL;
    return r ? rarity_index(r) : -1;
}

int Eco_Protected(int card) { return in_list("protected", card) || in_list("banned", card); }

/* round5(sell_rate * weq[class] * sell_base), the design formula, rounded to the price step */
int Eco_SellPrice(int card)
{
    JsonNode *p = eco ? Json_Get(eco, "prices") : NULL;
    int cls = Eco_CardClass(card), step, value;
    if (!p || cls < 0 || Eco_Protected(card)) return 0;
    value = (int)(Json_Num(p, "sell_rate", 0.25) * Json_Num(p, rarity_name(cls), 1.0) *
                  Json_Num(p, "sell_base", 80) + 0.5);
    step = (int)Json_Num(p, "round_to", 5);
    if (step > 1) value = (value + step / 2) / step * step;
    return value;
}

/* ------------------------------------------------- the stock of the shop */
static unsigned fnv1a32(const char *s)
{
    unsigned h = 2166136261u;
    while (*s) { h ^= (unsigned char)*s++; h *= 16777619u; }
    return h;
}

static int owned_of(int card) { return card > 0 && card <= 722 ? gLibrary_abCardChest[card] : 0; }

static void add_item(EcoItem *out, int *n, int max, int card, int price, int level_min, int bit, int kind)
{
    EcoItem *it;
    if (*n >= max || card <= 0) return;
    it = &out[*n];
    it->card = card;
    it->price = price;
    it->level_min = level_min;
    it->bit = bit;
    it->kind = kind;
    it->owned = owned_of(card);
    it->locked = Eco_Level() < level_min;
    it->name[0] = 0;
    Cards_NameUtf8(card, it->name, sizeof(it->name));
    if (!it->name[0]) snprintf(it->name, sizeof(it->name), "#%d", card);
    (*n)++;
}

/* The rotating slots follow the rule written down in the shop data: the stock turns over every few
 * duels and is derived from that count, so nothing about it is saved. */
static void rotating(EcoItem *out, int *n, int max)
{
    JsonNode *rot = Json_Get(shop, "rotating"), *slot, *pool, *e;
    JsonNode *rule = Json_Get(shop, "rotation");
    int every = (int)Json_Num(rule, "every_duels", 6);
    int epoch = every > 0 ? jm.duels / every : 0;
    int level = Eco_Level();
    pool = Json_Get(Json_Get(eco, "pools"), Json_Str(shop, "pool", ""));
    if (!rot || !pool) return;
    for (slot = rot->child; slot; slot = slot->next) {
        const char *key = Json_Str(slot, "slot", "");
        const char *want = Json_Str(slot, "rarity", "C");
        int count = (int)Json_Num(slot, "count", 1), price = (int)Json_Num(slot, "price", 0);
        int need = (int)Json_Num(slot, "min_level", 1), taken = 0;
        if (level < need) continue;
        /* the candidates with the smallest hash, one at a time: a stable pick without a sort */
        while (taken < count) {
            unsigned best_hash = 0;
            int best = 0, first = 1;
            for (e = pool->child; e; e = e->next) {
                char buf[64];
                unsigned h;
                int id = (int)Json_Num(e, "i", 0), k;
                if (strcmp(Json_Str(e, "r", "C"), want)) continue;
                if ((int)Json_Num(e, "l", 1) > level || (int)Json_Num(e, "a", 0)) continue;
                for (k = 0; k < *n; k++) if (out[k].card == id) break;
                if (k < *n) continue;               /* already on the list of this visit */
                snprintf(buf, sizeof(buf), "%s:%s:%d:%d", shop_id, key, epoch, id);
                h = fnv1a32(buf);
                if (first || h < best_hash) { best_hash = h; best = id; first = 0; }
            }
            if (!best) break;
            add_item(out, n, max, best, price, need, -1, ECO_ITEM_CARD);
            taken++;
        }
    }
}

int Eco_ShopItems(EcoItem *out, int max)
{
    JsonNode *g, *e;
    int n = 0;
    if (!shop) return 0;
    for (g = Json_Get(shop, "always"), e = g ? g->child : NULL; e; e = e->next)
        add_item(out, &n, max, (int)Json_Num(e, "i", 0), (int)Json_Num(e, "p", 0),
                 (int)Json_Num(e, "l", 1), -1, ECO_ITEM_CARD);
    rotating(out, &n, max);
    for (g = Json_Get(shop, "limited"), e = g ? g->child : NULL; e; e = e->next) {
        int bit = (int)Json_Num(e, "bit", -1);
        if (bit >= 0 && bit < 64 && (jm.eco.bought[bit / 32] & (1u << (bit % 32)))) continue;
        add_item(out, &n, max, (int)Json_Num(e, "i", 0), (int)Json_Num(e, "p", 0),
                 (int)Json_Num(e, "l", 1), bit, ECO_ITEM_ONCE);
    }
    return n;
}

int Eco_PackItems(EcoItem *out, int max)
{
    JsonNode *g = shop ? Json_Get(shop, "packs") : NULL, *e;
    int n = 0, i = 0;
    for (e = g ? g->child : NULL; e; e = e->next, i++) {
        const char *kind = Json_Str(e, "kind", "common");
        char path[32];
        EcoItem *it;
        if (n >= max) break;
        it = &out[n];
        it->card = 0;
        it->price = (int)Json_Num(e, "price", 0);
        it->level_min = (int)Json_Num(e, "min_level", 1);
        it->bit = i;                                /* which pack of this shop */
        it->kind = ECO_ITEM_PACK;
        it->owned = (int)Json_Num(e, "count", 5);   /* how many cards it holds */
        it->locked = Eco_Level() < it->level_min;
        snprintf(path, sizeof(path), "ui.pack_%s", kind);
        if (!strcmp(kind, "common")) snprintf(it->name, sizeof(it->name), "%s", EcoTr("ui.pack_common"));
        else snprintf(it->name, sizeof(it->name), "%s %s", EcoTr(path), EcoTr("ui.pack_common"));
        n++;
    }
    return n;
}

/* The spare copies: what the chest holds beyond what the deck uses, minus what may not be sold. */
int Eco_SellItems(EcoItem *out, int max)
{
    int id, n = 0, k;
    if (!eco) return 0;
    for (id = 1; id <= 722 && n < max; id++) {
        int have = owned_of(id), used = 0, price;
        if (have <= 0) continue;
        for (k = 0; k < 40; k++) if (gDuel_awPlayerDeck[k] == id) used++;
        if (have - used <= 0) continue;
        price = Eco_SellPrice(id);
        if (price <= 0) continue;
        add_item(out, &n, max, id, price, 1, -1, ECO_ITEM_SELL);
        out[n - 1].owned = have - used;             /* the spare copies, not the whole chest */
    }
    return n;
}

/* ------------------------------------------------------- buying, selling */
int Eco_Buy(const EcoItem *it)
{
    if (!it || it->locked || it->card <= 0) return 0;
    if (!Eco_TakeCoins(it->price)) return 0;
    if (it->kind == ECO_ITEM_ONCE && it->bit >= 0 && it->bit < 64)
        jm.eco.bought[it->bit / 32] |= 1u << (it->bit % 32);
    Story_Cards(it->card);                          /* the chest, and the save list of given cards */
    LOG("journey: bought card %d for %d (%d coins left)", it->card, it->price, jm.eco.coins);
    return 1;
}

int Eco_Sell(const EcoItem *it)
{
    if (!it || it->card <= 0 || it->owned <= 0) return 0;
    if (Eco_Protected(it->card) || owned_of(it->card) <= 0) return 0;
    gLibrary_abCardChest[it->card]--;
    Eco_GiveCoins(it->price);
    LOG("journey: sold card %d for %d", it->card, it->price);
    return 1;
}

/* A pack: each slot is a fixed class or a roll between classes, picked out of the shop pool. */
int Eco_OpenPack(int index, int *cards, int max)
{
    JsonNode *packs = shop ? Json_Get(shop, "packs") : NULL;
    JsonNode *pack = Json_At(packs, index), *slots, *s, *pool;
    int n = 0, level = Eco_Level();
    pool = Json_Get(Json_Get(eco, "pools"), Json_Str(shop, "pool", ""));
    if (!pack || !pool) return 0;
    for (slots = Json_Get(pack, "slots"), s = slots ? slots->child : NULL; s && n < max; s = s->next) {
        JsonNode *odds = Json_Get(s, "odds"), *e;
        const char *want = Json_Str(s, "rarity", NULL);
        int weight = 0, roll, sum = 0;
        if (!want && odds) {                        /* a slot that rolls between classes */
            JsonNode *o;
            int total = 0, r;
            for (o = odds->child; o; o = o->next) total += (int)o->num;
            r = total > 0 ? rand() % total : 0;
            for (o = odds->child; o; o = o->next) {
                sum += (int)o->num;
                if (r < sum) { want = o->key; break; }
            }
            sum = 0;
        }
        if (!want) want = "C";
        for (e = pool->child; e; e = e->next)
            if (!strcmp(Json_Str(e, "r", "C"), want) && (int)Json_Num(e, "l", 1) <= level &&
                !(int)Json_Num(e, "a", 0)) weight += (int)Json_Num(e, "w", 1);
        if (weight <= 0) continue;
        roll = rand() % weight;
        for (e = pool->child; e; e = e->next) {
            if (strcmp(Json_Str(e, "r", "C"), want) || (int)Json_Num(e, "l", 1) > level ||
                (int)Json_Num(e, "a", 0)) continue;
            sum += (int)Json_Num(e, "w", 1);
            if (roll < sum) { cards[n++] = (int)Json_Num(e, "i", 0); break; }
        }
    }
    return n;
}
