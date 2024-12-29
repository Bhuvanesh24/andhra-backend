from django.shortcuts import render
from django.http import JsonResponse
from .models import RiskData
from forecast.models import District

def get_data(request, district_id, year, month):
    try:
        district = District.objects.get(id=district_id)
        risk_data = RiskData.objects.filter(district=district, year=year, month=month)

        # Serialize the data
        serialized_data = [
            {
                "district": str(risk.district),  # Convert ForeignKey to string representation
                "year": risk.year,
                "month": risk.month,
                "risk_type": risk.risk_type,
                "description": risk.description,
                "causes": risk.causes,
                "mitigation": risk.mitigation,
                "risk_score": risk.risk_score,
                "factors": risk.factors,
            }
            for risk in risk_data
        ]

        return JsonResponse({"response": serialized_data}, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, safe=False)
