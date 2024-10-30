import random
import string

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import RefLink
from loader import engine


def generate_random_string(length=14):
    random_string = ''
    random_str_seq = string.ascii_letters + string.digits
    for i in range(0,length):
        if i % length == 0 and i != 0:
            random_string += '-'
        random_string += str(random_str_seq[random.randint(0, len(random_str_seq) - 1)])
    return random_string


async def create_ref_link(for_user_id: int,) -> RefLink:
    ref_link: str = generate_random_string()
    async with AsyncSession(engine, expire_on_commit=False) as session:
        ref_link = RefLink(code=ref_link, for_user_id=for_user_id)
        session.add(ref_link)
        await session.commit()
        return ref_link


async def delete_ref_link(ref_link: str) -> None:
    async with AsyncSession(engine, expire_on_commit=False) as session:
        ref_link = (await session.execute(select(RefLink).where(RefLink.code == ref_link))).scalar_one_or_none()
        if ref_link is None:
            return
        await session.delete(ref_link)
        await session.commit()


async def get_ref_link(ref_link: str) -> RefLink:
    async with AsyncSession(engine, expire_on_commit=False) as session:
        ref_link = (await session.execute(select(RefLink).where(RefLink.code == ref_link))).scalar_one_or_none()
        return ref_link
