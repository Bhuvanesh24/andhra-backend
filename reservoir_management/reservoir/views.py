import requests
from django.http import JsonResponse
from forecast.models import District
from .models import *
from datetime import datetime




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

