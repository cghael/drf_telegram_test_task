# Simple Django REST API + Telegram bot
### Django REST API

Rest API has one endpoint `/weather/city=<city_name>` from which you can get data on temperature, pressure and wind speed in a specific city.

We receive weather data from Yandex.Weather, and if a request comes to a city for which data was already received less than 30 minutes ago, then a repeated request is not sent to the Yandex API.

Data on city coordinates for the Yandex API are obtained by the name of the city from the DaData.ru service

### Telegram bot

Telegram bot has only one function. When you click the button, it asks you to enter the name of the city. After that, he contacts the API and displays a message about the weather in this city.

## Startup instructions

1. Clone the repository
```commandline
git clone https://github.com/cghael/drf_telegram_test_task.git

cd drf_telegram_test_task
```
2. Install dependencies
```commandline
pip install -r requirements.txt
```
### Django server
To start Django server, go to the folder `drf_project`.
And do the migrations
```commandline
python manage.py migrate
```
Then start the server
```commandline
python manage.py runserver
```
### Telegram bot
To launch the bot, go to the folder `telegram_bot`.
And start the bot
```commandline
python bot.py
```
### TODO
1. Dockerfile and docker-compose
