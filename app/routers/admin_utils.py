from app.config import get_settings


def is_admin(user_id: int | None) -> bool:
    if user_id is None:
        return False
    settings = get_settings()
    return user_id in settings.admin_chat_ids
