/* JS card scripts (PoC): the mod half. Hears MEMORIES_EVENT_MONSTER, finds the
 * card's <script: name> note, loads scripts/<name>.js into QuickJS (the engine is
 * linked into the game: src/pc/script/js_host.c) and calls the handler.
 * The ctx operations turn into entries of the duel's effect queue
 * (MonsterEffects_ScriptAction), so they resolve with the game's own LP splash. */
#include "pc/mods/modapi.h"
#include "pc/script/js_host.h"
#include "game/duel_card.h"
#include "game/duel_side_state.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

extern int MonsterEffects_ScriptAction(int kind, int source_record, int a, int b, int c);
enum { ACT_LIFE = 1, ACT_BOOST = 2, ACT_DESTROY = 3 };

static const MemoriesModHost *host;
static int source_record;
static char banner[160];
static unsigned banner_serial;
static uint64_t banner_until;

static int record_ok(int r) { return r >= 0 && r < 30; }
static int side_ok(int s) { return s == 0 || s == 1; }

static int api_op(int op, int a, int b, int c, const char *s)
{
    switch (op) {
    case JS_OP_DAMAGE: return side_ok(a) && b > 0 && MonsterEffects_ScriptAction(ACT_LIFE, source_record, a, -b, 0);
    case JS_OP_HEAL: return side_ok(a) && b > 0 && MonsterEffects_ScriptAction(ACT_LIFE, source_record, a, b, 0);
    case JS_OP_BOOST: return record_ok(a) && MonsterEffects_ScriptAction(ACT_BOOST, source_record, a, b, c);
    case JS_OP_DESTROY: return record_ok(a) && MonsterEffects_ScriptAction(ACT_DESTROY, source_record, a, 0, 0);
    case JS_OP_HAND_COUNT: {
        int i, n = 0;
        if (!side_ok(a)) return 0;
        for (i = 0; i < HAND_SIZE; i++) if (D_800E9FF0[a].hand[i] >= 0) n++;
        return n;
    }
    case JS_OP_CARD_ID: return record_ok(a) && (D_801A7AD8[a].flags & DUEL_CARD_FLAG_OCCUPIED) ? D_801A7AD8[a].card_id : 0;
    case JS_OP_ATK: return record_ok(a) ? D_801A7AD8[a].attack + D_801A7AD8[a].stat_modifier + D_801A7AD8[a].terrain_modifier : 0;
    case JS_OP_DEF: return record_ok(a) ? D_801A7AD8[a].defense + D_801A7AD8[a].defense_modifier + D_801A7AD8[a].stat_modifier + D_801A7AD8[a].terrain_modifier : 0;
    case JS_OP_LIFE: return side_ok(a) ? D_800E9FF0[a].life_points.signed_value : 0;
    case JS_OP_LOG: host->log(host, "js: %s", s); return 1;
    case JS_OP_SAY:
        snprintf(banner, sizeof(banner), "%s", s);
        banner_serial++;
        banner_until = host->now_us(host) + 4500000ull;
        host->log(host, "js: say: %s", s);
        return 1;
    }
    return 0;
}

static int api_list(int what, int side, int *out, int max)
{
    int r, n = 0;
    if (what != JS_LIST_FIELD_MONSTERS || !side_ok(side)) return 0;
    for (r = side * 15 + 5; r < side * 15 + 10 && n < max; r++)
        if (D_801A7AD8[r].flags & DUEL_CARD_FLAG_OCCUPIED) out[n++] = r;
    return n;
}

static const JsHostApi api = {api_op, api_list};

static int load_script(const char *name)
{
    char path[96];
    FILE *f;
    char *buffer;
    long size;
    int status;
    if (JsHost_Loaded(name)) return 1;
    snprintf(path, sizeof(path), "scripts/%s.js", name);
    f = host->open_asset(host, path);
    if (!f) { host->log(host, "js: no %s", path); return 0; }
    fseek(f, 0, SEEK_END);
    size = ftell(f);
    fseek(f, 0, SEEK_SET);
    buffer = malloc((size_t)size + 1);
    if (!buffer) { fclose(f); return 0; }
    size = (long)fread(buffer, 1, (size_t)size, f);
    buffer[size] = 0;
    fclose(f);
    status = JsHost_Load(name, buffer, (size_t)size);
    free(buffer);
    host->log(host, "js: loaded %s (%s)", path, status ? JsHost_LastError() : "ok");
    return status == 0;
}

static void on_monster(MemoriesModEvent *e)
{
    static const char *const handler[] = {"onSummon", "onFlip", "onTurnStart", "onCombat", "onDestroyed",
                                          "onDestroyOpponent"};
    char name[40];
    int card = e->a, record = e->b, when = e->c, status;
    if (e->phase != MEMORIES_BEFORE || when < 0 || when > 5) return;
    if (host->card_tag(host, card, "script", name, sizeof(name)) <= 0) return;
    if (!load_script(name)) return;
    source_record = record;
    status = JsHost_Call(name, handler[when], card, record, record / 15);
    if (status < 0) host->log(host, "js: %s.%s failed: %s", name, handler[when], JsHost_LastError());
}

static void overlay(void)
{
    int w, h, scale, tw;
    if (!banner[0] || host->now_us(host) > banner_until) return;
    host->overlay_size(host, &w, &h, &scale);
    scale *= 2;
    tw = host->text_width(host, banner, scale);
    host->fill(host, (w - tw) / 2 - 14 * scale, h / 2 - 14 * scale, tw + 28 * scale, 28 * scale, 0x101030, 200);
    host->draw_text(host, (w - tw) / 2, h / 2, banner, 0xFFE060, scale);
}
static unsigned overlay_signature(void)
{
    return banner[0] && host->now_us(host) <= banner_until ? banner_serial * 2 + 1 : banner_serial * 2;
}

int MemoriesModInit(const MemoriesModHost *from, MemoriesMod *mod)
{
    host = from;
    if (host->api < 10 || !host->subscribe || !host->card_tag) return 0;
    JsHost_SetApi(&api);
    mod->api = MEMORIES_MOD_API;
    mod->overlay = overlay;
    mod->overlay_signature = overlay_signature;
    if (!host->subscribe(host, MEMORIES_EVENT_MONSTER, 0, on_monster)) return 0;
    return 1;
}
