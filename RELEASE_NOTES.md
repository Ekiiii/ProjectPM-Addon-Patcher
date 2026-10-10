# ProjectPM Addon Patcher & Randomizer - v1.0.4

---

## 🇫🇷 Français

### Nouveautés et Améliorations de la version 1.0.4

- **Expérience Partagée d'Équipe (Multi Exp Gen 6+)** :
  - Intégration d'un patch binaire in-game sur l'Overlay 16 permettant le partage d'expérience à toute l'équipe (100% pour les combattants actifs, 50% pour les Pokémon sur le banc).
  - Détection automatique et dynamique de l'état du Multi Exp sur la ROM chargée, avec affichage d'un badge en temps réel (`Multi Exp : Actif` / `Multi Exp : Inactif`) et synchronisation de la case à cocher.
- **Désinstallation Propre du SoulLocke** :
  - Nouvelle option permettant de désinstaller complètement le mode SoulLocke / Nuzlocke d'une ROM modifiée pour restaurer les mécaniques de combat normales sans altérer la sauvegarde.
  - Traductions et intitulés clarifiés en français et en anglais.
- **Améliorations du Randomizer & Préservation des Données** :
  - Préservation intégrale et réinjection automatique des tables randomisées (Pokémon sauvages, dresseurs, starters, évolutions) lors de l'application d'un add-on ou du Multi Exp sur une ROM déjà randomisée.
  - Padding standard à 128 Mo pour garantir une compatibilité matérielle et émulateur optimale.
  - Prévisualisation interactive des starters dans l'interface : affichage des sprites d'origine (Tortipouss, Ouisticram, Tiplouf) ou d'une Pokéball mystère avec point d'interrogation en mode aléatoire.
  - Séparation claire des réglages pour les arbres à miel et les rencontres fixes.
- **Sauvegardes et Synchronisation Automatique** :
  - Détection automatique et copie de sécurité des sauvegardes `.sav` et melonDS `.dsv`.
  - Duplication automatique de la sauvegarde vers le nouveau nom de ROM modifiée pour une reprise immédiate de la partie.
- **Nouveau Système de Logs Physiques** :
  - Journalisation en temps réel dans le dossier `logs/` (`patcher_YYYY-MM-DD.log` et `patcher_latest.log`) pour faciliter l'assistance et le débogage.
  - Verrouillage réentrant (`threading.RLock`) éliminant tout risque de deadlock au démarrage.
- **Interface & Préférences Utilisateur** :
  - Sauvegarde automatique des préférences et des derniers chemins de ROMs dans `config.json`.
  - Pop-up de sélection initiale de langue (Français / Anglais) au tout premier lancement.

---

## 🇬🇧 English

### What's New in Version 1.0.4

- **Team EXP Share (Gen 6+ Style)**:
  - Integrated in-game binary patch on Overlay 16 granting shared battle experience to the entire party (100% to active battlers, 50% to benched team members).
  - Dynamic ROM inspection detecting whether the loaded ROM currently has Team EXP Share enabled, displaying a real-time status pill (`Team EXP: Active` / `Team EXP: Inactive`) and auto-syncing the checkbox.
- **Clean SoulLocke Uninstaller**:
  - Dedicated option to cleanly uninstall SoulLocke / Nuzlocke hooks from a modified ROM, restoring standard battle behavior without corrupting your save files.
  - Updated bilingual terminology across UI and documentation.
- **Randomizer Enhancements & Table Preservation**:
  - Full preservation and re-injection of randomized tables (wild encounters, trainer rosters, starters, evolution trees) when toggling add-ons or Team EXP Share on pre-randomized ROMs.
  - 128 MB padding retention ensuring seamless compatibility with flashcarts and emulators.
  - Interactive starter preview: displays authentic Sinnoh starter sprites (Turtwig, Chimchar, Piplup) when original starters are selected, or a mystery Pokéball with question mark badge when randomized.
  - Clear separation between honey trees and stationary encounters settings.
- **Save Game Management & Auto-Backup**:
  - Automatic detection and backup of `.sav` and melonDS `.dsv` files before patching.
  - Automatic replication of save files to match generated output ROM names for instant playability.
- **Physical Diagnostic Logging**:
  - Real-time file logging under `logs/` (`patcher_YYYY-MM-DD.log` and `patcher_latest.log`) for streamlined troubleshooting.
  - Re-entrant locking (`threading.RLock`) preventing initialization deadlocks.
- **Interface & User Preferences**:
  - Settings and recent ROM file paths are automatically saved across sessions in `config.json`.
  - First-run language selection modal (English / French).
