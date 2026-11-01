/* The backpack (Mochila): the START menu's page of what the story gave.
 *
 * Two tabs: the items the story's flags hold now (journey.json "items", each with its own 24x24 icon) and the cards the
 * story's duelists gave (jm.got_cards less the shop's).  A grid to move over; X opens the details of the chosen one
 * (a big icon or the card's picture, its text and where it came from); S or Triangle goes back.  Drawn in the shop's
 * ornate style, in 1280x720 design units.  The texts are in the language's ui.json "bag" block, keyed by the item's flag. */
#include "jm.h"
#include <stdio.h>
#include <string.h>

extern int Cards_Type(int id);
extern int Cards_Level(int id);
extern int gDuel_adwCardStats[];

#define COLS 4
#define ROWS 3
#define GOLD 0xF0C850u
#define SOFT 0xC8C4E8u
#define DIM 0x7A76A0u
#define WHITE 0xFFFFFFu

static int tab, sel, top, detail;
static int list[48], count;
static int w, h, s, vtop, vis;

static int X(int v) { return Ui_DX(v); }
static int Y(int v) { return Ui_DY(v); }
static int S(int v) { return Ui_DS(v); }
static const char *T(const char *k) { return Jm_L1(Tr(k)); }

static void refresh(void)
{
    count = tab ? Story_GotCards(list, 48) : Story_Items(list, 48);
    if (sel >= count) sel = count ? count - 1 : 0;
    if (sel < top * COLS) top = sel / COLS;
    if (sel >= (top + ROWS) * COLS) top = sel / COLS - ROWS + 1;
}

void Bag_Open(void) { tab = 0; sel = 0; top = 0; detail = 0; refresh(); }

/* 1 when the backpack closes */
int Bag_Input(unsigned short edge)
{
    refresh();
    if (detail) {
        if (edge & (PAD_CIRCLE | PAD_TRIANGLE | PAD_CROSS)) detail = 0;
        return 0;
    }
    if (edge & (PAD_CIRCLE | PAD_TRIANGLE | PAD_START)) return 1;
    if (edge & (PAD_L1 | PAD_L2 | PAD_R1 | PAD_R2)) { tab ^= 1; sel = 0; top = 0; refresh(); return 0; }
    if (!count) return 0;
    if ((edge & PAD_LEFT) && sel > 0) sel--;
    if ((edge & PAD_RIGHT) && sel + 1 < count) sel++;
    if ((edge & PAD_UP) && sel >= COLS) sel -= COLS;
    if ((edge & PAD_DOWN) && sel + COLS < count) sel += COLS;
    if (edge & PAD_CROSS) detail = 1;
    refresh();
    return 0;
}

/* a label cut to a width, never ending on an accent */
static void fit(int x, int my, int maxw, const char *t, unsigned rgb, int sc)
{
    char b[96];
    size_t n;
    snprintf(b, sizeof(b), "%s", t);
    n = strlen(b);
    if (jm_host->text_width(jm_host, b, sc) > maxw) {
        while (n > 1 && jm_host->text_width(jm_host, b, sc) > maxw - jm_host->text_width(jm_host, "..", sc)) b[--n] = 0;
        while (n > 1 && ((unsigned char)b[n - 1] >= 0x80 || b[n - 1] == ' ')) b[--n] = 0;
        snprintf(b + n, sizeof(b) - n, "..");
    }
    jm_host->draw_text(jm_host, x, my, b, rgb, sc);
}

/* text wrapped into a box, line by line; the y after it */
static int para(int x, int y, int maxw, const char *t, unsigned rgb, int sc, int lh, int maxl)
{
    char line[128];
    int n = 0;
    while (*t && n < maxl) {
        int len = 0, last = -1;
        while (t[len] && len < 120) {
            memcpy(line, t, (size_t)len + 1); line[len + 1] = 0;
            if (jm_host->text_width(jm_host, line, sc) > maxw) break;
            if (t[len] == ' ') last = len;
            len++;
        }
        if (t[len] && last > 0) len = last;
        memcpy(line, t, (size_t)len); line[len] = 0;
        jm_host->draw_text(jm_host, x, y, line, rgb, sc);
        y += lh; n++;
        t += len;
        while (*t == ' ') t++;
    }
    return y;
}

/* 12x12 backpack for the header: '#' main, '+' light */
static const char *const ICON_BAG[12] = {"....####....", "...#....#...", "..########..", ".#++++++++#.", "#+########+#", "#+#++++++#+#", "#+#+####+#+#", "#+#+#++#+#+#", "#+########+#", "#++++++++++#", ".##########.", "............"};
static void icon12(const char *const pic[12], int cx, int cy, int z, unsigned main, unsigned light)
{
    int y, x;
    for (y = 0; y < 12; y++)
        for (x = 0; x < 12; x++) {
            char c = pic[y][x];
            if (c != '.') Ui_Fill(cx - 6 * z + x * z, cy - 6 * z + y * z, z, z, c == '#' ? main : light, 255);
        }
}

static const char *bag_text(int idx, const char *what)      /* "bag.<flag>.desc" or ".from", in the language */
{
    char k[64];
    snprintf(k, sizeof(k), "bag.%s.%s", Story_ItemKey(idx), what);
    return T(k);
}

static const char *name_of(int v, char *b, size_t n)
{
    if (tab) { b[0] = 0; Cards_NameUtf8(v, b, n); snprintf(b, n, "%s", Jm_L1(b)); }
    else if (Story_ItemCount(v) >= 0) snprintf(b, n, "%s x%d", Jm_L1(Story_ItemName(v)), Story_ItemCount(v));
    else snprintf(b, n, "%s", Jm_L1(Story_ItemName(v)));
    return b;
}

static void tile(int x, int y, int tw_, int th, int v, int chosen)
{
    char b[48];
    int ss = Ui_SmallS(), cx = x + tw_ / 2, area = th - S(34);
    if (chosen) {
        Ui_Frame(x - S(4), y - S(4), tw_ + S(8), th + S(8), S(3), GOLD, 70);
        Ui_VGrad(x, y, tw_, th, 0x3A346E, 0x221E52, 245);
        Ui_Frame(x, y, tw_, th, S(2), GOLD, 255);
        Ui_Fill(x + S(2), y + S(2), tw_ - S(4), S(1), 0xFFF0B0, 200);
    } else {
        Ui_Fill(x, y, tw_, th, 0x15143C, 225);
        Ui_Frame(x, y, tw_, th, S(1), 0x34346A, 255);
    }
    if (tab) {
        int aw = area * 102 / 96 - S(8), ah = area - S(12), ax = cx - aw / 2, ay = y + S(8);
        Ui_Fill(ax - S(3), ay - S(3), aw + S(6), ah + S(6), Jm_TypeFrame(v), 255);
        if (!Jm_CardArt(v, 0, ax, ay, aw, ah)) Ui_Fill(ax, ay, aw, ah, 0x202040, 255);
    } else {
        int px = (area - S(8)) / 24;
        if (px < 1) px = 1;
        Ui_Disc(cx, y + S(6) + area / 2, area / 2 - S(4), area / 2 - S(10), 0x0A0A22, 160);
        Jm_ItemIcon(cx - 12 * px, y + S(4) + area / 2 - 12 * px, px, Story_ItemFile(v));
    }
    fit(x + S(8), y + th - S(18), tw_ - S(16), name_of(v, b, sizeof(b)), chosen ? WHITE : SOFT, ss);
}

static void header(void)
{
    int hh = S(92), y0 = vtop, ss = Ui_SmallS();
    char b[48];
    Ui_VGrad(0, y0, w, hh, 0x221E5A, 0x0E0C2C, 245);
    Ui_Fill(0, y0 + hh - S(4), w, S(3), 0xB08A30, 255);
    Ui_Fill(0, y0 + hh - S(4), w, S(1), 0xFFE8A0, 255);
    icon12(ICON_BAG, X(60), y0 + S(46), S(4), 0xC08A40, 0x7A4A20);
    Ui_TextSh(X(100), y0 + S(32), T("bag.title"), GOLD, s + 1);
    fit(X(102), y0 + S(64), X(700), T("bag.subtitle"), SOFT, ss);
    snprintf(b, sizeof(b), "%s", Jm_L1(jm.name));
    Ui_Pill(X(1010), y0 + S(22), X(250), S(46), 0, 0);
    Ui_TextC(X(1135), y0 + S(45), b, GOLD, s);
}

static void tabs(int px, int pw)
{
    int i, tw_ = (pw - S(48)) / 2;
    int n[2];
    int tmp[48];
    n[0] = Story_Items(tmp, 48);
    n[1] = Story_GotCards(tmp, 48);
    for (i = 0; i < 2; i++) {
        char b[64];
        int x = px + S(16) + i * (tw_ + S(16)), y = Y(110);
        snprintf(b, sizeof(b), "%s (%d)", T(i ? "bag.tab_cards" : "bag.tab_items"), n[i]);
        Ui_Pill(x, y, tw_, S(42), tab == i, tab == i);
        Ui_TextC(x + tw_ / 2, y + S(21), b, tab == i ? 0x2A1A04 : SOFT, s);
    }
}

static void grid(void)
{
    int px = X(30), py = Y(100), pw = X(820), ph = S(530), i;
    int gx = px + S(20), gy = Y(168), gw = pw - S(40), tw_ = (gw - S(16) * (COLS - 1)) / COLS, th = S(140);
    Ui_OPanel(px, py, pw, ph, 1);
    tabs(px, pw);
    if (!count) { Ui_TextC(px + pw / 2, gy + S(150), T(tab ? "bag.no_cards" : "menu.items_empty"), SOFT, s); return; }
    for (i = top * COLS; i < count && i < (top + ROWS) * COLS; i++) {
        int k = i - top * COLS;
        tile(gx + (k % COLS) * (tw_ + S(16)), gy + (k / COLS) * (th + S(14)), tw_, th, list[i], i == sel);
    }
}

/* the right side: what the chosen one is, in short */
static void side(void)
{
    int px = X(870), py = Y(100), pw = X(380), ph = S(530), cx = px + pw / 2, ss = Ui_SmallS(), lh = S(22);
    char b[96];
    Ui_OPanel(px, py, pw, ph, 0);
    if (!count) { Ui_TextC(cx, py + ph / 2, T("bag.hint_empty"), DIM, ss); return; }
    if (tab) {
        int v = list[sel], aw = S(204), ah = aw * 96 / 102;
        Ui_Fill(cx - aw / 2 - S(4), py + S(24) - S(4), aw + S(8), ah + S(8), Jm_TypeFrame(v), 255);
        if (!Jm_CardArt(v, 1, cx - aw / 2, py + S(24), aw, ah)) Ui_Fill(cx - aw / 2, py + S(24), aw, ah, 0x202040, 255);
        fit(px + S(20), py + S(24) + ah + S(30), pw - S(40), name_of(v, b, sizeof(b)), WHITE, s);
        Jm_CardLine(v, b, sizeof(b));
        fit(px + S(20), py + S(24) + ah + S(58), pw - S(40), b, SOFT, ss);
    } else {
        int v = list[sel], px_ = 8;
        Ui_Disc(cx, py + S(130), S(104), S(104), 0x0A0A22, 200);
        Ui_Ring(cx, py + S(130), S(104), S(104), S(2), 0xB08A30, 255);
        Jm_ItemIcon(cx - 12 * S(px_), py + S(130) - 12 * S(px_), S(px_), Story_ItemFile(v));
        fit(px + S(20), py + S(268), pw - S(40), name_of(v, b, sizeof(b)), WHITE, s);
        para(px + S(20), py + S(300), pw - S(40), bag_text(v, "desc"), SOFT, ss, lh, 6);
    }
    Ui_Pill(px + S(20), py + ph - S(60), pw - S(40), S(42), 1, 1);
    snprintf(b, sizeof(b), "X  %s", T("bag.details"));
    Ui_TextC(cx, py + ph - S(39), b, 0x2A1A04, s);
}

/* X: the details, over the rest */
static void details(void)
{
    int pw = X(860), ph = S(470), px = (w - pw) / 2, py = vtop + (vis - ph) / 2, ss = Ui_SmallS(), lh = S(24);
    int v = list[sel], tx = px + S(300), tw_ = pw - S(330), y;
    char b[128], nm[64];
    Ui_Fill(0, vtop, w, vis, 0x000000, 150);
    Ui_OPanel(px, py, pw, ph, 1);
    if (tab) {
        int aw = S(250), ah = aw * 96 / 102, ax = px + S(28), ay = py + S(40);
        Ui_Fill(ax - S(6), ay - S(6), aw + S(12), ah + S(12), Jm_TypeFrame(v), 255);
        if (!Jm_CardArt(v, 1, ax, ay, aw, ah)) Ui_Fill(ax, ay, aw, ah, 0x202040, 255);
        Jm_CardBadge(ax, ay + ah + S(18), v);
    } else {
        int z = S(10), cx = px + S(150), cy = py + S(170);
        Ui_Disc(cx, cy, S(128), S(128), 0x0A0A22, 220);
        Ui_Ring(cx, cy, S(128), S(128), S(3), 0xB08A30, 255);
        Jm_ItemIcon(cx - 12 * z, cy - 12 * z, z, Story_ItemFile(v));
    }
    y = py + S(46);
    Ui_TextSh(tx, y, name_of(v, nm, sizeof(nm)), GOLD, s + 1);
    y += S(40);
    if (tab) {
        int t = Cards_Type(v);
        Jm_CardLine(v, b, sizeof(b));
        fit(tx, y, tw_, b, SOFT, s); y += S(32);
        if (t >= 0 && t < 20) {
            unsigned st = (unsigned)gDuel_adwCardStats[v - 1];
            int lv = Cards_Level(v), k;
            snprintf(b, sizeof(b), "%s %d   %s %d", T("shop.atk"), (int)(st & 0x1FF) * 10, T("shop.def"), (int)(st >> 9 & 0x1FF) * 10);
            fit(tx, y, tw_, b, WHITE, s); y += S(32);
            Ui_Fmt1(b, sizeof(b), T("bag.level"), lv);
            fit(tx, y, tw_, b, SOFT, ss);
            for (k = 0; k < lv && k < 12; k++) Ui_Disc(tx + S(110) + k * S(16), y, S(6), S(6), 0xF0B030, 255);
            y += S(32);
        }
        snprintf(nm, sizeof(nm), "%s", Jm_L1(Story_CardGiver(v) ? Story_CardGiver(v) : "?"));
        snprintf(b, sizeof(b), T("bag.card_from"), nm);
        y += S(10);
        para(tx, y, tw_, b, 0x8CD08C, s, lh + S(4), 3);
    } else {
        y = para(tx, y, tw_, bag_text(v, "desc"), WHITE, s, lh + S(4), 7);
        y += S(14);
        Ui_Fill(tx, y - S(10), tw_, S(1), 0x5A5A90, 255);
        snprintf(b, sizeof(b), "%s", T("bag.origin"));
        fit(tx, y + S(6), tw_, b, GOLD, ss);
        para(tx, y + S(34), tw_, bag_text(v, "from"), 0x8CD08C, ss, lh, 3);
    }
    snprintf(b, sizeof(b), "S  %s", T("bag.back"));
    Ui_Pill(px + pw - S(200), py + ph - S(58), S(176), S(40), 0, 0);
    Ui_TextC(px + pw - S(112), py + ph - S(38), b, WHITE, s);
}

static void bottom(void)
{
    const char *k[8];
    int n = 0;
    k[n * 2] = "Q/E"; k[n * 2 + 1] = T("bag.k_tab"); n++;
    k[n * 2] = "<>^v"; k[n * 2 + 1] = T("bag.k_move"); n++;
    k[n * 2] = "X"; k[n * 2 + 1] = T("bag.details"); n++;
    k[n * 2] = "S"; k[n * 2 + 1] = T("bag.back"); n++;
    Ui_KeyBar(k, n, w / 2, Y(680), X(1100));
}

void Bag_Overlay(void)
{
    Ui_Metrics(&w, &h, &s, &vtop, &vis);
    refresh();
    Ui_VGrad(0, 0, w, h, 0x15123A, 0x07061A, 255);
    header();
    grid();
    side();
    bottom();
    if (detail && count) details();
}

unsigned Bag_Signature(void)
{
    return 40503u + (unsigned)(tab * 7 + sel * 131 + top * 17 + detail * 7919 + count * 31) + Jm_ArtLoads() * 2654435761u + (unsigned)Lang_Current() * 977u;
}
