import yaml
from pydantic import BaseModel, StrictStr, StrictInt
from typing import List


class Telegram(BaseModel):
    token: StrictStr


class Flyer(BaseModel):
    token: StrictStr


class CryptoPay(BaseModel):
    token: StrictStr


class Database(BaseModel):
    driver: StrictStr
    host: StrictStr
    port: StrictInt
    database: StrictStr
    user: StrictStr
    password: StrictStr


class Bot(BaseModel):
    telegram: Telegram
    cryptoPay: CryptoPay
    flyer: Flyer
    admins: List[StrictInt]


class App(BaseModel):
    bot: Bot
    database: Database


def _load_yaml_config():
    try:
        return yaml.safe_load(open("config.yaml"))

    except FileNotFoundError as error:
        message = "Error: yaml config file not found."
        raise FileNotFoundError(error, message) from error


app = App(**_load_yaml_config())
settings = app.bot
database = app.database
