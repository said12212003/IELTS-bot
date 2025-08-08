from openai import OpenAI
import os
# from config import OPENAI_API_KEY, WHISPER_MODEL, LANGUAGE

client = OpenAI(api_key=os.getenv(OPENAI_API_KEY))


def chat_with_gpt(messages: list, model="gpt-3.5-turbo"):
    response = client.chat.completions.create(
        model=model, messages=messages
    )
    return response.choices[0].message.content.strip()


def transcribe_audio(filepath: str, model=os.getenv(WHISPER_MODEL), language=os.getenv(LANGUAGE)) -> str:
    with open(filepath, "rb") as audio_file:
        response = client.audio.transcriptions.create(
            model=model,
            file=audio_file,
            language=language
        )
        return response.text.strip()

