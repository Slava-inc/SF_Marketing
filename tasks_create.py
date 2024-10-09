# Take database class
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from dispatcher import Dispatcher as dp
from keyboard import KeyBoardBot

storage = MemoryStorage()


class Task(StatesGroup):
    goal = State()
    amount = State()
    income = State()
    income_frequency = State()
    duration = State()

    @staticmethod
    def calculate(amount, income, income_frequency, duration):
        total_income = income*income_frequency
        frequency = amount/duration
        return frequency, total_income


@dp.message_handler(commands=['task_create'])
async def goal(message: types.Message):
    await message.reply("Давай определим твою цель! Напиши ее")
    await Task.goal.set()

@dp.message_handler(state=Task.goal)
async def process_amount(message: types.Message, state: FSMContext):
    await state.update_data(goal=message.text)
    await message.reply("Теперь давай сумму, которую ты хочешь накопить")
    await Task.amount.set()

@dp.message_handler(state=Task.amount)
async def process_income(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text)
        await state.update_data(amount=amount)
        await message.reply("Какой твой доход?")
        await Task.income.set()
    except ValueError:
        await message.reply("Пожалуйста, введи число в российских рублях")

@dp.message_handler(state=Task.income)
async def process_frequency(message:types.Message, state:FSMContext):
    try:
        income = float(message.text)
        await state.update_data(income=income)
        await message.reply("Сколько раз в месяц ты получаешь доход?")
        await Task.income_frequency.set()
    except ValueError:
        await message.reply("Пожалуйста, напиши сколько раз в месяц ты получаешь доход")

@dp.message_handler(state=Task.income_frequency)
async def process_income_frequency(message:types.Message, state: FSMContext):
    await state.update_data(income_frequency=message.text)
    await message.reply("Через сколько месяцев ты хочешь накопить эту сумму?")
    await Task.duration.set()

@dp.message_handler(state=Task.duration)
async def process_duration(message: types.Message, state: FSMContext, keyboard: KeyBoardBot):
    try:
        duration = int(message.text)
        await state.update_data(duration=duration)
        data = await state.get_data()

        goal = data.get('goal')
        amount = data.get('amount')
        income = data.get('income')
        income_frequency = data.get('income_frequency')
        duration = data.get('duration')

        frequency, total_income = Task.calculate(amount, income, income_frequency, duration)
        if frequency >= (total_income/2):
            await message.reply(f"Достигнуть цели {goal}, в размере {amount} рублей, за {duration} месяцев, будет очень сложно\n"
                                f"Предлагаю увеличить срок в 2 раза до {2*duration} месяцев")
        else:
            await message.reply(f"Для достижения цели {goal}, в размере{amount} рублей, за {duration} месяцев,\n"
                                f"необходимо откладывать, не менее {frequency} рублей в месяц")
            await message.reply(f"Давай установим напоминание, о дне в который мы будем откладывать деньги")
            # добавить функцию установки напоминания
    except ValueError:
        await message.reply("Пожалуйста, введи число")