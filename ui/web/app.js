/* ==========================================================================
   PROJECT PM ADDON PATCHER & RANDOMIZER - APPLICATION LOGIC
   Author: Ekiii
   Bilingual Support (FR / EN) & Integrated Sinnoh Randomizer Wizard
   ========================================================================== */

let currentLang = 'en';
let translations = {};
let currentRomInfo = null;
let pokemonNames = {};

const SHINY_STEPS = {
  1: { val: 8, label_fr: '1/8192 (Vanilla Platine)', label_en: '1/8192 (Vanilla Platinum)' },
  2: { val: 16, label_fr: '1/4096 (Génération 6+)', label_en: '1/4096 (Generation 6+)' },
  3: { val: 32, label_fr: '1/2048 (x4)', label_en: '1/2048 (x4)' },
  4: { val: 64, label_fr: '~1/1024 (x8 - Équilibré)', label_en: '~1/1024 (x8 - Balanced)' },
  5: { val: 128, label_fr: '~1/512 (x16)', label_en: '~1/512 (x16)' },
  6: { val: 256, label_fr: '~1/256 (x32)', label_en: '~1/256 (x32)' },
  7: { val: 655, label_fr: '~1/100 (Ultra Shiny)', label_en: '~1/100 (Ultra Shiny)' }
};

// Wizard and Randomizer Global State
let currentWizardStep = 1;
let wizardState = {
  wilds: true,
  mode: 'area_1to1',
  rule: 'similar_strength',
  noleg: true,
  starters: false,
  starters_mode: 'vanilla',
  starters_any: false,
  shiny: 8,
  honey: true,
  statics: true,
  battles: false,
  gifts: false,
  trade_get: false,
  trade_want: false,
  wild_special: false,
  gba_slots: false,
  evolutions_mode: 'vanilla',
  trainers: true,
  coop_simstr: true,
  coop_noleg: true,
  types: false,
  abilities: false,
  movesets: false,
  seed: '',
  coop_seed: '',
  world_code: '',
  coop_code: ''
};

// ============================================================================
// WINDOW CONTROLS & SEAMLESS DRAG
// ============================================================================
function startWindowDrag(e) {
  // Handled natively by .pywebview-drag-region and CSS -webkit-app-region: drag
}

function windowMinimize() {
  if (window.pywebview && window.pywebview.api && window.pywebview.api.window_minimize) {
    window.pywebview.api.window_minimize();
  }
}

function windowToggleMaximize() {
  if (window.pywebview && window.pywebview.api && window.pywebview.api.window_toggle_maximize) {
    window.pywebview.api.window_toggle_maximize();
  }
}

function windowClose() {
  if (window.pywebview && window.pywebview.api && window.pywebview.api.window_close) {
    window.pywebview.api.window_close();
  }
}

// ============================================================================
// INITIALIZATION
// ============================================================================
window.addEventListener('pywebviewready', async () => {
  console.log('[App] PyWebView Ready. Initializing...');
  try {
    const initData = await window.pywebview.api.init_app();
    currentLang = initData.lang || 'en';
    translations = initData.translations || {};
    pokemonNames = initData.pokemon_names || {};
    
    // Set version
    const verEl = document.getElementById('app-version');
    if (verEl) verEl.innerText = initData.version || 'v1.0.4';
    
    // Set initial seeds & codes
    if (initData.initial_coop) {
      wizardState.coop_code = initData.initial_coop.code || '';
      wizardState.coop_seed = initData.initial_coop.seed || '';
    }
    if (initData.initial_world) {
      wizardState.world_code = initData.initial_world.code || '';
      wizardState.seed = initData.initial_world.seed || '';
    }

    const mainCoop = document.getElementById('main-coop-code');
    const mainWorld = document.getElementById('main-world-code');
    if (mainCoop) mainCoop.value = wizardState.coop_code;
    if (mainWorld) mainWorld.value = wizardState.world_code;

    // Apply language buttons active state
    document.getElementById('btn-lang-fr').classList.toggle('active', currentLang === 'fr');
    document.getElementById('btn-lang-en').classList.toggle('active', currentLang === 'en');

    applyTranslations(currentLang);
    updateQuickSummaryText();
    updateWizardStartersPreview();
    onMpModeChange();
    updateFooterStatus();

    // Check if user has selected language before (first-launch modal)
    if (!initData.has_selected_language) {
      openLanguageSelectModal();
    }

    // Restore saved user preferences & ROM paths
    if (initData.saved_config) {
      const cfg = initData.saved_config;
      if (cfg.last_source_rom) {
        document.getElementById('input-source-rom').value = cfg.last_source_rom;
        await processSelectedRom(cfg.last_source_rom);
      }
      if (cfg.last_output_rom) {
        document.getElementById('input-output-rom').value = cfg.last_output_rom;
      }
      if (cfg.addon_mode) {
        const rad = document.querySelector(`input[name="addon-mode"][value="${cfg.addon_mode}"]`);
        if (rad) {
          rad.checked = true;
          onAddonModeChange();
        }
      }
      if (cfg.visual_bg !== undefined) {
        const tBg = document.getElementById('toggle-visual-bg');
        if (tBg) tBg.checked = cfg.visual_bg;
      }
      if (cfg.visual_cam !== undefined) {
        const tCam = document.getElementById('toggle-visual-cam');
        if (tCam) tCam.checked = cfg.visual_cam;
      }
      if (cfg.backup_save !== undefined) {
        const tSav = document.getElementById('toggle-backup-save');
        if (tSav) tSav.checked = cfg.backup_save;
      }
      if (cfg.team_exp_share !== undefined) {
        const tExp = document.getElementById('toggle-team-exp-share');
        if (tExp) tExp.checked = cfg.team_exp_share;
      }
    }
  } catch (err) {
    console.error('[App Init Error]', err);
  }
});

function openLanguageSelectModal() {
  const modal = document.getElementById('modal-first-lang');
  if (modal) modal.style.display = 'flex';
}

async function chooseInitialLanguage(lang) {
  const modal = document.getElementById('modal-first-lang');
  if (modal) modal.style.display = 'none';
  await changeLang(lang);
}

function saveCurrentOptionsToConfig() {
  if (window.pywebview && window.pywebview.api && window.pywebview.api.save_app_config) {
    const addonRad = document.querySelector('input[name="addon-mode"]:checked');
    const dstInput = document.getElementById('input-dest-rom');
    const cfg = {
      addon_mode: addonRad ? addonRad.value : 'none',
      visual_bg: document.getElementById('toggle-visual-bg') ? document.getElementById('toggle-visual-bg').checked : true,
      visual_cam: document.getElementById('toggle-visual-cam') ? document.getElementById('toggle-visual-cam').checked : true,
      backup_save: document.getElementById('toggle-backup-save') ? document.getElementById('toggle-backup-save').checked : true,
      team_exp_share: document.getElementById('toggle-team-exp-share') ? document.getElementById('toggle-team-exp-share').checked : false,
      last_output_rom: dstInput ? dstInput.value : ''
    };
    window.pywebview.api.save_app_config(cfg);
  }
}

// ============================================================================
// TAB NAVIGATION
// ============================================================================
function switchTab(tabId) {
  document.querySelectorAll('.nav-tab').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

  const btn = document.getElementById(`tab-btn-${tabId}`);
  const content = document.getElementById(`tab-${tabId}`);
  if (btn && content) {
    btn.classList.add('active');
    content.classList.add('active');
  }
}

// ============================================================================
// LOCALIZATION (FR / EN DYNAMIC SWITCHING)
// ============================================================================
async function changeLang(lang) {
  if (lang === currentLang) return;
  currentLang = lang;
  
  document.getElementById('btn-lang-fr').classList.toggle('active', lang === 'fr');
  document.getElementById('btn-lang-en').classList.toggle('active', lang === 'en');

  try {
    const res = await window.pywebview.api.set_language(lang);
    if (res) {
      translations = res.translations || {};
      pokemonNames = res.pokemon_names || {};
    }
    applyTranslations(lang);
    updateQuickSummaryText();
    updateWizardStartersPreview();
    const step = document.getElementById('wiz-slider-shiny') ? document.getElementById('wiz-slider-shiny').value : 1;
    const cfg = SHINY_STEPS[step] || SHINY_STEPS[1];
    const shinyDisplay = document.getElementById('wiz-shiny-odds-display');
    if (shinyDisplay) {
      shinyDisplay.innerText = (lang === 'fr' ? cfg.label_fr : cfg.label_en);
    }
    onMpModeChange();

    // Re-render badges if ROMs analyzed
    if (currentRomInfo && currentRomInfo.valid) {
      renderPatcherBadges(currentRomInfo);
      updateMpDetectIndicator();
    }
    updateFooterStatus();
  } catch (e) {
    console.error('[Change Lang Error]', e);
  }
}

function applyTranslations(lang) {
  // 1. Text elements with data-i18n
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (translations[key] !== undefined) {
      el.innerHTML = translations[key];
    }
  });

  // 2. Input placeholders with data-i18n-placeholder
  document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
    const key = el.getAttribute('data-i18n-placeholder');
    if (translations[key] !== undefined) {
      el.placeholder = translations[key];
    }
  });

  // 3. Titles / Tooltips with data-i18n-title
  document.querySelectorAll('[data-i18n-title]').forEach(el => {
    const key = el.getAttribute('data-i18n-title');
    if (translations[key] !== undefined) {
      el.title = translations[key];
    }
  });
}

// ============================================================================
// FILE SELECTION & ROM DETECTION (MAIN WORKSPACE)
// ============================================================================
async function browseSourceRom() {
  try {
    const path = await window.pywebview.api.browse_source_rom();
    if (path) {
      document.getElementById('input-source-rom').value = path;
      await processSelectedRom(path);
    }
  } catch (e) {
    console.error('[Browse ROM Error]', e);
  }
}

function updateMpDetectIndicator() {
  const mpDetectEl = document.getElementById('mp-detect-indicator');
  if (!mpDetectEl || !currentRomInfo || !currentRomInfo.valid) return;
  const res = currentRomInfo;
  const mpSelect = document.getElementById('select-mp-mode');
  const effectiveLang = (mpSelect ? mpSelect.value : null) || (res.has_multiplayer ? res.mp_lang : res.lang) || 'fr';

  mpDetectEl.style.display = 'block';
  if (res.has_multiplayer) {
    const curLangStr = (res.mp_lang === 'fr') 
      ? (currentLang === 'fr' ? 'Français' : 'French') 
      : (currentLang === 'fr' ? 'USA / Anglais' : 'USA / English');
    const targetLangStr = (effectiveLang === 'fr') 
      ? (currentLang === 'fr' ? 'Français' : 'French') 
      : (currentLang === 'fr' ? 'USA / Anglais' : 'USA / English');

    if (effectiveLang !== res.mp_lang && effectiveLang !== 'none') {
      mpDetectEl.innerHTML = currentLang === 'fr'
        ? `<svg class="inline-svg text-amber" viewBox="0 0 16 16"><use href="#icon-lightning"></use></svg> <strong>Multijoueur détecté :</strong> Project PM v${res.mp_version || '0.4.5'} (${curLangStr}) &rarr; <strong>Changement vers le Multijoueur ${targetLangStr}</strong>`
        : `<svg class="inline-svg text-amber" viewBox="0 0 16 16"><use href="#icon-lightning"></use></svg> <strong>Multiplayer detected:</strong> Project PM v${res.mp_version || '0.4.5'} (${curLangStr}) &rarr; <strong>Switching to ${targetLangStr} Multiplayer</strong>`;
    } else {
      mpDetectEl.innerHTML = currentLang === 'fr'
        ? `<svg class="inline-svg text-emerald" viewBox="0 0 16 16"><use href="#icon-check"></use></svg> <strong>ROM Project PM détectée :</strong> v${res.mp_version || '0.4.5'} (${curLangStr}) &rarr; Prête pour mise à jour / réactualisation`
        : `<svg class="inline-svg text-emerald" viewBox="0 0 16 16"><use href="#icon-check"></use></svg> <strong>Project PM ROM detected:</strong> v${res.mp_version || '0.4.5'} (${curLangStr}) &rarr; Ready to update / refresh`;
    }
  } else {
    const langStr = (res.lang === 'fr') 
      ? (currentLang === 'fr' ? 'Platine France' : 'Platinum France') 
      : (currentLang === 'fr' ? 'Platine USA' : 'Platinum USA');
    const targetStr = (effectiveLang === 'fr') 
      ? (currentLang === 'fr' ? 'Français (v0.4.5)' : 'French (v0.4.5)') 
      : (currentLang === 'fr' ? 'USA / Anglais (v0.4.5)' : 'USA / English (v0.4.5)');
    mpDetectEl.innerHTML = currentLang === 'fr'
      ? `<svg class="inline-svg text-emerald" viewBox="0 0 16 16"><use href="#icon-check"></use></svg> <strong>ROM Vanilla détectée :</strong> ${langStr} &rarr; Multijoueur ${targetStr} sélectionné automatiquement`
      : `<svg class="inline-svg text-emerald" viewBox="0 0 16 16"><use href="#icon-check"></use></svg> <strong>Vanilla ROM detected:</strong> ${langStr} &rarr; Multiplayer ${targetStr} auto-selected`;
  }

  if (res.is_randomized) {
    const randNote = currentLang === 'fr'
      ? `<div style="margin-top: 5px; font-size: 11px; color: #a78bfa;"><svg class="inline-svg text-purple" viewBox="0 0 16 16"><use href="#icon-check"></use></svg> <strong>Randomisation existante détectée :</strong> Les tables aléatoires seront automatiquement préservées et ré-appliquées à la fin du patch.</div>`
      : `<div style="margin-top: 5px; font-size: 11px; color: #a78bfa;"><svg class="inline-svg text-purple" viewBox="0 0 16 16"><use href="#icon-check"></use></svg> <strong>Existing randomization detected:</strong> Tables will be automatically preserved and re-applied at the end of patching.</div>`;
    mpDetectEl.innerHTML += randNote;
  }
}

function updateFooterStatus() {
  const indicator = document.getElementById('footer-pulse-indicator');
  const textEl = document.getElementById('footer-status-text');
  if (!indicator || !textEl) return;

  if (!currentRomInfo || !currentRomInfo.path) {
    indicator.className = 'pulse-indicator waiting';
    textEl.innerText = translations['footer_status_waiting'] || (currentLang === 'fr' 
      ? "En attente d'une ROM valide (USA rev1 ou FR)..." 
      : "Waiting for a valid ROM (USA rev1 or FR)...");
    return;
  }

  if (!currentRomInfo.valid) {
    indicator.className = 'pulse-indicator error';
    textEl.innerText = translations['footer_status_incompatible'] || (currentLang === 'fr' 
      ? "ROM non compatible (Platine USA rev1 ou FR requis)" 
      : "Incompatible ROM (Platinum USA rev1 or FR required)");
    return;
  }

  // Check language compatibility for clean base ROMs
  const mpSelect = document.getElementById('select-mp-mode');
  const mpMode = mpSelect ? mpSelect.value : 'fr';
  if (!currentRomInfo.has_multiplayer) {
    if (currentRomInfo.lang === 'fr' && mpMode === 'en') {
      indicator.className = 'pulse-indicator error';
      textEl.innerText = currentLang === 'fr' 
        ? "La ROM FR nécessite le patch Multijoueur FR (ou utilisez USA rev1 pour l'anglais)" 
        : "French ROM requires FR Multiplayer patch (or use USA rev1 for English)";
      return;
    }
  }

  indicator.className = 'pulse-indicator ready';
  textEl.innerText = currentLang === 'fr' 
    ? `Prêt à patcher (${currentRomInfo.game || 'Platine'})` 
    : `Ready to patch (${currentRomInfo.game || 'Platinum'})`;
}

async function processSelectedRom(path) {
  const box = document.getElementById('rom-status-box');
  box.style.display = 'block';
  document.getElementById('rom-title-display').innerText = currentLang === 'fr' ? "Analyse en cours..." : "Analyzing ROM...";
  document.getElementById('rom-badges-container').innerHTML = '';

  const res = await window.pywebview.api.analyze_rom(path);
  currentRomInfo = res;
  
  if (res.valid) {
    document.getElementById('rom-title-display').innerText = `${res.game} (${res.game_code})`;
    document.getElementById('rom-size-display').innerText = `${res.size_mb} MB`;
    
    // Auto-detect & set Multiplayer base language:
    const mpSelect = document.getElementById('select-mp-mode');
    const effectiveLang = (res.has_multiplayer ? res.mp_lang : res.lang) || 'fr';
    if (mpSelect) {
      mpSelect.value = effectiveLang;
    }

    updateMpDetectIndicator();

    // Addon mode selection:
    if (res.has_soullocke) {
      const radioRestore = document.querySelector('input[name="addon-mode"][value="restore"]');
      if (radioRestore) radioRestore.checked = true;
    } else {
      const radioNone = document.querySelector('input[name="addon-mode"][value="none"]');
      if (radioNone) radioNone.checked = true;
    }

    // Sync visual options if already present on ROM
    const toggleBg = document.getElementById('toggle-visual-bg');
    if (toggleBg && res.has_visualplus_bg) {
      toggleBg.checked = true;
    }
    const toggleCam = document.getElementById('toggle-visual-cam');
    if (toggleCam && res.has_visualplus_cam) {
      toggleCam.checked = true;
    }

    // Sync Team EXP Share option from ROM
    const toggleExp = document.getElementById('toggle-team-exp-share');
    if (toggleExp && res.has_exp_share !== undefined) {
      toggleExp.checked = !!res.has_exp_share;
    }

    // Suggest in-place update by default for existing ProjectPM ROMs
    const overwriteToggle = document.getElementById('toggle-overwrite-source');
    if (overwriteToggle) {
      overwriteToggle.checked = !!res.has_multiplayer;
    }

    // Update destination path & UI buttons & SoulLocke badges
    onMpModeChange();

    renderPatcherBadges(res);
    updateFooterStatus();
  } else {
    document.getElementById('rom-title-display').innerText = currentLang === 'fr' ? "Fichier Invalide" : "Invalid File";
    document.getElementById('rom-badges-container').innerHTML = `<span class="status-badge amber">${res.error || 'Erreur'}</span>`;
    updateFooterStatus();
  }
}

function renderPatcherBadges(res) {
  const badgesHtml = res.badges.map(b => {
    const label = (b.key && translations[b.key]) ? translations[b.key] : b.label;
    return `<span class="status-badge ${b.color}">${label}</span>`;
  }).join('');
  document.getElementById('rom-badges-container').innerHTML = badgesHtml;
}

async function browseDestRom() {
  try {
    const sug = document.getElementById('input-dest-rom').value;
    const defaultName = sug ? sug.split('/').pop() : 'ProjectPM_modded.nds';
    const path = await window.pywebview.api.browse_save_rom(defaultName);
    if (path) {
      document.getElementById('input-dest-rom').value = path;
      saveCurrentOptionsToConfig();
    }
  } catch (e) {
    console.error('[Browse Dest Error]', e);
  }
}

async function browseCustomPatch() {
  try {
    const path = await window.pywebview.api.browse_patch_file();
    if (path) {
      document.getElementById('input-custom-patch').value = path;
    }
  } catch (e) {
    console.error('[Browse Patch Error]', e);
  }
}

// Drag & drop support
window.addEventListener('dragover', (e) => e.preventDefault());
window.addEventListener('drop', (e) => {
  e.preventDefault();
  if (e.dataTransfer && e.dataTransfer.files.length > 0) {
    const f = e.dataTransfer.files[0];
    if (f.path && f.path.toLowerCase().endsWith('.nds')) {
      const p = f.path.replace(/\\/g, '/');
      document.getElementById('input-source-rom').value = p;
      processSelectedRom(p);
    }
  }
});

// ============================================================================
// PATCHER & MODES PIPELINE
// ============================================================================
function onMpModeChange() {
  const mpSelect = document.getElementById('select-mp-mode');
  const mpVal = mpSelect ? mpSelect.value : 'fr';
  const isEn = (mpVal === 'en');
  const isNone = (mpVal === 'none');

  const soullinkBadge = document.getElementById('soullink-sync-badge');
  const soullinkNote = document.getElementById('soullink-lang-note');
  const restoreBadge = document.getElementById('restore-sync-badge');

  if (isNone) {
    if (soullinkBadge) {
      soullinkBadge.className = 'status-badge slate';
      soullinkBadge.innerText = currentLang === 'fr' ? 'Base requise' : 'Base required';
    }
    if (soullinkNote) {
      soullinkNote.innerHTML = currentLang === 'fr'
        ? '<svg class="inline-svg text-amber" viewBox="0 0 16 16"><use href="#icon-warning"></use></svg> <em>Nécessite une base multijoueur active pour fonctionner.</em>'
        : '<svg class="inline-svg text-amber" viewBox="0 0 16 16"><use href="#icon-warning"></use></svg> <em>Requires an active multiplayer base to work.</em>';
    }
    if (restoreBadge) {
      restoreBadge.innerText = 'Project PM';
    }
  } else if (isEn) {
    if (soullinkBadge) {
      soullinkBadge.className = 'status-badge blue';
      soullinkBadge.innerText = currentLang === 'fr' ? 'Mod EN' : 'EN Mod';
    }
    if (soullinkNote) {
      soullinkNote.innerHTML = currentLang === 'fr'
        ? '<svg class="inline-svg" viewBox="0 0 16 16"><use href="#icon-lightning"></use></svg> <strong>Langue du mod : English / USA</strong> (définie automatiquement par la base multijoueur).'
        : '<svg class="inline-svg" viewBox="0 0 16 16"><use href="#icon-lightning"></use></svg> <strong>Mod language: English / USA</strong> (automatically defined by multiplayer base).';
    }
    if (restoreBadge) {
      restoreBadge.innerText = 'Project PM USA';
    }
  } else {
    // fr
    if (soullinkBadge) {
      soullinkBadge.className = 'status-badge emerald';
      soullinkBadge.innerText = currentLang === 'fr' ? 'Mod FR' : 'FR Mod';
    }
    if (soullinkNote) {
      soullinkNote.innerHTML = currentLang === 'fr'
        ? '<svg class="inline-svg" viewBox="0 0 16 16"><use href="#icon-lightning"></use></svg> <strong>Langue du mod : Français</strong> (définie automatiquement par la base multijoueur).'
        : '<svg class="inline-svg" viewBox="0 0 16 16"><use href="#icon-lightning"></use></svg> <strong>Mod language: French</strong> (automatically defined by multiplayer base).';
    }
    if (restoreBadge) {
      restoreBadge.innerText = 'Project PM FR';
    }
  }

  updateMpDetectIndicator();
  onAddonModeChange();
}

function onToggleOverwriteSource() {
  onAddonModeChange();
}

function onAddonModeChange() {
  // Update visual active state of radio cards
  document.querySelectorAll('input[name="addon-mode"]').forEach(r => {
    const card = r.closest('.pixel-radio-card');
    if (card) card.classList.toggle('active', r.checked);
  });

  const addonRadio = document.querySelector('input[name="addon-mode"]:checked');
  const addonVal = addonRadio ? addonRadio.value : 'none';
  const dstInput = document.getElementById('input-dest-rom');
  const dstBtn = document.getElementById('i18n-btn-browse-dst');
  const btn = document.getElementById('btn-start-patch');
  const btnSpan = btn ? btn.querySelector('span') : null;

  const randToggle = document.getElementById('toggle-enable-randomizer');
  const randEnabled = randToggle ? randToggle.checked : false;
  const randSuffix = randEnabled ? '_Randomized' : '';

  const overwriteToggle = document.getElementById('toggle-overwrite-source');
  const isOverwrite = !!(overwriteToggle && overwriteToggle.checked);

  if (currentRomInfo && currentRomInfo.path) {
    const srcPath = currentRomInfo.path;
    const dirName = srcPath.substring(0, srcPath.lastIndexOf('/'));
    const baseName = srcPath.substring(srcPath.lastIndexOf('/') + 1).replace(/\.nds$/i, '');
    const mpMode = document.getElementById('select-mp-mode').value;
    const lang = (mpMode === 'en') ? 'EN' : 'FR';

    if (isOverwrite) {
      dstInput.value = srcPath;
      dstInput.disabled = true;
      dstInput.style.opacity = '0.7';
      if (dstBtn) dstBtn.disabled = true;

      if (addonVal === 'restore') {
        if (btnSpan) {
          btnSpan.innerText = randEnabled
            ? (currentLang === 'fr' ? "RESTAURER & RANDOMISER SUR PLACE" : "RESTORE & RANDOMIZE IN-PLACE")
            : (currentLang === 'fr' ? "RESTAURER LA ROM SUR PLACE (PROPRE)" : "RESTORE CLEAN ROM IN-PLACE");
        }
      } else if (addonVal === 'soullink') {
        if (btnSpan) {
          btnSpan.innerText = randEnabled
            ? (currentLang === 'fr' ? `INJECTER SOULLOCKE & RANDOMISER SUR PLACE (${lang})` : `INJECT SOULLOCKE & RANDOMIZE IN-PLACE (${lang})`)
            : (currentLang === 'fr' ? `METTRE À JOUR & INJECTER SOULLOCKE SUR PLACE (${lang})` : `UPDATE & INJECT SOULLOCKE IN-PLACE (${lang})`);
        }
      } else {
        if (btnSpan) {
          btnSpan.innerText = randEnabled
            ? (currentLang === 'fr' ? "METTRE À JOUR & RANDOMISER SUR PLACE" : "UPDATE & RANDOMIZE ROM IN-PLACE")
            : (translations['btn_execute_update_rom'] || (currentLang === 'fr' ? "METTRE À JOUR LA ROM SUR PLACE" : "UPDATE ROM IN-PLACE"));
        }
      }
    } else {
      dstInput.disabled = false;
      dstInput.style.opacity = '1';
      if (dstBtn) dstBtn.disabled = false;

      if (addonVal === 'restore') {
        dstInput.value = `${dirName}/${baseName}_Clean${randSuffix}.nds`;
        if (btnSpan) {
          btnSpan.innerText = randEnabled
            ? (currentLang === 'fr' ? "RESTAURER & RANDOMISER LA ROM" : "RESTORE & RANDOMIZE ROM")
            : (currentLang === 'fr' ? "RESTAURER LA ROM PROPRE (RETIRER SOULLOCKE)" : "RESTORE CLEAN ROM (UNINSTALL SOULLOCKE)");
        }
      } else if (addonVal === 'soullink') {
        dstInput.value = `${dirName}/ProjectPM_${lang}_SoulLocke${randSuffix}.nds`;
        if (btnSpan) {
          btnSpan.innerText = randEnabled
            ? (currentLang === 'fr' ? `INJECTER SOUL LINK & RANDOMISER LA ROM (${lang})` : `INJECT SOUL LINK & RANDOMIZE ROM (${lang})`)
            : (currentLang === 'fr' ? `INJECTER LE MOD SOUL LINK / SOULLOCKE (${lang})` : `INJECT SOUL LINK / SOULLOCKE MOD (${lang})`);
        }
      } else {
        // none
        if (currentRomInfo.has_multiplayer) {
          dstInput.value = `${dirName}/${baseName}_Modded${randSuffix}.nds`;
        } else {
          dstInput.value = `${dirName}/ProjectPM_${lang}_Multiplayer${randSuffix}.nds`;
        }
        if (btnSpan) {
          btnSpan.innerText = randEnabled
            ? (translations['btn_execute_patch_and_rand'] || (currentLang === 'fr' ? "APPLIQUER LES PATCHS & RANDOMISER LA ROM" : "APPLY PATCHES & RANDOMIZE ROM"))
            : (translations['btn_execute_patch'] || (currentLang === 'fr' ? "APPLIQUER LES PATCHS SUR LA ROM" : "APPLY PATCHES TO ROM"));
        }
      }
    }
  } else {
    if (btnSpan) {
      btnSpan.innerText = randEnabled
        ? (translations['btn_execute_patch_and_rand'] || (currentLang === 'fr' ? "APPLIQUER LES PATCHS & RANDOMISER LA ROM" : "APPLY PATCHES & RANDOMIZE ROM"))
        : (translations['btn_execute_patch'] || (currentLang === 'fr' ? "APPLIQUER LES PATCHS SUR LA ROM" : "APPLY PATCHES TO ROM"));
    }
  }
  saveCurrentOptionsToConfig();
  updateFooterStatus();
}

async function startPatching() {
  const inRom = document.getElementById('input-source-rom').value.trim();
  const outRom = document.getElementById('input-dest-rom').value.trim();

  if (!inRom) {
    alert(currentLang === 'fr' ? "Veuillez sélectionner une ROM source Pokémon Platine." : "Please select a Pokémon Platinum source ROM.");
    return;
  }
  if (!outRom) {
    alert(currentLang === 'fr' ? "Veuillez spécifier l'emplacement de la ROM de destination." : "Please specify the destination ROM path.");
    return;
  }

  const btn = document.getElementById('btn-start-patch');
  btn.disabled = true;
  document.getElementById('patch-progress-fill').style.width = '0%';
  document.getElementById('patch-status-text').innerText = currentLang === 'fr' ? "En cours d'application..." : "Patching in progress...";
  document.getElementById('patch-log').innerText = '';

  const mpMode = document.getElementById('select-mp-mode').value;
  const addonRadio = document.querySelector('input[name="addon-mode"]:checked');
  const addonVal = addonRadio ? addonRadio.value : 'none';
  const effectiveVariant = (mpMode === 'en') ? 'en' : 'fr';

  const randToggle = document.getElementById('toggle-enable-randomizer');
  const randEnabled = randToggle ? randToggle.checked : false;

  const options = {
    mp_enabled: mpMode !== 'none',
    mp_version: mpMode === 'none' ? 'none' : effectiveVariant,
    sl_enabled: addonVal === 'soullink',
    sl_mode: addonVal === 'restore' ? 'restore' : 'apply',
    sl_variant: effectiveVariant,
    bg_opt: document.getElementById('toggle-visual-bg').checked ? 'builtin' : 'none',
    cam_opt: document.getElementById('toggle-visual-cam').checked ? 'builtin' : 'none',
    backup_save: document.getElementById('toggle-backup-save').checked,
    team_exp_share: document.getElementById('toggle-team-exp-share') ? document.getElementById('toggle-team-exp-share').checked : false,
    custom_patch: document.getElementById('input-custom-patch').value.trim() || null,
    rand_enabled: randEnabled,
    rand_settings: randEnabled ? getWizardSettingsObject() : null
  };

  try {
    await window.pywebview.api.run_patching(inRom, outRom, options);
  } catch (e) {
    console.error('[Patch Execution Error]', e);
    btn.disabled = false;
  }
}

// Window callbacks from Python for Patcher
window.onPatchLog = (msg) => {
  const el = document.getElementById('patch-log');
  el.innerText += msg + '\n';
  el.scrollTop = el.scrollHeight;
};

window.onPatchProgress = (pct, msg) => {
  const fill = document.getElementById('patch-progress-fill');
  fill.style.width = `${Math.round(pct * 100)}%`;
  document.getElementById('patch-status-text').innerText = msg;
};

window.onPatchComplete = (ok, msg) => {
  document.getElementById('btn-start-patch').disabled = false;
  document.getElementById('patch-status-text').innerText = ok ? (currentLang === 'fr' ? "Terminé !" : "Done!") : (currentLang === 'fr' ? "Erreur" : "Error");
  updateFooterStatus();
  if (ok) {
    document.getElementById('patch-progress-fill').style.width = '100%';
    alert((currentLang === 'fr' ? "Succès !\n" : "Success!\n") + msg);
  } else {
    alert((currentLang === 'fr' ? "Erreur lors du patch :\n" : "Patch error:\n") + msg);
  }
};

// ============================================================================
// INTEGRATED RANDOMIZER & STEP-BY-STEP WIZARD
// ============================================================================
function onToggleRandomizerChange() {
  const toggle = document.getElementById('toggle-enable-randomizer');
  const activeBox = document.getElementById('rand-active-controls');
  const badge = document.getElementById('badge-rand-state');
  const isChecked = toggle ? toggle.checked : false;

  if (activeBox) activeBox.style.display = isChecked ? 'block' : 'none';
  if (badge) {
    if (isChecked) {
      badge.className = 'status-badge emerald';
      badge.innerText = translations['rand_badge_active'] || (currentLang === 'fr' ? 'Randomizer Activé' : 'Randomizer Active');
    } else {
      badge.className = 'status-badge slate';
      badge.innerText = translations['rand_badge_disabled'] || (currentLang === 'fr' ? 'Désactivé' : 'Disabled');
    }
  }

  if (isChecked) {
    updateQuickSummaryText();
    refreshWizardCodes();
  }

  onAddonModeChange();
}

function openRandomizerWizard(mode) {
  const modal = document.getElementById('modal-randomizer');
  if (modal) modal.style.display = 'flex';
  
  if (mode === 'codes') {
    switchModalTab('codes');
  } else {
    switchModalTab('wizard');
    goToWizardStep(1);
  }
  
  applyTranslations(currentLang);
  syncWizardUIFromState();
  updateWizardStartersPreview();
  const step = document.getElementById('wiz-slider-shiny') ? document.getElementById('wiz-slider-shiny').value : 1;
  const cfg = SHINY_STEPS[step] || SHINY_STEPS[1];
  const shinyDisplay = document.getElementById('wiz-shiny-odds-display');
  if (shinyDisplay) {
    shinyDisplay.innerText = (currentLang === 'fr' ? cfg.label_fr : cfg.label_en);
  }
  refreshWizardCodes();
}

function closeRandomizerModal() {
  const modal = document.getElementById('modal-randomizer');
  if (modal) modal.style.display = 'none';
}

function switchModalTab(tab) {
  const btnWiz = document.getElementById('modal-tab-btn-wizard');
  const btnCodes = document.getElementById('modal-tab-btn-codes');
  const panelWiz = document.getElementById('modal-tab-wizard');
  const panelCodes = document.getElementById('modal-tab-codes');

  if (tab === 'codes') {
    if (btnWiz) btnWiz.classList.remove('active');
    if (btnCodes) btnCodes.classList.add('active');
    if (panelWiz) panelWiz.classList.remove('active');
    if (panelCodes) panelCodes.classList.add('active');
  } else {
    if (btnWiz) btnWiz.classList.add('active');
    if (btnCodes) btnCodes.classList.remove('active');
    if (panelWiz) panelWiz.classList.add('active');
    if (panelCodes) panelCodes.classList.remove('active');
  }
}

function goToWizardStep(stepNum) {
  currentWizardStep = stepNum;

  // Update Category Badge & Counter
  const catBadge = document.getElementById('wiz-cat-badge');
  const counterEl = document.getElementById('wiz-step-counter');

  let catKey = 'wiz_badge_wilds';
  if (stepNum >= 1 && stepNum <= 4) catKey = 'wiz_badge_wilds';
  else if (stepNum >= 5 && stepNum <= 6) catKey = 'wiz_badge_starters';
  else if (stepNum >= 7 && stepNum <= 11) catKey = 'wiz_badge_events';
  else if (stepNum === 12) catKey = 'wiz_badge_evolutions';
  else if (stepNum >= 13 && stepNum <= 15) catKey = 'wiz_badge_coop';
  else if (stepNum === 16) catKey = 'wiz_badge_summary';

  if (catBadge) {
    catBadge.innerText = translations[catKey] || (currentLang === 'fr' ? 'CONFIGURATEUR' : 'CONFIGURATOR');
  }

  if (counterEl) {
    if (stepNum <= 15) {
      const qPrefix = translations['wiz_counter_prefix'] || (currentLang === 'fr' ? 'Question' : 'Question');
      const qOf = translations['wiz_counter_of'] || (currentLang === 'fr' ? 'sur' : 'of');
      counterEl.innerText = `${qPrefix} ${stepNum} ${qOf} 15`;
    } else {
      counterEl.innerText = translations['wiz_badge_summary'] || (currentLang === 'fr' ? 'Résumé & Codes' : 'Summary & Codes');
    }
  }

  // Update Pills (1 to 16) & Panes
  for (let i = 1; i <= 16; i++) {
    const pill = document.getElementById(`pill-${i}`);
    if (pill) {
      pill.classList.toggle('active', i === stepNum);
      pill.classList.toggle('completed', i < stepNum);
    }
    const pane = document.getElementById(`wizard-step-${i}`);
    if (pane) {
      pane.classList.toggle('active', i === stepNum);
    }
  }

  // Update Progress Bar
  const progFill = document.getElementById('wiz-progress-fill');
  if (progFill) {
    const pct = Math.round(((stepNum - 1) / 15) * 100);
    progFill.style.width = `${Math.max(7, pct)}%`;
  }

  // Update Navigation Buttons
  const btnPrev = document.getElementById('btn-wiz-prev');
  const btnNext = document.getElementById('btn-wiz-next');
  const btnApply = document.getElementById('btn-wiz-apply');

  if (btnPrev) btnPrev.disabled = (stepNum === 1);
  if (stepNum === 16) {
    if (btnNext) btnNext.style.display = 'none';
    if (btnApply) btnApply.style.display = 'inline-flex';
    refreshWizardCodes();
  } else {
    if (btnNext) btnNext.style.display = 'inline-flex';
    if (btnApply) btnApply.style.display = 'none';
  }
}

function wizardPrevStep() {
  if (currentWizardStep > 1) {
    goToWizardStep(currentWizardStep - 1);
  }
}

function wizardNextStep() {
  if (currentWizardStep < 16) {
    goToWizardStep(currentWizardStep + 1);
  }
}

function setWizardWilds(val) {
  wizardState.wilds = val;
  syncWizardUIFromState();
  refreshWizardCodes();
}

function setWizardMode(mode) {
  wizardState.mode = mode;
  syncWizardUIFromState();
  refreshWizardCodes();
}

function setWizardSimstr(val) {
  wizardState.rule = val ? 'similar_strength' : 'none';
  syncWizardUIFromState();
  refreshWizardCodes();
}

function setWizardNoleg(val) {
  wizardState.noleg = val;
  syncWizardUIFromState();
  refreshWizardCodes();
}

function setWizardStarters(mode) {
  wizardState.starters_mode = mode;
  syncWizardUIFromState();
  updateWizardStartersPreview();
  refreshWizardCodes();
}

function setWizardHoney(val) {
  wizardState.honey = val;
  syncWizardUIFromState();
  refreshWizardCodes();
}

function setWizardStatics(val) {
  wizardState.statics = val;
  syncWizardUIFromState();
  refreshWizardCodes();
}

function setWizardBattles(val) {
  wizardState.battles = val;
  syncWizardUIFromState();
  refreshWizardCodes();
}

function setWizardGifts(val) {
  wizardState.gifts = val;
  wizardState.trade_get = val;
  wizardState.trade_want = val;
  syncWizardUIFromState();
  refreshWizardCodes();
}

function setWizardSpecial(val) {
  wizardState.wild_special = val;
  wizardState.gba_slots = val;
  syncWizardUIFromState();
  refreshWizardCodes();
}

function setWizardEvolutions(mode) {
  wizardState.evolutions_mode = mode;
  syncWizardUIFromState();
  refreshWizardCodes();
}

function setWizardTrainers(val) {
  wizardState.trainers = val;
  syncWizardUIFromState();
  refreshWizardCodes();
}

function setWizardCoopBal(val) {
  wizardState.coop_simstr = val;
  wizardState.coop_noleg = val;
  syncWizardUIFromState();
  refreshWizardCodes();
}

function onWizardSettingsChanged() {
  const toggleTypes = document.getElementById('wiz-toggle-types');
  if (toggleTypes) wizardState.types = toggleTypes.checked;
  const toggleAbilities = document.getElementById('wiz-toggle-abilities');
  if (toggleAbilities) wizardState.abilities = toggleAbilities.checked;
  const toggleMovesets = document.getElementById('wiz-toggle-movesets');
  if (toggleMovesets) wizardState.movesets = toggleMovesets.checked;

  updateQuickSummaryText();
  refreshWizardCodes();
}

function onWizardStartersChanged() {
  const startersRadio = document.querySelector('input[name="wiz-starters-mode"]:checked');
  wizardState.starters_mode = startersRadio ? startersRadio.value : 'vanilla';
  document.querySelectorAll('input[name="wiz-starters-mode"]').forEach(r => {
    const card = r.closest('.pixel-radio-card');
    if (card) card.classList.toggle('active', r.checked);
  });
  updateWizardStartersPreview();
  onWizardSettingsChanged();
}

function onWizardShinyChanged() {
  const step = document.getElementById('wiz-slider-shiny').value;
  const cfg = SHINY_STEPS[step] || SHINY_STEPS[1];
  wizardState.shiny = cfg.val;
  document.getElementById('wiz-shiny-odds-display').innerText = (currentLang === 'fr' ? cfg.label_fr : cfg.label_en);
  onWizardSettingsChanged();
}

function updateWizardStartersPreview() {
  const mode = wizardState.starters_mode;
  if (mode === 'vanilla') {
    setWizardStarterSlot(1, 387, pokemonNames['387'] || (currentLang === 'fr' ? "Tortipouss" : "Turtwig"), 'assets/starter_387.png');
    setWizardStarterSlot(2, 390, pokemonNames['390'] || (currentLang === 'fr' ? "Ouisticram" : "Chimchar"), 'assets/starter_390.png');
    setWizardStarterSlot(3, 393, pokemonNames['393'] || (currentLang === 'fr' ? "Tiplouf" : "Piplup"), 'assets/starter_393.png');
  } else {
    const randLabel = currentLang === 'fr' ? "Aléatoire" : "Random";
    setWizardStarterSlot(1, "???", randLabel, null);
    setWizardStarterSlot(2, "???", randLabel, null);
    setWizardStarterSlot(3, "???", randLabel, null);
  }
}

function setWizardStarterSlot(slotNum, id, name, spritePath) {
  const idEl = document.getElementById(`wiz-starter-${slotNum}-id`);
  const nameEl = document.getElementById(`wiz-starter-${slotNum}-name`);
  const iconEl = document.getElementById(`wiz-starter-${slotNum}-icon`);

  if (idEl) idEl.innerText = typeof id === 'number' ? `#${id}` : id;
  if (nameEl) nameEl.innerText = name;

  if (iconEl) {
    if (spritePath) {
      iconEl.innerHTML = `<img src="${spritePath}" class="starter-sprite-img" alt="${name}">`;
    } else {
      iconEl.innerHTML = `
        <div class="starter-rand-badge">
          <svg class="starter-rand-ball" viewBox="0 0 32 32">
            <ellipse cx="16" cy="30" rx="9" ry="1.8" fill="rgba(0,0,0,0.3)"/>
            <circle cx="16" cy="15.5" r="13" fill="#0f172a"/>
            <path d="M 3 15.5 A 13 13 0 0 1 29 15.5 Z" fill="#ef4444"/>
            <path d="M 6.5 12 A 10.5 10.5 0 0 1 18 5" fill="none" stroke="rgba(255,255,255,0.7)" stroke-width="1.8" stroke-linecap="round"/>
            <circle cx="8.5" cy="8" r="1.2" fill="#ffffff"/>
            <path d="M 3 15.5 A 13 13 0 0 0 29 15.5 Z" fill="#f8fafc"/>
            <rect x="3" y="14.3" width="26" height="2.4" fill="#0f172a"/>
            <circle cx="16" cy="15.5" r="4.8" fill="#0f172a"/>
            <circle cx="16" cy="15.5" r="3.2" fill="#e2e8f0"/>
            <circle cx="16" cy="15.5" r="2.2" fill="#ffffff"/>
          </svg>
          <svg class="starter-qmark-svg" viewBox="0 0 24 24">
            <path fill="#facc15" stroke="#78350f" stroke-width="1.2" stroke-linejoin="round" d="M12 2C8.7 2 6 4.7 6 8h3c0-1.7 1.3-3 3-3s3 1.3 3 3c0 1.2-.7 2-1.7 2.7C11.9 11.6 11 12.8 11 15h2c0-1.4.7-2.1 1.7-2.8 1.2-.8 2.3-2 2.3-4.2 0-3.3-2.7-6-6-6zm-1 15v3h3v-3h-3z"/>
          </svg>
        </div>`;
    }
  }
}

function getWizardSettingsObject() {
  return {
    wilds: wizardState.wilds,
    mode: wizardState.mode,
    rule: wizardState.rule,
    noleg: wizardState.noleg,
    starters: wizardState.starters_mode !== 'vanilla',
    starters_any: wizardState.starters_mode === 'any',
    honey: wizardState.honey,
    statics: wizardState.statics,
    evolutions_mode: wizardState.evolutions_mode,
    battles: wizardState.battles,
    gifts: wizardState.gifts,
    trade_get: wizardState.trade_get,
    trade_want: wizardState.trade_want,
    wild_special: wizardState.wild_special,
    gba_slots: wizardState.gba_slots,
    trainers: wizardState.trainers,
    coop_simstr: wizardState.coop_simstr,
    coop_noleg: wizardState.coop_noleg,
    types: wizardState.types,
    abilities: wizardState.abilities,
    movesets: wizardState.movesets,
    shiny: wizardState.shiny,
    seed: wizardState.seed,
    coop_seed: wizardState.coop_seed
  };
}

async function refreshWizardCodes() {
  if (!wizardState.seed) {
    wizardState.seed = Math.floor(1000000000 + Math.random() * 9000000000).toString();
  }
  if (!wizardState.coop_seed) {
    wizardState.coop_seed = Math.floor(1000000000 + Math.random() * 9000000000).toString();
  }

  const s = getWizardSettingsObject();
  try {
    const [wRes, cRes] = await Promise.all([
      window.pywebview.api.generate_world_code(s),
      window.pywebview.api.generate_coop_code(s)
    ]);
    if (wRes && wRes.code) {
      wizardState.world_code = wRes.code;
      const wEl = document.getElementById('wiz-output-world-code');
      const wMain = document.getElementById('main-world-code');
      if (wEl) wEl.value = wRes.code;
      if (wMain) wMain.value = wRes.code;
      const wSeed = document.getElementById('wiz-world-seed-display');
      if (wSeed) wSeed.innerText = wizardState.seed;
    }
    if (cRes && cRes.code) {
      wizardState.coop_code = cRes.code;
      const cEl = document.getElementById('wiz-output-coop-code');
      const cMain = document.getElementById('main-coop-code');
      if (cEl) cEl.value = cRes.code;
      if (cMain) cMain.value = cRes.code;
      const cSeed = document.getElementById('wiz-coop-seed-display');
      if (cSeed) cSeed.innerText = wizardState.coop_seed;
    }
  } catch (err) {
    console.error('[Refresh Codes Error]', err);
  }
}

function updateQuickSummaryText() {
  const parts = [];
  if (wizardState.mode === 'area_1to1') parts.push(currentLang === 'fr' ? 'Équilibré par Zone' : 'Area 1-to-1');
  else if (wizardState.mode === 'global_1to1') parts.push(currentLang === 'fr' ? 'Global 1-pour-1' : 'Global 1-to-1');
  else parts.push(currentLang === 'fr' ? 'Aléatoire (Chaos)' : 'Random');

  if (wizardState.rule === 'similar_strength') parts.push(currentLang === 'fr' ? 'Force similaire' : 'Similar strength');
  if (wizardState.noleg) parts.push(currentLang === 'fr' ? 'Sans légendaires' : 'No legendaries');

  if (wizardState.starters_mode === 'vanilla') parts.push(currentLang === 'fr' ? 'Starters Vanilla' : 'Vanilla Starters');
  else if (wizardState.starters_mode === 'balanced') parts.push(currentLang === 'fr' ? 'Starters Équilibrés' : 'Balanced Starters');
  else parts.push(currentLang === 'fr' ? 'Starters Aléatoires' : 'Random Starters');

  if (wizardState.evolutions_mode === 'similar_strength') parts.push(currentLang === 'fr' ? 'Évolutions Équilibrées' : 'Similar Str. Evolutions');
  else if (wizardState.evolutions_mode === 'chaos') parts.push(currentLang === 'fr' ? 'Évolutions Chaos' : 'Chaos Evolutions');

  for (const [k, v] of Object.entries(SHINY_STEPS)) {
    if (v.val === wizardState.shiny) {
      parts.push('Shiny ' + (currentLang === 'fr' ? v.label_fr.split(' ')[0] : v.label_en.split(' ')[0]));
      break;
    }
  }

  if (wizardState.trainers) parts.push(currentLang === 'fr' ? 'Dresseurs Co-op' : 'Co-op Trainers');
  if (wizardState.types) parts.push(currentLang === 'fr' ? 'Types Reroll' : 'Types Reroll');

  const el = document.getElementById('rand-quick-summary-text');
  if (el) el.innerText = parts.join(' • ');
}

function applyWizardAndClose() {
  const toggle = document.getElementById('toggle-enable-randomizer');
  if (toggle && !toggle.checked) {
    toggle.checked = true;
    onToggleRandomizerChange();
  } else {
    updateQuickSummaryText();
    onAddonModeChange();
  }
  closeRandomizerModal();
}

function syncWizardUIFromState() {
  // Q1: Wilds
  const wildsYes = !!wizardState.wilds;
  const cardWildsYes = document.getElementById('card-wilds-yes');
  const cardWildsNo = document.getElementById('card-wilds-no');
  if (cardWildsYes) cardWildsYes.classList.toggle('active', wildsYes);
  if (cardWildsNo) cardWildsNo.classList.toggle('active', !wildsYes);
  const radWilds = document.querySelector(`input[name="wiz-q-wilds"][value="${wildsYes ? 'yes' : 'no'}"]`);
  if (radWilds) radWilds.checked = true;

  // Q2: Mode
  const cardModeArea = document.getElementById('card-mode-area');
  const cardModeGlobal = document.getElementById('card-mode-global');
  const cardModeRand = document.getElementById('card-mode-random');
  if (cardModeArea) cardModeArea.classList.toggle('active', wizardState.mode === 'area_1to1');
  if (cardModeGlobal) cardModeGlobal.classList.toggle('active', wizardState.mode === 'global_1to1');
  if (cardModeRand) cardModeRand.classList.toggle('active', wizardState.mode === 'random');
  const radMode = document.querySelector(`input[name="wiz-rand-mode"][value="${wizardState.mode}"]`);
  if (radMode) radMode.checked = true;

  // Q3: Strength balance
  const isSimstr = (wizardState.rule === 'similar_strength');
  const cardSimstrYes = document.getElementById('card-simstr-yes');
  const cardSimstrNo = document.getElementById('card-simstr-no');
  if (cardSimstrYes) cardSimstrYes.classList.toggle('active', isSimstr);
  if (cardSimstrNo) cardSimstrNo.classList.toggle('active', !isSimstr);
  const radSimstr = document.querySelector(`input[name="wiz-q-simstr"][value="${isSimstr ? 'yes' : 'no'}"]`);
  if (radSimstr) radSimstr.checked = true;

  // Q4: Legendaries
  const noleg = !!wizardState.noleg;
  const cardNolegYes = document.getElementById('card-noleg-yes');
  const cardNolegNo = document.getElementById('card-noleg-no');
  if (cardNolegYes) cardNolegYes.classList.toggle('active', noleg);
  if (cardNolegNo) cardNolegNo.classList.toggle('active', !noleg);
  const radNoleg = document.querySelector(`input[name="wiz-q-noleg"][value="${noleg ? 'yes' : 'no'}"]`);
  if (radNoleg) radNoleg.checked = true;

  // Q5: Starters
  const startersMode = wizardState.starters_mode;
  const cardStartersVanilla = document.getElementById('card-starters-vanilla');
  const cardStartersBalanced = document.getElementById('card-starters-balanced');
  const cardStartersAny = document.getElementById('card-starters-any');
  if (cardStartersVanilla) cardStartersVanilla.classList.toggle('active', startersMode === 'vanilla');
  if (cardStartersBalanced) cardStartersBalanced.classList.toggle('active', startersMode === 'balanced');
  if (cardStartersAny) cardStartersAny.classList.toggle('active', startersMode === 'any');
  const radStarters = document.querySelector(`input[name="wiz-starters-mode"][value="${startersMode}"]`);
  if (radStarters) radStarters.checked = true;

  // Q6: Shiny
  const sliderShiny = document.getElementById('wiz-slider-shiny');
  if (sliderShiny) {
    for (const [k, v] of Object.entries(SHINY_STEPS)) {
      if (v.val === wizardState.shiny) {
        sliderShiny.value = k;
        document.getElementById('wiz-shiny-odds-display').innerText = (currentLang === 'fr' ? v.label_fr : v.label_en);
        break;
      }
    }
  }

  // Q7: Honey Trees
  const honey = !!wizardState.honey;
  const cardHoneyYes = document.getElementById('card-honey-yes');
  const cardHoneyNo = document.getElementById('card-honey-no');
  if (cardHoneyYes) cardHoneyYes.classList.toggle('active', honey);
  if (cardHoneyNo) cardHoneyNo.classList.toggle('active', !honey);
  const radHoney = document.querySelector(`input[name="wiz-q-honey"][value="${honey ? 'yes' : 'no'}"]`);
  if (radHoney) radHoney.checked = true;

  // Q8: Static Encounters & Eggs
  const statics = !!wizardState.statics;
  const cardStaticsYes = document.getElementById('card-statics-yes');
  const cardStaticsNo = document.getElementById('card-statics-no');
  if (cardStaticsYes) cardStaticsYes.classList.toggle('active', statics);
  if (cardStaticsNo) cardStaticsNo.classList.toggle('active', !statics);
  const radStatics = document.querySelector(`input[name="wiz-q-statics"][value="${statics ? 'yes' : 'no'}"]`);
  if (radStatics) radStatics.checked = true;

  // Q9: Bosses / Scripted
  const battles = !!wizardState.battles;
  const cardBattlesYes = document.getElementById('card-battles-yes');
  const cardBattlesNo = document.getElementById('card-battles-no');
  if (cardBattlesYes) cardBattlesYes.classList.toggle('active', battles);
  if (cardBattlesNo) cardBattlesNo.classList.toggle('active', !battles);
  const radBattles = document.querySelector(`input[name="wiz-q-battles"][value="${battles ? 'yes' : 'no'}"]`);
  if (radBattles) radBattles.checked = true;

  // Q10: Gifts & Trades
  const gifts = !!wizardState.gifts;
  const cardGiftsYes = document.getElementById('card-gifts-yes');
  const cardGiftsNo = document.getElementById('card-gifts-no');
  if (cardGiftsYes) cardGiftsYes.classList.toggle('active', gifts);
  if (cardGiftsNo) cardGiftsNo.classList.toggle('active', !gifts);
  const radGifts = document.querySelector(`input[name="wiz-q-gifts"][value="${gifts ? 'yes' : 'no'}"]`);
  if (radGifts) radGifts.checked = true;

  // Q11: Special / GBA
  const special = !!wizardState.wild_special;
  const cardSpecialYes = document.getElementById('card-special-yes');
  const cardSpecialNo = document.getElementById('card-special-no');
  if (cardSpecialYes) cardSpecialYes.classList.toggle('active', special);
  if (cardSpecialNo) cardSpecialNo.classList.toggle('active', !special);
  const radSpecial = document.querySelector(`input[name="wiz-q-special"][value="${special ? 'yes' : 'no'}"]`);
  if (radSpecial) radSpecial.checked = true;

  // Q12: Evolutions
  const evoMode = wizardState.evolutions_mode || 'vanilla';
  const cardEvoVanilla = document.getElementById('card-evo-vanilla');
  const cardEvoSimstr = document.getElementById('card-evo-simstr');
  const cardEvoChaos = document.getElementById('card-evo-chaos');
  if (cardEvoVanilla) cardEvoVanilla.classList.toggle('active', evoMode === 'vanilla');
  if (cardEvoSimstr) cardEvoSimstr.classList.toggle('active', evoMode === 'similar_strength');
  if (cardEvoChaos) cardEvoChaos.classList.toggle('active', evoMode === 'chaos');
  const radEvo = document.querySelector(`input[name="wiz-evo-mode"][value="${evoMode}"]`);
  if (radEvo) radEvo.checked = true;

  // Q13: Trainers
  const trainers = !!wizardState.trainers;
  const cardTrainersYes = document.getElementById('card-trainers-yes');
  const cardTrainersNo = document.getElementById('card-trainers-no');
  if (cardTrainersYes) cardTrainersYes.classList.toggle('active', trainers);
  if (cardTrainersNo) cardTrainersNo.classList.toggle('active', !trainers);
  const radTrainers = document.querySelector(`input[name="wiz-q-trainers"][value="${trainers ? 'yes' : 'no'}"]`);
  if (radTrainers) radTrainers.checked = true;

  // Q14: Co-op Balance
  const coopBal = !!wizardState.coop_simstr;
  const cardCoopBalYes = document.getElementById('card-coop-bal-yes');
  const cardCoopBalNo = document.getElementById('card-coop-bal-no');
  if (cardCoopBalYes) cardCoopBalYes.classList.toggle('active', coopBal);
  if (cardCoopBalNo) cardCoopBalNo.classList.toggle('active', !coopBal);
  const radCoopBal = document.querySelector(`input[name="wiz-q-coop-bal"][value="${coopBal ? 'yes' : 'no'}"]`);
  if (radCoopBal) radCoopBal.checked = true;

  // Q15: Chaos toggles
  const toggleTypes = document.getElementById('wiz-toggle-types');
  if (toggleTypes) toggleTypes.checked = !!wizardState.types;
  const toggleAbilities = document.getElementById('wiz-toggle-abilities');
  if (toggleAbilities) toggleAbilities.checked = !!wizardState.abilities;
  const toggleMovesets = document.getElementById('wiz-toggle-movesets');
  if (toggleMovesets) toggleMovesets.checked = !!wizardState.movesets;

  updateWizardStartersPreview();
  updateQuickSummaryText();
}

function copyMainCoopCode() {
  const val = document.getElementById('main-coop-code').value;
  if (!val) return;
  navigator.clipboard.writeText(val);
  alert(currentLang === 'fr' ? "Code Co-op copié dans le presse-papier !" : "Co-op Code copied to clipboard!");
}

function copyMainWorldCode() {
  const val = document.getElementById('main-world-code').value;
  if (!val) return;
  navigator.clipboard.writeText(val);
  alert(currentLang === 'fr' ? "Code Monde copié dans le presse-papier !" : "World Code copied to clipboard!");
}

function copyWizardCoopCode() {
  const val = document.getElementById('wiz-output-coop-code').value;
  if (!val) return;
  navigator.clipboard.writeText(val);
  alert(currentLang === 'fr' ? "Code Co-op copié dans le presse-papier !" : "Co-op Code copied to clipboard!");
}

function copyWizardWorldCode() {
  const val = document.getElementById('wiz-output-world-code').value;
  if (!val) return;
  navigator.clipboard.writeText(val);
  alert(currentLang === 'fr' ? "Code Monde copié dans le presse-papier !" : "World Code copied to clipboard!");
}

async function pasteImportCoopCode() {
  try {
    const text = await navigator.clipboard.readText();
    if (text) document.getElementById('input-import-coop').value = text.trim();
  } catch (e) {
    console.error('[Paste Error]', e);
  }
}

async function pasteImportWorldCode() {
  try {
    const text = await navigator.clipboard.readText();
    if (text) document.getElementById('input-import-world').value = text.trim();
  } catch (e) {
    console.error('[Paste Error]', e);
  }
}

async function executeImportCodes() {
  const coopCode = document.getElementById('input-import-coop').value.trim();
  const worldCode = document.getElementById('input-import-world').value.trim();

  if (!coopCode && !worldCode) {
    alert(currentLang === 'fr' ? "Veuillez entrer au moins un Code Co-Op ou un Code Monde." : "Please enter at least a Co-Op Code or a World Code.");
    return;
  }

  let successCount = 0;
  try {
    if (coopCode) {
      const res = await window.pywebview.api.decode_code(coopCode);
      if (res.success && res.settings) {
        const s = res.settings;
        wizardState.coop_code = coopCode;
        if (s.coop_seed) wizardState.coop_seed = s.coop_seed;
        if (s.trainers !== undefined) wizardState.trainers = s.trainers;
        if (s.coop_simstr !== undefined) wizardState.coop_simstr = s.coop_simstr;
        if (s.coop_noleg !== undefined) wizardState.coop_noleg = s.coop_noleg;
        if (s.types !== undefined) wizardState.types = s.types;
        if (s.abilities !== undefined) wizardState.abilities = s.abilities;
        if (s.movesets !== undefined) wizardState.movesets = s.movesets;
        successCount++;
      } else {
        alert((currentLang === 'fr' ? "Erreur dans le Code Co-Op : " : "Co-Op Code Error: ") + (res.error || 'Invalide'));
        return;
      }
    }

    if (worldCode) {
      const res = await window.pywebview.api.decode_code(worldCode);
      if (res.success && res.settings) {
        const s = res.settings;
        wizardState.world_code = worldCode;
        if (s.seed) wizardState.seed = s.seed;
        if (s.wilds !== undefined) wizardState.wilds = s.wilds;
        if (s.starters !== undefined) {
          if (!s.starters) wizardState.starters_mode = 'vanilla';
          else if (s.starters_any) wizardState.starters_mode = 'any';
          else wizardState.starters_mode = 'balanced';
        }
        if (s.statics !== undefined) wizardState.statics = s.statics;
        if (s.battles !== undefined) wizardState.battles = s.battles;
        if (s.special !== undefined || s.wild_special !== undefined) {
          wizardState.wild_special = s.wild_special || s.special || false;
          wizardState.gba_slots = wizardState.wild_special;
        }
        if (s.gifts !== undefined) wizardState.gifts = s.gifts;
        if (s.trade_get !== undefined) {
          wizardState.trade_get = s.trade_get;
          wizardState.trade_want = s.trade_get;
        }
        if (s.mode) wizardState.mode = s.mode;
        if (s.rule !== undefined) wizardState.rule = s.rule;
        if (s.noleg !== undefined) wizardState.noleg = s.noleg;
        if (s.shiny) wizardState.shiny = s.shiny;
        successCount++;
      } else {
        alert((currentLang === 'fr' ? "Erreur dans le Code Monde : " : "World Code Error: ") + (res.error || 'Invalide'));
        return;
      }
    }

    if (successCount > 0) {
      syncWizardUIFromState();
      applyWizardAndClose();
      alert(currentLang === 'fr' ? "Codes importés et appliqués avec succès !" : "Codes successfully imported and applied!");
    }
  } catch (err) {
    console.error('[Import Error]', err);
    alert("Import Error: " + err);
  }
}

// ============================================================================
// SAVES & ABOUT ACTIONS
// ============================================================================
function clearLog(id) {
  const el = document.getElementById(id);
  if (el) el.innerText = '';
}

function openBackupsFolder() {
  const srcRom = document.getElementById('input-source-rom') ? document.getElementById('input-source-rom').value : '';
  const outRom = document.getElementById('input-output-rom') ? document.getElementById('input-output-rom').value : '';
  const target = srcRom || outRom || '';
  if (window.pywebview && window.pywebview.api && window.pywebview.api.open_backups_folder) {
    window.pywebview.api.open_backups_folder(target);
  } else if (window.pywebview && window.pywebview.api && window.pywebview.api.open_external_url) {
    window.pywebview.api.open_external_url(target || "PMBackups");
  }
}

function openGitHub() {
  window.pywebview.api.open_external_url("https://github.com/Ekiiii/ProjectPM-Addon-Patcher");
}

async function openLogsFolder() {
  if (window.pywebview && window.pywebview.api && window.pywebview.api.open_logs_folder) {
    await window.pywebview.api.open_logs_folder();
  }
}

async function checkForUpdates() {
  const box = document.getElementById('update-result-box');
  box.style.display = 'block';
  box.innerHTML = currentLang === 'fr' ? '<em>Recherche de mise à jour sur GitHub...</em>' : '<em>Checking for updates on GitHub...</em>';
  await window.pywebview.api.check_for_updates();
}

window.onUpdateCheckResult = (data) => {
  const box = document.getElementById('update-result-box');
  if (data.available) {
    box.innerHTML = `
      <div style="background-color: #064e3b; border: 1px solid #10b981; padding: 10px; border-radius: 4px; color: #a7f3d0;">
        <strong>${currentLang === 'fr' ? 'Nouvelle version disponible :' : 'New version available:'} ${data.latest} !</strong> (${currentLang === 'fr' ? 'Actuelle' : 'Current'} : ${data.current})<br>
        <button class="pixel-btn primary mini mt-2" onclick="window.pywebview.api.open_external_url('${data.url}')">${currentLang === 'fr' ? 'Télécharger la mise à jour' : 'Download Update'}</button>
      </div>
    `;
  } else {
    box.innerHTML = `
      <div style="background-color: #1e293b; border: 1px solid #334155; padding: 10px; border-radius: 4px; color: #94a3b8;">
        ${currentLang === 'fr' ? `Vous disposez de la dernière version (${data.current}).` : `You are using the latest version (${data.current}).`}
      </div>
    `;
  }
};
