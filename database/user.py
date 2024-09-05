import json
from datetime import date, datetime, timedelta
from typing import Dict

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count, func

from database.models import User
from loader import engine

from datetime import datetime, timedelta


async def create_user(telegram_id: int, username: str):
    async with AsyncSession(engine) as session:
        if username:
            user = User(telegram_id=telegram_id, nickname=username)
        else:
            user = User(telegram_id=telegram_id)
        session.add(user)
        await session.commit()
        user = (await session.execute(select(User).where(User.telegram_id == telegram_id))).scalar_one()
        return user


async def get_user(telegram_id: int):
    async with AsyncSession(engine) as session:
        user: User = (await session.execute(select(User).where(User.telegram_id == telegram_id))).scalar_one_or_none()
        return user


async def set_love_card(telegram_id: int, love_card_id: int):
    async with AsyncSession(engine) as session:
        user: User = (await session.execute(select(User).where(User.telegram_id == telegram_id))).scalar_one_or_none()
        if user is None:
            return False
        user.love_card = love_card_id
        await session.commit()
        return True


async def update_last_get(telegram_id: int):
    async with AsyncSession(engine) as session:
        user: User = (await session.execute(select(User).where(User.telegram_id == telegram_id))).scalar_one_or_none()
        user.last_usage = datetime.now()
        await session.commit()


async def add_points(telegram_id: int, points: int):
    async with AsyncSession(engine) as session:
        user: User = (await session.execute(select(User).where(User.telegram_id == telegram_id))).scalar_one_or_none()
        user.points += points
        user.all_points += points
        await session.commit()


async def add_card(telegram_id: int, card_id: int):
    async with AsyncSession(engine) as session:
        user: User = (await session.execute(select(User).where(User.telegram_id == telegram_id))).scalar_one_or_none()
        user.cards += [card_id]
        user.card_count += 1
        await session.commit()


async def change_username(telegram_id: int, username: str):
    async with AsyncSession(engine) as session:
        user: User = (await session.execute(select(User).where(User.telegram_id == telegram_id))).scalar_one_or_none()
        user.nickname = username
        await session.commit()


async def is_nickname_taken(nickname: str) -> bool:
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(User).where(User.nickname == nickname)
        )
        users = result.scalars().all()
        return len(users) > 0


async def check_premium(premium_expire: datetime):
    return True if premium_expire is not None and premium_expire.date() > datetime.now().date() else False


async def get_premium_users() -> [User]:
    async with AsyncSession(engine) as session:
        users: [User] = (
            await session.execute(
                select(User).where(User.premium_expire.is_not(None)).where(User.premium_expire > datetime.now())
            )
        ).scalars().all()
        return users


async def get_top_users_by_cards():
    async with AsyncSession(engine) as session:
        top_users = (
            await session.execute(
                select(User).order_by(desc(func.cardinality(User.cards))).filter(func.cardinality(User.cards) > 0)
                .limit(10)
            )
        ).scalars().all()
        top = []
        i = 1
        for top_user in top_users:
            icon = "💎" if await check_premium(top_user.premium_expire) else ""
            top += [[i, icon, top_user.nickname, len(top_user.cards), top_user.telegram_id]]
            i += 1
        return top

async def get_top_users_by_points():
    async with (AsyncSession(engine) as session):
        top_users = (
            await session.execute(
                select(User).order_by(desc(User.points)).limit(10)
            )
        ).scalars().all()
        top = []
        i = 1
        for top_user in top_users:
            icon = "💎" if await check_premium(top_user.premium_expire) else ""
            top += [[i, icon, top_user.nickname, top_user.points]]
            i += 1
        return top


async def get_top_users_by_all_points():
    async with (AsyncSession(engine) as session):
        top_users = (
            await session.execute(
                select(User).order_by(desc(User.all_points)).limit(10)
            )
        ).scalars().all()
        top = []
        i = 1
        for top_user in top_users:
            icon = "💎" if await check_premium(top_user.premium_expire) else ""
            top += [[i, icon, top_user.nickname, top_user.all_points]]
            i += 1
        return top


async def get_me_on_top(by, telegram_id: int):
    async with AsyncSession(engine) as session:
        position = (await session.execute(
            select(1 + count("*")).where(by > select(by).where(User.telegram_id == telegram_id).scalar_subquery())
        )).scalar_one()
        return position


async def premium_from_datetime(telegram_id: int, end_date: datetime):
    async with AsyncSession(engine) as session:
        user: User = (await session.execute(select(User).where(User.telegram_id == telegram_id))).scalar_one_or_none()
        user.premium_expire = end_date
        await session.commit()


async def add_premium(telegram_id: int, days: timedelta):
    async with AsyncSession(engine) as session:
        user: User = (await session.execute(select(User).where(User.telegram_id == telegram_id))).scalar_one_or_none()

        if user.premium_expire is None or datetime.now() >= user.premium_expire:
            user.premium_expire = datetime.now() + days
        else:
            user.premium_expire = user.premium_expire + days

        await session.commit()


async def clear_season():
    async with AsyncSession(engine) as session:
        users: [User] = (await session.execute(select(User))).scalars().all()
        for user in users:
            user.cards = []
            user.points = 0
            user.last_usage = None
        await session.commit()
        return


async def ban_user(telegram_id: int):
    async with AsyncSession(engine) as session:
        user: User = (await session.execute(select(User).where(User.telegram_id == telegram_id))).scalar_one_or_none()
        user.is_banned = True
        await session.commit()
        return


async def unban_user(telegram_id: int):
    async with AsyncSession(engine) as session:
        user: User = (await session.execute(select(User).where(User.telegram_id == telegram_id))).scalar_one_or_none()
        user.is_banned = False
        await session.commit()
        return


async def get_all_users() -> [User]:
    async with AsyncSession(engine) as session:
        users: Dict[User] = (await session.execute(select(User))).scalars().all()
        return users


async def parse_users(users_file: str, premium_file: str):
    async with AsyncSession(engine) as session:
        with open(users_file, 'r', encoding="utf8") as f:
            with open(premium_file, 'r', encoding="utf8") as p:
                user_date: Dict = json.load(f)
                premium_data: Dict = json.load(p)
                for bot_user in user_date:
                    if bot_user == "6184515646":
                        continue
                    user: Dict = user_date[bot_user]
                    nickname = user['nickname']
                    if user.get('card_count'):
                        card_count = user['card_count']
                    else:
                        card_count = 0
                        print(">>>")
                    if user.get('all_points'):
                        all_points = user['all_points']
                    else:
                        all_points = 0
                        print("<<<")
                    if premium_data.get(bot_user):
                        premium_expire = datetime.strptime(premium_data[bot_user], '%Y-%m-%d').date()
                    else:
                        premium_expire = None
                    botUser = User(telegram_id=int(bot_user), nickname=nickname, card_count=card_count,
                                   all_points=all_points, premium_expire=premium_expire)
                    session.add(botUser)
        await session.commit()
