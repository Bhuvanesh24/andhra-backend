from django.urls import path
from .views import *


urlpatterns = [
    path("get-scenario-data",get_data,name='get_scenario-datas'),
]