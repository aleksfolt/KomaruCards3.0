import asyncio
import logging

import schedule
from colorama import Fore

from database.statistic import create_app_if_not_exist, update_yesterday_last_activities


async def schedule_checker():
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)


async def setup_logger():
    logger = logging.getLogger("bot")
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        f'{Fore.BLUE}%(asctime)s:{Fore.RESET} %(levelname)s: %(message)s', datefmt='%d.%m %R')
    )
    logger.addHandler(console_handler)
    logger.setLevel(logging.WARN)


# noinspection PyAsyncCall
async def on_startup():
    await setup_logger()
    logger = logging.getLogger("bot")
    logger.warning("Bot started!")
    await create_app_if_not_exist()
    schedule.every().day.at("23:59:00").do(lambda: asyncio.create_task(update_yesterday_last_activities()))
    asyncio.create_task(schedule_checker())
