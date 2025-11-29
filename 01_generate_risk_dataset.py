import pandas as pd
import numpy as np
import os
from datetime import datetime

# ==========================================
# 1. CONFIGURATION & PATHS
# ==========================================
BASE_PATH = r"C:\Users\Ruchit\Desktop\Code\2025\eIPL\Let's start again"

# Inputs
WEATHER_PATH = fr"{BASE_PATH}\pune.csv\pune.csv" 
OPTICAL_PATH = fr"{BASE_PATH}\Sitaphal_Optical_RachitFarms.csv"
RADAR_PATH = fr"{BASE_PATH}\Sitaphal_Radar_RachitFarms.csv"
SOIL_STATIC_PATH = fr"{BASE_PATH}\Sitaphal_Soil_Static_RachitFarms.csv"

# Output (Fixed to your specific folder)
OUTPUT_DIR = fr"{BASE_PATH}\Output"
if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)

# Biology Config
BIOFIX_START_MONTH = 6
BIOFIX_END_MONTH = 8
BIOFIX_MIN_RAIN = 10.0
DD_PER_GENERATION = 350.0 

# ==========================================
# 2. DATA LOADING & CLEANING (FIXED)
# ==========================================
def load_and_clean_data():
    print("--- Step 1: Loading Data (Rachit Farms Fusion) ---")
    
    # A. Weather
    try:
        weather = pd.read_csv(WEATHER_PATH)
        weather.rename(columns={'date_time': 'datetime', 'maxtempC': 'tempmax', 
                                'mintempC': 'tempmin', 'precipMM': 'precip', 
                                'humidity': 'humidity'}, inplace=True)
        weather['datetime'] = pd.to_datetime(weather['datetime'], dayfirst=True, format='mixed')
        weather.set_index('datetime', inplace=True)
        weather = weather.resample('D').agg({'tempmax': 'max', 'tempmin': 'min', 
                                             'precip': 'sum', 'humidity': 'mean'}).reset_index()
        weather.dropna(subset=['tempmax'], inplace=True)
    except Exception as e:
        print(f"❌ Error loading Weather: {e}"); return None, None

    # B. Satellites
    try:
        # 1. Load & Clean Dates
        radar = pd.read_csv(RADAR_PATH)
        radar['datetime'] = pd.to_datetime(radar['datetime'], dayfirst=True, format='mixed')
        radar = radar.groupby('datetime')[['VH', 'VV', 'Radar_Ratio']].mean()
        
        optical = pd.read_csv(OPTICAL_PATH)
        optical['datetime'] = pd.to_datetime(optical['datetime'], dayfirst=True, format='mixed')
        optical = optical.groupby('datetime')['RVI'].mean()
        
        # 2. Merge Optical + Radar
        satellite = pd.merge(optical, radar, on='datetime', how='outer')
        
        # 3. *** THE FIX: Resample to Daily to fill time gaps ***
        satellite = satellite.resample('D').mean()
        satellite = satellite.interpolate(method='time', limit_direction='both')
        
        # 4. Fill historical gaps (Pre-2015)
        satellite['RVI'] = satellite['RVI'].fillna(0.3)
        satellite['VH'] = satellite['VH'].fillna(-18.0)
        satellite['VV'] = satellite['VV'].fillna(-10.0)
        satellite['Radar_Ratio'] = satellite['Radar_Ratio'].fillna(-8.0)
        
        satellite.reset_index(inplace=True)
        
    except Exception as e:
        print(f"❌ Error loading Satellites: {e}"); return None, None

    return weather, satellite

# ==========================================
# 3. SIMULATION WITH SOIL DNA
# ==========================================
def run_simulation_pipeline():
    weather, satellite = load_and_clean_data()
    if weather is None: return

    print("--- Step 2: Merging Datasets ---")
    # Align Daily Weather with Interpolated Satellite Data
    master_df = pd.merge_asof(weather.sort_values('datetime'), 
                              satellite.sort_values('datetime'), 
                              on='datetime', direction='nearest', 
                              tolerance=pd.Timedelta(days=2))
    
    # Fill remaining edges
    master_df['RVI'] = master_df['RVI'].fillna(0.3)
    master_df['Radar_Ratio'] = master_df['Radar_Ratio'].fillna(-8.0)

    print("--- Step 3: Biological Simulation (Ants + Clay Logic) ---")
    
    # 1. Load Soil DNA (Static)
    try:
        soil_meta = pd.read_csv(SOIL_STATIC_PATH)
        # Handle if the CSV has 1 row
        if len(soil_meta) > 0:
            # Unit Conversion: SoilGrids uses g/kg (e.g. 382 = 38.2%)
            # We divide by 10 to get Percentage
            clay_pct = soil_meta['Clay_Pct'].iloc[0] / 10.0 
            print(f"   -> Soil DNA Detected: Clay Content = {clay_pct:.1f}%")
        else:
            clay_pct = 30.0
    except Exception as e:
        print(f"⚠️ Could not load Soil DNA ({e}), assuming standard loam.")
        clay_pct = 30.0 

    # 2. Risk Loop
    master_df['month'] = master_df['datetime'].dt.month
    master_df['avg_temp'] = (master_df['tempmax'] + master_df['tempmin']) / 2
    
    risk_scores = []
    accumulated_dd = 0.0
    season_active = False

    for i, row in master_df.iterrows():
        # A. Biofix (Season Start)
        if row['month'] <= 2: season_active = False; accumulated_dd = 0.0
        if not season_active and (BIOFIX_START_MONTH <= row['month'] <= BIOFIX_END_MONTH):
            if row['precip'] >= BIOFIX_MIN_RAIN:
                season_active = True; accumulated_dd = 35.0

        current_risk = 0.0
        if season_active:
            # B. Degree Days
            daily_dd = max(0, min(row['avg_temp'], 35) - 15)
            accumulated_dd += daily_dd
            if row['precip'] > 80: accumulated_dd *= 0.5 # Washout
            
            base_score = min(accumulated_dd / (DD_PER_GENERATION * 3.5), 1.0)
            if row['month'] in [9,10,11]: base_score = min(base_score * 1.5, 1.0)
            
            current_risk = base_score
            
            # --- C. ANT & SOIL LOGIC ---
            # 1. Weather Suitability (20-35C, Dry)
            ant_weather_good = (20 <= row['tempmax'] <= 35) and (row['humidity'] < 80) and (row['precip'] < 1)
            
            if ant_weather_good:
                # 2. Soil Penalty: Ants struggle in Heavy Clay (>35%)
                # If Clay is high, the "Ant Boost" is dampened (0.9x).
                # If Soil is sandy/loam, the boost is full (1.2x).
                soil_factor = 0.9 if clay_pct > 35 else 1.2
                
                # Apply the boost/penalty
                current_risk = min(current_risk * soil_factor, 1.0)
                
        risk_scores.append(current_risk)

    master_df['mealybug_risk_score'] = risk_scores
    
    # Save
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"CustardApple_Risk_Master_RACHIT_{timestamp}.csv"
    save_path = os.path.join(OUTPUT_DIR, filename)
    master_df.to_csv(save_path, index=False)
    print(f"✅ SUCCESS! Created Digital Twin Dataset: {save_path}")

if __name__ == "__main__":
    run_simulation_pipeline()