from django.db import models


class RiskData(models.Model):
    district = models.ForeignKey("forecast.District", on_delete=models.CASCADE)
    year = models.IntegerField()
    month = models.IntegerField(null=True)
    risk_type=models.TextField(null=True)
    description=models.TextField(null=True)
    causes = models.TextField(null=True)
    mitigation = models.TextField(null=True)
    risk_score=models.IntegerField()
    factors = models.TextField(null=True)
   
    class Meta:
        indexes = [
            models.Index(fields=['district', 'year']),
        ]
    def __str__(self):
        return f"{self.district} ({self.year})"