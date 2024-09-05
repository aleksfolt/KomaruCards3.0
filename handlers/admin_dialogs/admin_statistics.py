from aiogram_dialog import DialogManager
from database.user import get_all_users, get_premium_users
from database.group import get_all_groups


async def get_statistics(dialog_manager: DialogManager, **kwargs):
    total_users = len(await get_all_users())
    premium_users = len(await get_premium_users())
    total_groups = len(await get_all_groups())

    return {
        "total_users": total_users,
        "premium_users": premium_users,
        "total_groups": total_groups
    }
