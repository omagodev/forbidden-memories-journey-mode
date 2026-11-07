/* The hero assembled from LPC layers at run time (bake: tools/bake_lpc_parts.py, format "journey-lpc-parts-1").
 * assets/lpc_parts/manifest.json lists the body (male / female), the categories and their options, the colours and the base presets; each
 * layer is an .lpl: 4 directions x (1 idle + 9 walk) cells of 25x38 texels, alpha + RGB, already downsized like import_lpc_test.py.
 * A layer is tinted (skin: a per-channel multiplier; hair / top: the importer's colorize, grey -> lo..hi of the colour; legs, shoes,
 * accessories: their own fixed colour), the layers are composed in z order and alpha is thresholded at half, which gives the same
 * sprite as spr_lpc_test.bin for the base "Hero".
 * The choice is jm.cg[8] (journey.sav, save version 4, no format change): skin, hair, hair colour, top, top colour, legs, shoes, accessory;
 * the body type is jm.gender (0 male, 1 female).  An older save's numbers are simply taken modulo the option counts. */
#include "jm.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define LW 25
#define LH 38
#define LF 10
#define HI_SZ 64
#define MW 50          /* the map cells at the source resolution (manifest "map_hi"): the 64x64 LPC cell's columns 8..57 */
#define MH 64
static int map_hi;     /* 1: every layer carries them; the map draws them at half size, the 25x38 cell's footprint, twice the detail */
#define MAXL 128
enum { CG_SKIN, CG_HAIR, CG_HAIR_COL, CG_TOP, CG_TOP_COL, CG_LEGS, CG_SHOES, CG_ACC, CG_N };
static const char *const cat_id[CG_N] = {"skin", "hair", "hair_colour", "top", "top_colour", "legs", "shoes", "accessory"};

typedef struct { char key[72]; unsigned char *d; long size; int ok; } Layer;
static JsonNode *man;
static int ready = -1;
static Layer cache[MAXL];
static int ncache;

int Cg_Ready(void)
{
    if (ready < 0) {
        char *t = Jm_ReadText("assets/lpc_parts/manifest.json");
        ready = 0;
        if (t) {
            man = Json_Parse(t);
            free(t);
            ready = man && Json_Get(man, "body") && Json_Get(man, "hair") && Json_Get(man, "skin") && (int)Json_Num(man, "w", 0) == LW &&
                    (int)Json_Num(man, "h", 0) == LH && (int)Json_Num(man, "frames", 0) == LF;
            {
                const JsonNode *mh = Json_Get(man, "map_hi");
                map_hi = ready && mh && mh->child && mh->child->next && (int)mh->child->num == MW && (int)mh->child->next->num == MH;
            }
        }
        if (!ready) LOG("chargen: assets/lpc_parts/manifest.json is not usable");
        else LOG("chargen: LPC parts ready, hair %d tops %d legs %d shoes %d accessories %d bases %d", Cg_OptCount(CG_HAIR), Cg_OptCount(CG_TOP),
                 Cg_OptCount(CG_LEGS), Cg_OptCount(CG_SHOES), Cg_OptCount(CG_ACC), Cg_BaseCount());
    }
    return ready == 1;
}
int Cg_Frames(void) { return LF; }
int Cg_W(void) { return Cg_Ready() && map_hi ? MW : LW; }
int Cg_H(void) { return Cg_Ready() && map_hi ? MH : LH; }
int Cg_MapHi(void) { return Cg_Ready() && map_hi; }

static const JsonNode *list_of(int c) { return c >= 0 && c < CG_N ? Json_Get(man, cat_id[c]) : NULL; }
int Cg_CatCount(void) { return Cg_Ready() ? CG_N : 0; }
const char *Cg_CatId(int c) { return c >= 0 && c < CG_N ? cat_id[c] : ""; }
int Cg_OptCount(int c) { return ready == 1 ? Json_Count(list_of(c)) : 0; }
int Cg_Get(int c) { int n = Cg_OptCount(c); return c >= 0 && c < CG_N && n > 0 ? jm.cg[c] % n : 0; }
void Cg_Set(int c, int v)
{
    int n = Cg_OptCount(c);
    if (c < 0 || c >= CG_N || n <= 0) return;
    jm.cg[c] = (unsigned char)(((v % n) + n) % n);
}
int Cg_Style(void) { return 1; }
void Cg_SetStyle(int style) { (void)style; }
int Cg_Avoided(void) { return 0; }
void Cg_Defaults(void)
{
    memset(jm.cg, 0, sizeof(jm.cg));
    jm.gender = 0;
    jm.cg_set = Cg_Ready() ? 1 : 0;
}
unsigned Cg_Signature(void)
{
    unsigned h = (unsigned)jm.cg_set * 7u + (unsigned)jm.gender;
    int i;
    for (i = 0; i < CG_N; i++) h = h * 31u + jm.cg[i];
    return h;
}

/* bases: ready-made heroes ("bases" in the manifest) */
int Cg_BaseCount(void) { return Cg_Ready() ? Json_Count(Json_Get(man, "bases")) : 0; }
const char *Cg_BaseName(int b) { const char *n = Json_Str(Json_At(Json_Get(man, "bases"), b), "name", "?"); char p[64]; const char *t; snprintf(p, sizeof(p), "chargen.bases.%s", n); t = Tr(p); return strncmp(t, "chargen.", 8) ? t : n; }
int Cg_BaseLook(int b, unsigned char cg[8], int *gender)
{
    const JsonNode *e = Json_At(Json_Get(man, "bases"), b), *a, *v;
    int i = 0;
    if (!e) return 0;
    memset(cg, 0, 8);
    a = Json_Get(e, "cg");
    for (v = a ? a->child : NULL; v && i < 8; v = v->next) cg[i++] = (unsigned char)v->num;
    *gender = !strcmp(Json_Str(e, "body", "male"), "female");
    return 1;
}
void Cg_ApplyBase(int b) { int g; if (Cg_BaseLook(b, jm.cg, &g)) { jm.gender = g; jm.cg_set = 1; } }
int Cg_MatchBase(void)       /* the base the current look is exactly, else -1 */
{
    int b, g;
    unsigned char cg[8];
    for (b = 0; b < Cg_BaseCount(); b++) if (Cg_BaseLook(b, cg, &g) && g == jm.gender && !memcmp(cg, jm.cg, 8)) return b;
    return -1;
}

static const char *tr_name(const char *name)
{
    char path[80];
    const char *t;
    snprintf(path, sizeof(path), "chargen.names.%s", name);
    t = Tr(path);
    return strncmp(t, "chargen.", 8) ? t : name;
}
const char *Cg_CatLabel(int c) { char p[48]; if (c < 0 || c >= CG_N) return "?"; snprintf(p, sizeof(p), "chargen.rows.%s", cat_id[c]); return Tr(p); }
const char *Cg_OptLabel(int c, int o) { return Cg_Ready() ? tr_name(Json_Str(Json_At(list_of(c), o), "name", "?")) : "?"; }

static int rgb_of(const JsonNode *a, int *r, int *g, int *b)
{
    if (!a || !a->child || !a->child->next || !a->child->next->next) return 0;
    *r = (int)a->child->num; *g = (int)a->child->next->num; *b = (int)a->child->next->next->num;
    return 1;
}
static int clampi(int v) { return v < 0 ? 0 : v > 255 ? 255 : v; }
/* the swatch colour of an option (what the tinted part looks like at mid grey), 0xRRGGBB; -1 when it has none */
int Cg_OptRgb(int c, int o)
{
    const JsonNode *e;
    int r, g, b;
    if (!Cg_Ready()) return -1;
    e = Json_At(list_of(c), o);
    if (c == CG_SKIN) {
        const JsonNode *m = Json_Get(e, "mul");
        if (!m || !m->child || !m->child->next || !m->child->next->next) return -1;
        return clampi((int)(236 * m->child->num)) << 16 | clampi((int)(178 * m->child->next->num)) << 8 | clampi((int)(140 * m->child->next->next->num));
    }
    if (!rgb_of(Json_Get(e, "rgb"), &r, &g, &b)) return -1;
    if (c == CG_HAIR_COL || c == CG_TOP_COL) {          /* colorize at grey ~150: lo + (hi - lo) * 0.6 */
        int lr = r / 6 < 8 ? 8 : r / 6 > 48 ? 48 : r / 6, lg = g / 6 < 8 ? 8 : g / 6 > 48 ? 48 : g / 6, lb = b / 6 < 8 ? 8 : b / 6 > 48 ? 48 : b / 6;
        int hr = clampi(r * 2 + 42), hg = clampi(g * 2 + 42), hb = clampi(b * 2 + 42);
        r = lr + (hr - lr) * 6 / 10; g = lg + (hg - lg) * 6 / 10; b = lb + (hb - lb) * 6 / 10;
    }
    return r << 16 | g << 8 | b;
}
int Cg_OptRgb2(int c, int o) { (void)c; (void)o; return -1; }

static Layer *layer(const char *file)
{
    char path[112];
    int i;
    Layer *l;
    if (!file) return NULL;
    for (i = 0; i < ncache; i++) if (!strcmp(cache[i].key, file)) return cache[i].ok ? &cache[i] : NULL;
    if (ncache >= MAXL) return NULL;
    l = &cache[ncache++];
    memset(l, 0, sizeof(*l));
    strncpy(l->key, file, sizeof(l->key) - 1);
    snprintf(path, sizeof(path), "assets/lpc_parts/%s", file);
    l->d = Jm_Slurp(path, &l->size);
    l->ok = l->d && l->size >= 8 + 4L * LF * LW * LH * 4 && !memcmp(l->d, "LPL1", 4) && l->d[4] == LW && l->d[5] == LH && l->d[6] == LF;
    if (l->ok && map_hi && l->size < 8 + 4L * LF * LW * LH * 4 + 4L * HI_SZ * HI_SZ * 4 + 4L * LF * MW * MH * 4) {
        LOG("chargen: %s has no 64px map cells, the map hero falls back to 25x38", path);
        map_hi = 0;
    }
    if (!l->ok) LOG("chargen: cannot use %s", path);
    return l->ok ? l : NULL;
}

typedef struct { const JsonNode *n; int kind; } Part;     /* kind: 0 fixed / own tint, 1 skin, 2 hair, 3 top */
/* Composes one cell (direction * 10 + frame) of a look into out[38*25] as RGB555 (0x8000 set; 0 = clear). */
#define HI 64
static float A[HI * HI], C[HI * HI][3];
static int compose(const unsigned char cg[8], int gender, int cell, int hi, uint16_t *out);
/* hi 2: a map cell (direction * 10 + frame) at 50x64 */
int Cg_ComposeMapCell(const unsigned char cg[8], int gender, int cell, uint16_t *out) { return compose(cg, gender, cell, 2, out); }
int Cg_ComposeCell(const unsigned char cg[8], int gender, int cell, uint16_t *out) { return compose(cg, gender, cell, 0, out); }
/* the idle pose of a direction at the source resolution, 64x64 (the creator's big preview and busts) */
int Cg_ComposeHi(const unsigned char cg[8], int gender, int dir, uint16_t *out) { return compose(cg, gender, dir & 3, 1, out); }
static int compose(const unsigned char cg[8], int gender, int cell, int hi, uint16_t *out)
{
    Part parts[24];
    int np = 0, i, j, k, x, W = hi == 2 ? MW : hi ? HI : LW, H = hi == 2 ? MH : hi ? HI : LH;
    float mul[3] = {1, 1, 1};
    int hair_rgb[3] = {0, 0, 0}, top_rgb[3] = {0, 0, 0}, have_hair = 0, have_top = 0;
    const char *body = gender ? "female" : "male";
    const JsonNode *n, *e;
    if (!Cg_Ready() || cell < 0 || cell >= (hi == 1 ? 4 : 4 * LF) || (hi == 2 && !map_hi)) return 0;
    {
        const JsonNode *m = Json_Get(Json_At(Json_Get(man, "skin"), cg[CG_SKIN] % (unsigned)(Json_Count(Json_Get(man, "skin")) ? Json_Count(Json_Get(man, "skin")) : 1)), "mul");
        if (m && m->child && m->child->next && m->child->next->next) { mul[0] = (float)m->child->num; mul[1] = (float)m->child->next->num; mul[2] = (float)m->child->next->next->num; }
    }
#define PICK(c) Json_At(list_of(c), Json_Count(list_of(c)) ? cg[c] % Json_Count(list_of(c)) : 0)
    have_hair = rgb_of(Json_Get(PICK(CG_HAIR_COL), "rgb"), &hair_rgb[0], &hair_rgb[1], &hair_rgb[2]);
    have_top = rgb_of(Json_Get(PICK(CG_TOP_COL), "rgb"), &top_rgb[0], &top_rgb[1], &top_rgb[2]);
    for (n = Json_Get(Json_Get(man, "body"), body) ? Json_Get(Json_Get(man, "body"), body)->child : NULL; n && np < 24; n = n->next) { parts[np].n = n; parts[np++].kind = 1; }
    {
        static const int cats[5] = {CG_HAIR, CG_TOP, CG_LEGS, CG_SHOES, CG_ACC};
        for (k = 0; k < 5; k++) {
            e = Json_Get(PICK(cats[k]), body);
            for (n = e ? e->child : NULL; n && np < 24; n = n->next) { parts[np].n = n; parts[np++].kind = cats[k] == CG_HAIR ? 2 : cats[k] == CG_TOP ? 3 : 0; }
        }
    }
#undef PICK
    for (i = 1; i < np; i++)                               /* z order (stable insertion sort) */
        for (j = i; j > 0 && Json_Num(parts[j - 1].n, "z", 0) > Json_Num(parts[j].n, "z", 0); j--) { Part t = parts[j]; parts[j] = parts[j - 1]; parts[j - 1] = t; }
    memset(A, 0, sizeof(float) * W * H);
    memset(C, 0, sizeof(float) * 3 * W * H);
    for (i = 0; i < np; i++) {
        Layer *l = layer(Json_Str(parts[i].n, "file", NULL));
        const unsigned char *pa, *pc;
        int tint = 0, tr = 0, tg = 0, tb = 0;
        float lo[3], hv[3];
        if (!l) continue;
        if (hi && l->size < 8 + 4L * LF * LW * LH * 4 + 4L * HI * HI * 4) continue;
        if (hi == 2 && l->size < 8 + 4L * LF * LW * LH * 4 + 4L * HI * HI * 4 + 4L * LF * MW * MH * 4) continue;
        pa = hi == 2 ? l->d + 8 + 4L * LF * LW * LH * 4 + 4L * HI * HI * 4 + (size_t)cell * MW * MH * 4 :
             hi ? l->d + 8 + 4L * LF * LW * LH * 4 + (size_t)cell * HI * HI * 4 : l->d + 8 + (size_t)cell * LW * LH * 4;
        pc = pa + W * H;
        if (parts[i].kind == 2 && have_hair) { tint = 1; tr = hair_rgb[0]; tg = hair_rgb[1]; tb = hair_rgb[2]; }
        else if (parts[i].kind == 3 && have_top) { tint = 1; tr = top_rgb[0]; tg = top_rgb[1]; tb = top_rgb[2]; }
        else if (parts[i].kind == 0 && rgb_of(Json_Get(parts[i].n, "tint"), &tr, &tg, &tb)) tint = 1;
        if (tint) {
            int c3[3] = {tr, tg, tb};
            for (k = 0; k < 3; k++) { int lv = c3[k] / 6; hv[k] = (float)clampi(c3[k] * 2 + 42); lo[k] = (float)(lv < 8 ? 8 : lv > 48 ? 48 : lv); }
        }
        for (x = 0; x < W * H; x++) {
            float a = pa[x] / 255.0f, r = pc[x * 3], g = pc[x * 3 + 1], b = pc[x * 3 + 2], oa;
            if (a <= 0) continue;
            if (parts[i].kind == 1) { r *= mul[0]; g *= mul[1]; b *= mul[2]; if (r > 255) r = 255; if (g > 255) g = 255; if (b > 255) b = 255; }
            else if (tint) {
                float gy = (r * 299 + g * 587 + b * 114) / 1000.0f / 255.0f;
                r = lo[0] + (hv[0] - lo[0]) * gy; g = lo[1] + (hv[1] - lo[1]) * gy; b = lo[2] + (hv[2] - lo[2]) * gy;
            }
            oa = a + A[x] * (1 - a);
            C[x][0] = (r * a + C[x][0] * A[x] * (1 - a)) / oa;
            C[x][1] = (g * a + C[x][1] * A[x] * (1 - a)) / oa;
            C[x][2] = (b * a + C[x][2] * A[x] * (1 - a)) / oa;
            A[x] = oa;
        }
    }
    for (x = 0; x < W * H; x++) {
        int r = clampi((int)(C[x][0] + 0.5f)), g = clampi((int)(C[x][1] + 0.5f)), b = clampi((int)(C[x][2] + 0.5f));
        out[x] = A[x] >= 0.5f ? (uint16_t)(0x8000 | (r >> 3) | (g >> 3) << 5 | (b >> 3) << 10) : 0;
    }
    return 1;
}
/* The same cell as SPR1-style kind (0 solid, 255 clear) and RGB888, for jm_painted.c's sprite table. */
int Cg_ComposeCellRgb(int cell, unsigned char *kind, unsigned char *rgb)
{
    static uint16_t px[MW * MH];
    int x, n = Cg_MapHi() ? MW * MH : LW * LH;
    if (!(Cg_MapHi() ? Cg_ComposeMapCell(jm.cg, jm.gender, cell, px) : Cg_ComposeCell(jm.cg, jm.gender, cell, px))) return 0;
    for (x = 0; x < n; x++) {
        kind[x] = px[x] ? 0 : 255;
        rgb[x * 3] = (unsigned char)((px[x] & 31) * 255 / 31); rgb[x * 3 + 1] = (unsigned char)((px[x] >> 5 & 31) * 255 / 31); rgb[x * 3 + 2] = (unsigned char)((px[x] >> 10 & 31) * 255 / 31);
    }
    return 1;
}
