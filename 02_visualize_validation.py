import pandas as pd
import matplotlib.pyplot as plt
import os
import glob

# --- CONFIGURATION ---
BASE_DIR = r"C:\Users\Ruchit\Desktop\Code\2025\eIPL\Let's start again"
OUTPUT_DIR = os.path.join(BASE_DIR, "Output")

# Find the latest generated CSV automatically
list_of_files = glob.glob(os.path.join(OUTPUT_DIR, 'CustardApple_Risk_Master_*.csv'))
LATEST_FILE = max(list_of_files, key=os.path.getctime)

print(f"Validating File: {os.path.basename(LATEST_FILE)}")

# --- LOAD DATA ---
df = pd.read_csv(LATEST_FILE)
df['datetime'] = pd.to_datetime(df['datetime'])

# --- PLOT 1: The "Heartbeat" of the System (2016-2018 Zoom) ---
# We zoom in on 3 years to see the details clearly
zoom_df = df[(df['datetime'].dt.year >= 2016) & (df['datetime'].dt.year <= 2018)]

plt.figure(figsize=(15, 10))

# Subplot 1: The Risk Score (The Target)
plt.subplot(3, 1, 1)
plt.plot(zoom_df['datetime'], zoom_df['mealybug_risk_score'], color='red', label='Risk Score (0-1)')
plt.title('Validation Check: Did the Risk Model behave logically? (2016-2018 Zoom)')
plt.ylabel('Risk Score')
plt.grid(True, alpha=0.3)
plt.legend()

# Subplot 2: The Rain (The Trigger & Washout)
plt.subplot(3, 1, 2)
plt.bar(zoom_df['datetime'], zoom_df['precip'], color='blue', alpha=0.5, label='Rainfall (mm)')
plt.ylabel('Rain (mm)')
plt.grid(True, alpha=0.3)
plt.legend()

# Subplot 3: The Radar (The Vegetation)
plt.subplot(3, 1, 3)
plt.plot(zoom_df['datetime'], zoom_df['RVI'], color='green', label='Radar RVI (Vegetation)')
plt.ylabel('RVI Index')
plt.xlabel('Date')
plt.grid(True, alpha=0.3)
plt.legend()

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "Validation_Plot_Zoom.png"))
print("Generated: Validation_Plot_Zoom.png")

# --- PLOT 2: The Yearly Comparison (Consistency Check) ---
# Check if every year peaks at the right time
df['doy'] = df['datetime'].dt.dayofyear
df['year'] = df['datetime'].dt.year

plt.figure(figsize=(12, 6))
for year in range(2016, 2023):
    year_data = df[df['year'] == year]
    plt.plot(year_data['doy'], year_data['mealybug_risk_score'], label=str(year), alpha=0.7)

plt.title('Seasonality Check: Do all years peak in Oct/Nov?')
plt.xlabel('Day of Year (1 = Jan 1, 300 = Late Oct)')
plt.ylabel('Risk Score')
# Highlight the "Danger Zone" (Sept-Nov is roughly Day 244 to 334)
plt.axvspan(244, 334, color='red', alpha=0.1, label='Fruit Vulnerability Window')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig(os.path.join(OUTPUT_DIR, "Validation_Seasonality.png"))
print("Generated: Validation_Seasonality.png")

print("\n--- HOW TO INTERPRET THE PLOTS ---")
print("1. Open 'Validation_Seasonality.png'")
print("   - All lines should be near 0 on the left (Jan-May).")
print("   - All lines should rise in the middle.")
print("   - All lines should peak inside the RED BOX (Sept-Nov).")
print("   - If lines are flat or peak in May, the Biofix is wrong.")