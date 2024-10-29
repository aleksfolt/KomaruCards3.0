import random

from aiogram import Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_dialog import DialogManager
import loader
from database.user import get_user, in_pm_change
from handlers.admin_dialogs import AdminSG
from handlers.premium import send_payment_method_selection
from kb import help_kb, start_kb
from states import user_button
from text import HELP_MESSAGE, PRIVACY_MESSAGE, WELCOME_MESSAGE, WELCOME_MESSAGE_PRIVATE

commands_router = Router()


@commands_router.message(CommandStart())
async def handler_start_command(msg: Message, command: CommandObject):
    if command.args == "premium":
        unique_id = str(random.randint(10000, 9999999999))
        user_button[unique_id] = str(msg.from_user.id)
        await send_payment_method_selection(msg, msg.from_user.id, unique_id)
    else:
        if msg.chat.type == "private":
            user = await get_user(msg.from_user.id)
            if user.in_pm is None or user.in_pm is False:
                await in_pm_change(msg.from_user.id, True)
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


async def admin_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(text="Рассылка", callback_data="Vvjff mailing")

    builder.button(text="Премиум", callback_data="Vjdsd premium")
    builder.button(text="Сменить ник", callback_data="Vfsdfj __change_username__")

    builder.button(text="Бан", callback_data="Vifdo ban")
    builder.button(text="Разбан", callback_data="Vjfjdk unban")

    builder.button(text="Сбросить сезон", callback_data="Vpksn reset_season")
    builder.button(text="Статистика", callback_data="VhVujk statistics")
    builder.adjust(1, 2, 2, 1, 1)

    return builder.as_markup()


@commands_router.message(Command("admin"))
async def admin_cmd(message: Message, dialog_manager: DialogManager):
    if message.chat.type == "private":
        if message.from_user.id == 851455143:
            await message.answer("Привет админ!", reply_markup=await admin_keyboard())
        if message.from_user.id not in loader.admins:
            return
        await dialog_manager.start(AdminSG.menu)
    else:
        return
