"""
Explainable recommendation engine.

Design intent
--------------
Every recommendation is produced by a small set of *named, inspectable*
rules rather than an opaque model. Each rule contributes a signed score
and is recorded as a "factor" with its raw sensor value, the direction it
pushed the decision, and a weight. This means every recommendation can
show its work: confidence is derived from how much the factors agree and
how complete the underlying data is, and cost-benefit is derived from
transparent, editable reference tables (see COST_REFERENCE) rather than
a black box.

Swap-in point for real ML: replace the `score_*` functions with model
inference, but keep returning the same `Factor` list (e.g. SHAP values
mapped into this schema) so the API contract — and the UI that renders
"why" — never has to change.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import List, Literal

from i18n import t
from models import Farm, SatelliteSnapshot, SensorReading, WeatherSnapshot

Direction = Literal["increases_need", "decreases_need", "neutral"]


@dataclass
class Factor:
    key: str
    label: str
    value: str
    weight: float          # 0-1, relative influence on this decision
    direction: Direction

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "label": self.label,
            "value": self.value,
            "weight": round(self.weight, 2),
            "direction": self.direction,
        }


@dataclass
class Recommendation:
    id: str
    category: str            # irrigation | crop_choice | nutrient | risk
    action_key: str
    action_label: str
    confidence_pct: float
    expected_cost_inr: float
    expected_benefit_inr: float
    factors: List[Factor] = field(default_factory=list)
    severity: str = "normal"   # normal | advisory | urgent

    @property
    def net_benefit_inr(self) -> float:
        return round(self.expected_benefit_inr - self.expected_cost_inr, 2)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "category": self.category,
            "action_key": self.action_key,
            "action_label": self.action_label,
            "confidence_pct": round(self.confidence_pct, 1),
            "expected_cost_inr": round(self.expected_cost_inr, 2),
            "expected_benefit_inr": round(self.expected_benefit_inr, 2),
            "net_benefit_inr": self.net_benefit_inr,
            "cost_benefit_ratio": (
                round(self.expected_benefit_inr / self.expected_cost_inr, 2)
                if self.expected_cost_inr > 0
                else None
            ),
            "severity": self.severity,
            "factors": [f.to_dict() for f in self.factors],
        }


# --------------------------------------------------------------------------
# Reference tables — the "cost-benefit" ground truth. In production these
# would come from a mandi-price feed + agronomy dept. cost norms, kept
# editable by an agronomist without touching code.
# --------------------------------------------------------------------------

CROP_PRICE_INR_PER_KG = {"rice": 22, "cotton": 65, "wheat": 24, "maize": 20}
IRRIGATION_COST_PER_MM_PER_HA = {"canal": 90, "borewell": 260, "rainfed": 0}
FERTILIZER_COST_INR = {"urea_topdress": 900, "npk_balanced": 1500}

# stage -> (moisture_low_pct, moisture_high_pct) optimal band, by crop
MOISTURE_BANDS = {
    "rice": {"sowing": (60, 80), "vegetative": (65, 85), "flowering": (70, 90),
             "grain_fill": (60, 80), "maturity": (40, 60)},
    "cotton": {"sowing": (30, 50), "vegetative": (35, 55), "flowering": (45, 65),
               "grain_fill": (40, 60), "maturity": (25, 45)},
    "default": {"sowing": (30, 55), "vegetative": (35, 60), "flowering": (40, 65),
                "grain_fill": (35, 60), "maturity": (25, 45)},
}

# soil_type -> recommended lower-water alternative crops for diversification
DIVERSIFICATION_OPTIONS = {
    "clay": ["jute", "pulses (post-rice)"],
    "sandy_loam": ["millet", "groundnut"],
    "black_cotton": ["sorghum", "chickpea"],
    "red_loam": ["groundnut", "pigeon pea"],
    "silty_loam": ["maize", "mustard"],
}


def _band(crop: str, stage: str) -> tuple[float, float]:
    table = MOISTURE_BANDS.get(crop, MOISTURE_BANDS["default"])
    return table.get(stage, MOISTURE_BANDS["default"]["vegetative"])


def _avg_yield(farm: Farm) -> float:
    hist = farm.farmer_record.yield_history_t_per_ha
    return sum(hist) / len(hist) if hist else 3.0


def _et_estimate(weather: WeatherSnapshot) -> float:
    """Very simplified Penman-style proxy (mm/day), for demo purposes only."""
    temp_factor = max(weather.temp_max_c - 20, 0) * 0.25
    humidity_factor = max(60 - weather.humidity_pct, 0) * 0.05
    wind_factor = weather.wind_kmph * 0.03
    return round(2.0 + temp_factor + humidity_factor + wind_factor, 1)


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _confidence(agree: float, data_completeness: float, forecast_conf: float) -> float:
    """Blend rule-agreement strength with data quality into a single 0-100 score."""
    base = 50 + agree * 40                     # how strongly the rules agree
    quality_penalty = (100 - data_completeness) * 0.2
    forecast_penalty = (100 - forecast_conf) * 0.1
    return _clamp(base - quality_penalty - forecast_penalty, 5, 97)


# --------------------------------------------------------------------------
# Irrigation
# --------------------------------------------------------------------------

def recommend_irrigation(farm: Farm, sensor: SensorReading, weather: WeatherSnapshot,
                          sat: SatelliteSnapshot, lang: str) -> Recommendation:
    lo, hi = _band(farm.crop_stage.crop, farm.crop_stage.stage)
    moisture = sensor.soil_moisture_pct
    et = _et_estimate(weather)
    rain = weather.rainfall_next_48h_mm

    deficit = lo - moisture           # positive => below optimal
    surplus = moisture - hi           # positive => above optimal
    rain_covers_deficit = rain >= (deficit / max(et, 1)) * et  # simple: rain expected to offset ET-driven loss

    factors: List[Factor] = [
        Factor("soil_moisture", t(lang, "f_soil_moisture"), f"{moisture:.1f}% (band {lo:.0f}-{hi:.0f}%)",
               0.9, "increases_need" if deficit > 0 else "decreases_need"),
        Factor("evapotranspiration", t(lang, "f_evapotranspiration"), f"{et:.1f} mm/day",
               0.6, "increases_need"),
        Factor("rainfall_forecast", t(lang, "f_rainfall_forecast"), f"{rain:.0f} mm",
               0.8, "decreases_need" if rain > 5 else "neutral"),
        Factor("ndwi", t(lang, "f_ndwi"), f"{sat.ndwi:.2f}",
               0.4, "increases_need" if sat.ndwi < 0 else "decreases_need"),
    ]

    agree = 0.0
    n_signals = 0
    for f in factors:
        n_signals += 1
        if deficit > 0 and f.direction == "increases_need":
            agree += f.weight
        elif deficit <= 0 and f.direction == "decreases_need":
            agree += f.weight
    agree_norm = agree / max(sum(f.weight for f in factors), 0.01)

    data_completeness = 100.0  # all four signals present in this reading
    confidence = _confidence(agree_norm, data_completeness, weather.forecast_confidence_pct)

    area = farm.area_ha
    cost_per_mm = IRRIGATION_COST_PER_MM_PER_HA.get(farm.farmer_record.irrigation_source, 150)
    price = CROP_PRICE_INR_PER_KG.get(farm.crop_stage.crop, 20)
    avg_yield_kg_ha = _avg_yield(farm) * 1000

    if surplus > 10 and rain > 30:
        action_key, severity = "drain_field", "urgent"
        mm_applied = 0
        # benefit = avoided waterlogging yield loss (assume up to 15% loss risk)
        expected_benefit = 0.15 * avg_yield_kg_ha * price * area * 0.5
        expected_cost = 300 * area  # labour to open drainage channels
    elif deficit > 15 and not rain_covers_deficit:
        action_key, severity = "irrigate_now", "urgent"
        mm_applied = round(deficit * 0.6 + et, 1)
        expected_cost = mm_applied * cost_per_mm * area
        # benefit = avoided yield loss from water stress at this stage (stage-weighted)
        stress_sensitivity = 0.22 if farm.crop_stage.stage in ("flowering", "grain_fill") else 0.12
        expected_benefit = stress_sensitivity * avg_yield_kg_ha * price * area
    elif deficit > 5:
        action_key, severity = "irrigate_light", "advisory"
        mm_applied = round(deficit * 0.3, 1)
        expected_cost = mm_applied * cost_per_mm * area
        expected_benefit = 0.08 * avg_yield_kg_ha * price * area
    else:
        action_key, severity = "hold_irrigation", "normal"
        mm_applied = 0
        expected_cost = 0
        expected_benefit = 0.03 * avg_yield_kg_ha * price * area  # value of not over-watering

    return Recommendation(
        id=f"irr_{farm.farm_id}_{int(time.time())}",
        category="irrigation",
        action_key=action_key,
        action_label=t(lang, action_key) + (f" (~{mm_applied} mm)" if mm_applied else ""),
        confidence_pct=confidence,
        expected_cost_inr=expected_cost,
        expected_benefit_inr=expected_benefit,
        factors=factors,
        severity=severity,
    )


# --------------------------------------------------------------------------
# Nutrient application
# --------------------------------------------------------------------------

def recommend_nutrient(farm: Farm, sensor: SensorReading, sat: SatelliteSnapshot, lang: str) -> Recommendation:
    stage = farm.crop_stage.stage
    ndvi = sat.ndvi
    expected_ndvi = {"sowing": 0.3, "vegetative": 0.65, "flowering": 0.75,
                      "grain_fill": 0.7, "maturity": 0.5}.get(stage, 0.6)
    ndvi_deficit = expected_ndvi - ndvi

    now = time.time()
    days_since = (
        int((now - farm.farmer_record.last_fertilizer_ts) / 86400)
        if farm.farmer_record.last_fertilizer_ts else 999
    )

    factors = [
        Factor("ndvi", t(lang, "f_ndvi"), f"{ndvi:.2f} (expected ~{expected_ndvi:.2f})",
               0.85, "increases_need" if ndvi_deficit > 0.05 else "decreases_need"),
        Factor("days_since_fertilizer", t(lang, "f_days_since_fertilizer"), f"{days_since} days",
               0.6, "increases_need" if days_since > 21 else "decreases_need"),
        Factor("soil_ec", t(lang, "f_soil_ec"), f"{sensor.soil_ec_ds_m:.1f} dS/m",
               0.4, "decreases_need" if sensor.soil_ec_ds_m > 3.0 else "neutral"),
        Factor("crop_stage", t(lang, "f_crop_stage"), stage.replace("_", " "),
               0.3, "increases_need" if stage in ("vegetative", "flowering") else "neutral"),
    ]

    agree = sum(f.weight for f in factors if f.direction == "increases_need")
    total_w = sum(f.weight for f in factors)
    agree_norm = agree / total_w
    confidence = _confidence(agree_norm if ndvi_deficit > 0.05 else 1 - agree_norm, 100.0, 90.0)

    area = farm.area_ha
    price = CROP_PRICE_INR_PER_KG.get(farm.crop_stage.crop, 20)
    avg_yield_kg_ha = _avg_yield(farm) * 1000

    salinity_capped = sensor.soil_ec_ds_m > 3.5

    if salinity_capped:
        action_key, severity = "hold_fertilizer", "advisory"
        expected_cost = 0
        expected_benefit = 0.05 * avg_yield_kg_ha * price * area  # avoided salt stress damage
    elif ndvi_deficit > 0.12 and days_since > 21 and stage in ("vegetative", "flowering"):
        action_key, severity = "apply_n", "urgent"
        expected_cost = FERTILIZER_COST_INR["urea_topdress"] * area
        expected_benefit = 0.18 * avg_yield_kg_ha * price * area
    elif ndvi_deficit > 0.05 and days_since > 14:
        action_key, severity = "apply_balanced", "advisory"
        expected_cost = FERTILIZER_COST_INR["npk_balanced"] * area
        expected_benefit = 0.10 * avg_yield_kg_ha * price * area
    else:
        action_key, severity = "hold_fertilizer", "normal"
        expected_cost = 0
        expected_benefit = 0.02 * avg_yield_kg_ha * price * area

    return Recommendation(
        id=f"nut_{farm.farm_id}_{int(time.time())}",
        category="nutrient",
        action_key=action_key,
        action_label=t(lang, action_key),
        confidence_pct=confidence,
        expected_cost_inr=expected_cost,
        expected_benefit_inr=expected_benefit,
        factors=factors,
        severity=severity,
    )


# --------------------------------------------------------------------------
# Crop choice (strategic / seasonal)
# --------------------------------------------------------------------------

def recommend_crop_choice(farm: Farm, weather: WeatherSnapshot, lang: str) -> Recommendation:
    hist = farm.farmer_record.yield_history_t_per_ha
    trend = "flat"
    if len(hist) >= 2:
        trend = "declining" if hist[-1] < hist[0] * 0.9 else ("improving" if hist[-1] > hist[0] * 1.1 else "flat")

    water_risk = farm.farmer_record.irrigation_source in ("borewell", "rainfed")
    low_rain_signal = weather.rainfall_next_48h_mm < 5 and weather.temp_max_c > 38

    factors = [
        Factor("yield_trend", t(lang, "f_yield_trend"), trend, 0.5,
               "increases_need" if trend == "declining" else "neutral"),
        Factor("irrigation_source", t(lang, "f_irrigation_source"), farm.farmer_record.irrigation_source,
               0.7, "increases_need" if water_risk else "decreases_need"),
        Factor("soil_type", t(lang, "f_soil_type"), farm.soil_type.replace("_", " "), 0.3, "neutral"),
        Factor("temp_max", t(lang, "f_temp_max"), f"{weather.temp_max_c:.0f}°C", 0.4,
               "increases_need" if low_rain_signal else "neutral"),
    ]
    agree = sum(f.weight for f in factors if f.direction == "increases_need")
    total_w = sum(f.weight for f in factors)
    confidence = _confidence(agree / total_w, 90.0, weather.forecast_confidence_pct)

    area = farm.area_ha
    price = CROP_PRICE_INR_PER_KG.get(farm.crop_stage.crop, 20)
    avg_yield_kg_ha = _avg_yield(farm) * 1000

    if water_risk and (trend in ("declining", "flat")):
        alt = DIVERSIFICATION_OPTIONS.get(farm.soil_type, ["millet", "pulses"])
        action_key, severity = "diversify_crop", "advisory"
        action_label = t(lang, action_key) + ": " + ", ".join(alt)
        expected_cost = 400 * area  # cost of trial plot / seed switch
        expected_benefit = 0.12 * avg_yield_kg_ha * price * area  # water-cost savings + resilience value
    else:
        action_key, severity = "keep_current_crop", "normal"
        action_label = t(lang, action_key)
        expected_cost = 0
        expected_benefit = 0.02 * avg_yield_kg_ha * price * area

    return Recommendation(
        id=f"crop_{farm.farm_id}_{int(time.time())}",
        category="crop_choice",
        action_key=action_key,
        action_label=action_label,
        confidence_pct=confidence,
        expected_cost_inr=expected_cost,
        expected_benefit_inr=expected_benefit,
        factors=factors,
        severity=severity,
    )


# --------------------------------------------------------------------------
# Risk mitigation
# --------------------------------------------------------------------------

def recommend_risk(farm: Farm, sensor: SensorReading, weather: WeatherSnapshot, lang: str) -> Recommendation:
    heat_risk = weather.temp_max_c >= 40 and farm.crop_stage.stage in ("flowering", "grain_fill")
    fungal_risk = weather.humidity_pct >= 80 and 22 <= weather.temp_max_c <= 32
    flood_risk = weather.rainfall_next_48h_mm >= 50 and farm.soil_type in ("clay", "silty_loam")

    factors = [
        Factor("temp_max", t(lang, "f_temp_max"), f"{weather.temp_max_c:.0f}°C", 0.7,
               "increases_need" if heat_risk else "neutral"),
        Factor("humidity", t(lang, "f_humidity"), f"{weather.humidity_pct:.0f}%", 0.6,
               "increases_need" if fungal_risk else "neutral"),
        Factor("rainfall_forecast", t(lang, "f_rainfall_forecast"), f"{weather.rainfall_next_48h_mm:.0f} mm", 0.7,
               "increases_need" if flood_risk else "neutral"),
        Factor("forecast_confidence", t(lang, "f_forecast_confidence"),
               f"{weather.forecast_confidence_pct:.0f}%", 0.3, "neutral"),
    ]

    area = farm.area_ha
    price = CROP_PRICE_INR_PER_KG.get(farm.crop_stage.crop, 20)
    avg_yield_kg_ha = _avg_yield(farm) * 1000

    if flood_risk:
        action_key, severity = "flood_risk", "urgent"
        expected_cost = 250 * area
        expected_benefit = 0.20 * avg_yield_kg_ha * price * area
        conf_signal = 0.9
    elif heat_risk:
        action_key, severity = "heat_stress_risk", "urgent"
        expected_cost = 500 * area  # mulch/shade net
        expected_benefit = 0.15 * avg_yield_kg_ha * price * area
        conf_signal = 0.85
    elif fungal_risk:
        action_key, severity = "pest_risk", "advisory"
        expected_cost = 350 * area  # scouting + preventive spray
        expected_benefit = 0.10 * avg_yield_kg_ha * price * area
        conf_signal = 0.7
    else:
        action_key, severity = "low_risk", "normal"
        expected_cost = 0
        expected_benefit = 0
        conf_signal = 0.6

    confidence = _confidence(conf_signal, 100.0, weather.forecast_confidence_pct)

    return Recommendation(
        id=f"risk_{farm.farm_id}_{int(time.time())}",
        category="risk",
        action_key=action_key,
        action_label=t(lang, action_key),
        confidence_pct=confidence,
        expected_cost_inr=expected_cost,
        expected_benefit_inr=expected_benefit,
        factors=factors,
        severity=severity,
    )


def generate_all(farm: Farm, sensor: SensorReading, weather: WeatherSnapshot,
                  sat: SatelliteSnapshot, lang: str) -> List[Recommendation]:
    return [
        recommend_irrigation(farm, sensor, weather, sat, lang),
        recommend_nutrient(farm, sensor, sat, lang),
        recommend_crop_choice(farm, weather, lang),
        recommend_risk(farm, sensor, weather, lang),
    ]
