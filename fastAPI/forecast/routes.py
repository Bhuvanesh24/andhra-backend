from fastapi import APIRouter, HTTPException
from .schemas import ForecastRequest, ForecastResponse
from .services import call_model

router = APIRouter()

@router.post("/predict")
async def predict(data: ForecastRequest):
    """
    Route to call the model with incoming data and return the prediction.
    """
    try:
        prediction = await call_model(data)  
        prediction_response = {
            data.target_year: {
                "domestic": prediction[0],
                "industrial": prediction[1],
                "irrigation": prediction[2],
            }
        }
        return prediction_response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model prediction failed: {str(e)}")

