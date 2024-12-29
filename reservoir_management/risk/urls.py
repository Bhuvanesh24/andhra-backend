from django.urls import path
from .views import *


urlpatterns = [
    path("get-risk/<int:district_id>/<int:year>",get_data,name='get_risk_datas')
]