import os
from dotenv import load_dotenv


load_dotenv()

your_bot_token = os.getenv("BOT_TOKEN")
openai_api_key = os.getenv("OPENAI_API_KEY")
gpt_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
whisper_model = os.getenv("WHISPER_MODEL", "whisper-1")
language = os.getenv("LANGUAGE", "en")