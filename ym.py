




token = "AQAAAABUEq_5AAG8XleghLapBUvLj7OPKJ2ooDg"
from yandex_music import Client
client =  Client(token).init()
print(client.search(text = " Metallica - Master of Puppets").best)
print(client.search(text = "  Metallica - Nothing Else Matters").best)