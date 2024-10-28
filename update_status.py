import asyncio
import logging

from utils.check_users_and_groups import run_check
logging.info("Updating started!")
asyncio.run(run_check())
logging.info("Updating finished!")