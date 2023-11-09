from aiogram.fsm.state import State, StatesGroup


class CityWeather(StatesGroup):
    enter_city = State()
