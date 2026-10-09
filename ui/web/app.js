/* ==========================================================================
   PROJECT PM ADDON PATCHER & RANDOMIZER - APPLICATION LOGIC
   ========================================================================== */

let currentLang = 'fr';
let translations = {};
let currentRomInfo = null;
let pokemonNames = {};

const SHINY_STEPS = {
  1: { val: 8, label: '1/8192 (Vanilla Platine)' },
  2: { val: 16, label: '1/4096 (Génération 6+)' },
  3: { val: 32, label: '1/2048 (x4)' },
  4: { val: 64, label: '~1/1024 (x8 - Équilibré)' },
  5: { val: 128, label: '~1/512 (x16)' },
  6: { val: 256, label: '~1/256 (x32)' },
  7: { val: 655, label: '~1/100 (Ultra Shiny)' }
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
    document.getElementById('app-version').innerText = initData.version || 'v1.0.3';
    
    // Set initial seeds & codes
    if (initData.initial_coop) {
      document.getElementById('input-coop-code').value = initData.initial_coop.code;
      document.getElementById('preview-coop-seed').innerText = `Seed: ${initData.initial_coop.seed}`;
    }
    if (initData.initial_world) {
      document.getElementById('input-world-code').value = initData.initial_world.code;
      document.getElementById('preview-world-seed').innerText = `Seed: ${initData.initial_world.seed}`;
    }

    updateLangUI();
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
// LOCALIZATION
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
    updateLangUI();
    updateStartersPreview();
  } catch (e) {
    console.error('[Change Lang Error]', e);
  }
}

function updateLangUI() {
  if (currentLang === 'fr') {
    document.getElementById('i18n-app-subtitle').innerText = "Gestionnaire de Mods, Multijoueur & Randomizer pour Pokémon Platine";
    document.getElementById('i18n-tab-patcher').innerText = "MODS & MULTI";
    document.getElementById('i18n-tab-randomizer').innerText = "RANDOMIZER CO-OP";
    document.getElementById('i18n-tab-saves').innerText = "SAUVEGARDES";
    document.getElementById('i18n-tab-about').innerText = "OPTIONS & INFOS";
    document.getElementById('i18n-card-rom-title').innerText = "1. SÉLECTION DE LA ROM SOURCE & DESTINATION";
    document.getElementById('i18n-label-src-rom').innerText = "ROM Source (Pokémon Platine NDS) :";
    document.getElementById('i18n-label-dst-rom').innerText = "ROM de destination (Où enregistrer) :";
    document.getElementById('i18n-btn-browse-src').innerText = "Parcourir...";
    document.getElementById('i18n-btn-browse-dst').innerText = "Enregistrer sous...";
    document.getElementById('i18n-card-mods-title').innerText = "2. BASE MULTI ET MODES DE JEU";
    document.getElementById('i18n-card-visual-title').innerText = "3. GRAPHISMES & CONFORT (VISUAL+)";
    document.getElementById('btn-start-patch').querySelector('span').innerText = "APPLIQUER LES PATCHS SUR LA ROM";
    document.getElementById('btn-start-randomizer').querySelector('span').innerText = "GÉNÉRER LA ROM RANDOMISÉE";
  } else {
    document.getElementById('i18n-app-subtitle').innerText = "Mods, Multiplayer & Randomizer Manager for Pokémon Platinum";
    document.getElementById('i18n-tab-patcher').innerText = "MODS & MULTI";
    document.getElementById('i18n-tab-randomizer').innerText = "CO-OP RANDOMIZER";
    document.getElementById('i18n-tab-saves').innerText = "SAVED GAMES";
    document.getElementById('i18n-tab-about').innerText = "OPTIONS & ABOUT";
    document.getElementById('i18n-card-rom-title').innerText = "1. SELECT SOURCE ROM & DESTINATION";
    document.getElementById('i18n-label-src-rom').innerText = "Source ROM (Pokémon Platinum NDS):";
    document.getElementById('i18n-label-dst-rom').innerText = "Destination ROM (Where to save):";
    document.getElementById('i18n-btn-browse-src').innerText = "Browse...";
    document.getElementById('i18n-btn-browse-dst').innerText = "Save As...";
    document.getElementById('i18n-card-mods-title').innerText = "2. MULTIPLAYER BASE & GAMEPLAY MODS";
    document.getElementById('i18n-card-visual-title').innerText = "3. GRAPHICS & ENHANCEMENTS (VISUAL+)";
    document.getElementById('btn-start-patch').querySelector('span').innerText = "APPLY PATCHES TO ROM";
    document.getElementById('btn-start-randomizer').querySelector('span').innerText = "GENERATE RANDOMIZED ROM";
  }
}

// ============================================================================
// FILE SELECTION & ROM DETECTION
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

async function processSelectedRom(path) {
  const box = document.getElementById('rom-status-box');
  box.style.display = 'block';
  document.getElementById('rom-title-display').innerText = "Analyse en cours...";
  document.getElementById('rom-badges-container').innerHTML = '';

  const res = await window.pywebview.api.analyze_rom(path);
  currentRomInfo = res;
  
  if (res.valid) {
    document.getElementById('rom-title-display').innerText = `${res.game} (${res.game_code})`;
    document.getElementById('rom-size-display').innerText = `${res.size_mb} Mo`;
    
    // Auto-fill destination ROM if empty
    const dstInput = document.getElementById('input-dest-rom');
    if (!dstInput.value || dstInput.value.trim() === '') {
      dstInput.value = res.suggested_output || '';
    }

    // Render badges
    const badgesHtml = res.badges.map(b => `<span class="status-badge ${b.color}">${b.label}</span>`).join('');
    document.getElementById('rom-badges-container').innerHTML = badgesHtml;
  } else {
    document.getElementById('rom-title-display').innerText = "Fichier Invalide";
    document.getElementById('rom-badges-container').innerHTML = `<span class="status-badge amber">${res.error || 'Erreur'}</span>`;
  }
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
    alert("Veuillez sélectionner une ROM source Pokémon Platine.");
    return;
  }
  if (!outRom) {
    alert("Veuillez spécifier l'emplacement de la ROM de destination.");
    return;
  }

  const btn = document.getElementById('btn-start-patch');
  btn.disabled = true;
  document.getElementById('patch-progress-fill').style.width = '0%';
  document.getElementById('patch-status-text').innerText = "En cours d'application...";
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

// Window callbacks from Python
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
  document.getElementById('patch-status-text').innerText = ok ? "Terminé !" : "Erreur";
  if (ok) {
    document.getElementById('patch-progress-fill').style.width = '100%';
    alert("Succès !\n" + msg);
  } else {
    alert("Erreur lors du patch :\n" + msg);
  }
};

// ============================================================================
// RANDOMIZER
// ============================================================================
async function generateNewCoopCode() {
  const res = await window.pywebview.api.generate_coop_code({
    trainers: document.getElementById('toggle-rand-trainers').checked,
    types: document.getElementById('toggle-rand-types').checked,
    abilities: document.getElementById('toggle-rand-abilities').checked,
    movesets: document.getElementById('toggle-rand-movesets').checked,
    coop_noleg: document.getElementById('toggle-rand-noleg').checked,
    coop_simstr: false
  });
  document.getElementById('input-coop-code').value = res.code;
  document.getElementById('preview-coop-seed').innerText = `Seed: ${res.seed}`;
}

async function generateNewWorldCode() {
  const step = document.getElementById('slider-shiny').value;
  const thr = SHINY_STEPS[step] ? SHINY_STEPS[step].val : 8;

  const res = await window.pywebview.api.generate_world_code({
    wilds: document.getElementById('toggle-rand-wilds').checked,
    mode: document.getElementById('select-rand-mode').value,
    rule: document.getElementById('select-rand-rule').value,
    noleg: document.getElementById('toggle-rand-noleg').checked,
    starters: true,
    statics: document.getElementById('toggle-rand-statics').checked,
    shiny: thr
  });
  document.getElementById('input-world-code').value = res.code;
  document.getElementById('preview-world-seed').innerText = `Seed: ${res.seed}`;
  updateStartersPreview();
}

function copyCoopCode() {
  const val = document.getElementById('input-coop-code').value;
  navigator.clipboard.writeText(val);
  alert("Code Co-op copié dans le presse-papier !");
}

async function pasteCoopCode() {
  const text = await navigator.clipboard.readText();
  if (text) {
    document.getElementById('input-coop-code').value = text.trim();
    onCoopCodeChanged();
  }
}

function copyWorldCode() {
  const val = document.getElementById('input-world-code').value;
  navigator.clipboard.writeText(val);
  alert("Code Monde copié dans le presse-papier !");
}

async function pasteWorldCode() {
  const text = await navigator.clipboard.readText();
  if (text) {
    document.getElementById('input-world-code').value = text.trim();
    onWorldCodeChanged();
  }
}

async function onCoopCodeChanged() {
  const code = document.getElementById('input-coop-code').value.trim();
  const res = await window.pywebview.api.decode_code(code);
  if (res.success && res.settings) {
    const s = res.settings;
    if (s.coop_seed) document.getElementById('preview-coop-seed').innerText = `Seed: ${s.coop_seed}`;
    if (s.trainers !== undefined) document.getElementById('toggle-rand-trainers').checked = s.trainers;
    if (s.types !== undefined) document.getElementById('toggle-rand-types').checked = s.types;
    if (s.abilities !== undefined) document.getElementById('toggle-rand-abilities').checked = s.abilities;
    if (s.movesets !== undefined) document.getElementById('toggle-rand-movesets').checked = s.movesets;
    if (s.coop_noleg !== undefined) document.getElementById('toggle-rand-noleg').checked = s.coop_noleg;
  }
}

async function onWorldCodeChanged() {
  const code = document.getElementById('input-world-code').value.trim();
  const res = await window.pywebview.api.decode_code(code);
  if (res.success && res.settings) {
    const s = res.settings;
    if (s.seed) document.getElementById('preview-world-seed').innerText = `Seed: ${s.seed}`;
    if (s.wilds !== undefined) document.getElementById('toggle-rand-wilds').checked = s.wilds;
    if (s.mode) document.getElementById('select-rand-mode').value = s.mode;
    if (s.rule) document.getElementById('select-rand-rule').value = s.rule;
    if (s.noleg !== undefined) document.getElementById('toggle-rand-noleg').checked = s.noleg;
    if (s.statics !== undefined) document.getElementById('toggle-rand-statics').checked = s.statics;
    if (s.shiny) {
      for (const [k, v] of Object.entries(SHINY_STEPS)) {
        if (v.val === s.shiny) {
          document.getElementById('slider-shiny').value = k;
          onShinySliderChange();
          break;
        }
      }
    }
  }
}

function onShinySliderChange() {
  const step = document.getElementById('slider-shiny').value;
  const cfg = SHINY_STEPS[step] || SHINY_STEPS[4];
  document.getElementById('shiny-odds-display').innerText = cfg.label;
}

function updateStartersPreview() {
  const mode = document.querySelector('input[name="starters-mode"]:checked').value;
  if (mode === 'vanilla') {
    setStarterSlot(1, 387, pokemonNames['387'] || "Tortipouss");
    setStarterSlot(2, 390, pokemonNames['390'] || "Ouisticram");
    setStarterSlot(3, 393, pokemonNames['393'] || "Tiplouf");
  } else {
    setStarterSlot(1, "???", "Aléatoire");
    setStarterSlot(2, "???", "Aléatoire");
    setStarterSlot(3, "???", "Aléatoire");
  }
}

function setStarterSlot(slotNum, id, name) {
  document.getElementById(`starter-${slotNum}-id`).innerText = typeof id === 'number' ? `#${id}` : id;
  document.getElementById(`starter-${slotNum}-name`).innerText = name;
}

async function startRandomizer() {
  const inRom = document.getElementById('input-source-rom').value.trim();
  let outRom = document.getElementById('input-dest-rom').value.trim();

  if (!inRom) {
    alert("Veuillez sélectionner une ROM source.");
    return;
  }
  if (!outRom) {
    outRom = inRom.replace(/\.nds$/i, '_Randomized.nds');
  }

  const btn = document.getElementById('btn-start-randomizer');
  btn.disabled = true;
  document.getElementById('rand-status-text').innerText = "Génération en cours...";
  document.getElementById('rand-log').innerText = '';

  const step = document.getElementById('slider-shiny').value;
  const shinyThr = SHINY_STEPS[step] ? SHINY_STEPS[step].val : 64;
  const startersMode = document.querySelector('input[name="starters-mode"]:checked').value;

  const coopSeedText = document.getElementById('preview-coop-seed').innerText.replace('Seed: ', '').trim();
  const worldSeedText = document.getElementById('preview-world-seed').innerText.replace('Seed: ', '').trim();

  const settings = {
    in_rom: inRom,
    wilds: document.getElementById('toggle-rand-wilds').checked,
    mode: document.getElementById('select-rand-mode').value,
    rule: document.getElementById('select-rand-rule').value,
    noleg: document.getElementById('toggle-rand-noleg').checked,
    starters: startersMode !== 'vanilla',
    starters_any: startersMode === 'any',
    statics: document.getElementById('toggle-rand-statics').checked,
    battles: document.getElementById('toggle-rand-statics').checked,
    gifts: document.getElementById('toggle-rand-statics').checked,
    trade_get: document.getElementById('toggle-rand-statics').checked,
    trade_want: document.getElementById('toggle-rand-statics').checked,
    wild_special: document.getElementById('toggle-rand-statics').checked,
    trainers: document.getElementById('toggle-rand-trainers').checked,
    types: document.getElementById('toggle-rand-types').checked,
    abilities: document.getElementById('toggle-rand-abilities').checked,
    movesets: document.getElementById('toggle-rand-movesets').checked,
    coop_noleg: document.getElementById('toggle-rand-noleg').checked,
    coop_simstr: false,
    shiny: shinyThr,
    seed: worldSeedText,
    coop_seed: coopSeedText
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
  document.getElementById('rand-status-text').innerText = data.ok ? "Terminé !" : "Erreur";
  
  if (data.ok) {
    // Update starters cards if returned
    if (data.starters && data.starters.length === 3) {
      data.starters.forEach((st, idx) => {
        const frName = pokemonNames[st.id] || st.name;
        setStarterSlot(idx + 1, st.id, frName);
      });
    }
    alert("Randomisation terminée avec succès !\nFichier de rapport : " + data.report_file);
  } else {
    alert("Erreur lors de la randomisation :\n" + (data.error || 'Erreur inconnue'));
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
  box.innerHTML = '<em>Recherche de mise à jour sur GitHub...</em>';
  await window.pywebview.api.check_for_updates();
}

window.onUpdateCheckResult = (data) => {
  const box = document.getElementById('update-result-box');
  if (data.available) {
    box.innerHTML = `
      <div style="background-color: #064e3b; border: 1px solid #10b981; padding: 10px; border-radius: 4px; color: #a7f3d0;">
        <strong>Nouvelle version disponible : ${data.latest} !</strong> (Version actuelle : ${data.current})<br>
        <button class="pixel-btn primary mini mt-2" onclick="window.pywebview.api.open_external_url('${data.url}')">Télécharger la mise à jour</button>
      </div>
    `;
  } else {
    box.innerHTML = `
      <div style="background-color: #1e293b; border: 1px solid #334155; padding: 10px; border-radius: 4px; color: #94a3b8;">
        Vous disposez de la dernière version (${data.current}).
      </div>
    `;
  }
};
