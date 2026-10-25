#ifndef MEMORIES_PC_SCRIPT_JS_HOST_H
#define MEMORIES_PC_SCRIPT_JS_HOST_H
/* QuickJS embedded in the game, for card scripts (YGOPro style).
 * The engine knows nothing about the duel: a code mod gives it a JsHostApi
 * (the duel operations a script's ctx may ask for) and loads scripts.
 * A proof of concept: mods/js-scripts is the one user. */
#include <stddef.h>

enum {
    JS_OP_DAMAGE = 1,   /* a side, b amount */
    JS_OP_HEAL,         /* a side, b amount */
    JS_OP_BOOST,        /* a record, b atk, c def */
    JS_OP_DESTROY,      /* a record */
    JS_OP_HAND_COUNT,   /* a side -> cards in hand */
    JS_OP_CARD_ID,      /* a record -> card id (0 empty) */
    JS_OP_ATK,          /* a record -> current ATK */
    JS_OP_DEF,          /* a record -> current DEF */
    JS_OP_LIFE,         /* a side -> life points */
    JS_OP_LOG,          /* s message (log line) */
    JS_OP_SAY           /* s message (on-screen line) */
};
enum { JS_LIST_FIELD_MONSTERS = 1 };

typedef struct {
    int (*op)(int op, int a, int b, int c, const char *s);
    /* Fills out[] (at most max) with duel records; returns how many. */
    int (*list)(int what, int side, int *out, int max);
} JsHostApi;

void JsHost_SetApi(const JsHostApi *api);
/* Compile and run a script's top level in a context of its own. 0 on success. */
int JsHost_Load(const char *name, const char *source, size_t length);
int JsHost_Loaded(const char *name);
/* Whether the script defines a global function `fn`. */
int JsHost_Has(const char *name, const char *fn);
/* Calls fn(ctx) with ctx {card, record, side, opp, ...}. Returns 0 on success, -1 on a JS error
 * (see JsHost_LastError), 1 when the script has no such function. */
int JsHost_Call(const char *name, const char *fn, int card, int record, int side);
const char *JsHost_LastError(void);

#endif
