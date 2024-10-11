import os
import requests
from aiogram import types
from dispatcher import Dispatcher as dp
from aiogram.fsm.state import StatesGroup, State

class AI(StatesGroup):
    ask_ai = State()


@dp.message_handler(commands=['ask_ai'])
async def process_start_command(message: types.Message):
    await message.answer('Привет! Я ваш виртуальный ассистент, чем могу помочь?')
    await AI.ask_ai.set()

@dp.message_handler(state=AI.ask_ai)
async def process_user_message(message: types.Message):
    answer = await get_gigachat_response(message.text)
    await message.answer(answer) # добавить кнопку выхода из ассистента и смену состояния

async def get_gigachat_response(query):
    url = f'https://api.sber.ai/dialog/v1/chat?access_token={os.environ['TOKEN']}'
    response = requests.post(url, json={'text': query})
    return response.json()['text']