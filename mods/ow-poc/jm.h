/* Journey Mode: what the parts of the mod share.
 *
 *   ow_poc.c    entry, events, the per-frame state machine, the overlay
 *   jm_gfx.c    assets, meshes, the projection and the polygon sorting
 *   jm_world.c  the map: loading, collision, areas, drawing, the people on it
 *   jm_json.c   a small JSON reader for the story and rules data
 *   jm_story.c  rules, scenes and dialogue
 *   jm_ui.c     character creation and the START menu
 *   jm_save.c   the save file
 */
#ifndef JM_H
#define JM_H
#include "pc/mods/modapi.h"

extern const MemoriesModHost *jm_host;
#define LOG(...) jm_host->log(jm_host, __VA_ARGS__)

/* The console's pad word (host->pad). */
#define PAD_SELECT 0x0001
#define PAD_START 0x0008
#define PAD_UP 0x0010
#define PAD_RIGHT 0x0020
#define PAD_DOWN 0x0040
#define PAD_LEFT 0x0080
#define PAD_L1 0x0400
#define PAD_R1 0x0800
#define PAD_TRIANGLE 0x1000
#define PAD_CIRCLE 0x2000
#define PAD_CROSS 0x4000
#define PAD_SQUARE 0x8000

/* ------------------------------------------------------------------ json */
typedef struct JsonNode JsonNode;
struct JsonNode {
    char type;            /* 'o' object, 'a' array, 's' string, 'n' number, 'b' bool, '0' null */
    const char *key;      /* in an object: the member's name */
    const char *str;      /* 's' */
    double num;           /* 'n', 'b' */
    JsonNode *child, *next;
};
JsonNode *Json_Parse(const char *text);          /* NULL on a syntax error; free with Json_Free */
void Json_Free(JsonNode *root);
JsonNode *Json_Get(const JsonNode *object, const char *key);
const char *Json_Str(const JsonNode *object, const char *key, const char *fallback);
double Json_Num(const JsonNode *object, const char *key, double fallback);
int Json_Count(const JsonNode *array);
JsonNode *Json_At(const JsonNode *array, int index);
/* The whole of an asset as a NUL-terminated string (free it), NULL if missing. */
char *Jm_ReadText(const char *name);
unsigned char *Jm_Slurp(const char *name, long *size);

/* ------------------------------------------------------------------- gfx */
#define BANK 14
#define ATLAS_W 768
#define ATLAS_H 256
/* The atlas (assets/atlas.raw): 64x64 tiles on page 0, sprites on page 1, portraits on page 2. */
enum {
    TX_SAND0, TX_SAND1, TX_SAND2, TX_CRACKED, TX_PATH0, TX_PATH1, TX_WATER0, TX_WATER1,
    TX_WALL_TOP, TX_WALL_SIDE, TX_MARBLE, TX_LAPIS, TX_ARENA, TX_GLOW, TX_GRANITE, TX_OASIS,
    /* page 2, below the portraits (tools/make_props.py) */
    TX_GRASS, TX_PLANK
};
void Gfx_TexXY(int tex, int *ax, int *ay);           /* where texture `tex` is in the atlas */
/* Prop sprites on page 2, y 176: a jar (24x32 at x 512), a signpost (32x40 at 536), a crate (32x32 at 568) */
#define SPR_X 256            /* page 1 */
#define PORT_X 512           /* page 2: player portraits 0..3, the Prince at 4 */
#define PORT_Y 0
#define DYN_PORT_X 256       /* the speaker's portrait, read from the disc */
#define DYN_PORT_Y 128

typedef struct {
    int nv, nf, nframes, smooth;
    short *verts;               /* nframes * nv * 3 */
    signed char *nrm;           /* nv * 3 (smooth) */
    unsigned char *slot;        /* nv (smooth): 0 other, 1 skin, 2 hair, 3 outfit, 4 trousers */
    unsigned char *col;         /* smooth: nv * 3; flat: nf * 3 */
    unsigned char *lift;        /* flat: half the depth units a face is sorted nearer (doors on a wall) */
    unsigned short *faces;      /* nf * 3 */
} Mesh;

int Gfx_LoadAssets(void);
int Gfx_Ready(void);
Mesh *Gfx_Mesh(const char *name);    /* "Wizard", "p_agave", ...; loaded once */

/* Camera */
extern float cam_x, cam_z, cam_d;
void Gfx_SetCamera(float distance, float pitch_degrees);
#ifndef CAM_D
#define CAM_D 1350.0f
#endif
#ifndef CAM_PITCH
#define CAM_PITCH 50.0f
#endif
#ifndef CAM_RING
#define CAM_RING 1            /* a ring under the player */
#endif
#ifndef CHAR_SCALE
#define CHAR_SCALE 1.6f
#endif
int Gfx_Project(float wx, float wy, float wz, float *sx, float *sy, float *depth);
void Gfx_Begin(void);                /* the sky, and an empty scene */
int Gfx_Items(void);                 /* polygons pushed so far this frame */
void Gfx_End(void);                  /* sorts the scene into the ordering table */
void Gfx_GroundQuad(const float sx[4], const float sy[4], int tile, const unsigned char rgb[4][3]);
/* Textured quad into the sorted scene; u,v,w,h a rectangle of the atlas. tl, tr, bl, br order. */
void Gfx_SceneQuad(const float sx[4], const float sy[4], int ax, int ay, int w, int h, float depth,
                   const unsigned char rgb[4][3], int flip);
void Gfx_SceneTri(float x0, float y0, float x1, float y1, float x2, float y2, const unsigned char rgb[3][3],
                  float depth);
void Gfx_Sprite(float wx, float wz, int ax, int ay, int w, int h, float ww, float wh, int shade, int flip);
void Gfx_Shadow(float wx, float wz, float size);
/* A mesh at (wx, wz), turned by yaw, scaled; colours set the four creator slots (0xRRGGBB or -1). */
void Gfx_DrawMesh(const Mesh *m, int frame, float wx, float wy, float wz, float yaw, float scale, const int slot_rgb[5],
                  float bias);
/* A 2D quad straight into the ordering table, nearest slot (portraits). */
void Gfx_Portrait(int x, int y, int size, int ax, int ay);
void Gfx_Rect(int x, int y, int w, int h, int r, int g, int b);
void Gfx_Backdrop(int top_rgb, int bottom_rgb);
int Gfx_LoadFace(int duelist);                       /* disc portrait into the speaker slot */
extern unsigned gfx_frame;

/* ----------------------------------------------------------------- world */
#define MW 64
#define MH 168                /* 72 rows of map, then four rows of two rooms */
#define RW 32                 /* a room: 32 x 24 tiles */
#define RH 24
#define TS 32
#define RO 16
enum { T_SAND, T_PATH, T_WATER, T_WALL, T_4, T_ARENA, T_6, T_7, T_PALM, T_RUIN, T_COL, T_OBEL, T_PORTAL, T_PAL,
       T_DOOR, T_THRONE, T_GATE, T_HOUSE, T_HOUSE_B, T_BRIDGE, T_GRASS };
/* deco numbers: 1..7 meshes, 8..15 plants, 16 jar, 17 sign, 20 crate (sprites), 23 solid and invisible (a mesh of props.json) */

typedef struct {
    char id[16];
    char name[24];
    char mesh[24];
    int duelist_id;              /* the game's duelist number, 0 for none */
    int portrait_id;             /* the duelist whose face the dialogue shows, 0 for none */
    float x, z, yaw;
    int hidden;
    JsonNode *rules;             /* "talk" */
    JsonNode *moves;             /* "places" */
    JsonNode *base;              /* "tile" */
    Mesh *mesh_ptr;
} Npc;
#define MAX_NPC 40
extern Npc npcs[MAX_NPC];
extern int npc_count;

int World_Load(void);
void World_PlaceNpcs(void);                          /* positions and visibility for the story state */
int World_Solid(float x, float z);                   /* tile collision with the flag locks */
int World_Blocked(float x, float z);                 /* the whole body: tiles, props, people */
int World_LockedTile(float x, float z);              /* the locked gate/portal tile at a point, 0 none */
int World_Area(float x, float z);
const char *World_AreaName(int area);
int World_AreaMusic(int area);
void World_Draw(float px, float pz, float pyaw, int walking, const int body_rgb[5], const Mesh *body);
int World_NearestNpc(float x, float z, float reach);
void World_Spawn(float *x, float *z);

/* ------------------------------------------------------------- languages */
int Lang_Count(void);
const char *Lang_Name(int i);
int Lang_Current(void);
int Lang_Set(int i);                                 /* loads the interface and the story of language i */
const char *Tr(const char *path);                    /* "menu.items.2" in the current language, else the path */
const char *TrAt(const char *path, int index, const char *fallback);
const char *TrKey(const char *group, const char *id, const char *fallback);
void Story_LoadScenes(const char *code);

/* ----------------------------------------------------------------- guide */
void Guide_Update(void);                             /* picks the target and the way to it from the story state */
void Guide_Reset(void);
extern int jm_guide_on;                              /* the frame hook sets it while the player walks */
void Guide_Draw(float px, float pz);                 /* into the scene: marker, edge arrow, compass */
int Guide_Target(float *x, float *z, float *wx, float *wz);
unsigned World_MapColor(int tx, int tz);             /* a tile as 0xRRGGBB for the maps */

/* ----------------------------------------------------------------- story */
typedef struct {
    unsigned flags;              /* the duelists beaten, bit by name order in rules */
    int stage;
    int wins, losses, duels;
    unsigned item_flags;
    char name[20];
    int gender, hair, hair_col, skin, outfit, portrait;
    float x, z;                  /* where the player stands */
    unsigned short got_cards[48]; /* card ids rewards gave, so a loaded save can give them again */
    int got_count;
    int lang;                    /* index into assets/lang/languages.json */
} Journey;
extern Journey jm;

int Story_Load(void);
int Story_FlagBit(const char *name);                 /* the bit a flag name has (assigned on first use), -1 full */
int Story_Has(const char *flag);
int Story_Cond(const JsonNode *c);
extern JsonNode *jm_rules;
void Story_Set(const char *flag);
void Story_Reset(void);
const char *Story_Objective(void);
const char *Story_Chapter(void);
/* What pressing X near an NPC does: returns a scene id or NULL; fills the duel and result data. */
typedef struct {
    const char *scene;           /* shown first */
    int duel;                    /* an NPC id to duel after the scene, or -1 */
    const JsonNode *on_win, *on_lose;
    const JsonNode *scene_node;
    const char *then;            /* a scene to play when this one is over */
    const JsonNode *choice;      /* {yes, no} results for a Yes/No page that is not a duel */
} Talk;
int Story_TalkRule(const Npc *npc, Talk *out);
int Story_PoiAt(float x, float z, Talk *out);        /* a locked tile or spot the player pushes against */
int Story_Trigger(Talk *out, float *tp_x, float *tp_z, int *teleport); /* a line crossed; applies set_stage */
void Story_ApplyResult(const JsonNode *result);
extern int jm_warp;                                  /* set by a result with "teleport": where to put the player */
extern float jm_warp_x, jm_warp_z;
void Story_Regrant(void);      /* flags, stage, cards, items */
/* Pages of a scene. */
typedef struct { const char *who, *name, *text; int ask; } Page;
int Story_PageCount(const char *scene);
int Story_Page(const char *scene, int index, Page *out);
int Story_ItemList(char names[][32], int max);
int Story_Cards(int id);                             /* grants a card to the chest */

/* -------------------------------------------------------------- dialogue */
void Say_Page(const Page *page);                     /* builds the box text, opens the game's box */
void Say_Text(const char *name, const char *body);
void Say_Close(void);
int Say_Done(void);
void Say_Tick(void);

/* ------------------------------------------------------------------ save */
int Save_Exists(void);
int Save_Write(void);
int Save_Read(void);
void Save_Init(void);
void Save_Delete(void);

/* -------------------------------------------------------------------- ui */
typedef enum { UI_NONE, UI_CREATE, UI_MENU, UI_CONFIRM } UiMode;
void Ui_StartCreate(void);
int Ui_CreateInput(unsigned short edge);             /* 1 when the journey should begin */
void Ui_DrawCreate(void);                            /* 3D preview and portrait, in the frame hook */
void Ui_CreateOverlay(void);
void Ui_RefreshLook(void);
void Ui_BodyColours(int out[5]);
const char *Ui_BodyMesh(void);
int Ui_MenuInput(unsigned short edge);               /* 0 stay, 1 close, 2 deck, 3 title */
void Ui_MenuOverlay(void);
void Ui_MenuOpen(void);
unsigned Ui_Signature(void);
extern int ui_message_timer;
void Ui_Message(const char *text);
void Ui_RefreshName(void);
extern int jm_save_requested, jm_save_ok, jm_name_entry_requested;
const char *Ui_MessageText(void);

#endif
