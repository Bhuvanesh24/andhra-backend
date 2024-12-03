# import torch
# import numpy as np
# import pandas as pd
# import pickle
# from sklearn.preprocessing import StandardScaler
# from torch.utils.data import DataLoader

# def retrain_model(data_file, model_file): 
#     # Load dataset 
#     dataset = ResDataset(data_file) 
#     train_loader = DataLoader(dataset, batch_size=32, shuffle=True)

#     # Load model 
#     device = 'cuda' if torch.cuda.is_available() else 'cpu' 
#     model = torch.load(model_file, map_location=device)
#     criterion = nn.MSELoss() 
#     optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

#     # Training loop 
#     num_epochs = 10 
#     for epoch in range(num_epochs): 
#         model.train() 
#         for inputs, targets in train_loader: 
#             inputs, targets = inputs.to(device), targets.to(device) 
#             optimizer.zero_grad() 
#             outputs = model(inputs) 
#             loss = criterion(outputs, targets) 
#             loss.backward() 
#             optimizer.step() 
#         print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}") 
    
#     # Save model 
#     torch.save(model, model_file) 
#     return model

# def predict_next_5_years_monthly(data_file, model_file, scaler_x_file, scaler_y_file, output_file):
#     """
#     Predicts the next 5 years (monthly) for all districts and saves the results to a CSV file.

#     Args:
#         data_file (str): Path to the data CSV file.
#         model_file (str): Path to the trained model file.
#         scaler_x_file (str): Path to the scaler for input features.
#         scaler_y_file (str): Path to the scaler for target features.
#         output_file (str): Path to the output CSV file to save predictions.
#     """
#     # Load data
#     data = pd.read_csv(data_file)
#     data.replace('-', 0, inplace=True)
#     data = data.dropna()

#     # Load scalers
#     with open(scaler_x_file, 'rb') as f:
#         scaler_x = pickle.load(f)
#     with open(scaler_y_file, 'rb') as f:
#         scaler_y = pickle.load(f)

#     # Load model
#     device = 'cuda' if torch.cuda.is_available() else 'cpu'
#     model = torch.load(model_file, map_location=device)
#     model.eval()

#     # Predict for the next 5 years (60 months)
#     predictions = []
#     for res in data['Reservoir'].unique():
#         district_data = data[data['Reservoir'] == res].sort_values(['Year']).tail(2)
#         district = district_data['District'].iloc[0]
#         # Store the original Gross Capacity value
#         original_gross_capacity = district_data['Gross Capacity'].values[0]
#         last_year = int(district_data['Year'].values[-1])

#         for year in range(1, 6):  # Next 5 years
#             # Extract input features
#             inputs = district_data[['Gross Capacity', 'Current Storage','Inflow','Outflow']].tail(2).values
#             inputs = scaler_x.transform(inputs)
#             gross = inputs[0][0]
#             # Predict
#             inputs = torch.tensor(inputs, dtype=torch.float32).to(device).unsqueeze(0)
#             with torch.no_grad():
#                 outputs = model(inputs).cpu().numpy()

#             # Inverse transform to original scale
#             outputs_original_scale = scaler_y.inverse_transform(outputs).flatten()

#             # Apply absolute value to ensure non-negative predictions
#             outputs_original_scale = np.abs(outputs_original_scale)

#             # Determine the new year
#             new_year = last_year + year

#             new_entry = pd.DataFrame({
#                 'Reservoir' : [res],
#                 'District': [district],
#                 'Year': [new_year],
#                 'Gross Capacity': [gross],
#                 'Current Storage': [outputs[0][1]],
#                 'Inflow' : [outputs[0][2]],
#                 'Outflow' : [outputs[0][3]]
#             })

#             # Append the new entry to district_data
#             district_data = pd.concat([district_data, new_entry])

#             # Append results
#             predictions.append({
#                 'Reservoir' : res,
#                 'District': district,
#                 'Year': new_year,
#                 'Gross Capacity': original_gross_capacity,  # Keep the original value
#                 'Current Storage': outputs_original_scale[1],
#                 'Inflow' : np.exp(outputs_original_scale[2]),
#                 'Outflow' : np.exp(outputs_original_scale[3])
#             })

#     # Save to CSV
#     predictions_df = pd.DataFrame(predictions)
#     predictions_df.to_csv(output_file, index=False)

# # Example usage
# predict_next_5_years_monthly(
#     data_file='data/res_2.csv',
#     model_file='model/enhanced_res_6.pt',
#     scaler_x_file='data/scaler_x.pkl',
#     scaler_y_file='data/scaler_y.pkl',
#     output_file='predictions_next_5_years_monthly.csv'
# )


