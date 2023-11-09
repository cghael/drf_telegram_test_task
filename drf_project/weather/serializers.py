from rest_framework import serializers

from .models import Weather


class WeatherSerializer(serializers.ModelSerializer):
    city = serializers.CharField(max_length=100, required=True)

    class Meta:
        model = Weather
        fields = ('city', 'temperature', 'pressure', 'wind_speed')
