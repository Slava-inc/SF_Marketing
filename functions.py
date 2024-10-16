import asyncio
import logging
import re
import os
import phonenumbers
from datetime import date
from dateutil.relativedelta import relativedelta
from keyboard import KeyBoardBot
from database_requests import Execute
from edit_pdf import GetTextOCR
from ai import AI
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery, FSInputFile, ChatPermissions
from aiogram.utils.keyboard import InlineKeyboardMarkup
from aiogram.enums.parse_mode import ParseMode
from aiogram.utils.media_group import MediaGroupBuilder

logging.basicConfig(level=logging.INFO)


class Function:
    def __init__(self, bot, dispatcher):
        self.bot = bot
        self.dispatcher = dispatcher
        self.keyboard = KeyBoardBot()
        self.execute = Execute()
        self.info_pdf = GetTextOCR()
        self.ai = AI(os.environ["TOKEN_SBER"])
        self.dict_user = asyncio.run(self.execute.get_dict_user)
        self.dict_goal = asyncio.run(self.execute.get_dict_goal)

    async def show_back(self, call_back: CallbackQuery):
        try:
            previous_history = self.dict_user[call_back.from_user.id]['history'].pop()
            if self.dict_user[call_back.from_user.id]['history'][-1] == 'start':
                await self.return_start(call_back)
            elif self.dict_user[call_back.from_user.id]['history'][-1] == 'ai':
                await self.show_virtual_assistant(call_back, previous_history)
            elif self.dict_user[call_back.from_user.id]['history'][-1] == 'goal':
                await self.show_add_goal(call_back, previous_history)
            elif self.dict_user[call_back.from_user.id]['history'][-1] == 'outlay':
                await self.show_outlay(call_back, previous_history)
            elif self.dict_user[call_back.from_user.id]['history'][-1] == 'income':
                await self.show_income(call_back, previous_history)
            elif self.dict_user[call_back.from_user.id]['history'][-1] == 'add_goal_name':
                await self.show_add_name_goal(call_back.message, previous_history, call_back)
            elif self.dict_user[call_back.from_user.id]['history'][-1] == 'add_sum_goal':
                await self.show_done_sum_goal(call_back, previous_history)
            elif self.dict_user[call_back.from_user.id]['history'][-1] == 'add_income_user':
                await self.show_done_income_user(call_back, previous_history)
            elif self.dict_user[call_back.from_user.id]['history'][-1] == 'add_income_frequency':
                await self.show_done_income_frequency(call_back, previous_history)
            elif self.dict_user[call_back.from_user.id]['history'][-1] == 'add_duration':
                await self.show_done_duration(call_back, previous_history)
            elif self.dict_user[call_back.from_user.id]['history'][-1] == 'add_reminder_days':
                await self.show_done_reminder_days(call_back, previous_history)
            elif self.dict_user[call_back.from_user.id]['history'][-1] == 'add_reminder_time':
                await self.show_done_reminder_time(call_back, previous_history)
            else:
                await self.return_start(call_back)
            return True
        except IndexError:
            await self.return_start(call_back)
            return True

    async def checking_bot(self, message: Message):
        if message.from_user.is_bot:
            await self.bot.restrict_chat_member(message.chat.id, message.from_user.id, ChatPermissions())
            this_bot = True
        else:
            this_bot = False
        return this_bot

    async def show_virtual_assistant(self, call_back: CallbackQuery, back_history: str = None):
        if back_history is None:
            back_ai = {'back': 'Выйти из виртуального ассистента 🚪'}
            text = 'Привет! Я ваш виртуальный ассистент, чем могу помочь?'
            answer = await self.bot.send_message_news(call_back.message.chat.id, self.build_keyboard(back_ai, 1), text)
            self.dict_user[call_back.from_user.id]['messages'] = await self.delete_messages(
                call_back.from_user.id, self.dict_user[call_back.from_user.id]['messages'])
            self.dict_user[call_back.from_user.id]['messages'].append(str(answer.message_id))
            self.dict_user[call_back.from_user.id]['history'].append('ai')
        else:
            first_keyboard = await self.keyboard.get_first_menu(self.dict_user[call_back.from_user.id]['history'])
            text = f"{self.format_text('Поставить цель 🎯')} - выбрать цель, на которую будем копить!\n" \
                   f"{self.format_text('Расходы 🧮')} - меню учета расходов\n" \
                   f"{self.format_text('Доходы 💰')} - меню учета доходов\n"
            answer = await self.bot.push_photo(call_back.message.chat.id, text,
                                               self.build_keyboard(first_keyboard, 1), self.bot.logo_main_menu)
            self.dict_user[call_back.from_user.id]['messages'] = await self.delete_messages(
                call_back.from_user.id, self.dict_user[call_back.from_user.id]['messages'])
            self.dict_user[call_back.from_user.id]['messages'].append(str(answer.message_id))
        await self.execute.update_user(call_back.from_user.id, self.dict_user[call_back.from_user.id])
        return True

    async def answer_ai(self, message: Message):
        answer_ai = await self.ai.answer_ai(message.text)
        back_ai = {'back': 'Выйти из виртуального ассистента 🚪'}
        answer = await self.answer_message(message, answer_ai, self.build_keyboard(back_ai, 1))
        self.dict_user[message.from_user.id]['messages'].append(str(message.message_id))
        self.dict_user[message.from_user.id]['messages'].append(str(answer.message_id))
        await self.execute.update_user(message.from_user.id, self.dict_user[message.from_user.id])
        return True

    async def show_ok(self, call_back: CallbackQuery):
        self.dict_user[call_back.from_user.id]['messages'] = await self.delete_messages(
            call_back.from_user.id, self.dict_user[call_back.from_user.id]['messages'],
            str(call_back.message.message_id), True)
        await self.execute.update_user(call_back.from_user.id, self.dict_user[call_back.from_user.id])
        return True

    async def show_command_start(self, message: Message):
        check = await self.checking_bot(message)
        if check:
            await self.delete_messages(message.from_user.id, [message.message_id])
        else:
            if message.from_user.id not in self.dict_user.keys():
                self.dict_user[message.from_user.id] = {'history': ['start'], 'messages': [],
                                                        'first_name': message.from_user.first_name,
                                                        'last_name': message.from_user.last_name,
                                                        'user_name': message.from_user.username}
            first_keyboard = await self.keyboard.get_first_menu(self.dict_user[message.from_user.id]['history'])
            text_message = f"{self.format_text('Поставить цель 🎯')} - выбрать цель, на которую будем копить!\n" \
                           f"{self.format_text('Расходы 🧮')} - меню учета расходов\n" \
                           f"{self.format_text('Доходы 💰')} - меню учета доходов\n"
            answer = await self.bot.push_photo(message.chat.id, text_message, self.build_keyboard(first_keyboard, 1),
                                               self.bot.logo_main_menu)
            self.dict_user[message.from_user.id]['messages'].append(str(message.message_id))
            self.dict_user[message.from_user.id]['messages'] = await self.delete_messages(message.from_user.id,
                                                                                          self.dict_user[
                                                                                              message.from_user.id][
                                                                                              'messages'])
            self.dict_user[message.from_user.id]['messages'].append(str(answer.message_id))
            self.dict_user[message.from_user.id]['history'].append('start')
            await self.execute.update_user(message.from_user.id, self.dict_user[message.from_user.id])
        return True

    async def show_command_goal(self, message: Message):
        check = await self.checking_bot(message)
        if check:
            await self.delete_messages(message.from_user.id, [message.message_id])
        else:
            if message.from_user.id not in self.dict_user.keys():
                self.dict_user[message.from_user.id] = {'history': ['start'], 'messages': [],
                                                        'first_name': message.from_user.first_name,
                                                        'last_name': message.from_user.last_name,
                                                        'user_name': message.from_user.username}
            keyboard_goal = await self.keyboard.get_goal_menu()
            text = f"{self.format_text('Добавить новую цель ➕')} - " \
                   f"добавить новую цель, на которую собираетесь копить\n" \
                   f"{self.format_text('Показать список целей 👀')} - показать список уже имеющихся у Вас целей\n"
            answer = await self.bot.push_photo(message.chat.id, text, self.build_keyboard(keyboard_goal, 1),
                                               self.bot.logo_main_menu)
            self.dict_user[message.from_user.id]['messages'].append(str(message.message_id))
            self.dict_user[message.from_user.id]['messages'] = await self.delete_messages(message.from_user.id,
                                                                                          self.dict_user[
                                                                                              message.from_user.id][
                                                                                              'messages'])
            self.dict_user[message.from_user.id]['messages'].append(str(answer.message_id))
            self.dict_user[message.from_user.id]['history'].append('goal')
            await self.execute.update_user(message.from_user.id, self.dict_user[message.from_user.id])
        return True

    async def show_command_outlay(self, message: Message):
        check = await self.checking_bot(message)
        if check:
            await self.delete_messages(message.from_user.id, [message.message_id])
        else:
            if message.from_user.id not in self.dict_user.keys():
                self.dict_user[message.from_user.id] = {'history': ['start'], 'messages': [],
                                                        'first_name': message.from_user.first_name,
                                                        'last_name': message.from_user.last_name,
                                                        'user_name': message.from_user.username}
            keyboard_outlay = await self.keyboard.get_outlay_menu()
            text = f"{self.format_text('Добавить новые расходы ➕')} " \
                   f"- добавьте расходы, отправив файл PDF или вручную\n" \
                   f"{self.format_text('Показать список расходов 👀')} " \
                   f"- вывести на экран список всех расходов за месяц\n" \
                   f"{self.format_text('Аналитика расходов 📊')} - показать распределение расходов по категориям\n" \
                   f"{self.format_text('Изменить категории расходов ⚙')} - изменить список категорий расходов\n" \
                   f"{self.format_text('Назад 🔙')} - вернуться в предыдущее меню\n"
            answer = await self.bot.push_photo(message.chat.id, text, self.build_keyboard(keyboard_outlay, 1),
                                               self.bot.logo_main_menu)
            self.dict_user[message.from_user.id]['messages'].append(str(message.message_id))
            self.dict_user[message.from_user.id]['messages'] = await self.delete_messages(message.from_user.id,
                                                                                          self.dict_user[
                                                                                              message.from_user.id][
                                                                                              'messages'])
            self.dict_user[message.from_user.id]['messages'].append(str(answer.message_id))
            self.dict_user[message.from_user.id]['history'].append('goal')
            await self.execute.update_user(message.from_user.id, self.dict_user[message.from_user.id])
        return True

    async def show_command_income(self, message: Message):
        check = await self.checking_bot(message)
        if check:
            await self.delete_messages(message.from_user.id, [message.message_id])
        else:
            if message.from_user.id not in self.dict_user.keys():
                self.dict_user[message.from_user.id] = {'history': ['start'], 'messages': [],
                                                        'first_name': message.from_user.first_name,
                                                        'last_name': message.from_user.last_name,
                                                        'user_name': message.from_user.username}
            keyboard_income = await self.keyboard.get_income_menu()
            text = f"{self.format_text('Добавить новые доходы ➕')} " \
                   f"- добавьте доходы, отправив файл PDF или вручную\n" \
                   f"{self.format_text('Показать список доходов 👀')} " \
                   f"- вывести на экран список всех доходов за месяц\n" \
                   f"{self.format_text('Аналитика доходов 📊')} - показать распределение доходов по категориям\n" \
                   f"{self.format_text('Изменить категории доходов ⚙')} - изменить список категорий доходов\n" \
                   f"{self.format_text('Назад 🔙')} - вернуться в предыдущее меню\n"
            answer = await self.bot.push_photo(message.chat.id, text, self.build_keyboard(keyboard_income, 1),
                                               self.bot.logo_main_menu)
            self.dict_user[message.from_user.id]['messages'].append(str(message.message_id))
            self.dict_user[message.from_user.id]['messages'] = await self.delete_messages(message.from_user.id,
                                                                                          self.dict_user[
                                                                                              message.from_user.id][
                                                                                              'messages'])
            self.dict_user[message.from_user.id]['messages'].append(str(answer.message_id))
            self.dict_user[message.from_user.id]['history'].append('goal')
            await self.execute.update_user(message.from_user.id, self.dict_user[message.from_user.id])
        return True

    async def return_start(self, call_back: CallbackQuery):
        first_keyboard = await self.keyboard.get_first_menu(self.dict_user[call_back.from_user.id]['history'])
        text = f"{self.format_text('Поставить цель 🎯')} - выбрать цель, на которую будем копить!\n" \
               f"{self.format_text('Расходы 🧮')} - меню учета расходов\n" \
               f"{self.format_text('Доходы 💰')} - меню учета доходов\n"
        answer = await self.bot.push_photo(call_back.message.chat.id, text,
                                           self.build_keyboard(first_keyboard, 1), self.bot.logo_main_menu)
        self.dict_user[call_back.from_user.id]['messages'] = await self.delete_messages(
            call_back.from_user.id, self.dict_user[call_back.from_user.id]['messages'])
        self.dict_user[call_back.from_user.id]['messages'].append(str(answer.message_id))
        await self.execute.update_user(call_back.from_user.id, self.dict_user[call_back.from_user.id])
        return True

    async def send_reminder(self, user_id: int, text_message: str):
        ok_button = {'ок': 'OK 👌'}
        try:
            answer = await self.bot.push_photo(user_id, text_message, self.build_keyboard(ok_button, 1),
                                               self.bot.logo_main_menu)
            self.dict_user[user_id]['messages'].append(str(answer.message_id))
        except TelegramForbiddenError:
            self.dict_user.pop(user_id)

    async def send_recommendation(self, user_id, text_recommendation):
        ok_button = {'ок': 'OK 👌'}
        try:
            answer = await self.bot.push_photo(user_id, text_recommendation, self.build_keyboard(ok_button, 1),
                                               self.bot.logo_main_menu)
            self.dict_user[user_id]['messages'] = await self.delete_messages(user_id,
                                                                             self.dict_user[user_id]['messages'])
            self.dict_user[user_id]['messages'].append(str(answer.message_id))
        except TelegramForbiddenError:
            self.dict_user.pop(user_id)

    async def show_info_pdf(self, user_id: int, text_document: str):
        first_keyboard = await self.keyboard.get_first_menu(self.dict_user[user_id]['history'])
        answer = await self.bot.push_photo(user_id, text_document, self.build_keyboard(first_keyboard, 1),
                                           self.bot.logo_main_menu)
        self.dict_user[user_id]['messages'] = await self.delete_messages(user_id,
                                                                         self.dict_user[user_id]['messages'])
        self.dict_user[user_id]['messages'].append(str(answer.message_id))
        self.dict_user[user_id]['history'].append('start')
        await self.execute.update_user(user_id, self.dict_user[user_id])
        return True

    async def show_goal(self, call_back: CallbackQuery, back_history: str = None):
        if back_history is None:
            keyboard_goal = await self.keyboard.get_goal_menu()
            text = f"{self.format_text('Добавить новую цель ➕')} - " \
                   f"добавить новую цель, на которую собираетесь копить\n" \
                   f"{self.format_text('Показать список целей 👀')} - показать список уже имеющихся у Вас целей\n"
            answer = await self.bot.push_photo(call_back.message.chat.id, text, self.build_keyboard(keyboard_goal, 1),
                                               self.bot.logo_goal_menu)
            self.dict_user[call_back.from_user.id]['messages'] = await self.delete_messages(
                call_back.from_user.id, self.dict_user[call_back.from_user.id]['messages'])
            self.dict_user[call_back.from_user.id]['messages'].append(str(answer.message_id))
            self.dict_user[call_back.from_user.id]['history'].append(call_back.data)
        else:
            first_keyboard = await self.keyboard.get_first_menu(self.dict_user[call_back.from_user.id]['history'])
            text = f"{self.format_text('Поставить цель 🎯')} - выбрать цель, на которую будем копить!\n" \
                   f"{self.format_text('Расходы 🧮')} - меню учета расходов\n" \
                   f"{self.format_text('Доходы 💰')} - меню учета доходов\n"
            answer = await self.bot.push_photo(call_back.message.chat.id, text,
                                               self.build_keyboard(first_keyboard, 1), self.bot.logo_main_menu)
            self.dict_user[call_back.from_user.id]['messages'] = await self.delete_messages(
                call_back.from_user.id, self.dict_user[call_back.from_user.id]['messages'])
            self.dict_user[call_back.from_user.id]['messages'].append(str(answer.message_id))
        await self.execute.update_user(call_back.from_user.id, self.dict_user[call_back.from_user.id])
        return True

    async def show_outlay(self, call_back: CallbackQuery, back_history: str = None):
        if back_history is None:
            keyboard_outlay = await self.keyboard.get_outlay_menu()
            text = f"{self.format_text('Добавить новые расходы ➕')} " \
                   f"- добавьте расходы, отправив файл PDF или вручную\n" \
                   f"{self.format_text('Показать список расходов 👀')} " \
                   f"- вывести на экран список всех расходов за месяц\n" \
                   f"{self.format_text('Аналитика расходов 📊')} - показать распределение расходов по категориям\n" \
                   f"{self.format_text('Изменить категории расходов ⚙')} - изменить список категорий расходов\n" \
                   f"{self.format_text('Назад 🔙')} - вернуться в предыдущее меню\n"
            answer = await self.bot.push_photo(call_back.message.chat.id, text, self.build_keyboard(keyboard_outlay, 1),
                                               self.bot.logo_outlay_menu)
            self.dict_user[call_back.from_user.id]['messages'] = await self.delete_messages(
                call_back.from_user.id, self.dict_user[call_back.from_user.id]['messages'])
            self.dict_user[call_back.from_user.id]['messages'].append(str(answer.message_id))
            self.dict_user[call_back.from_user.id]['history'].append(call_back.data)
        else:
            first_keyboard = await self.keyboard.get_first_menu(self.dict_user[call_back.from_user.id]['history'])
            text = f"{self.format_text('Поставить цель 🎯')} - выбрать цель, на которую будем копить!\n" \
                   f"{self.format_text('Расходы 🧮')} - меню учета расходов\n" \
                   f"{self.format_text('Доходы 💰')} - меню учета доходов\n"
            answer = await self.bot.push_photo(call_back.message.chat.id, text,
                                               self.build_keyboard(first_keyboard, 1), self.bot.logo_main_menu)
            self.dict_user[call_back.from_user.id]['messages'] = await self.delete_messages(
                call_back.from_user.id, self.dict_user[call_back.from_user.id]['messages'])
            self.dict_user[call_back.from_user.id]['messages'].append(str(answer.message_id))
        await self.execute.update_user(call_back.from_user.id, self.dict_user[call_back.from_user.id])
        return True

    async def show_income(self, call_back: CallbackQuery, back_history: str = None):
        if back_history is None:
            keyboard_income = await self.keyboard.get_income_menu()
            text = f"{self.format_text('Добавить новые доходы ➕')} " \
                   f"- добавьте доходы, отправив файл PDF или вручную\n" \
                   f"{self.format_text('Показать список доходов 👀')} " \
                   f"- вывести на экран список всех доходов за месяц\n" \
                   f"{self.format_text('Аналитика доходов 📊')} - показать распределение доходов по категориям\n" \
                   f"{self.format_text('Изменить категории доходов ⚙')} - изменить список категорий доходов\n" \
                   f"{self.format_text('Назад 🔙')} - вернуться в предыдущее меню\n"
            answer = await self.bot.push_photo(call_back.message.chat.id, text, self.build_keyboard(keyboard_income, 1),
                                               self.bot.logo_income_menu)
            self.dict_user[call_back.from_user.id]['messages'] = await self.delete_messages(
                call_back.from_user.id, self.dict_user[call_back.from_user.id]['messages'])
            self.dict_user[call_back.from_user.id]['messages'].append(str(answer.message_id))
            self.dict_user[call_back.from_user.id]['history'].append(call_back.data)
        else:
            first_keyboard = await self.keyboard.get_first_menu(self.dict_user[call_back.from_user.id]['history'])
            text = f"{self.format_text('Поставить цель 🎯')} - выбрать цель, на которую будем копить!\n" \
                   f"{self.format_text('Расходы 🧮')} - меню учета расходов\n" \
                   f"{self.format_text('Доходы 💰')} - меню учета доходов\n"
            answer = await self.bot.push_photo(call_back.message.chat.id, text,
                                               self.build_keyboard(first_keyboard, 1), self.bot.logo_main_menu)
            self.dict_user[call_back.from_user.id]['messages'] = await self.delete_messages(
                call_back.from_user.id, self.dict_user[call_back.from_user.id]['messages'])
            self.dict_user[call_back.from_user.id]['messages'].append(str(answer.message_id))
        await self.execute.update_user(call_back.from_user.id, self.dict_user[call_back.from_user.id])
        return True

    async def show_add_goal(self, call_back: CallbackQuery, back_history: str = None):
        if back_history is None:
            row_id = await self.execute.check_new_goal(call_back.from_user.id)
            if not row_id:
                default_value = {"goal_name": "", "sum_goal": 0, "income_user": 0, "income_frequency": 0, "duration": 0,
                                 "reminder_days": {'MON': 0, 'TUE': 0, 'WED': 0, 'THU': 0, 'FRI': 0, 'SAT': 0,
                                                   'SUN': 0},
                                 'reminder_time': '10:00', 'data_finish': '30-12-31', 'status_goal': 'new'}
                row_id = await self.execute.insert_goal(call_back.from_user.id, default_value)
                default_value['user_id'] = call_back.from_user.id
                self.dict_goal[row_id] = default_value
            keyboard_back = {'back': 'Назад 🔙'}
            text_in_message = 'Давай определим твою цель! Напиши ее ✍'
            text = f"{self.format_text(text_in_message)} - отправь боту сообщение с названием твоей будущей цели, " \
                   f"например, <code>Автомобиль</code>"
            await self.bot.edit_head_caption(text, call_back.message.chat.id,
                                             self.dict_user[call_back.from_user.id]['messages'][-1],
                                             self.build_keyboard(keyboard_back, 1))
            self.dict_user[call_back.from_user.id]['history'].append('add_goal_name')
        else:
            keyboard_goal = await self.keyboard.get_goal_menu()
            text = f"{self.format_text('Добавить новую цель ➕')} " \
                   f"- добавить новую цель, на которую собираетесь копить\n" \
                   f"{self.format_text('Показать список целей 👀')} - показать список уже имеющихся у Вас целей\n"
            if back_history == 'add_goal_name':
                await self.edit_caption(call_back.message, text, self.build_keyboard(keyboard_goal, 1))
            else:
                answer = await self.bot.push_photo(call_back.message.chat.id, text,
                                                   self.build_keyboard(keyboard_goal, 1), self.bot.logo_goal_menu)
                self.dict_user[call_back.from_user.id]['messages'] = await self.delete_messages(
                    call_back.from_user.id, self.dict_user[call_back.from_user.id]['messages'])
                self.dict_user[call_back.from_user.id]['messages'].append(str(answer.message_id))
        await self.execute.update_user(call_back.from_user.id, self.dict_user[call_back.from_user.id])
        return True

    async def show_add_name_goal(self, message: Message, back_history: str = None, call_back: CallbackQuery = None):
        if back_history is None:
            user_id = message.from_user.id
            row_id = await self.execute.check_new_goal(user_id)
            check_name_goal = await self.check_text(message.text)
            await self.bot.delete_messages_chat(message.chat.id, [message.message_id])
            if not check_name_goal:
                goal_name = ""
                self.dict_goal[row_id]['goal_name'] = goal_name
                keyboard_back = {'back': 'Назад 🔙'}
                text_in_message = 'Наименование цели должно содержать хотя бы одну букву или цифру!'
                text = f"{self.format_text(text_in_message)} - отправь боту сообщение с названием " \
                       f"твоей будущей цели, например, <code>Автомобиль</code>"
                try:
                    await self.bot.edit_head_caption(text, user_id,
                                                     self.dict_user[user_id]['messages'][-1],
                                                     self.build_keyboard(keyboard_back, 1))
                    await self.execute.update_goal(row_id, self.dict_goal[row_id])
                except TelegramBadRequest:
                    await self.execute.update_goal(row_id, self.dict_goal[row_id])
            else:
                goal_name = check_name_goal
                self.dict_goal[row_id]['goal_name'] = goal_name
                sum_goal = '0'
                self.dict_goal[row_id]['sum_goal'] = float(sum_goal)
                keyboard_calculater = await self.keyboard.get_calculater()
                button_done = {'done_sum_goal': 'Готово ✅'}
                text_in_message = 'Теперь нужна сумма, которую Вы хотите накопить 💸'
                text = f"Наименование цели: {self.format_text(goal_name)}\n" \
                       f"{self.format_text(text_in_message)} - введите сумму в рублях, " \
                       f"которую планируете накопить для достижения цели\n" \
                       f"Сумма цели: {self.format_text(sum_goal)} ₽"
                await self.bot.edit_head_caption(text, user_id,
                                                 self.dict_user[user_id]['messages'][-1],
                                                 self.build_keyboard(keyboard_calculater, 3, button_done))
                self.dict_user[user_id]['history'].append("add_sum_goal")
        else:
            user_id = call_back.from_user.id
            row_id = await self.execute.check_new_goal(user_id)
            self.dict_goal[row_id]['goal_name'] = ""
            keyboard_back = {'back': 'Назад 🔙'}
            text_in_message = 'Давай определим твою цель! Напиши ее ✍'
            text = f"{self.format_text(text_in_message)} - отправь боту сообщение с названием твоей будущей цели, " \
                   f"например, <code>Автомобиль</code>"
            if back_history == 'add_sum_goal':
                await self.bot.edit_head_caption(text, user_id,
                                                 self.dict_user[user_id]['messages'][-1],
                                                 self.build_keyboard(keyboard_back, 1))
            else:
                answer = await self.bot.push_photo(user_id, text,
                                                   self.build_keyboard(keyboard_back, 1),
                                                   self.bot.logo_goal_menu)
                self.dict_user[user_id]['messages'] = await self.delete_messages(
                    user_id, self.dict_user[user_id]['messages'])
                self.dict_user[user_id]['messages'].append(str(answer.message_id))
        await self.execute.update_user(user_id, self.dict_user[user_id])
        return True

    async def show_change(self, call_back: CallbackQuery):
        if self.dict_user[call_back.from_user.id]['history'][-1] == 'add_sum_goal':
            await self.change_sum_goal(call_back)
        elif self.dict_user[call_back.from_user.id]['history'][-1] == 'add_income_user':
            await self.change_income_user(call_back)
        elif self.dict_user[call_back.from_user.id]['history'][-1] == 'add_income_frequency':
            await self.change_income_frequency(call_back)
        elif self.dict_user[call_back.from_user.id]['history'][-1] == 'add_duration':
            await self.change_duration(call_back)
        else:
            print(f"Калькулятор там, где не нужно: {self.dict_user[call_back.from_user.id]['history'][-1]}")
        return True

    async def change_sum_goal(self, call_back: CallbackQuery):
        row_id = await self.execute.check_new_goal(call_back.from_user.id)
        name_goal = self.dict_goal[row_id]['goal_name']
        amount = await self.get_amount(call_back.message.caption, call_back.data, 'Сумма цели: ', ' ₽')
        self.dict_goal[row_id]['sum_goal'] = float(amount)
        keyboard_calculater = await self.keyboard.get_calculater()
        button_done = {'done_sum_goal': 'Готово ✅'}
        text = f"Наименование цели: {self.format_text(name_goal)}\n" \
               f"{self.format_text('Теперь нужна сумма, которую Вы хотите накопить 💸')} - введите сумму в рублях, " \
               f"которую планируете накопить для достижения цели\n" \
               f"Сумма цели: {self.format_text(str(amount))} ₽"
        try:
            await self.bot.edit_head_caption(text, call_back.message.chat.id,
                                             self.dict_user[call_back.from_user.id]['messages'][-1],
                                             self.build_keyboard(keyboard_calculater, 3, button_done))
            await self.execute.update_goal(row_id, self.dict_goal[row_id])
        except TelegramBadRequest:
            await self.execute.update_goal(row_id, self.dict_goal[row_id])

    async def change_income_user(self, call_back: CallbackQuery):
        row_id = await self.execute.check_new_goal(call_back.from_user.id)
        name_goal = self.dict_goal[row_id]['goal_name']
        sum_goal = str(int(self.dict_goal[row_id]['sum_goal']))
        amount = await self.get_amount(call_back.message.caption, call_back.data, 'Ваш доход: ', ' ₽')
        self.dict_goal[row_id]['income_user'] = float(amount)
        keyboard_calculater = await self.keyboard.get_calculater()
        button_done = {'done_income_user': 'Готово ✅'}
        text = f"Наименование цели: {self.format_text(name_goal)}\n" \
               f"Сумма цели: {self.format_text(sum_goal)} ₽\n" \
               f"{self.format_text('Укажите Ваш доход 💰')} - введите доход в рублях.\n" \
               f"Ваш доход: {self.format_text(amount)} ₽"
        try:
            await self.bot.edit_head_caption(text, call_back.message.chat.id,
                                             self.dict_user[call_back.from_user.id]['messages'][-1],
                                             self.build_keyboard(keyboard_calculater, 3, button_done))
            await self.execute.update_goal(row_id, self.dict_goal[row_id])
        except TelegramBadRequest:
            await self.execute.update_goal(row_id, self.dict_goal[row_id])

    async def change_income_frequency(self, call_back: CallbackQuery):
        row_id = await self.execute.check_new_goal(call_back.from_user.id)
        name_goal = self.dict_goal[row_id]['goal_name']
        sum_goal = str(int(self.dict_goal[row_id]['sum_goal']))
        income_user = str(int(self.dict_goal[row_id]['income_user']))
        frequency = await self.get_amount(call_back.message.caption, call_back.data, 'Количество поступлений в месяц: ')
        self.dict_goal[row_id]['income_frequency'] = int(frequency)
        keyboard_calculater = await self.keyboard.get_calculater()
        button_done = {'done_income_frequency': 'Готово ✅'}
        text = f"Наименование цели: {self.format_text(name_goal)}\n" \
               f"Сумма цели: {self.format_text(sum_goal)} ₽\n" \
               f"Ваш доход: {self.format_text(income_user)} ₽\n" \
               f"{self.format_text('Пожалуйста, укажите сколько раз в месяц Вы получаете доход.')}\n" \
               f"Количество поступлений в месяц: {self.format_text(frequency)}"
        try:
            await self.bot.edit_head_caption(text, call_back.message.chat.id,
                                             self.dict_user[call_back.from_user.id]['messages'][-1],
                                             self.build_keyboard(keyboard_calculater, 3, button_done))
            await self.execute.update_goal(row_id, self.dict_goal[row_id])
        except TelegramBadRequest:
            await self.execute.update_goal(row_id, self.dict_goal[row_id])

    async def change_duration(self, call_back: CallbackQuery):
        row_id = await self.execute.check_new_goal(call_back.from_user.id)
        name_goal = self.dict_goal[row_id]['goal_name']
        sum_goal = str(int(self.dict_goal[row_id]['sum_goal']))
        income_user = str(int(self.dict_goal[row_id]['income_user']))
        income_frequency = str(int(self.dict_goal[row_id]['income_frequency']))
        duration = await self.get_amount(call_back.message.caption, call_back.data, 'Срок достижения цели: ', ' мес.')
        if int(duration) == 0:
            monthly_payment = '0'
        else:
            monthly_payment = str(int(int(self.dict_goal[row_id]['sum_goal']) / int(duration)))
        self.dict_goal[row_id]['duration'] = int(duration)
        keyboard_calculater = await self.keyboard.get_calculater()
        button_done = {'done_duration': 'Готово ✅'}
        text_in_message = 'Через сколько месяцев ты хочешь накопить эту сумму? Помни, что месячный платеж не должен ' \
                          'превышать 50% от твоего совокупного дохода!'
        text = f"Наименование цели: {self.format_text(name_goal)}\n" \
               f"Сумма цели: {self.format_text(sum_goal)} ₽\n" \
               f"Ваш доход: {self.format_text(income_user)} ₽\n" \
               f"Количество поступлений: {self.format_text(income_frequency)}\n" \
               f"{self.format_text(text_in_message)}\n" \
               f"Срок достижения цели: {self.format_text(duration)} мес.\n" \
               f"Каждый месяц нужно откладывать: {self.format_text(monthly_payment)} ₽"
        try:
            await self.bot.edit_head_caption(text, call_back.message.chat.id,
                                             self.dict_user[call_back.from_user.id]['messages'][-1],
                                             self.build_keyboard(keyboard_calculater, 3, button_done))
            await self.execute.update_goal(row_id, self.dict_goal[row_id])
        except TelegramBadRequest:
            await self.execute.update_goal(row_id, self.dict_goal[row_id])

    async def show_minus(self, call_back: CallbackQuery):
        if self.dict_user[call_back.from_user.id]['history'][-1] == 'add_sum_goal':
            await self.minus_sum_goal(call_back)
        elif self.dict_user[call_back.from_user.id]['history'][-1] == 'add_income_user':
            await self.minus_income_user(call_back)
        elif self.dict_user[call_back.from_user.id]['history'][-1] == 'add_income_frequency':
            await self.minus_income_frequency(call_back)
        elif self.dict_user[call_back.from_user.id]['history'][-1] == 'add_duration':
            await self.minus_duration(call_back)
        else:
            print(f"Калькулятор там, где не нужно: {self.dict_user[call_back.from_user.id]['history'][-1]}")
        return True

    async def minus_sum_goal(self, call_back: CallbackQuery):
        row_id = await self.execute.check_new_goal(call_back.from_user.id)
        name_goal = self.dict_goal[row_id]['goal_name']
        amount = await self.get_amount_minus(call_back.message.caption, 'Сумма цели: ', ' ₽')
        self.dict_goal[row_id]['sum_goal'] = float(amount)
        keyboard_calculater = await self.keyboard.get_calculater()
        button_done = {'done_sum_goal': 'Готово ✅'}
        text = f"Наименование цели: {self.format_text(name_goal)}\n" \
               f"{self.format_text('Теперь нужна сумма, которую Вы хотите накопить 💸')} - введите сумму в рублях, " \
               f"которую планируете накопить для достижения цели\n" \
               f"Сумма цели: {self.format_text(str(amount))} ₽"
        try:
            await self.bot.edit_head_caption(text, call_back.message.chat.id,
                                             self.dict_user[call_back.from_user.id]['messages'][-1],
                                             self.build_keyboard(keyboard_calculater, 3, button_done))
            await self.execute.update_goal(row_id, self.dict_goal[row_id])
        except TelegramBadRequest:
            await self.execute.update_goal(row_id, self.dict_goal[row_id])

    async def minus_income_user(self, call_back: CallbackQuery):
        row_id = await self.execute.check_new_goal(call_back.from_user.id)
        name_goal = self.dict_goal[row_id]['goal_name']
        sum_goal = str(int(self.dict_goal[row_id]['sum_goal']))
        amount = await self.get_amount_minus(call_back.message.caption, 'Ваш доход: ', ' ₽')
        self.dict_goal[row_id]['income_user'] = float(amount)
        keyboard_calculater = await self.keyboard.get_calculater()
        button_done = {'done_income_user': 'Готово ✅'}
        text = f"Наименование цели: {self.format_text(name_goal)}\n" \
               f"Сумма цели: {self.format_text(sum_goal)} ₽\n" \
               f"{self.format_text('Укажите Ваш доход 💰')} - введите доход в рублях.\n" \
               f"Ваш доход: {self.format_text(amount)} ₽"
        try:
            await self.bot.edit_head_caption(text, call_back.message.chat.id,
                                             self.dict_user[call_back.from_user.id]['messages'][-1],
                                             self.build_keyboard(keyboard_calculater, 3, button_done))
            await self.execute.update_goal(row_id, self.dict_goal[row_id])
        except TelegramBadRequest:
            await self.execute.update_goal(row_id, self.dict_goal[row_id])

    async def minus_income_frequency(self, call_back: CallbackQuery):
        row_id = await self.execute.check_new_goal(call_back.from_user.id)
        name_goal = self.dict_goal[row_id]['goal_name']
        sum_goal = str(int(self.dict_goal[row_id]['sum_goal']))
        income_user = str(int(self.dict_goal[row_id]['income_user']))
        frequency = await self.get_amount_minus(call_back.message.caption,  'Количество поступлений в месяц: ')
        self.dict_goal[row_id]['income_frequency'] = int(frequency)
        keyboard_calculater = await self.keyboard.get_calculater()
        button_done = {'done_income_frequency': 'Готово ✅'}
        text = f"Наименование цели: {self.format_text(name_goal)}\n" \
               f"Сумма цели: {self.format_text(sum_goal)} ₽\n" \
               f"Ваш доход: {self.format_text(income_user)} ₽\n" \
               f"{self.format_text('Пожалуйста, укажите сколько раз в месяц Вы получаете доход.')}\n" \
               f"Количество поступлений в месяц: {self.format_text(frequency)}"
        try:
            await self.bot.edit_head_caption(text, call_back.message.chat.id,
                                             self.dict_user[call_back.from_user.id]['messages'][-1],
                                             self.build_keyboard(keyboard_calculater, 3, button_done))
            await self.execute.update_goal(row_id, self.dict_goal[row_id])
        except TelegramBadRequest:
            await self.execute.update_goal(row_id, self.dict_goal[row_id])

    async def minus_duration(self, call_back: CallbackQuery):
        row_id = await self.execute.check_new_goal(call_back.from_user.id)
        name_goal = self.dict_goal[row_id]['goal_name']
        sum_goal = str(int(self.dict_goal[row_id]['sum_goal']))
        income_user = str(int(self.dict_goal[row_id]['income_user']))
        income_frequency = str(int(self.dict_goal[row_id]['income_frequency']))
        duration = await self.get_amount_minus(call_back.message.caption,  'Срок достижения цели: ', ' мес.')
        if int(duration) == 0:
            monthly_payment = '0'
        else:
            monthly_payment = str(int(int(self.dict_goal[row_id]['sum_goal']) / int(duration)))
        self.dict_goal[row_id]['duration'] = int(duration)
        keyboard_calculater = await self.keyboard.get_calculater()
        button_done = {'done_duration': 'Готово ✅'}
        text_in_message = 'Через сколько месяцев ты хочешь накопить эту сумму? Помни, что месячный платеж не должен ' \
                          'превышать 50% от твоего совокупного дохода!'
        text = f"Наименование цели: {self.format_text(name_goal)}\n" \
               f"Сумма цели: {self.format_text(sum_goal)} ₽\n" \
               f"Ваш доход: {self.format_text(income_user)} ₽\n" \
               f"Количество поступлений: {self.format_text(income_frequency)}\n" \
               f"{self.format_text(text_in_message)}\n" \
               f"Срок достижения цели: {self.format_text(duration)} мес.\n" \
               f"Каждый месяц нужно откладывать: {self.format_text(monthly_payment)} ₽"
        try:
            await self.bot.edit_head_caption(text, call_back.message.chat.id,
                                             self.dict_user[call_back.from_user.id]['messages'][-1],
                                             self.build_keyboard(keyboard_calculater, 3, button_done))
            await self.execute.update_goal(row_id, self.dict_goal[row_id])
        except TelegramBadRequest:
            await self.execute.update_goal(row_id, self.dict_goal[row_id])

    async def show_plus(self, call_back: CallbackQuery):
        if self.dict_user[call_back.from_user.id]['history'][-1] == 'add_sum_goal':
            await self.plus_sum_goal(call_back)
        elif self.dict_user[call_back.from_user.id]['history'][-1] == 'add_income_user':
            await self.plus_income_user(call_back)
        elif self.dict_user[call_back.from_user.id]['history'][-1] == 'add_income_frequency':
            await self.plus_income_frequency(call_back)
        elif self.dict_user[call_back.from_user.id]['history'][-1] == 'add_duration':
            await self.plus_duration(call_back)
        else:
            print(f"Калькулятор там, где не нужно: {self.dict_user[call_back.from_user.id]['history'][-1]}")
        return True

    async def plus_sum_goal(self, call_back: CallbackQuery):
        row_id = await self.execute.check_new_goal(call_back.from_user.id)
        name_goal = self.dict_goal[row_id]['goal_name']
        amount = await self.get_amount_plus(call_back.message.caption, 'Сумма цели: ', ' ₽')
        self.dict_goal[row_id]['sum_goal'] = float(amount)
        keyboard_calculater = await self.keyboard.get_calculater()
        button_done = {'done_sum_goal': 'Готово ✅'}
        text = f"Наименование цели: {self.format_text(name_goal)}\n" \
               f"{self.format_text('Теперь нужна сумма, которую Вы хотите накопить 💸')} - введите сумму в рублях, " \
               f"которую планируете накопить для достижения цели\n" \
               f"Сумма цели: {self.format_text(str(amount))} ₽"
        try:
            await self.bot.edit_head_caption(text, call_back.message.chat.id,
                                             self.dict_user[call_back.from_user.id]['messages'][-1],
                                             self.build_keyboard(keyboard_calculater, 3, button_done))
            await self.execute.update_goal(row_id, self.dict_goal[row_id])
        except TelegramBadRequest:
            await self.execute.update_goal(row_id, self.dict_goal[row_id])

    async def plus_income_user(self, call_back: CallbackQuery):
        row_id = await self.execute.check_new_goal(call_back.from_user.id)
        name_goal = self.dict_goal[row_id]['goal_name']
        sum_goal = str(int(self.dict_goal[row_id]['sum_goal']))
        amount = await self.get_amount_plus(call_back.message.caption, 'Ваш доход: ', ' ₽')
        self.dict_goal[row_id]['income_user'] = float(amount)
        keyboard_calculater = await self.keyboard.get_calculater()
        button_done = {'done_income_user': 'Готово ✅'}
        text = f"Наименование цели: {self.format_text(name_goal)}\n" \
               f"Сумма цели: {self.format_text(sum_goal)} ₽\n" \
               f"{self.format_text('Укажите Ваш доход 💰')} - введите доход в рублях.\n" \
               f"Ваш доход: {self.format_text(amount)} ₽"
        try:
            await self.bot.edit_head_caption(text, call_back.message.chat.id,
                                             self.dict_user[call_back.from_user.id]['messages'][-1],
                                             self.build_keyboard(keyboard_calculater, 3, button_done))
            await self.execute.update_goal(row_id, self.dict_goal[row_id])
        except TelegramBadRequest:
            await self.execute.update_goal(row_id, self.dict_goal[row_id])

    async def plus_income_frequency(self, call_back: CallbackQuery):
        row_id = await self.execute.check_new_goal(call_back.from_user.id)
        name_goal = self.dict_goal[row_id]['goal_name']
        sum_goal = str(int(self.dict_goal[row_id]['sum_goal']))
        income_user = str(int(self.dict_goal[row_id]['income_user']))
        frequency = await self.get_amount_plus(call_back.message.caption, 'Количество поступлений в месяц: ')
        self.dict_goal[row_id]['income_frequency'] = int(frequency)
        keyboard_calculater = await self.keyboard.get_calculater()
        button_done = {'done_income_frequency': 'Готово ✅'}
        text = f"Наименование цели: {self.format_text(name_goal)}\n" \
               f"Сумма цели: {self.format_text(sum_goal)} ₽\n" \
               f"Ваш доход: {self.format_text(income_user)} ₽\n" \
               f"{self.format_text('Пожалуйста, укажите сколько раз в месяц Вы получаете доход.')}\n" \
               f"Количество поступлений в месяц: {self.format_text(frequency)}"
        try:
            await self.bot.edit_head_caption(text, call_back.message.chat.id,
                                             self.dict_user[call_back.from_user.id]['messages'][-1],
                                             self.build_keyboard(keyboard_calculater, 3, button_done))
            await self.execute.update_goal(row_id, self.dict_goal[row_id])
        except TelegramBadRequest:
            await self.execute.update_goal(row_id, self.dict_goal[row_id])

    async def plus_duration(self, call_back: CallbackQuery):
        row_id = await self.execute.check_new_goal(call_back.from_user.id)
        name_goal = self.dict_goal[row_id]['goal_name']
        sum_goal = str(int(self.dict_goal[row_id]['sum_goal']))
        income_user = str(int(self.dict_goal[row_id]['income_user']))
        income_frequency = str(int(self.dict_goal[row_id]['income_frequency']))
        duration = await self.get_amount_plus(call_back.message.caption, 'Срок достижения цели: ', ' мес.')
        if int(duration) == 0:
            monthly_payment = '0'
        else:
            monthly_payment = str(int(int(self.dict_goal[row_id]['sum_goal']) / int(duration)))
        self.dict_goal[row_id]['duration'] = int(duration)
        keyboard_calculater = await self.keyboard.get_calculater()
        button_done = {'done_duration': 'Готово ✅'}
        text_in_message = 'Через сколько месяцев ты хочешь накопить эту сумму? Помни, что месячный платеж не должен ' \
                          'превышать 50% от твоего совокупного дохода!'
        text = f"Наименование цели: {self.format_text(name_goal)}\n" \
               f"Сумма цели: {self.format_text(sum_goal)} ₽\n" \
               f"Ваш доход: {self.format_text(income_user)} ₽\n" \
               f"Количество поступлений: {self.format_text(income_frequency)}\n" \
               f"{self.format_text(text_in_message)}\n" \
               f"Срок достижения цели: {self.format_text(duration)} мес.\n" \
               f"Каждый месяц нужно откладывать: {self.format_text(monthly_payment)} ₽"
        try:
            await self.bot.edit_head_caption(text, call_back.message.chat.id,
                                             self.dict_user[call_back.from_user.id]['messages'][-1],
                                             self.build_keyboard(keyboard_calculater, 3, button_done))
            await self.execute.update_goal(row_id, self.dict_goal[row_id])
        except TelegramBadRequest:
            await self.execute.update_goal(row_id, self.dict_goal[row_id])

    async def show_delete(self, call_back: CallbackQuery):
        if self.dict_user[call_back.from_user.id]['history'][-1] == 'add_sum_goal':
            await self.delete_sum_goal(call_back)
        elif self.dict_user[call_back.from_user.id]['history'][-1] == 'add_income_user':
            await self.delete_income_user(call_back)
        elif self.dict_user[call_back.from_user.id]['history'][-1] == 'add_income_frequency':
            await self.delete_income_frequency(call_back)
        elif self.dict_user[call_back.from_user.id]['history'][-1] == 'add_duration':
            await self.delete_duration(call_back)
        else:
            print(f"Калькулятор там, где не нужно: {self.dict_user[call_back.from_user.id]['history'][-1]}")
        return True

    async def delete_sum_goal(self, call_back: CallbackQuery):
        row_id = await self.execute.check_new_goal(call_back.from_user.id)
        name_goal = self.dict_goal[row_id]['goal_name']
        amount = await self.get_amount_delete(call_back.message.caption, 'Сумма цели: ', ' ₽')
        self.dict_goal[row_id]['sum_goal'] = float(amount)
        keyboard_calculater = await self.keyboard.get_calculater()
        button_done = {'done_sum_goal': 'Готово ✅'}
        text = f"Наименование цели: {self.format_text(name_goal)}\n" \
               f"{self.format_text('Теперь нужна сумма, которую Вы хотите накопить 💸')} - введите сумму в рублях, " \
               f"которую планируете накопить для достижения цели\n" \
               f"Сумма цели: {self.format_text(str(amount))} ₽"
        try:
            await self.bot.edit_head_caption(text, call_back.message.chat.id,
                                             self.dict_user[call_back.from_user.id]['messages'][-1],
                                             self.build_keyboard(keyboard_calculater, 3, button_done))
            await self.execute.update_goal(row_id, self.dict_goal[row_id])
        except TelegramBadRequest:
            await self.execute.update_goal(row_id, self.dict_goal[row_id])

    async def delete_income_user(self, call_back: CallbackQuery):
        row_id = await self.execute.check_new_goal(call_back.from_user.id)
        name_goal = self.dict_goal[row_id]['goal_name']
        sum_goal = str(int(self.dict_goal[row_id]['sum_goal']))
        amount = await self.get_amount_delete(call_back.message.caption, 'Ваш доход: ', ' ₽')
        self.dict_goal[row_id]['income_user'] = float(amount)
        keyboard_calculater = await self.keyboard.get_calculater()
        button_done = {'done_income_user': 'Готово ✅'}
        text = f"Наименование цели: {self.format_text(name_goal)}\n" \
               f"Сумма цели: {self.format_text(sum_goal)} ₽\n" \
               f"{self.format_text('Укажите Ваш доход 💰')} - введите доход в рублях.\n" \
               f"Ваш доход: {self.format_text(amount)} ₽"
        try:
            await self.bot.edit_head_caption(text, call_back.message.chat.id,
                                             self.dict_user[call_back.from_user.id]['messages'][-1],
                                             self.build_keyboard(keyboard_calculater, 3, button_done))
            await self.execute.update_goal(row_id, self.dict_goal[row_id])
        except TelegramBadRequest:
            await self.execute.update_goal(row_id, self.dict_goal[row_id])

    async def delete_income_frequency(self, call_back: CallbackQuery):
        row_id = await self.execute.check_new_goal(call_back.from_user.id)
        name_goal = self.dict_goal[row_id]['goal_name']
        sum_goal = str(int(self.dict_goal[row_id]['sum_goal']))
        income_user = str(int(self.dict_goal[row_id]['income_user']))
        frequency = await self.get_amount_delete(call_back.message.caption, 'Количество поступлений в месяц: ')
        self.dict_goal[row_id]['income_frequency'] = int(frequency)
        keyboard_calculater = await self.keyboard.get_calculater()
        button_done = {'done_income_frequency': 'Готово ✅'}
        text = f"Наименование цели: {self.format_text(name_goal)}\n" \
               f"Сумма цели: {self.format_text(sum_goal)} ₽\n" \
               f"Ваш доход: {self.format_text(income_user)} ₽\n" \
               f"{self.format_text('Пожалуйста, укажите сколько раз в месяц Вы получаете доход.')}\n" \
               f"Количество поступлений в месяц: {self.format_text(frequency)}"
        try:
            await self.bot.edit_head_caption(text, call_back.message.chat.id,
                                             self.dict_user[call_back.from_user.id]['messages'][-1],
                                             self.build_keyboard(keyboard_calculater, 3, button_done))
            await self.execute.update_goal(row_id, self.dict_goal[row_id])
        except TelegramBadRequest:
            await self.execute.update_goal(row_id, self.dict_goal[row_id])

    async def delete_duration(self, call_back: CallbackQuery):
        row_id = await self.execute.check_new_goal(call_back.from_user.id)
        name_goal = self.dict_goal[row_id]['goal_name']
        sum_goal = str(int(self.dict_goal[row_id]['sum_goal']))
        income_user = str(int(self.dict_goal[row_id]['income_user']))
        income_frequency = str(int(self.dict_goal[row_id]['income_frequency']))
        duration = await self.get_amount_delete(call_back.message.caption, 'Срок достижения цели: ', ' мес.')
        if int(duration) == 0:
            monthly_payment = '0'
        else:
            monthly_payment = str(int(int(self.dict_goal[row_id]['sum_goal']) / int(duration)))
        self.dict_goal[row_id]['duration'] = int(duration)
        keyboard_calculater = await self.keyboard.get_calculater()
        button_done = {'done_duration': 'Готово ✅'}
        text_in_message = 'Через сколько месяцев ты хочешь накопить эту сумму? Помни, что месячный платеж не должен ' \
                          'превышать 50% от твоего совокупного дохода!'
        text = f"Наименование цели: {self.format_text(name_goal)}\n" \
               f"Сумма цели: {self.format_text(sum_goal)} ₽\n" \
               f"Ваш доход: {self.format_text(income_user)} ₽\n" \
               f"Количество поступлений: {self.format_text(income_frequency)}\n" \
               f"{self.format_text(text_in_message)}\n" \
               f"Срок достижения цели: {self.format_text(duration)} мес.\n" \
               f"Каждый месяц нужно откладывать: {self.format_text(monthly_payment)} ₽"
        try:
            await self.bot.edit_head_caption(text, call_back.message.chat.id,
                                             self.dict_user[call_back.from_user.id]['messages'][-1],
                                             self.build_keyboard(keyboard_calculater, 3, button_done))
            await self.execute.update_goal(row_id, self.dict_goal[row_id])
        except TelegramBadRequest:
            await self.execute.update_goal(row_id, self.dict_goal[row_id])

    async def show_done_sum_goal(self, call_back: CallbackQuery, back_history: str = None):
        row_id = await self.execute.check_new_goal(call_back.from_user.id)
        name_goal = self.dict_goal[row_id]['goal_name']
        sum_goal = int(self.dict_goal[row_id]['sum_goal'])
        if back_history is None:
            check_sum_goal = await self.check_sum(call_back, sum_goal,
                                                  f"Сумма цели не может быть равна {str(sum_goal)} рублей")
            if not check_sum_goal:
                sum_goal = '0'
                self.dict_goal[row_id]['sum_goal'] = float(sum_goal)
                keyboard_calculater = await self.keyboard.get_calculater()
                button_done = {'done_sum_goal': 'Готово ✅'}
                text_in_message = 'Теперь нужна сумма, которую Вы хотите накопить 💸'
                text = f"Наименование цели: {self.format_text(name_goal)}\n" \
                       f"{self.format_text(text_in_message)} - введите сумму в рублях, " \
                       f"которую планируете накопить для достижения цели\n" \
                       f"Сумма цели: {self.format_text(sum_goal)} ₽"
                try:
                    await self.bot.edit_head_caption(text, call_back.message.chat.id,
                                                     self.dict_user[call_back.from_user.id]['messages'][-1],
                                                     self.build_keyboard(keyboard_calculater, 3, button_done))
                    await self.execute.update_goal(row_id, self.dict_goal[row_id])
                except TelegramBadRequest:
                    await self.execute.update_goal(row_id, self.dict_goal[row_id])
            else:
                income_user = '0'
                self.dict_goal[row_id]['income_user'] = float(income_user)
                keyboard_calculater = await self.keyboard.get_calculater()
                button_done = {'done_income_user': 'Готово ✅'}
                text_in_message = 'Укажите Ваш доход 💰'
                text = f"Наименование цели: {self.format_text(name_goal)}\n" \
                       f"Сумма цели: {self.format_text(str(sum_goal))} ₽\n" \
                       f"{self.format_text(text_in_message)} - введите доход в рублях.\n" \
                       f"Ваш доход: {self.format_text(income_user)} ₽"
                await self.bot.edit_head_caption(text, call_back.message.chat.id,
                                                 self.dict_user[call_back.from_user.id]['messages'][-1],
                                                 self.build_keyboard(keyboard_calculater, 3, button_done))
                self.dict_user[call_back.from_user.id]['history'].append("add_income_user")
        else:
            keyboard_calculater = await self.keyboard.get_calculater()
            button_done = {'done_sum_goal': 'Готово ✅'}
            text_in_message = 'Теперь нужна сумма, которую Вы хотите накопить 💸'
            text = f"Наименование цели: {self.format_text(name_goal)}\n" \
                   f"{self.format_text(text_in_message)} - введите сумму в рублях, " \
                   f"которую планируете накопить для достижения цели\n" \
                   f"Сумма цели: {self.format_text(str(sum_goal))} ₽"
            if back_history == 'add_income_user':
                await self.bot.edit_head_caption(text, call_back.message.chat.id,
                                                 self.dict_user[call_back.from_user.id]['messages'][-1],
                                                 self.build_keyboard(keyboard_calculater, 3, button_done))
            else:
                answer = await self.bot.push_photo(call_back.message.chat.id, text,
                                                   self.build_keyboard(keyboard_calculater, 3, button_done),
                                                   self.bot.logo_goal_menu)
                self.dict_user[call_back.from_user.id]['messages'] = await self.delete_messages(
                    call_back.from_user.id, self.dict_user[call_back.from_user.id]['messages'])
                self.dict_user[call_back.from_user.id]['messages'].append(str(answer.message_id))
        await self.execute.update_user(call_back.from_user.id, self.dict_user[call_back.from_user.id])
        return True

    async def show_done_income_user(self, call_back: CallbackQuery, back_history: str = None):
        row_id = await self.execute.check_new_goal(call_back.from_user.id)
        name_goal = self.dict_goal[row_id]['goal_name']
        sum_goal = str(int(self.dict_goal[row_id]['sum_goal']))
        income_user = int(self.dict_goal[row_id]['income_user'])
        if back_history is None:
            check_sum_goal = await self.check_sum(call_back, income_user,
                                                  f"Ваш доход не может быть равен {str(income_user)} рублей")
            if not check_sum_goal:
                income_user = '0'
                self.dict_goal[row_id]['income_user'] = float(income_user)
                keyboard_calculater = await self.keyboard.get_calculater()
                button_done = {'done_income_user': 'Готово ✅'}
                text_in_message = 'Укажите Ваш доход 💰'
                text = f"Наименование цели: {self.format_text(name_goal)}\n" \
                       f"Сумма цели: {self.format_text(sum_goal)} ₽\n" \
                       f"{self.format_text(text_in_message)} - введите доход в рублях.\n" \
                       f"Ваш доход: {self.format_text(income_user)} ₽"
                try:
                    await self.bot.edit_head_caption(text, call_back.message.chat.id,
                                                     self.dict_user[call_back.from_user.id]['messages'][-1],
                                                     self.build_keyboard(keyboard_calculater, 3, button_done))
                    await self.execute.update_goal(row_id, self.dict_goal[row_id])
                except TelegramBadRequest:
                    await self.execute.update_goal(row_id, self.dict_goal[row_id])
            else:
                income_frequency = '0'
                self.dict_goal[row_id]['income_frequency'] = int(income_frequency)
                keyboard_calculater = await self.keyboard.get_calculater()
                button_done = {'done_income_frequency': 'Готово ✅'}
                text_in_message = 'Пожалуйста, укажите сколько раз в месяц Вы получаете доход.'
                text = f"Наименование цели: {self.format_text(name_goal)}\n" \
                       f"Сумма цели: {self.format_text(sum_goal)} ₽\n" \
                       f"Ваш доход: {self.format_text(str(income_user))} ₽\n" \
                       f"{self.format_text(text_in_message)}\n" \
                       f"Количество поступлений в месяц: {self.format_text(income_frequency)}"
                await self.bot.edit_head_caption(text, call_back.message.chat.id,
                                                 self.dict_user[call_back.from_user.id]['messages'][-1],
                                                 self.build_keyboard(keyboard_calculater, 3, button_done))
                self.dict_user[call_back.from_user.id]['history'].append("add_income_frequency")
        else:
            keyboard_calculater = await self.keyboard.get_calculater()
            button_done = {'done_income_user': 'Готово ✅'}
            text_in_message = 'Укажите Ваш доход 💰'
            text = f"Наименование цели: {self.format_text(name_goal)}\n" \
                   f"Сумма цели: {self.format_text(sum_goal)} ₽\n" \
                   f"{self.format_text(text_in_message)} - введите доход в рублях.\n" \
                   f"Ваш доход: {self.format_text(str(income_user))} ₽"
            if back_history == 'add_income_frequency':
                await self.bot.edit_head_caption(text, call_back.message.chat.id,
                                                 self.dict_user[call_back.from_user.id]['messages'][-1],
                                                 self.build_keyboard(keyboard_calculater, 3, button_done))
            else:
                answer = await self.bot.push_photo(call_back.message.chat.id, text,
                                                   self.build_keyboard(keyboard_calculater, 3, button_done),
                                                   self.bot.logo_goal_menu)
                self.dict_user[call_back.from_user.id]['messages'] = await self.delete_messages(
                    call_back.from_user.id, self.dict_user[call_back.from_user.id]['messages'])
                self.dict_user[call_back.from_user.id]['messages'].append(str(answer.message_id))
        await self.execute.update_user(call_back.from_user.id, self.dict_user[call_back.from_user.id])
        return True

    async def show_done_income_frequency(self, call_back: CallbackQuery, back_history: str = None):
        row_id = await self.execute.check_new_goal(call_back.from_user.id)
        name_goal = self.dict_goal[row_id]['goal_name']
        sum_goal = str(int(self.dict_goal[row_id]['sum_goal']))
        income_user = str(int(self.dict_goal[row_id]['income_user']))
        income_frequency = int(self.dict_goal[row_id]['income_frequency'])
        if back_history is None:
            check_frequency = await self.check_sum(call_back, self.dict_goal[row_id]['income_frequency'],
                                                   f'Количество поступлений доходов не может быть равно '
                                                   f'{str(income_frequency)}')
            if not check_frequency:
                income_frequency = '0'
                self.dict_goal[row_id]['income_frequency'] = income_frequency
                keyboard_calculater = await self.keyboard.get_calculater()
                button_done = {'done_income_frequency': 'Готово ✅'}
                text_in_message = 'Пожалуйста, укажите сколько раз в месяц Вы получаете доход.'
                text = f"Наименование цели: {self.format_text(name_goal)}\n" \
                       f"Сумма цели: {self.format_text(sum_goal)} ₽\n" \
                       f"Ваш доход: {self.format_text(income_user)} ₽\n" \
                       f"{self.format_text(text_in_message)}\n" \
                       f"Количество поступлений в месяц: {self.format_text(income_frequency)}"
                try:
                    await self.bot.edit_head_caption(text, call_back.message.chat.id,
                                                     self.dict_user[call_back.from_user.id]['messages'][-1],
                                                     self.build_keyboard(keyboard_calculater, 3, button_done))
                    await self.execute.update_goal(row_id, self.dict_goal[row_id])
                except TelegramBadRequest:
                    await self.execute.update_goal(row_id, self.dict_goal[row_id])
            else:
                duration = '0'
                monthly_payment = '0'
                self.dict_goal[row_id]['duration'] = int(duration)
                keyboard_calculater = await self.keyboard.get_calculater()
                button_done = {'done_duration': 'Готово ✅'}
                text_in_message = 'Через сколько месяцев ты хочешь накопить эту сумму? Помни, что месячный платеж ' \
                                  'не должен превышать 50% от твоего совокупного дохода!'
                text = f"Наименование цели: {self.format_text(name_goal)}\n" \
                       f"Сумма цели: {self.format_text(sum_goal)} ₽\n" \
                       f"Ваш доход: {self.format_text(income_user)} ₽\n" \
                       f"Количество поступлений: {self.format_text(str(income_frequency))}\n" \
                       f"{self.format_text(text_in_message)}\n" \
                       f"Срок достижения цели: {self.format_text(duration)} мес.\n" \
                       f"Каждый месяц нужно откладывать: {self.format_text(monthly_payment)} ₽"
                await self.bot.edit_head_caption(text, call_back.message.chat.id,
                                                 self.dict_user[call_back.from_user.id]['messages'][-1],
                                                 self.build_keyboard(keyboard_calculater, 3, button_done))
                self.dict_user[call_back.from_user.id]['history'].append("add_duration")
        else:
            keyboard_calculater = await self.keyboard.get_calculater()
            button_done = {'done_income_frequency': 'Готово ✅'}
            text_in_message = 'Пожалуйста, укажите сколько раз в месяц Вы получаете доход.'
            text = f"Наименование цели: {self.format_text(name_goal)}\n" \
                   f"Сумма цели: {self.format_text(sum_goal)} ₽\n" \
                   f"Ваш доход: {self.format_text(income_user)} ₽\n" \
                   f"{self.format_text(text_in_message)}\n" \
                   f"Количество поступлений в месяц: {self.format_text(str(income_frequency))}"
            if back_history == 'add_duration':
                await self.bot.edit_head_caption(text, call_back.message.chat.id,
                                                 self.dict_user[call_back.from_user.id]['messages'][-1],
                                                 self.build_keyboard(keyboard_calculater, 3, button_done))
            else:
                answer = await self.bot.push_photo(call_back.message.chat.id, text,
                                                   self.build_keyboard(keyboard_calculater, 3, button_done),
                                                   self.bot.logo_goal_menu)
                self.dict_user[call_back.from_user.id]['messages'] = await self.delete_messages(
                    call_back.from_user.id, self.dict_user[call_back.from_user.id]['messages'])
                self.dict_user[call_back.from_user.id]['messages'].append(str(answer.message_id))
        await self.execute.update_user(call_back.from_user.id, self.dict_user[call_back.from_user.id])
        return True

    async def show_done_duration(self, call_back: CallbackQuery, back_history: str = None):
        row_id = await self.execute.check_new_goal(call_back.from_user.id)
        name_goal = self.dict_goal[row_id]['goal_name']
        sum_goal = str(int(self.dict_goal[row_id]['sum_goal']))
        income_user = str(int(self.dict_goal[row_id]['income_user']))
        income_frequency = str(int(self.dict_goal[row_id]['income_frequency']))
        duration = self.dict_goal[row_id]['duration']
        if int(duration) == 0:
            monthly_payment = '0'
        else:
            monthly_payment = str(int(int(self.dict_goal[row_id]['sum_goal']) / int(duration)))
        if back_history is None:
            check_payment = await self.check_duration(call_back, self.dict_goal[row_id])
            if not check_payment:
                duration = '0'
                monthly_payment = '0'
                self.dict_goal[row_id]['duration'] = int(duration)
                keyboard_calculater = await self.keyboard.get_calculater()
                button_done = {'done_duration': 'Готово ✅'}
                text_in_message = 'Через сколько месяцев ты хочешь накопить эту сумму? Помни, что месячный платеж ' \
                                  'не должен превышать 50% от твоего совокупного дохода!'
                text = f"Наименование цели: {self.format_text(name_goal)}\n" \
                       f"Сумма цели: {self.format_text(sum_goal)} ₽\n" \
                       f"Ваш доход: {self.format_text(income_user)} ₽\n" \
                       f"Количество поступлений: {self.format_text(income_frequency)}\n" \
                       f"{self.format_text(text_in_message)}\n" \
                       f"Срок достижения цели: {self.format_text(duration)} мес.\n" \
                       f"Каждый месяц нужно откладывать: {self.format_text(monthly_payment)} ₽"
                try:
                    await self.bot.edit_head_caption(text, call_back.message.chat.id,
                                                     self.dict_user[call_back.from_user.id]['messages'][-1],
                                                     self.build_keyboard(keyboard_calculater, 3, button_done))
                    await self.execute.update_goal(row_id, self.dict_goal[row_id])
                except TelegramBadRequest:
                    await self.execute.update_goal(row_id, self.dict_goal[row_id])
            else:
                self.dict_goal[row_id]['reminder_days'] = {'MON': 0, 'TUE': 0, 'WED': 0, 'THU': 0, 'FRI': 0, 'SAT': 0,
                                                           'SUN': 0}
                weekday = await self.get_str_weekday(self.dict_goal[row_id]['reminder_days'])
                keyboard_weekday = await self.keyboard.get_weekday()
                button_done = {'done_reminder_days': 'Готово ✅'}
                text_in_message = 'Давайте установим, в какие дни недели получать напоминание о цели.'
                text = f"Наименование цели: {self.format_text(name_goal)}\n" \
                       f"Сумма цели: {self.format_text(sum_goal)} ₽\n" \
                       f"Ваш доход: {self.format_text(income_user)} ₽\n" \
                       f"Количество поступлений: {self.format_text(income_frequency)}\n" \
                       f"Срок достижения цели: {self.format_text(str(duration))} мес.\n" \
                       f"Каждый месяц нужно откладывать: {self.format_text(str(monthly_payment))} ₽\n" \
                       f"{self.format_text(text_in_message)}\n" \
                       f"Дни напоминания о цели: {self.format_text(weekday)}"
                await self.bot.edit_head_caption(text, call_back.message.chat.id,
                                                 self.dict_user[call_back.from_user.id]['messages'][-1],
                                                 self.build_keyboard(keyboard_weekday, 3, button_done))
                self.dict_user[call_back.from_user.id]['history'].append("add_reminder_days")
        else:
            keyboard_calculater = await self.keyboard.get_calculater()
            button_done = {'done_duration': 'Готово ✅'}
            text_in_message = 'Через сколько месяцев ты хочешь накопить эту сумму? Помни, что месячный платеж ' \
                              'не должен превышать 50% от твоего совокупного дохода!'
            text = f"Наименование цели: {self.format_text(name_goal)}\n" \
                   f"Сумма цели: {self.format_text(sum_goal)} ₽\n" \
                   f"Ваш доход: {self.format_text(income_user)} ₽\n" \
                   f"Количество поступлений: {self.format_text(income_frequency)}\n" \
                   f"{self.format_text(text_in_message)}\n" \
                   f"Срок достижения цели: {self.format_text(str(duration))} мес.\n" \
                   f"Каждый месяц нужно откладывать: {self.format_text(str(monthly_payment))} ₽"
            if back_history == 'add_reminder_days':
                await self.bot.edit_head_caption(text, call_back.message.chat.id,
                                                 self.dict_user[call_back.from_user.id]['messages'][-1],
                                                 self.build_keyboard(keyboard_calculater, 3, button_done))
            else:
                answer = await self.bot.push_photo(call_back.message.chat.id, text,
                                                   self.build_keyboard(keyboard_calculater, 3, button_done),
                                                   self.bot.logo_goal_menu)
                self.dict_user[call_back.from_user.id]['messages'] = await self.delete_messages(
                    call_back.from_user.id, self.dict_user[call_back.from_user.id]['messages'])
                self.dict_user[call_back.from_user.id]['messages'].append(str(answer.message_id))
        await self.execute.update_user(call_back.from_user.id, self.dict_user[call_back.from_user.id])
        return True

    async def show_weekday(self, call_back: CallbackQuery):
        row_id = await self.execute.check_new_goal(call_back.from_user.id)
        name_goal = self.dict_goal[row_id]['goal_name']
        sum_goal = str(int(self.dict_goal[row_id]['sum_goal']))
        income_user = str(int(self.dict_goal[row_id]['income_user']))
        income_frequency = str(int(self.dict_goal[row_id]['income_frequency']))
        duration = str(int(self.dict_goal[row_id]['duration']))
        monthly_payment = str(int(int(self.dict_goal[row_id]['sum_goal']) / int(duration)))
        if self.dict_goal[row_id]['reminder_days'][call_back.data]:
            self.dict_goal[row_id]['reminder_days'][call_back.data] = 0
        else:
            self.dict_goal[row_id]['reminder_days'][call_back.data] = 1
        weekday = await self.get_str_weekday(self.dict_goal[row_id]['reminder_days'])
        keyboard_weekday = await self.keyboard.get_weekday()
        button_done = {'done_reminder_days': 'Готово ✅'}
        text_in_message = 'Давайте установим, в какие дни недели получать напоминание о цели.'
        text = f"Наименование цели: {self.format_text(name_goal)}\n" \
               f"Сумма цели: {self.format_text(sum_goal)} ₽\n" \
               f"Ваш доход: {self.format_text(income_user)} ₽\n" \
               f"Количество поступлений: {self.format_text(income_frequency)}\n" \
               f"Срок достижения цели: {self.format_text(duration)} мес.\n" \
               f"Каждый месяц нужно откладывать: {self.format_text(monthly_payment)} ₽\n" \
               f"{self.format_text(text_in_message)}\n" \
               f"Дни напоминания о цели: {self.format_text(weekday)}"
        try:
            await self.bot.edit_head_caption(text, call_back.message.chat.id,
                                             self.dict_user[call_back.from_user.id]['messages'][-1],
                                             self.build_keyboard(keyboard_weekday, 3, button_done))
            await self.execute.update_goal(row_id, self.dict_goal[row_id])
            return True
        except TelegramBadRequest:
            await self.execute.update_goal(row_id, self.dict_goal[row_id])
            return True

    async def show_done_reminder_days(self, call_back: CallbackQuery, back_history: str = None):
        row_id = await self.execute.check_new_goal(call_back.from_user.id)
        name_goal = self.dict_goal[row_id]['goal_name']
        sum_goal = str(int(self.dict_goal[row_id]['sum_goal']))
        income_user = str(int(self.dict_goal[row_id]['income_user']))
        income_frequency = str(int(self.dict_goal[row_id]['income_frequency']))
        duration = str(int(self.dict_goal[row_id]['duration']))
        monthly_payment = str(int(int(self.dict_goal[row_id]['sum_goal']) / int(duration)))
        weekday = await self.get_str_weekday(self.dict_goal[row_id]['reminder_days'])
        if back_history is None:
            if weekday == 'Не напоминать о цели':
                time_reminder = 'Не напоминать о цели'
            else:
                time_reminder = '10:00'
            self.dict_goal[row_id]['reminder_time'] = time_reminder
            keyboard_time = await self.keyboard.get_time_reminder()
            button_done = {'done_reminder_time': 'Готово ✅'}
            text_in_message = 'Установите, в какое время будет удобно получать напоминание о цели.'
            text = f"Наименование цели: {self.format_text(name_goal)}\n" \
                   f"Сумма цели: {self.format_text(sum_goal)} ₽\n" \
                   f"Ваш доход: {self.format_text(income_user)} ₽\n" \
                   f"Количество поступлений: {self.format_text(income_frequency)}\n" \
                   f"Срок достижения цели: {self.format_text(duration)} мес.\n" \
                   f"Каждый месяц нужно откладывать: {self.format_text(monthly_payment)} ₽\n" \
                   f"Дни напоминания о цели: {self.format_text(weekday)}\n" \
                   f"{self.format_text(text_in_message)}\n" \
                   f"Время напоминания о цели: {self.format_text(time_reminder)}"
            await self.bot.edit_head_caption(text, call_back.message.chat.id,
                                             self.dict_user[call_back.from_user.id]['messages'][-1],
                                             self.build_keyboard(keyboard_time, 5, button_done))
            self.dict_user[call_back.from_user.id]['history'].append("add_reminder_time")
        else:
            keyboard_weekday = await self.keyboard.get_weekday()
            button_done = {'done_reminder_days': 'Готово ✅'}
            text_in_message = 'Давайте установим, в какие дни недели получать напоминание о цели.'
            text = f"Наименование цели: {self.format_text(name_goal)}\n" \
                   f"Сумма цели: {self.format_text(sum_goal)} ₽\n" \
                   f"Ваш доход: {self.format_text(income_user)} ₽\n" \
                   f"Количество поступлений: {self.format_text(income_frequency)}\n" \
                   f"Срок достижения цели: {self.format_text(duration)} мес.\n" \
                   f"Каждый месяц нужно откладывать: {self.format_text(monthly_payment)} ₽\n" \
                   f"{self.format_text(text_in_message)}\n" \
                   f"Дни напоминания о цели: {self.format_text(weekday)}"
            if back_history == 'add_reminder_time':
                await self.bot.edit_head_caption(text, call_back.message.chat.id,
                                                 self.dict_user[call_back.from_user.id]['messages'][-1],
                                                 self.build_keyboard(keyboard_weekday, 3, button_done))
            else:
                answer = await self.bot.push_photo(call_back.message.chat.id, text,
                                                   self.build_keyboard(keyboard_weekday, 3, button_done),
                                                   self.bot.logo_goal_menu)
                self.dict_user[call_back.from_user.id]['messages'] = await self.delete_messages(
                    call_back.from_user.id, self.dict_user[call_back.from_user.id]['messages'])
                self.dict_user[call_back.from_user.id]['messages'].append(str(answer.message_id))
        await self.execute.update_user(call_back.from_user.id, self.dict_user[call_back.from_user.id])
        return True

    async def show_reminder_time(self, call_back: CallbackQuery):
        row_id = await self.execute.check_new_goal(call_back.from_user.id)
        name_goal = self.dict_goal[row_id]['goal_name']
        sum_goal = str(int(self.dict_goal[row_id]['sum_goal']))
        income_user = str(int(self.dict_goal[row_id]['income_user']))
        income_frequency = str(int(self.dict_goal[row_id]['income_frequency']))
        duration = str(int(self.dict_goal[row_id]['duration']))
        monthly_payment = str(int(int(self.dict_goal[row_id]['sum_goal']) / int(duration)))
        weekday = await self.get_str_weekday(self.dict_goal[row_id]['reminder_days'])
        time_reminder = call_back.data
        self.dict_goal[row_id]['reminder_time'] = time_reminder
        keyboard_time = await self.keyboard.get_time_reminder()
        button_done = {'done_reminder_time': 'Готово ✅'}
        text_in_message = 'Установите, в какое время будет удобно получать напоминание о цели.'
        text = f"Наименование цели: {self.format_text(name_goal)}\n" \
               f"Сумма цели: {self.format_text(sum_goal)} ₽\n" \
               f"Ваш доход: {self.format_text(income_user)} ₽\n" \
               f"Количество поступлений: {self.format_text(income_frequency)}\n" \
               f"Срок достижения цели: {self.format_text(duration)} мес.\n" \
               f"Каждый месяц нужно откладывать: {self.format_text(monthly_payment)} ₽\n" \
               f"Дни напоминания о цели: {self.format_text(weekday)}\n" \
               f"{self.format_text(text_in_message)}\n" \
               f"Время напоминания о цели: {self.format_text(time_reminder)}"
        try:
            await self.bot.edit_head_caption(text, call_back.message.chat.id,
                                             self.dict_user[call_back.from_user.id]['messages'][-1],
                                             self.build_keyboard(keyboard_time, 5, button_done))
            await self.execute.update_goal(row_id, self.dict_goal[row_id])
            return True
        except TelegramBadRequest:
            await self.execute.update_goal(row_id, self.dict_goal[row_id])
            return True

    async def show_done_reminder_time(self, call_back: CallbackQuery, back_history: str = None):
        row_id = await self.execute.check_new_goal(call_back.from_user.id)
        name_goal = self.dict_goal[row_id]['goal_name']
        sum_goal = str(int(self.dict_goal[row_id]['sum_goal']))
        income_user = str(int(self.dict_goal[row_id]['income_user']))
        income_frequency = str(int(self.dict_goal[row_id]['income_frequency']))
        duration = int(self.dict_goal[row_id]['duration'])
        monthly_payment = str(int(int(self.dict_goal[row_id]['sum_goal']) / int(duration)))
        weekday = await self.get_str_weekday(self.dict_goal[row_id]['reminder_days'])
        time_reminder = self.dict_goal[row_id]['reminder_time']
        if back_history is None:
            current_date = date.today()
            future_date = str(current_date + relativedelta(months=+duration))
            self.dict_goal[row_id]['data_finish'] = future_date
            data_in_message = f"{self.format_text(future_date.split('-')[2])}." \
                              f"{self.format_text(future_date.split('-')[1])}." \
                              f"{self.format_text(future_date.split('-')[0])} г."
            self.dict_goal[row_id]['status_goal'] = 'current'
            await self.execute.update_goal(row_id, self.dict_goal[row_id])
            text = f"{self.format_text('Добавлена новая цель:')}\n" \
                   f"Наименование цели: {self.format_text(name_goal)}\n" \
                   f"Сумма цели: {self.format_text(sum_goal)} ₽\n" \
                   f"Ваш доход: {self.format_text(income_user)} ₽\n" \
                   f"Количество поступлений: {self.format_text(income_frequency)}\n" \
                   f"Срок достижения цели: {self.format_text(str(duration))} мес.\n" \
                   f"Каждый месяц нужно откладывать: {self.format_text(monthly_payment)} ₽\n" \
                   f"Дни напоминания о цели: {self.format_text(weekday)}\n" \
                   f"Время напоминания о цели: {self.format_text(time_reminder)}\n" \
                   f"Цель рассчитана до: {self.format_text(data_in_message)}"
            self.dict_user[call_back.from_user.id]['history'] = ['start']
            first_keyboard = await self.keyboard.get_first_menu(self.dict_user[call_back.from_user.id]['history'])
            await self.bot.edit_head_caption(text, call_back.message.chat.id,
                                             self.dict_user[call_back.from_user.id]['messages'][-1],
                                             self.build_keyboard(first_keyboard, 1))
            await self.dispatcher.scheduler.add_new_reminder(row_id, self.dict_goal[row_id])
        else:
            keyboard_time = await self.keyboard.get_time_reminder()
            button_done = {'done_reminder_time': 'Готово ✅'}
            text_in_message = 'Установите, в какое время будет удобно получать напоминание о цели.'
            text = f"Наименование цели: {self.format_text(name_goal)}\n" \
                   f"Сумма цели: {self.format_text(sum_goal)} ₽\n" \
                   f"Ваш доход: {self.format_text(income_user)} ₽\n" \
                   f"Количество поступлений: {self.format_text(income_frequency)}\n" \
                   f"Срок достижения цели: {self.format_text(str(duration))} мес.\n" \
                   f"Каждый месяц нужно откладывать: {self.format_text(monthly_payment)} ₽\n" \
                   f"Дни напоминания о цели: {self.format_text(weekday)}\n" \
                   f"{self.format_text(text_in_message)}\n" \
                   f"Время напоминания о цели: {self.format_text(time_reminder)}"

            answer = await self.bot.push_photo(call_back.message.chat.id, text,
                                               self.build_keyboard(keyboard_time, 5, button_done),
                                               self.bot.logo_goal_menu)
            self.dict_user[call_back.from_user.id]['messages'] = await self.delete_messages(
                call_back.from_user.id, self.dict_user[call_back.from_user.id]['messages'])
            self.dict_user[call_back.from_user.id]['messages'].append(str(answer.message_id))
        await self.execute.update_user(call_back.from_user.id, self.dict_user[call_back.from_user.id])
        return True

    async def get_document(self, message: Message, list_messages: list):
        document_info = await self.bot.save_document(message)
        arr_message = self.add_message_user(list_messages, str(message.message_id))
        await self.bot.delete_messages_chat(message.chat.id, arr_message[1:])
        return document_info

    async def get_audio(self, message: Message, list_messages: list):
        audio_info = await self.bot.save_audio(message)
        arr_message = self.add_message_user(list_messages, str(message.message_id))
        await self.bot.delete_messages_chat(message.chat.id, arr_message[1:])
        return audio_info

    async def get_voice(self, message: Message, list_messages: list):
        voice_info = await self.bot.save_voice(message)
        arr_message = self.add_message_user(list_messages, str(message.message_id))
        await self.bot.delete_messages_chat(message.chat.id, arr_message[1:])
        return voice_info

    async def get_photo(self, message: Message, list_messages: list):
        photo_info = await self.bot.save_photo(message)
        arr_message = self.add_message_user(list_messages, str(message.message_id))
        await self.bot.delete_messages_chat(message.chat.id, arr_message[1:])
        return photo_info

    async def get_video(self, message: Message, list_messages: list):
        video_info = await self.bot.save_video(message)
        arr_message = self.add_message_user(list_messages, str(message.message_id))
        await self.bot.delete_messages_chat(message.chat.id, arr_message[1:])
        return video_info

    async def check_duration(self, call_back: CallbackQuery, dict_info_goal: dict):
        monthly_payment, total_income = await self.calculate(dict_info_goal['sum_goal'], dict_info_goal['income_user'],
                                                             dict_info_goal['income_frequency'],
                                                             dict_info_goal['duration'])
        if monthly_payment >= (total_income / 2) or int(dict_info_goal['duration']) == 0:
            await self.bot.alert_message(call_back.id, f"Достигнуть цели {dict_info_goal['goal_name']}, "
                                                       f"в размере {str(int(dict_info_goal['sum_goal']))} рублей, "
                                                       f"за {str(int(dict_info_goal['duration']))} месяцев, "
                                                       f"будет очень сложно")
            return False
        else:
            return True

    async def check_sum(self, call_back: CallbackQuery, value_sum: int, alert_message: str):
        if value_sum == 0:
            await self.bot.alert_message(call_back.id, alert_message)
            return False
        else:
            return True

    async def get_str_weekday(self, dict_reminder_days: dict) -> str:
        dict_weekday = await self.keyboard.get_weekday()
        list_weekday = []
        for key, item in dict_reminder_days.items():
            if item:
                list_weekday.append(dict_weekday[key])
        if len(list_weekday) == 0:
            weekday = 'Не напоминать о цели'
        else:
            weekday = ', '.join(list_weekday)
        return weekday

    @staticmethod
    async def calculate(sum_goal: float, income_user: float, income_frequency: int, duration: int):
        total_income = income_user * income_frequency
        if duration == 0:
            monthly_payment = 0
        else:
            monthly_payment = sum_goal / duration
        return monthly_payment, total_income

    @staticmethod
    async def check_text(string_text: str):
        arr_text = string_text.split()
        new_arr_text = []
        for item in arr_text:
            new_item = re.sub(r"[^ \w]", '', item)
            if new_item != '':
                new_arr_text.append(new_item)
        if len(new_arr_text) == 0:
            return False
        else:
            return ' '.join(new_arr_text)

    @staticmethod
    async def check_email(string_text: str):
        arr_text = string_text.split(' ')
        new_arr_text = []
        for item in arr_text:
            new_item = re.sub("[^A-Za-z@.]", "", item)
            if new_item != '':
                new_arr_text.append(new_item)
        new_string = ' '.join(new_arr_text)
        return new_string

    @staticmethod
    async def check_telephone(string_text: str):
        telephone = re.sub("[^0-9+]", "", string_text)
        if telephone[0] != '+' and len(telephone) == 10:
            telephone = '+7' + telephone
        elif len(telephone) == 11:
            telephone = '+7' + telephone[1:]
        return telephone

    @staticmethod
    def validate_phone_number(potential_number: str) -> bool:
        try:
            phone_number_obj = phonenumbers.parse(potential_number)
        except phonenumbers.phonenumberutil.NumberParseException:
            return False
        if not phonenumbers.is_valid_number(phone_number_obj):
            return False
        return True

    @staticmethod
    async def get_amount(text_message: str, button: str, separator_one: str, separator_two: str = None):
        if separator_two is not None:
            amount_string = text_message.split(separator_one)[-1].split(separator_two)[0]
        else:
            amount_string = text_message.split(separator_one)[-1]
        if amount_string == '0':
            amount = button
        else:
            amount = f"{amount_string}{button}"
        return str(amount)

    @staticmethod
    async def get_amount_minus(text_message: str, separator_one: str, separator_two: str = None):
        if separator_two is not None:
            amount_string = text_message.split(separator_one)[-1].split(separator_two)[0]
        else:
            amount_string = text_message.split(separator_one)[-1]
        if amount_string == '1' or amount_string == '0':
            amount = '0'
        else:
            amount = int(amount_string) - 1
        return str(amount)

    @staticmethod
    async def get_amount_plus(text_message: str, separator_one: str, separator_two: str = None):
        if separator_two is not None:
            amount_string = text_message.split(separator_one)[-1].split(separator_two)[0]
        else:
            amount_string = text_message.split(separator_one)[-1]
        amount = int(amount_string) + 1
        return str(amount)

    @staticmethod
    async def get_amount_delete(text_message: str, separator_one: str, separator_two: str = None):
        if separator_two is not None:
            amount_string = text_message.split(separator_one)[-1].split(separator_two)[0]
        else:
            amount_string = text_message.split(separator_one)[-1]
        if len(amount_string) == 1:
            amount = '0'
        else:
            amount = amount_string[:-1]
        return str(amount)

    @staticmethod
    async def answer_message(message: Message, text: str, keyboard: InlineKeyboardMarkup):
        return await message.answer(text=text, parse_mode=ParseMode.HTML, reply_markup=keyboard)

    @staticmethod
    async def edit_message(message: Message, text: str, keyboard: InlineKeyboardMarkup):
        return await message.edit_text(text=text, parse_mode=ParseMode.HTML, reply_markup=keyboard)

    @staticmethod
    async def answer_text(message: Message, text: str):
        return await message.answer(text=text, parse_mode=ParseMode.HTML, reply_to_message_id=message.message_id)

    @staticmethod
    async def edit_caption(message: Message, text: str, keyboard: InlineKeyboardMarkup):
        return await message.edit_caption(caption=text, parse_mode=ParseMode.HTML, reply_markup=keyboard)

    async def answer_photo(self, message: Message, photo: str, caption: str, keyboard: InlineKeyboardMarkup):
        try:
            return await message.answer_photo(photo=photo, caption=caption, parse_mode=ParseMode.HTML,
                                              reply_markup=keyboard)
        except TelegramBadRequest:
            photo = "https://www.rossvik.moscow/images/no_foto.png"
            text_by_format = self.format_text(caption)
            return await message.answer_photo(photo=photo, caption=text_by_format, parse_mode=ParseMode.HTML,
                                              reply_markup=keyboard)

    async def send_photo(self, message: Message, photo: str, text: str, amount_photo: int):
        media_group = MediaGroupBuilder(caption=text)
        if photo:
            arr_photo = photo.split()[:amount_photo]
        else:
            arr_photo = ["https://www.rossvik.moscow/images/no_foto.png"]
        for item in arr_photo:
            media_group.add_photo(media=item, parse_mode=ParseMode.HTML)
        try:
            return await self.bot.send_media_group(chat_id=message.chat.id, media=media_group.build())
        except TelegramBadRequest as error:
            print(error)
            media_group = MediaGroupBuilder(caption=text)
            arr_photo = ["https://www.rossvik.moscow/images/no_foto.png"]
            for item in arr_photo:
                media_group.add_photo(media=item, parse_mode=ParseMode.HTML)
            return await self.bot.send_media_group(chat_id=message.chat.id, media=media_group.build())

    async def send_file(self, message: Message, document: str, text: str, keyboard: InlineKeyboardMarkup):
        if document != '':
            arr_content = document.split('///')
            return await message.answer_document(document=FSInputFile(arr_content[0]), caption=text,
                                                 parse_mode=ParseMode.HTML, reply_markup=keyboard)
        else:
            return await self.answer_message(message, text, keyboard)

    async def send_media(self, message: Message, media: list, server: bool = False):
        media_group = MediaGroupBuilder()
        for item in media:
            if server:
                if 'C:\\Users\\Rossvik\\PycharmProjects\\' in item:
                    path_file = os.path.join(os.path.split(os.path.dirname(__file__))[0],
                                             item.split('C:\\Users\\Rossvik\\PycharmProjects\\')[1])
                else:
                    path_file = item
            else:
                if 'C:\\Users\\Rossvik\\PycharmProjects\\' in item:
                    path_file = item
                else:
                    path_reverse = "\\".join(item.split("/"))
                    path_file = 'C:\\Users\\Rossvik\\PycharmProjects\\' + path_reverse
            file_input = FSInputFile(path_file)
            media_group.add_document(media=file_input, parse_mode=ParseMode.HTML)
        return await self.bot.send_media_group(chat_id=message.chat.id, media=media_group.build())

    async def delete_messages(self, user_id: int, list_messages: list, except_id: str = None,
                              individual: bool = False) -> list:
        if not list_messages:
            new_list_message = []
        elif except_id and individual:
            new_list_message = []
            for message in list_messages:
                if message != except_id:
                    new_list_message.append(message)
            await self.bot.delete_messages_chat(user_id, [except_id])
        elif except_id and not individual:
            new_list_message = []
            for message in list_messages:
                if message != except_id:
                    new_list_message.append(message)
            await self.bot.delete_messages_chat(user_id, new_list_message)
            new_list_message = [except_id]
        else:
            await self.bot.delete_messages_chat(user_id, list_messages)
            new_list_message = []
        return new_list_message

    def build_keyboard(self, dict_button: dict, column: int, dict_return_button=None) -> InlineKeyboardMarkup:
        keyboard = self.build_menu(self.get_list_keyboard_button(dict_button), column,
                                   footer_buttons=self.get_list_keyboard_button(dict_return_button))
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    async def edit_keyboard(message: Message, keyboard: InlineKeyboardMarkup):
        return await message.edit_reply_markup(reply_markup=keyboard)

    @staticmethod
    def add_message_user(arr_messages: list, message: str) -> list:
        arr_messages.append(message)
        return arr_messages

    @staticmethod
    def get_list_keyboard_button(dict_button: dict):
        button_list = []
        if dict_button:
            for key, value in dict_button.items():
                if 'https://' in key:
                    button_list.append(InlineKeyboardButton(text=value, url=key))
                else:
                    button_list.append(InlineKeyboardButton(text=value, callback_data=key))
        else:
            button_list = None
        return button_list

    @staticmethod
    def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None) -> list:
        menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
        if header_buttons:
            menu.insert(0, [header_buttons])
        if footer_buttons:
            for item in footer_buttons:
                menu.append([item])
        return menu

    @staticmethod
    def format_text(text_message: str) -> str:
        cleaner = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
        clean_text = re.sub(cleaner, '', text_message)
        return f'<b>{clean_text}</b>'

    @staticmethod
    def format_price(item: float) -> str:
        return '{0:,} ₽'.format(item).replace(',', ' ')

    @staticmethod
    def quote(request) -> str:
        return f"'{str(request)}'"
