import io
import os
import json
from gtts import gTTS
from openai import OpenAI
# from config import OPENAI_API_KEY, GPT_MODEL
from aiogram.types import BufferedInputFile

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_listening_test():
    system_prompt = (
        "You are an IELTS Listening test generator. Create a short academic-style listening passage "
        "(around 50–60 seconds when read aloud), and generate 5 multiple-choice questions with 3 options each. "
        "Structure your response strictly in JSON like:\n"
        "{\n"
        "  \"script\": \"...\",\n"
        "  \"questions\": [\n"
        "    {\n"
        "      \"question\": \"...\",\n"
        "      \"options\": [\"A\", \"B\", \"C\"],\n"
        "      \"answer\": \"A\"\n"
        "    }, ...\n"
        "  ]\n"
        "}"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Generate a new IELTS listening task"}
    ]

    response = client.chat.completions.create(
        model=os.getenv("GPT_MODEL"),
        messages=messages
    )

    # Парсинг JSON
    raw = response.choices[0].message.content.strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        raise ValueError("Failed to parse JSON from GPT response.")

    script = data["script"]
    questions = data["questions"]

    # Генерация озвучки
    tts = gTTS(script)
    audio_buffer = io.BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)

    audio_input = BufferedInputFile(audio_buffer.read(), filename="listening.mp3")
    return audio_input, questions
