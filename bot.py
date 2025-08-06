import asyncio
import random
import database
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, FSInputFile, BufferedInputFile, InlineKeyboardButton, InlineKeyboardMarkup, BufferedInputFile
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest, TelegramRetryAfter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from config import your_bot_token
from states import Writing_State, Reading_State, Speaking_State, ListeningState, RegistrationState
from sections import writing, reading, speaking, listening
from utils import transcribe_voice_message
from database import get_users_id, remove_user_id

bot = Bot(token=your_bot_token)
dp = Dispatcher(storage=MemoryStorage())


async def main():
    await dp.start_polling(bot)


@dp.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    await message.answer("Please register to use the bot. Send your mobile phone number in a following format "
                         "+998XXYYYYYYY")
    await state.set_state(RegistrationState.waiting_for_phone_number)


@dp.message(RegistrationState.waiting_for_phone_number)
async def processor(message: Message, state: FSMContext):
    phone_number = message.text
    tg_user_id = message.from_user.id

    if database.insert_data(tg_user_id, phone_number) == 200:
        await message.answer("registration has been completed, please use menu button to use the bot")
    else:
        await message.answer("please contact @saidfozil, something went wrong.")

    await state.clear()


@dp.message(F.text == "/satus", F.from_user.id == 771842442)
async def status(message: Message):
    # if message.from_user.id == "771842442":
    await message.answer("ok")
    # else:
    #     await message.answer("for employees only")


@dp.message(F.text == "/broadcast", F.from_user.id == 771842442)
async def broadcast_forwarded_message(message: Message, bot: Bot):
    if not message.reply_to_message:
        await message.answer("❗️Reply to the message you want to broadcast using /broadcast")
        return

    await message.answer("Broadcast has been started")
    source_msg = message.reply_to_message
    user_ids = get_users_id()
    success, failed = 0, 0

    for user_id in user_ids:
        try:
            await bot.copy_message(chat_id=user_id, from_chat_id=source_msg.chat.id, message_id=source_msg.message_id)
            success += 1
            await asyncio.sleep(0.05)
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except (TelegramForbiddenError, TelegramBadRequest):
            remove_user_id(user_id)
            failed += 1

    await message.answer(f"✅ Broadcast completed: {success} sent, {failed} failed.")

# writing


@dp.message(F.text == "/writing1")
async def writing_task(message: Message, state: FSMContext):
    # вызываем генерацию в фоновом потоке
    description, image_buffer = await asyncio.to_thread(writing.writing_task_one_giver_memory)

    # сохраняем описание в состоянии FSM
    await state.set_state(Writing_State.waiting_for_writing_task_one_response)
    await state.update_data(prompt=description)

    # передаём изображение из памяти
    photo = BufferedInputFile(image_buffer.read(), filename="task.png")
    await message.answer_photo(photo=photo, caption=description)


@dp.message(Writing_State.waiting_for_writing_task_one_response)
async def writing_task_one_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    description = data.get("prompt")
    user_essay = message.text

    await message.answer("Please wait while I evaluate your writing...")

    result = await asyncio.to_thread(writing.evaluate_given_writing, user_essay, description)
    await message.answer(result)

    await state.clear()


@dp.message(F.text == "/writing2")
async def writing_task_two(message: Message, state: FSMContext):
    task_data = await asyncio.to_thread(writing.writing_task_two_generator)
    question = task_data["question"]
    topic = task_data["topic"]

    await state.set_state(Writing_State.waiting_for_writing_task_two_response)
    await state.update_data(prompt=question)

    await message.answer(f"📝 **Topic**: {topic}\n\n**Task 2**:\n{question}", parse_mode="Markdown")


@dp.message(Writing_State.waiting_for_writing_task_two_response)
async def writing_task_two_evaluation(message: Message, state: FSMContext):
    data = await state.get_data()
    prompt = data.get("prompt")
    user_essay = message.text

    await message.answer("Evaluating your Task 2 essay, please wait...")

    result = await asyncio.to_thread(writing.evaluate_given_writing_two, prompt, user_essay)
    await message.answer(result)
    await state.clear()


# reading


async def send_next_question(message: Message, state: FSMContext):
    data = await state.get_data()
    questions = data["questions"]
    current = data["current"]

    if current >= len(questions):
        await message.answer(f"✅ Reading completed.\nCorrect answers: {data['correct']} out of {len(questions)}")
        await state.clear()
        return
    q = questions[current]
    text = f"❓ *Question {current + 1}:* {q['question']}"
    if "options" in q:
        text += "\nOptions:\n" + "\n".join(f"-{opt}" for opt in q["questions"])

    await message.answer(text, parse_mode="Markdown")


@dp.message(F.text == "/reading")
async def reading_task(message: Message, state: FSMContext):
    data = await asyncio.to_thread(reading.generate_reading_passage)
    passage = data["passage"]
    questions = data["questions"]

    await state.set_state(Reading_State.waiting_for_reading_answer)
    await state.update_data(questions=questions, current=0, correct=0)

    await message.answer("📘 *Reading Passage:*\n\n" + passage, parse_mode="Markdown")
    await asyncio.sleep(1)
    await send_next_question(message, state)


@dp.message(Reading_State.waiting_for_reading_answer)
async def reading_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    questions = data["questions"]
    current = data["current"]
    user_answer = message.text.strip()
    correct_answer = questions[current]["answer"]

    if user_answer.lower() == correct_answer.lower():
        data["correct"] += 1
        await message.answer("✅ Correct!")
    else:
        await message.answer(f"❌ Incorrect.\nCorrect answer: {correct_answer}")

    data["current"] += 1
    await state.update_data(**data)
    await send_next_question(message, state)


# speaking


@dp.message(F.text == "/speaking")
async def speaking_task(message: Message, state: FSMContext):
    data = await asyncio.to_thread(speaking.generate_speaking_task)

    await state.set_state(Speaking_State.waiting_for_part_one)
    await state.update_data(
        part1=data["part1"],
        part2=data["part2"],
        part3=data["part3"],
        evaluations={}
    )

    qestions = "\n".join(f"- {q}" for q in data["part1"])
    await message.answer(f"🗣 *IELTS Speaking Part 1*\n{qestions}\n\n🎙 Send your voice reply.", parse_mode="Markdown")


@dp.message(Speaking_State.waiting_for_part_one)
@dp.message(Speaking_State.waiting_for_part_two)
@dp.message(Speaking_State.waiting_for_part_three)
async def process_speaking_part(message: Message, state: FSMContext):
    state_data = await state.get_data()
    current_state = await state.get_state()

    transcript = await transcribe_voice_message(bot, message)
    if not transcript:
        await message.answer("❌ Could not recognize your voice.")
        return

    await message.answer(f"📄 *Transcript*:\n{transcript}", parse_mode="Markdown")

    if current_state == Speaking_State.waiting_for_part_one.state:
        result = await asyncio.to_thread(speaking.evaluate_general, transcript, "Part 1")
        state_data["evaluations"]["Part 1"] = result
        await message.answer(f"🧑‍⚖️ *Evaluation Part 1*:\n{result}", parse_mode="Markdown")

        await state.set_state(Speaking_State.waiting_for_part_two)
        await message.answer(f"🗣 *Part 2:* {state_data['part2']}\n🎙 Send your voice reply.")

    elif current_state == Speaking_State.waiting_for_part_two.state:
        result = await asyncio.to_thread(speaking.evaluate_general, transcript, "Part 2")
        state_data["evaluations"]["Part 2"] = result
        await message.answer(f"🧑‍⚖️ *Evaluation Part 2*:\n{result}", parse_mode="Markdown")

        await state.set_state(Speaking_State.waiting_for_part_three)
        q3 = "\n".join(f"- {q}" for q in state_data["part3"])
        await message.answer(f"🗣 *Part 3*:\n{q3}\n🎙 Send your voice reply.")

    elif current_state == Speaking_State.waiting_for_part_three.state:
        result = await asyncio.to_thread(speaking.evaluate_general, transcript, "Part 3")
        state_data["evaluations"]["Part 3"] = result
        await message.answer(f"🧑‍⚖️ *Evaluation Part 3*:\n{result}", parse_mode="Markdown")

        await message.answer("✅ *Speaking session complete.*\nHere's the summary:", parse_mode="Markdown")
        for part, res in state_data["evaluations"].items():
            await message.answer(f"*{part}:*\n{res}", parse_mode="Markdown")

        await state.clear()

#listening


async def finish_listening(message: Message, state: FSMContext):
    data = await state.get_data()
    total = len(data["questions"])
    score = data["correct"]

    await message.answer(f"🎉 You completed the test!\nYour score: {score} / {total}")
    await state.clear()


async def ask_listening_question(message: Message, state: FSMContext):
    data = await state.get_data()
    current = data["current"]
    questions = data["questions"]

    if current >= len(questions):
        return await finish_listening(message, state)

    q = questions[current]
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=opt, callback_data=opt)] for opt in q["options"]
        ]
    )

    await message.answer(
        f"❓ *Q{current + 1}:* {q['question']}",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

    await state.set_state(ListeningState.waiting_for_answer)


@dp.message(F.text == "/listening")
async def start_listening(message: Message, state: FSMContext):
    await message.answer("🎧 Generating your listening task. Please wait...")

    audio, questions = await asyncio.to_thread(listening.generate_listening_test)

    await message.answer_audio(audio, caption="🔊 Listen carefully to the audio.")
    await state.update_data(questions=questions, current=0, correct=0)

    await ask_listening_question(message, state)


@dp.callback_query(ListeningState.waiting_for_answer)
async def process_listening_answer(callback: types.CallbackQuery, state: FSMContext):
    answer = callback.data
    data = await state.get_data()
    current = data["current"]
    q = data["questions"][current]
    correct = data["correct"]

    if answer == q["answer"]:
        correct += 1
        await callback.message.answer("✅ Correct!")
    else:
        await callback.message.answer(f"❌ Incorrect. Correct answer: {q['answer']}")

    await state.update_data(current=current + 1, correct=correct)
    await callback.answer()
    await ask_listening_question(callback.message, state)


# Trigger Scalingo deployment

if __name__ == "__main__":
    asyncio.run(main())
