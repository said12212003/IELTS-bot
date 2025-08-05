import json
from openai import OpenAI
from config import openai_api_key, gpt_model

client = OpenAI(api_key=openai_api_key)

def generate_speaking_task():
    messages = [
        {
            "role": "system",
            "content": (
                "You are an IELTS Speaking question generator. "
                "Generate questions for all 3 parts of the IELTS Speaking test. "
                "Return ONLY JSON in this format:\n\n"
                "{\n"
                "  \"part1\": [\"question1\", \"question2\"],\n"
                "  \"part2\": \"cue card topic\",\n"
                "  \"part3\": [\"question1\", \"question2\"]\n"
                "}"
            )
        },
        {"role": "user", "content": "Generate a full IELTS Speaking test."}
    ]

    response = client.chat.completions.create(model=gpt_model, messages=messages)
    content = response.choices[0].message.content.strip()
    return json.loads(content)


def evaluate_general(transcript: str, part: str):
    messages = [
        {"role": "system", "content": "You are a certified IELTS Speaking examiner."},
        {"role": "user", "content": (
            f"Evaluate the following candidate response for IELTS {part}.\n\n"
            f"Transcript:\n{transcript}\n\n"
            f"Give scores (0–10) and short comments for:\n"
            f"- Fluency and Coherence\n"
            f"- Lexical Resource\n"
            f"- Grammatical Range and Accuracy\n"
            f"- Pronunciation (based on transcript only)\n"
            f"- Overall Score (rounded to 1 decimal)"
        )}
    ]
    response = client.chat.completions.create(model=gpt_model, messages=messages)
    return response.choices[0].message.content.strip()
