import os
from dispatcher import BotTelegram

if __name__ == '__main__':
    try:
        bot = BotTelegram(os.environ["BOT_TOKEN"])
        bot.run()
    except KeyboardInterrupt:
        print('FinAppBot остановлен вручную')
