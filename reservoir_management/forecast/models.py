from django.db import models


class District(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    

# class Population(models.Model):
#     district = models.ForeignKey(District,on_delete=models.CASCADE)
#     year = models.IntegerField(null=False)
#     total_population = models.FloatField(null=False)
#     urban_population = models.FloatField(null=False)
#     rural_population = models.FloatField(null=False)
    
#     def __str__(self) -> str:
#         return f"{self.year} - {self.total_population}"

class LandUse(models.Model):
    year = models.IntegerField(null=False)
    forest_use = models.FloatField()
    barren_use = models.FloatField()
    fallow_use = models.FloatField()
    cropped_use = models.FloatField()
    other_use = models.FloatField()
    
    def __str__(self) -> str:
        return f"{self.state} - {self.year}"


    
class Usage(models.Model):
    year = models.IntegerField()
    month = models.IntegerField()
    rainfall = models.FloatField()
    inflow_states = models.FloatField()  # Inflow From Other States
    ground_water = models.FloatField()
    soil_moisture = models.FloatField()
    reservoir = models.ForeignKey("reservoir.Reservoir", on_delete=models.PROTECT)
    major = models.FloatField()
    medium = models.FloatField()
    mi_tanks = models.FloatField()  # MI Tanks (Geotagged)
    evapo_trans = models.FloatField()  # Evapo-99transpiration
    outflow = models.FloatField()
    river = models.FloatField()
    micro_basin = models.FloatField()
    consumption = models.FloatField()
    irrigation = models.FloatField()
    industry = models.FloatField()
    domestic = models.FloatField()
    subsurface_outflow = models.FloatField()  # Surface and SubSurface Outflow
    district = models.ForeignKey(District,on_delete=models.CASCADE)  

    def __str__(self):
        return f"{self.district} - {self.year}/{self.month}"