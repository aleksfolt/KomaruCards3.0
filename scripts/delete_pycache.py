import logging
import os
import shutil

import asyncio

from utils.on_startup import setup_logger


def remove_pycache():
    for root, dirs, files in os.walk("."):
        if 'venv' in root or 'venv' == root:
            continue
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            logger.warning(f'Удаление: %s', pycache_path)
            shutil.rmtree(pycache_path)
        for file in files:
            if file.endswith('.py~'):
                pycache_path = os.path.join(root, file)
                logger.warning(f'Удаление: %s', pycache_path)
                os.remove(pycache_path)


if __name__ == "__main__":
    asyncio.run(setup_logger())
    logger = logging.getLogger("bot")
    logger.warning("Удаление мусора начато!")
    remove_pycache()
