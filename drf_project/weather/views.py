import logging
import pytz
import requests
from datetime import datetime
from dadata import Dadata
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from http import HTTPStatus
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Weather
from .serializers import WeatherSerializer


class WeatherView(APIView):
    def __get_city_with_cords(self, city_name: str) -> Weather:
        dadata = Dadata(settings.GEOLOCATION_API_KEY,
                        settings.GEOLOCATION_SECRET_KEY)
        result = dadata.suggest('address', city_name, 1)

        if (
            not result
            or not result[0].get('data')
            or not result[0].get('data').get('geo_lat')
            or not result[0].get('data').get('geo_lon')
        ):
            raise ValueError('City name error')

        return Weather(
            city=city_name,
            lat=result[0].get('data').get('geo_lat'),
            lon=result[0].get('data').get('geo_lon')
        )

    def __get_weather_from_yadex(self, lat: str, lon: str):
        url = (f'https://api.weather.yandex.ru/v2/informers?'
               f'lat={lat}&lon={lon}&[lang=ru_RU]')
        headers = {
            'X-Yandex-API-Key': settings.YA_WEATHER_KEY
        }

        response = requests.get(url, headers=headers)
        if response.status_code != HTTPStatus.OK:
            logging.info(response.status_code)
            raise ConnectionError('Yandex API error')

        response = response.json().get('fact')
        return {'temp': response.get('temp'),
                'wind_speed': response.get('wind_speed'),
                'pressure_mm': response.get('pressure_mm')}

    def get(self, request):
        city_name = request.query_params.get('city')
        weather = Weather.objects.filter(city=city_name).first()
        created = False

        try:
            if not weather:
                weather = self.__get_city_with_cords(city_name)
                created = True

            if created or (
                (
                    datetime.now(pytz.UTC) - weather.updated_at
                ).total_seconds() > 1800
            ):
                ya_weather_data: dict = self.__get_weather_from_yadex(
                    weather.lat, weather.lon
                )
                weather.temperature = ya_weather_data['temp']
                weather.pressure = ya_weather_data['pressure_mm']
                weather.wind_speed = ya_weather_data['wind_speed']
                weather.save()

        except ValueError as error:
            logging.error(error)
            return Response(
                {'error': str(error)},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as error:
            logging.error(error)
            return Response(
                {'error': 'Oops. Try again later.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            WeatherSerializer(weather).data,
            status=status.HTTP_200_OK
        )
