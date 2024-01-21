import os
import time
from datetime import datetime

import aioschedule as schedule
import asyncio
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from tinydb import TinyDB, Query

from shared import ROOT_DIR

User = Query()


async def bday_check(bot):
    load_dotenv()
    db = TinyDB(f'{ROOT_DIR}/db/bdays.json', indent=4, create_dirs=True)
    db.default_table_name = 'bdays'
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    channel_id = os.getenv('BDAY_CHANNEL_ID')
    channel = bot.get_channel(channel_id)

    for entry in db.all():
        bday_str = entry.get('bday')
        bday = datetime.strptime(bday_str, '%Y-%m-%d %H:%M:%S')
        age = (datetime.now() - relativedelta(years=int(bday.strftime('%Y')))).strftime('%Y').replace('0', '')

        if bday.strftime('%m-%d') == today.strftime('%m-%d'):
            print(f"bday today of {entry.get('user')}(uid:{entry.get('user-id')}): {bday}")
            if entry.get('user'):
                time.sleep(1)
                await channel.send(f"Happy Birthday to <@{entry.get('user-id')}>! They became {age} years old today 🎉🥳")
            else:
                print(f"User not found with ID: {entry.get('user-id')}")

        # Debug - (spams console for each user)
        # else:
        # print(f"no bday for {entry.get('user')} today")

    db.close()


async def schedules(bot):
    print("RUNNING: schedules.py")

    schedule.every().day.at("00:00").do(lambda: bday_check(bot))

    # debugging (run every 5sec instead of each day):
    # schedule.every(5).seconds.do(lambda: bday_check(bot))

    while True:
        await schedule.run_pending()
        await asyncio.sleep(1)
