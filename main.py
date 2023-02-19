# самописное
import dbModel
import openaiModel
import secret_keys
from states import Stash
from states import defs

# стандарт либрариес
import requests
import logging
import asyncio
import time

# паблик либрариес
import yandex_music

import googletrans

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


PLAYLIST_SIZE = defs.PLAYLIST_SIZE

logging.basicConfig(level=logging.INFO)
bot = aiogram.Bot(token=secret_keys.telegram)  # создаем бота
dispatcher = aiogram.Dispatcher(bot, storage=MemoryStorage())  # что это
PRICE = aiogram.types.LabeledPrice(
    label="Подписка на 1 месяц", amount=500*100)  # что это

cancel = False


def rate_limit(limit: int, key=None):
    """
    Decorator for configuring rate limit and key in different functions.

    :param limit:
    :param key:
    :return:
    """

    def decorator(func):
        setattr(func, 'throttling_rate_limit', limit)
        if key:
            setattr(func, 'throttling_key', key)
        return func

    return decorator


class ThrottlingMiddleware(BaseMiddleware):
    """
    Simple middleware
    """

    def __init__(self, limit=DEFAULT_RATE_LIMIT, key_prefix='antiflood_'):
        self.rate_limit = limit
        self.prefix = key_prefix
        super(ThrottlingMiddleware, self).__init__()

    async def on_process_message(self, message: types.Message, data: dict):
        """
        This handler is called when dispatcher receives a message

        :param message:
        """
        # Get current handler
        handler = current_handler.get()

        # Get dispatcher from context
        dispatcher = aiogram.Dispatcher.get_current()
        # If handler was configured, get rate limit and key from handler
        if handler:
            limit = getattr(handler, 'throttling_rate_limit', self.rate_limit)
            key = getattr(handler, 'throttling_key',
                          f"{self.prefix}_{handler.__name__}")
        else:
            limit = self.rate_limit
            key = f"{self.prefix}_message"

        # Use Dispatcher.throttle method.
        try:
            await dispatcher.throttle(key, rate=limit)
        except Throttled as t:
            # Execute action
            await self.message_throttled(message, t)

            # Cancel current handler
            raise CancelHandler()

    async def message_throttled(self, message: types.Message, throttled: Throttled):
        """
        Notify user only on first exceed and notify about unlocking only on last exceed

        :param message:
        :param throttled:
        """
        handler = current_handler.get()
        dispatcher = Dispatcher.get_current()
        if handler:
            key = getattr(handler, 'throttling_key',
                          f"{self.prefix}_{handler.__name__}")
        else:
            key = f"{self.prefix}_message"

        # Calculate how many time is left till the block ends
        delta = throttled.rate - throttled.delta

        # Prevent flooding
        if throttled.exceeded_count <= 2:
            await message.reply('Слишком много запросов, скоро бот будет снова доступен для вас')

        # Sleep.
        await asyncio.sleep(delta)

        # Check lock status
        thr = await dispatcher.check_key(key)

        # If current message is not last with current key - do not send message
        if thr.exceeded_count == throttled.exceeded_count:
            await message.reply('Бот доступен')


@dispatcher.callback_query_handler(lambda c: c.data == 'btn_Yandex')
@rate_limit(5)
async def process_callback_button1(callback_query: aiogram.types.CallbackQuery):
    db.clearMusicPlayer(callback_query.from_user.id)
    db.addMusicPlayer(callback_query.from_user.id, 'YandexMusic')
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Вы приобрели Premium!! Спасибо за доверие, выбранная площадка: Яндекс музка\n"
                                                        "теперь вы можете получать ссылки на плейлисты созднанные под ваше настроение")


@dispatcher.callback_query_handler(lambda c: c.data == 'btn_VK')
@rate_limit(5)
async def process_callback_button1(callback_query: aiogram.types.CallbackQuery):
    db.clearMusicPlayer(callback_query.from_user.id)
    db.addMusicPlayer(callback_query.from_user.id, 'VkMusic')
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Вы приобрели Premium!! Спасибо за доверие, выбранная площадка: Вконтакте музка\n"
                           "теперь вы можете получать ссылки на плейлисты созднанные под ваше настроение")


@dispatcher.callback_query_handler(lambda c: c.data == 'contiune_generate_music')
@rate_limit(5)
async def process_callback_button1(callback_query: aiogram.types.CallbackQuery):
    await music_handler(callback_query)
    await callback_query.message.edit_reply_markup(reply_markup=None)


@dispatcher.callback_query_handler(lambda c: c.data == 'ru')
@rate_limit(5)
async def process_callback_button1(callback_query: aiogram.types.CallbackQuery):
    btn_eng = aiogram.types.InlineKeyboardButton(
        text="Aнглийский",
        callback_data="eng"
    )
    btn_rus = aiogram.types.InlineKeyboardButton(
        text="Руссский",
        callback_data="ru"
    )
    keyboard = aiogram.types.InlineKeyboardMarkup().add(btn_eng, btn_rus)
    db.switchLang(callback_query.from_user.id, "ru")
    await bot.send_message(callback_query.from_user.id, "Готово! Теперь ответы бота будут на русском языке,"
                           "вы можете попросить его решить вам домашку, написать сочинение, или рассказать о чем-то простыми словами\n"
                           " eсли хотите изменить язык, то выбирите другой язык "
                           "в всплывающей клавиатуре или перейдите в /settings", reply_markup=keyboard)


@dispatcher.callback_query_handler(lambda c: c.data == 'eng')
@rate_limit(5)
async def process_callback_button1(callback_query: aiogram.types.CallbackQuery):
    btn_eng = aiogram.types.InlineKeyboardButton(
        text="Aнглийский",
        callback_data="eng"
    )
    btn_rus = aiogram.types.InlineKeyboardButton(
        text="Руссский",
        callback_data="ru"
    )
    keyboard = aiogram.types.InlineKeyboardMarkup().add(btn_eng, btn_rus)
    db.switchLang(callback_query.from_user.id, "en")
    await bot.send_message(callback_query.from_user.id, "Готово! Теперь ответы бота будут на английском языке,"
                           "вы можете попросить бота прислать вам скрипт на любом языке программирования или просто получать ответы на ангийском языке.\n"
                           " Если хотите изменить язык, то выбирите другой язык "
                           "в всплывающей клавиатуре или перейдите в /settings", reply_markup=keyboard)


@dispatcher.callback_query_handler(lambda c: c.data == 'cancel', state=Stash.music)
async def process_callback_button1(callback_query: aiogram.types.CallbackQuery, state: FSMContext):
    global cancel
    cancel = True
    await callback_query.answer("Запрос на генерацию музыки отменен")
    await callback_query.message.delete()
    await state.finish()


@dispatcher.callback_query_handler(lambda c: c.data == 'Add_message_to_previos')
async def process_callback_button1(callback_query: aiogram.types.CallbackQuery):
    db.updateMemory(callback_query.from_user.id,
                    db.getLastMessage(callback_query.from_user.id))
    await callback_query.answer("Уточнить")
    await callback_query.message.edit_reply_markup(reply_markup=None)


@dispatcher.callback_query_handler(lambda c: c.data == 'photo_one_more')
async def process_callback_button1(callback_query: aiogram.types.CallbackQuery):
    await photo_generete(callback_query)
    await callback_query.message.edit_reply_markup(reply_markup=None)


@dispatcher.message_handler(commands=['pay'])
async def buy(message: aiogram.types.Message):
    config = secret_keys.paymentTextToken
    if config.split(':')[1] == 'TEST':
        await bot.send_message(message.chat.id, "Тестовый платеж!!!")

    await bot.send_invoice(message.chat.id,
                           title="Подписка на бота",
                           description="Активация подписки на бота на 1 месяц",
                           provider_token=config,
                           currency="rub",
                           photo_url="https://www.aroged.com/wp-content/uploads/2022/06/Telegram-has-a-premium-subscription.jpg",
                           photo_width=416,
                           photo_height=234,
                           photo_size=416,
                           is_flexible=False,
                           prices=[PRICE],
                           start_parameter="one-month-subscription",
                           payload="test-invoice-payload")


@dispatcher.pre_checkout_query_handler(lambda query: True)
async def pre_checkout_query(pre_checkout_q: aiogram.types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


# successful payment
@dispatcher.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: aiogram.types.Message):
    db.updateSubscriptionType(message.from_user.id,
                              newSubscriptionType=dbModel.SUBSCRIPTION_PREM)

    payment_info = message.successful_payment.to_python()
    btn_Yandex = aiogram.types.InlineKeyboardButton(
        "Яндекс Музыка", callback_data='btn_Yandex')
    btn_VK = aiogram.types.InlineKeyboardButton(
        "Вк Музыка", callback_data='btn_VK')
    keyboard = aiogram.types.InlineKeyboardMarkup().add(btn_Yandex, btn_VK)
    for k, v in payment_info.items():
        print(f"{k} = {v}")

    await bot.send_message(message.chat.id,
                           f"Платеж на сумму {message.successful_payment.total_amount // 100} {message.successful_payment.currency} прошел успешно!!!\n"
                           f"Выберите площадку на которой вы слушаете музыку", reply_markup=keyboard)


@dispatcher.message_handler(Command('photo'))
@rate_limit(5, key="photo")
async def photo_generete(message):
    if db.getUser(message.from_user.id)["subscriptionEndDate"] < time.time():
        db.updateSubscriptionType(
            message.from_user.id, dbModel.SUBSCRIPTION_FREE)

    if db.getUser(message.from_user.id)['subscriptionType'] == dbModel.SUBSCRIPTION_PREM:

        await bot.send_message(message.from_user.id, "Пришлите описание картинки")
        await Stash.photo.set()
    else:
        await message.answer("Для того чтобы генерировать картинки, вы должны стать Premium пользователем"
                             "для этого пришлите команду /pay")


@dispatcher.message_handler(Command("change_musicplayer"))
async def change_musicplayer(message):
    dt = {"YandexMusic": "VkMusic", "VkMusic": "YandexMusic"}
    player = dt[db.getUser(message.from_user.id)['musicPlayers']]
    db.removeMusicPlayer(message.from_user.id, db.getUser(
        message.from_user.id)['musicPlayers'])
    db.addMusicPlayer(message.from_user.id, player)

    print(dt[db.getUser(message.from_user.id)['musicPlayers']])
    dt = {"YandexMusic": "Яндекс музыку", "VkMusic": "Вк Музыку"}
    await message.answer(f"Плеер успешно сменен на {dt[db.getUser(message.from_user.id)['musicPlayers']]}")


@dispatcher.message_handler(Command("change_lang"))
async def change_lang(message):
    dt = {'en': 'ru', 'ru': 'en'}
    db.switchLang(message.from_user.id, dt[db.getLang(message.from_user.id)])
    dt = {'ru': "русский", "en": 'английский'}
    await message.answer(f"Язык успешно сменен на {dt[db.getLang(message.from_user.id)]}")


@dispatcher.message_handler(Command('settings'))
async def settings(message):
    await message.answer("для смены языка нажмите /change_lang\n"
                         "для смены музыкальной площадки нажмите /change_musicplayer")


@dispatcher.message_handler(state=Stash.photo)
@rate_limit(10)
async def photo_answer(message: aiogram.types.Message, state: FSMContext):
    photo = message.text
    """для ожидания ботом сообщения"""
    await state.update_data(photo=photo)
    res = translator.translate(message.text, dest='en', src='ru')
    btn_photo = aiogram.types.InlineKeyboardButton(
        "Сгенерировать еще фото", callback_data='photo_one_more')
    keyboard = aiogram.types.InlineKeyboardMarkup().add(btn_photo)
    imageUrl = openaiModel.generatePhoto(res.text)
    if imageUrl == None:
        await message.answer("Извините, сейчас мы не можем сгенерировать картинку по вашему запросу")
    else:
        await bot.send_photo(message.from_user.id, imageUrl, reply_markup=keyboard)

    await state.finish()


@dispatcher.message_handler(commands=['start'])
@rate_limit(5, key='start')
async def welcome(message):

    btn_eng = aiogram.types.InlineKeyboardButton(
        text="Aнглийский",
        callback_data="eng"
    )
    btn_rus = aiogram.types.InlineKeyboardButton(
        text="Руссский",
        callback_data="ru"
    )
    keyboard = aiogram.types.InlineKeyboardMarkup().add(btn_eng, btn_rus)
    db.addUser(message.from_user.id, message.from_user.username,
               subscriptionType=dbModel.SUBSCRIPTION_PREM)
    db.updateSubscriptionEndDate(message.from_user.id, 2999999999.999)
    await message.answer("➖Здравствуй, я твой новый друг, меня зовут Ботти🙃."
                         "➖В меня загружен весь интернет, поэтому я знаю абсолютно все, до чего в данный момент дошло человечество🌚."
                         "И я могу стать твоим личным помощником🔥."
                         "Тебе нужно лишь сформулировать запрос."
                         "➖ Общайся со мной как с обычным человеком😉, чем подробнее будет запрос, тем шире и понятнее я смогу дать тебе ответ.", reply_markup=keyboard)


@dispatcher.message_handler(Command('music'))
@rate_limit(5, key="music")
async def music_handler(message):
    if db.getUser(message.from_user.id)["subscriptionEndDate"] < time.time():
        db.updateSubscriptionType(
            message.from_user.id, dbModel.SUBSCRIPTION_FREE)
    if db.getUser(message.from_user.id)['subscriptionType'] == dbModel.SUBSCRIPTION_PREM:
        btn1 = aiogram.types.InlineKeyboardButton(
            "Сгенерировать еще", callback_data='contiune_generate_music')
        btn2 = aiogram.types.InlineKeyboardButton(
            "Отменить", callback_data="cancel")
        keyboard = aiogram.types.InlineKeyboardMarkup().add(btn1, btn2)
        await bot.send_message(message.from_user.id, "Напишите что бы вы хотели послушать, не бойтесь проявлять фантазию", reply_markup=keyboard)
        await Stash.music.set()
    else:
        await message.answer("Для того чтобы генерировать картинки вы должны стать Premium пользователем"
                             "для этого пришлите команду /pay")


@dispatcher.message_handler(state=Stash.music)
@rate_limit(10)
async def music_answer(message: aiogram.types.Message, state: FSMContext):
    global cancel
    if cancel:
        cancel = False
        return
    print(db.getUsername(message.from_user.id), "/music", message.text)
    status_message = await bot.send_message(message.from_user.id, "Думаю что подходит под ваше описание")
    album = client.users_playlists_create(title=message.text)
    songsDict = {}
    while songsDict == {}:
        textEN = translator.translate(
            str(message.text), src='ru', dest='en').text
        await state.update_data(music=message.text)
        print(textEN)
        rawText = openaiModel.generateText(
            f'write me {PLAYLIST_SIZE} {textEN} songs in format author - title', max_tokens=2048)

        songsDict = defs.parseTracks(rawText)
        print(songsDict)
    tracksAdded = 0
    tracksAll = PLAYLIST_SIZE
    await status_message.edit_text(f"Делаю плейлист|{str(int(tracksAdded/tracksAll*100))}%")
    i = 0
    id = 507315
    for author in songsDict:
        if id != 507315:
            break
        for track in songsDict[author]:
            try:
                id = client.search(track+" "+author).best.result.albums[0].id
                break
            except:
                pass

    for author in songsDict:
        for track in songsDict[author]:
            try:
                yandexMusicTrack = client.search(track+" "+author).best.result
                client.users_playlists_insert_track(
                    kind=album.kind,
                    track_id=yandexMusicTrack.id,
                    album_id=id,
                    at=i,
                    revision=client.users_playlists(kind=album.kind).track_count+1)
                i += 1
                tracksAdded += 1
            except:
                tracksAll -= 1
                await message.answer("Хочу добавить вам в плейлист {} - {}, но на Яндекс Музыке его нету".format(author, track))
                await state.finish()

            await status_message.edit_text(f"Делаю плейлист|{str(int(tracksAdded/tracksAll*100))}%")
    url = f'https://music.yandex.ru/users/g0sha5063/playlists/{album.kind}'

    await status_message.delete()
    await message.answer(f"Ваш плейлист готов: {url}")

    await state.finish()


@dispatcher.message_handler(content_types=['text'])
@rate_limit(5)
async def text_handler(message):
    # добавляет username
    if message.text == "Сгенерировать музыку":
        await music_handler(message)
        return
    if message.text == "Сгенерировать фото":
        await photo_generete(message)
        return
    music = types.KeyboardButton("Сгенерировать музыку")
    photo = types.KeyboardButton("Сгенерировать фото")
    key = types.ReplyKeyboardMarkup(resize_keyboard=True).add(music, photo)
    db.updateUsername(message.from_user.id, message.from_user.username)

    result = translator.translate(str(message.text), src='ru', dest='en')

    response = openaiModel.generateText(result.text)

    last_message = result.text
    db.setLastMessage(message.from_user.id, last_message + " "+response)

    if db.getLang(message.from_user.id) == "ru":
        response = translator.translate(response, src='en', dest='ru').text
    await message.answer(response, reply_markup=key)

if __name__ == '__main__':

    dispatcher.middleware.setup(ThrottlingMiddleware())
    translator = googletrans.Translator()  # переводчик
    client = yandex_music.Client(
        secret_keys.yandexMusic).init()  # клиент яндекс музыки
    db = dbModel.DBModel()  # даза банных
    db.connect()
    aiogram.executor.start_polling(
        dispatcher, skip_updates=True)  # веч цикл телеграм бота
    db.close()
