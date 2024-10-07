import os
from dispatcher import BotTelegram

if __name__ == '__main__':
    bot = BotTelegram(os.environ["BOT_TOKEN"])
    bot.run()
