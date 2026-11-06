/* Journey Mode: a story mode with a walkable 3D world, run by a code mod (see notes/journey-mode.md).
 *
 *  - the title's button "ow-poc:journey" (mod.json) raises MEMORIES_EVENT_MENU; we answer with our
 *    own selection, and MEMORIES_EVENT_SCENE then hands the screen to ModMode (mode 13, the tower's
 *    slot, while the tower is not on: src/pc/platform/mod_mode.c);
 *  - the world is drawn each frame by our own projection into the ordering table (jm_gfx.c, jm_world.c);
 *  - people talk through the game's own text box (Tower_CreateBox, string id 0xFFF7 served by
 *    ModMode_Text); duels are the game's: func_80024DC8 arms one, D_8009B368 = 13 brings it back here;
 *  - the name is typed on the game's name-entry screen and the deck is edited on its deck editor;
 *    both return to this mode;
 *  - area music is the game's own BGM (SD_BGMPlay), progress is saved to a file in the data directory. */
#include "types.h"
#include "psyq/libgte.h"
#include "psyq/libgpu.h"
#include "psyq/libgs.h"
#include "game/ordering_tables.h"
#include "game/duel_effect.h"
#include "game/fade.h"
#include "game/func_80039794.h"
#include "game/sound.h"
#include "game/func_80024DC8.h"
#include "game/duel_rewards.h"
#include "game/display_object.h"
#include "game/duel_draw_status_numbers.h"
#include "pc/mods/modapi.h"
#include "pc/platform/mod_mode.h"
#include "jm.h"
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

extern u8 D_8009B26C, D_8009B26D, D_8009B26E, D_8009B268, D_8009B269, D_8009B368, D_8009B362;
extern void Tower_Background(s32 on);
extern u16 gDuel_awPlayerDeck[40];
extern u8 gLibrary_abCardChest[];
extern u32 gLibrary_dwStarchips;

const MemoriesModHost *jm_host;
int jm_save_requested, jm_save_ok, jm_name_entry_requested;
static int create_r;

/* The card a won duel drops.  The game picks one out of its own weighted table; while a Journey duel
 * is being fought the pool of the place it happens in picks instead (journey_content/economy), and
 * the game's own choice stands for every other duel, so Free Duel and the campaign are untouched. */
/* The card the duel just gave, shown turning in the air before the village comes back. */
static int card_show, card_age, card_back;
#define CARD_FRAMES 170
static s32 (*drop_original)(s32);
static int duel_live;                      /* a Journey duel is in flight */
static s32 drop_pick(s32 pool_index)
{
    if (duel_live && Eco_Ready()) {
        int id = Eco_RollDrop(Eco_DropContext());
        if (id > 0) { card_show = id; return id; }
    }
    {
        s32 id = drop_original ? drop_original(pool_index) : 0;
        if (duel_live && id > 0) card_show = (int)id;     /* the game's own pick is shown too */
        return id;
    }
}

enum { ST_CONFIRM, ST_CREATE, ST_WALK, ST_SCENE, ST_ASK, ST_MENU, ST_TO_DUEL, ST_LEAVE, ST_LANG, ST_MAP, ST_PAINT, ST_JOURNAL, ST_SHOP, ST_AMBUSH, ST_ARENA, ST_CARD, ST_WAGER, ST_GAMEOVER };
enum { REQ_NONE, REQ_NEW, REQ_CONTINUE };   /* what the title's NEW GAME / CONTINUE asked for */
enum { RET_NONE, RET_DUEL, RET_NAME, RET_DECK };
static int wager_bet, gameover_age;      /* the bet of the star duel being played; frames of the game-over screen */
static int state = ST_LEAVE, after_return = RET_NONE, menu_request = REQ_NONE;
static int paint_auto;   /* the painted village is the first thing a walk shows; L1 still toggles */
static int ready, choose_sel, lang_sel, minimap_on = 1;   /* choose_sel: the confirm box's cursor (0 start the new game, 1 cancel) */
static float pyaw = 3.14159265f;
static int walking, cooldown;
static unsigned frame_no;
static unsigned short pad_prev;
static int return_menu = 5;

/* the scene being shown */
static const char *scene_id;
static int scene_idx, scene_n, ask_sel;
static int scene_intro;                    /* the opening scene: the story starts when it ends */
static int scene_result;                   /* a duel's result scene: save when it ends */
static int duel_npc = -1;
static int duel_is_gang;                   /* the duel being fought is an ambush, not a story duel */
static int duel_is_arena;                  /* ... or a rung of an arena ladder */
static int arena_return;                   /* the duel came from the ladder: go back to it */

/* The gang duel uses a person of its own: the villagers in npcs[] are the story's, and a Jackal is
 * not one of them.  The last slot of the table is kept for whoever the economy puts in front of the
 * player - a Jackal now, an arena fighter later - so the duel code needs no special case. */
#define ECO_NPC (MAX_NPC - 1)
static void eco_opponent(const char *id, const char *name, int duelist)
{
    Npc *n = &npcs[ECO_NPC];
    memset(n, 0, sizeof(*n));
    snprintf(n->id, sizeof(n->id), "%s", id ? id : "");
    snprintf(n->name, sizeof(n->name), "%s", name ? name : "");
    n->duelist_id = duelist;
    n->portrait_id = duelist;
    n->hidden = 1;                         /* never placed in the world: he only duels */
}

/* The two duelists' faces beside their life points.
 *
 * The duel's life-point panel is one 64x40 picture of both sides, the opponent's half on top, and
 * the game slides it off the side of the screen between battles.  This hook runs where the game has
 * just queued the panel's digits, which is the one place that knows where the panel is this frame
 * and in which ordering table: the face and its frame go in beside it, at the same depth, so they
 * ride the slide with it and are layered with it.
 *
 * The opponent's face is read from the disc into the mod's page (Gfx_LoadFace), once per duel; the
 * player's is the portrait chosen in the Journey creator. Outside a Journey duel the hook does
 * nothing at all, so Free Duel and the campaign look as they always did.
 *
 * The numbers below are in the game's own pixels, measured from the panel's middle, which is where
 * duel_draw_status_numbers.c puts its digits from.  Nudge them if the face sits badly. */
#define FACE_SIZE 28               /* two compact portraits leave the centre of the board clear */
#define OPP_FACE_LEFT 92           /* opponent: portrait 188..216, LP half 224..288 */
#define PLAYER_FACE_LEFT 268       /* player: portrait 12..40, LP half 48..112 */
#define FACE_TOP 32                /* aligned with the opponent's half instead of touching the top */
#define FACE_EDGE 2                /* the frame around it */
static void (*panel_original)(DisplayObject *);
static int face_duelist = -1;      /* whose face is in the page */
static short opponent_face_x, opponent_face_y;
static short player_face_x, player_face_y;   /* where they went this frame, for names in the overlay */
static int face_on;

static void duel_face(int x, int y, int ax, int ay, DisplayObject *pos)
{
    Gfx_RectAt(x - FACE_EDGE, y - FACE_EDGE, FACE_SIZE + 2 * FACE_EDGE, FACE_SIZE + 2 * FACE_EDGE,
               200, 160, 60, pos->ot_index, pos->field_14 + 1u);
    Gfx_RectAt(x - 1, y - 1, FACE_SIZE + 2, FACE_SIZE + 2, 12, 14, 44, pos->ot_index, pos->field_14);
    Gfx_PortraitAt(x, y, FACE_SIZE, ax, ay, pos->ot_index, pos->field_14 - 1u);
}

static void panel_drawn(DisplayObject *widget)
{
    DisplayObject *pos;
    int duelist, panel_x, opponent_x, player_x, y, portrait;
    if (panel_original) panel_original(widget);
    face_on = 0;
    if (!duel_live || duel_npc < 0 || !ready) return;
    duelist = npcs[duel_npc].duelist_id;
    pos = (DisplayObject *)(void *)widget->field_50.word;
    if (!pos || duelist <= 0) return;
    panel_x = (int)pos->field_30.h.field_30;
    if (panel_x - 32 >= 320 || panel_x + 32 <= 0) return;   /* the game's panel completed its slide away */
    if (face_duelist != duelist) {         /* a disc read: once a duel, not once a frame */
        if (!Gfx_LoadFace(duelist)) return;
        face_duelist = duelist;
    }
    portrait = jm.portrait >= 0 && jm.portrait < 4 ? jm.portrait : 0;
    opponent_x = panel_x - OPP_FACE_LEFT;
    player_x = panel_x - PLAYER_FACE_LEFT;
    y = (int)pos->field_30.h.field_32 - FACE_TOP;
    duel_face(player_x, y, PORT_X + portrait * 48, PORT_Y, pos);
    duel_face(opponent_x, y, DYN_PORT_X, DYN_PORT_Y, pos);
    player_face_x = (short)player_x;
    player_face_y = (short)y;
    opponent_face_x = (short)opponent_x;
    opponent_face_y = (short)y;
    face_on = 1;
}

static const char *cur_name;                 /* the speaker of the page on screen: the nameplate above the text box */
static int cur_kind, notif_age;              /* a notification page (objective, item, complete, caption) is drawn as a banner, not as speech */
static char notif_text[300], notif_label[48];
static int dbg_age;                          /* frames a page / question has been open (debug skip) */
static const JsonNode *duel_win, *duel_lose;
static const char *scene_then;             /* a scene to play next */
static const JsonNode *scene_choice;       /* {yes, no} results of a Yes/No page that is not a duel */
static const JsonNode *scene_effects;      /* a talk rule's "effects": applied when its scene has been read (a rumor heard, a card given) */
static int pend_duel = -1;                 /* a duel to start when the ask page is answered yes */
static int portrait_x = -1, portrait_y;    /* atlas position of the speaker's face, -1 none */
static int loaded_face = -1;

/* area music and banner */
static int area = -1, area_cand = -1, area_count, area_timer, area_banner;

extern int Paint_Tick(unsigned short pad, unsigned short edge);
extern void Paint_Enter(void);
extern void Paint_Draw(const Mesh *body, const int body_rgb[5]);
extern void Paint_Set(float x, float y);
extern void Paint_Info(float *x, float *y, float *sx, float *sy);
extern int paint_view, paint_anim, paint_sway, paint_sprite;
extern const char *Paint_ModeName(void);
extern int Paint_NearNpc(void);
extern void Paint_TalkStart(int ow);
extern void Paint_TalkEnd(void);
extern int Paint_Target(float *tx, float *ty);
extern void Paint_MiniMap(int x, int y, int c, int s);
extern int paint_exit, paint_markers, paint_area;
extern int Paint_IsNight(void);
extern void Paint_PageEvent(const char *script, int page);
extern void Paint_SceneEnd(void);
extern int Paint_NearObject(void);
extern int Paint_Area(void);
extern void Paint_Warp(const char *area, const char *anchor);
extern int Paint_ObjectRule(int i, Talk *t);
extern void Paint_ObjectStart(int i, const char *pose);
static int in_paint_flow;                  /* a conversation (or the duel it leads to) began in the painted village: it returns there */
static int mini_big;

static const char *npc_name(int i) { return TrKey("npc_names", npcs[i].id, npcs[i].name); }

/* ----------------------------------------------------------------- scenes */
static void speaker(const Page *p, const char **name, int *ax, int *ay)
{
    const JsonNode *sp = Json_Get(Json_Get(jm_rules, "speakers"), p->who);
    int i, face = 0;
    *name = p->name;
    *ax = -1;
    *ay = 0;
    if (!strcmp(p->who, "atos") || !strcmp(p->who, "player")) {
        *name = jm.name;
        *ax = PORT_X + (jm.portrait % 4) * 48;
        *ay = PORT_Y;
        return;
    }
    if (sp && !strcmp(Json_Str(sp, "portrait", ""), "prince")) {
        *name = TrKey("speaker_names", p->who, Json_Str(sp, "name", "Prince"));
        *ax = PORT_X + 4 * 48;
        *ay = PORT_Y;
        return;
    }
    if (sp && strcmp(p->who, "narrator")) { *name = TrKey("speaker_names", p->who, Json_Str(sp, "name", p->name)); face = (int)Json_Num(sp, "portrait_id", 0); }
    for (i = 0; i < npc_count; i++)
        if (!strcmp(npcs[i].id, p->who)) { *name = npc_name(i); face = npcs[i].portrait_id; }
    if (!strcmp(p->who, "narrator")) face = 0;
    if (sp && Json_Str(sp, "portrait_file", NULL)) {       /* InsetoKaiba, Mago.dev: faces the disc does not have */
        const char *file = Json_Str(sp, "portrait_file", "");
        int key = -1000 - (int)(strlen(file) * 31 + (unsigned char)file[strlen(file) > 5 ? strlen(file) - 5 : 0]);
        if (key != loaded_face && Gfx_LoadFaceFile(file)) loaded_face = key;
        if (key == loaded_face) { *ax = DYN_PORT_X; *ay = DYN_PORT_Y; }
        return;
    }
    if (face > 0) {
        if (face != loaded_face && Gfx_LoadFace(face)) loaded_face = face;
        if (face == loaded_face) { *ax = DYN_PORT_X; *ay = DYN_PORT_Y; }
    }
}

static void open_page(void)
{
    Page p;
    const char *name;
    if (!Story_Page(scene_id, scene_idx, &p)) return;
    speaker(&p, &name, &portrait_x, &portrait_y);
    p.name = name;
    cur_kind = p.kind;
    notif_age = 0;
    LOG("journey: page %s %d kind %d", scene_id, scene_idx, p.kind);
    cur_name = (!p.kind && strcmp(p.who, "narrator")) ? name : NULL;
    if (p.kind) {                          /* not speech: a banner of its own, with a sound */
        Story_Expand(p.text, notif_text, sizeof(notif_text));
        snprintf(notif_label, sizeof(notif_label), "%s", p.kind == 4 && p.name ? p.name : "");
        Say_Close();
        portrait_x = -1;
        if (p.kind == 1) SD_SEPlayFull(7);
        else if (p.kind == 2) SD_SEPlayFull(47);
        else if (p.kind == 3) SD_SEPlayFull(48);
    } else Say_Text(cur_name, p.text, p.ask);
    state = ST_SCENE;
    dbg_age = 0;
    if (in_paint_flow) Paint_PageEvent(scene_id, scene_idx);     /* the sun sets, the observer shows */
}

/* music cues (defs used by begin_scene / duel return; exploration tick is below) */
static int music_cue = -1;
static const char *music_cue_tag;
static int track_cfg(const char *key);
static void Jm_MusicCue(int track, const char *tag);
static void Jm_MusicClear(void);

static void begin_scene(const char *id, int intro, int result)
{
    scene_id = id;
    scene_idx = 0;
    scene_n = id ? Story_PageCount(id) : 0;
    scene_intro = intro;
    scene_result = result;
    pend_duel = -1;
    if (scene_n < 1) { LOG("journey: no scene %s", id ? id : "(null)"); scene_then = NULL; scene_choice = NULL; state = ST_PAINT; if (in_paint_flow) { in_paint_flow = 0; Paint_TalkEnd(); } return; }
    LOG("journey: scene %s (%d pages)", id, scene_n);
    /* epic / festival cues for the Kingdom finale */
    if (id && !strcmp(id, "dk9_heishin_pre") && track_cfg("epic_heishin") >= 0)
        Jm_MusicCue(track_cfg("epic_heishin"), "epic_heishin");
    else if (id && !strcmp(id, "dk10_pegasus_pre") && track_cfg("epic_pegasus") >= 0)
        Jm_MusicCue(track_cfg("epic_pegasus"), "epic_pegasus");
    else if (id && (!strcmp(id, "dk10_epilogue") || !strcmp(id, "dk10_wish_orb") || !strcmp(id, "dk10_pegasus_win"))
             && track_cfg("epic_festival") >= 0)
        Jm_MusicCue(track_cfg("epic_festival"), "epic_festival");
    open_page();
}

static void apply_warp(void)
{
    if (!jm_warp) return;
    jm_warp = 0;
    jm.x = jm_warp_x;
    jm.z = jm_warp_z;
    cam_x = jm.x;
    cam_z = jm.z;
    area = -1;
}

static void apply_pwarp(void)
{
    if (!jm_pwarp) return;
    jm_pwarp = 0;
    if (Paint_Loaded()) Paint_Warp(jm_pwarp_area, jm_pwarp_anchor);
    area = -1;
}

static void end_scene(void)
{
    /* a bare warp (hatch / door) is not progress; stage/flags/cards with a warp (Festival epilogue) still save */
    int had_effects = scene_effects != NULL && (!Json_Get(scene_effects, "warp")
        || Json_Get(scene_effects, "stage") || Json_Get(scene_effects, "flags")
        || Json_Get(scene_effects, "cards") || Json_Get(scene_effects, "items"));
    Say_Close();
    portrait_x = -1;
    cooldown = 20;
    if (scene_effects) {                   /* a rumor heard, a card given: now that the scene has been read */
        const JsonNode *e = scene_effects;
        scene_effects = NULL;
        Story_ApplyResult(e);
        World_PlaceNpcs();
    }
    if (in_paint_flow) Paint_SceneEnd();
    state = ST_PAINT;
    if (jm_shop_req) {                     /* an "open_shop" result: the stall opens after the talk */
        jm_shop_req = 0;
        if (Eco_ShopSet(jm_shop_req_id)) { Shop_Open(); state = ST_SHOP; return; }
    }
    if (scene_then) {
        const char *next = scene_then;
        scene_then = NULL;
        begin_scene(next, 0, scene_result);
        return;
    }
    if (scene_intro && jm.stage < 1) jm.stage = 1;
    if (scene_intro || scene_result || had_effects) {
        jm_save_ok = Save_Write();
        Ui_Message(Tr(jm_save_ok ? "messages.progress_saved" : "messages.save_failed"));
    }
    scene_intro = scene_result = 0;
    if (in_paint_flow) { in_paint_flow = 0; Paint_TalkEnd(); }
    apply_pwarp();
}

/* ------------------------------------------------------------------- duel */
static void ensure_deck(void)
{
    int i, empty = 1;
    for (i = 0; i < 40; i++) if (gDuel_awPlayerDeck[i] >= 1 && gDuel_awPlayerDeck[i] <= 722) empty = 0;
    if (!empty) return;
    /* An empty edited deck is not permission to grant the classic 1..40.
     * Refill from this run's trunk only (moving, not duplicating copies). */
    memset(gDuel_awPlayerDeck, 0, 40 * sizeof(u16));
    for (i = 1; i <= 722; i++) {
        int copies = 0, slot;
        while (gLibrary_abCardChest[i - 1] && copies < 3) {
            for (slot = 0; slot < 40 && gDuel_awPlayerDeck[slot]; slot++);
            if (slot == 40) return;
            gDuel_awPlayerDeck[slot] = (u16)i;
            gLibrary_abCardChest[i - 1]--;
            copies++;
        }
    }
    LOG("journey: empty deck refilled from owned cards only");
}

/* A new journey starts with the story's weak forty (journey.json "starter_deck"): the player has to
 * win, drop or buy better cards on the way. Never inherit the classic chest. */
void Journey_GiveStarter(void)
{
    const JsonNode *list = Json_Get(jm_rules, "starter_deck"), *n;
    int i = 0;
    if (!list || Json_Count(list) != 40) return;
    for (n = list->child; n && i < 40; n = n->next) {
        int id = (int)n->num;
        if (id < 1 || id > 722) return;
    }
    memset(gLibrary_abCardChest, 0, 722);
    gLibrary_dwStarchips = 0;
    for (n = list->child; n && i < 40; n = n->next, i++) {
        int id = (int)n->num;
        gDuel_awPlayerDeck[i] = (u16)id;
    }
    Journey_CardsCapture();
    LOG("journey: starter deck given (40 weak cards)");
}

static void duel_returned(void);
static void arm_duel(int npc)
{
    if (Dbg_WinDuels()) {                  /* debug: no duel is played, it counts as won */
        LOG("debug: duel against %s skipped (counts as won)", npcs[npc].name);
        Say_Close();
        portrait_x = -1;
        jm.duels++;
        D_8009B362 = Dbg_LoseDuels() ? 1 : 0;
        after_return = RET_DUEL;
        duel_npc = npc;
        duel_returned();
        return;      /* the debug win plays no duel, so it rolls no drop */
    }
    ensure_deck();
    Say_Close();
    portrait_x = -1;
    SD_SEPlayFull(0x30);
    SD_BGMFadeOut();
    D_8009B368 = 13;                       /* the mode the duel returns to: ours */
    after_return = RET_DUEL;
    duel_npc = npc;
    jm.duels++;
    duel_live = 1;
    face_duelist = -1;                     /* the next opponent's face is read when the panel first draws */
    state = ST_TO_DUEL;
    LOG("journey: duel against %s (duelist %d)", npcs[npc].name, npcs[npc].duelist_id);
    func_80024DC8(-1, npcs[npc].duelist_id, 0x6000, 0x6000);
}

/* gLibrary_dwStarchips is the game's duel-performance currency, not jm.stars. */
static void duel_returned(void)
{
    int won = (D_8009B362 == 0);
    const JsonNode *r = won ? duel_win : duel_lose;
    /* whether this win was had before is read now: applying the result sets the flags that say so */
    int rematch = won && (Story_ResultDone(duel_win) || (duel_win && Json_Num(duel_win, "rematch", 0) != 0));
    int eliminated = 0;
    area = -1;                              /* the duel's song ended the village's: start it again */
    if (in_paint_flow) { Paint_Enter(); paint_auto = 1; }    /* the duel took the banks: the painted village is loaded again behind the scene */
    if (won) jm.wins++; else jm.losses++;
    LOG("journey: duel over, %s (wins %d, losses %d)", won ? "won" : "lost", jm.wins, jm.losses);
    if (won) Story_ApplyResult(duel_win);
    if (music_cue >= 0 && music_cue_tag && strcmp(music_cue_tag, "epic_festival") != 0) Jm_MusicClear();
    if (wager_bet > 0 && duel_win) {      /* Duelist Kingdom: the bet goes to the winner (jm_wager.c); the last star lost is a game over */
        Wager_Settle(duel_win, wager_bet, won);
        if (jm.stars <= 0) eliminated = 1;
    }
    wager_bet = 0;
    LOG("journey: after duel, kingdom chips %d, duel stars %u", jm.stars, (unsigned)gLibrary_dwStarchips);   /* separate counters */
    duel_live = 0;
    if (duel_is_gang) { duel_is_gang = 0; Gang_Result(won); }
    else if (duel_is_arena) { duel_is_arena = 0; Arena_Result(won); }
    else if (duel_npc >= 0) Eco_DuelReward(npcs[duel_npc].id, won, rematch);
    Eco_SetDropContext("duel");
    World_PlaceNpcs();
    after_return = RET_NONE;
    duel_npc = -1;
    apply_warp();
    if (card_show && !Paint_CardArt(card_show)) card_show = 0;   /* no picture: no reveal */
    if (eliminated) {                      /* no stars left: the journey is over */
        jm.eliminations++;
        LOG("journey: GAME OVER (no stars)");
        Say_Close();
        in_paint_flow = 0;
        Paint_TalkEnd();
        gameover_age = 0;
        state = ST_GAMEOVER;
        scene_then = NULL;
        scene_choice = NULL;
        card_show = 0;
        return;
    } else if (r && Json_Str(r, "scene", NULL)) {
        begin_scene(Json_Str(r, "scene", NULL), 0, 1);
        scene_then = Json_Str(r, "then", NULL);
        scene_choice = Json_Get(r, "choice");
    } else if (Arena_Running() || (arena_return && !r)) {
        arena_return = 0;
        in_paint_flow = 0;
        Paint_TalkEnd();
        state = ST_ARENA;                  /* back to the ladder, a rung further up or out of the run */
        cooldown = 12;
    } else if (in_paint_flow) { in_paint_flow = 0; Paint_TalkEnd(); state = ST_PAINT; cooldown = 20; }
    else { state = ST_PAINT; cooldown = 20; }
    if (card_show && state != ST_SCENE && state != ST_ASK) {   /* a scene of its own comes first */
        card_back = state;
        card_age = 0;
        state = ST_CARD;
    }
}

/* --------------------------------------------------------------- the world */
static void start_talk(const Talk *t)
{
    begin_scene(t->scene, 0, 0);
    scene_effects = NULL;
    if (state == ST_SCENE && t->duel >= 0) {
        pend_duel = t->duel;
        duel_win = t->on_win;
        duel_lose = t->on_lose;
    } else if (state == ST_SCENE) scene_effects = t->effects;
}

/* the village shown as a picture: the walk happens there, not on the 3D map */
static int in_village(void) { return World_Area(jm.x, jm.z) == 0 && (int)(jm.z / TS) >= 23; }

/* The painted village has its own songs (journey.json "painted": {"music": {"day": track, "night": track}}, a track being the sound
 * driver's song number / 16 - 0x700): the day song plays while the village is shown, the night song once night has fallen (the bench
 * scene and until the Stamp Card is given).  `area < 0` restarts the music (after a duel, the intro, a warp).
 * Cue tracks (tension_wager, epic_heishin, epic_pegasus, epic_festival) override exploration until cleared. */
static int pm_cur = -1, pm_timer, pm_ctx = -1;
static int menu_from_paint;                /* the START menu was opened in the painted village: the picture stays behind it, and Close returns to it */
static int painted_ctx(void) { return state == ST_PAINT || state == ST_JOURNAL || state == ST_SHOP || state == ST_ARENA || state == ST_AMBUSH || in_paint_flow || (state == ST_MENU && menu_from_paint) || state == ST_WAGER; }
static int track_cfg(const char *key)
{
    const JsonNode *po = Json_Get(jm_rules, "painted"), *mu = po ? Json_Get(po, "music") : NULL;
    return (int)Json_Num(mu, key, -1);
}
static void music_play_track(int track, const char *tag)
{
    SD_BGMPlay(0x7000 + (u32)track * 0x10);
    pm_cur = track;
    LOG("journey: music %d (%s)", track, tag ? tag : "?");
}
static void Jm_MusicCue(int track, const char *tag)
{
    if (track < 0) return;
    if (music_cue == track && pm_cur == track) return;
    music_cue = track;
    music_cue_tag = tag;
    LOG("journey: music cue %s", tag ? tag : "?");
    /* Start at once so the cue is heard before a debug wager auto-confirms (~30 frames). */
    music_play_track(track, tag);
}
static void Jm_MusicClear(void)
{
    if (music_cue < 0) return;
    music_cue = -1;
    music_cue_tag = NULL;
    pm_cur = -1;
    pm_timer = 0;
    area = -1;                             /* music_tick restarts the area song */
}

/* the place name of the HUD and the banner: the painted areas have their own (ui.json "painted"), else the old map's */
static const char *place_name(void)
{
    if (painted_ctx() && Paint_Area() == 1) return Tr("painted.cistern");
    if (painted_ctx() && Paint_Area() == 2) { const char *n = Arena_PlaceName(); return n && *n ? n : Tr("painted.arena"); }
    if (painted_ctx() && Paint_Area() >= 3) {
        static char key[40];
        snprintf(key, sizeof(key), "painted.%s", Paint_AreaId());
        return Tr(key);
    }
    return World_AreaName(area < 0 ? 0 : area);
}

static const char *music_tag_for(int want)
{
    if (music_cue >= 0 && want == music_cue && music_cue_tag) return music_cue_tag;
    if (Paint_Area() == 1) return "cistern";
    if (Paint_Area() >= 3) return Paint_AreaId();
    if (want == track_cfg("night")) return "night";
    if (want == track_cfg("day")) return "day";
    return "area";
}
static void music_tick(void)
{
    int a = World_Area(jm.x, jm.z), pc = painted_ctx();
    if (pc != pm_ctx) { pm_ctx = pc; area = -1; pm_cur = -1; pm_timer = 0; }     /* into or out of the painted village: its own song */
    if (music_cue >= 0) {
        int want = music_cue;
        if (pm_cur < 0) music_play_track(want, music_tag_for(want));
        else if (want != pm_cur && !pm_timer) { SD_BGMFadeOut(); pm_timer = 45; pm_cur = want; }
        if (pm_timer && --pm_timer == 0) music_play_track(pm_cur, music_tag_for(pm_cur));
        if (area_banner > 0) area_banner--;
        return;
    }
    if (pc && track_cfg("day") >= 0) {
        int want = Paint_Area() == 1 && track_cfg("cistern") >= 0 ? track_cfg("cistern") : track_cfg(Paint_IsNight() && track_cfg("night") >= 0 ? "night" : "day");
        if (Paint_Area() >= 3 && track_cfg(Paint_AreaId()) >= 0) want = track_cfg(Paint_AreaId());   /* the harbor, the ship, the beach: their own songs */
        if (area < 0) { area = area_cand = a; area_banner = 150; area_timer = 0; pm_cur = -1; pm_timer = 0; }
        if (pm_cur < 0) music_play_track(want, music_tag_for(want));
        else if (want != pm_cur && !pm_timer) { SD_BGMFadeOut(); pm_timer = 45; pm_cur = want; }
        if (pm_timer && --pm_timer == 0) music_play_track(pm_cur, music_tag_for(pm_cur));
        if (area_banner > 0) area_banner--;
        return;
    }
    if (area < 0) {
        area = area_cand = a;
        area_timer = 0;
        area_banner = 150;
        SD_BGMPlay(World_AreaMusic(a));
    }
    if (a != area_cand) { area_cand = a; area_count = 0; }
    else if (a != area && ++area_count >= 20) {
        area = a;
        area_banner = 150;
        SD_BGMFadeOut();
        area_timer = 30;
    }
    if (area_timer && --area_timer == 0) SD_BGMPlay(World_AreaMusic(area));
    if (area_banner > 0) area_banner--;
}

static void walk_tick(unsigned short pad, unsigned short edge)
{
    float dx = 0, dz = 0, sp = (pad & PAD_CIRCLE) ? 4.2f : 2.6f;
    Talk t;
    float tx_, tz_;
    if (!paint_auto) { paint_auto = 1; if (in_village()) { Paint_Enter(); state = ST_PAINT; return; } }
    int teleport, near;
    if (pad & PAD_UP) dz -= 1;
    if (pad & PAD_DOWN) dz += 1;
    if (pad & PAD_LEFT) dx -= 1;
    if (pad & PAD_RIGHT) dx += 1;
    walking = (dx != 0 || dz != 0);
    if (walking) {
        float l = sqrtf(dx * dx + dz * dz), target = atan2f(dx, dz), d, nx, nz;
        dx = dx / l * sp;
        dz = dz / l * sp;
        d = target - pyaw;
        while (d > 3.14159265f) d -= 6.2831853f;
        while (d < -3.14159265f) d += 6.2831853f;
        pyaw += d * 0.35f;
        nx = jm.x + dx;
        nz = jm.z + dz;
        if (!World_Blocked(nx, jm.z)) jm.x = nx;
        if (!World_Blocked(jm.x, nz)) jm.z = nz;
    }
    near = World_NearestNpc(jm.x, jm.z, 64);
    if (!cooldown && (edge & PAD_CROSS)) {
        if (near >= 0 && Story_TalkRule(&npcs[near], &t)) { start_talk(&t); return; }
        if (Story_PoiAt(jm.x, jm.z, &t)) { start_talk(&t); return; }
    }
    if (edge & PAD_START) { Ui_MenuOpen(); state = ST_MENU; return; }
    if (edge & PAD_TRIANGLE) { state = ST_MAP; return; }
    if (edge & PAD_SELECT) minimap_on ^= 1;
    if (Story_Trigger(&t, &tx_, &tz_, &teleport)) {
        if (teleport) { jm.x = tx_; jm.z = tz_; cam_x = jm.x; cam_z = jm.z; }
        apply_warp();
        World_PlaceNpcs();
        LOG("journey: stage %d", jm.stage);
        if (t.scene) { begin_scene(t.scene, 0, 0); scene_then = t.then; }
        area = -1;
    }
}

static void leave(void)
{
    Say_Close();
    Fade_WaitOut();
    SD_BGMFadeOut();
    ModMode_Leave(return_menu);
}

static void go_screen(int mode, int ret)
{
    Say_Close();
    SD_BGMFadeOut();
    Fade_WaitOut();
    after_return = ret;
    D_8009B269 = 13;                       /* where the screen returns to */
    D_8009B26E = 0;
    D_8009B26C = (u8)mode;                 /* 7 the deck editor, 9 the name entry */
}

static void new_journey(void)
{
    Story_Reset();
    Paint_SetArea(0);
    Journey_GiveStarter();
    ensure_deck();
    World_Spawn(&jm.x, &jm.z);
    cam_x = jm.x;
    cam_z = jm.z;
    World_PlaceNpcs();
    { float ax, ay; if (Paint_Anchor("hero_start", &ax, &ay)) Paint_Set(ax, ay); }   /* the story starts at the home door */
    lang_sel = Lang_Current();
    {
        int pref = Lang_PrefRead();
        if (pref >= 0) {                   /* the language was chosen on an earlier new game: straight to the creator */
            Lang_Set(pref);
            strncpy(jm.name, Tr("defaults.player_name"), sizeof(jm.name) - 1);
            Ui_StartCreate();
            state = ST_CREATE;
            return;
        }
    }
    state = ST_LANG;                       /* the first time: the language first, then the creator */
}

static void enter_world(void);

static void continue_journey(void)
{
    if (!Save_Read()) { new_journey(); return; }
    Lang_Set(jm.lang);
    Paint_SetArea(jm.pt_area);             /* a save keeps the hatch (the village) even if it was made in the cistern; the chapter 2 pictures are kept */
    Journey_CardsRestore();
    Dbg_Apply();
    Story_Regrant();
    ensure_deck();
    World_PlaceNpcs();
    cam_x = jm.x;
    cam_z = jm.z;
    if (jm.pt_set) Paint_Set(jm.pt_x, jm.pt_y);   /* and back to where it stood in the painted village */
    enter_world();
}

/* The village is a picture, and the 3D map behind it is only the old view (L1).  Entering it here
 * rather than on the first walking frame is what keeps that map from showing for a frame first. */
static void enter_world(void)
{
    /* There is one view: the painted village.  The old 3D map is no longer a place the player goes. */
    Paint_Enter();
    paint_auto = 1;
    state = ST_PAINT;
}

static void run(int first)
{
    unsigned short pad = jm_host->pad(jm_host, 0), edge = (unsigned short)(pad & ~pad_prev);
    pad_prev = pad;
    if (first) {
        if (!ready) {
            ready = Gfx_LoadAssets() && Story_Load() && World_Load() && Lang_Set(0);
            if (ready) { Save_Init(); Dbg_Init(); Dev_Load(); Eco_Load(); Eco_LoadLang(Lang_Code()); Gang_Load(); Arena_Load(); }
        }
        if (!ready) { ModMode_Leave(return_menu); return; }
        Tower_Background(0);
        Fade_WaitIn();
        area = -1;
        LOG("journey: mode on (return %d)", after_return);
        paint_auto = 0;
        switch (after_return) {
        case RET_DUEL: duel_returned(); break;
        case RET_NAME: after_return = RET_NONE; Ui_RefreshName(); state = ST_CREATE; break;
        case RET_DECK: after_return = RET_NONE; jm_save_ok = Save_Write(); enter_world(); cooldown = 10; break;
        default: {
            int req = menu_request;
            menu_request = REQ_NONE;
            if (req == REQ_CONTINUE && Save_Exists() && Save_Read()) {
                continue_journey();
            } else if (req == REQ_NEW && Save_Exists()) {   /* a save exists: ask before it can be replaced */
                if (Save_Read()) Lang_Set(jm.lang);       /* the box speaks the saved language */
                choose_sel = 1;                            /* Cancel is where the cursor starts */
                state = ST_CONFIRM;
            } else if (req == REQ_NEW) {
                new_journey();
            } else state = ST_LEAVE;                       /* nothing asked for (or no save to continue): back to the title */
        }
        }
        return;
    }
    frame_no++;
    if (Dbg_On() && (state == ST_PAINT || state == ST_WALK)) {
        int swallow;
        if (Dbg_Keys(pad, edge, &swallow)) { Story_Regrant(); World_PlaceNpcs(); if (state == ST_PAINT) Paint_Enter(); }
        if (swallow) pad = edge = 0;
    }
    dbg_age++;
    if (cooldown > 0) cooldown--;
    if (ui_message_timer > 0) ui_message_timer--;
    Eco_Tick();                             /* the queued coin, xp and level-up notices, one by one */
    if (ready && state != ST_PAINT && state != ST_WALK) Gang_Grace(GANG_GRACE_SCENE);   /* not mid-talk */
    if (ready && state == ST_PAINT) Gang_Area();
    if (ready) Eco_QuestTick();             /* a quest whose last step just completed pays its coins */
    switch (state) {
    case ST_CONFIRM:
        if (edge & (PAD_UP | PAD_DOWN | PAD_LEFT | PAD_RIGHT)) choose_sel ^= 1;
        if (edge & PAD_CROSS) { if (choose_sel == 0) new_journey(); else state = ST_LEAVE; }
        if (edge & (PAD_TRIANGLE | PAD_CIRCLE)) state = ST_LEAVE;
        break;
    case ST_LANG:
        if (edge & (PAD_UP | PAD_DOWN)) {
            int n = Lang_Count();
            lang_sel = (lang_sel + (edge & PAD_UP ? n - 1 : 1)) % n;
            Lang_Set(lang_sel);
        }
        if (edge & PAD_CROSS) {
            Lang_PrefWrite(lang_sel);                  /* asked once: the next new game goes straight to the creator */
            strncpy(jm.name, Tr("defaults.player_name"), sizeof(jm.name) - 1);
            Ui_StartCreate();
            state = ST_CREATE;
        }
        if (edge & PAD_TRIANGLE) state = ST_LEAVE;
        break;
    case ST_WAGER: {
        int r;
        music_tick();
        r = Wager_Input(edge);
        if (r == 1) { wager_bet = Wager_Bet(); LOG("journey: wager %d", wager_bet); Jm_MusicClear(); arm_duel(pend_duel); }
        else if (r == 2) { Jm_MusicClear(); duel_win = duel_lose = NULL; pend_duel = -1; end_scene(); }
        break;
    }
    case ST_GAMEOVER:
        gameover_age++;
        if (gameover_age > 60 && (edge & (PAD_CROSS | PAD_START))) state = ST_LEAVE;   /* back to the title: Continue loads the last save */
        break;
    case ST_SHOP:
        if (Shop_Input(edge)) { state = ST_PAINT; cooldown = 12; }
        break;
    case ST_CARD:
        if (++card_age >= CARD_FRAMES || (card_age > 24 && (edge & (PAD_CROSS | PAD_CIRCLE | PAD_START | PAD_TRIANGLE)))) {
            card_show = 0;
            state = card_back;
            cooldown = 10;
        }
        break;
    case ST_ARENA: {
        int start = 0;
        if (Arena_Input(edge, &start)) { state = ST_PAINT; cooldown = 12; break; }
        if (start) {
            char name[24];
            int tier = 1, duelist = Arena_NextFighter(name, sizeof(name), &tier);
            if (duelist <= 0) { LOG("journey: the arena fighter has no duelist this run"); break; }
            eco_opponent("eco_arena", name, duelist);
            duel_is_arena = 1;
            arena_return = 1;
            in_paint_flow = 1;
            Eco_SetDropContext("arena_bout");
            duel_win = duel_lose = NULL;    /* not the last story duel's result (its scene played again after an ambush) */
            arm_duel(ECO_NPC);
        }
        break;
    }
    case ST_AMBUSH:                        /* he has walked over and said his piece; then the duel */
        if (Say_Done() || (edge & (PAD_CROSS | PAD_CIRCLE | PAD_START))) {
            Say_Close();
            eco_opponent("eco_gang", Gang_Name(), Gang_Duelist());
            if (npcs[ECO_NPC].duelist_id <= 0) {    /* the host has no such duelist: let it go */
                LOG("journey: the ambusher has no duelist this run; skipped");
                Gang_Cancel();
                in_paint_flow = 0;
                state = ST_PAINT;
                cooldown = 20;
                break;
            }
            duel_is_gang = 1;
            in_paint_flow = 1;
            Eco_SetDropContext("ambush_win");
            duel_win = duel_lose = NULL;    /* not the last story duel's result (its scene played again after an ambush) */
            arm_duel(ECO_NPC);
        }
        break;
    case ST_PAINT:
        if (edge & PAD_START) { Ui_MenuOpen(); menu_from_paint = 1; state = ST_MENU; break; }   /* START: the menu (deck editor, items, status, save, title) */
        music_tick();
        if (edge & PAD_SELECT) minimap_on ^= 1;
        if (edge & PAD_TRIANGLE) { LOG("journey: journal open"); state = ST_JOURNAL; break; }
        if (!cooldown && Paint_Area() != 2 && Gang_Pending()) {     /* the countdown ran out: one of them walks over */
            Ui_MessageTone(EcoTr("ui.ambush_banner"), 0xFF6060);
            Say_Text(Gang_Name(), Gang_Line("taunt"), 0);
            in_paint_flow = 1;                 /* it all happens in the picture, not on the old map */
            state = ST_AMBUSH;
            break;
        }
        if (!cooldown) {                       /* a state of the story that starts a scene by itself (the three stamps) */
            Talk at;
            if (Story_Auto(&at)) {
                World_PlaceNpcs();             /* its result may bring someone out (the Forest Mage at the opened gate) */
                Paint_TalkStart(-1);
                in_paint_flow = 1;
                start_talk(&at);
                if (state == ST_SCENE) { scene_then = at.then; scene_result = 1; }
                else { in_paint_flow = 0; Paint_TalkEnd(); state = ST_PAINT; }
                break;
            }
        }
        if (!cooldown && (edge & PAD_CROSS)) {
            int n = Paint_NearNpc(), o;
            Talk t;
            if (Paint_ArenaPadAt()) {
                Paint_ArenaReady();
                state = ST_ARENA;
                cooldown = 10;
                break;
            }
            if (n >= 0 && Story_TalkRule(&npcs[n], &t)) {
                Paint_TalkStart(n);
                in_paint_flow = 1;
                start_talk(&t);
                if (state != ST_SCENE) { in_paint_flow = 0; Paint_TalkEnd(); state = ST_PAINT; }
                break;
            }
            if (n >= 0 && Eco_ShopAt(npcs[n].id)) {   /* a keeper with nothing left to say runs the stall */
                Shop_Open();
                state = ST_SHOP;
                break;
            }
            {                                  /* the cellar hatch: the ring under the bakery */
                float ax, ay, asx, asy;
                Paint_Info(&ax, &ay, &asx, &asy);
                if (Arena_DoorAt(ax, ay) && Arena_Open()) {
                    Paint_Warp("arena_village", "arena_player");
                    area = -1;
                    cooldown = 18;
                    break;
                }
            }
            o = Paint_NearObject();            /* the bench, the notice board */
            if (o >= 0 && Paint_ObjectRule(o, &t)) {
                Paint_ObjectStart(o, t.pose);
                in_paint_flow = 1;
                start_talk(&t);
                if (state != ST_SCENE) { in_paint_flow = 0; Paint_TalkEnd(); state = ST_PAINT; }
                break;
            }
        }
        {
            int paint_result = Paint_Tick(pad, edge);
            if (paint_result == 2) {          /* the player reached the bottom edge of the cellar stairs */
                { char from[24]; snprintf(from, sizeof(from), "%s", Paint_AreaId()); Paint_Warp(from, "arena_door"); }
                area = -1;
                cooldown = 18;
            } else if (paint_result && paint_exit && jm.stage >= 4) {   /* across the open bridge: the harbor road */
                paint_exit = 0;
                if (jm.stage < 5) jm.stage = 5;
                Paint_Warp("harbor", "spawn_gate");
                World_PlaceNpcs();
                area = -1;
                cooldown = 18;
            } else if (paint_result) {
                /* the picture could not be loaded, or the player walked off the far side of it: there is
                 * nowhere else to go now, so he is put back on the south bank where he came from */
                paint_exit = 0;
                Paint_Set(652.0f, 190.0f);
                Ui_Message(Tr("messages.part_end"));
                cooldown = 10;
            }
        }
        break;
    case ST_JOURNAL:
        music_tick();
        if (edge & (PAD_TRIANGLE | PAD_CIRCLE | PAD_CROSS | PAD_START | PAD_SELECT)) { state = ST_PAINT; cooldown = 10; }
        break;
    case ST_MAP:
        if (edge & (PAD_TRIANGLE | PAD_CIRCLE | PAD_CROSS | PAD_SELECT | PAD_START)) state = ST_PAINT;
        break;
    case ST_CREATE:
        if (jm_name_entry_requested) { jm_name_entry_requested = 0; go_screen(9, RET_NAME); return; }
        if ((create_r = Ui_CreateInput(edge)) == 2) { state = ST_LEAVE; break; }      /* Back on the first step: the title */
        if (create_r == 1) {
            jm.stage = 0;
            World_PlaceNpcs();
            area = -1;
            Paint_Enter();                         /* the story opens in the painted village, at the home door */
            paint_auto = 1;
            in_paint_flow = 1;
            begin_scene(Json_Str(jm_rules, "intro", "c1_intro"), 1, 0);
            if (state != ST_SCENE) state = ST_PAINT;
        }
        break;
    case ST_WALK:
        music_tick();
        walk_tick(pad, edge);
        if (state == ST_WALK) Guide_Update();
        break;
    case ST_SCENE:
        walking = 0;
        music_tick();
        if (cur_kind) notif_age++;
        {
            int adv = cur_kind ? ((edge & PAD_CROSS) && notif_age > 24) : Say_Done();
            if (Dbg_Skip() && dbg_age > (cur_kind ? 30 : 8)) adv = 1;
            if (!adv) break;
        }
        {
            Page p;
            Story_Page(scene_id, scene_idx, &p);
            if (p.ask) { state = ST_ASK; ask_sel = 0; dbg_age = 0; break;      /* the question stays in the box while it is answered */ }
            scene_idx++;
            if (scene_idx >= scene_n) end_scene(); else open_page();
        }
        break;
    case ST_ASK:
        music_tick();
        if (edge & (PAD_LEFT | PAD_RIGHT | PAD_UP | PAD_DOWN)) ask_sel ^= 1;
        if (Dbg_Skip() && dbg_age > 12) { ask_sel = 0; edge |= PAD_CROSS; }
        if (edge & PAD_CROSS) {
            if (ask_sel == 0 && pend_duel >= 0 && Wager_Max(duel_win) > 0) { Wager_Open(duel_win); if (track_cfg("tension_wager") >= 0) Jm_MusicCue(track_cfg("tension_wager"), "tension_wager"); state = ST_WAGER; break; }   /* a star duel: the bet first */
            if (ask_sel == 0 && pend_duel >= 0) { wager_bet = 0; arm_duel(pend_duel); break; }
            if (pend_duel < 0 && scene_choice) {
                const JsonNode *ans = Json_Get(scene_choice, ask_sel == 0 ? "yes" : "no");
                scene_choice = NULL;
                Story_ApplyResult(ans);
                apply_warp();
                World_PlaceNpcs();
                if (ans && Json_Str(ans, "scene", NULL)) { begin_scene(Json_Str(ans, "scene", NULL), 0, 1); scene_then = Json_Str(ans, "then", NULL); }
                else end_scene();
                break;
            }
            if (ask_sel == 0) { scene_idx++; if (scene_idx >= scene_n) end_scene(); else open_page(); }
            else { duel_win = duel_lose = NULL; end_scene(); }
        }
        break;
    case ST_MENU: {
        int r;
        music_tick();
        r = Ui_MenuInput(edge);
        if (jm_save_requested) { jm_save_requested = 0; jm_save_ok = Save_Write(); }
        if (r == 1) { state = ST_PAINT; menu_from_paint = 0; cooldown = 10; }
        else if (r == 2) { menu_from_paint = 0; go_screen(7, RET_DECK); }      /* back from the deck editor the village is loaded again (paint_auto) */
        else if (r == 3) { menu_from_paint = 0; state = ST_LEAVE; }
        break;
    }
    case ST_LEAVE:
        leave();
        break;
    default: break;
    }
    func_80039794();                       /* the text boxes' per-frame work, as the tower runs it */
    {
        /* the camera keeps the view inside the map, or inside the room; a room smaller than the view is centred */
        float tx_ = jm.x, tz_ = jm.z, hx = CAM_D * 0.42f, zb = CAM_D * 0.42f, zf = CAM_D * 0.20f;
        float lx = 0, hx_ = MW * TS, lz = 0, hz = MH * TS;
        if (jm.z >= 72 * TS) {
            lx = jm.x >= RW * TS ? RW * TS : 0;
            hx_ = lx + RW * TS;
            lz = (72 + (int)(jm.z / TS - 72) / RH * RH) * TS;
            hz = lz + RH * TS;
        }
        tx_ = tx_ < lx + hx ? lx + hx : tx_ > hx_ - hx ? hx_ - hx : tx_;
        tz_ = tz_ < lz + zb ? lz + zb : tz_ > hz - zf ? hz - zf : tz_;
        if (hx_ - lx < 2 * hx) tx_ = (lx + hx_) / 2;
        if (hz - lz < zb + zf) tz_ = lz + (hz - lz) * zb / (zb + zf);
        cam_x += (tx_ - cam_x) * 0.2f;
        cam_z += (tz_ - cam_z) * 0.2f;
    }
}

/* The card the duel gave, turning in the air over the village.
 *
 * It fades up out of nothing, floats, and turns about its own upright axis: the turn is the width
 * narrowing with the cosine of the angle, and the top and bottom edges leaning the other way by its
 * sine, which is what reads as a flat thing rotating rather than a picture being squeezed.  Edge on,
 * a thin bright line stands in for the card's side.
 *
 * Gfx_BankQuad branches on the sign of its depth: a negative one goes straight to the slot the
 * painted floor is drawn in, behind everything, which is where this card first went.  A depth of 0
 * takes the sorted path instead, and since everything else in the scene sorts at a larger depth
 * (characters are hundreds, the ground glow is 200000), 0 is the front of the list. */
static void card_draw(void)
{
    float a = (float)card_age * 0.075f;
    float c = cosf(a), turn = c < 0.0f ? -c : c;
    float lean = sinf(a) * 4.0f;
    float cx = 160.0f, cy = 104.0f + sinf((float)card_age * 0.06f) * 6.0f;
    float hw = 46.0f * turn, hh = 43.0f;
    float sx[4], sy[4];
    unsigned char keep[3];
    int lit = 20 + card_age * 11;                  /* it starts visible, not from pure black */
    if (!card_show) return;
    if (lit > 128) lit = 128;                      /* 128 is this scene's neutral brightness */
    if (card_age > CARD_FRAMES - 20) {             /* and it fades out again at the end */
        lit = (CARD_FRAMES - card_age) * 128 / 20;
        if (lit < 0) lit = 0;
    }
    if (hw < 1.0f) hw = 1.0f;
    sx[0] = cx - hw; sy[0] = cy - hh - lean;
    sx[1] = cx + hw; sy[1] = cy - hh + lean;
    sx[2] = cx - hw; sy[2] = cy + hh + lean;
    sx[3] = cx + hw; sy[3] = cy + hh - lean;
    memcpy(keep, gfx_tint, sizeof(keep));
    gfx_tint[0] = gfx_tint[1] = gfx_tint[2] = (unsigned char)lit;
    {
        int ax, ay, w, h;
        Paint_CardArtWhere(&ax, &ay, &w, &h);
        Gfx_BankQuad(sx, sy, 15, ax, ay, w, h, 0.0f);
    }
    if (turn < 0.12f) {                            /* edge on: a sliver of light for the card's side */
        float ex[4] = {cx - 1.5f, cx + 1.5f, cx - 1.5f, cx + 1.5f};
        Gfx_Rect((int)ex[0], (int)(cy - hh), 3, (int)(hh * 2.0f), lit + 60, lit + 60, lit + 30);
    }
    memcpy(gfx_tint, keep, sizeof(keep));
}

/* ------------------------------------------------------------------ frame */
static void frame_hook(void)
{
    int colours[5];
    if (!ModMode_Active() || !ready) return;
    Gfx_Begin();
    if (state == ST_CREATE) { Ui_DrawCreate(); return; }
    if (state == ST_CONFIRM || state == ST_LANG || state == ST_MAP) { Gfx_Backdrop(0x08061C, 0x2A2060); Gfx_End(); return; }
    if (state == ST_PAINT || state == ST_JOURNAL || state == ST_SHOP || state == ST_ARENA || state == ST_AMBUSH || state == ST_CARD || (state == ST_MENU && menu_from_paint) || state == ST_WAGER || state == ST_GAMEOVER || (in_paint_flow && (state == ST_SCENE || state == ST_ASK))) {
        Ui_BodyColours(colours);
        paint_markers = state == ST_PAINT;
        Paint_Draw(Gfx_Mesh(Ui_BodyMesh()), colours);
        /* Full-bleed shop illustration: its sides and lower edge overscan the 320x240 view, so the
         * source image's cropped waist/stall never leaves a visible rectangular boundary. */
        if (state == ST_SHOP && !Paint_ShopFigure(-8, 6, 336, 234))
            Paint_Figure(Shop_Keeper(), 34, 44, 104, 134);
        if (state == ST_CARD) card_draw();
        Gfx_End();
        if (portrait_x >= 0 && state != ST_PAINT) Gfx_Portrait(14, 40, 84, portrait_x, portrait_y);
        return;
    }
    /* Everything else is the painted village too - the old 3D map is not a screen any more.  Until
     * its picture is in memory there is nothing to draw but a plain field, which is what keeps that
     * map from showing for the frame or two between entering the mode and the picture arriving. */
    jm_guide_on = 0;
    if (Paint_Loaded()) {
        Ui_BodyColours(colours);
        paint_markers = 0;
        Paint_Draw(Gfx_Mesh(Ui_BodyMesh()), colours);
        Gfx_End();
        if (portrait_x >= 0) Gfx_Portrait(14, 40, 84, portrait_x, portrait_y);
        return;
    }
    Gfx_Backdrop(0x08061C, 0x1A1430);
    Gfx_End();
}

/* ---------------------------------------------------------------- overlay */
static int near_object(void) { Talk t; int o = Paint_NearObject(); return o >= 0 && Paint_ObjectRule(o, &t); }
/* The arena's cellar hatch answers X the way a person or a signpost does, so it offers it the same
 * way: the hatch carries no talk of its own (the arena screen handles the press), which is why it
 * is asked about separately here instead of coming out of Paint_NearObject. */
static int near_arena_door(void)
{
    float x, y, sx, sy;
    if (!Paint_Loaded()) return 0;
    if (Paint_ArenaPadAt()) return 1;
    Paint_Info(&x, &y, &sx, &sy);
    return Arena_DoorAt(x, y);
}
static int near_npc(void) { return state == ST_WALK ? World_NearestNpc(jm.x, jm.z, 64) : -1; }
static int has_poi(void) { Talk t; return state == ST_WALK && Story_PoiAt(jm.x, jm.z, &t); }

/* a rounded rectangle (rows of fills: the overlay has rectangles only) */
static void round_fill(int x, int y, int w, int h, unsigned rgb, unsigned alpha)
{
    int r = h / 2, j;
    for (j = 0; j < h; j++) {
        int dy2 = (2 * j + 1 - h), inset = 0;                  /* twice the row centre's distance from the middle */
        int rr = h * h - dy2 * dy2;                              /* (2*half-width)^2 of the circle of diameter h */
        if (rr > 0) { int hw = 0; while ((hw + 1) * (hw + 1) <= rr) hw++; inset = r - hw / 2; }
        else inset = r;
        if (inset < 0) inset = 0;
        if (w - 2 * inset > 0) jm_host->fill(jm_host, x + inset, y + j, w - 2 * inset, 1, rgb, alpha);
    }
}

/* The small action hint: a round button with the key (X is the keyboard key and the PlayStation Cross at once) and one word,
 * in a dim pill at the bottom right.  Drawn only while something can be talked to or examined. */
static void hint_pill(int w, int s, int lh, int top, int vis, const char *word)
{
    int d = lh - 7 * s, ph = lh - 1 * s, tw = jm_host->text_width(jm_host, word, s), pad = 4 * s;
    int pw = pad + d + 6 * s + tw + 10 * s, x = w - pw - 16 * s, y = top + vis - ph - 12 * s, bx = x + pad, by = y + (ph - d) / 2;
    int xw = jm_host->text_width(jm_host, "X", s);
    round_fill(x, y, pw, ph, 0x000000, 140);
    round_fill(bx - s, by - s, d + 2 * s, d + 2 * s, 0x7C9CF0, 235);
    round_fill(bx + s, by + s, d - 2 * s, d - 2 * s, 0x141C48, 255);
    jm_host->draw_text(jm_host, bx + (d - xw) / 2, by + d / 2, "X", 0xB8D0FF, s);
    jm_host->draw_text(jm_host, bx + d + 6 * s, y + ph / 2, word, 0xF4F4F4, s);
}


static void bar(int y, int h, const char *left, unsigned rgb)
{
    int w, hh, s;
    jm_host->overlay_size(jm_host, &w, &hh, &s);
    if (s < 2) s = 2;
    jm_host->fill(jm_host, 0, y, w, h, 0, 150);
    jm_host->draw_text(jm_host, 10, y + h / 2, left, rgb, s);
}

/* A map of the tiles tx0..tx1 x tz0..tz1 with its top left at (x, y), px canvas pixels a tile: rows of equal
 * colour are one fill each.  People, the player and the objective are drawn over it. */
static void draw_map(int x, int y, int px, int tx0, int tz0, int tx1, int tz1, int s)
{
    int tz, tx, i;
    float gx, gz, wx, wz;
    int pulse = (int)(frame_no / 10) & 1;
    for (tz = tz0; tz <= tz1; tz++) {
        int run = tx0;
        unsigned c0 = World_MapColor(tx0, tz);
        for (tx = tx0 + 1; tx <= tx1 + 1; tx++) {
            unsigned c = tx <= tx1 ? World_MapColor(tx, tz) : 0xFFFFFFFFu;
            if (c != c0) {
                jm_host->fill(jm_host, x + (run - tx0) * px, y + (tz - tz0) * px, (tx - run) * px, px, c0, 240);
                run = tx;
                c0 = c;
            }
        }
    }
    for (i = 0; i < npc_count; i++) {
        int tx_ = (int)(npcs[i].x / TS), tz_ = (int)(npcs[i].z / TS);
        if (npcs[i].hidden || tx_ < tx0 || tx_ > tx1 || tz_ < tz0 || tz_ > tz1) continue;
        jm_host->fill(jm_host, x + (tx_ - tx0) * px - px / 2, y + (tz_ - tz0) * px - px / 2, px + px / 2, px + px / 2, 0xE06020, 255);
    }
    if (Guide_Target(&gx, &gz, &wx, &wz)) {
        int tx_ = (int)(gx / TS), tz_ = (int)(gz / TS);
        if (tx_ >= tx0 && tx_ <= tx1 && tz_ >= tz0 && tz_ <= tz1) {
            int cx = x + (tx_ - tx0) * px + px / 2, cy = y + (tz_ - tz0) * px + px / 2, r = px + s * (pulse ? 2 : 1);
            jm_host->fill(jm_host, cx - r, cy - r, 2 * r, 2 * r, 0x201000, 255);
            jm_host->fill(jm_host, cx - r + s, cy - r + s, 2 * r - 2 * s, 2 * r - 2 * s, 0xFFD030, 255);
        }
    }
    {
        int tx_ = (int)(jm.x / TS), tz_ = (int)(jm.z / TS);
        int cx = x + (tx_ - tx0) * px + px / 2, cy = y + (tz_ - tz0) * px + px / 2, r = px - px / 4 + (pulse ? s : 0);
        jm_host->fill(jm_host, cx - r - s, cy - r - s, 2 * r + 2 * s, 2 * r + 2 * s, 0x000000, 255);
        jm_host->fill(jm_host, cx - r, cy - r, 2 * r, 2 * r, 0xFFFFFF, 255);
    }
}

/* The region the player is in: the main map, or one of the rooms below it. */
static void region(int *tx0, int *tz0, int *tx1, int *tz1)
{
    int tz = (int)(jm.z / TS), tx = (int)(jm.x / TS);
    if (tz >= 72) {
        *tx0 = tx >= RW ? RW : 0;
        *tz0 = 72 + (tz - 72) / RH * RH;
        *tx1 = *tx0 + RW - 1;
        *tz1 = *tz0 + RH - 1;
    } else {
        *tx0 = 0; *tz0 = 0; *tx1 = MW - 1; *tz1 = 71;
    }
}

/* The quest journal: journey.json "journal" lists the quests with the conditions that open them ("active") and close them ("done"); the
 * texts are the language file's quest_titles / quest_objectives / quest_rewards (one per quest) and quest_steps (the "text" of a line).
 * A line may carry "active" (shown only then) and the quest "hide_done" (finished lines go away): a quest then shows only what is open now.
 * Six quests must fit one screen: open quests first with their lines, the rewards only while two or fewer are open, finished ones compact. */
static int wrap_lines(const char *text, int maxw, int s, char lines[][100], int max);
static void journal_overlay(int w, int h, int s, int lh, int top, int vis)
{
    const JsonNode *list = Json_Get(jm_rules, "journal"), *q;
    int x = w / 10, y = top + lh, pw = w * 4 / 5, qi = 0, pass, shown = 0, nopen = 0, bottom = top + vis - lh * 4 - lh / 2, dl = lh * 3 / 4;
    char line[160];
    (void)h;
    for (q = list ? list->child : NULL; q; q = q->next)
        if (Story_Cond(Json_Get(q, "active")) && !(Json_Get(q, "done") && Story_Cond(Json_Get(q, "done")))) nopen++;
    jm_host->fill(jm_host, 0, 0, w, h, 0x000000, 150);
    jm_host->fill(jm_host, x - 8, top + lh / 4, pw + 16, vis - lh / 2, 0x0C0E2C, 230);
    jm_host->draw_text(jm_host, x + 4 * s, y, Tr("journal.heading"), 0xFFE9A0, s + 1);
    y += lh * 3 / 2;
    for (pass = 0; pass < 2; pass++) {      /* the open quests first, then the finished ones */
        qi = 0;
        for (q = list ? list->child : NULL; q; q = q->next, qi++) {
            const JsonNode *l;
            int done = Story_Cond(Json_Get(q, "done")) && Json_Get(q, "done");
            if (!Story_Cond(Json_Get(q, "active")) || done != pass) continue;
            snprintf(line, sizeof(line), "%s %s", done ? "[x]" : "[ ]", TrAt("quest_titles", qi, "?"));
            jm_host->draw_text(jm_host, x + 4 * s, y, line, done ? 0x80C080 : 0x40E0E0, s);
            y += done ? dl : lh;
            if (!done) {
                int k = 0, any_line = 0, hide = Json_Get(q, "hide_done") != NULL;
                for (l = Json_Get(q, "lines") ? Json_Get(q, "lines")->child : NULL; l; l = l->next, k++) {
                    const char *who = Json_Str(l, "npc", NULL);
                    int ldone = Json_Get(l, "done") && Story_Cond(Json_Get(l, "done"));
                    int ni, ti = (int)Json_Num(l, "text", -1);
                    const char *nm = who ? who : (ti >= 0 ? TrAt("quest_steps", ti, "") : "");
                    if (Json_Get(l, "active") && !Story_Cond(Json_Get(l, "active"))) continue;
                    if (hide && ldone) continue;
                    for (ni = 0; who && ni < npc_count; ni++) if (!strcmp(npcs[ni].id, who)) nm = npc_name(ni);
                    snprintf(line, sizeof(line), "%s %s", ldone ? "[x]" : "[ ]", nm);
                    jm_host->draw_text(jm_host, x + 20 * s, y, line, ldone ? 0x80C080 : 0xFFFFFF, s);
                    y += lh; any_line = 1;
                }
                if (!any_line && Json_Get(q, "lines") == NULL) { jm_host->draw_text(jm_host, x + 20 * s, y, TrAt("quest_objectives", qi, ""), 0xFFFFFF, s); y += lh; }
                else if (!any_line && Json_Get(q, "lines") && Json_Count(Json_Get(q, "lines")) == 0) { jm_host->draw_text(jm_host, x + 20 * s, y, TrAt("quest_objectives", qi, ""), 0xFFFFFF, s); y += lh; }
                if (nopen <= 2) {
                    snprintf(line, sizeof(line), "%s %s", Tr("journal.reward"), TrAt("quest_rewards", qi, ""));
                    jm_host->draw_text(jm_host, x + 20 * s, y, line, 0xC0C090, s);
                    y += lh;
                }
            }
            y += done ? 0 : lh / 4;
            shown++;
        }
    }
    (void)bottom;
    if (!shown) jm_host->draw_text(jm_host, x + 4 * s, y, Tr("journal.empty"), 0xB0B0B0, s);
    {   /* the backpack: the Stamp Card with its three slots, and the other items (wrapped over two lines) */
        char names[12][32], rows[3][100];
        int n = Story_ItemList(names, 12), k, nr;
        line[0] = 0;
        for (k = 0; k < n; k++) { strncat(line, k ? ", " : "", sizeof(line) - strlen(line) - 1); strncat(line, names[k], sizeof(line) - strlen(line) - 1); }
        if (n) {
            char out[200];
            snprintf(out, sizeof(out), "%s %s", Tr("journal.items"), line);
            nr = wrap_lines(out, pw - 8 * s, s, rows, 2);
            for (k = 0; k < nr; k++) jm_host->draw_text(jm_host, x + 4 * s, top + vis - lh * (4 - k) - lh / 2 + lh / 2, rows[k], 0xE0D090, s);
        }
        if (Story_Has("courier_met")) {
            char out[200];
            snprintf(out, sizeof(out), "%s  %s [%c]  %s [%c]  %s [%c]", Tr("journal.stamp"),
                     Tr("journal.stamp_lost"), Story_Has("treasure_lost") ? 'x' : ' ', Tr("journal.stamp_won"), Story_Has("treasure_won") ? 'x' : ' ',
                     Tr("journal.stamp_given"), Story_Has("treasure_given") ? 'x' : ' ');
            jm_host->draw_text(jm_host, x + 4 * s, top + vis - lh * 5, out, 0xE0D090, s);
        }
    }
    jm_host->draw_text(jm_host, x + 4 * s, top + vis - lh * 3 / 2, Tr("journal.close"), 0x8890C0, s);
}


/* ------------------------------------------------- nameplate and notification banners */
/* 12x12 pixel icons for the banners: '#' = icon colour, '+' = light, '.' = empty */
static const char *const ICON_OBJECTIVE[12] = {   /* a scroll with an exclamation mark */
    "..########..", ".#++++++++#.", ".#+##++##+#.", ".#++#++#++#.", ".#++#++#++#.", ".#++####++#.",
    ".#++####++#.", ".#++#++#++#.", ".#++#++#++#.", ".#+##++##+#.", ".#++++++++#.", "..########.." };
static const char *const ICON_ITEM[12] = {        /* a star */
    ".....##.....", ".....##.....", "....####....", "....####....", "############", ".##########.",
    "..########..", "...######...", "..########..", "..###..###..", ".###....###.", ".##......##." };
static const char *const ICON_CHIP[12] = {        /* a Kingdom Star Chip: a token with a star cut in it (currency, not the duel-performance star) */
    "...######...", "..#++++++#..", ".#+++##+++#.", "#++++##++++#", "#+########+#", "#++######++#",
    "#+++####+++#", "#++######++#", "#+##+++##+#.", ".#+++++++#..", "..#++++++#..", "...######..." };
static const char *const ICON_COMPLETE[12] = {    /* a check mark in a ring */
    "...######...", "..##++++##..", ".#++++++++#.", "#++++++++#.#", "#+++++++#++#", "##++#+++#++#",
    "#+#+##+#+++#", "#++###++++.#", ".#++#+++++#.", "..##++++##..", "...######...", "............" };
static const char *const ICON_COIN[12] = {        /* a coin, edge on the right */
    "...######...", "..##++++##..", ".#++####++#.", "#++#++++#++#", "#++#+##+#++#", "#++#+##+#++#",
    "#++#+##+#++#", "#++#+##+#++#", "#++#++++#++#", ".#++####++#.", "..##++++##..", "...######..." };
static const char *const ICON_XP[12] = {         /* a small chevron, for the experience bar */
    "............", "....####....", "...##++##...", "..##++++##..", ".##++##++##.", "##++##+##++#",
    "#++##+++##+#", ".##+++++##..", "..##+++##...", "...##+##....", "....###.....", "............" };

static const char *const ICON_CAPTION[12] = {     /* a feather */
    "..........##", ".........###", "........####", ".......#####", "......######", ".....#####+.",
    "....#####+..", "...#####+...", "..####+.....", ".###+.......", "##+.........", "#..........." };

/* an item's own 24 x 24 picture (assets/icon_*.bin: index bytes, then a 16 colour palette), drawn as runs of rectangles; 0 when it has none */
int Jm_ItemIcon(int x, int y, int px, const char *file)
{
    static struct { char name[64]; unsigned char idx[576]; unsigned clut[16]; int ok; } cache[12];
    int i, r, c;
    if (!file) return 0;
    for (i = 0; i < 12 && cache[i].name[0]; i++) if (!strcmp(cache[i].name, file)) break;
    if (i == 12) return 0;
    if (!cache[i].name[0]) {
        long sz = 0;
        unsigned char *d = Jm_Slurp(file, &sz);
        snprintf(cache[i].name, sizeof(cache[i].name), "%s", file);
        if (d && sz >= 608) {
            int k;
            memcpy(cache[i].idx, d, 576);
            for (k = 0; k < 16; k++) {
                unsigned v = d[576 + k * 2] | (d[577 + k * 2] << 8);
                cache[i].clut[k] = ((v & 31) * 255 / 31) << 16 | (((v >> 5) & 31) * 255 / 31) << 8 | (((v >> 10) & 31) * 255 / 31);
            }
            cache[i].ok = 1;
        }
        free(d);
    }
    if (!cache[i].ok) return 0;
    for (r = 0; r < 24; r++)
        for (c = 0; c < 24;) {
            int v = cache[i].idx[r * 24 + c], e = c + 1;
            while (e < 24 && cache[i].idx[r * 24 + e] == v) e++;
            if (v) jm_host->fill(jm_host, x + c * px, y + r * px, (e - c) * px, px, cache[i].clut[v & 15], 255);
            c = e;
        }
    return 1;
}

static void draw_icon(int x, int y, int px, const char *const *rows, unsigned col, unsigned light)
{
    int r, c;
    for (r = 0; r < 12; r++)
        for (c = 0; c < 12; c++) {
            char ch = rows[r][c];
            if (ch == '#') jm_host->fill(jm_host, x + c * px, y + r * px, px, px, col, 255);
            else if (ch == '+') jm_host->fill(jm_host, x + c * px, y + r * px, px, px, light, 255);
        }
}

/* ------------------------------------------------------------------- the HUD
 * A panel that is always on while the player walks the village: his face, his name, the level with
 * the bar to the next one, the star chips the game itself counts, and the purse.
 *
 * It is drawn in two layers, because a mod has no way to put a picture in the overlay: the face is a
 * quad in the game's scene (Gfx_Portrait, 320x240 space) and everything else is overlay text and
 * rectangles in window pixels.  So the panel's place is worked out once, here, and the face's place
 * is derived from it - that way the two layers cannot drift apart. */
#define FACE_TEX 48            /* the portrait in the atlas is 48 x 48 */

static void hud_box(int w, int s, int top, int vis, int *x, int *y, int *bw, int *bh, int *face)
{
    int lh = 16 * s + 8;
    *face = lh * 2 / FACE_TEX * FACE_TEX;   /* two rows of text, rounded to whole face texels */
    if (*face < FACE_TEX) *face = FACE_TEX;
    *bw = w * 30 / 100;
    if (*bw < *face + 150 * s) *bw = *face + 150 * s;
    *bh = *face + 14 * s;
    *x = w / 48;
    *y = top + vis / 40;
}

/* The player's face, drawn in the overlay as runs of rectangles.
 *
 * It began as a quad in the game's scene, which was wrong: the overlay is the whole window, and
 * where the game's picture sits inside it - under the menu bar, letterboxed as the aspect setting
 * says - is the port's own business (layout.dst in pc/platform/sdl.c) and is not handed to a mod.
 * There is no sound way to line the two up, so the face is read out of the texture atlas once and
 * drawn in the overlay with the rest of the HUD, in the same units, where it cannot drift.
 * The item banners already draw their pictures this way (draw_item_icon). */
static int hud_portrait(int x, int y, int px, int which)
{
    static unsigned char faces[4][FACE_TEX * FACE_TEX * 3];
    static unsigned char solid[4][FACE_TEX * FACE_TEX];
    static int loaded;                  /* 0 not tried, 1 there, -1 no atlas */
    int r, c;
    if (!loaded) {
        long size = 0;
        unsigned char *d = Jm_Slurp("assets/atlas.raw", &size);
        int aw = d && size >= 4 ? (d[0] | d[1] << 8) : 0;
        int ah = d && size >= 4 ? (d[2] | d[3] << 8) : 0;
        loaded = -1;
        if (d && aw >= PORT_X + 4 * FACE_TEX && ah >= PORT_Y + FACE_TEX &&
            size >= 4 + (long)aw * ah * 2) {
            int k;
            for (k = 0; k < 4; k++)
                for (r = 0; r < FACE_TEX; r++)
                    for (c = 0; c < FACE_TEX; c++) {
                        const unsigned char *t = d + 4 + ((size_t)(PORT_Y + r) * aw +
                                                          PORT_X + k * FACE_TEX + c) * 2;
                        unsigned v = (unsigned)t[0] | ((unsigned)t[1] << 8);
                        unsigned char *o = faces[k] + ((size_t)r * FACE_TEX + c) * 3;
                        o[0] = (unsigned char)((v & 31) * 255 / 31);
                        o[1] = (unsigned char)(((v >> 5) & 31) * 255 / 31);
                        o[2] = (unsigned char)(((v >> 10) & 31) * 255 / 31);
                        solid[k][(size_t)r * FACE_TEX + c] = (unsigned char)(v != 0);
                    }
            loaded = 1;
        }
        free(d);
    }
    if (loaded != 1) return 0;
    which &= 3;
    if (px < 1) px = 1;
    for (r = 0; r < FACE_TEX; r++)
        for (c = 0; c < FACE_TEX;) {
            const unsigned char *o = faces[which] + ((size_t)r * FACE_TEX + c) * 3;
            int end = c + 1;
            if (!solid[which][(size_t)r * FACE_TEX + c]) { c++; continue; }   /* 0 is see-through */
            while (end < FACE_TEX && solid[which][(size_t)r * FACE_TEX + end] &&
                   !memcmp(faces[which] + ((size_t)r * FACE_TEX + end) * 3, o, 3)) end++;
            jm_host->fill(jm_host, x + c * px, y + r * px, (end - c) * px, px,
                          ((unsigned)o[0] << 16) | ((unsigned)o[1] << 8) | o[2], 255);
            c = end;
        }
    return FACE_TEX * px;
}

static void hud_panel(int w, int s, int top, int vis)
{
    int x, y, bw, bh, face, lh = 16 * s + 8, tx, into = 0, span = 0, barw, bary;
    char buf[64];
    if (!Eco_Ready() || w <= 0 || vis <= 0 || s <= 0) return;
    hud_box(w, s, top, vis, &x, &y, &bw, &bh, &face);
    jm_host->fill(jm_host, x, y, bw, bh, 0x0C0E2C, 200);
    jm_host->fill(jm_host, x, y, bw, 2 * s, 0xC8A03C, 255);
    jm_host->fill(jm_host, x, y + bh - 2 * s, bw, 2 * s, 0xC8A03C, 255);
    jm_host->fill(jm_host, x, y, 2 * s, bh, 0xC8A03C, 255);
    jm_host->fill(jm_host, x + bw - 2 * s, y, 2 * s, bh, 0xC8A03C, 255);
    /* the frame round the face, which the scene has already drawn under this */
    jm_host->fill(jm_host, x + 5 * s, y + 5 * s, face + 4 * s, 2 * s, 0xC8A03C, 255);
    jm_host->fill(jm_host, x + 5 * s, y + 7 * s + face, face + 4 * s, 2 * s, 0xC8A03C, 255);
    jm_host->fill(jm_host, x + 5 * s, y + 5 * s, 2 * s, face + 4 * s, 0xC8A03C, 255);
    jm_host->fill(jm_host, x + 7 * s + face, y + 5 * s, 2 * s, face + 4 * s, 0xC8A03C, 255);

    hud_portrait(x + 7 * s, y + 7 * s, face / FACE_TEX, jm.portrait);

    tx = x + face + 16 * s;
    jm_host->draw_text(jm_host, tx, y + 7 * s + lh / 2, jm.name, 0xFFE9A0, s);
    Ui_Fmt1(buf, sizeof(buf), EcoTr("ui.hud_level"), Eco_Level());
    jm_host->draw_text(jm_host, x + bw - jm_host->text_width(jm_host, buf, s) - 10 * s,
                       y + 7 * s + lh / 2, buf, 0x40E0E0, s);

    /* the way to the next level, under the name */
    barw = bw - (face + 16 * s) - 10 * s;
    bary = y + 7 * s + lh;
    jm_host->fill(jm_host, tx, bary, barw, 5 * s, 0x202840, 255);
    if (Eco_XpBar(&into, &span) && span > 0)
        jm_host->fill(jm_host, tx, bary, barw * into / span, 5 * s, 0x40E0E0, 255);
    else jm_host->fill(jm_host, tx, bary, barw, 5 * s, 0xFFE9A0, 255);   /* at the cap it is full */
    draw_icon(tx - 13 * s, bary - 3 * s, s, ICON_XP, 0x40E0E0, 0x90F0F0);

    /* Two different "stars": the duel-performance star chips the game itself awards after every duel
     * (gLibrary_dwStarchips, pale star), and in the Kingdom the story's Fichas Estrela (jm.stars, a red-gold
     * token, x/10): those are wagered, lost and counted by the gates, almost money.  They never mix. */
    {
        int kingdom = jm.stage >= 6, col = kingdom ? barw / 3 : barw / 2;
        draw_icon(tx, bary + 9 * s, s, ICON_ITEM, 0xA0A8C0, 0xE8ECFF);
        snprintf(buf, sizeof(buf), "%u", (unsigned)gLibrary_dwStarchips);
        jm_host->draw_text(jm_host, tx + 15 * s, bary + 15 * s, buf, 0xD8DCF0, s);
        if (kingdom) {
            draw_icon(tx + col, bary + 9 * s, s, ICON_CHIP, 0xD04030, 0xFFD040);
            snprintf(buf, sizeof(buf), "%d/10", jm.stars);
            jm_host->draw_text(jm_host, tx + col + 15 * s, bary + 15 * s, buf, 0xFFD040, s);
        }
        draw_icon(tx + col * (kingdom ? 2 : 1), bary + 9 * s, s, ICON_COIN, 0xD8A838, 0xFFE090);
        snprintf(buf, sizeof(buf), "%d", jm.eco.coins);
        jm_host->draw_text(jm_host, tx + col * (kingdom ? 2 : 1) + 15 * s, bary + 15 * s, buf, 0xFFE9A0, s);
    }
}

/* Always-on mission shortcut: corner pill; Triangle (keyboard A) opens the journal. */
static void objective_chip(int w, int s, int lh, int top, int vis)
{
    const char *lab = Tr("hint.journal_short");
    int d = lh - 7 * s, ph = lh - 1 * s, pad = 4 * s, gap = 6 * s;
    int keyw, labw, pw, x, y, bx, by;
    if (!lab || !lab[0]) return;
    if (d < 10 * s) d = 10 * s;
    keyw = jm_host->text_width(jm_host, "A", s);
    labw = jm_host->text_width(jm_host, lab, s);
    pw = pad + d + gap + labw + pad;
    x = w - pw - 16 * s;
    y = top + 12 * s;   /* top-right corner; leave the bottom-right for talk/examine */
    if (Dev_BarOn()) y = top + 6 + (lh + 4) * 3;
    /* if minimap is on, sit just under it */
    if (minimap_on) {
        int c = 2 * s + (mini_big ? 2 * s : 0);
        int my = top + (Dev_BarOn() ? 2 * lh + 26 * s : lh + 14 * s);
        int mh = 48 * c;   /* painted minimap is roughly 48 cells tall at scale c */
        if (state == ST_PAINT) y = my + mh + 8 * s;
    }
    round_fill(x, y, pw, ph, 0x000000, 150);
    bx = x + pad;
    by = y + (ph - d) / 2;
    round_fill(bx - s, by - s, d + 2 * s, d + 2 * s, 0xE8C050, 235);
    round_fill(bx + s, by + s, d - 2 * s, d - 2 * s, 0x141C48, 255);
    jm_host->draw_text(jm_host, bx + (d - keyw) / 2, by + d / 2, "A", 0xFFE9A0, s);
    jm_host->draw_text(jm_host, bx + d + gap, y + ph / 2, lab, 0xF4F4F4, s);
}

/* greedy wrap of `text` into lines of at most `maxw` pixels */
static int wrap_lines(const char *text, int maxw, int s, char lines[][100], int max)
{
    int n = 0;
    const char *p = text;
    lines[0][0] = 0;
    while (*p && n < max) {
        char word[64];
        int k = 0;
        char trial[200];
        while (*p == ' ') p++;
        while (*p && *p != ' ' && k < 62) word[k++] = *p++;
        word[k] = 0;
        if (!k) break;
        snprintf(trial, sizeof(trial), "%s%s%s", lines[n], lines[n][0] ? " " : "", word);
        if (lines[n][0] && jm_host->text_width(jm_host, trial, s) > maxw) {
            if (++n >= max) { n = max - 1; break; }
            snprintf(lines[n], 100, "%s", word);
        } else snprintf(lines[n], 100, "%s", trial);
    }
    return lines[0][0] ? n + 1 : 0;
}

static void dialog_extras(int w, int h, int s, int lh, int top, int vis)
{
    if (state != ST_SCENE && state != ST_ASK) return;
    if (!cur_kind) {
        return;
    } else {
        static const unsigned BORDER[5] = {0, 0x40E0E0, 0xFFD030, 0x70E070, 0xD8C8A0}, BORDER2[5] = {0, 0xC0FFFF, 0xFFF0A0, 0xC8FFC8, 0xFFF4D8};
        static const unsigned BG[5] = {0, 0x082438, 0x2A1A06, 0x0C2A12, 0x2A2418};
        static const char *const KEY[5] = {"", "objective", "item", "complete", "caption"};
        char lines[6][100], title[64], key[40];
        int n, pw = w * 62 / 100, ph, px = 3 * s, x, y, a, pulse, i, tx, card = 0;
        int age = notif_age, slide = age < 18 ? (18 - age) * (18 - age) * lh / 90 : 0;
        const char *label;
        const char *const *icon = cur_kind == 1 ? ICON_OBJECTIVE : cur_kind == 2 ? ICON_ITEM : cur_kind == 3 ? ICON_COMPLETE : ICON_CAPTION;
        snprintf(key, sizeof(key), "notify.%s", KEY[cur_kind]);
        if (cur_kind == 2) {                 /* a reward that names a card the story gave: CARD OBTAINED, with its picture */
            char cn[48];
            for (i = 0; i < jm.got_count; i++) {
                cn[0] = 0;
                Cards_NameUtf8(jm.got_cards[i], cn, sizeof(cn));
                if (cn[0] && strstr(notif_text, cn)) { card = jm.got_cards[i]; snprintf(key, sizeof(key), "notify.card"); break; }
            }
        }
        label = cur_kind == 4 && notif_label[0] ? notif_label : Tr(key);
        snprintf(title, sizeof(title), "%s", label);
        n = wrap_lines(notif_text, pw - 12 * px - 16 * s, s, lines, 5);
        ph = lh * (n + 3);
        if (card && ph < 18 * px * 96 / 102 + 12 * s) ph = 18 * px * 96 / 102 + 12 * s;
        x = (w - pw) / 2;
        y = top + vis / 5 - slide;
        a = age < 10 ? age * 25 : 255;
        pulse = (age / 6) & 1;
        jm_host->fill(jm_host, 0, 0, w, h, 0, age < 12 ? age * 8 : 96);
        jm_host->fill(jm_host, x - 3 * s, y - 3 * s, pw + 6 * s, ph + 6 * s, pulse ? BORDER2[cur_kind] : BORDER[cur_kind], a);
        jm_host->fill(jm_host, x, y, pw, ph, BG[cur_kind], a);
        jm_host->fill(jm_host, x, y, pw, lh + 4 * s, BORDER[cur_kind], a / 3);
        {
            const char *ifile = NULL;
            if (card) {
                int aw = 18 * px, ah = aw * 96 / 102, ax = x + 8 * s, ay = y + 6 * s;
                jm_host->fill(jm_host, ax - 2 * s, ay - 2 * s, aw + 4 * s, ah + 4 * s, Jm_TypeFrame(card), 255);
                if (!Jm_CardArt(card, 1, ax, ay, aw, ah)) draw_icon(x + 10 * s, y + lh / 2 - 4 * s, px, icon, BORDER[cur_kind], BORDER2[cur_kind]);
            } else if (cur_kind == 2 && Story_ItemIcon(notif_text, &ifile) && Jm_ItemIcon(x + 10 * s - 2 * s, y + lh / 2 - 10 * s, px * 2 / 3, ifile)) ;
            else draw_icon(x + 10 * s, y + lh / 2 - 4 * s, px, icon, BORDER[cur_kind], BORDER2[cur_kind]);
        }
        tx = x + (card ? 18 : 12) * px + 22 * s;
        jm_host->draw_text(jm_host, tx, y + lh / 2 + 2 * s, title, BORDER2[cur_kind], s + 1);
        for (i = 0; i < n; i++) jm_host->draw_text(jm_host, tx - 8 * s, y + lh * (i + 2) + lh / 4, lines[i], 0xFFFFFF, s);
        if (age > 24 && ((age / 20) & 1) == 0) jm_host->draw_text(jm_host, x + pw - 120 * s, y + ph - lh / 2 - s, Tr("notify.press"), BORDER2[cur_kind], s);
        if (cur_kind == 2 || cur_kind == 3) {        /* sparkles around the icon */
            for (i = 0; i < 6; i++) {
                int ph2 = (age * 3 + i * 41) % 60, sz = ph2 < 30 ? ph2 / 6 + 1 : (60 - ph2) / 6 + 1;
                int sx = x + 10 * s + 6 * px + (int)(((i * 37) % 11 - 5) * 3 * s), sy = y + lh / 2 + 2 * px + (int)(((i * 53) % 9 - 4) * 4 * s);
                jm_host->fill(jm_host, sx, sy, sz * s, sz * s, 0xFFFFC0, 255 - ph2 * 3);
            }
        }
    }
}

/* Both names below their faces, during a duel.
 *
 * The face itself is a picture in the game's own scene (panel_drawn); the name is text, and the only
 * text a mod can draw is the port's overlay, which is in window pixels.  The two are lined up by
 * mapping the game's complete 320x240 picture to that canvas; the name sits below the small face.
 * The game's own "Opponent's name for COM" (View menu) is not used, because it would show the name
 * of the disc duelist whose slot a villager borrows ("Villager 1"), not the villager's. */
static void duel_nameplate(int w, int h, int s, int lh, int fx, int fy, const char *name, unsigned colour)
{
    if (!name || !*name) return;
    {
        int x = fx * w / 320;
        int y = (fy + FACE_SIZE + 6) * h / 240;
        int tw = jm_host->text_width(jm_host, name, s);
        jm_host->fill(jm_host, x - 2 * s, y, tw + 8 * s, lh, 0x0C0E2C, 210);
        jm_host->draw_text(jm_host, x + 2 * s, y + lh / 2, name, colour, s);
    }
}

static void duel_names(void)
{
    int w, h, s, lh;
    const char *opponent, *player;
    if (!face_on || duel_npc < 0) return;
    jm_host->overlay_size(jm_host, &w, &h, &s);
    if (s < 2) s = 2;
    lh = 16 * s + 8;
    opponent = TrKey("npc_names", npcs[duel_npc].id, npcs[duel_npc].name);
    player = jm.name[0] ? jm.name : Tr("defaults.player_name");
    duel_nameplate(w, h, s, lh, player_face_x, player_face_y, player, 0xB8D0FF);
    duel_nameplate(w, h, s, lh, opponent_face_x, opponent_face_y, opponent, 0xFFE9A0);
}

static void overlay(void)
{
    int w, h, s, lh, top, vis;
    char line[200];
    if (!ready) return;
    if (!ModMode_Active()) { duel_names(); return; }
    if (!Paint_Loaded() && state != ST_CREATE && state != ST_CONFIRM &&
        state != ST_LANG && state != ST_LEAVE) {        /* the picture is still coming */
        int i, dots;
        jm_host->overlay_size(jm_host, &w, &h, &s);
        if (s < 2) s = 2;
        if (w <= 0 || h <= 0) return;
        dots = (int)((frame_no / 14) % 4);
        for (i = 0; i < dots; i++)
            jm_host->fill(jm_host, w / 2 - 20 * s + i * 14 * s, h / 2, 8 * s, 8 * s, 0xC8A03C, 255);
        return;
    }
    jm_host->overlay_size(jm_host, &w, &h, &s);
    if (s < 2) s = 2;
    lh = 16 * s + 8;
    vis = w * 9 / 16;
    if (vis > h) vis = h;
    top = (h - vis) / 2;
    { static int once; if (!once++) LOG("journey: overlay %dx%d scale %d", w, h, s); }
    if (state == ST_CREATE) { Ui_CreateOverlay(); return; }
    if (state == ST_CARD) {                /* a veil, so the card reads against the village */
        int dim = card_age * 8;
        if (dim > 150) dim = 150;
        if (card_age > CARD_FRAMES - 20) dim = (CARD_FRAMES - card_age) * 150 / 20;
        if (dim < 0) dim = 0;
        jm_host->fill(jm_host, 0, 0, w, h, 0x05040E, (unsigned)dim);
        return;
    }
    if (state == ST_SHOP) { Shop_Overlay(); return; }
    if (state == ST_WAGER) { Wager_Overlay(); return; }
    if (state == ST_GAMEOVER) { GameOver_Overlay(gameover_age); return; }
    if (state == ST_ARENA) { Arena_Overlay(); return; }
    if (state == ST_CONFIRM) {
        int x = w / 6, y = top + vis / 4, pw = w * 2 / 3;
        char who[96];
        jm_host->fill(jm_host, 0, 0, w, h, 0x08061C, 235);
        jm_host->draw_text(jm_host, x, y - lh, Tr("confirm.heading"), 0xFFE9A0, s + 1);
        jm_host->fill(jm_host, x - 8, y, pw + 16, lh * 6, 0x0C0E2C, 220);
        snprintf(who, sizeof(who), Tr("confirm.saved"), jm.name, Story_Chapter());
        jm_host->draw_text(jm_host, x + 8 * s, y + lh, who, 0xFFFFFF, s);
        jm_host->draw_text(jm_host, x + 8 * s, y + lh * 2, Tr("confirm.warning"), 0xFF9090, s);
        jm_host->draw_text(jm_host, x + 28 * s, y + lh * 4, Tr("confirm.start"), choose_sel == 0 ? 0x40E0E0 : 0xB0B0B0, s);
        jm_host->draw_text(jm_host, x + 28 * s, y + lh * 5, Tr("confirm.cancel"), choose_sel == 1 ? 0x40E0E0 : 0xB0B0B0, s);
        jm_host->draw_text(jm_host, x + 12 * s, y + lh * (4 + choose_sel), ">", 0xFFFFFF, s);
        return;
    }
    if (state == ST_LANG) {
        int x = w / 3, y = top + vis / 3, pw = w / 3, i, n = Lang_Count();
        jm_host->fill(jm_host, 0, 0, w, h, 0x08061C, 235);
        jm_host->draw_text(jm_host, x, y - lh, Tr("language.label"), 0xFFE9A0, s + 1);
        jm_host->fill(jm_host, x - 8, y, pw + 16, lh * (n + 2), 0x0C0E2C, 220);
        for (i = 0; i < n; i++) {
            jm_host->draw_text(jm_host, x + 20 * s, y + lh * (i + 1), Lang_Name(i), i == lang_sel ? 0x40E0E0 : 0xB0B0B0, s);
            if (i == lang_sel) jm_host->draw_text(jm_host, x + 4 * s, y + lh * (i + 1), ">", 0xFFFFFF, s);
        }
        jm_host->draw_text(jm_host, x, y + lh * (n + 3), Tr("language.hint"), 0x8890C0, s);
        return;
    }
    if (state == ST_PAINT) {
        int n = Paint_NearNpc();
        snprintf(line, sizeof(line), Tr("hud.status_line"), place_name(), Story_Chapter(), Story_Objective());
        if (Dev_BarOn()) bar(top + 6, lh, line, 0xFFE9A0);
        if (Dev_BarOn()) {                 /* why the Jackals and the arena do or do not answer */
            char dbg[160];
            float ax, ay, asx, asy;
            Gang_Debug(dbg, sizeof(dbg));
            bar(top + 6 + lh + 4, lh, dbg, 0xFF9090);
            Paint_Info(&ax, &ay, &asx, &asy);
            Arena_Debug(dbg, sizeof(dbg), ax, ay);
            bar(top + 6 + (lh + 4) * 2, lh, dbg, 0xFFB060);
        }
        hud_panel(w, s, top, vis);         /* face, name, level, the bar, stars and the purse */
        objective_chip(w, s, lh, top, vis); /* current mission + Triangle shortcut */
        if (area_banner > 0) {
            const char *nm = place_name();
            int tw = jm_host->text_width(jm_host, nm, s + 1);
            jm_host->fill(jm_host, w / 2 - tw / 2 - 16, top + vis / 5, tw + 32, lh * 2, 0, 150);
            jm_host->draw_text(jm_host, w / 2 - tw / 2, top + vis / 5 + lh, nm, 0x40C0E0, s + 1);
        }
        if (minimap_on) {
            int c = 2 * s + (mini_big ? 2 * s : 0);
            Paint_MiniMap(w - 48 * c - 14 * s, top + (Dev_BarOn() ? 2 * lh + 26 * s : lh + 14 * s), c, s);
        }
        if (n >= 0) hint_pill(w, s, lh, top, vis, Tr("hint.talk_short"));
        else if (near_object() || near_arena_door()) hint_pill(w, s, lh, top, vis, Tr("hint.examine_short"));
        if (Ui_MessageText()) {
            int tw = jm_host->text_width(jm_host, Ui_MessageText(), s);
            jm_host->fill(jm_host, w - tw - 30 * s, top + 6 + (Dev_BarOn() ? lh + 6 : 0), tw + 24 * s, lh, 0, 170);
            jm_host->draw_text(jm_host, w - tw - 18 * s, top + 6 + (Dev_BarOn() ? lh + 6 : 0) + lh / 2, Ui_MessageText(), Ui_MessageColour(), s);
        }
        return;
    }
    if (state == ST_JOURNAL) { journal_overlay(w, h, s, lh, top, vis); return; }
    if (state == ST_MENU) { Ui_MenuOverlay(); return; }
    if (state == ST_MAP) {
        int tx0, tz0, tx1, tz1, px, mw, mh, x, y;
        region(&tx0, &tz0, &tx1, &tz1);
        px = (vis - 4 * lh) / (tz1 - tz0 + 1);
        if (px > (w * 2 / 3) / (tx1 - tx0 + 1)) px = (w * 2 / 3) / (tx1 - tx0 + 1);
        if (px < 2) px = 2;
        mw = px * (tx1 - tx0 + 1);
        mh = px * (tz1 - tz0 + 1);
        x = (w - mw) / 2;
        y = top + (vis - mh) / 2;
        jm_host->fill(jm_host, 0, 0, w, h, 0x000000, 200);
        jm_host->fill(jm_host, x - 4 * s, y - 4 * s, mw + 8 * s, mh + 8 * s, 0xC8A03C, 255);
        draw_map(x, y, px, tx0, tz0, tx1, tz1, s);
        snprintf(line, sizeof(line), "%s  -  %s", Tr("map.title"), World_AreaName(World_Area(jm.x, jm.z)));
        jm_host->draw_text(jm_host, x, y - 4 * s - lh / 2 - 2, line, 0xFFE9A0, s);
        snprintf(line, sizeof(line), "%s: %s", Tr("hud.objective_label"), Story_Objective());
        jm_host->draw_text(jm_host, x, y + mh + 4 * s + lh / 2 + 4, line, 0xFFFFFF, s);
        jm_host->draw_text(jm_host, x, y + mh + 4 * s + lh + lh / 2 + 4, Tr("map.close"), 0x8890C0, s);
        return;
    }
    snprintf(line, sizeof(line), Tr("hud.status_line"), place_name(), Story_Chapter(), Story_Objective());
    if (Dev_BarOn()) bar(top + 6, lh, line, 0xFFE9A0);
    if (area_banner > 0 && state == ST_WALK) {
        const char *n = World_AreaName(area);
        int tw = jm_host->text_width(jm_host, n, s + 1);
        jm_host->fill(jm_host, w / 2 - tw / 2 - 16, top + vis / 5, tw + 32, lh * 2, 0, 150);
        jm_host->draw_text(jm_host, w / 2 - tw / 2, top + vis / 5 + lh, n, 0x40C0E0, s + 1);
    }
    if (state == ST_WALK && minimap_on) {
        int px = 3 * s, tx0, tz0, tx1, tz1, rx0, rz0, rx1, rz1, cx = (int)(jm.x / TS), cz = (int)(jm.z / TS), x, y;
        region(&rx0, &rz0, &rx1, &rz1);
        tx0 = cx - 15; tx1 = cx + 15; tz0 = cz - 9; tz1 = cz + 9;
        if (tx0 < rx0) { tx1 += rx0 - tx0; tx0 = rx0; }
        if (tx1 > rx1) { tx0 -= tx1 - rx1; tx1 = rx1; }
        if (tz0 < rz0) { tz1 += rz0 - tz0; tz0 = rz0; }
        if (tz1 > rz1) { tz0 -= tz1 - rz1; tz1 = rz1; }
        if (tx0 < rx0) tx0 = rx0;
        if (tz0 < rz0) tz0 = rz0;
        x = w - (tx1 - tx0 + 1) * px - 14 * s;
        y = top + (Dev_BarOn() ? lh + 24 * s : 12 * s);
        jm_host->fill(jm_host, x - 3 * s, y - 3 * s, (tx1 - tx0 + 1) * px + 6 * s, (tz1 - tz0 + 1) * px + 6 * s, 0xC8A03C, 255);
        draw_map(x, y, px, tx0, tz0, tx1, tz1, s);
    }
    if (state == ST_WALK) {
        int n = near_npc();
        objective_chip(w, s, lh, top, vis);
        if (n >= 0) hint_pill(w, s, lh, top, vis, Tr("hint.talk_short"));
        else if (has_poi()) hint_pill(w, s, lh, top, vis, Tr("hint.examine_short"));
    }
    if (state == ST_ASK) {                  /* the question stays in the box (the game's font); the choices sit above its right end */
        int bx = w * 0x10 / 320, by = h * 0xA0 / 240, bw = w * 0x120 / 320, pw = bw / 4, ph = lh * 2 + 12 * s, px = bx + bw - pw - 6 * s, py = by - ph - 8 * s;
        jm_host->fill(jm_host, px - 2 * s, py - 2 * s, pw + 4 * s, ph + 4 * s, 0xE8C050, 255);
        jm_host->fill(jm_host, px, py, pw, ph, 0x0C0E2C, 245);
        jm_host->fill(jm_host, px + 3 * s, py + 5 * s + (ask_sel ? lh : 0), pw - 6 * s, lh, 0x2038A0, 220);
        jm_host->draw_text(jm_host, px + 28 * s, py + 5 * s + lh / 2 - 6 * s, Tr("ask.yes"), ask_sel == 0 ? 0xFFFFA0 : 0xB0B0B0, s);
        jm_host->draw_text(jm_host, px + 28 * s, py + 5 * s + lh + lh / 2 - 6 * s, Tr("ask.no"), ask_sel == 1 ? 0xFFFFA0 : 0xB0B0B0, s);
        jm_host->draw_text(jm_host, px + 10 * s, py + 5 * s + (ask_sel ? lh : 0) + lh / 2 - 6 * s, ">", 0xFFFFFF, s);
    }
    if (Ui_MessageText()) {
        int tw = jm_host->text_width(jm_host, Ui_MessageText(), s);
        jm_host->fill(jm_host, w - tw - 30 * s, top + 6 + (Dev_BarOn() ? lh + 6 : 0), tw + 24 * s, lh, 0, 170);
        jm_host->draw_text(jm_host, w - tw - 18 * s, top + 6 + (Dev_BarOn() ? lh + 6 : 0) + lh / 2, Ui_MessageText(), Ui_MessageColour(), s);
    }
    dialog_extras(w, h, s, lh, top, vis);
}

static unsigned overlay_sig(void)
{
    /* outside our own mode the only thing drawn is the duelling opponent's name */
    if (!ModMode_Active())
        return face_on ? 2166136261u + (unsigned)opponent_face_x * 131u + (unsigned)opponent_face_y * 7919u +
                         (unsigned)player_face_x * 17u + (unsigned)(duel_npc + 1) * 1009u : 0u;
    if (!Paint_Loaded()) return 3u + (unsigned)(frame_no / 14) * 131u;   /* the waiting dots */
    if (state == ST_CARD) return 17u + (unsigned)card_age * 131u;
    if (state == ST_SHOP) return 11u + Shop_Signature();
    if (state == ST_WAGER) return 19u + Wager_Signature();
    if (state == ST_GAMEOVER) return 23u + GameOver_Signature(gameover_age);
    if (state == ST_ARENA) return 13u + Arena_Signature();
    if (state == ST_PAINT) {
        float a, b, c, d;
        const char *obj = Story_Objective();
        unsigned oh = 2166136261u;
        Paint_Info(&a, &b, &c, &d);
        if (obj) while (*obj) oh = oh * 16777619u + (unsigned char)*obj++;
        return 7u + (unsigned)(Paint_NearNpc() + 2) * 131u + (near_object() ? 77u : 0u) + (unsigned)minimap_on * 17u + (unsigned)mini_big * 29u + (unsigned)(area_banner > 0 ? area_banner : 0) * 7919u +
               (unsigned)(ui_message_timer > 0) * 1000003u + (unsigned)(jm.stage * 41 + (int)jm.flags * 7 + (int)jm.kflags * 13 + jm.stars * 977) + (unsigned)(Lang_Current() * 1237) + (unsigned)Dev_BarOn() * 3331u +
               (unsigned)(minimap_on ? (int)(frame_no / 10 & 1) * 100003 + (int)a / 12 * 4421 + (int)b / 12 * 977 : 0) +
               (unsigned)jm.eco.coins * 1009u + (unsigned)jm.eco.xp * 97u + (unsigned)gLibrary_dwStarchips * 131u +
               (unsigned)near_arena_door() * 7u + oh;   /* objective chip text */
    }
    return (state == ST_SCENE || state == ST_ASK ? (unsigned)(scene_idx * 131 + cur_kind * 17 + (cur_kind ? notif_age : 0) * 3571 + (cur_name ? (unsigned char)cur_name[0] * 31 : 0)) : 0u) + 1u + (unsigned)state * 977u + (unsigned)(area + 2) * 31u + (unsigned)(area_banner > 0 ? area_banner : 0) * 7919u +
           (unsigned)(near_npc() + 2) * 131u + (unsigned)ask_sel * 17u + (unsigned)choose_sel * 3u + (unsigned)(state == ST_CONFIRM) * 7001u + Ui_Signature() * 13u +
           (unsigned)(ui_message_timer > 0) * 1000003u + (unsigned)(jm.stage * 41 + (int)jm.flags * 7 + (int)jm.kflags * 13 + jm.stars * 977) +
           (has_poi() ? 5u : 0u) + (unsigned)Dev_BarOn() * 3331u + (unsigned)(Lang_Current() * 1237 + lang_sel * 53 + minimap_on * 7) +
           ((state == ST_WALK && minimap_on) || state == ST_MAP ? (unsigned)((int)(jm.x / TS) * 4421 + (int)(jm.z / TS) * 977 + (int)(frame_no / 10 & 1) * 100003) : 0u);
}

/* ----------------------------------------------------------------- events */
enum { OW_SELECTION = 40 };

static void on_menu(MemoriesModEvent *e)
{
    const char *name = e->phase == MEMORIES_BEFORE ? jm_host->menu_item(jm_host, e->a) : NULL;
    if (name && (!strcmp(name, "ow-poc:new") || !strcmp(name, "ow-poc:continue"))) {
        menu_request = !strcmp(name, "ow-poc:new") ? REQ_NEW : REQ_CONTINUE;
        e->handled = 1;
        e->result = OW_SELECTION;
    }
}

static void on_scene(MemoriesModEvent *e)
{
    if (e->a != OW_SELECTION) return;
    if (e->phase == MEMORIES_BEFORE) {
        e->handled = 1;
        after_return = RET_NONE;
        state = ST_LEAVE;
        ModMode_Enter();
    } else {
        return_menu = D_8009B26D;
    }
}

int MemoriesModInit(const MemoriesModHost *h, MemoriesMod *mod)
{
    jm_host = h;
    mod->api = MEMORIES_MOD_API;
    mod->frame = frame_hook;
    mod->overlay = overlay;
    mod->overlay_signature = overlay_sig;
    Story_Reset();
    ModMode_Register(run);
    h->hook(h, (void *)Duel_SelectCardDrop, (void *)drop_pick, (void **)&drop_original);
    h->hook(h, (void *)Duel_DrawLifePointsAndDeckCounts, (void *)panel_drawn, (void **)&panel_original);
    h->subscribe(h, MEMORIES_EVENT_MENU, 0, on_menu);
    h->subscribe(h, MEMORIES_EVENT_SCENE, 0, on_scene);
    return 1;
}
