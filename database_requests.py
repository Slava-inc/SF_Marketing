# import asyncio
# import json
import logging
import aiosqlite
import os
from dotenv import load_dotenv
# import datetime
from prettytable import PrettyTable
from exception import send_message
# from aiogram.types import Message
# from operator import itemgetter

load_dotenv()
logging.basicConfig(level=logging.INFO)


class Execute:
    def __init__(self):
        self.connect_string = os.path.join(os.path.split(os.path.dirname(__file__))[0], os.environ["CONNECTION"])
        self.conn = None

    async def create_data_base(self):
        async with aiosqlite.connect(self.connect_string) as self.conn:
            print('База создана')

    async def create_table(self):
        try:
            async with aiosqlite.connect(self.connect_string) as self.conn:
                return await self.execute_create_table()
        except Exception as e:
            await send_message('Ошибка запроса в методе create_table', os.environ["EMAIL"], str(e))

    async def execute_create_table(self):
        async with self.conn.execute('PRAGMA journal_mode=wal') as cursor:
            sql_create_table = f"CREATE TABLE IF NOT EXISTS USERS (" \
                               f"ID INTEGER PRIMARY KEY, " \
                               f"HISTORY TEXT NOT NULL, " \
                               f"MESSAGES TEXT NOT NULL, " \
                               f"FIRST_NAME TEXT, " \
                               f"LAST_NAME TEXT, " \
                               f"USER_NAME TEXT NOT NULL)"
            await cursor.execute(sql_create_table)
            await self.conn.commit()

    @property
    async def get_list_user(self) -> dict:
        try:
            async with aiosqlite.connect(self.connect_string) as self.conn:
                return await self.execute_get_list_user()
        except Exception as e:
            await send_message('Ошибка запроса в методе get_list_user', os.environ["EMAIL"], str(e))

    async def execute_get_list_user(self) -> dict:
        async with self.conn.execute('PRAGMA journal_mode=wal') as cursor:
            sql_list_user = f"SELECT ID, HISTORY, MESSAGES, FIRST_NAME, LAST_NAME, USER_NAME " \
                            f"FROM USERS "
            await cursor.execute(sql_list_user)
            row_table = await cursor.fetchall()
            dict_user = {}
            for item in row_table:
                list_history = await self.get_list(item[1])
                list_messages = await self.get_list(item[2])
                dict_user[item[0]] = {'history': list_history, 'messages': list_messages, 'first_name': item[3],
                                      'last_name': item[4], 'user_name': item[5]}
            return dict_user

    async def get_user(self, id_user: int) -> dict:
        try:
            async with aiosqlite.connect(self.connect_string) as self.conn:
                return await self.execute_get_user(id_user)
        except Exception as e:
            await send_message('Ошибка запроса в методе get_user', os.environ["EMAIL"], str(e))

    async def execute_get_user(self, id_user: int) -> dict:
        async with self.conn.execute('PRAGMA journal_mode=wal') as cursor:
            sql_user = f"SELECT HISTORY, MESSAGES, FIRST_NAME, LAST_NAME, USER_NAME " \
                       f"FROM USERS " \
                       f"WHERE ID = {self.quote(id_user)} "
            await cursor.execute(sql_user)
            row_table = await cursor.fetchone()
            if row_table is None:
                dict_user = None
            else:
                list_history = await self.get_list(row_table[0])
                list_messages = await self.get_list(row_table[1])
                dict_user = {'history': list_history, 'messages': list_messages, 'first_name': row_table[2],
                             'last_name': row_table[3], 'user_name': row_table[4]}
            return dict_user

    async def set_user(self, id_user: int, dict_info_user: dict):
        try:
            async with aiosqlite.connect(self.connect_string) as self.conn:
                await self.execute_set_user(id_user, dict_info_user)
        except Exception as e:
            await send_message('Ошибка запроса в методе set_user', os.environ["EMAIL"], str(e))

    async def execute_set_user(self, id_user: int, dict_info_user: dict):
        async with self.conn.execute('PRAGMA journal_mode=wal') as cursor:
            history = await self.get_str(dict_info_user["history"])
            messages = await self.get_str(dict_info_user["messages"])
            sql_record = f"INSERT INTO USERS " \
                         f"(ID, HISTORY, MESSAGES, FIRST_NAME, LAST_NAME, USER_NAME) " \
                         f"VALUES('{id_user}', '{history}', '{messages}', '{dict_info_user["first_name"]}', " \
                         f"'{dict_info_user["last_name"]}', '{dict_info_user["user_name"]}') " \
                         f"ON CONFLICT (ID) DO UPDATE SET " \
                         f"HISTORY = '{history}', " \
                         f"MESSAGES = '{messages}', " \
                         f"FIRST_NAME = '{dict_info_user["first_name"]}', " \
                         f"LAST_NAM = '{dict_info_user["last_name"]}', " \
                         f"USER_NAME = '{dict_info_user["user_name"]}' " \
                         f"WHERE ID = {id_user} "
            await cursor.execute(sql_record)
            await self.conn.commit()

    async def delete_user(self, id_user: int):
        try:
            async with aiosqlite.connect(self.connect_string) as self.conn:
                await self.execute_delete_user(id_user)
        except Exception as e:
            await send_message('Ошибка запроса в методе delete_user', os.environ["EMAIL"], str(e))

    async def execute_delete_user(self, id_user: int):
        async with self.conn.execute('PRAGMA journal_mode=wal') as cursor:
            sql_delete = f"DELETE FROM USERS WHERE ID = {self.quote(id_user)} "
            await cursor.execute(sql_delete)
            await self.conn.commit()

    async def show_users(self):
        try:
            async with aiosqlite.connect(self.connect_string) as self.conn:
                await self.execute_show_users()
        except Exception as e:
            await send_message('Ошибка запроса в методе show_users', os.environ["EMAIL"], str(e))

    async def execute_show_users(self):
        async with self.conn.execute('PRAGMA journal_mode=wal') as cursor:
            sql_show_users = f"SELECT ID, HISTORY, MESSAGES, FIRST_NAME, LAST_NAME, USER_NAME FROM USERS "
            await cursor.execute(sql_show_users)
            row_table = await cursor.fetchall()
            if not row_table:
                print(f"В базе нет пользователей")
            else:
                my_table = PrettyTable()
                for item in row_table:
                    my_table.field_names = ["ID_USER", "HISTORY", "MESSAGES", "FIRST_NAME", "LAST_NAME", "USER_NAME"]
                    my_table.add_row([item[0], item[1], item[2], item[3], item[4], item[5]])
                print(my_table)
                print(f"В базе {len(row_table)} пользователей")

    async def show_columns(self, name_table: str):
        try:
            async with aiosqlite.connect(self.connect_string) as self.conn:
                await self.execute_show_columns(name_table)
        except Exception as e:
            await send_message('Ошибка запроса в методе show_columns', os.environ["EMAIL"], str(e))


    async def execute_show_columns(self, name_table: str):
        async with self.conn.execute(f'PRAGMA table_info({name_table})') as cursor:
            row_table = await cursor.fetchall()
            for item in row_table:
                print(item)

    @staticmethod
    def quote(request) -> str:
        return f"'{str(request)}'"

    @staticmethod
    async def get_list(messages_user: str) -> list:
        return messages_user.split()

    @staticmethod
    async def get_str(list_messages: list) -> str:
        return ' '.join(list_messages)

# my_base = Execute()
# asyncio.run(my_base.show_columns('USERS'))
