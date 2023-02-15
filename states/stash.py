from aiogram.dispatcher.filters.state import StatesGroup, State


class Stash(StatesGroup):
    photo = State()
    http = State()
    music = State()