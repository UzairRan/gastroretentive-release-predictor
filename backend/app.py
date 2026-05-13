from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import uvicorn
from model_loader import predict_release_rate

app = FastAPI(
    title="Gastroretentive Release Rate Predictor",
    description="ML model to predict drug release rate from gastroretentive tablets",
    version="1.0.0"
)

class PredictionRequest(BaseModel):
    dose_mg: float
    ph_stomach: float
    desired_release_hr: float
    matrix_density: float
    temperature_c: float
    drug_type: str

class PredictionResponse(BaseModel):
    predicted_release_rate_mg_per_hr: float
    status: str

@app.get("/")
def root():
    return {"message": "Gastroretentive Release Rate Predictor API is running", "status": "active"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/drug-types")
def get_drug_types():
    from model_loader import drug_type_mapping
    return {"drug_types": list(drug_type_mapping.keys())}

@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    try:
        predicted_rate = predict_release_rate(
            dose_mg=request.dose_mg,
            ph_stomach=request.ph_stomach,
            desired_release_hr=request.desired_release_hr,
            matrix_density=request.matrix_density,
            temperature_c=request.temperature_c,
            drug_type=request.drug_type
        )
        
        return PredictionResponse(
            predicted_release_rate_mg_per_hr=predicted_rate,
            status="success"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 