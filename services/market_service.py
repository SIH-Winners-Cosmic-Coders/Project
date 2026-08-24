import os
import joblib
import datetime
import pandas as pd

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
try:
    yield_model = joblib.load(os.path.join(MODEL_DIR, "yield_model.pkl"))
    price_model = joblib.load(os.path.join(MODEL_DIR, "mandi_price_model.pkl"))
    MODELS_LOADED = True
except Exception:
    MODELS_LOADED = False

# Government MSP Rates (₹/Quintal)
MSP_RATES = {
    "Wheat": 2275, "Paddy": 2183, "Sugarcane": 340, "Maize": 2090, "Cotton": 6620,
    "Soybean": 4600, "Mustard": 5450, "Groundnut": 6377, "Gram": 5440, "Tur": 7000,
    "Moong": 8558, "Jute": 5050, "Potato": 1200, "Onion": 1500, "Tomato": 1500,
    "Bajra": 2500, "Jowar": 3180, "Ragi": 3846, "Barley": 1850, "Sesame": 8635
}

def recommend_best_crop(moisture_pct, soil_temp):
    if moisture_pct > 55.0: return "Paddy"
    if moisture_pct < 30.0 and soil_temp > 32.0: return "Bajra"
    if 30.0 <= soil_temp <= 38.0 and moisture_pct < 40.0: return "Cotton"
    if 20.0 <= soil_temp <= 25.0: return "Wheat"
    return "Maize"

def predict_crop_metrics(crop: str, acres: float, moisture_pct: float = 42.0, soil_temp: float = 28.0, npk_score: float = 0.85, rainfall_mm: float = 950.0) -> dict:
    crop_clean = crop.split(' (')[0].strip().capitalize()
    ai_suggestion = recommend_best_crop(moisture_pct, soil_temp)
    if crop_clean == "Auto": crop_clean = ai_suggestion

    current_month = datetime.datetime.now().month
    next_month = (current_month % 12) + 1

    if MODELS_LOADED:
        df_yield = pd.DataFrame([{"crop": crop_clean, "soil_moisture": float(moisture_pct), "soil_temp": float(soil_temp), "npk_score": float(npk_score), "rainfall_mm": float(rainfall_mm)}])
        yield_per_acre = float(yield_model.predict(df_yield)[0])
        
        # Current month price
        df_price_now = pd.DataFrame([{"crop": crop_clean, "month": current_month, "supply_factor": 1.0}])
        price_now = int(price_model.predict(df_price_now)[0])
        
        # Next month price for Hold/Sell strategy
        df_price_next = pd.DataFrame([{"crop": crop_clean, "month": next_month, "supply_factor": 0.9}])
        price_next = int(price_model.predict(df_price_next)[0])
    else:
        yield_per_acre, price_now, price_next = 20.0, 2400, 2500

    total_yield = round(yield_per_acre * acres, 2)
    projected_revenue = int(total_yield * price_now)
    msp = MSP_RATES.get(crop_clean, price_now - 200)

    # Strategy Logic
    if price_next > (price_now * 1.05): 
        strategy = "HOLD"
        strategy_msg = f"Prices expected to rise to ₹{price_next}/Q next month."
    else:
        strategy = "SELL NOW"
        strategy_msg = "Market prices are peaking. Sell immediately."

    return {
        "status": "success",
        "crop": crop_clean,
        "ai_recommended_crop": ai_suggestion,
        "farm_acres": acres,
        "total_predicted_yield_quintals": total_yield,
        "projected_mandi_price_per_q": price_now,
        "msp_rate": msp,
        "msp_warning": price_now < msp,
        "projected_revenue_inr": projected_revenue,
        "market_strategy": strategy,
        "strategy_msg": strategy_msg
    }