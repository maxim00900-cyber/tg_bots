from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from app import keyboards as kb
from app import texts
from app.services.payments import (
    RubPaymentStatus,
    RubReceiptSentStatus,
    RubReceiptUploadStatus,
    build_rub_receipt_sent,
    check_rub_receipt_upload,
    start_rub_payment,
)
from app.routers.admin_utils import is_admin

router = Router()


async def _safe_answer(callback: CallbackQuery, text: str, reply_markup=None) -> None:
    if callback.message is None:
        return
    await callback.message.answer(text, reply_markup=reply_markup)


@router.callback_query(F.data == "pay_rub")
async def callback_rub(callback: CallbackQuery) -> None:
    await callback.answer()
    result = await start_rub_payment(callback.from_user.id)
    if result.status == RubPaymentStatus.ALREADY_PAID:
        await _safe_answer(callback, texts.ACCESS_TEXT)
        return

    if result.status == RubPaymentStatus.DISABLED or not result.pay_url:
        await _safe_answer(callback, texts.PAYMENT_RUB_DISABLED_TEXT)
        return

    await _safe_answer(
        callback,
        texts.PAY_RUB_QR_TEXT,
        reply_markup=kb.rub_payment_kb(result.pay_url),
    )


@router.callback_query(F.data == "rub_receipt_sent")
async def callback_rub_receipt_sent(callback: CallbackQuery) -> None:
    await callback.answer()
    result = build_rub_receipt_sent(
        callback.from_user.id,
        callback.from_user.first_name,
        callback.from_user.last_name,
        callback.from_user.username,
    )
    if (
        result.status == RubReceiptSentStatus.DISABLED
        or not result.admin_chat_ids
        or not any(is_admin(admin_id) for admin_id in result.admin_chat_ids)
    ):
        await _safe_answer(callback, texts.PAYMENT_RUB_DISABLED_TEXT)
        return

    for admin_id in result.admin_chat_ids:
        if is_admin(admin_id):
            await callback.bot.send_message(
                admin_id,
                result.message or "",
                reply_markup=kb.admin_action_kb(callback.from_user.id),
            )
    await _safe_answer(callback, texts.RECEIPT_SENT_TEXT)


@router.message(F.photo | F.document)
async def receipt_message(message: Message) -> None:
    result = await check_rub_receipt_upload(message.from_user.id)
    if result.status == RubReceiptUploadStatus.IGNORED:
        return

    if (
        result.status == RubReceiptUploadStatus.DISABLED
        or not result.admin_chat_ids
        or not any(is_admin(admin_id) for admin_id in result.admin_chat_ids)
    ):
        await message.answer(texts.PAYMENT_RUB_DISABLED_TEXT)
        return

    for admin_id in result.admin_chat_ids:
        if is_admin(admin_id):
            await message.copy_to(admin_id)
    await message.answer(texts.RECEIPT_RECEIVED_TEXT)
