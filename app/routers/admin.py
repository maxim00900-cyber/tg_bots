import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from app import keyboards as kb
from app import texts
import app.database.requests as rq
from app.routers.admin_utils import is_admin

router = Router()


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


@router.message(F.text == texts.BUTTON_APPROVE)
async def approve_hint(message: Message) -> None:
    if not is_admin(message.from_user.id if message.from_user else None):
        await message.answer(texts.ADMIN_ONLY_TEXT)
        return
    await message.answer(texts.APPROVE_USAGE_TEXT)


@router.message(F.text == texts.BUTTON_DENY)
async def deny_hint(message: Message) -> None:
    if not is_admin(message.from_user.id if message.from_user else None):
        await message.answer(texts.ADMIN_ONLY_TEXT)
        return
    await message.answer(texts.DENY_USAGE_TEXT)


@router.message(Command(commands="approve"))
async def approve_payment(message: Message) -> None:
    if not is_admin(message.from_user.id if message.from_user else None):
        await message.answer(texts.ADMIN_ONLY_TEXT)
        return

    user_id = _parse_target_user_id(message)
    if user_id is None:
        await message.answer(texts.APPROVE_USAGE_TEXT)
        return

    user = await rq.mark_paid_by_user(user_id, "rub")
    if not user:
        await message.answer(texts.USER_NOT_FOUND_TEXT)
        return

    await _notify_user(message, user_id, texts.USER_APPROVED_TEXT, reply_markup=kb.user_kb(True))
    await message.answer(texts.APPROVE_SUCCESS_TEXT)


@router.message(Command(commands="deny"))
async def deny_payment(message: Message) -> None:
    if not is_admin(message.from_user.id if message.from_user else None):
        await message.answer(texts.ADMIN_ONLY_TEXT)
        return

    user_id = _parse_target_user_id(message)
    if user_id is None:
        await message.answer(texts.DENY_USAGE_TEXT)
        return

    user = await rq.reset_payment(user_id, paid_method="rub")
    if not user:
        await message.answer(texts.USER_NOT_FOUND_TEXT)
        return

    await _notify_user(message, user_id, texts.USER_DENIED_TEXT, reply_markup=kb.user_kb(False))
    await message.answer(texts.DENY_SUCCESS_TEXT)


@router.message(Command(commands="queue"))
async def pending_queue(message: Message) -> None:
    if not is_admin(message.from_user.id if message.from_user else None):
        await message.answer(texts.ADMIN_ONLY_TEXT)
        return

    pending = await rq.get_pending_users(limit=10)
    if not pending:
        await message.answer(texts.ADMIN_QUEUE_EMPTY_TEXT)
        return

    await message.answer(texts.ADMIN_QUEUE_HEADER_TEXT)
    for user in pending:
        info = (
            f"User ID: {user.user_id}\n"
            f"Method: {user.paid_method or '-'}\n"
            f"Status: {user.payment_status or '-'}\n"
            f"Invoice: {user.invoice_id or '-'}"
        )
        await message.answer(info, reply_markup=kb.admin_action_kb(user.user_id))


def _parse_callback_user_id(callback: CallbackQuery, prefix: str) -> int | None:
    if not callback.data or not callback.data.startswith(prefix):
        return None
    raw = callback.data.split(":", 1)[1]
    try:
        return int(raw)
    except ValueError:
        return None


@router.callback_query(F.data.startswith("admin_approve:"))
async def approve_callback(callback: CallbackQuery) -> None:
    await callback.answer()
    if not is_admin(callback.from_user.id if callback.from_user else None):
        if callback.message:
            await callback.message.answer(texts.ADMIN_ONLY_TEXT)
        return

    user_id = _parse_callback_user_id(callback, "admin_approve:")
    if user_id is None:
        if callback.message:
            await callback.message.answer(texts.APPROVE_USAGE_TEXT)
        return

    user = await rq.mark_paid_by_user(user_id, "rub")
    if not user:
        if callback.message:
            await callback.message.answer(texts.USER_NOT_FOUND_TEXT)
        return

    await _notify_user(
        callback.message,
        user_id,
        texts.USER_APPROVED_TEXT,
        reply_markup=kb.user_kb(True),
    )
    if callback.message:
        await callback.message.answer(texts.APPROVE_SUCCESS_TEXT)
    await _mark_admin_message(callback, f"✅ {texts.APPROVE_SUCCESS_TEXT}")


@router.callback_query(F.data.startswith("admin_deny:"))
async def deny_callback(callback: CallbackQuery) -> None:
    await callback.answer()
    if not is_admin(callback.from_user.id if callback.from_user else None):
        if callback.message:
            await callback.message.answer(texts.ADMIN_ONLY_TEXT)
        return

    user_id = _parse_callback_user_id(callback, "admin_deny:")
    if user_id is None:
        if callback.message:
            await callback.message.answer(texts.DENY_USAGE_TEXT)
        return

    user = await rq.reset_payment(user_id, paid_method="rub")
    if not user:
        if callback.message:
            await callback.message.answer(texts.USER_NOT_FOUND_TEXT)
        return

    await _notify_user(
        callback.message,
        user_id,
        texts.USER_DENIED_TEXT,
        reply_markup=kb.user_kb(False),
    )
    if callback.message:
        await callback.message.answer(texts.DENY_SUCCESS_TEXT)
    await _mark_admin_message(callback, f"❌ {texts.DENY_SUCCESS_TEXT}")
