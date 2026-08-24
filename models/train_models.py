import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split

os.makedirs("models", exist_ok=True)
print("[1/3] Generating Agronomic Datasets for 20 Major Crops...")

np.random.seed(42)
n_samples = 15000

# 20 Major Indian Crops
crops = [
    "Wheat", "Paddy", "Sugarcane", "Maize", "Cotton", 
    "Soybean", "Mustard", "Groundnut", "Gram", "Tur", 
    "Moong", "Jute", "Potato", "Onion", "Tomato", 
    "Bajra", "Jowar", "Ragi", "Barley", "Sesame"
]

# Base Yield Multipliers (Quintals/Acre)
base_yield_map = {
    "Wheat": 20.0, "Paddy": 25.0, "Sugarcane": 330.0, "Maize": 28.0, "Cotton": 11.0,
    "Soybean": 9.0, "Mustard": 8.5, "Groundnut": 10.0, "Gram": 6.0, "Tur": 5.5,
    "Moong": 4.5, "Jute": 14.0, "Potato": 110.0, "Onion": 95.0, "Tomato": 120.0,
    "Bajra": 12.0, "Jowar": 10.5, "Ragi": 13.0, "Barley": 16.0, "Sesame": 3.5
}

# Base Mandi Prices (INR/Quintal)
base_price_map = {
    "Wheat": 2450, "Paddy": 2300, "Sugarcane": 340, "Maize": 2100, "Cotton": 7100,
    "Soybean": 4600, "Mustard": 5400, "Groundnut": 6300, "Gram": 5800, "Tur": 7000,
    "Moong": 8500, "Jute": 5000, "Potato": 1500, "Onion": 1800, "Tomato": 2000,
    "Bajra": 2500, "Jowar": 3100, "Ragi": 3800, "Barley": 2200, "Sesame": 8600
}

crop_choices = np.random.choice(crops, size=n_samples)
acres_choices = np.random.uniform(1.0, 50.0, size=n_samples)
moisture_choices = np.random.uniform(20.0, 70.0, size=n_samples)
temp_choices = np.random.uniform(18.0, 42.0, size=n_samples)
npk_choices = np.random.uniform(0.4, 1.0, size=n_samples)
rainfall_choices = np.random.uniform(400.0, 1800.0, size=n_samples)
months = np.random.randint(1, 13, size=n_samples)
supply_factor = np.random.uniform(0.8, 1.2, size=n_samples)

yields = []
prices = []
for c, m, t, npk, sup in zip(crop_choices, moisture_choices, temp_choices, npk_choices, supply_factor):
    # Yield Logic
    b_yield = base_yield_map[c]
    m_pen = 1.0 - (abs(m - 45.0) / 100.0)
    t_pen = 1.0 - (abs(t - 27.0) / 60.0)
    y = b_yield * m_pen * t_pen * (0.7 + 0.3 * npk) + np.random.normal(0, b_yield * 0.05)
    yields.append(max(1.0, round(y, 2)))
    
    # Price Logic
    b_price = base_price_map[c]
    p = (b_price / sup) + np.random.normal(0, b_price * 0.03)
    prices.append(max(100.0, round(p, 2)))

df_combined = pd.DataFrame({
    "crop": crop_choices, "acres": acres_choices, "soil_moisture": moisture_choices, 
    "soil_temp": temp_choices, "npk_score": npk_choices, "rainfall_mm": rainfall_choices, 
    "month": months, "supply_factor": supply_factor, "yield_per_acre": yields, "mandi_price": prices
})

print("[2/3] Training Upgraded Random Forest Models...")

# 1. Train Yield Model
X_yield = df_combined[["crop", "soil_moisture", "soil_temp", "npk_score", "rainfall_mm"]]
y_yield = df_combined["yield_per_acre"]

prep_yield = ColumnTransformer(
    transformers=[("cat", OneHotEncoder(handle_unknown="ignore"), ["crop"])], 
    remainder="passthrough"
)

yield_pipeline = Pipeline(steps=[
    ("prep", prep_yield), 
    ("reg", RandomForestRegressor(n_estimators=100, max_depth=12))
])
yield_pipeline.fit(X_yield, y_yield)

# 2. Train Price Model
X_price = df_combined[["crop", "month", "supply_factor"]]
y_price = df_combined["mandi_price"]

prep_price = ColumnTransformer(
    transformers=[("cat", OneHotEncoder(handle_unknown="ignore"), ["crop"])], 
    remainder="passthrough"
)

price_pipeline = Pipeline(steps=[
    ("prep", prep_price), 
    ("reg", RandomForestRegressor(n_estimators=100, max_depth=10))
])
price_pipeline.fit(X_price, y_price)

print("[3/3] Exporting Universal Models...")
joblib.dump(yield_pipeline, "models/yield_model.pkl")
joblib.dump(price_pipeline, "models/mandi_price_model.pkl")
print("Success! Models are ready for inference.")