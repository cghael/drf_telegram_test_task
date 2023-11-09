from django.db import models


class Weather(models.Model):
    city = models.CharField(max_length=100, unique=True)
    temperature = models.FloatField(blank=True, null=True)
    pressure = models.FloatField(blank=True, null=True)
    wind_speed = models.FloatField(blank=True, null=True)
    lat = models.FloatField()
    lon = models.FloatField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Погода {self.city}'
