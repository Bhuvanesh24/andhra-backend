from django.urls import path
from .views import *


urlpatterns = [
    path("get-risk/<int:district_id>/<int:year>/<int:month>/",get_data,name='get_risk_datas')
]