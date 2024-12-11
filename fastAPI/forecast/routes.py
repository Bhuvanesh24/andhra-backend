import torch
import torch.nn as nn
import torch.nn.functional as F
from src.model import EnhancedLSTM
from pathlib import Path
import os
from fastapi import FastAPI, HTTPException, APIRouter
import pickle

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "forecast" / "models"
model_path = os.path.join(MODEL_DIR,"model_fold_3.pt")
pickle_path = os.path.join(MODEL_DIR,"usage_x.pkl")
router = APIRouter()

@router.post("/get-factors/")
async def get_factors_endpoint(request:dict):
    """
    API endpoint to compute input weightage factors for the LSTM model.
    
    Returns:
        JSON response containing the computed weightage.
    """
    print("Got")
    print(request)

    try:
        # Define input size (adjust as per your model's requirement)
        input_size = 12  # Example input size
        
        # Load the trained model from the specified path
        model = torch.load(model_path, map_location='cpu')
        data = request
        values = [
            data["District"],  
            data["Month"],
            data["Rainfall"],
            data["Irrigation"],
            data["Industry"],
            data["Domestic"],
            data["Built-up"],
            data["Agricultural"],
            data["Forest"],
            data["Wasteland"],
            data["Wetlands"],
            data["Waterbodies"],
        ]
        input_data = torch.tensor(values, dtype=torch.float32).reshape(1, 1, 12)
        
        with open(pickle_path, 'rb') as f:
            scaler_x = pickle.load(f)
        
        input_data_np = input_data.numpy().reshape(-1, input_size)
        
        print("Before Trans",input_data_np)
        # Apply the scaler
        scaled_input_data_np = scaler_x.transform(input_data_np)
        print("After trans",scaled_input_data_np)
        # Convert back to PyTorch tensor
        input_data = torch.tensor(scaled_input_data_np, dtype=torch.float32).unsqueeze(1)
        
        # Compute weightage
        weightage = compute_input_weightage(model, input_data)

        
        return {"weightage": weightage}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error computing factors: {str(e)}")


def compute_input_weightage(model, input_data, normalize=False):
    """
    Computes the weightage of each input timestep or feature using gradients.

    Args:
        model (nn.Module): The trained LSTM model.
        input_data (torch.Tensor): Input data of shape (batch_size, seq_length, input_size = 12).
        normalize (bool): Whether to normalize the weightage to a range of 0-1.

    Returns:
        torch.Tensor: Normalized weightage of shape (batch_size, seq_length, input_size).
    """
    model.eval()
    input_data = input_data.requires_grad_(True)

    output = model(input_data)
    output_sum = output.sum()

    output_sum.backward()

    gradients = input_data.grad

    weightage = torch.abs(gradients)

    if normalize:
        weightage = weightage / weightage.sum(dim=1, keepdim=True)

    return weightage.squeeze().tolist()

