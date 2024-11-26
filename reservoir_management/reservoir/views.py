from django.shortcuts import render
import requests
from django.http import JsonResponse
from forecast.models import District
from .models import *
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist




def reservoirs_by_districts(request, district_id):
    if request.method == 'GET':
        try:
            # Fetch the district based on the provided district_id
            district = District.objects.get(id=district_id)
            
            # Fetch the reservoirs for the specified district
            reservoirs = Reservoir.objects.filter(district=district)
            
            # If no reservoirs exist for the district, return an error message
            if not reservoirs.exists():
                return JsonResponse({"error": "No reservoirs found for the given district."}, status=404)

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
                return JsonResponse({"error": "No reservoir data found for the given year."}, status=404)

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
                return JsonResponse({"error": "No data available for the selected year or earlier."}, status=404)

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
                return JsonResponse({"error": "No reservoir data found for the past 5 years."}, status=404)

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

# def reservoirs_by_name_dist(request, state_id, year, name, dist_name):
#     if request.method == 'GET':
#         try:
#             state = get_object_or_404(State, id=state_id)
#             reservoirs = Reservoir.objects.filter(
#                 state=state,
#                 year=year,
#                 name__icontains=name,  
#                 district__icontains=dist_name 
#             )

#             reservoirs_data = []
#             for reservoir in reservoirs:
#                 reservoirs_data.append({
#                     "agency_name": reservoir.agency_name,
#                     "frl": reservoir.frl,
#                     "live_cap_frl": reservoir.live_cap_frl,
#                     "level": reservoir.level,
#                     "current_live_storage": reservoir.current_live_storage,
#                     "month": reservoir.month,
#                 })

            
#             return JsonResponse(reservoirs_data, safe=False)

#         except State.DoesNotExist:
#             return JsonResponse({"error": "State not found"}, status=200)
#         except Exception as e:
#             return JsonResponse({"error": str(e)}, status=500)
        


# def reservoirs_five_years(request, state_id, year, name, dist_name):
#     if request.method == 'GET':
#         try:
#             state = get_object_or_404(State, id=state_id)
#             years_found = set()  
#             current_year = year  
#             min_year = 2000  
#             final_reservoirs = []
            
#             while len(years_found) < 5:
#                 if current_year < min_year:
#                     break
                    
#                 reservoir = Reservoir.objects.filter(
#                     state=state,
#                     name__icontains=name,
#                     district__icontains=dist_name,
#                     year=current_year
#                 ).first()  
                
#                 if reservoir and current_year not in years_found:
#                     final_reservoirs.append(reservoir) 
#                     years_found.add(current_year)  
                
#                 current_year -= 1  

           
#             data = [  
#                 {
#                     "agency_name": reservoir.agency_name,
#                     "frl": reservoir.frl,
#                     "live_cap_frl": reservoir.live_cap_frl,
#                     "level": reservoir.level,
#                     "current_live_storage": reservoir.current_live_storage,
#                     "month": reservoir.month,
#                     "year": reservoir.year,  
#                 } for reservoir in final_reservoirs
#             ]

#             return JsonResponse(data, safe=False)

#         except State.DoesNotExist:
#             return JsonResponse({'error': 'State not found'}, status=200)
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)
