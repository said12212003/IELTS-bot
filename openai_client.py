from openai import OpenAI
from config import openai_api_key, whisper_model, language

client = OpenAI(api_key=openai_api_key)


def chat_with_gpt(messages: list, model="gpt-3.5-turbo"):
    response = client.chat.completions.create(
        model=model, messages=messages
    )
    return response.choices[0].message.content.strip()


def transcribe_audio(filepath: str, model=whisper_model, language=language) -> str:
    with open(filepath, "rb") as audio_file:
        response = client.audio.transcriptions.create(
            model=model,
            file=audio_file,
            language=language
        )
        return response.text.strip()

