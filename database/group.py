from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Group
from loader import engine


async def create_group(group_id: int, title: str) -> Group:
    """Creating group"""
    async with AsyncSession(engine) as session:
        group = Group(group_id=group_id, title=title)
        session.add(group)
        await session.commit()
        group = (await session.execute(select(Group).where(Group.group_id == group_id))).scalar_one()
        return group


async def get_group(group_id: int) -> Group:
    """Getting exists group or none"""
    async with AsyncSession(engine) as session:
        group = (await session.execute(select(Group).where(Group.group_id == group_id))).scalar_one_or_none()
        return group


async def get_group_with_bot_count():
    async with (AsyncSession(engine) as session):
        group_count = (await session.execute(
            select(func.count(Group.id))
            .where(Group.in_group == True))
                       ).scalar_one_or_none()
        return group_count


async def get_all_groups_ids() -> [Group]:
    async with AsyncSession(engine) as session:
        groups = (await session.execute(select(Group.group_id))).scalars().all()
        return groups


async def get_all_groups_with_bot_ids() -> [Group]:
    async with AsyncSession(engine) as session:
        groups = (await session.execute(select(Group.group_id).where(Group.in_group == True))).scalars().all()
        return groups


async def in_group_change(group_id: int, status: bool) -> None:
    async with AsyncSession(engine) as session:
        group: Group = (await session.execute(select(Group).where(Group.group_id == group_id))).scalar_one_or_none()
        group.in_group = status
        await session.commit()
