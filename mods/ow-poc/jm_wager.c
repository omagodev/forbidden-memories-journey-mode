/* The star wager (Duelist Kingdom) and the game-over screen.
 *
 * Every star duelist holds a number of stars (journey.json win "wager", his count in the content; the save keeps what he holds now in
 * jm.duel_held[slot], plus 1, 0 = the content count).  Before his duel the hero picks a bet from 1 to min(his own stars, the rival's);
 * a win takes the bet from the rival, a loss leaves it with him.  After the story win a rival only plays for stars again while he holds
 * more than his count after a minimum loss (stars won from the hero), and then only those ("rematch").  Losing the last star is the end:
 * the game-over screen, back to the title (jm_save.c never writes a save at zero stars, so Continue loads the last one).
 * Drawn in the shop's ornate style, 1280x720 design units; texts in ui.json "wager". */
#include "jm.h"
#include <stdio.h>
#include <string.h>

#define GOLD 0xF0C850u
#define SOFT 0xC8C4E8u
#define DIM 0x7A76A0u
#define WHITE 0xFFFFFFu
#define RED 0xFF7A6Au

static const JsonNode *cur;
static int bet, maxbet, held_now, rematch_now;
static int w, h, s, vtop, vis;

static int X(int v) { return Ui_DX(v); }
static int Y(int v) { return Ui_DY(v); }
static int S(int v) { return Ui_DS(v); }
static const char *T(const char *k) { return Jm_L1(Tr(k)); }

int Wager_HeldRaw(int slot, int base, const char *beaten_flag)
{
    if (slot < 0 || slot >= 16) return 0;
    if (jm.duel_held[slot]) return jm.duel_held[slot] - 1;
    return base - (beaten_flag && Story_Has(beaten_flag) ? 1 : 0);   /* an older save that beat him: the minimum bet left him one short */
}

static int held_of(const JsonNode *win)
{
    return Wager_HeldRaw((int)Json_Num(win, "slot", 0), (int)Json_Num(win, "wager", 1), Json_Str(win, "beaten", NULL));
}

int Wager_Max(const JsonNode *win)
{
    int held, cap, m;
    if (!win || !Json_Get(win, "wager") || !Json_Get(win, "slot")) return 0;
    held = held_of(win);
    cap = Json_Num(win, "rematch", 0) != 0 ? held - ((int)Json_Num(win, "wager", 1) - 1) : held;
    if (!Json_Num(win, "rematch", 0) && Json_Get(win, "beaten") && Story_Has(Json_Str(win, "beaten", ""))) return 0;  /* a beaten rival's story rule: no stars */
    m = jm.stars < cap ? jm.stars : cap;
    /* Wins clamp to 10 in Wager_Settle; keep the picker at the star cap so
     * late chapters (Heishin / Pegasus at 10) can still risk stars. */
    return m > 0 ? m : 0;
}

void Wager_Open(const JsonNode *win)
{
    cur = win;
    maxbet = Wager_Max(win);
    held_now = held_of(win);
    {   /* pinned now: the story win's flags are set before the bet is settled */
        int sl = (int)Json_Num(win, "slot", 0);
        if (sl >= 0 && sl < 16) jm.duel_held[sl] = (unsigned char)(held_now + 1);
    }
    rematch_now = Json_Num(win, "rematch", 0) != 0;
    bet = 1;
    LOG("journey: wager picker (max %d, %s holds %d)", maxbet, Json_Str(win, "wid", "?"), held_now);
    Wager_Input(0xFFFF);
}

int Wager_Bet(void) { return bet; }

int Wager_Input(unsigned short edge)
{
    static int age;
    if (edge == 0xFFFF) { age = 0; return 0; }
    if (Dbg_On() && Dbg_Wager() >= 0 && (Dbg_Skip() || Dbg_Wager() > 0) && ++age > 30) {   /* the smoke's bet */
        int b = Dbg_Wager() > 0 ? Dbg_Wager() : 1;
        bet = b < 1 ? 1 : b > maxbet ? maxbet : b;
        jm.wager_seen = 1;
        return 1;
    }
    if ((edge & (PAD_LEFT | PAD_DOWN)) && bet > 1) bet--;
    if ((edge & (PAD_RIGHT | PAD_UP)) && bet < maxbet) bet++;
    if (edge & PAD_CROSS) { jm.wager_seen = 1; return 1; }
    if (edge & (PAD_CIRCLE | PAD_TRIANGLE)) return 2;
    return 0;
}

void Wager_Settle(const JsonNode *win, int b, int won)
{
    int slot = (int)Json_Num(win, "slot", 0), held = held_of(win);
    if (b <= 0 || slot < 0 || slot >= 16) return;
    if (won) { jm.stars += b; held -= b; if (jm.stars > 10) jm.stars = 10; }
    else { jm.stars -= b; held += b; if (jm.stars < 0) jm.stars = 0; }
    if (held < 0) held = 0;
    if (held > 250) held = 250;
    jm.duel_held[slot] = (unsigned char)(held + 1);
    LOG("journey: star duel %s, bet %d, stars %d (%s holds %d)", won ? "won" : "lost", b, jm.stars, Json_Str(win, "wid", "?"), held);
}

/* a row of star chips: gold discs with a light ring; `n` of them, centred on cx */
static void chips(int cx, int cy, int n, int r, unsigned col)
{
    int i, gap = r * 2 + S(6), x0;
    if (n > 10) n = 10;
    x0 = cx - (n - 1) * gap / 2;
    for (i = 0; i < n; i++) {
        Ui_Disc(x0 + i * gap, cy, r, r, col, 255);
        Ui_Ring(x0 + i * gap, cy, r, r, S(2), 0xFFF2C0, 255);
        Ui_Disc(x0 + i * gap, cy, r / 3, r / 3, 0xFFF8E0, 255);
    }
}

static void side_box(int x, int y, int bw, const char *who, int n, int lit)
{
    char b[48];
    Ui_OPanel(x, y, bw, S(170), lit);
    Ui_TextC(x + bw / 2, y + S(34), who, GOLD, s);
    snprintf(b, sizeof(b), "%d %s", n, T(n == 1 ? "wager.star" : "wager.stars"));
    Ui_TextC(x + bw / 2, y + S(76), b, WHITE, s + 1);
    chips(x + bw / 2, y + S(128), n, S(11), 0xD8A830);
}

void Wager_Overlay(void)
{
    int px = X(190), py = Y(110), pw = X(900), ph = S(500), cx = px + pw / 2, ss;
    char b[128], key[48];
    const char *wid = cur ? Json_Str(cur, "wid", "") : "";
    const char *k[6];
    Ui_Metrics(&w, &h, &s, &vtop, &vis);
    ss = Ui_SmallS();
    Ui_Fill(0, 0, w, h, 0x05040E, 170);
    Ui_OPanel(px, py, pw, ph, 1);
    Ui_TextC(cx, py + S(40), T("wager.title"), GOLD, s + 1);
    Ui_TextC(cx, py + S(76), T(rematch_now ? "wager.rematch" : "wager.subtitle"), SOFT, ss);
    snprintf(key, sizeof(key), "wager.names.%s", wid);
    side_box(px + S(30), py + S(104), X(270), Jm_L1(jm.name), jm.stars, 0);
    side_box(px + pw - S(30) - X(270), py + S(104), X(270), T(key), held_now, 0);
    {   /* the bet in the middle: < n > */
        int bx = cx - X(140), by = py + S(120), bw = X(280);
        Ui_Pill(bx, by, bw, S(56), 1, 1);
        snprintf(b, sizeof(b), "%s  %c %d %c", T("wager.bet"), bet > 1 ? '<' : ' ', bet, bet < maxbet ? '>' : ' ');
        Ui_TextC(cx, by + S(28), b, 0x2A1A04, s + 1);
        chips(cx, by + S(100), bet, S(14), 0xF0C850);
    }
    Ui_Fill(px + S(40), py + S(300), pw - S(80), S(2), 0xB08A30, 255);
    snprintf(b, sizeof(b), T("wager.win"), bet);
    Ui_TextC(cx, py + S(330), b, 0x9CF0A0, s);
    snprintf(b, sizeof(b), T("wager.lose"), bet);
    Ui_TextC(cx, py + S(366), b, RED, s);
    if (bet >= jm.stars) Ui_TextC(cx, py + S(410), T("wager.allin"), RED, s);
    else if (!jm.wager_seen) Ui_TextC(cx, py + S(410), T("wager.warn"), 0xFFB060, ss);
    k[0] = "<>"; k[1] = T("wager.k_bet"); k[2] = "X"; k[3] = T("wager.k_duel"); k[4] = "S"; k[5] = T("wager.k_back");
    Ui_KeyBar(k, 3, w / 2, py + ph - S(36), pw - S(60));
}

unsigned Wager_Signature(void)
{
    return 70001u + (unsigned)(bet * 131 + maxbet * 17 + held_now * 7 + jm.stars * 977 + jm.wager_seen * 31) + (unsigned)Lang_Current() * 4421u + Jm_ArtLoads() * 2654435761u;
}

void GameOver_Overlay(int age)
{
    int a = age * 6 > 255 ? 255 : age * 6, cy;
    const char *k[2];
    Ui_Metrics(&w, &h, &s, &vtop, &vis);
    cy = vtop + vis / 2;
    Ui_VGrad(0, 0, w, h, 0x2A0408, 0x060104, (unsigned)a);
    if (age < 20) return;
    Ui_OPanel(X(240), cy - S(170), X(800), S(340), 1);
    Ui_TextC(w / 2, cy - S(100), T("wager.go_title"), 0xFF5A4A, s + 3);
    chips(w / 2, cy - S(36), 1, S(16), 0x4A3A30);
    Ui_TextC(w / 2, cy + S(14), T("wager.go_line1"), WHITE, s);
    Ui_TextC(w / 2, cy + S(50), T("wager.go_line2"), SOFT, s);
    Ui_TextC(w / 2, cy + S(86), T("wager.go_line3"), DIM, Ui_SmallS());
    if (age > 60) { k[0] = "X"; k[1] = T("wager.go_key"); Ui_KeyBar(k, 1, w / 2, cy + S(136), X(600)); }
}

unsigned GameOver_Signature(int age) { return 90001u + (unsigned)(age < 64 ? age : 64) * 131u + (unsigned)Lang_Current() * 977u; }
