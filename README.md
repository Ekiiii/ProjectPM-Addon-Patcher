# ProjectPM Addon Patcher

[![Release](https://img.shields.io/github/v/release/Ekiiii/ProjectPM-Addon-Patcher?color=blue&logo=github)](https://github.com/Ekiiii/ProjectPM-Addon-Patcher/releases/latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/Platform-Windows%20(64--bit)-0078D6?logo=windows)](https://github.com/Ekiiii/ProjectPM-Addon-Patcher/releases/latest)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python)](https://www.python.org/)

> **An independent, modern community mod and addon manager for Pokémon Platinum & Project PM.**  
> *Gestionnaire communautaire moderne et indépendant de mods et d'addons pour Pokémon Platine & Project PM.*

---

## 🇬🇧 English

### Overview
**ProjectPM Addon Patcher** allows players to easily install, configure, and manage community addons for Pokémon Platinum multiplayer (Project PM), without risking ROM corruption or dealing with fragile xDelta checksum mismatch errors.

### ✨ Features
- **Smart Direct Injection Engine**: Injects C mods cleanly into the Nitro-SDK Autoload Table and high arena memory. Zero xDelta checksum mismatch errors, works across any ROM configuration!
- **SoulLocke Edition**: Full multiplayer support for synchronized fainting, automated graveyard PC boxes (Box 18), single shared catch per area, and live streamer overlay.
- **Visual+ Graphics Options**:
  - *Visual+ Battle Backgrounds*: High-definition redrawn battle scenes (`Enable` / `Disable` / `Keep As-Is`).
  - *Visual+ 3D Camera*: Closer overworld perspective for an enhanced 3D look (`Enable` / `Disable` / `Keep As-Is`).
- **One-Click Reversible**: Easily uninstall addons to revert to clean stock ProjectPM at any time.
- **Save & Randomizer Protection**: Automatically backs up and synchronizes companion save files (`.sav` and `.dsv`) into `PMBackups/`. Automatically preserves and re-applies randomizer seeds (`.rand.txt`).
- **Additional Custom Patches**: Apply an optional external `.xdelta` patch after all other mods are applied.
- **Bilingual Interface**: Full English and French support with instant in-app switching and sleek Dark Modern UI.
- **Standalone Portable `.exe`**: No Python installation required for players!

### 🚀 Quick Start
1. Download `ProjectPM-Addon-Patcher.exe` from the [Latest Release](https://github.com/Ekiiii/ProjectPM-Addon-Patcher/releases/latest).
2. Launch the application.
3. Select your source ROM (Vanilla Platinum USA Rev 1, Platine France, or ProjectPM 0.4.5).
4. Choose your desired multiplayer language and addons (SoulLocke, Visual+, etc.).
5. Click **APPLY ADDONS & PATCH**!

---

## 🇫🇷 Français

### Vue d'ensemble
**ProjectPM Addon Patcher** permet aux joueurs d'installer, configurer et gérer facilement les addons communautaires pour Pokémon Platine Multijoueur (Project PM), sans conflit d'empreinte de ROM ni erreur de checksum xDelta.

### ✨ Fonctionnalités
- **Moteur d'Injection Directe Intelligent** : Injecte proprement le code C via la table d'Autoload du SDK Nitro et la mémoire haute de l'arène. Zéro erreur de checksum, compatible avec toutes les ROMs existantes !
- **Édition SoulLocke** : Destins liés en multijoueur, mort synchronisée, boîtes cimetière automatiques (boîte 18), 1 capture partagée par zone et overlay streamer en direct.
- **Options Graphiques Visual+** :
  - *Arrière-plans de combat HD* (`Activer` / `Désactiver` / `Conserver`).
  - *Caméra 3D Rapprochée* (`Activer` / `Désactiver` / `Conserver`).
- **Restauration en 1 clic** : Retirez les addons pour revenir à la version ProjectPM classique propre à tout moment.
- **Protection des Sauvegardes & Randomisation** : Synchronisation et backup automatiques des sauvegardes (`.sav` et `.dsv`) dans `PMBackups/`. Préservation et réapplication automatique des tables de randomisation (`.rand.txt`).
- **Patchs Personnalisés XDelta** : Appliquez un patch externe optionnel en étape finale.
- **Interface Bilingue & Moderne** : Français et Anglais avec bascule instantanée et thème sombre soigné.
- **Exécutable `.exe` Autonome** : Aucune installation de Python requise pour les joueurs !

### 🚀 Démarrage Rapide
1. Téléchargez `ProjectPM-Addon-Patcher.exe` depuis la [dernière Release](https://github.com/Ekiiii/ProjectPM-Addon-Patcher/releases/latest).
2. Lancez l'exécutable.
3. Sélectionnez votre ROM source (Platine France, Platinum USA Rev 1 ou ProjectPM 0.4.5).
4. Choisissez la version du multijoueur et vos addons (SoulLocke, Visual+, etc.).
5. Cliquez sur **APPLIQUER LES ADDONS & PATCHER** !

---

## 📜 License / Licence

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Credits & Acknowledgements / Remerciements

- **[ndspy](https://github.com/RoadrunnerWMC/ndspy)** by RoadrunnerWMC - Nintendo DS ROM inspection and manipulation library.
- **[xdelta3](https://github.com/jmacd/xdelta)** by Josh MacDonald - Binary differential compression tool.
- **[Pillow (PIL)](https://python-pillow.org/)** - Image processing for visual previews.
- **Project PM Community** - The original Pokémon Platinum Multiplayer romhack and melonDS modifications.

---

## ⚖️ Legal Disclaimer / Avertissement Légal

- *This is an unofficial community project developed by Ekiiii. It is not affiliated with, endorsed by, or sponsored by Nintendo, The Pokémon Company, Game Freak, or the core Project PM team.*  
- *Pokémon and Nintendo DS are registered trademarks of Nintendo, Creatures Inc., and GAME FREAK inc.*  
- *This tool does NOT contain or distribute copyrighted ROM files, game assets, or proprietary Nintendo code. Users must supply their own legally obtained ROM backups.*
