from aiogram import Router

from .add_admin_dialog import add_admin_dialog

add_admin_dialogs = Router()
add_admin_dialogs.include_routers(add_admin_dialog)
