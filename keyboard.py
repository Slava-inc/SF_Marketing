import json
import random
import re
from database_requests import Execute


class KeyBoardBot:
    def __init__(self):
        self.execute = Execute()

    @staticmethod
    async def get_first_menu(history: list) -> dict:
        if len(history) > 1:
            button_first_keyboard = {'goal': 'Цели 🎯',
                                     'outlay': 'Расходы 🧮',
                                     'income': 'Доходы 💰',
                                     'virtual_assistant': 'Виртуальный помощник 🤖',
                                     'back': 'Назад 🔙'}
        else:
            button_first_keyboard = {'goal': 'Цели 🎯',
                                     'outlay': 'Расходы 🧮',
                                     'income': 'Доходы 💰',
                                     'virtual_assistant': 'Виртуальный помощник 🤖'}
        return button_first_keyboard

    @staticmethod
    async def get_goal_menu():
        button_goal_keyboard = {'add_new_goal': 'Добавить новую цель ➕',
                                'show_goal': 'Показать список целей 👀',
                                'back': 'Назад 🔙'}
        return button_goal_keyboard

    @staticmethod
    async def get_outlay_menu():
        button_outlay_keyboard = {'add_new_outlay': 'Добавить новые расходы ➕',
                                  'show_outlay': 'Показать список расходов 👀',
                                  'analytic_outlay': 'Аналитика расходов 📊',
                                  'back': 'Назад 🔙'}
        return button_outlay_keyboard

    @staticmethod
    async def get_income_menu():
        button_income_keyboard = {'add_new_income': 'Добавить новые доходы ➕',
                                  'show_income': 'Показать список доходов 👀',
                                  'analytic_income': 'Аналитика доходов 📊',
                                  'back': 'Назад 🔙'}
        return button_income_keyboard

    @staticmethod
    async def get_keyboard_outlay() -> dict:
        button_outlay_keyboard = {'auto': 'Автомобиль 🏎️',
                                  'business': 'Бизнес  👨‍💼',
                                  'souvenir': 'Подарки 🎁',
                                  'home_appliances': 'Бытовая техника 📻',
                                  'children': 'Дети 👶',
                                  'pets': 'Домашние животные🐱🐕',
                                  'health ': 'Здоровье и красота 💊',
                                  'loans': 'Ипотека, долги, кредиты 💳',
                                  'communal': 'Коммунальные платежи 🏠',
                                  'taxes': 'Налоги и страхование 📒',
                                  'education': 'Образование 🧑‍🎓',
                                  'clothes': 'Одежда и аксессуары 👒👗',
                                  'relax': 'Отдых и развлечение 🏖️',
                                  'food': 'Питание 🍴🥄',
                                  'repair': 'Ремонт и мебель 🛏🛁',
                                  'household ': 'Товары для дома 🧼🧹',
                                  'transport': 'Транспорт 🚌🚇',
                                  'hobby': 'Хобби 🎩',
                                  'connection': 'Связь и интернет 🌏',
                                  'no_name': 'Прочие 📋',
                                  'back': 'Назад 🔙'}
        return button_outlay_keyboard

    @staticmethod
    async def get_bank() -> dict:
        bank_keyboard = {'Сбербанк': 'Сбербанк',
                         'ВТБ': 'ВТБ',
                         'Газпромбанк': 'Газпромбанк',
                         'Альфа-Банк': 'Альфа-Банк',
                         'Россельхозбанк': 'Россельхозбанк',
                         'МКБ': 'МКБ',
                         'Совкомбанк ': 'Совкомбанк',
                         'Т-Банк': 'Т-Банк',
                         'Росбанк': 'Росбанк',
                         'Райффайзен Банк': 'Райффайзен Банк',
                         'Открытие': 'Открытие',
                         'Ак Барс Банк': 'Ак Барс Банк',
                         'ЮниКредит Банк ': 'ЮниКредит Банк',
                         'Ситибанк': 'Ситибанк',
                         'Уралсиб': 'Уралсиб',
                         'Почта Банк': 'Почта Банк',
                         'Точка': 'Точка',
                         'Наличные': 'Наличные',
                         'back': 'Назад 🔙'}
        return bank_keyboard

    @staticmethod
    async def text_for_news() -> str:
        text = ['Не бывает статей расходов, которые не были бы важны для вас. Чтобы тратить меньше следует '
                'сокращать каждую статью пропорционально друг другу, т.е. вычитывать средства из каждой статьи '
                'в одинаковом процентном соотношении.',
                'Наибольшей оптимизации подлежат те статьи расходов, на которые уходит наибольшее количество '
                'средств из вашего бюджета, т.к. расходы по ним, скорее всего, можно сократить.',
                'Не нужно стремиться к покупкам вещей, разрекламированных как экономные, или оптовым закупкам. '
                'Психика человека устроена таким образом, что за счёт кажущейся дешевизны или предполагаемой '
                'скидки он будет неосознанно стремиться к тому, чтобы взять больше, а это означает, что и '
                'тратить он будет больше.',
                'Финансовое планирование – залог материального благополучия, наличия «подушки безопасности» в '
                'непредвиденных жизненных ситуациях, возможность достичь многих материальных целей, и даже стать '
                'финансово независимым человеком.',
                'Чтобы иметь возможность быть готовым, если уж не ко всему, то ко многому, нужно иметь чёткое '
                'представление о том, что вы будете делать в той или иной ситуации, а также разработать свою '
                'стратегию по достижению целей. Всё это и включает в себя финансовое планирование.',
                'Лучшим временем для приведения в порядок своего бюджета и планирования является начало года. '
                'Но, конечно же, ждать его наступления ни в коем случае не нужно. Приступайте к делу сразу же: '
                'определяйте свои цели, просчитывайте действия, ищите новые возможности и варианты. '
                'Это станет вашим первым шагом к процветанию и финансовому благополучию.',
                'Грамотное отношение к своему бюджету должно стать частью образа жизни, стимулом к профессиональному, '
                'карьерному и личностному росту; навыком, который сделает достаток вашим верным спутником и гарантом '
                'уверенности в любой жизненной ситуации.',
                'Вместо того, чтобы придерживаться жестких правил, лучше проанализировать свои финансы и определить '
                'процент, который получится комфортно откладывать каждый месяц. Без ущерба для уровня жизни.',
                'Иногда мелкие траты на удовольствия — стаканчик кофе или кино — играют важную роль в нашем '
                'психоэмоциональном состоянии, да и просто помогают расслабиться. '
                'Вместо полного исключения мелких трат, лучше установить лимит на них и следить за своими '
                'расходами в целом.',
                'Иногда покупка товара по цене на 50% дешевле оказывается «мусором», который вскоре придется '
                'заменить или даже выбросить. Последнее касается продуктов, которые по уценке первой свежести '
                'точно не будут. Вместо тотальной экономии на здоровье лучше действовать с умом и анализировать, '
                'действительно ли вам нужен продукт и стоит ли он своих денег.',
                'Лучше ограничиться одной кредитной картой, которую вы сможете обслуживать, и использовать ее не '
                'для набора бонусных баллов, а для удобства в оплате и контроля расходов.',
                'Инвестирование — это важная часть финансового планирования, но не стоит рисковать всей своей '
                'свободной наличностью. Всегда существует риск потери финансов при неудачном инвестировании. '
                'Лучше разумно распределить деньги между различными активами и инструментами с разным уровнем риска. '
                'Такой подход поможет сбалансировать доход и минимизировать потери.']
        return random.choice(text)

    async def text_for_reminder(self, dict_info_goal: dict) -> str:
        duration = int(dict_info_goal['duration'])
        monthly_payment = str(int(int(dict_info_goal['sum_goal']) / duration))
        weekday = await self.get_str_weekday(dict_info_goal['reminder_days'])
        time_reminder = dict_info_goal['reminder_time']
        data_in_message = f"{dict_info_goal['data_finish'].split('-')[2]}." \
                          f"{dict_info_goal['data_finish'].split('-')[1]}." \
                          f"{dict_info_goal['data_finish'].split('-')[0]} г."
        text = f"Напоминаем про цель, которую Вы перед собой поставили:\n" \
               f"Наименование цели: {self.format_text(dict_info_goal['goal_name'])}\n" \
               f"Сумма цели: {self.format_text(str(int(dict_info_goal['sum_goal'])))} ₽\n" \
               f"Дата завершения: {self.format_text(data_in_message)}" \
               f"Срок достижения цели: {self.format_text(str(duration))} мес.\n" \
               f"Каждый месяц нужно откладывать: {self.format_text(monthly_payment)} ₽\n" \
               f"Дни напоминания о цели: {self.format_text(weekday)}\n" \
               f"Время напоминания о цели: {self.format_text(time_reminder)}"
        return text

    async def get_info_goal(self, list_info_goal: list) -> str:
        duration = int(list_info_goal[5])
        monthly_payment = str(int(int(list_info_goal[2]) / duration))
        list_reminder_days = await self.get_dict_reminder_days(list_info_goal[6])
        weekday = await self.get_str_weekday(list_reminder_days)
        time_reminder = list_info_goal[7]
        data_in_message = f"{list_info_goal[8].split('-')[2]}." \
                          f"{list_info_goal[8].split('-')[1]}." \
                          f"{list_info_goal[8].split('-')[0]} г."
        text = f"Наименование цели: {self.format_text(list_info_goal[1])}\n" \
               f"Сумма цели: {self.format_text(str(int(list_info_goal[2])))} ₽\n" \
               f"Дата завершения: {self.format_text(data_in_message)}\n" \
               f"Срок достижения цели: {self.format_text(str(duration))} мес.\n" \
               f"Каждый месяц нужно откладывать: {self.format_text(monthly_payment)} ₽\n" \
               f"Дни напоминания о цели: {self.format_text(weekday)}\n" \
               f"Время напоминания о цели: {self.format_text(time_reminder)}"
        return text

    async def get_info_outlay(self, list_info_outlay: list) -> str:
        data_time = list_info_outlay[1]
        sum_outlay = int(list_info_outlay[2])
        name_bank = list_info_outlay[3]
        recipient_funds = list_info_outlay[4]
        value_category_out = list_info_outlay[5]
        str_category_out = await self.execute.get_name_category_outlay(value_category_out)
        text = f"Дата расходов: {self.format_text(data_time)}\n" \
               f"Сумма расходов: {self.format_text(str(sum_outlay))} ₽\n" \
               f"Способ списания расходов: {self.format_text(name_bank)}\n" \
               f"Наименование получателя: {self.format_text(recipient_funds)}\n" \
               f"Категория расходов: {self.format_text(str_category_out)}"
        return text

    async def get_info_income(self, list_info_income: list) -> str:
        data_time = list_info_income[1]
        sum_income = int(list_info_income[2])
        name_bank = list_info_income[3]
        sender_funds = list_info_income[4]
        value_category_in = list_info_income[5]
        str_category_in = await self.execute.get_name_category_income(value_category_in)
        text = f"Дата доходов: {self.format_text(data_time)}\n" \
               f"Сумма доходов: {self.format_text(str(sum_income))} ₽\n" \
               f"Способ поступления доходов: {self.format_text(name_bank)}\n" \
               f"Наименование отправителя: {self.format_text(sender_funds)}\n" \
               f"Категория доходов: {self.format_text(str_category_in)}"
        return text

    @staticmethod
    async def get_calculater() -> dict:
        calculater = {'1': '1⃣', '2': '2⃣', '3': '3⃣',
                      '4': '4⃣', '5': '5⃣', '6': '6⃣',
                      '7': '7⃣', '8': '8️⃣', '9': '9⃣',
                      'minus': '➖', '0': '0️⃣', 'plus': '➕',
                      'back': 'Назад 🔙', 'delete': '⌫'}
        return calculater

    @staticmethod
    def format_text(text_message: str) -> str:
        cleaner = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
        clean_text = re.sub(cleaner, '', text_message)
        return f'<b>{clean_text}</b>'

    @staticmethod
    async def get_weekday() -> dict:
        dict_weekday = {'MON': 'Понедельник', 'TUE': 'Вторник', 'WED': 'Среда', 'THU': 'Четверг', 'FRI': 'Пятница',
                        'SAT': 'Суббота', 'back': 'Назад 🔙', 'SUN': 'Воскресенье'}
        return dict_weekday

    @staticmethod
    async def get_time_reminder() -> dict:
        dict_time = {'06:00': '06:00', '07:00': '07:00', '08:00': '08:00', '09:00': '09:00', '10:00': '10:00',
                     '11:00': '11:00', '12:00': '12:00', '13:00': '13:00', '14:00': '14:00', '15:00': '15:00',
                     '16:00': '16:00', '17:00': '17:00', '18:00': '18:00', '19:00': '19:00', '20:00': '20:00',
                     'back': 'Назад 🔙', '21:00': '21:00', '22:00': '22:00', '23:00': '23:00', '00:00': '00:00'}
        return dict_time

    @property
    def get_pages_goal(self):
        dict_pages = {}
        for item in range(100):
            dict_pages['Цели Стр.' + str(item)] = str(item)
        return dict_pages

    @property
    def get_pages_outlay(self):
        dict_pages = {}
        for item in range(100):
            dict_pages['Расходы Стр.' + str(item)] = str(item)
        return dict_pages

    @property
    def get_pages_income(self):
        dict_pages = {}
        for item in range(100):
            dict_pages['Доходы Стр.' + str(item)] = str(item)
        return dict_pages

    async def get_str_weekday(self, dict_reminder_days: dict) -> str:
        dict_weekday = await self.get_weekday()
        list_weekday = []
        for key, item in dict_reminder_days.items():
            if item:
                list_weekday.append(dict_weekday[key])
        if len(list_weekday) == 0:
            weekday = 'Не напоминать о цели'
        else:
            weekday = ', '.join(list_weekday)
        return weekday

    @staticmethod
    async def get_dict_reminder_days(string: str) -> dict:
        reminder_days = json.loads(string)
        return reminder_days
