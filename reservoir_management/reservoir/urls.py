from django.contrib import admin
from django.urls import path
from .views import *
urlpatterns = [
    path('get-all-reservoirs/<int:district_id>/',reservoirs_by_districts,name='get-all-reservoirs'),
    path('get-reservoir-by-id/<int:reservoir_id>/<int:year>',reservoir_by_id,name='get-reservoir-by-id'),
    # path('get-reservoir-by-id-five/<int:reservoir_id>/<int:year>',reservoir_by_id_five,name='get-reservoir-by-id-five'),
    path('get-reservoir-prediction/<int:reservoir_id>/<int:year>',reservoir_prediction,name="get_reservoir_prediction"),
    path('get-score',calculate_reservoir_health_score,name='score'),
    path('get-score-data',get_age_siltation,name='get-age-data'),
    path('model-retrain/',retrain_and_update_data,name='retrain_model'),
    
]