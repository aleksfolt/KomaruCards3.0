import asyncio

from aiogram import Bot
from aiogram.types import Animation, PhotoSize, Video

from database.group import get_all_groups_with_bot_ids
from database.user import get_all_users_with_pm_ids


async def mailing(send_on_groups: bool, send_dm: bool, media, text, bot: Bot):
    if media:
        if type(media) is Animation:
            coroutine = bot.send_animation
        elif type(media) is Video:
            coroutine = bot.send_video
        elif type(media[-1]) is PhotoSize:
            coroutine = bot.send_photo
        mode = "media"
    else:
        coroutine = bot.send_message
        mode = "text"

    if send_on_groups:
        await asyncio.create_task(send_all_groups(mode, coroutine, media, text, bot))
    if send_dm:
        await asyncio.create_task(send_all_users(mode, coroutine, media, text, bot))


async def send_all_groups(mode: str, coroutine, media, text, bot: Bot):
    for group_id in await get_all_groups_with_bot_ids():
        try:
            if mode == "media":
                await coroutine(group_id, media.file_id, caption=text, parse_mode='Markdown')
            else:
                await coroutine(group_id, text, parse_mode='Markdown')
        except Exception as e:
            pass


async def send_all_users(mode: str, coroutine, media, text, bot: Bot):
    for user_id in await get_all_users_with_pm_ids():
        try:
            if mode == "media":
                await coroutine(user_id, media.file_id, caption=text, parse_mode='Markdown')
            else:
                await coroutine(user_id, text, parse_mode='Markdown')
        except Exception as e:
            pass
