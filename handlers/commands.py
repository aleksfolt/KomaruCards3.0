import random
from datetime import datetime, timedelta

from aiogram import F, Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_dialog import DialogManager
import loader
from database.premium import check_premium
from database.ref_link import delete_ref_link, get_ref_link
from database.user import get_user, in_pm_change, update_last_bonus_get
from handlers.admin_dialogs import AdminSG
from handlers.premium import send_payment_method_selection
from kb import check_subscribe_keyboard, help_kb, start_kb
from states import user_button
from text import HELP_MESSAGE, PRIVACY_MESSAGE, WELCOME_MESSAGE, WELCOME_MESSAGE_PRIVATE
from loader import flyer
from database.user import set_last_get, check_last_get
commands_router = Router()


@commands_router.message(CommandStart(deep_link=True, magic=F.args.startswith("bonus_")))
async def handler_bot_start(msg: Message, command: CommandObject):
    link = await get_ref_link(command.args.split("_")[-1])

    if link is None:
        await msg.answer("Бонус не найден или использован")
        return

    user_id = link.for_user_id
    if user_id != msg.from_user.id:
        await msg.answer("Этот бонус предназначен для другого пользователя")
        return

    user = await get_user(msg.from_user.id)
    if user.check_bonus_available():
        is_subscribe = await flyer.check(msg.from_user.id, msg.from_user.language_code)
        if is_subscribe:
            if await check_last_get(user.last_usage, await check_premium(user.premium_expire)):
                await msg.answer("У вас есть возможность получить карточку сейчас, используйте ее "
                                 "и возвращайтесь за бонусом!")
            else:
                await update_last_bonus_get(msg.from_user.id)
                await delete_ref_link(link.code)
                await set_last_get(user.telegram_id, datetime.now() - timedelta(hours=4))
                await msg.answer("Бонус получен. Вы можете снова получить карточку")
        else:
            await msg.answer("После подписки на каналы спонсоров нажмите что бы получить бонус",
                             reply_markup=await check_subscribe_keyboard(link.code))
    else:
        await msg.answer("Упс... 12 часов с последнего бонуса не пришло")


@commands_router.callback_query(F.data.startswith("check_subscribe_"))
async def check_subscribe(callback: CallbackQuery, dialog_manager: DialogManager):
    link_code = callback.data.split('_')[-1]
    is_subscribe = await flyer.check(callback.from_user.id, callback.from_user.language_code)
    user = await get_user(callback.from_user.id)
    if is_subscribe:
        if await check_last_get(user.last_usage, await check_premium(user.premium_expire)):
            await callback.message.answer("У вас есть возможность получить карточку сейчас, используйте ее "
                                          "и возвращайтесь за бонусом!")
        else:
            await update_last_bonus_get(callback.from_user.id)
            await delete_ref_link(link_code)
            await set_last_get(user.telegram_id, datetime.now() - timedelta(hours=4))
            await callback.message.answer("Бонус получен. Вы можете снова получить карточку")
            await callback.message.delete()
    else:
        await callback.answer("Подпишитесь что бы получить бонус")

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
