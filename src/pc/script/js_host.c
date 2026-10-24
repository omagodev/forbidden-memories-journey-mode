/* QuickJS host for card scripts: see js_host.h. */
#include "js_host.h"
#include "../third_party/quickjs/quickjs.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_SCRIPTS 64
static JSRuntime *rt;
static const JsHostApi *api;
static struct { char name[48]; JSContext *ctx; } scripts[MAX_SCRIPTS];
static int script_count;
static char last_error[512];

void JsHost_SetApi(const JsHostApi *a) { api = a; }
const char *JsHost_LastError(void) { return last_error; }

static int op(int code, int a, int b, int c, const char *s)
{
    return api && api->op ? api->op(code, a, b, c, s) : 0;
}

static void remember_error(JSContext *ctx)
{
    JSValue ex = JS_GetException(ctx);
    const char *text = JS_ToCString(ctx, ex);
    JSValue stack = JS_GetPropertyStr(ctx, ex, "stack");
    const char *where = JS_IsUndefined(stack) ? NULL : JS_ToCString(ctx, stack);
    snprintf(last_error, sizeof(last_error), "%s%s%s", text ? text : "exception", where ? "\n" : "", where ? where : "");
    if (text) JS_FreeCString(ctx, text);
    if (where) JS_FreeCString(ctx, where);
    JS_FreeValue(ctx, stack);
    JS_FreeValue(ctx, ex);
    op(JS_OP_LOG, 0, 0, 0, last_error);
}

/* ctx.fn(a, b, c): every method is one op; the magic number says which. */
static JSValue js_op(JSContext *ctx, JSValueConst this_val, int argc, JSValueConst *argv, int magic)
{
    int v[3] = {0, 0, 0}, i;
    for (i = 0; i < argc && i < 3; i++) JS_ToInt32(ctx, &v[i], argv[i]);
    switch (magic) {
    case JS_OP_LOG: case JS_OP_SAY: {
        const char *s = argc ? JS_ToCString(ctx, argv[0]) : NULL;
        op(magic, 0, 0, 0, s ? s : "");
        if (s) JS_FreeCString(ctx, s);
        return JS_UNDEFINED;
    }
    case JS_OP_HAND_COUNT: case JS_OP_CARD_ID: case JS_OP_ATK: case JS_OP_DEF: case JS_OP_LIFE:
        return JS_NewInt32(ctx, op(magic, v[0], 0, 0, NULL));
    default:
        return JS_NewInt32(ctx, op(magic, v[0], v[1], v[2], NULL));
    }
}

static JSValue js_field_monsters(JSContext *ctx, JSValueConst this_val, int argc, JSValueConst *argv, int magic)
{
    int side = 0, out[16], n, i;
    JSValue array = JS_NewArray(ctx);
    if (argc) JS_ToInt32(ctx, &side, argv[0]);
    n = api && api->list ? api->list(JS_LIST_FIELD_MONSTERS, side, out, 16) : 0;
    for (i = 0; i < n; i++) JS_SetPropertyUint32(ctx, array, (uint32_t)i, JS_NewInt32(ctx, out[i]));
    return array;
}

static JSContext *find(const char *name)
{
    int i;
    for (i = 0; i < script_count; i++)
        if (!strcmp(scripts[i].name, name)) return scripts[i].ctx;
    return NULL;
}

int JsHost_Loaded(const char *name) { return find(name) != NULL; }

int JsHost_Load(const char *name, const char *source, size_t length)
{
    JSContext *ctx;
    JSValue result;
    if (!rt) {
        rt = JS_NewRuntime();
        if (!rt) return -1;
        JS_SetMaxStackSize(rt, 0);   /* the game's stack is not the one QuickJS measures */
    }
    if (find(name) || script_count == MAX_SCRIPTS) return -1;
    ctx = JS_NewContext(rt);
    if (!ctx) return -1;
    result = JS_Eval(ctx, source, length, name, JS_EVAL_TYPE_GLOBAL);
    if (JS_IsException(result)) {
        remember_error(ctx);
        JS_FreeContext(ctx);
        return -1;
    }
    JS_FreeValue(ctx, result);
    snprintf(scripts[script_count].name, sizeof(scripts[0].name), "%s", name);
    scripts[script_count++].ctx = ctx;
    return 0;
}

int JsHost_Has(const char *name, const char *fn)
{
    JSContext *ctx = find(name);
    JSValue global, f;
    int has;
    if (!ctx) return 0;
    global = JS_GetGlobalObject(ctx);
    f = JS_GetPropertyStr(ctx, global, fn);
    has = JS_IsFunction(ctx, f);
    JS_FreeValue(ctx, f);
    JS_FreeValue(ctx, global);
    return has;
}

int JsHost_Call(const char *name, const char *fn, int card, int record, int side)
{
    static const struct { const char *name; int magic, args; } methods[] = {
        {"damage", JS_OP_DAMAGE, 2}, {"heal", JS_OP_HEAL, 2}, {"boost", JS_OP_BOOST, 3},
        {"destroy", JS_OP_DESTROY, 1}, {"handCount", JS_OP_HAND_COUNT, 1}, {"cardId", JS_OP_CARD_ID, 1},
        {"atk", JS_OP_ATK, 1}, {"def", JS_OP_DEF, 1}, {"life", JS_OP_LIFE, 1},
        {"log", JS_OP_LOG, 1}, {"say", JS_OP_SAY, 1}};
    JSContext *ctx = find(name);
    JSValue global, f, c, r;
    unsigned i;
    int status = 0;
    if (!ctx) return 1;
    global = JS_GetGlobalObject(ctx);
    f = JS_GetPropertyStr(ctx, global, fn);
    if (!JS_IsFunction(ctx, f)) {
        JS_FreeValue(ctx, f);
        JS_FreeValue(ctx, global);
        return 1;
    }
    c = JS_NewObject(ctx);
    JS_SetPropertyStr(ctx, c, "card", JS_NewInt32(ctx, card));
    JS_SetPropertyStr(ctx, c, "record", JS_NewInt32(ctx, record));
    JS_SetPropertyStr(ctx, c, "side", JS_NewInt32(ctx, side));
    JS_SetPropertyStr(ctx, c, "opp", JS_NewInt32(ctx, side ^ 1));
    for (i = 0; i < sizeof(methods) / sizeof(methods[0]); i++)
        JS_SetPropertyStr(ctx, c, methods[i].name,
                          JS_NewCFunctionMagic(ctx, js_op, methods[i].name, methods[i].args, JS_CFUNC_generic_magic,
                                               methods[i].magic));
    JS_SetPropertyStr(ctx, c, "fieldMonsters",
                      JS_NewCFunctionMagic(ctx, js_field_monsters, "fieldMonsters", 1, JS_CFUNC_generic_magic, 0));
    r = JS_Call(ctx, f, global, 1, &c);
    if (JS_IsException(r)) {
        remember_error(ctx);
        status = -1;
    }
    JS_FreeValue(ctx, r);
    JS_FreeValue(ctx, c);
    JS_FreeValue(ctx, f);
    JS_FreeValue(ctx, global);
    /* Drain nothing: scripts are synchronous. */
    return status;
}
