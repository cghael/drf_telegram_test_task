import aiohttp
from http import HTTPStatus
from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards.for_weather import get_city_name_kb
from states.states import CityWeather


router = Router()


@router.message(StateFilter(None))
async def message_with_text(message: Message):
    await message.answer(
        'Простите, но я умею только сообщать о погоде. '
        'Чтобы узнать о погоде в каком-то городе, '
        'нажми на кнопку <b>"Узнать погоду"</b>',
        reply_markup=get_city_name_kb()
    )


@router.message(CityWeather.enter_city)
async def message_with_text(message: Message, state: FSMContext):
    city = message.text

    async with aiohttp.ClientSession() as session:
        url = f'http://127.0.0.1:8000/weather?city={city}'
        async with session.get(url) as response:
            if response.status == HTTPStatus.OK:
                data = await response.json()
                await message.answer(
                    f'Город {city}:\n'
                    f'Температура {int(data.get("temperature"))} градусов\n'
                    f'Давление {data.get("pressure")} мм рт.с.\n'
                    f'Скорость ветра {data.get("wind_speed")} м\\с',
                    reply_markup=get_city_name_kb()
                )
            elif response.status == HTTPStatus.NOT_FOUND:
                await message.answer(
                    f'Попробуйте ввести другое название города.',
                    reply_markup=get_city_name_kb()
                )
            else:
                await message.answer(
                    f'Упс, произошла ошибка на сервере. Попробуйте позже',
                    reply_markup=get_city_name_kb()
                )
    await state.clear()
