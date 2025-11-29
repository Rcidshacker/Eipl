import joblib
import xgboost as xgb
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ==========================================
# CONFIGURATION
# ==========================================
BASE_DIR = r"C:\Users\Ruchit\Desktop\Code\2025\eIPL\Let's start again"
MODEL_PATH = os.path.join(BASE_DIR, "Models", "CustardApple_Blind_Model.joblib")

def inspect_brain():
    print(f"--- 🧠 Inspecting Model Brain: {os.path.basename(MODEL_PATH)} ---")
    
    # 1. Load the Model
    if not os.path.exists(MODEL_PATH):
        print("❌ Model not found! Train it first.")
        return

    model = joblib.load(MODEL_PATH)
    
    # 2. Extract Feature Importance
    # XGBoost tracks 'Gain' (How much a feature improves accuracy)
    # and 'Weight' (How many times a feature is used in logic trees)
    
    # Get the booster object from the wrapper
    booster = model.get_booster()
    
    # Get importance (Gain is best for "Biological Impact")
    importance_map = booster.get_score(importance_type='gain')
    
    # Convert to DataFrame
    df_imp = pd.DataFrame(list(importance_map.items()), columns=['Feature', 'Biological_Impact'])
    df_imp.sort_values('Biological_Impact', ascending=False, inplace=True)
    
    # 3. Visualize
    plt.figure(figsize=(12, 8))
    
    # Color Coding: Biological (Weather) vs Inertial (Lags)
    # We want to see Weather features HIGH up.
    colors = []
    for feat in df_imp['Feature']:
        if 'risk' in feat or 'lag' in feat:
            colors.append('#95a5a6') # Grey for Lags (Memory)
        elif 'temp' in feat or 'precip' in feat or 'humidity' in feat:
            colors.append('#e74c3c') # Red for Weather (Biology)
        elif 'RVI' in feat:
            colors.append('#2ecc71') # Green for Satellites
        else:
            colors.append('#34495e')

    sns.barplot(x='Biological_Impact', y='Feature', data=df_imp.head(20), palette=colors)
    
    plt.title('X-Ray of AI Decision Making\n(Red=Biology, Green=Satellites, Grey=Memory)', fontsize=15)
    plt.xlabel('Impact on Prediction (Gain)', fontsize=12)
    plt.ylabel('Feature Name', fontsize=12)
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    # Save
    save_path = os.path.join(BASE_DIR, "Blind_Feature_Importance.png")
    plt.savefig(save_path)
    print(f"✅ X-Ray Saved to: {save_path}")
    print("\n--- TOP 5 DRIVERS ---")
    print(df_imp.head(5))

if __name__ == "__main__":
    inspect_brain()