import time
from aiogram.filters import BaseFilter
from aiogram.types import Message

class RateLimitFilter(BaseFilter):
    def __init__(self, limit: float):
        self.limit = limit
        self.last_request_time = {}

    async def __call__(self, message: Message) -> bool:
        user_id = message.from_user.id
        current_time = time.time()

        if user_id in self.last_request_time:
            if (current_time - self.last_request_time[user_id]) < self.limit:
                return False

        self.last_request_time[user_id] = current_time
        return True
