PLAYLIST_SIZE = 10


def parseTracks(rawString):  # из сырого ответа нейросети вытаскиваем треки
    # номер точка пробел, в двойных назв трека, пробел тире пробел, имя группы
    result = {}
    rawString = rawString.replace("\n", "")  # убираем \n
    # убираем номер точка пробел
    for n in range(PLAYLIST_SIZE, 0, -1):
        rawString = rawString.replace(str(n)+". ", " -- ")
    rawString = rawString.split(" -- ")[1:]
    # теперь у нас лист из: "автор - трек"
    for i in rawString:
        author, track = i.split(" - ")
        if not author in result:
            result[author] = []
        result[author].append(track)
    return result
