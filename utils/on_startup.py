import asyncio
import schedule

from database.statistic import create_app_if_not_exist, update_yesterday_last_activities


async def schedule_checker():
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)


# noinspection PyAsyncCall
async def on_startup():
    await create_app_if_not_exist()
    schedule.every().day.at("23:59:00").do(lambda: asyncio.create_task(update_yesterday_last_activities()))
    asyncio.create_task(schedule_checker())
