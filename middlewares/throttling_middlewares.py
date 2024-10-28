from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message
from cachetools import TTLCache


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self):
        self.cache = TTLCache(maxsize=10_000, ttl=1)

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]):
        if event.from_user.id in self.cache:
            return
        else:
            self.cache[event.chat.id] = None
        return await handler(event, data)
