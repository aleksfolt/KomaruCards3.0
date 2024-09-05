from aiogram_dialog import DialogManager
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User, Group
from loader import engine


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
