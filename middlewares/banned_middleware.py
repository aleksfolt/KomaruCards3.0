from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from database.user import get_user


class BannedMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        if "user" in data:
            user = data["user"]
        else:
            user = await get_user(event.from_user.id)
        if not user.is_banned:
            return await handler(event, data)
