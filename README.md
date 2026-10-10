# ProjectPM Addon Patcher

[![Release](https://img.shields.io/github/v/release/Ekiiii/ProjectPM-Addon-Patcher?color=blue&logo=github)](https://github.com/Ekiiii/ProjectPM-Addon-Patcher/releases/latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/Platform-Windows%20(64--bit)-0078D6?logo=windows)](https://github.com/Ekiiii/ProjectPM-Addon-Patcher/releases/latest)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python)](https://www.python.org/)

> **An independent, modern community mod and addon manager for Pokémon Platinum & Project PM.**  
> *Gestionnaire communautaire moderne et indépendant de mods et d'addons pour Pokémon Platine & Project PM.*

---

## English (EN)

### Overview
**ProjectPM Addon Patcher** allows players to easily install, configure, and manage community addons for Pokémon Platinum multiplayer (Project PM), without risking ROM corruption or dealing with fragile xDelta checksum mismatch errors.

### Features
- **Smart Direct Injection Engine**: Directly patches internal ROM code and file archives without relying on rigid full-ROM checksums. No xDelta hash mismatches: works seamlessly whether using a clean vanilla ROM or an existing modified/randomized ROM!
- **Modern Team EXP Share (Gen 6+ Style)**: Optional in-game battle engine patch (Overlay 16) granting shared experience to your entire party (100% for active battlers, 50% for benched members). Features dynamic ROM detection with a real-time status pill (`Team EXP: Active` / `Team EXP: Inactive`).
- **SoulLocke Edition & Clean Uninstaller**: Full multiplayer support for synchronized fainting, automated graveyard PC boxes (Box 18), single shared catch per area, and live streamer overlay. Includes a clean 1-click uninstaller to revert battle mechanics back to normal without corrupting save files.
- **Visual+ Graphics Options**:
  - *Visual+ Battle Backgrounds*: Redrawn, high-detail battle scenes (`Enable` / `Disable` / `Keep As-Is`).
  - *Visual+ 3D Camera*: Closer overworld perspective for an enhanced 3D look (`Enable` / `Disable` / `Keep As-Is`).
- **Save & Randomizer Protection**: Automatically backs up and synchronizes companion save files (`.sav` and melonDS `.dsv`) into `PMBackups/`. Automatically preserves and re-injects randomized tables (`.rand.txt`) with standard 128 MB padding.
- **Built-in Co-op Randomizer**: Full high-compatibility randomizer engine supporting:
  - Wild Encounters (187 areas)
  - Starter Trios (with interactive authentic Sinnoh sprites or mystery question-mark Pokéballs)
  - 973 Trainer parties and Gym Leaders
  - Species Types, Abilities, and Level-up Movesets
  - Randomized Evolutions (Similar Strength, Completely Random, or Preserved Stage)
  - Dedicated individual options for Honey Trees and Stationary Legendaries
  - Gift Eggs, In-Game Trades, and ARM9 Shiny Odds patching (~1/100 to 1/8192)
  - Shareable `PMC-...` Co-op codes ensuring 100% multiplayer sync between players!
- **Physical Diagnostic Logging**: Real-time rotating diagnostic logs in `logs/` (`patcher_YYYY-MM-DD.log` and `patcher_latest.log`) with re-entrant thread safety (`threading.RLock`).
- **Bilingual Interface & Persistent Settings**: Full French / English localization, initial language selection modal, and automatic preferences saving (`config.json`).
- **Sinnoh Pixel Art Interface**: Authentic Nintendo DS Pokémon Platinum aesthetic featuring retro pixel typography, DS dialogue frames, animated components, and type badges.
- **Standalone Portable `.exe`**: Built with PyWebView (Edge WebView2) and PyInstaller — zero Python installation required for players!

### Quick Start
1. Download `ProjectPM-Addon-Patcher.exe` from the [Latest Release](https://github.com/Ekiiii/ProjectPM-Addon-Patcher/releases/latest).
2. Launch the application.
3. Select your source ROM (Vanilla Platinum USA Rev 1, Platine France, or ProjectPM 0.4.5).
4. Choose your desired multiplayer language, add-ons (Team EXP Share, SoulLocke, Visual+, etc.), or configure the randomizer.
5. Click **APPLY ADDONS & PATCH**!

---

## Français (FR)

### Vue d'ensemble
**ProjectPM Addon Patcher** permet aux joueurs d'installer, configurer et gérer facilement les addons communautaires pour Pokémon Platine Multijoueur (Project PM), sans conflit d'empreinte de ROM ni erreur de checksum xDelta.

### Fonctionnalités
- **Moteur d'Injection Directe Intelligent** : Modifie directement le code et les fichiers internes de la ROM sans dépendre d'un patch xDelta rigide. Fini les erreurs de checksum : fonctionne aussi bien sur une ROM originale (Vanilla) que sur une ROM déjà patchée ou randomisée !
- **Expérience Partagée d'Équipe (Multi Exp Gen 6+)** : Patch in-game intégré sur l'Overlay 16 permettant le partage d'expérience à toute l'équipe (100% pour les combattants actifs, 50% pour les Pokémon sur le banc). Détection dynamique de l'état du Multi Exp sur la ROM chargée avec badge visuel en temps réel (`Multi Exp : Actif` / `Inactif`).
- **Édition SoulLocke & Désinstallation Propre** : Destins liés en multijoueur, mort synchronisée, mise au cimetière automatique (boîte PC 18), règle d'une seule capture partagée par zone et overlay streamer en direct. Inclut une option de désinstallation propre en 1 clic pour restaurer le système de combat standard sans toucher aux sauvegardes.
- **Options Graphiques Visual+** :
  - *Arrière-plans de combat détaillés (style HGSS)* (`Activer` / `Désactiver` / `Conserver`).
  - *Caméra 3D Rapprochée* (`Activer` / `Désactiver` / `Conserver`).
- **Protection des Sauvegardes & Randomisation** : Copie de secours automatique de vos sauvegardes (`.sav` et `.dsv`) dans `PMBackups/`. Préservation et réapplication automatique des tables de randomisation (`.rand.txt`) avec conservation du padding standard 128 Mo.
- **Randomizer Co-op Intégré** : Moteur de randomisation complet et robuste gérant :
  - Rencontres sauvages (187 zones)
  - Trio de Starters (avec prévisualisation interactive des sprites authentiques de Sinnoh ou Pokéball mystère)
  - 973 Dresseurs et Champions d'arène
  - Types, Talents et Attaques apprises
  - Randomisation des évolutions (Puissance similaire, Totalement aléatoire ou Conservation du stade d'évolution)
  - Options séparées et indépendantes pour les Arbres à miel et les Rencontres fixes / Légendaires
  - Œufs donnés, Échanges PNJs et seuil de Shiny ARM9 (~1/100 à 1/8192)
  - Génération de codes Co-op `PMC-...` garantissant une synchronisation multijoueur parfaite sans désync !
- **Nouveau Système de Logs Physiques** : Journalisation en temps réel dans le dossier `logs/` (`patcher_YYYY-MM-DD.log` et `patcher_latest.log`) avec verrouillage réentrant (`threading.RLock`) pour une stabilité maximale.
- **Interface Bilingue Complète & Préférences** : Traduction intégrale FR / EN, mémorisation des paramètres et des derniers chemins de ROMs dans `config.json`, et modal de sélection au tout premier lancement.
- **Interface Pixel Art Sinnoh Authentique** : Esthétique soignée inspirée des menus Nintendo DS de Pokémon Platine avec typographies pixel, fenêtres de dialogue rétro, animations et badges de types officiels.
- **Exécutable .exe Autonome & Portable** : Propulsé par PyWebView (Edge WebView2) et compilé via PyInstaller — aucune installation de Python requise pour les joueurs !

### Démarrage Rapide
1. Téléchargez `ProjectPM-Addon-Patcher.exe` depuis la [dernière Release](https://github.com/Ekiiii/ProjectPM-Addon-Patcher/releases/latest).
2. Lancez l'exécutable.
3. Sélectionnez votre ROM source (Platine France, Platinum USA Rev 1 ou ProjectPM 0.4.5).
4. Choisissez la version du multijoueur, vos addons (Multi Exp, SoulLocke, Visual+, etc.) ou configurez le randomizer.
5. Cliquez sur **APPLIQUER LES ADDONS & PATCHER** !

---

## License / Licence

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## Credits & Acknowledgements / Remerciements

- **[Project PM Team](https://github.com/Project-PM)** (nUt, MottledAbyss & Team) - The creators of the original Pokémon Platinum Multiplayer romhack and melonDS multiplayer architecture.
- **[ndspy](https://github.com/RoadrunnerWMC/ndspy)** by RoadrunnerWMC - Nintendo DS ROM inspection and manipulation library.
- **[xdelta3](https://github.com/jmacd/xdelta)** by Josh MacDonald - Binary differential compression tool.
- **[Pillow (PIL)](https://python-pillow.org/)** - Image processing for visual previews.

---

## Legal Disclaimer / Avertissement Légal

- *This is an unofficial community project developed by Ekiii. It is not affiliated with, endorsed by, or sponsored by Nintendo, The Pokémon Company, Game Freak, or the core Project PM team.*  
- *Pokémon and Nintendo DS are registered trademarks of Nintendo, Creatures Inc., and GAME FREAK inc.*  
- *This tool does NOT contain or distribute copyrighted ROM files, game assets, or proprietary Nintendo code. Users must supply their own legally obtained ROM backups.*
