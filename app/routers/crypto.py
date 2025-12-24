from aiogram import F, Router
from aiogram.types import CallbackQuery, ReplyKeyboardRemove

from app import keyboards as kb
from app import texts
import app.database.requests as rq
from app.services.payments import (
    CryptoCheckStatus,
    CryptoInvoiceStatus,
    check_crypto_invoice,
    create_crypto_invoice,
)

router = Router()


async def _safe_answer(callback: CallbackQuery, text: str, reply_markup=None) -> None:
    if callback.message is None:
        return
    await callback.message.answer(text, reply_markup=reply_markup)


@router.callback_query(F.data == "pay_usdt")
async def callback_usdt(callback: CallbackQuery) -> None:
    await callback.answer()
    if await rq.is_user_banned(callback.from_user.id):
        await _safe_answer(callback, texts.BANNED_TEXT, reply_markup=ReplyKeyboardRemove())
        return
    result = await create_crypto_invoice(callback.from_user.id, texts.PRICE_USDT)
    if result.status == CryptoInvoiceStatus.PAID:
        await _safe_answer(callback, texts.ACCESS_TEXT, reply_markup=kb.user_kb(True))
        return
    if result.status == CryptoInvoiceStatus.ERROR:
        await _safe_answer(callback, texts.PAYMENT_ERROR_TEXT)
        return
    if result.status == CryptoInvoiceStatus.ACTIVE and result.invoice_id and result.pay_url:
        await _safe_answer(
            callback,
            texts.PAY_USDT_TEXT,
            reply_markup=kb.check_payment_kb(result.invoice_id, result.pay_url),
        )
        return
    if (
        result.status != CryptoInvoiceStatus.CREATED
        or not result.invoice_id
        or not result.pay_url
    ):
        await _safe_answer(callback, texts.PAYMENT_ERROR_TEXT)
        return
    await _safe_answer(
        callback,
        texts.PAY_USDT_TEXT,
        reply_markup=kb.check_payment_kb(result.invoice_id, result.pay_url),
    )


@router.callback_query(F.data.startswith("check_invoice:"))
async def callback_check_invoice(callback: CallbackQuery) -> None:
    await callback.answer()
    if await rq.is_user_banned(callback.from_user.id):
        await _safe_answer(callback, texts.BANNED_TEXT, reply_markup=ReplyKeyboardRemove())
        return
    invoice_id = callback.data.split(":", 1)[1]
    result = await check_crypto_invoice(callback.from_user.id, invoice_id)
    if result.status == CryptoCheckStatus.INVALID_USER:
        await _safe_answer(callback, texts.PAYMENT_ERROR_TEXT)
        return
    if result.status in {CryptoCheckStatus.ERROR, CryptoCheckStatus.NOT_FOUND}:
        await _safe_answer(callback, texts.PAYMENT_ERROR_TEXT)
        return
    if result.status == CryptoCheckStatus.PAID:
        await _safe_answer(callback, texts.ACCESS_TEXT, reply_markup=kb.user_kb(True))
        return
    if result.status == CryptoCheckStatus.EXPIRED:
        await _safe_answer(callback, texts.PAYMENT_EXPIRED_TEXT)
        return
    if result.status == CryptoCheckStatus.FAILED:
        await _safe_answer(callback, texts.PAYMENT_FAILED_TEXT)
        return
    await _safe_answer(callback, texts.PAYMENT_PENDING_TEXT)
