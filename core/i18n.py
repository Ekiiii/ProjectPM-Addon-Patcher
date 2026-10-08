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
        "en": "1. SELECT YOUR ROM & DESTINATION",
        "fr": "1. SÉLECTION DE LA ROM & DESTINATION"
    },
    "rom_input_label": {
        "en": "Source ROM:",
        "fr": "ROM Source :"
    },
    "rom_output_label": {
        "en": "Destination ROM (Where to save):",
        "fr": "ROM de destination (Emplacement d'enregistrement) :"
    },
    "rom_browse": {
        "en": "Browse...",
        "fr": "Parcourir..."
    },
    "rom_output_browse": {
        "en": "Save As...",
        "fr": "Enregistrer sous..."
    },
    "rom_placeholder": {
        "en": "Select or drag & drop your ProjectPM.nds or Vanilla Platinum ROM...",
        "fr": "Sélectionnez ou glissez-déposez votre ROM ProjectPM.nds ou Platine Vanilla..."
    },
    "rom_detecting": {
        "en": "Analyzing ROM...",
        "fr": "Analyse de la ROM en cours..."
    },
    "badge_mp_active_fr": {
        "en": "ProjectPM 0.4.5 (FR) Active",
        "fr": "ProjectPM 0.4.5 (FR) Actif"
    },
    "badge_mp_active_en": {
        "en": "ProjectPM 0.4.5 (EN) Active",
        "fr": "ProjectPM 0.4.5 (EN) Actif"
    },
    "badge_mp_none": {
        "en": "Vanilla ROM (No Multiplayer)",
        "fr": "ROM Vanilla (Sans Multijoueur)"
    },
    "badge_sl_active": {
        "en": "SoulLocke Active",
        "fr": "SoulLocke Actif"
    },
    "badge_sl_none": {
        "en": "No SoulLocke",
        "fr": "SoulLocke Inactif"
    },
    "badge_rand_yes": {
        "en": "Randomized ROM",
        "fr": "ROM Randomisée"
    },
    "badge_rand_no": {
        "en": "Standard Encounters",
        "fr": "Rencontres Standard"
    },
    "badge_vbg_yes": {
        "en": "Visual+ BG: Active",
        "fr": "Visual+ BG : Actif"
    },
    "badge_vcam_yes": {
        "en": "Visual+ Cam: Active",
        "fr": "Visual+ Cam : Actif"
    },
    "badge_already_installed": {
        "en": "Already Installed on ROM",
        "fr": "Déjà installé sur la ROM"
    },
    "badge_incompatible_req_mp": {
        "en": "Requires ProjectPM Multiplayer",
        "fr": "Nécessite le multijoueur ProjectPM"
    },
    "badge_incompatible_lang": {
        "en": "Incompatible with chosen Multiplayer",
        "fr": "Incompatible avec le Multijoueur choisi"
    },
    "badge_incompatible_vanilla_fr": {
        "en": "Incompatible with Platinum FR",
        "fr": "Incompatible avec Platine France"
    },
    "badge_incompatible_vanilla_us": {
        "en": "Incompatible with Platinum USA",
        "fr": "Incompatible avec Platine USA"
    },
    "badge_requires_usa_rev1": {
        "en": "Requires Platinum USA Rev 1",
        "fr": "Nécessite Platine USA Rev 1"
    },
    "badge_requires_france": {
        "en": "Requires Platinum France",
        "fr": "Nécessite Platine France"
    },
    "section_multiplayer": {
        "en": "2. MULTIPLAYER BASE (PROJECT PM)",
        "fr": "2. BASE MULTIJOUEUR (PROJECT PM)"
    },
    "mp_installed_desc": {
        "en": "ProjectPM Multiplayer is already embedded on this ROM (Selection locked).",
        "fr": "Le multijoueur ProjectPM est déjà intégré à cette ROM (Sélection verrouillée)."
    },
    "mp_vanilla_desc": {
        "en": "Select which Multiplayer version to install onto your Vanilla ROM:",
        "fr": "Sélectionnez quelle version Multijoueur installer sur votre ROM Vanilla :"
    },
    "mp_opt_keep_vanilla": {
        "en": "None (Keep Vanilla ROM)",
        "fr": "Aucun (Conserver la ROM Vanilla)"
    },
    "mp_opt_fr": {
        "en": "ProjectPM Multiplayer 0.4.5 (Français)",
        "fr": "ProjectPM Multijoueur 0.4.5 (Français)"
    },
    "mp_opt_en": {
        "en": "ProjectPM Multiplayer 0.4.5 (English)",
        "fr": "ProjectPM Multijoueur 0.4.5 (Anglais)"
    },
    "section_addons": {
        "en": "3. SOULLOCKE ADDON",
        "fr": "3. ADDON SOULLOCKE"
    },
    "addon_soullocke_fr": {
        "en": "SoulLocke Edition (Français)",
        "fr": "Édition SoulLocke (Français)"
    },
    "addon_soullocke_en": {
        "en": "SoulLocke Edition (English)",
        "fr": "Édition SoulLocke (English)"
    },
    "addon_soullocke_desc": {
        "en": "Shared fates with partners: synchronized faint/graveyard, 1 shared catch per area, streamer overlay.",
        "fr": "Destins liés : mort partagée, boîte cimetière auto, 1 capture partagée par zone, overlay streamers."
    },
    "addon_none": {
        "en": "None / Do not add",
        "fr": "Aucun / Ne pas ajouter"
    },
    "addon_restore": {
        "en": "Restore Clean ProjectPM (Uninstall SoulLocke)",
        "fr": "Restaurer en ProjectPM Classique (Retirer SoulLocke)"
    },
    "addon_restore_desc": {
        "en": "Reverts to stock multiplayer ROM, removes SoulLocke hooks.",
        "fr": "Remet la ROM multijoueur propre, retire les hooks SoulLocke."
    },
    "section_visual": {
        "en": "4. VISUAL+ GRAPHIC OPTIONS",
        "fr": "4. OPTIONS GRAPHIQUES VISUAL+"
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
        "en": "Activate",
        "fr": "Activer"
    },
    "opt_off": {
        "en": "Deactivate",
        "fr": "Désactiver"
    },
    "opt_keep": {
        "en": "Keep As-Is",
        "fr": "Conserver"
    },
    "section_save": {
        "en": "5. SAVE FILE & BACKUPS",
        "fr": "5. SAUVEGARDE & BACKUPS"
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
