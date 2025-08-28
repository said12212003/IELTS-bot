import io
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import textwrap
import json
from openai import OpenAI
# from config import OPENAI_API_KEY, GPT_MODEL
from openai_client import chat_with_gpt

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def task_generator_data():
    messages = [
        {"role": "system", "content": (
            "You are an IELTS Academic Writing Task 1 generator. "
            "Create a JSON object with the following:\n"
            "{\n"
            "  \"chart_type\": \"bar|pie|line\",\n"
            "  \"title\": \"Chart title\",\n"
            "  \"description\": \"Task prompt\",\n"
            "  \"categories\": [\"A\", \"B\", ...],\n"
            "  \"values\": [Number1, Number2, ...]\n"
            "}\n\n"
            "Respond only with JSON."
        )},
        {"role": "user", "content": "Generate a random chart task."}
    ]

    response = client.chat.completions.create(model=os.getenv("GPT_MODEL"), messages=messages)
    content = response.choices[0].message.content.strip()
    return json.loads(content)


def render_chart_to_memory(data: dict) -> tuple[str, io.BytesIO]:
    chart_type = data["chart_type"]
    title = data["title"]
    description = data["description"]
    categories = data["categories"]
    values = data["values"]

    plt.figure(figsize=(10, 6))

    if chart_type == "bar":
        bars = plt.bar(categories, values, color="skyblue")
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2, height + 0.5, f"{height}", ha="center")
        plt.xlabel("Categories")
        plt.ylabel("Values")

    elif chart_type == "pie":
        plt.pie(values, labels=categories, autopct='%1.1f%%', startangle=140)

    elif chart_type == "line":
        plt.plot(categories, values, marker='o', linestyle='-', color='green')
        plt.xlabel("Time")
        plt.ylabel("Value")
        for i, v in enumerate(values):
            plt.text(i, v + 0.5, str(v), ha="center")

    else:
        raise ValueError("Unsupported chart type")

    plt.title(title)
    wrapped = textwrap.fill(description, width=80)
    plt.figtext(0.5, 0.01, wrapped, ha='center', fontsize=10)
    plt.tight_layout(rect=[0, 0.05, 1, 0.95])

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)
    return description, buf


def writing_task_one_giver_memory():
    data = task_generator_data()
    return render_chart_to_memory(data)


def writing_task_two_generator():
    messages = [
        {"role": "system", "content": (
            "You are an IELTS Writing Task 2 generator. "
            "Your task is to create realistic, original essay prompts for Academic IELTS.\n"
            "Respond ONLY with a JSON object in this structure:\n"
            "{\n"
            "  \"topic\": \"short topic summary\",\n"
            "  \"question\": \"full IELTS Task 2 prompt\"\n"
            "}\n\n"
            "Examples of question:\n"
            "- Some people believe X, while others think Y. Discuss both views and give your opinion.\n"
            "- In some countries, A is increasing. Why is this the case? Is it a positive or negative trend?\n"
            "- Do the advantages of X outweigh the disadvantages?\n\n"
            "Your JSON must be realistic and natural, not repeated."
        )},
        {"role": "user", "content": "Generate one random IELTS Writing Task 2 prompt."}
    ]

    response = client.chat.completions.create(model=os.getenv("GPT_MODEL"), messages=messages)
    content = response.choices[0].message.content.strip()
    return json.loads(content)


def evaluate_given_writing_two(prompt: str, user_essay: str) -> str:
    full_input = (
        f"You are a certified IELTS examiner. Evaluate the following Writing Task 2 response "
        f"based on official IELTS criteria. Use a 1-10-point scale for each band:\n\n"
        f"Task 2 Prompt:\n{prompt}\n\n"
        f"Candidate's Essay:\n{user_essay}\n\n"
        f"Provide evaluation in this format:\n"
        f"- Task Response: (score 0–10) + comment\n"
        f"- Coherence and Cohesion: (score 0–10) + comment\n"
        f"- Lexical Resource: (score 0–10) + comment\n"
        f"- Grammatical Range and Accuracy: (score 0–10) + comment\n"
        f"- Overall Band Score: (rounded to 1 decimal place)"
        f"- give any advices to improve writing."
    )

    messages = [
        {"role": "system", "content": "You are an IELTS Writing examiner."},
        {"role": "user", "content": full_input}
    ]

    return chat_with_gpt(messages)


def evaluate_given_writing(user_essay: str, description: str):
    full_input = (
        f"You are IELTS Writing examiner. Evaluate the following Writing Task 1"
        f"response based on official IELTS criteria, but give scores on a **10-point scale** instead of 9.\n\n"
        f"Task prompt:\n{description}\n\n"
        f"Candidate's response:\n{user_essay}\n\n"
        f"Respond in the following format:\n"
        f"Evaluation:\n"
        f"- Task Response: (score 0–10) + short comment\n"
        f"- Coherence and Cohesion: (score 0–10) + short comment\n"
        f"- Lexical Resource: (score 0–10) + short comment\n"
        f"- Grammatical Range and Accuracy: (score 0–10) + short comment\n"
        f"- Overall Score: (average score rounded to 1 decimal)\n"
    )

    messages = [
        {"role": "system", "content": "You are certified IELTS examiner."},
        {"role": "user", "content": full_input}
    ]

    result = chat_with_gpt(messages)
    return result
