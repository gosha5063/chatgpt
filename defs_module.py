
def parse_the_responce(response:str):
    treks = response.split()
    treks_dict = {}
    for i in range(1,11):
        title = 'title' + str(i)
        artist = 'artist' + str(i)
        treks_dict[str(i) + '.'] = {title:'', artist:''}
    arr = []
    for trek in range(len(treks)):
        if treks[trek] in treks_dict:
            k = 0
            num = treks[trek]
            for words in range(trek+1,len(treks)):
                if treks[words] not in treks_dict:
                    if k < 2:
                        treks_dict[num] = {
                            "title" + num.replace('.', ''): treks_dict[num]["title" + num.replace('.', '')] + ' ' +
                                                            treks[words],
                            "artist" + num.replace('.', ''): treks_dict[num]["artist" + num.replace('.', '')]}
                    elif treks[words] != 'by' and treks[words] != '-':
                        treks_dict[num] = {
                            "title" + num.replace('.', ''): treks_dict[num]["title" + num.replace('.', '')],
                            "artist" + num.replace('.', ''): treks_dict[num]["artist" + num.replace('.', '')] + ' ' +
                                                               treks[words]}
                    if treks[words][0] == '"' and treks[words][-1] == '"':
                        k += 2
                    elif treks[words][0] == '"' or treks[words][-1] == '"':
                        k += 1

                else:break
    return treks_dict