# Simple Django REST API + Telegram bot
### Django REST API

Rest API has one endpoint `/weather/city=<city_name>` from which you can get data on temperature, pressure and wind speed in a specific city.

We receive weather data from Yandex.Weather, and if a request comes to a city for which data was already received less than 30 minutes ago, then a repeated request is not sent to the Yandex API.

Data on city coordinates for the Yandex API are obtained by the name of the city from the DaData.ru service

### Telegram bot

Telegram bot has only one function. When you click the button, it asks you to enter the name of the city. After that, he contacts the API and displays a message about the weather in this city.
