from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from database.user import get_user


class AdminMiddleware(BaseMiddleware):
    async def __call__(self, handler: Callable[[TelegramObject, Dict[str, Any]],
                       Awaitable[Any]], event: TelegramObject, data: Dict[str, Any]) -> Any:
        event: Message = event
        if "user" in data:
            user = data["user"]
        else:
            user = await get_user(event.from_user.id)
        if user.status == "ADMIN":
            return await handler(event, data)
