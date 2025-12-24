from aiogram.types import CallbackQuery, Message

import app.database.requests as rq
from app.routers.admin_utils import is_admin, is_staff


def get_message_user_id(message: Message) -> int | None:
    return message.from_user.id if message.from_user else None


def get_callback_user_id(callback: CallbackQuery) -> int | None:
    return callback.from_user.id if callback.from_user else None


def is_owner_user(user_id: int | None) -> bool:
    if user_id is None:
        return False
    return is_admin(user_id)


async def is_staff_user(user_id: int | None) -> bool:
    if user_id is None:
        return False
    return await is_staff(user_id)


async def is_banned_user(user_id: int | None) -> bool:
    if user_id is None:
        return False
    return await rq.is_user_banned(user_id)


async def is_paid_user(user_id: int | None) -> bool:
    if user_id is None:
        return False
    user = await rq.get_user(user_id)
    return bool(user and (user.payment_status == "paid" or user.is_paid))
