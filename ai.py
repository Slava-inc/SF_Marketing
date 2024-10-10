import os
import requests
from aiogram import types
from dispatcher import Dispatcher as dp


@dp.message_handler(commands=['ask_ai'])
async def process_start_command(message: types.Message):
    await message.answer('Привет! Я ваш виртуальный ассистент, чем могу помочь?')

@dp.message_handler()
async def process_user_message(message: types.Message):
    answer = await get_gigachat_response(message.text)
    await message.answer(answer)

async def get_gigachat_response(query):
    url = f'https://api.sber.ai/dialog/v1/chat?access_token={os.environ['TOKEN']}'
    response = requests.post(url, json={'text': query})
    return response.json()['text']