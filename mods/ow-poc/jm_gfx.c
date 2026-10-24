/* Journey Mode graphics: assets, meshes, the camera, and polygons into the game's ordering table.
 *
 * Everything is drawn the way the PoC drew it: our own projection (a 45 degree camera that follows
 * the player), polygons sorted into the ordering table D_800E9D90[1] with GsSortPoly, and the port's
 * rasterizer does the rest at the internal scale.  This file adds Gouraud shading (G3 for characters,
 * GT4 for ground and sprites), a texture atlas read from bank 14, and depth sorting of the scene. */
#include "types.h"
#include "psyq/libgte.h"
#include "psyq/libgpu.h"
#include "psyq/libgs.h"
#include "game/ordering_tables.h"
#include "pc/render/soft_gpu.h"
#include "pc/cards/disc_art.h"
#include "pc/free_duel/duelists.h"
#include "jm.h"
#include <math.h>
#include <stdlib.h>
#include <string.h>

unsigned gfx_frame;
float cam_x, cam_z;
float cam_d = 340.0f;

static int ready;
static float lit0(float v) { return v > 0.0f ? v : 0.0f; }

/* ---------------------------------------------------------------- assets */
static int load_atlas(void)
{
    long size;
    unsigned char *d = Jm_Slurp("assets/atlas.raw", &size);
    u16 *bank = SoftGpu_Bank(BANK);
    int w, h, row;
    if (!d || !bank || size < 4) { free(d); return 0; }
    w = d[0] | d[1] << 8;
    h = d[2] | d[3] << 8;
    if (size < 4 + (long)w * h * 2) { free(d); return 0; }
    for (row = 0; row < h; row++)
        memcpy(bank + (size_t)row * SOFT_GPU_WIDTH, d + 4 + (size_t)row * w * 2, (size_t)w * 2);
    free(d);
    return 1;
}

int Gfx_LoadAssets(void)
{
    if (ready) return 1;
    if (!load_atlas()) { LOG("journey: no texture atlas"); return 0; }
    ready = 1;
    return 1;
}

int Gfx_Ready(void) { return ready; }

#define MAX_MESHES 96
#define MESH_VERTS 1024
static struct { char name[28]; Mesh m; } meshes[MAX_MESHES];
static int mesh_count;

static int parse_n2(Mesh *m, const unsigned char *d, long size)
{
    long pos = 12, need;
    int i;
    m->nv = d[4] | d[5] << 8;
    m->nf = d[6] | d[7] << 8;
    m->nframes = d[8] | d[9] << 8;
    m->smooth = 1;
    need = 12 + (long)m->nframes * m->nv * 6 + (long)m->nv * 7 + (long)m->nf * 6;
    if (size < need || m->nv > MESH_VERTS) return 0;
    m->verts = malloc((size_t)m->nframes * m->nv * 6);
    m->nrm = malloc((size_t)m->nv * 3);
    m->slot = malloc((size_t)m->nv);
    m->col = malloc((size_t)m->nv * 3);
    m->faces = malloc((size_t)m->nf * 6);
    memcpy(m->verts, d + pos, (size_t)m->nframes * m->nv * 6);
    pos += (long)m->nframes * m->nv * 6;
    for (i = 0; i < m->nv; i++, pos += 7) {
        m->nrm[i * 3] = (signed char)d[pos];
        m->nrm[i * 3 + 1] = (signed char)d[pos + 1];
        m->nrm[i * 3 + 2] = (signed char)d[pos + 2];
        m->slot[i] = d[pos + 3];
        m->col[i * 3] = d[pos + 4];
        m->col[i * 3 + 1] = d[pos + 5];
        m->col[i * 3 + 2] = d[pos + 6];
    }
    for (i = 0; i < m->nf * 3; i++, pos += 2) m->faces[i] = (unsigned short)(d[pos] | d[pos + 1] << 8);
    return 1;
}

static int parse_npc1(Mesh *m, const unsigned char *d, long size)
{
    const unsigned char *f;
    int i;
    m->nv = d[4] | d[5] << 8;
    m->nf = d[6] | d[7] << 8;
    m->nframes = d[8] | d[9] << 8;
    if (size < 12 + (long)m->nframes * m->nv * 6 + (long)m->nf * 10 || m->nv > MESH_VERTS) return 0;
    m->verts = malloc((size_t)m->nframes * m->nv * 6);
    m->faces = malloc((size_t)m->nf * 6);
    m->col = malloc((size_t)m->nf * 3);
    m->lift = malloc((size_t)m->nf);
    memcpy(m->verts, d + 12, (size_t)m->nframes * m->nv * 6);
    f = d + 12 + (size_t)m->nframes * m->nv * 6;
    for (i = 0; i < m->nf; i++, f += 10) {
        m->faces[i * 3] = (unsigned short)(f[0] | f[1] << 8);
        m->faces[i * 3 + 1] = (unsigned short)(f[2] | f[3] << 8);
        m->faces[i * 3 + 2] = (unsigned short)(f[4] | f[5] << 8);
        m->col[i * 3] = f[6]; m->col[i * 3 + 1] = f[7]; m->col[i * 3 + 2] = f[8];
        m->lift[i] = f[9];
    }
    return 1;
}

Mesh *Gfx_Mesh(const char *name)
{
    char path[64];
    unsigned char *d;
    long size;
    int i;
    for (i = 0; i < mesh_count; i++)
        if (!strcmp(meshes[i].name, name)) return meshes[i].m.nv ? &meshes[i].m : NULL;
    if (mesh_count >= MAX_MESHES) return NULL;
    strncpy(meshes[mesh_count].name, name, sizeof(meshes[0].name) - 1);
    memset(&meshes[mesh_count].m, 0, sizeof(Mesh));
    snprintf(path, sizeof(path), "assets/%s.n2", name);
    d = Jm_Slurp(path, &size);
    if (d && size > 12 && !memcmp(d, "NPC2", 4)) parse_n2(&meshes[mesh_count].m, d, size);
    else {
        free(d);
        snprintf(path, sizeof(path), "assets/%s.bin", name);
        d = Jm_Slurp(path, &size);
        if (d && size > 12 && !memcmp(d, "NPC1", 4)) parse_npc1(&meshes[mesh_count].m, d, size);
    }
    free(d);
    if (!meshes[mesh_count].m.nv) LOG("journey: no mesh %s", name);
    i = mesh_count++;
    return meshes[i].m.nv ? &meshes[i].m : NULL;
}

/* The speaker's portrait, read from the disc into the dynamic slot (48x48, 64 colours + palette). */
#define PORTRAIT_RECORD 0x980
#define FREE_DUEL_PORTRAITS_SECTOR 0x1EAA
int Gfx_LoadFace(int duelist)
{
    static unsigned char sectors[3 * 2048];
    unsigned char *record;
    int offset, x, y;
    u16 *bank = SoftGpu_Bank(BANK);
    const u16 *palette;
    if (!bank || duelist < 0) return 0;
    offset = Duelists_BaseId(duelist) * PORTRAIT_RECORD;
    if (!DiscArt_Read(FREE_DUEL_PORTRAITS_SECTOR + offset / 2048, sectors, (int)sizeof(sectors))) return 0;
    record = sectors + offset % 2048;
    palette = (const u16 *)(record + 0x900);
    for (y = 0; y < 48; y++)
        for (x = 0; x < 48; x++) {
            int index = record[y * 48 + x];
            u16 c = index < 64 ? palette[index] : 0;
            bank[(size_t)(DYN_PORT_Y + y) * SOFT_GPU_WIDTH + DYN_PORT_X + x] = c ? (u16)(c | 0x8000) : 0;
        }
    return 1;
}

/* ---------------------------------------------------------------- camera */
static float PITCH_C = 0.7071f, PITCH_S = 0.7071f;
#define FOCAL 380.0f
#define OFX 160
#define OFY 118

void Gfx_TexXY(int tex, int *ax, int *ay)
{
    if (tex < 16) { *ax = (tex & 3) * 64; *ay = (tex >> 2) * 64; }
    else { *ax = 512 + ((tex - 16) & 3) * 64; *ay = 48 + ((tex - 16) >> 2) * 64; }
}

void Gfx_SetCamera(float distance, float pitch_degrees)
{
    float r = pitch_degrees * 3.14159265f / 180.0f;
    cam_d = distance;
    PITCH_C = cosf(r);
    PITCH_S = sinf(r);
}

int Gfx_Project(float wx, float wy, float wz, float *sx, float *sy, float *depth)
{
    float rx = wx - cam_x, rz = cam_z - wz, z = PITCH_S * wy + PITCH_C * rz + cam_d, y = PITCH_C * wy - PITCH_S * rz;
    if (z < 40.0f) return 0;
    *sx = OFX + rx * FOCAL / z;
    *sy = OFY + y * FOCAL / z;
    *depth = z;
    return 1;
}

/* --------------------------------------------------------------- polygons */
static GsOT *table(void) { return D_800E9D90[1]; }
static unsigned ot_count(void) { return 1u << table()->length; }
static void sort(void *prim, unsigned slot) { GsSortPoly(prim, table(), (unsigned short)(table()->offset + slot)); }

typedef struct { float z; int quad; union { POLY_G3 g3; POLY_GT4 gt4; POLY_FT4 ft4; } p; } Item;   /* quad: 0 triangle, 1 gouraud quad, 2 flat quad */
#define MAX_ITEMS 20000
static Item items[MAX_ITEMS];
static Item *order[MAX_ITEMS];
static int nitems;

static Item *push(float z, int quad)
{
    Item *it;
    if (nitems >= MAX_ITEMS) return NULL;
    it = &items[nitems++];
    it->z = z;
    it->quad = quad;
    memset(&it->p, 0, sizeof(it->p));
    return it;
}

static int by_depth(const void *a, const void *b)
{
    float za = (*(Item *const *)a)->z, zb = (*(Item *const *)b)->z;
    return za < zb ? -1 : za > zb ? 1 : 0;
}

int Gfx_Items(void) { return nitems; }
#define SLOT_SCENE (ot_count() - 8)
#define PACKET_BUDGET 124000     /* ground quads and shadows go straight to the table: they count too */
static int direct_bytes;
void Gfx_End(void)
{
    int i, used = 0;
    for (i = 0; i < nitems; i++) order[i] = &items[i];
    qsort(order, (size_t)nitems, sizeof(order[0]), by_depth);
    /* The game's packet area (GRAPHICS_PACKET_BUFFER_SIZE, 140000 bytes) is shared by the whole frame, and
     * an overflow writes over the next buffer: keep to a budget and leave the farthest polygons out. */
    for (i = 0; i < nitems; i++) {
        used += order[i]->quad == 1 ? 14 * 4 : order[i]->quad == 2 ? 9 * 4 : 7 * 4;
        if (used + direct_bytes > PACKET_BUDGET) break;
    }
    {
        static unsigned calls;
        if (nitems > i && !(calls++ % 120)) LOG("journey: packet budget hit, %d of %d polygons drawn", i, nitems);
        else if (!(calls++ % 240)) LOG("journey: %d polygons, %d bytes of ground and shadows", nitems, direct_bytes);
    }
    nitems = i;
    for (i = 0; i < nitems; i++) sort(&order[i]->p, SLOT_SCENE);
    nitems = 0;
    direct_bytes = 0;
}

static void gt4(POLY_GT4 *p, const float sx[4], const float sy[4], int ax, int ay, int w, int h, const unsigned char rgb[4][3], int flip)
{
    int base = (ax >> 8) << 8, u = ax - base, k;
    int u0 = flip ? u + w - 1 : u, u1 = flip ? u : u + w - 1;
    setPolyGT4(p);
    p->tpage = (u16)(GetTPage(2, 0, base, 0) | (u16)(BANK << 11));
    p->x0 = (short)sx[0]; p->y0 = (short)sy[0]; p->x1 = (short)sx[1]; p->y1 = (short)sy[1];
    p->x2 = (short)sx[2]; p->y2 = (short)sy[2]; p->x3 = (short)sx[3]; p->y3 = (short)sy[3];
    p->u0 = (u8)u0; p->v0 = (u8)ay; p->u1 = (u8)u1; p->v1 = (u8)ay;
    p->u2 = (u8)u0; p->v2 = (u8)(ay + h - 1); p->u3 = (u8)u1; p->v3 = (u8)(ay + h - 1);
    p->r0 = rgb[0][0]; p->g0 = rgb[0][1]; p->b0 = rgb[0][2];
    p->r1 = rgb[1][0]; p->g1 = rgb[1][1]; p->b1 = rgb[1][2];
    p->r2 = rgb[2][0]; p->g2 = rgb[2][1]; p->b2 = rgb[2][2];
    p->r3 = rgb[3][0]; p->g3 = rgb[3][1]; p->b3 = rgb[3][2];
    (void)k;
}

static void ft4(POLY_FT4 *p, const float sx[4], const float sy[4], int ax, int ay, int w, int h, int shade, int flip)
{
    int base = (ax >> 8) << 8, u = ax - base;
    int u0 = flip ? u + w - 1 : u, u1 = flip ? u : u + w - 1;
    setPolyFT4(p);
    p->tpage = (u16)(GetTPage(2, 0, base, 0) | (u16)(BANK << 11));
    p->x0 = (short)sx[0]; p->y0 = (short)sy[0]; p->x1 = (short)sx[1]; p->y1 = (short)sy[1];
    p->x2 = (short)sx[2]; p->y2 = (short)sy[2]; p->x3 = (short)sx[3]; p->y3 = (short)sy[3];
    p->u0 = (u8)u0; p->v0 = (u8)ay; p->u1 = (u8)u1; p->v1 = (u8)ay;
    p->u2 = (u8)u0; p->v2 = (u8)(ay + h - 1); p->u3 = (u8)u1; p->v3 = (u8)(ay + h - 1);
    p->r0 = p->g0 = p->b0 = (u8)shade;
}

void Gfx_GroundQuad(const float sx[4], const float sy[4], int tile, const unsigned char rgb[4][3])
{
    POLY_GT4 p;
    int ax, ay;
    memset(&p, 0, sizeof(p));
    Gfx_TexXY(tile, &ax, &ay);
    gt4(&p, sx, sy, ax, ay, 64, 64, rgb, 0);
    sort(&p, ot_count() - 3);
    direct_bytes += 14 * 4;
}

void Gfx_SceneQuad(const float sx[4], const float sy[4], int ax, int ay, int w, int h, float depth, const unsigned char rgb[4][3], int flip)
{
    Item *it = push(depth, 1);
    if (!it) return;
    gt4(&it->p.gt4, sx, sy, ax, ay, w, h, rgb, flip);
}

void Gfx_SceneTri(float x0, float y0, float x1, float y1, float x2, float y2, const unsigned char c[3][3], float depth)
{
    Item *it = push(depth, 0);
    POLY_G3 *p;
    if (!it) return;
    p = &it->p.g3;
    setPolyG3(p);
    p->r0 = c[0][0]; p->g0 = c[0][1]; p->b0 = c[0][2];
    p->r1 = c[1][0]; p->g1 = c[1][1]; p->b1 = c[1][2];
    p->r2 = c[2][0]; p->g2 = c[2][1]; p->b2 = c[2][2];
    p->x0 = (short)x0; p->y0 = (short)y0; p->x1 = (short)x1; p->y1 = (short)y1; p->x2 = (short)x2; p->y2 = (short)y2;
}

void Gfx_Sprite(float wx, float wz, int ax, int ay, int w, int h, float ww, float wh, int shade, int flip)
{
    float sx[4], sy[4], d0, d1;
    if (!Gfx_Project(wx - ww * 0.5f, -wh, wz, &sx[0], &sy[0], &d0)) return;
    Gfx_Project(wx + ww * 0.5f, -wh, wz, &sx[1], &sy[1], &d1);
    Gfx_Project(wx - ww * 0.5f, 0, wz, &sx[2], &sy[2], &d1);
    Gfx_Project(wx + ww * 0.5f, 0, wz, &sx[3], &sy[3], &d1);
    if (sx[1] < -30 || sx[0] > 350 || sy[3] < -30 || sy[0] > 270) return;
    {   /* a flat quad: 36 bytes of the packet buffer instead of 56 */
        Item *it = push(d1, 2);
        if (!it) return;
        ft4(&it->p.ft4, sx, sy, ax, ay, w, h, shade < 0 ? 0 : shade > 255 ? 255 : shade, flip);
    }
}

void Gfx_Shadow(float wx, float wz, float size)
{
    float sx[4], sy[4], d;
    unsigned char rgb[4][3];
    POLY_GT4 p;
    int k;
    if (!Gfx_Project(wx - size, 0, wz - size * 0.55f, &sx[0], &sy[0], &d)) return;
    Gfx_Project(wx + size, 0, wz - size * 0.55f, &sx[1], &sy[1], &d);
    Gfx_Project(wx - size, 0, wz + size * 0.55f, &sx[2], &sy[2], &d);
    Gfx_Project(wx + size, 0, wz + size * 0.55f, &sx[3], &sy[3], &d);
    for (k = 0; k < 4; k++) rgb[k][0] = rgb[k][1] = rgb[k][2] = 96;
    memset(&p, 0, sizeof(p));
    gt4(&p, sx, sy, SPR_X, 100, 32, 16, rgb, 0);
    sort(&p, ot_count() - 4);
    direct_bytes += 14 * 4;
}

/* A character mesh. Smooth meshes (NPC2) are lit per vertex from a fixed sun; flat ones (props)
 * keep their baked face colours. Triangles facing away are dropped. */
void Gfx_DrawMesh(const Mesh *m, int frame, float wx, float wy, float wz, float yaw, float scale, const int slot_rgb[5], float bias)
{
    static float vx[MESH_VERTS], vy[MESH_VERTS], vz[MESH_VERTS];
    static unsigned char vc[MESH_VERTS][3];
    float cy = cosf(yaw), sy = sinf(yaw);
    int i, nv = m->nv > 640 ? 640 : m->nv;
    const short *v;
    if (!m || !m->verts) return;
    v = m->verts + (size_t)(frame % m->nframes) * m->nv * 3;
    for (i = 0; i < nv; i++) {
        float mx = v[i * 3] * scale, my = v[i * 3 + 1] * scale + wy, mz = v[i * 3 + 2] * scale, zc;
        float dx = cy * mx + sy * mz, dz = cy * mz - sy * mx;
        if (!Gfx_Project(wx + dx, my, wz + dz, &vx[i], &vy[i], &zc)) vz[i] = -1; else vz[i] = zc;
        if (m->smooth) {
            float nx = m->nrm[i * 3] / 127.0f, ny = m->nrm[i * 3 + 1] / 127.0f, nz = m->nrm[i * 3 + 2] / 127.0f;
            float rx = cy * nx + sy * nz, rz = cy * nz - sy * nx, l;
            int r = m->col[i * 3], g = m->col[i * 3 + 1], b = m->col[i * 3 + 2], s = m->slot[i];
            if (slot_rgb && s && slot_rgb[s] >= 0) {
                r = (slot_rgb[s] >> 16) & 255; g = (slot_rgb[s] >> 8) & 255; b = slot_rgb[s] & 255;
            }
            /* sun from the upper left front; the rest is a sky/ground ambient */
            l = 0.40f + 0.55f * lit0(rx * 0.35f - ny * 0.80f + rz * 0.50f) + 0.10f * (-ny);
            r = (int)(r * l * 1.15f); g = (int)(g * l * 1.15f); b = (int)(b * l * 1.15f);
            vc[i][0] = (unsigned char)(r > 255 ? 255 : r < 0 ? 0 : r);
            vc[i][1] = (unsigned char)(g > 255 ? 255 : g < 0 ? 0 : g);
            vc[i][2] = (unsigned char)(b > 255 ? 255 : b < 0 ? 0 : b);
        }
    }
    for (i = 0; i < m->nf; i++) {
        int a = m->faces[i * 3], b = m->faces[i * 3 + 1], c = m->faces[i * 3 + 2];
        unsigned char col[3][3];
        float area;
        if (a >= nv || b >= nv || c >= nv || vz[a] < 0 || vz[b] < 0 || vz[c] < 0) continue;
        area = (vx[b] - vx[a]) * (vy[c] - vy[a]) - (vx[c] - vx[a]) * (vy[b] - vy[a]);
        if (m->smooth && area < 0) continue;
        if (!m->smooth && area == 0) continue;
        if (m->smooth) {
            memcpy(col[0], vc[a], 3); memcpy(col[1], vc[b], 3); memcpy(col[2], vc[c], 3);
        } else {
            int k;
            for (k = 0; k < 3; k++) { col[k][0] = m->col[i * 3]; col[k][1] = m->col[i * 3 + 1]; col[k][2] = m->col[i * 3 + 2]; }
        }
        Gfx_SceneTri(vx[a], vy[a], vx[b], vy[b], vx[c], vy[c], (const unsigned char (*)[3])col,
                     (vz[a] + vz[b] + vz[c]) / 3.0f + bias - (m->lift ? m->lift[i] * 0.5f : 0.0f));
    }
}

void Gfx_Portrait(int x, int y, int size, int ax, int ay)
{
    POLY_GT4 p;
    float sx[4] = {(float)x, (float)(x + size), (float)x, (float)(x + size)};
    float sy[4] = {(float)y, (float)y, (float)(y + size), (float)(y + size)};
    unsigned char rgb[4][3];
    int k;
    for (k = 0; k < 4; k++) rgb[k][0] = rgb[k][1] = rgb[k][2] = 128;
    memset(&p, 0, sizeof(p));
    gt4(&p, sx, sy, ax, ay, 48, 48, rgb, 0);
    sort(&p, 1);
}

void Gfx_Rect(int x, int y, int w, int h, int r, int g, int b)
{
    POLY_G4 p;
    memset(&p, 0, sizeof(p));
    setPolyG4(&p);
    p.r0 = p.r1 = p.r2 = p.r3 = (u8)r; p.g0 = p.g1 = p.g2 = p.g3 = (u8)g; p.b0 = p.b1 = p.b2 = p.b3 = (u8)b;
    p.x0 = (short)x; p.y0 = (short)y; p.x1 = (short)(x + w); p.y1 = (short)y;
    p.x2 = (short)x; p.y2 = (short)(y + h); p.x3 = (short)(x + w); p.y3 = (short)(y + h);
    sort(&p, 2);
}

void Gfx_Backdrop(int top, int bottom)
{
    POLY_G4 p;
    memset(&p, 0, sizeof(p));
    setPolyG4(&p);
    p.r0 = p.r1 = (u8)(top >> 16); p.g0 = p.g1 = (u8)(top >> 8); p.b0 = p.b1 = (u8)top;
    p.r2 = p.r3 = (u8)(bottom >> 16); p.g2 = p.g3 = (u8)(bottom >> 8); p.b2 = p.b3 = (u8)bottom;
    p.x0 = 0; p.y0 = 0; p.x1 = 320; p.y1 = 0; p.x2 = 0; p.y2 = 240; p.x3 = 320; p.y3 = 240;
    sort(&p, ot_count() - 2);
}

void Gfx_Begin(void)
{
    nitems = 0;
    gfx_frame++;
}
