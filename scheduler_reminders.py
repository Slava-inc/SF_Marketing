from apscheduler.schedulers.asyncio import AsyncIOScheduler


class Reminders(AsyncIOScheduler):
    def __init__(self, dispatcher, functions, keyboard, **kw):
        AsyncIOScheduler.__init__(self, timezone='Europe/Moscow', **kw)
        self.dispatcher = dispatcher
        self.functions = functions
        self.keyboard = keyboard

    async def add_new_reminder(self, row_id, dict_info_goal: dict):
        for key, item in dict_info_goal['reminder_days'].items():
            if item:
                text_reminder = await self.keyboard.text_for_reminder(dict_info_goal)
                hour = int(dict_info_goal['reminder_time'].split(':')[0])
                minute = int(dict_info_goal['reminder_time'].split(':')[1])
                end_date = dict_info_goal['data_finish']
                self.add_job(self.functions.send_reminder, 'cron', day_of_week=key, hour=hour, minute=minute,
                             end_date=end_date, args=[dict_info_goal['user_id'], text_reminder],
                             id=f'goal_{str(row_id)}_{key}', jobstore='default')

    async def delete_reminder(self, row_id, dict_info_goal: dict):
        for key, item in dict_info_goal['reminder_days'].items():
            if item:
                self.remove_job(f'goal_{str(row_id)}_{key}', 'default')

    async def add_newsletter(self, user_id: int, text_recommendation):
        self.add_job(self.functions.send_recommendation, 'cron', day_of_week='mon-sun', hour=14, minute=10,
                     end_date='2025-12-31', args=[user_id, text_recommendation], id=f'news_{str(user_id)}',
                     jobstore='default')
