from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import DialogManager

from handlers.admin_dialogs import AdminSG
from kb import help_kb, start_kb
from text import HELP_MESSAGE, PRIVACY_MESSAGE, WELCOME_MESSAGE, WELCOME_MESSAGE_PRIVATE

import config

commands_router = Router()


@commands_router.message(Command("start"))
async def start_handler(msg: Message, dialog_manager: DialogManager):
    if msg.chat.type == "private":
        markup = await start_kb(msg)
        await msg.answer(WELCOME_MESSAGE_PRIVATE, reply_markup=markup, parse_mode='HTML')
    else:
        await msg.answer(WELCOME_MESSAGE, parse_mode='HTML')


@commands_router.message(Command("help"))
async def help_handler(msg: Message, dialog_manager: DialogManager):
    markup = await help_kb(msg)
    await msg.answer(HELP_MESSAGE, reply_markup=markup, parse_mode='HTML')


@commands_router.message(Command("privacy"))
async def privacy_handler(msg: Message, dialog_manager: DialogManager):
    markup = await help_kb(msg)
    await msg.answer(PRIVACY_MESSAGE, reply_markup=markup)


@commands_router.message(Command("admin"))
async def admin_cmd(message: Message, dialog_manager: DialogManager):
    if message.chat.type == "private":
        if message.from_user.id not in config.admins:
            return
        await dialog_manager.start(AdminSG.menu)
    else:
        return
