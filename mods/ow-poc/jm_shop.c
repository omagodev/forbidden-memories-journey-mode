/* Journey Mode's shop screen: the stall a keeper runs, drawn with the same panel and font as the
 * START menu (Ui_Panel, Ui_Text).  Three tabs: the cards on sale, the packs, and the spare copies
 * the player can sell back.  What is on sale, what it costs and what a pack holds are all data
 * (assets/economy.json); this file only shows them and asks for a yes.
 *
 *   Left/Right  the tab        Up/Down  the row        X  buy or sell (then yes/no)
 *   Triangle or Circle  leave
 */
#include "jm.h"
#include <stdio.h>
#include <string.h>

extern int Cards_NameUtf8(int id, char *out, size_t size);

#define ROWS 9                          /* rows of the list on screen at once */
#define MAX_ITEMS 64
#define PACK_CARDS 8

enum { TAB_CARDS, TAB_PACKS, TAB_SELL, TABS };

static EcoItem items[MAX_ITEMS];
static int count, tab, sel, top;
static int asking;                      /* the yes/no panel is up (0 no, 1 buy, 2 sell) */
static int ask_yes;
static char flash[48];                  /* the last thing that happened (bought, sold, too poor) */
static int flash_timer;
static int pack_cards[PACK_CARDS], pack_count, pack_shown;   /* a pack being opened, revealed one by one */
static unsigned generation;             /* changes whenever the screen's content does */

static void reload(void)
{
    count = tab == TAB_PACKS ? Eco_PackItems(items, MAX_ITEMS)
          : tab == TAB_SELL ? Eco_SellItems(items, MAX_ITEMS)
          : Eco_ShopItems(items, MAX_ITEMS);
    if (sel >= count) sel = count > 0 ? count - 1 : 0;
    if (top > sel) top = sel;
    if (sel >= top + ROWS) top = sel - ROWS + 1;
    generation++;
}

void Shop_Open(void)
{
    tab = TAB_CARDS;
    sel = top = 0;
    asking = 0;
    ask_yes = 1;
    flash[0] = 0;
    flash_timer = 0;
    pack_count = pack_shown = 0;
    reload();
}

static void say(const char *s)
{
    snprintf(flash, sizeof(flash), "%s", s);
    flash_timer = 150;
    generation++;
}

/* ------------------------------------------------------------------ input */
static void confirm(void)
{
    EcoItem *it = &items[sel];
    if (tab == TAB_SELL) {
        if (Eco_Sell(it)) { say(EcoTr("ui.shop_sold")); reload(); }
        else say(EcoTr("ui.shop_no_spare"));
        return;
    }
    if (it->kind == ECO_ITEM_PACK) {
        if (jm.eco.coins < it->price) { say(EcoTr("ui.shop_not_enough")); return; }
        pack_count = Eco_OpenPack(it->bit, pack_cards, PACK_CARDS);
        if (pack_count <= 0) { say(EcoTr("ui.shop_sold_out")); return; }
        if (!Eco_TakeCoins(it->price)) { say(EcoTr("ui.shop_not_enough")); pack_count = 0; return; }
        pack_shown = 0;                 /* the cards are given as they are turned over */
        generation++;
        return;
    }
    if (jm.eco.coins < it->price) { say(EcoTr("ui.shop_not_enough")); return; }
    if (Eco_Buy(it)) { say(EcoTr("ui.shop_bought")); reload(); }
    else say(EcoTr("ui.shop_sold_out"));
}

int Shop_Input(unsigned short edge)
{
    if (flash_timer > 0) flash_timer--;
    if (pack_count > 0) {               /* turning the pack over, one card at a time */
        if (edge & (PAD_CROSS | PAD_CIRCLE | PAD_START)) {
            if (pack_shown < pack_count) {
                Story_Cards(pack_cards[pack_shown]);
                pack_shown++;
                generation++;
            } else { pack_count = pack_shown = 0; reload(); }
        }
        return 0;
    }
    if (asking) {
        if (edge & (PAD_LEFT | PAD_RIGHT | PAD_UP | PAD_DOWN)) { ask_yes ^= 1; generation++; }
        if (edge & PAD_CROSS) { if (ask_yes) confirm(); asking = 0; generation++; }
        else if (edge & (PAD_CIRCLE | PAD_TRIANGLE)) { asking = 0; generation++; }
        return 0;
    }
    if (edge & (PAD_TRIANGLE | PAD_CIRCLE | PAD_START)) return 1;
    if (edge & (PAD_LEFT | PAD_RIGHT)) {
        tab = (tab + (edge & PAD_LEFT ? TABS - 1 : 1)) % TABS;
        sel = top = 0;
        reload();
    }
    if ((edge & PAD_UP) && count > 0) {
        sel = (sel + count - 1) % count;
        if (sel < top) top = sel;
        if (sel >= top + ROWS) top = sel - ROWS + 1;
        generation++;
    }
    if ((edge & PAD_DOWN) && count > 0) {
        sel = (sel + 1) % count;
        if (sel < top) top = sel;
        if (sel >= top + ROWS) top = sel - ROWS + 1;
        generation++;
    }
    if ((edge & PAD_CROSS) && count > 0) {
        EcoItem *it = &items[sel];
        if (it->locked) { char b[48]; Ui_Fmt1(b, sizeof(b), EcoTr("ui.shop_need_level"), it->level_min); say(b); }
        else { asking = 1; ask_yes = 1; generation++; }
    }
    return 0;
}

/* ----------------------------------------------------------------- drawing */
void Shop_Overlay(void)
{
    int w, h, s, topy, vis, lh, x, y, pw, ph, i;
    char buf[64];
    const char *tab_name[TABS];
    Ui_Metrics(&w, &h, &s, &topy, &vis);
    lh = Ui_LineH();
    tab_name[TAB_CARDS] = EcoTr("ui.shop_singles");
    tab_name[TAB_PACKS] = EcoTr("ui.shop_packs");
    tab_name[TAB_SELL] = EcoTr("ui.shop_sell");
    jm_host->fill(jm_host, 0, 0, w, h, 0, 130);
    pw = w * 3 / 5;
    ph = lh * (ROWS + 6);
    x = (w - pw) / 2;
    y = topy + (vis - ph) / 2;
    if (y < topy) y = topy;
    Ui_Panel(x, y, pw, ph);

    Ui_Text(x + 14 * s, y + lh, Eco_ShopName(), 0xFFE9A0);
    Ui_Fmt1(buf, sizeof(buf), EcoTr("ui.money"), jm.eco.coins);
    Ui_Text(x + pw - jm_host->text_width(jm_host, buf, s) - 16 * s, y + lh, buf, 0xFFE9A0);

    for (i = 0; i < TABS; i++) {        /* the tabs, the open one lit */
        int tx = x + 14 * s + i * (pw / 4);
        Ui_Text(tx, y + lh * 2, tab_name[i], i == tab ? 0x40E0E0 : 0x808080);
        if (i == tab) jm_host->fill(jm_host, tx, y + lh * 2 + 8 * s, jm_host->text_width(jm_host, tab_name[i], s), 2 * s, 0x40E0E0, 255);
    }

    if (pack_count > 0) {               /* the pack being turned over */
        Ui_Text(x + 14 * s, y + lh * 4, EcoTr("ui.shop_bought"), 0xFFE9A0);
        for (i = 0; i < pack_count; i++) {
            char name[40];
            if (i < pack_shown) {
                name[0] = 0;
                Cards_NameUtf8(pack_cards[i], name, sizeof(name));
                Ui_Text(x + 20 * s, y + lh * (5 + i) + lh / 2, name[0] ? name : "?", 0xE0E0E0);
            } else Ui_Text(x + 20 * s, y + lh * (5 + i) + lh / 2, "?", 0x606060);
        }
        Ui_Text(x + 14 * s, y + ph - lh / 2, EcoTr("ui.shop_buy"), 0x8890C0);
        return;
    }

    if (count <= 0) {
        Ui_Text(x + 20 * s, y + lh * 4, EcoTr(tab == TAB_SELL ? "ui.shop_no_spare" : "ui.shop_sold_out"), 0x909090);
    }
    for (i = top; i < count && i < top + ROWS; i++) {
        int ry = y + lh * (3 + i - top) + lh / 2;
        const EcoItem *it = &items[i];
        unsigned rgb = it->locked ? 0x707070 : i == sel ? 0x40E0E0 : 0xB8B8B8;
        if (i == sel) Ui_Text(x + 6 * s, ry, ">", 0xFFFFFF);
        Ui_Text(x + 20 * s, ry, it->name, rgb);
        snprintf(buf, sizeof(buf), "%d", it->price);
        Ui_Text(x + pw * 3 / 4, ry, buf, it->locked ? 0x707070 : 0xFFE9A0);
        if (it->kind == ECO_ITEM_SELL || it->owned > 0) {
            snprintf(buf, sizeof(buf), "x%d", it->owned);
            Ui_Text(x + pw * 5 / 8, ry, buf, 0x808080);
        }
        if (it->kind == ECO_ITEM_ONCE && !it->locked) Ui_Text(x + pw - 26 * s, ry, "*", 0xFFE9A0);
    }

    /* the bottom line: what the chosen row is, or what just happened */
    if (flash_timer > 0) Ui_Text(x + 14 * s, y + ph - lh / 2, flash, 0x60F060);
    else if (count > 0) {
        const EcoItem *it = &items[sel];
        if (tab == TAB_SELL) snprintf(buf, sizeof(buf), EcoTr("ui.shop_sell_for"), it->price);
        else if (it->kind == ECO_ITEM_PACK) snprintf(buf, sizeof(buf), EcoTr("ui.shop_price"), it->price);
        else snprintf(buf, sizeof(buf), EcoTr("ui.shop_owned"), it->owned);
        Ui_Text(x + 14 * s, y + ph - lh / 2, buf, 0x8890C0);
    } else Ui_Text(x + 14 * s, y + ph - lh / 2, Eco_ShopGreet(), 0x8890C0);

    if (asking) {                       /* the yes/no panel over the list */
        int px = x + pw / 4, py = y + ph / 2 - lh, pwid = pw / 2, phh = lh * 3;
        Ui_Panel(px, py, pwid, phh);
        Ui_Text(px + 14 * s, py + lh - lh / 3, items[sel].name, 0xFFE9A0);
        Ui_Text(px + 30 * s, py + lh * 2, Tr("ask.yes"), ask_yes ? 0x40E0E0 : 0x909090);
        Ui_Text(px + 30 * s + pwid / 2, py + lh * 2, Tr("ask.no"), ask_yes ? 0x909090 : 0x40E0E0);
        Ui_Text(px + 16 * s + (ask_yes ? 0 : pwid / 2), py + lh * 2, ">", 0xFFFFFF);
    }
}

unsigned Shop_Signature(void)
{
    return 2654435761u + generation * 2246822519u + (unsigned)(sel * 131 + top * 17 + tab * 7919) +
           (unsigned)asking * 1000003u + (unsigned)ask_yes * 31u + (unsigned)jm.eco.coins * 1009u +
           (unsigned)(flash_timer > 0) * 3331u + (unsigned)pack_shown * 97u + (unsigned)pack_count * 53u;
}
