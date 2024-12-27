from aiogram.fsm.state import StatesGroup, State


class states(StatesGroup):
    LANGUAGE = State()
    FIRSTNAME = State()
    LASTNAME = State()
    PHOTO = State()