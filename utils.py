import io
from pydub import AudioSegment
import speech_recognition as sr
from aiogram.types import Message



async def transcribe_voice_message(bot, message: Message) -> str:
    file = await bot.get_file(message.voice.file_id)
    voice_bytes = await bot.download_file(file.file_path)

    ogg_data = io.BytesIO()
    ogg_data.write(voice_bytes.read())
    ogg_data.seek(0)

    audio = AudioSegment.from_file(ogg_data, format="ogg")
    wav_io = io.BytesIO()
    audio.export(wav_io, format="wav")
    wav_io.seek(0)

    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_io) as source:
        audio_data = recognizer.record(source)
        try:
            return recognizer.recognize_google(audio_data)
        except Exception:
            print(Exception)
            return None