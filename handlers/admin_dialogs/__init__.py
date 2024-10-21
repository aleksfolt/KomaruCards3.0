import io

from aiogram import Router, types
from aiogram.filters import Command

from database import get_all_groups, get_all_users
from middlewares import AdminMiddleware
from .admin_dialog import admin_dialog, AdminSG
from .premium_dialog import premium_dialog
from .ban_dialog import ban_dialog
from .unban_dialog import unban_dialog
from .season_delete_dialog import season_delete_dialog
from .change_nickname_dialog import change_nickname_dialog
from .mailing_dialog import mailing_dialog
from .create_promo_dialog import promo_dialog
from .delete_promo_dialog import delete_promo_dialog
dialogs_router = Router()

dialogs_router.include_routers(admin_dialog, premium_dialog, ban_dialog, unban_dialog, season_delete_dialog,
                               change_nickname_dialog, mailing_dialog, promo_dialog, delete_promo_dialog)
dialogs_router.message.middleware(AdminMiddleware())
dialogs_router.callback_query.middleware(AdminMiddleware())


@dialogs_router.message(Command("ids"))
async def get_ids(message: types.Message):
    groups = await get_all_groups()
    users = await get_all_users()

    group_ids = "\n".join(str(group.group_id) for group in groups)
    user_ids = "\n".join(str(user.telegram_id) for user in users)
    print(user_ids)
    await message.answer_document(types.BufferedInputFile(io.BytesIO(group_ids.encode()).getbuffer(), "groups.txt"))
    await message.answer_document(types.BufferedInputFile(io.BytesIO(user_ids.encode()).getbuffer(), "users.txt"))

