import openai
import secret_keys

openai.api_key = secret_keys.openai

startConversationText = "The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly.\n\nHuman: Hello, who are you?\nAI: I am an AI created by OpenAI. How can I help you today?\nHuman: "


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


def generateText(text, model="text-davinci-003", temperature=0.8, max_tokens=1024):
    response = openai.Completion.create(
        model=model,
        prompt=text,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response['choices'][0]['text']


def continueConversation(prev, question):
    response = generateText(prev+question+"\nAI: ")
    return response
