from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from keyboards.for_weather import get_city_name_kb


router = Router()


@router.message(Command('start'))
async def cmd_start(message: Message):
    await message.answer(
        'Привет! Если хочешь узнать о погоде в каком-то городе, '
        'нажми на кнопку <b>"Узнать погоду"</b>',
        reply_markup=get_city_name_kb()
    )
