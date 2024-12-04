from fastapi import FastAPI, HTTPException, Request, Depends,APIRouter
import torch
import numpy as np
from scipy.stats import norm
from src.model import EnhancedLSTM
import pandas as pd
from .schemas import ScenarioRequest
import os

base_dir = os.getenv("BASE_DIR", os.path.dirname(os.path.abspath(__file__)))

# Construct the path to the model
model_path = os.path.join(base_dir, "model", "usage_for_bhuvi.pt")
input_size = 14
output_size = 3
water_usage_model = EnhancedLSTM(input_size=input_size, lstm_layer_sizes=[128]*3, linear_layer_size=[64]*6, output_size=output_size)
water_usage_model.load_state_dict(torch.load(model_path, map_location='cpu', weights_only=False))
water_usage_model.eval()

router = APIRouter()


def simulate_risk_score(rainfall, evaporation, inflow, outflow, population, water_usage_model, district):
    """
    Simulate and calculate the risk score for flood and drought, along with storage change details.

    Parameters:
    rainfall (float): Monthly rainfall in mm.
    evaporation (float): Monthly potential evapotranspiration (PET) in mm.
    inflow (float): Monthly reservoir inflow in m³.
    outflow (float): Monthly reservoir outflow in m³.
    population (int): Population of the region.
    water_usage_model (callable): Predictive model for water usage based on population.
    
    Returns:
    dict: Risk scores for flood and drought, including changes in inflow, outflow, and storage.
    """
    water_balance = rainfall - evaporation
    #water_usage = 2e6

    df = pd.read_csv('data/usage.csv')['District']
    unique_districts = df.unique()
    df = pd.DataFrame(unique_districts, columns=['District'])
    one_hot = pd.get_dummies(df['District'], prefix='District')
    df = pd.concat([df, one_hot], axis=1)
    input = np.array(df[df["District"] == district].iloc[:, 1:].values.astype(int))
    input = np.append(input, [[population]], axis=1)
    input = torch.tensor(input, dtype=torch.float32).unsqueeze(0)
    print(input.size())
    
    with torch.no_grad():
        water_usage = water_usage_model(input).sum().item() * 1e6
    
    adjusted_inflow = inflow * (1 + water_balance / 100)  # Modify inflow based on water balance (rainfall/evaporation)
    adjusted_outflow = outflow * (1 - water_balance / 100)  # Modify outflow based on water balance

    # Calculate net water balance
    net_water_balance = water_balance + (adjusted_inflow - adjusted_outflow) / 1e6
    
    # Calculate storage change in the district
    storage_change = adjusted_inflow - adjusted_outflow  # Change in storage is the difference between inflow and outflow
    
    # Aggregate water balance for SPEI calculation
    aggregated_balance = [water_balance, net_water_balance]
    mu, sigma = np.mean(aggregated_balance), np.std(aggregated_balance)
    print(mu,sigma)
    spei = (net_water_balance  - mu) / sigma
    
    # Define flood and drought risks based on SPEI value
    if spei <= -2:
        drought_risk = "High Risk"
        flood_risk = "Low Risk"
    elif spei >= 2:
        drought_risk = "Low Risk"
        flood_risk = "High Risk"
    else:
        drought_risk = "Moderate Risk"
        flood_risk = "Moderate Risk"
    
    
    drought_score = max(0, min(100, (1 - norm.cdf(spei)) * 100)) * (water_usage / 1e6)
    flood_score = max(0, min(100, norm.cdf(spei) * 100)) * (water_usage / 1e6)
    
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