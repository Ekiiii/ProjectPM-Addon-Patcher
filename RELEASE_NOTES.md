# v1.0.8

---

## 🇫🇷 Français

### Nouveautés de la version 1.0.8

- **Badges d'efficacité des types en combat (Capsules Pixel-Art Solo & Duo)** :
  - Affichage dynamique de véritables badges capsules colorés (Vert `x4`/`x2`, Neutre `x1`, Orange/Rouge `x½`/`x¼`, Sombre `x0`) directement sur les boutons des attaques offensives.
  - Prise en charge native des Combats Doubles : affichage d'une capsule scindée bicolore `[Gauche | Droite]` (19×12 pixels) indiquant instantanément l'efficacité sur chaque adversaire en vie.
  - Écran de sélection des cibles (`BattleSubscreen_DrawTargetSelectMenu`) : badge capsule individuel affiché à côté du nom de chaque Pokémon ciblé.
  - Les capacités de statut restent parfaitement neutres sans badge.

- **Aperçus visuels interactifs et dépliables (Flèches d'aperçu)** :
  - Remplacement des aperçus permanents par une flèche discrète en bas à droite de chaque carte d'option.
  - Clic intuitif pour afficher ou masquer les images de démonstration en dessous de l'option sans surcharger l'interface.

- **Écran de chargement (Splash Screen) épuré & moderne** :
  - Simplification intégrale du splash screen natif et WebView : affichage centré du logo Project PM (`PM.ico`) avec une barre de progression discrète sur fond sombre.
  - Suppression des cadres, sous-titres et éléments superflus pour un démarrage rapide et fluide.

- **Interface clarifiée & détection de ROM allégée** :
  - Épuration de la zone d'analyse de ROM : suppression des étiquettes de statut encombrantes pour une lisibilité optimale.
  - Retrait des options instables pour garantir une expérience de jeu parfaitement stable et sans crash.

---

## 🇬🇧 English

### What's New in Version 1.0.8

- **In-Battle Move Effectiveness Capsule Badges (Single & Double Battles)**:
  - Dynamic pixel-art capsule badges (Green `x4`/`x2`, Neutral `x1`, Orange/Red `x½`/`x¼`, Dark `x0`) rendered on damaging move touchscreen buttons.
  - Full Double Battle support: dual-color split capsule `[Left | Right]` (19×12 px) displaying simultaneous effectiveness for each active opponent.
  - Target selection menu (`BattleSubscreen_DrawTargetSelectMenu`): individual multiplier capsule displayed alongside each targeted Pokémon's name.
  - Status moves remain clean without badges.

- **Collapsible Interactive Previews (Preview Chevron)**:
  - Replaced persistent preview thumbnails with a discreet arrow button on visual option cards.
  - Click to expand/collapse sample screenshots directly under the option card without cluttering the UI.

- **Minimalist & Streamlined Splash Screen**:
  - Redesigned native PyInstaller and WebView boot splash: centered Project PM logo (`PM.ico`) with an elegant progress track.
  - Removed bulky borders and status texts for faster, cleaner app launch.

- **Refined User Interface & Clean ROM Header**:
  - Streamlined ROM detection header by removing cluttered status tags.
  - Cleaned up obsolete experimental toggles to ensure maximum stability and crash-free gameplay.
