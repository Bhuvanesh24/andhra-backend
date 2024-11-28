from django.contrib import admin
from django.urls import path
from .views import *
urlpatterns = [
    path('get-all-reservoirs/<int:district_id>/',reservoirs_by_districts,name='get-all-reservoirs'),
    path('get-reservoir-by-id/<int:reservoir_id>/<int:year>',reservoir_by_id,name='get-reservoir-by-id'),
    path('get-reservoir-by-id-five/<int:reservoir_id>/<int:year>',reservoir_by_id_five,name='get-reservoir-by-id-five'),
    path('get-reservoir-prediction/<int:reservoir_id>/<int:year>',reservoir_prediction,name="get_reservoir_prediction"),
    # path('reservoirs/<int:state_id>/<int:year>/<str:name>/<str:dist_name>/', reservoirs_by_name_dist,name='reservoirs_by_name_dist'),
    # path('reservoir-five/<int:state_id>/<int:year>/<str:name>/<str:dist_name>/',reservoirs_five_years,name='reservoir_five_years'),
]