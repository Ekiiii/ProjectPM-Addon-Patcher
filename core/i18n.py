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
    "badge_exp_share_yes": {
        "en": "Shared EXP: Active",
        "fr": "Multi Exp : Actif"
    },
    "badge_exp_share_no": {
        "en": "Shared EXP: Inactive",
        "fr": "Multi Exp : Inactif"
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
        "en": "Version: %s ▾",
        "fr": "Version : %s ▾"
    },
    "btn_select_lang": {
        "en": "Select Language ▾",
        "fr": "Sélectionner la langue ▾"
    },
    "btn_select_version": {
        "en": "Select Version ▾",
        "fr": "Sélectionner la version ▾"
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
        "en": "Version: %s ▾",
        "fr": "Version : %s ▾"
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
        "en": "Uninstall SoulLocke",
        "fr": "Désinstaller le SoulLocke"
    },
    "addon_restore_desc": {
        "en": "Uninstalls the SoulLocke mod and restores the clean multiplayer ROM.",
        "fr": "Désinstalle le mod SoulLocke et restaure la ROM multijoueur propre."
    },
    "exp_share_title": {
        "en": "Shared Team EXP (Gen 6+ Style)",
        "fr": "Multi Exp d'Équipe (Style Gen 6+)"
    },
    "exp_share_desc": {
        "en": "Distributes battle experience to all Pokémon in your party (the active battler earns a higher share while non-combatants receive partial EXP).",
        "fr": "Partage l'expérience de combat avec toute l'équipe (le Pokémon au combat reçoit la part principale et les remplaçants reçoivent une part d'appoint)."
    },
    "exp_share_badge": {
        "en": "EXP ALL",
        "fr": "MULTI EXP"
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
        "fr": "2. BASE MULTIJOUEUR & MODES DE JEU"
    },
    "label_mp_base": {
        "en": "Project PM Multiplayer Language (Required Base):",
        "fr": "Langue du Multijoueur Project PM (Base obligatoire) :"
    },
    "opt_mp_fr": {
        "en": "Project PM French Multiplayer (v0.4.5)",
        "fr": "Project PM Multijoueur Français (v0.4.5)"
    },
    "opt_mp_en": {
        "en": "Project PM USA / English Multiplayer (v0.4.5)",
        "fr": "Project PM Multijoueur USA / Anglais (v0.4.5)"
    },
    "opt_mp_none": {
        "en": "None (Keep Vanilla ROM without multiplayer)",
        "fr": "Aucun (Conserver la ROM Vanilla sans multijoueur)"
    },
    "help_mp_base": {
        "en": "The multiplayer language selected here automatically defines the language of the SoulLocke mod.",
        "fr": "La langue du multijoueur choisie ici définit automatiquement la langue du mod SoulLocke."
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
        "en": "SoulLocke",
        "fr": "SoulLocke"
    },
    "addon_soullink_desc": {
        "en": "Linked souls between players (shared death, 1 encounter/zone, automatic graveyard).",
        "fr": "Âmes liées entre joueurs (mort partagée, capture unique par zone, cimetière automatique)."
    },
    "addon_restore_title": {
        "en": "Uninstall SoulLocke",
        "fr": "Désinstaller le SoulLocke"
    },
    "addon_restore_desc": {
        "en": "Uninstalls the SoulLocke mod and restores the clean multiplayer ROM.",
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
    "label_overwrite_source": {
        "en": "Overwrite source ROM directly (In-place update)",
        "fr": "Écraser la ROM source directement (Mise à jour sur place)"
    },
    "label_overwrite_source_desc": {
        "en": "Updates your current ROM directly without creating an extra file. Backups are automatically preserved in PMBackups.",
        "fr": "Met à jour directement votre ROM actuelle sans créer de doublon. Vos sauvegardes sont automatiquement protégées dans PMBackups."
    },
    "btn_execute_update_rom": {
        "en": "UPDATE ROM IN-PLACE",
        "fr": "METTRE À JOUR LA ROM SUR PLACE"
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
    "btn_logs": {
        "en": "Logs",
        "fr": "Logs"
    },
    "btn_open_logs": {
        "en": "Open Logs",
        "fr": "Ouvrir les Logs"
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
    # Window controls & Placeholders
    "win_minimize": {
        "en": "Minimize",
        "fr": "Réduire"
    },
    "win_maximize": {
        "en": "Maximize / Restore",
        "fr": "Agrandir / Restaurer"
    },
    "win_close": {
        "en": "Close",
        "fr": "Fermer"
    },
    "dest_rom_placeholder": {
        "en": "Path to output patched ROM...",
        "fr": "Chemin du fichier patché..."
    },
    "rand_src_placeholder": {
        "en": "Select ROM to randomize...",
        "fr": "Sélectionnez la ROM à randomiser..."
    },
    "seed_placeholder": {
        "en": "Numeric seed...",
        "fr": "Graine numérique..."
    },
    "code_placeholder": {
        "en": "Share code...",
        "fr": "Code de partage..."
    },
    "err_file_not_found": {
        "en": "File not found",
        "fr": "Fichier introuvable"
    },
    "err_invalid_rom": {
        "en": "This file is not a valid Pokémon Platinum ROM.",
        "fr": "Ce fichier n'est pas une ROM Pokémon Platine valide."
    },
    "err_patching_in_progress": {
        "en": "A patch operation is already in progress.",
        "fr": "Un processus de patch est déjà en cours."
    },
    "err_randomizing_in_progress": {
        "en": "A randomization process is already in progress.",
        "fr": "Une randomisation est déjà en cours."
    },
    "badge_platine_fr": {
        "en": "Pokémon Platinum (France)",
        "fr": "Pokémon Platine (France)"
    },
    "badge_platine_us": {
        "en": "Pokémon Platinum (USA)",
        "fr": "Pokémon Platine (USA)"
    },
    # Progress & Console Messages
    "progress_analyzing": {
        "en": "Analyzing source ROM...",
        "fr": "Analyse de la ROM source..."
    },
    "progress_extract_rand": {
        "en": "Extracting and preserving randomized tables...",
        "fr": "Extraction et préservation des tables randomisées..."
    },
    "progress_convert_mp": {
        "en": "Converting Vanilla ROM to ProjectPM Multiplayer (%s)...",
        "fr": "Conversion de la ROM Vanilla vers ProjectPM Multijoueur (%s)..."
    },
    "progress_switch_mp": {
        "en": "Switching ProjectPM Multiplayer language (%s -> %s)...",
        "fr": "Changement de langue du multijoueur ProjectPM (%s -> %s)..."
    },
    "progress_refresh_mp": {
        "en": "Refreshing ProjectPM Multiplayer components (%s)...",
        "fr": "Actualisation des composants Multijoueur ProjectPM (%s)..."
    },
    "progress_inplace_replace": {
        "en": "Applying in-place update directly to source ROM...",
        "fr": "Application atomique de la mise à jour sur la ROM source..."
    },
    "mp_detect_switch": {
        "en": "Multiplayer detected: ProjectPM v%s (%s) → Switching to %s",
        "fr": "Multijoueur détecté : ProjectPM v%s (%s) → Changement vers %s"
    },
    "mp_detect_update": {
        "en": "ProjectPM ROM detected (%s) → Ready to update / refresh",
        "fr": "ROM ProjectPM détectée (%s) → Prête pour mise à jour / réactualisation"
    },
    "rand_reapply_notice": {
        "en": "Randomization detected: tables will be automatically preserved and re-applied at the end.",
        "fr": "Randomisation détectée : les tables seront automatiquement préservées et ré-appliquées à la fin."
    },
    "progress_save_backup": {
        "en": "Backing up and synchronizing .sav / .dsv saves...",
        "fr": "Sauvegarde et synchronisation des fichiers .sav / .dsv..."
    },
    "progress_apply_soullocke": {
        "en": "Applying SoulLink / SoulLocke mod...",
        "fr": "Application du mod SoulLink / SoulLocke..."
    },
    "progress_restore_projectpm": {
        "en": "Restoring clean stock ProjectPM...",
        "fr": "Restauration vers ProjectPM d'origine..."
    },
    "progress_apply_visual_bg": {
        "en": "Applying Visual+ HD Battle Backgrounds...",
        "fr": "Application des décors de combat Visual+..."
    },
    "progress_disable_visual_bg": {
        "en": "Disabling Visual+ Battle Backgrounds...",
        "fr": "Désactivation des décors de combat Visual+..."
    },
    "progress_apply_visual_cam": {
        "en": "Applying Visual+ 3D Camera...",
        "fr": "Application de la caméra 3D élargie Visual+..."
    },
    "progress_restore_visual_cam": {
        "en": "Restoring default camera...",
        "fr": "Restauration de la caméra par défaut..."
    },
    "progress_restore_rand": {
        "en": "Reinjecting randomized tables into final ROM...",
        "fr": "Réinjection des tables randomisées sur la ROM finale..."
    },
    "progress_apply_custom": {
        "en": "Applying custom patch: %s...",
        "fr": "Application du patch personnalisé : %s..."
    },
    "progress_running_rand": {
        "en": "Randomizing Pokémon encounters and rules...",
        "fr": "Randomisation des rencontres et des règles en cours..."
    },
    "err_rand_failed": {
        "en": "Failed to randomize ROM.",
        "fr": "Échec lors de la randomisation de la ROM."
    },
    "progress_success": {
        "en": "Patch applied successfully!",
        "fr": "Patch terminé avec succès !"
    },
    # Integrated Randomizer & Wizard
    "card_rand_title": {
        "en": "4. INTEGRATED RANDOMIZER (OPTIONAL)",
        "fr": "4. RANDOMIZER INTÉGRÉ (OPTIONNEL)"
    },
    "rand_enable_label": {
        "en": "Enable Randomizer on this ROM",
        "fr": "Activer le Randomizer sur cette ROM"
    },
    "rand_enable_desc": {
        "en": "Randomizes wild encounters, starters, trainers and co-op rules during the patching process.",
        "fr": "Randomise les rencontres sauvages, les starters, les dresseurs et les règles co-op lors de l'application."
    },
    "rand_badge_active": {
        "en": "Randomizer Active",
        "fr": "Randomizer Activé"
    },
    "rand_badge_disabled": {
        "en": "Disabled",
        "fr": "Désactivé"
    },
    "rand_btn_wizard": {
        "en": "Configurator...",
        "fr": "Configurateur..."
    },
    "rand_btn_codes": {
        "en": "Import Friend Codes",
        "fr": "Importer des Codes Ami"
    },
    "rand_summary_title": {
        "en": "Current Configuration:",
        "fr": "Configuration actuelle :"
    },
    "rand_code_coop_label": {
        "en": "Co-op Code (Give to friends):",
        "fr": "Code Co-op (À donner à vos amis) :"
    },
    "rand_code_world_label": {
        "en": "World Code (Personal):",
        "fr": "Code Monde (Personnel) :"
    },
    "rand_modal_title": {
        "en": "SINNOH RANDOMIZER CONFIGURATOR",
        "fr": "CONFIGURATEUR RANDOMIZER SINNOH"
    },
    "rand_modal_tab_wizard": {
        "en": "Step-by-Step Configurator",
        "fr": "Configurateur Pas-à-Pas"
    },
    "rand_modal_tab_codes": {
        "en": "Direct Code Import",
        "fr": "Saisie Directe de Codes"
    },
    "wiz_badge_wilds": {
        "en": "WILD ENCOUNTERS",
        "fr": "RENCONTRES SAUVAGES"
    },
    "wiz_badge_starters": {
        "en": "STARTERS & SHINY",
        "fr": "STARTERS & SHINY"
    },
    "wiz_badge_events": {
        "en": "WORLD EVENTS",
        "fr": "ÉVÉNEMENTS DU MONDE"
    },
    "wiz_badge_evolutions": {
        "en": "POKÉMON EVOLUTIONS",
        "fr": "ÉVOLUTIONS DES POKÉMON"
    },
    "wiz_badge_coop": {
        "en": "TRAINERS & CO-OP",
        "fr": "DRESSEURS & CO-OP"
    },
    "wiz_badge_summary": {
        "en": "SUMMARY & CODES",
        "fr": "RÉSUMÉ & CODES"
    },
    "wiz_counter_prefix": {
        "en": "Question",
        "fr": "Question"
    },
    "wiz_counter_of": {
        "en": "of",
        "fr": "sur"
    },
    "wiz_q1_title": {
        "en": "1. Randomize wild encounters?",
        "fr": "1. Randomiser les Pokémon sauvages ?"
    },
    "wiz_q1_desc": {
        "en": "Applies random species to tall grass, surfing, and fishing spots across Sinnoh.",
        "fr": "Modifie les Pokémon apparaissant dans les hautes herbes, la pêche et le surf à travers tout Sinnoh."
    },
    "wiz_q1_opt_yes_title": {
        "en": "Yes, randomize wild encounters (Recommended)",
        "fr": "Oui, randomiser les Pokémon sauvages (Recommandé)"
    },
    "wiz_q1_opt_yes_desc": {
        "en": "Each area receives new species for tall grass, surfing, and fishing spots.",
        "fr": "Chaque zone aura de nouvelles espèces dans les herbes, le surf et la canne à pêche."
    },
    "wiz_q1_opt_no_title": {
        "en": "No, keep original encounters",
        "fr": "Non, conserver les rencontres d'origine"
    },
    "wiz_q1_opt_no_desc": {
        "en": "Maintains official Pokémon Platinum wild encounter tables unchanged.",
        "fr": "Conserve exactement les Pokémon sauvages du jeu officiel Pokémon Platine."
    },
    "wiz_q2_title": {
        "en": "2. Wild distribution mode across Sinnoh",
        "fr": "2. Mode de distribution des Pokémon sauvages"
    },
    "wiz_q2_desc": {
        "en": "How should wild Pokémon species be distributed across routes and zones?",
        "fr": "Comment les espèces doivent-elles être réparties entre les différentes zones et routes ?"
    },
    "wiz_q2_opt_area_title": {
        "en": "Area 1-to-1 (Recommended)",
        "fr": "Zone 1-pour-1 (Recommandé)"
    },
    "wiz_q2_opt_area_desc": {
        "en": "Each route and area has its own unique, balanced species diversity.",
        "fr": "Chaque route possède sa propre diversité unique et équilibrée."
    },
    "wiz_q2_opt_global_title": {
        "en": "Global 1-to-1",
        "fr": "Global 1-pour-1"
    },
    "wiz_q2_opt_global_desc": {
        "en": "A species is replaced with the exact same Pokémon everywhere across Sinnoh.",
        "fr": "Une espèce est remplacée par la même partout dans Sinnoh (ex: tous les Étourmi deviennent des Roucool)."
    },
    "wiz_q2_opt_random_title": {
        "en": "Completely Random (Chaos)",
        "fr": "Totalement Aléatoire (Chaos)"
    },
    "wiz_q2_opt_random_desc": {
        "en": "Pure randomness. Every encounter tile and fishing cast is completely independent.",
        "fr": "Aléatoire pur. Chaque case d'herbe et coup de canne est complètement indépendant."
    },
    "wiz_q3_title": {
        "en": "3. Wild Pokémon strength balance",
        "fr": "3. Équilibrage de la force des Pokémon sauvages"
    },
    "wiz_q3_desc": {
        "en": "Controls the power curve of Pokémon encountered in early routes.",
        "fr": "Contrôle la puissance des Pokémon rencontrés en début de jeu."
    },
    "wiz_q3_opt_simstr_yes_title": {
        "en": "Keep similar base stat totals (Recommended)",
        "fr": "Conserver une force similaire (Recommandé)"
    },
    "wiz_q3_opt_simstr_yes_desc": {
        "en": "Wild Pokémon are replaced by species with comparable base stats, avoiding unfair early encounters.",
        "fr": "Les Pokémon sont remplacés par des espèces de stats comparables (évite Dracaufeu niveau 2)."
    },
    "wiz_q3_opt_simstr_no_title": {
        "en": "Unrestricted base stats (Chaos)",
        "fr": "Totalement libre (Sans restriction)"
    },
    "wiz_q3_opt_simstr_no_desc": {
        "en": "Any species can appear at low level regardless of evolution stage or base stats.",
        "fr": "N'importe quel Pokémon peut apparaître à n'importe quel niveau dès la route 201."
    },
    "wiz_q4_title": {
        "en": "4. Legendary Pokémon in the wild",
        "fr": "4. Pokémon Légendaires dans la nature"
    },
    "wiz_q4_desc": {
        "en": "Allow or forbid legendary Pokémon in ordinary tall grass and water.",
        "fr": "Autoriser ou interdire les Pokémon Légendaires dans les herbes et l'eau ordinaires."
    },
    "wiz_q4_opt_noleg_yes_title": {
        "en": "Exclude Legendaries (Recommended)",
        "fr": "Exclure les Légendaires (Recommandé)"
    },
    "wiz_q4_opt_noleg_yes_desc": {
        "en": "Prevents early legendary encounters like Mewtwo or Dialga on Route 201.",
        "fr": "Empêche les rencontres prématurées avec Mewtwo, Rayquaza ou Dialga dans les hautes herbes."
    },
    "wiz_q4_opt_noleg_no_title": {
        "en": "Allow Legendaries in the wild",
        "fr": "Autoriser les Légendaires"
    },
    "wiz_q4_opt_noleg_no_desc": {
        "en": "Legendary Pokémon have a chance to appear as ordinary wild encounters.",
        "fr": "Les Pokémon Légendaires ont une chance d'apparaître parmi les rencontres sauvages."
    },
    "wiz_q5_title": {
        "en": "5. Starter Pokémon in Rowan's briefcase",
        "fr": "5. Pokémon de départ (Starters)"
    },
    "wiz_q5_desc": {
        "en": "Which starter Pokémon will be inside Professor Rowan's briefcase at Lake Verity?",
        "fr": "Quels Pokémon seront proposés dans la mallette du Professeur Sorbier au lac Vérité ?"
    },
    "wiz_q5_opt_vanilla_title": {
        "en": "Originals (Vanilla)",
        "fr": "Originaux (Vanilla)"
    },
    "wiz_q5_opt_vanilla_desc": {
        "en": "Turtwig, Chimchar, Piplup.",
        "fr": "Tortipouss, Ouisticram, Tiplouf."
    },
    "wiz_q5_opt_balanced_title": {
        "en": "Balanced Random (Recommended)",
        "fr": "Aléatoires Équilibrés (Recommandé)"
    },
    "wiz_q5_opt_balanced_desc": {
        "en": "3 random basic Pokémon that have 2 evolution stages (e.g. Charmander, Gastly, Starly).",
        "fr": "3 Pokémon de base à 2 évolutions (ex: Salamèche, Fantominus, Grainipiot)."
    },
    "wiz_q5_opt_any_title": {
        "en": "Completely Random",
        "fr": "Complètement Aléatoires"
    },
    "wiz_q5_opt_any_desc": {
        "en": "Any basic Pokémon, including single-stage species.",
        "fr": "N'importe quel Pokémon de base (y compris sans évolution)."
    },
    "wiz_q6_title": {
        "en": "6. Shiny Pokémon Odds",
        "fr": "6. Probabilité des Pokémon Chromatiques (Shiny)"
    },
    "wiz_q6_desc": {
        "en": "Adjust the rate of encountering shiny Pokémon during your playthrough.",
        "fr": "Ajustez la rareté des Pokémon chromatiques pour votre aventure."
    },
    "wiz_q7_title": {
        "en": "7. Sinnoh Honey Tree Encounters",
        "fr": "7. Arbres à Miel de Sinnoh"
    },
    "wiz_q7_desc": {
        "en": "Randomizes wild Pokémon that appear after slathering Honey on the 21 Sinnoh honey trees (Combee, Heracross, Munchlax...).",
        "fr": "Randomise les espèces sauvages qui apparaissent après avoir étalé du miel sur les 21 arbres de Sinnoh (Apiraine, Scarhino, Goinfrex...)."
    },
    "wiz_q7_opt_yes_title": {
        "en": "Yes, randomize honey trees (Recommended)",
        "fr": "Oui, randomiser les arbres à miel (Recommandé)"
    },
    "wiz_q7_opt_yes_desc": {
        "en": "All 21 honey trees in Sinnoh will yield surprise wild species.",
        "fr": "Les 21 arbres à miel de Sinnoh proposeront des espèces sauvages aléatoires."
    },
    "wiz_q7_opt_no_title": {
        "en": "No, keep original honey tree encounters",
        "fr": "Non, conserver les arbres officiels"
    },
    "wiz_q7_opt_no_desc": {
        "en": "Preserves official Platinum honey tree spawn tables (Combee, Heracross, Munchlax).",
        "fr": "Conserve les tables officielles des arbres à miel (Apiraine, Scarhino, Goinfrex)."
    },
    "wiz_q8_title": {
        "en": "8. Static & Overworld Encounters",
        "fr": "8. Pokémon Fixes & Rencontres d'Événements"
    },
    "wiz_q8_desc": {
        "en": "Randomizes static overworld Pokémon: Windworks Drifloon, Old Chateau Rotom, Route 209 Spiritomb, and gifted eggs (Cynthia's Togepi, Riley's Riolu).",
        "fr": "Randomise les Pokémon fixes visibles sur la carte : Baudrive aux Éoliennes, Motisma au Vieux Château, Spiritomb Route 209, et les œufs offerts (Togepi de Cynthia, Riolu de Riley)."
    },
    "wiz_q8_opt_yes_title": {
        "en": "Yes, randomize static encounters & eggs (Recommended)",
        "fr": "Oui, randomiser les Pokémon fixes & œufs (Recommandé)"
    },
    "wiz_q8_opt_yes_desc": {
        "en": "Drifloon, Rotom, Spiritomb, and gifted story eggs will feature random Pokémon.",
        "fr": "Baudrive, Motisma, Spiritomb et les œufs offerts contiendront des Pokémon aléatoires."
    },
    "wiz_q8_opt_no_title": {
        "en": "No, keep original static encounters",
        "fr": "Non, conserver les Pokémon fixes officiels"
    },
    "wiz_q8_opt_no_desc": {
        "en": "Preserves Drifloon, Rotom, Spiritomb, and egg gifts identical to official Platinum.",
        "fr": "Laisse Baudrive, Motisma, Spiritomb et les œufs identiques au jeu officiel."
    },
    "wiz_q9_title": {
        "en": "9. Scripted Boss & Rival Battles",
        "fr": "9. Combats de Boss & Rivaux Scriptés"
    },
    "wiz_q9_desc": {
        "en": "Randomizes one-time scripted battles (fixed legendaries: Dialga, Palkia, Giratina, etc.).",
        "fr": "Randomise les combats fixes scénarisés (Légendaires fixes comme Dialga, Palkia, Giratina, etc.)."
    },
    "wiz_q9_opt_yes_title": {
        "en": "Yes, randomize scripted boss battles",
        "fr": "Oui, randomiser les combats scénarisés"
    },
    "wiz_q9_opt_yes_desc": {
        "en": "Story legendary battles will be replaced with other random species.",
        "fr": "Les combats d'histoire contre les Légendaires seront remplacés par d'autres Pokémon."
    },
    "wiz_q9_opt_no_title": {
        "en": "No, keep original boss encounters (Recommended)",
        "fr": "Non, conserver les boss d'origine (Recommandé)"
    },
    "wiz_q9_opt_no_desc": {
        "en": "Keeps story encounters with Dialga, Palkia, and Giratina true to the lore.",
        "fr": "Préserve les cinématiques et rencontres de scénario avec Dialga, Palkia et Giratina."
    },
    "wiz_q10_title": {
        "en": "10. NPC Gifts & In-Game Trades",
        "fr": "10. Cadeaux de PNJ & Échanges en jeu"
    },
    "wiz_q10_desc": {
        "en": "Randomizes Bebe's Eevee, Veilstone Porygon, revived fossils, and NPC trades.",
        "fr": "Randomise l'Évoli d'Unionpolis, le Porygon de Voilaroc, les fossiles réanimés et les échanges avec les PNJ."
    },
    "wiz_q10_opt_yes_title": {
        "en": "Yes, randomize gifts & trades (Recommended)",
        "fr": "Oui, randomiser les dons et échanges (Recommandé)"
    },
    "wiz_q10_opt_yes_desc": {
        "en": "NPCs will gift surprise Pokémon and request/give random species in trades.",
        "fr": "Les PNJ vous offriront des Pokémon surprises et échangeront de nouvelles espèces."
    },
    "wiz_q10_opt_no_title": {
        "en": "No, keep official gifts & trades",
        "fr": "Non, conserver les dons et échanges d'origine"
    },
    "wiz_q10_opt_no_desc": {
        "en": "Keeps official Eevee, Porygon, fossils, and in-game trade tables.",
        "fr": "Conserve Évoli, Porygon, fossiles et échanges officiels."
    },
    "wiz_q11_title": {
        "en": "11. Feebas, Great Marsh & GBA Dual-Slot",
        "fr": "11. Barpau, Grand Marais & Double-Slot GBA"
    },
    "wiz_q11_desc": {
        "en": "Randomizes Feebas tiles, Trophy Garden, Great Marsh binoculars, and GBA dual-slot spawns.",
        "fr": "Randomise Barpau (les 4 cases d'eau du Mont Couronné), le Grand Marais, le Jardin Trophée et le double-slot GBA."
    },
    "wiz_q11_opt_yes_title": {
        "en": "Yes, randomize special events (Recommended)",
        "fr": "Oui, randomiser les événements spéciaux (Recommandé)"
    },
    "wiz_q11_opt_yes_desc": {
        "en": "Randomizes special daily encounters and GBA dual-slot cartridge bonuses.",
        "fr": "Mélange les apparitions spéciales quotidiennes et le double slot GBA."
    },
    "wiz_q11_opt_no_title": {
        "en": "No, leave standard",
        "fr": "Non, laisser standard"
    },
    "wiz_q11_opt_no_desc": {
        "en": "Maintains standard behavior for Feebas and the Great Marsh.",
        "fr": "Garde la logique standard pour Barpau et le Grand Marais."
    },
    "wiz_q12_title": {
        "en": "12. Pokémon Evolution Paths",
        "fr": "12. Randomisation des Évolutions des Pokémon"
    },
    "wiz_q12_desc": {
        "en": "Modifies the target species obtained when Pokémon evolve (via level-up, stones, trade or friendship).",
        "fr": "Modifie les espèces obtenues lors des évolutions (par niveau, pierre, échange ou bonheur)."
    },
    "wiz_q12_opt_vanilla_title": {
        "en": "Keep Official Evolutions (Vanilla - Recommended)",
        "fr": "Conserver les évolutions officielles (Vanilla - Recommandé)"
    },
    "wiz_q12_opt_vanilla_desc": {
        "en": "Standard evolution lines are preserved (e.g. Turtwig -> Grotle -> Torterra).",
        "fr": "Chaque Pokémon conserve ses évolutions normales (ex: Tortipouss -> Boskara -> Torterra)."
    },
    "wiz_q12_opt_simstr_title": {
        "en": "Balanced Random Evolutions (Similar Strength)",
        "fr": "Évolutions aléatoires équilibrées (Similar Strength)"
    },
    "wiz_q12_opt_simstr_desc": {
        "en": "Evolves into a random Pokémon with comparable base stats and evolution tier.",
        "fr": "Les Pokémon évoluent vers une espèce aléatoire de force comparable et au même stade d'évolution."
    },
    "wiz_q12_opt_chaos_title": {
        "en": "Completely Random Evolutions (Chaos)",
        "fr": "Évolutions complètement aléatoires (Chaos)"
    },
    "wiz_q12_opt_chaos_desc": {
        "en": "Unrestricted randomness: any Pokémon can evolve into any species (even legendaries).",
        "fr": "N'importe quel Pokémon peut évoluer en n'importe quelle espèce (même un légendaire)."
    },
    "wiz_q13_title": {
        "en": "13. Trainer & Gym Leader Teams (Co-op Synced)",
        "fr": "13. Dresseurs & Champions d'Arène (Co-op)"
    },
    "wiz_q13_desc": {
        "en": "Randomizes trainer Pokémon. 100% identical between co-op players sharing the same code!",
        "fr": "Randomise les équipes de tous les dresseurs du jeu. 100% synchronisé en Co-op entre les joueurs avec le même code !"
    },
    "wiz_q13_opt_yes_title": {
        "en": "Yes, randomize trainers (Recommended for Co-op)",
        "fr": "Oui, randomiser les dresseurs (Recommandé pour Co-op)"
    },
    "wiz_q13_opt_yes_desc": {
        "en": "Every trainer and gym leader gets a fresh, balanced team tailored to their level.",
        "fr": "Chaque dresseur et champion d'arène aura de nouveaux Pokémon adaptés à leur niveau."
    },
    "wiz_q13_opt_no_title": {
        "en": "No, keep original trainer teams",
        "fr": "Non, conserver les équipes d'origine"
    },
    "wiz_q13_opt_no_desc": {
        "en": "Retains standard official Pokémon Platinum trainer compositions.",
        "fr": "Conserve les dresseurs et champions officiels de Pokémon Platine."
    },
    "wiz_q14_title": {
        "en": "14. Trainer Balance & Legendaries",
        "fr": "14. Équilibrage des Dresseurs ordinaires"
    },
    "wiz_q14_desc": {
        "en": "Difficulty and balance rules for ordinary route trainers.",
        "fr": "Règles de difficulté pour les dresseurs rencontrés sur les routes."
    },
    "wiz_q14_opt_bal_yes_title": {
        "en": "Balanced trainers & No Legendaries (Recommended)",
        "fr": "Dresseurs équilibrés & Sans Légendaires (Recommandé)"
    },
    "wiz_q14_opt_bal_yes_desc": {
        "en": "Matches vanilla power curve and restricts legendaries strictly to major boss fights.",
        "fr": "Les dresseurs suivent la courbe de difficulté et les dresseurs ordinaires ne possèdent aucun légendaire."
    },
    "wiz_q14_opt_bal_no_title": {
        "en": "Completely Unrestricted (Chaos)",
        "fr": "Totalement libre (Chaos)"
    },
    "wiz_q14_opt_bal_no_desc": {
        "en": "Ordinary route trainers can field any Pokémon including legendaries.",
        "fr": "N'importe quel dresseur ordinaire peut posséder des Pokémon légendaires ou évolués."
    },
    "wiz_q15_title": {
        "en": "15. Types, Abilities & Movesets (Co-op Chaos)",
        "fr": "15. Types, Talents & Attaques (Chaos Co-op)"
    },
    "wiz_q15_desc": {
        "en": "Optional chaos modifiers. 100% synchronized across players sharing the same Co-op Code.",
        "fr": "Options de chaos optionnelles. Synchronisées à 100% entre les joueurs partageant le même Code Co-op."
    },
    "wiz_q15_types_label": {
        "en": "Reroll Pokémon Types (Dual types preserved)",
        "fr": "Reroll des Types des 493 Pokémon"
    },
    "wiz_q15_types_desc": {
        "en": "Rerolls types for all 493 Pokémon (Dual types preserved). Identical for all players.",
        "fr": "Redistribue les types pour chaque espèce (ex: Bulbizarre devient Feu/Vol). Identique pour tous les joueurs."
    },
    "wiz_q15_abilities_label": {
        "en": "Reroll Pokémon Abilities (Talents)",
        "fr": "Reroll des Talents (Capacités spéciales)"
    },
    "wiz_q15_abilities_desc": {
        "en": "Rerolls passive abilities for all Pokémon (Wonder Guard banned). Identical for all players.",
        "fr": "Redistribue les talents passifs (Garde Mystik interdite). Identique pour tous les joueurs."
    },
    "wiz_q15_movesets_label": {
        "en": "Reroll Pokémon Level-up Movesets",
        "fr": "Reroll des Attaques apprises par niveau"
    },
    "wiz_q15_movesets_desc": {
        "en": "Rerolls level-up learning moves for all Pokémon. Identical for all players.",
        "fr": "Redistribue les attaques apprises en montant de niveau. Identique pour tous les joueurs."
    },
    "wiz_q16_title": {
        "en": "16. Summary & Share Codes",
        "fr": "16. Résumé & Codes de Partage"
    },
    "wiz_q16_desc": {
        "en": "Your randomizer configuration is ready! Share your Co-op Code with your friend so both of you play with identical trainer teams and rules.",
        "fr": "Votre configuration est prête ! Donnez votre Code Co-op à votre ami(e) pour que vos deux parties soient synchronisées."
    },
    "rand_step_1_title": {
        "en": "Step 1: Wild Encounters & Distribution",
        "fr": "Étape 1 : Rencontres Sauvages & Distribution"
    },
    "rand_step_2_title": {
        "en": "Step 2: Starters & Shiny Odds",
        "fr": "Étape 2 : Starters & Taux de Shiny"
    },
    "rand_step_3_title": {
        "en": "Step 3: Special World Events",
        "fr": "Étape 3 : Événements Spéciaux du Monde"
    },
    "rand_step_4_title": {
        "en": "Step 4: Co-op & Multiplayer Rules",
        "fr": "Étape 4 : Règles Co-Op & Multijoueur"
    },
    "rand_step_5_title": {
        "en": "Step 5: Summary & Share Codes",
        "fr": "Étape 5 : Résumé & Codes de Partage"
    },
    "rand_q_wilds": {
        "en": "Randomize wild Pokémon encounters?",
        "fr": "Voulez-vous randomiser les Pokémon sauvages ?"
    },
    "rand_q_wilds_yes": {
        "en": "Yes, randomize wild encounters",
        "fr": "Oui, randomiser les Pokémon sauvages"
    },
    "rand_q_mode": {
        "en": "How should wild Pokémon be distributed across Sinnoh?",
        "fr": "Comment répartir les Pokémon dans les zones de Sinnoh ?"
    },
    "rand_mode_area_title": {
        "en": "Area 1-to-1 (Recommended)",
        "fr": "Équilibré par Zone (Recommandé)"
    },
    "rand_mode_area_desc": {
        "en": "Each route and area has its own unique, balanced species diversity.",
        "fr": "Chaque route et zone possède sa propre diversité d'espèces équilibrée."
    },
    "rand_mode_global_title": {
        "en": "Global 1-to-1",
        "fr": "Global 1-pour-1"
    },
    "rand_mode_global_desc": {
        "en": "A species is replaced with the exact same Pokémon everywhere across Sinnoh.",
        "fr": "Une espèce est remplacée de manière unique et identique dans tout Sinnoh."
    },
    "rand_mode_random_title": {
        "en": "Completely Random (Chaos)",
        "fr": "Totalement Aléatoire (Chaos)"
    },
    "rand_mode_random_desc": {
        "en": "Pure randomness. Every encounter tile and rod cast is completely independent.",
        "fr": "Chaos complet : chaque case d'herbe ou coup de canne à pêche est indépendant."
    },
    "rand_q_simstr": {
        "en": "Similar Strength Rule (Balanced Progression)?",
        "fr": "Règle de Force Similaire (Progression Équilibrée) ?"
    },
    "rand_simstr_title": {
        "en": "Keep similar base stat totals (Recommended)",
        "fr": "Conserver une force équivalente (Recommandé)"
    },
    "rand_simstr_desc": {
        "en": "Wild Pokémon are replaced by species with comparable base stats, avoiding unfair early encounters.",
        "fr": "Les Pokémon sauvages sont remplacés par des espèces de puissance équivalente (BST)."
    },
    "rand_q_noleg": {
        "en": "Ban Legendary Pokémon from wild grass?",
        "fr": "Bannir les Pokémon Légendaires de la nature ?"
    },
    "rand_noleg_title": {
        "en": "Exclude Legendaries (Recommended)",
        "fr": "Exclure les Légendaires (Recommandé)"
    },
    "rand_noleg_desc": {
        "en": "Prevents early legendary encounters like Mewtwo or Dialga on Route 201.",
        "fr": "Empêche les légendaires (Mewtwo, Dialga, etc.) d'apparaître dans les herbes de début de jeu."
    },
    "rand_q_starters": {
        "en": "Which starter Pokémon in Professor Rowan's briefcase?",
        "fr": "Quels Pokémon de départ dans la mallette du Prof. Sorbier ?"
    },
    "rand_starters_vanilla_title": {
        "en": "Originals (Vanilla)",
        "fr": "Originaux (Vanilla)"
    },
    "rand_starters_vanilla_desc": {
        "en": "Turtwig, Chimchar, Piplup.",
        "fr": "Tortipouss, Ouisticram, Tiplouf."
    },
    "rand_starters_balanced_title": {
        "en": "Balanced Random (Recommended)",
        "fr": "Aléatoire Équilibré (Recommandé)"
    },
    "rand_starters_balanced_desc": {
        "en": "3 random basic Pokémon that have 2 evolution stages (e.g. Charmander, Gastly, Starly).",
        "fr": "3 Pokémon de base ayant 2 évolutions (ex: Salamèche, Fantominus, Étourmi)."
    },
    "rand_starters_any_title": {
        "en": "Completely Random",
        "fr": "Totalement Aléatoire"
    },
    "rand_starters_any_desc": {
        "en": "Any basic Pokémon, including single-stage species.",
        "fr": "N'importe quel Pokémon de base, y compris sans évolution."
    },
    "rand_q_shiny": {
        "en": "Shiny Pokémon Odds:",
        "fr": "Taux d'apparition des Pokémon Chromatiques (Shiny) :"
    },
    "rand_q_events": {
        "en": "Which special world elements should be randomized?",
        "fr": "Quels éléments spéciaux du monde souhaitez-vous randomiser ?"
    },
    "rand_q_coop": {
        "en": "Which rules should be synchronized with your co-op friends?",
        "fr": "Quels éléments voulez-vous synchroniser avec vos partenaires ?"
    },
    "rand_coop_help": {
        "en": "For Co-op & Soul Link, players must share the exact same Co-op Code to keep trainer teams and types synchronized!",
        "fr": "En Co-op ou Soul Link, tous les joueurs doivent avoir le même Code Co-op pour synchroniser les dresseurs et types !"
    },
    "rand_btn_prev": {
        "en": "< Previous",
        "fr": "< Précédent"
    },
    "rand_btn_next": {
        "en": "Next >",
        "fr": "Suivant >"
    },
    "rand_btn_apply": {
        "en": "Apply Configuration",
        "fr": "Valider et Appliquer la Configuration"
    },
    "rand_code_import_title": {
        "en": "Import Shared Codes from a Friend",
        "fr": "Importer les Codes d'un Ami"
    },
    "rand_code_import_desc": {
        "en": "If your multiplayer partner already configured the randomizer, paste their codes here to synchronize instantly without going through the configurator.",
        "fr": "Si votre partenaire multijoueur a déjà configuré le randomizer, collez ses codes ici pour vous synchroniser instantanément sans passer par le configurateur."
    },
    "rand_btn_load_codes": {
        "en": "Load and Apply Codes",
        "fr": "Charger et Appliquer les Codes"
    },
    "btn_copy": {
        "en": "Copy",
        "fr": "Copier"
    },
    "btn_paste": {
        "en": "Paste",
        "fr": "Coller"
    },
    "btn_execute_patch_and_rand": {
        "en": "APPLY PATCHES & RANDOMIZE ROM",
        "fr": "APPLIQUER LES PATCHS & RANDOMISER LA ROM"
    },
    "btn_execute_soullink_and_rand": {
        "en": "INJECT SOUL LINK & RANDOMIZE ROM (%s)",
        "fr": "INJECTER SOUL LINK & RANDOMISER LA ROM (%s)"
    },
    "stepper_wilds": {
        "en": "1. Wilds",
        "fr": "1. Sauvages"
    },
    "stepper_starters": {
        "en": "2. Starters & Shiny",
        "fr": "2. Starters & Shiny"
    },
    "stepper_events": {
        "en": "3. Events",
        "fr": "3. Événements"
    },
    "stepper_coop": {
        "en": "4. Trainers & Co-Op",
        "fr": "4. Dresseurs & Co-Op"
    },
    "stepper_summary": {
        "en": "5. Summary & Codes",
        "fr": "5. Résumé & Codes"
    },
    "rand_cat_wilds_desc": {
        "en": "Applies random species to tall grass, surfing, and fishing spots.",
        "fr": "Applique des espèces aléatoires aux hautes herbes, au surf et à la pêche."
    },
    "rand_cat_honey": {
        "en": "Static & Honey Tree Encounters",
        "fr": "Arbres à Miel & Pokémon Fixes"
    },
    "rand_cat_honey_desc": {
        "en": "Randomizes Honey tree spawns, Windworks Drifloon, Rotom, Spiritomb, and gift eggs.",
        "fr": "Randomise les arbres à miel, Baudrive aux Éoliennes, Motisma, Spiritomb et les œufs offerts."
    },
    "rand_cat_battles": {
        "en": "Scripted Boss & Rival Battles",
        "fr": "Combats de Boss & Rivaux Scriptés"
    },
    "rand_cat_battles_desc": {
        "en": "Randomizes one-time scripted battles (fixed legendaries, Rotom, Spiritomb).",
        "fr": "Randomise les combats uniques scriptés (légendaires fixes, Motisma, Spiritomb)."
    },
    "rand_cat_gifts": {
        "en": "NPC Gift Pokémon (Eevee, Porygon...)",
        "fr": "Pokémon Offerts par les PNJ (Évoli, Porygon...)"
    },
    "rand_cat_gifts_desc": {
        "en": "Randomizes friendly gift Pokémon: Bebe's Eevee, Veilstone Porygon, and revived fossils.",
        "fr": "Randomise les Pokémon donnés par des PNJ : Évoli d'Amelle, Porygon de Voilaroc et fossiles."
    },
    "rand_cat_trades": {
        "en": "In-Game NPC Trades",
        "fr": "Échanges en Jeu avec les PNJ"
    },
    "rand_cat_trades_desc": {
        "en": "Randomizes both the Pokémon requested and given by NPCs in trades.",
        "fr": "Randomise à la fois les Pokémon demandés et reçus lors des échanges en jeu."
    },
    "rand_cat_special": {
        "en": "Special Events & GBA Dual-Slot",
        "fr": "Événements Spéciaux & Insertion GBA"
    },
    "rand_cat_special_desc": {
        "en": "Randomizes Feebas, daily Trophy Garden / Great Marsh binoculars, and GBA dual-slot spawns.",
        "fr": "Randomise Barpau, le Jardin Trophée, le Grand Marais et les insertions de cartouches GBA."
    },
    "rand_cat_trainers": {
        "en": "Randomize Trainer & Gym Leader Teams (Co-op Synced)",
        "fr": "Randomiser les Dresseurs & Champions (Synchronisés Co-op)"
    },
    "rand_cat_trainers_desc": {
        "en": "Changes every trainer's Pokémon. Levels stay the same, moves come from leveling up. In Co-op, trainer teams are 100% identical between players with the same code!",
        "fr": "Remplace les Pokémon de chaque dresseur, Champion d'Arène et Rival. Les niveaux restent identiques. En Co-op, les équipes sont 100% identiques entre amis !"
    },
    "rand_cat_trainers_simstr": {
        "en": "Trainer Similar Strength",
        "fr": "Dresseurs : Force Similaire (Recommandé)"
    },
    "rand_cat_trainers_simstr_desc": {
        "en": "Matches trainers' power to their vanilla difficulty curve.",
        "fr": "Préserve la courbe de difficulté et la puissance originale des champions."
    },
    "rand_cat_trainers_noleg": {
        "en": "Exclude Legendaries from Ordinary Trainers",
        "fr": "Exclure les Légendaires des Dresseurs Ordinaires"
    },
    "rand_cat_trainers_noleg_desc": {
        "en": "Restricts legendary Pokémon to major boss battles.",
        "fr": "Réserve les Pokémon légendaires aux combats majeurs."
    },
    "rand_types": {
        "en": "Reroll Pokémon Types",
        "fr": "Reroll des Types des Pokémon"
    },
    "rand_types_desc": {
        "en": "Rerolls types for all 493 Pokémon (Dual types preserved). Identical for all players.",
        "fr": "Reroll les types des 493 Pokémon (doubles types préservés). Identique pour tous les joueurs."
    },
    "rand_abilities": {
        "en": "Reroll Pokémon Abilities (Talents)",
        "fr": "Reroll des Talents (Abilities)"
    },
    "rand_abilities_desc": {
        "en": "Rerolls passive abilities for all Pokémon (Wonder Guard banned). Identical for all players.",
        "fr": "Reroll les talents passifs de tous les Pokémon (Garde Mystik banni). Identique pour tous."
    },
    "rand_movesets": {
        "en": "Reroll Pokémon Movesets",
        "fr": "Reroll des Capacités (Movesets)"
    },
    "rand_movesets_desc": {
        "en": "Rerolls level-up learning moves for all Pokémon. Identical for all players.",
        "fr": "Reroll les attaques apprises par montée de niveau. Identique pour tous les joueurs."
    },
    "rand_summary_heading": {
        "en": "Step 5: Summary & Share Codes",
        "fr": "Étape 5 : Résumé & Codes de Partage"
    },
    "rand_summary_desc": {
        "en": "Your randomizer configuration is ready! Share your Co-op Code with your friend so both of you play with identical trainer teams and rules.",
        "fr": "Votre configuration est prête ! Donnez votre Code Co-op à votre ami pour avoir exactement les mêmes dresseurs et types que lui."
    },
    "rand_code_coop_badge": {
        "en": "CO-OP CODE (FRIENDS MUST MATCH)",
        "fr": "CODE CO-OP (À DONNER À VOS AMIS)"
    },
    "rand_code_world_badge": {
        "en": "WORLD CODE (PERSONAL)",
        "fr": "CODE MONDE (PERSONNEL)"
    },
    "rand_import_coop_label": {
        "en": "Co-op Code from partner (PMC-XXXX-XXXX):",
        "fr": "Code Co-op de votre ami (PMC-XXXX-XXXX) :"
    },
    "rand_import_world_label": {
        "en": "World Code (PMW-XXXX-XXXX, Optional):",
        "fr": "Code Monde (PMW-XXXX-XXXX, Optionnel) :"
    },
    "rand_import_world_help": {
        "en": "Leave blank if you prefer generating your own personal wild encounters and shiny odds.",
        "fr": "Laissez vide si vous préférez générer vos propres rencontres sauvages et votre taux de shiny."
    },
    "rand_starter_1": {
        "en": "STARTER #1",
        "fr": "STARTER #1"
    },
    "rand_starter_2": {
        "en": "STARTER #2",
        "fr": "STARTER #2"
    },
    "rand_starter_3": {
        "en": "STARTER #3",
        "fr": "STARTER #3"
    },
    "rand_coop_seed_lbl": {
        "en": "Co-Op Seed:",
        "fr": "Seed Co-Op :"
    },
    "rand_world_seed_lbl": {
        "en": "World Seed:",
        "fr": "Seed Monde :"
    },
    # Footer
    "footer_status_ready": {
        "en": "Ready to patch",
        "fr": "Prêt à patcher"
    },
    "footer_status_waiting": {
        "en": "Waiting for a valid ROM (USA rev1 or FR)...",
        "fr": "En attente d'une ROM valide (USA rev1 ou FR)..."
    },
    "footer_status_incompatible": {
        "en": "Incompatible ROM (Platinum USA rev1 or FR required)",
        "fr": "ROM non compatible (Platine USA rev1 ou FR requis)"
    },
    "footer_community": {
        "en": "Project PM Community",
        "fr": "Communauté Project PM"
    },
    # Credits & About Section
    "credits_title": {
        "en": "CREDITS & CONTRIBUTORS",
        "fr": "CRÉDITS & REMERCIEMENTS"
    },
    "credits_pm_title": {
        "en": "Project PM (Platinum Multiplayer)",
        "fr": "Project PM (Platinum Multiplayer)"
    },
    "credits_pm_desc": {
        "en": "Creators of Project PM: online/LAN multiplayer network bridge, ROM modification & emulator integrations.",
        "fr": "Créateurs de Project PM : protocole multijoueur en ligne/LAN, pont réseau melonDS/DeSmuME et romhack."
    },
    "credits_soullink_title": {
        "en": "Soul Link Mod & French Suite",
        "fr": "Mod Soul Link & Suite Française"
    },
    "credits_soullink_desc": {
        "en": "SoulLink/SoulLocke C mod payload, Direct P2P system, streaming overlay, and French translation & tool suite.",
        "fr": "Développement du mod Soul Link / SoulLocke, Direct P2P, overlay streaming et adaptation intégrale en français."
    },
    "credits_visual_title": {
        "en": "Visual+ & 3D Camera",
        "fr": "Visual+ & Caméra 3D"
    },
    "credits_visual_desc": {
        "en": "Visual+ battle backgrounds & dynamic 3D camera. Battle backdrops created by Young for Pokémon Another Red.",
        "fr": "Création de Visual+ et caméra 3D. Décors de combat originaux dessinés par Young pour Pokémon Another Red."
    },
    "credits_art_title": {
        "en": "Community Art & Sprites",
        "fr": "Art & Sprites Communautaires"
    },
    "credits_art_desc": {
        "en": "@hyo (Brendan ORAS sprites), DiegoWT (Gen 5 OW sprites), Lucidious89 (Animated Intros), Anarlaurendil (Fairy Feather icon).",
        "fr": "@hyo (Sprites Brice ORAS), DiegoWT (Sprites Overworld 5G), Lucidious89 (Intros animées), Anarlaurendil (Icône Écaille Féerique)."
    },
    "credits_tools_title": {
        "en": "Emulators & Reverse Engineering",
        "fr": "Émulateurs & Décompilation"
    },
    "credits_tools_desc": {
        "en": "melonDS team, DeSmuME team, and the pret pokeplatinum decomp team for invaluable research and documentation.",
        "fr": "Équipes melonDS et DeSmuME, ainsi que le projet pret pokeplatinum pour leurs recherches et documentations inestimables."
    },
    # Legal Disclaimer & ROM Notice Section
    "legal_title": {
        "en": "LEGAL DISCLAIMER & ROM NOTICE",
        "fr": "MENTIONS LÉGALES & NON-FOURNITURE DE ROM"
    },
    "legal_rom_badge": {
        "en": "NO ROM INCLUDED",
        "fr": "AUCUNE ROM FOURNIE"
    },
    "legal_rom_head": {
        "en": "Strict Non-Distribution Policy",
        "fr": "Politique stricte de non-fourniture de ROM"
    },
    "legal_rom_desc": {
        "en": "This software does NOT provide, host, download, or distribute <strong>ANY game ROMs</strong>, copyrighted Pokémon Platinum files, or Nintendo proprietary code. Users must strictly provide their own legally dumped copy from an original retail cartridge they physically own.",
        "fr": "Ce logiciel ne fournit, ne contient, n'héberge, ne télécharge et ne distribue <strong>AUCUNE ROM de jeu</strong>, fichier binaire propriétaire ou ressource protégée par le droit d'auteur de Nintendo ou Pokémon. Les utilisateurs doivent obligatoirement fournir leur propre copie légale de Pokémon Version Platine (dump personnel réalisé à partir de leur propre cartouche de jeu physique originale)."
    },
    "legal_indie_badge": {
        "en": "COMMUNITY PROJECT",
        "fr": "PROJET FAN-MADE"
    },
    "legal_indie_head": {
        "en": "Independent Fan-Made Initiative",
        "fr": "Projet Communautaire Indépendant"
    },
    "legal_indie_desc": {
        "en": "Project PM Addon Patcher is an independent open-source community tool created for fair-use game modding and multiplayer interoperability. It is not affiliated with, endorsed by, or partnered with Nintendo, Creatures Inc., The Pokémon Company, GAME FREAK inc., or the Project PM core development team.",
        "fr": "Project PM Addon Patcher est un utilitaire communautaire indépendant et open-source développé par des fans à des fins d'interopérabilité et de confort de jeu. Il n'est en aucun cas sponsorisé, approuvé, affilié ou associé à Nintendo, Creatures Inc., The Pokémon Company, GAME FREAK inc., ni à l'équipe officielle de développement de Project PM."
    },
    "legal_ip_badge": {
        "en": "TRADEMARKS",
        "fr": "MARQUES DÉPOSÉES"
    },
    "legal_ip_head": {
        "en": "Trademarks & Copyrights",
        "fr": "Propriété Intellectuelle & Marques"
    },
    "legal_ip_desc": {
        "en": "Pokémon, Pokémon Platinum, and Nintendo DS are registered trademarks of Nintendo, Creatures Inc., and GAME FREAK inc. All characters, names, media, and related assets remain the exclusive intellectual property of their respective copyright holders.",
        "fr": "Pokémon, Pokémon Version Platine et Nintendo DS sont des marques déposées de Nintendo, Creatures Inc. et GAME FREAK inc. L'ensemble des noms de créatures, personnages, jeux et visuels cités demeurent la propriété exclusive de leurs détenteurs respectifs."
    },
    "legal_terms_badge": {
        "en": "PERSONAL USE",
        "fr": "USAGE PERSONNEL"
    },
    "legal_terms_head": {
        "en": "Private Use & Disclaimer of Warranty",
        "fr": "Usage Privé & Absence de Garantie"
    },
    "legal_terms_desc": {
        "en": "This utility is distributed free of charge 'as is', without warranty of any kind. The user assumes full responsibility for any modifications applied to their own game files and the management of their backups.",
        "fr": "Cet utilitaire est distribué gratuitement « en l'état », sans garantie d'aucune sorte. L'utilisateur assume l'entière responsabilité des modifications appliquées sur ses propres fichiers de jeu et de la gestion de ses sauvegardes."
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
