/* ==========================================================================
   Farm Digital Twin — frontend app
   Vanilla JS, no build step. Talks to the FastAPI backend, renders the
   field-strip twin visual + explainable recommendation cards, and queues
   farmer feedback / sensor pushes in localStorage when offline so nothing
   is lost on a poor rural connection.
   ========================================================================== */

const API_BASE = window.API_BASE || "http://localhost:8000";
const QUEUE_KEY = "fdt_offline_queue_v1";
const LANG_KEY = "fdt_lang";

const state = {
  farms: [],
  currentFarmId: null,
  lang: localStorage.getItem(LANG_KEY) || "en",
  i18n: {},
  twin: null,
  recommendations: [],
};

const $ = (sel) => document.querySelector(sel);

// -------------------------------------------------------------- fetch helpers

async function api(path, opts = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...opts,
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`${res.status} ${path}: ${body}`);
  }
  return res.json();
}

// -------------------------------------------------------------- offline queue

function loadQueue() {
  try { return JSON.parse(localStorage.getItem(QUEUE_KEY)) || { sensor_readings: [], feedback: [], client_generated_ids: [] }; }
  catch { return { sensor_readings: [], feedback: [], client_generated_ids: [] }; }
}
function saveQueue(q) { localStorage.setItem(QUEUE_KEY, JSON.stringify(q)); }

function queueFeedback(fb) {
  const q = loadQueue();
  const id = `fb_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
  q.feedback.push(fb);
  q.client_generated_ids.push(id);
  saveQueue(q);
  updateSyncStatus();
}

async function flushQueue() {
  const q = loadQueue();
  if (q.feedback.length === 0 && q.sensor_readings.length === 0) { updateSyncStatus(); return; }
  if (!state.currentFarmId) return;
  setSyncing(true);
  try {
    const result = await api("/api/sync", {
      method: "POST",
      body: JSON.stringify({
        farm_id: state.currentFarmId,
        sensor_readings: q.sensor_readings,
        feedback: q.feedback,
        client_generated_ids: q.client_generated_ids,
      }),
    });
    localStorage.removeItem(QUEUE_KEY);
    showToast(`Synced ${result.accepted_feedback + result.accepted_sensor_readings} item(s)`);
  } catch (e) {
    console.warn("Sync failed, will retry later", e);
  } finally {
    setSyncing(false);
    updateSyncStatus();
  }
}

function setSyncing(on) {
  const el = $("#syncStatus");
  el.classList.toggle("syncing", on);
}

function updateSyncStatus() {
  const el = $("#syncStatus");
  const label = $("#syncLabel");
  const q = loadQueue();
  const pending = q.feedback.length + q.sensor_readings.length;
  const offline = !navigator.onLine;
  el.classList.toggle("offline", offline);
  $("#offlineBanner").hidden = !offline;
  if (offline) {
    label.textContent = t("offline_banner");
  } else if (pending > 0) {
    label.textContent = `${t("syncing")} (${pending})`;
  } else {
    label.textContent = t("synced");
  }
}

window.addEventListener("online", () => { updateSyncStatus(); flushQueue(); });
window.addEventListener("offline", updateSyncStatus);

// -------------------------------------------------------------- i18n

function t(key) {
  return (state.i18n && state.i18n[key]) || key;
}

function applyStaticI18n() {
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    el.textContent = t(key);
  });
}

async function loadI18n(lang) {
  state.i18n = await api(`/api/i18n/${lang}`);
  state.lang = lang;
  localStorage.setItem(LANG_KEY, lang);
  applyStaticI18n();
  updateSyncStatus();
}

// -------------------------------------------------------------- farms & twin

async function loadFarms() {
  state.farms = await api("/api/farms");
  const sel = $("#farmSelect");
  sel.innerHTML = state.farms.map((f) => `<option value="${f.farm_id}">${f.name} — ${f.village}</option>`).join("");
  if (!state.currentFarmId) state.currentFarmId = state.farms[0]?.farm_id;
  sel.value = state.currentFarmId;
}

async function loadTwinAndRecommendations() {
  const farmId = state.currentFarmId;
  const [twin, recs] = await Promise.all([
    api(`/api/farms/${farmId}/twin`),
    api(`/api/farms/${farmId}/recommendations?lang=${state.lang}`),
  ]);
  state.twin = twin;
  state.recommendations = recs.recommendations;
  renderFarmMeta();
  renderFieldStrip();
  renderReadouts();
  renderRecommendations();
}

function renderFarmMeta() {
  const f = state.twin.farm;
  $("#farmMeta").innerHTML = `
    <strong>${f.owner}</strong>
    ${f.village}, ${f.district}<br>${f.state}<br>
    ${f.area_ha} ha · ${f.soil_type.replace("_", " ")}
  `;
}

// ---- field strip: soil-moisture depth bands + NDVI canopy tint

function renderFieldStrip() {
  const sensor = state.twin.latest_sensor;
  const sat = state.twin.satellite;
  const cs = state.twin.farm.crop_stage;

  $("#stripCrop").textContent = cs.crop;
  $("#stripStage").textContent = cs.stage.replace("_", " ");
  $("#stripDas").textContent = `DAS ${cs.days_after_sowing}`;

  // canopy tint driven by NDVI (vegetation vigor)
  const canopy = $("#canopyLayer");
  const ndvi = sat ? sat.ndvi : 0.5;
  canopy.style.opacity = String(0.35 + ndvi * 0.65);
  canopy.style.height = `${30 + ndvi * 40}px`;

  // moisture depth bands drawn as horizontal bars fading with depth,
  // width mapped to soil_moisture_pct
  const svg = $("#moistureSvg");
  const moisture = sensor ? sensor.soil_moisture_pct : 30;
  const bands = 5;
  let rects = "";
  for (let i = 0; i < bands; i++) {
    const y = (i / bands) * 140;
    const bandH = 140 / bands;
    const depthFalloff = 1 - i / (bands * 1.4);
    const w = Math.min(1000, (moisture / 100) * 1000 * depthFalloff);
    const opacity = 0.15 + 0.5 * depthFalloff;
    rects += `<rect x="0" y="${y}" width="${w}" height="${bandH - 3}" fill="var(--water)" opacity="${opacity.toFixed(2)}" rx="3"></rect>`;
  }
  svg.innerHTML = rects;
}

function renderReadouts() {
  const s = state.twin.latest_sensor;
  const w = state.twin.weather;
  const sat = state.twin.satellite;
  const items = [
    [t("f_soil_moisture"), s ? `${s.soil_moisture_pct.toFixed(1)}%` : "—"],
    [t("f_rainfall_forecast"), w ? `${w.rainfall_next_48h_mm.toFixed(0)} mm` : "—"],
    [t("f_temp_max"), w ? `${w.temp_max_c.toFixed(0)}°C` : "—"],
    [t("f_humidity"), w ? `${w.humidity_pct.toFixed(0)}%` : "—"],
    [t("f_ndvi"), sat ? sat.ndvi.toFixed(2) : "—"],
    [t("f_ndwi"), sat ? sat.ndwi.toFixed(2) : "—"],
    [t("f_soil_ec"), s ? `${s.soil_ec_ds_m.toFixed(1)} dS/m` : "—"],
    ["pH", s ? s.soil_ph.toFixed(1) : "—"],
  ];
  $("#twinReadouts").innerHTML = items.map(([k, v]) => `
    <div class="readout"><div class="rk">${k}</div><div class="rv">${v}</div></div>
  `).join("");
}

// ---- recommendation cards

const CATEGORY_KEY = { irrigation: "irrigation", nutrient: "nutrient", crop_choice: "crop_choice", risk: "risk" };

function inr(n) {
  return `₹${Math.round(n).toLocaleString("en-IN")}`;
}

function renderRecommendations() {
  const grid = $("#recGrid");
  grid.innerHTML = state.recommendations.map(cardHtml).join("");

  grid.querySelectorAll(".why-toggle").forEach((btn) => {
    btn.addEventListener("click", () => {
      const panel = btn.nextElementSibling;
      const open = panel.classList.toggle("open");
      btn.setAttribute("aria-expanded", String(open));
    });
  });

  grid.querySelectorAll(".fb-btn").forEach((btn) => {
    btn.addEventListener("click", () => onFeedback(btn));
  });
}

function cardHtml(rec) {
  const factorsHtml = rec.factors.map((f) => `
    <div class="factor-row">
      <span class="factor-name">${f.label}</span>
      <span class="factor-value">${f.value}</span>
      <span class="factor-dir ${f.direction}">${dirSymbol(f.direction)}</span>
    </div>
  `).join("");

  return `
  <article class="rec-card" data-severity="${rec.severity}" data-rec-id="${rec.id}">
    <div class="rec-head">
      <div>
        <div class="rec-category">${t(CATEGORY_KEY[rec.category])}</div>
        <h3 class="rec-action">${rec.action_label}</h3>
      </div>
      <span class="severity-pill">${rec.severity}</span>
    </div>

    <div class="confidence-row">
      <span class="confidence-label">${t("confidence")}</span>
      <div class="confidence-track"><div class="confidence-fill" style="width:${rec.confidence_pct}%"></div></div>
      <span class="confidence-pct">${rec.confidence_pct}%</span>
    </div>

    <div class="cost-benefit">
      <div class="cb-item"><div class="cb-k">${t("expected_cost")}</div><div class="cb-v">${inr(rec.expected_cost_inr)}</div></div>
      <div class="cb-item"><div class="cb-k">${t("expected_benefit")}</div><div class="cb-v">${inr(rec.expected_benefit_inr)}</div></div>
      <div class="cb-item ${rec.net_benefit_inr >= 0 ? "pos" : "neg"}"><div class="cb-k">${t("net_benefit")}</div><div class="cb-v">${inr(rec.net_benefit_inr)}</div></div>
    </div>

    <button class="why-toggle" aria-expanded="false">
      <span class="chev">▸</span> ${t("why")}
    </button>
    <div class="factors">${factorsHtml}</div>

    <div class="feedback-row">
      <span class="feedback-prompt">${t("feedback_prompt")}</span>
      <button class="fb-btn" data-rating="helpful">${t("helpful")}</button>
      <button class="fb-btn" data-rating="partially_helpful">${t("partial")}</button>
      <button class="fb-btn" data-rating="not_helpful">${t("not_helpful")}</button>
    </div>
  </article>`;
}

function dirSymbol(dir) {
  if (dir === "increases_need") return "▲";
  if (dir === "decreases_need") return "▼";
  return "•";
}

async function onFeedback(btn) {
  const card = btn.closest(".rec-card");
  const recId = card.dataset.recId;
  card.querySelectorAll(".fb-btn").forEach((b) => b.classList.remove("selected"));
  btn.classList.add("selected");

  const feedback = {
    farm_id: state.currentFarmId,
    recommendation_id: recId,
    rating: btn.dataset.rating,
    timestamp: Date.now() / 1000,
  };

  if (!navigator.onLine) {
    queueFeedback(feedback);
    showToast("Saved offline — will sync later");
    return;
  }
  try {
    await api("/api/feedback", { method: "POST", body: JSON.stringify(feedback) });
    showToast("Feedback recorded — thank you");
  } catch (e) {
    queueFeedback(feedback);
    showToast("Saved offline — will sync later");
  }
}

// -------------------------------------------------------------- toast

let toastTimer = null;
function showToast(msg) {
  const el = $("#toast");
  el.textContent = msg;
  el.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { el.hidden = true; }, 2600);
}

// -------------------------------------------------------------- wiring

async function refreshAll() {
  try {
    await loadTwinAndRecommendations();
  } catch (e) {
    console.error(e);
    showToast("Could not reach the farm twin API");
  }
}

async function init() {
  $("#langSelect").value = state.lang;
  await loadI18n(state.lang);

  try {
    await loadFarms();
  } catch (e) {
    console.error(e);
    showToast(`Cannot reach backend at ${API_BASE}`);
    return;
  }

  await refreshAll();
  updateSyncStatus();

  $("#farmSelect").addEventListener("change", async (e) => {
    state.currentFarmId = e.target.value;
    await refreshAll();
  });

  $("#langSelect").addEventListener("change", async (e) => {
    await loadI18n(e.target.value);
    // Recommendation text (action labels, factor labels) is localized
    // server-side, so re-fetch rather than just re-rendering cached data.
    await refreshAll();
  });

  $("#tickBtn").addEventListener("click", async () => {
    if (!navigator.onLine) { showToast(t("offline_banner")); return; }
    try {
      await api(`/api/farms/${state.currentFarmId}/simulate-tick`, { method: "POST" });
      await refreshAll();
      showToast("Advanced one day");
    } catch (e) {
      showToast("Simulation failed");
    }
  });

  // periodic background flush attempt
  setInterval(() => { if (navigator.onLine) flushQueue(); }, 15000);
}

init();
