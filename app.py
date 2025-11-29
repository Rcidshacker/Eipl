import streamlit as st
import pandas as pd
import numpy as np
import joblib
import requests
import os
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim
from scipy.signal import savgol_filter
import math
import folium
from streamlit_folium import st_folium

# ==========================================
# 1. CONFIGURATION & STATIC LOADING
# ==========================================
BASE_PATH = r"C:\Users\Ruchit\Desktop\Code\2025\eIPL\Let's start again"
MODEL_PATH = fr"{BASE_PATH}\Models\CustardApple_Blind_Model.joblib"
SOIL_STATIC_PATH = fr"{BASE_PATH}\Sitaphal_Soil_Static_RachitFarms.csv"
RADAR_PATH = fr"{BASE_PATH}\Sitaphal_Radar_RachitFarms.csv"

DEFAULT_API_KEY = "ENPYVRQT5SRYBZFGW68BCB4CP"

# Initialize Global Variables with Defaults
CLAY_PCT = 30.0
LATEST_VH = -18.0
LATEST_VV = -11.0
LATEST_RATIO = -8.0

# Attempt to load static files
try:
    if os.path.exists(SOIL_STATIC_PATH):
        soil_data = pd.read_csv(SOIL_STATIC_PATH)
        if len(soil_data) > 0:
            val = soil_data['Clay_Pct'].iloc[0]
            # Handle unit conversion if needed (g/kg vs %)
            CLAY_PCT = val / 10.0 if val > 100 else val

    if os.path.exists(RADAR_PATH):
        radar_df = pd.read_csv(RADAR_PATH)
        radar_df['datetime'] = pd.to_datetime(radar_df['datetime'], dayfirst=True, format='mixed')
        radar_df = radar_df.sort_values('datetime')
        if not radar_df.empty:
            LATEST_VH = radar_df['VH'].iloc[-1]
            LATEST_VV = radar_df['VV'].iloc[-1]
            LATEST_RATIO = radar_df['Radar_Ratio'].iloc[-1]
except Exception as e:
    pass # Silent fail, defaults will be used

# ==========================================
# 2. CORE FUNCTIONS
# ==========================================

def get_coordinates(place_name):
    """Converts a city name into Lat/Lon using OpenStreetMap"""
    try:
        geolocator = Nominatim(user_agent="custard_apple_pest_app")
        location = geolocator.geocode(place_name)
        if location:
            return location.latitude, location.longitude, location.address
        return None, None, None
    except: return None, None, None

@st.cache_data(ttl=3600)
def fetch_weather_data(api_key, lat, lon):
    """Fetches weather forecast from Visual Crossing."""
    today = datetime.now()
    start_date = (today - timedelta(days=75)).strftime('%Y-%m-%d')
    end_date = (today + timedelta(days=7)).strftime('%Y-%m-%d')
    
    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{lat},{lon}/{start_date}/{end_date}?unitGroup=metric&include=days&key={api_key}&contentType=json"
    
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return None, f"Error {response.status_code}: {response.text}"
        
        data = response.json()
        df = pd.DataFrame(data['days'])
        
        cols_needed = ['datetime', 'tempmax', 'tempmin', 'precip', 'humidity']
        # flexible column selection
        available_cols = [c for c in cols_needed if c in df.columns]
        df = df[available_cols].copy()
        
        if 'datetime' in df.columns:
            df['datetime'] = pd.to_datetime(df['datetime'])
        if 'precip' in df.columns:
            df['precip'] = df['precip'].fillna(0.0)
        
        return df, None
    except Exception as e: return None, str(e)

@st.cache_data(ttl=86400)
def fetch_live_soil_dna(lat, lon):
    """Fetches Clay % from SoilGrids API."""
    try:
        url = f"https://rest.isric.org/soilgrids/v2.0/properties/query?lat={lat}&lon={lon}&property=clay&depth=0-5cm&value=mean"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            clay_val = data['properties']['layers'][0]['depths'][0]['values']['mean']
            return clay_val / 10.0
        return 30.0
    except: return 30.0

def run_enkf_correction(predicted_risk, slider_rvi):
    """Fuses Model Prediction with User Observation."""
    expected_rvi = predicted_risk 
    surprise = slider_rvi - expected_rvi
    K = 0.7 
    return max(0.0, min(1.0, predicted_risk + (K * surprise)))

def process_features(df, manual_rvi=None):
    """Prepares the features for XGBoost."""
    df = df.sort_values('datetime')
    df['month'] = df['datetime'].dt.month
    
    # Optical
    df['RVI'] = manual_rvi if manual_rvi is not None else 0.65

    # Radar Forward Fill
    df['Radar_Ratio'] = LATEST_RATIO
    df['VH'] = LATEST_VH
    df['VV'] = LATEST_VV

    # Robust Features
    if 'precip' not in df.columns: df['precip'] = 0.0
    df['Bio_Heat_Index'] = df['tempmax'] * df['humidity']
    df['Rain_Intensity_Index'] = df['precip'] * df['precip']

    # Smoothing
    cols_to_smooth = ['VH', 'VV', 'RVI', 'Radar_Ratio']
    if len(df) > 15:
        try:
            for col in cols_to_smooth:
                df[f'{col}_smooth'] = savgol_filter(df[col], window_length=15, polyorder=2)
        except:
            for col in cols_to_smooth: df[f'{col}_smooth'] = df[col]
    else:
         for col in cols_to_smooth: df[f'{col}_smooth'] = df[col]

    # Rolling Windows
    for window in [14, 30, 60]:
        if 'tempmax' in df.columns: 
            df[f'temp_roll_mean_{window}'] = df['tempmax'].rolling(window).mean()
        if 'precip' in df.columns: 
            df[f'rain_roll_sum_{window}'] = df['precip'].rolling(window).sum()
        if 'humidity' in df.columns: 
            df[f'humid_roll_mean_{window}'] = df['humidity'].rolling(window).mean()
        
        df[f'heat_index_roll_{window}'] = df['Bio_Heat_Index'].rolling(window).mean()

    # Lags
    df['radar_ratio_roll_30'] = df['Radar_Ratio_smooth'].rolling(30).mean().fillna(LATEST_RATIO)
    df['VH_roll_30'] = df['VH_smooth'].rolling(30).mean().fillna(LATEST_VH)
    df['VV_roll_30'] = df['VV_smooth'].rolling(30).mean().fillna(LATEST_VV)
    df['radar_ratio_lag_14'] = df['Radar_Ratio_smooth'].shift(14).fillna(LATEST_RATIO)
    df['rvi_lag_30'] = df['RVI_smooth'].shift(30).fillna(df['RVI'])

    return df.dropna()

# ==========================================
# 3. UI LAYOUT & EXECUTION
# ==========================================

if 'lat' not in st.session_state: st.session_state['lat'] = 18.5204
if 'lon' not in st.session_state: st.session_state['lon'] = 73.8567
if 'city' not in st.session_state: st.session_state['city'] = "Pune"
if 'analyzed' not in st.session_state: st.session_state['analyzed'] = False

st.set_page_config(page_title="Custard Apple Risk AI", page_icon="🍎", layout="centered")
st.title("🍎 Custard Apple Pest Guard")
st.markdown("**AI-Powered Mealybug Early Warning System**")
st.markdown("---")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Location Settings")
    
    st.markdown("### 🔎 Find Your Farm")
    search_query = st.text_input("Enter City/Village Name", placeholder="e.g. Nashik, Indapur")

    col_search, col_show = st.columns([1, 1])
    with col_search:
        if st.button("📍 Find"):
            if search_query:
                new_lat, new_lon, address = get_coordinates(search_query)
                if new_lat:
                    st.success(f"Found: {address}")
                    st.session_state['lat'] = new_lat
                    st.session_state['lon'] = new_lon
                    st.session_state['city'] = address.split(",")[0].strip().replace(" ", "_")
                    st.rerun()
                else: st.error("Not found.")
    
    with col_show:
        if st.button("🏠 Demo", help="Load Rachit Farms (Ground Truth)"):
            st.session_state['lat'] = 18.4089
            st.session_state['lon'] = 74.1079
            st.session_state['city'] = "Rachit_Farms"
            st.rerun()

    st.markdown("---")
    st.markdown("### 🧬 Digital Twin DNA")
    lat = st.session_state['lat']
    lon = st.session_state['lon']
    
    with st.spinner("Analyzing Soil..."):
        current_clay_pct = fetch_live_soil_dna(lat, lon)

    soil_type = "Heavy Clay" if current_clay_pct > 35 else ("Sandy Loam" if current_clay_pct < 20 else "Loam")
    st.metric("Soil Profile (Live)", f"{soil_type}", f"{current_clay_pct:.1f}% Clay")
    st.metric("Canopy Structure (Est.)", f"{LATEST_RATIO:.2f} dB", delta="Biomass")

    st.markdown("---")
    current_city = st.session_state['city']
    spray_log_file = f"spray_log_{current_city}.txt"
    st.markdown(f"### 🚜 Intervention: **{current_city}**")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("I Sprayed 🚿"):
            with open(spray_log_file, "w") as f: f.write(datetime.now().strftime("%Y-%m-%d"))
            st.success("Recorded!"); st.rerun()
    with col2:
        if st.button("🔄 Reset"):
            if os.path.exists(spray_log_file): os.remove(spray_log_file); st.rerun()

    st.markdown("---")
    st.markdown("### 🌐 Exact Coordinates")
    col_lat, col_lon = st.columns(2)
    lat = col_lat.number_input("Lat", value=st.session_state['lat'], format="%.4f")
    lon = col_lon.number_input("Lon", value=st.session_state['lon'], format="%.4f")
    
    location_name = search_query if search_query else current_city
    user_api_key = st.text_input("Visual Crossing API Key", value=DEFAULT_API_KEY, type="password")
    
    st.markdown("---")
    st.markdown("### 🌳 Orchard Condition")
    
    crop_stage = st.selectbox(
        "Current Crop Stage",
        ["Dormant / Post-Harvest", "Vegetative (New Leaves)", "Flowering", "Fruiting (Fruit Set)", "Harvesting"],
        index=3,
        help="Adjusts risk based on economic vulnerability."
    )
    
    manual_rvi_input = st.slider("Canopy Density", 0.2, 0.9, 0.65, 0.05)
    if manual_rvi_input < 0.4: desc = "High sunlight. Root zone risk."
    elif manual_rvi_input < 0.6: desc = "Moderate cover. Flower drop risk."
    else: desc = "Thick canopy. Fruit spoilage risk."
    st.info(f"_{desc}_")
    
    submit = st.button("🚀 Analyze Risk", type="primary")

# --- MAIN LOGIC ---
if submit or st.session_state['analyzed']:
    st.session_state['analyzed'] = True
    
    if "PASTE_YOUR" in user_api_key or len(user_api_key) < 10:
        st.error("⚠️ Please enter a valid Visual Crossing API Key.")
    else:
        if not os.path.exists(MODEL_PATH):
            st.error(f"❌ Model not found: {MODEL_PATH}"); st.stop()
        try:
            model = joblib.load(MODEL_PATH)
        except Exception as e: st.error(f"❌ Failed to load model: {e}"); st.stop()

        with st.spinner(f"🛰️ Connecting satellites for {location_name}..."):
            df_weather, error = fetch_weather_data(user_api_key, lat, lon)
        
        if error:
            st.error(f"API Error: {error}")
        else:
            # PROCESS DATA
            full_data = process_features(df_weather, manual_rvi=manual_rvi_input)
            today = pd.Timestamp.now().normalize()
            current_row = full_data[full_data['datetime'] <= today + timedelta(days=1)].iloc[[-1]]
            future_rows = full_data[full_data['datetime'] > today].copy()
            
            try:
                # PREDICT
                try: expected_features = model.get_booster().feature_names
                except: expected_features = ['tempmax', 'tempmin', 'precip', 'humidity', 'RVI']
                
                for feat in expected_features:
                    if feat not in full_data.columns: full_data[feat] = 0.0
                
                X_today = current_row[expected_features]
                raw_risk = max(0.0, min(1.0, model.predict(X_today)[0]))
                
                # B) SOIL PENALTY (Biology)
                soil_suitability = math.exp(-0.025 * current_clay_pct)
                baseline = math.exp(-0.025 * 30.0)
                soil_multiplier = max(0.5, min(1.3, soil_suitability / baseline))
                biological_risk = raw_risk * soil_multiplier
                
                # C) INTERVENTION CHECK
                is_protected = False
                days_since = 0
                if os.path.exists(spray_log_file):
                    with open(spray_log_file, "r") as f:
                        try:
                            last_spray = datetime.strptime(f.read().strip(), "%Y-%m-%d")
                            days_since = (datetime.now() - last_spray).days
                            if days_since < 14: is_protected = True
                        except: pass

                # D) HUMAN CORRECTION (EnKF) & STAGE VETO
                if is_protected:
                    final_risk = 0.1
                    st.success(f"🛡️ PROTECTED MODE (Sprayed {days_since} days ago)")
                else:
                    fused_risk = run_enkf_correction(biological_risk, manual_rvi_input)
                    if abs(fused_risk - biological_risk) > 0.15:
                        st.info(f"🧠 AI adjusted based on your Canopy observation.")

                    stage_multipliers = {
                        "Dormant / Post-Harvest": 0.2, "Vegetative (New Leaves)": 0.3, 
                        "Flowering": 0.7, "Fruiting (Fruit Set)": 1.0, "Harvesting": 1.0
                    }
                    stage_mod = stage_multipliers.get(crop_stage, 1.0)
                    final_risk = fused_risk * stage_mod

                # --- VISUALIZATION ---
                st.markdown("### 🛰️ Farm Surveillance")
                if final_risk > 0.7: risk_color = "#ff3f3f"; risk_fill = "red"
                elif final_risk > 0.3: risk_color = "#ffbf00"; risk_fill = "orange"
                else: risk_color = "#00cc96"; risk_fill = "green"

                m = folium.Map(location=[lat, lon], zoom_start=16, tiles=None)
                folium.TileLayer(
                    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                    attr='Esri', name='Satellite', overlay=False, control=True
                ).add_to(m)

                folium.Circle(
                    radius=300, location=[lat, lon], color=risk_color, fill=True,
                    fill_color=risk_fill, fill_opacity=0.35, popup=f"Risk: {final_risk*100:.1f}%"
                ).add_to(m)
                folium.Marker([lat, lon], tooltip="Farm Center", icon=folium.Icon(color="blue", icon="leaf")).add_to(m)
                st_folium(m, width=700, height=400)

                st.markdown("### 📊 Current Status (Today)")
                fig_gauge = go.Figure(go.Indicator(
                    mode = "gauge+number+delta", value = final_risk * 100,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Economic Risk (%)"},
                    delta = {'reference': 50, 'increasing': {'color': "red"}},
                    gauge = {
                        'axis': {'range': [None, 100]}, 'bar': {'color': "darkblue"},
                        'steps': [{'range': [0, 30], 'color': "#00cc96"},
                                  {'range': [30, 70], 'color': "#ffbf00"},
                                  {'range': [70, 100], 'color': "#ff3f3f"}]
                    }
                ))
                st.plotly_chart(fig_gauge, use_container_width=True)
                
                # --- FORECAST ---
                if not future_rows.empty:
                    st.markdown("### 📅 7-Day Risk Forecast")
                    X_future = future_rows[expected_features]
                    preds_future = model.predict(X_future)
                    
                    forecast_risks = []
                    for p in preds_future:
                        bio = p * soil_multiplier
                        fused = run_enkf_correction(bio, manual_rvi_input)
                        final = fused * stage_mod # Veto
                        forecast_risks.append(max(0.0, min(1.0, final)))

                    future_rows['Predicted_Risk'] = forecast_risks
                    
                    fig_line = px.line(future_rows, x='datetime', y='Predicted_Risk', markers=True)
                    fig_line.add_hrect(y0=0.7, y1=1.0, fillcolor="red", opacity=0.1)
                    fig_line.update_yaxes(range=[0, 1.1])
                    st.plotly_chart(fig_line, use_container_width=True)

                    with st.expander("📊 Detailed Forecast Data", expanded=True):
                        clean_view = future_rows[['datetime', 'tempmax', 'humidity', 'precip', 'Predicted_Risk']].copy()
                        clean_view.columns = ['Date', 'Max Temp (°C)', 'Humidity (%)', 'Rain (mm)', 'Risk Probability']
                        st.dataframe(clean_view.style.format({
                            'Date': lambda t: t.strftime('%d-%b-%Y'),
                            'Max Temp (°C)': "{:.1f}", 'Humidity (%)': "{:.1f}", 'Rain (mm)': "{:.1f}",
                            'Risk Probability': "{:.1%}"
                        }).background_gradient(subset=['Risk Probability'], cmap="RdYlGn_r", vmin=0, vmax=1))

            except Exception as e: st.error(f"Prediction Error: {e}")