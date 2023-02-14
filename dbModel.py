import sqlite3  # спроси нахуя
import time  # чтобы текущ время получить для регистрации


class DBModel:  # то, ради чего этот модуль
    # типы подписок
    SUBSCRIPTION_ADMIN = 0
    SUBSCRIPTION_FREE = 1
    SUBSCRIPTION_PREM = 2

    # коды ошибок
    OK = 0  # без ошибок маладца
    ERROR_ANY = 1  # если каким либо чудом я не прописал обработку, то код будет такой
    TELEGRAM_ID_ALREADY_EXISTS = 2  # куда второго юзера с таким-же айди пихаешь?

    # путь файла с БД
    dbFilename = "database.db"

    # коннект курсор
    con, cur = None, None

    # можно тупо модель создать, а можно сразу файл бд указать
    def __init__(self, dbFileName=None):
        if dbFileName != None:
            self.dbFilename = dbFileName

    def connect(self, dbFileName=None):  # конект ту датабейс по файлнейму
        try:
            if dbFileName != None:
                self.dbFilename = dbFileName
            self.con = sqlite3.connect(dbFileName)
            self.cur = self.con.cursor()
            return self.OK
        except:
            return self.ERROR_ANY

    # закончили работу, закрываемся
    def close(self):
        try:
            self.con.close()
            return self.OK
        except:
            return self.ERROR_ANY

    # взаимодействия с юзером через телеграм айди

    def addUser(self, telegramId, subscriptionType=None):
        pass

    def removeUser(self, telegramId):
        pass

    def changeUserSubscriptionType(self, user, newSubscriptionType=None):
        pass

    def banUser(self, telegramId):
        pass

    def unbanUser(self, telegramId):
        pass

    def updateSubscriptionEndDate(self, telegramId, newDate):
        pass

    def getUserFreeRolls(self, telegramId):
        pass

    def updateUserFreeRolls(self, telegramId, newCountFreeRolls=None):
        pass
