import pandas as pd
import joblib
import os
from fastapi import HTTPException, APIRouter, File, UploadFile
from .schemas import ScoreRequest
from fastapi.responses import FileResponse
import torch
import pickle
import numpy as np
from sklearn.preprocessing import StandardScaler
from torch.utils.data import DataLoader,Dataset
import torch.nn as nn
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Define paths relative to the base directory
UPLOAD_DIR = BASE_DIR / "reservoir" / "uploads"
OUTPUT_DIR = BASE_DIR / "reservoir" / "outputs"
MODEL_DIR = BASE_DIR / "reservoir" / "models"
DATA_DIR = BASE_DIR / "reservoir" / "data"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

if not MODEL_DIR.exists():
    raise FileNotFoundError(f"Model directory does not exist: {MODEL_DIR}")
if not (MODEL_DIR / "enhanced_res_6.pt").exists():
    raise FileNotFoundError(f"Model file does not exist: {MODEL_DIR / 'enhanced_res_6.pt'}")

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



@router.post("/retrain")
async def retrain_model_endpoint(file: UploadFile = File(...)):
    """
    Endpoint to upload a CSV file, retrain the model, and generate predictions for the next 5 years.
    """
    
    try:
        # Ensure it's a CSV file
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are supported.")

        # Save the uploaded file
        uploaded_file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(uploaded_file_path, "wb") as f:
            f.write(await file.read())

        model_file = os.path.join(MODEL_DIR, "enhanced_res_5.pt")
        retrain_model(uploaded_file_path,model_file)
        
        # Define paths for required files
        
        scaler_x_file = os.path.join(DATA_DIR, "res_x.pkl")
        scaler_y_file = os.path.join(DATA_DIR, "res_y.pkl")
        output_file = os.path.join(OUTPUT_DIR, "predictions_next_5_years.csv")
        
        # Call the prediction function
        predict_next_5_years_monthly(
            data_file=uploaded_file_path,
            model_file=model_file,
            scaler_x_file=scaler_x_file,
            scaler_y_file=scaler_y_file,
            output_file=output_file
        )

        
        # Return the generated CSV file as a downloadable response
        return FileResponse(
            output_file,
            media_type="text/csv",
            filename="predictions_next_5_years.csv"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Cleanup: Delete the uploaded file
        if uploaded_file_path and os.path.exists(uploaded_file_path):
            os.remove(uploaded_file_path)

class ResDataset(Dataset):
    def __init__(self, file, sequence_length=5):
        super().__init__()
        self.sequence_length = sequence_length
        self.res = pd.read_csv(file)
        
        # Remove outliers
        #self.res = self.remove_outliers(self.res, ['Gross Capacity', 'Current Storage', 'Inflow', 'Outflow'])
        
        self.reservoirs = set(self.res['Reservoir'])
        self.x, self.y = self.generate_sequence()
        
        # Apply log transformation to Inflow and Outflow
        #self.x[:, :, 2] = np.log1p(self.x[:, :, 2])  # log1p is log(1 + x)
        #self.x[:, :, 3] = np.log1p(self.x[:, :, 3])
        #self.y[:, 2] = np.log1p(self.y[:, 2])
        #self.y[:, 3] = np.log1p(self.y[:, 3])

        # Standardize the data column-wise
        self.scaler_x = StandardScaler()
        self.scaler_y = StandardScaler()
        self.x = self.standardize_data(self.x, self.scaler_x)
        self.y = self.standardize_data(self.y, self.scaler_y)
        
        # Save the scalers
        with open(f'{DATA_DIR}res_x.pkl', 'wb') as f:
            pickle.dump(self.scaler_x, f)
        with open(f'{DATA_DIR}res_y.pkl', 'wb') as f:
            pickle.dump(self.scaler_y, f)

    def remove_outliers(self, df, columns):
        for column in columns:
            Q1 = df[column].quantile(0.25)
            Q3 = df[column].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            df = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
        return df

    def generate_sequence(self):
        x, y = [], []
        for res in self.reservoirs:
            res_data = self.res[self.res['Reservoir'] == res].sort_values(['Year'])
            for i in range(len(res_data) - self.sequence_length):
                seq_x = res_data.iloc[i:i + self.sequence_length][['Gross Capacity', 'Current Storage']].values.astype(np.float32)
                seq_y = res_data.iloc[i + self.sequence_length][['Gross Capacity', 'Current Storage']].values.astype(np.float32)
                x.append(seq_x)
                y.append(seq_y)
        return np.array(x, dtype=np.float32), np.array(y, dtype=np.float32)  # Save as float

    def standardize_data(self, data, scaler):
        shape = data.shape
        data = data.reshape(-1, shape[-1])
        data = scaler.fit_transform(data)
        data = data.reshape(shape)
        return data

    def __len__(self):
        return len(self.x)

    def __getitem__(self, idx):
        return torch.tensor(self.x[idx], dtype=torch.float32), torch.tensor(self.y[idx], dtype=torch.float32)


def retrain_model(data_file, model_file): 
    # Load dataset 
    
    dataset = ResDataset(data_file) 
    train_loader = DataLoader(dataset, batch_size=32, shuffle=True)

    # Load model 
    device = 'cuda' if torch.cuda.is_available() else 'cpu' 
    model = torch.load(model_file, map_location=device)
    criterion = nn.MSELoss() 
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    # Training loop 
    num_epochs = 1 
    for epoch in range(num_epochs): 
        model.train() 
        for inputs, targets in train_loader: 
            inputs, targets = inputs.to(device), targets.to(device) 
            optimizer.zero_grad() 
            outputs = model(inputs) 
            loss = criterion(outputs, targets) 
            loss.backward() 
            optimizer.step() 
        print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}") 
    
    # Save model 
    torch.save(model, model_file) 
    return model

def predict_next_5_years_monthly(data_file, model_file, scaler_x_file, scaler_y_file, output_file):
    """
    Predicts the next 5 years (monthly) for all districts and saves the results to a CSV file.

    Args:
        data_file (str): Path to the data CSV file.
        model_file (str): Path to the trained model file.
        scaler_x_file (str): Path to the scaler for input features.
        scaler_y_file (str): Path to the scaler for target features.
        output_file (str): Path to the output CSV file to save predictions.
    """
    # Load data
    data = pd.read_csv(data_file)
    data.replace('-', 0, inplace=True)
    data = data.dropna()

    # Load scalers
    with open(scaler_x_file, 'rb') as f:
        scaler_x = pickle.load(f)
    with open(scaler_y_file, 'rb') as f:
        scaler_y = pickle.load(f)

    # Load model
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = torch.load(model_file, map_location=device)
    model.eval()

    # Predict for the next 5 years (60 months)
    predictions = []
    for res in data['Reservoir'].unique():
        district_data = data[data['Reservoir'] == res].sort_values(['Year']).tail(2)
        district = district_data['District'].iloc[0]
        # Store the original Gross Capacity value
        original_gross_capacity = district_data['Gross Capacity'].values[0]
        last_year = int(district_data['Year'].values[-1])

        for year in range(1, 6):  # Next 5 years
            # Extract input features
            inputs = district_data[['Gross Capacity', 'Current Storage']].tail(2).values
            inputs = scaler_x.transform(inputs)
            gross = inputs[0][0]
            # Predict
            inputs = torch.tensor(inputs, dtype=torch.float32).to(device).unsqueeze(0)
            with torch.no_grad():
                outputs = model(inputs).cpu().numpy()

            # Inverse transform to original scale
            outputs_original_scale = scaler_y.inverse_transform(outputs).flatten()

            # Apply absolute value to ensure non-negative predictions
            outputs_original_scale = np.abs(outputs_original_scale)

            # Determine the new year
            new_year = last_year + year

            new_entry = pd.DataFrame({
                'Reservoir' : [res],
                'District': [district],
                'Year': [new_year],
                'Gross Capacity': [gross],
                'Current Storage': [outputs[0][1]],
            })

            # Append the new entry to district_data
            district_data = pd.concat([district_data, new_entry])

            # Append results
            predictions.append({
                'Reservoir' : res,
                'District': district,
                'Year': new_year,
                'Gross Capacity': original_gross_capacity,  # Keep the original value
                'Current Storage': outputs_original_scale[1],
            })

    # Save to CSV
    predictions_df = pd.DataFrame(predictions)
    predictions_df.to_csv(output_file, index=False)

