import requests
from django.http import JsonResponse
from .models import *
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

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
        

# def get_population(request,year):
#     if request.method == "GET":

#         population_data = Population.objects.filter(year=year)
        
#         if not population_data:
#             return JsonResponse({"error": "Population data not found for the given state and year"}, status=404)
        
#         population_data_dict = population_data.values('year', 'total_population', 'urban_population', 'rural_population').first()
        
#         return JsonResponse(population_data_dict, status=200,safe=False)
    

# def water_usage(request,district_id,year):
#     if request.method == "GET":
#         district = get_object_or_404(District, id=district_id)

#         water_usage_data = Usage.objects.filter(district=district, year=year)

#         if not water_usage_data.exists():
#             return JsonResponse({
#                 "message": f"No water usage data available for the selected year ({year}) and state ({state.name}).",
#                 "data": None  
#             }, status=200)

        
#         water_usage_dict = water_usage_data.values('year', 'state', 'domestic_use', 'industrial_use', 'irrigation_use').first()
        
#         return JsonResponse(water_usage_dict, status=200, safe=False)

# @csrf_exempt
# def predict_usage(request):
#     """
#     Django view to fetch data from the database, send it to FastAPI,
#     and return the prediction.
#     """
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body)            
#             state_id = data.get("state_idx")
#             target_year = data.get("target_year")

#             if not state_id or not target_year:
#                 return JsonResponse({"error": "state_idx and target_year are required in the request body."}, status=400)
            
#             state = State.objects.get(id=state_id)
            
#             last_three_years = [target_year - i - 1 for i in range(3)]

           
#             landuse_data = LandUse.objects.filter(state=state, year__in=last_three_years)
#             population_data = Population.objects.filter(year__in=last_three_years)

          
#             structured_data = {}
#             for population in population_data:
#                 structured_data[population.year] = [
#                     population.urban_population,
#                     population.rural_population,
#                 ]

#             for landuse in landuse_data:
#                 structured_data[landuse.year].extend(
#                     [
#                         landuse.forest_use,
#                         landuse.barren_use,
#                         landuse.other_use,
#                         landuse.fallow_use,
#                         landuse.cropped_use,
#                     ]
#                 )



#             payload = {
#                 "state_idx": state_id,
#                 "target_year": target_year,
#                 "structured_data": structured_data,
#             }

        
          
#             response = requests.post(FASTAPI_URL, json=payload)
        
#             if response.status_code == 200:
#                 return JsonResponse(response.json(), safe=False)
#             else:
#                 return JsonResponse(
#                     {"error": f"Failed to get prediction: {response.json()}"}, status=500
#                 )

#         except json.JSONDecodeError:
#             return JsonResponse({"error": "Invalid JSON in request body."}, status=400)
#         except State.DoesNotExist:
#             return JsonResponse({"error": "State not found."}, status=404)
#         except Exception as e:
#             return JsonResponse({"error": str(e)}, status=500)
