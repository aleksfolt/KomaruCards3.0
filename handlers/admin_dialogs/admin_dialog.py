from aiogram.enums import ContentType
from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Back, Row, Start, SwitchTo
from aiogram_dialog.widgets.text import Const, Format

from .admin_states import AdminSG, PremiumSG, BanSG, UnBanSG, DelSeasonSG, ChangeUsernameSG, MailingSG
from middlewares import AdminMiddleware
from .admin_statistics import get_statistics


async def message_to_mailing_handler(
        message: Message,
        message_input: Message,
        manager: DialogManager,
): await manager.switch_to(AdminSG)


admin_dialog = Dialog(
    Window(
        Const("Привет админ!"),
        Start(Const("Рассылка"), id="mailing", state=MailingSG.choose_type),
        Row(
            Start(Const("Премиум"), id="premium", state=PremiumSG.premium_get_id),
            Start(Const("Сменить ник"), id="__change_username__", state=ChangeUsernameSG.get_id),
        ),
        Row(
            Start(Const("Бан"), id="ban", state=BanSG.get_id),
            Start(Const("Разбан"), id="unban", state=UnBanSG.get_id),
        ),
        Start(Const("Сбросить сезон"), id="reset_season", state=DelSeasonSG.accept_del),
        Start(Const("Статистика"), id="statistics", state=AdminSG.statistics),
        state=AdminSG.menu,
    ),
    Window(
        Format("Общая статистика:\n"
               "Пользователи: {total_users}\n"
               "Премиум пользователи: {premium_users}\n"
               "Группы: {total_groups}"),
        Back(Const('Назад')),
        getter=get_statistics,
        state=AdminSG.statistics
    ),
)



