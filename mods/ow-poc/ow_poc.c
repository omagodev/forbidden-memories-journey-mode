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

const MemoriesModHost *jm_host;
int jm_save_requested, jm_save_ok, jm_name_entry_requested;

enum { ST_CONFIRM, ST_CREATE, ST_WALK, ST_SCENE, ST_ASK, ST_MENU, ST_TO_DUEL, ST_LEAVE, ST_LANG, ST_MAP, ST_PAINT, ST_JOURNAL };
enum { REQ_NONE, REQ_NEW, REQ_CONTINUE };   /* what the title's NEW GAME / CONTINUE asked for */
enum { RET_NONE, RET_DUEL, RET_NAME, RET_DECK };
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

static void begin_scene(const char *id, int intro, int result)
{
    scene_id = id;
    scene_idx = 0;
    scene_n = id ? Story_PageCount(id) : 0;
    scene_intro = intro;
    scene_result = result;
    pend_duel = -1;
    if (scene_n < 1) { LOG("journey: no scene %s", id ? id : "(null)"); scene_then = NULL; scene_choice = NULL; state = in_paint_flow ? ST_PAINT : ST_WALK; if (in_paint_flow) { in_paint_flow = 0; Paint_TalkEnd(); } return; }
    LOG("journey: scene %s (%d pages)", id, scene_n);
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
    int had_effects = scene_effects != NULL && !Json_Get(scene_effects, "warp");      /* a walk through the hatch alone is not progress to save */
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
    state = in_paint_flow ? ST_PAINT : ST_WALK;
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
    for (i = 0; i < 40; i++) {
        gDuel_awPlayerDeck[i] = (u16)(1 + i);
        if (gLibrary_abCardChest[1 + i] < 3) gLibrary_abCardChest[1 + i] = 3;
    }
    LOG("journey: starter deck given (the save had none)");
}

static void duel_returned(void);
static void arm_duel(int npc)
{
    if (Dbg_WinDuels()) {                  /* debug: no duel is played, it counts as won */
        LOG("debug: duel against %s skipped (counts as won)", npcs[npc].name);
        Say_Close();
        portrait_x = -1;
        jm.duels++;
        D_8009B362 = 0;
        after_return = RET_DUEL;
        duel_npc = npc;
        duel_returned();
        return;
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
    state = ST_TO_DUEL;
    LOG("journey: duel against %s (duelist %d)", npcs[npc].name, npcs[npc].duelist_id);
    func_80024DC8(-1, npcs[npc].duelist_id, 0x6000, 0x6000);
}

static void duel_returned(void)
{
    int won = (D_8009B362 == 0);
    const JsonNode *r = won ? duel_win : duel_lose;
    area = -1;                              /* the duel's song ended the village's: start it again */
    if (in_paint_flow) { Paint_Enter(); paint_auto = 1; }    /* the duel took the banks: the painted village is loaded again behind the scene */
    if (won) jm.wins++; else jm.losses++;
    LOG("journey: duel over, %s (wins %d, losses %d)", won ? "won" : "lost", jm.wins, jm.losses);
    if (won) Story_ApplyResult(duel_win);
    World_PlaceNpcs();
    after_return = RET_NONE;
    duel_npc = -1;
    apply_warp();
    if (r && Json_Str(r, "scene", NULL)) {
        begin_scene(Json_Str(r, "scene", NULL), 0, 1);
        scene_then = Json_Str(r, "then", NULL);
        scene_choice = Json_Get(r, "choice");
    } else if (in_paint_flow) { in_paint_flow = 0; Paint_TalkEnd(); state = ST_PAINT; cooldown = 20; }
    else { state = ST_WALK; cooldown = 20; }
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
 * scene and until the Stamp Card is given).  `area < 0` restarts the music (after a duel, the intro, a warp). */
static int pm_cur = -1, pm_timer, pm_ctx = -1;
static int menu_from_paint;                /* the START menu was opened in the painted village: the picture stays behind it, and Close returns to it */
static int painted_ctx(void) { return state == ST_PAINT || state == ST_JOURNAL || in_paint_flow || (state == ST_MENU && menu_from_paint); }
static int track_cfg(const char *key)
{
    const JsonNode *po = Json_Get(jm_rules, "painted"), *mu = po ? Json_Get(po, "music") : NULL;
    return (int)Json_Num(mu, key, -1);
}

/* the place name of the HUD and the banner: the painted areas have their own (ui.json "painted"), else the old map's */
static const char *place_name(void)
{
    return painted_ctx() && Paint_Area() == 1 ? Tr("painted.cistern") : World_AreaName(area < 0 ? 0 : area);
}

static void music_tick(void)
{
    int a = World_Area(jm.x, jm.z), pc = painted_ctx();
    if (pc != pm_ctx) { pm_ctx = pc; area = -1; pm_cur = -1; pm_timer = 0; }     /* into or out of the painted village: its own song */
    if (pc && track_cfg("day") >= 0) {
        int want = Paint_Area() == 1 && track_cfg("cistern") >= 0 ? track_cfg("cistern") : track_cfg(Paint_IsNight() && track_cfg("night") >= 0 ? "night" : "day");
        if (area < 0) { area = area_cand = a; area_banner = 150; area_timer = 0; pm_cur = -1; pm_timer = 0; }
        if (pm_cur < 0) { SD_BGMPlay(0x7000 + (u32)want * 0x10); pm_cur = want; LOG("journey: music %d (%s)", want, Paint_Area() == 1 ? "cistern" : want == track_cfg("night") ? "night" : "day"); }
        else if (want != pm_cur && !pm_timer) { SD_BGMFadeOut(); pm_timer = 45; pm_cur = want; }
        if (pm_timer && --pm_timer == 0) { SD_BGMPlay(0x7000 + (u32)pm_cur * 0x10); LOG("journey: music %d (%s)", pm_cur, Paint_Area() == 1 ? "cistern" : pm_cur == track_cfg("night") ? "night" : "day"); }
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
    if ((edge & PAD_L1) && in_village()) { Paint_Enter(); state = ST_PAINT; return; }
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
    paint_area = 0;
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

static void continue_journey(void)
{
    if (!Save_Read()) { new_journey(); return; }
    Lang_Set(jm.lang);
    paint_area = 0;                        /* a save keeps the hatch (the village) even if it was made in the cistern */
    Dbg_Apply();
    Story_Regrant();
    ensure_deck();
    World_PlaceNpcs();
    cam_x = jm.x;
    cam_z = jm.z;
    if (jm.pt_set) Paint_Set(jm.pt_x, jm.pt_y);   /* and back to where it stood in the painted village */
    state = ST_WALK;
}

static void run(int first)
{
    unsigned short pad = jm_host->pad(jm_host, 0), edge = (unsigned short)(pad & ~pad_prev);
    pad_prev = pad;
    if (first) {
        if (!ready) {
            ready = Gfx_LoadAssets() && Story_Load() && World_Load() && Lang_Set(0);
            if (ready) { Save_Init(); Dbg_Init(); }
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
        case RET_DECK: after_return = RET_NONE; state = ST_WALK; cooldown = 10; break;
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
    case ST_PAINT:
        if (edge & PAD_START) { Ui_MenuOpen(); menu_from_paint = 1; state = ST_MENU; break; }   /* START: the menu (deck editor, items, status, save, title) */
        music_tick();
        if (edge & PAD_SELECT) minimap_on ^= 1;
        if (edge & PAD_TRIANGLE) { state = ST_JOURNAL; break; }
        if (!cooldown) {                       /* a state of the story that starts a scene by itself (the three stamps) */
            Talk at;
            if (Story_Auto(&at)) {
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
            if (n >= 0 && Story_TalkRule(&npcs[n], &t)) {
                Paint_TalkStart(n);
                in_paint_flow = 1;
                start_talk(&t);
                if (state != ST_SCENE) { in_paint_flow = 0; Paint_TalkEnd(); state = ST_PAINT; }
                break;
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
        if (Paint_Tick(pad, edge)) {
            if (paint_exit) {      /* across the bridge: the harbor is not built yet (part 2): back to the south bank */
                paint_exit = 0;
                Paint_Set(652.0f, 190.0f);
                Ui_Message(Tr("messages.part_end"));
            } else { state = ST_WALK; cooldown = 10; }
        }
        break;
    case ST_JOURNAL:
        music_tick();
        if (edge & (PAD_TRIANGLE | PAD_CIRCLE | PAD_CROSS | PAD_START | PAD_SELECT)) { state = ST_PAINT; cooldown = 10; }
        break;
    case ST_MAP:
        if (edge & (PAD_TRIANGLE | PAD_CIRCLE | PAD_CROSS | PAD_SELECT | PAD_START)) state = ST_WALK;
        break;
    case ST_CREATE:
        if (jm_name_entry_requested) { jm_name_entry_requested = 0; go_screen(9, RET_NAME); return; }
        if (Ui_CreateInput(edge)) {
            jm.stage = 0;
            World_PlaceNpcs();
            area = -1;
            Paint_Enter();                         /* the story opens in the painted village, at the home door */
            paint_auto = 1;
            in_paint_flow = 1;
            begin_scene(Json_Str(jm_rules, "intro", "c1_intro"), 1, 0);
            if (state != ST_SCENE) state = ST_PAINT;
        }
        if (edge & PAD_TRIANGLE) state = ST_LEAVE;     /* back to the title; a saved journey stays as it was */
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
            if (ask_sel == 0 && pend_duel >= 0) { arm_duel(pend_duel); break; }
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
        if (r == 1) { state = menu_from_paint && Paint_Loaded() ? ST_PAINT : ST_WALK; menu_from_paint = 0; cooldown = 10; }
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

/* ------------------------------------------------------------------ frame */
static void frame_hook(void)
{
    int colours[5];
    if (!ModMode_Active() || !ready) return;
    Gfx_Begin();
    if (state == ST_CREATE) { Ui_DrawCreate(); return; }
    if (state == ST_CONFIRM || state == ST_LANG || state == ST_MAP) { Gfx_Backdrop(0x08061C, 0x2A2060); Gfx_End(); return; }
    if (state == ST_PAINT || state == ST_JOURNAL || (state == ST_MENU && menu_from_paint) || (in_paint_flow && (state == ST_SCENE || state == ST_ASK))) {
        Ui_BodyColours(colours);
        paint_markers = state == ST_PAINT;
        Paint_Draw(Gfx_Mesh(Ui_BodyMesh()), colours);
        Gfx_End();
        if (portrait_x >= 0 && state != ST_PAINT) Gfx_Portrait(14, 40, 84, portrait_x, portrait_y);
        return;
    }
    jm_guide_on = state == ST_WALK;
    Gfx_SetCamera(CAM_D, CAM_PITCH);
    Ui_BodyColours(colours);
    World_Draw(jm.x, jm.z, pyaw, walking, colours, Gfx_Mesh(Ui_BodyMesh()));
    if (portrait_x >= 0 && (state == ST_SCENE || state == ST_ASK)) Gfx_Portrait(14, 40, 84, portrait_x, portrait_y);
}

/* ---------------------------------------------------------------- overlay */
static int near_object(void) { Talk t; int o = Paint_NearObject(); return o >= 0 && Paint_ObjectRule(o, &t); }
static int near_npc(void) { return state == ST_WALK ? World_NearestNpc(jm.x, jm.z, 64) : -1; }
static int has_poi(void) { Talk t; return state == ST_WALK && Story_PoiAt(jm.x, jm.z, &t); }

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
static const char *const ICON_COMPLETE[12] = {    /* a check mark in a ring */
    "...######...", "..##++++##..", ".#++++++++#.", "#++++++++#.#", "#+++++++#++#", "##++#+++#++#",
    "#+#+##+#+++#", "#++###++++.#", ".#++#+++++#.", "..##++++##..", "...######...", "............" };
static const char *const ICON_CAPTION[12] = {     /* a feather */
    "..........##", ".........###", "........####", ".......#####", "......######", ".....#####+.",
    "....#####+..", "...#####+...", "..####+.....", ".###+.......", "##+.........", "#..........." };

/* an item's own 24 x 24 picture (assets/icon_*.bin: index bytes, then a 16 colour palette), drawn as runs of rectangles; 0 when it has none */
static int draw_item_icon(int x, int y, int px, const char *file)
{
    static struct { char name[64]; unsigned char idx[576]; unsigned clut[16]; int ok; } cache[6];
    int i, r, c;
    for (i = 0; i < 6 && cache[i].name[0]; i++) if (!strcmp(cache[i].name, file)) break;
    if (i == 6) return 0;
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
        int n, pw = w * 62 / 100, ph, px = 3 * s, x, y, a, pulse, i, tx;
        int age = notif_age, slide = age < 18 ? (18 - age) * (18 - age) * lh / 90 : 0;
        const char *label;
        const char *const *icon = cur_kind == 1 ? ICON_OBJECTIVE : cur_kind == 2 ? ICON_ITEM : cur_kind == 3 ? ICON_COMPLETE : ICON_CAPTION;
        snprintf(key, sizeof(key), "notify.%s", KEY[cur_kind]);
        label = cur_kind == 4 && notif_label[0] ? notif_label : Tr(key);
        snprintf(title, sizeof(title), "%s", label);
        n = wrap_lines(notif_text, pw - 12 * px - 16 * s, s, lines, 5);
        ph = lh * (n + 3);
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
            if (cur_kind == 2 && Story_ItemIcon(notif_text, &ifile) && draw_item_icon(x + 10 * s - 2 * s, y + lh / 2 - 10 * s, px * 2 / 3, ifile)) ;
            else draw_icon(x + 10 * s, y + lh / 2 - 4 * s, px, icon, BORDER[cur_kind], BORDER2[cur_kind]);
        }
        tx = x + 12 * px + 22 * s;
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

static void overlay(void)
{
    int w, h, s, lh, top, vis;
    char line[200];
    if (!ModMode_Active() || !ready) return;
    jm_host->overlay_size(jm_host, &w, &h, &s);
    if (s < 2) s = 2;
    lh = 16 * s + 8;
    vis = w * 9 / 16;
    if (vis > h) vis = h;
    top = (h - vis) / 2;
    { static int once; if (!once++) LOG("journey: overlay %dx%d scale %d", w, h, s); }
    if (state == ST_CREATE) { Ui_CreateOverlay(); return; }
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
        bar(top + 6, lh, line, 0xFFE9A0);
        if (area_banner > 0) {
            const char *nm = place_name();
            int tw = jm_host->text_width(jm_host, nm, s + 1);
            jm_host->fill(jm_host, w / 2 - tw / 2 - 16, top + vis / 5, tw + 32, lh * 2, 0, 150);
            jm_host->draw_text(jm_host, w / 2 - tw / 2, top + vis / 5 + lh, nm, 0x40C0E0, s + 1);
        }
        if (minimap_on) {
            int c = 2 * s + (mini_big ? 2 * s : 0);
            Paint_MiniMap(w - 48 * c - 14 * s, top + 2 * lh + 26 * s, c, s);
        }
        if (n >= 0) snprintf(line, sizeof(line), Tr("hint.talk"), npc_name(n));
        else if (near_object()) snprintf(line, sizeof(line), "%s", Tr("hint.examine"));
        else snprintf(line, sizeof(line), "%s", Tr("hint.painted"));
        bar(top + vis - lh - 6, lh, line, 0xFFFFFF);
        if (Ui_MessageText()) {
            int tw = jm_host->text_width(jm_host, Ui_MessageText(), s);
            jm_host->fill(jm_host, w - tw - 30 * s, top + 6 + lh + 6, tw + 24 * s, lh, 0, 170);
            jm_host->draw_text(jm_host, w - tw - 18 * s, top + 6 + lh + 6 + lh / 2, Ui_MessageText(), 0x60F060, s);
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
    bar(top + 6, lh, line, 0xFFE9A0);
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
        y = top + lh + 24 * s;
        jm_host->fill(jm_host, x - 3 * s, y - 3 * s, (tx1 - tx0 + 1) * px + 6 * s, (tz1 - tz0 + 1) * px + 6 * s, 0xC8A03C, 255);
        draw_map(x, y, px, tx0, tz0, tx1, tz1, s);
    }
    if (state == ST_WALK) {
        int n = near_npc();
        if (n >= 0) snprintf(line, sizeof(line), Tr("hint.talk"), npc_name(n));
        else if (has_poi()) snprintf(line, sizeof(line), "%s", Tr("hint.examine"));
        else snprintf(line, sizeof(line), "%s   %s", Tr("hint.controls"), Tr("map.hint"));
        bar(top + vis - lh - 6, lh, line, 0xFFFFFF);
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
        jm_host->fill(jm_host, w - tw - 30 * s, top + 6 + lh + 6, tw + 24 * s, lh, 0, 170);
        jm_host->draw_text(jm_host, w - tw - 18 * s, top + 6 + lh + 6 + lh / 2, Ui_MessageText(), 0x60F060, s);
    }
    dialog_extras(w, h, s, lh, top, vis);
}

static unsigned overlay_sig(void)
{
    if (!ModMode_Active()) return 0u;
    if (state == ST_PAINT) {
        float a, b, c, d;
        Paint_Info(&a, &b, &c, &d);
        return 7u + (unsigned)(Paint_NearNpc() + 2) * 131u + (near_object() ? 77u : 0u) + (unsigned)minimap_on * 17u + (unsigned)mini_big * 29u + (unsigned)(area_banner > 0 ? area_banner : 0) * 7919u +
               (unsigned)(ui_message_timer > 0) * 1000003u + (unsigned)(jm.stage * 41 + (int)jm.flags * 7) + (unsigned)(Lang_Current() * 1237) +
               (unsigned)(minimap_on ? (int)(frame_no / 10 & 1) * 100003 + (int)a / 12 * 4421 + (int)b / 12 * 977 : 0);
    }
    return (state == ST_SCENE || state == ST_ASK ? (unsigned)(scene_idx * 131 + cur_kind * 17 + (cur_kind ? notif_age : 0) * 3571 + (cur_name ? (unsigned char)cur_name[0] * 31 : 0)) : 0u) + 1u + (unsigned)state * 977u + (unsigned)(area + 2) * 31u + (unsigned)(area_banner > 0 ? area_banner : 0) * 7919u +
           (unsigned)(near_npc() + 2) * 131u + (unsigned)ask_sel * 17u + (unsigned)choose_sel * 3u + (unsigned)(state == ST_CONFIRM) * 7001u + Ui_Signature() * 13u +
           (unsigned)(ui_message_timer > 0) * 1000003u + (unsigned)(jm.stage * 41 + (int)jm.flags * 7) +
           (has_poi() ? 5u : 0u) + (unsigned)(Lang_Current() * 1237 + lang_sel * 53 + minimap_on * 7) +
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
    h->subscribe(h, MEMORIES_EVENT_MENU, 0, on_menu);
    h->subscribe(h, MEMORIES_EVENT_SCENE, 0, on_scene);
    return 1;
}
