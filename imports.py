# самописное
import dbModel
import openaiModel
import secret_keys
from states import Stash
from states import defs

# стандарт либрариес
import requests
import asyncio
import time

# паблик либрариес
import yandex_music

import googletrans
import openai
import aiogram
import aiogram.bot.api
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.exceptions import Throttled
from aiogram.dispatcher import FSMContext, DEFAULT_RATE_LIMIT
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types.message import ContentType