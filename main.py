# не ебу зачем это надо но оставлю закоменченным
#IAM_TOKEN = 't1.9euelZqdz4yUx4nGnprJnpuLys-Omu3rnpWai8-Xzp6LnsmZkp3Lypubi87l8_dWR0Zg-e98dlgo_t3z9xZ2Q2D573x2WCj-.RAQQ7NC4zSty2vay61yg36WKBy9TDRjX6UPDove48DEdZnV0Hpe0ozPCc0jnAtpEhIXmgQ9WizNy6Xnh0WqpBA'
#folder_id = 'b1gr9n62s9oofoaj0cke'

# перенес логику openai в openaiModel.py

# сделал норм парсер треков parseTracks

# самописное
import dbModel
import openaiModel
import secret_keys
from states import Stash
from states import defs
# стандарт либрариес
import requests
import logging
import time

# паблик либрариес
import yandex_music

import googletrans

import aiogram
import aiogram.bot.api
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types.message import ContentType

logging.basicConfig(level=logging.INFO)
bot = aiogram.Bot(token=secret_keys.telegram)  # создаем бота
dispatcher = aiogram.Dispatcher(bot, storage=MemoryStorage())  # что это
PRICE = aiogram.types.LabeledPrice(
    label="Подписка на 1 месяц", amount=500*100)  # что это


@dispatcher.callback_query_handler(lambda c: c.data == 'btn_Yandex')
async def process_callback_button1(callback_query: aiogram.types.CallbackQuery):
    db.addMusicPlayer(callback_query.from_user.id, 'YandexMusic')
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Вы приобрели Premium!! Спасибо за доверие, выбранная площадка: Яндекс музка\n"
                                                        "теперь вы можете получать ссылки на плейлисты созднанные под ваше настроение")


@dispatcher.callback_query_handler(lambda c: c.data == 'btn_VK')
async def process_callback_button1(callback_query: aiogram.types.CallbackQuery):
    db.addMusicPlayer(callback_query.from_user.id, 'VkMusic')
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Вы приобрели Premium!! Спасибо за доверие, выбранная площадка: Вконтакте музка\n"
                           "теперь вы можете получать ссылки на плейлисты созднанные под ваше настроение")


@dispatcher.callback_query_handler(lambda c: c.data == 'contiune_generate_music')
async def process_callback_button1(callback_query: aiogram.types.CallbackQuery):
    await music_handler(callback_query)
    await callback_query.message.edit_reply_markup(reply_markup=None)


@dispatcher.callback_query_handler(lambda c: c.data == 'ru')
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


@dispatcher.callback_query_handler(lambda c: c.data == 'clean_history')
async def process_callback_button1(callback_query: aiogram.types.CallbackQuery):

    db.clearMemory(callback_query.from_user.id)
    await callback_query.answer("Общайтесь на новую тему")
    await callback_query.message.edit_reply_markup(reply_markup=None)


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


@dispatcher.message_handler(Command('text'))
def discript_of_bot(message):
    message.answer(""
                   ""
                   ""
                   ""
                   ""
                   "")


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
async def photo_generete(message):
    if db.getUser(message.from_user.id)["subscriptionEndDate"] < time.time():
        db.updateSubscriptionType(
            message.from_user.id, dbModel.SUBSCRIPTION_FREE)

    if db.getUser(message.from_user.id)['subscriptionType'] == dbModel.SUBSCRIPTION_PREM:

        await bot.send_message(message.from_user.id, "Пришлите описание картинки")
        await Stash.photo.set()
    else:
        await message.answer("Для того чтобы генерировать картинки вы должны стать Premium пользователем"
                             "для этого пришлите команду /pay")


@dispatcher.message_handler(state=Stash.photo)
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
    db.addUser(message.from_user.id,
               subscriptionType=dbModel.SUBSCRIPTION_PREM)
    db.updateSubscriptionEndDate(message.from_user.id, 2999999999.999)

    await message.answer("Здравстуй, я твой новый друг, меня зовут Валли.\n"
                         "В меня загружен весь интернет и я знаю абсолютно все, до чего в данный момент дошло человечество.\n"
                         "И я могу быть лично твоим помошником, тебе нужно лишь сформулировать запрос. Общайся со мной как с человеком,"
                         "чем подробнее будет запрос, тем шире и понятнее я смогу дать тебе ответ", reply_markup=keyboard)


@dispatcher.message_handler(Command('music'))
async def music_handler(message):
    if db.getUser(message.from_user.id)["subscriptionEndDate"] < time.time():
        db.updateSubscriptionType(
            message.from_user.id, dbModel.SUBSCRIPTION_FREE)
    if db.getUser(message.from_user.id)['subscriptionType'] == dbModel.SUBSCRIPTION_PREM:
        btn1 = aiogram.types.InlineKeyboardButton(
            "Сгенерировать еще", callback_data='contiune_generate_music')
        keyboard = aiogram.types.InlineKeyboardMarkup().add(btn1)
        await bot.send_message(message.from_user.id, "Напишите что бы вы хотели послушать, не бойтесь проявлять фантазию", reply_markup=keyboard)
        await Stash.music.set()
    else:
        await message.answer("Для того чтобы генерировать картинки вы должны стать Premium пользователем"
                             "для этого пришлите команду /pay")


@dispatcher.message_handler(state=Stash.music)
async def photo_answer(message: aiogram.types.Message, state: FSMContext):
    textEN = translator.translate(str(message.text), src='ru', dest='en').text
    await state.update_data(music=message.text)
    rawText = openaiModel.generateText(
        'write me 10 ' + textEN+' songs in format author - title')
    album = client.users_playlists_create(title=message.text)
    songsDict = defs.parseTracks(rawText)
    print(songsDict)
    if not songsDict:
        await message.answer("Извините что-то пошло не так, пришлите описание еще раз")
        await state.finish()
    i = 0
    for author in songsDict:
        for track in songsDict[author]:
            try:
                id = client.search(track+" "+author).best.result.albums[0].id
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
            except:
                await message.answer("Хочу добавить вам в плейлист {} - {}, но на Яндекс Музыке его нету".format(author, track))
                await state.finish()
    url = f'https://music.yandex.ru/users/g0sha5063/playlists/{album.kind}'
    await message.answer("Ваш плейлист готов:")
    await message.answer(url)
    await state.finish()


@dispatcher.message_handler(content_types=['text'])
async def text_handler(message):

    btn_contiune = aiogram.types.InlineKeyboardButton(
        "Продолжить эту тему", callback_data='Add_message_to_previos')
    btn_new_theme = aiogram.types.InlineKeyboardButton(
        "Новая тема", callback_data='clean_history')
    keyboard = aiogram.types.InlineKeyboardMarkup().add(btn_contiune, btn_new_theme)
    
    result = translator.translate(str(message.text), src='ru', dest='en')

    response = openaiModel.generateText(result.text)

    last_message = result.text
    db.setLastMessage(message.from_user.id, last_message + " "+response)

    if db.getLang(message.from_user.id) == "ru":
        response = translator.translate(response, src='en', dest='ru').text

    await message.answer(response, reply_markup=None)

if __name__ == '__main__':
    translator = googletrans.Translator()  # переводчик
    client = yandex_music.Client(
        secret_keys.yandexMusic).init()  # клиент яндекс музыки
    db = dbModel.DBModel()  # даза банных
    db.connect()
    aiogram.executor.start_polling(
        dispatcher, skip_updates=True)  # веч цикл телеграм бота
    db.close()
