from django.urls import path

from weather.views import WeatherView


urlpatterns = [
    path('weather/', WeatherView.as_view(), name='city-weather')
]