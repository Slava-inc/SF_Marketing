import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler


class Reminders(AsyncIOScheduler):
    def __init__(self, dispatcher, functions, keyboard, **kw):
        AsyncIOScheduler.__init__(self, **kw)
        self.dispatcher = dispatcher
        self.functions = functions
        self.keyboard = keyboard
        self.dict_job_reminder = {}

    async def add_new_reminder(self, row_id, dict_info_goal: dict):
        for key, item in dict_info_goal['reminder_days'].items():
            if item:
                text_reminder = await self.keyboard.text_for_reminder(dict_info_goal)
                hour = int(dict_info_goal['reminder_time'].split(':')[0])
                minute = int(dict_info_goal['reminder_time'].split(':')[1])
                end_date = dict_info_goal['data_finish']
                self.dict_job_reminder[row_id] = self.add_job(self.start_up_reminder, 'cron', day_of_week=key,
                                                              hour=hour, minute=minute, end_date=end_date,
                                                              args=[dict_info_goal['user_id'], text_reminder, row_id])

    async def start_up_reminder(self, user_id: int, text_reminder: str, row_id: int):
        task = asyncio.create_task(self.functions.send_reminder(user_id, text_reminder))
        task.set_name(f'{str(user_id)}_{str(row_id)}_task_send_reminder')
        await self.dispatcher.queues_message.start(task)

    async def add_newsletter(self, user_id: int):
        text_recommendation = await self.keyboard.text_for_news()
        self.add_job(self.start_newsletter, 'cron', day_of_week='mon-sun', hour=00, minute=35,
                     end_date='2025-12-31', args=[user_id, text_recommendation])

    async def start_newsletter(self, user_id: int, text_recommendation: str):
        task = asyncio.create_task(self.functions.send_recommendation(user_id, text_recommendation))
        task.set_name(f'{str(user_id)}_task_send_recommendation')
        await self.dispatcher.queues_message.start(task)
