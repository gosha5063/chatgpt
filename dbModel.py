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

    # название таблицы с юзерами
    usersTable = "users"

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

    @checkDB
    def addUser(self, telegramId, subscriptionType=SUBSCRIPTION_FREE, freeRolls=15):
        # если строка с таким айди уже есть
        if len(self.cur.execute("SELECT * FROM {} WHERE telegramId={};".format(self.usersTable, telegramId)).fetchall()) != 0:
            return self.TELEGRAM_ID_ALREADY_EXISTS
        now = time.time()
        month = 2592000  # seconds
        endDate = 0
        if subscriptionType == SUBSCRIPTION_PREM:
            endDate = now+month
        # добавляем строку
        self.cur.execute(
            "INSERT INTO {} VALUES ({},{},{},{},{},{});".format(self.usersTable, telegramId, now, subscriptionType, freeRolls, endDate, 0))
        self.con.commit()  # коммит
        return self.OK

    @checkDB
    def getUser(self, telegramId):
        values = self.cur.execute(
            "SELECT * FROM {} WHERE telegramId={};".format(self.usersTable, telegramId)).fetchone()
        keys = ["telegramId", "registrationDate", "subscriptionType",
                "freeRolls", "subscriptionEndDate", "banned"]  # ключи для него
        d = {}  # словарь который возвращаем
        for i in range(len(keys)):
            d[keys[i]] = values[i]
        return d

    @checkDB
    def removeUser(self, telegramId):
        # если нету строки с таким id
        if len(self.cur.execute("SELECT * FROM {} WHERE telegramId={};".format(self.usersTable, telegramId)).fetchall()) == 0:
            return self.USER_DOES_NOT_EXIST
        self.cur.execute(
            "DELETE FROM {} WHERE telegramId={};".format(self.usersTable, telegramId))
        self.con.commit()  # коммит
        return self.OK

    @checkDB
    def changeUserSubscriptionType(self, telegramId, newSubscriptionType=SUBSCRIPTION_FREE):
        # если нету строки с таким id
        if len(self.cur.execute("SELECT * FROM {} WHERE telegramId={};".format(self.usersTable, telegramId)).fetchall()) == 0:
            return self.USER_DOES_NOT_EXIST
        self.cur.execute(
            "UPDATE {} SET subscriptionType={} WHERE telegramId={};".format(self.usersTable, newSubscriptionType, telegramId))
        self.con.commit()  # коммит
        return self.OK

    @checkDB
    def banUser(self, telegramId):
        # если нету строки с таким id
        if len(self.cur.execute("SELECT * FROM {} WHERE telegramId={};".format(self.usersTable, telegramId)).fetchall()) == 0:
            return self.USER_DOES_NOT_EXIST
        self.cur.execute(
            "UPDATE {} SET banned=1 WHERE telegramId={};".format(self.usersTable, telegramId))
        self.con.commit()  # коммит
        return self.OK

    @checkDB
    def unbanUser(self, telegramId):
        # если нету строки с таким id
        if len(self.cur.execute("SELECT * FROM {} WHERE telegramId={};".format(self.usersTable, telegramId)).fetchall()) == 0:
            return self.USER_DOES_NOT_EXIST
        self.cur.execute(
            "UPDATE {} SET banned=0 WHERE telegramId={};".format(self.usersTable, telegramId))
        self.con.commit()  # коммит
        return self.OK

    @checkDB
    def updateSubscriptionEndDate(self, telegramId, newDate):
        # если нету строки с таким id
        if len(self.cur.execute("SELECT * FROM {} WHERE telegramId={};".format(self.usersTable, telegramId)).fetchall()) == 0:
            return self.USER_DOES_NOT_EXIST
        self.cur.execute(
            "UPDATE {} SET subscriptionEndDate={} WHERE telegramId={};".format(self.usersTable, newDate, telegramId))
        self.con.commit()  # коммит
        return self.OK

    @checkDB
    def updateUserFreeRolls(self, telegramId, newFreeRolls=15):
        # если нету строки с таким id
        if len(self.cur.execute("SELECT * FROM {} WHERE telegramId={};".format(self.usersTable, telegramId)).fetchall()) == 0:
            return self.USER_DOES_NOT_EXIST
        self.cur.execute(
            "UPDATE {} SET freeRolls={} WHERE telegramId={};".format(self.usersTable, newFreeRolls, telegramId))
        self.con.commit()  # коммит
        return self.OK
