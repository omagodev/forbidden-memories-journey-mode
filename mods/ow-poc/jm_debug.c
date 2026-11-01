/* Debug aid for testing the story without replaying it.  OFF unless a file "debug.json" sits beside mod.json (or in the mod's data
 * folder): without it nothing here runs and no key does anything.  The file may be "{}".  Keys (it may hold any of them):
 *   "preset": "name" | number   a story state from journey.json "debug": [{name, stage, flags, anchor, time}] applied on Continue
 *   "stage": n, "flags": [names], "clear_flags": [names], "wins": n    set on Continue, after the preset
 *   "teleport": "anchor" | [x, y]    where to stand in the painted village (picture texels)
 *   "time": "day" | "night" | "auto"
 *   "coins": n, "xp": n     the purse and the experience, set on Continue
 *   "walked": seconds       walking already done, which is what the Jackals count
 *   "gang_ready": true      the Jackals have watched long enough: the next step brings one over
 *   "skip_dialogue": true   pages turn by themselves; Yes is chosen at questions
 *   "win_duels": true       a duel is not played: it counts as won
 *   "look": [0, 1, 2, ...]  the layered hero: the option number of each chargen category, set on Continue
 * In the painted village, with L1 + R1 held:  Up / Down  next / previous preset,  Left  time auto > night > day,
 * Right  next anchor,  Square  skip dialogue on/off,  Triangle  win duels on/off,  Circle  ambush now. */
#include "jm.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

extern int paint_area;
static JsonNode *cfg;
static int on, skip, win, preset_at = -1, anchor_at = -1;

int Dbg_On(void) { return on; }

/* "Dev mode" (START menu row): the top status bar (place, chapter, objective).  Kept in devmode.cfg in the mod's data folder
 * ("0" or "1") so it survives restarts and is the same for every save.  No file yet: ON when debug.json is active, else OFF. */
static int devbar = -1;
void Dev_Load(void)
{
    FILE *f = jm_host->open_data(jm_host, "devmode.cfg", "rb");
    char c = 0;
    if (f) { if (fread(&c, 1, 1, f) != 1) c = 0; fclose(f); }
    devbar = c == '0' ? 0 : c == '1' ? 1 : on;
    LOG("journey: dev mode %d (%s)", devbar, c == '0' || c == '1' ? "file" : on ? "default, debug.json" : "default");
}
int Dev_BarOn(void) { return on && (devbar < 0 ? 1 : devbar); }   /* developers only: needs debug.json, never in a player build */
void Dev_Set(int v)
{
    FILE *f;
    devbar = v ? 1 : 0;
    f = jm_host->open_data(jm_host, "devmode.cfg", "wb");
    if (f) { fwrite(devbar ? "1\n" : "0\n", 1, 2, f); fclose(f); }
    LOG("journey: dev mode %d (saved)", devbar);
}
int Dbg_Skip(void) { return on && skip; }
int Dbg_WinDuels(void) { return on && win; }

void Dbg_Init(void)
{
    char *text = Jm_ReadText("debug.json");
    on = 0;
    if (!text) {
        FILE *f = jm_host->open_data(jm_host, "debug.json", "rb");
        long n;
        if (f) {
            fseek(f, 0, SEEK_END); n = ftell(f); fseek(f, 0, SEEK_SET);
            text = malloc((size_t)n + 1);
            if (text && fread(text, 1, (size_t)n, f) == (size_t)n) text[n] = 0; else { free(text); text = NULL; }
            fclose(f);
        }
    }
    if (!text) return;
    cfg = Json_Parse(text);
    free(text);
    if (!cfg) { LOG("debug: debug.json has a syntax error, debug stays off"); return; }
    on = 1;
    skip = Json_Num(cfg, "skip_dialogue", 0) != 0;
    win = Json_Num(cfg, "win_duels", 0) != 0;
    LOG("debug: ON (skip dialogue %d, win duels %d)", skip, win);
}

static void set_flags(const JsonNode *list, int on_)
{
    const JsonNode *n;
    for (n = list ? list->child : NULL; n; n = n->next) {
        int b = n->str ? Story_FlagBit(n->str) : -1;
        if (b < 0) { LOG("debug: unknown flag %s", n->str ? n->str : "?"); continue; }
        if (on_) jm.flags |= 1u << b; else jm.flags &= ~(1u << b);
    }
}

static const JsonNode *presets(void) { return Json_Get(jm_rules, "debug"); }

static int apply_preset(int i)
{
    const JsonNode *l = presets(), *p = Json_At(l, i);
    float x, y;
    if (!p) return 0;
    jm.flags = 0;
    set_flags(Json_Get(p, "flags"), 1);
    jm.stage = (int)Json_Num(p, "stage", jm.stage);
    if (Paint_Anchor(Json_Str(p, "anchor", ""), &x, &y)) { Paint_GoAnchor(Json_Str(p, "anchor", "")); jm.pt_x = x; jm.pt_y = y; jm.pt_set = 1; }   /* the anchor may be in the cistern */
    if (Json_Str(p, "time", NULL)) Paint_ForceTime(!strcmp(Json_Str(p, "time", ""), "night") ? 1 : !strcmp(Json_Str(p, "time", ""), "day") ? 0 : -1);
    else Paint_ForceTime(-1);
    LOG("debug: preset %d %s (stage %d, flags %08x)", i, Json_Str(p, "name", "?"), jm.stage, jm.flags);
    Ui_Message(Json_Str(p, "name", "?"));
    return 1;
}

/* on Continue, after the save is read: the file's own settings */
void Dbg_Apply(void)
{
    const JsonNode *t;
    float x, y;
    if (!on) return;
    paint_area = 0;                    /* a debug state names its own place, the village otherwise */
    t = Json_Get(cfg, "preset");
    if (t) {
        int i = -1, k;
        if (t->str) { for (k = 0; k < Json_Count(presets()); k++) if (!strcmp(Json_Str(Json_At(presets(), k), "name", ""), t->str)) i = k; }
        else i = (int)t->num;
        if (i < 0 || !apply_preset(i)) LOG("debug: no preset %s", t->str ? t->str : "?");
        else preset_at = i;
    }
    set_flags(Json_Get(cfg, "flags"), 1);
    set_flags(Json_Get(cfg, "clear_flags"), 0);
    if (Json_Get(cfg, "stage")) jm.stage = (int)Json_Num(cfg, "stage", jm.stage);
    if (Json_Get(cfg, "wins")) jm.wins = (int)Json_Num(cfg, "wins", jm.wins);
    /* the economy, so a test does not have to be played up to: coins and xp outright, and
     * "gang_ready" to stand where the Jackals have finished watching and are about to move */
    if (Json_Get(cfg, "coins")) jm.eco.coins = (int)Json_Num(cfg, "coins", jm.eco.coins);
    if (Json_Get(cfg, "xp")) jm.eco.xp = (int)Json_Num(cfg, "xp", jm.eco.xp);
    if (Json_Get(cfg, "walked")) jm.eco.amb_walk = (int)(Json_Num(cfg, "walked", 0) * 30);
    if (Json_Num(cfg, "gang_ready", 0) != 0) Gang_Force();
    t = Json_Get(cfg, "teleport");
    if (t && t->str && Paint_Anchor(t->str, &x, &y)) { Paint_GoAnchor(t->str); jm.pt_x = x; jm.pt_y = y; jm.pt_set = 1; }
    else if (t && t->child) { x = (float)t->child->num; y = (float)(t->child->next ? t->child->next->num : 0); Paint_Set(x, y); jm.pt_x = x; jm.pt_y = y; jm.pt_set = 1; }
    t = Json_Get(cfg, "look");                 /* [skin, outfit, outfit colour, hair, ...]: the chargen choice, set on Continue */
    if (t && t->child && Cg_Ready()) {
        const JsonNode *n; int c = 0;
        for (n = t->child; n && c < 8; n = n->next, c++) Cg_Set(c, (int)n->num);
        jm.cg_set = 1;
    }
    t = Json_Get(cfg, "time");
    if (t && t->str) Paint_ForceTime(!strcmp(t->str, "night") ? 1 : !strcmp(t->str, "day") ? 0 : -1);
}

/* the chord: returns 1 when the world must be refreshed (flags, stage or place changed); the caller then ignores the pad this frame */
int Dbg_Keys(unsigned short pad, unsigned short edge, int *swallow)
{
    int n;
    *swallow = 0;
    if (!on || (pad & (PAD_L1 | PAD_R1)) != (PAD_L1 | PAD_R1)) return 0;
    *swallow = 1;
    n = Json_Count(presets());
    if ((edge & (PAD_UP | PAD_DOWN)) && n > 0) {
        preset_at = (edge & PAD_UP) ? (preset_at + 1) % n : (preset_at <= 0 ? n - 1 : preset_at - 1);
        return apply_preset(preset_at);
    }
    if (edge & PAD_LEFT) {
        int cur = Paint_ForcedTime();
        Paint_ForceTime(cur < 0 ? 1 : cur == 1 ? 0 : -1);
        Ui_Message(Paint_ForcedTime() < 0 ? "time: auto" : Paint_ForcedTime() ? "time: night" : "time: day");
        return 0;
    }
    if (edge & PAD_RIGHT) {
        float x, y;
        const char *name;
        anchor_at++;
        name = Paint_AnchorName(anchor_at);
        if (!name) { anchor_at = 0; name = Paint_AnchorName(0); }
        if (name && Paint_Anchor(name, &x, &y)) { Paint_GoAnchor(name); jm.pt_x = x; jm.pt_y = y; jm.pt_set = 1; Ui_Message(name); LOG("debug: teleport %s", name); return 1; }
        return 0;
    }
    if (edge & PAD_CIRCLE) {               /* bring the Jackals over on the next step */
        if (Gang_Force()) Ui_Message("ambush: walk a step");
        else Ui_Message("ambush: no gang data");
        return 0;
    }
    if (edge & PAD_SQUARE) { skip ^= 1; Ui_Message(skip ? "skip dialogue: on" : "skip dialogue: off"); }
    if (edge & PAD_TRIANGLE) { win ^= 1; Ui_Message(win ? "win duels: on" : "win duels: off"); }
    return 0;
}
