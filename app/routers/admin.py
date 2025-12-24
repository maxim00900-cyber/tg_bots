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
    if user.is_banned:
        await message.answer(texts.ADMIN_BANNED_USER_TEXT)
        return

    user = await rq.approve_by_staff(user_id, message.from_user.id, "rub")
    if not user:
        await message.answer(texts.ADMIN_ALREADY_HANDLED_TEXT)
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
    if user.is_banned:
        await message.answer(texts.ADMIN_BANNED_USER_TEXT)
        return

    user = await rq.deny_by_staff(user_id, message.from_user.id, paid_method="rub")
    if not user:
        await message.answer(texts.ADMIN_ALREADY_HANDLED_TEXT)
        return

    await _notify_user(message, user_id, texts.USER_DENIED_TEXT, reply_markup=kb.user_kb(False))
    await message.answer(texts.DENY_SUCCESS_TEXT)


@router.message(Command(commands="ban"))
async def ban_user(message: Message) -> None:
    if not await is_staff(message.from_user.id if message.from_user else None):
        await message.answer(texts.ADMIN_ONLY_TEXT)
        return

    user_id = _parse_target_user_id(message)
    if user_id is None:
        await message.answer(texts.BAN_USAGE_TEXT)
        return

    await rq.ban_user(user_id)
    await message.answer(texts.BAN_SUCCESS_TEXT)
    await _notify_user(message, user_id, texts.BANNED_TEXT)


@router.message(Command(commands="unban"))
async def unban_user(message: Message) -> None:
    if not await is_staff(message.from_user.id if message.from_user else None):
        await message.answer(texts.ADMIN_ONLY_TEXT)
        return

    user_id = _parse_target_user_id(message)
    if user_id is None:
        await message.answer(texts.UNBAN_USAGE_TEXT)
        return

    user = await rq.unban_user(user_id)
    if not user:
        await message.answer(texts.USER_NOT_FOUND_TEXT)
        return

    await message.answer(texts.UNBAN_SUCCESS_TEXT)


@router.message(Command(commands="admin_add"))
async def add_admin(message: Message) -> None:
    if not is_admin(message.from_user.id if message.from_user else None):
        await message.answer(texts.ADMIN_ONLY_TEXT)
        return

    user_id = _parse_target_user_id(message)
    if user_id is None:
        await message.answer(texts.ADMIN_ADD_USAGE_TEXT)
        return

    await rq.add_admin(user_id)
    await message.answer(texts.ADMIN_ADDED_TEXT)


@router.message(Command(commands="admin_remove"))
async def remove_admin(message: Message) -> None:
    if not is_admin(message.from_user.id if message.from_user else None):
        await message.answer(texts.ADMIN_ONLY_TEXT)
        return

    user_id = _parse_target_user_id(message)
    if user_id is None:
        await message.answer(texts.ADMIN_REMOVE_USAGE_TEXT)
        return

    user = await rq.remove_admin(user_id)
    if not user:
        await message.answer(texts.USER_NOT_FOUND_TEXT)
        return

    await message.answer(texts.ADMIN_REMOVED_TEXT)


@router.message(F.text == texts.BUTTON_ADMIN_APPROVE_HELP)
async def approve_help(message: Message) -> None:
    if not await is_staff(message.from_user.id if message.from_user else None):
        await message.answer(texts.ADMIN_ONLY_TEXT)
        return

    await message.answer(texts.APPROVE_USAGE_TEXT)


@router.message(F.text == texts.BUTTON_ADMIN_DENY_HELP)
async def deny_help(message: Message) -> None:
    if not await is_staff(message.from_user.id if message.from_user else None):
        await message.answer(texts.ADMIN_ONLY_TEXT)
        return

    await message.answer(texts.DENY_USAGE_TEXT)


@router.message(F.text == texts.BUTTON_ADMIN_BAN_HELP)
async def ban_help(message: Message) -> None:
    if not await is_staff(message.from_user.id if message.from_user else None):
        await message.answer(texts.ADMIN_ONLY_TEXT)
        return

    await message.answer(texts.BAN_USAGE_TEXT)


@router.message(F.text == texts.BUTTON_ADMIN_UNBAN_HELP)
async def unban_help(message: Message) -> None:
    if not await is_staff(message.from_user.id if message.from_user else None):
        await message.answer(texts.ADMIN_ONLY_TEXT)
        return

    await message.answer(texts.UNBAN_USAGE_TEXT)


@router.message(F.text == texts.BUTTON_ADMIN_ADD_HELP)
async def admin_add_help(message: Message) -> None:
    if not is_admin(message.from_user.id if message.from_user else None):
        await message.answer(texts.ADMIN_ONLY_TEXT)
        return

    await message.answer(texts.ADMIN_ADD_USAGE_TEXT)


@router.message(F.text == texts.BUTTON_ADMIN_REMOVE_HELP)
async def admin_remove_help(message: Message) -> None:
    if not is_admin(message.from_user.id if message.from_user else None):
        await message.answer(texts.ADMIN_ONLY_TEXT)
        return

    await message.answer(texts.ADMIN_REMOVE_USAGE_TEXT)


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
    if user.is_banned:
        if callback.message:
            await callback.message.answer(texts.ADMIN_BANNED_USER_TEXT)
        await _mark_admin_message(callback, texts.ADMIN_BANNED_USER_TEXT)
        return

    user = await rq.approve_by_staff(user_id, callback.from_user.id, "rub")
    if not user:
        if callback.message:
            await callback.message.answer(texts.ADMIN_ALREADY_HANDLED_TEXT)
        await _mark_admin_message(callback, texts.ADMIN_ALREADY_HANDLED_TEXT)
        return

    await _notify_user(
        callback.message,
        user_id,
        texts.USER_APPROVED_TEXT,
        reply_markup=kb.user_kb(True),
    )
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
    if user.is_banned:
        if callback.message:
            await callback.message.answer(texts.ADMIN_BANNED_USER_TEXT)
        await _mark_admin_message(callback, texts.ADMIN_BANNED_USER_TEXT)
        return

    user = await rq.deny_by_staff(user_id, callback.from_user.id, paid_method="rub")
    if not user:
        if callback.message:
            await callback.message.answer(texts.ADMIN_ALREADY_HANDLED_TEXT)
        await _mark_admin_message(callback, texts.ADMIN_ALREADY_HANDLED_TEXT)
        return

    await _notify_user(
        callback.message,
        user_id,
        texts.USER_DENIED_TEXT,
        reply_markup=kb.user_kb(False),
    )
    await _mark_admin_message(callback, "❌ " + texts.DENY_SUCCESS_TEXT)


@router.callback_query(F.data.startswith("admin_ban:"))
async def ban_callback(callback: CallbackQuery) -> None:
    await callback.answer()
    if not await is_staff(callback.from_user.id if callback.from_user else None):
        if callback.message:
            await callback.message.answer(texts.ADMIN_ONLY_TEXT)
        return

    user_id = _parse_callback_user_id(callback, "admin_ban:")
    if user_id is None:
        if callback.message:
            await callback.message.answer(texts.BAN_USAGE_TEXT)
        return

    await rq.ban_user(user_id)
    await _notify_user(callback.message, user_id, texts.BANNED_TEXT)
    await _mark_admin_message(callback, "🚫 " + texts.BAN_SUCCESS_TEXT)
