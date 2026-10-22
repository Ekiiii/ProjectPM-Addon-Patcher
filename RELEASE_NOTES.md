# v1.1.0

---

## 🇫🇷 Français

### Nouveautés de la version 1.1.0

- **Correction des Combats Doubles Co-Op en mode SoulLocke & Nuzlocke (`0.4.5` / `0.4.6` / `0.4.7`)** :
  - Correction de l'offset `mapLabelTextID` (`0x178`) dans la structure `BattleDTO` : les 2e rencontres sauvages et suivantes sur une même route restent désormais en **Combat Double Co-Op 2v2** avec votre partenaire au lieu de basculer en combat solo 1v1.
  - Protection du tampon réseau `ov122` pendant les combats (`SoulLink_SyncTick`) : la synchronisation SoulLocke n'écrase plus le hash d'état de combat (`exportBlk + 0xCA..0xCB`) ni le tampon de commandes dresseur, éliminant les déconnexions et blocages à l'entrée des Combats Doubles.
  - Correction de l'adresse `OV122_PARTY_EXP_ADDR` (`0x022A01CC`) sur `0.4.7` et ajout de payloads C dédiés par version (`0.4.5`, `0.4.6`, `0.4.7` FR / EN / USA).

- **Correctif d'Affichage des Magasins (Moteur Visuel 60 FPS)** :
  - Correction de la gestion du calque `BG 2` dans `Visual_UpdateCloudBg2` : la liste des articles (`Win 0`) et la description des objets (`Win 1`) dans les Boutiques Pokémon ne sont plus masquées ni décalées par le calque des ombres de nuages (en intérieur comme en extérieur).

- **Randomizer Dresseurs (Solo & Co-Op) & Re-Randomisation** :
  - Respect strict des 4 structures `trpoke.narc` de Project PM (`16`, `20`, `24` et `28` octets) sans débordement sur `ball_seal`, la nature ou les IVs, avec prise en charge de la conservation des objets tenus et des équipes dresseurs Co-Op (`trpoke[973..1944]`).
  - Possibilité de relancer le Randomizer plusieurs fois sur une ROM déjà randomisée (légendaires fixes, cadeaux, œufs et fossiles).

- **Bascule Binaire CT Infinies / Affichage IV-EV & Validation Automatique de ROM** :
  - Activation et désactivation binaires complètes pour les **CT Infinies** et l'**Affichage IV/EV** dans l'écran de résumé (`0.4.5`, `0.4.6`, `0.4.7`).
  - Intégration d'un validateur automatique post-patch vérifiant l'intégrité des tables NARC, des scripts, des banques de textes et des hooks `ARM9`/Overlays avant chaque sauvegarde, ainsi que la correction des textes FR manquants (Casino de Voilaroc, générique de fin, Moiteur).

---

## 🇬🇧 English

### What's New in Version 1.1.0

- **Fixed Co-Op Double Battles in SoulLocke & Nuzlocke Modes (`0.4.5` / `0.4.6` / `0.4.7`)**:
  - Fixed the `BattleDTO.mapLabelTextID` struct offset (`0x178`): 2nd and subsequent wild encounters on a route where a Pokémon was already caught now properly stay in **2v2 Co-Op Double Battles** with your partner instead of dropping to 1v1 solo battles.
  - Guarded the `ov122` network buffer during battles (`SoulLink_SyncTick`): SoulLocke sync packets no longer overwrite the 16-bit Battle State Hash (`exportBlk + 0xCA..0xCB`) or trainer command buffer, preventing Co-Op Double Battle disconnects and softlocks.
  - Corrected `OV122_PARTY_EXP_ADDR` (`0x022A01CC`) on `0.4.7` and added version-specific C payloads (`0.4.5`, `0.4.6`, `0.4.7` FR / EN / USA).

- **Fixed Poké Mart Shop Item List Display (60 FPS Visual Engine)**:
  - Fixed `BG 2` layer handling in `Visual_UpdateCloudBg2`: the shop item list (`Win 0`) and item descriptions (`Win 1`) in Poké Marts are no longer hidden or scroll-shifted by the cloud shadow layer (both indoors and outdoors).

- **Trainer Randomizer (Solo & Co-Op) & Idempotent Re-Randomization**:
  - Full support for all 4 Project PM `trpoke.narc` layouts (`16`, `20`, `24`, and `28` bytes) with zero overflow into `ball_seal`, nature, or IV fields, held item preservation, and Co-Op trainer party randomization (`trpoke[973..1944]`).
  - Static encounters, gifts, eggs, and fossils can now be re-randomized cleanly on an already-randomized ROM.

- **Binary Toggles for Infinite TMs / IV-EV Display & Automated ROM Validator**:
  - Complete binary enable/disable toggles for **Infinite TMs** and **Summary Screen IV/EV Display** across `0.4.5`, `0.4.6`, and `0.4.7`.
  - Built-in post-patch ROM validator checking NARC tables, scripts, text banks, and `ARM9`/Overlay hooks before saving, plus French text fixes (Veilstone Game Corner, End Credits, Damp battle messages).
