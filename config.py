import json
import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
AIO_TOKEN = os.getenv("AIO_TOKEN")
FLYER_TOKEN = os.getenv("FLYER_TOKEN")
admins = json.loads(os.getenv('ADMINS'))
