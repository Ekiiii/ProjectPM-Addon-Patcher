/*
 * type_eff_badge.c
 * Clean C implementation of in-battle Move Type Effectiveness Capsule Badges
 * for Pokémon Platinum FR / US (ProjectPM) - Single & Double Battle Edition.
 *
 * Compiled with:
 *   arm-none-eabi-gcc -mcpu=arm946e-s -mthumb -Os -fno-builtin -nostdlib
 *
 * Features:
 * 1. Move Selection Screen (Sub OBJ Palette 3):
 *    - Single enemy or identical effectiveness on both enemies:
 *      Renders a 17x12 pixel-art single capsule badge ([x4], [x2], [x1], [x1/2], [x1/4], [x0]).
 *    - Double battle with 2 alive enemies having different effectiveness:
 *      Renders a 19x12 pixel-art bicolor split capsule badge ([Left | Right], e.g. [2|1], [1|1/2]).
 * 2. Target Selection Screen (Sub OBJ Palette 6):
 *    - Renders the individual 17x12 pixel-art capsule badge right next to each target's name
 *      (e.g. "CANINOS ♂ [x2]", "DYNAVOLT ♂ [x1]").
 */
#include <stdint.h>

typedef uint8_t  u8;
typedef uint16_t u16;
typedef uint32_t u32;
typedef int32_t  s32;

typedef struct {
    void *bgConfig;
    u8 bgLayer;
    u8 tilemapLeft;
    u8 tilemapTop;
    u8 width;
    u8 height;
    u8 palette;
    u16 baseTileAndColorMode;
    u8 *pixels;
} Window;

typedef struct {
    Window window;
    u16 width;
    u16 height;
} TextWindowLayout;

typedef struct {
    u32 moveTable_LoadParam;
    u32 battleContext_Get;
    u32 typeMatchupMultiplier;
    u32 calcStringDimensions;
    u32 window_Remove;
    u32 window_Init;
    u32 battleSystem_GetBgConfig;
    u32 window_AddToTopLeftCorner;
    u32 text_AddPrinterWithParams;
    u32 newFontOAM;
} BadgeApiTable;

__attribute__((section(".header"), used))
volatile const BadgeApiTable gApi = {
    0x0206E269, // MoveTable_LoadParam
    0x02255CE9, // BattleContext_Get
    0x02252A35, // TypeMatchupMultiplier
    0x0227D6E1, // CalcStringDimensions
    0x0201B01D, // Window_Remove
    0x0201AEBD, // Window_Init
    0x0224D559, // BattleSystem_GetBgConfig
    0x0201AF91, // Window_AddToTopLeftCorner
    0x0201DFC9, // Text_AddPrinterWithParamsColorAndSpacing
    0x0227D711, // BattleSubscreen_NewFontOAM
};

// 13-bit wide x 7-row pixel-art white glyph bitmaps for single capsule badges:
// Index 0: x0   (Immune)
// Index 1: x1/4 (0.25x)
// Index 2: x1/2 (0.5x)
// Index 3: x1   (1.0x)
// Index 4: x2   (2.0x)
// Index 5: x4   (4.0x)
static const u16 gBadgeGlyphs[6][7] = {
    // 0: x0
    { 0x01C0, 0x0360, 0x036A, 0x0364, 0x0364, 0x036A, 0x01CA },
    // 1: x1/4
    { 0x0110, 0x0090, 0x0655, 0x0722, 0x06A2, 0x0F95, 0x0605 },
    // 2: x1/2
    { 0x0110, 0x0090, 0x0755, 0x0C22, 0x0712, 0x0195, 0x0F85 },
    // 3: x1
    { 0x00C0, 0x00E0, 0x00CA, 0x00C4, 0x00C4, 0x00CA, 0x01EA },
    // 4: x2
    { 0x01C0, 0x0320, 0x030A, 0x01C4, 0x0064, 0x006A, 0x03EA },
    // 5: x4
    { 0x0180, 0x01C0, 0x01AA, 0x01A4, 0x03E4, 0x018A, 0x018A },
};

// 5-bit wide x 7-row compact glyphs for bicolor split capsule halves (0, 1/4, 1/2, 1, 2, 4):
static const u8 gMiniGlyphs[6][7] = {
    // 0: "0"
    { 0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E },
    // 1: "1/4"
    { 0x01, 0x01, 0x05, 0x12, 0x14, 0x1F, 0x10 },
    // 2: "1/2"
    { 0x01, 0x01, 0x1D, 0x12, 0x1C, 0x04, 0x1C },
    // 3: "1"
    { 0x04, 0x06, 0x04, 0x04, 0x04, 0x04, 0x0E },
    // 4: "2"
    { 0x0E, 0x11, 0x10, 0x0E, 0x01, 0x01, 0x1F },
    // 5: "4"
    { 0x08, 0x0C, 0x0A, 0x09, 0x1F, 0x08, 0x08 },
};

// Palette 3 color indices (Move Selection buttons): { topHighlight, mainFill, bottomBorder }
static const u8 gMoveBadgeThemeColors[6][3] = {
    { 8,  13, 9  }, // 0: x0   (Dark / Immune)
    { 10, 11, 12 }, // 1: x1/4 (Orange-Red / Not Very Effective)
    { 10, 11, 12 }, // 2: x1/2 (Orange-Red / Not Very Effective)
    { 4,  5,  6  }, // 3: x1   (Neutral Slate Gray)
    { 1,  2,  3  }, // 4: x2   (Vibrant Green / Super Effective)
    { 1,  2,  3  }, // 5: x4   (Vibrant Green / Super Effective)
};

// Palette 6 color indices (Target Selection buttons): { topHighlight, mainFill, bottomBorder }
static const u8 gTargetBadgeThemeColors[6][3] = {
    { 5,  14, 6  }, // 0: x0   (Dark / Immune)
    { 10, 15, 3  }, // 1: x1/4 (Orange-Red / Not Very Effective)
    { 10, 15, 3  }, // 2: x1/2 (Orange-Red / Not Very Effective)
    { 5,  13, 6  }, // 3: x1   (Neutral Slate Gray)
    { 11, 12, 6  }, // 4: x2   (Vibrant Green / Super Effective)
    { 11, 12, 6  }, // 5: x4   (Vibrant Green / Super Effective)
};

static inline void SetPixel4bpp(u8 *pixels, int tileStride, int x, int y, u8 color) {
    int tx = x >> 3;
    int ty = y >> 3;
    if (tx < 0 || tx >= tileStride || ty < 0 || ty >= 2) {
        return;
    }
    int tileIdx = ty * tileStride + tx;
    int byteOff = (tileIdx << 5) + ((y & 7) << 2) + ((x & 7) >> 1);
    if (x & 1) {
        pixels[byteOff] = (pixels[byteOff] & 0x0F) | (color << 4);
    } else {
        pixels[byteOff] = (pixels[byteOff] & 0xF0) | (color & 0x0F);
    }
}

static void DrawCapsuleBadge(
    u8 *pixels,
    int tileStride,
    int startX,
    int badgeIdx,
    const u8 themeColors[6][3],
    u8 colSha,
    u8 colText
) {
    const u8 colTop  = themeColors[badgeIdx][0];
    const u8 colFill = themeColors[badgeIdx][1];
    const u8 colBot  = themeColors[badgeIdx][2];

    // 1. Capsule top bevel (y = 2) and bottom dark border (y = 13)
    for (int x = 1; x < 16; x++) {
        SetPixel4bpp(pixels, tileStride, startX + x, 2,  colTop);
        SetPixel4bpp(pixels, tileStride, startX + x, 13, colBot);
    }

    // 2. Capsule main body fill (y = 3..12, x = 0..16)
    for (int y = 3; y <= 12; y++) {
        for (int x = 0; x < 17; x++) {
            SetPixel4bpp(pixels, tileStride, startX + x, y, colFill);
        }
    }

    // 3. Rounded capsule corners (y = 3 and y = 12 at x = 0, 16)
    SetPixel4bpp(pixels, tileStride, startX + 0,  3,  colTop);
    SetPixel4bpp(pixels, tileStride, startX + 16, 3,  colTop);
    SetPixel4bpp(pixels, tileStride, startX + 0,  12, colBot);
    SetPixel4bpp(pixels, tileStride, startX + 16, 12, colBot);

    // 4. Pass 1: 3-way drop shadow (right, down, down-right)
    const u16 *glyph = gBadgeGlyphs[badgeIdx];
    for (int gy = 0; gy < 7; gy++) {
        u16 rowBits = glyph[gy];
        for (int gx = 0; gx < 13; gx++) {
            if (rowBits & (1 << gx)) {
                int wx = startX + 2 + gx;
                int wy = 4 + gy;
                SetPixel4bpp(pixels, tileStride, wx + 1, wy,     colSha);
                SetPixel4bpp(pixels, tileStride, wx,     wy + 1, colSha);
                SetPixel4bpp(pixels, tileStride, wx + 1, wy + 1, colSha);
            }
        }
    }

    // 5. Pass 2: Crisp white foreground pixel-art glyphs
    for (int gy = 0; gy < 7; gy++) {
        u16 rowBits = glyph[gy];
        for (int gx = 0; gx < 13; gx++) {
            if (rowBits & (1 << gx)) {
                int wx = startX + 2 + gx;
                int wy = 4 + gy;
                SetPixel4bpp(pixels, tileStride, wx, wy, colText);
            }
        }
    }
}

static void DrawBicolorCapsuleBadge(
    u8 *pixels,
    int tileStride,
    int startX,
    int badgeLeft,
    int badgeRight
) {
    const u8 topL  = gMoveBadgeThemeColors[badgeLeft][0];
    const u8 fillL = gMoveBadgeThemeColors[badgeLeft][1];
    const u8 botL  = gMoveBadgeThemeColors[badgeLeft][2];

    const u8 topR  = gMoveBadgeThemeColors[badgeRight][0];
    const u8 fillR = gMoveBadgeThemeColors[badgeRight][1];
    const u8 botR  = gMoveBadgeThemeColors[badgeRight][2];

    const u8 colSha  = 14;
    const u8 colText = 15;

    // 1. Left half (x = 0..8) and Right half (x = 10..18), plus center divider (x = 9)
    for (int x = 1; x <= 8; x++) {
        SetPixel4bpp(pixels, tileStride, startX + x, 2,  topL);
        SetPixel4bpp(pixels, tileStride, startX + x, 13, botL);
    }
    for (int x = 10; x <= 17; x++) {
        SetPixel4bpp(pixels, tileStride, startX + x, 2,  topR);
        SetPixel4bpp(pixels, tileStride, startX + x, 13, botR);
    }
    for (int y = 2; y <= 13; y++) {
        SetPixel4bpp(pixels, tileStride, startX + 9, y, colSha);
    }

    // 2. Body fill (y = 3..12)
    for (int y = 3; y <= 12; y++) {
        for (int x = 0; x <= 8; x++) {
            SetPixel4bpp(pixels, tileStride, startX + x, y, fillL);
        }
        for (int x = 10; x <= 18; x++) {
            SetPixel4bpp(pixels, tileStride, startX + x, y, fillR);
        }
    }

    // 3. Rounded outer corners (x = 0, 18 at y = 3, 12)
    SetPixel4bpp(pixels, tileStride, startX + 0,  3,  topL);
    SetPixel4bpp(pixels, tileStride, startX + 0,  12, botL);
    SetPixel4bpp(pixels, tileStride, startX + 18, 3,  topR);
    SetPixel4bpp(pixels, tileStride, startX + 18, 12, botR);

    // 4. Draw Left & Right compact 5x7 glyphs with 3-way drop shadow
    for (int side = 0; side < 2; side++) {
        int bIdx = (side == 0) ? badgeLeft : badgeRight;
        int baseX = startX + ((side == 0) ? 2 : 11);
        const u8 *glyph = gMiniGlyphs[bIdx];

        for (int gy = 0; gy < 7; gy++) {
            u8 rowBits = glyph[gy];
            for (int gx = 0; gx < 5; gx++) {
                if (rowBits & (1 << gx)) {
                    int wx = baseX + gx;
                    int wy = 4 + gy;
                    SetPixel4bpp(pixels, tileStride, wx + 1, wy,     colSha);
                    SetPixel4bpp(pixels, tileStride, wx,     wy + 1, colSha);
                    SetPixel4bpp(pixels, tileStride, wx + 1, wy + 1, colSha);
                }
            }
        }
        for (int gy = 0; gy < 7; gy++) {
            u8 rowBits = glyph[gy];
            for (int gx = 0; gx < 5; gx++) {
                if (rowBits & (1 << gx)) {
                    int wx = baseX + gx;
                    int wy = 4 + gy;
                    SetPixel4bpp(pixels, tileStride, wx, wy, colText);
                }
            }
        }
    }
}

static int ComputeMoveBadgeVsBattler(void *btlSubscreen, u16 moveID, int targetBattler) {
    if (moveID == 0 || btlSubscreen == 0) {
        return -1;
    }

    typedef int (*MoveTableLoadFn)(int, int);
    typedef int (*BattleCtxGetFn)(void *, int, int, void *);
    typedef int (*TypeMatchupFn)(int, int, int);

    MoveTableLoadFn MoveTable_LoadParam = (MoveTableLoadFn)gApi.moveTable_LoadParam;
    BattleCtxGetFn  BattleContext_Get   = (BattleCtxGetFn)gApi.battleContext_Get;
    TypeMatchupFn   TypeMatchup         = (TypeMatchupFn)gApi.typeMatchupMultiplier;

    int power = MoveTable_LoadParam(moveID, 2); // MOVEATTRIBUTE_POWER
    if (power == 0) {
        return -1; // Status move -> no badge
    }

    int moveType = MoveTable_LoadParam(moveID, 3); // MOVEATTRIBUTE_TYPE

    void *battleSys = *(void **)btlSubscreen;
    if (battleSys == 0) {
        return -1;
    }
    void *battleCtx = *(void **)((u8 *)battleSys + 0x30);
    if (battleCtx == 0) {
        return -1;
    }

    int defType1 = BattleContext_Get(battleCtx, targetBattler, 0x1B, 0);
    int defType2 = BattleContext_Get(battleCtx, targetBattler, 0x1C, 0);
    int mul = TypeMatchup(moveType, defType1, defType2);

    if (mul == 0)  return 0; // x0
    if (mul < 20)  return 1; // x1/4
    if (mul < 40)  return 2; // x1/2
    if (mul < 80)  return 3; // x1
    if (mul < 160) return 4; // x2
    return 5;                // x4
}

__attribute__((used))
void BattleBadge_PrepareMoveTextWindow(
    void *btlSubscreen,
    const void *str,
    int font,
    TextWindowLayout *textLayout,
    u32 textColor,
    const u16 *movePtr
) {
    typedef void (*CalcDimFn)(const void *, int, int *, int *);
    typedef void (*WinRemoveFn)(Window *);
    typedef void (*WinInitFn)(Window *);
    typedef void *(*GetBgCfgFn)(void *);
    typedef void (*WinAddFn)(void *, Window *, int, int, int, int);
    typedef int  (*AddPrinterFn)(Window *, int, const void *, int, int, int, u32, int, int, void *);
    typedef int  (*BattleCtxGetFn)(void *, int, int, void *);

    CalcDimFn      CalcStringDimensions = (CalcDimFn)gApi.calcStringDimensions;
    WinRemoveFn    Window_Remove        = (WinRemoveFn)gApi.window_Remove;
    WinInitFn      Window_Init          = (WinInitFn)gApi.window_Init;
    GetBgCfgFn     GetBgConfig          = (GetBgCfgFn)gApi.battleSystem_GetBgConfig;
    WinAddFn       Window_Add           = (WinAddFn)gApi.window_AddToTopLeftCorner;
    AddPrinterFn   Text_AddPrinter      = (AddPrinterFn)gApi.text_AddPrinterWithParams;
    BattleCtxGetFn BattleContext_Get    = (BattleCtxGetFn)gApi.battleContext_Get;

    int textWidth = 0;
    int tileWidth = 0;
    CalcStringDimensions(str, font, &textWidth, &tileWidth);

    u16 moveID = movePtr ? *movePtr : 0;
    int badgeLeft  = -1;
    int badgeRight = -1;
    int isBicolor  = 0;

    void *battleSys = btlSubscreen ? *(void **)btlSubscreen : 0;
    void *battleCtx = battleSys ? *(void **)((u8 *)battleSys + 0x30) : 0;

    if (battleCtx && moveID != 0) {
        int hpRight = BattleContext_Get(battleCtx, 1, 0x2F, 0);
        int hpLeft  = BattleContext_Get(battleCtx, 3, 0x2F, 0);
        if (hpLeft > 0 && hpRight > 0) {
            badgeLeft  = ComputeMoveBadgeVsBattler(btlSubscreen, moveID, 3);
            badgeRight = ComputeMoveBadgeVsBattler(btlSubscreen, moveID, 1);
            if (badgeLeft >= 0 && badgeRight >= 0 && badgeLeft != badgeRight) {
                isBicolor = 1;
            }
        } else if (hpRight > 0) {
            badgeLeft = ComputeMoveBadgeVsBattler(btlSubscreen, moveID, 1);
        } else if (hpLeft > 0) {
            badgeLeft = ComputeMoveBadgeVsBattler(btlSubscreen, moveID, 3);
        }
    }

    int badgeX = 0;
    if (badgeLeft >= 0) {
        int badgeW = isBicolor ? 19 : 17;
        int gap = (textWidth + 3 + badgeW <= 96) ? 3 : ((textWidth + 2 + badgeW <= 96) ? 2 : 1);
        badgeX = textWidth + gap;
        textWidth = badgeX + badgeW;
        tileWidth = (textWidth + 7) >> 3;
    }

    textLayout->height = (u16)textWidth;
    textLayout->width  = (u16)tileWidth;

    if (textLayout->window.pixels) {
        Window_Remove(&textLayout->window);
    }

    Window_Init(&textLayout->window);
    void *bgConfig = GetBgConfig(battleSys);
    Window_Add(bgConfig, &textLayout->window, tileWidth & 0xFF, 2, 0, 0);
    Text_AddPrinter(&textLayout->window, font, str, 0, 0, 0xFF, textColor, 0, 0, 0);

    if (badgeLeft >= 0 && textLayout->window.pixels) {
        if (isBicolor) {
            DrawBicolorCapsuleBadge(textLayout->window.pixels, tileWidth, badgeX, badgeLeft, badgeRight);
        } else {
            DrawCapsuleBadge(textLayout->window.pixels, tileWidth, badgeX, badgeLeft, gMoveBadgeThemeColors, 14, 15);
        }
    }
}

__attribute__((used))
void BattleBadge_TargetSelectNewFontOAM(
    void *btlSubscreen,
    void *fontOAMEntry,
    const void *str,
    int font,
    const u32 *stackArgs,
    int targetBattler
) {
    typedef void (*CalcDimFn)(const void *, int, int *, int *);
    typedef void (*WinRemoveFn)(Window *);
    typedef void (*WinInitFn)(Window *);
    typedef void *(*GetBgCfgFn)(void *);
    typedef void (*WinAddFn)(void *, Window *, int, int, int, int);
    typedef int  (*AddPrinterFn)(Window *, int, const void *, int, int, int, u32, int, int, void *);
    typedef void (*NewFontOAMFn)(void *, void *, const void *, int, u32, int, int, int, int, int, TextWindowLayout *);

    CalcDimFn    CalcStringDimensions = (CalcDimFn)gApi.calcStringDimensions;
    WinRemoveFn  Window_Remove        = (WinRemoveFn)gApi.window_Remove;
    WinInitFn    Window_Init          = (WinInitFn)gApi.window_Init;
    GetBgCfgFn   GetBgConfig          = (GetBgCfgFn)gApi.battleSystem_GetBgConfig;
    WinAddFn     Window_Add           = (WinAddFn)gApi.window_AddToTopLeftCorner;
    AddPrinterFn Text_AddPrinter      = (AddPrinterFn)gApi.text_AddPrinterWithParams;
    NewFontOAMFn NewFontOAM           = (NewFontOAMFn)gApi.newFontOAM;

    u32 textColor  = stackArgs[0];
    int plttOffset = (int)stackArgs[1];
    int plttResID  = (int)stackArgs[2];
    int x          = (int)stackArgs[3];
    int y          = (int)stackArgs[4];
    int centerX    = (int)stackArgs[5];

    u8 battlerType = *((const u8 *)btlSubscreen + 0x3C);
    int attackerBattler = (battlerType < 6) ? ((const u8 *)stackArgs)[0x34 + battlerType] : 0;

    void *battleSys = *(void **)btlSubscreen;
    void *battleCtx = battleSys ? *(void **)((u8 *)battleSys + 0x30) : 0;
    u16 moveID = battleCtx ? *(u16 *)((u8 *)battleCtx + 0x30F4 + attackerBattler * 2) : 0;

    int badgeIdx = ComputeMoveBadgeVsBattler(btlSubscreen, moveID, targetBattler);
    if (badgeIdx < 0) {
        NewFontOAM(btlSubscreen, fontOAMEntry, str, font, textColor, plttOffset, plttResID, x, y, centerX, 0);
        return;
    }

    int textWidth = 0;
    int tileWidth = 0;
    CalcStringDimensions(str, font, &textWidth, &tileWidth);

    int gap = (textWidth + 3 + 17 <= 96) ? 3 : 2;
    int badgeX = textWidth + gap;
    textWidth = badgeX + 17;
    tileWidth = (textWidth + 7) >> 3;

    TextWindowLayout tmpLayout;
    tmpLayout.height = (u16)textWidth;
    tmpLayout.width  = (u16)tileWidth;

    Window_Init(&tmpLayout.window);
    void *bgConfig = GetBgConfig(battleSys);
    Window_Add(bgConfig, &tmpLayout.window, tileWidth & 0xFF, 2, 0, 0);
    Text_AddPrinter(&tmpLayout.window, font, str, 0, 0, 0xFF, textColor, 0, 0, 0);

    if (tmpLayout.window.pixels) {
        u8 colSha = (badgeIdx == 0) ? 6 : 14;
        DrawCapsuleBadge(tmpLayout.window.pixels, tileWidth, badgeX, badgeIdx, gTargetBadgeThemeColors, colSha, 1);
    }

    NewFontOAM(btlSubscreen, fontOAMEntry, str, font, textColor, plttOffset, plttResID, x, y, centerX, &tmpLayout);

    if (tmpLayout.window.pixels) {
        Window_Remove(&tmpLayout.window);
    }
}

__attribute__((naked, section(".entry"), used))
void Entry_Trampoline(void) {
    __asm__ volatile(
        ".thumb\n"
        "push {r4, lr}\n"
        "sub sp, #8\n"
        "ldr r4, [sp, #16]\n"
        "str r4, [sp, #0]\n"
        "str r5, [sp, #4]\n"
        "bl BattleBadge_PrepareMoveTextWindow\n"
        "add sp, #8\n"
        "pop {r4, pc}\n"
        "mov r8, r8\n"
    );
}

__attribute__((naked, section(".entry2"), used))
void TargetSelect_Entry_Trampoline(void) {
    __asm__ volatile(
        ".thumb\n"
        "push {r4, lr}\n"
        "add r4, sp, #8\n"
        "sub sp, #8\n"
        "str r4, [sp, #0]\n"
        "str r6, [sp, #4]\n"
        "bl BattleBadge_TargetSelectNewFontOAM\n"
        "add sp, #8\n"
        "pop {r4, pc}\n"
        "mov r8, r8\n"
    );
}
