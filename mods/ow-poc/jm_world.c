/* Journey Mode world: the map from assets/world.jwld, collision, areas, the people standing on it,
 * and drawing it all.  The map is 64 x 72 tiles of 32 units in five areas; see tools/make_world.py. */
#include "types.h"
#include "jm.h"
#include <math.h>
#include <stdlib.h>
#include <string.h>
static char home_anchor[MAX_NPC][40];   /* the anchor journey.json gives each one; "places" may move him for a while */

extern JsonNode *jm_rules;
extern int Story_Cond(const JsonNode *c);

static unsigned char tile[MH][MW], deco[MH][MW], tint[MH][MW];
static unsigned char vcol[MH + 1][MW + 1][3];
static int loaded;
/* Meshes standing on the map (houses, fences, stalls, rocks), from assets/props.json. */
#define MAX_PROPS 512
static struct { Mesh *mesh; float x, z, yaw; } props[MAX_PROPS];
static int prop_count;
Npc npcs[MAX_NPC];
int npc_count;

#define MAX_AREAS 16
static struct { char name[28]; int track; } areas[MAX_AREAS];
static int area_count;

static unsigned hash2(int x, int z) { unsigned h = (unsigned)(x * 73856093) ^ (unsigned)(z * 19349663); h ^= h >> 13; h *= 0x5bd1e995u; return h ^ (h >> 15); }

/* Props that are meshes, by deco number. */
static const char *const prop_mesh[8] = {NULL, "p_boulder_sandstone", NULL, "p_agave", "p_skull_cattle",
                                         "p_tumbleweed", "p_hoodoo", "p_barrel_cactus"};

static void build_light(void)
{
    int x, z;
    for (z = 0; z <= MH; z++)
        for (x = 0; x <= MW; x++) {
            int sum = 0, n = 0, g = 0, dx, dz, r, gg, b;
            float base;
            for (dz = -1; dz <= 0; dz++)
                for (dx = -1; dx <= 0; dx++) {
                    int tx = x + dx, tz = z + dz, t;
                    if (tx < 0 || tz < 0 || tx >= MW || tz >= MH) continue;
                    t = tile[tz][tx];
                    sum += t == T_WATER ? 112 : (t >= T_RUIN && t <= T_HOUSE_B) || t == T_WALL || t == T_PALM ? 108 : 128;
                    g += tint[tz][tx];
                    n++;
                }
            if (!n) n = 1;
            base = (float)sum / n * (0.93f + 0.14f * (float)(hash2(x, z) & 255) / 255.0f);
            r = (int)(base - g * 4.0f / n);
            gg = (int)(base + g * 1.5f / n);
            b = (int)(base - g * 6.0f / n);
            vcol[z][x][0] = (unsigned char)(r < 0 ? 0 : r > 255 ? 255 : r);
            vcol[z][x][1] = (unsigned char)(gg < 0 ? 0 : gg > 255 ? 255 : gg);
            vcol[z][x][2] = (unsigned char)(b < 0 ? 0 : b > 255 ? 255 : b);
        }
}

static void tile_vec(const JsonNode *t, float *x, float *z)
{
    *x = (float)Json_At(t, 0)->num * TS;
    *z = (float)Json_At(t, 1)->num * TS;
}

int World_Load(void)
{
    long size;
    unsigned char *d;
    JsonNode *list, *n, *a;
    int i;
    if (loaded) return 1;
    d = Jm_Slurp("assets/world.jwld", &size);
    if (!d || size < 8 + 3 * MW * MH || memcmp(d, "JWLD", 4) || (d[4] | d[5] << 8) != MW || (d[6] | d[7] << 8) != MH) {
        LOG("journey: world.jwld missing or the wrong size");
        free(d);
        return 0;
    }
    memcpy(tile, d + 8, MW * MH);
    memcpy(deco, d + 8 + MW * MH, MW * MH);
    memcpy(tint, d + 8 + 2 * MW * MH, MW * MH);
    free(d);
    build_light();
    for (a = Json_Get(jm_rules, "areas"), n = a ? a->child : NULL; n && area_count < MAX_AREAS; n = n->next, area_count++) {
        strncpy(areas[area_count].name, Json_Str(n, "name", "?"), sizeof(areas[0].name) - 1);
        areas[area_count].track = (int)Json_Num(n, "track", 0);
    }
    list = Json_Get(jm_rules, "npcs");
    for (n = list ? list->child : NULL; n && npc_count < MAX_NPC; n = n->next) {
        Npc *p = &npcs[npc_count++];
        memset(p, 0, sizeof(*p));
        strncpy(p->id, Json_Str(n, "id", ""), sizeof(p->id) - 1);
        strncpy(p->name, Json_Str(n, "name", ""), sizeof(p->name) - 1);
        strncpy(p->mesh, Json_Str(n, "mesh", "Knight_Male"), sizeof(p->mesh) - 1);
        p->duelist_id = (int)Json_Num(n, "duelist_id", 0);
        if (Json_Str(n, "duelist", NULL)) {    /* a duelist of the mod's own (duelists/<id>.json): the host says which id it got this run */
            char identity[48];
            snprintf(identity, sizeof(identity), "ow-poc:%s", Json_Str(n, "duelist", ""));
            p->duelist_id = jm_host->duelist_id(jm_host, identity);
            if (p->duelist_id <= 0) p->duelist_id = (int)Json_Num(n, "duelist_id", 0);
        }
        p->portrait_id = (int)Json_Num(n, "portrait_id", 0);
        p->rules = Json_Get(n, "talk");
        p->moves = Json_Get(n, "places");
        p->base = Json_Get(n, "tile");
        strncpy(p->anchor, Json_Str(n, "anchor", ""), sizeof(p->anchor) - 1);
        snprintf(home_anchor[npc_count - 1], sizeof(home_anchor[0]), "%s", p->anchor);
        p->mesh_ptr = Gfx_Mesh(p->mesh);
        p->yaw = 3.14159265f;
    }
    for (i = 1; i < 8; i++) if (prop_mesh[i]) Gfx_Mesh(prop_mesh[i]);
    {
        char *text = Jm_ReadText("assets/props.json");
        JsonNode *pj = text ? Json_Parse(text) : NULL, *pl = pj ? Json_Get(pj, "props") : NULL;
        for (n = pl ? pl->child : NULL; n && prop_count < MAX_PROPS; n = n->next) {
            props[prop_count].mesh = Gfx_Mesh(Json_Str(n, "mesh", ""));
            props[prop_count].x = (float)Json_Num(n, "x", 0) * TS;
            props[prop_count].z = (float)Json_Num(n, "z", 0) * TS;
            props[prop_count].yaw = (float)Json_Num(n, "yaw", 0);
            if (props[prop_count].mesh) prop_count++;
        }
        free(text);
        if (pj) Json_Free(pj);
    }
    loaded = 1;
    LOG("journey: world loaded, %d npcs, %d areas", npc_count, area_count);
    return 1;
}

void World_PlaceNpcs(void)
{
    int i;
    for (i = 0; i < npc_count; i++) {
        Npc *p = &npcs[i];
        const JsonNode *where = p->base;
        JsonNode *m;
        if (i < MAX_NPC - 1 && home_anchor[i][0]) snprintf(p->anchor, sizeof(p->anchor), "%s", home_anchor[i]);
        for (m = p->moves ? p->moves->child : NULL; m; m = m->next)
            if (Story_Cond(Json_Get(m, "when"))) {
                /* "anchor": he stands somewhere else in the painted places (the farewells on the pier); "tile" is the old map's */
                if (Json_Str(m, "anchor", NULL)) { snprintf(p->anchor, sizeof(p->anchor), "%s", Json_Str(m, "anchor", "")); where = Json_Get(m, "tile") ? Json_Get(m, "tile") : p->base; if (!where) { p->hidden = 0; goto placed; } }
                else where = Json_Get(m, "tile");
                break;
            }
        if (!where || where->type != 'a') { p->hidden = 1; continue; }
        p->hidden = 0;
        tile_vec(where, &p->x, &p->z);
        continue;
placed:
        p->x = p->z = 2.5f * TS;           /* no tile on the old map: only the painted places show him */
    }
}

void World_Spawn(float *x, float *z)
{
    JsonNode *s = Json_Get(jm_rules, "start");
    *x = s ? (float)Json_At(s, 0)->num * TS : 15 * TS;
    *z = s ? (float)Json_At(s, 1)->num * TS : 33 * TS;
}

/* ------------------------------------------------------------- collision */
static int locked_by(int t, int tx, int tz)
{
    JsonNode *l = Json_Get(jm_rules, "locks"), *n;
    static const char *const names[] = {"portal", "door", "throne", "gate"};
    int k = t == T_PORTAL ? 0 : t == T_DOOR ? 1 : t == T_THRONE ? 2 : t == T_GATE ? 3 : -1;
    for (n = l ? l->child : NULL; n; n = n->next) {
        const char *tn = Json_Str(n, "tile", NULL);
        JsonNode *r = Json_Get(n, "rect"), *need = Json_Get(n, "needs"), *f;
        if (tn && k >= 0 && !strcmp(tn, names[k])) {
            for (f = need ? need->child : NULL; f; f = f->next)
                if (!Story_Has(f->str)) return 1;
            continue;
        }
        if (r && tx >= (int)Json_At(r, 0)->num && tz >= (int)Json_At(r, 1)->num && tx <= (int)Json_At(r, 2)->num &&
            tz <= (int)Json_At(r, 3)->num && Story_Cond(Json_Get(n, "when")))
            return 1;
    }
    return 0;
}

int World_Solid(float x, float z)
{
    int tx = (int)floorf(x / TS), tz = (int)floorf(z / TS), t;
    if (tx < 0 || tz < 0 || tx >= MW || tz >= MH) return 1;
    t = tile[tz][tx];
    if (locked_by(T_SAND, tx, tz)) return 1;
    if (t == T_PORTAL || t == T_DOOR || t == T_THRONE || t == T_GATE) return locked_by(t, tx, tz);
    if (deco[tz][tx] == 1 || deco[tz][tx] == 6 || deco[tz][tx] == 7 || deco[tz][tx] == 16 || deco[tz][tx] == 17 ||
        deco[tz][tx] == 20 || deco[tz][tx] == 23) return 1;
    return t == T_WATER || t == T_WALL || t == T_PALM || (t >= T_RUIN && t <= T_HOUSE_B);
}

int World_Blocked(float x, float z)
{
    int i;
    const float r = 9.0f;
    if (World_Solid(x - r, z - r) || World_Solid(x + r, z - r) || World_Solid(x - r, z + r) || World_Solid(x + r, z + r)) return 1;
    for (i = 0; i < npc_count; i++) {
        float dx = x - npcs[i].x, dz = z - npcs[i].z;
        if (!npcs[i].hidden && dx * dx + dz * dz < 44.0f * 44.0f) return 1;
    }
    return 0;
}

int World_NearestNpc(float x, float z, float reach)
{
    int i, best = -1;
    float bd = reach * reach;
    for (i = 0; i < npc_count; i++) {
        float dx = x - npcs[i].x, dz = z - npcs[i].z, d = dx * dx + dz * dz;
        if (!npcs[i].hidden && d < bd) { bd = d; best = i; }
    }
    return best;
}

int World_Area(float x, float z)
{
    int tx = (int)(x / TS), ty = (int)(z / TS);
    if (ty >= 72) return 8 + (ty - 72) / RH * 2 + (tx >= RW);   /* the rooms of chapters 6 to 8 */
    if (ty >= 56) return 6;
    if (tx >= 47) { if (ty <= 21) return 4; if (ty <= 42) return 5; }
    if (ty <= 3 + RO) return 3;
    if (ty <= 8 + RO) return 2;
    if (tx >= 28 && tx <= 41 && ty >= 24 + RO && ty <= 34 + RO) return 7;
    if (tx <= 26 && ty <= 34 + RO) return 0;
    return 1;
}

const char *World_AreaName(int a) { return a >= 0 && a < area_count ? TrAt("areas", a, areas[a].name) : ""; }

/* A tile as one colour of the maps. */
unsigned World_MapColor(int tx, int tz)
{
    int t, d;
    if (tx < 0 || tz < 0 || tx >= MW || tz >= MH) return 0x101018;
    t = tile[tz][tx];
    d = deco[tz][tx];
    switch (t) {
    case T_WATER: return 0x2F6BC8;
    case T_PATH: return 0xE2BC3A;
    case T_ARENA: return 0xF0D060;
    case T_WALL: case T_PAL: case T_RUIN: case T_COL: case T_OBEL: return 0x6E5A44;
    case T_PALM: return 0x2F8A3A;
    case T_HOUSE: case T_HOUSE_B: return 0xB07858;
    case T_BRIDGE: return 0xA06A38;
    case T_GRASS: return 0x4E9A48;
    case T_PORTAL: return 0x70C0F0;
    case T_DOOR: case T_GATE: return 0x8A2E3A;
    case T_THRONE: return 0xB070E0;
    }
    if (d >= 8 && d <= 11) return 0x4E9A48;
    if (d >= 1 && d <= 7) return 0xA08060;
    return tint[tz][tx] ? 0x9AB860 : 0xD8BC78;
}
int World_AreaMusic(int a) { return a >= 0 && a < area_count ? 0x7000 + areas[a].track * 0x10 : 0; }

/* --------------------------------------------------------------- drawing */
static float fog(float depth)
{
    float f = 1.12f - (depth - 0.65f * cam_d) / (2.1f * cam_d);      /* relative to the camera distance */
    return f < 0.70f ? 0.70f : f > 1.0f ? 1.0f : f;
}

static unsigned char clamp8(float v) { return (unsigned char)(v < 0 ? 0 : v > 255 ? 255 : v); }

static void rgb_fill(unsigned char rgb[4][3], float k0, float k1, float k2, float k3, float r, float g, float b)
{
    const float k[4] = {k0, k1, k2, k3};
    int i;
    for (i = 0; i < 4; i++) { rgb[i][0] = clamp8(r * k[i]); rgb[i][1] = clamp8(g * k[i]); rgb[i][2] = clamp8(b * k[i]); }
}

static int ground_texture(int tx, int tz)
{
    int t = tile[tz][tx];
    unsigned h = hash2(tx, tz);
    switch (t) {
    case T_PATH: return World_Area((float)tx * TS, (float)tz * TS) == 5 ? TX_GRANITE : ((tx + tz) & 1) ? TX_PATH1 : TX_PATH0;
    case T_WATER: return ((gfx_frame >> 4) + (unsigned)tx + (unsigned)tz) & 1 ? TX_WATER1 : TX_WATER0;
    case T_ARENA: return TX_ARENA;
    case T_PORTAL: case T_DOOR: case T_GATE: return TX_PATH0;
    case T_THRONE: return TX_GRANITE;
    case T_GRASS: return JM_QUALITY && (h & 3) ? TX_GRASS_Q : TX_GRASS;
    case T_BRIDGE: return TX_PLANK;
    case T_PAL: return World_Area((float)tx * TS, (float)tz * TS) == 5 ? TX_GRANITE : TX_SAND0;
    default:
        if (tint[tz][tx] >= 3 && (h & 3)) return TX_OASIS;
        if ((h & 15) == 0) return TX_CRACKED;
        if (JM_QUALITY && tint[tz][tx] < 3 && (h & 3)) return (h & 4) ? TX_SAND_Q0 : TX_SAND_Q1;
        return (int)(h >> 4) % 3;
    }
}

typedef struct { float x, y, d; int ok; } Pt;

static Pt corner(float wx, float wy, float wz)
{
    Pt p;
    p.ok = Gfx_Project(wx, wy, wz, &p.x, &p.y, &p.d);
    return p;
}

static void quad_of(float sx[4], float sy[4], Pt a, Pt b, Pt c, Pt d)
{
    sx[0] = a.x; sy[0] = a.y; sx[1] = b.x; sy[1] = b.y; sx[2] = c.x; sy[2] = c.y; sx[3] = d.x; sy[3] = d.y;
}

static int box_height(int t, int tx, int tz)
{
    switch (t) {
    case T_WALL: return 30;
    case T_PAL: return 64;
    case T_RUIN: return 10 + (int)(hash2(tx, tz) & 15);
    case T_COL: return 72;
    case T_OBEL: return 124;
    default: return 0;
    }
}

static void draw_box(int tx, int tz, int t)
{
    int in = t == T_COL ? 8 : t == T_OBEL ? 9 : t == T_RUIN ? 4 : 0, h = box_height(t, tx, tz);
    int top_tex = t == T_PAL ? TX_MARBLE : TX_WALL_TOP, side_tex = t == T_PAL ? TX_LAPIS : TX_WALL_SIDE;
    float x0 = (float)(tx * TS + in), x1 = (float)((tx + 1) * TS - in), z0 = (float)(tz * TS + in), z1 = (float)((tz + 1) * TS - in);
    float tin = t == T_OBEL ? 12.0f : 0.0f;
    float sx[4], sy[4], depth, f;
    unsigned char rgb[4][3];
    Pt tl, tr, bl, br, ttl, ttr, tbl, tbr;
    int same_s = (tz + 1 < MH && tile[tz + 1][tx] == t && !in), same_w = (tx > 0 && tile[tz][tx - 1] == t && !in),
        same_e = (tx + 1 < MW && tile[tz][tx + 1] == t && !in);
    ttl = corner(x0 + tin, (float)-h, z0 + tin); ttr = corner(x1 - tin, (float)-h, z0 + tin);
    tbl = corner(x0 + tin, (float)-h, z1 - tin); tbr = corner(x1 - tin, (float)-h, z1 - tin);
    tl = corner(x0, 0, z0); tr = corner(x1, 0, z0); bl = corner(x0, 0, z1); br = corner(x1, 0, z1);
    if (!ttl.ok || !tbl.ok || !bl.ok) return;
    depth = (bl.d + tr.d) * 0.5f;
    f = fog(depth);
    if (ttr.x < -40 || ttl.x > 360 || bl.y < -40 || ttl.y > 280) return;
    /* the top */
    quad_of(sx, sy, ttl, ttr, tbl, tbr);
    rgb_fill(rgb, 1.15f, 1.15f, 1.05f, 1.05f, 128 * f, 128 * f, 128 * f);
    Gfx_SceneQuad(sx, sy, (top_tex & 3) * 64, (top_tex >> 2) * 64, 64, 64, depth - 1.0f, rgb, 0);
    if (!same_s) {   /* the face toward the camera */
        quad_of(sx, sy, tbl, tbr, bl, br);
        rgb_fill(rgb, 0.92f, 0.92f, 0.62f, 0.62f, 128 * f, 128 * f, 128 * f);
        Gfx_SceneQuad(sx, sy, (side_tex & 3) * 64, (side_tex >> 2) * 64, 64, 64, depth, rgb, 0);
    }
    if (!same_w && cam_x < x0) {
        quad_of(sx, sy, ttl, tbl, tl, bl);
        rgb_fill(rgb, 0.80f, 0.80f, 0.55f, 0.55f, 128 * f, 128 * f, 128 * f);
        Gfx_SceneQuad(sx, sy, (side_tex & 3) * 64, (side_tex >> 2) * 64, 64, 64, depth - 0.5f, rgb, 0);
    }
    if (!same_e && cam_x > x1) {
        quad_of(sx, sy, tbr, ttr, br, tr);
        rgb_fill(rgb, 0.80f, 0.80f, 0.55f, 0.55f, 128 * f, 128 * f, 128 * f);
        Gfx_SceneQuad(sx, sy, (side_tex & 3) * 64, (side_tex >> 2) * 64, 64, 64, depth - 0.5f, rgb, 0);
    }
}

/* A gate that stands in its tile as a glowing plane, or a dark one while it is locked. */
static void draw_gate(int tx, int tz, int t)
{
    float x0 = (float)(tx * TS), x1 = (float)((tx + 1) * TS), z = (float)(tz * TS + TS / 2), h = t == T_THRONE ? 40.0f : 62.0f;
    Pt a = corner(x0, -h, z), b = corner(x1, -h, z), c = corner(x0, 0, z), d = corner(x1, 0, z);
    float sx[4], sy[4], f;
    unsigned char rgb[4][3];
    int locked = locked_by(t, tx, tz), tex = locked ? TX_GRANITE : TX_GLOW;
    float pulse = locked ? 0.0f : 0.25f * sinf((float)gfx_frame * 0.12f + tx);
    if (!a.ok || !c.ok) return;
    f = fog(c.d);
    quad_of(sx, sy, a, b, c, d);
    rgb_fill(rgb, 1.0f + pulse, 1.0f + pulse, 0.8f + pulse, 0.8f + pulse, 128 * f, 128 * f, 128 * f);
    Gfx_SceneQuad(sx, sy, (tex & 3) * 64, (tex >> 2) * 64, 64, 64, c.d, rgb, (gfx_frame >> 3) & 1);
}

static void sprite_at(float wx, float wz, int kind, unsigned h)
{
    float f = fog(0), ox = (float)((int)(h & 15) - 8), oz = (float)((int)((h >> 4) & 15) - 8);
    int shade = (int)(128 * 1.0f * f) - (int)((h >> 8) & 7);
    int flip = (int)((h >> 12) & 1);
    if (kind < 16) { wx += ox * 0.8f; wz += oz * 0.8f; }
    switch (kind) {
    case 8: Gfx_Sprite(wx, wz, SPR_X + 0, 0, 32, 40, 40, 48, shade, flip); break;
    case 9: Gfx_Sprite(wx, wz, SPR_X + 32, 0, 32, 40, 44, 66, shade, flip); break;
    case 10: Gfx_Sprite(wx, wz, SPR_X + 64, 0, 32, 40, 44, 50, shade, flip); break;
    case 11: Gfx_Sprite(wx, wz, SPR_X + 96, 0, 32, 40, 54, 68, shade, flip); break;
    case 12: case 13: Gfx_Sprite(wx, wz, SPR_X + 128 + (kind - 12) * 16, 0, 16, 16, 22, 22, shade, flip); break;
    case 14: case 15: Gfx_Sprite(wx, wz, SPR_X + 128 + (kind - 14) * 16, 16, 16, 8, 22, 11, shade, flip); break;
    case 16: Gfx_Sprite(wx, wz + 6, 512, 176, 24, 32, 20, 26, shade, 0); break;
    case 17: Gfx_Sprite(wx, wz + 6, 536, 176, 32, 40, 28, 36, shade, 0); break;
    case 20: Gfx_Sprite(wx, wz + 6, 568, 176, 32, 32, 28, 26, shade, 0); break;
    }
}

static void draw_npc(Npc *n, float px, float pz)
{
    float dx = px - n->x, dz = pz - n->z, want, d;
    int frame = 0;
    if (!n->mesh_ptr) return;
    if (dx * dx + dz * dz < 110.0f * 110.0f) {
        want = atan2f(dx, dz);
        d = want - n->yaw;
        while (d > 3.14159265f) d -= 6.2831853f;
        while (d < -3.14159265f) d += 6.2831853f;
        n->yaw += d * 0.2f;
    }
    Gfx_Shadow(n->x, n->z, 18);
    Gfx_DrawMesh(n->mesh_ptr, frame, n->x, 0, n->z, n->yaw, CHAR_SCALE, NULL, -3.0f);
}

/* A ring on the ground under the player, so he is easy to find when the camera is far away. */
static void player_ring(float px, float pz)
{
    enum { N = 20 };
    float r0 = 10.0f * CHAR_SCALE, r1 = 13.0f * CHAR_SCALE, sx[N + 1][2], sy[N + 1][2], d = 0, e;
    int i, pulse = 190 + (int)(60.0f * sinf((float)gfx_frame * 0.15f));
    unsigned char c[3][3];
    for (i = 0; i <= N; i++) {
        float a = (float)i * (6.2831853f / N);
        if (!Gfx_Project(px + cosf(a) * r0, 0, pz + sinf(a) * r0 * 0.9f, &sx[i][0], &sy[i][0], &e)) return;
        if (!Gfx_Project(px + cosf(a) * r1, 0, pz + sinf(a) * r1 * 0.9f, &sx[i][1], &sy[i][1], &e)) return;
    }
    Gfx_Project(px, 0, pz, &e, &e, &d);
    for (i = 0; i < 3; i++) { c[i][0] = (unsigned char)pulse; c[i][1] = (unsigned char)(pulse * 3 / 4); c[i][2] = 40; }
    for (i = 0; i < N; i++) {
        Gfx_SceneTri(sx[i][0], sy[i][0], sx[i][1], sy[i][1], sx[i + 1][0], sy[i + 1][0], c, d + 26.0f);
        Gfx_SceneTri(sx[i][1], sy[i][1], sx[i + 1][1], sy[i + 1][1], sx[i + 1][0], sy[i + 1][0], c, d + 26.0f);
    }
}

static int c_ground, c_tiles, c_props;

void World_Draw(float px, float pz, float pyaw, int walking, const int body_rgb[5], const Mesh *body)
{
    /* the grid reaches from the far edge of the view to the bottom one: with GH 56 the bottom rows were left blank */
    enum { GW = 64, GH = JM_QUALITY ? 68 : 56 };
    static Pt grid[GH][GW];
    static unsigned char cov[GH][GW];
    int cx = (int)(cam_x / TS), cz = (int)(cam_z / TS);
    int hx = (int)(cam_d * 0.026f) + 1, zb = (int)(cam_d * (JM_QUALITY ? 0.030f : 0.034f)), zf = (int)(cam_d * 0.017f) + 1;
    int x0 = cx - hx, x1 = cx + hx, z0 = cz - zb, z1 = cz + zf, x, z, i;
    int nx, nz, quads = 0;
    if (cz >= 72) {                          /* inside one of the rooms: do not draw its neighbours */
        int rx = cx >= RW ? RW : 0, rz = 72 + (cz - 72) / RH * RH;
        if (x0 < rx) x0 = rx;
        if (x1 > rx + RW - 1) x1 = rx + RW - 1;
        if (z0 < rz) z0 = rz;
        if (z1 > rz + RH - 1) z1 = rz + RH - 1;
    }
    if (x0 < 0) x0 = 0;
    if (z0 < 0) z0 = 0;
    if (x1 >= MW) x1 = MW - 1;
    if (z1 >= MH) z1 = MH - 1;
    if (x1 - x0 + 1 >= GW - 1) x1 = x0 + GW - 3;
    if (z1 - z0 + 1 >= GH - 1) z1 = z0 + GH - 3;
    nx = x1 - x0 + 1;
    nz = z1 - z0 + 1;
    Gfx_Backdrop(0x3C78D8, 0xEBD7AA);
    for (z = 0; z <= nz && z < GH; z++)
        for (x = 0; x <= nx && x < GW; x++) grid[z][x] = corner((float)((x0 + x) * TS), 0, (float)((z0 + z) * TS));
    memset(cov, 0, sizeof(cov));
    /* Ground: a quad a tile, except that plain sand or grass in blocks of 2 x 2 tiles is one quad when the camera is far. */
    for (z = 0; z < nz && z < GH - 1; z++)
        for (x = 0; x < nx && x < GW - 1; x++) {
            int tx = x0 + x, tz = z0 + z, k, step = 1, t = tile[tz][tx], u, v, same;
            Pt a = grid[z][x], b, c, d;
            float sx[4], sy[4], f;
            if (cov[z][x]) continue;
            if (cam_d > 700.0f && (t == T_SAND || t == T_GRASS || t == T_HOUSE || t == T_HOUSE_B || t == T_WATER)) {
                for (step = 4; step > 1; step >>= 1) {          /* a block of 4 x 4 or 2 x 2 tiles of one kind is one quad */
                    if ((tx | tz) & (step - 1) || x + step > nx || z + step > nz || (t == T_WATER && step > 2)) continue;
                    same = 1;
                    for (v = 0; v < step && same; v++)
                        for (u = 0; u < step; u++) {
                            int o = tile[tz + v][tx + u];
                            /* sand and grass may mix: the first tile decides the texture */
                            if (o != t && !((o == T_SAND || o == T_GRASS) && (t == T_SAND || t == T_GRASS))) { same = 0; break; }
                        }
                    if (same) break;
                }
                for (v = 0; v < step; v++)
                    for (u = 0; u < step; u++) cov[z + v][x + u] = 1;
            }
            unsigned char rgb[4][3];
            const Pt *p[4];
            b = grid[z][x + step]; c = grid[z + step][x]; d = grid[z + step][x + step];
            if (!a.ok || !d.ok || !b.ok || !c.ok) continue;
            if (b.x < -10 || a.x > 330 || c.y < -10 || a.y > 250) continue;
            if (++quads > 900) continue;                 /* 56 bytes each of the game's packet buffer */
            quad_of(sx, sy, a, b, c, d);
            p[0] = &a; p[1] = &b; p[2] = &c; p[3] = &d;
            for (k = 0; k < 4; k++) {
                const unsigned char *vc = vcol[tz + (k >> 1) * step][tx + (k & 1) * step];
                f = fog(p[k]->d);
                rgb[k][0] = clamp8(vc[0] * f); rgb[k][1] = clamp8(vc[1] * f); rgb[k][2] = clamp8(vc[2] * f);
            }
            Gfx_GroundQuad(sx, sy, ground_texture(tx, tz), rgb);
        }
    c_ground = Gfx_Items();
    /* things standing on the ground */
    for (z = z0; z <= z1; z++)
        for (x = x0; x <= x1; x++) {
            int t = tile[z][x], dk = deco[z][x];
            float wx = (float)(x * TS + TS / 2), wz = (float)(z * TS + TS / 2);
            float sxp, syp, dp;
            if (!Gfx_Project(wx, 0, wz, &sxp, &syp, &dp) || sxp < -70 || sxp > 390 || syp < -90 || syp > 330) continue;
            if (t == T_WALL || t == T_PAL || t == T_RUIN || t == T_COL || t == T_OBEL) draw_box(x, z, t);
            else if (t == T_PORTAL || t == T_DOOR || t == T_THRONE || t == T_GATE) draw_gate(x, z, t);
            else if (t == T_PALM) Gfx_Sprite(wx, wz - 2, SPR_X + 192, 0, 64, 96, 56, 84, (int)(128 * fog(dp)), (x + z) & 1);
            if (dk >= 8) {
                unsigned h = hash2(x, z);
                int far = dp > cam_d * 1.35f || cam_d > 900.0f;      /* level of detail: one sprite a tile in the distance, none for tufts */
                if (dk > 15) { sprite_at(wx, wz, dk, h); continue; }
                if (far && dk >= 12 && ((h & 3) || dp > cam_d * 1.15f)) continue;
                sprite_at(wx, wz, dk, h);
                if (far) continue;
                if (dk <= 11 && (h & 0x10000)) sprite_at(wx + 13, wz - 9, dk, h >> 3);
                if (dk >= 12) { sprite_at(wx + 12, wz + 6, dk, h >> 5); sprite_at(wx - 9, wz - 7, dk, h >> 9); }
            } else if (dk && prop_mesh[dk] && dp < cam_d * 1.5f) {
                Mesh *m = Gfx_Mesh(prop_mesh[dk]);
                /* not between the camera and the player: it would hide him */
                if (m && !(wz > pz - 8 && wz < pz + 0.3f * cam_d && wx > px - 80 && wx < px + 80)) Gfx_DrawMesh(m, 0, wx, 0, wz, (float)(hash2(x, z) & 255) * 0.0245f, 0.75f, NULL, 0);
            }
        }
    c_tiles = Gfx_Items();
    for (i = 0; i < prop_count; i++) {                    /* houses, fences, stalls, rocks */
        float sxp, syp, dp;
        if (!Gfx_Project(props[i].x, 0, props[i].z, &sxp, &syp, &dp) || sxp < -90 || sxp > 410 || syp < -90 || syp > 340) continue;
        if (cz >= 72 && props[i].z < 72 * TS) continue;
        Gfx_DrawMesh(props[i].mesh, 0, props[i].x, 0, props[i].z, props[i].yaw, 1.0f, NULL, 0);
    }
    c_props = Gfx_Items();
    for (i = 0; i < npc_count; i++) {
        float sxp, syp, dp;
        if (npcs[i].hidden) continue;
        if ((int)(npcs[i].x / TS) < x0 || (int)(npcs[i].x / TS) > x1 || (int)(npcs[i].z / TS) < z0 || (int)(npcs[i].z / TS) > z1) continue;
        if (!Gfx_Project(npcs[i].x, 0, npcs[i].z, &sxp, &syp, &dp) || sxp < -80 || sxp > 400 || syp < -100 || syp > 330) continue;
        draw_npc(&npcs[i], px, pz);
    }
    if (body) {
        int f = walking ? 1 + (int)((gfx_frame / 5) & 3) : 0;
        Gfx_Shadow(px, pz, 18);
        if (CAM_RING) player_ring(px, pz);
        Gfx_DrawMesh(body, f, px, 0, pz, pyaw, CHAR_SCALE, body_rgb, -3.0f);
    }
    if (jm_guide_on) Guide_Draw(px, pz);
    { static unsigned n; if (!(n++ % 240)) LOG("journey: items: tiles %d, props %d, people %d, quads %d", c_tiles - c_ground, c_props - c_tiles, Gfx_Items() - c_props, quads); }
    Gfx_End();
}
