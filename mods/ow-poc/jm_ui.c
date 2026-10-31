/* Journey Mode screens: character creation and the START menu.  They are drawn with the port's
 * overlay (its menu font and panels) over the 3D picture, and the name is typed on the game's own
 * name-entry screen (main mode 9), which writes the name the whole port shows for the player. */
#include "types.h"
#include "jm.h"
#include <math.h>
#include <stdio.h>
#include <string.h>
#include <stdint.h>

extern uint16_t *SoftGpu_Bank(int bank);
extern const char *HdText_PlayerName(void);

/* ---------------------------------------------------------------- helpers */
static int ui_w, ui_h, ui_s, ui_top, ui_vis;
/* The canvas is as wide as the window and taller than it, cropped top and bottom: keep to its middle 16:9. */
static void metrics(void)
{
    jm_host->overlay_size(jm_host, &ui_w, &ui_h, &ui_s);
    if (ui_s < 2) ui_s = 2;
    ui_vis = ui_w * 9 / 16;
    if (ui_vis > ui_h) ui_vis = ui_h;
    ui_top = (ui_h - ui_vis) / 2;
}

static void panel(int x, int y, int w, int h)
{
    jm_host->fill(jm_host, x, y, w, h, 0x0C0E2C, 215);
    jm_host->fill(jm_host, x, y, w, 2 * ui_s, 0xC8A03C, 255);
    jm_host->fill(jm_host, x, y + h - 2 * ui_s, w, 2 * ui_s, 0xC8A03C, 255);
    jm_host->fill(jm_host, x, y, 2 * ui_s, h, 0xC8A03C, 255);
    jm_host->fill(jm_host, x + w - 2 * ui_s, y, 2 * ui_s, h, 0xC8A03C, 255);
}

static int line_h(void) { return 16 * ui_s + 4; }
static void text(int x, int row_y, const char *s, unsigned rgb) { jm_host->draw_text(jm_host, x, row_y, s, rgb, ui_s); }

/* The same panel, font and metrics for a screen of another file (the shop). */
void Ui_Metrics(int *w, int *h, int *scale, int *top, int *vis)
{
    metrics();
    if (w) *w = ui_w;
    if (h) *h = ui_h;
    if (scale) *scale = ui_s;
    if (top) *top = ui_top;
    if (vis) *vis = ui_vis;
}
void Ui_Panel(int x, int y, int w, int h) { panel(x, y, w, h); }
/* `tmpl` with its first "%d" replaced by `value`.  Translated text with one number in it goes through
 * here rather than printf, so a translation with the wrong specifier reads oddly instead of crashing. */
void Ui_Fmt1(char *out, size_t size, const char *tmpl, int value)
{
    const char *at = strstr(tmpl, "%d");
    size_t head;
    if (!at) { snprintf(out, size, "%s", tmpl); return; }
    head = (size_t)(at - tmpl);
    if (head >= size - 1) head = size - 1;
    memcpy(out, tmpl, head);
    snprintf(out + head, size - head, "%d%s", value, at + 2);
}
int Ui_LineH(void) { return line_h(); }
void Ui_Text(int x, int row_y, const char *s, unsigned rgb) { text(x, row_y, s, rgb); }

char ui_message[48];
int ui_message_timer;
static unsigned message_rgb = 0x60F060;
void Ui_Message(const char *s) { Ui_MessageTone(s, 0x60F060); }
/* The same line in another colour: gold for a level up, red for a warning. */
void Ui_MessageTone(const char *s, unsigned rgb)
{
    strncpy(ui_message, s, sizeof(ui_message) - 1);
    ui_message[sizeof(ui_message) - 1] = 0;
    message_rgb = rgb;
    ui_message_timer = 120;
}
const char *Ui_MessageText(void) { return ui_message_timer > 0 ? ui_message : NULL; }
unsigned Ui_MessageColour(void) { return message_rgb; }

/* -------------------------------------------------------- character creator
 * Four steps (Base, Appearance, Name, Confirm) in the layout of a modern creator: a top bar with the step tracker, the bases on the left
 * with the small in-game sprite, the assembled hero big in the middle on a glowing ring, the tabs (Hair, Outfit, Colour, Accessories) with
 * an option grid and colour swatches on the right, Back / Next at the bottom with small key hints.  Everything is drawn in the overlay
 * from the texels themselves (the composed hero page, the portraits, the LPC sheet), nearest-neighbour, so it is crisp at any window size.
 * Keys (keyboard default): arrows move, Q / E (L1 / L2, also W = R1) switch tabs, X or Enter = next, S (Circle) = back, R (R2) turns the
 * sprite, Z (Square) switches the big view between sprite and portrait. */
enum { C_HAIR, C_HAIR_COL, C_SKIN, C_OUTFIT, C_ROWS };
enum { CG_SKIN_, CG_OUTFIT_, CG_OUTFIT_COL_, CG_HAIR_, CG_HAIR_COL_, CG_ACC_, CG_ACC_COL_ };   /* jm_chargen.c's category order */
enum { STEP_BASE, STEP_LOOK, STEP_NAME, STEP_CONFIRM, STEP_N };
enum { TAB_HAIR, TAB_OUTFIT, TAB_COLOUR, TAB_ACC, TAB_N };
#define GRID_COLS 4
#define GRID_ROWS 2
static int step, tab, sect, base_sect, view_portrait, turn_dir, done_mask;
static int cg_t;
static unsigned cg_sig = ~0u;                 /* the choice the hero page was composed for */
extern int jm_name_entry_requested;

static const int HAIR_RGB[5] = {0x5A2A78, 0x1C1C22, 0x6A4020, 0xE0C050, 0xB82818};
static const int SKIN_RGB[3] = {0xEBBE96, 0xBE8C64, 0x785032};
static const int OUTFIT_RGB[5] = {0x3246AA, 0xAA2828, 0x287838, 0x2C2C34, 0xC8C8CE};

void Ui_BodyColours(int out[5])
{
    int o = OUTFIT_RGB[jm.outfit % 5];
    out[0] = -1;
    out[1] = SKIN_RGB[jm.skin % 3];
    out[2] = HAIR_RGB[jm.hair_col % 5];
    out[3] = o;
    out[4] = ((o >> 16 & 255) * 5 / 11) << 16 | ((o >> 8 & 255) * 5 / 11) << 8 | ((o & 255) * 5 / 11);
}

const char *Ui_BodyMesh(void)
{
    static const char *const male[3] = {"Casual_Male", "Casual2_Male", "Casual3_Male"};
    static const char *const female[3] = {"Casual_Female", "Casual2_Female", "Casual3_Female"};
    return jm.gender ? female[jm.hair % 3] : male[jm.hair % 3];
}

/* the tabs with data, and the sections of each: a style grid (or none) then the colour rows */
static int tab_grid(int t) { return t == TAB_HAIR ? CG_HAIR_ : t == TAB_OUTFIT ? CG_OUTFIT_ : t == TAB_ACC ? CG_ACC_ : -1; }
static int tab_cols(int t, int out[4])
{
    int n = 0;
    if (t == TAB_HAIR) out[n++] = CG_HAIR_COL_;
    else if (t == TAB_OUTFIT) out[n++] = CG_OUTFIT_COL_;
    else if (t == TAB_ACC) { if (Cg_OptCount(CG_ACC_COL_) > 0) out[n++] = CG_ACC_COL_; }
    else { out[n++] = CG_SKIN_; out[n++] = CG_HAIR_COL_; out[n++] = CG_OUTFIT_COL_; if (Cg_OptCount(CG_ACC_COL_) > 0) out[n++] = CG_ACC_COL_; }
    return n;
}
static int tab_has(int t) { int c[4]; return Cg_Ready() && ((tab_grid(t) >= 0 && Cg_OptCount(tab_grid(t)) > 0) || tab_cols(t, c) > 0); }
static int grid_rows_of(int t) { int g = tab_grid(t), n = g >= 0 ? Cg_OptCount(g) : 0, r; if (!n) return 0; r = (n + GRID_COLS - 1) / GRID_COLS; return r; }
/* sections of the tab: rows of the grid first (one section per grid row), then each colour row */
static int sect_count(void) { int c[4]; return grid_rows_of(tab) + tab_cols(tab, c); }
static int sect_cat(int s, int *is_grid)
{
    int c[4], gr = grid_rows_of(tab), n = tab_cols(tab, c);
    if (s < gr) { *is_grid = 1; return tab_grid(tab); }
    *is_grid = 0;
    s -= gr;
    return s >= 0 && s < n ? c[s] : -1;
}

void Ui_StartCreate(void)
{
    step = STEP_BASE; tab = TAB_HAIR; sect = 0; base_sect = 0; view_portrait = 0; turn_dir = 0; done_mask = 0;
    cg_t = 0;
    cg_sig = ~0u;
    Cg_Defaults();
    if (Cg_Ready()) Cg_SetStyle(0);           /* the creator customises the layered hero; the LPC sprite stays one choice away on Base */
    while (!tab_has(tab) && tab < TAB_N - 1) tab++;
}

static void set_cat(int c, int v, int d)
{
    int tries = Cg_OptCount(c);
    Cg_Set(c, v);
    while (Cg_Avoided() && tries-- > 0) Cg_Set(c, Cg_Get(c) + d);        /* skip hair + accessory pairs the art marks as clashing */
    cg_t = 0;
}

static void change_tab(int d)
{
    int k;
    for (k = 0; k < TAB_N; k++) { tab = (tab + d + TAB_N) % TAB_N; if (tab_has(tab)) break; }
    sect = 0;
}

static int look_input(unsigned short edge)
{
    int is_grid, c, n, v;
    if (edge & (PAD_L1)) change_tab(-1);
    if (edge & (PAD_R1 | PAD_L2)) change_tab(1);
    n = sect_count();
    if (!n) return 0;
    if (sect >= n) sect = n - 1;
    c = sect_cat(sect, &is_grid);
    if (c < 0) return 0;
    v = Cg_Get(c);
    if (is_grid) {
        int cnt = Cg_OptCount(c), gr = grid_rows_of(tab);
        if (edge & PAD_LEFT) set_cat(c, (v + cnt - 1) % cnt, -1);
        if (edge & PAD_RIGHT) set_cat(c, (v + 1) % cnt, 1);
        if (edge & PAD_UP) { if (v - GRID_COLS >= 0) { set_cat(c, v - GRID_COLS, -1); sect = (v - GRID_COLS) / GRID_COLS; } }
        if (edge & PAD_DOWN) {
            if (v + GRID_COLS < cnt) { set_cat(c, v + GRID_COLS, 1); sect = (v + GRID_COLS) / GRID_COLS; }
            else if (n > gr) sect = gr;
        }
        if (is_grid && sect < gr) sect = Cg_Get(c) / GRID_COLS;     /* the grid section follows the selected tile */
    } else {
        int cnt = Cg_OptCount(c), gr = grid_rows_of(tab);
        if (cnt > 0 && (edge & PAD_LEFT)) set_cat(c, (v + cnt - 1) % cnt, -1);
        if (cnt > 0 && (edge & PAD_RIGHT)) set_cat(c, (v + 1) % cnt, 1);
        if (edge & PAD_UP) { if (sect > gr) sect--; else if (gr) sect = Cg_Get(tab_grid(tab)) / GRID_COLS; }
        if (edge & PAD_DOWN) { if (sect < n - 1) sect++; }
    }
    return 0;
}

static void base_input(unsigned short edge)
{
    int d = edge & PAD_LEFT ? -1 : edge & PAD_RIGHT ? 1 : 0;
    if (edge & PAD_UP) base_sect = (base_sect + 2) % 3;
    if (edge & PAD_DOWN) base_sect = (base_sect + 1) % 3;
    if (!d) return;
    if (base_sect == 0) jm.portrait = (jm.portrait + d + 4) % 4;
    else if (base_sect == 1) jm.gender ^= 1;
    else if (Cg_Ready()) { Cg_SetStyle(!Cg_Style()); cg_t = 0; }
}

/* 1 = begin the journey, 2 = back to the title */
int Ui_CreateInput(unsigned short edge)
{
    if (edge & PAD_R2) turn_dir = (turn_dir + 1) & 3;
    if (edge & PAD_SQUARE) view_portrait ^= 1;
    if (edge & PAD_CIRCLE) {
        if (step == STEP_BASE) return 2;
        step--;
        return 0;
    }
    switch (step) {
    case STEP_BASE: base_input(edge); break;
    case STEP_LOOK: look_input(edge); break;
    case STEP_NAME:
        if (edge & PAD_CROSS) { jm_name_entry_requested = 1; return 0; }
        break;
    case STEP_CONFIRM:
        if (edge & (PAD_CROSS | PAD_START)) {
            if (jm.name[0]) return 1;
            step = STEP_NAME;
            return 0;
        }
        break;
    }
    if ((edge & PAD_START) || ((edge & PAD_CROSS) && step != STEP_NAME)) {
        if (step == STEP_NAME && !jm.name[0]) { jm_name_entry_requested = 1; return 0; }
        done_mask |= 1 << step;
        if (step < STEP_CONFIRM) step++;
        if (step == STEP_LOOK && !tab_has(tab)) change_tab(1);
    }
    return 0;
}

void Ui_RefreshName(void)
{
    const char *n = HdText_PlayerName();
    if (n && n[0]) { strncpy(jm.name, n, sizeof(jm.name) - 1); jm.name[sizeof(jm.name) - 1] = 0; }
}

/* In the frame hook: a dim backdrop, and the hero's page composed when the choice changed.  The rest is the overlay. */
void Ui_DrawCreate(void)
{
    cg_t++;
    Gfx_Backdrop(0x0A0A22, 0x1E1642);
    if (Cg_Ready() && cg_sig != Cg_Signature()) {
        Cg_Compose(13, 2);
        cg_sig = Cg_Signature();
        LOG("journey: creator look %d %d %d %d %d %d %d", jm.cg[0], jm.cg[1], jm.cg[2], jm.cg[3], jm.cg[4], jm.cg[5], jm.cg[6]);
    }
    Gfx_End();
}

/* ------------------------------------------------ overlay drawing for the creator */
static int DX(int v) { return v * ui_w / 1280; }
static int DY(int v) { return ui_top + v * ui_vis / 720; }
static int DS(int v) { int r = v * ui_vis / 720; return r < 1 ? 1 : r; }
static void fillr(int x, int y, int w, int h, unsigned rgb, unsigned a) { jm_host->fill(jm_host, x, y, w, h, rgb, a); }
static void frame_r(int x, int y, int w, int h, int t, unsigned rgb, unsigned a)
{
    fillr(x, y, w, t, rgb, a); fillr(x, y + h - t, w, t, rgb, a);
    fillr(x, y + t, t, h - 2 * t, rgb, a); fillr(x + w - t, y + t, t, h - 2 * t, rgb, a);
}
/* a dark navy panel with a thin gold border and cut corners */
static void cpanel(int x, int y, int w, int h, int strong)
{
    int c = DS(6), t = DS(strong ? 2 : 1);
    fillr(x + c, y, w - 2 * c, h, 0x12133A, 228);
    fillr(x, y + c, c, h - 2 * c, 0x12133A, 228);
    fillr(x + w - c, y + c, c, h - 2 * c, 0x12133A, 228);
    fillr(x + c, y, w - 2 * c, t, 0xC8A03C, strong ? 255 : 170);
    fillr(x + c, y + h - t, w - 2 * c, t, 0xC8A03C, strong ? 255 : 170);
    fillr(x, y + c, t, h - 2 * c, 0xC8A03C, strong ? 255 : 170);
    fillr(x + w - t, y + c, t, h - 2 * c, 0xC8A03C, strong ? 255 : 170);
    {
        int k;
        for (k = 0; k < c; k++) {                     /* the diagonal corners */
            fillr(x + c - k, y + k, t, t, 0xC8A03C, strong ? 255 : 170);
            fillr(x + w - c + k - t, y + k, t, t, 0xC8A03C, strong ? 255 : 170);
            fillr(x + c - k, y + h - k - t, t, t, 0xC8A03C, strong ? 255 : 170);
            fillr(x + w - c + k - t, y + h - k - t, t, t, 0xC8A03C, strong ? 255 : 170);
        }
    }
}
static int tw(const char *s, int sc) { return jm_host->text_width(jm_host, s, sc); }
static int small_s(void) { return ui_s > 2 ? ui_s - 1 : ui_s; }
static void text_c(int cx, int my, const char *s, unsigned rgb, int sc) { jm_host->draw_text(jm_host, cx - tw(s, sc) / 2, my, s, rgb, sc); }
static void text_fit(int x, int my, int maxw, const char *s, unsigned rgb, int sc)       /* shrinks, then cuts, a label to a width */
{
    char b[64];
    size_t n;
    while (sc > 1 && tw(s, sc) > maxw) sc--;
    snprintf(b, sizeof(b), "%s", s);
    n = strlen(b);
    while (n > 1 && tw(b, sc) > maxw) b[--n] = 0;
    jm_host->draw_text(jm_host, x, my, b, rgb, sc);
}
static unsigned rgb555(uint16_t v) { return ((v & 31) * 255 / 31) << 16 | ((v >> 5 & 31) * 255 / 31) << 8 | ((v >> 10 & 31) * 255 / 31); }
/* texels (stride 1024, 0 = clear) at an integer zoom, one fill per run of equal texels */
static void blit(const uint16_t *src, int w, int h, int dx, int dy, int z)
{
    int y, x;
    if (!src) return;
    for (y = 0; y < h; y++) {
        const uint16_t *r = src + (size_t)y * 1024;
        for (x = 0; x < w;) {
            int x1 = x + 1;
            if (!(r[x] & 0x7FFF) && !(r[x] & 0x8000)) { x++; continue; }
            while (x1 < w && r[x1] == r[x]) x1++;
            fillr(dx + x * z, dy + y * z, (x1 - x) * z, z, rgb555(r[x]), 255);
            x = x1;
        }
    }
}
/* the drawn rows of a sprite frame (its top and bottom), for framing a crop */
static void bounds(const uint16_t *src, int w, int h, int *top, int *bot)
{
    int y, x;
    *top = h; *bot = 0;
    for (y = 0; y < h; y++) for (x = 0; x < w; x++) if (src[(size_t)y * 1024 + x]) { if (y < *top) *top = y; *bot = y; break; }
    if (*top > *bot) { *top = 0; *bot = h - 1; }
}
static void check_mark(int x, int y, int sz)
{
    int k, t = sz / 6 < 1 ? 1 : sz / 6;
    fillr(x, y, sz, sz, 0xE8C050, 255);
    for (k = 0; k < sz / 3; k++) fillr(x + sz / 5 + k, y + sz / 2 + k - t, t, t * 2, 0x1A1430, 255);
    for (k = 0; k < sz / 2; k++) fillr(x + sz / 5 + sz / 3 + k, y + sz / 2 + sz / 3 - k - t * 2, t, t * 2, 0x1A1430, 255);
}
static void glow_ellipse(int cx, int cy, int rx, int ry, unsigned rgb, unsigned a)
{
    int y;
    for (y = -ry; y <= ry; y++) {
        float f = 1.0f - (float)(y * y) / (float)(ry * ry);
        int hw = (int)(rx * sqrtf(f > 0 ? f : 0));
        if (hw > 0) fillr(cx - hw, cy + y, hw * 2, 1, rgb, a);
    }
}
static const uint16_t *hero_frame(int dir, int fr) { uint16_t *b = SoftGpu_Bank(13); return b ? b + (size_t)(dir * 64) * 1024 + 512 + fr * 48 : NULL; }
static const uint16_t *portrait_px(int i) { uint16_t *b = SoftGpu_Bank(BANK); return b ? b + (size_t)PORT_Y * 1024 + PORT_X + (i & 3) * 48 : NULL; }

/* option tiles: the hero composed with that option, cached per look */
#define TILE_MAX 16
static uint16_t tile_scratch[1024 * 256];
static struct { unsigned sig; int ok; uint16_t px[62][48]; } tiles[TILE_MAX];
static const uint16_t *tile_of(int c, int o, int slot)
{
    unsigned char keep[8];
    unsigned sig;
    int y;
    if (slot < 0 || slot >= TILE_MAX) return NULL;
    memcpy(keep, jm.cg, sizeof(keep));
    jm.cg[c] = (unsigned char)o;
    if (c == CG_OUTFIT_ || c == CG_ACC_) jm.cg[c + 1] = keep[c] == o ? keep[c + 1] : 0;
    sig = Cg_Signature() * 7u + (unsigned)c;
    if (!tiles[slot].ok || tiles[slot].sig != sig) {
        memset(tile_scratch, 0, sizeof(tile_scratch));
        Cg_ComposeTo(tile_scratch);
        for (y = 0; y < 62; y++) memcpy(tiles[slot].px[y], tile_scratch + (size_t)y * 1024, 48 * sizeof(uint16_t));
        tiles[slot].sig = sig; tiles[slot].ok = 1;
    }
    memcpy(jm.cg, keep, sizeof(keep));
    return &tiles[slot].px[0][0];
}
/* a tile's texels are 48 wide, not 1024: blit with stride 48 */
static void blit48(const uint16_t *src, int x0, int w, int y0, int h, int dx, int dy, int z)
{
    int y, x;
    for (y = 0; y < h; y++) {
        const uint16_t *r = src + (size_t)(y0 + y) * 48 + x0;
        for (x = 0; x < w;) {
            int x1 = x + 1;
            if (!r[x]) { x++; continue; }
            while (x1 < w && r[x1] == r[x]) x1++;
            fillr(dx + x * z, dy + y * z, (x1 - x) * z, z, rgb555(r[x]), 255);
            x = x1;
        }
    }
}

static void key_cap(int *x, int my, const char *key, const char *label)
{
    int ss = small_s(), kw = tw(key, ss) + DS(12), kh = DS(24);
    fillr(*x, my - kh / 2, kw, kh, 0x2A2C5A, 255);
    frame_r(*x, my - kh / 2, kw, kh, 1, 0x9090C0, 255);
    text_c(*x + kw / 2, my, key, 0xFFFFFF, ss);
    *x += kw + DS(6);
    jm_host->draw_text(jm_host, *x, my, label, 0xB8B8D8, ss);
    *x += tw(label, ss) + DS(18);
}
static int keys_width(const char *const *k, int n)
{
    int ss = small_s(), w = 0, i;
    for (i = 0; i < n; i++) w += tw(k[2 * i], ss) + DS(12) + DS(6) + tw(k[2 * i + 1], ss) + DS(18);
    return w;
}

static void draw_top(void)
{
    int i, ss = small_s();
    fillr(0, DY(0), ui_w, DY(84) - DY(0), 0x080820, 200);
    fillr(0, DY(84), ui_w, DS(2), 0xC8A03C, 200);
    jm_host->draw_text(jm_host, DX(40), DY(30), Tr("creation.v2.title"), 0xFFE9A0, ui_s);
    jm_host->draw_text(jm_host, DX(42), DY(62), Tr("creation.v2.subtitle"), 0x9AA0D0, ss);
    for (i = 0; i < STEP_N; i++) {
        int cx = DX(780 + i * 135), cy = DY(30), r = DS(15);
        unsigned col = i == step ? 0xE8C050 : (done_mask >> i & 1) ? 0xC8C8E0 : 0x6A6C98;
        char n[4];
        if (i < STEP_N - 1) fillr(cx + r + DS(4), cy, DX(135) - 2 * r - DS(8), DS(2), (done_mask >> i & 1) ? 0xC8A03C : 0x44466E, 255);
        glow_ellipse(cx, cy, r, r, col, 255);
        glow_ellipse(cx, cy, r - DS(3), r - DS(3), i == step ? 0x3A2A10 : 0x14153C, 255);
        if ((done_mask >> i & 1) && i != step) check_mark(cx - DS(8), cy - DS(8), DS(16));
        else { snprintf(n, sizeof(n), "%d", i + 1); text_c(cx, cy, n, col, ss); }
        text_c(cx, DY(64), TrAt("creation.v2.steps", i, "?"), i == step ? 0xFFE9A0 : 0x9A9CC8, ss);
    }
}

static void draw_left(void)
{
    int x = DX(24), y = DY(100), w = DX(240), h = DY(600) - DY(100), i, ss = small_s();
    int ph = (DY(398) - DY(140)) / 4 - DS(6), pw = w - DX(36), pz;
    cpanel(x, y, w, h, step == STEP_BASE);
    jm_host->draw_text(jm_host, x + DX(16), DY(122), Tr("creation.v2.choose_base"), 0xFFE9A0, ss);
    pz = ph / 48; if (pz < 1) pz = 1;
    for (i = 0; i < 4; i++) {
        int ty = DY(140) + i * (ph + DS(6)), tx = x + DX(18), sel = jm.portrait % 4 == i;
        fillr(tx, ty, pw, ph, sel ? 0x2A2440 : 0x1A1C48, 255);
        blit(portrait_px(i), 48, 48, tx + DS(6), ty + (ph - 48 * pz) / 2, pz);
        text_fit(tx + DS(12) + 48 * pz, ty + ph / 2, pw - 48 * pz - DS(18), TrAt("creation.portraits", i, "?"), sel ? 0xFFFFFF : 0x9090B0, ss);
        frame_r(tx, ty, pw, ph, sel ? DS(3) : 1, sel ? 0xE8C050 : 0x44466E, 255);
        if (sel) check_mark(tx + pw - DS(22), ty + ph - DS(22), DS(18));
        if (sel && step == STEP_BASE && base_sect == 0) frame_r(tx - DS(4), ty - DS(4), pw + DS(8), ph + DS(8), 1, 0xFFF0B0, 200);
    }
    /* the small in-game sprite, walking, with the arrows that turn it */
    {
        int by = DY(410), bh = DY(590) - by, bx = x + DX(18), bw = pw, fr = 1 + (cg_t / 8) % 4, top, bot;
        jm_host->draw_text(jm_host, bx, by + DS(10), Tr("creation.v2.sprite_game"), 0xFFE9A0, ss);
        fillr(bx, by + DS(24), bw, bh - DS(24), 0x0C0E2A, 255);
        for (i = 1; i < 6; i++) fillr(bx + bw * i / 6, by + DS(24), 1, bh - DS(24), 0x1E2250, 255);       /* a faint grid */
        for (i = 1; i < 5; i++) fillr(bx, by + DS(24) + (bh - DS(24)) * i / 5, bw, 1, 0x1E2250, 255);
        frame_r(bx, by + DS(24), bw, bh - DS(24), 1, 0x44466E, 255);
        if (Cg_Style()) {
            int lw, lh, fx, fy, nf;
            const uint16_t *p = Paint_LpcFrame(turn_dir == 1 ? 1 : turn_dir == 2 ? 3 : turn_dir == 3 ? 2 : 0, 0, &lw, &lh, &fx, &fy, &nf);
            if (p) { p = Paint_LpcFrame(turn_dir == 1 ? 1 : turn_dir == 2 ? 3 : turn_dir == 3 ? 2 : 0, nf > 1 ? 1 + (cg_t / 5) % (nf - 1) : 0, &lw, &lh, &fx, &fy, &nf);
                     blit(p, lw, lh, bx + bw / 2 - lw * 2 / 2, by + DS(24) + (bh - DS(24) - lh * 2) / 2, 2); }
        } else if (Cg_Ready()) {
            static const int dirs[4] = {0, 2, 3, 1};
            const uint16_t *p = hero_frame(dirs[turn_dir], fr);
            bounds(p, 48, 62, &top, &bot);
            blit(p + (size_t)top * 1024, 48, bot - top + 1, bx + bw / 2 - 48, by + DS(24) + (bh - DS(24) - (bot - top + 1) * 2) / 2, 2);
        }
        text_c(bx + DS(12), by + DS(24) + (bh - DS(24)) / 2, "<", 0xE8C050, ui_s);
        text_c(bx + bw - DS(12), by + DS(24) + (bh - DS(24)) / 2, ">", 0xE8C050, ui_s);
    }
}

static void draw_center(void)
{
    int cx = DX(520), x0 = DX(280), x1 = DX(760), top = DY(96), floor_y = DY(500), ss = small_s();
    /* a soft vignette behind the hero, the ring of light under the feet */
    fillr(x0, top, x1 - x0, DY(600) - top, 0x0C0A26, 90);
    glow_ellipse(cx, DY(270), DX(200), DS(190), 0x2A2470, 60);
    glow_ellipse(cx, floor_y, DX(170), DS(36), 0x2E58C8, 70);
    glow_ellipse(cx, floor_y, DX(130), DS(26), 0x4C8CF0, 90);
    glow_ellipse(cx, floor_y, DX(118), DS(22), 0x10143A, 200);
    glow_ellipse(cx, floor_y, DX(96), DS(16), 0x5AA8FF, 110);
    glow_ellipse(cx, floor_y, DX(80), DS(12), 0x141A48, 220);
    if (view_portrait) {
        int z = (DY(470) - DY(150)) / 48;
        if (z < 1) z = 1;
        frame_r(cx - 24 * z - DS(4), floor_y - 48 * z - DS(30), 48 * z + DS(8), 48 * z + DS(8), DS(2), 0xC8A03C, 255);
        blit(portrait_px(jm.portrait), 48, 48, cx - 24 * z, floor_y - 48 * z - DS(26), z);
    } else if (Cg_Style()) {
        int lw, lh, fx, fy, nf, z;
        const uint16_t *p = Paint_LpcFrame(0, 0, &lw, &lh, &fx, &fy, &nf);
        if (p) {
            static const int dirs[4] = {0, 2, 3, 1};
            p = Paint_LpcFrame(dirs[turn_dir] == 2 ? 2 : dirs[turn_dir] == 1 ? 1 : dirs[turn_dir], 0, &lw, &lh, &fx, &fy, &nf);
            z = (floor_y - DY(110)) / (fy > 0 ? fy : lh);
            if (z < 1) z = 1;
            blit(p, lw, lh, cx - fx * z, floor_y - fy * z, z);
        }
    } else if (Cg_Ready()) {
        static const int dirs[4] = {0, 2, 3, 1};
        const uint16_t *p = hero_frame(dirs[turn_dir], 0);
        int z = (floor_y - DY(110)) / 56;
        if (z < 1) z = 1;
        blit(p, 48, 62, cx - 24 * z, floor_y - 56 * z, z);
    }
    /* View: sprite / portrait */
    {
        int vy = DY(548), vw = DX(300), vx = cx - vw / 2, bw = (vw - DX(24)) / 2, k;
        cpanel(vx, vy - DS(22), vw, DS(44), 0);
        for (k = 0; k < 2; k++) {
            int bx = vx + DX(8) + k * (bw + DX(8)), on = view_portrait == k;
            fillr(bx, vy - DS(15), bw, DS(30), on ? 0x3A2E14 : 0x1A1C48, 255);
            frame_r(bx, vy - DS(15), bw, DS(30), 1, on ? 0xE8C050 : 0x44466E, 255);
            text_c(bx + bw / 2, vy, Tr(k ? "creation.v2.view_portrait" : "creation.v2.view_sprite"), on ? 0xFFE9A0 : 0x9090B0, ss);
        }
    }
}

static void swatch_row(int x, int y, int w, int c, int focused, int ss)
{
    int n = Cg_OptCount(c), k, sw = DS(36), gap = DS(8), sel = Cg_Get(c);
    char lab[48];
    snprintf(lab, sizeof(lab), "%s", Cg_CatLabel(c));
    jm_host->draw_text(jm_host, x, y, lab, focused ? 0xFFE9A0 : 0xC8C8E0, ss);
    if (n > 0) { text_fit(x + w - DX(150), y, DX(150), Cg_OptLabel(c, sel), 0x9090B0, ss); }
    if (n * (sw + gap) > w) { sw = w / n - gap; if (sw < DS(12)) sw = DS(12); }
    for (k = 0; k < n; k++) {
        int sx = x + k * (sw + gap), sy = y + DS(16), rgb = Cg_OptRgb(c, k), rgb2 = Cg_OptRgb2(c, k);
        fillr(sx, sy, sw, sw, rgb < 0 ? 0x303030 : (unsigned)rgb, 255);
        if (rgb2 >= 0) fillr(sx, sy + sw * 2 / 3, sw, sw - sw * 2 / 3, (unsigned)rgb2, 255);
        frame_r(sx, sy, sw, sw, k == sel ? DS(3) : 1, k == sel ? 0xE8C050 : 0x50527A, 255);
        if (k == sel) check_mark(sx + sw - DS(12), sy - DS(4), DS(14));
        if (k == sel && focused) frame_r(sx - DS(4), sy - DS(4), sw + DS(8), sw + DS(8), 1, 0xFFF0B0, 220);
    }
}

static void draw_right(void)
{
    int x = DX(780), y = DY(100), w = DX(1256) - x, h = DY(600) - y, t, ss = small_s(), ntabs = 0, k, tx, tbw;
    int vis[TAB_N];
    cpanel(x, y, w, h, step == STEP_LOOK);
    for (t = 0; t < TAB_N; t++) if (tab_has(t)) vis[ntabs++] = t;
    if (!ntabs) { text_c(x + w / 2, y + h / 2, "-", 0x9090B0, ui_s); return; }
    {                                        /* tab widths follow their labels */
        int lw[TAB_N], tot = 0, room = w - DX(24) - (ntabs - 1) * DX(8);
        for (k = 0; k < ntabs; k++) { lw[k] = tw(TrAt("creation.v2.tabs", vis[k], "?"), ss) + DX(20); tot += lw[k]; }
        tx = x + DX(12);
        for (k = 0; k < ntabs; k++) {
            int on = vis[k] == tab, s2 = ss;
            const char *lab = TrAt("creation.v2.tabs", vis[k], "?");
            tbw = room * lw[k] / tot;
            fillr(tx, y + DS(12), tbw, DS(44), on ? 0x3A2E14 : 0x1A1C48, 255);
            frame_r(tx, y + DS(12), tbw, DS(44), on ? DS(2) : 1, on ? 0xE8C050 : 0x44466E, 255);
            if (on) fillr(tx + DS(8), y + DS(50), tbw - DS(16), DS(3), 0xE8C050, 255);
            while (s2 > 1 && tw(lab, s2) > tbw - DS(6)) s2--;
            text_c(tx + tbw / 2, y + DS(33), lab, on ? 0xFFE9A0 : 0x9A9CC8, s2);
            tx += tbw + DX(8);
        }
    }
    {
        int g = tab_grid(tab), cols[4], nc = tab_cols(tab, cols), cy = y + DS(84), gx = x + DX(30), gw = w - DX(60), is_grid = 0;
        int fc = step == STEP_LOOK ? sect_cat(sect, &is_grid) : -1;
        if (g >= 0 && Cg_OptCount(g) > 0) {
            int n = Cg_OptCount(g), sel = Cg_Get(g), tw_ = (gw - (GRID_COLS - 1) * DX(10)) / GRID_COLS, th = DS(96), i, page = sel / (GRID_COLS * GRID_ROWS);
            int pages = (n + GRID_COLS * GRID_ROWS - 1) / (GRID_COLS * GRID_ROWS), focused = is_grid && fc == g;
            const char *key = g == CG_HAIR_ ? "creation.v2.style_hair" : g == CG_OUTFIT_ ? "creation.v2.style_outfit" : "creation.v2.style_acc";
            jm_host->draw_text(jm_host, gx, cy, Tr(key), focused ? 0xFFE9A0 : 0xC8C8E0, ss);
            text_fit(x + w - DX(30) - DX(150), cy, DX(150), Cg_OptLabel(g, sel), 0x9090B0, ss);
            cy += DS(16);
            for (i = page * GRID_COLS * GRID_ROWS; i < n && i < (page + 1) * GRID_COLS * GRID_ROWS; i++) {
                int li = i - page * GRID_COLS * GRID_ROWS, ix = gx + (li % GRID_COLS) * (tw_ + DX(10)), iy = cy + (li / GRID_COLS) * (th + DS(10));
                const uint16_t *px = tile_of(g, i, li);
                int on = i == sel, z, y0, hh;
                fillr(ix, iy, tw_, th, on ? 0x2A2440 : 0x1A1C48, 255);
                if (px) {
                    if (g == CG_HAIR_ || g == CG_ACC_) { y0 = 2; hh = 30; }       /* head and shoulders */
                    else { y0 = 16; hh = 42; }                                    /* the outfit: neck to feet */
                    z = (th - DS(8)) / hh; if (z < 1) z = 1;
                    while (z > 1 && 34 * z > tw_ - DS(4)) z--;
                    blit48(px, 7, 34, y0, hh, ix + (tw_ - 34 * z) / 2, iy + (th - hh * z) / 2, z);
                }
                if (g == CG_ACC_ && i == 0) text_c(ix + tw_ / 2, iy + th - DS(12), Cg_OptLabel(g, 0), 0xB0B0C8, small_s() > 1 ? small_s() - 1 : 1);
                frame_r(ix, iy, tw_, th, on ? DS(3) : 1, on ? 0xE8C050 : 0x44466E, 255);
                if (on) check_mark(ix + tw_ - DS(20), iy + DS(4), DS(16));
                if (on && focused) frame_r(ix - DS(4), iy - DS(4), tw_ + DS(8), th + DS(8), 1, 0xFFF0B0, 220);
            }
            cy += GRID_ROWS * (th + DS(10)) + DS(4);
            if (pages > 1) {                         /* page dots, and arrows at the grid's sides */
                for (i = 0; i < pages; i++) glow_ellipse(x + w / 2 + (i * 2 - pages + 1) * DS(10), cy, DS(4), DS(4), i == page ? 0xE8C050 : 0x50527A, 255);
                text_c(x + DX(14), cy - GRID_ROWS * (th + DS(10)) / 2 - DS(8), "<", 0xE8C050, ui_s);
                text_c(x + w - DX(14), cy - GRID_ROWS * (th + DS(10)) / 2 - DS(8), ">", 0xE8C050, ui_s);
            }
            cy += DS(22);
        }
        if (Cg_Style()) { text_fit(gx, y + h - DS(20), gw, Tr("creation.v2.lpc_note"), 0xE0A060, ss); }
        for (k = 0; k < nc; k++) {
            swatch_row(gx, cy, gw, cols[k], !is_grid && fc == cols[k], ss);
            cy += DS(76);
        }
    }
}

/* Base step: the right panel holds the gender and sprite set rows */
static void draw_right_base(void)
{
    int x = DX(780), y = DY(100), w = DX(1256) - x, h = DY(600) - y, ss = small_s(), i;
    const char *lab[3], *val[3];
    cpanel(x, y, w, h, 1);
    jm_host->draw_text(jm_host, x + DX(24), y + DS(30), Tr("creation.v2.steps.0"), 0xFFE9A0, ui_s);
    lab[0] = Tr("creation.rows.portrait"); val[0] = TrAt("creation.portraits", jm.portrait % 4, "?");
    lab[1] = Tr("creation.rows.gender"); val[1] = Tr(jm.gender ? "creation.gender.female" : "creation.gender.male");
    lab[2] = Tr("creation.rows.sprite"); val[2] = Tr(Cg_Style() ? "creation.sprite.lpc" : "creation.sprite.layered");
    for (i = 0; i < 3; i++) {
        int ry = y + DS(80) + i * DS(70), on = base_sect == i, bw = w - DX(48);
        fillr(x + DX(24), ry, bw, DS(56), on ? 0x2A2440 : 0x1A1C48, 255);
        frame_r(x + DX(24), ry, bw, DS(56), on ? DS(2) : 1, on ? 0xE8C050 : 0x44466E, 255);
        jm_host->draw_text(jm_host, x + DX(36), ry + DS(16), lab[i], on ? 0xFFE9A0 : 0xC8C8E0, ss);
        text_c(x + DX(24) + bw / 2, ry + DS(40), val[i], 0xFFFFFF, ss);
        if (on) { jm_host->draw_text(jm_host, x + DX(36), ry + DS(40), "<", 0xE8C050, ss); jm_host->draw_text(jm_host, x + DX(24) + bw - DX(24), ry + DS(40), ">", 0xE8C050, ss); }
    }
}

static void draw_right_name(void)
{
    int x = DX(780), y = DY(100), w = DX(1256) - x, h = DY(600) - y, ss = small_s();
    cpanel(x, y, w, h, 1);
    jm_host->draw_text(jm_host, x + DX(24), y + DS(30), Tr("creation.v2.name_title"), 0xFFE9A0, ui_s);
    fillr(x + DX(24), y + DS(70), w - DX(48), DS(60), 0x0C0E2A, 255);
    frame_r(x + DX(24), y + DS(70), w - DX(48), DS(60), DS(2), 0xE8C050, 255);
    text_c(x + w / 2, y + DS(100), jm.name[0] ? jm.name : Tr("creation.v2.name_empty"), jm.name[0] ? 0xFFFFFF : 0x7070A0, ui_s);
    text_fit(x + DX(24), y + DS(160), w - DX(48), Tr("creation.v2.name_hint"), 0x9AA0D0, ss);
}

static void draw_right_confirm(void)
{
    int x = DX(780), y = DY(100), w = DX(1256) - x, h = DY(600) - y, ss = small_s(), c, ry;
    char b[96];
    cpanel(x, y, w, h, 1);
    jm_host->draw_text(jm_host, x + DX(24), y + DS(30), Tr("creation.v2.confirm_title"), 0xFFE9A0, ui_s);
    ry = y + DS(68);
#define ROW(L, V) do { text_fit(x + DX(30), ry, w * 46 / 100 - DX(36), (L), 0x9AA0D0, ss); text_fit(x + w * 46 / 100, ry, w * 54 / 100 - DX(20), (V), 0xFFFFFF, ss); ry += DS(30); } while (0)
    ROW(Tr("creation.rows.name"), jm.name[0] ? jm.name : "-");
    ROW(Tr("creation.rows.portrait"), TrAt("creation.portraits", jm.portrait % 4, "?"));
    ROW(Tr("creation.rows.gender"), Tr(jm.gender ? "creation.gender.female" : "creation.gender.male"));
    ROW(Tr("creation.rows.sprite"), Tr(Cg_Style() ? "creation.sprite.lpc" : "creation.sprite.layered"));
    if (!Cg_Style()) for (c = 0; c < Cg_CatCount(); c++) {
        if (!Cg_OptCount(c)) continue;
        snprintf(b, sizeof(b), "%s", Cg_OptLabel(c, Cg_Get(c)));
        ROW(Cg_CatLabel(c), b);
        if (ry > y + h - DS(20)) break;
    }
#undef ROW
}

static void draw_bottom(void)
{
    int by = DY(650), bh = DS(52), ss = small_s(), x, w;
    const char *nl = Tr(step == STEP_CONFIRM ? "creation.v2.begin" : "creation.v2.next");
    char nb[48];
    /* Back */
    cpanel(DX(24), by - bh / 2, DX(170), bh, 0);
    text_c(DX(24) + DX(85), by, Tr("creation.v2.back"), 0xE0E0F0, ui_s);
    /* Next, gold */
    snprintf(nb, sizeof(nb), "%s >", nl);
    fillr(DX(1060), by - bh / 2, DX(196), bh, 0xD8A830, 255);
    fillr(DX(1060), by - bh / 2, DX(196), bh / 3, 0xF0C850, 255);
    frame_r(DX(1060), by - bh / 2, DX(196), bh, DS(2), 0xFFF0B0, 255);
    text_c(DX(1060) + DX(98), by, nb, 0x241A08, ui_s);
    /* the keys of this step */
    {
        const char *k[12];
        int n = 0;
        k[n * 2] = "\x1b\x1a"; k[n * 2 + 1] = Tr("creation.v2.k_move"); n++;
        if (step == STEP_LOOK) { k[n * 2] = "Q/E"; k[n * 2 + 1] = Tr("creation.v2.k_tab"); n++; }
        if (step == STEP_NAME) { k[n * 2] = "X"; k[n * 2 + 1] = Tr("creation.v2.k_edit"); n++; }
        else { k[n * 2] = "X"; k[n * 2 + 1] = nl; n++; }
        k[n * 2] = "S"; k[n * 2 + 1] = Tr("creation.v2.back"); n++;
        k[n * 2] = "R"; k[n * 2 + 1] = Tr("creation.v2.k_rotate"); n++;
        k[n * 2] = "Z"; k[n * 2 + 1] = Tr("creation.v2.k_view"); n++;
        k[0] = "<>";
        if (step == STEP_LOOK || step == STEP_BASE) k[0] = "<^v>";
        w = keys_width(k, n);
        x = (DX(210) + DX(1044)) / 2 - w / 2;
        if (x < DX(210)) { while (n > 2 && keys_width(k, n) > DX(834)) n--; w = keys_width(k, n); x = (DX(210) + DX(1044)) / 2 - w / 2; }
        fillr(x - DX(12), by - DS(18), w + DX(12), DS(36), 0x0C0E2A, 200);
        frame_r(x - DX(12), by - DS(18), w + DX(12), DS(36), 1, 0x44466E, 255);
        {
            int i, xx = x;
            for (i = 0; i < n; i++) key_cap(&xx, by, k[2 * i], k[2 * i + 1]);
        }
        (void)ss;
    }
}

void Ui_CreateOverlay(void)
{
    metrics();
    draw_top();
    draw_left();
    draw_center();
    switch (step) {
    case STEP_BASE: draw_right_base(); break;
    case STEP_LOOK: draw_right(); break;
    case STEP_NAME: draw_right_name(); break;
    default: draw_right_confirm(); break;
    }
    draw_bottom();
}

static unsigned create_sig(void)
{
    return (unsigned)(step * 3 + tab * 41 + sect * 59 + base_sect * 71 + view_portrait * 83 + turn_dir * 97 + done_mask * 101) + (unsigned)(cg_t / 5) * 7907u;
}

unsigned Ui_Signature(void);

/* --------------------------------------------------------------- START menu */
enum { M_DECK, M_ITEMS, M_STATUS, M_SAVE, M_LANG, M_DEV, M_TITLE, M_CLOSE, M_COUNT };
static const int menu_text[M_COUNT] = {0, 1, 2, 3, -1, -2, 4, 5};   /* index in ui "menu.items"; the language and Dev mode rows are made */
static int msel, msub, qsel;

static const char *menu_name(int i, char *buf, size_t size)
{
    if (menu_text[i] == -2) {
        snprintf(buf, size, Tr("menu.dev"), Tr(Dev_BarOn() ? "menu.dev_on" : "menu.dev_off"));
        return buf;
    }
    if (menu_text[i] < 0) {
        snprintf(buf, size, Tr("choose.language"), Lang_Name(Lang_Current()));
        return buf;
    }
    return TrAt("menu.items", menu_text[i], "?");
}

void Ui_MenuOpen(void) { msel = 0; msub = 0; qsel = 1; }

int Ui_MenuInput(unsigned short edge)
{
    if (msub) {
        if (msel == M_TITLE) {
            if (edge & (PAD_LEFT | PAD_RIGHT | PAD_UP | PAD_DOWN)) qsel ^= 1;
            if (edge & PAD_CIRCLE) msub = 0;
            else if (edge & PAD_CROSS) { if (qsel == 0) return 3; msub = 0; }
        } else if (edge & (PAD_CIRCLE | PAD_CROSS | PAD_START | PAD_TRIANGLE)) msub = 0;
        return 0;
    }
    if (msel == M_LANG && (edge & (PAD_LEFT | PAD_RIGHT))) { Lang_Set((Lang_Current() + (edge & PAD_LEFT ? Lang_Count() - 1 : 1)) % Lang_Count()); jm_save_requested = 1; }
    if (msel == M_DEV && (edge & (PAD_LEFT | PAD_RIGHT))) Dev_Set(!Dev_BarOn());
    if (edge & PAD_UP) msel = (msel + M_COUNT - 1) % M_COUNT;
    if (edge & PAD_DOWN) msel = (msel + 1) % M_COUNT;
    if (edge & (PAD_CIRCLE | PAD_START | PAD_TRIANGLE)) return 1;
    if (edge & PAD_CROSS) {
        switch (msel) {
        case M_DECK: return 2;
        case M_CLOSE: return 1;
        case M_LANG:
            Lang_Set((Lang_Current() + 1) % Lang_Count());
            jm_save_requested = 1;
            break;
        case M_DEV: Dev_Set(!Dev_BarOn()); break;
        case M_SAVE:
            jm_save_requested = 1;
            msub = 1;
            break;
        case M_TITLE: msub = 1; qsel = 1; break;
        default: msub = 1; break;
        }
    }
    return 0;
}

void Ui_MenuOverlay(void)
{
    int x, y, w, h, lh, i;
    char buf[64], nb[48];
    metrics();
    lh = line_h();
    jm_host->fill(jm_host, 0, 0, ui_w, ui_h, 0, 110);
    x = ui_w / 40;
    y = ui_top + ui_vis / 16;
    w = ui_w / 4;
    for (i = 0; i < M_COUNT; i++) {          /* the box is as wide as its longest row (a language or Dev mode label may be long) */
        int rw = jm_host->text_width(jm_host, menu_name(i, nb, sizeof(nb)), ui_s) + 22 * ui_s + 14 * ui_s;
        if (rw > w) w = rw;
    }
    h = lh * (M_COUNT + 3);
    panel(x, y, w, h);
    text(x + 12 * ui_s, y + lh, jm.name, 0xFFE9A0);
    for (i = 0; i < M_COUNT; i++) {
        int ry = y + lh * (i + 2) + lh / 2;
        if (i == msel) text(x + 6 * ui_s, ry, ">", 0xFFFFFF);
        text(x + 22 * ui_s, ry, menu_name(i, nb, sizeof(nb)), i == msel ? 0x40E0E0 : 0xB8B8B8);
    }
    if (!msub) return;
    {
        int px = x + w + 8 * ui_s, pw = ui_w / 2, ph = lh * (msel == M_STATUS && Eco_Ready() ? 13 : 11), py = y;
        panel(px, py, pw, ph);
        text(px + 12 * ui_s, py + lh, menu_name(msel, nb, sizeof(nb)), 0xFFE9A0);
        if (msel == M_ITEMS) {
            char names[16][32];
            int n = Story_ItemList(names, 16);
            if (!n) text(px + 14 * ui_s, py + lh * 2 + lh / 2, Tr("menu.items_empty"), 0x909090);
            for (i = 0; i < n; i++) text(px + 14 * ui_s, py + lh * (i + 2) + lh / 2, names[i], 0xE0E0E0);
        } else if (msel == M_STATUS) {
            int cards = 0, k;
            extern u16 gDuel_awPlayerDeck[40];
            for (k = 0; k < 40; k++) if (gDuel_awPlayerDeck[k]) cards++;
            text(px + 14 * ui_s, py + lh * 2, Story_Chapter(), 0x40E0E0);
            snprintf(buf, sizeof(buf), Tr("menu.objective"), Story_Objective());
            text(px + 14 * ui_s, py + lh * 3, buf, 0xE0E0E0);
            snprintf(buf, sizeof(buf), Tr("menu.status"), jm.duels, jm.wins, jm.losses);
            text(px + 14 * ui_s, py + lh * 5, buf, 0xE0E0E0);
            snprintf(buf, sizeof(buf), Tr("menu.deck"), cards);
            text(px + 14 * ui_s, py + lh * 6, buf, 0xE0E0E0);
            if (Eco_Ready()) {
                int into, span, bw = pw / 3, bx = px + 14 * ui_s, by = py + lh * 8 + lh / 3;
                snprintf(buf, sizeof(buf), "%s", EcoTr("ui.status_title"));
                text(px + 14 * ui_s, py + lh * 7 + lh / 2, buf, 0x40E0E0);
                Ui_Fmt1(buf, sizeof(buf), EcoTr("ui.level_label"), Eco_Level());
                text(px + 14 * ui_s, py + lh * 8, buf, 0xE0E0E0);
                Ui_Fmt1(buf, sizeof(buf), EcoTr("ui.money"), jm.eco.coins);
                text(px + pw / 2, py + lh * 8, buf, 0xFFE9A0);
                snprintf(buf, sizeof(buf), EcoTr("ui.status_rank"), Eco_RankName());
                text(px + 14 * ui_s, py + lh * 9, buf, 0xE0E0E0);
                if (Eco_XpBar(&into, &span)) {       /* the bar of the way to the next level */
                    jm_host->fill(jm_host, bx, by + lh, bw, 6 * ui_s, 0x202840, 255);
                    jm_host->fill(jm_host, bx, by + lh, bw * into / span, 6 * ui_s, 0x40E0E0, 255);
                    snprintf(buf, sizeof(buf), EcoTr("ui.xp_label"), into, span);
                    text(bx + bw + 10 * ui_s, py + lh * 10, buf, 0x909090);
                } else text(bx, py + lh * 10, EcoTr("ui.xp_max"), 0xFFE9A0);
                if (jm.eco.amb_won || jm.eco.amb_lost) {
                    snprintf(buf, sizeof(buf), EcoTr("ui.status_gang"), jm.eco.amb_won, jm.eco.amb_lost);
                    text(px + 14 * ui_s, py + lh * 11, buf, 0xE0E0E0);
                }
            }
        } else if (msel == M_SAVE) {
            text(px + 14 * ui_s, py + lh * 2 + lh / 2, Tr(jm_save_ok ? "menu.saved" : "menu.save_failed"), jm_save_ok ? 0x60F060 : 0xF06060);
        } else if (msel == M_TITLE) {
            text(px + 14 * ui_s, py + lh * 2, Tr("menu.quit_title"), 0xE0E0E0);
            text(px + 14 * ui_s, py + lh * 3, Tr("menu.quit_warn"), 0x909090);
            text(px + 30 * ui_s, py + lh * 5, Tr("menu.yes"), qsel == 0 ? 0x40E0E0 : 0x909090);
            text(px + 30 * ui_s + w / 2, py + lh * 5, Tr("menu.no"), qsel == 1 ? 0x40E0E0 : 0x909090);
            text(px + 16 * ui_s + (qsel ? w / 2 : 0), py + lh * 5, ">", 0xFFFFFF);
        }
    }
}

unsigned Ui_Signature(void)
{
    return create_sig() * 31u + (unsigned)( msel * 131 + msub * 1009 + qsel * 17 + jm.gender * 3 + jm.hair * 5 + jm.hair_col * 7 + jm.skin * 11 +
                      jm.outfit * 13 + jm.portrait * 19 + (int)jm.name[0] * 23 + (int)jm.name[1] * 29 + Lang_Current() * 37 + Dev_BarOn() * 43 + (int)Cg_Signature() * 47) +
           (unsigned)jm.eco.coins * 1009u + (unsigned)jm.eco.xp * 7919u;
}
