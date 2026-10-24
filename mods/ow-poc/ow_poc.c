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

enum { ST_CHOOSE, ST_CREATE, ST_WALK, ST_SCENE, ST_ASK, ST_MENU, ST_TO_DUEL, ST_LEAVE, ST_LANG, ST_MAP };
enum { RET_NONE, RET_DUEL, RET_NAME, RET_DECK };
static int state = ST_CHOOSE, after_return = RET_NONE;
static int ready, choose_sel, lang_sel, minimap_on = 1;
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
static const JsonNode *duel_win, *duel_lose;
static const char *scene_then;             /* a scene to play next */
static const JsonNode *scene_choice;       /* {yes, no} results of a Yes/No page that is not a duel */
static int pend_duel = -1;                 /* a duel to start when the ask page is answered yes */
static int portrait_x = -1, portrait_y;    /* atlas position of the speaker's face, -1 none */
static int loaded_face = -1;

/* area music and banner */
static int area = -1, area_cand = -1, area_count, area_timer, area_banner;

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
    if (sp) { *name = TrKey("speaker_names", p->who, Json_Str(sp, "name", p->name)); face = (int)Json_Num(sp, "portrait_id", 0); }
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
    Say_Page(&p);
    state = ST_SCENE;
}

static void begin_scene(const char *id, int intro, int result)
{
    scene_id = id;
    scene_idx = 0;
    scene_n = id ? Story_PageCount(id) : 0;
    scene_intro = intro;
    scene_result = result;
    pend_duel = -1;
    if (scene_n < 1) { LOG("journey: no scene %s", id ? id : "(null)"); scene_then = NULL; scene_choice = NULL; state = ST_WALK; return; }
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

static void end_scene(void)
{
    Say_Close();
    portrait_x = -1;
    cooldown = 20;
    state = ST_WALK;
    if (scene_then) {
        const char *next = scene_then;
        scene_then = NULL;
        begin_scene(next, 0, scene_result);
        return;
    }
    if (scene_intro && jm.stage < 1) jm.stage = 1;
    if (scene_intro || scene_result) {
        jm_save_ok = Save_Write();
        Ui_Message(Tr(jm_save_ok ? "messages.progress_saved" : "messages.save_failed"));
    }
    scene_intro = scene_result = 0;
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

static void arm_duel(int npc)
{
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
    } else { state = ST_WALK; cooldown = 20; }
}

/* --------------------------------------------------------------- the world */
static void start_talk(const Talk *t)
{
    begin_scene(t->scene, 0, 0);
    if (state == ST_SCENE && t->duel >= 0) {
        pend_duel = t->duel;
        duel_win = t->on_win;
        duel_lose = t->on_lose;
    }
}

static void music_tick(void)
{
    int a = World_Area(jm.x, jm.z);
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
    ensure_deck();
    World_Spawn(&jm.x, &jm.z);
    cam_x = jm.x;
    cam_z = jm.z;
    World_PlaceNpcs();
    lang_sel = Lang_Current();
    state = ST_LANG;                       /* the language first, then the creator */
}

static void continue_journey(void)
{
    if (!Save_Read()) { new_journey(); return; }
    Lang_Set(jm.lang);
    Story_Regrant();
    ensure_deck();
    World_PlaceNpcs();
    cam_x = jm.x;
    cam_z = jm.z;
    state = ST_WALK;
}

static void run(int first)
{
    unsigned short pad = jm_host->pad(jm_host, 0), edge = (unsigned short)(pad & ~pad_prev);
    pad_prev = pad;
    if (first) {
        if (!ready) {
            ready = Gfx_LoadAssets() && Story_Load() && World_Load() && Lang_Set(0);
            if (ready) Save_Init();
        }
        if (!ready) { ModMode_Leave(return_menu); return; }
        Tower_Background(0);
        Fade_WaitIn();
        area = -1;
        LOG("journey: mode on (return %d)", after_return);
        switch (after_return) {
        case RET_DUEL: duel_returned(); break;
        case RET_NAME: after_return = RET_NONE; Ui_RefreshName(); state = ST_CREATE; break;
        case RET_DECK: after_return = RET_NONE; state = ST_WALK; cooldown = 10; break;
        default:
            if (Save_Exists()) {
                if (Save_Read()) Lang_Set(jm.lang);       /* the menu speaks the saved language */
                choose_sel = 0;
                state = ST_CHOOSE;
            } else new_journey();
        }
        return;
    }
    frame_no++;
    if (cooldown > 0) cooldown--;
    if (ui_message_timer > 0) ui_message_timer--;
    switch (state) {
    case ST_CHOOSE:
        if (edge & (PAD_UP | PAD_DOWN)) choose_sel ^= 1;
        if (edge & PAD_CROSS) { if (choose_sel == 0) continue_journey(); else new_journey(); }
        if (edge & PAD_TRIANGLE) state = ST_LEAVE;
        break;
    case ST_LANG:
        if (edge & (PAD_UP | PAD_DOWN)) {
            int n = Lang_Count();
            lang_sel = (lang_sel + (edge & PAD_UP ? n - 1 : 1)) % n;
            Lang_Set(lang_sel);
        }
        if (edge & PAD_CROSS) {
            strncpy(jm.name, Tr("defaults.player_name"), sizeof(jm.name) - 1);
            Ui_StartCreate();
            state = ST_CREATE;
        }
        if (edge & PAD_TRIANGLE) {
            if (Save_Exists() && Save_Read()) { Lang_Set(jm.lang); state = ST_CHOOSE; } else state = ST_LEAVE;
        }
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
            begin_scene("c1_intro", 1, 0);
            if (state != ST_SCENE) state = ST_WALK;
        }
        if (edge & PAD_TRIANGLE) { if (Save_Exists()) state = ST_CHOOSE; else state = ST_LEAVE; }
        break;
    case ST_WALK:
        music_tick();
        walk_tick(pad, edge);
        if (state == ST_WALK) Guide_Update();
        break;
    case ST_SCENE:
        walking = 0;
        music_tick();
        if (Say_Done()) {
            Page p;
            Story_Page(scene_id, scene_idx, &p);
            if (p.ask) { state = ST_ASK; ask_sel = 0; Say_Close(); break; }
            scene_idx++;
            if (scene_idx >= scene_n) end_scene(); else open_page();
        }
        break;
    case ST_ASK:
        music_tick();
        if (edge & (PAD_LEFT | PAD_RIGHT | PAD_UP | PAD_DOWN)) ask_sel ^= 1;
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
        if (r == 1) { state = ST_WALK; cooldown = 10; }
        else if (r == 2) go_screen(7, RET_DECK);
        else if (r == 3) state = ST_LEAVE;
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
    if (state == ST_CHOOSE || state == ST_LANG || state == ST_MAP) { Gfx_Backdrop(0x08061C, 0x2A2060); Gfx_End(); return; }
    jm_guide_on = state == ST_WALK;
    Gfx_SetCamera(CAM_D, CAM_PITCH);
    Ui_BodyColours(colours);
    World_Draw(jm.x, jm.z, pyaw, walking, colours, Gfx_Mesh(Ui_BodyMesh()));
    if (portrait_x >= 0 && (state == ST_SCENE || state == ST_ASK)) Gfx_Portrait(14, 40, 84, portrait_x, portrait_y);
}

/* ---------------------------------------------------------------- overlay */
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
    if (state == ST_CHOOSE) {
        int x = w / 3, y = top + vis / 3, pw = w / 3;
        jm_host->fill(jm_host, 0, 0, w, h, 0x08061C, 235);
        jm_host->draw_text(jm_host, x, y - lh, Tr("choose.heading"), 0xFFE9A0, s + 1);
        jm_host->fill(jm_host, x - 8, y, pw + 16, lh * 3, 0x0C0E2C, 220);
        jm_host->draw_text(jm_host, x + 20 * s, y + lh, Tr("choose.continue"), choose_sel == 0 ? 0x40E0E0 : 0xB0B0B0, s);
        jm_host->draw_text(jm_host, x + 20 * s, y + lh * 2, Tr("choose.new_journey"), choose_sel == 1 ? 0x40E0E0 : 0xB0B0B0, s);
        jm_host->draw_text(jm_host, x + 4 * s, y + lh * (1 + choose_sel), ">", 0xFFFFFF, s);
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
    snprintf(line, sizeof(line), Tr("hud.status_line"), World_AreaName(area < 0 ? 0 : area), Story_Chapter(), Story_Objective());
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
    if (state == ST_ASK) {
        int x = w - w / 4, y = top + vis / 2 - lh;
        jm_host->fill(jm_host, x, y, w / 5, lh * 3, 0x0C0E2C, 225);
        jm_host->draw_text(jm_host, x + 24 * s, y + lh, Tr("ask.yes"), ask_sel == 0 ? 0x40E0E0 : 0xA0A0A0, s);
        jm_host->draw_text(jm_host, x + 24 * s, y + lh * 2, Tr("ask.no"), ask_sel == 1 ? 0x40E0E0 : 0xA0A0A0, s);
        jm_host->draw_text(jm_host, x + 8 * s, y + lh * (1 + ask_sel), ">", 0xFFFFFF, s);
    }
    if (Ui_MessageText()) {
        int tw = jm_host->text_width(jm_host, Ui_MessageText(), s);
        jm_host->fill(jm_host, w - tw - 30 * s, top + 6 + lh + 6, tw + 24 * s, lh, 0, 170);
        jm_host->draw_text(jm_host, w - tw - 18 * s, top + 6 + lh + 6 + lh / 2, Ui_MessageText(), 0x60F060, s);
    }
}

static unsigned overlay_sig(void)
{
    if (!ModMode_Active()) return 0u;
    return 1u + (unsigned)state * 977u + (unsigned)(area + 2) * 31u + (unsigned)(area_banner > 0 ? area_banner : 0) * 7919u +
           (unsigned)(near_npc() + 2) * 131u + (unsigned)ask_sel * 17u + (unsigned)choose_sel * 3u + Ui_Signature() * 13u +
           (unsigned)(ui_message_timer > 0) * 1000003u + (unsigned)(jm.stage * 41 + (int)jm.flags * 7) +
           (has_poi() ? 5u : 0u) + (unsigned)(Lang_Current() * 1237 + lang_sel * 53 + minimap_on * 7) +
           ((state == ST_WALK && minimap_on) || state == ST_MAP ? (unsigned)((int)(jm.x / TS) * 4421 + (int)(jm.z / TS) * 977 + (int)(frame_no / 10 & 1) * 100003) : 0u);
}

/* ----------------------------------------------------------------- events */
enum { OW_SELECTION = 40 };

static void on_menu(MemoriesModEvent *e)
{
    const char *name = e->phase == MEMORIES_BEFORE ? jm_host->menu_item(jm_host, e->a) : NULL;
    if (name && !strcmp(name, "ow-poc:journey")) {
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
        state = ST_CHOOSE;
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
