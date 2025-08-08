import json
import os

from openai import OpenAI
# from config import OPENAI_API_KEY, GPT_MODEL

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_reading_passage():
    messages = [
        {
            "role": "system",
            "content": (
                "You are an IELTS Reading passage generator."
                "Create a JSON object with a full-IELTS academic-style passage and 10-13 questions."
                "Questions should be of types: multiple choice, true/false/not given, or short answer.\n\n"
                "Respond ONLY with a JSON in this structure:\n"
                "{\n"
                "  \"passage\": \"text of the passage\",\n"
                "  \"questions\": [\n"
                "    {\"question\": \"...\", \"options\": [...], \"answer\": \"...\"},\n"
                "    {\"question\": \"...\", \"answer\": \"...\"},\n"
                "    ...\n"
                "  ]\n"
                "}"
            )
        },
        {"role": "user", "content": "Generate one IELTS Reading passage with questions."}
    ]

    response = client.chat.completions.create(model=os.getenv("GPT_MODEL"), messages=messages)
    content = response.choices[0].message.content.strip()
    return json.loads(content)