import asyncio

from aiogram import Bot
from aiogram.types import Animation, PhotoSize, Video

from database.group import get_all_groups
from database.models import Base
from database.user import get_all_users
from loader import engine


async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


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
    for chat in await get_all_groups():
        try:
            if mode == "media":
                await coroutine(chat.group_id, media.file_id, caption=text, parse_mode='Markdown')
            else:
                await coroutine(chat.group_id, text, parse_mode='Markdown')
        except Exception as e:
            pass


async def send_all_users(mode: str, coroutine, media, text, bot: Bot):
    for bot_user in await get_all_users():
        try:
            if mode == "media":
                await coroutine(bot_user.telegram_id, media.file_id, caption=text, parse_mode='Markdown')
            else:
                await coroutine(bot_user.telegram_id, text, parse_mode='Markdown')
        except Exception as e:
            pass
