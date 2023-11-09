import logging
import pytz
import requests
from datetime import datetime
from dadata import Dadata
from django.conf import settings
from http import HTTPStatus
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Weather
from .serializers import WeatherSerializer


class WeatherView(APIView):
    def __get_city_cords(self, city_name: str) -> dict:
        dadata = Dadata(settings.GEOLOCATION_API_KEY,
                        settings.GEOLOCATION_SECRET_KEY)
        result = dadata.suggest('address', city_name, 1)
        print(result)
        print(result[0].get('data'))
        if not result:
            raise ValueError('City name error')
        return {
            'lat': result[0].get('data').get('geo_lat'),
            'lon': result[0].get('data').get('geo_lon')
        }

    def __get_weather_from_yadex(self, lat: str, lon: str, lang: str):
        url = (f'https://api.weather.yandex.ru/v2/informers?'
               f'lat={lat}&lon={lon}&[lang={lang}]')
        headers = {
            'X-Yandex-API-Key': settings.YA_WEATHER_KEY
        }
        print(lat, lon)
        response = requests.get(url, headers=headers)
        print(response.status_code)
        print(response.json())
        if response.status_code != HTTPStatus.OK:
            logging.info(response.status_code)
            raise ConnectionError('Yandex API error')

        response = response.json()
        return {'temp': response['fact']['temp'],
                'wind_speed': response['fact']['wind_speed'],
                'pressure_mm': response['fact']['pressure_mm']}

    def get(self, request):
        city_name = request.query_params.get('city')
        weather, created = Weather.objects.get_or_create(city=city_name)

        if created or weather.temperature is None or (
            (datetime.now(pytz.UTC) - weather.updated_at).total_seconds() > 1800
        ):
            try:
                city_cords: dict = self.__get_city_cords(city_name)
                if not city_cords.get('lat') or not city_cords.get('lon'):
                    raise ValueError(f'City {city_name} cords not found')
                city_cords.update({'lang': 'ru_RU'})
                ya_weather_data: dict = self.__get_weather_from_yadex(
                    **city_cords
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
