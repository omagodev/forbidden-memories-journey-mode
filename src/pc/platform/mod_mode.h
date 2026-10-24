#ifndef MEMORIES_PC_MOD_MODE_H
#define MEMORIES_PC_MOD_MODE_H
/* A proof of concept: a game mode a code mod runs. It borrows the developer-mode slot
 * (MAIN_MODE_UNUSED_DEVELOPER = 13) that the tower also uses: the tower's runner only
 * runs while no mod mode is on. A mod registers its per-frame runner, enters the
 * mode from a title menu item (MENU/SCENE events), and leaves with ModMode_Leave().
 * Text for the game's own dialogue box comes from ModMode_SetText (string id 0xFFF7). */
#define MOD_MODE_TEXT_ID 0xFFF7
#define MOD_MODE_TEXT_SIZE 1024

void ModMode_Register(void (*run)(int first_frame));
int ModMode_Active(void);
/* Take the screen: the next frame the game runs the mod's runner (first_frame = 1). */
void ModMode_Enter(void);
/* Back to the title (menu byte D_8009B26D = menu), through a fade that the mod has done. */
void ModMode_Leave(int menu);
/* The game's codes (as Glyphs_Code makes them, 0xFE line, 0xFA page wait, 0xFF end). */
void ModMode_SetText(const unsigned char *codes, int length);
const unsigned char *ModMode_Text(int id);
/* Called by Main_RunUnusedDeveloperMode: 1 when a mod mode ran. */
int ModMode_Run(void);

#endif
