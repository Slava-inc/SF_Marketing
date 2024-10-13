import aiosqlite
import asyncio
import os
import json

class Execute:
    def __init__(self):
        self.connect_string = os.path.join(os.path.split(os.path.dirname(__file__))[0], os.environ["CONNECTION"])
        self.conn = None

    async def create_table(self, text_execute: str):
        try:
            async with aiosqlite.connect(self.connect_string) as self.conn:
                await self.execute_create_table(text_execute)
        except Exception as e:
            print(f'Ошибка запроса в методе create_table {str(e)}')

    async def execute_create_table(self, text_execute: str):
        async with self.conn.execute('PRAGMA journal_mode=wal') as cursor:
            sql_create_table = text_execute
            await cursor.execute(sql_create_table)
            await self.conn.commit()

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

if __name__ == "__main__":
    base = Execute()
    asyncio.run(base.create_table(f"CREATE TABLE IF NOT EXISTS CATEGORY_INCOME ("
                                  f"ID INTEGER PRIMARY KEY, "
                                  f"USER_ID integer, "                                  
                                  f"NAME  TEXT)"))
    
    # asyncio.run(base.set_category_income(1, {'user_id': 1710730454, 'name': 'my salary'})) 
    # asyncio.run(base.set_category_income(2, {'user_id': 1710730454, 'name': 'my wife salary'})) 
    # asyncio.run(base.set_category_income(3, {'user_id': 1710730454, 'name': 'stock revenue'})) 
    asyncio.run(base.create_table(f"CREATE TABLE IF NOT EXISTS CATEGORY_OUTLAY ("
                                  f"ID INTEGER PRIMARY KEY, "
                                  f"USER_ID integer, "                                  
                                  f"NAME  TEXT)"))

    # asyncio.run(base.set_category_outlay(1, {'user_id': 1710730454, 'name': 'food'})) 
    # asyncio.run(base.set_category_outlay(2, {'user_id': 1710730454, 'name': 'entertainment'})) 
    # asyncio.run(base.set_category_outlay(3, {'user_id': 1710730454, 'name': 'free '})) 

    
    # asyncio.run(base.delete_table(f"GOAL"))
    str_reminder_days = json.dumps({'MON': 0, 'TUE': 0, 'WED': 0, 'THU': 0, 'FRI': 0, 'SAT': 0, 'SUN': 0})
    asyncio.run(base.create_table(f"CREATE TABLE IF NOT EXISTS USERS ("
                                  f"ID INTEGER PRIMARY KEY, "
                                  f"HISTORY text, "                                  
                                  f"MESSAGES  TEXT, "
                                  f"FIRST_NAME   TEXT, "
                                  f"LAST_NAME   TEXT, "
                                  f"USER_NAME   TEXT)"))
    asyncio.run(base.set_user(1710730454, {'history': '/start', 'messages': 'message1',
                                             'first_name': 'Felix', 'last_name':'Dzerjinsky', 'user_name': 'Iron'}))
    
    asyncio.run(base.create_table(f"CREATE TABLE IF NOT EXISTS GOAL ("
                                  f"USER_ID INTEGER NOT NULL, "
                                  f"GOAL_NAME TEXT, "
                                  f"SUM_GOAL REAL, "
                                  f"INCOME_USER REAL, "
                                  f"INCOME_FREQUENCY INTEGER, "
                                  f"DURATION INTEGER, "
                                  f"REMINDER_DAYS TEXT , "
                                  f"REMINDER_TIME TEXT, "
                                  f"DATA_FINISH TEXT, "
                                  f"STATUS_GOAL TEXT, "
                                  f"FOREIGN KEY (USER_ID) REFERENCES USERS (ID))"))
    
    asyncio.run(base.create_table(f"CREATE TABLE IF NOT EXISTS CATEGORY_INCOME ("
                                  f"ID INTEGER PRIMARY KEY, "
                                  f"USER_ID INTEGER NOT NULL, "
                                  f"NAME TEXT)"))
    # asyncio.run(base.show_columns('GOAL'))

    asyncio.run(base.insert_goal(1, {'user_id': 1710730454, 'goal_name': 'Квартира', 'sum_goal': 6000.00,
                                             'income_user': 2000.00, 'income_frequency': 2, 'duration': 60,
                                             'reminder_days': {'MON': 0, 'TUE': 0, 'WED': 0, 'THU': 0, 'FRI': 0, 'SAT': 0,
                                                               'SUN': 0},
                                             'reminder_time': '10:00', 'data_finish': '25-01-30', 'status_goal': 'current'}))

    asyncio.run(base.update_goal(1, {'user_id': 1710730454, 'goal_name': 'Квартира', 'sum_goal': 6000.00,
                                             'income_user': 4000.00, 'income_frequency': 3, 'duration': 60,
                                             'reminder_days': {'MON': 0, 'TUE': 0, 'WED': 0, 'THU': 0, 'FRI': 0, 'SAT': 0,
                                                               'SUN': 0},
                                             'reminder_time': '10:00', 'data_finish': '25-01-30', 'status_goal': 'current'}))
    # asyncio.run(base.delete_user(1710730454))
    # asyncio.run(base.delete_goal(1660842495))
    asyncio.run(base.show_goals())    
