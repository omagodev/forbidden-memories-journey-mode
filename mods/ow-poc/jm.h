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
#define PAD_L2 0x0100
#define PAD_R2 0x0200
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
/* The game has a JSON reader of its own with these names: the mod's are its own symbols (the Android translated
 * build checks every name a mod defines against the game's signatures). */
#define Json_Parse Jm_Json_Parse
#define Json_Free Jm_Json_Free
#define Json_Get Jm_Json_Get
#define Json_Str Jm_Json_Str
#define Json_Num Jm_Json_Num
#define Json_Count Jm_Json_Count
#define Json_At Jm_Json_At
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
    TX_GRASS, TX_PLANK,
           /* the Kenney meshes' surfaces and the richer ground (JM_QUALITY) */
           TX_PLASTER, TX_ROOF, TX_WOOD, TX_SAND_Q0, TX_SAND_Q1, TX_GRASS_Q
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
/* Visual-quality pass: painted textures on the walls and roofs of the Kenney meshes, richer sand and grass,
 * and a ground that reaches the bottom of the view.  0 is the first look. */
#ifndef JM_QUALITY
#define JM_QUALITY 1
#endif

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
/* The same, and a flat rectangle, into one of the game's own tables at a chosen depth: for drawing
 * among pictures the game queued, like the duel's life-point panel. */
void Gfx_PortraitAt(int x, int y, int size, int ax, int ay, int ot_index, unsigned depth);
void Gfx_RectAt(int x, int y, int w, int h, int r, int g, int b, int ot_index, unsigned depth);
void Gfx_Rect(int x, int y, int w, int h, int r, int g, int b);
void Gfx_Backdrop(int top_rgb, int bottom_rgb);
int Gfx_LoadFaceFile(const char *path);               /* a 48x48 record of our own (assets/portrait_*.bin) */
int Gfx_LoadFaceRgb(const unsigned short *img);
#define HERO_FACE_HI 168     /* the hero's talk face: 168 texels for the 84-pixel slot (2x at the console's resolution) */
#define HERO_FACE_Y 256      /* ...in bank 14 below the atlas, x 0 */
#define NPC_FACE_X 256       /* a second 168x168 slot beside it (x 256..423, y 256..423: its own texture page, nothing else there) for the person
                              * the hero talks or duels with, so both high-resolution faces can be up at once */
int Gfx_LoadHeroFaceHi(const unsigned short *img);
int Gfx_LoadFaceHiAt(int x, const unsigned short *img);   /* a 168x168 face at (x, HERO_FACE_Y): 0 the hero, NPC_FACE_X the other person */
int Paint_HeroFaceHi(void);                          /* the chosen look's 168x168 face into the bank, 0 without a look */     /* a 48x48 face cut from a map sprite */
int Gfx_LoadFace(int duelist);                       /* disc portrait into the speaker slot */
extern unsigned gfx_frame;
extern float gfx_sort_override;
void Gfx_BankQuad(const float sx[4], const float sy[4], int bank, int ax, int ay, int uw, int vh, float depth);
extern unsigned char gfx_tint[3];
void Gfx_SpriteQuadEx(int x0, int y0, int w, int h, int bank, int page, int u0, int v0, int uw, int vh, float depth, const unsigned char *rgb, int abr);
void Gfx_SpriteQuad(int x0, int y0, int w, int h, int bank, int page, int u0, int v0, int uw, int vh, float depth);

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
    char anchor[40];             /* "anchor": the named place in the painted village where he stands (see Paint_Anchor) */
    Mesh *mesh_ptr;
} Npc;
#define MAX_NPC 64           /* the last slot is ECO_NPC (ow_poc.c), never a journey.json person */
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
const char *Lang_Code(void);                         /* "en", "pt" */
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

/* --------------------------------------------------------------- economy
 * Coins, experience and what the player has done with them.  The block is appended to Journey, so
 * Save_Read zero-fills it for a save written before it existed: every field must mean something at 0.
 * Layout and meaning are journey_content/economy/economy.json ("state"). */
typedef struct {
    int coins;                   /* 0..cap (99999) */
    int xp;                      /* total xp earned; the level is derived from it */
    int amb_cd;                  /* ambush countdown, 30ths of a second of walking; 0 = roll a new one */
    int amb_walk;                /* walking time since NEW GAME, 30ths of a second */
    int gang_loot;               /* coins the last ambush took (half comes back on the next win) */
    unsigned short amb_won, amb_lost;
    unsigned char amb_streak, amb_first_done;
    unsigned short quests_paid;  /* the journal quests whose coins have been paid (the block's spare 2 bytes) */
    unsigned char arena[8];      /* per arena: bit7 found, bits 3-6 clears, bits 0-2 the rung reached */
    unsigned int bought[2];      /* the one-time shop items taken (shops.json limited[].bit) */
    unsigned int eco_bits;       /* ECO_INTRO, ECO_TRUCE, ECO_CAP_SEEN */
} Economy;                       /* 48 bytes */
#define ECO_INTRO 1u             /* the "you have coins now" tutorial page has been shown */
#define ECO_TRUCE 2u             /* Old Jackal beaten: ambushes are halved for good */
#define ECO_CAP_SEEN 4u          /* the level-cap notice has been shown */

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
    float pt_x, pt_y;            /* where the player stands in the painted village (save version 3) */
    int pt_set;                  /* 1 when pt_x, pt_y were saved */
    unsigned char cg[8];         /* seven layered options plus render style (0 layered, 1 LPC); saved since version 4 */
    int cg_set;                  /* 1 when the creator made the hero; 0 on an older save, which keeps the painted hero */
    Economy eco;                 /* coins, xp and the rest of the economy (save version 5) */
    unsigned kflags;             /* story flags 32..63 (the Kingdom's), save version 6; 0 on an older save */
                                 /* flags 64..95 live in kflags2 (save version 7) */
    int stars;                   /* Duelist Kingdom star chips (0 on an older save: the Shore Camp gives one back) */
    int eliminations;            /* times the hero lost his last star and woke at the Shore Camp */
    int pt_area;                 /* the painted area the save was made in (0 village; 3.. the harbor, ship, beach) */
    int stars_beaten[2];         /* the named duelists already beaten for stars (bit by kingdom duel index) */
    unsigned char arena_x[4];    /* arenas 9-12 (the ship's Bilge Ring onward): same bits as eco.arena[]; at the end so older saves load */
    int stars_owed;              /* legacy (0.5.3): stars lost and owed back; a loaded save hands them back to the hero (jm_save.c) */
    unsigned char duel_held[16]; /* the stars each star duelist holds now, plus 1 (0: his content count; slot = journey.json win "slot") */
    int wager_seen;              /* the picker's game-over warning has been shown once */
    unsigned kflags2;            /* story flags 64..95, save version 7; 0 on an older save */
    /* Version 8: private run inventory, never imported from the classic save. */
    unsigned short deck[40];
    unsigned char chest[722];
    unsigned duel_stars;
    int cards_set;
    /* Version 9: the InsetoKaiba (Feupys parody) cards owned, by their order in jm_feupys.c; their deck slots are saved as
     * 0xF000 + that index, so a change in the mods' load order (runtime card ids) never turns them into other cards. */
    unsigned char feupys[16];
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
    const JsonNode *effects;     /* a result ({flags, stage, cards}) applied when the scene has been read */
    const char *pose;            /* "sit": the player sits on the bench while the scene plays */
} Talk;
int Story_TalkRule(const Npc *npc, Talk *out);
int Story_PoiAt(float x, float z, Talk *out);        /* a locked tile or spot the player pushes against */
int Story_Trigger(Talk *out, float *tp_x, float *tp_z, int *teleport); /* a line crossed; applies set_stage */
void Story_ApplyResult(const JsonNode *result);
int Story_ResultDone(const JsonNode *result);        /* its flags are all set already: a duel won before */
extern int jm_shop_req;                              /* set by a result with "open_shop": the screen opens after the scene */
extern char jm_shop_req_id[16];
extern int jm_warp;                                  /* set by a result with "teleport": where to put the player */
extern float jm_warp_x, jm_warp_z;
void Story_Regrant(void);      /* flags, stage, cards, items */
/* Pages of a scene. */
typedef struct { const char *who, *name, *text; int ask; int kind; } Page;   /* kind: 0 speech, 1 objective, 2 item / card gained, 3 quest or part complete, 4 scene caption (a narrator card) */
void Story_Expand(const char *text, char *out, int size);   /* {name} and {a|b} tokens of a page */
int Story_PageCount(const char *scene);
int Story_Page(const char *scene, int index, Page *out);
int Story_ItemList(char names[][32], int max);
int Story_Cards(int id);
const char *Story_CardGiver(int id);                 /* the story duelist who gives a card; NULL if none */
int Story_GotCards(int *out, int max);               /* the cards the story gave */
int Story_Items(int *out, int max);                  /* held items, as journey.json item indices */
const char *Story_ItemName(int i); const char *Story_ItemFile(int i); const char *Story_ItemFlag(int i);
const char *Story_ItemKey(int i);     /* the ui.json "bag" key: "key" if the item has one, else its flag */
int Story_ItemCount(int i);           /* -1, or the count shown with the name ("count": "stars") */
int Jm_ItemIcon(int x, int y, int px, const char *file);   /* an item's 24x24 icon, px screen pixels a texel */
extern int Cards_Seen(int id);
extern int Cards_NameUtf8(int id, char *out, size_t size);
const char *Jm_L1(const char *utf8);                 /* UTF-8 folded to the overlay font's Latin-1 */
int Jm_CardArt(int card, int big, int x, int y, int w, int h);
unsigned Jm_ArtLoads(void);
void Jm_CardLine(int card, char *b, size_t n);
void Jm_CardBadge(int x, int y, int card);
unsigned Jm_TypeFrame(int card);
/* jm_wager.c: the star wager picker and the game-over screen */
int Wager_HeldRaw(int slot, int base, const char *beaten_flag);
int Wager_Max(const JsonNode *win);                 /* the biggest bet now, 0 = no star duel */
void Wager_Open(const JsonNode *win);
int Wager_Input(unsigned short edge);               /* 0 stay, 1 duel, 2 back out */
int Wager_Bet(void);
void Wager_Settle(const JsonNode *win, int bet, int won);
void Wager_Overlay(void); unsigned Wager_Signature(void);
void GameOver_Overlay(int age); unsigned GameOver_Signature(int age);
void Bag_Open(void); int Bag_Input(unsigned short edge); void Bag_Overlay(void); unsigned Bag_Signature(void);                             /* grants a card to the chest */
int Story_Auto(Talk *out);                           /* an "auto" rule of journey.json that holds now (stage change, then a scene), applied once */
extern int jm_pwarp;                                 /* set by a result with "warp": [area, anchor]: the painted player goes there when the scene is over */
extern char jm_pwarp_area[32], jm_pwarp_anchor[24];
int Story_ItemIcon(const char *text, const char **file);   /* the icon file of an item named in a banner's text, if journey.json gives it one */
int paint_area_now(void);                            /* 0 village, 1 cistern, 2 secret arena (also story "area") */

/* -------------------------------------------------------------- dialogue */
void Say_Text(const char *name, const char *body, int ask);   /* builds the box text (speaker first, in yellow), opens the game's box */
void Say_Close(void);
int Say_Done(void);
void Say_Tick(void);

/* ------------------------------------------------------------------ save */
int Save_Exists(void);
void Journey_CardsCapture(void);
void Journey_CardsRestore(void);
#define FEUPYS_N 12
int Feupys_Id(int i);                    /* this run's card id of the i-th InsetoKaiba card, 0 if the mod's cards did not load */
int Feupys_Index(int id);                /* -1 for any other card */
void Feupys_Capture(void);               /* live chest/deck -> jm (encoded) */
void Feupys_Restore(void);
void Feupys_ClearChest(void);               /* jm -> live chest/deck */
int Feupys_RollDrop(const char *npc_id); /* a won duel: one InsetoKaiba card at FEUPYS_DROP_BP / 10000, else 0 */
int Save_Write(void);
int Save_Read(void);
void Save_Init(void);
void Save_Delete(void);
int Lang_PrefRead(void);                             /* the language chosen the first time, -1 before any */
void Lang_PrefWrite(int i);
void Paint_Info(float *x, float *y, float *sx, float *sy);
void Paint_Set(float x, float y);
int Paint_Target(float *tx, float *ty);              /* the guide arrow's target in this area */
int Dbg_Wager(void);
int Dbg_LoseDuels(void);                             /* debug "lose_duels": a skipped duel counts as lost */
int Paint_Anchor(const char *name, float *x, float *y);   /* a named place of a painted area in picture texels */
int Paint_AnchorArea(const char *name);              /* 0 village, 1 cistern, 2 arena, -1 unknown */
int Paint_Area(void);
int Paint_SaveArea(void);
void Paint_SetArea(int area);       /* before the picture is entered: where a loaded save resumes */           /* the area a save resumes in: the kingdom pictures, or 0 (the village) for the rest */
const char *Paint_AreaId(void);     /* "village", "cistern", "harbor", "ship_deck", "kingdom_beach"; in an arena: the place its door is in */
void Paint_Warp(const char *area, const char *anchor);   /* go there; changing area loads the other picture, with a fade in */
void Paint_GoAnchor(const char *anchor);             /* debug: the same without the fade, whatever the area */
int Paint_ArenaPadAt(void);                          /* standing in the empty challenger mark */
void Paint_ArenaReady(void);                         /* snap to the challenger mark, facing the keeper */
int Paint_Loaded(void);
/* A villager's idle picture, big, in the view's own 320x240 space (the shop's keeper). 0 if unknown. */
int Paint_Figure(const char *npc_id, int x, int y, int w, int h);
/* The keeper's painted picture for the shop screen, when assets/shop_<keeper>.raw is there. */
/* A card's picture from the disc, into a texture page, for the reveal after a duel. */
int Paint_CardArt(int card);
void Paint_CardArtWhere(int *ax, int *ay, int *w, int *h);
int Paint_ShopArt(const char *keeper);
int Paint_ShopFigure(int x, int y, int box_w, int box_h);
const uint16_t *Paint_LpcFrame(int dir, int frame, int *w, int *h, int *fx, int *fy, int *nf); /* the LPC frame's texels in its bank (stride 1024) */
int Paint_LpcPreview(int x, int y, int scale, int dir, int frame, float depth); /* creator preview, x/y is the feet */
/* The opaque horizontal span of the shop art at an overlay-canvas row. */
int Paint_ShopMaskSpan(int output_y, int output_w, int output_h, int *x0, int *x1);
const char *Paint_AnchorName(int i);                 /* the i-th named place, NULL past the last */
void Paint_ForceTime(int t);                         /* debug: 1 night, 0 day, -1 the story decides */
int Paint_ForcedTime(void);

/* --------------------------------------------------- economy (jm_eco.c): coins, xp and the shops
 * The data is assets/economy.json (tier tables, the level curve, drop odds, the local card pools and
 * the shops), built from journey_content/economy by tools/eco_to_journey.py; the strings it shows are
 * assets/lang/<code>/economy.json.  Without those files every call here is a no-op, so a build that
 * has not run the converter plays as it did before. */
int Eco_Load(void);                                  /* reads the data once; 0 when it is not there */
int Eco_Ready(void);
void Eco_LoadLang(const char *code);                 /* the strings of a language (Lang_Set calls it) */
const char *EcoTr(const char *path);                 /* "ui.coins" of economy.json, else the path */
int Eco_Level(void);                                 /* 1..cap, from jm.eco.xp and the level table */
int Eco_Rank(void);                                  /* the rank number of the current level */
const char *Eco_RankName(void);
int Eco_XpBar(int *into, int *span);                 /* xp into the level and the span to the next; 0 at the cap */
void Eco_GiveCoins(int n);                           /* capped, with a notice */
int Eco_TakeCoins(int n);                            /* 0 when the purse is short (nothing is taken) */
int Eco_GiveXp(int n);                               /* returns the levels gained (0 or more) */
int Eco_DuelTier(const char *npc_id);                /* the difficulty tier of a story duel, 0 unknown */
int Eco_WinCoins(int tier, const char *context);     /* coins a win of that tier pays in that context */
int Eco_WinXp(int tier);
int Eco_LossXp(int tier);
int Eco_QuestCoins(const char *quest_id);
void Eco_DuelReward(const char *npc_id, int won, int rematch);   /* the whole payout of one duel */
void Eco_Tick(void);                                 /* shows the queued notices, one after another */
void Eco_QuestTick(void);                            /* pays a quest the player has just finished */
const char *EcoDlg(const char *key);                 /* a line of the economy's dialogue block */

/* The card a won duel drops comes from the pool of the place it was fought in (0 for a place with
 * no pool, like the cistern).  `context` is a key of the drop odds: "duel", "ambush_win", ... */
int Eco_RollDrop(const char *context);
void Eco_SetDropContext(const char *context);        /* which odds the next won duel drops by */
const char *Eco_DropContext(void);
int Eco_DropCount(const char *context);

/* A shop.  Eco_ShopAt picks the one a person keeps, if it is open at this point of the story; the
 * screen then reads its stock as a flat list of these. */
enum { ECO_ITEM_CARD, ECO_ITEM_ONCE, ECO_ITEM_PACK, ECO_ITEM_SELL };
typedef struct {
    int card;                    /* the card id, 0 for a pack */
    int price;
    int owned;                   /* copies in the chest; for a pack, the cards in it; to sell, the spares */
    int level_min;
    int bit;                     /* a one-time item's bit, a pack's index, else -1 */
    int kind;
    int locked;                  /* the level is too low */
    char name[34];
} EcoItem;
int Eco_ShopAt(const char *npc_id);
int Eco_ShopSet(const char *shop_id);
const char *Eco_ShopName(void);
const char *Eco_ShopGreet(void);
const char *Eco_ShopKeeper(void);
int Eco_ShopItems(EcoItem *out, int max);
int Eco_PackItems(EcoItem *out, int max);
int Eco_SellItems(EcoItem *out, int max);
int Eco_Buy(const EcoItem *item);
int Eco_Sell(const EcoItem *item);
int Eco_OpenPack(int index, int *cards, int max);
int Eco_CardClass(int card);                         /* 0 C, 1 B, 2 A, 3 S; -1 for a card with no class */
int Eco_SellPrice(int card);                         /* 0 when it may not be sold */
int Eco_Protected(int card);
const char *Eco_Exclusive(int card);                 /* the arena id whose ring alone drops it, NULL for the rest */

JsonNode *Eco_Block(const char *key);                /* a block of the data, for jm_gang.c */
void Eco_Note(const char *text, int alert);          /* a line on the message queue */

/* ------------------------------------------- the Dune Jackals (jm_gang.c)
 * They are in the place the player is, in plain sight, and a countdown that only runs while he
 * walks decides when one of them comes over.  Everything they do is in jm.eco. */
typedef struct { float x, y; int member; unsigned tint; } GangFigure;
enum { GANG_GRACE_WIN, GANG_GRACE_LOSS, GANG_GRACE_AREA, GANG_GRACE_SCENE };
int Gang_Load(void);
int Gang_Present(void);                              /* they are about the place (from stage 3) */
int Gang_Awake(void);                                /* and the ambush clock may run (past the warm-up) */
int Gang_Figures(GangFigure *out, int max);          /* where they loiter in this place, now */
void Gang_Walked(int frames);                        /* frames the player actually moved */
void Gang_Near(float px, float py);                  /* every painted frame: standing in their spot */
int Gang_Dwell(void);
int Gang_AlertAt(int slot);                          /* 0-100: how much this one has noticed */
float Gang_Reach(void);                              /* how far their ground reaches, in texels */
void Gang_Grace(int which);                          /* hold them off for a while */
void Gang_Area(void);                                /* the player changed area */
int Gang_Pending(void);                              /* one of them is coming over */
int Gang_Member(void);
const char *Gang_Line(const char *kind);             /* "taunt", "win", "lose" */
const char *Gang_Name(void);
int Gang_Duelist(void);                              /* the id the host gave this member this run */
int Gang_Tier(void);
void Gang_Result(int won);
void Gang_Cancel(void);
void Gang_Debug(char *out, size_t size);             /* the state of every condition, for Dev mode */
int Gang_Force(void);                                /* debug: let the next step bring one of them */

/* -------------------------------------- the clandestine arenas (jm_arena.c)
 * A ladder of four duels behind a door, for a fee.  Where a run stands is in jm.eco.arena[]. */
int Arena_Load(void);
int Arena_DoorAt(float x, float y);                  /* the player is at this place's arena door */
float Arena_DoorDistance(float x, float y);          /* texels to it, -1 when this place has none */
void Arena_Debug(char *out, size_t size, float x, float y);   /* why it does or does not answer */
int Arena_Open(void);
const char *Arena_PlaceName(void);
void Journey_GiveStarter(void);                      /* the weak forty of a new journey (journey.json "starter_deck") */                   /* inside a ring: its name ("Bilge Ring"), NULL without data */
const char *Arena_Name(void);
int Arena_Input(unsigned short edge, int *start_duel);   /* 1 when the player is done with it */
void Arena_Overlay(void);
unsigned Arena_Signature(void);
int Arena_NextFighter(char *name, size_t size, int *tier);   /* the duelist of the rung to fight */
const char *Arena_FighterLine(void);
int Arena_Running(void);
void Arena_Result(int won);

/* --------------------------------------------- the shop screen (jm_shop.c) */
void Shop_Open(void);                                /* after Eco_ShopAt or Eco_ShopSet said yes */
const char *Shop_Keeper(void);                       /* whose stall it is, for the figure behind it */
int Shop_Input(unsigned short edge);                 /* 1 when the player is done with it */
void Shop_Overlay(void);
unsigned Shop_Signature(void);

/* ----------------------------------------------------------- chargen (jm_chargen.c): the hero assembled from layers */
int Paint_BakeHeroFace(int force);                     /* the hero's talk preset from jm.cg/jm.gender (data dir hero.face) */
int Cg_Ready(void);                                  /* assets/lpc_parts/manifest.json is there and usable */
int Cg_CatCount(void);
const char *Cg_CatLabel(int c);
const char *Cg_CatId(int c);
int Cg_OptCount(int c);
const char *Cg_OptLabel(int c, int o);
int Cg_Get(int c);
void Cg_Set(int c, int v);
int Cg_Style(void);                                   /* always 1: the hero is LPC */
void Cg_SetStyle(int style);
void Cg_Defaults(void);                              /* base "Hero", cg_set = 1 (when the parts exist) */
unsigned Cg_Signature(void);                         /* changes with the choice (and the body type) */
int Cg_OptRgb(int c, int o);
int Cg_OptRgb2(int c, int o);
int Cg_Frames(void);
int Cg_W(void);
int Cg_H(void);
int Cg_MapHi(void);   /* the map hero comes from the 50x64 source cells (drawn at half size) */
int Cg_Avoided(void);
int Cg_BaseCount(void);
const char *Cg_BaseName(int b);
int Cg_BaseLook(int b, unsigned char cg[8], int *gender);
void Cg_ApplyBase(int b);
int Cg_MatchBase(void);
int Cg_ComposeCell(const unsigned char cg[8], int gender, int cell, uint16_t *out);   /* cell = direction * 10 + frame, out 25x38 RGB555 */
int Cg_ComposeHi(const unsigned char cg[8], int gender, int dir, uint16_t *out);       /* idle pose at 64x64 */
int Cg_ComposeCellRgb(int cell, unsigned char *kind, unsigned char *rgb);

/* ----------------------------------------------------------------- debug (jm_debug.c, off without debug.json) */
void Dbg_Init(void);
int Dbg_On(void);
int Dbg_Skip(void);
int Dbg_WinDuels(void);
void Dbg_Apply(void);
int Dbg_Keys(unsigned short pad, unsigned short edge, int *swallow);
void Dev_Load(void);                                 /* reads devmode.cfg (after Dbg_Init) */
int Dev_BarOn(void);                                 /* 1: the top status bar is drawn ("Dev mode" in the START menu) */
void Dev_Set(int on);                                /* sets it and writes devmode.cfg */

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
void Ui_MessageTone(const char *text, unsigned rgb);   /* the same line in another colour */
unsigned Ui_MessageColour(void);
/* The panel, font and metrics of the menus, for a screen written in another file (the shop). */
void Ui_Metrics(int *w, int *h, int *scale, int *top, int *vis);
void Ui_Panel(int x, int y, int w, int h);
int Ui_DX(int v); int Ui_DY(int v); int Ui_DS(int v); int Ui_SmallS(void);   /* the creator's drawing kit (1280x720 design units) */
void Ui_Fill(int x, int y, int w, int h, unsigned rgb, unsigned a);
void Ui_Frame(int x, int y, int w, int h, int t, unsigned rgb, unsigned a);
void Ui_VGrad(int x, int y, int w, int h, unsigned top, unsigned bot, unsigned a);
void Ui_Disc(int cx, int cy, int rx, int ry, unsigned rgb, unsigned a);
void Ui_Ring(int cx, int cy, int rx, int ry, int t, unsigned rgb, unsigned a);
void Ui_OPanel(int x, int y, int w, int h, int active);
void Ui_Pill(int x, int y, int w, int h, int gold, int lit);
void Ui_TextC(int cx, int my, const char *t, unsigned rgb, int sc);
void Ui_TextSh(int x, int my, const char *t, unsigned rgb, int sc);
void Ui_TextFit(int x, int my, int maxw, const char *t, unsigned rgb, int sc);
void Ui_KeyBar(const char *const *k, int n, int cx, int my, int maxw);
int Ui_LineH(void);
void Ui_Text(int x, int row_y, const char *text, unsigned rgb);
void Ui_Fmt1(char *out, size_t size, const char *tmpl, int value);
void Ui_RefreshName(void);
extern int jm_save_requested, jm_save_ok, jm_name_entry_requested;
const char *Ui_MessageText(void);

#endif
