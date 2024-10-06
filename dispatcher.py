import asyncio
import json
import logging
import re
import os
import datetime
# import openpyxl
# import requests
import phonenumbers
# import json
from keyboard import KeyBoardBot
from database_requests import Execute
from edit_pdf import GetTextOCR
from aiogram import F
from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.filters.command import Command
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery, FSInputFile, ChatPermissions
from aiogram.utils.keyboard import InlineKeyboardMarkup
from aiogram.enums.parse_mode import ParseMode
from aiogram.utils.media_group import MediaGroupBuilder
# from operator import itemgetter
# from openpyxl.styles import GradientFill
# from number_parser import parse
# from nltk.stem import SnowballStemmer
# from validate_email import validate_email
# from check import is_valid

logging.basicConfig(level=logging.INFO)
# snowball = SnowballStemmer(language="russian")


class BotTelegram:
    def __init__(self, token_from_telegram):
        self.bot = BotMessage(token_from_telegram)
        self.dispatcher = DispatcherMessage(self.bot)

    async def start_dispatcher(self):
        await self.dispatcher.start_polling(self.bot)

    def run(self):
        asyncio.run(self.start_dispatcher())


class BotMessage(Bot):
    def __init__(self, token, **kw):
        Bot.__init__(self, token, **kw)

    async def delete_messages_chat(self, chat_id: int, list_message: list):
        try:
            await self.delete_messages(chat_id=chat_id, message_ids=list_message)
        except TelegramBadRequest:
            print(f'Не удалось удалить сообщения {list_message} у пользователя {chat_id}')

    async def alert_message(self, id_call_back: str, text: str):
        await self.answer_callback_query(id_call_back, text=text, show_alert=True)

    async def edit_head_message(self, text_message: str, chat_message: int, id_message: int,
                                          keyboard: InlineKeyboardMarkup):
        return await self.edit_message_text(text=text_message, chat_id=chat_message,
                                            message_id=id_message, parse_mode=ParseMode.HTML, reply_markup=keyboard)

    async def edit_head_caption(self, text_message: str, chat_message: int, id_message: int,
                                          keyboard: InlineKeyboardMarkup):
        return await self.edit_message_caption(caption=text_message, chat_id=chat_message,
                                               message_id=id_message, parse_mode=ParseMode.HTML, reply_markup=keyboard)

    async def edit_head_keyboard(self, chat_message: int, id_message: int, keyboard: InlineKeyboardMarkup):
        return await self.edit_message_reply_markup(chat_id=chat_message, message_id=id_message, reply_markup=keyboard)

    async def send_message_start(self, chat_id: int, keyboard: InlineKeyboardMarkup, text_message: str):
        return await self.send_message(chat_id=chat_id, text=self.format_text(text_message),
                                       parse_mode=ParseMode.HTML, reply_markup=keyboard)

    async def push_photo(self, message_chat_id: int, text: str, keyboard: InlineKeyboardMarkup,
                         name_photo: FSInputFile):
        return await self.send_photo(chat_id=message_chat_id, photo=name_photo, caption=text,
                                     parse_mode=ParseMode.HTML, reply_markup=keyboard)

    async def save_audio(self, message: Message):
        id_file = re.sub('[^0-9]', '', str(datetime.datetime.now()))
        name_file = f"audio_{id_file}"
        filepath = os.path.join(os.path.split(os.path.dirname(__file__))[0], f'data/content/{name_file}.mp3')
        file_id = message.audio.file_id
        caption = message.caption
        file = await self.get_file(file_id)
        await self.download_file(file_path=file.file_path, destination=f"{filepath}")
        return filepath, caption

    async def save_document(self, message: Message):
        id_file = re.sub('[^0-9]', '', str(datetime.datetime.now()))
        name_file = f"{id_file}_{message.document.file_name}"
        filepath = os.path.join(os.path.split(os.path.dirname(__file__))[0], f'data/content/{name_file}')
        file_id = message.document.file_id
        caption = message.caption
        file = await self.get_file(file_id)
        await self.download_file(file_path=file.file_path, destination=f"{filepath}")
        return filepath, caption

    async def save_voice(self, message: Message):
        id_file = re.sub('[^0-9]', '', str(datetime.datetime.now()))
        name_file = f"voice_{id_file}"
        filepath = os.path.join(os.path.split(os.path.dirname(__file__))[0], f'data/content/{name_file}.ogg')
        file_id = message.voice.file_id
        caption = message.caption
        file = await self.get_file(file_id)
        await self.download_file(file_path=file.file_path, destination=f"{filepath}")
        return filepath, caption

    async def save_photo(self, message: Message):
        id_file = re.sub('[^0-9]', '', str(datetime.datetime.now()))
        name_file = f"photo_{id_file}"
        filepath = os.path.join(os.path.split(os.path.dirname(__file__))[0], f'data/content/{name_file}.jpg')
        file_id = message.photo[-1].file_id
        caption = message.caption
        file = await self.get_file(file_id)
        await self.download_file(file_path=file.file_path, destination=f"{filepath}")
        return filepath, caption

    async def save_video(self, message: Message):
        id_file = re.sub('[^0-9]', '', str(datetime.datetime.now()))
        name_file = f"video_{id_file}"
        filepath = os.path.join(os.path.split(os.path.dirname(__file__))[0], f'data/content/{name_file}.mp4')
        file_id = message.video.file_id
        caption = message.caption
        file = await self.get_file(file_id)
        await self.download_file(file_path=file.file_path, destination=f"{filepath}")
        return filepath, caption

    @staticmethod
    def format_text(text_message: str):
        cleaner = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
        clean_text = re.sub(cleaner, '', text_message)
        return f'<b>{clean_text}</b>'


class DispatcherMessage(Dispatcher):
    def __init__(self, parent, **kw):
        Dispatcher.__init__(self, **kw)
        self.bot = parent
        self.keyboard = KeyBoardBot()
        self.execute = Execute()
        self.timer = TimerClean(self, 82800)
        self.queues = QueuesMedia(self)
        self.info_pdf = GetTextOCR()
        self.queues_message = QueuesMessage()
        self.list_user = asyncio.run(self.execute.get_list_user)

        @self.message(Command("start"))
        async def cmd_start(message: Message):
            task = asyncio.create_task(self.task_command_start(message))
            task.set_name(f'{message.from_user.id}_task_command_start')
            await self.queues_message.start(task)
            await self.timer.start(message.from_user.id)

        @self.message(F.from_user.id.in_(self.list_user) & F.content_type.in_({
            "text", "audio", "document", "photo", "sticker", "video", "video_note", "voice", "location", "contact",
            "new_chat_members", "left_chat_member", "new_chat_title", "new_chat_photo", "delete_chat_photo",
            "group_chat_created", "supergroup_chat_created", "channel_chat_created", "migrate_to_chat_id",
            "migrate_from_chat_id", "pinned_message"}))
        async def get_message(message: Message):
            if message.content_type == "text":
                await self.bot.delete_messages_chat(message.chat.id, [message.message_id])
                print("text")
            elif message.content_type == "audio":
                await self.bot.delete_messages_chat(message.chat.id, [message.message_id])
                print("audio")
            elif message.content_type == "document":
                task = asyncio.create_task(self.get_document(message, self.list_user[message.from_user.id]['messages']))
                await self.queues.start(message.from_user.id, task)
                await self.timer.start(message.from_user.id)
            elif message.content_type == "photo":
                await self.bot.delete_messages_chat(message.chat.id, [message.message_id])
                print("photo")
            elif message.content_type == "sticker":
                await self.bot.delete_messages_chat(message.chat.id, [message.message_id])
                print("sticker")
            elif message.content_type == "video":
                await self.bot.delete_messages_chat(message.chat.id, [message.message_id])
                print("video")
            elif message.content_type == "video_note":
                await self.bot.delete_messages_chat(message.chat.id, [message.message_id])
                print("video_note")
            elif message.content_type == "voice":
                await self.bot.delete_messages_chat(message.chat.id, [message.message_id])
                print("voice")
            elif message.content_type == "location":
                await self.bot.delete_messages_chat(message.chat.id, [message.message_id])
                print("location")
            elif message.content_type == "contact":
                await self.bot.delete_messages_chat(message.chat.id, [message.message_id])
                print("contact")
            else:
                await self.bot.delete_messages_chat(message.chat.id, [message.message_id])

        @self.callback_query(F.from_user.id.in_(self.list_user) & (F.data == 'call_back1'))
        async def send_catalog_message(callback: CallbackQuery):
            await self.bot.delete_messages_chat(callback.message.chat.id, [callback.message.message_id])
            print("call_back1")

        @self.callback_query(F.from_user.id.in_(self.list_user) & (F.data == 'call_back2'))
        async def remove_dealer_price(callback: CallbackQuery):
            await self.bot.delete_messages_chat(callback.message.chat.id, [callback.message.message_id])
            print("call_back2")

        @self.callback_query(F.from_user.id.in_(self.list_user) & (F.data == 'call_back3'))
        async def show_dealer_price(callback: CallbackQuery):
            await self.bot.delete_messages_chat(callback.message.chat.id, [callback.message.message_id])
            print("call_back3")

    async def checking_bot(self, message: Message):
        if message.from_user.is_bot:
            await self.bot.restrict_chat_member(message.chat.id, message.from_user.id, ChatPermissions())
            this_bot = True
        else:
            this_bot = False
        return this_bot

    async def task_command_start(self, message: Message):
        check = await self.checking_bot(message)
        if check:
            await self.delete_messages(message.from_user.id, [message.message_id])
        else:
            if message.from_user.id not in self.list_user.keys():
                self.list_user[message.from_user.id] = {'history': ['start'], 'messages': [],
                                                        'first_name': message.from_user.first_name,
                                                        'last_name': message.from_user.last_name,
                                                        'user_name': message.from_user.username}
            first_keyboard = await self.keyboard.get_first_keyboard()
            text_message = f'Привет, {message.from_user.first_name} {message.from_user.last_name}!'
            answer = await self.answer_message(message, text_message, self.build_keyboard(first_keyboard, 1))
            self.list_user[message.from_user.id]['messages'].append(str(message.message_id))
            list_messages_for_record = await self.delete_messages(message.from_user.id,
                                                                  self.list_user[message.from_user.id]['messages'])
            list_messages_for_record.append(str(answer.message_id))
            self.list_user[message.from_user.id]['messages'] = list_messages_for_record
            self.list_user[message.from_user.id]['history'] = ['start']
            await self.execute.set_user(message.from_user.id, self.list_user[message.from_user.id])
        return True

    async def return_start(self, call_back: CallbackQuery):
        first_keyboard = await self.keyboard.get_first_keyboard()
        text_message = f'Привет, {call_back.from_user.first_name} {call_back.from_user.last_name}!'
        answer = await self.answer_message(call_back.message, text_message, self.build_keyboard(first_keyboard, 1))
        list_messages_for_record = await self.delete_messages(call_back.from_user.id,
                                                              self.list_user[call_back.from_user.id]['messages'])
        list_messages_for_record.append(str(answer.message_id))
        self.list_user[call_back.from_user.id]['messages'] = list_messages_for_record
        self.list_user[call_back.from_user.id]['history'] = ['start']
        await self.execute.set_user(call_back.from_user.id, self.list_user[call_back.from_user.id])

    async def start_for_timer(self, user_id: int, text_message: str):
        try:
            first_keyboard = await self.keyboard.get_first_keyboard()
            answer = await self.bot.send_message_start(user_id, self.build_keyboard(first_keyboard, 1),
                                                       text_message)
            list_messages_for_record = await self.delete_messages(user_id, self.list_user[user_id]['messages'])
            list_messages_for_record.append(str(answer.message_id))
            self.list_user[user_id]['messages'] = list_messages_for_record
            self.list_user[user_id]['history'] = ['start']
            await self.execute.set_user(user_id, self.list_user[user_id])
            return True
        except TelegramForbiddenError:
            await self.execute.delete_user(user_id)
            self.list_user.pop(user_id)
            return False

    async def task_command_link(self, message: Message):
        check = await self.checking_bot(message)
        if check:
            await self.delete_messages(message.from_user.id, [message.message_id])
        else:
            await self.show_link(message)
        return True

    async def show_link(self, message: Message):
        link_keyboard = {'https://t.me/rossvik_moscow': 'Канал @ROSSVIK_MOSCOW 📣💬',
                         'https://www.rossvik.moscow/': 'Сайт WWW.ROSSVIK.MOSCOW 🌐', 'back': '◀ 👈 Назад'}
        answer = await self.answer_message(message,
                                           f"Перейдите по ссылкам ниже, чтобы узнать ещё больше информации:",
                                           self.build_keyboard(link_keyboard, 1))
        self.list_user[message.from_user.id]['messages'].append(str(message.message_id))
        list_messages_for_record = await self.delete_messages(message.from_user.id,
                                                              self.list_user[message.from_user.id]['messages'])
        list_messages_for_record.append(str(answer.message_id))
        self.list_user[message.from_user.id]['messages'] = list_messages_for_record
        self.list_user[message.from_user.id]['history'].append('news')
        await self.execute.set_user(message.from_user.id, self.list_user[message.from_user.id])

    async def return_show_link(self, call_back: CallbackQuery):
        link_keyboard = {'https://t.me/rossvik_moscow': 'Канал @ROSSVIK_MOSCOW 📣💬',
                         'https://www.rossvik.moscow/': 'Сайт WWW.ROSSVIK.MOSCOW 🌐', 'back': '◀ 👈 Назад'}
        answer = await self.answer_message(call_back.message, f"Перейдите по ссылкам ниже, чтобы узнать ещё больше информации:",
                                           self.build_keyboard(link_keyboard, 1))
        list_messages_for_record = await self.delete_messages(call_back.from_user.id,
                                                              self.list_user[call_back.from_user.id]['messages'])
        list_messages_for_record.append(str(answer.message_id))
        self.list_user[call_back.from_user.id]['messages'] = list_messages_for_record
        await self.execute.set_user(call_back.from_user.id, self.list_user[call_back.from_user.id])

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

    @staticmethod
    async def check_text(string_text: str):
        arr_text = string_text.split(' ')
        new_arr_text = []
        for item in arr_text:
            new_item = re.sub(r"[^ \w]", '', item)
            if new_item != '':
                new_arr_text.append(new_item)
        new_string = ' '.join(new_arr_text)
        return new_string

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
    async def answer_message(message: Message, text: str, keyboard: InlineKeyboardMarkup):
        return await message.answer(text=text, parse_mode=ParseMode.HTML, reply_markup=keyboard)

    @staticmethod
    async def edit_message(message: Message, text: str, keyboard: InlineKeyboardMarkup):
        return await message.edit_text(text=text, parse_mode=ParseMode.HTML, reply_markup=keyboard)

    @staticmethod
    async def answer_text(self, message: Message, text: str):
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
            text_by_format = await self.format_text(caption)
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
    async def format_text(text_message: str) -> str:
        cleaner = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
        clean_text = re.sub(cleaner, '', text_message)
        return f'<b>{clean_text}</b>'

    @staticmethod
    def format_price(item: float) -> str:
        return '{0:,} ₽'.format(item).replace(',', ' ')

    @staticmethod
    def quote(request) -> str:
        return f"'{str(request)}'"


class TimerClean:
    def __init__(self, parent, second: int):
        self.parent = parent
        self._clean_time = second
        self.t = {}

    async def start(self, user: int):
        if user in self.t.keys():
            self.t[user].cancel()
            self.t.pop(user)
            self.t[user] = asyncio.create_task(self.clean_chat(user))
            await self.t[user]
        else:
            self.t[user] = asyncio.create_task(self.clean_chat(user))
            await self.t[user]

    async def clean_chat(self, user: int):
        await asyncio.sleep(self._clean_time)
        id_message = await self.parent.start_for_timer(user)
        if id_message:
            await self.clean_timer(user)

    async def clean_timer(self, user: int):
        self.t.pop(user)
        await self.start(user)


class QueuesMedia:
    def __init__(self, parent):
        self.parent = parent
        self.queues = []
        self.text_document = None

    async def start(self, user_id: int, new_media: asyncio.Task):
        if len(self.queues) == 0:
            self.queues.append(new_media)
            await self.start_task(user_id)
        else:
            self.queues.append(new_media)

    async def start_task(self, user_id: int):
        info = await self.queues[0]
        print(info)
        list_info = self.parent.info_pdf.get_text_file(info[0])
        self.text_document = "".join(list_info)
        await self.delete_task_queues(user_id)

    async def delete_task_queues(self, user_id: int):
        self.queues.remove(self.queues[0])
        await self.restart_queues(user_id)

    async def restart_queues(self, user_id: int):
        if len(self.queues) != 0:
            await self.start_task(user_id)
        else:
            # await self.parent.execute.set_outlay(user_id)
            await self.parent.start_for_timer(user_id, self.text_document)
            self.text_document = None


class QueuesMessage:
    def __init__(self):
        self.queues = []
        self.dict_name_task = {}
        self.queue_busy = False

    async def start(self, new_task: asyncio.Task):
        if new_task.get_name() in self.dict_name_task.keys():
            new_task.cancel()
        else:
            if len(self.queues) == 0:
                self.dict_name_task[new_task.get_name()] = new_task
                self.queues.append(new_task)
                await self.start_task()
            else:
                self.dict_name_task[new_task.get_name()] = new_task
                self.queues.append(new_task)

    async def start_task(self):
        self.queue_busy = await self.queues[0]
        if self.queue_busy:
            await self.delete_task_queues()
        else:
            print('Задача не выполнилась')

    async def delete_task_queues(self):
        self.dict_name_task.pop(self.queues[0].get_name())
        self.queues.remove(self.queues[0])
        await self.restart_queues()

    async def restart_queues(self):
        if len(self.queues) == 0:
            self.queue_busy = False
        else:
            await self.start_task()