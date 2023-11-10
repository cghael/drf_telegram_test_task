from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from states.states import CityWeather


router = Router()


@router.callback_query(F.data == 'weather_value')
async def send_weather_value(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Введите название города')
    await callback.answer()
    await state.set_state(CityWeather.enter_city)
