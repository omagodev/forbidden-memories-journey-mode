/* The hero assembled from layers at run time (art: art_dk/chargen, format "journey-chargen-1"; notes in tools/CHARGEN_FORMAT.md).
 * assets/chargen/manifest.json lists the layers (body, outfit styles, hair styles, accessories) and the palettes; each layer is a packed
 * CGP1 file: 4 directions x 5 frames of 48x62 texels, a texel being "outline" or a descriptor (kind, 4 palette-slot weights, fixed rgb).
 * Cg_Compose paints body, outfit, hair, accessory in that order into the hero's bank page (a later layer overwrites; an empty texel leaves
 * what is below), the same layout as every sprite sheet of the mod (a column a frame, a 64-texel row a direction), on the CPU:
 *     colour = clip(rgb + sum over slots q of W_q / 100 * palette[q] + 0.5)        (jm_painted.c spr_bake's formula)
 * The choice is jm.cg[] (saved in journey.sav, save version 4); jm.cg_set is 0 on a save from before the creator, which keeps the old hero.
 * Categories (the creator's rows): skin, outfit, outfit colour, hair, hair colour, accessory, accessory colour. */
#include "jm.h"
#include <stdlib.h>
#include <string.h>

#define CW 48
#define CH 62
#define MAXL 32
extern uint16_t *SoftGpu_Bank(int bank);

typedef struct { char key[40]; unsigned char *d; long size; int ok; } Layer;
static JsonNode *man;
static int ready = -1;
static Layer cache[MAXL];
static int ncache;
static const JsonNode *parts_o, *pal_skin, *pal_hair;
static int outline[3] = {34, 24, 30};

int Cg_Ready(void)
{
    if (ready < 0) {
        char *t = Jm_ReadText("assets/chargen/manifest.json");
        ready = 0;
        if (t) {
            man = Json_Parse(t);
            free(t);
            if (man && Json_Get(man, "parts") && Json_Get(man, "palettes") && Json_Get(man, "draw_order")) {
                const JsonNode *o = Json_Get(man, "outline_rgb");
                parts_o = Json_Get(man, "parts");
                pal_skin = Json_Get(Json_Get(man, "palettes"), "skin");
                pal_hair = Json_Get(Json_Get(man, "palettes"), "hair");
                if (o && o->child && o->child->next && o->child->next->next) {
                    outline[0] = (int)o->child->num; outline[1] = (int)o->child->next->num; outline[2] = (int)o->child->next->next->num;
                }
                ready = pal_skin && pal_hair && Json_Get(parts_o, "body") && Json_Get(parts_o, "outfit") && Json_Get(parts_o, "hair") && Json_Get(parts_o, "accessory") ? 1 : 0;
            }
            if (ready != 1) { LOG("chargen: manifest.json is not usable"); ready = 0; }
            else LOG("chargen: ready, skin %d outfit %d hair %d accessory %d", Json_Count(pal_skin), Json_Count(Json_Get(parts_o, "outfit")),
                     Json_Count(Json_Get(parts_o, "hair")), Json_Count(Json_Get(parts_o, "accessory")));
        }
    }
    return ready == 1;
}
int Cg_Frames(void) { return 5; }

/* ------------------------------------------------------------ the choice */
enum { CG_SKIN, CG_OUTFIT, CG_OUTFIT_COL, CG_HAIR, CG_HAIR_COL, CG_ACC, CG_ACC_COL, CG_N };
static const char *const cat_id[CG_N] = {"skin", "outfit", "outfit_colour", "hair", "hair_colour", "accessory", "accessory_colour"};

static const JsonNode *style_at(const char *part, int i)         /* the i-th style of a part; accessories: 0 is "none", then the manifest's order */
{
    const JsonNode *n, *p = Json_Get(parts_o, part);
    int k = 0;
    if (!p) return NULL;
    if (!strcmp(part, "accessory")) {
        if (i == 0) return Json_Get(p, "none");
        i--;
    }
    for (n = p->child; n; n = n->next) {
        if (!strcmp(part, "accessory") && n->key && !strcmp(n->key, "none")) continue;
        if (k++ == i) return n;
    }
    return NULL;
}
static int style_count(const char *part)
{
    const JsonNode *p = Json_Get(parts_o, part);
    return p ? Json_Count(p) : 0;       /* accessory: the manifest holds "none" too, so this is 1 + the real ones */
}
static const char *style_name(const char *part, int i) { const JsonNode *n = style_at(part, i); return n && n->key ? n->key : "?"; }

int Cg_CatCount(void) { return Cg_Ready() ? CG_N : 0; }
const char *Cg_CatId(int c) { return c >= 0 && c < CG_N ? cat_id[c] : ""; }
static int cur_style(int c, const char *part) { int n = style_count(part); return n > 0 ? jm.cg[c] % n : 0; }
static const JsonNode *colourways(int style_cat, const char *part)
{
    const JsonNode *s = style_at(part, cur_style(style_cat, part));
    return s ? Json_Get(s, "colourways") : NULL;
}
int Cg_OptCount(int c)
{
    if (!Cg_Ready()) return 0;
    switch (c) {
    case CG_SKIN: return Json_Count(pal_skin);
    case CG_OUTFIT: return style_count("outfit");
    case CG_OUTFIT_COL: return Json_Count(colourways(CG_OUTFIT, "outfit"));
    case CG_HAIR: return style_count("hair");
    case CG_HAIR_COL: return Json_Count(pal_hair);
    case CG_ACC: return style_count("accessory");
    case CG_ACC_COL: { int n = Json_Count(colourways(CG_ACC, "accessory")); return cur_style(CG_ACC, "accessory") == 0 ? 0 : n; }   /* none: no colour to choose */
    }
    return 0;
}
int Cg_Get(int c) { int n = Cg_OptCount(c); return c >= 0 && c < CG_N && n > 0 ? jm.cg[c] % n : 0; }
void Cg_Set(int c, int v)
{
    int n = Cg_OptCount(c);
    if (c < 0 || c >= CG_N) return;
    if (c == CG_ACC_COL && n == 0) return;
    if (n <= 0) return;
    jm.cg[c] = (unsigned char)(((v % n) + n) % n);
    if (c == CG_OUTFIT) jm.cg[CG_OUTFIT_COL] = 0;          /* a style has its own colourways */
    if (c == CG_ACC) jm.cg[CG_ACC_COL] = 0;
}
void Cg_Defaults(void)
{
    memset(jm.cg, 0, sizeof(jm.cg));
    jm.cg_set = Cg_Ready() ? 1 : 0;
    if (jm.cg_set && Json_Count(pal_skin) > 1) jm.cg[CG_SKIN] = 1;      /* "tan": the old hero's skin */
}
unsigned Cg_Signature(void)
{
    unsigned h = (unsigned)jm.cg_set;
    int i;
    for (i = 0; i < CG_N; i++) h = h * 31u + jm.cg[i];
    return h;
}

/* the manifest's "avoid_combinations" ({hair, accessory}): the creator skips them while cycling */
int Cg_Avoided(void)
{
    const JsonNode *a, *list;
    if (!Cg_Ready()) return 0;
    list = Json_Get(man, "avoid_combinations");
    for (a = list ? list->child : NULL; a; a = a->next) {
        const char *h = Json_Str(a, "hair", NULL), *ac = Json_Str(a, "accessory", NULL);
        if (h && ac && !strcmp(h, style_name("hair", cur_style(CG_HAIR, "hair"))) && !strcmp(ac, style_name("accessory", cur_style(CG_ACC, "accessory")))) return 1;
    }
    return 0;
}

/* names -> the text of the current language (ui.json "chargen.names"), the raw name when there is none */
static const char *named(const char *name)
{
    char path[64];
    const char *t;
    snprintf(path, sizeof(path), "chargen.names.%s", name);
    t = Tr(path);
    return strncmp(t, "chargen.", 8) ? t : name;
}
const char *Cg_CatLabel(int c) { char p[48]; if (c < 0 || c >= CG_N) return "?"; snprintf(p, sizeof(p), "chargen.rows.%s", cat_id[c]); return Tr(p); }
const char *Cg_OptLabel(int c, int o)
{
    const JsonNode *n;
    if (!Cg_Ready()) return "?";
    switch (c) {
    case CG_SKIN: n = Json_At(pal_skin, o); return n ? named(Json_Str(n, "name", "?")) : "?";
    case CG_HAIR_COL: n = Json_At(pal_hair, o); return n ? named(Json_Str(n, "name", "?")) : "?";
    case CG_OUTFIT: return named(style_name("outfit", o));
    case CG_HAIR: return named(style_name("hair", o));
    case CG_ACC: return named(style_name("accessory", o));
    case CG_OUTFIT_COL: n = Json_At(colourways(CG_OUTFIT, "outfit"), o); return n ? named(Json_Str(n, "name", "?")) : "?";
    case CG_ACC_COL: n = Json_At(colourways(CG_ACC, "accessory"), o); return n ? named(Json_Str(n, "name", "?")) : "-";
    }
    return "?";
}

/* ------------------------------------------------------------ compose */
static Layer *layer(const JsonNode *style)
{
    const char *file = Json_Str(style, "packed", NULL);
    char path[96];
    int i;
    Layer *l;
    if (!file) return NULL;
    for (i = 0; i < ncache; i++) if (!strcmp(cache[i].key, file)) return cache[i].ok ? &cache[i] : NULL;
    if (ncache >= MAXL) return NULL;
    l = &cache[ncache++];
    memset(l, 0, sizeof(*l));
    strncpy(l->key, file, sizeof(l->key) - 1);
    snprintf(path, sizeof(path), "assets/chargen/%s", file);
    l->d = Jm_Slurp(path, &l->size);
    l->ok = l->d && l->size >= 9 && !memcmp(l->d, "CGP1", 4) && l->d[4] == 5 && l->d[5] == CW && l->d[6] == CH;
    if (!l->ok) LOG("chargen: cannot use %s", path);
    return l->ok ? l : NULL;
}

typedef struct { int rgb[5][3]; } Pal;      /* index 1..4 */
static const JsonNode *source_rgb(const char *name, const JsonNode *skin, const JsonNode *hair, const JsonNode *ow, const JsonNode *acc)
{
    if (!strcmp(name, "skin")) return Json_Get(skin, "rgb");
    if (!strcmp(name, "hair")) return Json_Get(hair, "rgb");
    if (!strcmp(name, "outfit.main")) return Json_Get(ow, "main");
    if (!strcmp(name, "outfit.trim")) return Json_Get(ow, "trim");
    if (!strcmp(name, "outfit.trousers")) return Json_Get(ow, "trousers");
    if (!strcmp(name, "accessory.a")) return Json_Get(acc, "a");
    if (!strcmp(name, "accessory.b")) return Json_Get(acc, "b");
    return NULL;
}

static void paint_layer(const Layer *l, const JsonNode *style, const Pal *pal, uint16_t *bank, int page)
{
    const unsigned char *d = l->d;
    long ndesc = d[7] | d[8] << 8, pos = 9 + ndesc * 8;
    int dir, f;
    (void)style;
    for (dir = 0; dir < 4; dir++)
        for (f = 0; f < 5; f++) {
            int x0, y0, w, h, yy, xx, ox = (page & 3) * 256 + f * CW, oy = (page >> 2) * 256 + dir * 64;
            if (pos + 4 > l->size) return;
            x0 = d[pos]; y0 = d[pos + 1]; w = d[pos + 2]; h = d[pos + 3]; pos += 4;
            if (!w || !h) continue;
            if (pos + (long)w * h > l->size) return;
            for (yy = 0; yy < h; yy++)
                for (xx = 0; xx < w; xx++) {
                    int idx = d[pos + yy * w + xx], r, g, b, q;
                    if (idx == 0) continue;
                    if (idx == 1) { r = outline[0]; g = outline[1]; b = outline[2]; }
                    else {
                        const unsigned char *e = d + 9 + (long)(idx - 2) * 8;           /* kind, W1..W4, r, g, b */
                        float fr = e[5], fg = e[6], fb = e[7];
                        for (q = 1; q <= 4; q++) {
                            float wq = e[q] / 100.0f;
                            if (wq == 0) continue;
                            fr += wq * pal->rgb[q][0]; fg += wq * pal->rgb[q][1]; fb += wq * pal->rgb[q][2];
                        }
                        r = (int)(fr + 0.5f); g = (int)(fg + 0.5f); b = (int)(fb + 0.5f);
                    }
                    r = r < 0 ? 0 : r > 255 ? 255 : r; g = g < 0 ? 0 : g > 255 ? 255 : g; b = b < 0 ? 0 : b > 255 ? 255 : b;
                    bank[(size_t)(oy + y0 + yy) * 1024 + ox + x0 + xx] = (uint16_t)(0x8000 | (r >> 3) | (g >> 3) << 5 | (b >> 3) << 10);
                }
            pos += (long)w * h;
        }
}

/* Paints the hero into a bank page (clears it first).  Returns 1 if it did. */
int Cg_Compose(int bank_no, int page)
{
    uint16_t *bank = SoftGpu_Bank(bank_no);
    const JsonNode *skin, *hair, *ow, *acc_cw, *order, *o;
    int dir, y, k;
    if (!Cg_Ready() || !bank) return 0;
    skin = Json_At(pal_skin, Cg_Get(CG_SKIN));
    hair = Json_At(pal_hair, Cg_Get(CG_HAIR_COL));
    ow = Json_At(colourways(CG_OUTFIT, "outfit"), Cg_Get(CG_OUTFIT_COL));
    acc_cw = Cg_OptCount(CG_ACC_COL) ? Json_At(colourways(CG_ACC, "accessory"), Cg_Get(CG_ACC_COL)) : NULL;
    for (dir = 0; dir < 4; dir++)
        for (y = 0; y < 64; y++) memset(bank + (size_t)((page >> 2) * 256 + dir * 64 + y) * 1024 + (page & 3) * 256, 0, 256 * sizeof(uint16_t));
    order = Json_Get(man, "draw_order");
    for (o = order ? order->child : NULL; o; o = o->next) {
        const JsonNode *style = NULL, *slots;
        Layer *l;
        Pal pal;
        if (!o->str) continue;
        if (!strcmp(o->str, "body")) style = Json_Get(Json_Get(parts_o, "body"), "base");
        else if (!strcmp(o->str, "outfit")) style = style_at("outfit", cur_style(CG_OUTFIT, "outfit"));
        else if (!strcmp(o->str, "hair")) style = style_at("hair", cur_style(CG_HAIR, "hair"));
        else if (!strcmp(o->str, "accessory")) style = style_at("accessory", cur_style(CG_ACC, "accessory"));
        if (!style || !Json_Get(style, "packed")) continue;                    /* an accessory "none" has no layer */
        l = layer(style);
        if (!l) continue;
        memset(&pal, 0, sizeof(pal));
        slots = Json_Get(style, "slots");
        for (k = 1; k <= 4; k++) {
            char key[4];
            const char *src;
            const JsonNode *rgb;
            snprintf(key, sizeof(key), "%d", k);
            src = Json_Str(slots, key, NULL);
            rgb = src ? source_rgb(src, skin, hair, ow, acc_cw) : NULL;
            if (rgb && rgb->child && rgb->child->next && rgb->child->next->next) {
                pal.rgb[k][0] = (int)rgb->child->num; pal.rgb[k][1] = (int)rgb->child->next->num; pal.rgb[k][2] = (int)rgb->child->next->next->num;
            }
        }
        paint_layer(l, style, &pal, bank, page);
    }
    return 1;
}
