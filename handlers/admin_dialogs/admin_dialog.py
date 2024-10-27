from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Back, Row, Start
from aiogram_dialog.widgets.text import Const, Format
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Group, User
from loader import engine
from .admin_states import AdminSG, BanSG, ChangeUsernameSG, DeletePromoSG, DelSeasonSG, MailingSG, PremiumSG, UnBanSG, \
    CreatePromoSG


async def message_to_mailing_handler(
        message: Message,
        message_input: Message,
        manager: DialogManager,
): await manager.switch_to(AdminSG)


async def get_statistics(dialog_manager: DialogManager, **kwargs):
    async with AsyncSession(engine) as session:
        total_users = await session.scalar(select(func.count()).select_from(User))
        premium_users = await session.scalar(
            select(func.count()).select_from(User).where(User.premium_expire.is_not(None))
        )
        total_groups = await session.scalar(select(func.count()).select_from(Group))

    return {
        "total_users": total_users,
        "premium_users": premium_users,
        "total_groups": total_groups
    }


admin_dialog = Dialog(
    Window(
        Const("Привет админ!"),
        Row(
            Start(Const("Рассылка"), id="mailing", state=MailingSG.choose_type),
            Start(Const("Статистика"), id="statistics", state=AdminSG.statistics),
        ),
        # Row(
        #     Start(Const("Премиум"), id="premium", state=PremiumSG.premium_get_id),
        #     Start(Const("Сменить ник"), id="__change_username__", state=ChangeUsernameSG.get_id),
        # ),
        # Row(
        #     Start(Const("Бан"), id="ban", state=BanSG.get_id),
        #     Start(Const("Разбан"), id="unban", state=UnBanSG.get_id),
        # ),
        # Row(
        #     Start(Const("Создать промо"), id="create_promo", state=CreatePromoSG.get_name),
        #     Start(Const("Удалить промо"), id="delete_promo", state=DeletePromoSG.get_name),
        # ),
        Start(Const("Сбросить сезон"), id="reset_season", state=DelSeasonSG.accept_del),

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
