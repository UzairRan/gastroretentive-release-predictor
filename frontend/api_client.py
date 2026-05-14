import requests
import streamlit as st

# API endpoint - change this to your Render URL after deployment
# Example: "https://your-app.onrender.com"
# API_BASE_URL = "http://localhost:8000"  # Local testing
API_BASE_URL = "https://gastroretentive-release-predictor.onrender.com" 
# API_BASE_URL = "https://your-app-name.onrender.com"  # After deployment on Render

def get_api_health():
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_drug_types():
    try:
        response = requests.get(f"{API_BASE_URL}/drug-types", timeout=10)
        if response.status_code == 200:
            return response.json().get("drug_types", [])
    except:
        pass
    return ['antibiotic', 'antacid', 'antiulcer', 'nutraceutical']

def predict_release_rate(dose_mg, ph_stomach, desired_release_hr, matrix_density, temperature_c, drug_type):
    payload = {
        "dose_mg": dose_mg,
        "ph_stomach": ph_stomach,
        "desired_release_hr": desired_release_hr,
        "matrix_density": matrix_density,
        "temperature_c": temperature_c,
        "drug_type": drug_type
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/predict", json=payload, timeout=30)
        if response.status_code == 200:
            return response.json().get("predicted_release_rate_mg_per_hr")
        else:
            st.error(f"API Error: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return None 