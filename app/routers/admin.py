import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from app import keyboards as kb
from app import texts
import app.database.requests as rq
from app.database.models import User
from app.routers.admin_utils import is_admin, is_staff

router = Router()


def _format_payment_status(status: str | None) -> str:
    mapping = {
        "pending": "ожидает оплаты",
        "receipt_sent": "чек отправлен",
        "paid": "оплачено",
        "failed": "неуспешно",
        "expired": "истек",
    }
    return mapping.get(status or "", "-")


async def _get_pending_user(user_id: int) -> tuple[User | None, bool]:
    user = await rq.get_user(user_id)
    if not user:
        return None, False
    if user.payment_status not in ("pending", "receipt_sent") or user.decision_at is not None:
        return user, False
    return user, True


def _parse_target_user_id(message: Message) -> int | None:
    if not message.text:
        return None
    parts = message.text.split(maxsplit=1)
    if len(parts) != 2:
        return None
    try:
        return int(parts[1])
    except ValueError:
        return None


def _parse_callback_user_id(callback: CallbackQuery, prefix: str) -> int | None:
    if not callback.data or not callback.data.startswith(prefix):
        return None
    raw = callback.data.split(":", 1)[1]
    try:
        return int(raw)
    except ValueError:
        return None


def _parse_callback_offset(callback: CallbackQuery, prefix: str) -> int | None:
    if not callback.data or not callback.data.startswith(prefix):
        return None
    raw = callback.data.split(":", 1)[1]
    try:
        value = int(raw)
    except ValueError:
        return None
    return value if value >= 0 else None


async def _notify_user(
    message: Message | None,
    user_id: int,
    text: str,
    reply_markup=None,
) -> None:
    if message is None:
        return
    try:
        await message.bot.send_message(user_id, text, reply_markup=reply_markup)
    except Exception as exc:
        logging.exception("Failed to notify user %s: %s", user_id, exc)


async def _mark_admin_message(callback: CallbackQuery, status_text: str) -> None:
    if not callback.message:
        return
    try:
        await callback.message.edit_text(status_text, reply_markup=None)
    except Exception as exc:
        logging.exception("Failed to update admin message: %s", exc)


async def _send_queue(message: Message, offset: int) -> None:
    limit = 10
    total = await rq.count_pending_users()
    if total == 0:
        await message.answer(texts.ADMIN_QUEUE_EMPTY_TEXT)
        return

    pending = await rq.get_pending_users_page(limit=limit, offset=offset)
    if not pending:
        await message.answer(texts.ADMIN_QUEUE_EMPTY_TEXT)
        return

    header = (
        f"{texts.ADMIN_QUEUE_HEADER_TEXT} "
        f"{offset + 1}-{min(offset + limit, total)} из {total}"
    )
    nav = kb.admin_queue_nav_kb(offset, limit, total)
    await message.answer(header, reply_markup=nav)
    for user in pending:
        info = (
            f"User ID: {user.user_id}\n"
            f"Method: {user.paid_method or '-'}\n"
            f"Status: {_format_payment_status(user.payment_status)}\n"
            f"Invoice: {user.invoice_id or '-'}"
        )
        await message.answer(info, reply_markup=kb.admin_action_kb(user.user_id))


@router.message(Command(commands="approve"))
async def approve_payment(message: Message) -> None:
    if not await is_staff(message.from_user.id if message.from_user else None):
        await message.answer(texts.ADMIN_ONLY_TEXT)
        return

    user_id = _parse_target_user_id(message)
    if user_id is None:
        await message.answer(texts.APPROVE_USAGE_TEXT)
        return

    user, is_pending = await _get_pending_user(user_id)
    if not user:
        await message.answer(texts.USER_NOT_FOUND_TEXT)
        return
    if not is_pending:
        await message.answer(texts.ADMIN_ALREADY_HANDLED_TEXT)
        return

    user = await rq.approve_by_staff(user_id, message.from_user.id, "rub")
    if not user:
        await message.answer(texts.USER_NOT_FOUND_TEXT)
        return

    await _notify_user(message, user_id, texts.USER_APPROVED_TEXT, reply_markup=kb.user_kb(True))
    await message.answer(texts.APPROVE_SUCCESS_TEXT)


@router.message(Command(commands="deny"))
async def deny_payment(message: Message) -> None:
    if not await is_staff(message.from_user.id if message.from_user else None):
        await message.answer(texts.ADMIN_ONLY_TEXT)
        return

    user_id = _parse_target_user_id(message)
    if user_id is None:
        await message.answer(texts.DENY_USAGE_TEXT)
        return

    user, is_pending = await _get_pending_user(user_id)
    if not user:
        await message.answer(texts.USER_NOT_FOUND_TEXT)
        return
    if not is_pending:
        await message.answer(texts.ADMIN_ALREADY_HANDLED_TEXT)
        return

    user = await rq.deny_by_staff(user_id, message.from_user.id, paid_method="rub")
    if not user:
        await message.answer(texts.USER_NOT_FOUND_TEXT)
        return

    await _notify_user(message, user_id, texts.USER_DENIED_TEXT, reply_markup=kb.user_kb(False))
    await message.answer(texts.DENY_SUCCESS_TEXT)


@router.message(Command(commands="queue"))
async def pending_queue(message: Message) -> None:
    if not await is_staff(message.from_user.id if message.from_user else None):
        await message.answer(texts.ADMIN_ONLY_TEXT)
        return

    await _send_queue(message, offset=0)


@router.message(F.text == texts.BUTTON_QUEUE)
async def pending_queue_button(message: Message) -> None:
    if not await is_staff(message.from_user.id if message.from_user else None):
        await message.answer(texts.ADMIN_ONLY_TEXT)
        return

    await _send_queue(message, offset=0)


@router.message(F.text == texts.BUTTON_MOD_ADD)
async def mod_add_button(message: Message) -> None:
    if not is_admin(message.from_user.id if message.from_user else None):
        await message.answer(texts.ADMIN_ONLY_TEXT)
        return

    await message.answer(texts.MOD_ADD_USAGE_TEXT)


@router.message(F.text == texts.BUTTON_MOD_REMOVE)
async def mod_remove_button(message: Message) -> None:
    if not is_admin(message.from_user.id if message.from_user else None):
        await message.answer(texts.ADMIN_ONLY_TEXT)
        return

    await message.answer(texts.MOD_REMOVE_USAGE_TEXT)


@router.callback_query(F.data.startswith("admin_queue:"))
async def queue_page_callback(callback: CallbackQuery) -> None:
    await callback.answer()
    if not await is_staff(callback.from_user.id if callback.from_user else None):
        if callback.message:
            await callback.message.answer(texts.ADMIN_ONLY_TEXT)
        return

    offset = _parse_callback_offset(callback, "admin_queue:")
    if offset is None:
        if callback.message:
            await callback.message.answer(texts.ADMIN_QUEUE_EMPTY_TEXT)
        return

    if callback.message:
        await _send_queue(callback.message, offset=offset)


@router.callback_query(F.data.startswith("admin_approve:"))
async def approve_callback(callback: CallbackQuery) -> None:
    await callback.answer()
    if not await is_staff(callback.from_user.id if callback.from_user else None):
        if callback.message:
            await callback.message.answer(texts.ADMIN_ONLY_TEXT)
        return

    user_id = _parse_callback_user_id(callback, "admin_approve:")
    if user_id is None:
        if callback.message:
            await callback.message.answer(texts.APPROVE_USAGE_TEXT)
        return

    user, is_pending = await _get_pending_user(user_id)
    if not user:
        if callback.message:
            await callback.message.answer(texts.USER_NOT_FOUND_TEXT)
        return
    if not is_pending:
        if callback.message:
            await callback.message.answer(texts.ADMIN_ALREADY_HANDLED_TEXT)
        await _mark_admin_message(callback, texts.ADMIN_ALREADY_HANDLED_TEXT)
        return

    user = await rq.approve_by_staff(user_id, callback.from_user.id, "rub")

    await _notify_user(
        callback.message,
        user_id,
        texts.USER_APPROVED_TEXT,
        reply_markup=kb.user_kb(True),
    )
    if callback.message:
        await callback.message.answer(texts.APPROVE_SUCCESS_TEXT)
    await _mark_admin_message(callback, "✅ " + texts.APPROVE_SUCCESS_TEXT)


@router.callback_query(F.data.startswith("admin_deny:"))
async def deny_callback(callback: CallbackQuery) -> None:
    await callback.answer()
    if not await is_staff(callback.from_user.id if callback.from_user else None):
        if callback.message:
            await callback.message.answer(texts.ADMIN_ONLY_TEXT)
        return

    user_id = _parse_callback_user_id(callback, "admin_deny:")
    if user_id is None:
        if callback.message:
            await callback.message.answer(texts.DENY_USAGE_TEXT)
        return

    user, is_pending = await _get_pending_user(user_id)
    if not user:
        if callback.message:
            await callback.message.answer(texts.USER_NOT_FOUND_TEXT)
        return
    if not is_pending:
        if callback.message:
            await callback.message.answer(texts.ADMIN_ALREADY_HANDLED_TEXT)
        await _mark_admin_message(callback, texts.ADMIN_ALREADY_HANDLED_TEXT)
        return

    user = await rq.deny_by_staff(user_id, callback.from_user.id, paid_method="rub")

    await _notify_user(
        callback.message,
        user_id,
        texts.USER_DENIED_TEXT,
        reply_markup=kb.user_kb(False),
    )
    if callback.message:
        await callback.message.answer(texts.DENY_SUCCESS_TEXT)
    await _mark_admin_message(callback, "❌ " + texts.DENY_SUCCESS_TEXT)


@router.message(Command(commands="mod_add"))
async def add_moderator(message: Message) -> None:
    if not is_admin(message.from_user.id if message.from_user else None):
        await message.answer(texts.ADMIN_ONLY_TEXT)
        return

    user_id = _parse_target_user_id(message)
    if user_id is None:
        await message.answer(texts.MOD_ADD_USAGE_TEXT)
        return

    await rq.set_role(user_id, rq.ROLE_MODERATOR)
    await message.answer(texts.MOD_ADDED_TEXT)


@router.message(Command(commands="mod_remove"))
async def remove_moderator(message: Message) -> None:
    if not is_admin(message.from_user.id if message.from_user else None):
        await message.answer(texts.ADMIN_ONLY_TEXT)
        return

    user_id = _parse_target_user_id(message)
    if user_id is None:
        await message.answer(texts.MOD_REMOVE_USAGE_TEXT)
        return

    await rq.set_role(user_id, rq.ROLE_USER)
    await message.answer(texts.MOD_REMOVED_TEXT)


@router.message(Command(commands="mods"))
async def list_moderators(message: Message) -> None:
    if not is_admin(message.from_user.id if message.from_user else None):
        await message.answer(texts.ADMIN_ONLY_TEXT)
        return

    moderators = await rq.get_users_by_roles([rq.ROLE_MODERATOR])
    if not moderators:
        await message.answer(texts.MOD_LIST_EMPTY_TEXT)
        return

    lines = "\n".join(str(user.user_id) for user in moderators)
    await message.answer(f"{texts.MOD_LIST_HEADER_TEXT}\n{lines}")
