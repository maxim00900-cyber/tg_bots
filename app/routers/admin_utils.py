from app.config import get_settings
import app.database.requests as rq


def is_admin(user_id: int | None) -> bool:
    if user_id is None:
        return False
    settings = get_settings()
    return user_id in settings.admin_chat_ids


async def is_staff(user_id: int | None) -> bool:
    if user_id is None:
        return False
    if is_admin(user_id):
        return True
    return await rq.is_user_admin(user_id)


async def get_staff_ids() -> list[int]:
    settings = get_settings()
    admin_ids = set(settings.admin_chat_ids)
    admin_ids.update(await rq.get_admin_ids())
    return sorted(admin_ids)
