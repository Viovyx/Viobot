import aioschedule as schedule
import asyncio

from automations import bday


async def schedules(bot):
    print("RUNNING: schedules.py")

    schedule.every().day.at("00:00").do(lambda: bday.check(bot))

    # debugging (run every 5sec instead of each day):
    # schedule.every(5).seconds.do(lambda: bday.check(bot))

    while True:
        await schedule.run_pending()
        await asyncio.sleep(1)
