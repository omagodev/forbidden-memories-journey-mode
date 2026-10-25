/* Journey Mode's save: one file in the player's data directory ("journey.sav", through
 * host->open_data), written by START > Save and read when Journey Mode is continued.  Save states
 * carry the same struct (host->register_state).  Cards a reward gave are in the game's own card
 * chest, which the game saves with its own save; the file lists them too, so a loaded Journey can
 * give any back that a different save lacks. */
#include "jm.h"
#include <string.h>

#define MAGIC 0x31534A4Du      /* "MJS1" */
#define VERSION 3          /* 2 added the language, 3 the painted village position; older files (176 bytes of Journey and up) still load */

typedef struct { unsigned magic, version, size; Journey data; } File;

void Save_Init(void)
{
    jm_host->register_state(jm_host, &jm, sizeof(jm), VERSION);
}

int Save_Exists(void)
{
    FILE *f = jm_host->open_data(jm_host, "journey.sav", "rb");
    long n;
    if (!f) return 0;
    fseek(f, 0, SEEK_END);
    n = ftell(f);
    fclose(f);
    return n > 0;
}

int Save_Write(void)
{
    File file;
    FILE *f;
    size_t n;
    if (Paint_Loaded()) { float a, b, c, d; Paint_Info(&a, &b, &c, &d); jm.pt_x = a; jm.pt_y = b; jm.pt_set = 1; }
    Lang_PrefWrite(jm.lang);
    file.magic = MAGIC;
    file.version = VERSION;
    file.size = sizeof(Journey);
    file.data = jm;
    f = jm_host->open_data(jm_host, "journey.sav", "wb");
    if (!f) { LOG("journey: cannot write the save"); return 0; }
    n = fwrite(&file, sizeof(file), 1, f);
    fclose(f);
    LOG("journey: saved (stage %d, flags %08x, %s)", jm.stage, jm.flags, jm.name);
    return n == 1;
}

int Save_Read(void)
{
    File file;
    FILE *f = jm_host->open_data(jm_host, "journey.sav", "rb");
    size_t n;
    if (!f) return 0;
    memset(&file, 0, sizeof(file));
    n = fread(&file, 1, sizeof(file), f);
    fclose(f);
    if (n < 12 + 176 || file.magic != MAGIC || file.version < 1 || file.version > VERSION || file.size > sizeof(Journey) ||
        n < 12 + file.size) {
        LOG("journey: the save file is not usable");
        return 0;
    }
    jm = file.data;
    if (file.size < sizeof(Journey)) memset((char *)&jm + file.size, 0, sizeof(Journey) - file.size);
    jm.name[sizeof(jm.name) - 1] = 0;
    LOG("journey: loaded (stage %d, flags %08x, %s)", jm.stage, jm.flags, jm.name);
    return 1;
}

void Save_Delete(void)
{
    FILE *f = jm_host->open_data(jm_host, "journey.sav", "wb");
    if (f) fclose(f);
}
