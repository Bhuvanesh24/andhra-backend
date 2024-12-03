from django.urls import path
from .views import *


urlpatterns = [
    path("get-scenario-data/<int:district_id>/<int:year>/",get_data,name='get_scenario-datas'),
    path("get-simulation/",get_simulator,name='simulation'),
]