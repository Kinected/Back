# models.py

from django.db import models

class Temperature(models.Model):
    value = models.FloatField()
    recorded_at = models.DateTimeField(auto_now_add=True)