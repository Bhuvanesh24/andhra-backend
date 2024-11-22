from django.db import models
from forecast.models import State
# Create your models here.
class Reservoir(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    district = models.CharField(max_length=100)  
    name = models.CharField(max_length=255)  
    agency_name = models.CharField(max_length=255)  
    frl = models.FloatField()  
    live_cap_frl = models.FloatField() 
    level = models.FloatField() 
    current_live_storage = models.FloatField()
    year = models.IntegerField()  
    month = models.IntegerField()  


    def __str__(self):
        return f"{self.name} - {self.state}"
