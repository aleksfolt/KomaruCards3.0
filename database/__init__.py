from database.group import get_all_groups_ids
from database.models import Base
from database.user import get_all_users_ids
from loader import engine


async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


