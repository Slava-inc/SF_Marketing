import json
import logging
import aiosqlite
import os
from operator import itemgetter
from dotenv import load_dotenv
from prettytable import PrettyTable
from exception import send_message

load_dotenv()
logging.basicConfig(level=logging.INFO)


class Execute:
    def __init__(self):
        self.connect_string = os.path.join(os.path.split(os.path.dirname(__file__))[0], os.environ["CONNECTION"])
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

    async def add_column(self, name_table: str, name_column: str, type_column: str):
        try:
            async with aiosqlite.connect(self.connect_string) as self.conn:
                await self.execute_add_column(name_table, name_column, type_column)
        except Exception as e:
            await send_message('Ошибка запроса в методе add_column', os.environ["EMAIL"], str(e))

    async def execute_add_column(self, name_table: str, name_column: str, type_column: str):
        async with self.conn.execute('PRAGMA journal_mode=wal') as cursor:
            await cursor.execute(f"ALTER TABLE {name_table} ADD COLUMN {name_column} {type_column}")
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

    @property
    async def get_dict_outlay(self) -> dict:
        try:
            async with aiosqlite.connect(self.connect_string) as self.conn:
                return await self.execute_get_dict_outlay()
        except Exception as e:
            await send_message('Ошибка запроса в методе get_dict_outlay', os.environ["EMAIL"], str(e))

    async def execute_get_dict_outlay(self) -> dict:
        async with self.conn.execute('PRAGMA journal_mode=wal') as cursor:
            sql_list_outlay = f"SELECT ROWID, USER_ID, DATA_TIME, SUM, NAME_BANK, RECIPIENT_FUNDS, CATEGORY_OUT, " \
                              f"STATUS_OUTLAY " \
                              f"FROM OUTLAY "
            await cursor.execute(sql_list_outlay)
            row_table = await cursor.fetchall()
            dict_outlay = {}
            for item in row_table:
                dict_outlay[item[0]] = {'user_id': item[1], 'data_time': item[2], 'sum_outlay': item[3],
                                        'name_bank': item[4], 'recipient_funds': item[5], 'category_out': item[6],
                                        'status_outlay': item[7]}
            return dict_outlay

    @property
    async def get_dict_income(self) -> dict:
        try:
            async with aiosqlite.connect(self.connect_string) as self.conn:
                return await self.execute_get_dict_income()
        except Exception as e:
            await send_message('Ошибка запроса в методе get_dict_income', os.environ["EMAIL"], str(e))

    async def execute_get_dict_income(self) -> dict:
        async with self.conn.execute('PRAGMA journal_mode=wal') as cursor:
            sql_list_income = f"SELECT ROWID, USER_ID, DATA_TIME, SUM, NAME_BANK, SENDER_FUNDS, CATEGORY_IN, " \
                              f"STATUS_INCOME " \
                              f"FROM INCOME "
            await cursor.execute(sql_list_income)
            row_table = await cursor.fetchall()
            dict_income = {}
            for item in row_table:
                dict_income[item[0]] = {'user_id': item[1], 'data_time': item[2], 'sum_income': item[3],
                                        'name_bank': item[4], 'sender_funds': item[5], 'category_in': item[6],
                                        'status_income': item[7]}
            return dict_income

    async def get_dict_category_outlay(self, user_id: int) -> dict:
        try:
            async with aiosqlite.connect(self.connect_string) as self.conn:
                return await self.execute_get_dict_category_outlay(user_id)
        except Exception as e:
            await send_message('Ошибка запроса в методе get_dict_category_outlay', os.environ["EMAIL"], str(e))

    async def execute_get_dict_category_outlay(self, user_id: int) -> dict:
        async with self.conn.execute('PRAGMA journal_mode=wal') as cursor:
            sql_list_category_outlay = f"SELECT ROWID, NAME " \
                                       f"FROM CATEGORY_OUTLAY " \
                                       f"WHERE USER_ID = '{user_id}'"
            await cursor.execute(sql_list_category_outlay)
            row_table = await cursor.fetchall()
            dict_category_outlay = {}
            for item in row_table:
                dict_category_outlay[item[0]] = item[1]
            return dict_category_outlay

    async def get_dict_category_income(self, user_id: int) -> dict:
        try:
            async with aiosqlite.connect(self.connect_string) as self.conn:
                return await self.execute_get_dict_category_income(user_id)
        except Exception as e:
            await send_message('Ошибка запроса в методе get_dict_category_income', os.environ["EMAIL"], str(e))

    async def execute_get_dict_category_income(self, user_id: int) -> dict:
        async with self.conn.execute('PRAGMA journal_mode=wal') as cursor:
            sql_list_category_income = f"SELECT ROWID, NAME " \
                                       f"FROM CATEGORY_INCOME " \
                                       f"WHERE USER_ID = '{user_id}'"
            await cursor.execute(sql_list_category_income)
            row_table = await cursor.fetchall()
            dict_category_income = {}
            for item in row_table:
                dict_category_income[item[0]] = item[1]
            return dict_category_income

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

    async def check_new_outlay(self, user_id: int) -> int:
        try:
            async with aiosqlite.connect(self.connect_string) as self.conn:
                return await self.execute_check_new_outlay(user_id)
        except Exception as e:
            await send_message('Ошибка запроса в методе check_new_outlay', os.environ["EMAIL"], str(e))

    async def execute_check_new_outlay(self, user_id: int) -> int:
        async with self.conn.execute('PRAGMA journal_mode=wal') as cursor:
            sql_check_new_outlay = f"SELECT ROWID " \
                                   f"FROM OUTLAY " \
                                   f"WHERE USER_ID = '{user_id}' AND STATUS_OUTLAY = 'new' "
            await cursor.execute(sql_check_new_outlay)
            row_table = await cursor.fetchone()
            if row_table is None:
                row_id = 0
            else:
                row_id = row_table[0]
            return row_id

    async def check_new_income(self, user_id: int) -> int:
        try:
            async with aiosqlite.connect(self.connect_string) as self.conn:
                return await self.execute_check_new_income(user_id)
        except Exception as e:
            await send_message('Ошибка запроса в методе check_new_income', os.environ["EMAIL"], str(e))

    async def execute_check_new_income(self, user_id: int) -> int:
        async with self.conn.execute('PRAGMA journal_mode=wal') as cursor:
            sql_check_new_income = f"SELECT ROWID " \
                                   f"FROM INCOME " \
                                   f"WHERE USER_ID = '{user_id}' AND STATUS_INCOME = 'new' "
            await cursor.execute(sql_check_new_income)
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

    async def get_pages_goals(self, user_id: int) -> dict:
        try:
            async with aiosqlite.connect(self.connect_string) as self.conn:
                return await self.execute_get_pages_goals(user_id)
        except Exception as e:
            await send_message('Ошибка запроса в методе get_pages_goals', os.environ["EMAIL"], str(e))

    async def execute_get_pages_goals(self, user_id: int) -> dict:
        async with self.conn.execute('PRAGMA journal_mode=wal') as cursor:
            sql_list_goal = f"SELECT ROWID, USER_ID, GOAL_NAME, SUM_GOAL, INCOME_USER, INCOME_FREQUENCY, DURATION, " \
                            f"REMINDER_DAYS, REMINDER_TIME, DATA_FINISH, STATUS_GOAL " \
                            f"FROM GOAL " \
                            f"WHERE STATUS_GOAL = 'current' AND USER_ID = '{user_id}'"
            await cursor.execute(sql_list_goal)
            row_table = await cursor.fetchall()
            return self.assembling_goals(row_table)

    async def get_pages_outlay(self, user_id: int) -> dict:
        try:
            async with aiosqlite.connect(self.connect_string) as self.conn:
                return await self.execute_get_pages_outlay(user_id)
        except Exception as e:
            await send_message('Ошибка запроса в методе get_pages_outlay', os.environ["EMAIL"], str(e))

    async def execute_get_pages_outlay(self, user_id: int) -> dict:
        async with self.conn.execute('PRAGMA journal_mode=wal') as cursor:
            sql_list_outlay = f"SELECT ROWID, USER_ID, DATA_TIME, SUM, NAME_BANK, RECIPIENT_FUNDS, CATEGORY_OUT, " \
                              f"STATUS_OUTLAY " \
                              f"FROM OUTLAY " \
                              f"WHERE STATUS_OUTLAY = 'current' AND USER_ID = '{user_id}'"
            await cursor.execute(sql_list_outlay)
            row_table = await cursor.fetchall()
            return self.assembling_outlay(row_table)

    async def get_pages_income(self, user_id: int) -> dict:
        try:
            async with aiosqlite.connect(self.connect_string) as self.conn:
                return await self.execute_get_pages_income(user_id)
        except Exception as e:
            await send_message('Ошибка запроса в методе get_pages_income', os.environ["EMAIL"], str(e))

    async def execute_get_pages_income(self, user_id: int) -> dict:
        async with self.conn.execute('PRAGMA journal_mode=wal') as cursor:
            sql_list_income = f"SELECT ROWID, USER_ID, DATA_TIME, SUM, NAME_BANK, SENDER_FUNDS, CATEGORY_IN, " \
                              f"STATUS_INCOME " \
                              f"FROM INCOME " \
                              f"WHERE STATUS_INCOME = 'current' AND USER_ID = '{user_id}'"
            await cursor.execute(sql_list_income)
            row_table = await cursor.fetchall()
            return self.assembling_income(row_table)

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

    async def insert_outlay(self, user_id: int, dict_info_outlay: dict) -> int:
        try:
            async with aiosqlite.connect(self.connect_string) as self.conn:
                return await self.execute_insert_outlay(user_id, dict_info_outlay)
        except Exception as e:
            await send_message('Ошибка запроса в методе insert_outlay', os.environ["EMAIL"], str(e))

    async def execute_insert_outlay(self, user_id: int, dict_info_outlay: dict):
        async with self.conn.execute('PRAGMA journal_mode=wal') as cursor:
            sql_insert_outlay = f"INSERT INTO OUTLAY " \
                                f"(USER_ID, DATA_TIME, SUM, NAME_BANK, RECIPIENT_FUNDS, CATEGORY_OUT, STATUS_OUTLAY) " \
                                f"VALUES('{user_id}', '{dict_info_outlay['data_time']}', " \
                                f"'{dict_info_outlay['sum_outlay']}', '{dict_info_outlay['name_bank']}', " \
                                f"'{dict_info_outlay['recipient_funds']}', '{dict_info_outlay['category_out']}', " \
                                f"'{dict_info_outlay['status_outlay']}') "
            await cursor.execute(sql_insert_outlay)
            await self.conn.commit()
            return cursor.lastrowid

    async def insert_income(self, user_id: int, dict_info_income: dict) -> int:
        try:
            async with aiosqlite.connect(self.connect_string) as self.conn:
                return await self.execute_insert_income(user_id, dict_info_income)
        except Exception as e:
            await send_message('Ошибка запроса в методе insert_income', os.environ["EMAIL"], str(e))

    async def execute_insert_income(self, user_id: int, dict_info_income: dict):
        async with self.conn.execute('PRAGMA journal_mode=wal') as cursor:
            sql_insert_income = f"INSERT INTO INCOME " \
                                f"(USER_ID, DATA_TIME, SUM, NAME_BANK, SENDER_FUNDS, CATEGORY_IN, STATUS_INCOME) " \
                                f"VALUES('{user_id}', '{dict_info_income['data_time']}', " \
                                f"'{dict_info_income['sum_income']}', '{dict_info_income['name_bank']}', " \
                                f"'{dict_info_income['sender_funds']}', '{dict_info_income['category_in']}', " \
                                f"'{dict_info_income['status_income']}') "
            await cursor.execute(sql_insert_income)
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

    async def update_outlay(self, row_id: int, dict_info_outlay: dict):
        try:
            async with aiosqlite.connect(self.connect_string) as self.conn:
                await self.execute_update_outlay(row_id, dict_info_outlay)
        except Exception as e:
            await send_message('Ошибка запроса в методе update_outlay', os.environ["EMAIL"], str(e))

    async def execute_update_outlay(self, row_id: int, dict_info_outlay: dict):
        async with self.conn.execute('PRAGMA journal_mode=wal') as cursor:
            sql_update_outlay = f"UPDATE OUTLAY SET " \
                                f"USER_ID = '{dict_info_outlay['user_id']}', " \
                                f"DATA_TIME = '{dict_info_outlay['data_time']}', " \
                                f"SUM = '{dict_info_outlay['sum_outlay']}', " \
                                f"NAME_BANK = '{dict_info_outlay['name_bank']}', " \
                                f"RECIPIENT_FUNDS = '{dict_info_outlay['recipient_funds']}', " \
                                f"CATEGORY_OUT = '{dict_info_outlay['category_out']}', " \
                                f"STATUS_OUTLAY = '{dict_info_outlay['status_outlay']}' " \
                                f"WHERE ROWID = '{row_id}' "
            await cursor.execute(sql_update_outlay)
            await self.conn.commit()

    async def update_income(self, row_id: int, dict_info_income: dict):
        try:
            async with aiosqlite.connect(self.connect_string) as self.conn:
                await self.execute_update_income(row_id, dict_info_income)
        except Exception as e:
            await send_message('Ошибка запроса в методе update_income', os.environ["EMAIL"], str(e))

    async def execute_update_income(self, row_id: int, dict_info_income: dict):
        async with self.conn.execute('PRAGMA journal_mode=wal') as cursor:
            sql_update_income = f"UPDATE INCOME SET " \
                                f"USER_ID = '{dict_info_income['user_id']}', " \
                                f"DATA_TIME = '{dict_info_income['data_time']}', " \
                                f"SUM = '{dict_info_income['sum_income']}', " \
                                f"NAME_BANK = '{dict_info_income['name_bank']}', " \
                                f"SENDER_FUNDS = '{dict_info_income['sender_funds']}', " \
                                f"CATEGORY_IN = '{dict_info_income['category_in']}', " \
                                f"STATUS_INCOME = '{dict_info_income['status_income']}' " \
                                f"WHERE ROWID = '{row_id}' "
            await cursor.execute(sql_update_income)
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

    async def delete_outlay(self, row_id: int):
        try:
            async with aiosqlite.connect(self.connect_string) as self.conn:
                await self.execute_delete_outlay(row_id)
        except Exception as e:
            await send_message('Ошибка запроса в методе delete_outlay', os.environ["EMAIL"], str(e))

    async def execute_delete_outlay(self, row_id: int):
        async with self.conn.execute('PRAGMA journal_mode=wal') as cursor:
            sql_delete = f"DELETE FROM OUTLAY WHERE ROWID = {self.quote(row_id)} "
            await cursor.execute(sql_delete)
            await self.conn.commit()

    async def delete_income(self, row_id: int):
        try:
            async with aiosqlite.connect(self.connect_string) as self.conn:
                await self.execute_delete_income(row_id)
        except Exception as e:
            await send_message('Ошибка запроса в методе delete_income', os.environ["EMAIL"], str(e))

    async def execute_delete_income(self, row_id: int):
        async with self.conn.execute('PRAGMA journal_mode=wal') as cursor:
            sql_delete = f"DELETE FROM INCOME WHERE ROWID = {self.quote(row_id)} "
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

    async def show_outlay(self):
        try:
            async with aiosqlite.connect(self.connect_string) as self.conn:
                await self.execute_show_outlay()
        except Exception as e:
            await send_message('Ошибка запроса в методе show_outlay', os.environ["EMAIL"], str(e))

    async def execute_show_outlay(self):
        async with self.conn.execute('PRAGMA journal_mode=wal') as cursor:
            sql_show_outlay = f"SELECT ROWID, USER_ID, DATA_TIME, SUM, NAME_BANK, RECIPIENT_FUNDS, CATEGORY_OUT, " \
                              f"STATUS_OUTLAY " \
                              f"FROM OUTLAY "
            await cursor.execute(sql_show_outlay)
            row_table = await cursor.fetchall()
            if not row_table:
                print(f"В базе нет расходов")
            else:
                my_table = PrettyTable()
                my_table.field_names = ["ROWID", "USER_ID", "DATA_TIME", "SUM", "NAME_BANK", "RECIPIENT_FUNDS",
                                        "CATEGORY_OUT", "STATUS_OUTLAY"]
                for item in row_table:
                    my_table.add_row([item[0], item[1], item[2], item[3], item[4], item[5], item[6],
                                      item[7]])
                print(my_table)
                print(f"В базе {len(row_table)} расходов")

    async def show_income(self):
        try:
            async with aiosqlite.connect(self.connect_string) as self.conn:
                await self.execute_show_income()
        except Exception as e:
            await send_message('Ошибка запроса в методе show_income', os.environ["EMAIL"], str(e))

    async def execute_show_income(self):
        async with self.conn.execute('PRAGMA journal_mode=wal') as cursor:
            sql_show_income = f"SELECT ROWID, USER_ID, DATA_TIME, SUM, NAME_BANK, SENDER_FUNDS, CATEGORY_IN, " \
                              f"STATUS_INCOME " \
                              f"FROM INCOME "
            await cursor.execute(sql_show_income)
            row_table = await cursor.fetchall()
            if not row_table:
                print(f"В базе нет доходов")
            else:
                my_table = PrettyTable()
                my_table.field_names = ["ROWID", "USER_ID", "DATA_TIME", "SUM", "NAME_BANK", "SENDER_FUNDS",
                                        "CATEGORY_IN", "STATUS_INCOME"]
                for item in row_table:
                    my_table.add_row([item[0], item[1], item[2], item[3], item[4], item[5], item[6],
                                      item[7]])
                print(my_table)
                print(f"В базе {len(row_table)} доходов")

    async def show_category(self, name_table: str):
        try:
            async with aiosqlite.connect(self.connect_string) as self.conn:
                await self.execute_show_category(name_table)
        except Exception as e:
            await send_message('Ошибка запроса в методе show_category', os.environ["EMAIL"], str(e))

    async def execute_show_category(self, name_table: str):
        async with self.conn.execute('PRAGMA journal_mode=wal') as cursor:
            sql_show_category = f"SELECT ROWID, USER_ID, NAME FROM {name_table} "
            await cursor.execute(sql_show_category)
            row_table = await cursor.fetchall()
            if not row_table:
                print(f"В базе нет категорий")
            else:
                my_table = PrettyTable()
                my_table.field_names = ["ROWID", "USER_ID", "NAME"]
                for item in row_table:
                    my_table.add_row([item[0], item[1], item[2]])
                print(my_table)
                print(f"В базе {len(row_table)} категорий")

    async def get_category_keyboard(self, user_id: int, name_table: str) -> dict:
        try:
            async with aiosqlite.connect(self.connect_string) as self.conn:
                return await self.execute_get_category_keyboard(user_id, name_table)
        except Exception as e:
            await send_message('Ошибка запроса в методе get_category_keyboard', os.environ["EMAIL"], str(e))

    async def execute_get_category_keyboard(self, user_id: int, name_table: str) -> dict:
        async with self.conn.execute('PRAGMA journal_mode=wal') as cursor:
            sql_get_category = f"SELECT ROWID, NAME FROM '{name_table}' WHERE USER_ID = '{user_id}' "
            await cursor.execute(sql_get_category)
            row_table = await cursor.fetchall()
            dict_category = {}
            for item in row_table:
                if name_table == 'CATEGORY_OUTLAY':
                    dict_category[f"category_outlay_row{str(item[0])}"] = item[1]
                else:
                    dict_category[f"category_income_row{str(item[0])}"] = item[1]
            return dict_category

    async def set_default_category(self, user_id: int):
        try:
            async with aiosqlite.connect(self.connect_string) as self.conn:
                await self.execute_set_default_category(user_id)
        except Exception as e:
            await send_message('Ошибка запроса в методе set_default_category_outlay', os.environ["EMAIL"], str(e))

    async def execute_set_default_category(self, user_id: int):
        async with self.conn.execute('PRAGMA journal_mode=wal') as cursor:
            default_category = ['Автомобиль 🏎️', 'Бизнес  👨‍💼', 'Подарки 🎁', 'Быт.техника 📻', 'Дети 👶',
                                'Питомцы🐱🐕', 'Здоровье 💊', 'Долг/кредиты💳',
                                'Ком.платежи 🏠', 'Налоги 📒', 'Образование 🧑‍🎓',
                                'Одежда 👒👗', 'Отдых 🏖️', 'Питание 🍴🥄',
                                'Ремонт/мебель🛏', 'Товары дом🧼🧹', 'Транспорт 🚌🚇',  'Хобби 🎩',
                                'Связь/интернет 🌏', 'Прочие 📋']
            for category_name in default_category:
                sql_category = f"INSERT INTO CATEGORY_OUTLAY " \
                               f"(USER_ID, NAME) " \
                               f"VALUES('{user_id}', '{category_name}') "
                await cursor.execute(sql_category)
            default_category = ['Аванс 💵', 'Алименты  👨‍💼', 'Возврат налог🧾', 'Грант 🏦', 'Дивиденды 📈',
                                'От бизнеса 💹', 'Зарплата 💰', 'Пенсия 👴',
                                'Подарки 🎁', 'Помощь 🆘', 'Премия 🤑',
                                'Выигрыш 🕊️', 'Приработок 👨‍💻', '% депозит 🏧',
                                'Пособие 💳', 'Стипендия 🧑‍🎓', 'Прочие 📋']
            for category_name in default_category:
                sql_category = f"INSERT INTO CATEGORY_INCOME " \
                               f"(USER_ID, NAME) " \
                               f"VALUES('{user_id}', '{category_name}') "
                await cursor.execute(sql_category)
            await self.conn.commit()

    async def delete_category(self, user_id: int):
        try:
            async with aiosqlite.connect(self.connect_string) as self.conn:
                await self.execute_delete_category(user_id)
        except Exception as e:
            await send_message('Ошибка запроса в методе delete_category', os.environ["EMAIL"], str(e))

    async def execute_delete_category(self, user_id: int):
        async with self.conn.execute('PRAGMA journal_mode=wal') as cursor:
            sql_delete = f"DELETE FROM CATEGORY_OUTLAY WHERE USER_ID = {self.quote(user_id)} "
            await cursor.execute(sql_delete)
            sql_delete = f"DELETE FROM CATEGORY_INCOME WHERE USER_ID = {self.quote(user_id)} "
            await cursor.execute(sql_delete)
            await self.conn.commit()

    async def set_category_income(self, user_id: int, category_name: str):
        try:
            async with aiosqlite.connect(self.connect_string) as self.conn:
                await self.execute_set_category_income(user_id, category_name)
        except Exception as e:
            await send_message('Ошибка запроса в методе set_category_income', os.environ["EMAIL"], str(e))

    async def execute_set_category_income(self, user_id: int, category_name: str):
        async with self.conn.execute('PRAGMA journal_mode=wal') as cursor:
            sql_category = f"INSERT INTO CATEGORY_INCOME " \
                           f"(USER_ID, NAME) " \
                           f"VALUES('{user_id}', '{category_name}') "
            await cursor.execute(sql_category)
            await self.conn.commit() 

    async def set_category_outlay(self, user_id: int, category_name: str):
        try:
            async with aiosqlite.connect(self.connect_string) as self.conn:
                await self.execute_set_category_outlay(user_id, category_name)
        except Exception as e:
            await send_message('Ошибка запроса в методе set_category_outlay', os.environ["EMAIL"], str(e))

    async def execute_set_category_outlay(self, user_id: int, category_name: str):
        async with self.conn.execute('PRAGMA journal_mode=wal') as cursor:
            sql_category = f"INSERT INTO CATEGORY_OUTLAY " \
                           f"(USER_ID, NAME) " \
                           f"VALUES('{user_id}', '{category_name}') "
            await cursor.execute(sql_category)
            await self.conn.commit()   

    async def get_row_id_category_outlay(self, user_id: int, category_name: str) -> int:
        try:
            async with aiosqlite.connect(self.connect_string) as self.conn:
                return await self.execute_get_row_id_category_outlay(user_id, category_name)
        except Exception as e:
            await send_message('Ошибка запроса в методе get_row_id_category_outlay', os.environ["EMAIL"], str(e))

    async def execute_get_row_id_category_outlay(self, user_id: int, category_name: str) -> int:
        async with self.conn.execute('PRAGMA journal_mode=wal') as cursor:
            sql_get_row_id_category_outlay = f"SELECT ROWID " \
                                             f"FROM CATEGORY_OUTLAY " \
                                             f"WHERE USER_ID = '{user_id}' AND NAME = '{category_name}'"
            await cursor.execute(sql_get_row_id_category_outlay)
            row_table = await cursor.fetchone()
            if row_table is None:
                row_id = 0
            else:
                row_id = row_table[0]
            return row_id

    async def get_row_id_category_income(self, user_id: int, category_name: str) -> int:
        try:
            async with aiosqlite.connect(self.connect_string) as self.conn:
                return await self.execute_get_row_id_category_income(user_id, category_name)
        except Exception as e:
            await send_message('Ошибка запроса в методе get_row_id_category_income', os.environ["EMAIL"], str(e))

    async def execute_get_row_id_category_income(self, user_id: int, category_name: str) -> int:
        async with self.conn.execute('PRAGMA journal_mode=wal') as cursor:
            sql_get_row_id_category_income = f"SELECT ROWID " \
                                             f"FROM CATEGORY_INCOME " \
                                             f"WHERE USER_ID = '{user_id}' AND NAME = '{category_name}' "
            await cursor.execute(sql_get_row_id_category_income)
            row_table = await cursor.fetchone()
            if row_table is None:
                row_id = 0
            else:
                row_id = row_table[0]
            return row_id

    async def get_name_category_outlay(self, row_id: int) -> str:
        try:
            async with aiosqlite.connect(self.connect_string) as self.conn:
                return await self.execute_get_name_category_outlay(row_id)
        except Exception as e:
            await send_message('Ошибка запроса в методе get_name_category_outlay', os.environ["EMAIL"], str(e))

    async def execute_get_name_category_outlay(self, row_id: int) -> str:
        async with self.conn.execute('PRAGMA journal_mode=wal') as cursor:
            sql_get_name_category_outlay = f"SELECT NAME " \
                                           f"FROM CATEGORY_OUTLAY " \
                                           f"WHERE ROWID = '{row_id}' "
            await cursor.execute(sql_get_name_category_outlay)
            row_table = await cursor.fetchone()
            if row_table is None:
                row_id = 0
            else:
                row_id = row_table[0]
            return row_id

    async def get_name_category_income(self, row_id: int) -> str:
        try:
            async with aiosqlite.connect(self.connect_string) as self.conn:
                return await self.execute_get_name_category_income(row_id)
        except Exception as e:
            await send_message('Ошибка запроса в методе get_name_category_income', os.environ["EMAIL"], str(e))

    async def execute_get_name_category_income(self, row_id: int) -> str:
        async with self.conn.execute('PRAGMA journal_mode=wal') as cursor:
            sql_get_name_category_income = f"SELECT NAME " \
                                           f"FROM CATEGORY_INCOME " \
                                           f"WHERE ROWID = '{row_id}' "
            await cursor.execute(sql_get_name_category_income)
            row_table = await cursor.fetchone()
            if row_table is None:
                row_id = 0
            else:
                row_id = row_table[0]
            return row_id

    async def get_data_diagram_outlay(self, user_id: int):
        try:
            async with aiosqlite.connect(self.connect_string) as self.conn:
                return await self.execute_get_data_diagram_outlay(user_id)
        except Exception as e:
            await send_message('Ошибка запроса в методе get_data_diagram_outlay', os.environ["EMAIL"], str(e))

    async def execute_get_data_diagram_outlay(self, user_id: int):
        async with self.conn.execute('PRAGMA journal_mode=wal') as cursor:
            sql_get_data_diagram_outlay = f"SELECT CATEGORY_OUTLAY.NAME, sum(OUTLAY.SUM) " \
                                          f"FROM OUTLAY " \
                                          f"INNER JOIN CATEGORY_OUTLAY " \
                                          f"ON OUTLAY.CATEGORY_OUT = CATEGORY_OUTLAY.ROWID " \
                                          f"AND OUTLAY.USER_ID = '{user_id}' " \
                                          f"GROUP BY CATEGORY_OUT"
            await cursor.execute(sql_get_data_diagram_outlay)
            row_table = await cursor.fetchall()
            list_name = []
            list_value = []
            if row_table:
                for item in row_table:
                    list_name.append(item[0])
                    list_value.append(item[1])
            return list_name, list_value

    async def get_data_diagram_income(self, user_id: int):
        try:
            async with aiosqlite.connect(self.connect_string) as self.conn:
                return await self.execute_get_data_diagram_income(user_id)
        except Exception as e:
            await send_message('Ошибка запроса в методе get_data_diagram_income', os.environ["EMAIL"], str(e))

    async def execute_get_data_diagram_income(self, user_id: int):
        async with self.conn.execute('PRAGMA journal_mode=wal') as cursor:
            sql_get_data_diagram_income = f"SELECT CATEGORY_INCOME.NAME, sum(INCOME.SUM) " \
                                          f"FROM INCOME " \
                                          f"INNER JOIN CATEGORY_INCOME " \
                                          f"ON INCOME.CATEGORY_IN = CATEGORY_INCOME.ROWID " \
                                          f"AND INCOME.USER_ID = '{user_id}' " \
                                          f"GROUP BY CATEGORY_IN"
            await cursor.execute(sql_get_data_diagram_income)
            row_table = await cursor.fetchall()
            list_name = []
            list_value = []
            if row_table:
                for item in row_table:
                    list_name.append(item[0])
                    list_value.append(item[1])
            return list_name, list_value
            
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

    @staticmethod
    def assembling_goals(arr: list) -> dict:
        assembling_dict_goals = {}
        dict_goal = {}
        i = 1
        y = 1
        for item_goal in sorted(arr, key=itemgetter(3), reverse=True):
            if i < 7:
                dict_goal[item_goal[0]] = [item_goal[1], item_goal[2], item_goal[3],
                                           item_goal[4], item_goal[5], item_goal[6],
                                           item_goal[7], item_goal[8], item_goal[9],
                                           item_goal[10]]
                i += 1

            else:
                assembling_dict_goals['Цели Стр.' + str(y)] = dict_goal
                i = 1
                dict_goal = {}
                y += 1
                dict_goal[item_goal[0]] = [item_goal[1], item_goal[2], item_goal[3],
                                           item_goal[4], item_goal[5], item_goal[6],
                                           item_goal[7], item_goal[8], item_goal[9],
                                           item_goal[10]]
                i += 1
        assembling_dict_goals['Цели Стр.' + str(y)] = dict_goal
        return assembling_dict_goals

    @staticmethod
    def assembling_outlay(arr: list) -> dict:
        assembling_dict_outlay = {}
        dict_goal = {}
        i = 1
        y = 1
        for item_goal in arr:
            if i < 7:
                dict_goal[item_goal[0]] = [item_goal[1], item_goal[2], item_goal[3],
                                           item_goal[4], item_goal[5], item_goal[6],
                                           item_goal[7]]
                i += 1

            else:
                assembling_dict_outlay['Расходы Стр.' + str(y)] = dict_goal
                i = 1
                dict_goal = {}
                y += 1
                dict_goal[item_goal[0]] = [item_goal[1], item_goal[2], item_goal[3],
                                           item_goal[4], item_goal[5], item_goal[6],
                                           item_goal[7]]
                i += 1
        assembling_dict_outlay['Расходы Стр.' + str(y)] = dict_goal
        return assembling_dict_outlay

    @staticmethod
    def assembling_income(arr: list) -> dict:
        assembling_dict_income = {}
        dict_goal = {}
        i = 1
        y = 1
        for item_goal in arr:
            if i < 7:
                dict_goal[item_goal[0]] = [item_goal[1], item_goal[2], item_goal[3],
                                           item_goal[4], item_goal[5], item_goal[6],
                                           item_goal[7]]
                i += 1

            else:
                assembling_dict_income['Доходы Стр.' + str(y)] = dict_goal
                i = 1
                dict_goal = {}
                y += 1
                dict_goal[item_goal[0]] = [item_goal[1], item_goal[2], item_goal[3],
                                           item_goal[4], item_goal[5], item_goal[6],
                                           item_goal[7]]
                i += 1
        assembling_dict_income['Доходы Стр.' + str(y)] = dict_goal
        return assembling_dict_income
