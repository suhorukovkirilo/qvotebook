from bot import Bot
from data import BotData

if __name__ == "__main__":
    bot = Bot(BotData.TOKEN)
    print(f"{BotData.ADMIN_KEY=}")
    bot.run()
