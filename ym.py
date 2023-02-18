token = "AQAAAABUEq_5AAG8XleghLapBUvLj7OPKJ2ooDg"
from yandex_music import Client
client =  Client(token).init()
h2 = client.search(text = '"Moon River" Henry Mancini').best.result
print(h2)