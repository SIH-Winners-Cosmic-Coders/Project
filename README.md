# AnnaDATA — Farm Digital Twin

AnnaDATA fuses **soil data, live weather, satellite vegetation index, crop
stage and farmer records** into a single digital twin of a field, then
recommends **irrigation, crop choice, nutrient application and risk
mitigation** — each with a confidence score, a cost-benefit estimate, and
the factors that drove it.

## What's included

- **Map-based field picker** — search a village/district or tap the map
  (street or satellite tiles), powered by OpenStreetMap/Nominatim + Esri.
- **Live data fusion** — weather + soil temperature/moisture from
  Open-Meteo, a simulated satellite NDVI reading (clearly labeled —
  see `src/services/satelliteApi.js` for how to swap in a real
  Sentinel-2/MODIS feed), and a per-field farmer record (crop stage,
  last irrigation, soil type, historical yield).
- **AI recommendation engine** (`src/services/aiService.js`) — calls
  Gemini when `VITE_GEMINI_API_KEY` is set, and **always** falls back to a
  transparent rule-based engine if the key is missing or the call fails,
  so the app is never left without a recommendation.
- **Confidence, cost-benefit & factors** on every recommendation card,
  shown with a radial confidence gauge.
- **Local language support** — UI strings are dictionary-driven
  (`src/i18n/translations.js`) with English and Hindi fully translated
  today; Odia, Bengali, Telugu, Tamil and Marathi are wired into the
  language switcher and fall back to English until translated (the
  language codes match the voice pipeline's codes, so text and voice
  stay consistent).
- **Offline synchronization** — field snapshots and farmer feedback are
  cached to `localStorage` (`src/services/offlineSync.js`). If the device
  goes offline, the last synced snapshot for a field is shown, and any
  new feedback is queued and flushed automatically once the browser
  fires an `online` event.
- **Farmer feedback loop** — thumbs up/down + comment per field,
  attached to the recommendation that was shown, for future retraining.

## Optional: voice pipeline (`server/`)

`server/voice_pipeline.py` is a FastAPI service (STT → Gemini/Sarvam →
translate → TTS) that lets a farmer speak a question and hear a spoken
answer in their language. It's independent of the web app above — wire
it up later by adding a "Ask by voice" button that posts to
`/api/v1/voice/master-consult`. Not started automatically.

## Getting started (web app)

```bash
npm install
cp .env.example .env   # then add your own VITE_GEMINI_API_KEY (optional)
npm run dev
```

The app works with **no API key** — it uses the rule-based recommendation
engine automatically. Add `VITE_GEMINI_API_KEY` in `.env` to switch to
Gemini-generated recommendations.

## Getting started (voice pipeline, optional)

```bash
cd server
pip install -r requirements.txt
cp ../.env.example .env   # fill in GEMINI_API_KEY and SARVAM_API_KEY
python voice_pipeline.py
```

## Project structure

```
src/
  components/     MapView, DataSidebar, RecommendationCard, ConfidenceGauge,
                   FeedbackForm, LanguageSwitcher, OfflineBanner
  services/        weatherApi, soilApi, satelliteApi, aiService, offlineSync
  data/            mockData.js (farmer record generator)
  i18n/            translations.js
  context/         LanguageContext.jsx
server/
  voice_pipeline.py   optional FastAPI voice consult endpoint
```

## Notes / next steps

- Replace `estimateNDVI` in `satelliteApi.js` with a real satellite data
  provider when available (needs a server-side key, e.g. Google Earth
  Engine or Copernicus).
- Replace `getFarmerRecord` in `data/mockData.js` with a real farmer/CRM
  backend once one exists.
- `offlineSync.js` currently simulates the sync endpoint client-side;
  point `queueAction`/`flushQueue` at a real API once a backend exists.
- **Security**: never commit a real `.env` — only `.env.example` should be
  checked in. If a real API key was ever pasted into a shared file or
  chat, rotate it.
