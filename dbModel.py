import sqlite3  # спроси нахуя
import time  # чтобы текущ время получить для регистрации

# типы подписок
SUBSCRIPTION_ADMIN = 0
SUBSCRIPTION_FREE = 1
SUBSCRIPTION_PREM = 2


class DBModel:  # объект БД
    # коды ошибок
    OK = 0  # без ошибок маладца
    ERROR_ANY = 1  # если каким либо чудом я не прописал обработку, то код будет такой
    NO_DB = 2  # подключись сначала епт
    TELEGRAM_ID_ALREADY_EXISTS = 3  # куда второго юзера с таким-же айди пихаешь?
    BAD_SUBSCRIPTION_TYPE = 4  # вот там выше в 4 строке читай че можно а че нет
    USER_DOES_NOT_EXIST = 5  # нету у нас таких клиентов

    # путь файла с БД
    dbFilename = "database.db"

    # название таблиц
    usersTable = "users"

    memoryTable = "memory"

    # коннект курсор
    con, cur = None, None

    # можно тупо модель создать, а можно сразу файл бд указать
    def __init__(self, dbFilename=None):
        if dbFilename != None:
            self.dbFilename = dbFilename

    def connect(self, dbFilename=None):  # конект ту датабейс по файлнейму
        try:
            if dbFilename != None:
                self.dbFilename = dbFilename
            self.con = sqlite3.connect(self.dbFilename)
            self.cur = self.con.cursor()

            return self.OK
        except:
            return self.ERROR_ANY

    def close(self):  # закончили работу, закрываемся
        try:
            self.con.close()
            return self.OK
        except:
            return self.ERROR_ANY

    # взаимодействия с юзером через телеграм айди

    def checkDB(func):  # если совсем еблан и не указал бд
        def wrapper(self, *args, **kwargs):
            if self.con == None:
                return self.NO_DB
            return func(self, *args, **kwargs)
        return wrapper

    def checkUserExist(func):  # если телеграм айди == хуета
        def wrapper(self, *args, **kwargs):
            telegramId = args[0]
            if len(self.cur.execute("SELECT * FROM {} WHERE telegramId={};".format(self.usersTable, telegramId)).fetchall()) == 0:
                return self.USER_DOES_NOT_EXIST
            return func(self, *args, **kwargs)
        return wrapper

    @checkDB
    def addUser(self, telegramId, username, subscriptionType=SUBSCRIPTION_FREE, freeRolls=10, musicPlayers=[], lang="ru"):
        # если строка с таким айди уже есть
        if len(self.cur.execute("SELECT * FROM {} WHERE telegramId={};".format(self.usersTable, telegramId)).fetchall()) != 0:
            return self.TELEGRAM_ID_ALREADY_EXISTS
        now = time.time()
        month = 2592000  # seconds
        endDate = 0
        if subscriptionType == SUBSCRIPTION_PREM:
            endDate = now+month
        musicPlayers = " ".join(musicPlayers)
        # добавляем строку
        self.cur.execute(
            "INSERT INTO {} VALUES ({},'{}',{},{},{},{},{},'{}','{}');".format(self.usersTable, telegramId, username, now, subscriptionType, freeRolls, endDate, 0, musicPlayers, lang))
        self.cur.execute("INSERT INTO {} VALUES ({},'');".format(self.memoryTable, telegramId))
        self.con.commit()  # коммит
        return self.OK

    @checkDB
    @checkUserExist
    def getUser(self, telegramId):
        values = self.cur.execute(
            "SELECT * FROM {} WHERE telegramId={};".format(self.usersTable, telegramId)).fetchone()
        keys = ["telegramId", "username", "registrationDate", "subscriptionType",
                "freeRolls", "subscriptionEndDate", "banned", "musicPlayers", "lang"]  # ключи для него
        d = {}  # словарь который возвращаем
        for i in range(len(keys)):
            d[keys[i]] = values[i]
        return d

    @checkDB
    @checkUserExist
    def removeUser(self, telegramId):
        self.cur.execute(
            "DELETE FROM {} WHERE telegramId={};".format(self.usersTable, telegramId))
        self.con.commit()  # коммит
        return self.OK

    @checkDB
    @checkUserExist
    def updateSubscriptionType(self, telegramId, newSubscriptionType=SUBSCRIPTION_FREE):
        self.cur.execute(
            "UPDATE {} SET subscriptionType={} WHERE telegramId={};".format(self.usersTable, newSubscriptionType, telegramId))
        self.con.commit()  # коммит
        return self.OK

    @checkDB
    @checkUserExist
    def banUser(self, telegramId):
        self.cur.execute(
            "UPDATE {} SET banned=1 WHERE telegramId={};".format(self.usersTable, telegramId))
        self.con.commit()  # коммит
        return self.OK

    @checkDB
    @checkUserExist
    def unbanUser(self, telegramId):
        self.cur.execute(
            "UPDATE {} SET banned=0 WHERE telegramId={};".format(self.usersTable, telegramId))
        self.con.commit()  # коммит
        return self.OK

    @checkDB
    @checkUserExist
    def updateSubscriptionEndDate(self, telegramId, newDate):
        self.cur.execute(
            "UPDATE {} SET subscriptionEndDate={} WHERE telegramId={};".format(self.usersTable, newDate, telegramId))
        self.con.commit()  # коммит
        return self.OK

    @checkDB
    @checkUserExist
    def updateFreeRolls(self, telegramId, newFreeRolls=10):
        self.cur.execute(
            "UPDATE {} SET freeRolls={} WHERE telegramId={};".format(self.usersTable, newFreeRolls, telegramId))
        self.con.commit()  # коммит
        return self.OK

    @checkDB
    @checkUserExist
    def addMusicPlayer(self, telegramId, musicPlayer):
        musicPlayers = set(self.cur.execute(
            "SELECT musicPlayers FROM {} WHERE telegramId={};".format(self.usersTable, telegramId)).fetchone()[0].split())
        musicPlayers.add(musicPlayer)
        musicPlayers = " ".join(musicPlayers).strip()
        self.cur.execute(
            'UPDATE {} SET musicPlayers="{}" WHERE telegramId={};'.format(self.usersTable, musicPlayers, telegramId))
        self.con.commit()  # коммит
        return self.OK

    @checkDB
    @checkUserExist
    def removeMusicPlayer(self, telegramId, musicPlayer):
        musicPlayers = set(self.cur.execute(
            "SELECT musicPlayers FROM {} WHERE telegramId={};".format(self.usersTable, telegramId)).fetchone()[0].split())
        musicPlayers.discard(musicPlayer)
        musicPlayers = " ".join(musicPlayers).strip()
        self.cur.execute(
            'UPDATE {} SET musicPlayers="{}" WHERE telegramId={};'.format(self.usersTable, musicPlayers, telegramId))
        self.con.commit()  # коммит
        return self.OK

    @checkDB
    @checkUserExist
    def clearMusicPlayer(self, telegramId):
        self.cur.execute(
            'UPDATE {} SET musicPlayers="" WHERE telegramId={};'.format(self.usersTable, telegramId))
        self.con.commit()  # коммит
        return self.OK

    @checkDB
    @checkUserExist
    def switchLang(self, telegramId, lang):
        self.cur.execute(
            'UPDATE {} SET lang="{}" WHERE telegramId={};'.format(self.usersTable, lang, telegramId))
        self.con.commit()  # коммит

    @checkDB
    @checkUserExist
    def getLang(self, telegramId):
        return self.cur.execute(
            'SELECT lang from "{}" WHERE telegramId={};'.format(self.usersTable, telegramId)).fetchone()[0]

    @checkDB
    @checkUserExist
    def updateUsername(self, telegramId, username):
        self.cur.execute(
            'UPDATE {} SET username="{}" WHERE telegramId={};'.format(self.usersTable, username, telegramId))
        self.con.commit()  # коммит

    @checkDB
    @checkUserExist
    def getUsername(self, telegramId):
        return self.cur.execute(
            'SELECT username from "{}" WHERE telegramId={};'.format(self.usersTable, telegramId)).fetchone()[0]

    @checkDB
    @checkUserExist
    def addMemory(self, telegramId, text):
        text = normalizeText(text)
        memory = self.cur.execute(
            'SELECT prevMessages from "{}" WHERE telegramId={};'.format(self.memoryTable, telegramId)).fetchone()[0]
        memory += text
        self.cur.execute(
            'UPDATE {} SET prevMessages="{}" WHERE telegramId={};'.format(self.memoryTable, memory, telegramId))
        self.con.commit()  # коммит
        return self.OK

    @checkDB
    @checkUserExist
    def getMemory(self, telegramId):
        return self.cur.execute(
            'SELECT prevMessages from "{}" WHERE telegramId={};'.format(self.memoryTable, telegramId)).fetchone()[0]

    @checkDB
    @checkUserExist
    def clearMemory(self, telegramId):
        self.cur.execute(
            'UPDATE {} SET prevMessages="" WHERE telegramId={};'.format(self.memoryTable, telegramId))
        self.con.commit()  # коммит
        return self.OK


def normalizeText(text):
    text = text.replace("\n", " ")
    text = text.replace("\"", "'")
    return text
