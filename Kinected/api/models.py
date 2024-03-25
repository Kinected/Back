from django.db import models

class TemperatureData(models.Model):
    temperature = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)