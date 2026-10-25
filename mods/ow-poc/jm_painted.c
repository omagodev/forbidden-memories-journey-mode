/* Painted-background prototype ("painted village"): a pre-painted 1280x720 picture drawn as a grid of
 * textured quads (16-bit direct colour, banks PB_BANK0..), a coarse collision mask, characters drawn live
 * from the existing meshes with the usual projection, and "occluder" cutouts of the picture (houses, palms)
 * that are drawn again, depth sorted by their base line, so people walk behind them. */
#include "types.h"
#include "psyq/libgte.h"
#include "psyq/libgpu.h"
#include "psyq/libgs.h"
#include "pc/render/soft_gpu.h"
#include "jm.h"
#include "painted_data.h"
#include <math.h>
#include <stdlib.h>
#include <string.h>

#define PB_BANK0 8
#define TPU 2                      /* texels per game unit */
#define VIEW_W 320
#define VIEW_H 240
#define PCAM_D 1400.0f
#define PCAM_PITCH 40.0f
#define PSCALE 2.3f
#define WATER_TICKS 9               /* game frames a water frame stays (about 6.7 a second at 60 fps) */

static int loaded, load_failed;
int paint_area;                    /* 0 the village, 1 the old cistern (journey.json "area" of anchors, objects and people) */
enum { AREA_VILLAGE, AREA_CISTERN, AREA_COUNT };
static const struct { const char *name, *pic, *col, *occ; int cw, ch, cell; } parea[AREA_COUNT] = {
    {"village", "assets/painted.raw", "assets/painted_col.bin", NULL, 160, 90, 8},
    {"cistern", "assets/painted_cistern.raw", "assets/painted_cistern_col.bin", "assets/painted_cistern_occ.bin", 320, 180, 4},
};
static unsigned char *col;         /* the collision mask: col_w x col_h cells of col_cell texels (the village 160 x 90 of 8, the cistern 320 x 180 of 4) */
static int col_w = 160, col_h = 90, col_cell = 8;
#define MAX_OCC 64
static short occ_t[MAX_OCC][4];    /* the occluder cells: x0, y0, cell, base_y */
static int nocc;
static int fade_in;                /* frames of fade from black after entering an area */
float pt_x = 640, pt_y = 450;      /* the player's feet, in texels of the picture */
static float scr_x, scr_y;         /* the scroll, in game units */
static float yaw = 3.14159265f;
int paint_view;                    /* 0 all, 1 picture only, 2 no occluders */
int paint_anim = 1;                /* water animation on (L2 / R2 toggles) */
#define ANIM_BANK0 4               /* water frames: banks 4.. (3 for 6 frames of 11 cells) */
static int wframes, wn;            /* frames, water cells */
static short wslot[PB_COLS * PB_ROWS];   /* cell -> index among the water cells, or -1 */
static int walking;
int paint_sway = 1;                /* palm sway on (R2 toggles; L2 toggles the water) */
#define PALM_TICKS 20              /* game frames a sway frame stays: 8 steps = a 2.7 s ping-pong at 60 fps */
#define MAXPALM 24
static const unsigned char palm_banks[] = {1, 2, 3, 7, 12};   /* free in the village (3D Monsters use 1-12 in duels, so everything is re-uploaded on entry) */
static const unsigned char sway_seq[8] = {0, 1, 2, 3, 4, 3, 2, 1};   /* frame 2 = the rest picture */
typedef struct { int x0, y0, by, first, n; unsigned char kc[6][2]; } PPalm;
static PPalm ppalm[MAXPALM];
static int npalm, pframes;


static void unproject(float sx, float sy, float *wx, float *wz, float *z);
static void draw_marker(void);
static void mini_build(const unsigned char *banks);
static int blocked(float x, float y);
static void props_load(void);
static int bench_at(float *x, float *y);
/* ---------------------------------------------------------------- sprite characters
 * Pre-rendered 4-direction sheets (sprite_work/bake_sprites.py): 48x62 texels a frame, feet at (24,56), 2 texels per game unit.
 * Per texel the file keeps what is needed to colour it at load time (a slot weight for skin/hair/outfit/trousers and a fixed
 * colour), so the character creator's colours can be applied without re-rendering. Frames live in a bank, two 256x256 pages
 * per character: frames 0-4 on the first page, 5-6 on the second; one row per direction (down, left, right, up). */
#define SPR_CW 48
#define SPR_CH 62
#define SPR_FX 24
#define SPR_FY 56
enum { SPR_KENNEY_M, SPR_PLAYER_MESH, SPR_AI, SPR_SIMON, SPR_TEANA, SPR_JONO, SPR_GUARD, SPR_RIVAL, SPR_MAGO, SPR_BAKER, SPR_FARMER, SPR_REX, SPR_BAKURA, SPR_COUNT };
typedef struct { const char *file; int recolour; int nf; unsigned char *kind, *wt, *rgb; int ok; int bank, page; } Spr;
static Spr spr[SPR_COUNT] = {
    {"assets/spr_kenney_m.bin", 0}, {"assets/spr_player.bin", 1}, {"assets/spr_ai.bin", 0},
    {"assets/spr_simon.bin", 0}, {"assets/spr_teana.bin", 0}, {"assets/spr_jono.bin", 0}, {"assets/spr_guard.bin", 0},
    {"assets/spr_rival.bin", 0}, {"assets/spr_mago_robe.bin", 0}, {"assets/spr_baker.bin", 0}, {"assets/spr_farmer.bin", 0},
    {"assets/spr_rex.bin", 0}, {"assets/spr_bakura.bin", 0},
};
/* Where each sheet lives: bank 13 has eight 256x256 pages. A 7-frame sheet takes two pages, a 5-frame sheet one. Bank 15 is still free. */
static const unsigned char spr_bank[SPR_COUNT] = {13, 13, 13, 13, 13, 13, 13, 15, 15, 15, 15, 15, 15};
static const unsigned char spr_page[SPR_COUNT] = {0, 2, 3, 4, 5, 6, 7, 0, 1, 2, 3, 6, 7};   /* bank 15: pages 0-3 the DK people, 4 the bench and the hatch, 5 the aura and the torch glow, 6 Rex, 7 the ghost */
int paint_sprite = 3;               /* 0 3D mesh, 1 Kenney sprite, 2 sprite baked from the player's mesh, 3 painted (AI) sprite, 4 all side by side */
static int spr_baked[SPR_COUNT];   /* cleared when the painted scene is entered: banks are reloaded then */
static int face = 0;              /* 0 down, 1 left, 2 right, 3 up */
static int spr_colours[5] = {-2, 0, 0, 0, 0};

static int spr_load(int i)
{
    long size;
    unsigned char *d, *p;
    int cells, tex;
    Spr *s = &spr[i];
    if (s->ok) return 1;
    if (s->nf < 0) return 0;
    d = Jm_Slurp(s->file, &size);
    if (!d || size < 14 || memcmp(d, "SPR1", 4)) { LOG("sprite: cannot read %s", s->file); s->nf = -1; free(d); return 0; }
    s->nf = d[4] | d[5] << 8;
    cells = s->nf * 4; tex = SPR_CW * SPR_CH;
    if (size < 14 + (long)cells * tex * 8 || s->nf > 7) { s->nf = -1; free(d); return 0; }
    s->kind = malloc((size_t)cells * tex); s->wt = malloc((size_t)cells * tex * 4); s->rgb = malloc((size_t)cells * tex * 3);
    p = d + 14;
    {
        int c;
        for (c = 0; c < cells; c++) {
            memcpy(s->kind + (size_t)c * tex, p, (size_t)tex); p += tex;
            memcpy(s->wt + (size_t)c * tex * 4, p, (size_t)tex * 4); p += tex * 4;
            memcpy(s->rgb + (size_t)c * tex * 3, p, (size_t)tex * 3); p += tex * 3;
        }
    }
    free(d);
    s->bank = spr_bank[i]; s->page = spr_page[i];   /* (bank 7 is the palms', 15 is free) */
    s->ok = 1;
    return 1;
}

static unsigned short rgb555(int r, int g, int b)
{
    r = r < 0 ? 0 : r > 255 ? 255 : r; g = g < 0 ? 0 : g > 255 ? 255 : g; b = b < 0 ? 0 : b > 255 ? 255 : b;
    return (unsigned short)(0x8000 | (r >> 3) | (g >> 3) << 5 | (b >> 3) << 10);
}

/* The ghost's see-through body is baked as a 1-texel dither, but sprites are drawn at 2 texels to a screen pixel with point sampling, so a
 * 1-texel checker keeps only one parity of texels and the whole body vanishes.  So the dither is redone at the drawn resolution: each aligned 2x2
 * block takes the average colour of its opaque texels and is kept, whole, where its opacity beats an ordered 2x2 threshold. */
static void ghost_blocks(uint16_t *bank, int ox, int oy)
{
    static const float thr[2][2] = {{0.125f, 0.625f}, {0.875f, 0.375f}};
    int bx, by, x, y;
    for (by = 0; by < SPR_CH / 2; by++)
        for (bx = 0; bx < SPR_CW / 2; bx++) {
            int n = 0, r = 0, g = 0, b = 0;
            unsigned short out = 0;
            for (y = 0; y < 2; y++)
                for (x = 0; x < 2; x++) {
                    unsigned short v = bank[(size_t)(oy + by * 2 + y) * 1024 + ox + bx * 2 + x];
                    if (v) { n++; r += (v & 31); g += (v >> 5) & 31; b += (v >> 10) & 31; }
                }
            if (n && n / 4.0f > thr[by & 1][bx & 1]) out = (unsigned short)(0x8000 | (r / n) | (g / n) << 5 | (b / n) << 10);
            for (y = 0; y < 2; y++)
                for (x = 0; x < 2; x++) bank[(size_t)(oy + by * 2 + y) * 1024 + ox + bx * 2 + x] = out;
        }
}

/* write the colours of one character into its bank pages (outline colour 34,24,30) */
static void spr_bake(int i, const int pal[5])
{
    Spr *s = &spr[i];
    uint16_t *bank = SoftGpu_Bank(s->bank);
    int dir, f, x, y, tex = SPR_CW * SPR_CH;
    if (!bank || !s->ok) return;
    for (dir = 0; dir < 4; dir++)
        for (f = 0; f < s->nf; f++) {
            int cell = dir * s->nf + f, page = s->page + (f >= 5), col = f % 5;
            int ox = (page & 3) * 256 + col * SPR_CW, oy = (page >> 2) * 256 + dir * 64;
            const unsigned char *k = s->kind + (size_t)cell * tex, *w = s->wt + (size_t)cell * tex * 4, *c = s->rgb + (size_t)cell * tex * 3;
            for (y = 0; y < SPR_CH; y++)
                for (x = 0; x < SPR_CW; x++) {
                    int n = y * SPR_CW + x;
                    unsigned short v = 0;
                    if (k[n] == 254) v = rgb555(34, 24, 30);
                    else if (k[n] == 0) {
                        float r = c[n * 3], g = c[n * 3 + 1], b = c[n * 3 + 2];
                        if (s->recolour && pal) {
                            int q;
                            for (q = 1; q <= 4; q++) {
                                float wq = w[n * 4 + q - 1] / 100.0f;
                                if (pal[q] < 0 || wq == 0) continue;
                                r += wq * ((pal[q] >> 16) & 255); g += wq * ((pal[q] >> 8) & 255); b += wq * (pal[q] & 255);
                            }
                        }
                        v = rgb555((int)(r + 0.5f), (int)(g + 0.5f), (int)(b + 0.5f));
                    }
                    bank[(size_t)(oy + y) * 1024 + ox + x] = v;
                }
            if (strstr(s->file, "bakura")) ghost_blocks(bank, ox, oy);
        }
}

static int spr_dir_from_yaw(float yw)
{
    while (yw > 3.14159265f) yw -= 6.2831853f;
    while (yw < -3.14159265f) yw += 6.2831853f;
    if (fabsf(yw) < 0.7854f) return 0;
    if (yw >= 0.7854f && yw < 2.3562f) return 2;
    if (yw <= -0.7854f && yw > -2.3562f) return 1;
    return 3;
}

static void draw_spr_lift(int i, float tx, float ty, int dir, int frame, float shadow, float lift)
{
    Spr *s = &spr[i];
    float sx = tx / TPU - scr_x, sy = ty / TPU - scr_y, wx, wz, z;
    int f, page, col;
    if (!s->ok || sx < -40 || sx > VIEW_W + 40 || sy < -20 || sy > VIEW_H + 80) return;
    unproject(sx, sy, &wx, &wz, &z);
    if (shadow > 0) Gfx_Shadow(wx, wz, shadow);
    f = frame < s->nf ? frame : 0;
    page = s->page + (f >= 5); col = f % 5;
    Gfx_SpriteQuad((int)floorf(sx + 0.5f) - SPR_FX / 2, (int)floorf(sy + 0.5f - lift) - SPR_FY / 2, SPR_CW / 2, SPR_CH / 2, s->bank, page,
                   col * SPR_CW, dir * 64, SPR_CW, SPR_CH, z);
}
static void draw_spr(int i, float tx, float ty, int dir, int frame, float shadow) { draw_spr_lift(i, tx, ty, dir, frame, shadow, 0); }

static int spr_frame_of(int i, int moving)
{
    Spr *s = &spr[i];
    if (!moving || s->nf < 2) return 0;
    return 1 + (int)((gfx_frame / (s->nf > 5 ? 3 : 5)) % (unsigned)(s->nf - 1));
}
static int spr_walk_frame(int i)
{
    Spr *s = &spr[i];
    if (!walking || s->nf < 2) return 0;
    return 1 + (int)((gfx_frame / (s->nf > 5 ? 3 : 4)) % (unsigned)(s->nf - 1));
}

static void sprites_prepare(const int body_rgb[5])
{
    int i, same = 1;
    for (i = 0; i < 5; i++) if (body_rgb && body_rgb[i] != spr_colours[i]) same = 0;
    for (i = 0; i < SPR_COUNT; i++) {
        int fresh = !spr_baked[i];
        if (!spr_load(i)) continue;
        if (fresh || (spr[i].recolour && !same)) { spr_bake(i, body_rgb); spr_baked[i] = 1; }
    }
    if (body_rgb) memcpy(spr_colours, body_rgb, sizeof(spr_colours));
}

const char *Paint_ModeName(void)
{
    static const char *const n[5] = {"3D mesh", "sprite: Kenney, animated skeleton", "sprite: baked from the 3D mesh", "sprite: hand-painted (AI)", "side by side: Kenney | baked | painted | 3D"};
    return n[paint_sprite % 5];
}

/* The village people (Journey Mode's chapter 1 cast): a sprite sheet (painted from the character's Forbidden Memories portrait) and the
 * 3D mesh the comparison mode (Z, "3D mesh") still shows. A patrol is a back and forth walk along one axis around the anchor. */
typedef struct { const char *mesh; int spr; float x, y, yaw; int patrol_axis; float range; float ax, ay; int dirn; int pause; int moving; int gathered; int area; float hover; } PNpc;
static PNpc pnpc[] = {
    {"Wizard", SPR_SIMON, 560, 250, 0.5f, 0, 0},              /* Simon Muran, standing */
    {"Ninja_Sand_Female", SPR_TEANA, 300, 392, -0.7f, 2, 36},   /* Teana, a short stroll up and down */
    {"Knight_Male", SPR_GUARD, 652, 168, 0.0f, 0, 0},         /* the Guard, at the south end of the bridge */
    {"Ninja_Sand", SPR_JONO, 120, 392, 0.0f, 1, 60},            /* Jono, walks to and fro */
    {"Wizard", SPR_RIVAL, 600, 300, 0.0f, 0, 0},            /* the hooded man (placed by the story at night) */
    {"Worker_Male", SPR_BAKER, 950, 585, 0.0f, 0, 0},           /* Hakim the baker */
    {"Ninja_Sand", SPR_FARMER, 700, 470, 1.5708f, 1, 40},       /* Kemet the farmer, a short stroll */
    {"Suit_Male", SPR_REX, 1215, 425, 4.7124f, 0, 0},            /* Rex Raptor on the east road (the story places him) */
    {"Wizard", SPR_BAKURA, 638, 365, 0.0f, 0, 0, 0, 0, 0, 0, 0, 0, AREA_CISTERN, 1.2f},   /* the ghost Bakura on the dais of the cistern: he hovers */
};
#define NPN ((int)(sizeof(pnpc) / sizeof(pnpc[0])))
static int npc_init;
/* Which journey.json person each villager is (the order of pnpc[]), and the talk state. */
static const char *const pid[NPN] = {"simon", "teana", "guard", "jono", "hooded_man", "baker", "farmer", "rex", "bakura"};
#define GUARD 2
static short guard_home[2] = {652, 168};   /* the bridge_north anchor (set from the table below) */
static const short guard_aside[2] = {566, 176};   /* he steps aside once the bridge is open */
/* The symbolic places of journey.json ("anchor") bound to picture texels (the 1280 x 720 painted village). */
static const struct { const char *name; short x, y; unsigned char area; } anchors[] = {
    {"hero_start", 184, 273, 0}, {"plaza_center", 600, 300, 0}, {"plaza_bench", 500, 292, 0}, {"house_ne_door", 1150, 262, 0},
    {"teana_stall", 252, 676, 0}, {"bakery_door", 950, 585, 0}, {"bridge_north", 652, 168, 0},
    {"farmer_field", 700, 470, 0}, {"mago_roof", 1205, 128, 0}, {"notice_sign", 1094, 340, 0},
    {"mini_pyramid_hatch", 182, 278, 0}, {"hatch_prop", 148, 262, 0}, {"date_palm", 840, 345, 0}, {"river_bank", 480, 114, 0}, {"east_road", 1215, 425, 0}, {"rex_approach", 1128, 432, 0},
    {"spawn_stairs", 638, 222, 1}, {"exit_stairs", 639, 50, 1}, {"bakura_spot", 638, 365, 1}, {"wall_glyph", 388, 200, 1},
};
const char *Paint_AnchorName(int i) { return i >= 0 && i < (int)(sizeof(anchors) / sizeof(anchors[0])) ? anchors[i].name : NULL; }
static int time_ov = -1;
int Paint_ForcedTime(void) { return time_ov; }
int Paint_AnchorArea(const char *name)
{
    int i;
    for (i = 0; name && i < (int)(sizeof(anchors) / sizeof(anchors[0])); i++)
        if (!strcmp(anchors[i].name, name)) return anchors[i].area;
    return -1;
}
int Paint_Area(void) { return paint_area; }
int paint_area_now(void) { return paint_area; }
int Paint_Anchor(const char *name, float *x, float *y)
{
    int i;
    for (i = 0; name && i < (int)(sizeof(anchors) / sizeof(anchors[0])); i++)
        if (!strcmp(anchors[i].name, name)) { *x = anchors[i].x; *y = anchors[i].y; return 1; }
    return 0;
}
static int ptalk[NPN];                  /* 1 while the player talks to him: he stands still and faces the player */
static int guard_block;                 /* the bridge is shut: the Guard has not been moved yet */
#define TALK_REACH 84.0f                /* texels: how close the feet must be to talk */
#define EXIT_X0 598
#define EXIT_X1 706
#define EXIT_Y 76                       /* the north bank: the bridge ends here and the next area (the 3D map) starts */
int paint_exit;                         /* the player has crossed the bridge */
static int sitting;                     /* the player sits on the bench (a scene is playing) */
static float night_t, night_target;     /* 0 day .. 1 night: the tint of the picture follows the target */
static int obs_on, obs_glitch;          /* the observer on the roof: shown / vanishing in a glitch (frames left) */
static const JsonNode *obs_cfg;         /* its entry of journey.json painted.observers */
int paint_markers = 1;                  /* the objective marker and edge arrow (off while a scene plays) */
extern int Story_Cond(const JsonNode *c);

static int load(void)
{
    long size;
    unsigned char *d;
    int b;
    if (loaded) return 1;
    if (load_failed) return 0;
    free(col);
    col_w = parea[paint_area].cw; col_h = parea[paint_area].ch; col_cell = parea[paint_area].cell;
    col = Jm_Slurp(parea[paint_area].col, &size);
    if (col && size < (long)col_w * col_h) { free(col); col = NULL; }
    d = Jm_Slurp(parea[paint_area].pic, &size);
    if (!col || !d || size < 8 + (long)PB_BANKS * 1024 * 512 * 2) { LOG("painted: assets missing"); load_failed = 1; return 0; }
    nocc = 0;
    if (parea[paint_area].occ) {
        long osz;
        unsigned char *o = Jm_Slurp(parea[paint_area].occ, &osz);
        int n = o && osz >= 2 ? o[0] | o[1] << 8 : 0, i;
        if (n > MAX_OCC || osz < 2 + 8L * n) n = 0;
        for (i = 0; i < n; i++) for (b = 0; b < 4; b++) occ_t[i][b] = (short)(o[2 + i * 8 + b * 2] | o[3 + i * 8 + b * 2] << 8);
        nocc = n;
        free(o);
    } else {
        for (b = 0; b < PB_OCC; b++) { occ_t[b][0] = pb_occ[b][0]; occ_t[b][1] = pb_occ[b][1]; occ_t[b][2] = pb_occ[b][2]; occ_t[b][3] = pb_occ[b][3]; }
        nocc = PB_OCC;
    }
    for (b = 0; b < PB_BANKS; b++) {
        uint16_t *bank = SoftGpu_Bank(PB_BANK0 + b);
        if (!bank) { LOG("painted: no bank %d", PB_BANK0 + b); load_failed = 1; return 0; }
        memcpy(bank, d + 8 + (size_t)b * 1024 * 512 * 2, 1024 * 512 * 2);
    }
    mini_build(d + 8);
    free(d);
    wframes = wn = 0;
    memset(wslot, -1, sizeof(wslot));
    d = paint_area == AREA_VILLAGE ? Jm_Slurp("assets/painted_water.raw", &size) : NULL;
    if (d && size >= 4) {
        int nf = d[0] | d[1] << 8, nc = d[2] | d[3] << 8, k, nb;
        long need = 4 + 2L * nc + (long)nf * nc * 128 * 128 * 2;
        nb = (nf * nc + 31) / 32;
        if (size >= need && nc <= PB_COLS * PB_ROWS && ANIM_BANK0 + nb <= PB_BANK0) {
            const unsigned char *cells = d + 4, *px = d + 4 + 2 * nc;
            for (k = 0; k < nb; k++) { if (!SoftGpu_Bank(ANIM_BANK0 + k)) break; }
            if (k == nb) {
                for (k = 0; k < nf * nc; k++) {   /* slot k -> bank cell: 8 columns x 4 rows of 128x128 per bank */
                    uint16_t *bank = SoftGpu_Bank(ANIM_BANK0 + k / 32);
                    int cx = (k % 32) % 8, cy = (k % 32) / 8, row;
                    for (row = 0; row < 128; row++)
                        memcpy(bank + (size_t)(cy * 128 + row) * 1024 + cx * 128, px + ((size_t)k * 128 + row) * 128 * 2, 128 * 2);
                }
                for (k = 0; k < nc; k++) wslot[cells[k * 2] | cells[k * 2 + 1] << 8] = (short)k;
                wframes = nf; wn = nc;
                LOG("painted: water animation, %d frames x %d cells, %d banks (%ld bytes)", nf, nc, nb, size);
            }
        }
        free(d);
    }
    npalm = pframes = 0;
    d = paint_area == AREA_VILLAGE ? Jm_Slurp("assets/painted_palms.raw", &size) : NULL;
    if (d && size >= 8) {
        int nf = d[0] | d[1] << 8, np = d[2] | d[3] << 8, nc = d[4] | d[5] << 8, i, k, ok = (nf == 5 && np <= MAXPALM);
        const unsigned char *p = d + 8;
        int nb = (nc + 31) / 32;
        if (nb > (int)sizeof(palm_banks)) ok = 0;
        for (i = 0; ok && i < np; i++) {
            PPalm *q = &ppalm[i];
            if (p + 10 > d + size) { ok = 0; break; }
            q->x0 = p[0] | p[1] << 8; q->y0 = p[2] | p[3] << 8; q->by = p[4] | p[5] << 8; q->first = p[6] | p[7] << 8; q->n = p[8];
            p += 10;
            if (q->n > 6 || p + q->n * 2 > d + size) { ok = 0; break; }
            for (k = 0; k < q->n; k++) { q->kc[k][0] = p[k * 2]; q->kc[k][1] = p[k * 2 + 1]; }
            p += q->n * 2;
        }
        if (ok && size >= (p - d) + (long)nc * 128 * 128 * 2) {
            for (k = 0; k < nb; k++) if (!SoftGpu_Bank(palm_banks[k])) ok = 0;
            if (ok) {
                for (k = 0; k < nc; k++) {
                    uint16_t *bank = SoftGpu_Bank(palm_banks[k / 32]);
                    int cx = (k % 32) % 8, cy = (k % 32) / 8, row;
                    for (row = 0; row < 128; row++)
                        memcpy(bank + (size_t)(cy * 128 + row) * 1024 + cx * 128, p + ((size_t)k * 128 + row) * 128 * 2, 128 * 2);
                }
                npalm = np; pframes = nf;
                LOG("painted: %d palms x %d sway frames, %d cells in %d banks (%ld bytes)", np, nf, nc, nb, size);
            }
        } else ok = 0;
        if (!ok && !npalm) LOG("painted: palm file rejected");
        free(d);
    }
    props_load();
    loaded = 1;
    LOG("painted: %s, %dx%d picture, %d banks, %d occluder cells", parea[paint_area].name, PB_W, PB_H, PB_BANKS, nocc);
    return 1;
}

/* A 48 x 27 thumbnail of the picture for the mini-map, averaged from the banks' cells (layout: cell n = row * 11 + col lives in
 * bank n / 32 at 128 x 128 slot n % 32, 8 slots a row). */
#define MINI_W 48
#define MINI_H 27
static unsigned mini[MINI_H][MINI_W];
static void mini_build(const unsigned char *banks)
{
    int cx, cy;
    for (cy = 0; cy < MINI_H; cy++)
        for (cx = 0; cx < MINI_W; cx++) {
            int x0 = cx * PB_W / MINI_W, x1 = (cx + 1) * PB_W / MINI_W, y0 = cy * PB_H / MINI_H, y1 = (cy + 1) * PB_H / MINI_H, x, y, n = 0;
            unsigned r = 0, g = 0, b = 0;
            for (y = y0; y < y1; y += 3)
                for (x = x0; x < x1; x += 3) {
                    int cell = (y / PB_STRIDE) * PB_COLS + x / PB_STRIDE, bk = cell / 32, k = cell % 32;
                    const unsigned char *p = banks + (size_t)bk * 1024 * 512 * 2 + ((size_t)((k / 8) * 128 + y % PB_STRIDE) * 1024 + (k % 8) * 128 + x % PB_STRIDE) * 2;
                    unsigned v = p[0] | p[1] << 8;
                    r += (v & 31) << 3; g += ((v >> 5) & 31) << 3; b += ((v >> 10) & 31) << 3; n++;
                }
            if (n) { r /= n; g /= n; b /= n; }
            mini[cy][cx] = ((r & 0xF0) << 16) | ((g & 0xF0) << 8) | (b & 0xF0);
        }
}

static int blocked_at(float x, float y)
{
    int cx = (int)(x / col_cell), cy = (int)(y / col_cell);
    if (x < 0 || y < 0 || cx >= col_w || cy >= col_h) return 1;
    return col[cy * col_w + cx];
}
static int blocked(float x, float y)
{
    if (paint_area == AREA_VILLAGE) {
        if (guard_block && x >= EXIT_X0 && x <= EXIT_X1 && y >= 96 && y <= 150) return 1;   /* the Guard's bar across the bridge */
        {   float bx, by;      /* the stone bench is a wall the width of its seat */
            if (bench_at(&bx, &by) && x >= bx - 37 && x <= bx + 37 && y >= by - 9 && y <= by + 2 && !sitting) return 1;
        }
    }
    return blocked_at(x - 5, y) || blocked_at(x + 5, y) || blocked_at(x, y - 3) || blocked_at(x, y + 2);
}

/* the ground point that projects to screen (sx, sy): the inverse of Gfx_Project for wy = 0 */
static void unproject(float sx, float sy, float *wx, float *wz, float *z)
{
    const float C = cosf(PCAM_PITCH * 3.14159265f / 180.0f), S = sinf(PCAM_PITCH * 3.14159265f / 180.0f), F = 380.0f;
    float dy = sy - 118.0f, rz = -dy * PCAM_D / (dy * C + S * F), zz = C * rz + PCAM_D;
    *wx = (sx - 160.0f) * zz / F;
    *wz = -rz;
    *z = zz;
}

static void draw_char(const Mesh *m, float tx, float ty, float cyaw, int frame, const int *rgb, float shadow)
{
    float sx = tx / TPU - scr_x, sy = ty / TPU - scr_y, wx, wz, z, ref;
    if (!m || sx < -40 || sx > VIEW_W + 40 || sy < -20 || sy > VIEW_H + 80) return;
    unproject(sx, sy, &wx, &wz, &z);
    if (shadow > 0) Gfx_Shadow(wx, wz, shadow);
    ref = z;
    gfx_sort_override = ref;
    Gfx_DrawMesh(m, frame, wx, 0, wz, cyaw, PSCALE, rgb, 0);
    gfx_sort_override = -1.0f;
}


static int ow_of(int i)
{
    int k;
    for (k = 0; k < npc_count; k++) if (!strcmp(npcs[k].id, pid[i])) return k;
    return -1;
}
/* at night the villagers who live in the picture's houses are indoors (Teana, Jono, Hakim, Kemet): the plaza is empty for the hooded man */
static int night_away(int i) { return night_t > 0.6f && (i == 1 || i == 3 || i == 5 || i == 6); }
static int npc_here(int i) { int k = ow_of(i); return k >= 0 && pnpc[i].area == paint_area && !npcs[k].hidden && !night_away(i); }
/* the bridge is open: journey.json's "painted": {"bridge_open": cond} holds (without it: the Guard has been moved) */
static int npc_moved(int i);
static int bridge_open(void)
{
    const JsonNode *po = Json_Get(jm_rules, "painted");
    if (po && Json_Get(po, "bridge_open")) return Story_Cond(Json_Get(po, "bridge_open"));
    return npc_moved(GUARD);
}
/* journey.json moved this person from his first tile (the Guard, once the way is open) */
static int npc_moved(int i)
{
    int k = ow_of(i);
    if (k < 0 || !npcs[k].base || npcs[k].base->child == NULL) return 0;
    return fabsf(npcs[k].x - (float)Json_At(npcs[k].base, 0)->num * TS) > 1.0f;
}
static int npc_body(float x, float y)
{
    int i;
    for (i = 0; i < NPN; i++) if (npc_here(i) && fabsf(x - pnpc[i].x) < 15 && fabsf(y - pnpc[i].y) < 9) return 1;
    return 0;
}

static void npcs_update(void)
{
    int i;
    for (i = 0; i < NPN; i++) {
        PNpc *n = &pnpc[i];
        float nx, ny, step = 0.8f;
        if (!npc_init) { n->ax = n->x; n->ay = n->y; n->dirn = 1; n->pause = 30 * i; }
        n->moving = 0;
        if (!npc_init) {   /* each villager stands at the anchor journey.json names for him */
            int k = ow_of(i);
            float ax, ay;
            if (k >= 0 && Paint_Anchor(npcs[k].anchor, &ax, &ay)) { n->x = n->ax = ax; n->y = n->ay = ay; if (i == GUARD) { guard_home[0] = (short)ax; guard_home[1] = (short)ay; } }
        }
        if (n->area != paint_area) continue;
        if (i == GUARD) {   /* the Guard bars the bridge until the story opens it; then he steps aside */
            int mv = bridge_open();
            float gx = mv ? guard_aside[0] : guard_home[0], gy = mv ? guard_aside[1] : guard_home[1];
            guard_block = !mv && npc_here(i);
            if (n->x != gx || n->y != gy) { n->x = n->ax = gx; n->y = n->ay = gy; }
        }
        if (ptalk[i]) {   /* in conversation: stands still, looking at the player */
            float ddx = pt_x - n->x, ddy = pt_y - n->y;
            n->yaw = atan2f(ddx, ddy);
            continue;
        }
        if (!n->patrol_axis) continue;
        if (n->pause > 0) { n->pause--; continue; }
        nx = n->x + (n->patrol_axis == 1 ? step * n->dirn : 0);
        ny = n->y + (n->patrol_axis == 2 ? step * n->dirn : 0);
        if (fabsf(nx - n->ax) > n->range || fabsf(ny - n->ay) > n->range || blocked(nx, ny)
            || (fabsf(nx - pt_x) < 14 && fabsf(ny - pt_y) < 10)) {   /* the end of the walk, a wall, or the player in the way: turn and wait */
            n->dirn = -n->dirn; n->pause = 70;
            continue;
        }
        n->x = nx; n->y = ny; n->moving = 1;
        n->yaw = n->patrol_axis == 1 ? (n->dirn > 0 ? 1.5708f : -1.5708f) : (n->dirn > 0 ? 0.0f : 3.14159f);
    }
    npc_init = 1;
}


/* ------------------------------------------------------------ props, night, the observer, objects
 * Bank 15 (free in the village): page 4 holds the stone bench, page 5 the Mago.dev aura (both little raw images: u16 w, u16 h,
 * then 1555 texels, 0 transparent).  Night is a colour modulation of every quad of the picture (gfx_tint) that follows a target the
 * story sets; the observer is a figure on a far rooftop that only shows during named script pages. */
#define NIGHT_R 52
#define NIGHT_G 68
#define NIGHT_B 138
#define GLITCH_FRAMES 48
static int bench_w, bench_h, aura_w, aura_h, obs_age;
static int hatch_w, hatch_h, glow_w, glow_h;
static int prop_blit(const char *file, int page, int ox, int oy, int *w, int *h)
{
    long size;
    unsigned char *d = Jm_Slurp(file, &size);
    uint16_t *bank = SoftGpu_Bank(15);
    int pw, ph, y;
    if (!d || !bank || size < 4) { free(d); return 0; }
    pw = d[0] | d[1] << 8; ph = d[2] | d[3] << 8;
    if (pw < 1 || ph < 1 || ox + pw > 255 || oy + ph > 256 || size < 4 + 2L * pw * ph) { free(d); return 0; }
    for (y = 0; y < ph; y++)
        memcpy(bank + (size_t)((page >> 2) * 256 + oy + y) * 1024 + (page & 3) * 256 + ox, d + 4 + (size_t)y * pw * 2, (size_t)pw * 2);
    *w = pw; *h = ph;
    free(d);
    return 1;
}
static void props_load(void)
{
    bench_w = bench_h = aura_w = aura_h = hatch_w = hatch_h = glow_w = glow_h = 0;
    prop_blit("assets/prop_bench.raw", 4, 0, 0, &bench_w, &bench_h);
    prop_blit("assets/prop_aura.raw", 5, 0, 0, &aura_w, &aura_h);
    prop_blit("assets/prop_hatch_closed.raw", 4, 0, 48, &hatch_w, &hatch_h);          /* page 4: the bench on top, the two hatches below it */
    prop_blit("assets/prop_hatch_open.raw", 4, 56, 48, &hatch_w, &hatch_h);
    prop_blit("assets/prop_torch_glow.raw", 5, 130, 0, &glow_w, &glow_h);              /* page 5: the aura (128 wide), the torch glow beside it */
}
static const JsonNode *objects(void) { return Json_Get(jm_rules, "objects"); }
/* the object that shows a prop of this kind in the current area ("prop": "bench" | "hatch"); its position is "prop_anchor" or "anchor" */
static const JsonNode *prop_object(const char *kind, float *x, float *y)
{
    const JsonNode *o = objects(), *n;
    for (n = o ? o->child : NULL; n; n = n->next)
        if (!strcmp(Json_Str(n, "prop", ""), kind) && Paint_AnchorArea(Json_Str(n, "anchor", "")) == paint_area
            && Paint_Anchor(Json_Str(n, "prop_anchor", Json_Str(n, "anchor", "")), x, y)) return n;
    return NULL;
}
static int bench_at(float *x, float *y) { return prop_object("bench", x, y) && bench_w > 0; }
/* the hatch of the little pyramid: shut until the object's "open_when" holds */
static void draw_hatch(void)
{
    float hx, hy, sx, sy, wx, wz, z;
    const JsonNode *o = prop_object("hatch", &hx, &hy);
    int w, h, open;
    if (!o || hatch_w <= 0) return;
    sx = hx / TPU - scr_x; sy = hy / TPU - scr_y;
    if (sx < -60 || sx > VIEW_W + 60 || sy < -20 || sy > VIEW_H + 40) return;
    open = Json_Get(o, "open_when") ? Story_Cond(Json_Get(o, "open_when")) : 0;
    unproject(sx, sy, &wx, &wz, &z);
    w = hatch_w / 2; h = hatch_h / 2;      /* drawn smaller than painted: the little pyramid's face is 45 texels wide */
    Gfx_SpriteQuad((int)floorf(sx + 0.5f) - w / 2, (int)floorf(sy + 0.5f) - h + 2, w, h, 15, 4, open ? 56 : 0, 48, hatch_w, hatch_h, z);
}
/* the wall torches of the cistern: a flickering orange glow added over each flame of the picture */
static void draw_torches(void)
{
    static const short torch[8][2] = {{271, 125}, {516, 125}, {759, 125}, {965, 125}, {121, 206}, {1155, 206}, {25, 469}, {1250, 469}};
    int i;
    if (paint_area != AREA_CISTERN || glow_w <= 0) return;
    for (i = 0; i < 8; i++) {
        float sx = torch[i][0] / (float)TPU - scr_x, sy = torch[i][1] / (float)TPU - scr_y, f;
        int g, sz;
        unsigned char c[3];
        if (sx < -40 || sx > VIEW_W + 40 || sy < -40 || sy > VIEW_H + 40) continue;
        f = 0.62f + 0.22f * sinf((float)gfx_frame * 0.21f + i * 2.1f) + 0.16f * sinf((float)gfx_frame * 0.53f + i * 5.3f);
        g = (int)(f * 120.0f);
        c[0] = (unsigned char)g; c[1] = (unsigned char)(g * 62 / 100); c[2] = (unsigned char)(g * 22 / 100);
        sz = 40 + (int)(6.0f * f);
        Gfx_SpriteQuadEx((int)floorf(sx + 0.5f) - sz / 2, (int)floorf(sy + 0.5f) - sz / 2 - 4, sz, sz, 15, 5, 130, 0, glow_w, glow_h, 100000.0f, c, 1);
    }
}
static int night_cond(void)
{
    const JsonNode *po = Json_Get(jm_rules, "painted"), *c = po ? Json_Get(po, "night") : NULL;
    if (paint_area != AREA_VILLAGE) return 0;       /* underground: no day or night */
    if (time_ov >= 0) return time_ov;
    return c && Story_Cond(c);
}
void Paint_ForceTime(int t) { time_ov = t; night_target = night_cond() ? 1.0f : 0.0f; }
static void night_step(void)
{
    float d = night_target - night_t;
    if (fabsf(d) < 0.009f) night_t = night_target; else night_t += d > 0 ? 0.008f : -0.008f;
    gfx_tint[0] = (unsigned char)(128 + (NIGHT_R - 128) * night_t);
    gfx_tint[1] = (unsigned char)(128 + (NIGHT_G - 128) * night_t);
    gfx_tint[2] = (unsigned char)(128 + (NIGHT_B - 128) * night_t);
    if (fade_in > 0) {      /* a fade in from black after the player goes through a hatch or up stairs */
        int f = 128 - fade_in * 128 / 30;
        gfx_tint[0] = (unsigned char)(gfx_tint[0] * f / 128); gfx_tint[1] = (unsigned char)(gfx_tint[1] * f / 128); gfx_tint[2] = (unsigned char)(gfx_tint[2] * f / 128);
        fade_in--;
    }
}
int Paint_IsNight(void) { return night_t > 0.5f; }

/* a page of a script opens: a time event (the sun sets) and the observer's cue */
void Paint_PageEvent(const char *script, int page)
{
    const JsonNode *po = Json_Get(jm_rules, "painted"), *l, *n, *cue = NULL;
    for (l = Json_Get(po, "time_events") ? Json_Get(po, "time_events")->child : NULL; l; l = l->next)
        if (!strcmp(Json_Str(l, "script", ""), script) && (int)Json_Num(l, "page", -1) == page)
            night_target = !strcmp(Json_Str(l, "time", "day"), "night") ? 1.0f : 0.0f;
    for (l = Json_Get(po, "observers") ? Json_Get(po, "observers")->child : NULL; l; l = l->next) {
        if (strcmp(Json_Str(l, "script", ""), script)) continue;
        for (n = Json_Get(l, "pages") ? Json_Get(l, "pages")->child : NULL; n; n = n->next)
            if ((int)n->num == page) cue = l;
    }
    if (cue && !obs_on) { obs_on = 1; obs_cfg = cue; obs_age = 0; obs_glitch = 0; LOG("painted: observer %s appears", Json_Str(cue, "npc", "?")); }
    else if (!cue && obs_on) { obs_on = 0; obs_glitch = GLITCH_FRAMES; LOG("painted: observer vanishes"); }
}
void Paint_SceneEnd(void)
{
    night_target = night_cond() ? 1.0f : 0.0f;
    if (obs_on) { obs_on = 0; obs_glitch = GLITCH_FRAMES; }
}

static void draw_bench(void)
{
    float bx, by, sx, sy, wx, wz, z;
    int w, h;
    if (!bench_at(&bx, &by)) return;
    sx = bx / TPU - scr_x; sy = by / TPU - scr_y;
    if (sx < -60 || sx > VIEW_W + 60 || sy < -20 || sy > VIEW_H + 40) return;
    unproject(sx, sy, &wx, &wz, &z);
    w = bench_w / 2; h = bench_h / 2;
    Gfx_SpriteQuad((int)floorf(sx + 0.5f) - w / 2, (int)floorf(sy + 0.5f) - h + 2, w, h, 15, 4, 0, 0, bench_w, bench_h, z);
}

/* The glyph observer (Mago.dev's writing on the cistern wall): rows of green characters that flicker on and off over the carved panel,
 * with the aura's glow behind them; when the page ends they tear apart and go (obs_glitch). */
static void draw_glyph(float ax, float ay)
{
    int row, colm, vis = obs_on || obs_glitch > 0, step = (int)(gfx_frame / 3);
    float px0 = (ax - 78) / TPU - scr_x, py0 = (ay - 138) / TPU - scr_y;     /* the panel is above the floor spot the anchor names */
    unsigned char c[3];
    int pulse = (int)(95 + 35 * sinf((float)gfx_frame * 0.14f));
    if (!vis) return;
    if (obs_on) obs_age++;
    else if (obs_glitch > 0) obs_glitch--;
    if (aura_w > 0) {
        int aw = 84 + (obs_on ? 0 : (obs_glitch % 5 - 2) * 5);
        c[0] = (unsigned char)(pulse / 3); c[1] = (unsigned char)pulse; c[2] = (unsigned char)(pulse / 3);
        Gfx_SpriteQuadEx((int)floorf(px0 + 39) - aw / 2, (int)floorf(py0 + 27) - aw / 2 + 4, aw, aw * 3 / 4, 15, 5, 0, 0, aura_w, aura_h, 300.0f, c, 1);
    }
    for (row = 0; row < 6; row++)
        for (colm = 0; colm < 13; colm++) {
            unsigned h = (unsigned)(row * 131 + colm * 31 + (unsigned)(step + row * 7) * 2654435761u >> 13) * 2246822519u >> 11;
            int lit, g;
            float x, y;
            unsigned char cc[3][3];
            if (!obs_on && ((h + (unsigned)obs_glitch) % 3)) continue;     /* tearing away: fewer and fewer characters */
            if (obs_on && obs_age < 30 && (h % 4) > (unsigned)(obs_age / 8)) continue;   /* appearing: they come in one by one */
            lit = (h >> 3) % 5;
            if (lit == 0) continue;
            g = 150 + lit * 25;
            x = px0 + colm * 6.0f + (row & 1) * 2.0f; y = py0 + row * 9.0f;
            cc[0][0] = cc[1][0] = cc[2][0] = (unsigned char)(g / 4); cc[0][1] = cc[1][1] = cc[2][1] = (unsigned char)(g > 255 ? 255 : g); cc[0][2] = cc[1][2] = cc[2][2] = (unsigned char)(g / 3);
            Gfx_SceneTri(x, y, x + 3.5f, y, x, y + 6.0f - (h & 2), cc, 0.7f);                 /* a "character": a notch and a bar, or a block */
            if (h & 1) Gfx_SceneTri(x + 3.5f, y, x + 3.5f, y + 6.0f, x, y + 6.0f - (h & 2), cc, 0.7f);
            if (h & 4) Gfx_SceneTri(x - 1.0f, y + 3.0f, x + 5.0f, y + 3.0f, x + 2.0f, y + 4.5f, cc, 0.69f);
        }
}

/* Mago.dev on the roof: the robe sprite in front of everything (it stands on the roof, the house cutout must not hide it), the
 * green aura behind it, and a glitch (flicker, torn halves) when he comes and goes. */
static void draw_observer(void)
{
    float ax, ay, sx, sy, t = (float)gfx_frame;
    int vis = 1, jx = 0, x0, y0, pulse, aw, ah;
    unsigned char c[3];
    if ((!obs_on && obs_glitch <= 0) || !obs_cfg) return;
    if (!Paint_Anchor(Json_Str(obs_cfg, "anchor", "mago_roof"), &ax, &ay)) return;
    sx = ax / TPU - scr_x; sy = ay / TPU - scr_y;
    if (Json_Get(obs_cfg, "glyph")) { draw_glyph(ax, ay); return; }       /* no figure: only his writing on the wall */
    if (!spr[SPR_MAGO].ok) return;
    if (obs_on) { obs_age++; vis = obs_age > 30 || ((obs_age / 2) & 1); if (obs_age <= 30) jx = ((obs_age * 7) % 5 - 2) * 2; }
    else { int g = obs_glitch--; vis = g > 42 || ((g * 37 >> 3) & 1); jx = ((g * 13) % 7 - 3) * 3; }
    x0 = (int)floorf(sx + 0.5f) - SPR_CW / 4; y0 = (int)floorf(sy + 0.5f) - SPR_FY / 2;
    pulse = (int)(110 + 40 * sinf(t * 0.12f));
    if (!obs_on) pulse = 90 + ((obs_glitch * 53) & 127);
    c[0] = (unsigned char)(pulse / 2); c[1] = (unsigned char)pulse; c[2] = (unsigned char)(pulse / 2);
    if (aura_w > 0 && vis) {
        aw = 64 + (obs_on ? 0 : ((obs_glitch % 5) - 2) * 6); ah = 64;
        if (!obs_on && (obs_glitch & 1)) aw = 28;
        Gfx_SpriteQuadEx((int)floorf(sx + 0.5f) - aw / 2, (int)floorf(sy + 0.5f) - 36 - ah / 2 + 10, aw, ah, 15, 5, 0, 0, aura_w, aura_h, 905.0f, c, 1);
    }
    if (vis) {
        static const unsigned char lit[3] = {132, 150, 132};
        int half = SPR_CH / 2;
        if (jx) {   /* torn: the halves slip sideways */
            Gfx_SpriteQuadEx(x0 + jx, y0, SPR_CW / 2, half / 2, 15, 1, 0, 0, SPR_CW, half, 900.0f, lit, -1);
            Gfx_SpriteQuadEx(x0 - jx, y0 + half / 2, SPR_CW / 2, SPR_CH / 2 - half / 2, 15, 1, 0, half, SPR_CW, SPR_CH - half, 900.0f, lit, -1);
        } else Gfx_SpriteQuadEx(x0, y0, SPR_CW / 2, SPR_CH / 2, 15, 1, 0, 0, SPR_CW, SPR_CH, 900.0f, lit, -1);
    }
}

/* the camera follows the player, or looks at the observer while he shows */
static void scroll_step(void)
{
    float tx = pt_x / TPU - VIEW_W / 2.0f, ty = pt_y / TPU - VIEW_H * 0.58f, rate = 0.2f;
    static int slow;
    float mx = PB_W / TPU - VIEW_W, my = PB_H / TPU - VIEW_H, ax, ay;
    if ((obs_on || obs_glitch > 0) && obs_cfg && Paint_Anchor(Json_Str(obs_cfg, "anchor", "mago_roof"), &ax, &ay)) {
        tx = ax / TPU - VIEW_W / 2.0f; ty = ay / TPU - VIEW_H * 0.42f; slow = 110;
    }
    if (slow > 0) { slow--; rate = 0.06f; }
    tx = tx < 0 ? 0 : tx > mx ? mx : tx;
    ty = ty < 0 ? 0 : ty > my ? my : ty;
    scr_x += (tx - scr_x) * rate;
    scr_y += (ty - scr_y) * rate;
    if (fabsf(tx - scr_x) < 0.5f) scr_x = tx;
    if (fabsf(ty - scr_y) < 0.5f) scr_y = ty;
}

/* objects: things of the picture that can be examined (the bench, the notice board) */
#define OBJ_REACH 70.0f
int Paint_NearObject(void)
{
    const JsonNode *o = objects(), *n;
    int i = 0, best = -1;
    float bd = 1e9f;
    for (n = o ? o->child : NULL; n; n = n->next, i++) {
        float ax, ay, dx, dy, d, r = (float)Json_Num(n, "reach", OBJ_REACH);
        if (!Paint_Anchor(Json_Str(n, "anchor", ""), &ax, &ay) || Paint_AnchorArea(Json_Str(n, "anchor", "")) != paint_area) continue;
        dx = pt_x - ax; dy = (pt_y - ay) * 1.4f; d = dx * dx + dy * dy;
        if (d < r * r && d < bd) { bd = d; best = i; }
    }
    return best;
}
/* the rule that applies to object i now; fills t */
int Paint_ObjectRule(int i, Talk *t)
{
    const JsonNode *n = Json_At(objects(), i);
    Npc o;
    if (!n) return 0;
    memset(&o, 0, sizeof(o));
    o.rules = Json_Get(n, "talk");
    return Story_TalkRule(&o, t);
}
void Paint_ObjectStart(int i, const char *pose)
{
    const JsonNode *n = Json_At(objects(), i);
    float ax, ay;
    int k;
    for (k = 0; k < NPN; k++) pnpc[k].moving = 0;
    walking = 0;
    if (!n || !Paint_Anchor(Json_Str(n, "anchor", ""), &ax, &ay)) return;
    if (pose && !strcmp(pose, "sit") && bench_at(&ax, &ay)) { pt_x = ax; pt_y = ay - 7; face = 0; sitting = 1; return; }
    { float dx = ax - pt_x, dy = ay - pt_y; face = (fabsf(dx) >= fabsf(dy) * 1.4f) ? (dx > 0 ? 2 : 1) : (dy > 0 ? 0 : 3); }
}

int Paint_Tick(unsigned short pad, unsigned short edge)
{
    float dx = 0, dy = 0, sp = (pad & PAD_CIRCLE) ? 4.4f : 2.6f;
    if (!load()) return 1;
    if (edge & PAD_L1) return 1;
    if (edge & 0x0100) paint_anim ^= 1;       /* L2 (key E): water */
    if (edge & 0x0200) paint_sway ^= 1;       /* R2 (key R): trees */
    if ((edge & PAD_SQUARE) && Dbg_On()) paint_sprite = (paint_sprite + 1) % 5;   /* Z: player look (comparison), debug builds only: the menu is START */
    if (pad & PAD_UP) dy -= 1;
    if (pad & PAD_DOWN) dy += 1;
    if (pad & PAD_LEFT) dx -= 1;
    if (pad & PAD_RIGHT) dx += 1;
    walking = (dx != 0 || dy != 0);
    if (walking) face = (dx != 0 && fabsf(dx) >= fabsf(dy)) ? (dx > 0 ? 2 : 1) : (dy > 0 ? 0 : 3);
    if (walking) {
        float l = sqrtf(dx * dx + dy * dy), target = atan2f(dx, dy), d, nx, ny;
        dx = dx / l * sp; dy = dy / l * sp;
        d = target - yaw;
        while (d > 3.14159265f) d -= 6.2831853f;
        while (d < -3.14159265f) d += 6.2831853f;
        yaw += d * 0.35f;
        nx = pt_x + dx; ny = pt_y + dy;
        {
            int in = npc_body(pt_x, pt_y);    /* standing inside one already (he walked up): free to step out */
            if (!blocked(nx, pt_y) && (in || !npc_body(nx, pt_y))) pt_x = nx;
            if (!blocked(pt_x, ny) && (in || !npc_body(pt_x, ny))) pt_y = ny;
        }
    }
    if (paint_area == AREA_VILLAGE && pt_y < EXIT_Y && pt_x > EXIT_X0 && pt_x < EXIT_X1) { paint_exit = 1; return 1; }   /* across the bridge */
    npcs_update();
    return 0;
}

static void Paint_Enter_Scroll(void)
{
    float mx = PB_W / TPU - VIEW_W, my = PB_H / TPU - VIEW_H;
    scr_x = pt_x / TPU - VIEW_W / 2.0f; scr_y = pt_y / TPU - VIEW_H * 0.58f;
    scr_x = scr_x < 0 ? 0 : scr_x > mx ? mx : scr_x; scr_y = scr_y < 0 ? 0 : scr_y > my ? my : scr_y;
}
void Paint_Enter(void) { loaded = 0; sitting = 0; obs_on = obs_glitch = 0; memset(spr_baked, 0, sizeof(spr_baked)); load();   /* banks 1-12 are also the 3D Monsters' (duels), so load again each time */
    night_target = night_t = night_cond() ? 1.0f : 0.0f; night_step();
    scr_x = pt_x / TPU - VIEW_W / 2.0f; scr_y = pt_y / TPU - VIEW_H * 0.58f;
    { float mx = PB_W / TPU - VIEW_W, my = PB_H / TPU - VIEW_H;   /* inside the picture from the first frame */
      scr_x = scr_x < 0 ? 0 : scr_x > mx ? mx : scr_x; scr_y = scr_y < 0 ? 0 : scr_y > my ? my : scr_y; } }

int Paint_Loaded(void) { return loaded; }
/* where the player is, for the save: in the cistern the save keeps the village's hatch (Continue starts in the village) */
void Paint_Info(float *x, float *y, float *sx, float *sy)
{
    *sx = scr_x; *sy = scr_y;
    if (paint_area != AREA_VILLAGE && Paint_Anchor("mini_pyramid_hatch", x, y)) return;
    *x = pt_x; *y = pt_y;
}
void Paint_Set(float x, float y) { pt_x = x; pt_y = y; }
/* go to a named place, which may be in the other area: the pictures are loaded again, with a fade in */
void Paint_Warp(const char *area_name, const char *anchor)
{
    float x, y;
    int a = -1, i;
    for (i = 0; i < AREA_COUNT; i++) if (area_name && !strcmp(parea[i].name, area_name)) a = i;
    if (a < 0) a = Paint_AnchorArea(anchor);
    if (a < 0 || !Paint_Anchor(anchor, &x, &y)) { LOG("painted: no place %s", anchor ? anchor : "?"); return; }
    memset(ptalk, 0, sizeof(ptalk));
    pt_x = x; pt_y = y; face = 0; walking = 0;
    if (a != paint_area) { paint_area = a; Paint_Enter(); fade_in = 30; }
    else Paint_Enter_Scroll();
    LOG("painted: now in the %s at %d,%d", parea[paint_area].name, (int)x, (int)y);
}
/* a named place, whichever area it is in (the debug aid): the area changes with it */
void Paint_GoAnchor(const char *anchor)
{
    float x, y;
    int a = Paint_AnchorArea(anchor);
    if (a < 0 || !Paint_Anchor(anchor, &x, &y)) return;
    if (a != paint_area) {
        paint_area = a;
        if (loaded) Paint_Enter();
    }
    pt_x = x; pt_y = y;
    if (loaded) Paint_Enter_Scroll();
}

void Paint_Draw(const Mesh *body, const int body_rgb[5])
{
    int r, c, i, ox, oy;
    night_step();
    scroll_step();
    ox = (int)floorf(scr_x); oy = (int)floorf(scr_y);
    Gfx_Backdrop(0x101820, 0x101820);
    Gfx_SetCamera(PCAM_D, PCAM_PITCH);
    cam_x = 0; cam_z = 0;
    for (r = 0; r < PB_ROWS; r++)
        for (c = 0; c < PB_COLS; c++) {
            int n = r * PB_COLS + c, b = n / 32, k = n % 32;
            int x0 = c * PB_STRIDE / TPU - ox, y0 = r * PB_STRIDE / TPU - oy, w = PB_STRIDE / TPU;
            float sx[4] = {(float)x0, (float)(x0 + w), (float)x0, (float)(x0 + w)};
            float sy[4] = {(float)y0, (float)y0, (float)(y0 + w), (float)(y0 + w)};
            if (x0 > VIEW_W + 60 || x0 + w < -60 || y0 > VIEW_H || y0 + w < 0) continue;
            if (paint_anim && wframes && wslot[n] >= 0) {   /* a water cell: this frame's picture of it */
                int f = (int)((gfx_frame / WATER_TICKS) % (unsigned)wframes), slot = f * wn + wslot[n];
                b = slot / 32; k = slot % 32;
                Gfx_BankQuad(sx, sy, ANIM_BANK0 + b, (k % 8) * 128, (k / 8) * 128, PB_STRIDE, PB_STRIDE, -1.0f);
                continue;
            }
            Gfx_BankQuad(sx, sy, PB_BANK0 + b, (k % 8) * 128, (k / 8) * 128, PB_STRIDE, PB_STRIDE, -1.0f);
        }
    for (i = 0; i < npalm; i++) {   /* the palms: sprites of the original picture; the clean plate under them shows no tree */
        const PPalm *q = &ppalm[i];
        int f = paint_sway ? sway_seq[((gfx_frame / PALM_TICKS) + (unsigned)(i * 3)) % 8] : 2, j;
        float wx, wz, z = 100000.0f;
        if (paint_view == 0) unproject(0, q->by / (float)TPU - oy, &wx, &wz, &z);
        for (j = 0; j < q->n; j++) {
            int slot = q->first + f * q->n + j, b = slot / 32, k = slot % 32;
            int x0 = (q->x0 + q->kc[j][0] * PB_STRIDE) / TPU - ox, y0 = (q->y0 + q->kc[j][1] * PB_STRIDE) / TPU - oy, w = PB_STRIDE / TPU;
            float sx[4] = {(float)x0, (float)(x0 + w), (float)x0, (float)(x0 + w)};
            float sy[4] = {(float)y0, (float)y0, (float)(y0 + w), (float)(y0 + w)};
            if (x0 > VIEW_W + 60 || x0 + w < -60 || y0 > VIEW_H || y0 + w < 0) continue;
            Gfx_BankQuad(sx, sy, palm_banks[b], (k % 8) * 128, (k / 8) * 128, PB_STRIDE, PB_STRIDE, z);
        }
    }
    if (paint_view == 1) return;
    if (paint_view == 0) {
        for (i = 0; i < nocc; i++) {
            int n = occ_t[i][2], b = n / 32, k = n % 32;
            int x0 = occ_t[i][0] / TPU - ox, y0 = occ_t[i][1] / TPU - oy, w = PB_STRIDE / TPU;
            float sx[4] = {(float)x0, (float)(x0 + w), (float)x0, (float)(x0 + w)};
            float sy[4] = {(float)y0, (float)y0, (float)(y0 + w), (float)(y0 + w)};
            float wx, wz, z;
            if (x0 > VIEW_W + 60 || x0 + w < -60 || y0 > VIEW_H || y0 + w < 0) continue;
            unproject(0, occ_t[i][3] / (float)TPU - oy, &wx, &wz, &z);
            Gfx_BankQuad(sx, sy, PB_BANK0 + b, (k % 8) * 128, (k / 8) * 128, PB_STRIDE, PB_STRIDE, z);
        }
    }
    sprites_prepare(body_rgb);
    draw_bench();
    draw_hatch();
    draw_torches();
    for (i = 0; i < NPN; i++) {
        int sp;
        if (!npc_here(i)) continue;
        sp = paint_sprite ? pnpc[i].spr : -1;   /* every look but "3D mesh" shows the people as sprites */
        if (sp >= 0 && spr[sp].ok) draw_spr_lift(sp, pnpc[i].x, pnpc[i].y, spr_dir_from_yaw(pnpc[i].yaw), spr_frame_of(sp, pnpc[i].moving), 20, pnpc[i].hover * sinf((float)gfx_frame * 0.07f));
        else draw_char(Gfx_Mesh(pnpc[i].mesh), pnpc[i].x, pnpc[i].y, pnpc[i].yaw, 0, NULL, 20);
    }
    {
        int mode = paint_sprite;
        float off = mode == 4 ? 28.0f : 0.0f;
        if (mode == 1) draw_spr(SPR_KENNEY_M, pt_x, pt_y, face, spr_walk_frame(SPR_KENNEY_M), 20);
        if (mode == 2) draw_spr(SPR_PLAYER_MESH, pt_x, pt_y, face, spr_walk_frame(SPR_PLAYER_MESH), 20);
        if (mode == 3) draw_spr(SPR_AI, pt_x, pt_y, face, spr_walk_frame(SPR_AI), 20);
        if (mode == 4) {
            draw_spr(SPR_KENNEY_M, pt_x - 3 * off, pt_y, face, spr_walk_frame(SPR_KENNEY_M), 20);
            draw_spr(SPR_PLAYER_MESH, pt_x - off, pt_y, face, spr_walk_frame(SPR_PLAYER_MESH), 20);
            draw_spr(SPR_AI, pt_x + off, pt_y, face, spr_walk_frame(SPR_AI), 20);
        }
        if (mode == 0 || mode == 4) draw_char(body, pt_x + 3 * off, pt_y, yaw, walking ? 1 + (int)((gfx_frame / 5) & 3) : 0, body_rgb, 20);
    }
    draw_observer();
    if (paint_markers) draw_marker();
    { static unsigned n; if (!(n++ % 20)) LOG("painted: scroll %d,%d player %d,%d items %d", ox, oy, (int)pt_x, (int)pt_y, Gfx_Items()); }
}


/* ------------------------------------------------------------ talking, the objective, the mini-map */
/* The villager the player can talk to now: an index into journey.json's npcs (npcs[]), or -1. */
int Paint_NearNpc(void)
{
    int i, best = -1;
    float bd = TALK_REACH * TALK_REACH;
    for (i = 0; i < NPN; i++) {
        float dx, dy, d;
        if (!npc_here(i)) continue;
        dx = pt_x - pnpc[i].x; dy = (pt_y - pnpc[i].y) * 1.4f;
        d = dx * dx + dy * dy;
        if (d < bd) { bd = d; best = i; }
    }
    return best < 0 ? -1 : ow_of(best);
}

/* The conversation starts: the villager stops and looks at the player, and the player looks at him. */
void Paint_TalkStart(int ow)
{
    int i;
    for (i = 0; i < NPN; i++) pnpc[i].moving = 0;   /* everyone holds still while the box is open */
    for (i = 0; i < NPN; i++) {
        ptalk[i] = npc_here(i) && ow_of(i) == ow;
        if (ptalk[i]) {
            float dx = pnpc[i].x - pt_x, dy = pnpc[i].y - pt_y;
            face = (fabsf(dx) >= fabsf(dy) * 1.4f) ? (dx > 0 ? 2 : 1) : (dy > 0 ? 0 : 3);
            walking = 0;
            pnpc[i].moving = 0;
            pnpc[i].yaw = atan2f(-dx, -dy);
        }
    }
    walking = 0;
}
void Paint_TalkEnd(void)
{
    memset(ptalk, 0, sizeof(ptalk));
    if (sitting) { float bx, by; sitting = 0; if (bench_at(&bx, &by)) { pt_x = bx; pt_y = by + 16; } }   /* stands up, in front of the bench */
}

/* Where the objective is, in picture texels: the villager the first applicable guide rule names, or the way out (the bridge)
 * when the rule leads somewhere the painted village does not show. */
int Paint_Target(float *tx, float *ty)
{
    const JsonNode *list = Json_Get(jm_rules, "guide"), *n;
    for (n = list ? list->child : NULL; n; n = n->next) {
        const char *id = Json_Str(n, "npc", NULL);
        const char *an = Json_Str(n, "anchor", NULL);
        if (!Story_Cond(Json_Get(n, "when"))) continue;
        if (an) { if (Paint_AnchorArea(an) == paint_area && Paint_Anchor(an, tx, ty)) return 1; continue; }   /* an anchor in another area: the next rule */
        if (id) {
            int i;
            for (i = 0; i < NPN; i++)
                if (!strcmp(pid[i], id) && npc_here(i)) { *tx = pnpc[i].x; *ty = pnpc[i].y; return 1; }
            continue;                  /* he is elsewhere: the next rule */
        }
        *tx = (EXIT_X0 + EXIT_X1) / 2.0f; *ty = 48.0f + 40.0f;   /* the bridge */
        return 1;
    }
    return 0;
}

static void ptri(float x0, float y0, float x1, float y1, float x2, float y2, int r, int g, int b, float depth)
{
    unsigned char c[3][3];
    int k;
    for (k = 0; k < 3; k++) { c[k][0] = (unsigned char)r; c[k][1] = (unsigned char)g; c[k][2] = (unsigned char)b; }
    Gfx_SceneTri(x0, y0, x1, y1, x2, y2, c, depth);
}

/* The objective marker over the target, or an arrow at the edge of the view pointing toward it. */
static void draw_marker(void)
{
    float tx, ty, sx, sy, t = (float)gfx_frame;
    int pulse = (int)(50.0f * (0.5f + 0.5f * sinf(t * 0.16f)));
    if (!Paint_Target(&tx, &ty)) return;
    sx = tx / TPU - scr_x;
    sy = ty / TPU - scr_y - 34.0f;
    if (sx > 12 && sx < 308 && sy > 34 && sy < 200) {
        float y = sy + 4.0f * sinf(t * 0.18f);
        ptri(sx, y + 1.0f, sx - 9.5f, y - 15.0f, sx + 9.5f, y - 15.0f, 20, 14, 6, 0.6f);
        ptri(sx, y, sx - 7, y - 13, sx + 7, y - 13, 255, 200 + pulse / 2, 40, 0.5f);
        ptri(sx, y - 3, sx - 3.5f, y - 10, sx + 3.5f, y - 10, 255, 250, 200, 0.4f);
    } else {
        float psx = pt_x / TPU - scr_x, psy = pt_y / TPU - scr_y, dx = sx - psx, dy = sy - psy, l = sqrtf(dx * dx + dy * dy), sc = 1e9f;
        float hx = 138, hy = 74, ex, ey, px, py, bx, by, s = 8.0f;
        int a = 200 + pulse;
        if (l < 1.0f) return;
        dx /= l; dy /= l;
        if (fabsf(dx) > 0.001f) sc = hx / fabsf(dx);
        if (fabsf(dy) > 0.001f) { float s2 = hy / fabsf(dy); if (s2 < sc) sc = s2; }
        ex = 160 + dx * sc; ey = 118 + dy * sc;
        px = -dy; py = dx; bx = ex - dx * s * 1.6f; by = ey - dy * s * 1.6f;
        ptri(ex + dx * 1.5f, ey + dy * 1.5f, bx + px * (s + 1.5f), by + py * (s + 1.5f), bx - px * (s + 1.5f), by - py * (s + 1.5f), 20, 16, 8, 0.5f);
        ptri(ex, ey, bx + px * s, by + py * s, bx - px * s, by - py * s, a, a * 3 / 4 > 255 ? 255 : a * 3 / 4, 30, 0.4f);
    }
}

/* The mini-map in the overlay: the picture as 48 x 27 cells of c canvas pixels, the villagers, the objective and the player. */
void Paint_MiniMap(int x, int y, int c, int s)
{
    int cy, cx, i, pulse = (int)(gfx_frame / 10) & 1;
    float tx, ty;
    jm_host->fill(jm_host, x - 3 * s, y - 3 * s, MINI_W * c + 6 * s, MINI_H * c + 6 * s, 0xC8A03C, 255);
    for (cy = 0; cy < MINI_H; cy++) {
        int run = 0;
        for (cx = 1; cx <= MINI_W; cx++) {
            if (cx == MINI_W || mini[cy][cx] != mini[cy][run]) {
                jm_host->fill(jm_host, x + run * c, y + cy * c, (cx - run) * c, c, mini[cy][run], 215);
                run = cx;
            }
        }
    }
    for (i = 0; i < NPN; i++) {
        int mx = (int)(pnpc[i].x * MINI_W * c / PB_W), my = (int)(pnpc[i].y * MINI_H * c / PB_H);
        if (!npc_here(i)) continue;
        jm_host->fill(jm_host, x + mx - 3 * s / 2, y + my - 3 * s / 2, 3 * s, 3 * s, 0xE06020, 255);
    }
    if (Paint_Target(&tx, &ty)) {
        int mx = (int)(tx * MINI_W * c / PB_W), my = (int)(ty * MINI_H * c / PB_H), r = 2 * s + (pulse ? s : 0);
        jm_host->fill(jm_host, x + mx - r, y + my - r, 2 * r, 2 * r, 0x201000, 255);
        jm_host->fill(jm_host, x + mx - r + s, y + my - r + s, 2 * r - 2 * s, 2 * r - 2 * s, 0xFFD030, 255);
    }
    {
        int mx = (int)(pt_x * MINI_W * c / PB_W), my = (int)(pt_y * MINI_H * c / PB_H), r = s + (pulse ? s / 2 + 1 : 0);
        jm_host->fill(jm_host, x + mx - r - s / 2 - 1, y + my - r - s / 2 - 1, 2 * r + s + 2, 2 * r + s + 2, 0x000000, 255);
        jm_host->fill(jm_host, x + mx - r, y + my - r, 2 * r, 2 * r, 0xFFFFFF, 255);
    }
}
