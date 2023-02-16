import requests

IAM_TOKEN = 't1.9euelZqdz4yUx4nGnprJnpuLys-Omu3rnpWai8-Xzp6LnsmZkp3Lypubi87l8_dWR0Zg-e98dlgo_t3z9xZ2Q2D573x2WCj-.RAQQ7NC4zSty2vay61yg36WKBy9TDRjX6UPDove48DEdZnV0Hpe0ozPCc0jnAtpEhIXmgQ9WizNy6Xnh0WqpBA'
folder_id = 'b1gr9n62s9oofoaj0cke'
target_language = 'ru'
texts = ["Hello World"]

body = {
    "targetLanguageCode": target_language,
    "texts": texts,
    "folderId": folder_id,
}

headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer {0}".format(IAM_TOKEN)
}

response = requests.post('https://translate.api.cloud.yandex.net/translate/v2/translate',
    json = body,
    headers = headers
)

print(response.text)