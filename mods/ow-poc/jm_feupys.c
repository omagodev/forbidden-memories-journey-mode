/* InsetoKaiba's deck of Feupys parody cards (mod.json "cards", ids "feupys_*"; art cropped from Feupys' public videos,
 * see CREDITS): they are owned only through Journey (jm.feupys, saved by identity, not by runtime id) and dropped only
 * by a won InsetoKaiba duel (the ship duel and the castle gate's), at FEUPYS_DROP_BP in 10000, one card at most. */
#include "jm.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define FEUPYS_DROP_BP 400            /* 4% per won InsetoKaiba duel */
#define DECK_TAG 0xF000u

extern unsigned char gCard_abExtraChest[];
extern unsigned short gDuel_awPlayerDeck[40];

static const char *const keys[FEUPYS_N] = {
    "feupys_clt", "feupys_amante", "feupys_cigarro", "feupys_roberto", "feupys_obelisco", "feupys_r10",
    "feupys_dragao_ra", "feupys_agiota", "feupys_conselho", "feupys_volta", "feupys_forca_espelho", "feupys_kuriboh_branco",
};
static int ids[FEUPYS_N], looked;

int Feupys_Id(int i)
{
    if (!looked) {
        int k;
        char identity[48];
        for (k = 0; k < FEUPYS_N; k++) {
            snprintf(identity, sizeof(identity), "ow-poc:%s:1", keys[k]);
            ids[k] = jm_host && jm_host->card_id ? jm_host->card_id(jm_host, identity) : 0;
            if (ids[k] <= 722) ids[k] = 0;
        }
        looked = 1;
        LOG("feupys: card ids %d..%d", ids[0], ids[FEUPYS_N - 1]);
    }
    return i >= 0 && i < FEUPYS_N ? ids[i] : 0;
}

int Feupys_Index(int id)
{
    int i;
    if (id <= 722) return -1;
    for (i = 0; i < FEUPYS_N; i++) if (Feupys_Id(i) == id) return i;
    return -1;
}

void Feupys_Capture(void)
{
    int i;
    for (i = 0; i < FEUPYS_N; i++) jm.feupys[i] = Feupys_Id(i) ? gCard_abExtraChest[Feupys_Id(i)] : jm.feupys[i];
    for (i = 0; i < 40; i++) {
        int k = Feupys_Index(jm.deck[i] & 0x7FFF);
        if (k >= 0) jm.deck[i] = (unsigned short)(DECK_TAG + k);
    }
}

void Feupys_Restore(void)
{
    int i;
    for (i = 0; i < FEUPYS_N; i++) if (Feupys_Id(i)) gCard_abExtraChest[Feupys_Id(i)] = jm.feupys[i];
    for (i = 0; i < 40; i++) {
        unsigned w = jm.deck[i];
        if ((w & 0xFFF0u) == DECK_TAG && (int)(w & 15) < FEUPYS_N) {
            int id = Feupys_Id((int)(w & 15));
            gDuel_awPlayerDeck[i] = (unsigned short)(id ? id : 0);
        }
    }
    {
        int owned = 0, in_deck = 0;
        for (i = 0; i < FEUPYS_N; i++) owned += jm.feupys[i];
        for (i = 0; i < 40; i++) in_deck += (jm.deck[i] & 0xFFF0u) == DECK_TAG;
        if (owned || in_deck) LOG("feupys: restored %d owned, %d in the deck", owned, in_deck);
    }
}

void Feupys_ClearChest(void)
{
    int i;
    for (i = 0; i < FEUPYS_N; i++) if (Feupys_Id(i)) gCard_abExtraChest[Feupys_Id(i)] = 0;
    memset(jm.feupys, 0, sizeof(jm.feupys));
}

int Feupys_RollDrop(const char *npc_id)
{
    int r;
    if (!npc_id || (strcmp(npc_id, "inseto_kaiba") && strcmp(npc_id, "inseto_gate"))) return 0;
    r = rand() % 10000;
    /* tests only: with debug.json present, MEMORIES_MOD_OW_POC_FEUPYS_DROP_BP (or mod.ow-poc.feupys_drop_bp) overrides the 4%; a player build always rolls 4% */
    if (r >= (Dbg_On() && jm_host->setting ? jm_host->setting(jm_host, "feupys_drop_bp", FEUPYS_DROP_BP) : FEUPYS_DROP_BP)) { LOG("feupys: InsetoKaiba won, no special card (roll %d)", r); return 0; }
    {
        int k = rand() % FEUPYS_N, id = Feupys_Id(k);
        LOG("feupys: InsetoKaiba drops %s (id %d, roll %d)", keys[k], id, r);
        return id;
    }
}
