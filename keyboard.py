from database_requests import Execute
# from operator import itemgetter


class KeyBoardBot:
    def __init__(self):
        self.execute = Execute()

    @staticmethod
    async def get_first_keyboard() -> dict:
        text_start_keyboard = {'call_back1': 'Кнопка №1',
                               'call_back2': 'Кнопка №2',
                               'call_back3': 'Кнопка №3'}
        return text_start_keyboard