/* A game mode a code mod runs (mod_mode.h); a proof of concept. */
#include "mod_mode.h"
#include "types.h"
#include <string.h>

extern u8 D_8009B26C, D_8009B268, D_8009B26D;

static void (*runner)(int first);
static int on;
static unsigned char text[MOD_MODE_TEXT_SIZE];

void ModMode_Register(void (*run)(int first)) { runner = run; }
int ModMode_Active(void) { return on && runner && (D_8009B26C & 0x1F) == 13; }

void ModMode_Enter(void)
{
    if (!runner) return;
    on = 1;
    D_8009B268 = 1;
    D_8009B26C = 13;   /* bit 0x40 clear: the first frame */
}

void ModMode_Leave(int menu)
{
    on = 0;
    D_8009B268 = 1;
    D_8009B26D = (u8)menu;
    D_8009B26C = 8;   /* MAIN_MODE_MENU */
}

void ModMode_SetText(const unsigned char *codes, int length)
{
    if (length < 1 || length > MOD_MODE_TEXT_SIZE) length = MOD_MODE_TEXT_SIZE;
    memcpy(text, codes, (size_t)length);
    text[length - 1] = 0xFF;
}

const unsigned char *ModMode_Text(int id)
{
    return (id == MOD_MODE_TEXT_ID && ModMode_Active()) ? text : NULL;
}

int ModMode_Run(void)
{
    int first;
    if (!ModMode_Active()) return 0;
    first = !(D_8009B26C & 0x40);
    D_8009B26C |= 0x40;
    runner(first);
    return 1;
}
