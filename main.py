import openai
import secret_keys
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types.message import ContentType
import sqlite3
from secret_keys import Model

con = sqlite3.connect("chatgpt/db_for_gpt.db")
cur = con.cursor()

logging.basicConfig(level=logging.INFO)
bot = Bot(token=Model.telegram_key)
dispatcher = Dispatcher(bot)
PRICE = types.LabeledPrice(label="Подписка на 1 месяц", amount=500*100)


@dispatcher.message_handler(commands=['buy'])
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
@dispatcher.pre_checkout_query_handler(lambda query: True)
async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


# successful payment
@dispatcher.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: types.Message):
    print("SUCCESSFUL PAYMENT:")
    payment_info = message.successful_payment.to_python()
    print(payment_info)
    for k, v in payment_info.items():
        print(f"{k} = {v}")

    await bot.send_message(message.chat.id,
                           f"Платеж на сумму {message.successful_payment.total_amount // 100} {message.successful_payment.currency} прошел успешно!!!")



@dispatcher.message_handler(commands = ['start','help','photo','ccылка','музыка'])
async def welcome(message):


    await message.answer("Добро пожаловать, я твой интелектуальный помошник.\n"
                        "Выбери площадку на котороый ты слушаешь музыку",reply_markup = type)
@dispatcher.message_handler(content_types=['text'])
async def text_handler(message):
    await message.answer("Thanks")

if __name__ == '__main__':
    executor.start_polling(dispatcher, skip_updates=True)