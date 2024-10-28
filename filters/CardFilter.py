from aiogram.filters import BaseFilter
from aiogram.types import Message


class CardFilter(BaseFilter):

    async def __call__(self, message: Message) -> bool:
        if message.text is not None and message.text.casefold() in \
                ["комару".casefold(), "карту, сэр".casefold(), "карту сэр".casefold(), "карту, сэр.".casefold(),
                 "камар".casefold(), "камару".casefold(), "получить карту".casefold()]:
            return True
        else:
            return False
