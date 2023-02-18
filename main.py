import yandex_music

import dbModel
import secret_keys
from defs_module import parse_the_responce

from secret_keys import Model

import aiogram.bot.api
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types.message import ContentType
import requests
import logging
import time
import openai
from yandex_music import Client
from googletrans import Translator
from states import Stash
from yandex_music import exceptions


db = dbModel.DBModel()

logging.basicConfig(level=logging.INFO)
bot = Bot(token=Model.telegram_key)
dispatcher = Dispatcher(bot, storage=MemoryStorage())
PRICE = types.LabeledPrice(label="Подписка на 1 месяц", amount=500*100)
openai.api_key = Model.open_ai_key
IAM_TOKEN = 't1.9euelZqdz4yUx4nGnprJnpuLys-Omu3rnpWai8-Xzp6LnsmZkp3Lypubi87l8_dWR0Zg-e98dlgo_t3z9xZ2Q2D573x2WCj-.RAQQ7NC4zSty2vay61yg36WKBy9TDRjX6UPDove48DEdZnV0Hpe0ozPCc0jnAtpEhIXmgQ9WizNy6Xnh0WqpBA'
folder_id = 'b1gr9n62s9oofoaj0cke'



@dispatcher.callback_query_handler(lambda c: c.data == 'btn_Yandex')
async def process_callback_button1(callback_query: types.CallbackQuery):
    db.addMusicPlayer(callback_query.from_user.id, 'YandexMusic')
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Вы приобрели Premium!! Спасибо за доверие, выбранная площадка: Яндекс музка\n"
                                                        "теперь вы можете получать ссылки на плейлисты созднанные под ваше настроение")


@dispatcher.callback_query_handler(lambda c: c.data == 'btn_VK')
async def process_callback_button1(callback_query: types.CallbackQuery):
    db.addMusicPlayer(callback_query.from_user.id, 'VkMusic')
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Вы приобрели Premium!! Спасибо за доверие, выбранная площадка: Вконтакте музка\n"
                           "теперь вы можете получать ссылки на плейлисты созднанные под ваше настроение")

@dispatcher.callback_query_handler(lambda c: c.data == 'contiune_generate_music')
async def process_callback_button1(callback_query: types.CallbackQuery):
    await music_handler(callback_query)
    await callback_query.message.edit_reply_markup(reply_markup=None)


@dispatcher.callback_query_handler(lambda c: c.data == 'clean_history')
async def process_callback_button1(callback_query: types.CallbackQuery):

    db.clearMemory(callback_query.from_user.id)
    await callback_query.answer("Общайтесь на новую тему")
    await callback_query.message.edit_reply_markup(reply_markup=None)


@dispatcher.callback_query_handler(lambda c: c.data == 'Add_message_to_previos')
async def process_callback_button1(callback_query: types.CallbackQuery):
    # db.updateMemory(callback_query.from_user.id, db.getLastMessage(callback_query.from_user.id))
    await callback_query.answer("Уточнить")
    await callback_query.message.edit_reply_markup(reply_markup=None)

@dispatcher.callback_query_handler(lambda c: c.data == 'photo_one_more')
async def process_callback_button1(callback_query: types.CallbackQuery):
    await photo_generete(callback_query)
    await callback_query.message.edit_reply_markup(reply_markup=None)

@dispatcher.message_handler(commands=['pay'])
async def buy(message: types.Message):
    config = Model.payment_test_token
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
async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
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
async def successful_payment(message: types.Message):
    db.updateSubscriptionType(message.from_user.id,
                              newSubscriptionType=dbModel.SUBSCRIPTION_PREM)

    payment_info = message.successful_payment.to_python()
    btn_Yandex = types.InlineKeyboardButton(
        "Яндекс Музыка", callback_data='btn_Yandex')
    btn_VK = types.InlineKeyboardButton("Вк Музыка", callback_data='btn_VK')
    keyboard = types.InlineKeyboardMarkup().add(btn_Yandex, btn_VK)
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
async def photo_answer(message: types.Message, state: FSMContext):
    photo = message.text
    """для ожидания ботом сообщения"""
    await state.update_data(photo=photo)
    try:
        res = translator.translate(message.text,dest='en',src='ru')
        btn_photo = types.InlineKeyboardButton("Сгенерировать еще фото", callback_data='photo_one_more')
        keyboard = types.InlineKeyboardMarkup().add(btn_photo)

        response = openai.Image.create(
            prompt=res.text,
            n=1,
            size="1024x1024"
        )
        await bot.send_photo(message.from_user.id, response['data'][0]['url'], reply_markup=keyboard)

    except openai.error.InvalidRequestError:
        await message.answer("Извините, сейчас мы не можем сгенерировать картинку по вашему запросу")
    await state.finish()


@dispatcher.message_handler(commands=['start'])
async def welcome(message):
    db.addUser(message.from_user.id,subscriptionType=dbModel.SUBSCRIPTION_PREM)
    db.updateSubscriptionEndDate(message.from_user.id, 2999999999.999)

    await message.answer("Здравстуй, я твой новый друг, меня зовут .\n")


@dispatcher.message_handler(Command('music'))
async def music_handler(message):
    if db.getUser(message.from_user.id)["subscriptionEndDate"] < time.time():
        db.updateSubscriptionType(
            message.from_user.id, dbModel.SUBSCRIPTION_FREE)
    if db.getUser(message.from_user.id)['subscriptionType'] == dbModel.SUBSCRIPTION_PREM:
        btn1 = types.InlineKeyboardButton("Сгенерировать еще", callback_data='contiune_generate_music')
        keyboard = types.InlineKeyboardMarkup().add(btn1)
        await bot.send_message(message.from_user.id, "Напишите что бы вы хотели послушать, не бойтесь проявлять фантазию",reply_markup=keyboard)
        await Stash.music.set()
    else:
        await message.answer("Для того чтобы генерировать картинки вы должны стать Premium пользователем"
                             "для этого пришлите команду /pay")


@dispatcher.message_handler(state=Stash.music)
async def photo_answer(message: types.Message, state: FSMContext):
    result = translator.translate(str(message.text), src='ru', dest='en')
    await state.update_data(music = message.text)
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=str('write me 10 songs and enumirate them from 1 to 10' + result.text),
        temperature=0.8,
        max_tokens=300,
    )

    album = client.users_playlists_create(title = message.text)
    kind = album.kind
    treks = parse_the_responce(response['choices'][0]['text'])
    print(treks)
    print(result)
    print(response)
    i = 0
    for trek in treks:
        try:
            id = client.search(treks[trek]["title" + trek.replace('.', '')] + treks[trek]["artist" + trek.replace('.', '')])
            client.users_playlists_insert_track(kind=kind,track_id = id.best.result.id,album_id=id.best.result.albums[0].id,at=i,revision=client.users_playlists(kind=kind).track_count+1)
            i += 1
        except AttributeError | IndexError | yandex_music.exceptions.BadRequestError:
            await message.answer("Извинните что-то пошло не так, попробуйте еще раз")
            await state.finish()
    url = f'https://music.yandex.ru/users/g0sha5063/playlists/{kind}'
    await message.answer("Ваш плейлист готов:")
    await message.answer(url)
    await state.finish()


@dispatcher.message_handler(content_types=['text'])
async def text_handler(message):

    btn_Yandex = types.InlineKeyboardButton("Продолжить эту тему", callback_data='Add_message_to_previos')
    btn_VK = types.InlineKeyboardButton("Новая тема", callback_data='clean_history')
    keyboard = types.InlineKeyboardMarkup().add(btn_Yandex, btn_VK)

    result = translator.translate(str(message.text), src = 'ru', dest='en')

    responce = openai.Completion.create(
        model="text-davinci-003",
        prompt= str(result.text),
        temperature=0.8,
        max_tokens=300,
    )

    last_message = result.text
    # db.setLastMessage(message.from_user.id, last_message + responce['choices'][0]['text'] )

    result = translator.translate(responce['choices'][0]['text'], src = 'en', dest='ru')

    await message.answer(result.text, reply_markup=keyboard)

if __name__ == '__main__':
    client = Client(secret_keys.Model.yandex_music_key).init()
    translator = Translator()
    db.connect()
    executor.start_polling(dispatcher, skip_updates=True)
    db.close()
