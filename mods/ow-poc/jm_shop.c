/* Journey Mode's shop screen.
 *
 * The painted village stays behind it, with the keeper standing on the left (her own art when
 * assets/shop_<keeper>.raw is there, else the sprite she walks the village in: ow_poc.c draws her).
 * This file draws what goes over that:
 *
 *   left, low    her name and what she is saying - her greeting, and her answer to what you just did
 *   right        the stock box: the purse, three tabs, the list, and the line about the chosen row
 *
 *   Left/Right  the tab        Up/Down  the row        X  buy or sell (then Yes/No)
 *   Triangle or Circle  leave
 *
 * What is on sale, what it costs and what a pack holds are data (assets/economy.json); this file
 * only shows them and asks for a yes.
 */
#include "jm.h"
#include <stdio.h>
#include <string.h>

extern int Cards_NameUtf8(int id, char *out, size_t size);

#define ROWS 8                          /* rows of the list on screen at once */
#define MAX_ITEMS 64
#define PACK_CARDS 8
#define SAY_LINES 3
#define SAY_COLS 34

enum { TAB_CARDS, TAB_PACKS, TAB_SELL, TABS };

static EcoItem items[MAX_ITEMS];
static int count, tab, sel, top;
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
static void reload(void)
{
    count = tab == TAB_PACKS ? Eco_PackItems(items, MAX_ITEMS)
          : tab == TAB_SELL ? Eco_SellItems(items, MAX_ITEMS)
          : Eco_ShopItems(items, MAX_ITEMS);
    if (sel >= count) sel = count > 0 ? count - 1 : 0;
    if (top > sel) top = sel;
    if (sel >= top + ROWS) top = sel - ROWS + 1;
    if (top > count - ROWS) top = count > ROWS ? count - ROWS : 0;
    generation++;
}

const char *Shop_Keeper(void) { return keeper; }

void Shop_Open(void)
{
    snprintf(keeper, sizeof(keeper), "%s", Eco_ShopKeeper());
    Paint_ShopArt(keeper);
    tab = TAB_CARDS;
    sel = top = 0;
    asking = 0;
    ask_yes = 1;
    pack_count = pack_shown = 0;
    reload();
    greet();
}

/* ------------------------------------------------------------------ input */
static void confirm(void)
{
    EcoItem *it = &items[sel];
    if (tab == TAB_SELL) {
        if (Eco_Sell(it)) { answer(EcoTr("ui.shop_sold")); reload(); }
        else answer(EcoTr("ui.shop_no_spare"));
        return;
    }
    if (jm.eco.coins < it->price) { answer(EcoDlg("keeper_poor")); return; }
    if (it->kind == ECO_ITEM_PACK) {
        pack_count = Eco_OpenPack(it->bit, pack_cards, PACK_CARDS);
        if (pack_count <= 0) { answer(EcoTr("ui.shop_sold_out")); return; }
        if (!Eco_TakeCoins(it->price)) { pack_count = 0; answer(EcoDlg("keeper_poor")); return; }
        pack_shown = 0;                 /* the cards are given as they are turned over */
        answer(EcoTr("ui.shop_bought"));
        return;
    }
    if (Eco_Buy(it)) { answer(EcoTr("ui.shop_bought")); reload(); }
    else answer(EcoTr("ui.shop_sold_out"));
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
    if (edge & (PAD_LEFT | PAD_RIGHT)) {
        tab = (tab + (edge & PAD_LEFT ? TABS - 1 : 1)) % TABS;
        sel = top = 0;
        reload();
    }
    if ((edge & (PAD_UP | PAD_DOWN)) && count > 0) {
        sel = (sel + (edge & PAD_UP ? count - 1 : 1)) % count;
        if (sel < top) top = sel;
        if (sel >= top + ROWS) top = sel - ROWS + 1;
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

/* ---------------------------------------------------------------- drawing */
#define GOLD 0xFFE9A0u
#define LIT 0x40E0E0u
#define PLAIN 0xC8C8C8u
#define DIM 0x6E6E7Au
#define COIN 0xF0C860u

static int w, h, s, vtop, vis, lh;

static void right_arrow(int x, int row_y, const char *text, unsigned rgb)
{
    Ui_Text(x - jm_host->text_width(jm_host, text, s), row_y, text, rgb);
}

/* her name and words, over the painted village, on the left */
static void say_panel(void)
{
    int pw = w * 42 / 100, px = w / 24, ph = lh * 4, py = vtop + vis - ph - vis / 14, i;
    Ui_Panel(px, py, pw, ph);
    Ui_Text(px + 12 * s, py + lh - lh / 3, TrKey("npc_names", keeper, Eco_ShopName()), GOLD);
    for (i = 0; i < SAY_LINES; i++)
        if (said[i][0]) Ui_Text(px + 12 * s, py + lh + lh * i * 2 / 3 + lh / 2, said[i], PLAIN);
}

/* the purse, the tabs, the stock, and the line about the chosen row */
static void stock_panel(void)
{
    int pw = w * 46 / 100, px = w - pw - w / 24, ph = lh * (ROWS + 5), py = vtop + vis / 16, i;
    char buf[72];
    const char *names[TABS];
    names[TAB_CARDS] = EcoTr("ui.shop_singles");
    names[TAB_PACKS] = EcoTr("ui.shop_packs");
    names[TAB_SELL] = EcoTr("ui.shop_sell");
    if (py + ph > vtop + vis) py = vtop + vis - ph;
    Ui_Panel(px, py, pw, ph);

    /* the purse, on its own line */
    Ui_Fmt1(buf, sizeof(buf), EcoTr("ui.money"), jm.eco.coins);
    Ui_Text(px + 14 * s, py + lh - lh / 3, buf, COIN);
    Ui_Fmt1(buf, sizeof(buf), EcoTr("ui.hud_level"), Eco_Level());
    right_arrow(px + pw - 14 * s, py + lh - lh / 3, buf, DIM);

    /* the tabs, the open one underlined */
    for (i = 0; i < TABS; i++) {
        int tw = jm_host->text_width(jm_host, names[i], s);
        int tx = px + 14 * s + i * (pw - 28 * s) / TABS;
        Ui_Text(tx, py + lh * 2 - lh / 4, names[i], i == tab ? LIT : DIM);
        if (i == tab) jm_host->fill(jm_host, tx, py + lh * 2 + 4 * s, tw, 2 * s, LIT, 255);
    }

    if (pack_count > 0) {               /* the pack, turned over one card at a time */
        for (i = 0; i < pack_count; i++) {
            char name[40];
            int ry = py + lh * (3 + i) + lh / 4;
            if (i < pack_shown) {
                name[0] = 0;
                Cards_NameUtf8(pack_cards[i], name, sizeof(name));
                jm_host->fill(jm_host, px + 10 * s, ry - lh / 2, pw - 20 * s, lh, 0x203058, 180);
                Ui_Text(px + 20 * s, ry, name[0] ? name : "?", GOLD);
            } else Ui_Text(px + 20 * s, ry, "- - -", DIM);
        }
        Ui_Text(px + 14 * s, py + ph - lh / 2, Tr("hint.talk_short"), DIM);
        return;
    }

    if (count <= 0)
        Ui_Text(px + 20 * s, py + lh * 4, EcoTr(tab == TAB_SELL ? "ui.shop_no_spare" : "ui.shop_sold_out"), DIM);

    for (i = top; i < count && i < top + ROWS; i++) {
        const EcoItem *it = &items[i];
        int ry = py + lh * (3 + i - top) + lh / 4;
        unsigned rgb = it->locked ? DIM : i == sel ? 0xFFFFFF : PLAIN;
        if (i == sel) {                 /* the chosen row is a bar, not just a colour */
            jm_host->fill(jm_host, px + 8 * s, ry - lh / 2, pw - 16 * s, lh, 0x2A58A0, 190);
            jm_host->fill(jm_host, px + 8 * s, ry - lh / 2, 3 * s, lh, LIT, 255);
        }
        Ui_Text(px + 18 * s, ry, it->name, rgb);
        if (it->kind == ECO_ITEM_SELL) {
            snprintf(buf, sizeof(buf), "x%d", it->owned);
            right_arrow(px + pw * 72 / 100, ry, buf, DIM);
        } else if (it->owned > 0) {
            snprintf(buf, sizeof(buf), "x%d", it->owned);
            right_arrow(px + pw * 72 / 100, ry, buf, 0x70A070);     /* already in the chest */
        }
        snprintf(buf, sizeof(buf), "%d", it->price);
        right_arrow(px + pw - 16 * s, ry, buf, it->locked ? DIM : it->price > jm.eco.coins && tab != TAB_SELL ? 0xC06060 : COIN);
    }

    if (count > ROWS) {                 /* where in the list we are */
        int track = lh * ROWS, bar = track * ROWS / count, by = track * top / count;
        jm_host->fill(jm_host, px + pw - 7 * s, py + lh * 3 - lh / 2, 2 * s, track, 0x303048, 200);
        jm_host->fill(jm_host, px + pw - 7 * s, py + lh * 3 - lh / 2 + by, 2 * s, bar < 4 * s ? 4 * s : bar, LIT, 255);
    }

    /* the bottom line: Yes/No while it asks, else what the chosen row is */
    if (asking && count > 0) {
        int by = py + ph - lh / 2;
        Ui_Text(px + 14 * s, by, items[sel].name, GOLD);
        Ui_Text(px + pw * 62 / 100, by, Tr("ask.yes"), ask_yes ? LIT : DIM);
        Ui_Text(px + pw * 82 / 100, by, Tr("ask.no"), ask_yes ? DIM : LIT);
        Ui_Text(px + pw * (ask_yes ? 57 : 77) / 100, by, ">", 0xFFFFFF);
        return;
    }
    if (count > 0) {
        const EcoItem *it = &items[sel];
        if (it->locked) Ui_Fmt1(buf, sizeof(buf), EcoTr("ui.shop_need_level"), it->level_min);
        else if (tab == TAB_SELL) snprintf(buf, sizeof(buf), EcoTr("ui.shop_sell_for"), it->price);
        else if (it->kind == ECO_ITEM_PACK) snprintf(buf, sizeof(buf), EcoTr("ui.shop_price"), it->price);
        else snprintf(buf, sizeof(buf), EcoTr("ui.shop_owned"), it->owned);
        Ui_Text(px + 14 * s, py + ph - lh / 2, buf, it->locked ? 0xC06060 : DIM);
    }
}

/* Dim the village but cut the keeper's opaque silhouette out of the veil.  Consecutive canvas rows
 * with the same span are merged, which keeps the cached overlay cheap even at a large window size. */
static void background_veil(void)
{
    int y = 0;
    while (y < h) {
        int x0 = 0, x1 = 0, next = y + 1;
        int has_art = Paint_ShopMaskSpan(y, w, h, &x0, &x1);
        while (next < h) {
            int nx0 = 0, nx1 = 0;
            int next_has_art = Paint_ShopMaskSpan(next, w, h, &nx0, &nx1);
            if (next_has_art != has_art || (has_art && (nx0 != x0 || nx1 != x1))) break;
            next++;
        }
        if (!has_art) {
            jm_host->fill(jm_host, 0, y, w, next - y, 0x05040E, 105);
        } else {
            if (x0 > 0) jm_host->fill(jm_host, 0, y, x0, next - y, 0x05040E, 105);
            if (x1 < w) jm_host->fill(jm_host, x1, y, w - x1, next - y, 0x05040E, 105);
        }
        y = next;
    }
}

void Shop_Overlay(void)
{
    Ui_Metrics(&w, &h, &s, &vtop, &vis);
    lh = Ui_LineH();
    background_veil();
    say_panel();
    stock_panel();
}

unsigned Shop_Signature(void)
{
    return 2654435761u + generation * 2246822519u + (unsigned)(sel * 131 + top * 17 + tab * 7919) +
           (unsigned)asking * 1000003u + (unsigned)ask_yes * 31u + (unsigned)jm.eco.coins * 1009u +
           (unsigned)pack_shown * 97u + (unsigned)pack_count * 53u + (unsigned)(said_hold > 0) * 3331u;
}
