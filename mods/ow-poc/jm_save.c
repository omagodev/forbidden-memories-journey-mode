/* Journey Mode's save: one file in the player's data directory ("journey.sav", through
 * host->open_data), written by START > Save and read when Journey Mode is continued.  Save states
 * carry the same struct (host->register_state), including this run's deck and chest. */
#include "jm.h"
#include <string.h>

#define MAGIC 0x31534A4Du      /* "MJS1" */
#define VERSION 8          /* 2 language, 3 painted position, 4 layered hero, 5 economy, 6 Kingdom (flags 32-63, stars, area), 7 flags 64-95 in kflags2, 8 private cards; older files still load (remainder zero-filled) */

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
    if (Paint_Loaded()) { float a, b, c, d; Paint_Info(&a, &b, &c, &d); jm.pt_x = a; jm.pt_y = b; jm.pt_set = 1; jm.pt_area = Paint_SaveArea(); }
    Lang_PrefWrite(jm.lang);
    if (jm.stage >= 10 && jm.stars <= 0) { LOG("journey: no save at zero stars (game over)"); return 0; }
    Journey_CardsCapture();
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
    if (jm.stars_owed > 0) { jm.stars += jm.stars_owed; if (jm.stars > 10) jm.stars = 10; jm.stars_owed = 0; }   /* 0.5.3's owed stars come back: the wagers replace them */
    if (jm.stage >= 10 && jm.stars <= 0) jm.stars = 1;      /* a 0.5.x save at zero (never written now) */
    LOG("journey: loaded (stage %d, flags %08x, %s)", jm.stage, jm.flags, jm.name);
    return 1;
}

void Save_Delete(void)
{
    FILE *f = jm_host->open_data(jm_host, "journey.sav", "wb");
    if (f) fclose(f);
}

/* Live guest RAM is only the working copy used by duels and Build Deck. */
extern unsigned short gDuel_awPlayerDeck[40];
extern unsigned char gLibrary_abCardChest[];
extern unsigned gLibrary_dwStarchips;

void Journey_CardsCapture(void)
{
    memcpy(jm.deck, gDuel_awPlayerDeck, sizeof(jm.deck));
    memcpy(jm.chest, gLibrary_abCardChest, sizeof(jm.chest));
    jm.duel_stars = gLibrary_dwStarchips;
    jm.cards_set = 1;
}

void Journey_CardsRestore(void)
{
    if (!jm.cards_set) {
        /* v1-v7 never saved deck/chest. Shared RAM may be a classic/Free Duel
         * deck: rebuild only the starter and explicitly recorded story rewards.
         * Unknown old drops/purchases cannot safely be inferred from that RAM. */
        Journey_GiveStarter();
        jm.cards_set = 0;
        Story_Regrant();
        Journey_CardsCapture();
        LOG("journey: migrated legacy inventory (starter + recorded rewards)");
    }
    memcpy(gDuel_awPlayerDeck, jm.deck, sizeof(jm.deck));
    memcpy(gLibrary_abCardChest, jm.chest, sizeof(jm.chest));
    gLibrary_dwStarchips = jm.duel_stars;
}
