import pandas as pd
import numpy as np
import xgboost as xgb
import joblib
import os
import glob
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split, GridSearchCV
from scipy.signal import savgol_filter
import optuna

# ==========================================
# 1. CONFIGURATION
# ==========================================
# Hardcoded Absolute Path to match your setup
BASE_DIR = r"C:\Users\Ruchit\Desktop\Code\2025\eIPL\Let's start again"
OUTPUT_DIR = os.path.join(BASE_DIR, "Output")
MODEL_DIR = os.path.join(BASE_DIR, "Models")
os.makedirs(MODEL_DIR, exist_ok=True)

# FIX: Search for the NEW 'RACHIT' pattern
search_pattern = os.path.join(OUTPUT_DIR, 'CustardApple_Risk_Master_RACHIT_*.csv')
list_of_files = glob.glob(search_pattern)

if not list_of_files:
    print(f"❌ CRITICAL ERROR: No files found in {OUTPUT_DIR}")
    print(f"   Looking for pattern: {search_pattern}")
    raise FileNotFoundError("Run 01_generate_risk_dataset.py first!")

LATEST_DATA_FILE = max(list_of_files, key=os.path.getctime)
print(f"✅ Using Data: {os.path.basename(LATEST_DATA_FILE)}")

# ==========================================
# 2. FEATURE ENGINEERING (ROBUST / DATA-CENTRIC)
# ==========================================
def create_features(df):
    print("--- Step 1: Feature Engineering (Robust) ---")
    df = df.copy()
    
    # FIX: Handle mixed date formats
    df['datetime'] = pd.to_datetime(df['datetime'], dayfirst=True, format='mixed')
    df = df.sort_values('datetime')

    # ------------------------------------
    # A. ROBUSTNESS: ANOMALY CLIPPING (Winsorization)
    # ------------------------------------
    # Cap outlier sensor readings that are physically impossible for trees
    # We use 1st and 99th percentiles as safe bounds
    for col in ['VH', 'VV', 'RVI', 'Radar_Ratio']:
        if col in df.columns:
            lower = df[col].quantile(0.01)
            upper = df[col].quantile(0.99)
            df[col] = df[col].clip(lower, upper)

    # ------------------------------------
    # B. ROBUSTNESS: BIOLOGICAL SMOOTHING (Savitzky-Golay)
    # ------------------------------------
    # Remove daily "jitter" to reveal the true biological trend
    # Window=15 days (2 weeks), Polyorder=2 (Quadratic curve)
    for col in ['VH', 'VV', 'RVI', 'Radar_Ratio']:
        if col in df.columns:
            # Create a new smoothed column
            df[f'{col}_smooth'] = savgol_filter(df[col], window_length=15, polyorder=2)

    # ------------------------------------
    # C. NEW: INTERACTION FEATURES (Biological Indices)
    # ------------------------------------
    # 1. Heat Stress Index (Temp * Humidity) - lethal combination for bugs
    df['Bio_Heat_Index'] = df['tempmax'] * df['humidity']
    
    # 2. Washout Potential (Rain * Wind/Storminess proxy)
    # Since we don't have wind, Rain * Rain intensity helps
    df['Rain_Intensity_Index'] = df['precip'] * df['precip']

    # ------------------------------------
    # D. STANDARD ROLLING WINDOWS (On Smoothed Data)
    # ------------------------------------
    # Now we calculate rolling means on the CLEAN '_smooth' data
    for window in [14, 30, 60]:
        df[f'temp_roll_mean_{window}'] = df['tempmax'].rolling(window).mean()
        df[f'rain_roll_sum_{window}'] = df['precip'].rolling(window).sum()
        df[f'humid_roll_mean_{window}'] = df['humidity'].rolling(window).mean()
        
        # Rolling on Biological Indices
        df[f'heat_index_roll_{window}'] = df['Bio_Heat_Index'].rolling(window).mean()

    # E. Optical Lags (Smoothed)
    if 'RVI_smooth' in df.columns:
        df['rvi_lag_30'] = df['RVI_smooth'].shift(30)
    
    # F. Radar Trends (Smoothed)
    if 'Radar_Ratio_smooth' in df.columns:
        print("   -> Adding Robust Radar Features...")
        df['radar_ratio_roll_30'] = df['Radar_Ratio_smooth'].rolling(30).mean()
        df['VH_roll_30'] = df['VH_smooth'].rolling(30).mean()
        df['VV_roll_30'] = df['VV_smooth'].rolling(30).mean()
        
        # Lagged structure check
        df['radar_ratio_lag_14'] = df['Radar_Ratio_smooth'].shift(14)

    # Drop NaN created by rolling/lags
    df.dropna(inplace=True)
    return df

# ==========================================
# 3. TRAINING
# ==========================================
def train_model():
    # Load
    df = pd.read_csv(LATEST_DATA_FILE)
    
    # Engineer
    df_featured = create_features(df)
    print(f"   -> Features Created. Rows available: {len(df_featured)}")

    # Define Features (X) and Target (y)
    # We exclude date, month, and the target itself from X
    features = [c for c in df_featured.columns if c not in ['datetime', 'month', 'mealybug_risk_score', 'year', 'avg_temp']]
    target = 'mealybug_risk_score'
    
    X = df_featured[features]
    y = df_featured[target]
    
    # Split (Time-based split, not random)
    train_size = int(len(X) * 0.8)
    X_train, X_test = X.iloc[:train_size], X.iloc[train_size:]
    y_train, y_test = y.iloc[:train_size], y.iloc[train_size:]
    
    print(f"--- Step 2: Running Optuna Bayesian Optimization ---")
    
    # 1. Define the Objective Function
    def objective(trial):
        params = {
            'n_estimators': trial.suggest_int('n_estimators', 100, 1000),
            'learning_rate': trial.suggest_float('learning_rate', 1e-3, 1e-1, log=True),
            'max_depth': trial.suggest_int('max_depth', 3, 10),
            'subsample': trial.suggest_float('subsample', 0.5, 1.0),
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.5, 1.0),
            'n_jobs': -1,
            'random_state': 42
        }
        
        model = xgb.XGBRegressor(**params)
        model.fit(X_train, y_train, verbose=False)
        preds = model.predict(X_test)
        rmse = np.sqrt(mean_squared_error(y_test, preds))
        return rmse

    # 2. Run Optimization
    study = optuna.create_study(direction='minimize')
    study.optimize(objective, n_trials=50) # Tries 50 smart combinations
    
    print(f"   -> Best Params: {study.best_params}")
    
    # 3. Train Final Model with Best Params
    best_model = xgb.XGBRegressor(**study.best_params)
    best_model.fit(X_train, y_train)
    
    # Save
    save_path = os.path.join(MODEL_DIR, "CustardApple_Blind_Model.joblib")
    joblib.dump(best_model, save_path)
    
    # Evaluate
    preds = best_model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    r2 = r2_score(y_test, preds)
    
    print(f"--- Step 3: Evaluation ---")
    print(f"   -> RMSE: {rmse:.4f}")
    print(f"   -> R2 Score: {r2:.4f}")
    print(f"✅ SUCCESS! Model saved to: {save_path}")

if __name__ == "__main__":
    train_model()