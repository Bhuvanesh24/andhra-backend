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


def get_landuse(request, state_id, year):
    """
    View to fetch land use data for a specific state and year, and return it as JSON.
    """

    try:
        
        state = get_object_or_404(State, id=state_id)
    except ObjectDoesNotExist:
        return JsonResponse({"error": "State not found"}, status=404)

   
    landuse_data = LandUse.objects.filter(state=state, year=year)
    
    if not landuse_data:
        return JsonResponse({"error": "No land use data found for this state and year"}, status=404)

    landuse_data_dict = landuse_data.values('year','state','forest_use','barren_use','fallow_use','cropped_use','other_use').first()
    return JsonResponse(landuse_data_dict,status = 200,safe=False)
   
def get_population(request,year):
    if request.method == "GET":

        population_data = Population.objects.filter(year=year)
        
        if not population_data:
            return JsonResponse({"error": "Population data not found for the given state and year"}, status=404)
        
        population_data_dict = population_data.values('year', 'total_population', 'urban_population', 'rural_population').first()
        
        return JsonResponse(population_data_dict, status=200,safe=False)
    

def water_usage(request,state_id,year):
    if request.method == "GET":
        state = get_object_or_404(State, id=state_id)

        
        water_usage_data = Usage.objects.filter(state=state, year=year)

        
        if not water_usage_data.exists():
            return JsonResponse({
                "message": f"No water usage data available for the selected year ({year}) and state ({state.name}).",
                "data": None  
            }, status=200)

        
        water_usage_dict = water_usage_data.values('year', 'state', 'domestic_use', 'industrial_use', 'irrigation_use').first()
        
        return JsonResponse(water_usage_dict, status=200, safe=False)
@csrf_exempt
def predict_usage(request):
    """
    Django view to fetch data from the database, send it to FastAPI,
    and return the prediction.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)            
            state_id = data.get("state_idx")
            target_year = data.get("target_year")

            if not state_id or not target_year:
                return JsonResponse({"error": "state_idx and target_year are required in the request body."}, status=400)
            
            state = State.objects.get(id=state_id)
            
            last_three_years = [target_year - i - 1 for i in range(3)]

           
            landuse_data = LandUse.objects.filter(state=state, year__in=last_three_years)
            population_data = Population.objects.filter(year__in=last_three_years)

          
            structured_data = {}
            for population in population_data:
                structured_data[population.year] = [
                    population.urban_population,
                    population.rural_population,
                ]

            for landuse in landuse_data:
                structured_data[landuse.year].extend(
                    [
                        landuse.forest_use,
                        landuse.barren_use,
                        landuse.other_use,
                        landuse.fallow_use,
                        landuse.cropped_use,
                    ]
                )



            payload = {
                "state_idx": state_id,
                "target_year": target_year,
                "structured_data": structured_data,
            }

        
          
            response = requests.post(FASTAPI_URL, json=payload)
        
            if response.status_code == 200:
                return JsonResponse(response.json(), safe=False)
            else:
                return JsonResponse(
                    {"error": f"Failed to get prediction: {response.json()}"}, status=500
                )

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON in request body."}, status=400)
        except State.DoesNotExist:
            return JsonResponse({"error": "State not found."}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
