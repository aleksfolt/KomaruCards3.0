from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from database.group import create_group, get_group, update_last_activity_group
from database.user import create_user, get_user, update_last_activity


class RegisterMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        event: Message = event
        user = await get_user(event.from_user.id)
        if user is None:
            in_pm = True if event.chat.type == "private" else False
            await create_user(event.from_user.id, event.from_user.username, in_pm)
        else:
            if event.chat.type == "private":
                await update_last_activity(event.from_user.id)
        if event.chat.type in ["group", "supergroup"]:
            if await get_group(event.chat.id) is None:
                await create_group(event.chat.id, event.chat.title)
            else:
                await update_last_activity_group(event.chat.id)

        return await handler(event, data)
