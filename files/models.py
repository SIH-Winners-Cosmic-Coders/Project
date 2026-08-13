"""
In-memory data models and seed data for the Farm Digital Twin.

In production these would be backed by a real database (Postgres +
TimescaleDB for sensor time-series is a common choice) but an in-memory
store keeps this reference implementation runnable anywhere with zero
setup, while keeping the exact same shape an API client would see.
"""
from __future__ import annotations

import itertools
import time
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

# --------------------------------------------------------------------------
# Pydantic schemas (also used for request validation / OpenAPI docs)
# --------------------------------------------------------------------------


class SensorReading(BaseModel):
    farm_id: str
    timestamp: float = Field(default_factory=time.time)
    soil_moisture_pct: float          # 0-100, % volumetric water content
    soil_temp_c: float
    soil_ph: float
    soil_ec_ds_m: float               # electrical conductivity -> salinity proxy
    source: str = "sensor"            # sensor | manual | synced_offline


class WeatherSnapshot(BaseModel):
    farm_id: str
    timestamp: float = Field(default_factory=time.time)
    rainfall_next_48h_mm: float
    temp_max_c: float
    temp_min_c: float
    humidity_pct: float
    wind_kmph: float
    forecast_confidence_pct: float = 80.0


class SatelliteSnapshot(BaseModel):
    farm_id: str
    timestamp: float = Field(default_factory=time.time)
    ndvi: float        # 0-1 vegetation vigor
    ndwi: float         # -1..1 canopy water content
    cloud_free: bool = True


class CropStage(BaseModel):
    crop: str
    variety: Optional[str] = None
    sowing_date: float
    stage: str            # sowing | vegetative | flowering | grain_fill | maturity
    days_after_sowing: int


class FarmerRecord(BaseModel):
    last_irrigation_ts: Optional[float] = None
    last_fertilizer_ts: Optional[float] = None
    last_fertilizer_type: Optional[str] = None
    yield_history_t_per_ha: List[float] = []
    irrigation_source: str = "canal"   # canal | borewell | rainfed
    budget_sensitivity: str = "medium"  # low | medium | high (how cost-averse farmer is)


class Farm(BaseModel):
    farm_id: str
    name: str
    owner: str
    village: str
    district: str
    state: str
    lat: float
    lon: float
    area_ha: float
    soil_type: str          # sandy_loam | clay | silty_loam | black_cotton | red_loam
    preferred_language: str = "en"
    crop_stage: CropStage
    farmer_record: FarmerRecord


class Feedback(BaseModel):
    farm_id: str
    recommendation_id: str
    rating: str          # helpful | not_helpful | partially_helpful
    comment: Optional[str] = None
    applied: Optional[bool] = None
    timestamp: float = Field(default_factory=time.time)


class SyncBatch(BaseModel):
    farm_id: str
    sensor_readings: List[SensorReading] = []
    feedback: List[Feedback] = []
    client_generated_ids: List[str] = []  # for idempotent replay


# --------------------------------------------------------------------------
# In-memory "database"
# --------------------------------------------------------------------------

_id_counter = itertools.count(1)


def next_id(prefix: str) -> str:
    return f"{prefix}_{next(_id_counter)}"


class Store:
    def __init__(self) -> None:
        self.farms: Dict[str, Farm] = {}
        self.sensor_readings: Dict[str, List[SensorReading]] = {}
        self.weather: Dict[str, WeatherSnapshot] = {}
        self.satellite: Dict[str, SatelliteSnapshot] = {}
        self.feedback: List[Feedback] = []
        self.recommendation_log: List[Dict[str, Any]] = []
        self.synced_ids: set = set()
        self._seed()

    def _seed(self) -> None:
        now = time.time()
        day = 86400

        farm1 = Farm(
            farm_id="farm_001",
            name="Halder Plot – North Field",
            owner="Bikash Halder",
            village="Amtala",
            district="South 24 Parganas",
            state="West Bengal",
            lat=22.15,
            lon=88.24,
            area_ha=1.2,
            soil_type="clay",
            preferred_language="bn",
            crop_stage=CropStage(
                crop="rice",
                variety="Swarna",
                sowing_date=now - 45 * day,
                stage="flowering",
                days_after_sowing=45,
            ),
            farmer_record=FarmerRecord(
                last_irrigation_ts=now - 4 * day,
                last_fertilizer_ts=now - 20 * day,
                last_fertilizer_type="urea",
                yield_history_t_per_ha=[3.8, 4.1, 3.6],
                irrigation_source="canal",
                budget_sensitivity="high",
            ),
        )

        farm2 = Farm(
            farm_id="farm_002",
            name="Sharma Kheti – Plot 3",
            owner="Rakesh Sharma",
            village="Bhiwadi",
            district="Alwar",
            state="Rajasthan",
            lat=28.21,
            lon=76.86,
            area_ha=2.5,
            soil_type="sandy_loam",
            preferred_language="hi",
            crop_stage=CropStage(
                crop="cotton",
                variety="Bt Cotton",
                sowing_date=now - 70 * day,
                stage="grain_fill",
                days_after_sowing=70,
            ),
            farmer_record=FarmerRecord(
                last_irrigation_ts=now - 9 * day,
                last_fertilizer_ts=now - 30 * day,
                last_fertilizer_type="DAP",
                yield_history_t_per_ha=[1.4, 1.6, 1.5],
                irrigation_source="borewell",
                budget_sensitivity="medium",
            ),
        )

        for f in (farm1, farm2):
            self.farms[f.farm_id] = f
            self.sensor_readings[f.farm_id] = []

        self.sensor_readings["farm_001"].append(
            SensorReading(
                farm_id="farm_001",
                soil_moisture_pct=22.0,
                soil_temp_c=29.5,
                soil_ph=6.1,
                soil_ec_ds_m=2.8,
            )
        )
        self.sensor_readings["farm_002"].append(
            SensorReading(
                farm_id="farm_002",
                soil_moisture_pct=11.5,
                soil_temp_c=34.0,
                soil_ph=7.6,
                soil_ec_ds_m=1.1,
            )
        )

        self.weather["farm_001"] = WeatherSnapshot(
            farm_id="farm_001",
            rainfall_next_48h_mm=65.0,
            temp_max_c=33.0,
            temp_min_c=27.0,
            humidity_pct=88.0,
            wind_kmph=14.0,
            forecast_confidence_pct=76.0,
        )
        self.weather["farm_002"] = WeatherSnapshot(
            farm_id="farm_002",
            rainfall_next_48h_mm=0.0,
            temp_max_c=41.5,
            temp_min_c=28.0,
            humidity_pct=24.0,
            wind_kmph=22.0,
            forecast_confidence_pct=83.0,
        )

        self.satellite["farm_001"] = SatelliteSnapshot(
            farm_id="farm_001", ndvi=0.71, ndwi=0.32, cloud_free=False
        )
        self.satellite["farm_002"] = SatelliteSnapshot(
            farm_id="farm_002", ndvi=0.44, ndwi=-0.18, cloud_free=True
        )


store = Store()
