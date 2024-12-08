import pandas as pd
import joblib
import os
from fastapi import FastAPI, HTTPException, APIRouter
from .schemas import ScoreRequest
base_dir = os.getenv("BASE_DIR", os.path.dirname(os.path.abspath(__file__)))

model_path = os.path.join(base_dir,"models","trained_reservoir_model.pkl")
scalar_path = os.path.join(base_dir,"models","scaler_for_input_data.pkl")

router = APIRouter()

model = joblib.load(model_path)
scaler = joblib.load(scalar_path)

@router.post("/predict_score/")
async def predict_score(request: ScoreRequest):
   
    new_data = {
        'mean storage': [request.mean_storage], 
        'flood cushion': [request.flood_cushion], 
        'rainfall': [request.rainfall], 
        'evaporation': [request.evaporation], 
        'Population': [request.population], 
        'Age': [request.age], 
        'Siltation(tmc)': [request.siltation],
        'capacity': [request.capacity]
    }

   
    new_data_df = pd.DataFrame(new_data)

    new_data_scaled = scaler.transform(new_data_df)

    predicted_score = model.predict(new_data_scaled)
    
    return {"predicted_score": predicted_score[0]}