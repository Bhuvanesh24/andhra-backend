from django.db import models

# Create your models here.
class Reservoir(models.Model):
    name = models.CharField(max_length=200, default='Unknown')    
    district = models.ForeignKey("forecast.District", on_delete=models.CASCADE,null=True)  
    def __str__(self):
        return f"{self.name}"

class ReservoirData(models.Model):
    reservoir = models.ForeignKey(Reservoir, on_delete=models.CASCADE)  # ForeignKey to Reservoir
    basin = models.CharField(max_length=255)
    district = models.ForeignKey("forecast.District", on_delete=models.CASCADE)
    gross_capacity = models.FloatField()  # Assuming these values are numerical
    current_level = models.FloatField()
    current_storage = models.FloatField()
    flood_cushion = models.FloatField()
    inflow = models.FloatField()
    outflow = models.FloatField()
    year = models.IntegerField()  # Year as an integer
    month = models.IntegerField()  # Month as an integer (1-12)

    class Meta:
        indexes = [
            models.Index(fields=['reservoir', 'year']),  # Most important index for your query
        ]

    def __str__(self):
        return f"{self.reservoir.name} ({self.year}-{self.month})"
    
class ReservoirPrediction(models.Model):
    reservoir = models.ForeignKey(Reservoir, on_delete=models.CASCADE)
    district = models.ForeignKey("forecast.District", on_delete=models.CASCADE)
    year = models.IntegerField()
    gross_capacity = models.FloatField()
    current_storage = models.FloatField()
    rainfall = models.FloatField(null=True)
    evaporation = models.FloatField(null=True)
    month = models.IntegerField(null=True)
    class Meta:
        indexes = [
            models.Index(fields=['reservoir', 'year']),
        ]
    def __str__(self):
        return f"{self.reservoir.name} ({self.year})"
    

class ReservoirScore(models.Model):
    reservoir = models.ForeignKey(Reservoir, on_delete=models.CASCADE)
    year  = models.IntegerField()
    mean_storage = models.FloatField()
    flood_cushion = models.FloatField()
    rainfall = models.FloatField()
    evaporation = models.FloatField()
    population = models.BigIntegerField()
    age = models.IntegerField()
    siltation = models.FloatField()
    capacity = models.FloatField()
    score = models.FloatField()

    def __str__(self):
        return f"{self.reservoir.name} ({self.year})"