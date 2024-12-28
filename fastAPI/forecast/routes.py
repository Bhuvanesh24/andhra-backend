import torch
from pathlib import Path
import os
from fastapi import  HTTPException, APIRouter
import pickle



BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "forecast" / "models"
model_path = os.path.join(MODEL_DIR,"enhanced_lstm_v4.pt")
pickle_path = os.path.join(MODEL_DIR,"usage_x.pkl")
router = APIRouter()


@router.post("/get-factors/")
async def get_factors_endpoint(request: dict):
    """
    API endpoint to compute input weightage factors for the LSTM model.
    
    Returns:
        JSON response containing the computed weightage.
    """
    

    try:
        input_size = 7  # Example input size

        
        model = torch.load(model_path, map_location='cpu')
        
        # Extract data from request
        data = request
        values = [
            data.get("Rainfall", 0),
            data.get("Irrigation", 0),
            data.get("Industry", 0),
            data.get("Domestic", 0),
            data.get("Built-up", 0),
            data.get("Agricultural", 0),
            data.get("Forest", 0),
        ]
        
        input_data = torch.tensor(values, dtype=torch.float32).reshape(1, 1, input_size)

        # Load the scaler
        with open(pickle_path, 'rb') as f:
            scaler_x = pickle.load(f)
        
        input_data_np = input_data.numpy().reshape(-1, input_size)
       

        try:
            
            scaled_input_data_np = scaler_x.transform(input_data_np)
           

        except Exception as e:
        
            raise HTTPException(status_code=500, detail=f"Error during scaling: {str(e)}")
        
        input_data = torch.tensor(scaled_input_data_np, dtype=torch.float32).unsqueeze(0)
        
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


