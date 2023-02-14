import dbModel
db = dbModel.DBModel()
db.connect()
db.addUser(0, dbModel.SUBSCRIPTION_ADMIN)
db.close()
