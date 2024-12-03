# from gradio_client import Client
# from .schemas import ForecastRequest

# GRADIO_API_URL = "Bhuvi20/forecast"  
# client = Client(GRADIO_API_URL)


# async def call_model(data: ForecastRequest) -> dict:
#     """
#     Sends data to the Hugging Face model and returns the prediction.
#     """
#     structured_data = data.structured_data  
#     try:
        
#         prediction = client.predict(
#             data.state_idx, data.target_year, structured_data, api_name="/predict"
#         )
#         return prediction
#     except Exception as e:
#         raise Exception(f"Error while calling the model: {str(e)}")
