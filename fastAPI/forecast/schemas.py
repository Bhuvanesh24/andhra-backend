from pydantic import BaseModel
from typing import Dict

class ForecastRequest(BaseModel):
    state_idx: int
    target_year: int
    structured_data: Dict[int, list] 

class ForecastResponse(BaseModel):
    prediction: dict  
