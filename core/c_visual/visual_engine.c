#include "visual_engine.h"

#define DELTA_RGB(r, g, b) ((u16)((s32)(r) + ((s32)(g) * 32) + ((s32)(b) * 1024)))
#define DELTA_STEP_ALL     0x0421 /* (+1, +1, +1) in 5-5-5 */
#define DELTA_GRASS_TINT   DELTA_RGB(-1, 1, -1)
#define PACK_SHADER(m, s)  ((u32)(m) | ((u32)(s) << 16))
#define PACK_LOBE(cx, cy, r) ((u16)((u32)(cx) | ((u32)(cy) << 6) | ((u32)(r) << 11)))

/* Fixed-layout global state at ORIGIN_VISUAL (0x023DE000) */
__attribute__((section(".data.state"), used))
VisualEngineState gVisualState = {
    .magic          = VISUAL_MAGIC,
    .frameCounter   = 0,
    .currPitchOff   = 0,
    .currDistOff    = 0,
    .isOutdoor      = 0,
    .inTallGrass    = 0,
    .sunColor       = 0x5AD6,
    .weatherShaderMode = SHADER_CLEAR_CLOUDS,
    .yawHoldTimer   = 0,
    .lastActiveIdx  = 0xFF,
    .lastSolarTq8   = 0xFF,
    .lastInGrass    = 0,
    .lastWeatherMode = 0xFF,
    .presetForcedWeather = 0,
    .lightDirty     = 1,
    .currYawOff     = 0,
    .activeCamPitch = 0xDD40,
    .baseSpecEmi    = 0,
    .sineWaveTable = {
        0, 12, 23, 30, 32, 30, 23, 12,
        0, -12, -23, -30, -32, -30, -23, -12
    },
    .horizonFogTable = {
         0,  0,  0,  0,  0,  0,  0,  0,
         0,  0,  0,  0,  0,  0,  0,  0,
         1,  2,  3,  5,  6,  7,  8, 10,
        11, 12, 13, 15, 16, 17, 18, 20
    },
    .shaderPack = {
        PACK_SHADER(DELTA_RGB( 0,  0,  0), DELTA_RGB(2, 2,  1)), /* 0: SHADER_CLEAR_CLOUDS */
        PACK_SHADER(DELTA_RGB( 1,  0,  2), DELTA_RGB(3, 3,  4)), /* 1: SHADER_DAWN_MIST */
        PACK_SHADER(DELTA_RGB( 3,  0, -2), DELTA_RGB(6, 3, -1)), /* 2: SHADER_GOLDEN_GLOW */
        PACK_SHADER(DELTA_RGB(-2, -1,  3), DELTA_RGB(3, 4,  6)), /* 3: SHADER_NIGHT_AURORA */
        PACK_SHADER(DELTA_RGB(-6, -4,  3), DELTA_RGB(7, 7,  9))  /* 4: SHADER_WET_STORM */
    },
    .lastCloudTileX  = 0x7FFF,
    .lastCloudTileY  = 0x7FFF
};

/* 16 multi-lobe cloud models (64x32 half-tile = 256x128px cell space) */
static const u16 gCloudLobes[16][4] = {
    /* 0..3: Compact Cumulus Puffs (96x64 to 128x72 px) */
    { PACK_LOBE(28, 16, 7), PACK_LOBE(36, 15, 6), 0, 0 },
    { PACK_LOBE(25, 15, 6), PACK_LOBE(33, 17, 7), PACK_LOBE(40, 15, 5), 0 },
    { PACK_LOBE(23, 17, 6), PACK_LOBE(31, 14, 7), PACK_LOBE(39, 16, 6), 0 },
    { PACK_LOBE(24, 16, 7), PACK_LOBE(32, 16, 8), PACK_LOBE(41, 16, 6), 0 },
    /* 4..9: Medium Rolling Cumulus (136x80 to 168x96 px) */
    { PACK_LOBE(20, 17, 6), PACK_LOBE(29, 15, 8), PACK_LOBE(39, 16, 7), 0 },
    { PACK_LOBE(19, 15, 7), PACK_LOBE(29, 17, 8), PACK_LOBE(39, 15, 7), PACK_LOBE(46, 17, 5) },
    { PACK_LOBE(18, 17, 6), PACK_LOBE(27, 14, 8), PACK_LOBE(37, 15, 8), PACK_LOBE(46, 17, 6) },
    { PACK_LOBE(19, 14, 6), PACK_LOBE(28, 16, 8), PACK_LOBE(38, 17, 7), PACK_LOBE(46, 19, 5) },
    { PACK_LOBE(19, 19, 5), PACK_LOBE(27, 17, 7), PACK_LOBE(37, 15, 8), PACK_LOBE(46, 14, 6) },
    { PACK_LOBE(18, 16, 7), PACK_LOBE(28, 14, 7), PACK_LOBE(38, 17, 8), PACK_LOBE(47, 16, 6) },
    /* 10..15: Giant Cumulus Congestus & Sweeping Banks (176x96 to 208x112 px) */
    { PACK_LOBE(15, 17, 6), PACK_LOBE(25, 15, 9), PACK_LOBE(37, 15, 8), PACK_LOBE(48, 17, 7) },
    { PACK_LOBE(15, 16, 7), PACK_LOBE(26, 17, 8), PACK_LOBE(37, 14, 9), PACK_LOBE(48, 16, 7) },
    { PACK_LOBE(14, 17, 6), PACK_LOBE(24, 15, 8), PACK_LOBE(35, 16, 9), PACK_LOBE(47, 15, 8) },
    { PACK_LOBE(15, 15, 7), PACK_LOBE(25, 17, 9), PACK_LOBE(37, 16, 8), PACK_LOBE(48, 18, 6) },
    { PACK_LOBE(14, 16, 7), PACK_LOBE(25, 14, 8), PACK_LOBE(36, 16, 9), PACK_LOBE(48, 17, 7) },
    { PACK_LOBE(14, 17, 7), PACK_LOBE(25, 15, 9), PACK_LOBE(37, 15, 9), PACK_LOBE(49, 17, 7) }
};

/* Forward declarations of C handlers called by naked trampolines */
__attribute__((used)) void Visual_FieldUpdate(AreaLightManager *lightMan, FieldSystem *fieldSystem);
__attribute__((used)) void Visual_AreaLightFree(void);
__attribute__((used)) void Visual_WaterShimmer(u32 slotIdx, u8 *slotPtr);
__attribute__((used)) void Hook2_AreaLightApply(const AreaLightTemplate *tpl, ModelAttributes *attrs, u32 count);
__attribute__((used)) void Hook5_BillboardMtx(MtxFx33 *mtx);

/* Naked assembly trampolines (.text.trampolines) */
__attribute__((naked, section(".text.trampolines"), used))
void Hook3_AreaLightFree(void) {
    __asm__ volatile(
        "str r0, [r4, #0]\n\t"
        "bl Visual_AreaLightFree\n\t"
        "pop {r4, pc}\n\t"
    );
}

__attribute__((naked, section(".text.trampolines"), used))
void Hook7_WaterShimmer(void) {
    __asm__ volatile(
        "push {r4-r7, lr}\n\t"
        "ldr r6, =%c0\n\t"
        "blx r6\n\t"
        "mov r0, r4\n\t"
        "mov r1, r5\n\t"
        "bl Visual_WaterShimmer\n\t"
        "pop {r4-r7, pc}\n\t"
        ".balign 4\n\t"
        ".ltorg\n\t"
        :
        : "i"(ADDR_VRAM_TRANSFER_REQ)
    );
}

__attribute__((naked, section(".text.trampolines"), used))
void Hook1_FieldUpdate(void) {
    __asm__ volatile(
        "push {r4-r7, lr}\n\t"
        "mov r1, r5\n\t"
        "bl Visual_FieldUpdate\n\t"
        "pop {r4-r7, pc}\n\t"
    );
}

/* Shared helpers (color math, ease-in/ease-out) */
static inline VisualEngineState *GetVisualState(void) {
    VisualEngineState *st = &gVisualState;
    __asm__ volatile("" : "+r"(st));
    return st;
}

static inline volatile u16 *GetIoBase16(void) {
    volatile u16 *io16 = (volatile u16 *)0x04000000u;
    __asm__ volatile("" : "+r"(io16));
    return io16;
}

__attribute__((noinline))
static u16 LerpModBgr555(u16 c0, u16 c1, u32 t_q8, s32 delta555) {
    u32 d555 = (u32)(delta555 + 0x4210);
    u16 out = 0;
    for (u32 shift = 0; shift < 15u; shift += 5u) {
        s32 v0 = (c0 >> shift) & 0x1F;
        s32 v1 = (c1 >> shift) & 0x1F;
        s32 d  = (s32)((d555 >> shift) & 0x1F) - 16;
        s32 v  = v0 + (((v1 - v0) * (s32)t_q8) >> 8) + d;
        if (v < 0) v = 0;
        if (v > 31) v = 31;
        out |= (u16)(v << shift);
    }
    return out;
}

__attribute__((noinline))
static s16 SmoothEaseStep(s32 *posVelQ8, s32 target) {
    s32 errQ8 = (target << 8) - posVelQ8[0];
    s32 dv = (errQ8 >> 4) - posVelQ8[1];
    if (dv > 128) dv = 128;
    if (dv < -128) dv = -128;
    s32 v = (errQ8 > -512 && errQ8 < 512) ? errQ8 : (posVelQ8[1] + dv);
    posVelQ8[1] = v;
    posVelQ8[0] += v;
    return (s16)(posVelQ8[0] >> 8);
}

/* Hardware BG2 2D multi-model cloud shadows */
__attribute__((noinline))
static u8 EvalCloudVertex(s32 wx, s32 wy) {
    s32 py = (wy & 15) << 1;
    if (py == 0) {
        return 0u;
    }
    s32 cy = wy >> 4;
    s32 wxShift = wx + cy * 19;
    s32 px = (wxShift & 31) << 1;
    if (px == 0) {
        return 0u;
    }

    u32 h = (u32)(wxShift >> 5) * 374761393u + (u32)cy * 668265263u;
    h = (h ^ (h >> 13)) * 1274126177u;

    if (((h >> 24) & 7u) >= 5u) {
        return 0u;
    }

    px -= (s32)((h >> 8) & 7u) - 4;
    py -= (s32)((h >> 12) & 3u) - 2;
    if (h & 0x10000u) px = 64 - px;
    if (h & 0x20000u) py = 32 - py;

    const u16 *lobes = gCloudLobes[(h >> 18) & 15u];
    s32 maxDiff = 0;
    for (u32 l = 0; l < 4u; l++) {
        u32 lb = lobes[l];
        if (lb == 0u) break;
        s32 dx = px - (s32)(lb & 63u);
        s32 dy = py - (s32)((lb >> 6) & 31u);
        s32 r  = (s32)(lb >> 11);
        s32 diff = r * r - (dx * dx + dy * dy);
        if (diff > maxDiff) {
            maxDiff = diff;
        }
    }
    if (maxDiff <= 0)  return 0u;
    if (maxDiff < 12)  return 1u;
    if (maxDiff < 24)  return 2u;
    return 3u;
}

__attribute__((noinline))
static void Visual_UpdateCloudBg2(FieldSystem *fieldSystem) {
    volatile u16 *io16 = GetIoBase16();
    volatile u32 *io32 = (volatile u32 *)io16;

    u32 uiUsingBg2 = ((io16[6] & 3u) == 0u) || ((io16[4] & 3u) == 3u);
    if (fieldSystem == NULL || uiUsingBg2) {
        if (uiUsingBg2) {
            io32[6] = 0;
            io16[0] |= 0x0400u;
        }
        if (io32[20] == 0x0E020144u) {
            io32[20] = 0;
            io32[6]  = 0;
            if (!uiUsingBg2) {
                io16[0] &= (u16)~0x0400u;
            }
        }
        return;
    }

    VisualEngineState *st = GetVisualState();

    /* Keep PAL6[0..1] pure black (0x0000) so shadows darken without tinting */
    PLTT_BG_PAL6[0] = 0u;

    /* Sentinel check: Tile 0 must be 0 (sky) and Tile 255 must be 0x11111111 (solid interior) */
    if (io32[20] != 0x0E020144u || VRAM_BG2_CHR[0] != 0u || VRAM_BG2_CHR[255u * 8u] != 0x11111111u) {
        for (u32 idx = 0; idx < 256u; idx++) {
            u32 v00 = idx & 3u;
            u32 v10 = (idx >> 2) & 3u;
            u32 v01 = (idx >> 4) & 3u;
            u32 v11 = (idx >> 6) & 3u;
            for (u32 py = 0; py < 8u; py++) {
                u32 row0 = (8u - py) * v00 + py * v01;
                u32 row1 = (8u - py) * v10 + py * v11;
                u32 word = 0u;
                for (u32 px = 0; px < 8u; px++) {
                    u32 val = (8u - px) * row0 + px * row1; /* 0..192 */
                    u32 bayer = (((px ^ py) & 1u) << 3) | ((py & 1u) << 2) | ((px ^ py) & 2u) | ((py & 2u) >> 1);
                    if (val > 80u + bayer) {
                        word |= 1u << (px << 2);
                    }
                }
                VRAM_BG2_CHR[(idx << 3) + py] = word;
            }
        }
        st->lastCloudTileX = 0x7FFF;
    }

    io16[4] = (io16[4] & (u16)~3u) | 2u; /* BG0 (3D) priority 2 */
    io16[6] = 0x1E09u;                   /* BG2 priority 1, charBase 2, scrBase 30 */
    io32[20] = 0x0E020144u;              /* BLDCNT = 0x0144 (BG2 -> BG0 only), BLDALPHA = 0x0E02 */

    Camera *cam = fieldSystem->camera;
    if (cam != NULL) {
        const VecFx32 *t = cam->trackedTarget ? cam->trackedTarget : &cam->target;
        u32 f = st->frameCounter;
        u32 hofs = (u32)(t->x >> 12) + (f >> 4);
        u32 vofs = (u32)((t->z * 3) >> 14) + (f >> 5);
        s16 baseWx = (s16)(hofs >> 3);
        s16 baseWy = (s16)(vofs >> 3);

        if (baseWx != st->lastCloudTileX || baseWy != st->lastCloudTileY) {
            st->lastCloudTileX = baseWx;
            st->lastCloudTileY = baseWy;
            u8 prevRow[33];
            for (u32 x = 0; x <= 32u; x++) {
                prevRow[x] = EvalCloudVertex((s32)baseWx + (s32)x, (s32)baseWy);
            }
            for (u32 y = 0; y < 32u; y++) {
                s32 wy = (s32)baseWy + (s32)y;
                u32 scrRow = ((u32)wy & 31u) << 5;
                u8 v00 = prevRow[0];
                u8 v01 = EvalCloudVertex((s32)baseWx, wy + 1);
                prevRow[0] = v01;
                for (u32 x = 0; x < 32u; x++) {
                    s32 wx = (s32)baseWx + (s32)x;
                    u8 v10 = prevRow[x + 1];
                    u8 v11 = EvalCloudVertex(wx + 1, wy + 1);
                    prevRow[x + 1] = v11;
                    u32 tileIdx = (u32)v00 | ((u32)v10 << 2) | ((u32)v01 << 4) | ((u32)v11 << 6);
                    VRAM_BG2_SCR[scrRow | ((u32)wx & 31u)] = (u16)(0x6000u | tileIdx);
                    v00 = v10;
                    v01 = v11;
                }
            }
        }
        io32[6] = (hofs & 0xFFFFu) | ((vofs & 0xFFFFu) << 16);
    }
    io16[0] |= 0x0400u;
}

/* Hook 2 & 3: AreaLight apply & free */
__attribute__((noinline))
void Visual_AreaLightFree(void) {
    VisualEngineState *st = GetVisualState();
    u8 preset = st->presetForcedWeather;
    u32 *p = (u32 *)&st->currPitchOff;
    for (u32 i = 0; i < 12; i++) {
        p[i] = 0;
    }
    st->presetForcedWeather = preset;
    st->lightDirty      = 1;
    st->activeCamPitch  = 0xDD40;
    st->lastCloudTileX  = 0x7FFF;
    G3X_SetFog(FALSE, 0, 0, 0);
    Visual_UpdateCloudBg2(NULL);
}

void Hook2_AreaLightApply(const AreaLightTemplate *tpl, ModelAttributes *attrs, u32 count) {
    VisualEngineState *st = GetVisualState();
    if (tpl->validLightsMask >= 8 && count > 1) {
        st->isOutdoor  = 1;
        st->lightDirty = 1;
    } else {
        Visual_AreaLightFree();
    }
    st->sunColor = tpl->lightColors[0];
    AreaLightTemplate_ApplyToModelAttributes(tpl, attrs);
}

/* 3D orbital camera step */
__attribute__((noinline))
static void Visual_StepCamera(FieldSystem *fieldSystem) {
    VisualEngineState *st = GetVisualState();
    u8 inGrass = 0;

    PlayerAvatar *avatar = fieldSystem->playerAvatar;
    if (avatar != NULL) {
        u8 *mapObj = avatar->mapObject;
        if (mapObj != NULL && (u32)(*(u32 *)(mapObj + 0xAC) - 2u) <= 1u) {
            inGrass = 1;
        }
    }
    st->inTallGrass = inGrass;

    Camera *cam = (fieldSystem->unk_20 == 0) ? fieldSystem->camera : NULL;
    if (cam == NULL || cam->fovY != 0x0830 || cam->trackedTarget == NULL) {
        return;
    }

    s32 pitchOff = SmoothEaseStep(&st->pitchPosQ8, inGrass ? -0x00B0 : 0);
    st->currPitchOff = (s16)pitchOff;
    u16 newPitch = (u16)(0xDD40 + pitchOff);
    cam->angle.x = newPitch;
    st->activeCamPitch = newPitch;

    st->currDistOff = 0;
    cam->distance = 0x1D8000;

    st->currYawOff = 0;
    cam->angle.y = 0;

    Camera_CalcLookAtPos(cam);
}

/* Lighting & hardware specular rebuild */
__attribute__((noinline))
static void Visual_RebuildLight(
    ModelAttributes *attrs,
    const AreaLightTemplate *prevTpl,
    const AreaLightTemplate *currTpl
) {
    VisualEngineState *st = GetVisualState();
    AreaLightTemplate liveTpl;
    u32 t_q8 = st->lastSolarTq8;

    liveTpl.endTime = currTpl->endTime;
    liveTpl.validLightsMask = prevTpl->validLightsMask | currTpl->validLightsMask;

    const u16 *p16 = (const u16 *)prevTpl;
    const u16 *c16 = (const u16 *)currTpl;
    u16 *l16       = (u16 *)&liveTpl;

    u32 wm = (st->weatherShaderMode < 5) ? st->weatherShaderMode : 0;
    u32 pack = st->shaderPack[wm];
    s32 baseMatD = (s16)pack;
    s32 specD    = (s16)(pack >> 16);

    for (u32 i = 3u; i < 23u; i++) {
        u16 p = p16[i];
        u16 c = c16[i];
        if (i >= 7u && i < 19u) {
            l16[i] = (u16)((s16)p + ((((s16)c - (s16)p) * (s32)t_q8) >> 8));
        } else {
            s32 md = (i == 3u) ? baseMatD
                   : ((i == 19u || i == 20u) ? (baseMatD + st->inTallGrass * (s32)(s16)DELTA_GRASS_TINT)
                   : ((i == 21u) ? specD : 0));
            l16[i] = LerpModBgr555(p, c, st->lastSolarTq8, md);
        }
    }
    st->sunColor = liveTpl.lightColors[0];

    if (attrs != NULL) {
        AreaLightTemplate_ApplyToModelAttributes(&liveTpl, attrs);
        attrs->enableSpecularReflectShininessTable = TRUE;
    }

    u32 mult = (wm == SHADER_DAWN_MIST || wm == SHADER_WET_STORM) ? 9u : 5u;
    for (u32 d = 0; d < 32; d++) {
        REG_G3_SHININESS = ((d * d) >> 3) * 0x01010101u;
        st->horizonFogTable[d] = (d < 16u) ? 0u : (u8)(((d - 15u) * mult) >> 2);
    }

    if (st->weatherShaderMode < SHADER_NATIVE_WEATHER) {
        G3X_SetFog(TRUE, 0, 3, 0x6A00);
        G3X_SetFogTable(st->horizonFogTable);
        REG_G3X_FOG_COLOR = (u32)st->sunColor | (31u << 16);
    }
}

/* Hook 1: 60 FPS field update (camera, shaders, BG2 cloud shadows) */
void Visual_FieldUpdate(AreaLightManager *lightMan, FieldSystem *fieldSystem) {
    AreaLightManager_UpdateActiveTemplate(lightMan);

    VisualEngineState *st = GetVisualState();
    st->frameCounter++;

    if (lightMan->templateCount <= 1 || lightMan->templates[0].validLightsMask < 8) {
        Visual_AreaLightFree();
        return;
    }
    st->isOutdoor = 1;

    Visual_StepCamera(fieldSystem);

    /* Select weather & time-of-day shader mode */
    u32 count = lightMan->templateCount;
    u32 activeIdx = (u32)lightMan->activeTemplateIndex;

    s32 rawWeather = 0;
    if (fieldSystem->unk_04 != NULL && fieldSystem->unk_04->weatherMan != NULL) {
        rawWeather = fieldSystem->unk_04->weatherMan->activeWeather;
    }
    __asm__ volatile("" : "+r"(rawWeather));

    u8 weatherMode;
    if (st->presetForcedWeather & 0x80u) {
        weatherMode = st->presetForcedWeather & 0x07u;
        activeIdx = (0x0008EB47u >> (weatherMode << 2)) & 0x0Fu;
    } else if ((u32)(rawWeather - 1) <= 3u) {
        weatherMode = SHADER_WET_STORM;
    } else if (rawWeather >= 6 && rawWeather != 8 && rawWeather != 13) {
        weatherMode = SHADER_NATIVE_WEATHER;
    } else {
        u32 lutIdx = (count < 10) ? (activeIdx * 3u) : activeIdx;
        weatherMode = (u8)((0xFEA0017Fu >> ((lutIdx & 15u) << 1)) & 3u);
    }
    if (activeIdx >= count) activeIdx = 0;
    st->weatherShaderMode = weatherMode;

    /* Continuous solar/lunar interpolation with dirty-flag caching */
    u32 curHalfSec = (u32)GetSecondsSinceMidnight() >> 1;
    const AreaLightTemplate *currTpl = &lightMan->templates[activeIdx];
    const AreaLightTemplate *prevTpl = (activeIdx > 0 && !(st->presetForcedWeather & 0x80u))
        ? (currTpl - 1)
        : currTpl;
    s32 startT = (s32)prevTpl->endTime;
    s32 span = (s32)currTpl->endTime - startT;
    s32 num  = (s32)curHalfSec - startT;
    u32 t_q8 = 0;
    for (u32 b = 0; b < 8; b++) {
        num <<= 1;
        t_q8 <<= 1;
        if (num >= span) {
            num -= span;
            t_q8 |= 1u;
        }
    }

    u16 *cache = (u16 *)&st->lastActiveIdx;
    u16 k0 = (u16)((activeIdx & 0xFFu) | (t_q8 << 8));
    u16 k1 = (u16)(st->inTallGrass | ((u32)weatherMode << 8));
    if (st->lightDirty || cache[0] != k0 || cache[1] != k1) {
        cache[0] = k0;
        cache[1] = k1;
        st->lightDirty = 0;
        Visual_RebuildLight(lightMan->areaModelAttrs, prevTpl, currTpl);
    }

    st->baseSpecEmi = *(volatile u32 *)ADDR_GLB_MAT_COL1 | 0x8000u;
    *(volatile u32 *)ADDR_GLB_MAT_COL1 = st->baseSpecEmi;

    /* Hardware BG2 cloud shadows on the ground */
    Visual_UpdateCloudBg2((weatherMode <= SHADER_GOLDEN_GLOW) ? fieldSystem : NULL);
}

/* Hook 5: 3D billboard pitch & yaw alignment */
void Hook5_BillboardMtx(MtxFx33 *mtx) {
    MTX_Identity33(mtx);
    VisualEngineState *st = GetVisualState();
    if (!st->isOutdoor) {
        return;
    }

    s32 deltaPitch = (s16)st->activeCamPitch + 0x29FE;
    if (deltaPitch <= 0) {
        return;
    }

    s32 sinP = (deltaPitch * 201) >> 9;
    s32 cosP = 0x1000 - ((sinP * sinP) >> 13);
    s32 sinY = ((s32)st->currYawOff * 201) >> 9;

    mtx->m[0][2] = -sinY;

    mtx->m[1][0] = -(sinP * sinY) >> 12;
    mtx->m[1][1] = cosP + (cosP >> 4);
    mtx->m[1][2] = -sinP;

    mtx->m[2][0] = (cosP * sinY) >> 12;
    mtx->m[2][1] = sinP;
    mtx->m[2][2] = cosP;
}

/* Hook 7: 60 FPS VRAM water palette shimmer */
void Visual_WaterShimmer(u32 slotIdx, u8 *slotPtr) {
    u8 *pAnimEntry = *(u8 **)(slotPtr + 0x08);
    if (pAnimEntry == NULL || (pAnimEntry[1] & 1u) == 0) {
        return;
    }

    u8 *texAnimMan = slotPtr - 8 - (slotIdx * 24u);
    u8 *pMapTex  = *(u8 **)(texAnimMan + 0x04);
    u8 *pAnimTex = *(u8 **)(slotPtr + 0x0C);
    u8 *pDict = pMapTex + *(u16 *)(pMapTex + 0x34);
    u32 pcount = pDict[1];
    u32 targetName = *(u32 *)pAnimEntry;
    u32 namesBaseOff = (pcount << 3) + 16u;

    for (u32 i = 0; i < pcount; i++) {
        if (*(u32 *)(pDict + namesBaseOff + (i << 4)) == targetName) {
            u32 valOff = *(u16 *)(pDict + 16u + ((pcount + i) << 2));
            u32 dstVramAddr = ((u32)(*(u16 *)(pMapTex + 0x2C)) + valOff) << 3;
            u16 *pAnimPltt = (u16 *)(pAnimTex + *(u32 *)(pAnimTex + 0x38));
            u16 *pMapPltt  = (u16 *)(pMapTex  + *(u32 *)(pMapTex  + 0x38) + (valOff << 3));

            VisualEngineState *st = GetVisualState();
            u32 fShift = st->frameCounter >> 2;

            for (u32 k = 0; k < 8; k++) {
                u16 col = pAnimPltt[k];
                if (col != 0) {
                    s32 w = (s32)st->sineWaveTable[(fShift + (k << 1)) & 15u] >> 4;
                    col = LerpModBgr555(col, col, 0, (1 + w) * DELTA_STEP_ALL);
                }
                pMapPltt[k] = col;
            }

            DC_FlushRange(pMapPltt, 16);
            VramTransfer_Request(1, dstVramAddr, pMapPltt, 16);
            return;
        }
    }
}
