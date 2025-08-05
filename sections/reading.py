import json
from openai import OpenAI
from config import openai_api_key, gpt_model

client = OpenAI(api_key=openai_api_key)


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

    response = client.chat.completions.create(model=gpt_model, messages=messages)
    content = response.choices[0].message.content.strip()
    return json.loads(content)