#ifndef VISUAL_ENGINE_H
#define VISUAL_ENGINE_H

typedef unsigned char  u8;
typedef signed char    s8;
typedef unsigned short u16;
typedef signed short   s16;
typedef unsigned int   u32;
typedef signed int     s32;
typedef int            BOOL;
typedef s32            fx32;
typedef s16            fx16;
typedef u16            GXRgb;

#define TRUE  1
#define FALSE 0
#ifndef NULL
#define NULL  ((void *)0)
#endif

#define VISUAL_MAGIC 0x354E4547u /* "GEN5" */

/* Weather Shader Modes */
#define SHADER_CLEAR_CLOUDS   0 /* Daytime fair weather + drifting 7-bit cloud shadows */
#define SHADER_DAWN_MIST      1 /* Morning volumetric rose-pearl mist + dew specular */
#define SHADER_GOLDEN_GLOW    2 /* Sunset golden hour horizon bloom + window specular */
#define SHADER_NIGHT_AURORA   3 /* Starlit nocturnal horizon halo + glowing amber windows */
#define SHADER_WET_STORM      4 /* Rain / wet-surface high-gloss specular + storm-blue fog */
#define SHADER_NATIVE_WEATHER 5 /* Snow / Blizzard / Deep Fog controlled by native FogManager */

/* Hardware Registers */
#define REG_DISPCNT       (*(volatile u32 *)0x04000000u)
#define REG_BG0CNT        (*(volatile u16 *)0x04000008u)
#define REG_BG2CNT        (*(volatile u16 *)0x0400000Cu)
#define REG_BG2HOFS       (*(volatile u16 *)0x04000018u)
#define REG_BG2VOFS       (*(volatile u16 *)0x0400001Au)
#define REG_BLDCNT        (*(volatile u16 *)0x04000050u)
#define REG_BLDALPHA      (*(volatile u16 *)0x04000052u)
#define REG_G3X_DISP3DCNT (*(volatile u16 *)0x04000060u)
#define REG_KEYINPUT      (*(volatile u16 *)0x04000130u)
#define REG_VRAMCNT_C     (*(volatile u8  *)0x04000242u)
#define REG_G3X_FOG_COLOR (*(volatile u32 *)0x04000358u)
#define REG_G3X_FOG_OFFSET (*(volatile u16 *)0x0400035Cu)
#define REG_G3_SHININESS  (*(volatile u32 *)0x040004C0u)

#define PLTT_BG_PAL6      ((volatile u32 *)0x050000C0u)
#define PLTT_BG_PAL6_COL1 (*(volatile u16 *)0x050000C2u)
#define VRAM_BG2_CHR      ((volatile u32 *)0x06008000u)
#define VRAM_BG2_SCR      ((volatile u16 *)0x0600F000u)

/* Profile-Specific Game Function & Global Addresses */
#if defined(PROFILE_US)
#define ADDR_GET_SEC_MIDNIGHT    0x020138C9u
#define ADDR_VRAM_TRANSFER_REQ   0x0201DC69u
#define ADDR_CAM_CALC_POS        0x02020021u
#define ADDR_MTX_IDENTITY33      0x020BB4C8u /* ARM */
#define ADDR_G3X_SET_FOG         0x020BFC74u /* ARM */
#define ADDR_G3X_SET_FOG_TABLE   0x020BFD44u /* ARM */
#define ADDR_DC_FLUSH_RANGE      0x020C2C58u /* ARM */
#define ADDR_GLB_MAT_COL0        0x021C5B20u
#define ADDR_GLB_MAT_COL1        0x021C5B24u
#define ADDR_AREALIGHT_UPDATE    0x021D5299u
#define ADDR_AREALIGHT_APPLY_TPL 0x021D52F5u
#define ADDR_CHK_COLLISION       0x02060B7Du
#define ADDR_ALLOC_STEP_STATE    0x02062AA5u
#define ADDR_STEP_COORDS         0x020641B5u
#define ADDR_SET_FACE_MOVE_DIR   0x020629A1u
#define ADDR_SET_ANIM_ID         0x02062A0Du
#define ADDR_SET_FLAGS_BITS      0x020628BDu
#define ADDR_ADV_MOVE_STEP       0x02062BC9u
#define ADDR_GET_STEP_STATE      0x02062AC9u
#define ADDR_ADD_DIR_TO_POS      0x020642A5u
#define ADDR_UPDATE_HEIGHT       0x020642F9u
#define ADDR_SYNC_PREV_COORDS    0x02064209u
#define ADDR_STEP_FINISH_CB      0x02062B69u
#elif defined(PROFILE_045)
#define ADDR_GET_SEC_MIDNIGHT    0x02013DD5u
#define ADDR_VRAM_TRANSFER_REQ   0x0201E4B1u
#define ADDR_CAM_CALC_POS        0x020208D1u
#define ADDR_MTX_IDENTITY33      0x020C20F4u /* ARM */
#define ADDR_G3X_SET_FOG         0x020C68A0u /* ARM */
#define ADDR_G3X_SET_FOG_TABLE   0x020C6970u /* ARM */
#define ADDR_DC_FLUSH_RANGE      0x020C9884u /* ARM */
#define ADDR_GLB_MAT_COL0        0x021D5020u
#define ADDR_GLB_MAT_COL1        0x021D5024u
#define ADDR_AREALIGHT_UPDATE    0x021E664Du
#define ADDR_AREALIGHT_APPLY_TPL 0x021E66A9u
#define ADDR_CHK_COLLISION       0x02065A5Du
#define ADDR_ALLOC_STEP_STATE    0x02067B2Du
#define ADDR_STEP_COORDS         0x020692F1u
#define ADDR_SET_FACE_MOVE_DIR   0x020679D9u
#define ADDR_SET_ANIM_ID         0x02067A6Du
#define ADDR_SET_FLAGS_BITS      0x020678F5u
#define ADDR_ADV_MOVE_STEP       0x02067C79u
#define ADDR_GET_STEP_STATE      0x02067B65u
#define ADDR_ADD_DIR_TO_POS      0x020693E1u
#define ADDR_UPDATE_HEIGHT       0x02069435u
#define ADDR_SYNC_PREV_COORDS    0x02069345u
#define ADDR_STEP_FINISH_CB      0x02067C19u
#elif defined(PROFILE_047)
#define ADDR_GET_SEC_MIDNIGHT    0x02013DF5u
#define ADDR_VRAM_TRANSFER_REQ   0x0201E4D1u
#define ADDR_CAM_CALC_POS        0x020208FDu
#define ADDR_MTX_IDENTITY33      0x020C247Cu /* ARM */
#define ADDR_G3X_SET_FOG         0x020C6C28u /* ARM */
#define ADDR_G3X_SET_FOG_TABLE   0x020C6CF8u /* ARM */
#define ADDR_DC_FLUSH_RANGE      0x020C9C0Cu /* ARM */
#define ADDR_GLB_MAT_COL0        0x021D53A0u
#define ADDR_GLB_MAT_COL1        0x021D53A4u
#define ADDR_AREALIGHT_UPDATE    0x021E69CDu
#define ADDR_AREALIGHT_APPLY_TPL 0x021E6A29u
#define ADDR_CHK_COLLISION       0x02065DE5u
#define ADDR_ALLOC_STEP_STATE    0x02067EB5u
#define ADDR_STEP_COORDS         0x02069679u
#define ADDR_SET_FACE_MOVE_DIR   0x02067D61u
#define ADDR_SET_ANIM_ID         0x02067DF5u
#define ADDR_SET_FLAGS_BITS      0x02067C7Du
#define ADDR_ADV_MOVE_STEP       0x02068001u
#define ADDR_GET_STEP_STATE      0x02067EEDu
#define ADDR_ADD_DIR_TO_POS      0x02069769u
#define ADDR_UPDATE_HEIGHT       0x020697BDu
#define ADDR_SYNC_PREV_COORDS    0x020696CDu
#define ADDR_STEP_FINISH_CB      0x02067FA1u
#else /* ProjectPM 0.4.6 (FR & US) */
#define ADDR_GET_SEC_MIDNIGHT    0x02013DD5u
#define ADDR_VRAM_TRANSFER_REQ   0x0201E4B1u
#define ADDR_CAM_CALC_POS        0x020208D1u
#define ADDR_MTX_IDENTITY33      0x020C2348u /* ARM */
#define ADDR_G3X_SET_FOG         0x020C6AF4u /* ARM */
#define ADDR_G3X_SET_FOG_TABLE   0x020C6BC4u /* ARM */
#define ADDR_DC_FLUSH_RANGE      0x020C9AD8u /* ARM */
#define ADDR_GLB_MAT_COL0        0x021D5240u
#define ADDR_GLB_MAT_COL1        0x021D5244u
#define ADDR_AREALIGHT_UPDATE    0x021E686Du
#define ADDR_AREALIGHT_APPLY_TPL 0x021E68C9u
#define ADDR_CHK_COLLISION       0x02065CB1u
#define ADDR_ALLOC_STEP_STATE    0x02067D81u
#define ADDR_STEP_COORDS         0x02069545u
#define ADDR_SET_FACE_MOVE_DIR   0x02067C2Du
#define ADDR_SET_ANIM_ID         0x02067CC1u
#define ADDR_SET_FLAGS_BITS      0x02067B49u
#define ADDR_ADV_MOVE_STEP       0x02067ECDu
#define ADDR_GET_STEP_STATE      0x02067DB9u
#define ADDR_ADD_DIR_TO_POS      0x02069635u
#define ADDR_UPDATE_HEIGHT       0x02069689u
#define ADDR_SYNC_PREV_COORDS    0x02069599u
#define ADDR_STEP_FINISH_CB      0x02067E6Du
#endif

typedef struct {
    fx32 x;
    fx32 y;
    fx32 z;
} VecFx32;

typedef struct {
    fx16 x;
    fx16 y;
    fx16 z;
} VecFx16;

typedef struct {
    fx32 m[3][3];
} MtxFx33;

typedef struct {
    u16 x;
    u16 y;
    u16 z;
    u16 padding;
} CameraAngle;

typedef struct {
    fx32 perspective[5];          /* +0x00..+0x13 */
    VecFx32 position;             /* +0x14..+0x1F */
    VecFx32 target;               /* +0x20..+0x2B */
    VecFx32 up;                   /* +0x2C..+0x37 */
    fx32 distance;                /* +0x38 */
    CameraAngle angle;            /* +0x3C..+0x43 */
    u8 projection;                /* +0x44 */
    u8 pad45;                     /* +0x45 */
    u16 fovY;                     /* +0x46 */
    VecFx32 prevTrackedTarget;    /* +0x48..+0x53 */
    const VecFx32 *trackedTarget; /* +0x54 */
} Camera;

typedef struct {
    u32 endTime;                 /* +0x00 */
    u8  validLightsMask;         /* +0x04 */
    u8  pad05;                   /* +0x05 */
    GXRgb lightColors[4];        /* +0x06..+0x0D */
    VecFx16 lightVectors[4];     /* +0x0E..+0x25 */
    GXRgb diffuseReflectColor;   /* +0x26 */
    GXRgb ambientReflectColor;   /* +0x28 */
    GXRgb specularReflectColor;  /* +0x2A */
    GXRgb emissionColor;         /* +0x2C */
    u16 pad2E;                   /* +0x2E */
} AreaLightTemplate;             /* 48 (0x30) bytes */

typedef struct {
    VecFx16 lightVectors[4];                   /* +0x00..+0x17 */
    GXRgb lightColors[4];                      /* +0x18..+0x1F */
    GXRgb diffuseReflectColor;                 /* +0x20 */
    GXRgb ambientReflectColor;                 /* +0x22 */
    GXRgb specularReflectColor;                /* +0x24 */
    GXRgb emissionColor;                       /* +0x26 */
    BOOL setDiffuseColorAsVertexColor;         /* +0x28 */
    BOOL enableSpecularReflectShininessTable;  /* +0x2C */
    s32 lightMask;                             /* +0x30 */
    s32 polyMode;                              /* +0x34 */
    s32 cullMode;                              /* +0x38 */
    s32 polygonID;                             /* +0x3C */
    s32 alpha;                                 /* +0x40 */
    u32 miscFlags;                             /* +0x44 */
} ModelAttributes;

typedef struct {
    u32 templateCount;             /* +0x00 */
    AreaLightTemplate *templates;  /* +0x04 */
    s32 activeTemplateIndex;       /* +0x08 */
    ModelAttributes *areaModelAttrs; /* +0x0C */
    BOOL applyToAreaModelAttrs;    /* +0x10 */
} AreaLightManager;

typedef struct {
    void *unk_00;
    s32 activeWeather;             /* +0x04: OVERWORLD_WEATHER_* */
} OverworldWeatherManager;

typedef struct {
    BOOL unk_00;
    void *unk_04;
    void *mapPopup;
    OverworldWeatherManager *weatherMan; /* +0x0C */
} FieldSystem_sub2;

typedef struct {
    u32 flags[7];                  /* +0x00..+0x1B */
    s32 playerAvatarState;         /* +0x1C: 1 = cycling */
    s32 gender;                    /* +0x20 */
    s32 speed;                     /* +0x24 */
    s32 faceLeftOrRight;           /* +0x28 */
    s32 faceUpOrDown;              /* +0x2C */
    u8 *mapObject;                 /* +0x30: +0xAC = currTileBehavior */
} PlayerAvatar;

typedef struct {
    u16 animId;                    /* +0x00 */
    s16 duration;                  /* +0x02 */
    s32 dir;                       /* +0x04 */
    fx32 speed;                    /* +0x08 */
} StepMovementState;

typedef struct {
    void *processManager;          /* +0x00 */
    FieldSystem_sub2 *unk_04;      /* +0x04 */
    void *bgConfig;                /* +0x08 */
    void *saveData;                /* +0x0C */
    void *task;                    /* +0x10 */
    void *mapHeaderData;           /* +0x14 */
    s32 bottomScreen;              /* +0x18 */
    void *location;                /* +0x1C */
    s32 unk_20;                    /* +0x20: 1 = Distortion World */
    Camera *camera;                /* +0x24 */
    void *landDataMan;             /* +0x28 */
    void *mapMatrix;               /* +0x2C */
    void *areaDataManager;         /* +0x30 */
    void *mapObjectsToPreload;     /* +0x34 */
    void *mapObjMan;               /* +0x38 */
    PlayerAvatar *playerAvatar;    /* +0x3C */
} FieldSystem;

/* Fixed-layout state struct at ORIGIN_VISUAL (0x023DE000), aligned for Thumb-1 immediate offsets */
typedef struct {
    u32 magic;                  /* +0x00: 0x354E4547 ("GEN5") */
    u32 frameCounter;           /* +0x04: 60 FPS frame counter */
    s16 currPitchOff;           /* +0x08: current camera pitch offset */
    s16 currDistOff;            /* +0x0A: current camera distance offset (>> 8) */
    u8  isOutdoor;              /* +0x0C: 1 if outdoor map, 0 if indoor */
    u8  inTallGrass;            /* +0x0D: 1 if in tall grass */
    u16 sunColor;               /* +0x0E: active Light 0 BGR555 color */
    u8  weatherShaderMode;      /* +0x10: active SHADER_* mode (0..5) */
    u8  yawHoldTimer;           /* +0x11: linger counter for horizontal yaw */
    u8  lastActiveIdx;          /* +0x12: dirty-flag cache: activeTemplateIndex */
    u8  lastSolarTq8;           /* +0x13: dirty-flag cache: solar t_q8 */
    u8  lastInGrass;            /* +0x14: dirty-flag cache: inTallGrass */
    u8  lastWeatherMode;        /* +0x15: dirty-flag cache: weatherShaderMode */
    u8  presetForcedWeather;    /* +0x16: 0=dynamic, 0x80|mode=forced preset */
    u8  lightDirty;             /* +0x17: 1 when lighting needs recomputation */
    s16 currYawOff;             /* +0x18: current orbital camera yaw offset */
    u16 activeCamPitch;         /* +0x1A: active cam->angle.x */
    u32 baseSpecEmi;            /* +0x1C: NNS_G3dGlb.prmMatColor1 */
    s32 pitchPosQ8;             /* +0x20 */
    s32 pitchVelQ8;             /* +0x24 */
    s32 distPosQ8;              /* +0x28 */
    s32 distVelQ8;              /* +0x2C */
    s32 yawPosQ8;               /* +0x30 */
    s32 yawVelQ8;               /* +0x34 */
    s32 prevCamDx;              /* +0x38 */
    s32 prevCamDy;              /* +0x3C */
    s32 prevCamDz;              /* +0x40 */
    s8  sineWaveTable[16];      /* +0x44..+0x53: 16-byte sine LUT */
    u8  horizonFogTable[32];    /* +0x54..+0x73: 32-byte 7-bit fog table */
    u32 shaderPack[5];          /* +0x74..+0x87: 20-byte packed shader LUT */
    s16 moveVecX;               /* +0x88: smoothed X movement heading (-256..+256) */
    s16 moveVecZ;               /* +0x8A: smoothed Z movement heading (-256..+256) */
    u8  primaryFaceDir;         /* +0x8C: dominant visual facing direction (0..3) */
    s8  diagStepDx;             /* +0x8D: active diagonal step X delta (-1, 0, +1) */
    s8  diagStepDz;             /* +0x8E: active diagonal step Z delta (-1, 0, +1) */
    u8  isDiagStep;             /* +0x8F: 1 if next player step is simultaneous 45-deg diagonal */
    s16 lastCloudTileX;         /* +0x90: last world tile X streamed to VRAM_BG2_SCR */
    s16 lastCloudTileY;         /* +0x92: last world tile Y streamed to VRAM_BG2_SCR */
    u8  manualMoveActive;       /* +0x94: 1 when step initiated by manual D-Pad input */
    u8  activeDiagFlags;        /* +0x95: bit7=diag active, bit1=(dx>0), bit0=(dz>0) */
    u8  stepInitDur;            /* +0x96: initial duration of current player step */
    u8  sideBlockedFlag;        /* +0x97: 1 if perpendicular sub-tile side should funnel to 0 */
    u8 *playerMapObj;           /* +0x98: cached pointer to playerAvatar->mapObject */
    PlayerAvatar *playerAvatar; /* +0x9C: cached pointer to fieldSystem->playerAvatar */
} VisualEngineState;

/* Game Function Pointers */
#define GetSecondsSinceMidnight ((s32 (*)(void))ADDR_GET_SEC_MIDNIGHT)
#define VramTransfer_Request    ((BOOL (*)(u32, u32, void *, u32))ADDR_VRAM_TRANSFER_REQ)
#define Camera_CalcLookAtPos    ((void (*)(Camera *))ADDR_CAM_CALC_POS)
#define MTX_Identity33          ((void (*)(MtxFx33 *))ADDR_MTX_IDENTITY33)
#define G3X_SetFog              ((void (*)(BOOL, s32, s32, s32))ADDR_G3X_SET_FOG)
#define G3X_SetFogTable         ((void (*)(const void *))ADDR_G3X_SET_FOG_TABLE)
#define DC_FlushRange           ((void (*)(const void *, u32))ADDR_DC_FLUSH_RANGE)
#define AreaLightManager_UpdateActiveTemplate ((void (*)(AreaLightManager *))ADDR_AREALIGHT_UPDATE)
#define AreaLightTemplate_ApplyToModelAttributes ((void (*)(const AreaLightTemplate *, ModelAttributes *))ADDR_AREALIGHT_APPLY_TPL)

#define PlayerAvatar_CheckCollision    ((u32 (*)(PlayerAvatar *, u8 *, s32))ADDR_CHK_COLLISION)
#define MapObject_AllocStepState       ((StepMovementState *(*)(u8 *, s32))ADDR_ALLOC_STEP_STATE)
#define MapObject_StepCoords           ((void (*)(u8 *, s32))ADDR_STEP_COORDS)
#define MapObject_SetFaceAndMoveDir    ((void (*)(u8 *, s32))ADDR_SET_FACE_MOVE_DIR)
#define MapObject_SetAnimId            ((void (*)(u8 *, u16))ADDR_SET_ANIM_ID)
#define MapObject_SetFlagsBits         ((void (*)(u8 *, u32))ADDR_SET_FLAGS_BITS)
#define MapObject_AdvanceMovementStep  ((void (*)(u8 *))ADDR_ADV_MOVE_STEP)
#define MapObject_GetStepState         ((StepMovementState *(*)(u8 *))ADDR_GET_STEP_STATE)
#define MapObject_AddDirToPos          ((void (*)(u8 *, s32, fx32))ADDR_ADD_DIR_TO_POS)
#define MapObject_UpdateHeight         ((void (*)(u8 *))ADDR_UPDATE_HEIGHT)
#define MapObject_SyncPrevCoords       ((void (*)(u8 *))ADDR_SYNC_PREV_COORDS)
#define MapObject_StepFinishCb         ((void (*)(u8 *))ADDR_STEP_FINISH_CB)

#endif /* VISUAL_ENGINE_H */
