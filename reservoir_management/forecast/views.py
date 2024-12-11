import requests
from django.http import JsonResponse
from .models import *
import csv
from django.core.exceptions import ObjectDoesNotExist
from io import StringIO
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.db.models import Sum
from django.core.files.storage import default_storage
from datetime import datetime

FASTAPI_URL = "http://127.0.0.1:8001/forecast/"  

def test(request):
    return JsonResponse({"test":"Fine"})

def get_dist(request):
    if request.method == "GET":
        districts = District.objects.all()
        return JsonResponse(list(districts.values()),safe=False)
    

def get_landuse(request, district_id,year):
    """
    View to fetch land use data for a specific year and return it as JSON.
    """
    if request.method == "GET":
        try:
            # Retrieve the district using the district_id
            district = District.objects.get(id=district_id)

            # Filter predictions for the given district and year
            predictive_data = LandusePast.objects.filter(district=district, year=year)

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

def get_usage(request,district_id,year):
    if request.method == "GET":
        try:
            district = District.objects.get(id=district_id)
            water_usage = Usage.objects.filter(district=district,year=year)
            predictions =[{
                "month" : water.month,
                "rainfall" : water.rainfall,
                "inflow_state" : water.inflow_states,
                "consumption" : water.consumption,
                "irrigation" : water.irrigation,
                "industry" : water.industry,
                "domestic" : water.domestic,
            }
            for water in water_usage
            ]
            if not water_usage:
                return JsonResponse({"error":"No data available for the selected year"},status=200)
            return JsonResponse(predictions , safe=False)
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


def get_factors(request, district_id, year):
    if request.method == "GET":
        try:
            # Retrieve the district using the district_id
            dist = District.objects.get(id=district_id)
            year = int(year)
            
            if year < 2023:
                return JsonResponse({"status": "error", "message": "No data found for the given parameters"}, status=200)

            if year == 2023:
                # Aggregate usage data for the given district and year
                usage_data = Usage.objects.filter(district=dist, year=year,month=6).aggregate(
                    rainfall=Sum("rainfall"),
                    irrigation=Sum("irrigation"),
                    industry=Sum("industry"),
                    domestic=Sum("domestic"),
                )
            else:
                # Fetch data from the prediction model
                usage_data = Usage.objects.filter(district=dist, year=year,month=6).aggregate(
                    rainfall=Sum("rainfall"),
                    irrigation=Sum("irrigation"),
                    industry=Sum("industry"),
                    domestic=Sum("domestic"),
                )

            if not usage_data:
                return JsonResponse({"status": "error", "message": "No data found for the given parameters"}, status=404)

            # Fetch land use data
            landuse = LucPredictionDist.objects.filter(district=dist, year=year).first()
            if not landuse:
                return JsonResponse({"status": "error", "message": "No land use data found for the given parameters"}, status=404)

            # Prepare data dictionary
            data_dict = {
                "District": dist.id,
                "Month": 6,
                "Rainfall": usage_data["rainfall"],
                "Irrigation": usage_data["irrigation"],
                "Domestic": usage_data["domestic"],
                "Industry": usage_data["industry"],
                "Built-up": landuse.built_up,
                "Agricultural": landuse.agriculuture,  # Ensure correct field name
                "Forest": landuse.forest,
                "Waterbodies": landuse.waterbodies,
                "Wetlands": landuse.wetlands,
                "Wasteland": landuse.wasteland,
            }
            print(data_dict)
            # Make a POST request to the FastAPI endpoint
            response = requests.post(f'{FASTAPI_URL}get-factors', json=data_dict)

            if response.status_code == 200:
                return JsonResponse(response.json(), status=200)
            else:
                return JsonResponse({"status": "error", "message": f"FastAPI error: {response.text}"}, status=response.status_code)

        except District.DoesNotExist:
            return JsonResponse({"status": "error", "message": "District not found"}, status=404)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)


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
            fastapi_url = "http://127.0.0.1:8001/forecast/retrain"  # Replace with the actual FastAPI endpoint
            with open(temp_file_path, 'rb') as file:
                response = requests.post(fastapi_url, files={"file": file})

            # Cleanup temporary file
            default_storage.delete(temp_file_path)

            # Handle response from FastAPI
            if response.status_code == 200:
                # Decode the CSV content from FastAPI response
                csv_content = response.content.decode("utf-8")

                # Call the update function with the CSV data
                print(csv_content)

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

