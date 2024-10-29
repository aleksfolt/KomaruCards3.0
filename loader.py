from aiocryptopay import AioCryptoPay, Networks
from aiogram import Bot
from flyerapi import Flyer
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine
from utils.config import settings, database

admins = settings.admins
bot = Bot(token=settings.telegram.token)

flyer = Flyer(settings.flyer.token)
url = URL.create(
    drivername=database.driver,
    username=database.user,
    password=database.password,
    host=database.host,
    database=database.database,
    port=database.port,
)
engine = create_async_engine(url)
async_session: AsyncSession = async_sessionmaker(engine, expire_on_commit=False)
crypto = AioCryptoPay(settings.cryptoPay.token, network=Networks.MAIN_NET)
