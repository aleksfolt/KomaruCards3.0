import asyncio
import logging
from mailbox import Message

from aiogram.filters import Command

from aiogram_dialog import setup_dialogs, DialogManager

from database.user import parse_users
from loader import bot
from aiogram import Dispatcher
from database import setup_db
from database.cards import parse_cards
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import commands_router, profile_router, text_triggers_router, premium_router
from middlewares import RegisterMiddleware, ThrottlingMiddleware, BannedMiddleware
from handlers.admin_dialogs import dialogs_router
dp = Dispatcher(storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)


async def main():
    await setup_db()
    dp.include_routers(commands_router, profile_router,  text_triggers_router, premium_router, dialogs_router)
    dp.message.middleware(ThrottlingMiddleware())
    dp.message.middleware(RegisterMiddleware())
    dp.message.middleware(BannedMiddleware())
    setup_dialogs(dp)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


@dp.message(Command("test"))
async def test(msg: Message, dialog_manager: DialogManager):
    if message.from_user.id not in config.admins:
        return
    await parse_cards("config.json")


if __name__ == "__main__":
    asyncio.run(main())
