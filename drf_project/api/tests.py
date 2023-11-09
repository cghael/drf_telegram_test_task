from datetime import datetime, timedelta

from django.urls import reverse
from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch

from weather.models import Weather


class WeatherAPITests(APITestCase):
    @patch('weather.views.Dadata.suggest')
    @patch('weather.views.requests.get')
    def test_get_weather_success(self, mock_requests_get, mock_dadata_suggest):
        """
        Объект Weather создается в базе с нужными полями и данными.
        """
        mock_dadata_suggest.return_value = [
            {'data': {'geo_lat': '10', 'geo_lon': '20'}}
        ]
        mock_requests_get.return_value.status_code = status.HTTP_200_OK
        values_from_yandex = {'temp': 10, 'wind_speed': 5, 'pressure_mm': 760}
        mock_requests_get.return_value.json.return_value = {
            'fact': values_from_yandex
        }
        objects_before_request = Weather.objects.count()

        url = reverse('city-weather')
        response = self.client.get(url, {'city': 'Moscow'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Weather.objects.count(), objects_before_request + 1)
        self.assertEqual(response.data['temperature'],
                         values_from_yandex['temp'])
        self.assertEqual(response.data['pressure'],
                         values_from_yandex['pressure_mm'])
        self.assertEqual(response.data['wind_speed'],
                         values_from_yandex['wind_speed'])

    @patch('weather.views.Dadata.suggest')
    @freeze_time("2023-11-09 12:00:00")
    def test_get_weather_calls_api_once_within_30_minutes(
            self, mock_dadata_suggest
    ):
        """
        При повторном запросе с тем же городом менее чем через 30 минут,
        не происходит запроса к Яндекс АПИ и берутся данные из базы.
        """
        mock_dadata_suggest.return_value = [
            {'data': {'geo_lat': '10', 'geo_lon': '20'}}
        ]

        initial_time = datetime.now()

        with patch('weather.views.requests.get') as mock_requests_get:
            mock_requests_get.return_value.status_code = status.HTTP_200_OK
            mock_requests_get.return_value.json.return_value = {
                'fact': {'temp': 10, 'wind_speed': 5, 'pressure_mm': 760}
            }
            url = reverse('city-weather')
            response = self.client.get(url, {'city': 'Moscow'})

            initial_time = datetime.now() + timedelta(minutes=29)
            with freeze_time(initial_time):
                response_second_request = self.client.get(url,
                                                          {'city': 'Moscow'})
                mock_requests_get.assert_called_once()

            initial_time = datetime.now() + timedelta(minutes=31)
            with freeze_time(initial_time):
                response_third_request = self.client.get(url,
                                                          {'city': 'Moscow'})
                assert mock_requests_get.call_count == 2

    @patch('weather.views.Dadata.suggest')
    def test_get_weather_city_error(self, mock_dadata_suggest):
        """
        Возвращает ошибку 404 если названия города нет в сервисе dadata
        и не создает объект в базе.
        """
        mock_dadata_suggest.return_value = []

        objects_before_request = Weather.objects.count()
        url = reverse('city-weather')
        response = self.client.get(url, {'city': 'NonexistentCity'})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Weather.objects.count(), objects_before_request)
