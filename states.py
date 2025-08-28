from aiogram.fsm.state import State, StatesGroup


class Writing_State(StatesGroup):
    waiting_for_writing_task_one_response = State()
    waiting_for_writing_task_two_response = State()
    waiting_for_self_writing_task_two_prompt = State()
    waiting_for_self_writing_task_two_response = State()


class Reading_State(StatesGroup):
    waiting_for_reading_answer = State()


class Speaking_State(StatesGroup):
    waiting_for_part_one = State()
    waiting_for_part_two = State()
    waiting_for_part_three = State()


class ListeningState(StatesGroup):
    waiting_for_answer = State()


class RegistrationState(StatesGroup):
    waiting_for_phone_number = State()

