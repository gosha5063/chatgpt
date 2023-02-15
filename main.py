import dbModel

from secret_keys import Model

import aiogram.bot.api
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types.message import ContentType

import logging
import time
import openai

from states import Stash

db = dbModel.DBModel()

logging.basicConfig(level=logging.INFO)
bot = Bot(token=Model.telegram_key)
dispatcher = Dispatcher(bot, storage=MemoryStorage())
PRICE = types.LabeledPrice(label="Подписка на 1 месяц", amount=500*100)
openai.api_key = Model.open_ai_key


# def check_if_subscription_is_active(func):
#     def wrapper(*args,**kwargs):
#         message = args[0]
#
#         if db.getUser(message.from_user.id)["subscriptionEndDate"] < time.time():
#
#             db.updateSubscriptionType(message.from_user.id,dbModel.SUBSCRIPTION_FREE)
#         return func(*args, **kwargs)
#     return wrapper


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


@dispatcher.callback_query_handler(lambda c: c.data == 'clean_history')
async def process_callback_button1(callback_query: types.CallbackQuery):
    await callback_query.answer("Общайтесь на новую тему")
    await callback_query.message.edit_reply_markup(reply_markup=None)


@dispatcher.callback_query_handler(lambda c: c.data == 'Add_message_to_previos')
async def process_callback_button1(callback_query: types.CallbackQuery):
    await callback_query.answer("Уточните запрос")
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
# pre checkout  (must be answered in 10 seconds)

# def check_if_user_autificated(func):
#     def wrapper(*args, **kwargs):



@dispatcher.pre_checkout_query_handler(lambda query: True)
async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


# successful payment
@dispatcher.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: types.Message):
    db.updateSubscriptionType(message.from_user.id,newSubscriptionType=dbModel.SUBSCRIPTION_PREM)

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
        db.updateSubscriptionType(message.from_user.id, dbModel.SUBSCRIPTION_FREE)

    if db.getUser(message.from_user.id)['subscriptionType'] == dbModel.SUBSCRIPTION_PREM:

        await bot.send_message(message.from_user.id, "Пришлите описание картинки")
        await Stash.photo.set()
    else:
        await message.answer("Для того чтобы генерировать картинки вы должны стать Premium пользователем"
                             "для этого пришлите команду /pay")


@dispatcher.message_handler(state=Stash.photo)
async def photo_answer(message: types.Message, state: FSMContext):
    photo = message.text
    await state.update_data(photo=photo)
    try:
        response = openai.Image.create(
            prompt=message.text,
            n=1,
            size="1024x1024"
        )
        await bot.send_photo(message.from_user.id, response['data'][0]['url'])

    except openai.error.InvalidRequestError:
        await message.answer("Извините, сейчас мы не можем сгенерировать картинку по вашему запросу")
    await state.finish()


@dispatcher.message_handler(commands=['start'])
async def welcome(message):
    db.addUser(message.from_user.id,subscriptionType=dbModel.SUBSCRIPTION_PREM)
    await message.answer("Добро пожаловать, я твой интелектуальный помошник.\n")



@dispatcher.message_handler(content_types=['text'])
async def text_handler(message):
    btn_Yandex = types.InlineKeyboardButton(
        "Продолжить эту тему", callback_data='Add_message_to_previos')
    btn_VK = types.InlineKeyboardButton(
        "Новая тема", callback_data='clean_history')
    keyboard = types.InlineKeyboardMarkup().add(btn_Yandex, btn_VK)
    responce = openai.Completion.create(
        model="text-davinci-003",
        prompt=message.text,
        temperature=0.8,
        max_tokens=300,
    )
    await message.answer(responce["choices"][0]['text'], reply_markup=keyboard)

if __name__ == '__main__':
    db.connect()
    executor.start_polling(dispatcher, skip_updates=True)
    db.close()
