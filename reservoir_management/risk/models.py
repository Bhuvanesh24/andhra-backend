from django.db import models

class District(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class RiskData(models.Model):
    district = models.ForeignKey("forecast.District", on_delete=models.CASCADE)
    year = models.IntegerField()
    month = models.IntegerField(null=True)
    gross_capacity = models.FloatField()
    current_storage = models.FloatField()
    rainfall = models.FloatField(null=True) 
    evaporation = models.FloatField(null=True)
    SPEI=models.FloatField(null=True)
    water_usage=models.FloatField(null=True)
    irrigation=models.FloatField(null=True)
    industry=models.FloatField(null=True)
    domestic=models.FloatField(null=True)
    population=models.FloatField(null=True)
    description=models.TextField(null=True)
    risk_type=models.CharField()
    risk_score=models.FloatField(null=True)
   
    class Meta:
        indexes = [
            models.Index(fields=['reservoir', 'year']),
        ]
    def __str__(self):
        return f"{self.district} ({self.year})"