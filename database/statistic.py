import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Group, User
from loader import engine


async def get_users_count_created_by_date(data: datetime.date) -> int:
    async with AsyncSession(engine) as session:
        return (await session.execute(select(func.count(User.id))
                                      .where(User.created_at == data))
                ).scalar_one()


async def get_users_count_last_active_by_date(data: datetime.date) -> int:
    async with AsyncSession(engine) as session:
        return (await session.execute(select(func.count(User.id))
                                      .where(User.last_activity == data))
                ).scalar_one()


async def get_groups_count_created_by_date(data: datetime.date) -> int:
    async with AsyncSession(engine) as session:
        return (await session.execute(select(func.count(Group.id))
                                      .where(Group.added_at == data and Group.in_group == True))
                ).scalar_one()


async def get_groups_count_last_active_by_date(data: datetime.date) -> int:
    async with AsyncSession(engine) as session:
        return (await session.execute(select(func.count(Group.id))
                                      .where(Group.last_activity == data))
                ).scalar_one()
