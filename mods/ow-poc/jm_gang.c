/* The Dune Jackals: the duelling gang that shadows the player and robs him.
 *
 * The design (journey_content/economy/gang.json) had them spawn off the edge of the view when a
 * countdown ran out.  They are in the place instead: two of them loiter wherever the player is, in
 * plain sight, and the countdown is what makes one of them walk over and find his excuse.  The
 * timing the design balanced is untouched - only what the player sees before it fires.
 *
 * The clock runs on walking, not on wall time: jm.eco.amb_cd is 30ths of a second of walking left,
 * so standing still never brings them, and running covers the same ground faster.  Everything they
 * do is in the Economy block of the save, so a loaded game picks the countdown up where it was.
 *
 * They have no art yet.  Until there is some they are drawn from a villager's sheet, each with a
 * colour of his own, which costs no texture page (jm_painted.c keeps the pages full as it is).
 */
#include "jm.h"
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

static JsonNode *gang;                  /* the "gang" block of assets/economy.json */
static int pending;                     /* an ambush is due: ow_poc starts it at a safe moment */
static int member_now = -1;             /* which member is doing it, an index into "members" */
static int grace;                       /* walking frames before the clock may run again */
static int last_area = -1;

static JsonNode *members(void) { return gang ? Json_Get(gang, "members") : NULL; }
static JsonNode *ambush(void) { return gang ? Json_Get(gang, "ambush") : NULL; }
static JsonNode *member_at(int i) { return Json_At(members(), i); }

int Gang_Load(void)
{
    gang = Eco_Block("gang");
    if (gang) LOG("journey: gang (%d members)", Json_Count(members()));
    return gang != NULL;
}

/* The place the player is in, by the id the data uses.  Only the home arc exists, so the painted
 * village and the cistern are all there is to tell apart; later parts add their own. */
static const char *area_id(void) { return paint_area_now() == 2 ? "arena" : Paint_AreaId(); }

/* Is this a place they work?  The cistern, indoors and the ship are not. */
static int area_ok(void)
{
    JsonNode *list = Json_Get(ambush(), "areas"), *n;
    const char *here = area_id();
    for (n = list ? list->child : NULL; n; n = n->next)
        if (n->str && !strcmp(n->str, here)) return 1;
    return 0;
}

/* ------------------------------------------------------------ who they are */
static int tier_now(void)
{
    JsonNode *rows = Json_Get(gang, "tier_by_level"), *r, *w, *n;
    int level = Eco_Level(), roll, sum = 0;
    for (r = rows ? rows->child : NULL; r; r = r->next) {
        if (level < (int)Json_Num(r, "from", 1) || level > (int)Json_Num(r, "to", 99)) continue;
        w = Json_Get(r, "weights");
        roll = rand() % 100;
        for (n = w ? w->child : NULL; n; n = n->next) {
            sum += (int)n->num;
            if (roll < sum) return atoi(n->key ? n->key : "1");
        }
        return 1;
    }
    return 1;
}

/* A member of that tier, or the one the tutorial names for the very first ambush. */
static int pick_member(void)
{
    JsonNode *m;
    int i, n = Json_Count(members()), tier, best = -1, seen = 0;
    if (!jm.eco.amb_first_done) {
        const char *first = Json_Str(ambush(), "first_member", "");
        for (i = 0; i < n; i++)
            if (!strcmp(Json_Str(member_at(i), "id", ""), first)) return i;
    }
    tier = tier_now();
    for (i = 0; i < n; i++) {           /* one of that tier, at random among them */
        m = member_at(i);
        if ((int)Json_Num(m, "tier", 1) != tier) continue;
        if (rand() % ++seen == 0) best = i;
    }
    if (best < 0) best = n > 0 ? rand() % n : -1;
    return best;
}

/* ---------------------------------------------------------- where they wait
 * They stand about the place, not on top of the player: a handful of spots, two of them taken, and
 * which two changes as the player duels, so the same corner is not theirs for ever. */
static const char *const hangouts[] = {"east_road", "notice_sign", "date_palm", "river_bank", "plaza_center", "bakery_door"};
#define HANGOUTS ((int)(sizeof(hangouts) / sizeof(hangouts[0])))

int Gang_Figures(GangFigure *out, int max)
{
    int n = 0, i, count = Json_Count(members());
    unsigned seed;
    if (!gang || !area_ok() || !Gang_Present() || count <= 0) return 0;
    seed = (unsigned)jm.duels * 2654435761u + (unsigned)jm.stage * 97u;
    for (i = 0; i < 2 && n < max; i++) {
        int spot = (int)((seed >> (i * 5)) % HANGOUTS);
        int who = (int)((seed >> (i * 7 + 3)) % (unsigned)count);
        float x, y;
        if (!Paint_Anchor(hangouts[spot], &x, &y)) continue;
        out[n].x = x + (i ? 34.0f : -34.0f);      /* two of them, a step apart */
        out[n].y = y + (i ? 8.0f : 0.0f);
        out[n].member = who;
        out[n].tint = (unsigned)Json_Num(member_at(who), "tint", 0);
        n++;
    }
    return n;
}

/* ------------------------------------------------------------- the clock */
/* Being there and being ready to rob are not the same thing.  They are about the place from the
 * point of the story they turn up, and the player sees them from the first moment; the warm-up the
 * design asks for only holds back the first ambush, so the opening minutes are watched, not robbed. */
int Gang_Present(void)
{
    if (!gang || !Eco_Ready()) return 0;
    if (jm.eco.eco_bits & ECO_TRUCE) return 1;          /* beaten, and still about */
    return jm.stage >= (int)Json_Num(ambush(), "stage_min", 3);
}

int Gang_Awake(void)
{
    if (!Gang_Present()) return 0;
    if (jm.eco.eco_bits & ECO_TRUCE) return 1;
    return jm.eco.amb_walk >= (int)Json_Num(ambush(), "warmup", 0);
}

static int cooldown_roll(void)
{
    int lo = (int)Json_Num(ambush(), "cooldown_min", 2250);
    int hi = (int)Json_Num(ambush(), "cooldown_max", 4500);
    int span = hi > lo ? hi - lo : 1;
    int cd = lo + rand() % span;
    JsonNode *st = Json_Get(gang, "stakes");
    if (jm.eco.eco_bits & ECO_TRUCE) cd = cd * 2;        /* the truce halves how often they come */
    if (jm.eco.amb_streak >= (unsigned char)Json_Num(st, "relief_after", 2))
        cd = (int)(cd * Json_Num(st, "relief_cooldown", 1.5));
    return cd;
}

/* ------------------------------------------------------- standing too close
 * Two of them watch the place.  Walk into the ground one is holding and stay there, and he stops
 * waiting: three seconds is long enough that it is the player's choice, short enough to be a threat.
 *
 * This runs beside the walking countdown, not instead of it - keeping away is not safe either - and
 * it does not wait for the tutorial warm-up, because going up to them is a deliberate act. */
/* Their ground, in picture texels.  The view shows 640 x 480 of them (TPU 2), so 200 is about a
 * third of the screen across: they notice someone who comes into their corner of the square, not
 * only someone standing on their feet.  A person's talking reach, for comparison, is 84. */
#define DWELL_REACH 150.0f
#define DWELL_FRAMES 180            /* about five seconds of standing in it */
#define HUNT_SPEED 3                /* ... and about a third of that once they are looking for him */
static int dwell, dwell_member = -1, dwell_slot = -1;
static int hunting;                 /* the long countdown ran out: the next one they see, they take */

int Gang_Dwell(void) { return dwell; }
float Gang_Reach(void) { return DWELL_REACH; }

/* How much attention the figure in this slot is paying, 0 to 100.  The village draws a mark over
 * the head of whoever is above 0, so being noticed is something the player sees coming. */
int Gang_AlertAt(int slot)
{
    if (slot != dwell_slot || dwell <= 0) return 0;
    return dwell * 100 / DWELL_FRAMES;
}

void Gang_Near(float px, float py)
{
    GangFigure g[4];
    int n, i, close = -1;
    /* The grace is a moment of being left alone, so it passes with the moment.  It used to run down
     * only while the player walked, which meant that standing still after a scene held it for ever
     * and they never noticed anyone: the mark appeared or not depending on what had just happened. */
    if (grace > 0) grace--;
    if (!gang || pending || !Gang_Present() || grace > 0) { dwell = 0; return; }
    if (jm.eco.coins < (int)Json_Num(ambush(), "min_purse", 25)) { dwell = 0; return; }   /* nothing to take */
    n = Gang_Figures(g, 4);
    for (i = 0; i < n; i++) {
        float dx = px - g[i].x, dy = py - g[i].y;
        if (dx * dx + dy * dy < DWELL_REACH * DWELL_REACH) { close = i; break; }
    }
    if (close < 0) { dwell = 0; dwell_slot = dwell_member = -1; return; }
    if (close != dwell_slot) { dwell_slot = close; dwell = 0; }   /* a different one: start again */
    dwell_member = g[close].member;
    dwell += hunting ? HUNT_SPEED : 1;
    if (dwell >= DWELL_FRAMES) {
        dwell = 0;
        dwell_slot = -1;
        hunting = 0;
        pending = 1;
        member_now = dwell_member;
        LOG("journey: stood by %s for too long", Json_Str(member_at(dwell_member), "id", "?"));
    }
}

/* Called from the painted village for every frame the player actually moves. */
void Gang_Walked(int frames)
{
    if (frames <= 0) return;
    jm.eco.amb_walk += frames;
    if (!Gang_Awake() || pending) return;
    if (grace > 0) return;              /* it runs down with time, in Gang_Near, not with walking */
    if (!area_ok()) return;
    if (jm.eco.coins < (int)Json_Num(ambush(), "min_purse", 25)) return;   /* nothing worth taking */
    if (jm.eco.amb_cd <= 0) { jm.eco.amb_cd = cooldown_roll(); return; }
    jm.eco.amb_cd -= frames;
    /* It used to take the player then and there, wherever he was - which, now that their ground is
     * drawn, reads as being robbed out of nowhere.  Instead it puts them on the hunt: the mark fills
     * three times as fast the next time he comes near one, so they still get him, and he sees it. */
    if (jm.eco.amb_cd <= 0 && !hunting) {
        hunting = 1;
        jm.eco.amb_cd = cooldown_roll();
        LOG("journey: the Jackals are looking for the player");
    }
}

void Gang_Grace(int which)
{
    const char *key = which == GANG_GRACE_WIN ? "grace_win" : which == GANG_GRACE_LOSS ? "grace_loss"
                    : which == GANG_GRACE_AREA ? "grace_area" : "grace_scene";
    int g = (int)Json_Num(ambush(), key, 300);
    if (g > grace) grace = g;
    /* A duel settles the account, so the next one is rolled afresh.  A scene, a menu or walking into
     * another place only holds them off for a moment: the countdown keeps what it had.  Clearing it
     * every time would mean a player who talks to anyone is never ambushed at all. */
    if (which == GANG_GRACE_WIN || which == GANG_GRACE_LOSS) jm.eco.amb_cd = 0;
}

/* The area changed: they are already in the new one, but give the player a moment. */
void Gang_Area(void)
{
    int a = paint_area_now();
    if (a == last_area) return;
    last_area = a;
    Gang_Grace(GANG_GRACE_AREA);
}

int Gang_Pending(void) { return pending; }
int Gang_Member(void) { return member_now; }

const char *Gang_Line(const char *kind)
{
    JsonNode *m = member_at(member_now);
    char key[32];
    if (!m) return "";
    snprintf(key, sizeof(key), "%s_id", kind);
    return EcoDlg(Json_Str(m, key, ""));
}

const char *Gang_Name(void)
{
    JsonNode *m = member_at(member_now);
    return m ? Json_Str(m, "name", "?") : "";
}

/* The duelist the host gave this member this run (it depends on the mods applied). */
int Gang_Duelist(void)
{
    JsonNode *m = member_at(member_now);
    char identity[48];
    if (!m) return 0;
    snprintf(identity, sizeof(identity), "ow-poc:%s", Json_Str(m, "duelist", ""));
    return jm_host->duelist_id(jm_host, identity);
}

int Gang_Tier(void)
{
    JsonNode *m = member_at(member_now);
    return m ? (int)Json_Num(m, "difficulty", 1) : 1;
}

/* ------------------------------------------------------------ the stakes */
static int stolen_coins(void)
{
    JsonNode *st = Json_Get(gang, "stakes"), *m = member_at(member_now);
    char key[8];
    double pct;
    int lo, hi, take;
    if (!st || !m) return 0;
    snprintf(key, sizeof(key), "%d", (int)Json_Num(m, "tier", 1));
    pct = Json_Num(Json_Get(st, "pct"), key, 0.1);
    lo = (int)Json_Num(Json_Get(st, "min"), key, 10);
    hi = (int)Json_Num(Json_Get(st, "max"), key, 120);
    take = (int)(jm.eco.coins * pct + 0.5);
    if (take < lo) take = lo;
    if (take > hi) take = hi;
    if (!jm.eco.amb_first_done) {       /* the first one is a lesson, not a robbery */
        int cap = (int)Json_Num(ambush(), "first_cap", 20);
        if (take > cap) take = cap;
    } else if (jm.eco.amb_won + jm.eco.amb_lost < 3) {
        take = (int)(take * Json_Num(st, "first_three", 0.5));
    }
    if (jm.eco.amb_streak >= (unsigned char)Json_Num(st, "relief_after", 2))
        take = (int)(take * Json_Num(st, "relief_stolen", 0.5));
    if (jm.eco.eco_bits & ECO_TRUCE) take = (int)(take * Json_Num(st, "truce", 0.5));
    if (take > jm.eco.coins) take = jm.eco.coins;        /* never below nothing */
    return take < 0 ? 0 : take;
}

/* What the duel did.  A win pays the ambush rate and gives back half of what the last one took; a
 * loss costs coins, and nothing else - there is no game over in Journey Mode. */
void Gang_Result(int won)
{
    JsonNode *m = member_at(member_now);
    char line[64];
    int tier = Gang_Tier();
    pending = 0;
    jm.eco.amb_first_done = 1;
    if (!m) return;
    if (won) {
        int back = (int)(jm.eco.gang_loot * Json_Num(Json_Get(gang, "stakes"), "recover", 0.5));
        jm.eco.amb_won++;
        jm.eco.amb_streak = 0;
        Eco_GiveCoins(Eco_WinCoins(tier, "ambush_win"));
        Eco_GiveXp(Eco_WinXp(tier));
        if (back > 0) {
            Eco_GiveCoins(back);
            jm.eco.gang_loot -= back;
            Ui_Fmt1(line, sizeof(line), EcoTr("ui.ambush_recovered"), back);
            Eco_Note(line, 1);
        }
        if (!strcmp(Json_Str(m, "id", ""), "old_jackal") && !(jm.eco.eco_bits & ECO_TRUCE)) {
            jm.eco.eco_bits |= ECO_TRUCE;               /* the boss is beaten: they ease off for good */
            Eco_Note(EcoTr("ui.ambush_truce"), 1);
        }
        Gang_Grace(GANG_GRACE_WIN);
    } else {
        int take = stolen_coins();
        jm.eco.amb_lost++;
        if (jm.eco.amb_streak < 250) jm.eco.amb_streak++;
        Eco_GiveXp(Eco_LossXp(tier));
        if (take > 0) {
            jm.eco.coins -= take;
            jm.eco.gang_loot = take;
            Ui_Fmt1(line, sizeof(line), EcoTr("ui.ambush_lost"), take);
            Eco_Note(line, 1);
        } else Eco_Note(EcoTr("ui.ambush_nothing"), 1);
        Gang_Grace(GANG_GRACE_LOSS);
    }
    LOG("journey: ambush %s (won %d, lost %d, purse %d)", won ? "won" : "lost",
        jm.eco.amb_won, jm.eco.amb_lost, jm.eco.coins);
    member_now = -1;
}

/* For Dev mode: every condition that decides whether they are here and whether they may rob, so a
 * "they do not show up" can be read off the screen instead of guessed at. */
void Gang_Debug(char *out, size_t size)
{
    GangFigure g[4];
    int n = gang ? Gang_Figures(g, 4) : 0;
    snprintf(out, size, "gang: data%d stage%d/%d area%d(%s) present%d awake%d walk%ds cd%ds purse%d fig%d",
             gang ? 1 : 0, jm.stage, gang ? (int)Json_Num(ambush(), "stage_min", 3) : -1,
             gang ? area_ok() : 0, area_id(), Gang_Present(), Gang_Awake(),
             jm.eco.amb_walk / 30, jm.eco.amb_cd / 30, jm.eco.coins, n);
    {   /* how long the player has been standing in one of their spots */
        size_t k = strlen(out);
        if (k + 32 < size) snprintf(out + k, size - k, " dwell%d/%d hunt%d", dwell, DWELL_FRAMES, hunting);
    }
}

/* Debug: skip the warm-up and the countdown, so the next step brings one of them over.  Testing an
 * ambush otherwise means several minutes of walking without stopping, which is the design's pacing
 * but no way to try the fight. */
int Gang_Force(void)
{
    if (!gang || !Eco_Ready()) return 0;
    jm.eco.amb_walk = (int)Json_Num(ambush(), "warmup", 0);   /* past the tutorial grace */
    if (jm.stage < (int)Json_Num(ambush(), "stage_min", 3)) jm.stage = (int)Json_Num(ambush(), "stage_min", 3);
    if (jm.eco.coins < (int)Json_Num(ambush(), "min_purse", 25))
        Eco_GiveCoins((int)Json_Num(ambush(), "min_purse", 25) - jm.eco.coins);   /* they want something to take */
    grace = 0;
    jm.eco.amb_cd = 1;                  /* the next walked frame runs it out */
    pending = 0;
    return 1;
}

void Gang_Cancel(void) { pending = 0; member_now = -1; dwell = 0; dwell_slot = -1; Gang_Grace(GANG_GRACE_SCENE); }
