/* Languages.  Every string the player reads is data: assets/lang/languages.json lists the codes, and
 * assets/lang/<code>/ui.json (menus, HUD, names) and story.json (the scripts) hold the text.  Adding a
 * language is adding that folder and its code to the list; nothing here knows what the languages are. */
#include "jm.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static JsonNode *codes;                 /* assets/lang/languages.json: ["en", "pt"] */
static JsonNode *ui;                    /* the current ui.json */
static JsonNode *names[8];              /* the language names, read once */
static int cur = -1;

int Lang_Count(void)
{
    if (!codes) {
        char *t = Jm_ReadText("assets/lang/languages.json");
        if (t) { codes = Json_Parse(t); free(t); }
    }
    return codes ? Json_Count(codes) : 0;
}

static const char *code_of(int i)
{
    JsonNode *n = codes ? Json_At(codes, i) : NULL;
    return n && n->str ? n->str : NULL;
}

static JsonNode *load_json(const char *code, const char *file)
{
    char path[80], *t;
    JsonNode *j = NULL;
    snprintf(path, sizeof(path), "assets/lang/%s/%s", code, file);
    t = Jm_ReadText(path);
    if (t) { j = Json_Parse(t); free(t); }
    if (!j) LOG("journey: cannot read %s", path);
    return j;
}

static const char *walk(const JsonNode *root, const char *path, const JsonNode **node)
{
    const JsonNode *n = root;
    const char *p = path;
    while (n && *p) {
        char seg[40];
        size_t len = 0;
        while (p[len] && p[len] != '.') len++;
        if (len >= sizeof(seg)) return NULL;
        memcpy(seg, p, len);
        seg[len] = 0;
        n = (seg[0] >= '0' && seg[0] <= '9') ? Json_At(n, atoi(seg)) : Json_Get(n, seg);
        p += len + (p[len] == '.');
    }
    *node = n;
    return n && n->str ? n->str : NULL;
}

/* The string at a dotted path of the current language ("menu.items.2"), or the path itself. */
const char *Tr(const char *path)
{
    const JsonNode *n;
    const char *s = walk(ui, path, &n);
    return s ? s : path;
}

const char *TrAt(const char *path, int index, const char *fallback)
{
    const JsonNode *n, *a;
    const char *s = NULL;
    walk(ui, path, &n);
    a = n ? Json_At(n, index) : NULL;
    if (a && a->str) s = a->str;
    return s ? s : fallback;
}

/* The name of a person or speaker: ui "npc_names" / "speaker_names" by id. */
const char *TrKey(const char *group, const char *id, const char *fallback)
{
    const JsonNode *g = ui ? Json_Get(ui, group) : NULL, *n = g ? Json_Get(g, id) : NULL;
    return n && n->str ? n->str : fallback;
}

static JsonNode *ui_of(int i)
{
    const char *c = code_of(i);
    if (i < 0 || i >= 8 || !c) return NULL;
    if (!names[i]) names[i] = load_json(c, "ui.json");
    return names[i];
}

const char *Lang_Name(int i)
{
    JsonNode *j = ui_of(i);
    return j ? Json_Str(Json_Get(j, "language"), "name", code_of(i)) : "?";
}

int Lang_Current(void) { return cur < 0 ? 0 : cur; }
const char *Lang_Code(void) { const char *c = code_of(Lang_Current()); return c ? c : "en"; }

/* The language picked the first time Journey Mode starts a new game is kept in language.cfg (the mod's data folder), so the
 * choice screen only shows then; the START menu's Language row changes it later (and every save writes it). */
int Lang_PrefRead(void)
{
    FILE *f = jm_host->open_data(jm_host, "language.cfg", "rb");
    int v = -1;
    char buf[16];
    size_t n;
    if (!f) return -1;
    n = fread(buf, 1, sizeof(buf) - 1, f);
    fclose(f);
    buf[n] = 0;
    if (n > 0 && buf[0] >= '0' && buf[0] <= '9') v = atoi(buf);
    return v >= 0 && v < Lang_Count() ? v : -1;
}

void Lang_PrefWrite(int i)
{
    FILE *f = jm_host->open_data(jm_host, "language.cfg", "wb");
    char buf[16];
    int n;
    if (!f) return;
    n = snprintf(buf, sizeof(buf), "%d\n", i);
    fwrite(buf, 1, (size_t)n, f);
    fclose(f);
}

/* Loads the interface and the story of language i (the first one if i is not a language). */
int Lang_Set(int i)
{
    JsonNode *j;
    if (Lang_Count() < 1) return 0;
    if (i < 0 || i >= Lang_Count()) i = 0;
    j = ui_of(i);
    if (!j) return 0;
    ui = j;
    cur = i;
    jm.lang = i;
    Story_LoadScenes(code_of(i));
    Eco_LoadLang(code_of(i));
    LOG("journey: language %s", code_of(i));
    return 1;
}
