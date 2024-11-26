from django.urls import path
from .views import *

urlpatterns = [
    path('test/',test,name='test'),
    path('get-districts/',get_dist,name='get-dist'),
    # path('predict/', predict_usage, name='forecast-predict'),
    path('get_landuse/<int:year>/', get_landuse, name='landuse-detail'),
    # path('get_population/<int:year>/', get_population, name='get-population'),
    # path('get_usage/<int:district_id>/<int:year>/', water_usage, name='usage'),
]