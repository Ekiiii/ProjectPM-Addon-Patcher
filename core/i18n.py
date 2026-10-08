# -*- coding: utf-8 -*-
"""
i18n.py
Bilingual dictionary for ProjectPM Addon Patcher.
Default language is English, switchable to French.
"""

LANGUAGES = {
    "en": "English",
    "fr": "Français"
}

TRANSLATIONS = {
    "app_title": {
        "en": "ProjectPM Addon Patcher",
        "fr": "ProjectPM Addon Patcher"
    },
    "app_subtitle": {
        "en": "Community Mod & Addon Manager for Pokémon Platinum",
        "fr": "Gestionnaire de Mods & Addons pour Pokémon Platine"
    },
    "header_version": {
        "en": "v1.0.0",
        "fr": "v1.0.0"
    },
    "section_rom": {
        "en": "1. SELECT YOUR ROM",
        "fr": "1. SÉLECTIONNEZ VOTRE ROM"
    },
    "rom_browse": {
        "en": "Browse...",
        "fr": "Parcourir..."
    },
    "rom_placeholder": {
        "en": "Select or drag & drop your ProjectPM.nds or Vanilla Platinum ROM...",
        "fr": "Sélectionnez ou glissez-déposez votre ROM ProjectPM.nds ou Platine Vanilla..."
    },
    "rom_detecting": {
        "en": "Analyzing ROM...",
        "fr": "Analyse de la ROM en cours..."
    },
    "rom_valid_fr": {
        "en": "ProjectPM 0.4.5 (French) Detected",
        "fr": "ProjectPM 0.4.5 (Français) Détecté"
    },
    "rom_valid_us": {
        "en": "ProjectPM 0.4.5 (English) Detected",
        "fr": "ProjectPM 0.4.5 (Anglais) Détecté"
    },
    "rom_vanilla_fr": {
        "en": "Vanilla Platinum (France) Detected",
        "fr": "Platine Vanilla (France) Détecté"
    },
    "rom_vanilla_us": {
        "en": "Vanilla Platinum (USA Rev 1) Detected",
        "fr": "Platine Vanilla (USA Rev 1) Détecté"
    },
    "rom_unknown": {
        "en": "Unrecognized / Custom ROM",
        "fr": "ROM non reconnue ou personnalisée"
    },
    "section_addons": {
        "en": "2. GAME MODS & ADDONS",
        "fr": "2. MODS DE JEU & ADDONS"
    },
    "addon_soullocke": {
        "en": "Soul Link / SoulLocke Edition",
        "fr": "Édition Soul Link / SoulLocke"
    },
    "addon_soullocke_desc": {
        "en": "Shared fates with partners: synchronized faint/graveyard, 1 shared catch per area, streamer overlay.",
        "fr": "Destins liés : mort partagée, boîte cimetière auto, 1 capture partagée par zone, overlay streamers."
    },
    "addon_restore": {
        "en": "Restore Clean ProjectPM (Remove Addons)",
        "fr": "Restaurer en ProjectPM Classique (Retirer les Addons)"
    },
    "addon_restore_desc": {
        "en": "Removes SoulLocke hooks and reverts to stock multiplayer ROM.",
        "fr": "Nettoie les points d'accroche et remet la ROM multijoueur propre."
    },
    "section_visual": {
        "en": "3. VISUAL+ GRAPHIC OPTIONS",
        "fr": "3. OPTIONS GRAPHIQUES VISUAL+"
    },
    "visual_battle_bg": {
        "en": "Visual+ Battle Backgrounds",
        "fr": "Visual+ Arrière-plans de Combat"
    },
    "visual_battle_bg_desc": {
        "en": "Replaces the battle backgrounds with redrawn, high-detail art.",
        "fr": "Remplace les arrière-plans de combat par des illustrations détaillées en HD."
    },
    "visual_camera": {
        "en": "Visual+ 3D Camera",
        "fr": "Visual+ Caméra 3D"
    },
    "visual_camera_desc": {
        "en": "Moves the overworld camera closer for an enhanced 3D perspective.",
        "fr": "Rapproche la caméra en extérieur pour un effet 3D renforcé."
    },
    "opt_builtin": {
        "en": "Built-in",
        "fr": "Activer"
    },
    "opt_off": {
        "en": "Off",
        "fr": "Désactiver"
    },
    "opt_keep": {
        "en": "Keep As-Is",
        "fr": "Conserver"
    },
    "section_save": {
        "en": "4. SAVE FILE & BACKUPS",
        "fr": "4. SAUVEGARDE & BACKUPS"
    },
    "save_preserve_checkbox": {
        "en": "Automatically backup and preserve companion save file (.dsv)",
        "fr": "Sauvegarder et conserver automatiquement le fichier de sauvegarde (.dsv)"
    },
    "save_detected": {
        "en": "Save file found: %s",
        "fr": "Sauvegarde détectée : %s"
    },
    "save_none": {
        "en": "No existing save file detected next to ROM",
        "fr": "Aucune sauvegarde détectée à côté de la ROM"
    },
    "rand_detected": {
        "en": "Randomization record (.rand.txt) found and protected.",
        "fr": "Fichier de randomisation (.rand.txt) détecté et préservé."
    },
    "btn_apply": {
        "en": "APPLY ADDONS & PATCH",
        "fr": "APPLIQUER LES ADDONS & PATCHER"
    },
    "status_ready": {
        "en": "Ready. Select a ROM to get started.",
        "fr": "Prêt. Sélectionnez une ROM pour commencer."
    },
    "status_patching": {
        "en": "Patching ROM in progress...",
        "fr": "Application des patchs en cours..."
    },
    "status_success": {
        "en": "SUCCESS! Your ROM was successfully updated.",
        "fr": "SUCCÈS ! Votre ROM a été mise à jour avec succès."
    },
    "status_error": {
        "en": "ERROR: Patching failed. Your original ROM was not changed.",
        "fr": "ERREUR : Échec du patchage. Votre ROM n'a pas été modifiée."
    },
    "update_available": {
        "en": "A new version of the patcher (%s) is available on GitHub!",
        "fr": "Une nouvelle version du patcher (%s) est disponible sur GitHub !"
    },
    "update_button": {
        "en": "Download Update",
        "fr": "Télécharger la mise à jour"
    },
    "disclaimer": {
        "en": "Unofficial Community Mod Manager by Ekiiii. Not affiliated with official Project PM team.",
        "fr": "Gestionnaire de Mods communautaire par Ekiiii. Non affilié à l'équipe officielle Project PM."
    }
}

CURRENT_LANG = "en"

def set_lang(lang_code):
    global CURRENT_LANG
    if lang_code in LANGUAGES:
        CURRENT_LANG = lang_code

def get_lang():
    return CURRENT_LANG

def t(key, *args):
    entry = TRANSLATIONS.get(key)
    if not entry:
        return key
    text = entry.get(CURRENT_LANG, entry.get("en", key))
    if args:
        try:
            return text % args
        except Exception:
            return text
    return text
