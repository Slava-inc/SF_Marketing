import asyncio
import logging
import re
import os
import datetime
from functions import Function
from database_requests import Execute
from aiogram import F
from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters.command import Command
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardMarkup
from aiogram.enums.parse_mode import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler

logging.basicConfig(level=logging.INFO)


class BotTelegram:
    def __init__(self, token_from_telegram):
        self.bot = BotMessage(token_from_telegram)
        self.dispatcher = DispatcherMessage(self.bot)

    async def start_dispatcher(self):
        self.dispatcher.scheduler.start()
        await self.dispatcher.start_polling(self.bot)

    def run(self):
        asyncio.run(self.start_dispatcher())


class BotMessage(Bot):
    def __init__(self, token, **kw):
        Bot.__init__(self, token, **kw)
        self.logo_main_menu = FSInputFile(os.path.join(os.path.split(os.path.dirname(__file__))[0],
                                                       os.environ["MAIN_MENU_PNG"]))
        self.logo_goal_menu = FSInputFile(os.path.join(os.path.split(os.path.dirname(__file__))[0],
                                                       os.environ["GOAL_MENU_PNG"]))
        self.logo_outlay_menu = FSInputFile(os.path.join(os.path.split(os.path.dirname(__file__))[0],
                                                         os.environ["OUTLAY_MENU_PNG"]))
        self.logo_income_menu = FSInputFile(os.path.join(os.path.split(os.path.dirname(__file__))[0],
                                                         os.environ["INCOME_MENU_PNG"]))

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

    async def send_message_news(self, chat_id: int, keyboard: InlineKeyboardMarkup, text_message: str):
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
        self.scheduler = AsyncIOScheduler()
        self.functions = Function(self.bot, self)
        self.execute = Execute()
        self.queues_message = QueuesMessage()
        self.queues = QueuesMedia(self)
        self.dict_user = self.functions.dict_user
        self.startup.register(self.on_startup)
        self.shutdown.register(self.on_shutdown)

        @self.message(Command("start"))
        async def cmd_start(message: Message):
            task = asyncio.create_task(self.functions.show_command_start(message))
            task.set_name(f'{message.from_user.id}_task_command_start')
            await self.queues_message.start(task)

        @self.message(F.from_user.id.in_(self.dict_user) & F.content_type.in_({
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
                task = asyncio.create_task(self.functions.get_document(
                    message,self.dict_user[message.from_user.id]['messages']))
                await self.queues.start(message.from_user.id, task)
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

        @self.callback_query(F.from_user.id.in_(self.dict_user) & (F.data == 'goal'))
        async def send_goal_message(callback: CallbackQuery):
            task = asyncio.create_task(self.functions.show_goal(callback))
            task.set_name(f'{callback.from_user.id}_task_goal')
            await self.queues_message.start(task)

        @self.callback_query(F.from_user.id.in_(self.dict_user) & (F.data == 'outlay'))
        async def send_outlay_message(callback: CallbackQuery):
            task = asyncio.create_task(self.functions.show_outlay(callback))
            task.set_name(f'{callback.from_user.id}_task_outlay')
            await self.queues_message.start(task)

        @self.callback_query(F.from_user.id.in_(self.dict_user) & (F.data == 'income'))
        async def send_income_message(callback: CallbackQuery):
            task = asyncio.create_task(self.functions.show_income(callback))
            task.set_name(f'{callback.from_user.id}_task_income')
            await self.queues_message.start(task)

        @self.callback_query(F.from_user.id.in_(self.dict_user) & (F.data == 'add_goal'))
        async def send_add_goal_message(callback: CallbackQuery):
            task = asyncio.create_task(self.functions.show_add_goal(callback))
            task.set_name(f'{callback.from_user.id}_task_add_goal')
            await self.queues_message.start(task)

        @self.callback_query(F.from_user.id.in_(self.dict_user) & (F.data == 'back'))
        async def send_return_message(callback: CallbackQuery):
            task = asyncio.create_task(self.functions.show_back(callback))
            task.set_name(f'{callback.from_user.id}_task_back')
            await self.queues_message.start(task)

    async def on_startup(self):
        # Отправляем сообщение администратору о том, что бот был запущен
        self.dict_user[int(os.environ["ADMIN_ID"])]['messages'] = await self.functions.delete_messages(
            int(os.environ["ADMIN_ID"]), self.dict_user[int(os.environ["ADMIN_ID"])]['messages'])
        answer = await self.bot.send_message(chat_id=os.environ["ADMIN_ID"], text='Бот FinAppBot запущен!')
        self.dict_user[int(os.environ["ADMIN_ID"])]['messages'].append(str(answer.message_id))
        self.dict_user[int(os.environ["ADMIN_ID"])]['history'] = ['start']
        await self.execute.set_user(int(os.environ["ADMIN_ID"]), self.dict_user[int(os.environ["ADMIN_ID"])])
        self.scheduler_send_news()

    def scheduler_send_news(self):
        # Добавляем задачу отправки полезных советов в scheduler каждый день в 10:00
        self.scheduler.add_job(self.functions.newsletter, 'cron', day_of_week='mon-sun', hour=10, minute=00,
                               end_date='2025-01-30')

    async def on_shutdown(self):
        # Отправляем сообщение администратору о том, что бот был остановлен
        self.dict_user[int(os.environ["ADMIN_ID"])]['messages'] = await self.functions.delete_messages(
            int(os.environ["ADMIN_ID"]), self.dict_user[int(os.environ["ADMIN_ID"])]['messages'])
        answer = await self.bot.send_message(chat_id=os.environ["ADMIN_ID"], text='Бот FinAppBot остановлен!')
        self.dict_user[int(os.environ["ADMIN_ID"])]['messages'].append(str(answer.message_id))
        self.dict_user[int(os.environ["ADMIN_ID"])]['history'] = ['start']
        await self.execute.set_user(int(os.environ["ADMIN_ID"]), self.dict_user[int(os.environ["ADMIN_ID"])])
        await self.bot.session.close()


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
        list_info = self.parent.functions.info_pdf.get_text_file(info[0])
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
            await self.parent.functions.start_for_timer(user_id, self.text_document)
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
