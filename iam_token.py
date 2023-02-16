from googletrans import Translator
translator = Translator()
result = translator.translate('hello world', src='en', dest='ru')
print(result.text)