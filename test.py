<<<<<<< HEAD
import openai

from secret_keys import Model

openai.api_key = Model.open_ai_key
first = openai.Completion.create(
    model= "text-davinci-003",
    prompt= "How to deal with paranoia",
    temperature = 1 ,
    max_tokens=300,

)
first_ans = first['choices'][0]['text']

second = openai.Completion.create(
    model="text-davinci-003",
    prompt=["How to deal with paranoia", first_ans,"I didnt get it"],
    temperature=0.8,
    max_tokens=300,
)
second_ans = second['choices'][0]['text']
third  = openai.Completion.create(
    model="text-davinci-003",
    prompt="How to deal with paranoia" + "I didnt get it" + "does love helpes",
    temperature=0.8,
    max_tokens=300,
)
print(first)
print(second)
print(third)
=======
import dbModel
db = dbModel.DBModel()
db.connect()
db.clearMusicPlayer(0)
db.close()
>>>>>>> dca22e65a94e86e4edbb6424dce1b5bb3e0b47bc
