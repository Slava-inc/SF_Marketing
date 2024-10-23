import asyncio
from database_requests import Execute
import os

TABLES = [f"CREATE TABLE IF NOT EXISTS USERS ("
                                  f"ID INTEGER PRIMARY KEY, "
                                  f"HISTORY text, "                                  
                                  f"MESSAGES  TEXT, "
                                  f"FIRST_NAME   TEXT, "
                                  f"LAST_NAME   TEXT, "
                                  f"USER_NAME   TEXT)",
                                  "CREATE TABLE IF NOT EXISTS GOAL ("
                                  f"ROWID INTEGER PRIMARY KEY, "
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
                                  f"NAME  TEXT, "
                                  f"GOAL_ID INTEGER,"
                                  f"FOREIGN KEY (GOAL_ID) REFERENCES GOAL (ID) )",
                                  f"CREATE TABLE IF NOT EXISTS OUTLAY ("
                                  f"ROWID INTEGER PRIMARY KEY, "
                                  f"USER_ID INTEGER, "                                  
                                  f"DATA_TIME  TEXT, "
                                  f"SUM   REAL, "
                                  f"NAME_BANK   TEXT, "
                                  f"RECIPIENT_FUNDS TEXT, "
                                  f"CATEGORY_OUT INTEGER, "
                                  f"STATUS_OUTLAY TEXT, "
                                  f"FOREIGN KEY (USER_ID) REFERENCES USERS (ID), "
                                  f"FOREIGN KEY (CATEGORY_OUT) REFERENCES CATEGORY_OUTLAY (ID) )",
                                  f"CREATE TABLE IF NOT EXISTS INCOME ("
                                  f"ROWID INTEGER PRIMARY KEY, "
                                  f"USER_ID INTEGER NOT NULL, "
                                  f"DATA_TIME TEXT, "
                                  f"SUM REAL, "
                                  f"NAME_BANK TEXT, "
                                  f"SENDER_FUNDS TEXT, "
                                  f"CATEGORY_IN INTEGER, "
                                  f"STATUS_INCOME TEXT, "
                                  f"FOREIGN KEY (USER_ID) REFERENCES USERS (ID), "
                                  f"FOREIGN KEY (CATEGORY_IN) REFERENCES CATEGORY_INCOME (ID) )",]

if __name__ == "__main__":
    base = Execute(os.path.join(os.path.split(os.path.dirname(__file__))[0], "SF_marketing/db.sqlite")
)
    asyncio.run(base.create_data_base())

    for table in TABLES:
        asyncio.run(base.create_table(table))
        # break

    print('Таблицы созданы')   
    # asyncio.run(base.set_category_income(1, {'user_id': 1710730454, 'name': 'my salary'})) 
    # asyncio.run(base.set_category_income(2, {'user_id': 1710730454, 'name': 'my wife salary'})) 
    # asyncio.run(base.set_category_income(3, {'user_id': 1710730454, 'name': 'stock revenue'})) 

    # asyncio.run(base.set_category_outlay(1, {'user_id': 1710730454, 'name': 'food'})) 
    # asyncio.run(base.set_category_outlay(2, {'user_id': 1710730454, 'name': 'entertainment'})) 
    # asyncio.run(base.set_category_outlay(3, {'user_id': 1710730454, 'name': 'free '})) 


    # str_reminder_days = json.dumps({'MON': 0, 'TUE': 0, 'WED': 0, 'THU': 0, 'FRI': 0, 'SAT': 0, 'SUN': 0})

    # asyncio.run(base.set_user(1710730454, {'history': '/start', 'messages': 'message1',
    #                                          'first_name': 'Felix', 'last_name':'Dzerjinsky', 'user_name': 'Iron'}))
    

    # asyncio.run(base.insert_goal(1, {'user_id': 1710730454, 'goal_name': 'Квартира', 'sum_goal': 6000.00,
    #                                          'income_user': 2000.00, 'income_frequency': 2, 'duration': 60,
    #                                          'reminder_days': {'MON': 0, 'TUE': 0, 'WED': 0, 'THU': 0, 'FRI': 0, 'SAT': 0,
    #                                                            'SUN': 0},
    #                                          'reminder_time': '10:00', 'data_finish': '25-01-30', 'status_goal': 'current'}))

    # asyncio.run(base.update_goal(1, {'user_id': 1710730454, 'goal_name': 'Квартира', 'sum_goal': 6000.00,
    #                                          'income_user': 4000.00, 'income_frequency': 3, 'duration': 60,
    #                                          'reminder_days': {'MON': 0, 'TUE': 0, 'WED': 0, 'THU': 0, 'FRI': 0, 'SAT': 0,
    #                                                            'SUN': 0},
    #                                          'reminder_time': '10:00', 'data_finish': '25-01-30', 'status_goal': 'current'}))
    # # asyncio.run(base.delete_user(1710730454))
    # asyncio.run(base.delete_goal(1660842495))
    # asyncio.run(base.show_goals())    
