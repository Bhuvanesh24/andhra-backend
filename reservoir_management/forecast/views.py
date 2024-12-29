import requests
from django.http import JsonResponse
from .models import *
import csv , os,io,csv
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum
from django.core.files.storage import default_storage
from django.conf import settings
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.apps import apps
from django.http import HttpResponse


# POPULATION_FILE =  os.path.join(settings.BASE_DIR, 'forecast', 'file', 'pop.csv')
# MODEL_DIR = os.path.join(settings.BASE_DIR,'forecast','modes')
# model_path = os.path.join(MODEL_DIR,"enhanced_lstm_v4.pt")
# scalar_x_path = os.path.join(MODEL_DIR,"f_usage_x.pkl")
# scalar_y_path = os.path.join(MODEL_DIR,"f_usage_y.pkl")

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


def get_factors(request, district_id, year,month):
    if request.method == "GET":
        try:
            # Retrieve the district using the district_id
            dist = District.objects.get(id=district_id)
            year = int(year)
            month = int(month)
            
            if year < 2014:
                return JsonResponse({"status": "error", "message": "No data found for the given parameters"}, status=200)

            if year <= 2024:
                # Aggregate usage data for the given district and year
                usage_data = Usage.objects.filter(district=dist, year=year,month=month).aggregate(
                    rainfall=Sum("rainfall"),
                    irrigation=Sum("irrigation"),
                    industry=Sum("industry"),
                    domestic=Sum("domestic"),
                )
            else:
                # Fetch data from the prediction model
                usage_data = UsagePredictionDist.objects.filter(district=dist, year=year,month=month).aggregate(
                    rainfall=Sum("rainfall"),
                    irrigation=Sum("irrigation"),
                    industry=Sum("industry"),
                    domestic=Sum("domestic"),
                )

            if not usage_data:
                return JsonResponse({"status": "error", "message": "No data found for the given parameters"}, status=404)

            # Fetch land use data
            if year >=2023:
                landuse = LucPredictionDist.objects.filter(district=dist, year=year).first()
            else:
                landuse = LandusePast.objects.filter(district=dist, year=year).first()
            if not landuse:
                return JsonResponse({"status": "error", "message": "No land use data found for the given parameters"}, status=404)

            # Prepare data dictionary
            data_dict = {
                "District": dist.id,
                "Month": month,
                "Rainfall": usage_data["rainfall"],
                "Irrigation": usage_data["irrigation"],
                "Domestic": usage_data["domestic"],
                "Industry": usage_data["industry"],
                "Built-up": landuse.built_up,
                "Agricultural": landuse.agriculuture,  # Ensure correct field name
                "Forest": landuse.forest,
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


# def get_eports_data(request,district_id,year,month):
#     if request.method == "GET":
#         get_landuse_predictions = True if year>2022 else False
#         get_usage = True if year>2024 else False
#         get_reservoir = True if year > 2024 else False
#         try:
#             # Fetch district data
#             dist = District.objects.get(id=district_id)

#             if get_landuse_predictions:
#                 landuse = LucPredictionDist.objects.filter(district=dist, year=year).first()
#             else:
#                 landuse = LandusePast.objects.filter(district=dist, year=year).first()
            


def get_exports_data(request, district_id, year, month):
    if request.method == "GET":
        get_predictions = year > 2022
        get_usage = year > 2024
        get_reservoir = year > 2024

        try:
            # Fetch district data
            district = District.objects.get(id=district_id)
        except ObjectDoesNotExist:
            return JsonResponse({"status": "error", "message": "District not found"}, status=404)

        response_data = {"district": str(district), "year": year, "month": month}

        # Fetch land use data
        try:
            if get_predictions:
                land_use = LucPredictionDist.objects.get(district=district, year=year)
            else:
                land_use = LandusePast.objects.get(district=district, year=year)
            response_data["land_use"] = {
                "built_up": land_use.built_up,
                "agriculture": land_use.agriculuture,
                "forest": land_use.forest,
                "wasteland": land_use.wasteland,
                "wetlands": land_use.wetlands,
                "waterbodies": land_use.waterbodies,
            }
        except ObjectDoesNotExist:
            response_data["land_use_error"] = "Land use data not found"

        # Fetch usage data
        try:
            if get_usage:
                usage = UsagePredictionDist.objects.get(district=district, year=year, month=month)
            else:
                usage = Usage.objects.get(district=district, year=year, month=month)
            response_data["usage"] = {
                "rainfall": usage.rainfall,
                "consumption": usage.consumption,
                "irrigation": usage.irrigation,
                "industry": usage.industry,
                "domestic": usage.domestic,
            }
        except ObjectDoesNotExist:
            response_data["usage_error"] = "Usage data not found"

        # Fetch reservoir data
        if get_reservoir:
            try:
                # Dynamically get the ReservoirPrediction model
                ReservoirPrediction = apps.get_model('reservoir', 'ReservoirPrediction')  # Replace 'another_app' with the actual app name
                reservoir_data = ReservoirPrediction.objects.get(district=district, year=year, month=month)
                response_data["reservoir"] = {
                    "gross_capacity": reservoir_data.gross_capacity,
                    "current_storage": reservoir_data.current_storage,
                    "rainfall": reservoir_data.rainfall,
                    "evaporation": reservoir_data.evaporation,
                }
            except ObjectDoesNotExist:
                response_data["reservoir_error"] = "Reservoir prediction data not found"
            except LookupError:
                response_data["reservoir_error"] = "ReservoirPrediction model not found in the specified app"
        else:
            try:
                ReservoirData = apps.get_model("reservoir","ReservoirData")
                reservoir_data = ReservoirData.objects.get(district=district, year=year, month=month)
                response_data["reservoir"] = {
                    "gross_capacity": reservoir_data.gross_capacity,
                    "current_level": reservoir_data.current_level,
                    "current_storage": reservoir_data.current_storage,
                    "inflow": reservoir_data.inflow,
                    "outflow": reservoir_data.outflow,
                }
            except ObjectDoesNotExist:
                response_data["reservoir_error"] = "Reservoir data not found"

        output = io.StringIO()
        writer = csv.writer(output)

        # Write headers
        writer.writerow(["Key", "Value"])

        # Write the response_data dictionary into rows
        for key, value in response_data.items():
            if isinstance(value, dict):  # Handle nested dictionaries
                for sub_key, sub_value in value.items():
                    writer.writerow([f"{key}.{sub_key}", sub_value])
            else:
                writer.writerow([key, value])

        # Prepare CSV response
        output.seek(0)
        response = HttpResponse(output, content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="report_{district_id}_{year}_{month}.csv"'

        return response