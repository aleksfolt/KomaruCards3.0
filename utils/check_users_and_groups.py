import asyncio

from aiogram.exceptions import TelegramForbiddenError
from aiogram.enums import ChatAction
from database.group import get_all_groups_ids, in_group_change
from database.user import get_all_users_ids, in_pm_change
from loader import bot


async def check_pm_users():
    user_ids = await get_all_users_ids()
    for user_id in user_ids:
        try:
            await bot.send_chat_action(
                user_id, ChatAction.TYPING
            )
            await in_pm_change(user_id, True)
        except TelegramForbiddenError as e:
            await in_pm_change(user_id, False)
        except Exception:
            pass
        await asyncio.sleep(0.0005)


async def check_in_groups():
    groups = await get_all_groups_ids()
    for group_id in groups:
        try:
            await bot.get_chat(group_id)
            await in_group_change(group_id, True)
        except TelegramForbiddenError as e:
            await in_group_change(group_id, False)
        except Exception:
            pass
        await asyncio.sleep(0.0005)
