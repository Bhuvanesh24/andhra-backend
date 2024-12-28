from django.http import JsonResponse
from forecast.models import District,Usage
import requests
# Create your views here.
FASTAPI_URL = "http://127.0.0.1:8001/scenario/predict/" 

def get_data(request, district_id, year):
    if request.method == "GET":
        try:
            district = District.objects.get(id=district_id)
            usage = Usage.objects.filter(district=district, year=year)
            
            
            if not usage.exists():
                return JsonResponse({"error": "No data found for the given district and year"}, status=200)
    
            data = []
            for u in usage:
                data.append({
                    "inflow_states": u.inflow_states if u.inflow_states is not None else 0.0,
                    "outflow": u.outflow if u.outflow is not None else 0.0,
                    "consumption": u.consumption if u.consumption is not None else 0.0,
                })
            
            return JsonResponse({"data": data}, status=200)
        
        except District.DoesNotExist:
            return JsonResponse({"error": "District not found"}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)



def get_simulator(request):
    # Extract query parameters
    evaporation = float(request.GET.get("evaporation", "0")) 
    rainfall = float(request.GET.get("rainfall", "0"))
    population = int(request.GET.get("population", "0"))
    district_id = int(request.GET.get("district_id","0"))
    inflow = int(request.GET.get("inflow"))
    outflow = int(request.GET.get("outflow"))
    


    data = {
        "evaporation": evaporation,
        "rainfall": rainfall,
        "population": population,
        "district": district_id,
        "inflow": inflow,
        "outflow": outflow,
        }
    response = requests.post(FASTAPI_URL, json=data)
    # Return response from FastAPI
    return JsonResponse(response.json(), status=200)
