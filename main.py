import asyncio
import logging
import threading

import schedule
from aiogram import Dispatcher
from aiogram import types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram_dialog import DialogManager, setup_dialogs

import loader
from database import setup_db
from database.cards import parse_cards
from database.statistic import create_app_if_not_exist, update_yesterday_last_activities
from handlers import commands_router, premium_router, profile_router, text_triggers_router
from handlers.admin_dialogs import dialogs_router
from loader import bot
from middlewares import BannedMiddleware, RegisterMiddleware, ThrottlingMiddleware
from utils.on_startup import on_startup

logging.basicConfig(level=logging.WARNING)
dp = Dispatcher(storage=MemoryStorage(), on_startup=on_startup)


async def main():
    await setup_db()
    dp.include_routers(commands_router, profile_router, text_triggers_router, premium_router, dialogs_router)
    dp.message.middleware(ThrottlingMiddleware())
    dp.message.middleware(RegisterMiddleware())
    dp.message.middleware(BannedMiddleware())
    setup_dialogs(dp)
    await bot.delete_webhook(drop_pending_updates=True)
    dp.startup.register(on_startup)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


@dp.message(Command("test"))
async def test(msg: types.Message, dialog_manager: DialogManager):
    if msg.from_user.id not in loader.admins:
        return
    await parse_cards("config.json")


if __name__ == "__main__":

    asyncio.run(main())
