
from aiocryptopay import AioCryptoPay, Networks
from aiogram import Bot
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine
import config
from flyerapi import Flyer


bot = Bot(token=config.BOT_TOKEN)

flyer = Flyer(config.FLYER_TOKEN)
url = URL.create(
    drivername="postgresql+asyncpg",
    username="postgres",
    host="localhost",
    database="komaru_cards",
    password="QwerTY",
)
engine = create_async_engine(url)
async_session: AsyncSession = async_sessionmaker(engine, expire_on_commit=False)
crypto = AioCryptoPay(token=config.AIO_TOKEN, network=Networks.MAIN_NET)
