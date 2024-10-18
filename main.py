import os
from dispatcher import BotTelegram
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), 'env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

if __name__ == '__main__':
    try:
        bot = BotTelegram(os.environ["BOT_TOKEN"])
        bot.run()
    except KeyboardInterrupt:
        print('FinAppBot остановлен вручную')
