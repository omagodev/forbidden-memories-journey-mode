/* A small JSON reader: the story and rules are data, not code. */
#include "jm.h"
#include <stdlib.h>
#include <string.h>

typedef struct { const char *p; int bad; } Cursor;

static void skip(Cursor *c)
{
    while (*c->p == ' ' || *c->p == '\n' || *c->p == '\r' || *c->p == '\t') c->p++;
}

static JsonNode *node(char type)
{
    JsonNode *n = calloc(1, sizeof(*n));
    if (n) n->type = type;
    return n;
}

static char *string(Cursor *c)
{
    size_t cap = 64, len = 0;
    char *s = malloc(cap);
    if (!s) { c->bad = 1; return NULL; }
    c->p++;
    while (*c->p && *c->p != '"') {
        unsigned ch = (unsigned char)*c->p++;
        if (ch == '\\') {
            ch = (unsigned char)*c->p++;
            if (ch == 'n') ch = '\n';
            else if (ch == 't') ch = '\t';
            else if (ch == 'u') {
                char hex[5] = {0};
                memcpy(hex, c->p, 4);
                c->p += 4;
                ch = (unsigned)strtoul(hex, NULL, 16);
            }
        }
        if (len + 5 > cap) { cap *= 2; s = realloc(s, cap); if (!s) { c->bad = 1; return NULL; } }
        if (ch < 0x80) s[len++] = (char)ch;
        else if (ch < 0x800) { s[len++] = (char)(0xC0 | ch >> 6); s[len++] = (char)(0x80 | (ch & 0x3F)); }
        else { s[len++] = (char)(0xE0 | ch >> 12); s[len++] = (char)(0x80 | ((ch >> 6) & 0x3F)); s[len++] = (char)(0x80 | (ch & 0x3F)); }
    }
    if (*c->p != '"') c->bad = 1;
    else c->p++;
    s[len] = 0;
    return s;
}

static JsonNode *value(Cursor *c, int depth)
{
    JsonNode *n, **tail;
    skip(c);
    if (depth > 24 || c->bad) { c->bad = 1; return NULL; }
    if (*c->p == '{' || *c->p == '[') {
        char open = *c->p++, close = open == '{' ? '}' : ']';
        n = node(open == '{' ? 'o' : 'a');
        tail = &n->child;
        skip(c);
        if (*c->p == close) { c->p++; return n; }
        for (;;) {
            JsonNode *v;
            char *key = NULL;
            skip(c);
            if (open == '{') {
                if (*c->p != '"') { c->bad = 1; return n; }
                key = string(c);
                skip(c);
                if (*c->p++ != ':') { c->bad = 1; return n; }
            }
            v = value(c, depth + 1);
            if (!v) { c->bad = 1; return n; }
            v->key = key;
            *tail = v;
            tail = &v->next;
            skip(c);
            if (*c->p == ',') { c->p++; continue; }
            if (*c->p == close) { c->p++; return n; }
            c->bad = 1;
            return n;
        }
    }
    if (*c->p == '"') {
        n = node('s');
        n->str = string(c);
        return n;
    }
    if (!strncmp(c->p, "true", 4)) { c->p += 4; n = node('b'); n->num = 1; return n; }
    if (!strncmp(c->p, "false", 5)) { c->p += 5; n = node('b'); return n; }
    if (!strncmp(c->p, "null", 4)) { c->p += 4; return node('0'); }
    {
        char *end;
        double d = strtod(c->p, &end);
        if (end == c->p) { c->bad = 1; return NULL; }
        c->p = end;
        n = node('n');
        n->num = d;
        return n;
    }
}

JsonNode *Json_Parse(const char *text)
{
    Cursor c = {text, 0};
    JsonNode *root = value(&c, 0);
    if (c.bad) { Json_Free(root); return NULL; }
    return root;
}

void Json_Free(JsonNode *n)
{
    while (n) {
        JsonNode *next = n->next;
        Json_Free(n->child);
        free((void *)n->key);
        free((void *)n->str);
        free(n);
        n = next;
    }
}

JsonNode *Json_Get(const JsonNode *o, const char *key)
{
    JsonNode *n;
    if (!o) return NULL;
    for (n = o->child; n; n = n->next)
        if (n->key && !strcmp(n->key, key)) return n;
    return NULL;
}

const char *Json_Str(const JsonNode *o, const char *key, const char *fallback)
{
    JsonNode *n = Json_Get(o, key);
    return n && n->type == 's' && n->str ? n->str : fallback;
}

double Json_Num(const JsonNode *o, const char *key, double fallback)
{
    JsonNode *n = Json_Get(o, key);
    return n && (n->type == 'n' || n->type == 'b') ? n->num : fallback;
}

int Json_Count(const JsonNode *a)
{
    int k = 0;
    JsonNode *n;
    if (!a) return 0;
    for (n = a->child; n; n = n->next) k++;
    return k;
}

JsonNode *Json_At(const JsonNode *a, int i)
{
    JsonNode *n;
    if (!a) return NULL;
    for (n = a->child; n && i > 0; n = n->next) i--;
    return n;
}

unsigned char *Jm_Slurp(const char *name, long *size)
{
    FILE *f = jm_host->open_asset(jm_host, name);
    unsigned char *data;
    long n;
    if (!f) return NULL;
    fseek(f, 0, SEEK_END);
    n = ftell(f);
    fseek(f, 0, SEEK_SET);
    data = malloc((size_t)n + 1);
    if (data && fread(data, 1, (size_t)n, f) != (size_t)n) { free(data); data = NULL; }
    fclose(f);
    if (data) data[n] = 0;
    if (size) *size = n;
    return data;
}

char *Jm_ReadText(const char *name) { return (char *)Jm_Slurp(name, NULL); }
