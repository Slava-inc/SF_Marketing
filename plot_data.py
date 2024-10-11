import aiosqlite
import asyncio
import os

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
