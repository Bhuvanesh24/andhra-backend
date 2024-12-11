from fastapi import FastAPI, HTTPException, APIRouter
import torch
import numpy as np
import pandas as pd
from scipy.stats import norm
from .schemas import ScenarioRequest
import os
from src.model import EnhancedLSTM

# Set base and data directories
base_dir = os.getenv("BASE_DIR", os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(base_dir, "data", "usage.csv")
model_path = os.path.join(base_dir, "model", "final_model.pt")

# Define the router for FastAPI
router = APIRouter()

# Load the water usage model
input_size = 14  # Adjust according to the model's input size
output_size = 3  # Adjust according to the model's output size
water_usage_model = EnhancedLSTM(input_size=input_size, lstm_layer_sizes=[1], linear_layer_size=[128] * 6, output_size=output_size)
water_usage_model.load_state_dict(torch.load(model_path, map_location='cpu', weights_only=False))
water_usage_model.eval()

def safe_float(value):
    """Replace NaN and infinite float values with None."""
    if isinstance(value, (float, np.float32, np.float64)):
        if np.isnan(value) or np.isinf(value):
            return None
    return value



def simulate_risk_score(rainfall, evaporation, inflow, outflow, population, water_usage_model, district):
    """
    Simulate and calculate the risk score for flood and drought, along with storage change details.

    Parameters:
    rainfall (list of float): Daily rainfall in mm for a month.
    evaporation (list of float): Daily potential evapotranspiration (PET) in mm for a month.
    inflow (float): Monthly reservoir inflow in m³.
    outflow (float): Monthly reservoir outflow in m³.
    population (int): Population of the region.
    water_usage_model (callable): Predictive model for water usage based on population.
    district (str): Name of the district for analysis.

    Returns:
    dict: Risk scores for flood and drought, including changes in inflow, outflow, and storage.
    """
    # Calculate water balance (rainfall - evaporation)
    water_balance = np.array(rainfall) - np.array(evaporation)
    water_balance_mean = np.mean(water_balance)

    # District data and one-hot encoding
    districts = [3, 6, 7, 9, 13, 10, 18, 20, 21, 23, 24, 25, 26]
    onehot = [0] * 13
    onehot[districts.index(district)] = 1
    population_tensor = torch.tensor([[population]], dtype=torch.float32)
    onehot_tensor = torch.tensor([onehot], dtype=torch.float32)

    # Predict water usage or use default value
    if water_usage_model:
        water_usage = water_usage_model(torch.cat((onehot_tensor, population_tensor), dim=1).unsqueeze(0)).sum().item() * 1e5
    else:
        water_usage = 2e4  # Default water usage (in m³)

    # Adjust inflow and outflow based on water balance
    adjusted_inflow = inflow / 1e4 * (1 + water_balance_mean / 100)
    adjusted_outflow = outflow / 1e4 * (1 - water_balance_mean / 100)

    # Net water balance and storage change
    net_water_balance = water_balance_mean + (adjusted_inflow - adjusted_outflow)
    storage_change = (adjusted_inflow - adjusted_outflow) * 1e4

    # SPEI calculation: use the entire water balance for the month
    aggregated_balance = water_balance  # Use all daily water balance values for SPEI
    mu, sigma = aggregated_balance.mean(), aggregated_balance.std()

    # Avoid division by zero by ensuring sigma is at least 1
    spei = (net_water_balance - mu) / max(sigma, 1)

    # Map SPEI to drought and flood scores based on defined thresholds
    if spei <= -2.5:
        drought_score = 75 + (min(-spei - 2.5, 1) * 25)  # Very High (75-100)
    elif -2.5 < spei <= -1.5:
        drought_score = 50 + ((-spei - 1.5) / 1 * 25)  # High (50-75)
    elif -1.5 < spei <= -0.5:
        drought_score = 25 + ((-spei - 0.5) / 1 * 25)  # Moderate (25-50)
    else:
        drought_score = max(0, (1 - norm.cdf(spei)) * 25)  # Low (<25)

    if spei >= 2.5:
        flood_score = 75 + (min(spei - 2.5, 1) * 25)  # Very High (75-100)
    elif 1.5 <= spei < 2.5:
        flood_score = 50 + ((spei - 1.5) / 1 * 25)  # High (50-75)
    elif 0.5 <= spei < 1.5:
        flood_score = 25 + ((spei - 0.5) / 1 * 25)  # Moderate (25-50)
    else:
        flood_score = max(0, norm.cdf(spei) * 25)  # Low (<25)

    # Scale scores based on water usage
    drought_score_adjusted = drought_score * (water_usage / 1e4)
    flood_score_adjusted = flood_score * (water_usage / 1e4)

    # Assign risk levels based on SPEI with "Very High Risk" included
    if spei <= -2.5:
        drought_risk = "Very High Risk"
    elif -2.5 < spei <= -0.5:
        drought_risk = "High Risk" if spei <= -1.5 else "Moderate Risk"
    else:
        drought_risk = "Low Risk"

    if spei >= 2.5:
        flood_risk = "Very High Risk"
    elif 0.5 <= spei < 2.5:
        flood_risk = "High Risk" if spei >= 1.5 else "Moderate Risk"
    else:
        flood_risk = "Low Risk"



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
            district=data.district,
            water_usage_model = water_usage_model
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500,detail = str(e))