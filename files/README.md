# Climate-Resilient Farm Digital Twin

An explainable advisory platform that fuses soil sensors, local weather,
satellite indices, crop growth stage and farmer records into a live "digital
twin" of a field, and turns that into **irrigation, crop-choice, nutrient
and risk-mitigation recommendations** — each with a confidence score, an
expected cost-benefit in ₹, and a transparent breakdown of the factors that
drove the decision.

Stack: **FastAPI (Python)** backend + **HTML / CSS / vanilla JS** frontend
(no build step, no framework — runs anywhere).

## Why it's explainable

Every recommendation comes from a small set of named, inspectable rules
(`backend/engine.py`), not a black-box model. Each rule contributes a
signed "factor" — its raw sensor value, the direction it pushed the
decision, and its weight. Confidence is computed from how strongly the
factors agree plus how complete the underlying data is; cost-benefit comes
from an editable reference table (crop prices, irrigation cost per mm,
fertilizer cost) rather than a hidden formula. If you later swap in a real
ML model, keep it emitting the same `Factor` list (e.g. mapped SHAP values)
so the "why" panel and API contract don't have to change.

## Features

- **Farm twin state**: soil moisture/temp/pH/EC, 48h rainfall forecast,
  temperature, humidity, NDVI/NDWI satellite indices, crop stage.
- **Four recommendation categories**: irrigation, nutrient application,
  crop choice (seasonal diversification), risk mitigation (heat, fungal,
  waterlogging).
- **Confidence + cost/benefit + "why"** on every card, with a plain-language
  factor breakdown (value, direction, weight).
- **Local language support**: English, Hindi, Bengali — both the UI chrome
  and the recommendation text itself are localized server-side (`i18n.py`),
  so adding a language is additive, not a rewrite.
- **Offline-first feedback & sync**: farmer feedback (👍/〰/👎 per
  recommendation) is queued in `localStorage` when offline and flushed to
  `POST /api/sync` once connectivity returns, using client-generated IDs so
  replays are idempotent.
- **Farmer feedback loop**: stored per-recommendation so a future model
  version can be tuned against real acceptance/rejection data.

## Project layout

```
backend/
  main.py        FastAPI app & routes
  engine.py       Explainable recommendation engine (the core logic)
  models.py       Pydantic schemas + in-memory seeded "database"
  i18n.py         Translation catalogs (en / hi / bn)
  requirements.txt
frontend/
  index.html      Dashboard shell
  style.css       Design system (soil/field palette, no build step)
  app.js          API calls, field-strip rendering, cards, offline queue
```

## Running it

**Backend**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
API docs: http://localhost:8000/docs

**Frontend** (any static file server)
```bash
cd frontend
python3 -m http.server 8080
```
Open http://localhost:8080 — it talks to the API at `http://localhost:8000`
by default. To point at a different backend, set `window.API_BASE` before
`app.js` loads, e.g. add `<script>window.API_BASE = "https://your-api";</script>`
in `index.html`.

Two demo farms are seeded (a rice farm in West Bengal, a cotton farm in
Rajasthan) so you can see how recommendations differ by soil type, crop
stage, climate and irrigation source. Use **"Simulate next day"** to nudge
sensor/weather/satellite values forward and watch recommendations update.

## API summary

| Endpoint | Purpose |
|---|---|
| `GET /api/farms` | List farms |
| `GET /api/farms/{id}/twin` | Full twin state (sensors, weather, satellite, crop stage) |
| `POST /api/farms/{id}/sensors` | Push a new sensor reading |
| `GET /api/farms/{id}/recommendations?lang=` | Generate the 4 explainable recommendations |
| `POST /api/feedback` | Record farmer feedback on a recommendation |
| `POST /api/sync` | Batch-replay offline-queued sensor readings + feedback |
| `GET /api/i18n/{lang}` | UI string catalog |

## Notes on production hardening (out of scope for this reference build)

- Swap the in-memory `Store` for Postgres/TimescaleDB; keep the same
  Pydantic schemas as the DB row shape.
- Real weather/satellite ingestion (e.g. IMD/Open-Meteo for weather, a
  Sentinel-2 NDVI/NDWI pipeline) behind the same `WeatherSnapshot` /
  `SatelliteSnapshot` contracts.
- Auth per farm/owner, and rate limiting on `/api/sync`.
- Move offline storage from `localStorage` to IndexedDB for larger queues
  and add a service worker so the app shell itself loads offline, not just
  data sync.
