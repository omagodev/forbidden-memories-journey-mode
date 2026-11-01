/* Journey Mode's shop screen, laid out like a console RPG card shop (the same ornate kit as the character creator).
 *
 *   top        the JOURNEY MODE plate, the shop icon, "Card Shop" and its subtitle, the level and the coins
 *   left       the card-shop interior (assets/ui/shop_bg.raw, tools/bake_shop_ui.py) with the keeper's own art
 *              (assets/shop_<keeper>.raw) and her name tag and words in the box at the bottom
 *   centre     tabs with icons (Cards, Packs, Sell), the filter and sort boxes, then the list: class badge, the
 *              card's real art from the disc as a thumbnail, name and type, copies owned, coin and price
 *   right      the chosen card big (its disc art in a card frame with ATK/DEF), name, type, a line about it,
 *              the quantity stepper, the total and the gold Buy / Sell button
 *   bottom     "< Back" and the key hints
 *
 *   Q / E (L1 / L2, also W = R1)  tab      Up/Down  row      Left/Right  quantity
 *   Z (Square)  filter      R (R2)  sort      X  buy or sell (then Yes/No)      S (Circle) or Triangle  leave
 *
 * What is on sale, what it costs and what a pack holds are data (assets/economy.json); this file only shows
 * them and asks for a yes.  Everything is drawn in the overlay (fills), so no texture bank is used. */
#include "jm.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

extern int Cards_NameUtf8(int id, char *out, size_t size);
extern int Cards_Type(int id);
extern int Cards_Level(int id);
extern int Cards_BaseId(int id);
extern int DiscArt_Read(int sector, void *out, int bytes);
extern int gDuel_adwCardStats[];

#define ROWS 7                          /* rows of the list on screen at once */
#define MAX_ITEMS 64
#define PACK_CARDS 8
#define SAY_LINES 3
#define SAY_COLS 36

enum { TAB_CARDS, TAB_PACKS, TAB_SELL, TABS };
enum { F_ALL, F_MONSTER, F_MAGIC, F_TRAP, F_OTHER, FILTERS };
enum { SORT_LOW, SORT_HIGH, SORT_NAME, SORTS };

static EcoItem items[MAX_ITEMS];
static int count, tab, sel, top, qty = 1, filter, sort_by;
static int asking;                      /* the Yes/No row is up */
static int ask_yes;
static char keeper[24];
static char said[SAY_LINES][SAY_COLS + 2];   /* what she is saying, already broken into lines */
static int said_hold;                   /* frames an answer stays before her greeting comes back */
static int pack_cards[PACK_CARDS], pack_count, pack_shown;
static unsigned generation;             /* changes whenever the screen's content does */

/* --------------------------------------------------------------- her words
 * The dialogue is written for a 3 x 32 box, so it is broken on spaces to that shape. */
static void say_text(const char *s)
{
    int line = 0, n = 0;
    memset(said, 0, sizeof(said));
    while (*s && line < SAY_LINES) {
        const char *word = s;
        int len = 0;
        while (word[len] && word[len] != ' ') len++;
        if (len > SAY_COLS) len = SAY_COLS;                  /* a word longer than the line: cut it */
        if (n && n + 1 + len > SAY_COLS) { line++; n = 0; if (line >= SAY_LINES) break; }
        if (n) said[line][n++] = ' ';
        memcpy(said[line] + n, word, (size_t)len);
        n += len;
        said[line][n] = 0;
        s = word + len;
        while (*s == ' ') s++;
    }
    generation++;
}

static void greet(void)
{
    const char *g = Eco_ShopGreet();
    said_hold = 0;
    say_text(g && *g ? g : Eco_ShopName());
}

/* Her answer to what just happened; it gives way to the greeting after a while. */
static void answer(const char *s)
{
    say_text(s);
    said_hold = 180;
}

/* ------------------------------------------------------------------ state */
static int card_type(int card) { return card > 0 ? Cards_Type(card) : -1; }
static int filter_ok(const EcoItem *it)
{
    int t = card_type(it->card);
    if (filter == F_ALL || it->kind == ECO_ITEM_PACK) return 1;
    if (t < 0) return 0;
    switch (filter) {
    case F_MONSTER: return t < 20;
    case F_MAGIC: return t == 20;
    case F_TRAP: return t == 21;
    default: return t >= 22;
    }
}
static int by_sort(const void *a, const void *b)
{
    const EcoItem *x = a, *y = b;
    if (sort_by == SORT_NAME) { int c = strcmp(x->name, y->name); if (c) return c; }
    if (x->price != y->price) return sort_by == SORT_HIGH ? y->price - x->price : x->price - y->price;
    return strcmp(x->name, y->name);
}
static void clamp_qty(void);
static void reload(void)
{
    static EcoItem all[MAX_ITEMS];
    int n = tab == TAB_PACKS ? Eco_PackItems(all, MAX_ITEMS)
          : tab == TAB_SELL ? Eco_SellItems(all, MAX_ITEMS)
          : Eco_ShopItems(all, MAX_ITEMS), i;
    count = 0;
    for (i = 0; i < n; i++) if (filter_ok(&all[i])) items[count++] = all[i];
    if (tab != TAB_PACKS && count > 1) qsort(items, (size_t)count, sizeof(items[0]), by_sort);
    if (sel >= count) sel = count > 0 ? count - 1 : 0;
    if (top > sel) top = sel;
    if (sel >= top + ROWS) top = sel - ROWS + 1;
    if (top > count - ROWS) top = count > ROWS ? count - ROWS : 0;
    if (top < 0) top = 0;
    clamp_qty();
    generation++;
}

/* how many of the chosen row may go in one go */
static int qty_max(void)
{
    const EcoItem *it;
    int m;
    if (count <= 0) return 1;
    it = &items[sel];
    if (tab == TAB_SELL) return it->owned > 0 ? it->owned : 1;
    if (it->kind != ECO_ITEM_CARD) return 1;
    m = it->price > 0 ? jm.eco.coins / it->price : 99;
    if (m > 99) m = 99;
    return m < 1 ? 1 : m;
}
static void clamp_qty(void)
{
    int m = qty_max();
    if (qty > m) qty = m;
    if (qty < 1) qty = 1;
}

const char *Shop_Keeper(void) { return keeper; }

void Shop_Open(void)
{
    snprintf(keeper, sizeof(keeper), "%s", Eco_ShopKeeper());
    Paint_ShopArt(keeper);
    tab = TAB_CARDS;
    sel = top = 0;
    qty = 1;
    filter = F_ALL;
    sort_by = SORT_LOW;
    asking = 0;
    ask_yes = 1;
    pack_count = pack_shown = 0;
    reload();
    greet();
}

/* ------------------------------------------------------------------ input */
static void confirm(void)
{
    EcoItem it = items[sel];
    int k, done = 0;
    if (tab == TAB_SELL) {
        for (k = 0; k < qty; k++) if (Eco_Sell(&it)) done++; else break;
        if (done) { answer(EcoTr("ui.shop_sold")); reload(); }
        else answer(EcoTr("ui.shop_no_spare"));
        return;
    }
    if (jm.eco.coins < it.price) { answer(EcoDlg("keeper_poor")); return; }
    if (it.kind == ECO_ITEM_PACK) {
        pack_count = Eco_OpenPack(it.bit, pack_cards, PACK_CARDS);
        if (pack_count <= 0) { answer(EcoTr("ui.shop_sold_out")); return; }
        if (!Eco_TakeCoins(it.price)) { pack_count = 0; answer(EcoDlg("keeper_poor")); return; }
        pack_shown = 0;                 /* the cards are given as they are turned over */
        answer(EcoTr("ui.shop_bought"));
        return;
    }
    for (k = 0; k < qty; k++) { if (jm.eco.coins < it.price || !Eco_Buy(&it)) break; done++; if (it.kind == ECO_ITEM_ONCE) break; }
    if (done) { answer(EcoTr("ui.shop_bought")); reload(); }
    else answer(EcoTr("ui.shop_sold_out"));
}

static void set_tab(int t)
{
    tab = (t + TABS) % TABS;
    sel = top = 0;
    qty = 1;
    reload();
}

int Shop_Input(unsigned short edge)
{
    if (said_hold > 0 && --said_hold == 0) greet();
    if (pack_count > 0) {               /* turning the pack over, one card at a time */
        if (edge & (PAD_CROSS | PAD_CIRCLE | PAD_START)) {
            if (pack_shown < pack_count) { Story_Cards(pack_cards[pack_shown]); pack_shown++; generation++; }
            else { pack_count = pack_shown = 0; reload(); greet(); }
        }
        return 0;
    }
    if (asking) {
        if (edge & (PAD_LEFT | PAD_RIGHT | PAD_UP | PAD_DOWN)) { ask_yes ^= 1; generation++; }
        if (edge & PAD_CROSS) { asking = 0; if (ask_yes) confirm(); generation++; }
        else if (edge & (PAD_CIRCLE | PAD_TRIANGLE)) { asking = 0; generation++; }
        return 0;
    }
    if (edge & (PAD_TRIANGLE | PAD_CIRCLE | PAD_START)) return 1;
    if (edge & PAD_L1) set_tab(tab - 1);
    if (edge & (PAD_L2 | PAD_R1)) set_tab(tab + 1);
    if (edge & PAD_SQUARE) { filter = (filter + 1) % FILTERS; sel = top = 0; reload(); }
    if (edge & PAD_R2) { sort_by = (sort_by + 1) % SORTS; sel = top = 0; reload(); }
    if ((edge & (PAD_UP | PAD_DOWN)) && count > 0) {
        sel = (sel + (edge & PAD_UP ? count - 1 : 1)) % count;
        if (sel < top) top = sel;
        if (sel >= top + ROWS) top = sel - ROWS + 1;
        qty = 1;
        generation++;
    }
    if (edge & (PAD_LEFT | PAD_RIGHT)) {
        int m = qty_max();
        qty += edge & PAD_LEFT ? -1 : 1;
        if (qty < 1) qty = m;
        if (qty > m) qty = 1;
        generation++;
    }
    if ((edge & PAD_CROSS) && count > 0) {
        EcoItem *it = &items[sel];
        if (it->locked) {
            char b[56];
            Ui_Fmt1(b, sizeof(b), EcoTr("ui.shop_need_level"), it->level_min);
            answer(b);
        } else { asking = 1; ask_yes = 1; generation++; }
    }
    return 0;
}

/* The overlay font draws one byte a glyph in Latin-1, so accented UTF-8 text is folded to it first. */
static const char *L1(const char *u)
{
    static char ring[8][96];
    static int at;
    char *o = ring[at = (at + 1) & 7];
    size_t n = 0;
    if (!u) return "";
    while (*u && n + 1 < sizeof(ring[0])) {
        unsigned char c = (unsigned char)*u;
        if (c < 0x80) { o[n++] = (char)c; u++; }
        else if ((c & 0xE0) == 0xC0 && u[1]) { unsigned v = (c & 0x1Fu) << 6 | ((unsigned char)u[1] & 0x3Fu); o[n++] = (char)(v < 256 ? v : '?'); u += 2; }
        else { o[n++] = '?'; u++; while ((*u & 0xC0) == 0x80) u++; }
    }
    o[n] = 0;
    return o;
}
static const char *T(const char *path) { return L1(Tr(path)); }
static const char *TA(const char *path, int i, const char *fb) { return L1(TrAt(path, i, fb)); }

/* ---------------------------------------------------------------- pictures */
#define OPAQUE 0x1000000u
/* the card's own picture from the disc: 102x96 texels through its 256-colour palette (as Paint_CardArt reads it) */
#define ART_W 102
#define ART_H 96
#define THUMB_W 34
#define THUMB_H 32
#define THUMBS 24
static struct { int card; unsigned px[THUMB_W * THUMB_H]; } thumbs[THUMBS];
static int thumb_next;
static int big_card = -1;
static unsigned big_px[ART_W * ART_H];
static unsigned art_loads;              /* goes up when a picture arrives, so the cached overlay is redrawn */

static unsigned rgb15(unsigned v) { return ((v & 31) * 255 / 31) << 16 | ((v >> 5 & 31) * 255 / 31) << 8 | ((v >> 10 & 31) * 255 / 31); }

static int read_art(int card, unsigned *out, int step, int ow, int oh)
{
    static unsigned char rec[7 * 2048];
    const unsigned short *clut;
    int base = Cards_BaseId(card), x, y;
    if (card < 1) return 0;
    if (base < 1) base = card;
    if (!DiscArt_Read((base - 1) * 7 + 722, rec, (int)sizeof(rec))) return 0;
    clut = (const unsigned short *)(rec + 0x2640);
    for (y = 0; y < oh; y++)
        for (x = 0; x < ow; x++) {
            int sx = x * step + step / 2, sy = y * step + step / 2;
            unsigned c = clut[rec[(sy < ART_H ? sy : ART_H - 1) * ART_W + (sx < ART_W ? sx : ART_W - 1)]] & 0x7FFF;
            out[y * ow + x] = rgb15(c) | OPAQUE;
        }
    art_loads++;
    return 1;
}
static const unsigned *thumb_of(int card)
{
    int i;
    for (i = 0; i < THUMBS; i++) if (thumbs[i].card == card) return thumbs[i].px;
    i = thumb_next;
    thumb_next = (thumb_next + 1) % THUMBS;
    if (!read_art(card, thumbs[i].px, 3, THUMB_W, THUMB_H)) { thumbs[i].card = 0; return NULL; }
    thumbs[i].card = card;
    return thumbs[i].px;
}
static const unsigned *big_of(int card)
{
    if (card == big_card) return big_px;
    if (!read_art(card, big_px, 1, ART_W, ART_H)) { big_card = -1; return NULL; }
    big_card = card;
    return big_px;
}

/* a picture (bit 24 = opaque) stretched into a box, one fill per run of equal texels */
static void picture(const unsigned *px, int w, int h, int dx, int dy, int dw, int dh)
{
    int y, x;
    if (!px || dw <= 0 || dh <= 0) return;
    for (y = 0; y < h; y++) {
        int y0 = dy + y * dh / h, y1 = dy + (y + 1) * dh / h;
        const unsigned *r = px + (size_t)y * w;
        if (y1 <= y0) continue;
        for (x = 0; x < w;) {
            int x1 = x + 1, sx0, sx1;
            if (!(r[x] & OPAQUE)) { x++; continue; }
            while (x1 < w && r[x1] == r[x]) x1++;
            sx0 = dx + x * dw / w; sx1 = dx + x1 * dw / w;
            if (sx1 > sx0) Ui_Fill(sx0, y0, sx1 - sx0, y1 - y0, r[x] & 0xFFFFFF, 255);
            x = x1;
        }
    }
}

/* the backdrop and the keeper's art, loaded once */
static unsigned char *bg;
static int bg_w, bg_h, bg_tried;
static unsigned *keeper_px;
static int keeper_w, keeper_h;
static char keeper_of[24];
static void load_pictures(void)
{
    long size;
    if (!bg_tried) {
        unsigned char *d = Jm_Slurp("assets/ui/shop_bg.raw", &size);
        bg_tried = 1;
        if (d && size > 8 && !memcmp(d, "CGB1", 4)) {
            bg_w = d[4] | d[5] << 8; bg_h = d[6] | d[7] << 8;
            if (size >= 8 + (long)bg_w * bg_h * 3) bg = d; else free(d);
        } else free(d);
    }
    if (strcmp(keeper_of, keeper)) {
        char file[48];
        unsigned char *d;
        int i;
        snprintf(keeper_of, sizeof(keeper_of), "%s", keeper);
        free(keeper_px); keeper_px = NULL; keeper_w = keeper_h = 0;
        snprintf(file, sizeof(file), "assets/shop_%s.raw", keeper);
        d = Jm_Slurp(file, &size);
        if (d && size > 4) {
            int w = d[0] | d[1] << 8, h = d[2] | d[3] << 8;
            if (w > 0 && h > 0 && size >= 4 + (long)w * h * 2 && (keeper_px = malloc((size_t)w * h * sizeof(unsigned))) != NULL) {
                for (i = 0; i < w * h; i++) {
                    unsigned v = d[4 + i * 2] | d[5 + i * 2] << 8;
                    keeper_px[i] = v ? rgb15(v) | OPAQUE : 0;
                }
                keeper_w = w; keeper_h = h;
            }
        }
        free(d);
    }
}
static void backdrop(void)
{
    int w, h, x, y;
    Ui_Metrics(&w, &h, NULL, NULL, NULL);
    Ui_Fill(0, 0, w, h, 0x07061A, 255);
    if (!bg) return;
    {
        int cw = w, ch = w * bg_h / bg_w, ox = 0, oy;
        if (ch < h) { ch = h; cw = h * bg_w / bg_h; ox = (w - cw) / 2; }
        oy = (h - ch) / 2;
        for (y = 0; y < bg_h; y++) {
            int sy = oy + y * ch / bg_h, sh = oy + (y + 1) * ch / bg_h - sy;
            const unsigned char *r = bg + 8 + (size_t)y * bg_w * 3;
            for (x = 0; x < bg_w; x++) {
                int sx = ox + x * cw / bg_w, sw = ox + (x + 1) * cw / bg_w - sx;
                if (sw > 0 && sh > 0) Ui_Fill(sx, sy, sw, sh, (unsigned)(r[x * 3] << 16 | r[x * 3 + 1] << 8 | r[x * 3 + 2]), 255);
            }
        }
    }
}

/* ---------------------------------------------------------------- drawing */
#define GOLD 0xFFE9A0u
#define GOLD_D 0xC09032u
#define WHITE 0xF4F2FFu
#define SOFT 0xB8B4DCu
#define DIM 0x6E6A96u
#define RED 0xE06A6Au
#define GREEN 0x8CD08Cu

static int S(int v) { return Ui_DS(v); }
static void fit(int x, int my, int maxw, const char *t, unsigned rgb, int sc)    /* a label cut (not shrunk) to a width */
{
    char b[96];
    size_t n;
    snprintf(b, sizeof(b), "%s", t);
    n = strlen(b);
    if (jm_host->text_width(jm_host, b, sc) > maxw) {
        while (n > 1 && jm_host->text_width(jm_host, b, sc) > maxw - jm_host->text_width(jm_host, "..", sc)) b[--n] = 0;
        while (n > 1 && ((unsigned char)b[n - 1] >= 0x80 || b[n - 1] == ' ')) b[--n] = 0;   /* never end on an accent or a space */
        snprintf(b + n, sizeof(b) - n, "..");
    }
    jm_host->draw_text(jm_host, x, my, b, rgb, sc);
}
static int X(int v) { return Ui_DX(v); }
static int Y(int v) { return Ui_DY(v); }
static int tw(const char *t, int sc) { return jm_host->text_width(jm_host, t, sc); }
static void txt(int x, int my, const char *t, unsigned rgb, int sc) { jm_host->draw_text(jm_host, x, my, t, rgb, sc); }
static void txt_r(int xr, int my, const char *t, unsigned rgb, int sc) { txt(xr - tw(t, sc), my, t, rgb, sc); }

static void coin(int cx, int cy, int r)
{
    Ui_Disc(cx, cy + S(1), r, r, 0x3A2606, 200);
    Ui_Disc(cx, cy, r, r, 0xB07818, 255);
    Ui_Disc(cx, cy, r - S(2), r - S(2), 0xF2C440, 255);
    Ui_Disc(cx - r / 4, cy - r / 4, r / 3, r / 3, 0xFFF0B0, 255);
    Ui_Fill(cx - S(1), cy - r / 2, S(2), r, 0xB07818, 255);
}

/* 12x12 pixel icons: '#' main, '+' light, '.' clear */
static const char *const ICON_SHOP[12] = {"############", "#+#+#+#+#+##", "############", ".#........#.", ".#.##..##.#.", ".#.##..##.#.", ".#........#.", ".#.######.#.", ".#.#++++#.#.", ".#.#++++#.#.", "############", "............"};
static const char *const ICON_TAB[TABS][12] = {
    {"....####....", "...#++++#...", "..#+####+#..", "..#+#..#+##.", ".##+#..#+#+#", "#+#+####+#+#", "#+#++++++#+#", "#+.######.+#", "#+++++++++##", ".#++++++++#.", "..########..", "............"},   /* cards */
    {"....####....", "..##++++##..", ".#++####++#.", "#+##....##+#", "#+#.####.#+#", "#+#.#++#.#+#", "#+#.#++#.#+#", "#+#.####.#+#", "#+##....##+#", ".#++####++#.", "..########..", "............"},   /* pack */
    {"...######...", "..#++++++#..", "...######...", "..#++++++#..", "...######...", ".#+++++++#..", "..#######...", ".#++++++++#.", "..########..", ".#+++++++++#", "..#########.", "............"},   /* coins */
};
static const char *const ICON_CART[12] = {"##..........", ".#..........", ".##########.", ".#+++++++#..", ".#+++++++#..", "..#+++++#...", "..#######...", "...#....#...", "..###..###..", "..###..###..", "............", "............"};
static void icon12(const char *const pic[12], int cx, int cy, int z, unsigned main, unsigned light)
{
    int y, x;
    for (y = 0; y < 12; y++)
        for (x = 0; x < 12; x++) {
            char c = pic[y][x];
            if (c != '.') Ui_Fill(cx - 6 * z + x * z, cy - 6 * z + y * z, z, z, c == '#' ? main : light, 255);
        }
}

/* the class badge: C grey, B blue, A purple, S gold; N when the card has none */
static void badge(int x, int y, int card)
{
    static const char *const L[4] = {"C", "B", "A", "S"};
    static const unsigned F[4] = {0x5A5A70, 0x2850C0, 0x7A38B8, 0xC89020};
    int c = card > 0 ? Eco_CardClass(card) : -1, w = S(26), h = S(22);
    unsigned f = c >= 0 && c < 4 ? F[c] : 0x4A4A62;
    Ui_Fill(x, y, w, h, 0x0A0A1C, 255);
    Ui_Fill(x + S(1), y + S(1), w - S(2), h - S(2), f, 255);
    Ui_Fill(x + S(1), y + S(1), w - S(2), S(1), 0xFFFFFF, 90);
    Ui_TextC(x + w / 2, y + h / 2, c >= 0 && c < 4 ? L[c] : "N", 0xFFFFFF, Ui_SmallS());
}

static unsigned type_frame(int t)
{
    if (t < 0) return 0x8A6A30;
    if (t < 20) return 0xC8843A;
    if (t == 20) return 0x2E9A80;
    if (t == 21) return 0xB0407A;
    if (t == 22) return 0x3A62C0;
    return 0x4A9A3A;
}
static const char *type_line(int card, char *b, size_t n)
{
    int t = card_type(card);
    if (t < 0) { snprintf(b, n, "%s", T("shop.pack")); return b; }
    if (t < 20) snprintf(b, n, "%s / %s", T("shop.monster"), TA("shop.types", t, "?"));
    else snprintf(b, n, "%s", TA("shop.types", t, "?"));
    return b;
}

static int w, h, s, vtop, vis;

static void header(void)
{
    int hh = S(92), y0 = vtop, ss = Ui_SmallS();
    char b[48];
    Ui_VGrad(0, y0, w, hh, 0x221E5A, 0x0E0C2C, 245);
    Ui_Fill(0, y0 + hh - S(4), w, S(3), GOLD_D, 255);
    Ui_Fill(0, y0 + hh - S(4), w, S(1), 0xFFE8A0, 255);
    Ui_Fill(0, y0 + hh - S(1), w, S(1), 0x3A2606, 255);
    /* our own plate (no game logo) */
    Ui_Pill(X(18), y0 + S(18), X(232), S(48), 0, 1);
    Ui_TextC(X(18) + X(116), y0 + S(42), T("shop.brand"), GOLD, s);
    Ui_Fill(X(270), y0 + S(12), S(2), hh - S(24), 0x6A5A9A, 255);
    icon12(ICON_SHOP, X(312), y0 + S(44), S(3), 0xF0C850, 0x7A5AC8);
    Ui_TextSh(X(352), y0 + S(28), T("shop.title"), GOLD, s + 1);
    fit(X(354), y0 + S(62), X(500), T("shop.subtitle"), SOFT, ss);
    /* level and coins */
    Ui_Fmt1(b, sizeof(b), T("shop.level"), Eco_Level());
    Ui_Pill(X(880), y0 + S(22), X(110), S(44), 0, 0);
    Ui_TextC(X(935), y0 + S(44), b, SOFT, ss);
    Ui_Pill(X(1006), y0 + S(22), X(250), S(44), 0, 1);
    coin(X(1006) + S(24), y0 + S(44), S(14));
    snprintf(b, sizeof(b), "%d", jm.eco.coins);
    txt_r(X(1006) + X(250) - S(22), y0 + S(44), b, WHITE, s);
}

static void keeper_side(void)
{
    int dh = S(440), dw = keeper_h > 0 ? dh * keeper_w / keeper_h : 0, bx = X(30), by = Y(570), bw = X(400), bh = S(92), i;
    if (keeper_px) picture(keeper_px, keeper_w, keeper_h, X(-24), Y(640) - dh, dw, dh);
    Ui_OPanel(bx, by, bw, bh, 0);
    {   /* the name tag over the box */
        const char *name = L1(TrKey("npc_names", keeper, Eco_ShopName()));
        int tw_ = tw(name, s) + S(40);
        Ui_Pill(bx + S(14), by - S(24), tw_, S(36), 0, 1);
        Ui_TextC(bx + S(14) + tw_ / 2, by - S(6), name, GOLD, s);
    }
    for (i = 0; i < SAY_LINES; i++)
        if (said[i][0]) txt(bx + S(22), by + S(30) + i * S(24), L1(said[i]), WHITE, Ui_SmallS());
    {   /* the little "more" arrow */
        int ax = bx + bw - S(28), ay = by + bh - S(22), k;
        for (k = 0; k < S(6); k++) Ui_Fill(ax - S(6) + k, ay + k, (S(6) - k) * 2, 1, 0xF0C850, 255);
    }
}

static void tabs_row(int px, int pw)
{
    static const char *const keys[TABS] = {"shop.tabs.0", "shop.tabs.1", "shop.tabs.2"};
    int i, gap = S(10), tw_ = (pw - 2 * S(16) - (TABS - 1) * gap) / TABS, ty = Y(106), th = S(46);
    (void)keys;
    for (i = 0; i < TABS; i++) {
        int tx = px + S(16) + i * (tw_ + gap), on = i == tab;
        const char *name = TA("shop.tabs", i, "?");
        int lw = tw(name, s) + S(34), lx = tx + (tw_ - lw) / 2;
        if (on) Ui_Frame(tx - S(3), ty - S(3), tw_ + S(6), th + S(6), S(3), 0xF0C850, 80);
        Ui_VGrad(tx, ty, tw_, th, on ? 0x34307A : 0x1A1A44, on ? 0x1C1A4C : 0x10102C, 245);
        Ui_Frame(tx, ty, tw_, th, S(2), on ? 0xF0C850 : 0x4A4A7A, 255);
        if (on) Ui_Fill(tx + S(2), ty + S(2), tw_ - S(4), S(1), 0xFFF0B0, 200);
        icon12(ICON_TAB[i], lx + S(10), ty + th / 2, S(2), on ? 0xF0C850 : 0x8C88B8, on ? 0xFFF4C8 : 0xC8C4E8);
        txt(lx + S(28), ty + th / 2, name, on ? WHITE : SOFT, s);
    }
}

static void select_box(int x, int y, int bw, int bh, const char *label, int arrows)
{
    int k, ax = x + bw - S(24), ay = y + bh / 2;
    Ui_Fill(x, y, bw, bh, 0x0C0C26, 240);
    Ui_Frame(x, y, bw, bh, S(1), 0x5A5A90, 255);
    fit(x + S(12), ay, bw - S(44), label, WHITE, Ui_SmallS());
    if (!arrows) for (k = 0; k < S(6); k++) Ui_Fill(ax - S(6) + k, ay - S(3) + k, (S(6) - k) * 2, 1, WHITE, 255);
    else {
        for (k = 0; k < S(5); k++) Ui_Fill(ax - S(8) - k, ay - S(6) + k, k * 2 + 1, 1, WHITE, 255);
        Ui_Fill(ax - S(8), ay - S(2), S(1), S(10), WHITE, 255);
        for (k = 0; k < S(5); k++) Ui_Fill(ax + S(6) - (S(4) - k), ay + S(2) + k, (S(4) - k) * 2 + 1, 1, WHITE, 255);
        Ui_Fill(ax + S(6), ay - S(8), S(1), S(10), WHITE, 255);
    }
}

static void pack_art(int x, int y, int pw, int ph, int rare)
{
    unsigned top = rare == 2 ? 0xE8B030 : rare == 1 ? 0x8A48D8 : 0x3A6AD8, bot = rare == 2 ? 0x8A5A10 : rare == 1 ? 0x3A1878 : 0x182A70;
    int cx = x + pw / 2, cy = y + ph / 2, k, r = pw / 4;
    Ui_Fill(x + S(3), y + S(4), pw, ph, 0x000000, 120);
    Ui_VGrad(x, y, pw, ph, top, bot, 255);
    Ui_Frame(x, y, pw, ph, S(2), 0xFFE8A0, 255);
    for (k = 0; k < S(4); k++) Ui_Fill(x + S(2), y + S(10) + k * S(3), pw - S(4), S(1), 0xFFFFFF, 40);
    for (k = -r; k <= r; k++) {         /* a four-point star */
        int hw = (r - (k < 0 ? -k : k)) / 3;
        Ui_Fill(cx - hw, cy + k, hw * 2 + 1, 1, 0xFFF4C8, 255);
        Ui_Fill(cx + k, cy - hw, 1, hw * 2 + 1, 0xFFF4C8, 255);
    }
}
static int pack_rarity(const EcoItem *it) { return it->price >= 900 ? 2 : it->price >= 300 ? 1 : 0; }

static void row(int x, int y, int rw, int rh, const EcoItem *it, int chosen, int card, const char *alt_name)
{
    char b[48], name[48];
    int ss = Ui_SmallS(), tx = x + S(96), my = y + rh / 2;
    int price_rgb = it && (it->locked || (tab != TAB_SELL && it->price > jm.eco.coins)) ? RED : WHITE;
    if (chosen) {
        Ui_Frame(x - S(4), y - S(4), rw + S(8), rh + S(8), S(3), 0xF0C850, 70);
        Ui_VGrad(x, y, rw, rh, 0x3A346E, 0x221E52, 245);
        Ui_Frame(x, y, rw, rh, S(2), 0xF0C850, 255);
        Ui_Fill(x + S(2), y + S(2), rw - S(4), S(1), 0xFFF0B0, 200);
    } else {
        Ui_Fill(x, y, rw, rh, 0x15143C, 225);
        Ui_Frame(x, y, rw, rh, S(1), 0x34346A, 255);
    }
    if (it && it->kind == ECO_ITEM_PACK) {
        Ui_Fill(x + S(10), my - S(11), S(26), S(22), 0x0A0A1C, 255);
        Ui_Fill(x + S(11), my - S(10), S(24), S(20), 0x2E8A60, 255);
        Ui_TextC(x + S(23), my, "P", 0xFFFFFF, ss);
        pack_art(x + S(48), y + S(6), S(34), rh - S(12), pack_rarity(it));
    } else {
        const unsigned *px = thumb_of(card);
        badge(x + S(10), my - S(11), card);
        Ui_Fill(x + S(44), y + S(5), S(44), rh - S(10), type_frame(card_type(card)), 255);
        if (px) picture(px, THUMB_W, THUMB_H, x + S(47), y + S(8), S(38), rh - S(16));
        else Ui_Fill(x + S(47), y + S(8), S(38), rh - S(16), 0x202040, 255);
    }
    snprintf(name, sizeof(name), "%s", L1(alt_name ? alt_name : it ? it->name : "?"));
    fit(tx, y + S(18), rw - S(96) - S(150), name, it && it->locked ? DIM : WHITE, ss);
    if (it && it->kind == ECO_ITEM_PACK) Ui_Fmt1(b, sizeof(b), T("shop.pack_line"), it->owned);
    else type_line(card, b, sizeof(b));
    fit(tx, y + S(43), rw - S(96) - S(150), b, 0x9894C0, ss);
    if (!it) return;
    if (it->kind != ECO_ITEM_PACK && it->owned > 0) {   /* copies owned (to sell: the spares) */
        int cw = S(46);
        snprintf(b, sizeof(b), "x%d", it->owned);
        Ui_Fill(x + rw - S(146), my - S(13), cw, S(26), 0x0A0A22, 230);
        Ui_Frame(x + rw - S(146), my - S(13), cw, S(26), S(1), 0x5A5A90, 255);
        Ui_TextC(x + rw - S(146) + cw / 2, my, b, it->kind == ECO_ITEM_SELL ? SOFT : GREEN, ss);
    }
    if (it->locked) {
        Ui_Fmt1(b, sizeof(b), T("shop.level"), it->level_min);
        txt_r(x + rw - S(14), my, b, RED, ss);
        return;
    }
    coin(x + rw - S(78), my, S(11));
    snprintf(b, sizeof(b), "%d", it->price);
    txt_r(x + rw - S(14), my, b, price_rgb, s);
}

static void list_panel(void)
{
    int px = X(445), py = Y(92), pw = X(520), ph = S(568), i;
    int rx = px + S(16), rw = pw - S(44), rh = S(60), pitch = S(64), ry0 = Y(208);
    Ui_OPanel(px, py, pw, ph, 1);
    tabs_row(px, pw);
    if (pack_count > 0) {               /* the pack, turned over one card at a time */
        select_box(rx, Y(162), rw, S(36), pack_shown < pack_count ? T("shop.opening") : T("shop.done"), 0);
        for (i = 0; i < pack_count && i < ROWS; i++) {
            char name[40];
            name[0] = 0;
            if (i < pack_shown) { Cards_NameUtf8(pack_cards[i], name, sizeof(name)); row(rx, ry0 + i * pitch, rw, rh, NULL, i == pack_shown - 1, pack_cards[i], name); }
            else { Ui_Fill(rx, ry0 + i * pitch, rw, rh, 0x15143C, 160); Ui_Frame(rx, ry0 + i * pitch, rw, rh, S(1), 0x34346A, 255); Ui_TextC(rx + rw / 2, ry0 + i * pitch + rh / 2, "? ? ?", DIM, s); }
        }
        return;
    }
    if (tab != TAB_PACKS) {
        select_box(rx, Y(162), X(218), S(36), TA("shop.filters", filter, "?"), 0);
        select_box(rx + X(232), Y(162), rw - X(232), S(36), TA("shop.sorts", sort_by, "?"), 1);
    }
    if (count <= 0) Ui_TextC(px + pw / 2, ry0 + S(60), L1(EcoTr(tab == TAB_SELL ? "ui.shop_no_spare" : "ui.shop_sold_out")), SOFT, s);
    for (i = top; i < count && i < top + ROWS; i++)
        row(rx, ry0 + (i - top) * pitch, rw, rh, &items[i], i == sel, items[i].card, NULL);
    if (count > ROWS) {                 /* where in the list we are */
        int track = pitch * ROWS - (pitch - rh), bar = track * ROWS / count, by = track * top / count, sx = px + pw - S(20);
        Ui_Fill(sx, ry0, S(4), track, 0x22224A, 230);
        Ui_Fill(sx, ry0 + by, S(4), bar < S(16) ? S(16) : bar, 0xD8B048, 255);
    }
}

static void stepper_btn(int cx, int cy, int r, int plus, int on)
{
    Ui_Disc(cx, cy, r + S(2), r + S(2), 0x000000, 100);
    Ui_Disc(cx, cy, r, r, on ? 0xF0C850 : 0x5A5A80, 255);
    Ui_Disc(cx, cy, r - S(3), r - S(3), on ? 0xD89A28 : 0x22224A, 255);
    Ui_Fill(cx - r / 2, cy - S(2), r, S(4), 0xFFFFFF, 255);
    if (plus) Ui_Fill(cx - S(2), cy - r / 2, S(4), r, 0xFFFFFF, 255);
}

static void detail_panel(void)
{
    int px = X(978), py = Y(160), pw = X(262), ph = S(498), cx = px + pw / 2, ss = Ui_SmallS();
    int card = 0, cw = S(150), chh = S(204), cy = py + S(22);
    const EcoItem *it = count > 0 && pack_count <= 0 ? &items[sel] : NULL;
    char b[64], name[48];
    Ui_OPanel(px, py, pw, ph, 0);
    if (pack_count > 0) card = pack_shown > 0 ? pack_cards[pack_shown - 1] : 0;
    else if (it) card = it->card;
    if (!it && !card) {
        if (pack_count > 0) pack_art(cx - cw / 2, cy, cw, chh, 0);
        return;
    }
    if (card > 0) badge(px + pw - S(40), py + S(16), card);
    /* the card */
    if (it && it->kind == ECO_ITEM_PACK) pack_art(cx - cw / 2, cy, cw, chh, pack_rarity(it));
    else {
        int t = card_type(card), x0 = cx - cw / 2, ax = x0 + S(10), aw = cw - S(20), ay = cy + S(30), ah = aw * ART_H / ART_W;
        const unsigned *px_ = big_of(card);
        Ui_Fill(x0 + S(4), cy + S(5), cw, chh, 0x000000, 120);
        Ui_Fill(x0, cy, cw, chh, 0x3A2A10, 255);
        Ui_Fill(x0 + S(3), cy + S(3), cw - S(6), chh - S(6), type_frame(t), 255);
        Ui_Fill(x0 + S(3), cy + S(3), cw - S(6), S(1), 0xFFFFFF, 80);
        name[0] = 0;
        Cards_NameUtf8(card, name, sizeof(name));
        Ui_Fill(x0 + S(8), cy + S(8), cw - S(16), S(18), 0xF4ECD8, 255);
        fit(x0 + S(12), cy + S(17), cw - S(24), L1(name), 0x1A1408, 1);
        Ui_Fill(ax - S(2), ay - S(2), aw + S(4), ah + S(4), 0x2A1E0A, 255);
        if (px_) picture(px_, ART_W, ART_H, ax, ay, aw, ah); else Ui_Fill(ax, ay, aw, ah, 0x202040, 255);
        if (t >= 0 && t < 20) {
            unsigned v = (unsigned)gDuel_adwCardStats[card - 1];
            int lv = Cards_Level(card), k;
            for (k = 0; k < lv && k < 12; k++) Ui_Disc(x0 + cw - S(14) - k * S(9), cy + S(36) + ah, S(3), S(3), 0xF0B030, 255);
            snprintf(b, sizeof(b), "%s %d  %s %d", T("shop.atk"), (int)(v & 0x1FF) * 10, T("shop.def"), (int)(v >> 9 & 0x1FF) * 10);
            Ui_Fill(x0 + S(8), cy + chh - S(30), cw - S(16), S(22), 0xF4ECD8, 255);
            Ui_TextC(cx, cy + chh - S(19), b, 0x1A1408, 1);
        } else {
            Ui_Fill(x0 + S(8), cy + chh - S(30), cw - S(16), S(22), 0xF4ECD8, 255);
            Ui_TextC(cx, cy + chh - S(19), TA("shop.types", t, ""), 0x1A1408, 1);
        }
    }
    /* name, type and a line */
    {
        int ty = cy + chh + S(24);
        if (it && it->kind == ECO_ITEM_PACK) snprintf(name, sizeof(name), "%s", it->name);
        else { name[0] = 0; Cards_NameUtf8(card, name, sizeof(name)); }
        fit(px + S(18), ty, pw - S(36), L1(name), WHITE, s);
        if (it && it->kind == ECO_ITEM_PACK) Ui_Fmt1(b, sizeof(b), T("shop.pack_line"), it->owned);
        else type_line(card, b, sizeof(b));
        {
            int t = card_type(card);
            Ui_Disc(px + S(24), ty + S(26), S(6), S(6), type_frame(t), 255);
            fit(px + S(36), ty + S(26), pw - S(46), b, SOFT, ss);
        }
        if (pack_count > 0) { fit(px + S(18), ty + S(52), pw - S(36), T(pack_shown < pack_count ? "shop.reveal" : "shop.done"), GOLD, ss); return; }
        if (it->locked) Ui_Fmt1(b, sizeof(b), T("shop.locked"), it->level_min);
        else if (tab == TAB_SELL) Ui_Fmt1(b, sizeof(b), T("shop.spares"), it->owned);
        else if (it->kind == ECO_ITEM_PACK) b[0] = 0;
        else Ui_Fmt1(b, sizeof(b), T("shop.owned"), it->owned);
        if (b[0]) fit(px + S(18), ty + S(52), pw - S(36), b, it->locked ? RED : SOFT, ss);
    }
    /* quantity, total, button */
    {
        int sy = py + ph - S(118), m = qty_max(), total = it->price * qty, by = py + ph - S(56), bw = pw - S(36), bh = S(44);
        if (asking) Ui_TextC(cx, sy, T("shop.confirm"), GOLD, s);
        else {
        stepper_btn(cx - S(70), sy, S(15), 0, qty > 1);
        Ui_Fill(cx - S(42), sy - S(15), S(84), S(30), 0x0A0A22, 235);
        Ui_Frame(cx - S(42), sy - S(15), S(84), S(30), S(1), 0x5A5A90, 255);
        snprintf(b, sizeof(b), "%d", qty);
        Ui_TextC(cx, sy, b, WHITE, s);
        stepper_btn(cx + S(70), sy, S(15), 1, qty < m);
        }
        txt(px + S(22), sy + S(38), T("shop.total"), WHITE, s);
        snprintf(b, sizeof(b), "%d", total);
        txt_r(px + pw - S(22), sy + S(38), b, tab != TAB_SELL && total > jm.eco.coins ? RED : WHITE, s);
        coin(px + pw - S(30) - tw(b, s) - S(14), sy + S(38), S(11));
        if (asking) {
            int hw = (bw - S(10)) / 2;
            Ui_Pill(px + S(18), by, hw, bh, ask_yes, ask_yes);
            Ui_Pill(px + S(18) + hw + S(10), by, hw, bh, !ask_yes, !ask_yes);
            Ui_TextC(px + S(18) + hw / 2, by + bh / 2, T("shop.yes"), ask_yes ? 0x2A1A04 : SOFT, s);
            Ui_TextC(px + S(28) + hw + hw / 2, by + bh / 2, T("shop.no"), ask_yes ? SOFT : 0x2A1A04, s);
        } else {
            const char *label = T(tab == TAB_SELL ? "shop.sell_btn" : "shop.buy");
            int lw = tw(label, s) + S(34), lx = cx - lw / 2;
            Ui_Pill(px + S(18), by, bw, bh, 1, 1);
            icon12(ICON_CART, lx + S(10), by + bh / 2, S(2), 0x2A1A04, 0x2A1A04);
            txt(lx + S(30), by + bh / 2, label, 0x2A1A04, s);
        }
    }
}

static void bottom(void)
{
    int by = Y(690), bh = S(40);
    char b[32];
    const char *k[14];
    int n = 0;
    Ui_Pill(X(16), by - bh / 2, X(150), bh, 0, 0);
    snprintf(b, sizeof(b), "< %s", T("shop.back"));
    Ui_TextC(X(16) + X(75), by, b, WHITE, s);
    k[n * 2] = "Q/E"; k[n * 2 + 1] = T("shop.k_tab"); n++;
    k[n * 2] = "^v"; k[n * 2 + 1] = T("shop.k_row"); n++;
    k[n * 2] = "<>"; k[n * 2 + 1] = T("shop.k_qty"); n++;
    k[n * 2] = "X"; k[n * 2 + 1] = T(tab == TAB_SELL ? "shop.sell_btn" : "shop.k_buy"); n++;
    if (tab != TAB_PACKS) { k[n * 2] = "Z"; k[n * 2 + 1] = T("shop.k_filter"); n++; k[n * 2] = "R"; k[n * 2 + 1] = T("shop.k_sort"); n++; }
    k[n * 2] = "S"; k[n * 2 + 1] = T("shop.k_back"); n++;
    Ui_KeyBar(k, n, (X(200) + X(1260)) / 2, by, X(1020));
}

void Shop_Overlay(void)
{
    Ui_Metrics(&w, &h, &s, &vtop, &vis);
    load_pictures();
    backdrop();
    keeper_side();
    header();
    list_panel();
    detail_panel();
    bottom();
}

unsigned Shop_Signature(void)
{
    return 2654435761u + generation * 2246822519u + (unsigned)(sel * 131 + top * 17 + tab * 7919) +
           (unsigned)asking * 1000003u + (unsigned)ask_yes * 31u + (unsigned)jm.eco.coins * 1009u +
           (unsigned)pack_shown * 97u + (unsigned)pack_count * 53u + (unsigned)(said_hold > 0) * 3331u +
           (unsigned)qty * 7027u + (unsigned)filter * 104729u + (unsigned)sort_by * 1299709u + art_loads * 15485863u +
           (unsigned)(keeper_px != NULL) * 179u + (unsigned)(bg != NULL) * 191u;
}

/* the shop's card pictures and labels, for the backpack (jm_bag.c) */
const char *Jm_L1(const char *utf8) { return L1(utf8); }
int Jm_CardArt(int card, int big, int x, int y, int w, int h)
{
    const unsigned *px = big ? big_of(card) : thumb_of(card);
    if (!px) return 0;
    picture(px, big ? ART_W : THUMB_W, big ? ART_H : THUMB_H, x, y, w, h);
    return 1;
}
unsigned Jm_ArtLoads(void) { return art_loads; }
void Jm_CardLine(int card, char *b, size_t n) { type_line(card, b, n); }
void Jm_CardBadge(int x, int y, int card) { badge(x, y, card); }
unsigned Jm_TypeFrame(int card) { return type_frame(card_type(card)); }
