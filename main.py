from config import TG_BOT_TOKEN
from bot.telegram_bot import TalkerBot

def main():
    bot = TalkerBot(TG_BOT_TOKEN)
    bot.run()

if __name__ == "__main__":
    main()