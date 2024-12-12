from django.db import models

class District(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    

# class Population(models.Model):
#     district = models.ForeignKey(District,on_delete=models.CASCADE)
#     year = models.IntegerField(null=False)
#     total_population = models.FloatField(null=False)
    
#     def __str__(self) -> str:
#         return f"{self.year} - {self.total_population}"

class LandusePast(models.Model):
    built_up = models.FloatField()
    agriculuture = models.FloatField()
    forest = models.FloatField()
    wasteland = models.FloatField()
    wetlands = models.FloatField()
    waterbodies = models.FloatField()
    year = models.IntegerField()
    district = models.ForeignKey(District,on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.district} - {self.year}"


    
class Usage(models.Model):
    year = models.IntegerField()
    month = models.IntegerField()
    rainfall = models.FloatField()
    inflow_states = models.FloatField()  # Inflow From Other States
    ground_water = models.FloatField()
    soil_moisture = models.FloatField()
    reservoir = models.FloatField()
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
    

class Evaporation(models.Model):
    district = models.ForeignKey(District,on_delete=models.CASCADE)
    evapo_transpiration = models.FloatField()
    year = models.IntegerField(null=False)
    month = models.IntegerField(null=False)
    total_evaporation = models.FloatField()

    def __str__(self):
        return f"{self.district} - {self.year}/{self.month}"
    
class Rainfall(models.Model):
    district = models.ForeignKey(District,on_delete=models.CASCADE)
    normal = models.FloatField()
    actual = models.FloatField()
    year = models.IntegerField(null = False)
    month = models.IntegerField(null = False)

    def __str__(self):
        return f"{self.district} - {self.year}/{self.month}"
    
class LucPredictionDist(models.Model):
    built_up = models.FloatField()
    agriculuture = models.FloatField()
    forest = models.FloatField()
    wasteland = models.FloatField()
    wetlands = models.FloatField()
    waterbodies = models.FloatField()
    year = models.IntegerField()
    district = models.ForeignKey(District,on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.district} - {self.year}"
     

class UsagePredictionDist(models.Model):
    district = models.ForeignKey(District,on_delete=models.CASCADE)
    year = models.IntegerField()
    month = models.IntegerField()
    rainfall = models.FloatField()
    inflow_states = models.FloatField()
    consumption = models.FloatField()
    irrigation = models.FloatField()
    industry = models.FloatField()
    domestic = models.FloatField()
    # built_up = models.FloatField(null=True)
    # agriculuture = models.FloatField(null=True)
    # forest = models.FloatField(null=True)
    # wasteland = models.FloatField(null=True)
    # wetlands = models.FloatField(null=True)
    # waterbodies = models.FloatField(null=True)

    def __str__(self):
        return f"{self.district} - {self.year}/{self.month}"