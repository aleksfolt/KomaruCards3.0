from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from database.group import create_group, get_group
from database.user import create_user, get_user


class RegisterMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        event: Message = event
        if await get_user(event.from_user.id) is None:
            in_pm = True if event.chat.type == "private" else False
            await create_user(event.from_user.id, event.from_user.username, in_pm)
        if event.chat.type in ["group", "supergroup"] and await get_group(event.chat.id) is None:
            await create_group(event.chat.id, event.chat.title)

        return await handler(event, data)
