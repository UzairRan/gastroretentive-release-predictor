import joblib
import pandas as pd
import os

# Get the directory where this file is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, 'models')

# Load all required files
model = joblib.load(os.path.join(MODELS_DIR, 'gastro_release_best_model.pkl'))
label_encoder = joblib.load(os.path.join(MODELS_DIR, 'label_encoder.pkl'))
feature_columns = joblib.load(os.path.join(MODELS_DIR, 'feature_columns.pkl'))
drug_type_mapping = joblib.load(os.path.join(MODELS_DIR, 'drug_type_mapping.pkl'))

def predict_release_rate(dose_mg, ph_stomach, desired_release_hr, matrix_density, temperature_c, drug_type):
    
    # Convert drug type string to encoded value
    if isinstance(drug_type, str):
        drug_type_encoded = label_encoder.transform([drug_type])[0]
    else:
        drug_type_encoded = drug_type
    
    # Create input dataframe
    input_data = pd.DataFrame([{
        'dose_mg': float(dose_mg),
        'ph_stomach': float(ph_stomach),
        'desired_release_hr': float(desired_release_hr),
        'matrix_density': float(matrix_density),
        'temperature_c': float(temperature_c),
        'drug_type_encoded': int(drug_type_encoded)
    }])
    
    # Make prediction
    prediction = model.predict(input_data)[0]
    return round(prediction, 2) 