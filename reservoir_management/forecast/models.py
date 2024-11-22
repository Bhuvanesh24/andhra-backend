from django.db import models

class State(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class Usage(models.Model):
    year = models.IntegerField(null=False)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    domestic_use = models.FloatField(null=False)
    industrial_use = models.FloatField(null=False)
    irrigation_use = models.FloatField(null=False)

    def __str__(self):
        return f"{self.state} - {self.year}"

class Population(models.Model):
    year = models.IntegerField(null=False)
    total_population = models.FloatField(null=False)
    urban_population = models.FloatField(null=False)
    rural_population = models.FloatField(null=False)
    
    def __str__(self) -> str:
        return f"{self.year} - {self.total_population}"

class LandUse(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    year = models.IntegerField(null=False)
    forest_use = models.FloatField()
    barren_use = models.FloatField()
    fallow_use = models.FloatField()
    cropped_use = models.FloatField()
    other_use = models.FloatField()
    
    def __str__(self) -> str:
        return f"{self.state} - {self.year}"

    class Evaporation(models.Model):
        state = models.ForeignKey(State, on_delete=models.CASCADE)
        district = models.CharField(max_length=200)
        year = models.IntegerField(null=False)
        month = models.IntegerField(null=False)
        level = models.FloatField(null=False)
        volume = models.FloatField(null = False)

        def __str__(self) -> str:
            return f"{self.state} - {self.year}"