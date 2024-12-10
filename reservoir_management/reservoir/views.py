import requests
from django.http import JsonResponse
from forecast.models import District
from .models import *
from datetime import datetime
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_exempt
import os
from django.http import FileResponse
import csv
from io import StringIO
from django.db import transaction

FASTAPI_URL = "http://127.0.0.1:8001/reservoir/" 

def reservoirs_by_districts(request, district_id):
    if request.method == 'GET':
        try:
            # Fetch the district based on the provided district_id
            district = District.objects.get(id=district_id)
            
            # Fetch the reservoirs for the specified district
            reservoirs = Reservoir.objects.filter(district=district)
            
            # If no reservoirs exist for the district, return an error message
            if not reservoirs.exists():
                return JsonResponse({"error": "No reservoirs found for the given district."}, status=200)

            # Prepare reservoir data for the response
            reservoirs_data = []
            for reservoir in reservoirs:
                reservoirs_data.append({
                    "id": reservoir.id,  # Reservoir ID
                    "district": district.name,  # District Name
                    "name": reservoir.name,  # Reservoir Name
                })

            # Return the response with the reservoirs data
            return JsonResponse(reservoirs_data, safe=False)

        except District.DoesNotExist:
            return JsonResponse({"error": "District not found"}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
        
def reservoir_by_id(request, reservoir_id, year):
    if request.method == 'GET':
        try:
            # Fetch the reservoir based on the provided reservoir_id
            reservoir = Reservoir.objects.get(id=reservoir_id)
            
            # Fetch the related ReservoirData for the specified year
            reservoir_data = ReservoirData.objects.filter(reservoir=reservoir, year=year)

            # If no reservoir data exists for the given year, return an error
            if not reservoir_data.exists():
                return JsonResponse({"error": "No reservoir data found for the given year."}, status=200)

            # Prepare the data to be returned as a response
            reservoir_data_list = []
            for data in reservoir_data:
                reservoir_data_list.append({
                    "id": data.id,
                    "reservoir": data.reservoir.name,
                    "district": data.district.name,  # Assuming district is a related model
                    "basin": data.basin,
                    "gross_capacity": data.gross_capacity,
                    "current_level": data.current_level,
                    "current_storage": data.current_storage,
                    "flood_cushion": data.flood_cushion,
                    "inflow": data.inflow,
                    "outflow": data.outflow,
                    "year": data.year,
                    "month": data.month,
                })

            # Return the response with the reservoir data
            return JsonResponse( reservoir_data_list, safe=False)

        except Reservoir.DoesNotExist:
            return JsonResponse({"error": "Reservoir not found"}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

def reservoir_by_id_five(request, reservoir_id, year):
    if request.method == 'GET':
        try:
            # Fetch the reservoir based on the provided reservoir_id
            reservoir = Reservoir.objects.get(id=reservoir_id)

            # Handle the case where the year is less than 2017 (minimum available data year)
            if year < 2017:
                return JsonResponse({"error": "No data available for the selected year or earlier."}, status=200)

            # If the year is 2017 or later, fetch data for the last 5 years
            current_year = datetime.now().year
            start_year = max(2017, int(year) - 5)  # Ensure we don't go below 2017

            # Fetch the related ReservoirData for the given reservoir and the last 5 years
            reservoir_data = ReservoirData.objects.filter(
                reservoir=reservoir,
                year__gte=start_year,
                year__lte=int(year)
            ).order_by('year', 'month')  # Optional: Order by year and month

            # If no reservoir data exists for the past 5 years, return an error
            if not reservoir_data.exists():
                return JsonResponse({"error": "No reservoir data found for the past 5 years."}, status=200)

            # Prepare the data to be returned as a response
            reservoir_data_list = []
            for data in reservoir_data:
                reservoir_data_list.append({
                    "id": data.id,
                    "reservoir": data.reservoir.name,
                    "district": data.district.name,  # Assuming district is a related model
                    "basin": data.basin,
                    "gross_capacity": data.gross_capacity,
                    "current_level": data.current_level,
                    "current_storage": data.current_storage,
                    "flood_cushion": data.flood_cushion,
                    "inflow": data.inflow,
                    "outflow": data.outflow,
                    "year": data.year,
                    "month": data.month,
                })

            # Return the response with the reservoir data for the past 5 years
            return JsonResponse( reservoir_data_list, safe=False)

        except Reservoir.DoesNotExist:
            return JsonResponse({"error": "Reservoir not found"}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


def reservoir_prediction(request,reservoir_id,year):
    if request.method == 'GET':
        try:
            # Fetch the reservoir based on the provided reservoir_id
            reservoir = Reservoir.objects.get(id=reservoir_id)
            
            # Fetch the related ReservoirData for the specified year
            reservoir_data = ReservoirPrediction.objects.filter(reservoir=reservoir, year=year)

            # If no reservoir data exists for the given year, return an error
            if not reservoir_data.exists():
                return JsonResponse({"error": "No reservoir data found for the given year."}, status=200)

            # Prepare the data to be returned as a response
            reservoir_data_list = []
            for data in reservoir_data:
                reservoir_data_list.append({
                    "id": data.id,
                    "reservoir": data.reservoir.name,
                    "district": data.district.name,  # Assuming district is a related model
                    "gross_capacity": data.gross_capacity,
                    "current_storage": data.current_storage,
                    "year": data.year,
                })

            # Return the response with the reservoir data
            return JsonResponse( reservoir_data_list, safe=False)

        except Reservoir.DoesNotExist:
            return JsonResponse({"error": "Reservoir not found"}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    

def get_reservoir_score(request):
    current_year = datetime.now().year
    if request.method == 'GET':
        year =  int(request.GET.get("year"))
        res_id = int(request.GET.get("reservoir_id"))
        if year > current_year:
            data_dict = {
            "mean_storage" : float(request.GET.get("mean-storage")),
            "flood_cushion" : float(request.GET.get("flood-cushion")),
            "rainfall" : float(request.GET.get("rainfall")),
            "evaporation"  : float(request.GET.get("evaporation")),
            "population" : int(request.GET.get("population")),
            "age" : int(request.GET.get("age")),
            "siltation" : float(request.GET.get("siltation")),
            "capacity" : float(request.GET.get("capacity")),
            }
            
            response = requests.post(f'{FASTAPI_URL}/predict_score', json=data_dict)

            if response.status_code == 200:
                result = response.json()
                return JsonResponse({"predicted_score": result["predicted_score"]}, status=200)
            else:
                return JsonResponse({"error": "Error occurred while predicting the score."}, status=500)
        else:
            res = Reservoir.objects.get(id = res_id)
            data = ReservoirScore.objects.get(year=current_year,reservoir = res)
            data_dict = {
                    "mean_storage": data.mean_storage,
                    "flood_cushion": data.flood_cushion,
                    "rainfall": data.rainfall,
                    "evaporation": data.evaporation,
                    "population": data.population,
                    "siltation": data.siltation,
                    "capacity": data.capacity,
                    "age": data.age,
                    "score" : data.score
            }
            return JsonResponse({"data" : data_dict},safe=False)
      

        
                                
@csrf_exempt
def retrain_and_update_data(request):
    if request.method == "POST":
        try:
            # Check if a file is included in the request
            csv_file = request.FILES.get('file')
            if not csv_file:
                return JsonResponse({
                    "status": "error",
                    "message": "No CSV file provided."
                }, status=400)

            # Save the uploaded file temporarily
            temp_file_path = default_storage.save(f"temp/{csv_file.name}", csv_file)

            # Send the file to FastAPI
            fastapi_url = "http://127.0.0.1:8001/reservoir/retrain"  # Replace with the actual FastAPI endpoint
            with open(temp_file_path, 'rb') as file:
                response = requests.post(fastapi_url, files={"file": file})

            # Cleanup temporary file
            default_storage.delete(temp_file_path)

            # Handle response from FastAPI
            if response.status_code == 200:
                # Decode the CSV content from FastAPI response
                csv_content = response.content.decode("utf-8")

                # Call the update function with the CSV data
                update_reservoir_predictions(csv_content)

                return JsonResponse({
                    "status": "success",
                    "message": "Data successfully updated."
                })

            else:
                return JsonResponse({
                    "status": "error",
                    "message": f"FastAPI returned an error: {response.text}"
                }, status=500)

        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": str(e)
            }, status=500)

    return JsonResponse({
        "status": "error",
        "message": "Invalid request method. Use POST."
    }, status=405)



def update_reservoir_predictions(csv_data):
    """
    Update the ReservoirPrediction table with data from a CSV file.

    :param csv_data: CSV content as a string
    """
    try:
        # Parse the CSV data
        csv_file = StringIO(csv_data)
        reader = csv.DictReader(csv_file)

        # Start a transaction for batch updates
        with transaction.atomic():
            for row in reader:
                # Fetch the related Reservoir and District objects
                reservoir = Reservoir.objects.get(id=int(row["Reservoir"].strip()))
                district = District.objects.get(id=row["District"].strip())

                # Update or create a ReservoirPrediction entry
                obj, created = ReservoirPrediction.objects.update_or_create(
                    reservoir=reservoir,
                    district=district,
                    year=int(row["Year"]),
                    defaults={
                        "gross_capacity": float(row["Gross Capacity"]),
                        "current_storage": float(row["Current Storage"]),
                    }
                )
                if created:
                    print(f"Created: {obj}")
                else:
                    print(f"Updated: {obj}")
        print("Reservoir predictions successfully updated.")
    except Exception as e:
        print(f"An error occurred: {e}")