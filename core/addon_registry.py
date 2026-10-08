# -*- coding: utf-8 -*-
"""
addon_registry.py
Central modular registry for Multiplayer versions and Addons.
Allows easily adding new multiplayer localizations and new community addons in the future.
"""

MULTIPLAYER_VERSIONS = [
    {
        "id": "fr",
        "name": "ProjectPM Multiplayer 0.4.5 (Français)",
        "short_name": "Français",
        "lang": "fr",
        "patch_fr": "PlatinumMultiplayerV0.4.5_FR.xdelta",
        "patch_us": "PlatinumMultiplayerV0.4.5_FR-From-USA.xdelta",
        "supported_rom_langs": ["fr", "en"],  # Can be installed on Platine France or Platinum USA Rev 1
    },
    {
        "id": "en",
        "name": "ProjectPM Multiplayer 0.4.5 (English)",
        "short_name": "English",
        "lang": "en",
        "patch_us": "PlatinumMultiplayerV0.4.5.xdelta",
        "supported_rom_langs": ["en"],        # Only Platinum USA Rev 1
    },
]

ADDONS_REGISTRY = [
    {
        "id": "soullocke",
        "name": "SoulLocke",
        "name_key": "addon_soullocke",
        "desc_key": "addon_soullocke_desc",
        "requires_multiplayer": True,
        "variants": [
            {
                "id": "fr",
                "name": "Français",
                "lang": "fr",
                "payload_file": "soullocke_fr.json",
            },
            {
                "id": "en",
                "name": "English",
                "lang": "en",
                "payload_file": "soullocke_en.json",
            },
        ],
        "default_variant": "fr",
    },
]

def get_mp_version(version_id):
    for v in MULTIPLAYER_VERSIONS:
        if v["id"] == version_id:
            return v
    return MULTIPLAYER_VERSIONS[0]

def is_mp_version_supported(version_id, rom_info):
    """
    Checks if a multiplayer version is compatible with the given source ROM.
    """
    if not rom_info:
        return True, ""
    
    v = get_mp_version(version_id)
    
    # If source is French Vanilla, only French Multiplayer is supported
    if rom_info.lang == "fr" and v["id"] != "fr":
        return False, "badge_incompatible_vanilla_fr"

    # If source is USA Vanilla, check Rev 1
    if rom_info.lang == "en":
        if rom_info.game_code == "CPUE" and not getattr(rom_info, "is_usa_rev1", True):
            return False, "badge_requires_usa_rev1"

    if rom_info.lang not in v.get("supported_rom_langs", ["fr", "en"]):
        return False, "badge_incompatible_lang"

    return True, ""

def get_addon_definition(addon_id):
    for a in ADDONS_REGISTRY:
        if a["id"] == addon_id:
            return a
    return None

def is_addon_variant_supported(addon_id, variant_id, effective_mp_lang):
    """
    Checks if an addon variant matches the selected multiplayer language.
    """
    addon = get_addon_definition(addon_id)
    if not addon:
        return True, ""

    if addon.get("requires_multiplayer", False) and not effective_mp_lang:
        return False, "badge_incompatible_req_mp"

    for v in addon["variants"]:
        if v["id"] == variant_id:
            if effective_mp_lang and v["lang"] != effective_mp_lang:
                return False, "badge_incompatible_lang"
            return True, ""

    return False, "badge_incompatible_lang"
