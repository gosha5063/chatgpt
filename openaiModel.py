import openai
import secret_keys

openai.api_key = secret_keys.openai


def generatePhoto(text, size="1024x1024"):
    try:
        response = openai.Image.create(
            prompt=text,
            n=1,
            size=size
        )
        url = response['data'][0]['url']
        return url

    except openai.error.InvalidRequestError:
        return None


def generateText(text, model="text-davinci-003", temperature=0.8, max_tokens=300):
    response = openai.Completion.create(
        model=model,
        prompt=text,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response['choices'][0]['text']
