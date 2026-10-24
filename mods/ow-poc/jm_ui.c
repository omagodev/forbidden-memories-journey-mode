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

char ui_message[48];
int ui_message_timer;
void Ui_Message(const char *s) { strncpy(ui_message, s, sizeof(ui_message) - 1); ui_message_timer = 120; }
const char *Ui_MessageText(void) { return ui_message_timer > 0 ? ui_message : NULL; }

/* -------------------------------------------------------- character creator */
enum { C_NAME, C_GENDER, C_HAIR, C_HAIR_COL, C_SKIN, C_OUTFIT, C_PORTRAIT, C_START, C_ROWS };
static int row;
static float spin;
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

void Ui_StartCreate(void)
{
    row = 0;
    spin = 0;
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

int Ui_CreateInput(unsigned short edge)
{
    if (edge & PAD_UP) row = (row + C_ROWS - 1) % C_ROWS;
    if (edge & PAD_DOWN) row = (row + 1) % C_ROWS;
    if (edge & (PAD_LEFT | PAD_RIGHT)) {
        int d = (edge & PAD_LEFT) ? -1 : 1;
        if (nopt[row]) set_option(row, (option(row) + d + nopt[row]) % nopt[row]);
    }
    if (edge & PAD_CROSS) {
        if (row == C_NAME) jm_name_entry_requested = 1;
        else if (row == C_START && jm.name[0]) return 1;
        else if (nopt[row]) set_option(row, (option(row) + 1) % nopt[row]);
    }
    return 0;
}

void Ui_RefreshName(void)
{
    const char *n = HdText_PlayerName();
    if (n && n[0]) { strncpy(jm.name, n, sizeof(jm.name) - 1); jm.name[sizeof(jm.name) - 1] = 0; }
}

/* In the frame hook: a podium, the turning character and the chosen portrait. */
void Ui_DrawCreate(void)
{
    int colours[5];
    static float cx, cz;
    Mesh *m = Gfx_Mesh(Ui_BodyMesh());
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
    Gfx_Shadow(cx, cz, 22);
    Gfx_End();
    Gfx_Portrait(14, 146, 52, PORT_X + jm.portrait * 48, PORT_Y);
}

void Ui_CreateOverlay(void)
{
    int i, x, y, w, h, lh;
    char buf[40];
    metrics();
    lh = line_h();
    w = 2 * ui_w / 5;
    x = ui_w / 32;
    y = ui_top + ui_vis / 14;
    h = lh * (C_ROWS + 3);
    panel(x, y, w, h);
    text(x + 12 * ui_s, y + lh / 2 + 2, Tr("creation.heading"), 0xFFE9A0);
    for (i = 0; i < C_ROWS; i++) {
        int ry = y + lh * (i + 2) - lh / 2 + 4;
        unsigned on = i == row ? 0x40E0E0 : 0xB8B8B8;
        const char *val = "";
        switch (i) {
        case C_NAME: val = jm.name; break;
        case C_GENDER: val = Tr(jm.gender ? "creation.gender.female" : "creation.gender.male"); break;
        case C_HAIR: val = TrAt("creation.hair_styles", jm.hair % 3, "?"); break;
        case C_HAIR_COL: val = TrAt("creation.hair_colours", jm.hair_col % 5, "?"); break;
        case C_SKIN: val = TrAt("creation.skins", jm.skin % 3, "?"); break;
        case C_OUTFIT: val = TrAt("creation.outfit_colours", jm.outfit % 5, "?"); break;
        case C_PORTRAIT: val = TrAt("creation.portraits", jm.portrait % 4, "?"); break;
        }
        if (i == row) text(x + 6 * ui_s, ry, ">", 0xFFFFFF);
        text(x + 22 * ui_s, ry, Tr(row_key[i]), on);
        text(x + w / 2, ry, val, i == row ? 0xFFFFFF : 0x909090);
    }
    snprintf(buf, sizeof(buf), "%s", Tr(row == C_NAME ? "creation.hint_name" : row == C_START ? "creation.hint_begin" : "creation.hint_change"));
    text(x + 12 * ui_s, y + h - lh / 2, buf, 0x8890C0);
}

unsigned Ui_Signature(void);

/* --------------------------------------------------------------- START menu */
enum { M_DECK, M_ITEMS, M_STATUS, M_SAVE, M_LANG, M_TITLE, M_CLOSE, M_COUNT };
static const int menu_text[M_COUNT] = {0, 1, 2, 3, -1, 4, 5};      /* index in ui "menu.items"; the language row is made */
static int msel, msub, qsel;

static const char *menu_name(int i, char *buf, size_t size)
{
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
        int px = x + w + 8 * ui_s, pw = ui_w / 2, ph = lh * 11, py = y;
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
                      jm.outfit * 13 + jm.portrait * 19 + (int)jm.name[0] * 23 + (int)jm.name[1] * 29 + Lang_Current() * 37);
}
