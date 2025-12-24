import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from app import keyboards as kb
from app import texts
from app.config import get_settings
import app.database.requests as rq

router = Router()


def _get_admin_chat_id() -> int | None:
    settings = get_settings()
    if settings.admin_chat_id is None:
        logging.error("ADMIN_CHAT_ID is not configured")
    return settings.admin_chat_id


def _get_rub_pay_url() -> str | None:
    settings = get_settings()
    if not settings.rub_pay_url:
        logging.error("RUB_PAY_URL is not configured")
    return settings.rub_pay_url


async def _safe_answer(callback: CallbackQuery, text: str, reply_markup=None) -> None:
    if callback.message is None:
        return
    await callback.message.answer(text, reply_markup=reply_markup)


@router.callback_query(F.data == "pay_rub")
async def callback_rub(callback: CallbackQuery) -> None:
    await callback.answer()
    user = await rq.get_user(callback.from_user.id)
    if user and user.is_paid:
        await _safe_answer(callback, texts.ACCESS_TEXT)
        return

    rub_pay_url = _get_rub_pay_url()
    if not rub_pay_url:
        await _safe_answer(callback, texts.PAYMENT_RUB_DISABLED_TEXT)
        return

    await rq.set_rub_pending(callback.from_user.id)
    await _safe_answer(
        callback,
        texts.PAY_RUB_QR_TEXT,
        reply_markup=kb.rub_payment_kb(rub_pay_url),
    )


@router.callback_query(F.data == "rub_receipt_sent")
async def callback_rub_receipt_sent(callback: CallbackQuery) -> None:
    await callback.answer()
    admin_chat_id = _get_admin_chat_id()
    if not admin_chat_id:
        await _safe_answer(callback, texts.PAYMENT_RUB_DISABLED_TEXT)
        return

    user = callback.from_user
    name = " ".join(part for part in [user.first_name, user.last_name] if part)
    username = f"@{user.username}" if user.username else "без username"
    await callback.bot.send_message(
        admin_chat_id,
        (
            "Новая оплата в рублях.\n"
            f"Пользователь: {name} ({username})\n"
            f"ID: {user.id}\n"
            "Пользователь нажал «Я отправил чек»."
        ),
    )
    await _safe_answer(callback, texts.RECEIPT_SENT_TEXT)


@router.message(F.photo | F.document)
async def receipt_message(message: Message) -> None:
    user = await rq.get_user(message.from_user.id)
    if not user or user.is_paid or user.paid_method != "rub":
        return

    admin_chat_id = _get_admin_chat_id()
    if not admin_chat_id:
        await message.answer(texts.PAYMENT_RUB_DISABLED_TEXT)
        return

    await message.copy_to(admin_chat_id)
    await message.answer(texts.RECEIPT_RECEIVED_TEXT)
