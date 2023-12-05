import os
from dotenv import load_dotenv
import bot

if __name__ == '__main__':
    load_dotenv()
    token = os.getenv('TOKEN')
    bot.run_discord_bot(token)
