import dbModel
db = dbModel.DBModel()
db.connect()
db.addUser(887112, dbModel.SUBSCRIPTION_PREM)
print(db.getUser(887112))
db.close()
