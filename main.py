import types

from imports import *


PLAYLIST_SIZE = defs.PLAYLIST_SIZE
ONE_MONTH = 2592000
bot = aiogram.Bot(token=secret_keys.telegram)  # создаем бота
dispatcher = aiogram.Dispatcher(bot, storage=MemoryStorage())
PRICE = aiogram.types.LabeledPrice(
    label="Подписка на 1 месяц", amount=249*100)  # что это

"""декоратор ограничивающий количество запросов, обращается к классу ThrottlingMiddleware"""


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


"""antyflood class"""


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


"""Сменить плеер на Yandex"""


@dispatcher.callback_query_handler(lambda c: c.data == 'btn_Yandex')
@rate_limit(5)
async def process_callback_button1(callback_query: aiogram.types.CallbackQuery):
    db.clearMusicPlayer(callback_query.from_user.id)
    db.addMusicPlayer(callback_query.from_user.id, 'YandexMusic')
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Вы приобрели Premium!! Спасибо за доверие, выбранная площадка: Яндекс музка\n"
                                                        "теперь вы можете получать ссылки на плейлисты созднанные под ваше настроение")

"""сменить плеер на ВК"""


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
    await callback_query.message.edit_reply_markup(reply_markup=None)
    await music_handler(callback_query)


"""Кнопка для обработки русского"""


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
    await bot.send_message(callback_query.from_user.id, open("files/texts/change_lang_russian", encoding="utf-8").read(), reply_markup=keyboard, parse_mode="Markdown")

"""#Этот код определяет две кнопки InlineKeyboardButton,
 одну для английского и одну для русского, и присваивает 
 им соответствующие данные обратного вызова. Затем он создает InlineKeyboardMarkup,
  добавляет к нему кнопки, переключает язык в записи базы данных пользователя
   на английский и отправляет сообщение с разметкой. Декоратор rate_limit
    ограничивает скорость вызова функции до 5 раз в секунду."""


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
    await bot.send_message(callback_query.from_user.id, open("files/texts/change_lang_eng", encoding="utf-8").read(), reply_markup=keyboard, parse_mode="Markdown")


@dispatcher.callback_query_handler(lambda c: c.data == 'cancel_music', state=Stash.music)
async def process_callback_button1(callback_query: aiogram.types.CallbackQuery, state: FSMContext):
    await callback_query.answer("Запрос на генерацию музыки отменен")
    await callback_query.message.delete()
    await state.finish()


@dispatcher.callback_query_handler(lambda c: c.data == 'cancel_photo', state=Stash.photo)
async def process_callback_button1(callback_query: aiogram.types.CallbackQuery, state: FSMContext):
    await callback_query.answer("Запрос на генерацию фото отменен")
    await callback_query.message.delete()
    await state.finish()


@dispatcher.callback_query_handler(lambda c: c.data == 'photo_one_more')
async def process_callback_button1(callback_query: aiogram.types.CallbackQuery):
    await photo_generete(callback_query)
    await callback_query.message.edit_reply_markup(reply_markup=None)
@dispatcher.callback_query_handler(lambda c: c.data == 'photo_one_more_None')
async def process_callback_button1(callback_query: aiogram.types.CallbackQuery):
    await callback_query.message.delete()
    await photo_generete(callback_query)


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
"""Функция, которая срабатывает при успешном платеже.
 Он обновляет тип подписки пользователя в базе данных на Премиум и обновляет 
 дату окончания подписки на месяц вперед. Он распечатывает платежную информацию 
 и отправляет пользователю сообщение с суммой платежа и выбором площадок для прослушивания музыки."""


@dispatcher.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: aiogram.types.Message):
    db.updateSubscriptionType(message.from_user.id,
                              newSubscriptionType=dbModel.SUBSCRIPTION_PREM)
    db.updateSubscriptionEndDate(message.from_user.id, time.time()+ONE_MONTH)

    payment_info = message.successful_payment.to_python()
    btn_Yandex = aiogram.types.InlineKeyboardButton(
        "Яндекс Музыка", callback_data='btn_Yandex')
    btn_VK = aiogram.types.InlineKeyboardButton(
        "Вк Музыка", callback_data='btn_VK')
    keyboard = aiogram.types.InlineKeyboardMarkup().add(btn_Yandex, btn_VK)
    print(message.from_user.username, "/pay")
    for k, v in payment_info.items():
        print(f"{k} = {v}")

    await bot.send_message(message.chat.id,
                           f"Платеж на сумму {message.successful_payment.total_amount // 100} {message.successful_payment.currency} прошел успешно!!!\n"
                           f"Выберите площадку на которой вы слушаете музыку", reply_markup=keyboard)

"""# This code creates a message handler for the command 'photo'
 and adds a rate limit of 5 per key. If the user's subscription 
 type is premium or they have more than 0 free rolls, they will 
 be sent a message with a keyboard containing a 'Cancel' button.
  Otherwise they will be sent a message asking them to become premium."""


@dispatcher.message_handler(Command('photo'))
@rate_limit(5, key="photo")
async def photo_generete(message:types.Message):
    updateUser(message.from_user.id, message.from_user.username)

    if db.getUser(message.from_user.id)['subscriptionType'] == dbModel.SUBSCRIPTION_PREM or db.getUser(message.from_user.id)['freeRolls'] >= 2:
        btn2 = aiogram.types.InlineKeyboardButton(
            "Отменить", callback_data="cancel_photo")
        keyboard = aiogram.types.InlineKeyboardMarkup().add(btn2)
        await bot.send_message(message.from_user.id, "Пришлите описание картинки", reply_markup=keyboard)
        await Stash.photo.set()
    else:
        await bot.send_message(message.from_user.id,open("files/texts/ask_for_become_premium",encoding="utf-8").read().format(db.getUser(message.from_user.id)["freeRolls"]))

"""Этот код является обработчиком обратного вызова для кнопки в чат-боте Telegram.
 При нажатии кнопки код проверяет пользователя в базе данных, чтобы узнать, 
 какой музыкальный проигрыватель у него есть в данный момент. 
 Затем он меняет музыкальный проигрыватель на другой и отправляет пользователю сообщение,
  подтверждающее изменение. Если у пользователя нет музыкального проигрывателя, подключенного к боту, 
  он отправляет пользователю сообщение с указанием нажать команду /premium для подключения проигрывателя."""

@dispatcher.callback_query_handler(lambda c: c.data == 'premium')
async def process_callback_button1(message: aiogram.types.CallbackQuery):
    await message.message.edit_reply_markup(reply_markup=None)
    await message.message.delete()
    await preium_info(message.message)

@dispatcher.callback_query_handler(lambda c: c.data == 'btn_change_music_player')
async def process_callback_button1(message: aiogram.types.CallbackQuery):
    dt = {"YandexMusic": "VkMusic", "VkMusic": "YandexMusic"}
    await message.message.edit_reply_markup(reply_markup=None)
    await message.message.delete()
    try:
        player = dt[db.getUser(message.from_user.id)['musicPlayers']]
        db.removeMusicPlayer(message.from_user.id, db.getUser(
            message.from_user.id)['musicPlayers'])
        db.addMusicPlayer(message.from_user.id, player)

        dt = {"YandexMusic": "Яндекс музыку", "VkMusic": "Вк Музыку"}

        await message.answer(f"Плеер успешно сменен на {dt[db.getUser(message.from_user.id)['musicPlayers']]}")
    except KeyError:
        btn = types.InlineKeyboardButton("Премиум",callback_data="premium")
        keyboard = types.InlineKeyboardMarkup().add(btn)

        await bot.send_message(message.from_user.id,"У вас пока не подключен ни один плеер,\n чтобы он стал доступен - нажмите на кнопку под сообщением",reply_markup=keyboard)


@dispatcher.callback_query_handler(lambda c: c.data == 'pay_premium')
async def process_callback_button1(message: aiogram.types.CallbackQuery):
    await message.message.edit_reply_markup(reply_markup=None)
    await buy(message.message)


@dispatcher.message_handler(Command('premium'))
async def preium_info(message: types.Message):
    btn_pay = types.InlineKeyboardButton("Купить подписку", callback_data="pay_premium")
    keyboard = types.InlineKeyboardMarkup().add(btn_pay)
    photo = open(
        "files/photo/__make_her_gold_hair_a8f644a7-5c20-4a91-a034-a892c55a47a4.png", 'rb')
    await message.answer_photo(photo=photo, caption=open("files/texts/premium", encoding="utf-8").read(),reply_markup=keyboard)


@dispatcher.callback_query_handler(lambda c: c.data == 'btn_change_lang')
async def process_callback_button1(callback_query: aiogram.types.CallbackQuery):
    dt = {'en': 'ru', 'ru': 'en'}

    db.switchLang(callback_query.from_user.id,
                  dt[db.getLang(callback_query.from_user.id)])
    dt = {'ru': open("./files/texts/change_lang_russian", encoding="utf-8").read(),
          "en": open("./files/texts/change_lang_eng", encoding="utf-8").read()}
    await callback_query.message.delete()
    await bot.send_message(callback_query.from_user.id, dt[db.getLang(callback_query.from_user.id)], parse_mode="Markdown")
    await callback_query.message.edit_reply_markup(reply_markup=None)



@dispatcher.message_handler(Command('settings'))
async def settings(message: types.Message):
    btn_change_lang = types.InlineKeyboardButton(
        "Сменить язык ответа", callback_data="btn_change_lang")
    btn_change_music_player = types.InlineKeyboardButton(
        "Сменить площадку", callback_data="btn_change_music_player")
    keyboard = types.InlineKeyboardMarkup().add(
        btn_change_lang, btn_change_music_player)
    dt_lang = {'ru':"Русский",'en':"Английский"}
    dt_player = {"YandexMusic": "Яндекс Музыка", "VkMusic":"Вк Музыка","":"Не выбрано"}
    await message.answer(open("files/texts/settings", encoding="utf-8").read().format(dt_lang[db.getUser(message.from_user.id)["lang"]],
            dt_player[db.getUser(message.from_user.id)["musicPlayers"]]),parse_mode="Markdown", reply_markup=keyboard)


"""Этот код печатает имя пользователя и текст, отправленный через сообщение.
 Затем он переводит сообщение на английский язык и создает изображение на основе этого текста.
  Затем добавляется кнопка, чтобы пользователь мог создавать больше фотографий. 
  Последний шаг — проверить, есть ли у пользователя бесплатная подписка, 
  и если да, то истощить их бесплатные рулоны. 
  Наконец, он возвращает сгенерированное изображение с кнопкой и завершает разговор."""


@dispatcher.message_handler(state=Stash.photo)
@rate_limit(5)
async def photo_answer(message: aiogram.types.Message, state: FSMContext):
    print(db.getUsername(message.from_user.id), "/photo", message.text)
    textEN = translator.translate(message.text, dest='en', src='ru').text
    print(textEN)
    btn_photo = aiogram.types.InlineKeyboardButton(
        "Сгенерировать еще фото", callback_data='photo_one_more')
    keyboard = aiogram.types.InlineKeyboardMarkup().add(btn_photo)
    try:
        imageUrl = openaiModel.generatePhoto(textEN)
    except:
        await message.answer(
            open("files/texts/server_error", encoding="utf-8").read())
        await state.finish()
        return
    print(imageUrl)
    if imageUrl == None:
        btn = types.InlineKeyboardButton("Попробовать еще раз", callback_data= "photo_one_more_None")
        key = types.InlineKeyboardMarkup()
        key.add(btn)
        await message.answer("Извините, ваш запрос содержит неприемлемую тему."
                             "\nСейчас мы не можем сгенерировать такую картинку\n"
                             "❗Ваш запрос прерван",reply_markup=key)

    else:
        try:
            await bot.send_photo(message.from_user.id, imageUrl, reply_markup=keyboard)
        except:
            await message.answer(open("files/texts/error",encoding="utf-8").read())
        print(imageUrl)
        if db.getUser(message.from_user.id)['subscriptionType'] == dbModel.SUBSCRIPTION_FREE:
            db.updateFreeRolls(message.from_user.id, db.getUser(
                message.from_user.id)["freeRolls"]-2)
    await state.finish()


"""Этот фрагмент кода используется для отправки приветственного сообщения с фотографией новому пользователю Telegram.
 Сначала создаются две встроенные кнопки с текстом «Английский» и «Русский». Затем он создает клавиатуру,
  содержащую эти две кнопки. Затем пользователь добавляется в базу данных с бесплатным типом подписки и 10 бесплатными рулонами.
   Наконец, фотография и приветственное сообщение отправляются пользователю с помощью клавиатуры."""


@dispatcher.message_handler(commands=['start'])
@rate_limit(5, key='start')
async def welcome(message: types.Message):

    music = types.KeyboardButton("Сгенерировать музыку 🌌")
    photo = types.KeyboardButton("Сгенерировать фото 🌄")
    setting = types.KeyboardButton("Настройки⚙")
    about_us = types.KeyboardButton("Наша группа🦋")
    premium = types.KeyboardButton("Премиум🔥")
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False,is_persistent = False).add(music, photo)
    keyboard.add(setting,about_us)
    keyboard.add(premium)

    db.addUser(message.from_user.id, message.from_user.username,
               subscriptionType=dbModel.SUBSCRIPTION_FREE, freeRolls=10)
    photo = open(
        "./files/photo/__make_her_most_realistic_4k_avatar_f0b21111-64c1-48fb-ba7d-6b55f56937ee.png", 'rb')
    await message.answer_photo(photo=photo, caption=open("./files/texts/welcome_message", encoding="utf-8").read(), reply_markup=keyboard, parse_mode="Markdown")

""" код обновляет информацию о пользователе (идентификатор и имя пользователя),
 когда пользователь отправляет сообщение боту. Затем он проверяет,
  есть ли у пользователя подписка или бесплатные ролики. Если они это сделают,
   пользователю отправляется сообщение с просьбой ввести то, что он хочет прослушать,
    и предоставляется возможность отменить. Если у них нет подписки или бесплатных роликов,
     пользователю отправляется сообщение с просьбой стать премиум-пользователем 
     и предоставляется возможность купить подписку."""


@dispatcher.message_handler(Command('music'))
@rate_limit(5, key="music")
async def music_handler(message):
    updateUser(message.from_user.id, message.from_user.username)
    if db.getUser(message.from_user.id)['subscriptionType'] == dbModel.SUBSCRIPTION_PREM or db.getUser(message.from_user.id)['freeRolls'] >= 4:
        btn2 = aiogram.types.InlineKeyboardButton(
            "Отменить", callback_data="cancel_music")
        keyboard = aiogram.types.InlineKeyboardMarkup().add(btn2)
        await bot.send_message(message.from_user.id, "Напишите что бы вы хотели послушать, не бойтесь проявлять фантазию", reply_markup=keyboard)
        await Stash.music.set()
    else:
        await bot.send_message(message.from_user.id,open("files/texts/ask_for_become_premium", encoding="utf-8").read().format(db.getUser(message.from_user.id)["freeRolls"]))


"""Этот код создает список воспроизведения с заданным именем и добавляет в него треки на основе заданных параметров. Во-первых, он получает имя пользователя и выводит его на консоль. Затем он отправляет сообщение пользователю, которое соответствует его описанию.
Затем он создает альбом с заданным именем. Затем он создает словарь песен и устанавливает для него пустой словарь. Если словарь пуст, он переводит сообщение на английский язык и использует модель openai для генерации текста. Затем он анализирует текст для создания словаря песен.
Затем он перебирает песни в словаре, ища наилучшее совпадение в Яндекс Музыке. Если совпадение найдено, оно добавляется в список воспроизведения. Он также отслеживает количество добавленных дорожек и обновляет пользователя сообщением о состоянии.
Наконец, он возвращает URL-адрес плейлиста пользователю и завершает состояние. Если пользователь находится на бесплатном плане подписки, это также уменьшает их бесплатные рулоны."""


@dispatcher.message_handler(state=Stash.music)
@rate_limit(10)
async def music_answer(message: aiogram.types.Message, state: FSMContext):
    print(db.getUsername(message.from_user.id), "/music", message.text)
    status_message = await bot.send_message(message.from_user.id, "Думаю что подходит под ваше описание")
    album = client.users_playlists_create(title=message.text)
    songsDict = {}
    while songsDict == {}:
        textEN = translator.translate(
            str(message.text), src='ru', dest='en').text
        await state.update_data(music=message.text)
        print(textEN)
        try:
            rawText = openaiModel.generateText(
                f'write me {PLAYLIST_SIZE} {textEN} songs in format author - title', max_tokens=300)
        except :
            await message.answer(open("files/texts/server_error", encoding="utf-8").read())
            await state.finish()
            return
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
            try:
                await status_message.edit_text(f"Делаю плейлист|{str(int(tracksAdded/tracksAll*100))}%")
            except:
                pass
    url = f'https://music.yandex.ru/users/g0sha5063/playlists/{album.kind}'
    btn_generatemore = types.InlineKeyboardButton(
        "Сгенерировать еще", callback_data="contiune_generate_music")
    keyboard = types.InlineKeyboardMarkup().add(btn_generatemore)
    await status_message.delete()
    try:
        await message.answer(f"Ваш плейлист готов: {url}", reply_markup=keyboard)
    except:
        await message.answer(open("files/texts/error",encoding="utf-8").read())
    print(url)
    if db.getUser(message.from_user.id)['subscriptionType'] == dbModel.SUBSCRIPTION_FREE:
        db.updateFreeRolls(message.from_user.id, db.getUser(
            message.from_user.id)["freeRolls"]-4)

    await state.finish()


@dispatcher.callback_query_handler(lambda c: c.data == 'btn_new_theme')
@rate_limit(5)
async def process_callback_button1(callback_query: aiogram.types.CallbackQuery):
    db.clearMemory(callback_query.from_user.id)
    await callback_query.answer("Вы общетесь на новую тему")
    await callback_query.message.edit_reply_markup(reply_markup=None)

"""Этот код начинается с набора операторов if, которые проверяют, соответствует ли текстовое сообщение, полученное пользователем, «Создать музыку 🌌», «Создать фото 🌄» или «Настройки языка и музыкальной платформы⚙️». В зависимости от полученного текстового сообщения вызывается соответствующая функция (music_handler, photo_generate или settings).
После операторов if создается кнопка клавиатуры, содержащая текст «Создать музыку 🌌», «Создать фото 🌄» и «Настройки языка и музыкального заведения⚙️». Затем клавиатура добавляется к разметке клавиатуры ответа.
Данные пользователя (включая его идентификатор и имя пользователя) затем обновляются в базе данных.
Далее выполняется проверка, есть ли у пользователя премиальная подписка или бесплатные ролики. Если это так, текстовое сообщение переводится с русского на английский и передается модели OpenAI для генерации ответа. Затем ответ переводится обратно на язык пользователя (если это английский) и отправляется пользователю с разметкой клавиатуры. Если у пользователя есть бесплатная подписка, количество бесплатных роллов уменьшается на единицу.
Наконец, если у пользователя нет премиум-подписки или бесплатных роликов, пользователю отправляется сообщение с просьбой стать премиум-участником с разметкой клавиатуры"""

async def send_info(message: types.Message):
    await message.answer(open("files/texts/info_about_us", encoding="utf-8").read())


"""This code is a text handler for an AI chatbot. It processes user inputs and responds accordingly.
 It allows users to choose from a list of options such as generating music, generating photos, 
 and adjusting settings. It also checks if the user is a premium user before allowing them to 
 interact with the chatbot. Additionally, it updates the user's profile in the database and adds 
 the user's conversation to the memor"""
@dispatcher.message_handler(content_types=['text'])
@rate_limit(5)
async def text_handler(message: types.Message):
    if message.text == "Сгенерировать музыку 🌌":
        await music_handler(message)
        return
    if message.text == "Сгенерировать фото 🌄":
        await photo_generete(message)
        return
    if message.text == "Настройки⚙":
        await settings(message)
        return
    if message.text == "Наша группа🦋":
        await send_info(message)
        return
    if message.text == "Премиум🔥":
        await preium_info(message)
        return
    btn_new_theme = types.InlineKeyboardButton(
        "Новая тема", callback_data="btn_new_theme")
    key = types.InlineKeyboardMarkup().add(btn_new_theme)
    updateUser(message.from_user.id, message.from_user.username)
    if db.getUser(message.from_user.id)['subscriptionType'] == dbModel.SUBSCRIPTION_PREM or db.getUser(message.from_user.id)['freeRolls'] >= 1:
        textEN = translator.translate(
            str(message.text), src='ru', dest='en').text
        print(db.getUsername(message.from_user.id), "/text", message.text)
        if db.getMemory(message.from_user.id) == "":
            db.addMemory(message.from_user.id,
                         openaiModel.startConversationText)
        prev = db.getMemory(message.from_user.id)
        try:
            response = openaiModel.continueConversation(prev, textEN)
            db.addMemory(message.from_user.id, textEN+"\nAI: "+response+"\nHuman: ")
        except Exception as e:
            print(e)
            await message.answer(open("files/texts/server_error", encoding="utf-8").read())
            return
        print(textEN)
        if db.getLang(message.from_user.id) == "ru":
            response = translator.translate(response, src='en', dest='ru').text
        await message.answer(response, reply_markup=key)
        if db.getUser(message.from_user.id)['subscriptionType'] == dbModel.SUBSCRIPTION_FREE:
            db.updateFreeRolls(message.from_user.id, db.getUser(
                message.from_user.id)["freeRolls"]-1)
    else:
        await message.reply(open("files/texts/ask_for_become_premium", encoding="utf-8").read().format(db.getUser(message.from_user.id)["freeRolls"]))


def updateUser(telegramId, username):
    db.updateUsername(telegramId, username)
    if db.getUser(telegramId)["subscriptionEndDate"] < time.time():
        db.updateSubscriptionType(telegramId, dbModel.SUBSCRIPTION_FREE)


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
