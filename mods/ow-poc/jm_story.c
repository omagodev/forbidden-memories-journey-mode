/* Journey Mode story: the rules in assets/journey.json (who says what, when, and what a win gives),
 * the scenes in assets/story.json, and the dialogue, which is the game's own text box.
 *
 * Both files are data, so the story is changed without touching this code; their format is in
 * notes/journey-mode.md.  Flags are named in journey.json ("flags") and kept as bits of Journey.flags. */
#include "types.h"
#include "psyq/libgte.h"
#include "psyq/libgpu.h"
#include "psyq/libgs.h"
#include "game/ordering_tables.h"
#include "game/duel_effect.h"
#include "game/text_box_lifecycle.h"
#include "pc/platform/mod_mode.h"
#include "pc/text/glyphs.h"
#include "jm.h"
extern void Cards_MarkSeen(int id);
extern int Cards_Seen(int id);
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

Journey jm;
JsonNode *jm_rules;                   /* assets/journey.json */
static JsonNode *story;               /* assets/story.json */
static JsonNode *scenes;              /* its "scenes" array */
extern u8 gLibrary_abCardChest[];

#define MAX_FLAGS 96
static char flag_names[MAX_FLAGS][24];
static int flag_count;

int Story_Load(void)
{
    char *text;
    JsonNode *f;
    int i;
    if (jm_rules) return 1;
    text = Jm_ReadText("assets/journey.json");
    if (text) { jm_rules = Json_Parse(text); free(text); }
    if (!jm_rules) { LOG("journey: story data missing or not JSON"); return 0; }
    f = Json_Get(jm_rules, "flags");
    for (i = 0; f && i < Json_Count(f) && i < MAX_FLAGS; i++) {
        JsonNode *n = Json_At(f, i);
        strncpy(flag_names[i], n->str ? n->str : "", sizeof(flag_names[0]) - 1);
        flag_count++;
    }
    LOG("journey: %d flags", flag_count);
    return 1;
}

/* The scripts of one language: assets/lang/<code>/story.json. */
void Story_LoadScenes(const char *code)
{
    char path[80], *text;
    JsonNode *j = NULL;
    snprintf(path, sizeof(path), "assets/lang/%s/story.json", code);
    text = Jm_ReadText(path);
    if (text) { j = Json_Parse(text); free(text); }
    if (!j) { LOG("journey: cannot read %s", path); return; }
    if (story) Json_Free(story);
    story = j;
    scenes = Json_Get(story, "scenes");
    if (!scenes) scenes = Json_Get(story, "scripts");
    LOG("journey: %d scenes (%s)", Json_Count(scenes), code);
}

int Story_FlagBit(const char *name)
{
    int i;
    for (i = 0; i < flag_count; i++)
        if (!strcmp(flag_names[i], name)) return i;
    return -1;
}

int Story_Has(const char *flag)
{
    int b = Story_FlagBit(flag);
    if (b >= 64) return jm.kflags2 >> (b - 64) & 1;
    if (b >= 32) return jm.kflags >> (b - 32) & 1;
    return b >= 0 && (jm.flags >> b & 1);
}

void Story_Set(const char *flag)
{
    int b = Story_FlagBit(flag);
    if (b >= 64) jm.kflags2 |= 1u << (b - 64);
    else if (b >= 32) jm.kflags |= 1u << (b - 32);
    else if (b >= 0) jm.flags |= 1u << b;
}

/* a flag that lasts only while the hero stays in one place (jm_painted.c clears "inseto_here" when the area changes) */
void Story_Unset(const char *flag)
{
    int b = Story_FlagBit(flag);
    if (b >= 64) jm.kflags2 &= ~(1u << (b - 64));
    else if (b >= 32) jm.kflags &= ~(1u << (b - 32));
    else if (b >= 0) jm.flags &= ~(1u << b);
}

void Story_Reset(void)
{
    memset(&jm, 0, sizeof(jm));
    strncpy(jm.name, Tr("defaults.player_name"), sizeof(jm.name) - 1);
    if (!strcmp(jm.name, "defaults.player_name")) strcpy(jm.name, "Hero");   /* before a language is loaded */
    jm.lang = Lang_Current();
    jm.hair_col = 0;
}

/* ------------------------------------------------------------ conditions */
static int all_set(const JsonNode *list)
{
    JsonNode *n;
    for (n = list ? list->child : NULL; n; n = n->next)
        if (n->str && !Story_Has(n->str)) return 0;
    return 1;
}

static int none_set(const JsonNode *list)
{
    JsonNode *n;
    for (n = list ? list->child : NULL; n; n = n->next)
        if (n->str && Story_Has(n->str)) return 0;
    return 1;
}

static int any_unset(const JsonNode *list)
{
    JsonNode *n;
    for (n = list ? list->child : NULL; n; n = n->next)
        if (n->str && !Story_Has(n->str)) return 1;
    return 0;
}

/* {"stage_ge", "stage_lt", "row_lt", "row_gt" (the player's tile row), "needs"/"has" (all set), "lacks" (none
 * set), "lacks_any" (at least one not set)}; no condition always holds. */
static int cond(const JsonNode *c)
{
    int row = (int)(jm.z / 32.0f);
    if (!c) return 1;
    if (Json_Get(c, "stage_ge") && jm.stage < (int)Json_Num(c, "stage_ge", 0)) return 0;
    if (Json_Get(c, "stage_lt") && jm.stage >= (int)Json_Num(c, "stage_lt", 99)) return 0;
    if (Json_Get(c, "row_lt") && row >= (int)Json_Num(c, "row_lt", 0)) return 0;
    if (Json_Get(c, "row_gt") && row <= (int)Json_Num(c, "row_gt", 0)) return 0;
    if (Json_Get(c, "area") && paint_area_now() != (int)Json_Num(c, "area", 0)) return 0;
    if (Json_Get(c, "stars_min") && jm.stars < (int)Json_Num(c, "stars_min", 0)) return 0;
    /* "earned_min": the stars the story has handed out so far (held, plus those a loss left with a duelist until he is beaten) */
    if (Json_Get(c, "earned_min") && jm.stars + jm.stars_owed < (int)Json_Num(c, "earned_min", 0)) return 0;
    if (Json_Get(c, "earned_lt") && jm.stars + jm.stars_owed >= (int)Json_Num(c, "earned_lt", 0)) return 0;
    if (Json_Get(c, "wager_extra")) {   /* [slot, count, beaten flag]: a beaten star duelist still holds stars he won from the hero */
        const JsonNode *we = Json_Get(c, "wager_extra");
        int sl = Json_At(we, 0) ? (int)Json_At(we, 0)->num : 0, base = Json_At(we, 1) ? (int)Json_At(we, 1)->num : 1;
        const char *bf = Json_At(we, 2) ? Json_At(we, 2)->str : NULL;
        if (Wager_HeldRaw(sl, base, bf) <= base - 1 || jm.stars <= 0) return 0;
    }
    if (Json_Get(c, "coins_min") && jm.eco.coins < (int)Json_Num(c, "coins_min", 0)) return 0;
    if (Json_Get(c, "level_min") && Eco_Level() < (int)Json_Num(c, "level_min", 0)) return 0;
    if (Json_Get(c, "level_max") && Eco_Level() > (int)Json_Num(c, "level_max", 99)) return 0;
    if (!all_set(Json_Get(c, "needs")) || !all_set(Json_Get(c, "has"))) return 0;
    if (!none_set(Json_Get(c, "lacks"))) return 0;
    if (Json_Get(c, "lacks_any") && !any_unset(Json_Get(c, "lacks_any"))) return 0;
    return 1;
}

int Story_Cond(const JsonNode *c) { return cond(c); }

/* "auto" rules: {when, result, scene, then}: a state that holds starts them (journey.json); their "when" must rule out the new state, so they run once */
int Story_Auto(Talk *out)
{
    JsonNode *s = Json_Get(jm_rules, "auto"), *n;
    for (n = s ? s->child : NULL; n; n = n->next) {
        if (!cond(Json_Get(n, "when"))) continue;
        memset(out, 0, sizeof(*out));
        out->duel = -1;
        Story_ApplyResult(Json_Get(n, "result"));
        out->scene = Json_Str(n, "scene", NULL);
        out->then = Json_Str(n, "then", NULL);
        return out->scene != NULL;
    }
    return 0;
}

/* an item banner's text names the item: the icon journey.json gives it ("icon" of the item; the names are the language's) */
int Story_ItemIcon(const char *text, const char **file)
{
    JsonNode *o = Json_Get(jm_rules, "items"), *n;
    int i = 0;
    for (n = o ? o->child : NULL; n; n = n->next, i++) {
        const char *ic = Json_Str(n, "icon", NULL), *nm = TrAt("items", i, Json_Str(n, "name", ""));
        if (ic && nm[0] && strstr(text, nm)) { *file = ic; return 1; }
    }
    return 0;
}

const char *Story_Objective(void)
{
    JsonNode *o = Json_Get(jm_rules, "objectives"), *n;
    int i = 0;
    for (n = o ? o->child : NULL; n; n = n->next, i++)
        if (cond(Json_Get(n, "when"))) return TrAt("objectives", i, Json_Str(n, "text", ""));
    return "";
}

const char *Story_Chapter(void)
{
    JsonNode *o = Json_Get(jm_rules, "chapters"), *n;
    int i = 0;
    for (n = o ? o->child : NULL; n; n = n->next, i++)
        if (cond(Json_Get(n, "when"))) return TrAt("chapters", i, Json_Str(n, "text", ""));
    return "";
}

int Story_ItemList(char names[][32], int max)
{
    JsonNode *o = Json_Get(jm_rules, "items"), *n;
    int k = 0, i = 0;
    for (n = o ? o->child : NULL; n && k < max; n = n->next, i++)
        if (Story_Has(Json_Str(n, "flag", "")) && !(Json_Get(n, "until") && Story_Has(Json_Str(n, "until", "")))) {
            strncpy(names[k], TrAt("items", i, Json_Str(n, "name", "?")), 31);
            names[k++][31] = 0;
        }
    return k;
}

/* --------------------------------------------------------------- talking */
int Story_TalkRule(const Npc *npc, Talk *out)
{
    JsonNode *n;
    memset(out, 0, sizeof(*out));
    out->duel = -1;
    for (n = npc->rules ? npc->rules->child : NULL; n; n = n->next) {
        if (!cond(Json_Get(n, "when"))) continue;
        out->scene = Json_Str(n, "scene", NULL);
        out->duel = Json_Num(n, "duel", 0) != 0 ? (int)(npc - npcs) : -1;
        out->on_win = Json_Get(n, "win");
        out->on_lose = Json_Get(n, "lose");
        out->effects = Json_Get(n, "effects");
        out->pose = Json_Str(n, "pose", NULL);
        return out->scene != NULL;
    }
    return 0;
}

int Story_PoiAt(float x, float z, Talk *out)
{
    JsonNode *s = Json_Get(jm_rules, "spots"), *n;
    memset(out, 0, sizeof(*out));
    out->duel = -1;
    for (n = s ? s->child : NULL; n; n = n->next) {
        JsonNode *t = Json_Get(n, "tile");
        float dx, dz, r = (float)Json_Num(n, "reach", 40);
        if (!t || !cond(Json_Get(n, "when"))) continue;
        dx = x - (float)Json_At(t, 0)->num * 32.0f;
        dz = z - (float)Json_At(t, 1)->num * 32.0f;
        if (dx * dx + dz * dz < r * r) { out->scene = Json_Str(n, "scene", NULL); return out->scene != NULL; }
    }
    return 0;
}

int Story_Trigger(Talk *out, float *tp_x, float *tp_z, int *teleport)
{
    JsonNode *s = Json_Get(jm_rules, "triggers"), *n;
    memset(out, 0, sizeof(*out));
    out->duel = -1;
    *teleport = 0;
    for (n = s ? s->child : NULL; n; n = n->next) {
        JsonNode *tp;
        JsonNode *rc = Json_Get(n, "rect");
        if (!cond(Json_Get(n, "when"))) continue;
        if (rc && (jm.x < Json_At(rc, 0)->num * 32.0 || jm.z < Json_At(rc, 1)->num * 32.0 ||
                   jm.x >= (Json_At(rc, 2)->num + 1) * 32.0 || jm.z >= (Json_At(rc, 3)->num + 1) * 32.0))
            continue;
        jm.stage = (int)Json_Num(n, "set_stage", jm.stage);
        Story_ApplyResult(Json_Get(n, "result"));
        tp = Json_Get(n, "teleport");
        if (tp) {
            *tp_x = (float)Json_At(tp, 0)->num * 32.0f;
            *tp_z = (float)Json_At(tp, 1)->num * 32.0f;
            *teleport = 1;
        }
        out->scene = Json_Str(n, "scene", NULL);
        return 1;
    }
    return 0;
}

int Story_Cards(int id)
{
    int i;
    if (id < 1 || id > 722) return 0;
    if (gLibrary_abCardChest[id - 1] < 99) gLibrary_abCardChest[id - 1]++;   /* the chest's byte for card n is n - 1 */
    Cards_MarkSeen(id);
    LOG("journey: card %d given (seen %d)", id, Cards_Seen(id));                 /* the chest lists it by name (an unseen card is a blank row there) */
    for (i = 0; i < jm.got_count; i++)
        if (jm.got_cards[i] == id) return 1;
    if (jm.got_count < 48) jm.got_cards[jm.got_count++] = (unsigned short)id;
    return 1;
}

/* Mark recorded rewards seen; only legacy migration reconstructs missing copies. */
void Story_Regrant(void)
{
    int i, k;
    extern unsigned short gDuel_awPlayerDeck[40];
    for (i = 0; i < jm.got_count && i < 48; i++) {
        int id = jm.got_cards[i], in_deck = 0;
        for (k = 0; k < 40; k++) if (gDuel_awPlayerDeck[k] == id) in_deck = 1;
        /* Only legacy migration reconstructs rewards. A modern inventory may
         * legitimately have sold one; loading must not mint another copy. */
        if (!jm.cards_set && id >= 1 && id <= 722 && !in_deck && !gLibrary_abCardChest[id - 1]) gLibrary_abCardChest[id - 1] = 1;
        if (id >= 1 && id <= 722) Cards_MarkSeen(id);    /* older saves gave it without marking it seen */
    }
}

/* does this rule subtree give the card (a "cards" array holding id)? */
static int gives_card(const JsonNode *n, int id)
{
    for (; n; n = n->next) {
        if (n->key && !strcmp(n->key, "cards") && n->type == 'a') {
            const JsonNode *c;
            for (c = n->child; c; c = c->next) if (c->type == 'n' && (int)c->num == id) return 1;
        }
        if (n->child && gives_card(n->child, id)) return 1;
    }
    return 0;
}

/* who in the story gives a card (the duelist's name); NULL for a card from a shop or a pack */
const char *Story_CardGiver(int id)
{
    JsonNode *o = Json_Get(jm_rules, "npcs"), *n;
    for (n = o ? o->child : NULL; n; n = n->next)
        if (n->child && gives_card(n->child, id)) return Json_Str(n, "name", "?");
    return NULL;
}

/* the cards the story gave (not the shop's), in the order they came */
int Story_GotCards(int *out, int max)
{
    int i, k = 0;
    for (i = 0; i < jm.got_count && k < max; i++)
        if (Story_CardGiver(jm.got_cards[i])) out[k++] = jm.got_cards[i];
    return k;
}

/* the items held now, as indices of journey.json "items" */
int Story_Items(int *out, int max)
{
    JsonNode *o = Json_Get(jm_rules, "items"), *n;
    int k = 0, i = 0;
    for (n = o ? o->child : NULL; n && k < max; n = n->next, i++)
        if (Story_Has(Json_Str(n, "flag", "")) && !(Json_Get(n, "until") && Story_Has(Json_Str(n, "until", "")))) out[k++] = i;
    return k;
}

/* item i's name (the language's), icon file and flag */
const char *Story_ItemName(int i) { JsonNode *n = Json_At(Json_Get(jm_rules, "items"), i); return n ? TrAt("items", i, Json_Str(n, "name", "?")) : "?"; }
const char *Story_ItemFile(int i) { JsonNode *n = Json_At(Json_Get(jm_rules, "items"), i); return n ? Json_Str(n, "icon", NULL) : NULL; }
const char *Story_ItemFlag(int i) { JsonNode *n = Json_At(Json_Get(jm_rules, "items"), i); return n ? Json_Str(n, "flag", "") : ""; }
const char *Story_ItemKey(int i) { JsonNode *n = Json_At(Json_Get(jm_rules, "items"), i); return n ? Json_Str(n, "key", Json_Str(n, "flag", "")) : ""; }
int Story_ItemCount(int i)
{
    JsonNode *n = Json_At(Json_Get(jm_rules, "items"), i);
    return n && !strcmp(Json_Str(n, "count", ""), "stars") ? jm.stars : -1;
}

int jm_warp;
int jm_shop_req;                      /* an "open_shop" result asked for a shop: its screen opens after the scene */
char jm_shop_req_id[16];
float jm_warp_x, jm_warp_z;
int jm_pwarp;
char jm_pwarp_area[32], jm_pwarp_anchor[24];

/* 1 when every flag this result sets is set already: the duel has been won before, so it pays the
 * rematch rate.  A result that sets no flag cannot be told apart and counts as a first win. */
int Story_ResultDone(const JsonNode *r)
{
    JsonNode *f = r ? Json_Get(r, "flags") : NULL, *n;
    int any = 0;
    for (n = f ? f->child : NULL; n; n = n->next) {
        if (!n->str) continue;
        any = 1;
        if (!Story_Has(n->str)) return 0;
    }
    return any;
}

void Story_ApplyResult(const JsonNode *r)
{
    JsonNode *f, *c, *n;
    if (!r) return;
    for (f = Json_Get(r, "flags"), n = f ? f->child : NULL; n; n = n->next) {
        int was = Story_Has(n->str);
        Story_Set(n->str);
        /* a reward is only given once: the first time its flag is set */
        (void)was;
    }
    if (Json_Get(r, "teleport")) {
        JsonNode *tp = Json_Get(r, "teleport");
        jm_warp_x = (float)Json_At(tp, 0)->num * 32.0f;
        jm_warp_z = (float)Json_At(tp, 1)->num * 32.0f;
        jm_warp = 1;
    }
    if (Json_Get(r, "warp")) {         /* "warp": [area, anchor]: the painted player goes to a named place (the hatch, the stairs) */
        JsonNode *w = Json_Get(r, "warp");
        snprintf(jm_pwarp_area, sizeof(jm_pwarp_area), "%s", Json_At(w, 0) && Json_At(w, 0)->str ? Json_At(w, 0)->str : "");
        snprintf(jm_pwarp_anchor, sizeof(jm_pwarp_anchor), "%s", Json_At(w, 1) && Json_At(w, 1)->str ? Json_At(w, 1)->str : "");
        jm_pwarp = 1;
    }
    if (Json_Get(r, "stage") && jm.stage < (int)Json_Num(r, "stage", 0)) jm.stage = (int)Json_Num(r, "stage", 0);
    if (Json_Get(r, "stars")) {        /* "stars": n, the Star Passage's first chip; the kingdom's wagers are settled after a duel (ow_poc.c) */
        jm.stars += (int)Json_Num(r, "stars", 0);
        if (jm.stars > 10) jm.stars = 10;
        if (jm.stars < 0) jm.stars = 0;
    }
    for (c = Json_Get(r, "cards"), n = c ? c->child : NULL; n; n = n->next) Story_Cards((int)n->num);
    /* the economy's own results (journey_content/economy: "effects_new") */
    if (Json_Get(r, "give_coins")) Eco_GiveCoins((int)Json_Num(r, "give_coins", 0));
    if (Json_Get(r, "take_coins")) Eco_TakeCoins((int)Json_Num(r, "take_coins", 0));
    if (Json_Get(r, "give_xp")) Eco_GiveXp((int)Json_Num(r, "give_xp", 0));
    if (Json_Get(r, "open_shop")) {
        snprintf(jm_shop_req_id, sizeof(jm_shop_req_id), "%s", Json_Str(r, "open_shop", ""));
        jm_shop_req = 1;
    }
}

/* ----------------------------------------------------------------- scenes */
static const JsonNode *find_scene(const char *id)
{
    JsonNode *n;
    for (n = scenes ? scenes->child : NULL; n; n = n->next)
        if (!strcmp(Json_Str(n, "id", ""), id)) return n;
    return NULL;
}

int Story_PageCount(const char *id)
{
    const JsonNode *s = find_scene(id);
    return s ? Json_Count(Json_Get(s, "pages")) : 0;
}

int Story_Page(const char *id, int index, Page *out)
{
    const JsonNode *s = find_scene(id), *p;
    if (!s) return 0;
    p = Json_At(Json_Get(s, "pages"), index);
    if (!p) return 0;
    out->who = Json_Str(p, "speaker", Json_Str(p, "who", "narrator"));
    out->name = Json_Str(p, "label", NULL);
    out->text = Json_Str(p, "text", "");
    out->ask = Json_Num(p, "ask", 0) != 0;
    {
        const char *k = Json_Str(p, "kind", "");
        out->kind = !strcmp(k, "objective") ? 1 : !strcmp(k, "item") ? 2 : !strcmp(k, "complete") ? 3 : !strcmp(k, "caption") ? 4 : 0;
    }
    return 1;
}

/* -------------------------------------------------------------- dialogue */
extern void *Tower_CreateBox(s32 id, s32 x, s32 y, s32 width, s32 height, s32 flags);
#define LETTER 8
#define BOX_W 268
static unsigned char text[MOD_MODE_TEXT_SIZE];
static int tlen, tx;

static void tput(int b) { if (tlen < MOD_MODE_TEXT_SIZE - 8) text[tlen++] = (u8)b; }

static void tglyph(int code)
{
    if (code < 0) code = Glyphs_Code('?');
    if (code >= 0xF0) tput(0xF0 + (code >> 8));
    tput(code & 0xFF);
    tx += LETTER;
}

/* Expands {name} and {male|female} into `out` (UTF-8). */
static void expand(const char *s, char *out, size_t size)
{
    size_t n = 0;
    while (*s && n + 24 < size) {
        if (*s == '{') {
            const char *e = strchr(s, '}');
            char tag[40];
            size_t len = e ? (size_t)(e - s - 1) : 0;
            if (e && len < sizeof(tag)) {
                char *bar;
                memcpy(tag, s + 1, len);
                tag[len] = 0;
                bar = strchr(tag, '|');
                if (!strcmp(tag, "name")) { strcpy(out + n, jm.name); n += strlen(jm.name); }
                else if (bar) {
                    const char *pick = jm.gender ? bar + 1 : tag;
                    size_t k = jm.gender ? strlen(bar + 1) : (size_t)(bar - tag);
                    memcpy(out + n, pick, k);
                    n += k;
                }
                s = e + 1;
                continue;
            }
        }
        out[n++] = *s++;
    }
    out[n] = 0;
}

static void build_text(const char *name, const char *body, int ask)
{
    static char expanded[600];
    const char *s;
    int line = 0;
    expand(body, expanded, sizeof(expanded));
    s = expanded;
    tlen = 0;
    tx = 0;
    if (name && *name) {                    /* the speaker: first on the line, in the game's yellow text, then a colon */
        const char *n = name;
        tput(0xF8); tput(0x0A); tput(0x01);          /* secondary command 0A: text colour = ramp 1 (yellow) */
        while (*n) { uint32_t ch = Glyphs_NextCharacter(&n); tglyph(Glyphs_Code(ch)); }
        tglyph(Glyphs_Code(':'));
        tput(0xF8); tput(0x0A); tput(0x00);          /* back to white for the message */
        tglyph(0);
    }
    while (*s) {
        const char *w = s;
        int letters = 0, room = (BOX_W - tx) / LETTER;
        if (*s == ' ') { if (tx) tglyph(0); s++; continue; }
        {
            const char *p = w;
            while (*p && *p != ' ') { Glyphs_NextCharacter(&p); letters++; }
        }
        if (letters > room && tx) {
            if (++line % 3 == 0) tput(0xFA);
            else tput(0xFE);
            tx = 0;
            continue;
        }
        while (letters--) { uint32_t ch = Glyphs_NextCharacter(&s); tglyph(Glyphs_Code(ch)); }
    }
    if (!ask) tput(0xFA);                   /* a question has no page wait: the box stays up while it is answered */
    tput(0xFF);
    ModMode_SetText(text, tlen);
}

static DuelEffectChannel *box(void) { return &D_800EB0F8[0]; }
void Say_Close(void) { if (box()->flags_34 & 0x8000) TextBox_Destroy((struct DuelEffectChannel *)box()); }
int Say_Done(void) { return (box()->flags_34 & TEXT_BOX_FLAG_DONE) && !(box()->flags_34 & 0x08); }

void Say_Text(const char *name, const char *body, int ask)
{
    build_text(name, body, ask);
    Say_Close();
    Tower_CreateBox(MOD_MODE_TEXT_ID, 0x10, 0xA0, 0x120, 0x40, 0x20);
}

void Story_Expand(const char *text, char *out, int size) { expand(text, out, (size_t)size); }
