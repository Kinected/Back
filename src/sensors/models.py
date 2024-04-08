from django.db import models

class SensorsData(models.Model):
    temperature = models.FloatField()
    humidity = models.FloatField()
    luminosity = models.FloatField()