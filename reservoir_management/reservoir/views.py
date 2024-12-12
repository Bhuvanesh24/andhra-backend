import requests
from django.http import JsonResponse
from forecast.models import District,Evaporation,Rainfall
from .models import *
from datetime import datetime
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_exempt
import os
from django.http import FileResponse
import csv
from io import StringIO
from django.db import transaction
from django.apps import apps


# Evaporation = apps.get_model('forecast', 'Evaporation')
# Rainfall = apps.get_model('forecast', 'Rainfall')
# District = apss
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
                    "month" : data.month,
                })

            # Return the response with the reservoir data
            return JsonResponse( reservoir_data_list, safe=False)

        except Reservoir.DoesNotExist:
            return JsonResponse({"error": "Reservoir not found"}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    

def calculate_reservoir_health_score(request):
    """
    Calculate the reservoir health score based on storage, capacity, siltation, flood cushion, evaporation, rainfall, and age.

    Parameters:
    - storage_tmc (float): Current water storage in TMC.
    - capacity_tmc (float): Maximum reservoir capacity in TMC.
    - siltation_tmc (float): Siltation volume in TMC.
    - flood_cushion_tmc (float): Available flood cushion in TMC.
    - evaporation_mm (float): Evaporation loss in mm.
    - rainfall_mm (float): Rainfall in mm.
    - age_years (float): Age of the reservoir in years.
    - design_life_years (float): Design life of the reservoir in years.

    Returns:
    - float: Final reservoir health score (0-100).
    """
    storage_tmc = float(request.GET.get("current_storage"))
    capacity_tmc = float(request.GET.get("gross_capacity"))
    siltation_tmc = float(request.GET.get("siltation"))
    flood_cushion_tmc = float(request.GET.get("flood_cushion"))
    evaporation_mm = float(request.GET.get("evaporation"))
    rainfall_mm = float(request.GET.get("rainfall"))
    age_years = int(request.GET.get("age"))
    design_life_years = int(request.GET.get("design_life"))

    # Weights for each parameter
    weights = {
        'storage_capacity_ratio': 0.25,
        'siltation': 0.10,
        'flood_cushion': 0.15,
        'evaporation': 0.10,
        'age': 0.20,
        'rainfall': 0.20
    }

    # 1. Storage/Capacity Ratio Score (higher is better)
    storage_capacity_ratio = (storage_tmc / capacity_tmc) * 100
    storage_capacity_score = min(storage_capacity_ratio, 100)

    # 2. Siltation Score (lower siltation is better)
    siltation_impact = (siltation_tmc / capacity_tmc) * 100
    siltation_score = max(100 - siltation_impact, 0)

    # 3. Flood Cushion Score (higher is better)
    flood_cushion_ratio = (flood_cushion_tmc / capacity_tmc) * 100
    flood_cushion_score = min(flood_cushion_ratio, 100)

    # 4. Evaporation Score (lower is better)
    evaporation_score = max(100 - evaporation_mm / 10, 0)  # Scaling evaporation impact

    # 5. Age Score (younger reservoirs are better)
    age_ratio = (age_years / design_life_years) * 100
    age_score = max(100 - age_ratio, 0)

    # 6. Rainfall Score (higher rainfall is better)
    rainfall_score = min(rainfall_mm / 10, 100)  # Scaling rainfall to a 0-100 range

    # Weighted Sum of All Scores
    final_score = (
        storage_capacity_score * weights['storage_capacity_ratio'] +
        siltation_score * weights['siltation'] +
        flood_cushion_score * weights['flood_cushion'] +
        evaporation_score * weights['evaporation'] +
        age_score * weights['age'] +
        rainfall_score * weights['rainfall']
    )

    return JsonResponse({"score" : round(final_score, 2)},status = 200)


def get_age_siltation(request):
    if request.method == "GET":
        dist_id = int(request.GET.get("district_id"))
        year    = int(request.GET.get("year"))
        month   = int(request.GET.get("month"))
        res_id = int(request.GET.get("reservoir_id"))
        
        res = Reservoir.objects.get(id=res_id)
        dist = District.objects.get(id=dist_id)
        
        evap = None
        rain = None

        try:
            evap = Evaporation.objects.get(district=dist, year=year, month=month)
        except Evaporation.DoesNotExist:
            print(f"Evaporation data not found for district {dist}, year {year}, month {month}")

        try:
            rain = Rainfall.objects.get(district=dist, year=year, month=month)
        except Rainfall.DoesNotExist:
            print(f"Rainfall data not found for district {dist}, year {year}, month {month}")

        get = ReservoirScore.objects.get(reservoir = res,year=2024)
        silt = get.siltation
        age = get.age
        evaporation = 50
        rainfall = 50
        if evap:
            evaporation = evap.total_evaporation
        if rain:
            rainfall = rain.actual
        
        return JsonResponse({"silt":silt,"age":age,"evaporation":evaporation,"rainfall":rainfall},status=200)
    
        

        



        

        
                                
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