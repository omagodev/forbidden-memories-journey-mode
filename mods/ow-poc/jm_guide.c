/* The objective guide: where to go next, drawn as a marker over the target, an arrow at the screen
 * edge when it is out of view, a compass arrow around the player, and the data for the maps.
 *
 * journey.json "guide" is a list of rules like the objectives: the first whose "when" holds names the
 * target, one of {"npc": id}, {"tile": [x, z]}, {"rect": [x0, z0, x1, z1]} (tiles).  The way there is a
 * breadth-first search over the walkable tiles; a trigger that has a "rect" and a "teleport" (the pads
 * between the rooms) is an edge of that search, so the guide leads to the next warp pad when the target
 * is in another room. */
#include "types.h"
#include "jm.h"
#include <math.h>
#include <stdlib.h>
#include <string.h>

int jm_guide_on;

#define NODES (MW * MH)
static short from[NODES];                  /* index of the tile before, -1 none, -2 start */
static unsigned char seen[NODES];
static int queue[NODES];
static int jump[NODES];                    /* teleport edge: destination tile index + 1, 0 none */

static int rule = -1;                      /* index of the active guide rule, -1 none */
static int have;                           /* a target exists */
static int goal_tile = -1;                 /* the tile the search ended on */
static float goal_x, goal_z;               /* world position of the target */
static float way_x, way_z;                 /* the point to walk to next: a few tiles along the path */
static int way_pad;                        /* the next step is a warp pad */
static unsigned last_sig = ~0u;
static int last_tile = -1, last_frame;

static int tile_ok(int tx, int tz) { return tx >= 0 && tz >= 0 && tx < MW && tz < MH && !World_Solid(tx * TS + TS / 2.0f, tz * TS + TS / 2.0f); }

/* The rule that holds now, and its goal test for a tile. */
static const JsonNode *current_rule(int *index)
{
    JsonNode *list = Json_Get(jm_rules, "guide"), *n;
    int i = 0;
    for (n = list ? list->child : NULL; n; n = n->next, i++) {
        const char *id = Json_Str(n, "npc", NULL);
        if (!Story_Cond(Json_Get(n, "when"))) continue;
        if (id) {
            int k;
            for (k = 0; k < npc_count; k++) if (!strcmp(npcs[k].id, id) && !npcs[k].hidden) break;
            if (k == npc_count) continue;
        }
        *index = i;
        return n;
    }
    *index = -1;
    return NULL;
}

static int at_goal(const JsonNode *r, int tx, int tz)
{
    const char *id = Json_Str(r, "npc", NULL);
    JsonNode *rc = Json_Get(r, "rect");
    JsonNode *tl = Json_Get(r, "tile");
    if (id) {
        int k;
        for (k = 0; k < npc_count; k++)
            if (!strcmp(npcs[k].id, id) && !npcs[k].hidden) {
                float dx = tx * TS + TS / 2.0f - npcs[k].x, dz = tz * TS + TS / 2.0f - npcs[k].z;
                return dx * dx + dz * dz < 62.0f * 62.0f;
            }
        return 0;
    }
    if (rc) return tx >= (int)Json_At(rc, 0)->num && tz >= (int)Json_At(rc, 1)->num && tx <= (int)Json_At(rc, 2)->num && tz <= (int)Json_At(rc, 3)->num;
    if (tl) { int x = (int)Json_At(tl, 0)->num, z = (int)Json_At(tl, 1)->num; return tx == x && tz == z; }
    return 0;
}

static void build_jumps(void)
{
    JsonNode *list = Json_Get(jm_rules, "triggers"), *n;
    memset(jump, 0, sizeof(jump));
    for (n = list ? list->child : NULL; n; n = n->next) {
        JsonNode *rc = Json_Get(n, "rect"), *tp = Json_Get(n, "teleport");
        int x, z, d;
        if (!rc || !tp || !Story_Cond(Json_Get(n, "when"))) continue;
        d = (int)floorf((float)Json_At(tp, 1)->num) * MW + (int)floorf((float)Json_At(tp, 0)->num);
        for (z = (int)Json_At(rc, 1)->num; z <= (int)Json_At(rc, 3)->num; z++)
            for (x = (int)Json_At(rc, 0)->num; x <= (int)Json_At(rc, 2)->num; x++)
                if (x >= 0 && z >= 0 && x < MW && z < MH) jump[z * MW + x] = d + 1;
    }
}

static void search(const JsonNode *r)
{
    int start = (int)(jm.z / TS) * MW + (int)(jm.x / TS), head = 0, tail = 0, found = -1, i;
    static const int dx[4] = {1, -1, 0, 0}, dz[4] = {0, 0, 1, -1};
    if (start < 0 || start >= NODES) { have = 0; return; }
    memset(seen, 0, sizeof(seen));
    build_jumps();
    queue[tail++] = start;
    seen[start] = 1;
    from[start] = -2;
    while (head < tail) {
        int cur = queue[head++], cx = cur % MW, cz = cur / MW, k;
        if (at_goal(r, cx, cz)) { found = cur; break; }
        if (jump[cur] && !seen[jump[cur] - 1]) { seen[jump[cur] - 1] = 1; from[jump[cur] - 1] = (short)cur; queue[tail++] = jump[cur] - 1; }
        for (k = 0; k < 4; k++) {
            int nx = cx + dx[k], nz = cz + dz[k], ni = nz * MW + nx;
            if (!tile_ok(nx, nz) || seen[ni]) continue;
            seen[ni] = 1;
            from[ni] = (short)cur;
            queue[tail++] = ni;
        }
    }
    have = found >= 0;
    if (!have) return;
    goal_tile = found;
    goal_x = (found % MW) * TS + TS / 2.0f;
    goal_z = (found / MW) * TS + TS / 2.0f;
    {   /* the target itself is a person: mark him, not the tile next to him */
        const char *id = Json_Str(r, "npc", NULL);
        if (id)
            for (i = 0; i < npc_count; i++)
                if (!strcmp(npcs[i].id, id) && !npcs[i].hidden) { goal_x = npcs[i].x; goal_z = npcs[i].z; }
    }
    /* walk the path from the goal back; keep the tile 9 steps from the start, or the first pad */
    {
        int path[NODES / 4 + 8], n = 0, cur = found;
        while (cur >= 0 && n < NODES / 4) { path[n++] = cur; cur = from[cur] == -2 ? -1 : from[cur]; }
        /* path[n - 1] is the start */
        way_pad = 0;
        way_x = goal_x;
        way_z = goal_z;
        for (i = n - 1; i >= 0; i--) {
            int idx = n - 1 - i;
            if (jump[path[i]] && i > 0 && path[i - 1] == jump[path[i]] - 1) {
                way_x = (path[i] % MW) * TS + TS / 2.0f;
                way_z = (path[i] / MW) * TS + TS / 2.0f;
                way_pad = 1;
                break;
            }
            if (idx >= 9 || i == 0) {
                if (i > 0) { way_x = (path[i] % MW) * TS + TS / 2.0f; way_z = (path[i] / MW) * TS + TS / 2.0f; }
                break;
            }
        }
    }
}

void Guide_Update(void)
{
    int tile = (int)(jm.z / TS) * MW + (int)(jm.x / TS);
    unsigned sig = (unsigned)jm.stage * 2654435761u ^ jm.flags * 40503u ^ (unsigned)npc_count;
    const JsonNode *r;
    int idx;
    if (sig == last_sig && tile == last_tile) return;
    if (sig == last_sig && gfx_frame - last_frame < 8) return;
    last_sig = sig;
    last_tile = tile;
    last_frame = (int)gfx_frame;
    r = current_rule(&idx);
    rule = idx;
    if (!r) { have = 0; return; }
    search(r);
}

void Guide_Reset(void) { last_sig = ~0u; last_tile = -1; have = 0; }

int Guide_Target(float *x, float *z, float *wx, float *wz)
{
    if (!have) return 0;
    *x = goal_x; *z = goal_z; *wx = way_x; *wz = way_z;
    return 1;
}

/* ---------------------------------------------------------------- drawing */
static void col3(unsigned char c[3][3], int r, int g, int b)
{
    int k;
    for (k = 0; k < 3; k++) { c[k][0] = (unsigned char)r; c[k][1] = (unsigned char)g; c[k][2] = (unsigned char)b; }
}

static void tri(float x0, float y0, float x1, float y1, float x2, float y2, int r, int g, int b, float depth)
{
    unsigned char c[3][3];
    col3(c, r, g, b);
    Gfx_SceneTri(x0, y0, x1, y1, x2, y2, c, depth);
}

/* An arrow with its tip at (x, y) pointing along (dx, dy), size s. */
static void arrow(float x, float y, float dx, float dy, float s, int pulse)
{
    float px = -dy, py = dx;
    float bx = x - dx * s * 1.6f, by = y - dy * s * 1.6f;
    int a = 200 + pulse;
    tri(x + dx * 1.5f, y + dy * 1.5f, bx + px * (s * 1.0f + 1.5f), by + py * (s * 1.0f + 1.5f), bx - px * (s * 1.0f + 1.5f), by - py * (s * 1.0f + 1.5f), 20, 16, 8, 0.5f);
    tri(x, y, bx + px * s, by + py * s, bx - px * s, by - py * s, a, a * 3 / 4 > 255 ? 255 : a * 3 / 4, 30, 0.4f);
}

void Guide_Draw(float pxw, float pzw)
{
    float gx, gz, wx, wz, sx, sy, d, psx, psy;
    float t = (float)gfx_frame;
    int pulse = (int)(50.0f * (0.5f + 0.5f * sinf(t * 0.16f)));
    if (!have || !Gfx_Project(pxw, 0, pzw, &psx, &psy, &d)) return;
    if (!Guide_Target(&gx, &gz, &wx, &wz)) return;
    {   /* compass: a flat arrow on the ground around the player, toward the next waypoint */
        float dx = wx - pxw, dz = wz - pzw, l = sqrtf(dx * dx + dz * dz);
        if (l > 70.0f) {
            float ux = dx / l, uz = dz / l, ax, ay, bx, by, cx, cy, e;
            float r0 = 34.0f, r1 = 58.0f + 4.0f * sinf(t * 0.2f);
            if (Gfx_Project(pxw + ux * r1, 0, pzw + uz * r1, &ax, &ay, &e) &&
                Gfx_Project(pxw + ux * r0 - uz * 11.0f, 0, pzw + uz * r0 + ux * 11.0f, &bx, &by, &e) &&
                Gfx_Project(pxw + ux * r0 + uz * 11.0f, 0, pzw + uz * r0 - ux * 11.0f, &cx, &cy, &e)) {
                tri(ax, ay, bx, by, cx, cy, 255, 210 + pulse / 4, 40, d - 20.0f);
            }
        }
    }
    /* marker over the target (or over the next pad) when it is on the screen; arrow at the edge when not */
    {
        float tx = way_pad ? wx : gx, tz = way_pad ? wz : gz;
        int on = Gfx_Project(tx, -96.0f, tz, &sx, &sy, &d);
        if (on && sx > 12 && sx < 308 && sy > 34 && sy < 200) {
            float bob = 4.0f * sinf(t * 0.18f);
            float y = sy + bob;
            tri(sx, y + 1.0f, sx - 9.5f, y - 15.0f, sx + 9.5f, y - 15.0f, 20, 14, 6, 0.6f);
            tri(sx, y, sx - 7, y - 13, sx + 7, y - 13, 255, 200 + pulse / 2, 40, 0.5f);
            tri(sx, y - 3, sx - 3.5f, y - 10, sx + 3.5f, y - 10, 255, 250, 200, 0.4f);
        } else {
            float cx = 160, cy = 118, dx, dy, l, sc, hx = 138, hy = 74, ex, ey;
            float ox, oy, e;
            if (!Gfx_Project(tx, 0, tz, &ox, &oy, &e)) { ox = cx; oy = cy - 100; }
            dx = ox - psx; dy = oy - psy;
            l = sqrtf(dx * dx + dy * dy);
            if (l < 1.0f) return;
            dx /= l; dy /= l;
            sc = 1e9f;
            if (dx > 0.001f || dx < -0.001f) sc = hx / fabsf(dx);
            if (dy > 0.001f || dy < -0.001f) { float s2 = hy / fabsf(dy); if (s2 < sc) sc = s2; }
            ex = cx + dx * sc; ey = cy + dy * sc;
            arrow(ex, ey, dx, dy, 8.0f, pulse);
        }
    }
}
