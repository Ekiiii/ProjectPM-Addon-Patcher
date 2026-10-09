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
        "en": "v1.0.2",
        "fr": "v1.0.2"
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
        "en": "SoulLocke Inactive",
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
        "en": "Enable ProjectPM Multiplayer on your Vanilla ROM and choose a version:",
        "fr": "Activez le Multijoueur ProjectPM sur votre ROM Vanilla et choisissez la version :"
    },
    "mp_enable_checkbox": {
        "en": "Enable ProjectPM Multiplayer",
        "fr": "Activer le Multijoueur ProjectPM"
    },
    "mp_version_btn": {
        "en": "⚙ Version: %s ▾",
        "fr": "⚙ Version : %s ▾"
    },
    "btn_select_lang": {
        "en": "⚙ Select Language ▾",
        "fr": "⚙ Sélectionner la langue ▾"
    },
    "btn_select_version": {
        "en": "⚙ Select Version ▾",
        "fr": "⚙ Sélectionner la version ▾"
    },
    "err_need_select_mp_lang": {
        "en": "Please select a language for ProjectPM Multiplayer before proceeding.",
        "fr": "Veuillez sélectionner une langue pour le Multijoueur ProjectPM avant de continuer."
    },
    "err_need_select_addon_lang": {
        "en": "Please select a language / version for addon: %s",
        "fr": "Veuillez sélectionner une langue / version pour l'addon : %s"
    },
    "dialog_select_prompt": {
        "en": "Please choose an option from the list before confirming.",
        "fr": "Veuillez choisir une option dans la liste avant de confirmer."
    },
    "dialog_mp_title": {
        "en": "Select Multiplayer Version",
        "fr": "Sélectionner la version du Multijoueur"
    },
    "dialog_mp_desc": {
        "en": "Choose the multiplayer language & version to install onto your ROM:",
        "fr": "Choisissez la version linguistique du Multijoueur à installer sur votre ROM :"
    },
    "dialog_confirm": {
        "en": "Confirm",
        "fr": "Confirmer"
    },
    "dialog_cancel": {
        "en": "Cancel",
        "fr": "Annuler"
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
        "en": "3. ADDONS & MODS",
        "fr": "3. ADDONS & MODS"
    },
    "addon_soullocke": {
        "en": "SoulLocke",
        "fr": "SoulLocke"
    },
    "dialog_addon_title": {
        "en": "Configure Addon: %s",
        "fr": "Configuration de l'Addon : %s"
    },
    "dialog_addon_desc": {
        "en": "Select the variant / language for this addon:",
        "fr": "Sélectionnez la variante / langue pour cet addon :"
    },
    "btn_configure": {
        "en": "Configure...",
        "fr": "Configurer..."
    },
    "btn_uninstall_addon": {
        "en": "Uninstall Addon (Revert to Clean)",
        "fr": "Désinstaller l'Addon (Restaurer)"
    },
    "addon_installed_badge": {
        "en": "Installed on ROM",
        "fr": "Installé sur la ROM"
    },
    "addon_version_btn": {
        "en": "⚙ Version: %s ▾",
        "fr": "⚙ Version : %s ▾"
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
        "en": "Shared fate with partner: synchronized faints/graveyard, 1 shared catch per area, streamer overlay.",
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
        "en": "4. VISUAL+ GRAPHICS OPTIONS",
        "fr": "4. OPTIONS GRAPHIQUES VISUAL+"
    },
    "visual_battle_bg": {
        "en": "Visual+ Battle Backgrounds",
        "fr": "Visual+ Arrière-plans de Combat"
    },
    "visual_battle_bg_desc": {
        "en": "Replaces the battle backgrounds with redrawn, high-detail illustrations.",
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
        "en": "Enable",
        "fr": "Activer"
    },
    "opt_off": {
        "en": "Disable",
        "fr": "Désactiver"
    },
    "opt_keep": {
        "en": "Keep As-Is",
        "fr": "Conserver"
    },
    "section_custom_patch": {
        "en": "5. ADDITIONAL XDELTA PATCH (OPTIONAL)",
        "fr": "5. PATCH XDELTA SUPPLÉMENTAIRE (OPTIONNEL)"
    },
    "custom_patch_desc": {
        "en": "Apply an additional custom .xdelta patch onto the final ROM after all other mods are applied:",
        "fr": "Appliquez un patch .xdelta personnalisé supplémentaire sur la ROM finale après tous les autres patchs :"
    },
    "custom_patch_checkbox": {
        "en": "Enable additional custom xDelta patch",
        "fr": "Activer un patch xDelta supplémentaire"
    },
    "custom_patch_browse": {
        "en": "Browse...",
        "fr": "Parcourir..."
    },
    "custom_patch_clear": {
        "en": "Clear",
        "fr": "Effacer"
    },
    "custom_patch_info": {
        "en": "Applied as the final step. Ensure this patch is compatible with the resulting ROM.",
        "fr": "Appliqué en étape finale. Veillez à ce que ce patch corresponde à la ROM résultante."
    },
    "custom_patch_none": {
        "en": "No custom patch selected",
        "fr": "Aucun patch personnalisé sélectionné"
    },
    "section_save": {
        "en": "6. SAVE FILE & BACKUPS",
        "fr": "6. SAUVEGARDE & BACKUPS"
    },
    "save_preserve_checkbox": {
        "en": "Automatically back up and preserve companion save files (.dsv / .sav)",
        "fr": "Sauvegarder et conserver automatiquement les fichiers de sauvegarde (.dsv / .sav)"
    },
    "save_detected": {
        "en": "Save file found: %s",
        "fr": "Sauvegarde détectée : %s"
    },
    "save_none": {
        "en": "No existing save file detected next to ROM (.dsv / .sav)",
        "fr": "Aucune sauvegarde détectée à côté de la ROM (.dsv / .sav)"
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
    "update_btn_auto": {
        "en": "Update Now",
        "fr": "Mettre à jour"
    },
    "update_btn_notes": {
        "en": "Changelog",
        "fr": "Notes de version"
    },
    "update_downloading": {
        "en": "Downloading update... %d%% (%.1f / %.1f MB)",
        "fr": "Téléchargement de la mise à jour... %d%% (%.1f / %.1f Mo)"
    },
    "update_ready_title": {
        "en": "Update Ready",
        "fr": "Mise à jour prête"
    },
    "update_ready_msg": {
        "en": "Version %s has been downloaded successfully.\nThe application will now restart to apply the update.",
        "fr": "La version %s a été téléchargée avec succès.\nL'application va redémarrer pour appliquer la mise à jour."
    },
    "update_err_title": {
        "en": "Update Failed",
        "fr": "Échec de la mise à jour"
    },
    "update_err_msg": {
        "en": "Failed to download update (%s).\nOpening the release page in your browser instead.",
        "fr": "Échec du téléchargement (%s).\nOuverture de la page GitHub dans votre navigateur."
    },
    "update_dev_mode": {
        "en": "Development mode detected (running from Python source).\nAutomatic update is only active for compiled .exe versions.",
        "fr": "Mode développement actif (exécution depuis les sources Python).\nLa mise à jour automatique est réservée aux versions .exe compilées."
    },
    "disclaimer": {
        "en": "Unofficial Community Mod Manager by Ekiii. Not affiliated with the official Project PM team.",
        "fr": "Gestionnaire de Mods communautaire par Ekiii. Non affilié à l'équipe officielle Project PM."
    },
    # --- NAVIGATION & APP ---
    "tab_patcher": {
        "en": "MODS & MULTI",
        "fr": "MODS & MULTI"
    },
    "tab_randomizer": {
        "en": "RANDOMIZER",
        "fr": "RANDOMIZER"
    },
    "tab_saves": {
        "en": "SAVED GAMES",
        "fr": "SAUVEGARDES"
    },
    "tab_about": {
        "en": "OPTIONS & ABOUT",
        "fr": "OPTIONS & INFOS"
    },
    "app_subtitle": {
        "en": "Mods, Multiplayer & Randomizer Manager for Pokémon Platinum",
        "fr": "Gestionnaire de Mods, Multijoueur & Randomizer pour Pokémon Platine"
    },
    # --- SECTION 1: ROM SELECTION ---
    "card_rom_title": {
        "en": "1. SELECT SOURCE ROM & DESTINATION",
        "fr": "1. SÉLECTION DE LA ROM SOURCE & DESTINATION"
    },
    "label_src_rom": {
        "en": "Source ROM (Pokémon Platinum NDS):",
        "fr": "ROM Source (Pokémon Platine NDS) :"
    },
    "label_dst_rom": {
        "en": "Destination ROM (Where to save):",
        "fr": "ROM de destination (Où enregistrer) :"
    },
    "btn_browse_src": {
        "en": "Browse...",
        "fr": "Parcourir..."
    },
    "btn_browse_dst": {
        "en": "Save As...",
        "fr": "Enregistrer sous..."
    },
    # --- SECTION 2: MULTIPLAYER & MODS ---
    "card_mods_title": {
        "en": "2. MULTIPLAYER BASE & GAMEPLAY MODS",
        "fr": "2. BASE MULTI ET MODES DE JEU"
    },
    "label_mp_base": {
        "en": "Project PM Multiplayer Base:",
        "fr": "Base Multijoueur Project PM :"
    },
    "opt_mp_auto": {
        "en": "Automatic Detection (Recommended)",
        "fr": "Détection Automatique (Recommandé)"
    },
    "opt_mp_fr": {
        "en": "Force French Multiplayer (v0.4.5)",
        "fr": "Forcer Project PM Multijoueur Français (v0.4.5)"
    },
    "opt_mp_en": {
        "en": "Force USA Multiplayer (v0.4.5)",
        "fr": "Forcer Project PM Multiplayer USA (v0.4.5)"
    },
    "opt_mp_none": {
        "en": "None (Keep Base ROM)",
        "fr": "Aucun (Garder ROM de base)"
    },
    "help_mp_base": {
        "en": "If your ROM is Vanilla, the multiplayer patch will be applied automatically.",
        "fr": "Si votre ROM est une version originale (Vanilla), le patch multijoueur sera appliqué automatiquement."
    },
    "label_addon_mode": {
        "en": "Additional Gameplay Mode:",
        "fr": "Mode de Jeu Additionnel :"
    },
    "addon_standard_title": {
        "en": "Standard / Official",
        "fr": "Standard / Officiel"
    },
    "addon_standard_desc": {
        "en": "Classic Project PM multiplayer experience without restrictions.",
        "fr": "Expérience multijoueur Project PM classique sans règles restrictives."
    },
    "addon_soullink_title": {
        "en": "Soul Link & SoulLocke",
        "fr": "Soul Link & SoulLocke"
    },
    "addon_soullink_desc": {
        "en": "Linked souls: shared deaths, 1 catch per area, automatic graveyard box.",
        "fr": "Âmes liées entre joueurs : mort partagée, capture unique par zone, cimetière automatique."
    },
    "addon_restore_title": {
        "en": "Restore Clean ROM",
        "fr": "Restaurer ROM Propre"
    },
    "addon_restore_desc": {
        "en": "Uninstalls SoulLocke mod and restores clean multiplayer ROM.",
        "fr": "Désinstalle le mod SoulLocke et restaure la ROM multijoueur propre."
    },
    # --- SECTION 3: VISUAL+ & PREVIEWS ---
    "card_visual_title": {
        "en": "3. GRAPHICS & ENHANCEMENTS (VISUAL+)",
        "fr": "3. GRAPHISMES & CONFORT (VISUAL+)"
    },
    "visual_bg_title": {
        "en": "HD Battle Backgrounds (Visual+)",
        "fr": "Décors de combat HD (Visual+)"
    },
    "visual_bg_desc": {
        "en": "Replaces 2D battle arenas with high-detail 3D textured scenery.",
        "fr": "Remplace les arènes de combat 2D pixelisées par des décors 3D texturés fidèles."
    },
    "visual_bg_caption": {
        "en": "Preview: High-resolution 3D battle arena",
        "fr": "Aperçu : Arène de combat 3D en haute résolution"
    },
    "visual_cam_title": {
        "en": "Extended 3D Camera (Visual+)",
        "fr": "Caméra 3D Élargie (Visual+)"
    },
    "visual_cam_desc": {
        "en": "Closer overworld camera angle in towns and routes for stronger 3D depth.",
        "fr": "Angle de vue optimisé dans les villes et les routes pour une meilleure immersion."
    },
    "visual_cam_town": {
        "en": "Overworld / Town",
        "fr": "Vue Extérieure / Ville"
    },
    "visual_cam_center": {
        "en": "Pokémon Center",
        "fr": "Centre Pokémon"
    },
    "backup_title": {
        "en": "Automatic Save Backup (.sav / .dsv)",
        "fr": "Sauvegarde Automatique (.sav / .dsv)"
    },
    "backup_desc": {
        "en": "Keeps a timestamped backup copy of your save data before patching.",
        "fr": "Conserve une copie de sécurité horodatée de vos données de sauvegarde avant patch."
    },
    "btn_execute_patch": {
        "en": "APPLY PATCHES & MODS",
        "fr": "APPLIQUER LES PATCHS & MODS"
    },
    # --- SECTION 4: RANDOMIZER TAB ---
    "rand_rom_title": {
        "en": "1. ROM TO RANDOMIZE",
        "fr": "1. ROM À RANDOMISER"
    },
    "rand_label_src": {
        "en": "Target ROM (Patched Project PM or Vanilla):",
        "fr": "ROM Cible (Project PM patchée ou Vanilla) :"
    },
    "rand_label_dst": {
        "en": "Destination ROM (Where to save):",
        "fr": "ROM de destination (Où enregistrer) :"
    },
    "rand_world_col_title": {
        "en": "YOUR WORLD (INDIVIDUAL & ADVENTURE)",
        "fr": "VOTRE MONDE (INDIVIDUEL & AVENTURE)"
    },
    "rand_world_col_desc": {
        "en": "These options customize your personal world. Sharing the World Code is optional.",
        "fr": "Ces options personnalisent votre monde. Le partage du Code Monde est optionnel."
    },
    "rand_coop_col_title": {
        "en": "CO-OP MODE (MULTIPLAYER SYNC)",
        "fr": "MODE CO-OP (SYNCHRONISATION MULTIJOUEUR)"
    },
    "rand_coop_alert": {
        "en": "CRITICAL MULTIPLAYER RULE: This code MUST match exactly across all players who battle together to prevent desyncs in double and gym battles.",
        "fr": "RÈGLE MULTIJOUEUR CRITIQUE : Ce code DOIT être strictement identique entre tous les joueurs qui combattent ensemble pour éviter les désynchronisations en combat double ou en arène."
    },
    # World categories
    "rand_cat_wilds": {
        "en": "Wild Encounters (187 Sinnoh Areas)",
        "fr": "Rencontres Sauvages (187 zones de Sinnoh)"
    },
    "rand_cat_wilds_desc": {
        "en": "Modifies tall grass, surfing, fishing, and radar encounters.",
        "fr": "Modifie les hautes herbes, surf, pêche et rencontres radar."
    },
    "rand_cat_starters": {
        "en": "Briefcase Starter Trio",
        "fr": "Trio de Starters dans la Valise"
    },
    "rand_starters_evolving": {
        "en": "Evolving Starters Only (3-stage families - Recommended)",
        "fr": "Starters évolutifs uniquement (Familles à 3 stades - Recommandé)"
    },
    "rand_starters_any": {
        "en": "Completely Random (Any basic Pokémon)",
        "fr": "Totalement aléatoire (Tout Pokémon niveau de base)"
    },
    "rand_starters_vanilla": {
        "en": "Vanilla Starters (Turtwig, Chimchar, Piplup)",
        "fr": "Starters Vanilla (Tortipouss, Ouisticram, Tiplouf)"
    },
    "rand_starter_slot_left": {
        "en": "LEFT STARTER",
        "fr": "STARTER GAUCHE"
    },
    "rand_starter_slot_mid": {
        "en": "MIDDLE STARTER",
        "fr": "STARTER MILIEU"
    },
    "rand_starter_slot_right": {
        "en": "RIGHT STARTER",
        "fr": "STARTER DROITE"
    },
    "rand_cat_honey_eggs": {
        "en": "Honey Trees & Gift Eggs",
        "fr": "Arbres à Miel & Œufs Offerts"
    },
    "rand_cat_statics": {
        "en": "Static & Legendary Encounters",
        "fr": "Rencontres Fixes & Légendaires"
    },
    "rand_cat_special": {
        "en": "Special Wild Encounters (Feebas, Marsh...)",
        "fr": "Rencontres Sauvages Spéciales (Barpau, Grand Marais...)"
    },
    "rand_cat_gba": {
        "en": "GBA Dual-Slot Encounters",
        "fr": "Rencontres Cartouches GBA insérées"
    },
    "rand_cat_gifts": {
        "en": "NPC Gift Pokémon (Eevee, Porygon...)",
        "fr": "Pokémon Cadeaux des PNJ (Évoli, Porygon...)"
    },
    "rand_cat_trades": {
        "en": "In-Game NPC Trades",
        "fr": "Échanges Internes avec les PNJ"
    },
    # Wild options
    "rand_wild_opts_title": {
        "en": "Wild Encounter Options",
        "fr": "Options des Rencontres Sauvages"
    },
    "rand_mode_label": {
        "en": "Replacement Mode:",
        "fr": "Mode de substitution :"
    },
    "rand_mode_area": {
        "en": "Area 1-to-1 (Coherent species per zone - Recommended)",
        "fr": "Zone 1-pour-1 (Équivalence cohérente par zone - Recommandé)"
    },
    "rand_mode_global": {
        "en": "Global 1-to-1 (One species replaces another everywhere)",
        "fr": "Global 1-pour-1 (Une espèce remplace une espèce dans tout Sinnoh)"
    },
    "rand_mode_random": {
        "en": "Completely Random (Each slot rolled independently)",
        "fr": "Totalement Aléatoire (Chaque slot est indépendant)"
    },
    "rand_rule_label": {
        "en": "Strength Rule:",
        "fr": "Règle de force :"
    },
    "rand_rule_similar": {
        "en": "Similar Strength (BST ±15% - Balanced)",
        "fr": "Force Similaire (BST ±15% - Équilibré)"
    },
    "rand_rule_type": {
        "en": "Type Theme (Keep element affinity)",
        "fr": "Thème par Type (Conserver affinité élémentaire)"
    },
    "rand_rule_none": {
        "en": "None (Completely unconstrained)",
        "fr": "Aucune (Totalement libre)"
    },
    "rand_noleg": {
        "en": "No Legendaries in the wild (Excludes 35 Legendaries)",
        "fr": "Exclure les 35 Pokémon Légendaires de la nature"
    },
    # ROM Tweaks
    "rand_tweaks_title": {
        "en": "ROM Tweaks",
        "fr": "Ajustements ROM"
    },
    "rand_shiny_label": {
        "en": "Shiny Encounter Odds:",
        "fr": "Taux d'apparition des Shiny :"
    },
    # World Seed & Code
    "rand_world_seed_title": {
        "en": "Your World Seed & Code",
        "fr": "Graine & Code Monde"
    },
    "rand_world_seed_desc": {
        "en": "This code is OPTIONAL to share. Import a friend's only if you want an identical world.",
        "fr": "Ce code est OPTIONNEL à partager. Importez le code d'un ami uniquement si vous voulez un monde identique."
    },
    "rand_world_seed_label": {
        "en": "World Seed:",
        "fr": "Graine Monde :"
    },
    "rand_world_code_label": {
        "en": "World Code:",
        "fr": "Code Monde :"
    },
    # Co-Op categories
    "rand_coop_categories_title": {
        "en": "Synchronized Co-Op Features",
        "fr": "Fonctionnalités Co-Op Synchronisées"
    },
    "rand_trainers": {
        "en": "Trainer Teams (973 battles)",
        "fr": "Équipes des Dresseurs & Champions (973 combats)"
    },
    "rand_trainers_simstr": {
        "en": "Similar Strength (Trainer Teams)",
        "fr": "Force Similaire (Équipes de Dresseurs)"
    },
    "rand_trainers_noleg": {
        "en": "No Legendaries (Trainer Teams)",
        "fr": "Exclure les Légendaires (Dresseurs)"
    },
    "rand_types": {
        "en": "Pokémon Types",
        "fr": "Types Élémentaires des Pokémon"
    },
    "rand_types_desc": {
        "en": "Rerolls types for all 493 Pokémon (Dual types preserved).",
        "fr": "Reroll les types élémentaires (double-types cohérents)."
    },
    "rand_abilities": {
        "en": "Abilities",
        "fr": "Talents des Pokémon (Abilities)"
    },
    "rand_abilities_desc": {
        "en": "Rerolls passive abilities among all species.",
        "fr": "Reroll les 123 talents passifs parmi les Pokémon."
    },
    "rand_movesets": {
        "en": "Movesets (Learned by Level)",
        "fr": "Attaques apprises par Niveau (Movesets)"
    },
    "rand_movesets_desc": {
        "en": "Rerolls moves learned while leveling up.",
        "fr": "Reroll les attaques apprises tout en conservant les paliers."
    },
    # Co-Op Seed & Code
    "rand_coop_seed_title": {
        "en": "Co-Op Seed & Code",
        "fr": "Graine & Code Co-Op"
    },
    "rand_coop_seed_desc": {
        "en": "Everyone who battles together MUST import this exact same code.",
        "fr": "Tous ceux qui jouent ensemble DOIVENT importer exactement ce même code."
    },
    "rand_coop_seed_label": {
        "en": "Co-Op Seed:",
        "fr": "Graine Co-Op :"
    },
    "rand_coop_code_label": {
        "en": "Co-Op Code:",
        "fr": "Code Co-Op :"
    },
    # Buttons
    "btn_roll_seed": {
        "en": "Roll New Seed",
        "fr": "Nouveau tirage"
    },
    "btn_copy_code": {
        "en": "Copy",
        "fr": "Copier"
    },
    "btn_paste_code": {
        "en": "Paste Friend's Code",
        "fr": "Coller le code d'un ami"
    },
    "btn_execute_randomize": {
        "en": "RANDOMIZE ROM",
        "fr": "RANDOMISER LA ROM"
    },
    # Badges & Statuses
    "badge_clean_platine": {
        "en": "Clean Platinum ROM",
        "fr": "ROM Platine Propre"
    },
    "badge_already_rand": {
        "en": "Already Randomized",
        "fr": "Déjà Randomisée"
    },
    "badge_ready": {
        "en": "Ready",
        "fr": "Prêt"
    },
    # Terminal & Action Keys
    "custom_patch_label": {
        "en": "Additional xDelta patch (Optional):",
        "fr": "Patch xDelta additionnel (Optionnel) :"
    },
    "custom_patch_placeholder": {
        "en": "Select an external .xdelta patch...",
        "fr": "Sélectionnez un patch .xdelta externe..."
    },
    "terminal_progress": {
        "en": "PROGRESS CONSOLE",
        "fr": "CONSOLE DE PROGRESSION"
    },
    "terminal_rand_report": {
        "en": "RANDOMIZATION REPORT",
        "fr": "RAPPORT DE RANDOMISATION"
    },
    "terminal_status_ready": {
        "en": "Ready",
        "fr": "Prêt"
    },
    "btn_clear": {
        "en": "Clear",
        "fr": "Vider"
    },
    # Saves & Backups Tab
    "saves_title": {
        "en": "AUTOMATIC SAVE BACKUP MANAGER",
        "fr": "GESTIONNAIRE DE SAUVEGARDES AUTOMATIQUES"
    },
    "saves_desc": {
        "en": "When you apply a patch or modify your ROM, the patcher automatically backs up and syncs your companion .sav and .dsv files (melonDS / DeSmuME) to prevent any loss of progress.",
        "fr": "Lorsque vous appliquez un patch ou modifiez votre ROM, le patcher sauvegarde et synchronise automatiquement vos fichiers .sav et .dsv (melonDS / DeSmuME) pour éviter toute perte de progression."
    },
    "saves_folder_label": {
        "en": "Backups location:",
        "fr": "Emplacement des sauvegardes :"
    },
    "btn_open_folder": {
        "en": "Open Folder",
        "fr": "Ouvrir le dossier"
    },
    # About Tab
    "about_title": {
        "en": "ABOUT PROJECT PM ADDON PATCHER",
        "fr": "À PROPOS DE PROJECT PM ADDON PATCHER"
    },
    "about_app_name": {
        "en": "Project PM Addon Patcher & Randomizer",
        "fr": "Project PM Addon Patcher & Randomizer"
    },
    "about_desc": {
        "en": "All-in-one suite for the Pokémon Platinum community: Co-op Multiplayer, Soul Link / SoulLocke Mod, Visual+ enhancements, and high-compatibility randomizer engine.",
        "fr": "Outil tout-en-un pour la communauté Pokémon Platine : Multijoueur coopératif, Mod Soul Link / SoulLocke, Améliorations visuelles Visual+, et moteur de randomisation haute compatibilité."
    },
    "about_credits": {
        "en": "Developed with passion by <strong>Ekiii</strong>",
        "fr": "Développé avec passion par <strong>Ekiii</strong>"
    },
    "btn_check_updates": {
        "en": "Check for Updates",
        "fr": "Vérifier les mises à jour"
    },
    "btn_github": {
        "en": "Official GitHub",
        "fr": "GitHub Officiel"
    },
    # Footer
    "footer_status_ready": {
        "en": "Ready to patch",
        "fr": "Prêt à patcher"
    },
    "footer_community": {
        "en": "Project PM Platinum Community",
        "fr": "Communauté Project PM Platine"
    }
}

CURRENT_LANG = "fr"

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
