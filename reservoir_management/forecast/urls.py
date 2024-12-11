from django.urls import path
from .views import *

urlpatterns = [
    path('test/',test,name='test'),
    path('get-districts/',get_dist,name='get-dist'),
    path('get-evapo/<int:district_id>/<int:year>/',get_evaporation,name='get-evap'),
    path('get-usage/<int:district_id>/<int:year>/',get_usage,name="water_usage"),
    path('get-rainfall/<int:district_id>/<int:year>/',get_rainfall,name="get_rainfall"),
    path('predict-usage/<int:district_id>/<int:year>/',get_predictions_usage, name='usage-predict'),
    path('predict-luc/<int:district_id>/<int:year>/',get_predictions_luc,name='luc-predict'),
    path('get_landuse/<int:district_id>/<int:year>/', get_landuse, name='landuse-detail'),
    path('get-factors/<int:district_id>/<int:year>/',get_factors,name='factors'),
    path('retrain/',retrain_and_update_data,name='retrain_model'),
    # path('get_population/<int:year>/', get_population, name='get-population'),
]