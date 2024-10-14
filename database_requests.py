import asyncio
import json
import logging
import aiosqlite
import os
from dotenv import load_dotenv
from prettytable import PrettyTable
from exception import send_message

load_dotenv()
logging.basicConfig(level=logging.INFO)


class Execute:
    def __init__(self):
        # self.connect_string = os.path.join(os.path.split(os.path.dirname(__file__))[0], os.environ["CONNECTION"])
        self.connect_string = os.path.join(os.path.split(os.path.dirname(__file__))[0], "SF_marketing/db.sqlite")

        self.conn = None

    async def create_data_base(self):
        async with aiosqlite.connect(self.connect_string) as self.conn:
            print('База создана')

    async def create_table(self, text_execute: str):
        try:
            async with aiosqlite.connect(self.connect_string) as self.conn:
                await self.execute_create_table(text_execute)
        except Exception as e:
            await send_message('Ошибка запроса в методе create_table', os.environ["EMAIL"], str(e))

    async def execute_create_table(self, text_execute: str):
        async with self.conn.execute('PRAGMA journal_mode=wal') as cursor:
            sql_create_table = text_execute
            await cursor.execute(sql_create_table)
            await self.conn.commit()

    async def delete_table(self, name_table: str):
        try:
            async with aiosqlite.connect(self.connect_string) as self.conn:
                await self.execute_delete_table(name_table)
        except Exception as e:
            await send_message('Ошибка запроса в методе delete_table', os.environ["EMAIL"], str(e))

    async def execute_delete_table(self, name_table: str):
        async with self.conn.execute('PRAGMA journal_mode=wal') as cursor:
            await cursor.execute(f"DROP TABLE {name_table}")
            await self.conn.commit()

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

    @property
    async def get_dict_user(self) -> dict:
        try:
            async with aiosqlite.connect(self.connect_string) as self.conn:
                return await self.execute_get_dict_user()
        except Exception as e:
            await send_message('Ошибка запроса в методе get_dict_user', os.environ["EMAIL"], str(e))

    async def execute_get_dict_user(self) -> dict:
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
    async def set_user(self, id: int, dict_info: dict):
        try:
            async with aiosqlite.connect(self.connect_string) as self.conn:
                await self.execute_set_user(id, dict_info)
        except Exception as e:
            # await send_message('Ошибка запроса в методе set_user', os.environ["EMAIL"], str(e))
            print(str(e))

    async def execute_set_user(self, id: int, dict_info: dict):
        async with self.conn.execute('PRAGMA journal_mode=wal') as cursor:
            try:
                sql_record = f"INSERT INTO USERS " \
                            f"(ID, USER_ID, HISTORY, MESSAGES, FIRST_NAME, LAST_NAME, USER_NAME) " \
                            f"VALUES({id}, " \
                            f"{dict_info['user_id']}, " \
                            f"{dict_info['history']}, " \
                            f"{dict_info['messages']}, " \
                            f"{dict_info['first_name']}, " \
                            f"{dict_info['last_name']}, " \
                            f"'{dict_info['user_name']}') "
            except Exception as e:
                print(str(e))

            await cursor.execute(sql_record)
            await self.conn.commit() 
                                
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

    async def update_user(self, id_user: int, dict_info_user: dict):
        try:
            async with aiosqlite.connect(self.connect_string) as self.conn:
                await self.execute_update_user(id_user, dict_info_user)
        except Exception as e:
            await send_message('Ошибка запроса в методе update_user', os.environ["EMAIL"], str(e))

    async def execute_update_user(self, id_user: int, dict_info_user: dict):
        async with self.conn.execute('PRAGMA journal_mode=wal') as cursor:
            history = await self.get_str(dict_info_user['history'])
            messages = await self.get_str(dict_info_user['messages'])
            sql_record = f"INSERT INTO USERS " \
                         f"(ID, HISTORY, MESSAGES, FIRST_NAME, LAST_NAME, USER_NAME) " \
                         f"VALUES('{id_user}', '{history}', '{messages}', '{dict_info_user['first_name']}', " \
                         f"'{dict_info_user['last_name']}', '{dict_info_user['user_name']}') " \
                         f"ON CONFLICT (ID) DO UPDATE SET " \
                         f"HISTORY = '{history}', " \
                         f"MESSAGES = '{messages}', " \
                         f"FIRST_NAME = '{dict_info_user['first_name']}', " \
                         f"LAST_NAME = '{dict_info_user['last_name']}', " \
                         f"USER_NAME = '{dict_info_user['user_name']}' " \
                         f"WHERE ID = {id_user} "
            await cursor.execute(sql_record)
            await self.conn.commit()

    async def update_all_users(self, dict_user: dict):
        try:
            async with aiosqlite.connect(self.connect_string) as self.conn:
                await self.execute_update_all_users(dict_user)
        except Exception as e:
            await send_message('Ошибка запроса в методе update_all_users', os.environ["EMAIL"], str(e))

    async def execute_update_all_users(self, dict_users: dict):
        async with self.conn.execute('PRAGMA journal_mode=wal') as cursor:
            for key, item in dict_users.items():
                history = await self.get_str(item['history'])
                messages = await self.get_str(item['messages'])
                sql_record = f"INSERT INTO USERS " \
                             f"(ID, HISTORY, MESSAGES, FIRST_NAME, LAST_NAME, USER_NAME) " \
                             f"VALUES('{key}', '{history}', '{messages}', '{item['first_name']}', " \
                             f"'{item['last_name']}', '{item['user_name']}') " \
                             f"ON CONFLICT (ID) DO UPDATE SET " \
                             f"HISTORY = '{history}', " \
                             f"MESSAGES = '{messages}', " \
                             f"FIRST_NAME = '{item['first_name']}', " \
                             f"LAST_NAME = '{item['last_name']}', " \
                             f"USER_NAME = '{item['user_name']}' " \
                             f"WHERE ID = {key} "
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

    @property
    async def get_dict_goal(self) -> dict:
        try:
            async with aiosqlite.connect(self.connect_string) as self.conn:
                return await self.execute_get_dict_goal()
        except Exception as e:
            await send_message('Ошибка запроса в методе get_dict_goal', os.environ["EMAIL"], str(e))

    async def execute_get_dict_goal(self) -> dict:
        async with self.conn.execute('PRAGMA journal_mode=wal') as cursor:
            sql_list_goal = f"SELECT ROWID, USER_ID, GOAL_NAME, SUM_GOAL, INCOME_USER, INCOME_FREQUENCY, DURATION, " \
                            f"REMINDER_DAYS, REMINDER_TIME, DATA_FINISH, STATUS_GOAL " \
                            f"FROM GOAL "
            await cursor.execute(sql_list_goal)
            row_table = await cursor.fetchall()
            dict_goal = {}
            for item in row_table:
                list_reminder_days = await self.get_dict_reminder_days(item[7])
                dict_goal[item[0]] = {'user_id': item[1], 'goal_name': item[2], 'sum_goal': item[3],
                                      'income_user': item[4], 'income_frequency': item[5], 'duration': item[6],
                                      'reminder_days': list_reminder_days, 'reminder_time': item[8],
                                      'data_finish': item[9], 'status_goal': item[10]}
            return dict_goal

    async def check_new_goal(self, user_id: int) -> int:
        try:
            async with aiosqlite.connect(self.connect_string) as self.conn:
                return await self.execute_check_new_goal(user_id)
        except Exception as e:
            await send_message('Ошибка запроса в методе check_new_goal', os.environ["EMAIL"], str(e))

    async def execute_check_new_goal(self, user_id: int) -> int:
        async with self.conn.execute('PRAGMA journal_mode=wal') as cursor:
            sql_check_new_goal = f"SELECT ROWID " \
                                 f"FROM GOAL " \
                                 f"WHERE USER_ID = '{user_id}' AND STATUS_GOAL = 'new' "
            await cursor.execute(sql_check_new_goal)
            row_table = await cursor.fetchone()
            if row_table is None:
                row_id = 0
            else:
                row_id = row_table[0]
            return row_id

    @property
    async def get_current_goal(self) -> dict:
        try:
            async with aiosqlite.connect(self.connect_string) as self.conn:
                return await self.execute_get_current_goal()
        except Exception as e:
            await send_message('Ошибка запроса в методе get_current_goal', os.environ["EMAIL"], str(e))

    async def execute_get_current_goal(self) -> dict:
        async with self.conn.execute('PRAGMA journal_mode=wal') as cursor:
            sql_list_goal = f"SELECT ROWID, USER_ID, GOAL_NAME, SUM_GOAL, INCOME_USER, INCOME_FREQUENCY, DURATION, " \
                            f"REMINDER_DAYS, REMINDER_TIME, DATA_FINISH, STATUS_GOAL " \
                            f"FROM GOAL " \
                            f"WHERE STATUS_GOAL = 'current' "
            await cursor.execute(sql_list_goal)
            row_table = await cursor.fetchall()
            dict_goal = {}
            for item in row_table:
                list_reminder_days = await self.get_dict_reminder_days(item[7])
                dict_goal[item[0]] = {'user_id': item[1], 'goal_name': item[2], 'sum_goal': item[3],
                                      'income_user': item[4], 'income_frequency': item[5], 'duration': item[6],
                                      'reminder_days': list_reminder_days, 'reminder_time': item[8],
                                      'data_finish': item[9], 'status_goal': item[10]}
            return dict_goal

    async def insert_goal(self, user_id: int, dict_info_goal: dict) -> int:
        try:
            async with aiosqlite.connect(self.connect_string) as self.conn:
                return await self.execute_insert_goal(user_id, dict_info_goal)
        except Exception as e:
            await send_message('Ошибка запроса в методе insert_goal', os.environ["EMAIL"], str(e))

    async def execute_insert_goal(self, user_id: int, dict_info_goal: dict):
        async with self.conn.execute('PRAGMA journal_mode=wal') as cursor:
            str_reminder_days = await self.get_str_reminder_days(dict_info_goal['reminder_days'])
            sql_insert_goal = f"INSERT INTO GOAL " \
                              f"(USER_ID, GOAL_NAME, SUM_GOAL, INCOME_USER, INCOME_FREQUENCY, DURATION, " \
                              f"REMINDER_DAYS, REMINDER_TIME, DATA_FINISH, STATUS_GOAL) " \
                              f"VALUES('{user_id}', '{dict_info_goal['goal_name']}', '{dict_info_goal['sum_goal']}', " \
                              f"'{dict_info_goal['income_user']}', '{dict_info_goal['income_frequency']}', " \
                              f"'{dict_info_goal['duration']}', '{str_reminder_days}', " \
                              f"'{dict_info_goal['reminder_time']}', '{dict_info_goal['data_finish']}', " \
                              f"'{dict_info_goal['status_goal']}') "
            await cursor.execute(sql_insert_goal)
            await self.conn.commit()
            return cursor.lastrowid

    async def update_goal(self, row_id: int, dict_info_goal: dict):
        try:
            async with aiosqlite.connect(self.connect_string) as self.conn:
                await self.execute_update_goal(row_id, dict_info_goal)
        except Exception as e:
            await send_message('Ошибка запроса в методе update_goal', os.environ["EMAIL"], str(e))

    async def execute_update_goal(self, row_id: int, dict_info_goal: dict):
        async with self.conn.execute('PRAGMA journal_mode=wal') as cursor:
            str_reminder_days = await self.get_str_reminder_days(dict_info_goal['reminder_days'])
            sql_update_goal = f"UPDATE GOAL SET " \
                              f"USER_ID = '{dict_info_goal['user_id']}', " \
                              f"GOAL_NAME = '{dict_info_goal['goal_name']}', " \
                              f"SUM_GOAL = '{dict_info_goal['sum_goal']}', " \
                              f"INCOME_USER = '{dict_info_goal['income_user']}', " \
                              f"INCOME_FREQUENCY = '{dict_info_goal['income_frequency']}', " \
                              f"DURATION = '{dict_info_goal['duration']}', " \
                              f"REMINDER_DAYS = '{str_reminder_days}', " \
                              f"REMINDER_TIME = '{dict_info_goal['reminder_time']}', " \
                              f"DATA_FINISH = '{dict_info_goal['data_finish']}', " \
                              f"STATUS_GOAL = '{dict_info_goal['status_goal']}' " \
                              f"WHERE ROWID = '{row_id}' "
            await cursor.execute(sql_update_goal)
            await self.conn.commit()

    async def delete_goal(self, row_id: int):
        try:
            async with aiosqlite.connect(self.connect_string) as self.conn:
                await self.execute_delete_goal(row_id)
        except Exception as e:
            await send_message('Ошибка запроса в методе delete_goal', os.environ["EMAIL"], str(e))

    async def execute_delete_goal(self, row_id: int):
        async with self.conn.execute('PRAGMA journal_mode=wal') as cursor:
            sql_delete = f"DELETE FROM GOAL WHERE ROWID = {self.quote(row_id)} "
            await cursor.execute(sql_delete)
            await self.conn.commit()

    async def show_goals(self):
        try:
            async with aiosqlite.connect(self.connect_string) as self.conn:
                await self.execute_show_goals()
        except Exception as e:
            await send_message('Ошибка запроса в методе show_goals', os.environ["EMAIL"], str(e))

    async def execute_show_goals(self):
        async with self.conn.execute('PRAGMA journal_mode=wal') as cursor:
            sql_show_goals = f"SELECT ROWID, USER_ID, GOAL_NAME, SUM_GOAL, INCOME_USER, INCOME_FREQUENCY, DURATION, " \
                             f"REMINDER_DAYS, REMINDER_TIME, DATA_FINISH, STATUS_GOAL " \
                             f"FROM GOAL "
            await cursor.execute(sql_show_goals)
            row_table = await cursor.fetchall()
            if not row_table:
                print(f"В базе нет целей")
            else:
                my_table = PrettyTable()
                my_table.field_names = ["ROWID", "USER_ID", "GOAL_NAME", "SUM_GOAL", "INCOME_USER", "INCOME_FREQUENCY",
                                        "DURATION", "REMINDER_DAYS", "REMINDER_TIME", "DATA_FINISH", "STATUS_GOAL"]
                for item in row_table:
                    my_table.add_row([item[0], item[1], item[2], item[3], item[4], item[5], item[6],
                                      item[7], item[8], item[9], item[10]])
                print(my_table)
                print(f"В базе {len(row_table)} целей")

    async def set_category_income(self, id: int, dict_info: dict):
        try:
            async with aiosqlite.connect(self.connect_string) as self.conn:
                await self.execute_set_category_income(id, dict_info)
        except Exception as e:
            # await send_message('Ошибка запроса в методе set_user', os.environ["EMAIL"], str(e))
            print(str(e))

    async def execute_set_category_income(self, id: int, dict_info: dict):
        async with self.conn.execute('PRAGMA journal_mode=wal') as cursor:

            sql_record = f"INSERT INTO CATEGORY_INCOME " \
                         f"(ID, USER_ID, NAME) " \
                         f"VALUES({id}, " \
                         f"{dict_info['user_id']}, " \
                         f"'{dict_info['name']}') " 
            await cursor.execute(sql_record)
            await self.conn.commit() 

    async def set_category_outlay(self, id: int, dict_info: dict):
        try:
            async with aiosqlite.connect(self.connect_string) as self.conn:
                await self.execute_set_category_outlay(id, dict_info)
        except Exception as e:
            # await send_message('Ошибка запроса в методе set_user', os.environ["EMAIL"], str(e))
            print(str(e))

    async def execute_set_category_outlay(self, id: int, dict_info: dict):
        async with self.conn.execute('PRAGMA journal_mode=wal') as cursor:

            sql_record = f"INSERT INTO CATEGORY_OUTLAY " \
                         f"(ID, USER_ID, NAME) " \
                         f"VALUES({id}, " \
                         f"{dict_info['user_id']}, " \
                         f"'{dict_info['name']}') " 
            await cursor.execute(sql_record)
            await self.conn.commit()   

            
    @staticmethod
    def quote(request) -> str:
        return f"'{str(request)}'"

    @staticmethod
    async def get_list(string: str) -> list:
        return string.split('///')

    @staticmethod
    async def get_str(list_item: list) -> str:
        return '///'.join(list_item)

    @staticmethod
    async def get_dict_reminder_days(string: str) -> dict:
        reminder_days = json.loads(string)
        return reminder_days

    @staticmethod
    async def get_str_reminder_days(dict_item: dict) -> str:
        dict_reminder_days = json.dumps(dict_item)
        return dict_reminder_days


# base = Execute()
# asyncio.run(base.delete_table(f"GOAL"))
# str_reminder_days = json.dumps({'MON': 0, 'TUE': 0, 'WED': 0, 'THU': 0, 'FRI': 0, 'SAT': 0, 'SUN': 0})
# asyncio.run(base.create_table(f"CREATE TABLE IF NOT EXISTS GOAL ("
#                               f"USER_ID INTEGER NOT NULL, "
#                               f"GOAL_NAME TEXT, "
#                               f"SUM_GOAL REAL, "
#                               f"INCOME_USER REAL, "
#                               f"INCOME_FREQUENCY INTEGER, "
#                               f"DURATION INTEGER, "
#                               f"REMINDER_DAYS TEXT , "
#                               f"REMINDER_TIME TEXT, "
#                               f"DATA_FINISH TEXT, "
#                               f"STATUS_GOAL TEXT, "
#                               f"FOREIGN KEY (USER_ID) REFERENCES USERS (ID))"))
# asyncio.run(base.create_table(f"CREATE TABLE IF NOT EXISTS CATEGORY_INCOME ("
#                               f"ID INTEGER PRIMARY KEY, "
#                               f"USER_ID INTEGER NOT NULL, "
#                               f"NAME TEXT)"))
# asyncio.run(base.show_columns('GOAL'))
# asyncio.run(base.update_goal(1, {'user_id': '1660842495', 'goal_name': 'Машина', 'sum_goal': 6000.00,
#                                  'income_user': 2000.00, 'income_frequency': 2, 'duration': 60,
#                                  'reminder_days': {'MON': 1, 'TUE': 0, 'WED': 0, 'THU': 0, 'FRI': 0, 'SAT': 1,
#                                                    'SUN': 1},
#                                  'reminder_time': '00:34', 'data_finish': '2025-01-30', 'status_goal': 'current'}))
# asyncio.run(base.delete_user(1660842495))
# asyncio.run(base.delete_goal(7))
# asyncio.run(base.show_users())
