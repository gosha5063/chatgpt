import dbModel
db = dbModel.DBModel()
db.connect()
db.clearMusicPlayer(0)
db.close()
