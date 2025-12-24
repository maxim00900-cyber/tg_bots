from app.config import get_settings
import app.database.requests as rq


def is_admin(user_id: int | None) -> bool:
    if user_id is None:
        return False
    settings = get_settings()
    return user_id in settings.admin_chat_ids


async def get_user_role(user_id: int | None) -> str:
    if user_id is None:
        return rq.ROLE_USER
    if is_admin(user_id):
        return rq.ROLE_ADMIN
    return await rq.get_role(user_id)


async def is_moderator(user_id: int | None) -> bool:
    return (await get_user_role(user_id)) == rq.ROLE_MODERATOR


async def is_staff(user_id: int | None) -> bool:
    role = await get_user_role(user_id)
    return role in (rq.ROLE_ADMIN, rq.ROLE_MODERATOR)


async def get_staff_ids() -> list[int]:
    return await rq.get_staff_ids()
