/* Journey Mode screens: character creation and the START menu.  They are drawn with the port's
 * overlay (its menu font and panels) over the 3D picture, and the name is typed on the game's own
 * name-entry screen (main mode 9), which writes the name the whole port shows for the player. */
#include "types.h"
#include "jm.h"
#include <math.h>
#include <stdio.h>
#include <string.h>

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
 * The rows: Name, Gender, then one row per chargen category (skin, outfit, outfit colour, hair, hair colour, accessory ... whatever
 * assets/chargen/manifest.json lists), Portrait, Start.  Without the chargen layers the old rows (hair, hair colour, skin, outfit colour)
 * and the turning 3D character are used.  Up/Down choose the row, Left/Right (or X) change it, X on Name opens the name screen. */
enum { C_NAME, C_GENDER, C_HAIR, C_HAIR_COL, C_SKIN, C_OUTFIT, C_PORTRAIT, C_START, C_ROWS };   /* the old rows and their ids */
enum { R_NAME, R_GENDER, R_CAT, R_OLD, R_PORTRAIT, R_START };
typedef struct { int kind, arg; } CRow;
static CRow rows[20];
static int nrows, row;
static float spin;
static int cg_t;
static unsigned cg_sig = ~0u;                 /* the choice the hero page was composed for */
extern int jm_name_entry_requested;
static const char *const row_key[C_ROWS] = {"creation.rows.name", "creation.rows.gender", "creation.rows.hair", "creation.rows.hair_colour",
                                            "creation.rows.skin", "creation.rows.outfit_colour", "creation.rows.portrait", "creation.rows.start"};
static const int nopt[C_ROWS] = {0, 2, 3, 5, 3, 5, 4, 0};

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

static void build_rows(void)
{
    int c;
    nrows = 0;
    rows[nrows].kind = R_NAME; rows[nrows++].arg = 0;
    rows[nrows].kind = R_GENDER; rows[nrows++].arg = 0;
    if (Cg_Ready()) for (c = 0; c < Cg_CatCount() && nrows < 16; c++) { rows[nrows].kind = R_CAT; rows[nrows++].arg = c; }
    else { static const int old[4] = {C_HAIR, C_HAIR_COL, C_SKIN, C_OUTFIT}; for (c = 0; c < 4; c++) { rows[nrows].kind = R_OLD; rows[nrows++].arg = old[c]; } }
    rows[nrows].kind = R_PORTRAIT; rows[nrows++].arg = 0;
    rows[nrows].kind = R_START; rows[nrows++].arg = 0;
}

void Ui_StartCreate(void)
{
    row = 0;
    spin = 0;
    cg_t = 0;
    cg_sig = ~0u;
    Cg_Defaults();
    build_rows();
}

static int option(int r)
{
    switch (r) {
    case C_GENDER: return jm.gender;
    case C_HAIR: return jm.hair;
    case C_HAIR_COL: return jm.hair_col;
    case C_SKIN: return jm.skin;
    case C_OUTFIT: return jm.outfit;
    case C_PORTRAIT: return jm.portrait;
    }
    return 0;
}

static void set_option(int r, int v)
{
    switch (r) {
    case C_GENDER: jm.gender = v; break;
    case C_HAIR: jm.hair = v; break;
    case C_HAIR_COL: jm.hair_col = v; break;
    case C_SKIN: jm.skin = v; break;
    case C_OUTFIT: jm.outfit = v; break;
    case C_PORTRAIT: jm.portrait = v; break;
    }
}

static int row_id(const CRow *r)       /* the old row id of a fixed row */
{
    return r->kind == R_GENDER ? C_GENDER : r->kind == R_PORTRAIT ? C_PORTRAIT : r->kind == R_OLD ? r->arg : -1;
}

static void change(int d)
{
    CRow *r = &rows[row];
    if (r->kind == R_CAT) {
        int c = r->arg, tries = Cg_OptCount(c);
        Cg_Set(c, Cg_Get(c) + d);
        while (Cg_Avoided() && tries-- > 0) Cg_Set(c, Cg_Get(c) + d);        /* skip hair + accessory pairs the art marks as clashing */
        cg_t = 0;
    }
    else if (row_id(r) >= 0 && nopt[row_id(r)]) { int id = row_id(r); set_option(id, (option(id) + d + nopt[id]) % nopt[id]); }
}

int Ui_CreateInput(unsigned short edge)
{
    if (!nrows) build_rows();
    if (edge & PAD_UP) row = (row + nrows - 1) % nrows;
    if (edge & PAD_DOWN) row = (row + 1) % nrows;
    if (edge & PAD_LEFT) change(-1);
    if (edge & PAD_RIGHT) change(1);
    if (edge & PAD_CROSS) {
        if (rows[row].kind == R_NAME) jm_name_entry_requested = 1;
        else if (rows[row].kind == R_START) { if (jm.name[0]) return 1; }
        else change(1);
    }
    return 0;
}

void Ui_RefreshName(void)
{
    const char *n = HdText_PlayerName();
    if (n && n[0]) { strncpy(jm.name, n, sizeof(jm.name) - 1); jm.name[sizeof(jm.name) - 1] = 0; }
}

/* In the frame hook: a podium, the turning character and the chosen portrait.  With the chargen layers the character is the
 * layered sprite (composed into the hero's bank page whenever the choice changes), shown big, walking and turning to all four sides. */
void Ui_DrawCreate(void)
{
    int colours[5];
    static float cx, cz;
    Mesh *m = Cg_Ready() ? NULL : Gfx_Mesh(Ui_BodyMesh());
    float sx[4], sy[4], d;
    unsigned char rgb[4][3];
    int k;
    spin += 0.035f;
    cx = 0; cz = 0;
    cam_x = cx - 52; cam_z = cz + 14; cam_d = 250;
    Gfx_Backdrop(0x16103C, 0x3A2C66);
    {
        float pts[4][2] = {{-40, -40}, {40, -40}, {-40, 40}, {40, 40}};
        for (k = 0; k < 4; k++) {
            Gfx_Project(cx + pts[k][0], 0, cz + pts[k][1], &sx[k], &sy[k], &d);
            rgb[k][0] = 150; rgb[k][1] = 140; rgb[k][2] = 160;
        }
        Gfx_GroundQuad(sx, sy, TX_MARBLE, rgb);
    }
    Ui_BodyColours(colours);
    if (m) Gfx_DrawMesh(m, 0, cx, 0, cz, spin, 1.15f, colours, 0);
    Gfx_Shadow(cx, cz + (Cg_Ready() ? 18 : 0), 22);
    if (Cg_Ready()) {
        static const int turn[4] = {0, 2, 3, 1};            /* down, right, up, left */
        float px, py, pd;
        int dir = turn[(cg_t / 110) & 3], fr = 1 + (cg_t / 6) % 4, sc = 2;
        if (cg_sig != Cg_Signature()) { Cg_Compose(13, 2); cg_sig = Cg_Signature(); LOG("journey: creator look %d %d %d %d %d %d %d", jm.cg[0], jm.cg[1], jm.cg[2], jm.cg[3], jm.cg[4], jm.cg[5], jm.cg[6]); }
        cg_t++;
        Gfx_Project(cx, 0, cz + 18, &px, &py, &pd);              /* a step in front of the podium's middle: the big sprite must fit under the top */
        Gfx_SpriteQuad((int)(px + 0.5f) - 24 * sc, (int)(py + 0.5f) - 56 * sc, 48 * sc, 62 * sc, 13, 2, fr * 48, dir * 64, 48, 62, pd);
        Gfx_End();
        Gfx_Portrait(258, 10, 52, PORT_X + jm.portrait * 48, PORT_Y);
        return;
    }
    Gfx_End();
    Gfx_Portrait(14, 146, 52, PORT_X + jm.portrait * 48, PORT_Y);
}

void Ui_CreateOverlay(void)
{
    int i, x, y, w, h, lh;
    char buf[40];
    metrics();
    if (!nrows) build_rows();
    lh = line_h();
    w = 2 * ui_w / 5;
    x = ui_w / 32;
    y = ui_top + ui_vis / 20;
    h = lh * (nrows + 3);
    panel(x, y, w, h);
    text(x + 12 * ui_s, y + lh / 2 + 2, Tr("creation.heading"), 0xFFE9A0);
    for (i = 0; i < nrows; i++) {
        int ry = y + lh * (i + 2) - lh / 2 + 4;
        unsigned on = i == row ? 0x40E0E0 : 0xB8B8B8;
        const char *val = "", *lab = "";
        const CRow *r = &rows[i];
        switch (r->kind) {
        case R_NAME: lab = Tr(row_key[C_NAME]); val = jm.name; break;
        case R_GENDER: lab = Tr(row_key[C_GENDER]); val = Tr(jm.gender ? "creation.gender.female" : "creation.gender.male"); break;
        case R_PORTRAIT: lab = Tr(row_key[C_PORTRAIT]); val = TrAt("creation.portraits", jm.portrait % 4, "?"); break;
        case R_START: lab = Tr(row_key[C_START]); break;
        case R_CAT: lab = Cg_CatLabel(r->arg); val = Cg_OptCount(r->arg) ? Cg_OptLabel(r->arg, Cg_Get(r->arg)) : "-"; break;
        case R_OLD:
            lab = Tr(row_key[r->arg]);
            switch (r->arg) {
            case C_HAIR: val = TrAt("creation.hair_styles", jm.hair % 3, "?"); break;
            case C_HAIR_COL: val = TrAt("creation.hair_colours", jm.hair_col % 5, "?"); break;
            case C_SKIN: val = TrAt("creation.skins", jm.skin % 3, "?"); break;
            case C_OUTFIT: val = TrAt("creation.outfit_colours", jm.outfit % 5, "?"); break;
            }
            break;
        }
        if (i == row) text(x + 6 * ui_s, ry, ">", 0xFFFFFF);
        text(x + 22 * ui_s, ry, lab, on);
        text(x + w * 11 / 20, ry, val, i == row ? 0xFFFFFF : 0x909090);
    }
    snprintf(buf, sizeof(buf), "%s", Tr(rows[row].kind == R_NAME ? "creation.hint_name" : rows[row].kind == R_START ? "creation.hint_begin" : "creation.hint_change"));
    text(x + 12 * ui_s, y + h - lh / 2, buf, 0x8890C0);
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
    return (unsigned)(row * 31 + msel * 131 + msub * 1009 + qsel * 17 + jm.gender * 3 + jm.hair * 5 + jm.hair_col * 7 + jm.skin * 11 +
                      jm.outfit * 13 + jm.portrait * 19 + (int)jm.name[0] * 23 + (int)jm.name[1] * 29 + Lang_Current() * 37 + Dev_BarOn() * 43 + (int)Cg_Signature() * 47) +
           (unsigned)jm.eco.coins * 1009u + (unsigned)jm.eco.xp * 7919u;
}
