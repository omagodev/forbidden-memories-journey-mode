/* Journey Mode screens: character creation and the START menu.  They are drawn with the port's
 * overlay (its menu font and panels) over the 3D picture, and the name is typed on the game's own
 * name-entry screen (main mode 9), which writes the name the whole port shows for the player. */
#include "types.h"
#include "jm.h"
#include <math.h>
#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <stdlib.h>

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
 * Four steps (Base, Appearance, Name, Confirm) laid out like a console RPG creator: the JOURNEY MODE plate, the title plate and a step
 * tracker of round gold nodes on top; "Choose base" on the left (busts of ready-made LPC heroes) above the small in-game sprite walking;
 * the hero big in the middle on a magic circle, over the castle plaza blurred (assets/ui/chargen_bg.raw, tools/bake_chargen_ui.py);
 * on the right tabs with pixel icons (Hair, Outfit, Colour, Accessories, Legs, Shoes), a 5x2 grid of busts wearing each option with page
 * arrows and dots, and round colour swatches; a dark "< Back" pill, the key hints in a rounded bar and a gold "Next >" pill at the bottom.
 * Everything is drawn in the overlay (fills) from the composed LPC texels (jm_chargen.c), so no texture bank is used by the screen.
 * Keys (keyboard default): arrows move, Q / E (L1 / L2, also W = R1) switch tabs, X or Enter next, S (Circle) back, R turns the sprite,
 * Z switches the big view (sprite / portrait).  Escape stays the host's exit key. */
enum { C_HAIR, C_HAIR_COL, C_SKIN, C_OUTFIT, C_ROWS };
enum { K_SKIN, K_HAIR, K_HAIR_COL, K_TOP, K_TOP_COL, K_LEGS, K_SHOES, K_ACC };     /* jm_chargen.c's categories */
enum { STEP_BASE, STEP_LOOK, STEP_NAME, STEP_CONFIRM, STEP_N };
enum { TAB_HAIR, TAB_OUTFIT, TAB_COLOUR, TAB_ACC, TAB_LEGS, TAB_SHOES, TAB_N };
#define GRID_COLS 5
#define GRID_ROWS 2
#define GRID_PAGE (GRID_COLS * GRID_ROWS)
static int step, tab, sect, base_row, base_top, view_portrait, turn_dir, done_mask;
static int cg_t;
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

/* a tab's grid category (or -1) and its swatch rows */
static int tab_grid(int t)
{
    switch (t) { case TAB_HAIR: return K_HAIR; case TAB_OUTFIT: return K_TOP; case TAB_ACC: return K_ACC; case TAB_LEGS: return K_LEGS; case TAB_SHOES: return K_SHOES; }
    return -1;
}
static int tab_cols(int t, int out[4])
{
    int n = 0;
    if (t == TAB_HAIR) out[n++] = K_HAIR_COL;
    else if (t == TAB_OUTFIT) out[n++] = K_TOP_COL;
    else if (t == TAB_COLOUR) { out[n++] = K_SKIN; out[n++] = K_HAIR_COL; out[n++] = K_TOP_COL; }
    return n;
}
static int tab_has(int t) { int c[4], g = tab_grid(t); return Cg_Ready() && ((g >= 0 && Cg_OptCount(g) > 0) || tab_cols(t, c) > 0); }
static int grid_rows_of(int t) { int g = tab_grid(t); return g >= 0 && Cg_OptCount(g) > 0 ? GRID_ROWS : 0; }
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
    step = STEP_BASE; tab = TAB_HAIR; sect = 0; base_row = 0; base_top = 0; view_portrait = 0; turn_dir = 0; done_mask = 0;
    cg_t = 0;
    Cg_Defaults();
    if (Cg_BaseCount() > 0) Cg_ApplyBase(0);
}

static void set_cat(int c, int v) { Cg_Set(c, v); cg_t = 0; }

static void change_tab(int d)
{
    int k;
    for (k = 0; k < TAB_N; k++) { tab = (tab + d + TAB_N) % TAB_N; if (tab_has(tab)) break; }
    sect = 0;
}

static void look_input(unsigned short edge)
{
    int is_grid, c, n, v, cnt, gr;
    if (edge & PAD_L1) change_tab(-1);
    if (edge & (PAD_R1 | PAD_L2)) change_tab(1);
    n = sect_count();
    if (!n) return;
    if (sect >= n) sect = n - 1;
    c = sect_cat(sect, &is_grid);
    if (c < 0) return;
    v = Cg_Get(c); cnt = Cg_OptCount(c); gr = grid_rows_of(tab);
    if (cnt <= 0) return;
    if (is_grid) {
        int row = (v % GRID_PAGE) / GRID_COLS;
        if (edge & PAD_LEFT) set_cat(c, (v + cnt - 1) % cnt);
        if (edge & PAD_RIGHT) set_cat(c, (v + 1) % cnt);
        if ((edge & PAD_UP) && row > 0) set_cat(c, v - GRID_COLS);
        if (edge & PAD_DOWN) {
            if (row < GRID_ROWS - 1 && v + GRID_COLS < cnt && (v + GRID_COLS) / GRID_PAGE == v / GRID_PAGE) set_cat(c, v + GRID_COLS);
            else if (n > gr) { sect = gr; return; }
        }
        sect = (Cg_Get(c) % GRID_PAGE) / GRID_COLS;           /* the grid section follows the selected tile */
    } else {
        if (edge & PAD_LEFT) set_cat(c, (v + cnt - 1) % cnt);
        if (edge & PAD_RIGHT) set_cat(c, (v + 1) % cnt);
        if (edge & PAD_UP) { if (sect > gr) sect--; else if (gr) sect = (Cg_Get(tab_grid(tab)) % GRID_PAGE) / GRID_COLS; }
        if ((edge & PAD_DOWN) && sect < n - 1) sect++;
    }
}

static void base_input(unsigned short edge)
{
    int d = edge & PAD_LEFT ? -1 : edge & PAD_RIGHT ? 1 : 0, nb = Cg_BaseCount();
    if (edge & PAD_UP) base_row = (base_row + 2) % 3;
    if (edge & PAD_DOWN) base_row = (base_row + 1) % 3;
    if (!d) return;
    if (base_row == 0 && nb > 0) { int b = Cg_MatchBase(); Cg_ApplyBase(((b < 0 ? base_top : b) + d + nb) % nb); }
    else if (base_row == 1) jm.gender ^= 1;
    else jm.portrait = (jm.portrait + d + 4) % 4;
    cg_t = 0;
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
            if (jm.name[0]) { jm.cg_set = 1; return 1; }
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

/* In the frame hook: only a dark backdrop (the overlay paints the whole screen). */
static unsigned logged_sig = ~0u;
void Ui_DrawCreate(void)
{
    cg_t++;
    Gfx_Backdrop(0x0A0A22, 0x1E1642);
    if (Cg_Ready() && logged_sig != Cg_Signature()) {
        logged_sig = Cg_Signature();
        LOG("journey: creator look %d %d %d %d %d %d %d %d body %d", jm.cg[0], jm.cg[1], jm.cg[2], jm.cg[3], jm.cg[4], jm.cg[5], jm.cg[6], jm.cg[7], jm.gender);
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
static unsigned mix(unsigned a, unsigned b, int t, int n)      /* a..b at t/n */
{
    int r = (int)(a >> 16 & 255) + ((int)(b >> 16 & 255) - (int)(a >> 16 & 255)) * t / n;
    int g = (int)(a >> 8 & 255) + ((int)(b >> 8 & 255) - (int)(a >> 8 & 255)) * t / n;
    int bl = (int)(a & 255) + ((int)(b & 255) - (int)(a & 255)) * t / n;
    return (unsigned)(r << 16 | g << 8 | bl);
}
static void vgrad(int x, int y, int w, int h, unsigned top, unsigned bot, unsigned a)
{
    int k, band = DS(4);
    for (k = 0; k < h; k += band) fillr(x, y + k, w, k + band > h ? h - k : band, mix(top, bot, k, h > 1 ? h : 1), a);
}
static void disc(int cx, int cy, int rx, int ry, unsigned rgb, unsigned a)          /* a filled ellipse */
{
    int y;
    if (rx < 1 || ry < 1) return;
    for (y = -ry; y <= ry; y++) {
        float f = 1.0f - (float)(y * y) / (float)(ry * ry);
        int hw = (int)(rx * sqrtf(f > 0 ? f : 0) + 0.5f);
        if (hw > 0) fillr(cx - hw, cy + y, hw * 2, 1, rgb, a);
    }
}
static void ring(int cx, int cy, int rx, int ry, int t, unsigned rgb, unsigned a)  /* an ellipse outline t thick */
{
    int y, irx = rx - t, iry = ry - t;
    for (y = -ry; y <= ry; y++) {
        float f = 1.0f - (float)(y * y) / (float)(ry * ry), fi;
        int hw = (int)(rx * sqrtf(f > 0 ? f : 0) + 0.5f), iw = 0;
        if (iry > 0 && y > -iry && y < iry) { fi = 1.0f - (float)(y * y) / (float)(iry * iry); iw = (int)(irx * sqrtf(fi > 0 ? fi : 0) + 0.5f); }
        if (hw <= 0) continue;
        if (iw <= 0) fillr(cx - hw, cy + y, hw * 2, 1, rgb, a);
        else { fillr(cx - hw, cy + y, hw - iw, 1, rgb, a); fillr(cx + iw, cy + y, hw - iw, 1, rgb, a); }
    }
}
static void diamond(int cx, int cy, int r, unsigned rgb, unsigned a)
{
    int k;
    for (k = -r; k <= r; k++) { int hw = r - (k < 0 ? -k : k); if (hw > 0) fillr(cx - hw, cy + k, hw * 2, 1, rgb, a); }
}
static void corner_orn(int cx, int cy)
{
    int r = DS(9);
    diamond(cx, cy, r + DS(2), 0x4A3008, 255);
    diamond(cx, cy, r, 0xE6BC52, 255);
    diamond(cx, cy, r - DS(4), 0x6A3CC8, 255);
    fillr(cx - DS(1), cy - r + DS(4), DS(2), DS(2), 0xFFF0C0, 255);
}
/* ornate panel: navy-to-purple gradient, a thick bevelled gold border, corner gems */
static void opanel(int x, int y, int w, int h, int active)
{
    int t = DS(3);
    if (active) frame_r(x - DS(4), y - DS(4), w + DS(8), h + DS(8), DS(3), 0xE8C050, 70);
    fillr(x + DS(5), y + DS(6), w, h, 0x000000, 110);                         /* drop shadow */
    vgrad(x, y, w, h, 0x1C1B52, 0x100D2E, 236);
    frame_r(x, y, w, h, DS(1), 0x3A2606, 255);
    frame_r(x + DS(1), y + DS(1), w - DS(2), h - DS(2), t, active ? 0xE8C050 : 0xC09032, 255);
    fillr(x + DS(1), y + DS(1), w - DS(2), DS(1), 0xFFE8A0, 255);              /* bevel light */
    fillr(x + DS(1), y + DS(1), DS(1), h - DS(2), 0xFFE8A0, 200);
    frame_r(x + DS(1) + t, y + DS(1) + t, w - DS(2) - 2 * t, h - DS(2) - 2 * t, DS(1), 0x4A3008, 255);
    fillr(x + DS(1) + t + DS(1), y + DS(1) + t + DS(1), w - 2 * t - DS(4), DS(1), 0x3C3C8C, 200);   /* inner sheen */
    corner_orn(x + DS(2), y + DS(2)); corner_orn(x + w - DS(2), y + DS(2));
    corner_orn(x + DS(2), y + h - DS(2)); corner_orn(x + w - DS(2), y + h - DS(2));
}
/* a pill (rounded ends); gold = the Next button */
static void pill(int x, int y, int w, int h, int gold, int lit)
{
    int r = h / 2;
    unsigned edge = gold ? 0xFFF0B0 : (lit ? 0xE8C050 : 0xA07828), top = gold ? 0xFFDC6A : 0x262660, bot = gold ? 0xC8901E : 0x12123A;
    disc(x + r, y + r, r + DS(2), r + DS(2), 0x000000, 90);
    disc(x + w - r, y + r, r + DS(2), r + DS(2), 0x000000, 90);
    disc(x + r, y + r, r, r, edge, 255); disc(x + w - r, y + r, r, r, edge, 255); fillr(x + r, y, w - 2 * r, h, edge, 255);
    {
        int i, ih = h - 2 * DS(2), ir = ih / 2, iy = y + DS(2);
        for (i = 0; i < ih; i++) {
            float f = 1.0f - (float)((i - ir) * (i - ir)) / (float)(ir * ir);
            int hw = (int)(ir * sqrtf(f > 0 ? f : 0) + 0.5f);
            fillr(x + r - hw, iy + i, w - 2 * r + 2 * hw, 1, mix(top, bot, i, ih), 255);
        }
    }
}
static int tw(const char *s, int sc) { return jm_host->text_width(jm_host, s, sc); }
static int small_s(void) { return ui_s > 2 ? ui_s - 1 : ui_s; }
static void text_c(int cx, int my, const char *s, unsigned rgb, int sc) { jm_host->draw_text(jm_host, cx - tw(s, sc) / 2, my, s, rgb, sc); }
static void text_sh(int x, int my, const char *s, unsigned rgb, int sc) { jm_host->draw_text(jm_host, x + DS(2), my + DS(2), s, 0x000000, sc); jm_host->draw_text(jm_host, x, my, s, rgb, sc); }
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
static void text_cfit(int cx, int my, int maxw, const char *s, unsigned rgb, int sc)
{
    while (sc > 1 && tw(s, sc) > maxw) sc--;
    text_c(cx, my, s, rgb, sc);
}
static unsigned rgb555(uint16_t v) { return ((v & 31) * 255 / 31) << 16 | ((v >> 5 & 31) * 255 / 31) << 8 | ((v >> 10 & 31) * 255 / 31); }
/* texels (any stride, 0 = clear) at an integer zoom, one fill per run of equal texels */
static void blit(const uint16_t *src, int stride, int x0, int y0, int w, int h, int dx, int dy, int z)
{
    int y, x;
    if (!src) return;
    for (y = 0; y < h; y++) {
        const uint16_t *r = src + (size_t)(y0 + y) * stride + x0;
        for (x = 0; x < w;) {
            int x1 = x + 1;
            if (!r[x]) { x++; continue; }
            while (x1 < w && r[x1] == r[x]) x1++;
            fillr(dx + x * z, dy + y * z, (x1 - x) * z, z, rgb555(r[x]), 255);
            x = x1;
        }
    }
}
static void check_badge(int x, int y, int sz)
{
    int k, t = sz / 7 < 1 ? 1 : sz / 7;
    disc(x + sz / 2, y + sz / 2, sz / 2 + DS(1), sz / 2 + DS(1), 0x3A2606, 255);
    disc(x + sz / 2, y + sz / 2, sz / 2, sz / 2, 0xF0C850, 255);
    for (k = 0; k < sz / 4; k++) fillr(x + sz / 4 + k, y + sz / 2 + k - t, t + 1, t + 1, 0x241A08, 255);
    for (k = 0; k < sz * 2 / 5; k++) fillr(x + sz / 4 + sz / 4 + k, y + sz / 2 + sz / 4 - k - t, t + 1, t + 1, 0x241A08, 255);
}
static const uint16_t *portrait_px(int i) { uint16_t *b = SoftGpu_Bank(BANK); return b ? b + (size_t)PORT_Y * 1024 + PORT_X + (i & 3) * 48 : NULL; }

/* the backdrop: the castle plaza blurred and tinted, 320x180 scaled to the screen */
static unsigned char *bg_px;
static int bg_w, bg_h, bg_tried;
static void draw_backdrop(void)
{
    int y, x;
    if (!bg_tried) {
        long size;
        unsigned char *d = Jm_Slurp("assets/ui/chargen_bg.raw", &size);
        bg_tried = 1;
        if (d && size > 8 && !memcmp(d, "CGB1", 4)) {
            bg_w = d[4] | d[5] << 8; bg_h = d[6] | d[7] << 8;
            if (size >= 8 + (long)bg_w * bg_h * 3) bg_px = d; else free(d);
        } else free(d);
    }
    fillr(0, 0, ui_w, ui_h, 0x07061A, 255);
    if (!bg_px) { vgrad(0, ui_top, ui_w, ui_vis, 0x1A1440, 0x0A0820, 255); return; }
    {
    int cw = ui_w, ch = ui_w * bg_h / bg_w, ox = 0, oy;     /* cover the whole canvas, cropping the sides when it is taller than 16:9 */
    if (ch < ui_h) { ch = ui_h; cw = ui_h * bg_w / bg_h; ox = (ui_w - cw) / 2; }
    oy = (ui_h - ch) / 2;
    for (y = 0; y < bg_h; y++) {
        int sy = oy + y * ch / bg_h, sh = oy + (y + 1) * ch / bg_h - sy;
        const unsigned char *r = bg_px + 8 + (size_t)y * bg_w * 3;
        for (x = 0; x < bg_w; x++) {
            int sx = ox + x * cw / bg_w, sw = ox + (x + 1) * cw / bg_w - sx;
            if (sx + sw < 0 || sx > ui_w) continue;
            fillr(sx, sy, sw, sh, (unsigned)(r[x * 3] << 16 | r[x * 3 + 1] << 8 | r[x * 3 + 2]), 255);
        }
    }
    }
}

/* 12x12 pixel icons of the tabs: '#' gold, '+' light, '.' clear */
static const char *const ICONS[TAB_N][12] = {
    {"...######...", "..########..", ".####++####.", ".##+....+##.", "##+......+##", "##........##", "##.#....#.##", "#..........#", "#..........#", "##........##", ".#........#.", "............"},  /* hair */
    {"..##....##..", ".###+..+###.", "####+##+####", "###......###", ".##......##.", "..#......#..", "..#......#..", "..#......#..", "..#......#..", "..#......#..", "..########..", "............"},  /* shirt */
    {"...######...", ".##......##.", "#..++....+.#", "#.++++..+++#", "#..++.....##", "#.........#.", "#..+++...#..", "#.+++++..##.", "#..+++....##", ".##......##.", "...######...", "............"},  /* palette */
    {"............", "............", "#..........#", "#..........#", "#####..#####", "#+++#..#+++#", "#+++####+++#", "#+++#..#+++#", "#####..#####", "............", "............", "............"},  /* glasses */
    {"..########..", "..########..", "..###..###..", "..##....##..", "..##....##..", "..##....##..", "..##....##..", "..##....##..", "..##....##..", "..##....##..", ".###....###.", "............"},  /* trousers */
    {"....###.....", "....###.....", "....###.....", "....###.....", "....###.....", "....####....", "....######..", "...########.", "..#########.", "..##########", "..##########", "............"},  /* boot */
};
static void icon(int cx, int cy, int t, int on)
{
    int y, x, z = DS(3);
    unsigned g = on ? 0xF0C850 : 0x8C88B8, l = on ? 0xFFF4C8 : 0xC8C4E8;
    for (y = 0; y < 12; y++)
        for (x = 0; x < 12; x++) {
            char c = ICONS[t][y][x];
            if (c == '.') continue;
            fillr(cx - 6 * z + x * z, cy - 6 * z + y * z, z, z, c == '#' ? g : l, 255);
        }
}

/* busts and figures of a look (current, a base, or the current with one option changed), cached by look */
#define TILE_MAX 24
static struct { unsigned sig; int ok; uint16_t px[64 * 64]; } tiles[TILE_MAX];
static unsigned look_sig(const unsigned char cg[8], int g, int cell) { unsigned h = (unsigned)g * 977u + (unsigned)cell; int i; for (i = 0; i < 8; i++) h = h * 131u + cg[i]; return h; }
static const uint16_t *look_cell(const unsigned char cg[8], int g, int cell, int slot)
{
    unsigned s = look_sig(cg, g, cell);
    if (slot < 0 || slot >= TILE_MAX) return NULL;
    if (!tiles[slot].ok || tiles[slot].sig != s) {
        if (!Cg_ComposeCell(cg, g, cell, tiles[slot].px)) return NULL;
        tiles[slot].sig = s; tiles[slot].ok = 1;
    }
    return tiles[slot].px;
}
/* the 64x64 idle pose of a direction (source resolution) */
static const uint16_t *look_hi(const unsigned char cg[8], int g, int dir, int slot)
{
    unsigned s = look_sig(cg, g, 1000 + dir);
    if (slot < 0 || slot >= TILE_MAX) return NULL;
    if (!tiles[slot].ok || tiles[slot].sig != s) {
        if (!Cg_ComposeHi(cg, g, dir, tiles[slot].px)) return NULL;
        tiles[slot].sig = s; tiles[slot].ok = 1;
    }
    return tiles[slot].px;
}
static const uint16_t *option_cell(int c, int o, int slot)
{
    unsigned char cg[8];
    memcpy(cg, jm.cg, 8);
    cg[c] = (unsigned char)o;
    return look_hi(cg, jm.gender, 0, slot);
}
static const int DIR_OF[4] = {0, 2, 3, 1};          /* turn order: down, right, up, left (cell rows: down, left, right, up) */

static void draw_top(void)
{
    int i, ss = small_s();
    /* JOURNEY MODE plate */
    opanel(DX(20), DY(14), DX(210), DY(84) - DY(14), 0);
    text_c(DX(125), DY(40), "JOURNEY", 0xFFE08A, ui_s);
    text_c(DX(125), DY(66), "MODE", 0xC8B8F0, ss);
    diamond(DX(60), DY(66), DS(4), 0xE6BC52, 255); diamond(DX(190), DY(66), DS(4), 0xE6BC52, 255);
    /* the title plate */
    opanel(DX(246), DY(14), DX(400), DY(84) - DY(14), 1);
    text_sh(DX(270), DY(38), Tr("creation.v2.title"), 0xFFE08A, ui_s);
    fillr(DX(270), DY(55), DX(30), DS(1), 0xC09032, 255);
    jm_host->draw_text(jm_host, DX(308), DY(64), Tr("creation.v2.subtitle"), 0xB8B4E0, ss);
    /* the step tracker */
    for (i = 0; i < STEP_N; i++) {
        int cx = DX(760 + i * 146), cy = DY(36), r = DS(17), done = (done_mask >> i & 1) && i != step;
        char n[4];
        if (i < STEP_N - 1) {
            fillr(cx + r + DS(4), cy - DS(1), DX(146) - 2 * r - DS(8), DS(3), 0x1A1430, 255);
            fillr(cx + r + DS(4), cy, DX(146) - 2 * r - DS(8), DS(1), (done_mask >> i & 1) ? 0xE8C050 : 0x5A5888, 255);
        }
        if (i == step) disc(cx, cy, r + DS(6), r + DS(6), 0xE8C050, 60);
        disc(cx, cy, r + DS(2), r + DS(2), 0x2A1A06, 255);
        disc(cx, cy, r, r, i == step || done ? 0xE8C050 : 0x6A6898, 255);
        disc(cx, cy, r - DS(3), r - DS(3), i == step ? 0xC8901E : 0x14143C, 255);
        if (i == step) disc(cx, cy - DS(4), r - DS(6), r - DS(9), 0xF0C850, 255);
        if (done) check_badge(cx - DS(10), cy - DS(10), DS(20));
        else { snprintf(n, sizeof(n), "%d", i + 1); text_c(cx, cy, n, i == step ? 0x241A08 : 0xB0B0D0, ss); }
        text_cfit(cx, DY(72), DX(i == STEP_N - 1 ? 124 : 142), TrAt("creation.v2.steps", i, "?"), i == step ? 0xFFE08A : 0xA8A6D0, ss);
    }
}

static void draw_left(void)
{
    int x = DX(20), y = DY(104), w = DX(232), h = DY(604) - DY(104), i, ss = small_s(), nb = Cg_BaseCount(), cur = Cg_MatchBase();
    int tx = x + DX(16), tw_ = w - DX(32), th = DS(84), gap = DS(8), ty0 = DY(140);
    opanel(x, y, w, h, step == STEP_BASE);
    diamond(x + DX(18), DY(124), DS(4), 0xE6BC52, 255);
    text_fit(x + DX(28), DY(124), w - DX(34), Tr("creation.v2.choose_base"), 0xFFE08A, ss);
    if (cur >= 0) { if (cur < base_top) base_top = cur; if (cur > base_top + 2) base_top = cur - 2; }
    for (i = 0; i < 3 && base_top + i < nb; i++) {
        int b = base_top + i, ty = ty0 + i * (th + gap), on = b == cur, g, bz;
        unsigned char cg[8];
        const uint16_t *px;
        vgrad(tx, ty, tw_, th, on ? 0x3A2A5E : 0x22265A, on ? 0x1A1438 : 0x121436, 255);
        bz = (th - DS(4)) / 32; if (bz < 1) bz = 1;
        if (Cg_BaseLook(b, cg, &g) && (px = look_hi(cg, g, 0, 17 + i)) != NULL) blit(px, 64, 14, 12, 36, 32, tx + DS(6), ty + th - 32 * bz - DS(2), bz);
        text_fit(tx + DS(14) + 36 * bz, ty + th / 2, tw_ - 36 * bz - DS(20), Cg_BaseName(b), on ? 0xFFFFFF : 0xA8A6D0, ss);
        frame_r(tx, ty, tw_, th, on ? DS(3) : DS(1), on ? 0xF0C850 : 0x4A4A88, 255);
        if (on) check_badge(tx + tw_ - DS(26), ty + th - DS(26), DS(22));
        if (on && step == STEP_BASE && base_row == 0) frame_r(tx - DS(3), ty - DS(3), tw_ + DS(6), th + DS(6), DS(1), 0xFFF4C8, 230);
    }
    if (base_top > 0) text_c(x + w / 2, ty0 - DS(8), "^", 0xF0C850, ss);
    if (base_top + 3 < nb) text_c(x + w / 2, ty0 + 3 * (th + gap) - DS(6), "v", 0xF0C850, ss);
    /* the small in-game sprite, walking, with the arrows that turn it */
    {
        int by = DY(452), bx = tx, bw = tw_, bh = DY(590) - by, fr = 1 + (cg_t / 5) % 9, z = 3;
        const uint16_t *px;
        diamond(x + DX(18), by - DS(13), DS(4), 0xE6BC52, 255);
        jm_host->draw_text(jm_host, x + DX(28), by - DS(13), Tr("creation.v2.sprite_game"), 0xFFE08A, ss);
        fillr(bx, by, bw, bh, 0x0A0C26, 255);
        for (i = 1; i < 8; i++) fillr(bx + bw * i / 8, by, 1, bh, 0x1C2050, 255);
        for (i = 1; i < 6; i++) fillr(bx, by + bh * i / 6, bw, 1, 0x1C2050, 255);
        frame_r(bx, by, bw, bh, DS(1), 0x4A4A88, 255);
        while (z > 1 && 38 * z > bh - DS(6)) z--;
        disc(bx + bw / 2, by + bh - DS(10), DS(22), DS(5), 0x000000, 120);
        px = look_cell(jm.cg, jm.gender, DIR_OF[turn_dir] * 10 + fr, 23);
        blit(px, 25, 0, 0, 25, 38, bx + bw / 2 - 25 * z / 2, by + bh - DS(4) - 36 * z, z);
        disc(bx + DS(16), by + bh / 2, DS(12), DS(12), 0x2A2A62, 255); text_c(bx + DS(16), by + bh / 2, "<", 0xF0C850, ss);
        disc(bx + bw - DS(16), by + bh / 2, DS(12), DS(12), 0x2A2A62, 255); text_c(bx + bw - DS(16), by + bh / 2, ">", 0xF0C850, ss);
    }
}

static void draw_center(void)
{
    int cx = DX(512), floor_y = DY(500), ss = small_s(), k;
    float a0 = cg_t * 0.012f;
    /* the magic circle */
    disc(cx, floor_y, DX(200), DS(52), 0x2848C0, 40);
    disc(cx, floor_y, DX(170), DS(42), 0x3A6CF0, 50);
    ring(cx, floor_y, DX(176), DS(44), DS(3), 0x6CB4FF, 200);
    ring(cx, floor_y, DX(160), DS(39), DS(1), 0xA8D8FF, 160);
    ring(cx, floor_y, DX(120), DS(29), DS(2), 0x6CB4FF, 180);
    ring(cx, floor_y, DX(78), DS(19), DS(2), 0xA8D8FF, 150);
    disc(cx, floor_y, DX(70), DS(16), 0x8CC8FF, 70);
    for (k = 0; k < 16; k++) {                              /* runes turning between the rings */
        float a = a0 + k * 0.3927f;
        int px = cx + (int)(DX(140) * cosf(a)), py = floor_y + (int)(DS(34) * sinf(a));
        diamond(px, py, DS(k & 1 ? 3 : 4), k & 1 ? 0xA8D8FF : 0xE8F4FF, 220);
    }
    for (k = 0; k < 6; k++) {                               /* a few sparks rising */
        int sx = cx - DX(150) + k * DX(60) + (int)(DX(10) * sinf(cg_t * 0.05f + k)), sy = floor_y - DS(20) - (int)((cg_t * 2 + k * 37) % 220) * ui_vis / 720;
        fillr(sx, sy, DS(3), DS(3), 0x9CD0FF, 160);
    }
    if (view_portrait) {
        int z = (DY(470) - DY(150)) / 48, fx, fy;
        if (z < 1) z = 1;
        fx = cx - 24 * z; fy = floor_y - 48 * z - DS(30);
        opanel(fx - DS(10), fy - DS(10), 48 * z + DS(20), 48 * z + DS(20), 0);
        blit(portrait_px(jm.portrait), 1024, 0, 0, 48, 48, fx, fy, z);
    } else {
        int z = (floor_y - DY(112)) / 52;
        const uint16_t *px = look_hi(jm.cg, jm.gender, DIR_OF[turn_dir], 22);
        if (z < 1) z = 1;
        disc(cx, floor_y, DX(70), DS(14), 0x000000, 120);
        blit(px, 64, 0, 0, 64, 64, cx - 32 * z, floor_y - 62 * z, z);
    }
    /* View: sprite / portrait */
    {
        int vy = DY(560), vw = DX(320), vx = cx - vw / 2, bw = (vw - DX(36)) / 2;
        opanel(vx, vy - DS(24), vw, DS(48), 0);
        for (k = 0; k < 2; k++) {
            int bx = vx + DX(12) + k * (bw + DX(12)), on = view_portrait == k;
            vgrad(bx, vy - DS(15), bw, DS(30), on ? 0x5A4214 : 0x22265A, on ? 0x2A1E08 : 0x121436, 255);
            frame_r(bx, vy - DS(15), bw, DS(30), on ? DS(2) : DS(1), on ? 0xF0C850 : 0x4A4A88, 255);
            text_cfit(bx + bw / 2, vy, bw - DS(8), Tr(k ? "creation.v2.view_portrait" : "creation.v2.view_sprite"), on ? 0xFFE08A : 0x9A98C8, ss);
        }
    }
}

static void swatch_row(int x, int y, int w, int c, int focused, int ss)
{
    int n = Cg_OptCount(c), k, d = DS(34), gap = DS(10), sel = Cg_Get(c);
    diamond(x + DS(4), y, DS(4), 0xE6BC52, 255);
    jm_host->draw_text(jm_host, x + DS(14), y, Cg_CatLabel(c), focused ? 0xFFE08A : 0xD0CCF0, ss);
    if (n > 0) text_fit(x + w - DX(140), y, DX(140), Cg_OptLabel(c, sel), 0x9A98C8, ss);
    if (n * (d + gap) > w) { d = w / n - gap; if (d < DS(14)) d = DS(14); }
    for (k = 0; k < n; k++) {
        int sx = x + k * (d + gap) + d / 2, sy = y + DS(20) + d / 2, rgb = Cg_OptRgb(c, k);
        if (k == sel) disc(sx, sy, d / 2 + DS(5), d / 2 + DS(5), focused ? 0xFFF4C8 : 0xE8C050, focused ? 255 : 200);
        disc(sx, sy, d / 2 + DS(2), d / 2 + DS(2), 0x1A1206, 255);
        disc(sx, sy, d / 2, d / 2, rgb < 0 ? 0x303030 : (unsigned)rgb, 255);
        disc(sx - d / 6, sy - d / 6, d / 6, d / 7, 0xFFFFFF, 70);              /* a shine */
        if (k == sel) check_badge(sx + d / 4, sy - d / 2 - DS(4), DS(16));
    }
}

static void draw_tabs(int x, int y, int w)
{
    int vis[TAB_N], n = 0, t, k, ss = small_s(), tbw, gap = DX(6);
    for (t = 0; t < TAB_N; t++) if (tab_has(t)) vis[n++] = t;
    if (!n) return;
    tbw = (w - (n - 1) * gap) / n;
    for (k = 0; k < n; k++) while (ss > 1 && tw(TrAt("creation.v2.tabs", vis[k], "?"), ss) > tbw - DS(6)) ss--;
    for (k = 0; k < n; k++) {
        int tx = x + k * (tbw + gap), on = vis[k] == tab, th = DS(64);
        vgrad(tx, y, tbw, th, on ? 0x6A4E18 : 0x262A64, on ? 0x2E2008 : 0x14163E, 255);
        frame_r(tx, y, tbw, th, on ? DS(3) : DS(1), on ? 0xF0C850 : 0x4A4A88, 255);
        if (on) frame_r(tx - DS(2), y - DS(2), tbw + DS(4), th + DS(4), DS(1), 0xFFF4C8, 120);
        icon(tx + tbw / 2, y + DS(22), vis[k], on);
        text_cfit(tx + tbw / 2, y + DS(50), tbw - DS(6), TrAt("creation.v2.tabs", vis[k], "?"), on ? 0xFFE08A : 0xA8A6D0, ss);
    }
}

static void draw_right(void)
{
    int x = DX(770), y = DY(104), w = DX(1260) - x, h = DY(604) - y, ss = small_s();
    opanel(x, y, w, h, step == STEP_LOOK);
    draw_tabs(x + DX(16), y + DS(16), w - DX(32));
    {
        int g = tab_grid(tab), cols[4], nc = tab_cols(tab, cols), cy = y + DS(104), gx = x + DX(24), gw = w - DX(48), is_grid = 0, k;
        int fc = sect_cat(sect, &is_grid);
        if (g >= 0 && Cg_OptCount(g) > 0) {
            int n = Cg_OptCount(g), sel = Cg_Get(g), page = sel / GRID_PAGE, pages = (n + GRID_PAGE - 1) / GRID_PAGE, i, focused = is_grid && fc == g;
            int ax = DX(22), tw_ = (gw - 2 * ax - (GRID_COLS - 1) * DX(8)) / GRID_COLS, th = DS(86), y0, hh;
            static const char *const key[8] = {"", "creation.v2.style_hair", "", "creation.v2.style_outfit", "", "creation.v2.style_legs", "creation.v2.style_shoes", "creation.v2.style_acc"};
            diamond(gx + DS(4), cy, DS(4), 0xE6BC52, 255);
            jm_host->draw_text(jm_host, gx + DS(14), cy, Tr(key[g]), focused ? 0xFFE08A : 0xD0CCF0, ss);
            text_fit(gx + gw - DX(150), cy, DX(150), Cg_OptLabel(g, sel), 0x9A98C8, ss);
            cy += DS(18);
            fillr(gx, cy - DS(4), gw, GRID_ROWS * (th + DS(8)) + DS(4), 0x0A0A24, 120);
            y0 = g == K_TOP ? 26 : g == K_LEGS ? 38 : g == K_SHOES ? 48 : 8;      /* rows of the 64x64 pose: head, chest, legs, feet */
            hh = g == K_SHOES ? 16 : 26;
            for (i = page * GRID_PAGE; i < n && i < (page + 1) * GRID_PAGE; i++) {
                int li = i - page * GRID_PAGE, ix = gx + ax + (li % GRID_COLS) * (tw_ + DX(8)), iy = cy + (li / GRID_COLS) * (th + DS(8)), on = i == sel, z;
                const uint16_t *px = option_cell(g, i, li);
                vgrad(ix, iy, tw_, th, on ? 0x40306A : 0x262A64, on ? 0x1C1440 : 0x14163E, 255);
                if (px) {
                    z = (th - DS(8)) / hh;
                    while (z > 1 && 32 * z > tw_ - DS(4)) z--;
                    blit(px, 64, 16, y0, 32, hh, ix + (tw_ - 32 * z) / 2, iy + (th - hh * z) / 2, z);
                }
                frame_r(ix, iy, tw_, th, on ? DS(3) : DS(1), on ? 0xF0C850 : 0x4A4A88, 255);
                if (on) check_badge(ix + tw_ - DS(20), iy - DS(6), DS(22));
                if (on && focused) frame_r(ix - DS(3), iy - DS(3), tw_ + DS(6), th + DS(6), DS(1), 0xFFF4C8, 230);
            }
            if (pages > 1) {
                int my = cy + GRID_ROWS * (th + DS(8)) / 2;
                text_c(gx + ax / 2, my, "<", 0xF0C850, ui_s);
                text_c(gx + gw - ax / 2, my, ">", 0xF0C850, ui_s);
            }
            cy += GRID_ROWS * (th + DS(8)) + DS(10);
            for (i = 0; i < pages && pages > 1; i++) disc(x + w / 2 + (i * 2 - pages + 1) * DS(12), cy, DS(4), DS(4), i == page ? 0xF0C850 : 0x5A5888, 255);
            cy += DS(22);
        }
        for (k = 0; k < nc; k++) {
            swatch_row(gx, cy, gw, cols[k], !is_grid && fc == cols[k], ss);
            cy += DS(84);
        }
    }
}

/* Base step: the base, the body type and the dialogue portrait */
static void draw_right_base(void)
{
    int x = DX(770), y = DY(104), w = DX(1260) - x, h = DY(604) - y, ss = small_s(), i, b = Cg_MatchBase();
    const char *lab[3], *val[3];
    opanel(x, y, w, h, 1);
    diamond(x + DX(28), y + DS(32), DS(5), 0xE6BC52, 255);
    text_sh(x + DX(42), y + DS(32), TrAt("creation.v2.steps", 0, "Base"), 0xFFE08A, ui_s);
    lab[0] = Tr("creation.v2.base"); val[0] = b >= 0 ? Cg_BaseName(b) : Tr("creation.v2.custom");
    lab[1] = Tr("creation.v2.body"); val[1] = Tr(jm.gender ? "creation.v2.body_female" : "creation.v2.body_male");
    lab[2] = Tr("creation.rows.portrait"); val[2] = TrAt("creation.portraits", jm.portrait % 4, "?");
    for (i = 0; i < 3; i++) {
        int ry = y + DS(76) + i * DS(84), on = base_row == i, bw = w - DX(56), bx = x + DX(28);
        vgrad(bx, ry, bw, DS(66), on ? 0x40306A : 0x262A64, on ? 0x1C1440 : 0x14163E, 255);
        frame_r(bx, ry, bw, DS(66), on ? DS(3) : DS(1), on ? 0xF0C850 : 0x4A4A88, 255);
        jm_host->draw_text(jm_host, bx + DX(14), ry + DS(18), lab[i], on ? 0xFFE08A : 0xA8A6D0, ss);
        text_cfit(bx + bw / 2, ry + DS(44), bw - DX(80), val[i], 0xFFFFFF, ss);
        if (on) { text_c(bx + DX(20), ry + DS(44), "<", 0xF0C850, ss); text_c(bx + bw - DX(20), ry + DS(44), ">", 0xF0C850, ss); }
    }
    if (i == 3 && jm.portrait >= 0) {
        int z = 2, py = y + DS(76) + 3 * DS(84) + DS(8);
        if (py + 48 * z < y + h - DS(14)) { frame_r(x + w / 2 - 24 * z - DS(4), py - DS(4), 48 * z + DS(8), 48 * z + DS(8), DS(2), 0xC09032, 255); blit(portrait_px(jm.portrait), 1024, 0, 0, 48, 48, x + w / 2 - 24 * z, py, z); }
    }
}

static void draw_right_name(void)
{
    int x = DX(770), y = DY(104), w = DX(1260) - x, h = DY(604) - y, ss = small_s();
    opanel(x, y, w, h, 1);
    diamond(x + DX(28), y + DS(32), DS(5), 0xE6BC52, 255);
    text_sh(x + DX(42), y + DS(32), Tr("creation.v2.name_title"), 0xFFE08A, ui_s);
    vgrad(x + DX(28), y + DS(70), w - DX(56), DS(64), 0x0A0C26, 0x161A44, 255);
    frame_r(x + DX(28), y + DS(70), w - DX(56), DS(64), DS(3), 0xF0C850, 255);
    text_c(x + w / 2, y + DS(102), jm.name[0] ? jm.name : Tr("creation.v2.name_empty"), jm.name[0] ? 0xFFFFFF : 0x7070A0, ui_s);
    text_fit(x + DX(28), y + DS(166), w - DX(56), Tr("creation.v2.name_hint"), 0xA8A6D0, ss);
}

static void draw_right_confirm(void)
{
    int x = DX(770), y = DY(104), w = DX(1260) - x, h = DY(604) - y, ss = small_s(), c, ry, b = Cg_MatchBase();
    opanel(x, y, w, h, 1);
    diamond(x + DX(28), y + DS(32), DS(5), 0xE6BC52, 255);
    text_sh(x + DX(42), y + DS(32), Tr("creation.v2.confirm_title"), 0xFFE08A, ui_s);
    ry = y + DS(72);
#define ROW(L, V) do { fillr(x + DX(26), ry - DS(13), w - DX(52), DS(26), 0x1A1C4C, ((ry / DS(30)) & 1) ? 150 : 60); \
    text_fit(x + DX(34), ry, w * 44 / 100 - DX(40), (L), 0xA8A6D0, ss); text_fit(x + w * 44 / 100, ry, w * 56 / 100 - DX(34), (V), 0xFFFFFF, ss); ry += DS(31); } while (0)
    ROW(Tr("creation.rows.name"), jm.name[0] ? jm.name : "-");
    ROW(Tr("creation.v2.base"), b >= 0 ? Cg_BaseName(b) : Tr("creation.v2.custom"));
    ROW(Tr("creation.v2.body"), Tr(jm.gender ? "creation.v2.body_female" : "creation.v2.body_male"));
    for (c = 0; c < Cg_CatCount(); c++) {
        if (!Cg_OptCount(c)) continue;
        ROW(Cg_CatLabel(c), Cg_OptLabel(c, Cg_Get(c)));
        if (ry > y + h - DS(24)) break;
    }
#undef ROW
}

static void key_cap(int *x, int my, const char *key, const char *label)
{
    int ss = small_s(), kw = tw(key, ss) + DS(14), kh = DS(26);
    if (kw < kh) kw = kh;
    pill(*x, my - kh / 2, kw, kh, 0, 1);
    text_c(*x + kw / 2, my, key, 0xFFFFFF, ss);
    *x += kw + DS(6);
    jm_host->draw_text(jm_host, *x, my, label, 0xC8C4E8, ss);
    *x += tw(label, ss) + DS(18);
}
static int keys_width(const char *const *k, int n)
{
    int ss = small_s(), w = 0, i, kw;
    for (i = 0; i < n; i++) { kw = tw(k[2 * i], ss) + DS(14); if (kw < DS(26)) kw = DS(26); w += kw + DS(6) + tw(k[2 * i + 1], ss) + DS(18); }
    return w - DS(18);
}

static void draw_bottom(void)
{
    int by = DY(656), bh = DS(54), x, w;
    const char *nl = Tr(step == STEP_CONFIRM ? "creation.v2.begin" : "creation.v2.next");
    char b[48];
    pill(DX(20), by - bh / 2, DX(190), bh, 0, 0);
    snprintf(b, sizeof(b), "< %s", Tr("creation.v2.back"));
    text_c(DX(20) + DX(95), by, b, 0xE8E4FF, ui_s);
    pill(DX(1050), by - bh / 2, DX(210), bh, 1, 1);
    snprintf(b, sizeof(b), "%s >", nl);
    text_c(DX(1050) + DX(105), by, b, 0x2A1A04, ui_s);
    {
        const char *k[12];
        int n = 0, i, xx;
        k[n * 2] = step == STEP_LOOK ? "<^v>" : "^v"; k[n * 2 + 1] = Tr("creation.v2.k_move"); n++;
        if (step == STEP_LOOK) { k[n * 2] = "Q/E"; k[n * 2 + 1] = Tr("creation.v2.k_tab"); n++; }
        if (step == STEP_BASE) { k[0] = "<^v>"; }
        if (step == STEP_NAME) { k[n * 2] = "X"; k[n * 2 + 1] = Tr("creation.v2.k_edit"); n++; }
        else { k[n * 2] = "X"; k[n * 2 + 1] = nl; n++; }
        k[n * 2] = "S"; k[n * 2 + 1] = Tr("creation.v2.back"); n++;
        k[n * 2] = "R"; k[n * 2 + 1] = Tr("creation.v2.k_rotate"); n++;
        k[n * 2] = "Z"; k[n * 2 + 1] = Tr("creation.v2.k_view"); n++;
        while (n > 2 && keys_width(k, n) > DX(720)) n--;
        w = keys_width(k, n);
        x = (DX(220) + DX(1040)) / 2 - w / 2;
        {   /* the rounded bar */
            int bx = x - DS(30), bw = w + DS(60), bhh = DS(40), r = bhh / 2;
            disc(bx + r, by, r, r, 0x0C0C2A, 220); disc(bx + bw - r, by, r, r, 0x0C0C2A, 220); fillr(bx + r, by - r, bw - 2 * r, bhh, 0x0C0C2A, 220);
            ring(bx + r, by, r, r, DS(1), 0x6A5A9A, 255); ring(bx + bw - r, by, r, r, DS(1), 0x6A5A9A, 255);
            fillr(bx + r, by - r, bw - 2 * r, DS(1), 0x6A5A9A, 255); fillr(bx + r, by + r - DS(1), bw - 2 * r, DS(1), 0x6A5A9A, 255);
            fillr(bx + r - DS(1), by - r + DS(1), DS(2), bhh - DS(2), 0x0C0C2A, 255); fillr(bx + bw - r - DS(1), by - r + DS(1), DS(2), bhh - DS(2), 0x0C0C2A, 255);
        }
        xx = x;
        for (i = 0; i < n; i++) key_cap(&xx, by, k[2 * i], k[2 * i + 1]);
    }
}

/* The creator's drawing kit, for the other ornate screens (the shop, jm_shop.c).  Design units are a 1280x720 canvas. */
int Ui_DX(int v) { return DX(v); }
int Ui_DY(int v) { return DY(v); }
int Ui_DS(int v) { return DS(v); }
int Ui_SmallS(void) { return small_s(); }
void Ui_Fill(int x, int y, int w, int h, unsigned rgb, unsigned a) { fillr(x, y, w, h, rgb, a); }
void Ui_Frame(int x, int y, int w, int h, int t, unsigned rgb, unsigned a) { frame_r(x, y, w, h, t, rgb, a); }
void Ui_VGrad(int x, int y, int w, int h, unsigned top, unsigned bot, unsigned a) { vgrad(x, y, w, h, top, bot, a); }
void Ui_Disc(int cx, int cy, int rx, int ry, unsigned rgb, unsigned a) { disc(cx, cy, rx, ry, rgb, a); }
void Ui_Ring(int cx, int cy, int rx, int ry, int t, unsigned rgb, unsigned a) { ring(cx, cy, rx, ry, t, rgb, a); }
void Ui_OPanel(int x, int y, int w, int h, int active) { opanel(x, y, w, h, active); }
void Ui_Pill(int x, int y, int w, int h, int gold, int lit) { pill(x, y, w, h, gold, lit); }
void Ui_TextC(int cx, int my, const char *t, unsigned rgb, int sc) { text_c(cx, my, t, rgb, sc); }
void Ui_TextSh(int x, int my, const char *t, unsigned rgb, int sc) { text_sh(x, my, t, rgb, sc); }
void Ui_TextFit(int x, int my, int maxw, const char *t, unsigned rgb, int sc) { text_fit(x, my, maxw, t, rgb, sc); }
/* key caps and their labels in the rounded bar, centred on cx (pairs: key, label) */
void Ui_KeyBar(const char *const *k, int n, int cx, int my, int maxw)
{
    int w, x, i;
    while (n > 1 && keys_width(k, n) > maxw) n--;
    w = keys_width(k, n);
    x = cx - w / 2;
    {
        int bx = x - DS(24), bw = w + DS(48), bhh = DS(38), r = bhh / 2;
        disc(bx + r, my, r, r, 0x0C0C2A, 225); disc(bx + bw - r, my, r, r, 0x0C0C2A, 225); fillr(bx + r, my - r, bw - 2 * r, bhh, 0x0C0C2A, 225);
        ring(bx + r, my, r, r, DS(1), 0x6A5A9A, 255); ring(bx + bw - r, my, r, r, DS(1), 0x6A5A9A, 255);
        fillr(bx + r, my - r, bw - 2 * r, DS(1), 0x6A5A9A, 255); fillr(bx + r, my + r - DS(1), bw - 2 * r, DS(1), 0x6A5A9A, 255);
        fillr(bx + r - DS(1), my - r + DS(1), DS(2), bhh - DS(2), 0x0C0C2A, 255); fillr(bx + bw - r - DS(1), my - r + DS(1), DS(2), bhh - DS(2), 0x0C0C2A, 255);
    }
    for (i = 0; i < n; i++) key_cap(&x, my, k[2 * i], k[2 * i + 1]);
}

void Ui_CreateOverlay(void)
{
    metrics();
    draw_backdrop();
    draw_top();
    draw_center();
    draw_left();
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
    return (unsigned)(step * 3 + tab * 41 + sect * 59 + base_row * 71 + view_portrait * 83 + turn_dir * 97 + done_mask * 101 + jm.portrait * 7) +
           (unsigned)(cg_t / 3) * 7907u + Cg_Signature() * 13u;
}

unsigned Ui_Signature(void);

/* --------------------------------------------------------------- START menu */
enum { M_DECK, M_ITEMS, M_STATUS, M_SAVE, M_LANG, M_DEV, M_TITLE, M_CLOSE, M_COUNT };
static const int menu_text[M_COUNT] = {0, 1, 2, 3, -1, -2, 4, 5};   /* index in ui "menu.items"; the language and Dev mode rows are made */
static int msel, msub, qsel;
static int menu_shown(int i) { return i != M_DEV || Dbg_On(); }   /* the Dev mode row exists only with debug.json */

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
    if (msub && msel == M_ITEMS) { if (Bag_Input(edge)) msub = 0; return 0; }   /* the backpack, its own screen */
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
    if (edge & PAD_UP) do msel = (msel + M_COUNT - 1) % M_COUNT; while (!menu_shown(msel));
    if (edge & PAD_DOWN) do msel = (msel + 1) % M_COUNT; while (!menu_shown(msel));
    if (edge & (PAD_CIRCLE | PAD_START | PAD_TRIANGLE)) return 1;
    if (edge & PAD_CROSS) {
        switch (msel) {
        case M_DECK: return 2;
        case M_CLOSE: return 1;
        case M_LANG:
            Lang_Set((Lang_Current() + 1) % Lang_Count());
            jm_save_requested = 1;
            break;
        case M_DEV: if (Dbg_On()) Dev_Set(!Dev_BarOn()); break;
        case M_SAVE:
            jm_save_requested = 1;
            msub = 1;
            break;
        case M_TITLE: msub = 1; qsel = 1; break;
        case M_ITEMS: Bag_Open(); msub = 1; break;
        default: msub = 1; break;
        }
    }
    return 0;
}

void Ui_MenuOverlay(void)
{
    int x, y, w, h, lh, i;
    char buf[64], nb[48];
    if (msub && msel == M_ITEMS) { Bag_Overlay(); return; }
    metrics();
    lh = line_h();
    jm_host->fill(jm_host, 0, 0, ui_w, ui_h, 0, 110);
    x = ui_w / 40;
    y = ui_top + ui_vis / 16;
    w = ui_w / 4;
    for (i = 0; i < M_COUNT; i++) {          /* the box is as wide as its longest row (a language or Dev mode label may be long) */
        int rw;
        if (!menu_shown(i)) continue;
        rw = jm_host->text_width(jm_host, menu_name(i, nb, sizeof(nb)), ui_s) + 22 * ui_s + 14 * ui_s;
        if (rw > w) w = rw;
    }
    h = lh * (M_COUNT - !menu_shown(M_DEV) + 3);
    panel(x, y, w, h);
    text(x + 12 * ui_s, y + lh, jm.name, 0xFFE9A0);
    for (i = 0, nb[0] = 0; i < M_COUNT; i++) {
        int row = i - (i > M_DEV && !menu_shown(M_DEV)), ry = y + lh * (row + 2) + lh / 2;
        if (!menu_shown(i)) continue;
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
           (unsigned)jm.eco.coins * 1009u + (unsigned)jm.eco.xp * 7919u + (msub && msel == M_ITEMS ? Bag_Signature() : 0u);
}
