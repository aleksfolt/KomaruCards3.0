import datetime

from .models import Promo
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from loader import engine


async def create_promo(code: str, link: str, action: str, days_add: int | None, channel_id: int,
                       activation_limit: int, expiration_time: datetime.datetime) -> Promo:
    async with AsyncSession(engine) as session:
        promo = Promo(code=code, link=link, action=action, activation_limit=activation_limit,
                      expiration_time=expiration_time, days_add=days_add, channel_id=channel_id)
        session.add(promo)
        await session.commit()
        promo = (await session.execute(select(Promo).where(Promo.code == code))).scalar_one()
        return promo


async def delete_promo(code: str) -> None:
    async with AsyncSession(engine) as session:
        promo = (await session.execute(select(Promo).where(Promo.code == code))).scalar_one()
        await session.delete(promo)
        await session.commit()


async def get_promo(code: str) -> Promo:
    async with AsyncSession(engine) as session:
        promo = (await session.execute(select(Promo).where(Promo.code == code))).scalar_one_or_none()
        return promo


async def add_activation(code: str) -> None:
    async with AsyncSession(engine) as session:
        promo = (await session.execute(select(Promo).where(Promo.code == code))).scalar_one()
        promo.activation_counts += 1
        await session.commit()




