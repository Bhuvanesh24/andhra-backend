from fastapi import FastAPI, HTTPException, Request, Depends,APIRouter
import torch
import numpy as np
from scipy.stats import norm
from src.model import EnhancedLSTM
import pandas as pd
from .schemas import ScenarioRequest
import os

base_dir = os.getenv("BASE_DIR", os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(base_dir,"data","usage.csv")
# # Construct the path to the model
# model_path = os.path.join(base_dir, "model", "usage_for_bhuvi.pt")
# input_size = 14
# output_size = 3
# water_usage_model = EnhancedLSTM(input_size=input_size, lstm_layer_sizes=[128]*3, linear_layer_size=[64]*6, output_size=output_size)
# water_usage_model.load_state_dict(torch.load(model_path, map_location='cpu', weights_only=False))
# water_usage_model.eval()

router = APIRouter()

import pandas as pd
import numpy as np
import torch
from scipy.stats import norm

import pandas as pd
import numpy as np
import torch
from scipy.stats import norm




def safe_float(value):
    """Replace NaN and infinite float values with None."""
    if isinstance(value, (float, np.float32, np.float64)):
        if np.isnan(value) or np.isinf(value):
            return None
    return value



def simulate_risk_score(rainfall, evaporation, inflow, outflow, population, district):
    """
    Simulate and calculate the risk score for flood and drought, along with storage change details.
    """
    water_balance = rainfall - evaporation
    water_usage = 2e6  # Example value for water usage

    # Load data from CSV
    df = pd.read_csv(data_dir)

    # Verify if the district exists in the DataFrame
    if district not in df['District'].values:
        raise ValueError(f"District '{district}' not found in the data.")

    # One-hot encode the 'District' column and concatenate with the original DataFrame
    one_hot = pd.get_dummies(df['District'], prefix='District')
    df_encoded = pd.concat([df, one_hot], axis=1)

    # Ensure that the column for the given district exists
    district_column_name = f'District_{district}'
    if district_column_name not in df_encoded.columns:
        raise ValueError(f"Column '{district_column_name}' not found in the DataFrame.")

    # Get the one-hot encoded row for the given district
    district_data = df_encoded[df_encoded['District'] == district]
    input = np.array(district_data[district_column_name].values.astype(int)).reshape(1, -1)
    input = np.append(input, [[population]], axis=1)
    input = torch.tensor(input, dtype=torch.float32).unsqueeze(0)

    print("Input shape:", input.shape)

    # Adjust inflow and outflow based on water balance
    adjusted_inflow = inflow * (1 + water_balance / 100)
    adjusted_outflow = outflow * (1 - water_balance / 100)

    # Calculate net water balance and storage change
    net_water_balance = water_balance + (adjusted_inflow - adjusted_outflow) / 1e6
    storage_change = adjusted_inflow - adjusted_outflow

    # Calculate SPEI
    aggregated_balance = [water_balance, net_water_balance]
    mu, sigma = np.mean(aggregated_balance), np.std(aggregated_balance)

    # Check for zero standard deviation
    if sigma == 0:
        spei = None  # or a default value like 0 or an error message
    else:
        spei = (net_water_balance - mu) / sigma

    # Replace non-compliant float values with None
    spei = safe_float(spei)
    adjusted_inflow = safe_float(adjusted_inflow)
    adjusted_outflow = safe_float(adjusted_outflow)
    storage_change = safe_float(storage_change)

    # Define flood and drought risks based on SPEI value
    if spei is not None:
        if spei <= -2:
            drought_risk = "High Risk"
            flood_risk = "Low Risk"
        elif spei >= 2:
            drought_risk = "Low Risk"
            flood_risk = "High Risk"
        else:
            drought_risk = "Moderate Risk"
            flood_risk = "Moderate Risk"
    else:
        drought_risk = "Unknown"
        flood_risk = "Unknown"

    # Calculate drought and flood scores
    drought_score = max(0, min(100, (1 - norm.cdf(spei)) * 100)) * (water_usage / 1e6) if spei is not None else None
    flood_score = max(0, min(100, norm.cdf(spei) * 100)) * (water_usage / 1e6) if spei is not None else None

    return {
        "SPEI": spei,
        "Drought Risk": drought_risk,
        "Flood Risk": flood_risk,
        "Drought Score": drought_score,
        "Flood Score": flood_score,
        "Adjusted Inflow": adjusted_inflow,
        "Adjusted Outflow": adjusted_outflow,
        "Storage Change": storage_change,
    }

@router.post("/predict/")
async def predict_risk(data: ScenarioRequest):
    try:
        result = simulate_risk_score(
            rainfall=data.rainfall,
            evaporation=data.evaporation,
            inflow=data.inflow,
            outflow=data.outflow,
            population=data.population,
            district=data.district
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))