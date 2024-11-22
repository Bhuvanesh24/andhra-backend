from django.contrib import admin
from django.urls import path,include
from .views import *
urlpatterns = [
    path('get-all-reservoirs/<int:state_id>/<int:year>',reservoirs_by_states,name='get-all-reservoirs'),
    path('reservoirs/<int:state_id>/<int:year>/<str:name>/<str:dist_name>/', reservoirs_by_name_dist,name='reservoirs_by_name_dist'),
    path('reservoir-five/<int:state_id>/<int:year>/<str:name>/<str:dist_name>/',reservoirs_five_years,name='reservoir_five_years'),
]