Структура бота: https://disk.yandex.ru/i/227LsCT2ZNnYgQ

Запись встречи 10.10.2024: https://disk.yandex.ru/i/PAC2cRSQ2s09Yw

Запись встречи 17.10.2924: https://disk.yandex.ru/i/jxD8gd4JY0J9Ag

Презентация >>> https://disk.yandex.ru/i/LR8_75s6J-5Ozg <<<

Визуал бота: https://disk.yandex.ru/d/jM6SSDF-uqSTqw
import asyncio
import os
import json
from database_requests import Execute

TABLES = [f"CREATE TABLE IF NOT EXISTS USERS ("
                                  f"ID INTEGER PRIMARY KEY, "
                                  f"HISTORY text, "                                  
                                  f"MESSAGES  TEXT, "
                                  f"FIRST_NAME   TEXT, "
                                  f"LAST_NAME   TEXT, "
                                  f"USER_NAME   TEXT)",
                                  "CREATE TABLE IF NOT EXISTS GOAL ("
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
                                  f"FOREIGN KEY (USER_ID) REFERENCES USERS (ID))",
                                  f"CREATE TABLE IF NOT EXISTS CATEGORY_INCOME ("
                                  f"ID INTEGER PRIMARY KEY, "
                                  f"USER_ID INTEGER NOT NULL, "
                                  f"NAME TEXT, "
                                  f"FOREIGN KEY (USER_ID) REFERENCES USERS (ID))",
                                  f"CREATE TABLE IF NOT EXISTS CATEGORY_OUTLAY ("
                                  f"ID INTEGER PRIMARY KEY, "
                                  f"USER_ID integer, "                                  
                                  f"NAME  TEXT)",
                                  f"CREATE TABLE IF NOT EXISTS OUTLAY ("
                                  f"ID INTEGER PRIMARY KEY, "
                                  f"USER_ID INTEGER, "                                  
                                  f"DATA_TIME  TEXT, "
                                  f"SUM   REAL, "
                                  f"NAME_BANK   TEXT, "
                                  f"SENDER_FUNDS TEXT, "
                                  f"CATEGORY_OUT   INTEGER, "
                                  f"FOREIGN KEY (USER_ID) REFERENCES USERS (ID), "
                                  f"FOREIGN KEY (CATEGORY_OUT) REFERENCES CATEGORY_OUTLAY (ID) )",
                                  f"CREATE TABLE IF NOT EXISTS INCOME ("
                                  f"ID INTEGER PRIMARY KEY, "
                                  f"USER_ID INTEGER NOT NULL, "
                                  f"DATE_TIME TEXT, "
                                  f"SUM REAL, "
                                  f"NAME BANK, "
                                  f"SENDER_FUNDS TEXT, "
                                  f"CATEGORY_IN INTEGER, "
                                  f"FOREIGN KEY (USER_ID) REFERENCES USERS (ID), "
                                  f"FOREIGN KEY (CATEGORY_IN) REFERENCES CATEGORY_INCOME (ID) )",]

if __name__ == "__main__":
    base = Execute()
    asyncio.run(base.create_data_base())

    for table in TABLES:
        asyncio.run(base.create_table(table))
        # break

    print('Таблицы созданы')  
