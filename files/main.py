"""
Climate-Resilient Farm Digital Twin — API
==========================================
FastAPI backend serving:
  - farm twin state (sensors + weather + satellite + crop stage)
  - explainable irrigation / crop / nutrient / risk recommendations
  - farmer feedback capture (closes the loop for future model tuning)
  - offline batch sync for connectivity-poor rural areas
  - i18n string catalog for the frontend

Run:
    pip install -r requirements.txt
    uvicorn main:app --reload --port 8000

Docs at http://localhost:8000/docs
"""
from __future__ import annotations

import time
import uuid
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import engine
from i18n import SUPPORTED_LANGUAGES, full_catalog
from models import Farm, Feedback, SensorReading, SyncBatch, store

app = FastAPI(
    title="Farm Digital Twin API",
    description="Explainable irrigation, crop, nutrient and risk advisory for smallholder farms.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten to known origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------------------------------
# Health & i18n
# --------------------------------------------------------------------------

@app.get("/api/health")
def health():
    return {"status": "ok", "time": time.time()}


@app.get("/api/languages")
def languages():
    return SUPPORTED_LANGUAGES


@app.get("/api/i18n/{lang}")
def i18n_catalog(lang: str):
    return full_catalog(lang)


# --------------------------------------------------------------------------
# Farms & twin state
# --------------------------------------------------------------------------

@app.get("/api/farms")
def list_farms():
    return [
        {
            "farm_id": f.farm_id,
            "name": f.name,
            "owner": f.owner,
            "village": f.village,
            "district": f.district,
            "state": f.state,
            "crop": f.crop_stage.crop,
            "stage": f.crop_stage.stage,
            "preferred_language": f.preferred_language,
        }
        for f in store.farms.values()
    ]


def _get_farm(farm_id: str) -> Farm:
    farm = store.farms.get(farm_id)
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    return farm


@app.get("/api/farms/{farm_id}/twin")
def get_twin(farm_id: str):
    farm = _get_farm(farm_id)
    readings = store.sensor_readings.get(farm_id, [])
    latest_sensor = readings[-1] if readings else None
    weather = store.weather.get(farm_id)
    sat = store.satellite.get(farm_id)

    return {
        "farm": farm.model_dump(),
        "latest_sensor": latest_sensor.model_dump() if latest_sensor else None,
        "sensor_history": [r.model_dump() for r in readings[-30:]],
        "weather": weather.model_dump() if weather else None,
        "satellite": sat.model_dump() if sat else None,
    }


# --------------------------------------------------------------------------
# Sensor ingestion
# --------------------------------------------------------------------------

@app.post("/api/farms/{farm_id}/sensors")
def push_sensor_reading(farm_id: str, reading: SensorReading):
    _get_farm(farm_id)
    if reading.farm_id != farm_id:
        raise HTTPException(status_code=400, detail="farm_id mismatch")
    store.sensor_readings.setdefault(farm_id, []).append(reading)
    return {"accepted": True, "count": len(store.sensor_readings[farm_id])}


# --------------------------------------------------------------------------
# Recommendations
# --------------------------------------------------------------------------

@app.get("/api/farms/{farm_id}/recommendations")
def get_recommendations(farm_id: str, lang: str = "en"):
    farm = _get_farm(farm_id)
    lang = lang if lang in SUPPORTED_LANGUAGES else farm.preferred_language

    readings = store.sensor_readings.get(farm_id, [])
    if not readings:
        raise HTTPException(status_code=422, detail="No sensor data available for this farm yet")
    sensor = readings[-1]
    weather = store.weather.get(farm_id)
    sat = store.satellite.get(farm_id)
    if not weather or not sat:
        raise HTTPException(status_code=422, detail="Weather or satellite data missing for this farm")

    recs = engine.generate_all(farm, sensor, weather, sat, lang)
    result = [r.to_dict() for r in recs]

    store.recommendation_log.append({
        "farm_id": farm_id, "lang": lang, "timestamp": time.time(),
        "recommendation_ids": [r["id"] for r in result],
    })
    return {"farm_id": farm_id, "lang": lang, "generated_at": time.time(), "recommendations": result}


# --------------------------------------------------------------------------
# Feedback (closes the loop — farmer tells the system whether advice worked)
# --------------------------------------------------------------------------

@app.post("/api/feedback")
def submit_feedback(fb: Feedback):
    _get_farm(fb.farm_id)
    store.feedback.append(fb)
    return {"accepted": True, "total_feedback": len(store.feedback)}


@app.get("/api/farms/{farm_id}/feedback")
def list_feedback(farm_id: str):
    _get_farm(farm_id)
    items = [f for f in store.feedback if f.farm_id == farm_id]
    helpful = sum(1 for f in items if f.rating == "helpful")
    return {
        "total": len(items),
        "helpful_pct": round(100 * helpful / len(items), 1) if items else None,
        "items": [f.model_dump() for f in items],
    }


# --------------------------------------------------------------------------
# Offline sync
# --------------------------------------------------------------------------
# Frontend queues sensor readings & feedback captured while offline in
# localStorage/IndexedDB, tagged with client-generated UUIDs, and replays
# them here once connectivity returns. `client_generated_ids` makes the
# operation idempotent — resubmitting an already-synced batch is a no-op.

class SyncResult(BaseModel):
    accepted_sensor_readings: int
    accepted_feedback: int
    duplicate_ids_skipped: int
    server_time: float


@app.post("/api/sync", response_model=SyncResult)
def sync_offline_batch(batch: SyncBatch):
    _get_farm(batch.farm_id)

    accepted_sensors = 0
    accepted_feedback = 0
    duplicates = 0

    new_ids = [cid for cid in batch.client_generated_ids if cid not in store.synced_ids]
    if len(new_ids) < len(batch.client_generated_ids):
        duplicates = len(batch.client_generated_ids) - len(new_ids)

    if new_ids or not batch.client_generated_ids:
        for reading in batch.sensor_readings:
            reading.source = "synced_offline"
            store.sensor_readings.setdefault(batch.farm_id, []).append(reading)
            accepted_sensors += 1
        for fb in batch.feedback:
            store.feedback.append(fb)
            accepted_feedback += 1
        for cid in batch.client_generated_ids:
            store.synced_ids.add(cid)

    return SyncResult(
        accepted_sensor_readings=accepted_sensors,
        accepted_feedback=accepted_feedback,
        duplicate_ids_skipped=duplicates,
        server_time=time.time(),
    )


# --------------------------------------------------------------------------
# Convenience: simulate a new sensor/weather/satellite tick (for demos)
# --------------------------------------------------------------------------

@app.post("/api/farms/{farm_id}/simulate-tick")
def simulate_tick(farm_id: str):
    """Nudges sensor/weather/satellite values to simulate a day passing —
    handy for demoing how recommendations change as the farm twin evolves."""
    import random

    farm = _get_farm(farm_id)
    readings = store.sensor_readings.setdefault(farm_id, [])
    last = readings[-1] if readings else SensorReading(
        farm_id=farm_id, soil_moisture_pct=40, soil_temp_c=28, soil_ph=6.5, soil_ec_ds_m=1.5
    )
    new_reading = SensorReading(
        farm_id=farm_id,
        soil_moisture_pct=max(5, min(95, last.soil_moisture_pct + random.uniform(-8, 4))),
        soil_temp_c=max(15, last.soil_temp_c + random.uniform(-1, 1)),
        soil_ph=last.soil_ph + random.uniform(-0.1, 0.1),
        soil_ec_ds_m=max(0.2, last.soil_ec_ds_m + random.uniform(-0.2, 0.2)),
    )
    readings.append(new_reading)

    w = store.weather[farm_id]
    w.rainfall_next_48h_mm = max(0, w.rainfall_next_48h_mm + random.uniform(-15, 15))
    w.temp_max_c = w.temp_max_c + random.uniform(-1.5, 1.5)
    w.humidity_pct = max(10, min(100, w.humidity_pct + random.uniform(-5, 5)))
    w.timestamp = time.time()

    s = store.satellite[farm_id]
    s.ndvi = max(0.05, min(0.95, s.ndvi + random.uniform(-0.05, 0.05)))
    s.ndwi = max(-1, min(1, s.ndwi + random.uniform(-0.05, 0.05)))
    s.timestamp = time.time()

    farm.crop_stage.days_after_sowing += 1

    return {"ok": True, "new_sensor_reading": new_reading.model_dump()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
