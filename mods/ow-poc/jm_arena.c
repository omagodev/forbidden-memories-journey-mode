/* The clandestine arenas: a ladder of four duels behind a door, for an entry fee.
 *
 * One arena to a place (journey_content/economy/arenas.json); the village's is a chalk ring in the
 * flour cellar under the bakery.  The player pays, fights rung after rung, and a loss ends the run -
 * the fee is gone and it is paid again to try afresh.  Clearing the fourth pays a purse, and the
 * first clear pays much more and gives a title.
 *
 * Where the run stands is in the save (jm.eco.arena[], three bits of rung and four of clears for
 * each), because every rung leaves this screen for the duel and comes back to it.
 *
 * The village door now leads to a painted flour cellar: Hakim stands on the far mark, the player
 * takes the empty challenger mark, and the villagers watch from both walls. This screen is opened
 * from that mark and remains the ladder/fee confirmation before the actual duel.
 */
#include "jm.h"
#include <math.h>
#include <stdio.h>
#include <string.h>

static JsonNode *arenas;
static JsonNode *here;                  /* the arena whose screen is open */
static char here_id[16];
static int here_index;                  /* its place in the data, which is its place in jm.eco.arena[] */
static int sel;                         /* 0 enter, 1 leave */
static int running;                     /* a rung is being fought */
static char note[64];
static int note_timer;
static unsigned generation;

int Arena_Load(void)
{
    arenas = Eco_Block("arenas");
    if (arenas) LOG("journey: arenas (%d)", Json_Count(arenas));
    return arenas != NULL;
}

/* --------------------------------------------------------- what the save says */
static int rung_of(int i) { return i >= 0 && i < 8 ? jm.eco.arena[i] & 7 : 0; }
static int clears_of(int i) { return i >= 0 && i < 8 ? (jm.eco.arena[i] >> 3) & 15 : 0; }
static int found_of(int i) { return i >= 0 && i < 8 ? (jm.eco.arena[i] >> 7) & 1 : 0; }
static void set_rung(int i, int rung)
{
    if (i < 0 || i >= 8) return;
    jm.eco.arena[i] = (unsigned char)((jm.eco.arena[i] & ~7) | (rung & 7));
}
static void add_clear(int i)
{
    int c = clears_of(i);
    if (i < 0 || i >= 8 || c >= 15) return;
    jm.eco.arena[i] = (unsigned char)((jm.eco.arena[i] & ~(15 << 3)) | ((c + 1) << 3));
}
static void set_found(int i)
{
    if (i >= 0 && i < 8) jm.eco.arena[i] |= 0x80;
}

/* ------------------------------------------------------------- the door */
static JsonNode *arena_of_area(int *index)
{
    JsonNode *n;
    const char *area = paint_area_now() == 0 ? "village" : paint_area_now() == 1 ? "cistern" : NULL;
    int i = 0;
    if (!area) return NULL;
    for (n = arenas ? arenas->child : NULL; n; n = n->next, i++) {
        const char *anchor = Json_Str(n, "entry_anchor", "");
        /* "village.arena_door": the place is the part before the dot */
        if (strncmp(anchor, area, strlen(area)) || anchor[strlen(area)] != '.') continue;
        if (index) *index = i;
        return n;
    }
    return NULL;
}

static int unlocked(JsonNode *a)
{
    JsonNode *u = Json_Get(a, "unlock");
    if (!u) return 1;
    if (Json_Get(u, "stage_min") && jm.stage < (int)Json_Num(u, "stage_min", 0)) return 0;
    if (Json_Get(u, "level_min") && Eco_Level() < (int)Json_Num(u, "level_min", 0)) return 0;
    return 1;
}

/* How far the player is from this place's arena door, in picture texels; -1 when there is no door
 * here.  The door can sit against a wall, where the player cannot stand on it, so the reach is
 * wider than a person's (TALK_REACH is 84) rather than the width of the hatch. */
#define DOOR_REACH 110.0f
float Arena_DoorDistance(float x, float y)
{
    JsonNode *a = arena_of_area(NULL);
    const char *anchor;
    float ax, ay, dx, dy;
    if (paint_area_now() != 0 || !a || !arenas) return -1.0f;
    anchor = Json_Str(a, "entry_anchor", "");
    anchor = strchr(anchor, '.');
    if (!anchor || !Paint_Anchor(anchor + 1, &ax, &ay)) return -1.0f;
    dx = x - ax;
    dy = y - ay;
    return (float)sqrt((double)(dx * dx + dy * dy));
}

int Arena_DoorAt(float x, float y)
{
    float d = Arena_DoorDistance(x, y);
    return d >= 0.0f && d < DOOR_REACH;
}

/* For Dev mode: why the door does or does not answer. */
void Arena_Debug(char *out, size_t size, float x, float y)
{
    float d = Arena_DoorDistance(x, y);
    JsonNode *a = arena_of_area(NULL);
    snprintf(out, size, "arena: data%d here%d dist%d/%d level%d/%d stage%d/%d fee%d/%d rung%d",
             arenas ? 1 : 0, a ? 1 : 0, (int)(d < 0 ? -1 : d), (int)DOOR_REACH,
             Eco_Level(), a ? (int)Json_Num(Json_Get(a, "unlock"), "level_min", 0) : -1,
             jm.stage, a ? (int)Json_Num(Json_Get(a, "unlock"), "stage_min", 0) : -1,
             jm.eco.coins, a ? (int)Json_Num(a, "fee", 0) : -1,
             a ? rung_of(here_index) : -1);
}

int Arena_Open(void)
{
    int index = 0;
    JsonNode *a = arena_of_area(&index);
    if (!a) return 0;
    here = a;
    here_index = index;
    snprintf(here_id, sizeof(here_id), "%s", a->key ? a->key : "");
    sel = 0;
    note[0] = 0;
    note_timer = 0;
    generation++;
    if (!found_of(index)) {             /* the first time it is seen it goes on the record */
        char line[64];
        set_found(index);
        snprintf(line, sizeof(line), EcoTr("ui.arena_found"), EcoTr(Json_Str(a, "name_id", "")));
        Eco_Note(line, 1);
    }
    return 1;
}

const char *Arena_Name(void) { return here ? EcoTr(Json_Str(here, "name_id", "")) : ""; }

/* ------------------------------------------------------------- the ladder */
static JsonNode *rung_at(int rung) { return here ? Json_At(Json_Get(here, "ladder"), rung) : NULL; }
static int rungs(void) { return here ? Json_Count(Json_Get(here, "ladder")) : 0; }

static void say(const char *s)
{
    snprintf(note, sizeof(note), "%s", s);
    note_timer = 180;
    generation++;
}

/* The opponent of the rung the run is on; ow_poc puts him in front of the player. */
int Arena_NextFighter(char *name, size_t size, int *tier)
{
    JsonNode *r = rung_at(rung_of(here_index));
    char identity[48];
    if (!r) return 0;
    snprintf(name, size, "%s", Json_Str(r, "name", "?"));
    if (tier) *tier = (int)Json_Num(r, "tier", 1);
    snprintf(identity, sizeof(identity), "ow-poc:%s", Json_Str(r, "duelist", ""));
    return jm_host->duelist_id(jm_host, identity);
}

const char *Arena_FighterLine(void)
{
    JsonNode *r = rung_at(rung_of(here_index));
    return r ? EcoDlg(Json_Str(r, "text_id", "")) : "";
}

int Arena_Running(void) { return running; }

/* A rung was fought.  A loss ends the run and the fee is lost; a win pays the rung and moves up, and
 * the top of the ladder pays the purse - much more the first time. */
void Arena_Result(int won)
{
    int rung = rung_of(here_index), last = rungs() - 1;
    JsonNode *r = rung_at(rung);
    char line[64];
    running = 0;
    if (!r) return;
    if (!won) {
        set_rung(here_index, 0);
        Eco_GiveXp(Eco_LossXp((int)Json_Num(r, "tier", 1)));
        say(EcoTr("ui.arena_run_over"));
        LOG("journey: arena %s run lost at rung %d", here_id, rung + 1);
        return;
    }
    Eco_GiveCoins((int)Json_Num(r, "coins", 0));
    Eco_GiveXp((int)Json_Num(r, "xp_base", 0));
    if (rung < last) {
        set_rung(here_index, rung + 1);
        Ui_Fmt1(line, sizeof(line), EcoTr("ui.arena_round"), rung + 2);
        say(line);
        return;
    }
    /* the ladder is cleared */
    {
        int first = clears_of(here_index) == 0;
        JsonNode *prize = Json_Get(here, first ? "first_clear" : "repeat_clear");
        set_rung(here_index, 0);
        add_clear(here_index);
        Eco_GiveCoins((int)Json_Num(prize, "coins", 0));
        say(EcoTr(first ? "ui.arena_first_clear" : "ui.arena_cleared"));
        Eco_Note(EcoTr("ui.arena_cleared"), 1);
        LOG("journey: arena %s cleared (%d times)", here_id, clears_of(here_index));
    }
}

/* ------------------------------------------------------------------ input */
int Arena_Input(unsigned short edge, int *start_duel)
{
    int fee = here ? (int)Json_Num(here, "fee", 0) : 0;
    *start_duel = 0;
    if (note_timer > 0) note_timer--;
    if (edge & (PAD_UP | PAD_DOWN | PAD_LEFT | PAD_RIGHT)) { sel ^= 1; generation++; }
    if (edge & (PAD_TRIANGLE | PAD_CIRCLE | PAD_START)) return 1;
    if (edge & PAD_CROSS) {
        if (sel == 1) return 1;
        if (!unlocked(here)) {
            char line[64];
            Ui_Fmt1(line, sizeof(line), EcoTr("ui.arena_need_level"),
                    (int)Json_Num(Json_Get(here, "unlock"), "level_min", 1));
            say(line);
            return 0;
        }
        if (rung_of(here_index) == 0) {         /* a new run is paid for; one in progress is not */
            if (!Eco_TakeCoins(fee)) { say(EcoTr("ui.arena_poor")); return 0; }
        }
        running = 1;
        *start_duel = 1;
        generation++;
    }
    return 0;
}

/* ---------------------------------------------------------------- drawing */
void Arena_Overlay(void)
{
    int w, h, s, vtop, vis, lh, pw, ph, px, py, i, n = rungs(), rung = rung_of(here_index);
    char buf[72];
    if (!here) return;
    Ui_Metrics(&w, &h, &s, &vtop, &vis);
    lh = Ui_LineH();
    jm_host->fill(jm_host, 0, 0, w, h, 0x05040E, 150);
    pw = w * 52 / 100;
    ph = lh * (n + 7);
    px = (w - pw) / 2;
    py = vtop + (vis - ph) / 2;
    if (py < vtop) py = vtop;
    Ui_Panel(px, py, pw, ph);

    Ui_Text(px + 14 * s, py + lh - lh / 3, Arena_Name(), 0xFFE9A0);
    Ui_Fmt1(buf, sizeof(buf), EcoTr("ui.money"), jm.eco.coins);
    Ui_Text(px + pw - jm_host->text_width(jm_host, buf, s) - 16 * s, py + lh - lh / 3, buf, 0xF0C860);
    Ui_Text(px + 14 * s, py + lh * 2 - lh / 3, EcoDlg(Json_Str(here, "tip_id", "")), 0x8890C0);

    for (i = 0; i < n; i++) {               /* the ladder, with where the run stands */
        JsonNode *r = rung_at(i);
        int ry = py + lh * (3 + i);
        unsigned rgb = i < rung ? 0x70A070 : i == rung ? 0xFFFFFF : 0x8A8A96;
        snprintf(buf, sizeof(buf), "%d. %s", i + 1, Json_Str(r, "name", "?"));
        if (i == rung && rung > 0) Ui_Text(px + 8 * s, ry, ">", 0x40E0E0);
        Ui_Text(px + 24 * s, ry, buf, rgb);
        if ((int)Json_Num(r, "champion", 0)) Ui_Text(px + pw - 90 * s, ry, EcoTr("ui.arena_champion"), 0xFFE9A0);
        snprintf(buf, sizeof(buf), "%d", (int)Json_Num(r, "coins", 0));
        Ui_Text(px + pw - 34 * s, ry, buf, 0xF0C860);
    }

    if (rung > 0) Ui_Fmt1(buf, sizeof(buf), EcoTr("ui.arena_round"), rung + 1);
    else Ui_Fmt1(buf, sizeof(buf), EcoTr("ui.arena_fee"), (int)Json_Num(here, "fee", 0));
    Ui_Text(px + 14 * s, py + lh * (n + 4), buf, 0xC8C8C8);
    if (clears_of(here_index) > 0) {
        Ui_Fmt1(buf, sizeof(buf), EcoTr("ui.status_arenas"), clears_of(here_index));
        Ui_Text(px + pw / 2, py + lh * (n + 4), buf, 0x8A8A96);
    }

    Ui_Text(px + 30 * s, py + lh * (n + 5) + lh / 2, EcoTr("ui.arena_enter"), sel == 0 ? 0x40E0E0 : 0x8A8A96);
    Ui_Text(px + pw / 2 + 30 * s, py + lh * (n + 5) + lh / 2, EcoTr("ui.arena_leave"), sel == 1 ? 0x40E0E0 : 0x8A8A96);
    Ui_Text(px + 16 * s + (sel ? pw / 2 : 0), py + lh * (n + 5) + lh / 2, ">", 0xFFFFFF);
    if (note_timer > 0) Ui_Text(px + 14 * s, py + ph - lh / 2, note, 0x60F060);
}

unsigned Arena_Signature(void)
{
    return 1234567891u + generation * 2246822519u + (unsigned)sel * 131u +
           (unsigned)jm.eco.coins * 1009u + (unsigned)jm.eco.arena[here_index & 7] * 7919u +
           (unsigned)(note_timer > 0) * 3331u;
}
