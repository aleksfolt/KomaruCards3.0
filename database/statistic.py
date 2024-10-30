import datetime

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Group, User, App
from loader import engine


async def get_users_count_created_by_date(data: datetime.date) -> int:
    async with AsyncSession(engine) as session:
        return (await session.execute(select(func.count(User.id))
                                      .where(and_(User.created_at == data, User.in_pm == True)))
                ).scalar_one()


async def get_users_count_last_active_today() -> int:
    async with AsyncSession(engine) as session:
        return (await session.execute(select(func.count(User.id))
                                      .where(User.last_activity == datetime.datetime.now().date()))
                ).scalar_one()


async def get_groups_count_created_by_date(data: datetime.date) -> int:
    async with AsyncSession(engine) as session:
        return (await session.execute(select(func.count(Group.id))
                                      .where(Group.added_at == data))
                ).scalar_one()


async def get_groups_count_last_active_today() -> int:
    async with AsyncSession(engine) as session:
        return (await session.execute(select(func.count(Group.id))
                                      .where(Group.last_activity == datetime.datetime.now().date()))
                ).scalar_one()


async def update_yesterday_last_activities() -> None:
    async with AsyncSession(engine) as session:
        app: App = (await session.execute(select(App).where(App.id == 1))).scalar_one_or_none()
        app.yesterday_groups_active = await get_groups_count_last_active_today()
        app.yesterday_users_active = await get_users_count_last_active_today()
        await session.commit()


async def get_yesterday_groups_active() -> int | str:
    async with AsyncSession(engine) as session:
        count = (await session.execute(select(
            App.yesterday_groups_active).where(App.id == 1))
                ).scalar_one_or_none()
        if count is None:
            return 'Вернитесь после 23.59'
        return count


async def get_yesterday_users_active() -> int | str:
    async with AsyncSession(engine) as session:
        count = (await session.execute(select(
            App.yesterday_users_active).where(App.id == 1))
                ).scalar_one_or_none()
        if count is None:
            return 'Активность не готова, вернитесь после 23.59'
        return count


async def create_app_if_not_exist() -> None:
    async with AsyncSession(engine) as session:
        app: App = (await session.execute(select(App).where(App.id == 1))).scalar_one_or_none()
        if app is None:
            app = App(id=1, yesterday_users_active=None, yesterday_groups_active=None)
            session.add(app)
            await session.commit()



