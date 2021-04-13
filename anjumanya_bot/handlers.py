from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types.input_file import InputFile


from services import User, Exercise, TrainingData


class InputDataTraining(StatesGroup):
    waiting_for_exercise = State()
    waiting_for_sets = State()
    waiting_for_end = State()


async def input_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    exercises = Exercise.get_exercises_all()
    for e in exercises:
        keyboard.add(e[0])  # название упражнения
    await message.answer("выбери упражнение:", reply_markup=keyboard)
    await InputDataTraining.waiting_for_exercise.set()


async def input_chosen_exercise(message: types.Message, state: FSMContext):
    ex = Exercise.get_exercise(message.text)
    if ex is None:
        await message.answer("мозги не делай, нормально выбери упражнение")
        return

    await state.update_data(exercise=ex.name)
    await state.update_data(type_ex=ex.type)
    if ex.type == "set":
        await message.answer(
            "сколько подходов сделал: ", reply_markup=types.ReplyKeyboardRemove()
        )
        await InputDataTraining.waiting_for_sets.set()
    elif ex.type == "time":
        await message.answer(
            "введи длительность тренировочки в минутах\nнапример 46 сек - 0.46, 1 минута 9 сек - 1.9, 2 часа 5 мин (секунды не надо) - 125",
            reply_markup=types.ReplyKeyboardRemove(),
        )
        await InputDataTraining.waiting_for_end.set()


async def input_chosen_set_or_time(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await InputDataTraining.waiting_for_end.set()
    if data["type_ex"] == "set":
        await state.update_data(sets=message.text)
        await message.answer("сколько повторений сделал в подходе (в среднем мб): ")


async def input_end(message: types.Message, state: FSMContext):
    training_data = await state.get_data()
    if training_data["type_ex"] == "set":
        await state.update_data(rep=message.text)
    elif training_data["type_ex"] == "time":
        await state.update_data(duration_training=message.text)
    training_data = await state.get_data()

    error = TrainingData.data_is_valid(training_data)
    if not error:
        data_for_database = TrainingData.data_for_database
        if TrainingData.add_training_data(message.from_user.id, **data_for_database):
            msg = f"""ты выполнил упражнение \"{training_data['exercise']}\": \n"""
            if training_data["type_ex"] == "set":
                await message.answer(
                    msg
                    + f"""{training_data['sets']} подходов, {training_data['rep']} повторений"""
                )
            elif training_data["type_ex"] == "time":
                await message.answer(
                    msg + f"""длительность: {training_data['duration_training']}"""
                )
            await message.answer("если хош, отправь в чат результаты /send_to_chat")
        else:
            await message.answer("чето не то")
    else:
        await message.answer(error)
    await state.finish()


class GetDataTraining(StatesGroup):
    get_data_training = State()


async def get_data_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    time_intervals = TrainingData.get_time_intervals_all()
    for int in time_intervals:
        keyboard.add(int)
    await message.answer("за какой срок хочешь увидеть свои результаты?", reply_markup=keyboard)
    await GetDataTraining.get_data_training.set()


async def get_data_end(message: types.Message, state: FSMContext):
    check_time_interval = TrainingData.time_interval_exist(message.text)
    if not check_time_interval:
        await message.answer("нормально выбери срок")
        return

    data, type_data = TrainingData.get_data_for_time_interval(message.from_user.id, message.text)
    types_data = TrainingData.TYPE_DATA_OUTPUT
    if type_data == types_data[0]:
        await message.answer_document(data, reply_markup=types.ReplyKeyboardRemove())
    elif type_data == types_data[1]:
        await message.answer(data, parse_mode='HTML', reply_markup=types.ReplyKeyboardRemove())
    else:
        await message.answer("че то нето")
        return

    await state.finish()


async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    if message.text == "/start":
        user = User(
            message.from_user.id,
            message.from_user.username,
            message.from_user.full_name,
        )
        user.registration()

    msg = f"""я бот для анжуманий
ща расскажу че могу:
сари, напиши /input выбираешь упражение, пишешь сколько сделал подходов и повторов и се
если не хочешь добавлять данные пиши /cancel
можешь отправить свои резы в беседу /send_to_chat
можешь их посмотреть /get_data
если хочешь предложить чето новое для бота пиши Сане 
если че то забыл пиши /help
это все, алависта
"""
    await message.answer(msg)


async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("нет так нет", reply_markup=types.ReplyKeyboardRemove())


async def cmd_echo(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("напиши /help и почитай")


def register_handlers(dp: Dispatcher):
    # Основные команды
    dp.register_message_handler(cmd_start, commands=["start", "help"], state="*")
    dp.register_message_handler(cmd_cancel, commands="cancel", state="*")

    # Регистрация обработчиков команды /get_data
    dp.register_message_handler(get_data_start, commands="get_data", state="*")
    dp.register_message_handler(get_data_end, state=GetDataTraining.get_data_training)

    # Регистрация обработчиков команды /input
    dp.register_message_handler(input_start, commands="input", state="*")
    dp.register_message_handler(
        input_chosen_exercise, state=InputDataTraining.waiting_for_exercise
    )
    dp.register_message_handler(
        input_chosen_set_or_time, state=InputDataTraining.waiting_for_sets
    )
    dp.register_message_handler(input_end, state=InputDataTraining.waiting_for_end)

    # Обработчик фигни от пользователя
    dp.register_message_handler(cmd_echo, state="*")

    # dp.register_message_handler(cmd_send_to_chat, commands="send_to_chat", state="*")