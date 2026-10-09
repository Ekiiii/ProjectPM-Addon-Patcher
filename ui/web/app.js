/* ==========================================================================
   PROJECT PM ADDON PATCHER & RANDOMIZER - APPLICATION LOGIC
   Author: Ekiii
   Bilingual Support (FR / EN) & Faithful World vs Co-Op Randomizer
   ========================================================================== */

let currentLang = 'fr';
let translations = {};
let currentRomInfo = null;
let currentRandRomInfo = null;
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
    currentLang = initData.lang || 'fr';
    translations = initData.translations || {};
    pokemonNames = initData.pokemon_names || {};
    
    // Set version
    const verEl = document.getElementById('app-version');
    if (verEl) verEl.innerText = initData.version || 'v1.0.3';
    
    // Set initial seeds & codes
    if (initData.initial_coop) {
      const coopCodeEl = document.getElementById('input-coop-code');
      const coopSeedEl = document.getElementById('input-coop-seed');
      if (coopCodeEl) coopCodeEl.value = initData.initial_coop.code || '';
      if (coopSeedEl) coopSeedEl.value = initData.initial_coop.seed || '';
    }
    if (initData.initial_world) {
      const worldCodeEl = document.getElementById('input-world-code');
      const worldSeedEl = document.getElementById('input-world-seed');
      if (worldCodeEl) worldCodeEl.value = initData.initial_world.code || '';
      if (worldSeedEl) worldSeedEl.value = initData.initial_world.seed || '';
    }

    // Apply language buttons active state
    document.getElementById('btn-lang-fr').classList.toggle('active', currentLang === 'fr');
    document.getElementById('btn-lang-en').classList.toggle('active', currentLang === 'en');

    applyTranslations(currentLang);
    onShinySliderChange();
    updateStartersPreview();
  } catch (err) {
    console.error('[App Init Error]', err);
  }
});

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
    onShinySliderChange();
    updateStartersPreview();

    // Re-render badges if ROMs analyzed
    if (currentRomInfo && currentRomInfo.valid) {
      renderPatcherBadges(currentRomInfo);
    }
    if (currentRandRomInfo && currentRandRomInfo.valid) {
      renderRandBadges(currentRandRomInfo);
    }
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
// FILE SELECTION & ROM DETECTION (TAB 1: PATCHER)
// ============================================================================
async function browseSourceRom() {
  try {
    const path = await window.pywebview.api.browse_source_rom();
    if (path) {
      document.getElementById('input-source-rom').value = path;
      await processSelectedRom(path);

      // Also pre-fill Randomizer source ROM if currently empty
      const randSrc = document.getElementById('input-rand-source-rom');
      if (randSrc && (!randSrc.value || randSrc.value.trim() === '')) {
        randSrc.value = path;
        await processRandRom(path);
      }
    }
  } catch (e) {
    console.error('[Browse ROM Error]', e);
  }
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
    
    // Auto-fill destination ROM if empty
    const dstInput = document.getElementById('input-dest-rom');
    if (!dstInput.value || dstInput.value.trim() === '') {
      dstInput.value = res.suggested_output || '';
    }

    renderPatcherBadges(res);
  } else {
    document.getElementById('rom-title-display').innerText = currentLang === 'fr' ? "Fichier Invalide" : "Invalid File";
    document.getElementById('rom-badges-container').innerHTML = `<span class="status-badge amber">${res.error || 'Erreur'}</span>`;
  }
}

function renderPatcherBadges(res) {
  const badgesHtml = res.badges.map(b => `<span class="status-badge ${b.color}">${b.label}</span>`).join('');
  document.getElementById('rom-badges-container').innerHTML = badgesHtml;
}

async function browseDestRom() {
  try {
    const sug = document.getElementById('input-dest-rom').value;
    const defaultName = sug ? sug.split('/').pop() : 'ProjectPM_modded.nds';
    const path = await window.pywebview.api.browse_save_rom(defaultName);
    if (path) {
      document.getElementById('input-dest-rom').value = path;
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

      const randSrc = document.getElementById('input-rand-source-rom');
      if (randSrc && (!randSrc.value || randSrc.value.trim() === '')) {
        randSrc.value = p;
        processRandRom(p);
      }
    }
  }
});

// ============================================================================
// PATCHER PIPELINE
// ============================================================================
function onMpModeChange() {}
function onAddonModeChange() {}

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

  const options = {
    mp_enabled: mpMode !== 'none',
    mp_version: mpMode === 'auto' ? (currentRomInfo ? currentRomInfo.lang : 'fr') : mpMode,
    sl_enabled: addonVal === 'soullink',
    sl_mode: addonVal === 'restore' ? 'restore' : 'apply',
    sl_variant: currentRomInfo ? currentRomInfo.lang : 'fr',
    bg_opt: document.getElementById('toggle-visual-bg').checked ? 'builtin' : 'none',
    cam_opt: document.getElementById('toggle-visual-cam').checked ? 'builtin' : 'none',
    backup_save: document.getElementById('toggle-backup-save').checked,
    custom_patch: document.getElementById('input-custom-patch').value.trim() || null
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
  if (ok) {
    document.getElementById('patch-progress-fill').style.width = '100%';
    alert((currentLang === 'fr' ? "Succès !\n" : "Success!\n") + msg);
  } else {
    alert((currentLang === 'fr' ? "Erreur lors du patch :\n" : "Patch error:\n") + msg);
  }
};

// ============================================================================
// RANDOMIZER FILE SELECTION & ROM ANALYSIS (TAB 2)
// ============================================================================
async function browseRandSourceRom() {
  try {
    const path = await window.pywebview.api.browse_source_rom();
    if (path) {
      document.getElementById('input-rand-source-rom').value = path;
      await processRandRom(path);
    }
  } catch (e) {
    console.error('[Browse Rand ROM Error]', e);
  }
}

async function processRandRom(path) {
  const badgesContainer = document.getElementById('rand-rom-badges');
  badgesContainer.innerHTML = `<span class="badge slate">${currentLang === 'fr' ? 'Analyse...' : 'Analyzing...'}</span>`;

  const res = await window.pywebview.api.analyze_rom(path);
  currentRandRomInfo = res;

  if (res.valid) {
    const dstInput = document.getElementById('input-rand-dest-rom');
    if (!dstInput.value || dstInput.value.trim() === '') {
      const baseNoExt = path.replace(/\.nds$/i, '');
      dstInput.value = `${baseNoExt}_Randomized.nds`;
    }
    renderRandBadges(res);
  } else {
    badgesContainer.innerHTML = `<span class="badge amber">${res.error || 'Erreur'}</span>`;
  }
}

function renderRandBadges(res) {
  const container = document.getElementById('rand-rom-badges');
  let badges = [];
  badges.push(`<span class="badge blue">${res.game} (${res.lang.toUpperCase()})</span>`);
  if (res.has_multiplayer) {
    badges.push(`<span class="badge emerald">Project PM v${res.mp_version}</span>`);
  }
  if (res.has_soullocke) {
    badges.push(`<span class="badge purple">SoulLink (${res.soullocke_variant.toUpperCase()})</span>`);
  }
  if (res.is_randomized) {
    badges.push(`<span class="badge amber">${translations['badge_already_rand'] || 'Déjà Randomisée'}</span>`);
  } else {
    badges.push(`<span class="badge slate">${translations['badge_ready'] || 'Prêt'}</span>`);
  }
  container.innerHTML = badges.join(' ');
}

async function browseRandDestRom() {
  try {
    const sug = document.getElementById('input-rand-dest-rom').value;
    const defaultName = sug ? sug.split('/').pop() : 'ProjectPM_Randomized.nds';
    const path = await window.pywebview.api.browse_save_rom(defaultName);
    if (path) {
      document.getElementById('input-rand-dest-rom').value = path;
    }
  } catch (e) {
    console.error('[Browse Rand Dest Error]', e);
  }
}

// ============================================================================
// RANDOMIZER: YOUR WORLD (COLUMN 1)
// ============================================================================
function onStartersModeChanged() {
  updateStartersPreview();
  updateWorldCodeFromUI();
}

function onShinySliderChange() {
  const step = document.getElementById('slider-shiny').value;
  const cfg = SHINY_STEPS[step] || SHINY_STEPS[4];
  const label = currentLang === 'fr' ? cfg.label_fr : cfg.label_en;
  document.getElementById('shiny-odds-display').innerText = label;
  updateWorldCodeFromUI();
}

function updateStartersPreview() {
  const checkedRadio = document.querySelector('input[name="starters-mode"]:checked');
  const mode = checkedRadio ? checkedRadio.value : 'balanced';

  if (mode === 'vanilla') {
    setStarterSlot(1, 387, pokemonNames['387'] || (currentLang === 'fr' ? "Tortipouss" : "Turtwig"));
    setStarterSlot(2, 390, pokemonNames['390'] || (currentLang === 'fr' ? "Ouisticram" : "Chimchar"));
    setStarterSlot(3, 393, pokemonNames['393'] || (currentLang === 'fr' ? "Tiplouf" : "Piplup"));
  } else {
    const randLabel = currentLang === 'fr' ? "Aléatoire" : "Random";
    setStarterSlot(1, "???", randLabel);
    setStarterSlot(2, "???", randLabel);
    setStarterSlot(3, "???", randLabel);
  }
}

function setStarterSlot(slotNum, id, name) {
  const idEl = document.getElementById(`starter-${slotNum}-id`);
  const nameEl = document.getElementById(`starter-${slotNum}-name`);
  if (idEl) idEl.innerText = typeof id === 'number' ? `#${id}` : id;
  if (nameEl) nameEl.innerText = name;
}

function generateNewWorldSeed() {
  const rnd = Math.floor(1000000000 + Math.random() * 9000000000).toString();
  document.getElementById('input-world-seed').value = rnd;
  updateWorldCodeFromUI();
}

function onWorldSeedInput() {
  updateWorldCodeFromUI();
}

async function updateWorldCodeFromUI() {
  const step = document.getElementById('slider-shiny').value;
  const shinyThr = SHINY_STEPS[step] ? SHINY_STEPS[step].val : 64;
  const startersMode = document.querySelector('input[name="starters-mode"]:checked').value;
  const seed = document.getElementById('input-world-seed').value.trim();

  const settings = {
    wilds: document.getElementById('toggle-rand-wilds').checked,
    starters: startersMode !== 'vanilla',
    starters_any: startersMode === 'any',
    statics: document.getElementById('toggle-rand-honey').checked,
    battles: document.getElementById('toggle-rand-battles').checked,
    gifts: document.getElementById('toggle-rand-gifts').checked,
    trade_get: document.getElementById('toggle-rand-trades').checked,
    trade_want: document.getElementById('toggle-rand-trades').checked,
    wild_special: document.getElementById('toggle-rand-special').checked,
    gba_slots: document.getElementById('toggle-rand-gba').checked,
    mode: document.getElementById('select-rand-mode').value,
    rule: document.getElementById('select-rand-rule').value,
    noleg: document.getElementById('toggle-rand-noleg').checked,
    shiny: shinyThr,
    seed: seed
  };

  try {
    const res = await window.pywebview.api.generate_world_code(settings);
    if (res && res.code) {
      document.getElementById('input-world-code').value = res.code;
      if (res.seed && !seed) {
        document.getElementById('input-world-seed').value = res.seed;
      }
    }
  } catch (e) {
    console.error('[Update World Code Error]', e);
  }
}

async function onWorldCodeChanged() {
  const code = document.getElementById('input-world-code').value.trim();
  if (!code) return;
  try {
    const res = await window.pywebview.api.decode_code(code);
    if (res.success && res.settings) {
      const s = res.settings;
      if (s.seed) document.getElementById('input-world-seed').value = s.seed;
      if (s.wilds !== undefined) document.getElementById('toggle-rand-wilds').checked = s.wilds;
      if (s.starters !== undefined) document.getElementById('toggle-rand-starters').checked = s.starters;
      if (s.statics !== undefined) document.getElementById('toggle-rand-honey').checked = s.statics;
      if (s.battles !== undefined) document.getElementById('toggle-rand-battles').checked = s.battles;
      if (s.special !== undefined || s.wild_special !== undefined) {
        document.getElementById('toggle-rand-special').checked = s.wild_special || s.special || false;
      }
      if (s.gba_slots !== undefined) document.getElementById('toggle-rand-gba').checked = s.gba_slots;
      if (s.gifts !== undefined) document.getElementById('toggle-rand-gifts').checked = s.gifts;
      if (s.trade_get !== undefined) document.getElementById('toggle-rand-trades').checked = s.trade_get;
      if (s.mode) document.getElementById('select-rand-mode').value = s.mode;
      if (s.rule) document.getElementById('select-rand-rule').value = s.rule;
      if (s.noleg !== undefined) document.getElementById('toggle-rand-noleg').checked = s.noleg;
      if (s.shiny) {
        for (const [k, v] of Object.entries(SHINY_STEPS)) {
          if (v.val === s.shiny) {
            document.getElementById('slider-shiny').value = k;
            onShinySliderChange();
            break;
          }
        }
      }
      updateStartersPreview();
    } else if (res.error) {
      alert((currentLang === 'fr' ? "Erreur dans le Code Monde : " : "World Code Error: ") + res.error);
    }
  } catch (e) {
    console.error('[Decode World Code Error]', e);
  }
}

function copyWorldCode() {
  const val = document.getElementById('input-world-code').value;
  navigator.clipboard.writeText(val);
  alert(currentLang === 'fr' ? "Code Monde copié dans le presse-papier !" : "World Code copied to clipboard!");
}

async function pasteWorldCode() {
  try {
    const text = await navigator.clipboard.readText();
    if (text) {
      document.getElementById('input-world-code').value = text.trim();
      onWorldCodeChanged();
    }
  } catch (e) {
    console.error('[Paste Error]', e);
  }
}

// ============================================================================
// RANDOMIZER: CO-OP (COLUMN 2)
// ============================================================================
function generateNewCoopSeed() {
  const rnd = Math.floor(1000000000 + Math.random() * 9000000000).toString();
  document.getElementById('input-coop-seed').value = rnd;
  updateCoopCodeFromUI();
}

function onCoopSeedInput() {
  updateCoopCodeFromUI();
}

async function updateCoopCodeFromUI() {
  const seed = document.getElementById('input-coop-seed').value.trim();
  const settings = {
    trainers: document.getElementById('toggle-rand-trainers').checked,
    coop_simstr: document.getElementById('toggle-coop-simstr').checked,
    coop_noleg: document.getElementById('toggle-coop-noleg').checked,
    types: document.getElementById('toggle-rand-types').checked,
    abilities: document.getElementById('toggle-rand-abilities').checked,
    movesets: document.getElementById('toggle-rand-movesets').checked,
    coop_seed: seed
  };

  try {
    const res = await window.pywebview.api.generate_coop_code(settings);
    if (res && res.code) {
      document.getElementById('input-coop-code').value = res.code;
      if (res.seed && !seed) {
        document.getElementById('input-coop-seed').value = res.seed;
      }
    }
  } catch (e) {
    console.error('[Update Coop Code Error]', e);
  }
}

async function onCoopCodeChanged() {
  const code = document.getElementById('input-coop-code').value.trim();
  if (!code) return;
  try {
    const res = await window.pywebview.api.decode_code(code);
    if (res.success && res.settings) {
      const s = res.settings;
      if (s.coop_seed) document.getElementById('input-coop-seed').value = s.coop_seed;
      if (s.trainers !== undefined) document.getElementById('toggle-rand-trainers').checked = s.trainers;
      if (s.coop_simstr !== undefined) document.getElementById('toggle-coop-simstr').checked = s.coop_simstr;
      if (s.coop_noleg !== undefined) document.getElementById('toggle-coop-noleg').checked = s.coop_noleg;
      if (s.types !== undefined) document.getElementById('toggle-rand-types').checked = s.types;
      if (s.abilities !== undefined) document.getElementById('toggle-rand-abilities').checked = s.abilities;
      if (s.movesets !== undefined) document.getElementById('toggle-rand-movesets').checked = s.movesets;
    } else if (res.error) {
      alert((currentLang === 'fr' ? "Erreur dans le Code Co-Op : " : "Co-Op Code Error: ") + res.error);
    }
  } catch (e) {
    console.error('[Decode Coop Code Error]', e);
  }
}

function copyCoopCode() {
  const val = document.getElementById('input-coop-code').value;
  navigator.clipboard.writeText(val);
  alert(currentLang === 'fr' ? "Code Co-op copié dans le presse-papier !" : "Co-Op Code copied to clipboard!");
}

async function pasteCoopCode() {
  try {
    const text = await navigator.clipboard.readText();
    if (text) {
      document.getElementById('input-coop-code').value = text.trim();
      onCoopCodeChanged();
    }
  } catch (e) {
    console.error('[Paste Error]', e);
  }
}

// ============================================================================
// RANDOMIZER: MASTER EXECUTION
// ============================================================================
async function startRandomizer() {
  let inRom = document.getElementById('input-rand-source-rom').value.trim();
  if (!inRom) {
    // Fallback to Tab 1 source ROM if available
    inRom = document.getElementById('input-source-rom').value.trim();
  }
  let outRom = document.getElementById('input-rand-dest-rom').value.trim();

  if (!inRom) {
    alert(currentLang === 'fr' ? "Veuillez sélectionner une ROM source à randomiser." : "Please select a source ROM to randomize.");
    return;
  }
  if (!outRom) {
    outRom = inRom.replace(/\.nds$/i, '_Randomized.nds');
    document.getElementById('input-rand-dest-rom').value = outRom;
  }

  const btn = document.getElementById('btn-start-randomizer');
  btn.disabled = true;
  document.getElementById('rand-status-text').innerText = currentLang === 'fr' ? "Génération en cours..." : "Generating...";
  document.getElementById('rand-log').innerText = '';

  const step = document.getElementById('slider-shiny').value;
  const shinyThr = SHINY_STEPS[step] ? SHINY_STEPS[step].val : 64;
  const startersMode = document.querySelector('input[name="starters-mode"]:checked').value;

  const worldSeed = document.getElementById('input-world-seed').value.trim();
  const coopSeed = document.getElementById('input-coop-seed').value.trim();

  const settings = {
    in_rom: inRom,
    wilds: document.getElementById('toggle-rand-wilds').checked,
    mode: document.getElementById('select-rand-mode').value,
    rule: document.getElementById('select-rand-rule').value,
    noleg: document.getElementById('toggle-rand-noleg').checked,
    starters: startersMode !== 'vanilla',
    starters_any: startersMode === 'any',
    statics: document.getElementById('toggle-rand-honey').checked,
    battles: document.getElementById('toggle-rand-battles').checked,
    gifts: document.getElementById('toggle-rand-gifts').checked,
    trade_get: document.getElementById('toggle-rand-trades').checked,
    trade_want: document.getElementById('toggle-rand-trades').checked,
    wild_special: document.getElementById('toggle-rand-special').checked,
    gba_slots: document.getElementById('toggle-rand-gba').checked,
    trainers: document.getElementById('toggle-rand-trainers').checked,
    types: document.getElementById('toggle-rand-types').checked,
    abilities: document.getElementById('toggle-rand-abilities').checked,
    movesets: document.getElementById('toggle-rand-movesets').checked,
    coop_noleg: document.getElementById('toggle-coop-noleg').checked,
    coop_simstr: document.getElementById('toggle-coop-simstr').checked,
    shiny: shinyThr,
    seed: worldSeed,
    coop_seed: coopSeed
  };

  try {
    await window.pywebview.api.run_randomizer(inRom, outRom, settings);
  } catch (e) {
    console.error('[Randomizer Execution Error]', e);
    btn.disabled = false;
  }
}

window.onRandLog = (msg) => {
  const el = document.getElementById('rand-log');
  el.innerText += msg + '\n';
  el.scrollTop = el.scrollHeight;
};

window.onRandComplete = (data) => {
  document.getElementById('btn-start-randomizer').disabled = false;
  document.getElementById('rand-status-text').innerText = data.ok ? (currentLang === 'fr' ? "Terminé !" : "Done!") : (currentLang === 'fr' ? "Erreur" : "Error");
  
  if (data.ok) {
    // Update starters cards if returned
    if (data.starters && data.starters.length === 3) {
      data.starters.forEach((st, idx) => {
        const localizedName = pokemonNames[st.id] || st.name;
        setStarterSlot(idx + 1, st.id, localizedName);
      });
    }
    const successMsg = currentLang === 'fr'
      ? `Randomisation terminée avec succès !\nFichier de rapport : ${data.report_file}`
      : `Randomization completed successfully!\nReport file: ${data.report_file}`;
    alert(successMsg);
  } else {
    alert((currentLang === 'fr' ? "Erreur lors de la randomisation :\n" : "Randomization Error:\n") + (data.error || 'Erreur inconnue'));
  }
};

// ============================================================================
// SAVES & ABOUT ACTIONS
// ============================================================================
function clearLog(id) {
  const el = document.getElementById(id);
  if (el) el.innerText = '';
}

function openBackupsFolder() {
  window.pywebview.api.open_external_url("PMBackups");
}

function openGitHub() {
  window.pywebview.api.open_external_url("https://github.com/Ekiiii/ProjectPM-Addon-Patcher");
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
