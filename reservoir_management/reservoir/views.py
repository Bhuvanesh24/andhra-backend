from django.shortcuts import render
import requests
from django.http import JsonResponse
from forecast.models import State
from .models import *
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist




def reservoirs_by_states(request, state_id, year):
    if request.method == 'GET':
        try:
            state = get_object_or_404(State, id=state_id)
            reservoirs = Reservoir.objects.filter(state=state, year=year)

            reservoirs_data = []
            for reservoir in reservoirs:
                reservoirs_data.append({
                    "id": reservoir.id,
                    "district": reservoir.district,
                    "name": reservoir.name,
                    "agency_name": reservoir.agency_name,
                    "frl": reservoir.frl,
                    "live_cap_frl": reservoir.live_cap_frl,
                    "level": reservoir.level,
                    "current_live_storage": reservoir.current_live_storage,
                    "year": reservoir.year,
                    "month": reservoir.month,
                })

            
            return JsonResponse({"state": state.name, "year": year, "reservoirs": reservoirs_data}, safe=False)

        except State.DoesNotExist:
            return JsonResponse({"error": "State not found"}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)



def reservoirs_by_name_dist(request, state_id, year, name, dist_name):
    if request.method == 'GET':
        try:
            state = get_object_or_404(State, id=state_id)
            reservoirs = Reservoir.objects.filter(
                state=state,
                year=year,
                name__icontains=name,  
                district__icontains=dist_name 
            )

            reservoirs_data = []
            for reservoir in reservoirs:
                reservoirs_data.append({
                    "agency_name": reservoir.agency_name,
                    "frl": reservoir.frl,
                    "live_cap_frl": reservoir.live_cap_frl,
                    "level": reservoir.level,
                    "current_live_storage": reservoir.current_live_storage,
                    "month": reservoir.month,
                })

            
            return JsonResponse(reservoirs_data, safe=False)

        except State.DoesNotExist:
            return JsonResponse({"error": "State not found"}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
        


def reservoirs_five_years(request, state_id, year, name, dist_name):
    if request.method == 'GET':
        try:
            state = get_object_or_404(State, id=state_id)
            years_found = set()  
            current_year = year  
            min_year = 2000  
            final_reservoirs = []
            
            while len(years_found) < 5:
                if current_year < min_year:
                    break
                    
                reservoir = Reservoir.objects.filter(
                    state=state,
                    name__icontains=name,
                    district__icontains=dist_name,
                    year=current_year
                ).first()  
                
                if reservoir and current_year not in years_found:
                    final_reservoirs.append(reservoir) 
                    years_found.add(current_year)  
                
                current_year -= 1  

           
            data = [  
                {
                    "agency_name": reservoir.agency_name,
                    "frl": reservoir.frl,
                    "live_cap_frl": reservoir.live_cap_frl,
                    "level": reservoir.level,
                    "current_live_storage": reservoir.current_live_storage,
                    "month": reservoir.month,
                    "year": reservoir.year,  
                } for reservoir in final_reservoirs
            ]

            return JsonResponse(data, safe=False)

        except State.DoesNotExist:
            return JsonResponse({'error': 'State not found'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
