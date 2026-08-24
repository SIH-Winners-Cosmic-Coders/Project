import os
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

def train_model():
    """
    Trains a Random Forest Regressor for mandi price predictions.
    """
    os.makedirs("models", exist_ok=True)

    # Generate synthetic training dataset mimicking Agmarknet structure
    np.random.seed(42)
    data_size = 1200
    
    states = ['Punjab', 'Haryana', 'Uttar Pradesh', 'Rajasthan', 'Madhya Pradesh']
    districts = ['Ludhiana', 'Karnal', 'Agra', 'Jaipur', 'Indore']
    commodities = ['Wheat', 'Paddy', 'Potato', 'Mustard', 'Onion']

    data = {
        'state': np.random.choice(states, data_size),
        'district': np.random.choice(districts, data_size),
        'commodity': np.random.choice(commodities, data_size),
        'day_of_year': np.random.randint(1, 365, data_size),
        'month': np.random.randint(1, 13, data_size),
        'arrival_qty_qtl': np.random.uniform(50, 2000, data_size),
        'modal_price': np.random.uniform(1200, 4500, data_size)  # ₹/Quintal
    }
    
    df = pd.DataFrame(data)

    X = df[['state', 'district', 'commodity', 'day_of_year', 'month', 'arrival_qty_qtl']]
    y = df['modal_price']

    categorical_cols = ['state', 'district', 'commodity']
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_cols)
        ],
        remainder='passthrough'
    )

    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
    ])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    pipeline.fit(X_train, y_train)

    # Save model pipeline
    model_path = 'models/mandi_model.pkl'
    joblib.dump(pipeline, model_path)
    print(f"Model successfully trained and saved to '{model_path}'.")

if __name__ == "__main__":
    train_model()