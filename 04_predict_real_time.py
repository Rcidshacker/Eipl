import pandas as pd
import numpy as np
import joblib
import requests
import os
from datetime import datetime, timedelta

# ==========================================
# 1. CONFIGURATION
# ==========================================
# LOCATION: Pune (Custard Apple Region)
LAT = 18.5204
LON = 73.8567
LOCATION_NAME = "Pune, Maharashtra"

# *** PASTE YOUR VISUAL CROSSING API KEY HERE ***
# Get it from: https://www.visualcrossing.com/weather-api
API_KEY = "ENPYVRQT5SRYBZFGW68BCB4CP" 

# EXACT MODEL PATH (As provided)
MODEL_PATH = r"C:\Users\Ruchit\Desktop\Code\2025\eIPL\Let's start again\Models\CustardApple_Blind_Model.joblib"

# ==========================================
# 2. LIVE DATA FETCHING
# ==========================================
def fetch_live_weather():
    print(f"--- Connecting to Satellite Weather for {LOCATION_NAME} ---")
    
    # We need 75 days of history to calculate the 60-day rolling features needed by the model
    today = datetime.now()
    start_date = (today - timedelta(days=75)).strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')
    
    # Visual Crossing API URL
    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{LAT},{LON}/{start_date}/{end_date}?unitGroup=metric&include=days&key={API_KEY}&contentType=json"
    
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"\n❌ ERROR: API Request failed. Status Code: {response.status_code}")
            print(f"   Reason: {response.text}")
            print("   -> Please check if your API_KEY is correct inside the script.")
            return None
            
        data = response.json()
        days = data['days']
        
        df = pd.DataFrame(days)
        # Keep only the columns the model knows about
        df = df[['datetime', 'tempmax', 'tempmin', 'precip', 'humidity']]
        df['datetime'] = pd.to_datetime(df['datetime'])
        df['precip'] = df['precip'].fillna(0.0)
        
        print(f"  -> Success! Downloaded {len(df)} days of recent weather history.")
        return df
        
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        return None

# ==========================================
# 3. FEATURE ENGINEERING (BLINDFOLDED)
# ==========================================
def prepare_features(df):
    print("--- Processing Features for AI ---")
    df = df.copy()
    df = df.sort_values('datetime')
    
    # We calculate 'month' ONLY for RVI estimation logic, 
    # but we will NOT pass it to the AI (Model is blindfolded).
    df['month'] = df['datetime'].dt.month
    
    # 1. Estimate RVI (Vegetation Density) based on Seasonality Rules
    def estimate_rvi(month):
        # Monsoon/Growth (June-Sept) -> High Vegetation
        if 6 <= month <= 9: return 0.75
        # Fruit/Harvest (Oct-Jan) -> Medium-High
        elif 10 <= month <= 1: return 0.65
        # Dormant (Feb-May) -> Low
        else: return 0.35
    
    df['RVI'] = df['month'].apply(estimate_rvi)
    
    # 2. Calculate Lags & Rolling Averages (Recreating the model's 'Memory')
    for lag in [1, 7, 14, 30]:
        df[f'temp_lag_{lag}'] = df['tempmax'].shift(lag)
        df[f'rain_lag_{lag}'] = df['precip'].shift(lag)
        df[f'rvi_lag_{lag}'] = df['RVI'].shift(lag)
        
    for window in [7, 14, 30, 60]: 
        df[f'temp_roll_mean_{window}'] = df['tempmax'].rolling(window).mean()
        df[f'rain_roll_sum_{window}'] = df['precip'].rolling(window).sum()
        
    # 3. Select ONLY the Last Row (Today) for prediction
    latest_data = df.iloc[[-1]].copy()
    
    # 4. Handle Missing Data (Forward Fill if API has small gaps)
    if latest_data.isnull().values.any():
        latest_data = latest_data.fillna(method='ffill').fillna(0)
        
    return latest_data

# ==========================================
# 4. EXECUTION
# ==========================================
def main():
    # 1. Load Model
    if not os.path.exists(MODEL_PATH):
        print(f"ERROR: Model file not found at: {MODEL_PATH}")
        return
    
    print(f"Loading Brain: {os.path.basename(MODEL_PATH)}")
    try:
        model = joblib.load(MODEL_PATH)
    except Exception as e:
        print(f"Error loading model: {e}")
        return
    
    # 2. Get Data
    weather_df = fetch_live_weather()
    if weather_df is None: return
    
    # 3. Prepare Input
    input_row = prepare_features(weather_df)
    
    # 4. Align Features
    # The model expects a specific list of columns. We must match it exactly.
    model_features = model.get_booster().feature_names
    
    try:
        X_input = input_row[model_features]
    except KeyError as e:
        print(f"\n❌ Feature Mismatch Error:")
        print(f"   The model wants feature: {e}")
        print("   But we didn't calculate it. Check 'prepare_features' function.")
        return

    # 5. Predict
    print("--- Running Inference ---")
    prediction = model.predict(X_input)[0]
    prediction = max(0.0, min(1.0, prediction)) # Clamp result between 0 and 1
    
    # 6. The Verdict
    today_str = datetime.now().strftime('%d %B %Y')
    
    print("\n" + "="*50)
    print(f"   CUSTARD APPLE MEALYBUG ALERT SYSTEM")
    print(f"   Date: {today_str}")
    print(f"   Location: {LOCATION_NAME}")
    print("="*50)
    
    print(f"\n🔮 FORECAST (14-Day Outlook):")
    print(f"   Risk Score: {prediction:.4f}  (Scale 0.0 to 1.0)")
    
    # Dynamic Advisory
    print("\n📋 ADVISORY:")
    if prediction < 0.3:
        print("   STATUS: 🟢 LOW RISK")
        print("   Action: Conditions are unfavorable for mealybugs.")
        print("           Routine monitoring is sufficient.")
    elif 0.3 <= prediction < 0.7:
        print("   STATUS: 🟡 MODERATE RISK")
        print("   Action: Weather is supporting population growth.")
        print("           - Scout the field specifically for ants.")
        print("           - Check inner canopy.")
    else:
        print("   STATUS: 🔴 HIGH RISK")
        print("   Action: CRITICAL ALERT. High heat accumulation detected.")
        print("           - Inspect fruit crevices immediately.")
        print("           - Prepare for management interventions (neem oil or chemical).")
        print("           - Avoid harvesting affected fruits to prevent spread.")
    
    print("\n" + "="*50)

if __name__ == "__main__":
    main()