# v1.0.9

---

## 🇫🇷 Français

### Nouveautés de la version 1.0.9

- **Support complet de Project PM v0.4.7 (Français & USA / Anglais)** :
  - Mise à jour intégrale des patchs de base `.xdelta` (`PlatinumMultiplayerV0.4.7_FR.xdelta`, `PlatinumMultiplayerV0.4.7_FR-From-USA.xdelta`, `PlatinumMultiplayerV0.4.7.xdelta`) et des packs de localisation (`lang_fr.pack`, `lang_en.pack`).
  - Conservation à 100 % de la traduction française intégrale (724 banques de textes dont les dialogues `617`/`618`, polices FR et 32 NARCs graphiques).
  - Intégration native du correctif `0.4.7` des **Pokémon Shiny capturés en Coopération** (`Overlay 16`) et compatibilité réseau multijoueur `0.4.7` (`Overlay 122`, protocole `0x9E120018`).

- **Mise à jour des Modes Soul Link & Nuzlocke et de tous les Patchs QoL / Visuels pour la v0.4.7** :
  - Réalignement complet des moteurs C **SoulLocke** et **Nuzlocke** (FR & EN) sur la mémoire `0.4.7` (tout en conservant la rétrocompatibilité `0.4.6` et `0.4.5`).
  - Réalignement de tous les patchs **QoL & Visuels** pour `0.4.7` : Badges Capsules d'Efficacité des Types (Solo & Duo), Multi Exp d'Équipe, CS Libres & Poké-Rider, CT Infinies, Évolutions Solo, Barres PV/EXP Rapides, Natures Colorées et Affichage IV/EV.
  - Correctif du **Super Bonbon Infini (Infinite Rare Candy)** : l'objet n'est plus consommé lors de son utilisation depuis le sac (`Bag_TryRemoveItem`) et protection anti-crash lorsque la poche du sac devient vide.

- **Nouvelle Option Graphique Expérimentale : Éclairage Dynamique, Ombres de Nuages & Eau** :
  - Ajout d'une option dédiée (indépendante de Visual+) intégrant les transitions fluides d'éclairage jour/nuit et météo, les ombres de nuages défilantes au sol et les reflets d'eau animés (compatible `0.4.7`, `0.4.6` et `0.4.5`).
  - Ajout des badges `NOUVEAU` et `EXPÉRIMENTAL` sur les nouvelles options de l'interface.

---

## 🇬🇧 English

### What's New in Version 1.0.9

- **Full Project PM v0.4.7 Support (French & USA / English)**:
  - Updated all base `.xdelta` patches (`PlatinumMultiplayerV0.4.7_FR.xdelta`, `PlatinumMultiplayerV0.4.7_FR-From-USA.xdelta`, `PlatinumMultiplayerV0.4.7.xdelta`) and localization packs (`lang_fr.pack`, `lang_en.pack`).
  - Preserved 100% of the complete French localization (all 724 text banks including `617`/`618`, French fonts, and 32 localized graphical NARCs).
  - Native `0.4.7` **Co-Op Shiny Capture** fix (`Overlay 16`) and `0.4.7` multiplayer network protocol compatibility (`Overlay 122`, protocol `0x9E120018`).

- **Updated Soul Link, Nuzlocke & All QoL / Visual Patches for v0.4.7**:
  - Re-aligned the **SoulLocke** and **Nuzlocke** C engines (FR & EN) for `0.4.7` memory offsets (while maintaining backward compatibility with `0.4.6` and `0.4.5`).
  - Updated all **QoL & Visual** patches for `0.4.7`: Move Effectiveness Capsule Badges (Single & Double Battles), Shared Team EXP, Free HMs & Poké-Rider, Infinite TMs, Trade Evolutions Without Trading, Fast HP/EXP Bars, Colored Natures, and In-Game IV/EV Display.
  - Fixed **Infinite Rare Candy** consumption in `Bag_TryRemoveItem` and added empty-pocket OOB crash protection.

- **New Experimental Graphics Option: Dynamic Lighting, Cloud Shadows & Water**:
  - Added a standalone option (separate from Visual+) featuring smooth day/night & weather lighting transitions, drifting cumulus cloud shadows on the ground, and animated water reflections (compatible with `0.4.7`, `0.4.6`, and `0.4.5`).
  - Added `NEW` and `EXPERIMENTAL` UI badges on new options.
