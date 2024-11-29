import requests
from django.http import JsonResponse
from .models import *
import csv
from django.core.exceptions import ObjectDoesNotExist
from io import StringIO
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.core.files.storage import default_storage
FASTAPI_URL = "http://127.0.0.1:8001/forecast/predict/"  

def test(request):
    return JsonResponse({"test":"Fine"})

def get_dist(request):
    if request.method == "GET":
        districts = District.objects.all()
        return JsonResponse(list(districts.values()),safe=False)
    

def get_landuse(request, year):
    """
    View to fetch land use data for a specific year and return it as JSON.
    """
    try:
        # Fetch land use data for the given year
        landuse_data = LandUse.objects.get(year=year)

        # Serialize the data into a dictionary
        landuse_data_dict = {
            "year": landuse_data.year,
            "forest_use": landuse_data.forest_use,
            "barren_use": landuse_data.barren_use,
            "fallow_use": landuse_data.fallow_use,
            "cropped_use": landuse_data.cropped_use,
            "other_use": landuse_data.other_use,
        }

        # Return serialized data as JSON response
        return JsonResponse(landuse_data_dict, status=200, safe=False)

    except ObjectDoesNotExist:
        # Handle the case where no data exists for the given year
        return JsonResponse({"error": "No land use data found for this year."}, status=200)

    except Exception as e:
        # Handle unexpected errors
        return JsonResponse({"error": str(e)}, status=500)
    

def get_usage(request,district_id,year):
    if request.method == "GET":
        try:
            district = District.objects.get(id=district_id)
            water_usage = Usage.objects.filter(district=district,year=year)
            if not water_usage:
                return JsonResponse({"error":"No data available for the selected year"},status=200)
            return JsonResponse(list(water_usage.values()),safe=False)
        except ObjectDoesNotExist:
            return JsonResponse({"error": "No data found for this district and year"}, status=200)
        
def get_evaporation(request,district_id,year):
    if request.method == "GET":
        try:
            district = District.objects.get(id=district_id)
            evaporation_data = Evaporation.objects.filter(district=district, year=year)
            serialized_data = [
                {
                    "evapo_transpiration": evaporation.evapo_transpiration,
                    "total_evaporation": evaporation.total_evaporation,
                    "month": evaporation.month,
                }
                for evaporation in evaporation_data
            ]
            return JsonResponse( serialized_data, status=200,safe=False)
        except District.DoesNotExist:
            return JsonResponse({"error": "District not found"}, status=200)
        except Evaporation.DoesNotExist:
            return JsonResponse({"error": "Evaporation data not found"}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)

def get_rainfall(request,district_id,year):
    if request.method == "GET":
        try:
            district = District.objects.get(id=district_id)
            rainfall_data = Rainfall.objects.filter(district=district, year=year)
            serialized_data = [
                {
                    "normal": rainfall.normal,
                    "actual": rainfall.actual,
                    "month": rainfall.month,
                }
                for rainfall in rainfall_data
            ]
            return JsonResponse( serialized_data, status=200,safe=False)
        except District.DoesNotExist:
            return JsonResponse({"error": "District not found"}, status=200)
        except Evaporation.DoesNotExist:
            return JsonResponse({"error": "Rainfall data not found"}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)
        

def get_predictions_usage(request,district_id,year):
    if request.method == "GET":
        try:
            # Retrieve the district using the district_id
            district = District.objects.get(id=district_id)

            # Retrieve all predictions for the given year and district
            predictive_data = UsagePredictionDist.objects.filter(year=year, district=district)

            if not predictive_data.exists():
               
                return JsonResponse({
                    "message": f"No prediction data found for district '{district.name}' in year {year}."
                }, status=404)
            
            # Format the data for JSON response
            predictions = [
                {
                    "month": data.month,
                    "rainfall": data.rainfall,
                    "inflow_states": data.inflow_states,
                    "consumption": data.consumption,
                    "irrigation": data.irrigation,
                    "industry": data.industry,
                    "domestic": data.domestic,
                }
                for data in predictive_data
            ]

            # Return the predictions in JSON format
            return JsonResponse(predictions, status=200,safe=False)


        except District.DoesNotExist:
            return JsonResponse({
                "message": f"District with ID {district_id} not found."
            }, status=200)
        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": str(e)
            }, status=500)


def get_predictions_luc(request, district_id, year):
    if request.method == "GET":
        try:
            # Retrieve the district using the district_id
            district = District.objects.get(id=district_id)

            # Filter predictions for the given district and year
            predictive_data = LucPredictionDist.objects.filter(district=district, year=year)

            if not predictive_data.exists():
                return JsonResponse({
                    "status": "error",
                    "message": f"No prediction data found for district '{district.name}' in year {year}."
                }, status=404)

            # Format the data for JSON response
            predictions = [
                {
                    "built_up": data.built_up,
                    "agriculture": data.agriculuture,
                    "forest": data.forest,
                    "wasteland": data.wasteland,
                    "wetlands": data.wetlands,
                    "waterbodies": data.waterbodies,
                    "year": data.year,
                }
                for data in predictive_data
            ]

            # Return the predictions in JSON format
            return JsonResponse(predictions, status=200,safe=False)

        except District.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": f"District with ID {district_id} not found."
            }, status=200)

        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": str(e)
            }, status=500)
        

@csrf_exempt
def retrain_and_update_data(request):
    if request.method == "POST":
        try:
            # 1. Check if a file is included in the request
            csv_file = request.FILES.get('file')
            if not csv_file:
                return JsonResponse({
                    "status": "error",
                    "message": "No CSV file provided."
                }, status=400)

            # Save the uploaded file temporarily
            temp_file_path = default_storage.save(f"temp/{csv_file.name}", csv_file)

            # 2. Send the file to FastAPI for retraining
            fastapi_url = "http://fastapi-url/retrain"  # Replace with the actual FastAPI endpoint
            with open(temp_file_path, 'rb') as file:
                response = requests.post(fastapi_url, files={"file": file})

            # Check if FastAPI returned a successful response
            if response.status_code != 200:
                return JsonResponse({
                    "status": "error",
                    "message": f"FastAPI returned an error: {response.text}"
                }, status=500)

            # 3. Parse the output CSV received from FastAPI
            output_csv = StringIO(response.text)
            reader = csv.DictReader(output_csv)

            # Start a transaction to update the database
            with transaction.atomic():
                for row in reader:
                    try:
                        # Fetch the district by ID
                        district = District.objects.get(id=int(row['District']))

                        # Update or create the record in LucPredictionDist
                        LucPredictionDist.objects.update_or_create(
                            district=district,
                            year=int(row['Year']),
                            defaults={
                                "built_up": float(row['Built-Up']),
                                "agriculuture": float(row['Agricultural']),
                                "forest": float(row['Forest']),
                                "wasteland": float(row['Wastelands']),
                                "wetlands": float(row['Wetlands']),
                                "waterbodies": float(row['Waterbodies']),
                            }
                        )
                    except District.DoesNotExist:
                        return JsonResponse({
                            "status": "error",
                            "message": f"District with ID {row['District']} not found."
                        }, status=404)

            # Cleanup temporary file
            default_storage.delete(temp_file_path)

            return JsonResponse({
                "status": "success",
                "message": "Database updated successfully."
            }, status=200)

        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": str(e)
            }, status=500)

    return JsonResponse({
        "status": "error",
        "message": "Invalid request method. Use POST."
    }, status=405)