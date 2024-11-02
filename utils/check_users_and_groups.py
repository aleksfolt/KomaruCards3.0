import asyncio
import logging
from asyncio import Semaphore

from aiogram.enums import ChatAction
from aiogram.exceptions import TelegramForbiddenError

from database.group import get_all_groups_ids, get_group_count, in_group_change
from database.user import get_all_users_ids, get_user_count, in_pm_change
from loader import bot

semaphore = Semaphore(10)

async def check_pm_users():
    user_count = await get_user_count()
    for i in range(int(user_count / 500 + 1)):
        user_ids = await get_all_users_ids(i * 500, 500)
        for user_id in user_ids:
            async with semaphore:
                try:
                    await bot.send_chat_action(user_id, ChatAction.TYPING)
                    await in_pm_change(user_id, True)
                    logging.info(user_id, " in pm")
                except TelegramForbiddenError:
                    await in_pm_change(user_id, False)
                    logging.info(user_id, " not in pm")
                except Exception as e:
                    logging.info(e)
            await asyncio.sleep(0.01)

async def check_in_groups():
    group_count = await get_group_count()
    for i in range(int(group_count / 500 + 1)):
        groups = await get_all_groups_ids(i * 500, 500)
        for group_id in groups:
            async with semaphore:
                try:
                    await bot.get_chat(group_id)
                    await in_group_change(group_id, True)
                    logging.info(group_id, " in group")
                except TelegramForbiddenError:
                    await in_group_change(group_id, False)
                    logging.info(group_id, " not in group")
                except Exception as e:
                    logging.info(e)
            await asyncio.sleep(0.01)


async def run_check():
    await asyncio.gather(check_pm_users(), check_in_groups())
